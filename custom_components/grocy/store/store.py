'''Online grocery store'''

from .store_api_client import get_store_api_client


class Store:
    """Online store"""
    
    def __init__(self, store_name: str = 'default', username: str = None, password: str = None):
        self._username = username
        self._password = password
        self._client = get_store_api_client(store_name)

    @property
    def name(self):
        return self._client.name

    def get_product_by_barcode(self, barcode: str):
        return self._client.get_product_by_barcode(barcode)

    def login(self):
        self._client.login(self._username, self._password)

    def logout(self):
        self._client.logout()

    def add_to_cart(self, items):
        self._client.add_to_cart(items)

    def empty_cart(self):
        self._client.empty_cart()