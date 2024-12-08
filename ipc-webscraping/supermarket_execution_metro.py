
import random
import os
import pandas as pd
# Importamos la clase base 
from scrapers.selenium_scraper import WebScraper_Selenium

# Funcion para el user agent
from selenium.webdriver.chrome.options import Options
import datetime

def generar_opts():
    # Definimos el User Agent en Selenium utilizando la clase Options
    opts = Options()
    
    # Escogemos un User Agent Aleatorio 
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
    
    # Lista de proxies
    proxies = [
        "189.240.60.169:9090",
        "189.240.60.166:9090",
        "189.240.60.168:9090",
        "116.107.105.191:12003",
        "116.203.135.164:8090",
        "103.169.187.35:6080",
        "116.203.56.216:3128",
        "116.203.135.164:8090",
        "92.113.144.119:8080",
        "189.240.60.168:9090",
        "45.8.21.29:47381",
        "181.233.62.9:999"
    ]
    
    # Seleccionar un proxy aleatorio
    proxy = random.choice(proxies)
    #opts.add_argument(f'--proxy-server={proxy}')
    #opts.add_argument("--headless=new")
    opts.add_argument("--window-size=800,600")
    
    # Configuraciones adicionales de seguridad
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    
    return opts


# Definmos en hilos y ejecutamos
current_date = datetime.datetime.now().strftime("%Y_%m_%d")


# Obtener la ruta absoluta del archivo
current_dir = os.path.dirname(__file__)  # Directorio actual del script
config_path = os.path.join(current_dir, 'config_websites', 'metro.xml')
output_path = os.path.join(current_dir, 'data', 'raw','metro', current_date)
csv_path = os.path.join(current_dir, 'base_period', 'IPC_BASE.csv')



aux = pd.read_csv(csv_path)
print(aux["CLASIFICACION"])

"""
opts = generar_opts()

# DEfinimos el objeto scraper
scraper = WebScraper_Selenium(config_path, opts)


raw_data_file = scraper.scrape_and_save(
        'metro', 
        'MAÍZ MORADO',
        output_path
        )
"""
import concurrent.futures
import logging

def scrape_term(termino):
    try:
        # Generar opciones únicas para cada hilo
        opts = generar_opts()
        
        # DEfinimos el objeto scraper
        scraper = WebScraper_Selenium(config_path, opts)
        
        # Intentar scraping
        raw_data_file = scraper.scrape_and_save(
            'metro',
            termino,
            output_path
        )
        
        # Log de éxito
        logging.info(f"Scraping exitoso para término: {termino}")
        
        return {
            'termino': termino,
            'raw_data_file': raw_data_file,
            'status': 'success'
        }
    
    except Exception as e:
        # Log del error específico
        logging.error(f"Error en scraping para término {termino}: {str(e)}")
        
        return {
            'termino': termino,
            'raw_data_file': None,
            'status': 'failed',
            'error': str(e)
        }

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='scraping_log.txt')

# Leer el archivo de configuración
aux = pd.read_csv(csv_path)
print(aux["CLASIFICACION"])

#scrape_term("leche")


# Usar ThreadPoolExecutor para ejecutar scraping en paralelo
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # Mapear la función de scraping a todos los términos
    resultados = list(executor.map(scrape_term, aux["CLASIFICACION"]))

# Analizar resultados
exitosos = [r for r in resultados if r['status'] == 'success']
fallidos = [r for r in resultados if r['status'] == 'failed']

# Resumen de resultados
print(f"Scraping completado. Éxitos: {len(exitosos)}, Fallos: {len(fallidos)}")

# Opcional: imprimir detalles de fallos
if fallidos:
    print("\nDetalles de fallos:")
    for fallo in fallidos:
        print(f"Término: {fallo['termino']}, Error: {fallo['error']}")
