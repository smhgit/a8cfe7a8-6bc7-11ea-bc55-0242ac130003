import logging
import requests

from datetime import datetime
from typing import List
from urllib.parse import urljoin

from .utils import parse_date, parse_int, parse_float

DEFAULT_PORT_NUMBER=9192

_LOGGER = logging.getLogger(__name__)
    

class ShoppingListItem(object):
    def __init__(self, parsed_json):
        self._id = parse_int(parsed_json.get('id'))
        self._product_id = parse_int(parsed_json.get('product_id', None))
        self._note = parsed_json.get('note',None)
        self._amount = parse_float(parsed_json.get('amount'),0)
        self._row_created_timestamp = parse_date(parsed_json.get('row_created_timestamp', None))
        self._shopping_list_id = parse_int(parsed_json.get('shopping_list_id'))
        self._done = parse_int(parsed_json.get('done'))

    @property
    def id(self) -> int:
        return self._id
    
    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def note(self) -> str:
        return self._note

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def shopping_list_id(self) -> int:
        return self._shopping_list_id

    @property
    def done(self) -> float:
        return self._done


class GrocyObject(object):
    def __init__(self, parsed_json):
        self._id = parse_int(parsed_json.get('id'))
        self._name = parsed_json.get('name')
        self._description = parsed_json.get('description')
        self._row_created_timestamp = parse_date(parsed_json.get('row_created_timestamp', None))

    @property
    def id(self) -> int:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description

        
class ProductData(GrocyObject):
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self._location_id = parse_int(parsed_json.get('location_id', None))
        self._product_group_id = parse_int(parsed_json.get('product_group_id', None))
        self._qu_id_stock = parse_int(parsed_json.get('qu_id_stock', None))
        self._qu_id_purchase = parse_int(parsed_json.get('qu_id_purchase', None))
        self._qu_factor_purchase_to_stock = parse_float(parsed_json.get('qu_factor_purchase_to_stock', None))
        self._picture_file_name = parsed_json.get('picture_file_name', None)
        self._allow_partial_units_in_stock = bool(parsed_json.get('allow_partial_units_in_stock', None) == "true")
        self._min_stock_amount = parse_int(parsed_json.get('min_stock_amount', None), 0)
        self._default_best_before_days = parse_int(parsed_json.get('default_best_before_days', None))
        self._userfields = {}

        barcodes_raw = parsed_json.get('barcode', "")
        if barcodes_raw is None:
            self._barcodes = None
        else:
            self._barcodes = barcodes_raw.split(",")

    @property
    def product_group_id(self) -> int:
        return self._product_group_id

    @property
    def location_id(self) -> int:
        return self._location_id

    @property
    def qu_id_purchase(self) -> int:
        return self._qu_id_purchase

    @property
    def picture_file_name(self) -> str:
        return self._picture_file_name

    @property
    def barcodes(self) -> List[str]:
        return self._barcodes

    @property
    def userfields(self):
        return self._userfields

    @userfields.setter
    def userfields(self, value):
        self._userfields = value

    @property
    def price(self) -> float:
        return parse_float(self._userfields['price'])

    @property
    def store(self) -> str:
        return self._userfields['store']


class ShoppingList(GrocyObject):
    def __init__(self, parsed_json):
        super().__init__(parsed_json)


class LocationData(GrocyObject):
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self._is_freezer = parsed_json.get('is_freezer')

        
class ProductGroupData(GrocyObject):
    def __init__(self, parsed_json):
        super().__init__(parsed_json)


class QuantityUnitData(GrocyObject):
    def __init__(self, parsed_json):
        super().__init__(parsed_json)
        self._name_plural = parsed_json.get('name_plural')


