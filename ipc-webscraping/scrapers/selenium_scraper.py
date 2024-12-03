import random

#### PARA SELENIUM
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Para el chrome driver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

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
    
    def scroll_to_element(self, css_selector):
        try:
            # Esperar a que el elemento sea visible en el DOM
            element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            
            # Usar ActionChains para desplazarse hasta el elemento
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            print(f"Se ha desplazado hasta el elemento: {css_selector}")
        except Exception as e:
            print(f"Error al hacer scroll hasta el elemento: {e}")
    
    def scroll_gradually(self, scroll_pause_time=0.5, scroll_step=200):
        """
        Realiza un scroll gradual hacia abajo en una página web.
        
        :param scroll_pause_time: Tiempo en segundos entre cada paso de scroll.
        :param scroll_step: Cantidad de píxeles a desplazar por cada paso.
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down by scroll_step pixels
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            
            # Espera para simular desplazamiento gradual
            time.sleep(scroll_pause_time)
            
            # Calcula la nueva posición del scroll
            new_height = self.driver.execute_script("return window.scrollY + window.innerHeight")
            
            if new_height >= last_height:
                break
            
            # Actualiza la altura si la página carga más contenido dinámicamente
            last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        print("Scroll completado.")

    # Función que maneja las acciones
    def perform_action(self, element, action, search_term):
        # Ejecutamos la acción de acuerdo al tipo
        if action.get('type') == 'click':
            element.click()
        elif action.get('type') == 'input':
            element.clear()
            value = action.get('value').format(search_term=search_term)
            element.send_keys(value)
        elif action.get('type') == 'enter':
            element.send_keys(Keys.RETURN)
        elif action.get('type') == 'scroll':
            print("haciendo scroll down")
            self.scroll_gradually(0.5, 100)
        elif action.get('type') == 'scroll-top':
            print("haciendo scroll top")
            self.driver.execute_script("window.scrollTo(0, 0);")     

    def execute_actions(self, website_elem, search_term):
        for action in website_elem.find('actions'):
            try:
                # Comportamiento aleatorio
                time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))
                
                ### Cambiar linea de codigo para que sea opcional
                selector = action.get('selector')

                element = None
                if len(selector) > 0:
                    element = WebDriverWait(self.driver, 30).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )


                # Manejamos que se pueda repetir varias veces
                if action.get("rep") == "All":
                    while True:
                        try:
                            # Ejecutamos la acción de acuerdo al tipo
                            self.perform_action(element, action, search_term)

                            #  Comportamiento aleatorio
                            time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))

                            # Verificamos si el elemento sigue presente
                            element = WebDriverWait(self.driver, 30).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                            
                        except Exception as e:
                            break  # Sale del ciclo cuando no encuentra el elemento
                else:
                    # Si no es 'All', solo ejecutamos la acción una vez
                    self.perform_action(element, action, search_term)
                                     
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
            # Maximiza
            #self.driver.maximize_window()
            #input("deteniendo")
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
                containers = WebDriverWait(self.driver, 25).until(
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
                            product[selector.tag] = element.text.strip().replace("\n", " ").replace("\r", " ")
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
                        # Scroll al elemento
                        self.scroll_to_element(next_page_selector)
                        print("se pudo scrollear al elemento")
                        # Se le hace click
                        next_page_button = WebDriverWait(self.driver, 25).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, next_page_selector))
                        )
                        
                        next_page_button.click()
                        page_number += 1

                        # Esperar a que cargue la siguiente página
                        WebDriverWait(self.driver, 10).until(
                            EC.staleness_of(containers[0])
                        )

                        # Hacemos scroll en caso sea neceseario
                        try:
                            scroll_value = int(pagination_selector.get('scroll'))

                            if scroll_value == 1:
                                print("Paginando con scroll....")
                                # Primero un top 
                                self.driver.execute_script("window.scrollTo(0, 0);") 

                                time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))
                                # Ahora un down
                                self.scroll_gradually(0.5, 100)

                                time.sleep(random.uniform(COTA_MINIMA_TIEMPO, COTA_MAXIMA_TIEMPO))

                                # Luego otro top 
                                #self.driver.execute_script("window.scrollTo(0, 0);") 

                        except Exception as e:
                            print("No se necesita el scroll")

                    #except (NoSuchElementException, TimeoutException):
                    except Exception as e:
                        print(e)
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
        return None