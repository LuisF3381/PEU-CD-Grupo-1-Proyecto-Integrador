from json import JSONDecodeError
import requests
from time import time
import pandas as pd
BASE_HEADER = {
    "purpose": "prefetch",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-nextjs-data": "1",
    "Referer": "https://www.rappi.com.pe/tiendas/tipo/market",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82"
}
MARKET_URL_API = "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}.json"
MARKET_PRODUCTS_URL_API = "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}/"
MARKET_CATEGORY_ENDPOINT = "{0}.json"
MARKETS = {
    "326-gas-station": "Listo",
    "33820-darkstores-nc": "La Cesta"
}
MAX_ATTEMPTS = 3
TIME_BETWEEN_ATTEMPS = 5
PRODUCTS_HEADER = {
    "accept": "*/*",
    "accept-language": "es",
    "if-none-match": "W/\"dvfo7fw9ae3yga\"",
    "priority": "u=1, i",
    "purpose": "prefetch",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-nextjs-data": "1",
    "Referer": "https://www.rappi.com.pe/tiendas/{0}",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82"
}
COLUMNS = ["Nombre", "precio", "website", "scrape_timestamp"]

class RappiScraper():
    def __init__(self, path) -> None:
        self.columns = COLUMNS
        self.path = path
        self.data = None

    def extract_information(self, url, headers):
        response = requests.get(url, headers=headers)
        return response.json()
    
    def extract(self):
        list_products = []
        for market_id, market_name in MARKETS.items():
            response = self.extract_information(MARKET_URL_API.format(market_id), BASE_HEADER)
            market_categories_list = response["pageProps"]["fallback"][f"storefront/{market_id}"]["aisles_tree_response"]["data"]["components"]
            PRODUCTS_HEADER["Referer"] = PRODUCTS_HEADER["Referer"].format(market_id)
            market_products_url = MARKET_PRODUCTS_URL_API.format(market_id)
            for category in market_categories_list:
                category_name = category["resource"]["friendly_url"]
                current_attempt = 0
                in_progress = True
                while in_progress and (current_attempt < MAX_ATTEMPTS):
                    try:
                        response = self.extract_information(market_products_url + MARKET_CATEGORY_ENDPOINT.format(category_name), PRODUCTS_HEADER)
                    except (JSONDecodeError, ValueError, KeyError):
                        print(market_id, category_name)
                        current_attempt += 1
                        print(current_attempt)
                    else:
                        try:
                            subcategories = response["pageProps"]["fallback"][f"storefront/{market_id}/{category_name}"]["sub_aisles_response"]["data"]["components"]
                        except KeyError:
                            print(response)
                            raise Exception()
                        for subcategory in subcategories:
                            list_products.extend([[product["name"], product["price"], market_name] for product in subcategory["resource"]["products"]])
                        in_progress = False
        self.data = pd.DataFrame(list_products, columns=COLUMNS[:3])
        self.data["scrape_timestamp"] = str(pd.Timestamp.now())
    
    def save_data(self):
        if len(self.data) > 0:
            self.data.to_csv(self.path, sep=",", index=False)

    def run(self):
        self.extract()
        self.save_data()

def main():
    scraper = RappiScraper(
        "PedidosYa_" + pd.Timestamp("today").strftime("%d%m%Y") + ".csv"
    )
    scraper.run()

if __name__ == "__main__":
    main()