class ProductDetailsResponse(object):
    def __init__(self, parsed_json):
        self._last_purchased = parse_date(parsed_json.get('last_purchased'))
        self._last_used = parse_date(parsed_json.get('last_used'))
        self._stock_amount = parse_int(parsed_json.get('stock_amount'))
        self._stock_amount_opened = parse_int(parsed_json.get('stock_amount_opened'))
        self._next_best_before_date = parse_date(parsed_json.get('next_best_before_date'))
        self._last_price = parse_float(parsed_json.get('last_price'))

        self._product = ProductData(parsed_json.get('product'))

        self._quantity_unit_purchase = QuantityUnitData(parsed_json.get('quantity_unit_purchase'))
        self._quantity_unit_stock = QuantityUnitData(parsed_json.get('quantity_unit_stock'))

        self._location = LocationData(parsed_json.get('location'))

    @property
    def last_purchased(self) -> datetime:
        return self._last_purchased

    @property
    def last_used(self) -> datetime:
        return self._last_used

    @property
    def stock_amount(self) -> int:
        return self._stock_amount

    @property
    def stock_amount_opened(self) -> int:
        return self._stock_amount_opened

    @property
    def next_best_before_date(self) -> datetime:
        return self._next_best_before_date

    @property
    def last_price(self) -> float:
        return self._last_price

    @property
    def product(self) -> ProductData:
        return self._product


