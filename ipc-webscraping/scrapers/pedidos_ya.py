from curl_cffi import requests
from time import sleep
import pandas as pd
from os import path, makedirs

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "es",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "Referer": "https://www.pedidosya.com.pe/cadenas/pedidosya-market",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Connection": "keep-alive",
}
MARKET_URL_API = "https://www.pedidosya.com.pe/chains-landing/api/offer/3679"
VENDOR_URL_API = "https://www.pedidosya.com.pe/groceries/web/v1/vendors/{0}"
CATEGORY_ENDPOINT = "/categories"
PRODUCT_ENDPOINT = "/products?categoryId={0}&limit=100&page={1}"
BASE_URL_API = "https://www.pedidosya.com.pe"
LARGE_PAUSE = 60
SESSION = requests.Session()
DATA_FOLDER_PATH = "data/raw/pedidos_ya/"
DATA_BASE_PATH = path.join(path.dirname(path.realpath(__file__))[:-9], DATA_FOLDER_PATH)


class PedidosYaScraper:
    def __init__(self, path) -> None:
        self.base_url = BASE_URL_API
        self.market_url = MARKET_URL_API
        self.vendor_url = VENDOR_URL_API
        self.category_endpoint = CATEGORY_ENDPOINT
        self.product_endpoint = PRODUCT_ENDPOINT
        self.data = None
        self.path = path

    def extract_information(self, url, headers):
        response = SESSION.get(url, headers=headers, impersonate="chrome")
        return response.json()

    def extract(self):
        market_info = self.extract_information(self.market_url, BASE_HEADERS)
        market_lince = market_info["data"][3]

        self.vendor_url = self.vendor_url.format(market_lince["id"])
        BASE_HEADERS["Referer"] = self.base_url + market_lince["url"]
        category_info = self.extract_information(
            self.vendor_url + self.category_endpoint, BASE_HEADERS
        )
        category_list = [
            [cat["global_id"], cat["name"]] for cat in category_info["categories"]
        ]
        list_products = []
        for cat_id, cat_name in category_list:
            is_not_last_page = True
            page = 0
            while is_not_last_page:
                try:
                    response = self.extract_information(
                        self.vendor_url + self.product_endpoint.format(cat_id, page),
                        BASE_HEADERS,
                    )
                    if response["lastPage"]:
                        is_not_last_page = False
                    else:
                        page += 1
                    list_products.extend(
                        [
                            {
                                "Market_name": "Pedidos Ya Lince",
                                "Category_name": cat_name,
                                "Product_name": prod["name"],
                                "Product_description": prod["description"],
                                "Product_unit_type": prod["size"]["unit"],
                                "Product_quantity": prod["size"]["content"],
                                "Product_price": prod["pricing"]["beforePrice"],
                                "Product_branch": prod["defaultBrandName"],
                                "Scrape_timestamp": str(pd.Timestamp.now()),
                            }
                            for prod in response["items"]
                        ]
                    )
                except Exception as e:
                    print(e)
                    break
            sleep(LARGE_PAUSE)

        self.data = pd.DataFrame(list_products)

    def process_data(self):
        self.data["Product_name"] = self.data["Product_name"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )
        self.data["Product_description"] = self.data["Product_description"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )
        self.data["website"] = "Pedidos Ya"
        self.data = self.data.drop_duplicates()
        self.data.reset_index(drop=True, inplace=True)

    def save_data(self):
        if len(self.data) > 0:
            if not path.exists(DATA_BASE_PATH):
                makedirs(DATA_BASE_PATH)
            self.data.to_csv(path.join(DATA_BASE_PATH, self.path), sep=",", index=False)

    def run(self):
        self.extract()
        self.process_data()
        self.save_data()


def main():
    scraper = PedidosYaScraper(
        "PedidosYa_" + pd.Timestamp("today").strftime("%d%m%Y") + ".csv"
    )
    scraper.run()


if __name__ == "__main__":
    main()
