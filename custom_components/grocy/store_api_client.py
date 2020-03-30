import json
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
        self._name = data['name']
        self._price = data['price']
        self._product_group_id = data['group_id']
        self._product_group_name = data['group_name']
        self._picture = data['picture']
        self._metadata = data['metadata']

    @property
    def id(self) -> int:
        return int(self._barcode)

    @property
    def store(self) -> int:
        return self._store

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

    @property
    def metadata(self) -> str:
        '''metaadata used by store api client'''
        return self._metadata


class StoreApiClient(ABC):
    """Online store api client interface"""

    def __init__(self, name, base_url):
        self._name = name
        self._base_url = f"https://{base_url}"

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

    def _do_post_request(self, end_url, data, verify_ssl: bool = True, headers = { "accept": "application/json" }):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.post(req_url, verify=verify_ssl, headers=headers, data=data)
        _LOGGER.debug(f"POST {req_url} {resp.status_code}")
        resp.raise_for_status()
        if len(resp.content) > 0:
            return resp.json()

    def login(self, username, password):
        pass

    def get_product_by_barcode(self, barcode: str):
        pass


class NoneStoreApiClient(StoreApiClient):
    """Rami levy online store cline"""
    name = 'None'

    def __init__(self):
        super().__init__(NoneStoreApiClient.name, "")

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        return None


class MySupermarketStoreApiClient(StoreApiClient):
    """MySupermarket online store client"""
    name = 'My Supermarket'

    def __init__(self):
        super().__init__(MySupermarketStoreApiClient.name, 'chp.co.il/')

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        parsed_json = self._do_get_request(f"autocompletion/product_extended?term={barcode}")
        if parsed_json:
            for item in parsed_json:
                data = {
                    "store": self._name,
                    "barcode": item['id'].split('_')[1],
                    "name": item['value'],
                    "group_id": 0,
                    "price": 0.0,
                    "group_name": "Others",
                    "picture": None,
                    "metadata": ""
                }
                if data['barcode'] == barcode:
                    return ProductData(item)


class ShufersalStoreApiClient(StoreApiClient):
    """Shufersal online store client"""
    name = 'Shufersal'

    def __init__(self):
        super().__init__(ShufersalStoreApiClient.name, 'www.shufersal.co.il')

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        limit = 10
        parsed_json = self._do_get_request(f"online/he/search/results?q={barcode}%3Arelevance&limit={limit}")
        if parsed_json:
            for item in parsed_json.get('results', []):
                data = {
                    "store": self._name,
                    "barcode": item['sku'],
                    "name": item['name'],
                    "group_id": 0,
                    "price": 0.0,
                    "group_name": "Others",
                    "picture": item['images'][0]['url'],
                    "metadata": ""
                }
                if data['barcode'] == barcode:
                    _LOGGER.debug(item)
                    return ProductData(item)


class RamiLevyStoreApiClient(StoreApiClient):
    """Rami levy online store client"""
    name = 'Rami Levy'

    def __init__(self):
        super().__init__(RamiLevyStoreApiClient.name, 'www.rami-levy.co.il')
        self._store_id = 331

    def login(self, username, password):
        pass

    def logout(self):
        pass

    def add_to_cart(self):
        # {"store":331,"items":[{"C":329258,"Quantity":"5.00"}]}
        pass

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
                        "name": item['name'],
                        "group_id": item['group_id'],
                        "price": parse_float(item['price']['price']),
                        "group_name": "Others",
                        "picture": "https://static.rami-levy.co.il/storage/images/{}/{}/small.jpg".format(
                                        item['barcode'], item['id']),
                        "metadata": json.dumps({'id': item['id']})
                    }
                    if data['barcode'] == barcode:
                        _LOGGER.debug(item)
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