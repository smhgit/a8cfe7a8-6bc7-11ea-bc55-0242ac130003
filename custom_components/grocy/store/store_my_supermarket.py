'''My Supermarket Israel online store'''

import logging

from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from .store_api_client import StoreApiClient, ProductData

_LOGGER = logging.getLogger(__name__)


class MySupermarketStoreApiClient(StoreApiClient):
    """MySupermarket online store client"""
    name = 'My Supermarket'

    def __init__(self, username: str = None, password: str = None):
        super().__init__(MySupermarketStoreApiClient.name, 'chp.co.il/', username, password)

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
