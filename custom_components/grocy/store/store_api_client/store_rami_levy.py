'''Rami Levy Israel online store'''

import logging

from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from .utils import parse_int, parse_float

from .store_api_client import StoreApiClient, ProductData

_LOGGER = logging.getLogger(__name__)


class RamiLevyStoreApiClient(StoreApiClient):
    """Rami levy online store client"""
    name = 'Rami Levy'

    def __init__(self):
        super().__init__(RamiLevyStoreApiClient.name, 'www.rami-levy.co.il')
        self._store_id = 331
        self._token = None

    def login(self, username, password):
        _LOGGER.debug(f"Login to store {self.name}")
        self._session = requests.Session()
        data = {
            "username": username,
            "password": password
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8'
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/auth/login')
        response = self._session.post(req_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        self._token = response.json()['user']['token']

    def logout(self):
        _LOGGER.debug(f"Store logout")
        self._session = None
        self._token = None
        pass

    def add_to_cart(self, items):
        _LOGGER.debug(f"Add to cart")
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            # 'Content-Length': '0',
            'EcomToken': self._token
        }
        # Convert items to store format
        data = {
            "store": self._store_id,
            "items": list(map(lambda i: {"C": i["id"], "Quantity": str(i['quantity'])}, items))
        }
        req_url = urljoin('https://api-prod.rami-levy.co.il', 'api/v1/cart/add-line-to-cart')
        response = self._session.post(req_url, headers=headers, data=json.dumps(data))
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
        response.raise_for_status()

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