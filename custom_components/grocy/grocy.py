import logging

from typing import List

from .grocy_api_client import (DEFAULT_PORT_NUMBER, GrocyApiClient, ShoppingList,
                               LocationData, ProductData, LocationData, QuantityUnitData, ProductGroupData,
                               ShoppingListItem)

_LOGGER = logging.getLogger(__name__)
        

class ShoppingListProduct(object):
    def __init__(self, raw_shopping_list: ShoppingListItem):
        self._id = raw_shopping_list.id
        self._product_id = raw_shopping_list.product_id
        self._note = raw_shopping_list.note
        self._amount = raw_shopping_list.amount
        self._done = raw_shopping_list.done
        self._product = None
        self._shopping_list_id = raw_shopping_list.shopping_list_id
        
    def get_details(self, api_client: GrocyApiClient):
        if self._product_id:
            self._product = api_client.get_product(self._product_id).product
        
    @property
    def id(self) -> int:
        return self._id
        
    @property
    def product_id(self) -> int:
        return self._product_id
        
    @property
    def amount(self) -> int:
        return self._amount
        
    @property
    def note(self) -> str:
        return self._note
        
    @property
    def done(self) -> str:
        return self._done

    @property
    def shopping_list_id(self) -> int:
        return self._shopping_list_id

    # @property
    # def product(self) -> Product:
    #     if self._product_id is None:
    #         self.get_details()
    #     return self._product


class Grocy(object):
    def __init__(self, base_url, api_key, port: int = DEFAULT_PORT_NUMBER, verify_ssl = True):
        self._api_client = GrocyApiClient(base_url, api_key, port, verify_ssl)

    def is_connected(self):
        # ???
        return True

    def get_info(self):
        return self._api_client.get_info()

    def locations(self) -> List[LocationData]:
        return self._api_client.get_locations()

    def quantity_units(self) -> List[QuantityUnitData]:
        return self._api_client.get_quantity_units()

    def product_groups(self) -> List[ProductGroupData]:
        return self._api_client.get_product_groups()

    def get_products(self) -> List[ProductData]:
        return self._api_client.get_products()

    def add_product(self, id, name, barcode, description,
                    product_group_id, qu_id_purchase, location, picture):
        return self._api_client.add_product(id, name, barcode, description,
                                            product_group_id, qu_id_purchase, location, picture)

    def update_product(self, id, name = None, barcode = None, description = None,
                       product_group_id = None, qu_id_purchase = None, location = None,
                       picture = None):
        return self._api_client.update_product(id, name, barcode, description,
                                               product_group_id, qu_id_purchase, location, picture)

    def remove_product(self, id):
        return self._api_client.remove_objects_products(id)

    def add_product_group(self, id, name):
        return self._api_client.add_product_group(id, name)

    def add_location(self, id, name):
        return self._api_client.add_location(id, name)

    def add_quantity_unit(self, id, name):
        return self._api_client.add_quantity_unit(id, name)

    def add_shopping_list(self, id, name):
        return self._api_client.add_shopping_list(id, name)

    def get_product_by_barcode(self, barcode) -> ProductData:
        return self._api_client.get_product_by_barcode(barcode)

    def shopping_lists(self) -> List[ShoppingList]:
        return self._api_client.get_shopping_lists()

    def shopping_list(self, shopping_list_id: int = 1, get_details: bool = False) -> List[ShoppingListProduct]:
        raw_shoppinglist = self._api_client.get_shopping_list(shopping_list_id)
        if raw_shoppinglist is None:
            return
        shopping_list = [ShoppingListProduct(resp) for resp in raw_shoppinglist]
        if get_details:
            for item in shopping_list:
                item.get_details(self._api_client)
        return shopping_list

    def add_product_to_shopping_list(self, product_id: int, shopping_list_id: int = 1, amount: int = 1):
        return self._api_client.add_product_to_shopping_list(product_id, shopping_list_id, amount)
        
    def clear_shopping_list(self, shopping_list_id: int = 1):
        return self._api_client.clear_shopping_list(shopping_list_id)

    def remove_product_in_shopping_list(self, product_id: int, shopping_list_id: int = 1, amount: int = 1):
        return self._api_client.remove_product_in_shopping_list(product_id, shopping_list_id, amount)

    def complete_product_in_shopping_list(self, id: int, complete: int = 1):
        return self._api_client.complete_product_in_shopping_list(id, complete)

    def get_last_db_changed(self):
        return self._api_client.get_last_db_changed()