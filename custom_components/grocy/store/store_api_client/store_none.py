'''None store'''

from .store_api_client import StoreApiClient, ProductData

class NoneStoreApiClient(StoreApiClient):
    """Rami levy online store cline"""
    name = 'None'

    def __init__(self):
        super().__init__(NoneStoreApiClient.name, "")

    def get_product_by_barcode(self, barcode: str) -> ProductData:
        return None