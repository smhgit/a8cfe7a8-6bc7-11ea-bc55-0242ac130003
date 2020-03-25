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

    @abstractmethod
    def get_product_by_barcode(self, barcode: str) -> ProductData:
        pass

    @property
    def name(self):
        return self._name

    def get(self, end_url, timeout: int = 20, verify_ssl: bool = True, headers = { "accept": "application/json" }):
        try:
            req_url = urljoin(self._base_url, end_url)
            resp = requests.get(req_url, verify=verify_ssl, headers=headers, timeout=timeout)
            _LOGGER.debug("GET {} {}".format(req_url, resp.status_code))
            resp.raise_for_status()
            return resp
        except requests.exceptions.ReadTimeout:
            _LOGGER.debug("GET {} timeout".format(req_url))
            return None
        except requests.exceptions.HTTPError:
            _LOGGER.debug('GET {} error: '.format(resp.status_code))
            return None


class ShufersalStoreApiClient(StoreApiClient):
    """Shufersal online store client"""
    name = 'Shufersal'

    def __init__(self):
        self._name = ShufersalStoreApiClient.name
        self._base_url = 'https://www.shufersal.co.il'

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        _LOGGER.debug('Store search product: ' + barcode)
        limit = 10
        resp = self.get("online/he/search/results?q={}%3Arelevance&limit={}".format(barcode, limit))
        if resp:
            parsed_json = resp.json()
            # Iterate all found products
            for item in parsed_json['results']:
                # Get product data
                product = ProductData(self.get_product_data(item))
                if product.barcode == barcode:
                    return product
        # failed to query store or product wasn't found
        return None

    def get_product_data(self, response):
        return {
            "store": self._name,
            "barcode": response['sku'],
            "id": parse_int(response.get('sku')),
            "name": response['name'],
            "group_id": 0,
            "price": 0.0,
            "group_name": "Others",
            "picture": response['images'][0]['url']
        }


class RamiLevyStoreApiClient(StoreApiClient):
    """Rami levy online store cline"""
    name = 'Rami Levy'

    def __init__(self):
        self._name = RamiLevyStoreApiClient.name
        self._store_id = 331
        self._base_url = 'https://www.rami-levy.co.il'

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        _LOGGER.debug('Store search product: ' + barcode)
        index = 0
        total = 1
        while index < total:
            resp = self.get("api/search?store={}&q={}&from={}".format(self._store_id, barcode, index))
            if resp:
                parsed_json = resp.json()
                # Search for barcode in page
                for item in parsed_json['data']:
                    # Get product data
                    product = ProductData(self.get_product_data(item))
                    if product.barcode == barcode:
                        return product
                # Next page
                index += len(parsed_json['data'])
                total = parse_int(parsed_json.get('total'))
            else:
                break
        # failed to query store or product wasn't found
        return None

    def get_product_data(self, response):
        return {
            "store": self._name,
            "barcode": str(response['barcode']),
            "id": response['id'],
            "name": response['name'],
            "group_id": response['group_id'],
            "price": parse_float(response['price']['price']),
            "group_name": "Others",
            "picture": "https://static.rami-levy.co.il/storage/images/{}/{}/small.jpg".format(
                            response['barcode'], response['id'])
        }


def get_store_api_client(store_name: str = 'default'):
    if store_name.lower() == RamiLevyStoreApiClient.name.lower():
        return RamiLevyStoreApiClient()
    elif store_name.lower() == ShufersalStoreApiClient.name.lower():
        return ShufersalStoreApiClient()
    return RamiLevyStoreApiClient()