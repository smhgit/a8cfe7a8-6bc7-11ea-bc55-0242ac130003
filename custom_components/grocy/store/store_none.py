'''None store'''

from .store_api_client import StoreApiClient, ProductData

class NoneStoreApiClient(StoreApiClient):
    """None store client"""
    name = 'None'

    def __init__(self, username: str = None, password: str = None):
        super().__init__(NoneStoreApiClient.name, "", username, password)

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        return None