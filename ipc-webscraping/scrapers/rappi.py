from json import JSONDecodeError
from time import sleep
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests
import itertools
from collections import ChainMap
import pandas as pd
from os import path, makedirs

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
RAPPI_ACCESS_HEADER = {
    "accept": "*/*",
    "accept-language": "es",
    "content-type": "application/json",
    "deviceid": "f8d92605-81d4-4a70-99b4-c57310b9d33f",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "Referer": "https://www.rappi.com.pe/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
}

MAX_WORKERS = 4
MARKET_URL_API = (
    "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}.json"
)
MARKET_CATEGORY_URL_API = (
    "https://www.rappi.com.pe/_next/data/SQj6GD4SjvTQxRS33HKCi/es-PE/ssg/{0}/"
)
MARKET_CATEGORY_ENDPOINT = "{0}.json"
MARKET_PRODUCTS_URL_API = (
    "https://services.rappi.pe/api/web-gateway/web/dynamic/context/content/"
)
MARKETS = {
    "326-gas-station": "Listo",
    "33820-darkstores-nc": "La Cesta",
    "22885-oxxo-market": "Oxxo",
}
API_URL_GUEST = "https://services.rappi.pe/api/rocket/v2/guest"
API_URL_GUEST_PASSPORT = "https://services.rappi.pe/api/rocket/v2/guest/passport/"
MAX_ATTEMPTS = 5
TIME_BETWEEN_ATTEMPS = 5
CATEGORY_HEADER = {
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
MARKET_PRODUCTS_HEADER = {
    "accept": "application/json",
    "accept-language": "es-PE",
    "access-control-allow-headers": "*",
    "access-control-allow-origin": "*",
    "app-version": "",
    "authorization": "",
    "content-type": "application/json",
    "deviceid": "6cb01ea9-f708-4f96-8566-dd63f988e88e",
    "include_context_info": "true",
    "language": "es",
    "needappsflyerid": "false",
    "priority": "u=1, i",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "Referer": "https://www.rappi.com.pe/",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
}

PRODUCT_HEADER_REFERER = "https://www.rappi.com.pe/tiendas/{0}"
THREAD = ThreadPoolExecutor(max_workers=4)
DATA_FOLDER_PATH = "data/raw/rappi/"
DATA_BASE_PATH = path.join(path.dirname(path.realpath(__file__))[:-9], DATA_FOLDER_PATH)
MARKET_INFO_DICT = {
    "326-gas-station": {
        "lat": "-12.145395",
        "lng": "-77.021936",
        "store_type": "gas_station",
        "stores": [326],
    },
    "33820-darkstores-nc": {
        "lat": "-12.145395",
        "lng": "-77.021936",
        "store_type": "darkstores_nc",
        "stores": [33820],
    },
    "22885-oxxo-market": {
        "lat": "-12.145395",
        "lng": "-77.021936",
        "store_type": "oxxo_market",
        "stores": [22885],
    },
}
PRODUCTS_VARIABLES = {
    "limit": 50,
    "offset": 0,
    "state": {
        "parent_store_type": "market",
        "lat": "-12.145395",
        "lng": "-77.021936",
        "aisle_id": "250",
        "parent_id": "244",
        "store_type": "oxxo_market",
    },
    "stores": [22885],
    "context": "aisle_detail",
}


def extract_information(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()


class RappiCrawler:
    def __init__(self) -> None:
        self.df_market = pd.DataFrame()
        self.market_dict = MARKETS
        self.market_headers = {
            market_id: CATEGORY_HEADER.copy() for market_id in self.market_dict.keys()
        }
        for market_id, market_value in self.market_headers.items():
            market_value["Referer"] = PRODUCT_HEADER_REFERER.format(market_id)

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

    def extract_market_subcategories(self, market_id, market_cat_id, market_cat_url):
        current_attempt = 0
        is_in_progress = True
        current_header = self.market_headers[market_id]
        while is_in_progress and current_attempt < MAX_ATTEMPTS:
            try:
                response = extract_information(market_cat_url, current_header)
                if "fallback" not in response["pageProps"]:
                    header_by_category = current_header.copy()
                    header_by_category["Referer"] = (
                        current_header["Referer"] + "/" + market_cat_id
                    )
                    current_header = header_by_category
                    current_attempt += 1
                    sleep(1)
                else:
                    is_in_progress = False
            except JSONDecodeError:
                current_attempt += 1
        try:
            subcategories = response["pageProps"]["fallback"][
                f"storefront/{market_id}/{market_cat_id}"
            ]["sub_aisles_response_extras"]["aisle"]["categories"]
        except Exception as e:
            print(response)

            raise Exception(e)

        return list(
            THREAD.map(
                lambda x: {
                    "Market_cat_url": market_cat_url,
                    "Market_subcat_id": x["id"],
                    "Market_subcat_name": x["name"],
                    "Market_count": x["product_count"],
                },
                subcategories,
            )
        )

    def format_market_categories_url(self, market_id, market_dict):
        market_products_url = MARKET_CATEGORY_URL_API.format(market_id)
        return list(
            THREAD.map(
                lambda x: {
                    "Market_id": market_id,
                    "Market_name": market_dict["market_name"],
                    "Market_cat_number": x["resource"]["id"],
                    "Market_cat_id": x["resource"]["friendly_url"],
                    "Market_cat_name": x["resource"]["name"],
                    "Market_cat_url": market_products_url
                    + MARKET_CATEGORY_ENDPOINT.format(x["resource"]["friendly_url"]),
                },
                market_dict["category_list"],
            )
        )

    def extract(self):
        market_info_url = dict(
            ChainMap(
                *list(
                    THREAD.map(self.extract_market_categories, self.market_dict.keys())
                )
            )
        )
        market_cat_info_list = []
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.format_market_categories_url, market_id, market_info
                )
                for market_id, market_info in market_info_url.items()
            ]
            for market_future in as_completed(market_futures):
                market_cat_info_list.extend(market_future.result())

        self.df_market = pd.DataFrame(market_cat_info_list)

        market_subcat_info_list = []
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.extract_market_subcategories,
                    market_row.Market_id,
                    market_row.Market_cat_id,
                    market_row.Market_cat_url,
                )
                for market_row in self.df_market.itertuples()
            ]
            for market_future in as_completed(market_futures):
                market_subcat_info_list.extend(market_future.result())
        self.df_market = pd.merge(
            self.df_market,
            pd.DataFrame(market_subcat_info_list),
            "left",
            "Market_cat_url",
        )
        self.df_market["Market_cat_number"] = self.df_market[
            "Market_cat_number"
        ].astype(str)
        self.df_market["Market_subcat_id"] = self.df_market["Market_subcat_id"].astype(
            str
        )


