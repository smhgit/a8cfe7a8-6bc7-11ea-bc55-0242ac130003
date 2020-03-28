import logging
import requests

from abc import ABC, abstractmethod

from urllib.parse import urljoin

from .utils import parse_int, parse_float

_LOGGER = logging.getLogger(__name__)


class ProductData(object):
    """Store product data"""

    def __init__(self, data):
        self._store = data['store']
        self._barcode = data['barcode']
        self._id = data['id']
        self._name = data['name']
        self._price = data['price']
        self._product_group_id = data['group_id']
        self._product_group_name = data['group_name']
        self._picture = data['picture']

    @property
    def store(self) -> int:
        return self._store

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def barcode(self) -> str:
        return self._barcode

    @property
    def product_group_id(self) -> int:
        return self._product_group_id

    @property
    def product_group_name(self) -> int:
        return self._product_group_name

    @property
    def qu_id_purchase(self) -> str:
        return 1

    @property
    def picture(self) -> str:
        return self._picture


class StoreApiClient(ABC):
    """Online store api client interface"""

    @property
    def name(self):
        return self._name

    def _do_get_request(self, end_url, timeout: int = 20, verify_ssl: bool = True, headers = { "accept": "application/json" }):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.get(req_url, verify=verify_ssl, headers=headers, timeout=timeout)
        _LOGGER.debug(f"GET {req_url} {resp.status_code}")
        resp.raise_for_status()
        if len(resp.content) > 0:
            return resp.json()


class NoneStoreApiClient(StoreApiClient):
    """Rami levy online store cline"""
    name = 'None'

    def __init__(self):
        self._name = NoneStoreApiClient.name

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        return None


class MySupermarketStoreApiClient(StoreApiClient):
    """MySupermarket online store client"""
    name = 'My Supermarket'

    def __init__(self):
        self._name = MySupermarketStoreApiClient.name
        self._base_url = 'https://chp.co.il/'

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        parsed_json = self._do_get_request(f"autocompletion/product_extended?term={barcode}")
        if parsed_json:
            for item in parsed_json:
                data = {
                    "store": self._name,
                    "barcode": item['id'].split('_')[1],
                    "id": parse_int(item['id'].split('_')[1]),
                    "name": item['value'],
                    "group_id": 0,
                    "price": 0.0,
                    "group_name": "Others",
                    "picture": None
                }
                if data['barcode'] == barcode:
                    return ProductData(item)


class ShufersalStoreApiClient(StoreApiClient):
    """Shufersal online store client"""
    name = 'Shufersal'

    def __init__(self):
        self._name = ShufersalStoreApiClient.name
        self._base_url = 'https://www.shufersal.co.il'

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        limit = 10
        parsed_json = self._do_get_request(f"online/he/search/results?q={barcode}%3Arelevance&limit={limit}")
        if parsed_json:
            for item in parsed_json.get('results', []):
                data = {
                    "store": self._name,
                    "barcode": item['sku'],
                    "id": parse_int(item.get('sku')),
                    "name": item['name'],
                    "group_id": 0,
                    "price": 0.0,
                    "group_name": "Others",
                    "picture": item['images'][0]['url']
                }
                if data['barcode'] == barcode:
                    return ProductData(item)


class RamiLevyStoreApiClient(StoreApiClient):
    """Rami levy online store client"""
    name = 'Rami Levy'

    def __init__(self):
        self._name = RamiLevyStoreApiClient.name
        self._store_id = 331
        self._base_url = 'https://www.rami-levy.co.il'

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        index = 0
        total = 1
        while index < total:
            parsed_json = self._do_get_request(f"api/search?store={self._store_id}&q={barcode}&from={index}")
            if parsed_json:
                # Search for barcode in page
                for item in parsed_json['data']:
                    data = {
                        "store": self._name,
                        "barcode": str(item['barcode']),
                        "id": parse_int(str(item['barcode'])),
                        "name": item['name'],
                        "group_id": item['group_id'],
                        "price": parse_float(item['price']['price']),
                        "group_name": "Others",
                        "picture": "https://static.rami-levy.co.il/storage/images/{}/{}/small.jpg".format(
                                        item['barcode'], item['id'])
                    }
                    if data['barcode'] == barcode:
                        return ProductData(data)
                # Next page
                index += len(parsed_json['data'])
                total = parse_int(parsed_json.get('total'))
            else:
                break


def get_store_api_client(store_name: str = 'default'):
    if store_name.lower() == RamiLevyStoreApiClient.name.lower():
        return RamiLevyStoreApiClient()
    elif store_name.lower() == ShufersalStoreApiClient.name.lower():
        return ShufersalStoreApiClient()
    elif store_name.lower() == MySupermarketStoreApiClient.name.lower():
        return MySupermarketStoreApiClient()
    return NoneStoreApiClient()