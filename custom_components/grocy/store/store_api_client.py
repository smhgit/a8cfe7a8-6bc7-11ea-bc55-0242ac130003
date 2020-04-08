import logging
import requests

from abc import ABC, abstractmethod

from urllib.parse import urljoin

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
        
    def __init__(self, name: str, base_url: str, username: str, password: str):
        '''Initialize online store client'''
        self._name = name
        self._base_url = f"https://{base_url}"
        self._session = None
        self._username = username
        self._password = password

    @property
    def name(self) -> str:
        '''Return online store name'''
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

    def get_product_by_barcode(self, barcode: str):
        '''Return store product by barcode'''
        pass

    def login(self, username: str, password: str):
        '''Login to online store'''
        raise Exception('online store cart not supported')

    def logout(self):
        '''Logout from online store'''
        raise Exception('online store cart not supported')

    def fill_cart(self, items):
        '''Fill online store cart with items'''
        raise Exception('online store cart not supported')

    def get_cart(self):
        '''Get online store cart items'''
        raise Exception('online store cart not supported')

    def clear_cart(self):
        ''''''
        raise Exception('online store cart not supported')

    def empty_cart(self):
        ''''''
        raise Exception('online store cart not supported')

    def to_cart_item(self, product, quantity):
        '''Convert grocy product to store cart item representation'''
        raise Exception('online store cart not supported')