class RappiScraper:
    def __init__(self, path, market_cat_data):
        self.path = path
        self.market_cat_data = market_cat_data
        self.market_products_header = MARKET_PRODUCTS_HEADER
        self.variables = {market_id: PRODUCTS_VARIABLES.copy() for market_id in MARKETS}
        for market_id, market_value in self.variables.items():
            market_value["state"]["lat"] = MARKET_INFO_DICT[market_id]["lat"]
            market_value["state"]["lng"] = MARKET_INFO_DICT[market_id]["lng"]
            market_value["state"]["store_type"] = MARKET_INFO_DICT[market_id][
                "store_type"
            ]
            market_value["stores"] = MARKET_INFO_DICT[market_id]["stores"]
        self.data = None

    def set_request_headers(self):
        RAPPI_ACCESS_HEADER["x-guest-api-key"] = extract_information(
            API_URL_GUEST_PASSPORT, RAPPI_ACCESS_HEADER
        )["token"]
        user_credentials = requests.post(
            API_URL_GUEST, headers=RAPPI_ACCESS_HEADER
        ).json()
        self.market_products_header["authorization"] = (
            user_credentials["token_type"] + " " + user_credentials["access_token"]
        )
        self.market_products_header["app-version"] = "web_v1.216.6"

    def extract_market_subcategories_info(self, market_id, category_id, subcategory_id):
        current_variable = self.variables[market_id].copy()
        current_variable["state"]["parent_id"] = category_id
        current_variable["state"]["aisle_id"] = subcategory_id
        current_attempt = 0
        while current_attempt < MAX_ATTEMPTS:
            try:
                response = requests.post(
                    MARKET_PRODUCTS_URL_API,
                    headers=self.market_products_header,
                    json=current_variable,
                ).json()
            except JSONDecodeError:
                print(self.market_products_header)
                current_attempt += 1
            else:
                break
        return {
            "Market_id": market_id,
            "Market_cat_number": category_id,
            "Market_subcat_id": subcategory_id,
            "data": response["data"]["components"],
        }

    def extract_market_products(self, market_subcat_info):
        subcat_id = market_subcat_info["Market_subcat_id"]
        cat_id = market_subcat_info["Market_cat_number"]
        market_id = market_subcat_info["Market_id"]
        return list(
            itertools.chain.from_iterable(
                THREAD.map(
                    lambda x: [
                        {
                            "Market_id": market_id,
                            "Market_cat_number": cat_id,
                            "Market_subcat_id": subcat_id,
                            "Product_name": product["name"],
                            "Product_price": product["price"],
                            "Product_description": product["description"],
                            "Product_unit_type": product["unit_type"],
                            "Product_quantity": product["quantity"],
                            "Product_type": product["product_type"],
                            "Product_is_available": product["in_stock"],
                            "scrape_timestamp": str(pd.Timestamp.now()),
                        }
                        for product in x["resource"]["products"]
                    ],
                    market_subcat_info["data"],
                )
            )
        )

    def extract(self):
        self.set_request_headers()
        market_subcategories_list = []

        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(
                    self.extract_market_subcategories_info,
                    market_row.Market_id,
                    market_row.Market_cat_number,
                    market_row.Market_subcat_id,
                )
                for market_row in self.market_cat_data.itertuples()
            ]
            for market_future in as_completed(market_futures):
                market_subcategories_list.append(market_future.result())

        list_products = []
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            market_futures = [
                executor.submit(self.extract_market_products, market_subcat_info)
                for market_subcat_info in market_subcategories_list
            ]
            for market_future in as_completed(market_futures):
                list_products.extend(market_future.result())
        self.data = pd.DataFrame(list_products)

    def process_data(self):
        self.data = pd.merge(
            self.market_cat_data,
            self.data,
            "left",
            ["Market_id", "Market_cat_number", "Market_subcat_id"],
        )
        self.data = self.data.drop(["Market_id", "Market_cat_number", "Market_cat_id", "Market_cat_url", "Market_subcat_id"], axis=1)
        self.data["Product_name"] = self.data["Product_name"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )
        self.data["Product_description"] = self.data["Product_description"].replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True
        )

    def save_data(self):
        if len(self.data) > 0:
            if not path.exists(DATA_BASE_PATH):
                makedirs(DATA_BASE_PATH)
            self.data.to_csv(self.path, sep=",", index=False)

    def run(self):
        self.extract()
        self.process_data()
        self.save_data()


def main():
    crawler = RappiCrawler()
    crawler.extract()
    scraper = RappiScraper(
        path.join(
            DATA_BASE_PATH, "Rappi_" + pd.Timestamp("today").strftime("%d%m%Y") + ".csv"
        ),
        crawler.df_market,
    )
    scraper.run()


if __name__ == "__main__":
    main()