class GrocyApiClient(object):
    def __init__(self, base_url, api_key, port: int = DEFAULT_PORT_NUMBER, verify_ssl = True):
        self._base_url = '{}:{}/api/'.format(base_url, port)
        self._api_key = api_key
        self._verify_ssl = verify_ssl
        if self._api_key == "demo_mode":
            self._headers = { "accept": "application/json" }
        else:
            self._headers = {
                "accept": "application/json",
                "GROCY-API-KEY": api_key
            }

    def _do_get_request(self, end_url: str):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.get(req_url, verify=self._verify_ssl, headers=self._headers)
        _LOGGER.debug(f"GET {req_url} {resp.status_code}")
        resp.raise_for_status()
        if len(resp.content) > 0:
            return resp.json()

    def _do_post_request(self, end_url: str, data):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.post(req_url, verify=self._verify_ssl, headers=self._headers, data=data)
        _LOGGER.debug(f"POST {req_url} {resp.status_code}")
        resp.raise_for_status()
        if len(resp.content) > 0:
            return resp.json()

    def _do_put_request(self, end_url: str, data):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.put(req_url, verify=self._verify_ssl, headers=self._headers, data=data)
        _LOGGER.debug(f"PUT {req_url} {resp.status_code}")
        resp.raise_for_status()
        if len(resp.content) > 0:
            return resp.json()

    def _do_delete_request(self, end_url: str):
        req_url = urljoin(self._base_url, end_url)
        resp = requests.delete(req_url, verify=self._verify_ssl, headers=self._headers)
        _LOGGER.debug(f"DELETE {req_url} {resp.status_code}")
        resp.raise_for_status()

    def add_product(self, id, name, barcode, description, product_group_id,
                    qu_id_purchase, location_id, picture):
        data = {
            "id": id,
            "name": name,
            "qu_id_purchase": qu_id_purchase,
            "barcode": barcode,
            "product_group_id": product_group_id,
            "description": description,
            "qu_id_stock": qu_id_purchase,
            "location_id": location_id,
            "qu_factor_purchase_to_stock": "1.0",
            "min_stock_amount": "1",
            "default_best_before_days": "0",
            "picture_file_name": picture,
            "default_best_before_days_after_open": "0",
            "allow_partial_units_in_stock": "0",
            "enable_tare_weight_handling": "0",
            "tare_weight": "0.0",
            "not_check_stock_fulfillment_for_recipes": "0"
        }
        self._do_post_request("objects/products", data=data)

    def update_product(self, id, name = None, barcode = None, description = None,
                       product_group_id = None, qu_id_purchase = None, location_id = None,
                       picture = None):
        data = {}
        if name: data['name'] = name
        if barcode: data['barcode'] = barcode
        if description: data['description'] = description
        if product_group_id: data['product_group_id'] = product_group_id
        if location_id: data['location_id'] = location_id
        if picture: data['picture'] = picture
        self._do_put_request(f"objects/products/{id}", data=data)        

    def add_product_group(self, id, name):
        data = {
            "id": id,
            "name": name
        }
        self._do_post_request("objects/product_groups", data=data)

    def remove_objects_products(self, id):
        self._do_delete_request(f"objects/products/{id}")

    def add_location(self, id, name):
        data = {
            "id": id,
            "name": name
        }
        self._do_post_request("objects/locations", data=data)

    def add_quantity_unit(self, id, name):
        data = {
            "id": id,
            "name": name
        }
        self._do_post_request("objects/quantity_units", data=data)

    def add_shopping_list(self, id, name):
        data = {
            "id": id,
            "name": name
        }
        self._do_post_request("objects/shopping_lists", data=data)

    def get_info(self):
        return self._do_get_request("system/info")

    def get_locations(self) -> List[LocationData]:
        parsed_json = self._do_get_request("objects/locations")
        return [LocationData(response) for response in parsed_json]

    def get_quantity_units(self) -> List[QuantityUnitData]:
        parsed_json = self._do_get_request("objects/quantity_units")
        return [QuantityUnitData(response) for response in parsed_json]

    def get_shopping_lists(self) -> List[ShoppingList]:
        parsed_json = self._do_get_request("objects/shopping_lists")
        return [ShoppingList(response) for response in parsed_json]

    def get_products(self) -> List[ProductData]:
        parsed_json = self._do_get_request("objects/products")
        return [ProductData(response) for response in parsed_json]

    def get_product_groups(self) -> List[ProductGroupData]:
        parsed_json = self._do_get_request("objects/product_groups")
        return [ProductGroupData(response) for response in parsed_json]

    def get_product_by_barcode(self, barcode):
        parsed_json = self._do_get_request(f"stock/products/by-barcode/{barcode}")
        return ProductData(parsed_json['product'])

    def get_shopping_list(self, shopping_list_id) -> List[ShoppingListItem]:
        shopping_list_items = []
        parsed_json = self._do_get_request("objects/shopping_list")
        for response in parsed_json:
            if response['shopping_list_id'] == str(shopping_list_id) or not shopping_list_id:
                shopping_list_items.append(ShoppingListItem(response))
        return shopping_list_items

    def add_product_to_shopping_list(self, product_id: int, shopping_list_id: int = 1, amount: int = 1):
        data = {
            "product_id": product_id,
            "list_id": shopping_list_id,
            "product_amount": amount
        }
        self._do_post_request("stock/shoppinglist/add-product", data)
            
    def remove_product_in_shopping_list(self, product_id: int, shopping_list_id: int = 1, amount: int = 1):
        data = {
            "product_id": product_id,
            "list_id": shopping_list_id,
            "product_amount": amount
        }
        self._do_post_request("stock/shoppinglist/remove-product", data)

    def clear_shopping_list(self, shopping_list_id: int = 1):
        data = {
            "list_id": shopping_list_id
        }
        self._do_post_request("stock/shoppinglist/clear", data=data)

    def complete_product_in_shopping_list(self, id: int, complete: int = 1):
        data = {
            "done": complete
        }
        self._do_put_request(f"objects/shopping_list/{id}", data=data)
        
    def set_userfield(self, entity: str, object_id: int, key: str, value):
        data = {
            key: value
        }
        self.set_userfields(entity, object_id, data)

    def get_userfields(self, entity: str, object_id: int):
        return self._do_get_request(f"userfields/{entity}/{object_id}")

    def set_userfields(self, entity: str, object_id: int, data):
        self._do_put_request(f"userfields/{entity}/{object_id}", data)

    def get_last_db_changed(self):
        parsed_json = self._do_get_request("system/db-changed-time")
        last_change_timestamp = parse_date(parsed_json.get('changed_time'))
        return last_change_timestamp