"""
En este archivo estamos testeando que tengamos las librerias correctamente configuradas para 
emplear selenium
"""

import random

#### PARA SELENIUM
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Funcion para el user agent
from selenium.webdriver.chrome.options import Options

# Para el chrome driver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


##### PARA XML
import xml.etree.ElementTree as ET

# Para los mensajes de error
import logging


# Para crear los directorios
from pathlib import Path

# Pandas para guardar en .csv
import pandas as pd

# Para el datetime
from datetime import datetime


import time

COTA_MINIMA_TIEMPO = 2
COTA_MAXIMA_TIEMPO = 5

### Clase Generica para hacer scraping en selenium

class WebScraper_Selenium:
    """
    Clase que permite realizar la extraccion de informacion para una web empleando el 
    enfoque de Selenium
    """
    def __init__(self, config_path, opts):
        # Definimos el driver de selenium
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
        # Leemos el archivo xml
        self.config = self._load_config(config_path)
        #self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _load_config(self, config_path):
        tree = ET.parse(config_path)
        return tree.getroot()
    
    def execute_actions(self, website_elem, search_term):
        for action in website_elem.find('actions'):
            try:
                # Comportamiento aleatorio
                time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))
                
                selector = action.get('selector')
                
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # Hacer click a un elemento
                if action.get('type') == 'click':
                    element.click()
                elif action.get('type') == 'input':
                    element.clear()
                    value = action.get('value').format(search_term=search_term)
                    element.send_keys(value)
                
                    
            except Exception as e:
                if action.get('optional') != 'true':
                    raise e
                logging.warning(f"Optional action failed: {str(e)}")
            
        #input("deteniendo la ejecucion master")

        return None


    def scrape_products(self, website_name, search_term):
        
        # Buscamos el nombre del sitio web a scrapear 
        website = self.config.find(f".//website[@name='{website_name}']")
        if website is None:
            raise ValueError(f"Website {website_name} not found in config")

        # Selectores para paginación
        pagination_selector = website.find('selectors/pagination')
        next_page_selector = pagination_selector.get('next_page_selector') if pagination_selector is not None else None

        # Límite de páginas (por defecto ilimitado)
        max_pages = int(pagination_selector.get('max_pages', '9999')) if pagination_selector is not None else 9999

        print(next_page_selector, max_pages)

        all_products = []
        page_number = 1

        try:
            # Navegar a la página
            self.driver.get(website.get('base_url'))

            # Comportamiento aleatorio
            time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))

            # Ejecutar acciones de búsqueda
            self.execute_actions(website, search_term)

            # Comportamiento aleatorio
            time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))
            
            # Ahora procedemos a encontrar los containers en los que estan los productos
            # Obtener selectores
            while page_number <= max_pages:

                # Seleccionamos la informacion de la pagina actual
                selectors = website.find('selectors')
                containers = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, selectors.find('container').text)
                    )
                )
                
                print(len(containers))
                
                
                # Aplicar límite si existe
                limit = selectors.find('limit')
                if limit is not None:
                    containers = containers[:int(limit.text)]
                
                # Extraer datos de cada producto
                
                for container in containers:
                    product = {}
                    for selector in selectors:
                        if selector.tag in ['container', 'limit', 'pagination']:
                            continue
                        try:
                            # El selector puede ser compuesto (separado por comas)
                            element = container.find_element(By.CSS_SELECTOR, selector.text)
                            product[selector.tag] = element.text.strip()
                        except:
                            product[selector.tag] = None
                            
                    if any(product.values()):  # Solo agregar si se encontró algún dato
                        all_products.append(product)
                
                # Logica para cambiar de pagina
                if next_page_selector != None and page_number < max_pages:
                    # El siguiente codigo aun por testear 
                    try:
                        print("Aplicando paginacion.....")
                        # Comportamiento aleatorio
                        time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))

                        next_page_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                        )
                        
                        next_page_button.click()
                        page_number += 1

                        # Esperar a que cargue la siguiente página
                        WebDriverWait(self.driver, 10).until(
                            EC.staleness_of(containers[0])
                        )

                    #except (NoSuchElementException, TimeoutException):
                    except Exception as e:
                    # No hay más páginas
                        break

                else:
                    # Sin más páginas o se alcanzó el límite
                    break

            return all_products

        except Exception as e:
            logging.error(f"Error scraping {website_name}: {str(e)}")
            return []
            
        finally:
            self.driver.quit()


    def scrape_and_save(self, website_name, search_term, output_dir):
        """Scrape products and save raw data to Parquet file using Pandas"""
        # Aqui va la logica con el output_dir para crear la carpeta y eso
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Scrapeamos el producto
        products = self.scrape_products(website_name, search_term)

        if len(products) > 0:
            df = pd.DataFrame(products)

            # Añadimos los metadatos
            df['website'] = website_name
            df['search_term'] = search_term
            df['scrape_timestamp'] = pd.Timestamp.now()

            # Generar nombre de archivo con timestamp
            filename = f"{website_name}_{search_term}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = output_dir / filename
            # Guardar como CSV
            df.to_csv(filepath, index=False)
            
            return filepath
        #print(products)
        return None






# Definimos el User Agent en Selenium utilizando la clase Options
opts = Options()

    # Escogemos un User Agent Aleatorio para prevenir un baneo de ip
opcion = random.randint(1, 4)
if opcion == 1:
    opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/74.0.3729.169 Safari/537.36")
elif opcion == 2:
    opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.149 Safari/537.36")
elif opcion == 3:
    opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/74.0.3729.157 Safari/537.36")
elif opcion == 4:
    opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/79.0.3945.117 Safari/537.36")



# LOGICA PARA USAR PROXIES

proxies = [
            "43.134.68.153:3128",
            "150.230.214.66:1080",
            "43.134.229.98:3128",
            "129.226.193.16:3128",
            "43.133.59.220:3128",
            "31.40.248.2:8080"
        ]

proxy = random.choice(proxies)
opts.add_argument(f'--proxy-server={proxy}')
 # Configuraciones adicionales de seguridad


# adding argument to disable the AutomationControlled flag 
opts.add_argument("--disable-blink-features=AutomationControlled") 
 
# exclude the collection of enable-automation switches 
opts.add_experimental_option("excludeSwitches", ["enable-automation"]) 
 
# turn-off userAutomationExtension 
opts.add_experimental_option("useAutomationExtension", False) 





# DEfinimos el objeto scraper
scraper = WebScraper_Selenium('tiendas_conv_online.xml', opts)

# Ejecutamos el metodo de extraccion
"""
raw_data_file = scraper.scrape_and_save(
        'tambo', 
        'leche', 
        'leche/'
)
"""
#print(scraper.config)


raw_data_file = scraper.scrape_and_save(
        'Listo', 
        'leche', 
        'leche/'
)






# Cargamos el driver de chrome
#driverMetro = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)

#driverMetro.get('https://www.tambo.pe/')



"""
div class="absolute h-8 w-8 -right-3 -top-3 primaryBackgroundColor rounded-full text-sm font-semibold text-white shadow-sm flex justify-center items-center cursor-pointer
"""