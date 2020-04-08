'''Rami Levy Israel online store'''

import json
import logging
import requests

from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from .utils import parse_int, parse_float

from .store_api_client import StoreApiClient, ProductData

_LOGGER = logging.getLogger(__name__)


class RamiLevyStoreApiClient(StoreApiClient):
    """Rami levy online store client"""
    name = 'Rami Levy'

    def __init__(self, username: str = None, password: str = None):
        super().__init__(RamiLevyStoreApiClient.name, 'www.rami-levy.co.il', username, password)
        self._store_id = 331
        self._token = None

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

    def login(self, username: str = None, password: str = None):
        '''Login to online store'''
        self._session = requests.Session()
        data = {
            "username": username or self._username,
            "password": password or self._password
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/auth/login')
        response = self._session.post(req_url, headers=headers, data=json.dumps(data))
        _LOGGER.debug(f"POST {req_url} {headers} {response.status_code}")
        response.raise_for_status()
        _LOGGER.debug(f"RESPONSE: {response.json()['user']}")
        self._token = response.json()['user']['token']

    def logout(self):
        '''Logout from online store'''
        self._session = None
        self._token = None

    def fill_cart(self, items):
        '''Fill online store with cart items'''
        data = json.dumps({
            "store": self._store_id,
            "items": items
        })
        headers = {
            'Origin': 'https://www.rami-levy.co.il',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'Locale': 'he',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Content-Length': str(len(data)),
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0',
            'ecomtoken': self._token
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/add-line-to-cart')
        response = self._session.post(req_url, headers=headers, data=data)
        _LOGGER.debug(f"POST {req_url} {headers} {data} {response.status_code}")
        response.raise_for_status()

    def get_cart(self):
        '''Get items from online store cart'''
        headers = {
            'Origin': 'https://www.rami-levy.co.il',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'Locale': 'he',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Content-Length': '0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0',
            'ecomtoken': self._token
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/get-cart')
        response = self._session.post(req_url, headers=headers)
        _LOGGER.debug(f"POST {req_url} {headers} {response.status_code}")
        response.raise_for_status()
        _LOGGER.debug(f"RESPONSE {json.loads(response.text)}")
        return json.loads(response.text)

    def clear_cart(self):
        '''Clear online store cart (empty cart by sending 0 quantity)'''
        cart = self.get_cart()
        for item in cart:
            item['Quantity'] = '0'
        self.fill_cart(cart)

    def empty_cart(self):
        '''Empty online store cart'''
        headers = {
            'Origin': 'https://www.rami-levy.co.il',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7',
            'Locale': 'he',
            'Content-Type': 'application/json;charset=UTF-8',
            'Content-Length': '0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0',
            'ecomtoken': self._token
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/delete-cart')
        response = self._session.post(req_url, headers=headers)
        _LOGGER.debug(f"POST {req_url} {headers} {response.status_code}")
        response.raise_for_status()

    def to_cart_item(self, product, quantity):
        '''Convert grocy product to online store cart item format'''
        meta = json.loads(product.userfields['metadata'])
        cart_item = {
            "C": meta['id'],
            "Quantity": str(quantity)
        }
        return cart_item