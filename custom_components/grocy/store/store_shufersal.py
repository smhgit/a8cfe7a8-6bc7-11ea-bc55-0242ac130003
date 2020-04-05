'''Shufersal Levy Israel online store'''

import logging

from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from .store_api_client import StoreApiClient, ProductData

_LOGGER = logging.getLogger(__name__)


class ShufersalStoreApiClient(StoreApiClient):
    """Shufersal online store client"""
    name = 'Shufersal'

    def __init__(self, username: str = None, password: str = None):
        super().__init__(ShufersalStoreApiClient.name, 'www.shufersal.co.il', username, password)

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