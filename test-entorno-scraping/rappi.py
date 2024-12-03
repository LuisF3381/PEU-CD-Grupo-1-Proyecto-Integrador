from json import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests
import itertools
from collections import ChainMap
import pandas as pd

BASE_HEADER = {
    "purpose": "prefetch",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "x-nextjs-data": "1",
    "Referer": "https://www.rappi.com.pe/tiendas/tipo/market",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
}
MAX_WORKERS = 4
MARKET_URL_API = (
    "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}.json"
)
MARKET_PRODUCTS_URL_API = (
    "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}/"
)
MARKET_CATEGORY_ENDPOINT = "{0}.json"
MARKETS = {
    "326-gas-station": "Listo",
    "33820-darkstores-nc": "La Cesta",
    "22885-oxxo-market": "Oxxo",
}
MAX_ATTEMPTS = 3
TIME_BETWEEN_ATTEMPS = 5
PRODUCTS_HEADER = {
    "accept": "*/*",
    "accept-language": "es",
    "if-none-match": 'W/"dvfo7fw9ae3yga"',
    "priority": "u=1, i",
    "purpose": "prefetch",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-nextjs-data": "1",
    "Referer": "https://www.rappi.com.pe/tiendas/{0}",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
}
PRODUCT_HEADER_REFERER = "https://www.rappi.com.pe/tiendas/{0}"
THREAD = ThreadPoolExecutor(max_workers=4)


def extract_information(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()


class RappiCrawler:
    def __init__(self) -> None:
        self.df_market = pd.DataFrame()
        self.market_dict = MARKETS

    def extract_market_categories(self, market_id):
        response = extract_information(MARKET_URL_API.format(market_id), BASE_HEADER)
        market_categories_list = response["pageProps"]["fallback"][
            f"storefront/{market_id}"
        ]["aisles_tree_response"]["data"]["components"]
        return {
            market_id: {
                "market_name": self.market_dict[market_id],
                "category_list": market_categories_list,
            }
        }

    def format_market_categories_url(self, market_id, market_dict):
        market_products_url = MARKET_PRODUCTS_URL_API.format(market_id)
        return list(
            THREAD.map(
                lambda x: {
                    "Market_id": market_id,
                    "Market_name": market_dict["market_name"],
                    "Market_cat_id": x["resource"]["friendly_url"],
                    "Market_cat_name": x["resource"]["name"],
                    "Market_cat_url": market_products_url
                    + MARKET_CATEGORY_ENDPOINT.format(x["resource"]["friendly_url"]),
                },
                market_dict["category_list"],
            )
        )

    def extract_url(self):
        market_info_url = dict(
            ChainMap(
                *list(
                    THREAD.map(self.extract_market_categories, self.market_dict.keys())
                )
            )
        )
        market_info_list = []
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.format_market_categories_url, market_id, market_info
                )
                for market_id, market_info in market_info_url.items()
            ]
            for market_future in as_completed(market_futures):
                market_info_list.extend(market_future.result())
        self.df_market = pd.DataFrame(market_info_list)


class RappiScraper:
    def __init__(self, path, market_cat_data):
        self.path = path
        self.market_cat_data = market_cat_data
        self.data = None

    def extract_information(self, url, headers):
        response = requests.get(url, headers=headers)
        return response.json()

    def extract_market_subcategories(
        self, market_cat_url, header_market, market_id, category_id
    ):
        header_market_2 = header_market.copy()
        current_attempt = 0
        is_in_progress = True
        while is_in_progress and current_attempt < MAX_ATTEMPTS:
            try:
                response = extract_information(market_cat_url, header_market)
                if "fallback" not in response["pageProps"]:
                    header_market_2["Referer"] = (
                        header_market["Referer"] + "/" + category_id
                    )
                    response = extract_information(market_cat_url, header_market_2)
                    current_attempt += 1
                else:
                    is_in_progress = False
            except JSONDecodeError:
                current_attempt += 1
        subcategories = response["pageProps"]["fallback"][
            f"storefront/{market_id}/{category_id}"
        ]["sub_aisles_response"]["data"]["components"]
        return {market_cat_url: subcategories}

    def extract_market_products(self, market_url, market_subcat_list):
        return list(
            itertools.chain.from_iterable(
                THREAD.map(
                    lambda x: [
                        {
                            "Market_cat_url": market_url,
                            "Product_name": product["name"],
                            "Product_price": product["price"],
                            "Product_description": product["description"],
                            "scrape_timestamp": str(pd.Timestamp.now()),
                        }
                        for product in x["resource"]["products"]
                    ],
                    market_subcat_list,
                )
            )
        )

    def extract(self):
        markets_id_list = self.market_cat_data.Market_id.unique()
        headers_by_market = {}
        for market_id in markets_id_list:
            headers_by_market[market_id] = PRODUCTS_HEADER.copy()
            headers_by_market[market_id]["Referer"] = PRODUCT_HEADER_REFERER.format(
                market_id
            )

        market_subcategories_dict = {}
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.extract_market_subcategories,
                    market_row.Market_cat_url,
                    headers_by_market[market_row.Market_id],
                    market_row.Market_id,
                    market_row.Market_cat_id,
                )
                for market_row in self.market_cat_data.itertuples()
            ]
            for market_future in as_completed(market_futures):
                market_subcategories_dict.update(market_future.result())
        list_products = []
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.extract_market_products, market_cat_url, market_subcat_list
                )
                for market_cat_url, market_subcat_list in market_subcategories_dict.items()
            ]
            for market_future in as_completed(market_futures):
                list_products.extend(market_future.result())
        self.data = pd.DataFrame(list_products)

    def process_data(self):
        self.data = pd.merge(self.market_cat_data, self.data, "left", "Market_cat_url")
        self.data["Date"] = pd.Timestamp("today").strftime("%d%m%Y")
        self.data["Product_name"] = self.data["Product_name"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )
        self.data["Product_description"] = self.data["Product_description"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )

    def save_data(self):
        if len(self.data) > 0:
            self.data.to_csv(self.path, sep=",", index=False)

    def run(self):
        self.extract()
        self.process_data()
        self.save_data()


def main():
    crawler = RappiCrawler()
    crawler.extract_url()
    scraper = RappiScraper(
        "Rappi_" + pd.Timestamp("today").strftime("%d%m%Y") + ".csv",
        crawler.df_market,
    )
    scraper.run()


if __name__ == "__main__":
    main()
