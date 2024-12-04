from curl_cffi import requests
from time import sleep
import pandas as pd
from os import path, makedirs
import random

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
    "User-Agent": "",
    "Connection": "keep-alive",
}
MARKET_URL_API = "https://www.pedidosya.com.pe/chains-landing/api/offer/3679"
VENDOR_URL_API = "https://www.pedidosya.com.pe/groceries/web/v1/vendors/{0}"
CATEGORY_ENDPOINT = "/categories"
PRODUCT_ENDPOINT = "/products?categoryId={0}&limit=100&page={1}"
BASE_URL_API = "https://www.pedidosya.com.pe"
SHORT_PAUSE = 3
NORMAL_PAUSE = 1
LARGE_PAUSE = 180
LOW_BOUND = 3
USER_AGENT_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"
]

UPPER_BOUND = 12
DATA_FOLDER_PATH = "data/raw/pedidos_ya/"
DATA_BASE_PATH = path.join(path.dirname(path.realpath(__file__))[:-9], DATA_FOLDER_PATH)
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

    def extract_information(self, session, url, headers):
        response = session.get(url, headers=headers, impersonate="chrome")
        return response.json()

    def extract(self):
        SESSION = requests.Session()
        list_user_agents = random.sample(USER_AGENT_LIST, 10)
        BASE_HEADERS["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82"
        market_info = self.extract_information(SESSION, self.market_url, BASE_HEADERS)
        market_lince = market_info["data"][3]

        self.vendor_url = self.vendor_url.format(market_lince["id"])
        BASE_HEADERS["Referer"] = self.base_url + market_lince["url"]
        category_info = self.extract_information(
            SESSION, self.vendor_url + self.category_endpoint, BASE_HEADERS
        )
        category_list = [
            [cat["global_id"], cat["name"]] for cat in category_info["categories"]
        ]
        list_products = []
        count = 0

        for cat_id, cat_name in category_list:
            is_not_last_page = True
            page = 0
            while is_not_last_page:
                try:
                    count += 1
                    response = self.extract_information(
                        SESSION,
                        self.vendor_url + self.product_endpoint.format(cat_id, page),
                        BASE_HEADERS,
                    )
                    if (count % UPPER_BOUND) == 0:
                        print(LARGE_PAUSE)
                        SESSION.close()
                        SESSION = requests.Session()
                        BASE_HEADERS["User-Agent"] = list_user_agents.pop()
                        sleep(LARGE_PAUSE)
                    else:
                        pause = random.randint(1,3)
                        print(pause)
                        sleep(pause)

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
                                "Product_price": prod["pricing"]["beforePrice"],
                                "Scrape_timestamp": str(pd.Timestamp.now()),
                            }
                            for prod in response["items"]
                        ]
                    )
                except Exception as e:
                    print(e)
                    break

        self.data = pd.DataFrame(list_products)

    def process_data(self):
        self.data["Product_name"] = self.data["Product_name"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )
        self.data["Product_description"] = self.data["Product_description"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )

    def save_data(self, data):
        if len(self.data) > 0:
            if not path.exists(DATA_BASE_PATH):
                makedirs(DATA_BASE_PATH)
            self.data.to_csv(path.join(DATA_BASE_PATH, self.path), sep=",", index=False)

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
