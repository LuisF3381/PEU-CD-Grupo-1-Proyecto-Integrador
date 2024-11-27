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

import logging


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
        
    
    def _load_config(self, config_path):
        tree = ET.parse(config_path)
        return tree.getroot()
    
    def execute_actions(self, website_elem, search_term):
        for action in website_elem.find('actions'):
            try:
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

        try:
            # Navegar a la página
            self.driver.get(website.get('base_url'))
            
            # Ejecutar acciones de búsqueda
            self.execute_actions(website, search_term)
            
            # Ahora procedemos a encontrar los containers en los que estan los productos
            # Obtener selectores
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
            products = []
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
                    products.append(product)
                    
            return products
            


        except Exception as e:
            logging.error(f"Error scraping {website_name}: {str(e)}")
            return []
            
        finally:
            self.driver.quit()


    def scrape_and_save(self, website_name, search_term, output_dir):
        """Scrape products and save raw data to Parquet file using Pandas"""
        # Aqui va la logica con el output_dir para crear la carpeta y eso
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        """

        # Scrapeamos el producto}
        products = self.scrape_products(website_name, search_term)

        print(products)

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


# DEfinimos el objeto scraper
scraper = WebScraper_Selenium('arroz.xml', opts)

# Ejecutamos el metodo de extraccion
raw_data_file = scraper.scrape_and_save(
        'tambo', 
        'leche', 
        'data/raw'
)

#print(scraper.config)







# Cargamos el driver de chrome
#driverMetro = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)

#driverMetro.get('https://www.tambo.pe/')



"""
div class="absolute h-8 w-8 -right-3 -top-3 primaryBackgroundColor rounded-full text-sm font-semibold text-white shadow-sm flex justify-center items-center cursor-pointer
"""