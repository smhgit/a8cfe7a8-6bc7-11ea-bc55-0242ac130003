"""Constants for grocy."""

VERSION = "0.0.22"

DOMAIN = "ha_grocy"
DOMAIN_DATA = "{}_data".format(DOMAIN)
DOMAIN_EVENT = "grocy_updated"

REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "sensor.py",
    ".translations/en.json"
]
ISSUE_URL = "https://github.com/custom-components/grocy/issues"
DOMAIN_SERVICE = "{}"

# Integration local data
DATA_GROCY = "grocy"
DATA_DATA = "data"
DATA_ENTITIES = "entities"

# Domain events
EVENT_ADDED_TO_LIST='added_to_list'
EVENT_SUBTRACT_FROM_LIST='subtract_from_list'
EVENT_PRODUCT_REMOVED='product_removed'
EVENT_PRODUCT_ADDED='product_added'
EVENT_GROCY_ERROR='error'

# Configuration
CONF_APIKEY = "apikey"
CONF_AMOUNT = "amount"
CONF_NAME = "name"
CONF_VALUE = "value"
CONF_SHOPPING_LIST_ID = 'shopping_list'
CONF_PRODUCT_DESCRIPTION = 'product_description'
CONF_PRODUCT_GROUP_ID = 'product_group_id'
CONF_PRODUCT_LOCATION_ID = 'product_location_id'
CONF_STORE = 'store'
CONF_BARCODE = 'barcode'
CONF_UNIT_OF_MEASUREMENT = 'unit_of_measurement'

# Defaults
DEFAULT_AMOUNT = 1
DEFAULT_STORE = ''
DEFAULT_SHOPPING_LIST_ID = 1
DEFAULT_PRODUCT_DESCRIPTION = ""

# Services
ADD_TO_LIST_SERVICE = DOMAIN_SERVICE.format('add_to_list')
SUBTRACT_FROM_LIST_SERVICE = DOMAIN_SERVICE.format('subtract_from_list')
ADD_PRODUCT_SERVICE = DOMAIN_SERVICE.format('add_product')
UPDATE_PRODUCT_SERVICE = DOMAIN_SERVICE.format('update_product')
REMOVE_PRODUCT_SERVICE = DOMAIN_SERVICE.format('remove_product')
SYNC_GROCY_SERVICE = DOMAIN_SERVICE.format('sync')

# Device classes
STOCK_NAME = "stock"
CHORES_NAME = "chores"
PRODUCTS_NAME = "products"
SHOPPING_LIST_NAME = "shopping_list"
SHOPPING_LISTS_NAME = "shopping_lists"
LOCATIONS_NAME = "locations"
QUANTITY_UNITS_NAME = "quantity_units"
PRODUCT_GROUPS_NAME = "product_groups"
