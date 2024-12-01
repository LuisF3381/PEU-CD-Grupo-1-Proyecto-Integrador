import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any
import re


class WebScraper_BeautifulSoup:
    def __init__(self, config_path: str, output_folder: str = 'scraping_results'):
        """
        Inicializa el scraper con configuración XML y carpeta de resultados
        
        Args:
            config_path (str): Ruta al archivo XML de configuración
            output_folder (str): Carpeta raíz para guardar resultados
        """
        # Configurar logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

        # Configurar rutas y carpetas
        self.config_path = config_path
        self.root_output_folder = output_folder
        os.makedirs(self.root_output_folder, exist_ok=True)

        # Parsear configuración
        self.config = self._parse_config()
    
    def _parse_config(self) -> List[Dict[str, Any]]:
        """
        Parsea el archivo XML de configuración de manera flexible
        
        Returns:
            List[Dict[str, Any]]: Configuraciones de sitios web
        """
        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
            
            websites = []
            for website in root.findall('website'):
                site_config = {
                    'name': website.get('name'),
                    'base_url': website.get('base_url'),
                    'selectors': {}
                }
                
                # Iterar dinámicamente sobre todos los selectores
                selectors = website.find('selectors')
                if selectors is not None:
                    for selector in selectors:
                        site_config['selectors'][selector.tag] = selector.text
                
                # Manejar paginación si existe
                pagination = website.find('selectors/pagination')
                if pagination is not None:
                    site_config['pagination'] = {
                        'url_pagination': pagination.get('url_pagination'),
                        'max_pages': int(pagination.get('max_pages', 1))
                    }
                
                websites.append(site_config)
            
            return websites
        except Exception as e:
            self.logger.error(f"Error parseando configuración XML: {e}")
            raise

    def scrape_all(self, keywords: List[str]):
        """
        Realiza scraping para múltiples palabras clave
        
        Args:
            keywords (List[str]): Lista de palabras clave a buscar
        """
        for keyword in keywords:
            self.scrape(keyword)


    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza un nombre de archivo eliminando caracteres no permitidos
        
        Args:
            filename (str): Nombre de archivo original
        
        Returns:
            str: Nombre de archivo sanitizado
        """
        # Reemplazar caracteres no permitidos con guiones
        return re.sub(r'[^\w\-_\. ]', '_', filename)


    def scrape(self, keyword: str):
        """
        Realiza scraping con manejo dinámico de selectores para un término
        
        Args:
            keyword (str): Palabra clave para buscar
        """
        # Crear carpeta para el término de búsqueda
        search_term_folder = os.path.join(
            self.root_output_folder, 
            self._sanitize_filename(keyword)
        )
        os.makedirs(search_term_folder, exist_ok=True)
        
        all_results = []
        
        for site in self.config:
            try:
                website_name = site['name']
                
                # Procesar primera página
                url = site['base_url'].replace('{keyword}', keyword)
                print(url)
                results = self._scrape_page(url, site)
                
                # Añadir metadatos a cada resultado
                for result in results:
                    result['website'] = website_name
                    result['search_term'] = keyword
                    result['scrape_timestamp'] = datetime.now().isoformat()
                
                all_results.extend(results)
                
                # Manejar paginación si está configurada
                if site.get('pagination'):
                    for page_num in range(2, site['pagination']['max_pages'] + 1):
                        pagination_url = site['pagination']['url_pagination'].format(
                            keyword=keyword, 
                            number=page_num
                        )
                        page_results = self._scrape_page(pagination_url, site)
                        
                        # Añadir metadatos a resultados de páginas
                        for result in page_results:
                            result['website'] = website_name
                            result['search_term'] = keyword
                            result['scrape_timestamp'] = datetime.now().isoformat()
                        
                        if not page_results:
                            break
                        
                        all_results.extend(page_results)
                
                # Exportar resultados por sitio web
                if all_results:
                    self._export_to_csv(
                        data=all_results, 
                        website_name=website_name, 
                        search_term=keyword, 
                        output_folder=search_term_folder
                    )
                
            except Exception as e:
                self.logger.error(f"Error scrapeando {site['name']}: {e}")



    def _scrape_page(self, url: str, site_config: Dict) -> List[Dict]:
        """
        Extrae elementos de una página usando selectores dinámicos
        
        Args:
            url (str): URL de la página
            site_config (Dict): Configuración del sitio
        
        Returns:
            List[Dict]: Elementos extraídos
        """
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
                        
            # Extraer contenedores
            container_selector = site_config['selectors'].get('container', '')
            
            containers = soup.select(container_selector) if container_selector else [soup]
            print(containers)
            results = []
            for container in containers:
                # Extraer dinámicamente todos los selectores configurados
                result = {}
                for key, selector in site_config['selectors'].items():
                    # Ignorar el selector de contenedor y pagination
                    if key not in ['container', 'pagination']:
                        result[key] = self._extract_text(container, selector)
                
                # Agregar solo si se extrajo al menos un campo
                if any(result.values()):
                    results.append(result)
            
            print(results)
            return results
            
        except requests.RequestException as e:
            print("errror ps")
            self.logger.error(f"Error de solicitud en {url}: {e}")
            return []

    def _extract_text(self, soup_element, selector: str) -> Optional[str]:
        """
        Extrae texto de un elemento usando un selector
        
        Args:
            soup_element: Elemento BeautifulSoup
            selector (str): Selector CSS
        
        Returns:
            Optional[str]: Texto extraído o None
        """
        try:
            # Intentar extraer texto de múltiples formas
            element = soup_element.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                # Si no hay texto, intentar con atributos comunes
                return text if text else (element.get('content') or element.get('title') or element.get('alt'))
            return None
        except Exception:
            return None

    def _export_to_csv(self, 
                        data: List[Dict], 
                        website_name: str, 
                        search_term: str, 
                        output_folder: str):
        """
        Exporta los datos extraídos a un archivo CSV con metadatos
        
        Args:
            data (List[Dict]): Datos a exportar
            website_name (str): Nombre del sitio web
            search_term (str): Término de búsqueda
            output_folder (str): Carpeta para guardar el archivo
        
        Returns:
            str: Ruta del archivo CSV generado
        """
        try:
            if not data:
                self.logger.warning("No hay datos para exportar")
                return None
            
            # Convertir a DataFrame para facilitar manipulación
            df = pd.DataFrame(data)
            
            # Añadir metadatos
            df['website'] = website_name
            df['search_term'] = search_term
            df['scrape_timestamp'] = pd.Timestamp.now()
            
            # Generar nombre de archivo con timestamp
            filename = f"{website_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(output_folder, filename)
            
            # Exportar a CSV
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.logger.info(f"Datos exportados a {filepath}")
            return filepath
        
        except Exception as e:
            self.logger.error(f"Error exportando CSV: {e}")
            return None




# Crear scraper con configuración y carpeta raíz de resultados
scraper = WebScraper_BeautifulSoup('supermercados.xml', output_folder='supermercados_data_raw')

# Realizar scraping para múltiples términos
scraper.scrape_all(['aceite'])




