import logging
import requests

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

    def get(self, req_url):
        resp = requests.get(req_url, verify=self._verify_ssl, headers=self._headers)
        _LOGGER.debug("GET {} {}".format(req_url, resp.status_code))
        return resp

    def post(self, req_url, data):
        resp = requests.post(req_url, verify=self._verify_ssl, headers=self._headers, data=data)
        _LOGGER.debug("POST {} {}".format(req_url, resp.status_code))
        return resp

    def put(self, req_url, data):
        resp = requests.put(req_url, verify=self._verify_ssl, headers=self._headers, data=data)
        _LOGGER.debug("PUT {} {}".format(req_url, resp.status_code))
        return resp

    def delete(self, req_url):
        resp = requests.delete(req_url, verify=self._verify_ssl, headers=self._headers)
        _LOGGER.debug("DELETE {} {}".format(req_url, resp.status_code))
        return resp

    def add_product(self, id, name, barcode, description, product_group_id,
                    qu_id_purchase, location_id, picture):
        req_url = urljoin(self._base_url, "objects/products")
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
        return self.post(req_url, data=data)

    def update_product(self, id, name = None, barcode = None, description = None,
                       product_group_id = None, qu_id_purchase = None, location_id = None,
                       picture = None):
        req_url = urljoin(urljoin(self._base_url, "objects/products/"), str(id))
        data = {}
        if name: data['name'] = name
        if barcode: data['barcode'] = barcode
        if description: data['description'] = description
        if product_group_id: data['product_group_id'] = product_group_id
        if location_id: data['location_id'] = location
        if picture: data['picture'] = picture
        return self.put(req_url, data=data)        

    def add_product_group(self, id, name):
        req_url = urljoin(self._base_url, "objects/product_groups")
        data = {
            "id": id,
            "name": name
        }
        return self.post(req_url, data=data)

    def remove_objects_products(self, id):
        req_url = urljoin(urljoin(self._base_url, "objects/products/"), str(id))
        return self.delete(req_url)

    def add_location(self, id, name):
        req_url = urljoin(self._base_url, "objects/locations")
        data = {
            "id": id,
            "name": name
        }
        return self.post(req_url, data=data)

    def add_quantity_unit(self, id, name):
        req_url = urljoin(self._base_url, "objects/quantity_units")
        data = {
            "id": id,
            "name": name
        }
        return self.post(req_url, data=data)

    def add_shopping_list(self, id, name):
        req_url = urljoin(self._base_url, "objects/shopping_lists")
        data = {
            "id": id,
            "name": name
        }
        return self.post(req_url, data=data)

    def get_info(self):
        req_url = urljoin(self._base_url, "system/info")
        return self.get(req_url)

    def get_locations(self) -> List[LocationData]:
        req_url = urljoin(self._base_url, "objects/locations")
        resp = self.get(req_url)
        if resp.status_code != 200 or not resp.text:
            return
        parsed_json = resp.json()
        return [LocationData(response) for response in parsed_json]

    def get_quantity_units(self) -> List[QuantityUnitData]:
        req_url = urljoin(self._base_url, "objects/quantity_units")
        resp = self.get(req_url)
        if resp.status_code != 200 or not resp.text:
            return
        parsed_json = resp.json()
        return [QuantityUnitData(response) for response in parsed_json]

    def get_shopping_lists(self) -> List[ShoppingList]:
        req_url = urljoin(self._base_url, "objects/shopping_lists")
        resp = self.get(req_url)
        if resp.status_code != 200 or not resp.text:
            return
        parsed_json = resp.json()
        return [ShoppingList(response) for response in parsed_json]

    def get_products(self) -> List[ProductData]:
        req_url = urljoin(self._base_url, "objects/products")
        resp = self.get(req_url)
        if resp.status_code != 200 or not resp.text:
            return
        parsed_json = resp.json()
        return [ProductData(response) for response in parsed_json]

    def get_product_groups(self) -> List[ProductGroupData]:
        req_url = urljoin(self._base_url, "objects/product_groups")
        resp = self.get(req_url)
        if resp.status_code != 200 or not resp.text:
            return
        parsed_json = resp.json()
        return [ProductGroupData(response) for response in parsed_json]

    def get_product_by_barcode(self, barcode):
        req_url = urljoin(urljoin(self._base_url, "stock/products/by-barcode/"), barcode)
        resp = self.get(req_url)
        if resp.status_code != 200:
            return
        parsed_json = resp.json()
        return ProductData(parsed_json['product'])

    def get_shopping_list(self, shopping_list_id) -> List[ShoppingListItem]:
        shopping_list_items = []
        req_url = urljoin(self._base_url, "objects/shopping_list")
        resp = self.get(req_url)
        if resp.status_code != 200:
            return None
        parsed_json = resp.json()
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
        req_url = urljoin(self._base_url, "stock/shoppinglist/add-product")
        return self.post(req_url, data)
            
    def remove_product_in_shopping_list(self, product_id: int, shopping_list_id: int = 1, amount: int = 1):
        data = {
            "product_id": product_id,
            "list_id": shopping_list_id,
            "product_amount": amount
        }
        req_url = urljoin(self._base_url, "stock/shoppinglist/remove-product")
        return self.post(req_url, data)

    def clear_shopping_list(self, shopping_list_id: int = 1):
        data = {
            "list_id": shopping_list_id
        }
        req_url = urljoin(self._base_url, "stock/shoppinglist/clear")
        return self.post(req_url, data=data)

    def complete_product_in_shopping_list(self, id: int, complete: int = 1):
        data = {
            "done": complete
        }
        req_url = urljoin(urljoin(self._base_url, "objects/shopping_list/"), str(id))
        return self.put(req_url, data=data)

    def get_last_db_changed(self):
        req_url = urljoin(self._base_url, "system/db-changed-time")
        resp = self.get(req_url)
        last_change_timestamp = parse_date(resp.json().get('changed_time'))
        return last_change_timestamp