''' Grocy integration '''

import logging

from homeassistant.util import Throttle
from homeassistant.const import CONF_HOST

from .grocy import Grocy

from .services import setup_services

from .const import (DOMAIN, DOMAIN_DATA,
                    CONF_APIKEY, CONF_STORE,
                    DATA_GROCY, DATA_DATA, DATA_ENTITIES, DATA_STORE_CONF,
                    PRODUCTS_NAME, SHOPPING_LISTS_NAME, SHOPPING_LIST_NAME, LOCATIONS_NAME,
                    QUANTITY_UNITS_NAME, PRODUCT_GROUPS_NAME)
from .schema import CONFIG_SCHEMA

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    
    # Check configuration exists
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    # Get "global" configuration.
    grocy_host = conf.get(CONF_HOST)
    grocy_apikey = conf.get(CONF_APIKEY)

    # Extarct address and ports
    host = "{}:{}".format(grocy_host.split(":")[0], grocy_host.split(":")[1])
    port = grocy_host.split(":")[2]

    # Configure the grocy client
    grocy = Grocy(host, grocy_apikey, port = port)
    if not grocy.is_connected():
        _LOGGER.error('Failed to connect to grocy, check apikey: ' + grocy_host)
        return None
    _LOGGER.debug('Connected to grocy: ' + grocy_host)

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {
        DATA_GROCY: grocy,
        DATA_DATA: Data(hass, grocy),
        DATA_ENTITIES: Entities(hass),
        DATA_STORE_CONF: conf.get(CONF_STORE),
        PRODUCTS_NAME: [],
        SHOPPING_LIST_NAME: [],
        SHOPPING_LISTS_NAME: [],
        LOCATIONS_NAME: [],
        QUANTITY_UNITS_NAME: [],
        PRODUCT_GROUPS_NAME: []
    }

    setup_services(hass);

    # Initial objects upddate
    await hass.data[DOMAIN_DATA]['data'].async_update_data(None, wait=True, userfields=True)

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config)
    )

    # Initialization was successful.
    return True


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

    async def async_update_data(self, sensor_types = None, wait: bool = True, force: bool = False, userfields:bool = False):
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
                        await self._sensor_types_dict[sensor_type](userfields=userfields)
                    else:
                        self._hass.async_create_task(self._sensor_types_dict[sensor_type](userfields=userfields))

    async def async_update_products(self, userfields:bool = False):
        """Update data."""
        _LOGGER.debug('Update data: ' + PRODUCTS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][PRODUCTS_NAME] = (
            await self._hass.async_add_executor_job(self._client.get_products, userfields))

    async def async_update_shopping_list(self, userfields:bool = False):
        """Update data."""
        _LOGGER.debug('Update data: ' + SHOPPING_LIST_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][SHOPPING_LIST_NAME] = (
            await self._hass.async_add_executor_job(self._client.shopping_list))

    async def async_update_shopping_lists(self, userfields:bool = False):
        """Update data."""
        _LOGGER.debug('Update data: ' + SHOPPING_LISTS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][SHOPPING_LISTS_NAME] = (
            await self._hass.async_add_executor_job(self._client.shopping_lists))

    async def async_update_locations(self, userfields:bool = False):
        """Update data."""
        _LOGGER.debug('Update data: ' + LOCATIONS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][LOCATIONS_NAME] = (
            await self._hass.async_add_executor_job(self._client.locations))

    async def async_update_quantity_units(self, userfields:bool = False):
        """Update data."""
        _LOGGER.debug('Update data: ' + QUANTITY_UNITS_NAME)
        # This is where the main logic to update platform data goes.
        self._hass.data[DOMAIN_DATA][QUANTITY_UNITS_NAME] = (
            await self._hass.async_add_executor_job(self._client.quantity_units))

    async def async_update_product_groups(self, userfields:bool = False):
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
            barcodes = entity.device_state_attributes.get('barcodes')
            if barcodes and barcodes[0] == barcode:
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