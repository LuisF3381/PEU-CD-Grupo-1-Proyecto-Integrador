import json
import requests
from datetime import datetime
from time import sleep
import pandas as pd

COLUMNS = ["Nombre", "precio", "website", "scrape_timestamp"]
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
}
MARKET_URL_API = "https://www.pedidosya.com.pe/chains-landing/api/offer/3679"
VENDOR_URL_API = "https://www.pedidosya.com.pe/groceries/web/v1/vendors/{0}"
CATEGORY_ENDPOINT = "/categories"
PRODUCT_ENDPOINT = "/products?categoryId={0}&limit=20&page={1}"
BASE_URL_API = "https://www.pedidosya.com.pe"

"""
{'id': 225411,
  'name': 'PedidosYa Market - Surquillo',
  'logo': 'pedidosya-market-logo.png',
  'url': '/restaurantes/lima/pedidosya-market-surquillo-menu'
}
"""


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
        response = requests.get(url, headers=headers)
        return response.json()

    def extract(self):
        market_info = self.extract_information(self.market_url, BASE_HEADERS)
        market_lince = market_info["data"][3]

        self.vendor_url = self.vendor_url.format(market_lince["id"])
        BASE_HEADERS["Referer"] = self.base_url + market_lince["url"]
        category_info = self.extract_information(
            self.vendor_url + self.category_endpoint, BASE_HEADERS
        )
        category_id_list = [cat["global_id"] for cat in category_info["categories"]]

        list_products = []
        for cat in category_id_list:
            is_not_last_page = True
            page = 0

            while is_not_last_page:
                try:
                    response = self.extract_information(
                        self.vendor_url + self.product_endpoint.format(cat, page),
                        BASE_HEADERS,
                    )

                    if response["lastPage"]:
                        is_not_last_page = False
                    else:
                        page += 1
                        list_products.extend(
                            [
                                [prod["name"], prod["pricing"]["beforePrice"]]
                                for prod in response["items"]
                            ]
                        )

                except Exception as e:
                    print(e)
                    break
        return list_products

    def save_data(self, data):
        self.data = pd.DataFrame(data, columns=COLUMNS[:2])
        if len(self.data) > 0:
            self.data["website"] = "Pedidos Ya"
            self.data["scrape_timestamp"] = str(pd.Timestamp.now())
            self.data.to_csv(self.path, sep=",", index=False)

    def run(self):
        data = self.extract()
        self.save_data(data)


def main():
    scraper = PedidosYaScraper(
        "PedidosYa_" + pd.Timestamp("today").strftime("%d%m%Y") + ".csv"
    )
    scraper.run()


if __name__ == "__main__":
    main()
