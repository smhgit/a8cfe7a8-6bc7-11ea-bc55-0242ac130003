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
        _LOGGER.debug(f"POST {req_url} {response.status_code}")
        response.raise_for_status()
        self._token = response.json()['user']['token']

    def logout(self):
        '''Logout from online store'''
        self._session = None
        self._token = None

    def fill_cart(self, products):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Content-Length': '0',
            'EcomToken': self._token
        }
        # Convert items to store format
        data = {
            "store": self._store_id,
            "items": list(map(lambda i: {"C": i["id"], "Quantity": str(i['quantity'])}, products))
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/add-line-to-cart')
        response = self._session.post(req_url, headers=headers, data=json.dumps(data))
        _LOGGER.debug(f"POST {req_url} {data} {response.status_code}")
        response.raise_for_status()

    def empty_cart(self):
        _LOGGER.debug(f"Empty cart")
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Content-Length': '0',
            'EcomToken': self._token
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/delete-cart')
        response = self._session.post(req_url, headers=headers)
        _LOGGER.debug(f"POST {req_url} {response.status_code}")
        response.raise_for_status()