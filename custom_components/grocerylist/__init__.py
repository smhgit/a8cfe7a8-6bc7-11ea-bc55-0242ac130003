''' Grocy integration '''

import logging

from integrationhelper.const import CC_STARTUP_VERSION

from homeassistant.util import Throttle
from homeassistant.const import CONF_HOST

from .grocy import Grocy
from .services import setup_services
from .helpers import async_check_files

from .const import (DOMAIN, DOMAIN_DATA, REQUIRED_FILES, VERSION, ISSUE_URL,
                    CONF_APIKEY,
                    DATA_GROCY, DATA_DATA, DATA_ENTITIES,
                    PRODUCTS_NAME, SHOPPING_LISTS_NAME, SHOPPING_LIST_NAME, LOCATIONS_NAME,
                    QUANTITY_UNITS_NAME, PRODUCT_GROUPS_NAME)
from .schema import CONFIG_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )
    
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    # Check that all required files are present
    file_check = await async_check_files(hass)
    if not file_check:
        return False

    grocy = setup_grocy(conf)
    if not grocy:
        return False

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {
        DATA_GROCY: grocy,
        DATA_DATA: Data(hass, grocy),
        DATA_ENTITIES: Entities(hass)
    }

    setup_services(hass);

    # Initial objects upddate
    await hass.data[DOMAIN_DATA]['data'].async_update_data(None, True)

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config)
    )

    # Initialization was successful.
    return True


def setup_grocy(conf):
    # Get "global" configuration.
    grocy_host = conf.get(CONF_HOST)
    grocy_apikey = conf.get(CONF_APIKEY)

    # Extarct address and port
    host = "{}:{}".format(grocy_host.split(":")[0], grocy_host.split(":")[1])
    port = grocy_host.split(":")[2]

    # Configure the grocy client
    grocy = Grocy(host, grocy_apikey, port = port)
    if not grocy.is_connected():
        _LOGGER.error('Failed to connect to grocy, check apikey: ' + grocy_host)
        return None
    _LOGGER.debug('Connect to grocy: ' + grocy_host)

    # product_groups = {
    #     'Sweets': 1,
    #     'Bakery': 2,
    #     'Canned': 3,
    #     'Butchery': 4,
    #     'Fruits': 5,
    #     'Refrigerated': 6,
    #     'Beverages': 7,
    #     'Frozen': 8,
    #     'Grains & Pasta': 9,
    #     'Dairy': 10,
    #     'Fish': 12,
    #     'Personal hygiene': 13,
    #     'Vegetables': 14,
    #     'Others': 15
    # }
    # for name, id in product_groups.items():
    #     grocy.add_product_group(str(id), name)

    # locations = {
    #     'Pantry': 1,
    #     'Fridge': 2,
    #     'Freeze': 3,
    #     'Other': 4
    # }
    # for name, id in locations.items():
    #     grocy.add_location(str(id), name)

    # lists = {
    #     'Grocery List': 1
    # }
    # for name, id in lists.items():
    #     grocy.add_shopping_list(str(id), name)

    return grocy


class Data:
    """This helper class handle communication and stores the data in DOMAIN_DATA."""

    def __init__(self, hass, client):
        """Initialize the class."""
        self._hass = hass
        self._client = client
        self._sensor_types_dict = {
            PRODUCTS_NAME: self.async_update_products,
            SHOPPING_LIST_NAME: self.async_update_shopping_list,
            SHOPPING_LISTS_NAME: self.async_update_shopping_lists,
            LOCATIONS_NAME: self.async_update_locations,
            QUANTITY_UNITS_NAME: self.async_update_quantity_units,
            PRODUCT_GROUPS_NAME: self.async_update_product_groups
        }
        self._sensor_update_dict = {
            PRODUCTS_NAME : None,
            SHOPPING_LIST_NAME : None,
            SHOPPING_LISTS_NAME : None,
            LOCATIONS_NAME: None,
            QUANTITY_UNITS_NAME: None,
            PRODUCT_GROUPS_NAME: None
        }

    async def async_update_data(self, sensor_types = None, wait: bool = True, force: bool = False):
        """Update data."""
        sensor_types = sensor_types if sensor_types else [
            PRODUCTS_NAME, SHOPPING_LIST_NAME, SHOPPING_LISTS_NAME, LOCATIONS_NAME,
            QUANTITY_UNITS_NAME, PRODUCT_GROUPS_NAME]
        db_changed = await self._hass.async_add_executor_job(self._client.get_last_db_changed) 
        for sensor_type in sensor_types:
            sensor_update = self._sensor_update_dict[sensor_type]
            if (db_changed != sensor_update) or force:
                self._sensor_update_dict[sensor_type] = db_changed
                if sensor_type in self._sensor_types_dict:
                    # This is where the main logic to update platform data goes.
                    if wait:
                        await self._sensor_types_dict[sensor_type]()
                    else:
                        self._hass.async_create_task(self._sensor_types_dict[sensor_type]())

    async def async_update_products(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + PRODUCTS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][PRODUCTS_NAME] = (
            await self._hass.async_add_executor_job(self._client.get_products))

    async def async_update_shopping_list(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + SHOPPING_LIST_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][SHOPPING_LIST_NAME] = (
            await self._hass.async_add_executor_job(self._client.shopping_list))

    async def async_update_shopping_lists(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + SHOPPING_LISTS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][SHOPPING_LISTS_NAME] = (
            await self._hass.async_add_executor_job(self._client.shopping_lists))

    async def async_update_locations(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + LOCATIONS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][LOCATIONS_NAME] = (
            await self._hass.async_add_executor_job(self._client.locations))

    async def async_update_quantity_units(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + QUANTITY_UNITS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][QUANTITY_UNITS_NAME] = (
            await self._hass.async_add_executor_job(self._client.quantity_units))

    async def async_update_product_groups(self):
        """Update data."""
        _LOGGER.debug('Update data: ' + PRODUCT_GROUPS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][PRODUCT_GROUPS_NAME] = (
            await self._hass.async_add_executor_job(self._client.product_groups))
            

class Entities:
    """This helper class handle and store integration entities."""

    def __init__(self, hass):
        """Initialize the class."""
        self._hass = hass
        self._entities = []

    def async_add(self, entity, update: bool = False):
        """Handle add entity to entity registry"""
        _LOGGER.debug("Add {}".format(entity.name))
        self._entities.append(entity)
        
    def async_get(self, entity_id):
        for entity in self._entities:
            if entity.entity_id == entity_id:
                return entity
        return None

    def async_get_by_barcode(self, barcode):
        for entity in self._entities:
            if entity.device_state_attributes['_barcodes'][0] == barcode:
                return entity
        return None

    def async_get_all_by_class_name(self, class_name):
        entities = []
        for entity in self._entities:
            if type(entity).__name__ == class_name:
                entities.append(entity)
        return entities;

    def async_get_all(self):
        """Return all registered entities"""
        return self._entities

    def async_remove(self, entity_id):
        """Handle the removal of an entity."""
        self._entities = [e for e in self._entities if e.entity_id != entity_id]
        return True
    
    def async_schedule_update_ha_state(self, entity_id):
        entity = self.async_get(entity_id)
        if entity:
            entity.async_schedule_update_ha_state(True)

    def is_exists(self, entity_id) -> bool:
        return True if self.async_get(entity_id) else False