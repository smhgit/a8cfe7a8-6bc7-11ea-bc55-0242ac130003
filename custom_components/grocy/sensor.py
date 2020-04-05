"""Platform for sensor integration."""

import logging

from datetime import timedelta

from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.components.sensor import ENTITY_ID_FORMAT

from .const import (VERSION, DOMAIN, DOMAIN_DATA, DATA_ENTITIES,
                    PRODUCTS_NAME, SHOPPING_LISTS_NAME, SHOPPING_LIST_NAME, LOCATIONS_NAME,
                    QUANTITY_UNITS_NAME, PRODUCT_GROUPS_NAME)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""

    # Save it to enable adding products via service
    GrocySensorEntity.async_add_entities = async_add_entities

    for product in hass.data[DOMAIN_DATA][PRODUCTS_NAME]:
        hass.add_job(ProductSensor(hass, product).async_add())

    for shopping_list in hass.data[DOMAIN_DATA][SHOPPING_LISTS_NAME]:
        hass.add_job(ShoppingListSensor(hass, shopping_list).async_add())

    hass.add_job(GrocySensor(hass).async_add())


class GrocySensorEntity(Entity):
    async_add_entities = None

    """Base class for grocy sensors"""
    def __init__(self, hass) -> None:
        self._hass = hass

    async def async_add(self, update=True):
        """Add this entity"""
        # Add it to the integration entity registry
        self._hass.data[DOMAIN_DATA][DATA_ENTITIES].async_add(self, True)
        # Add it to HA
        self.async_add_entities([self], update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon


class ProductSensor(GrocySensorEntity):
    """Product sensor class."""

    def __init__(self, hass, product) -> None:
        """Initialize entity"""
        super().__init__(hass)
        self._state = 0
        self._name = product.name
        self._attributes = {}
        self._entity_picture = product.picture_file_name
        self._product_id = product.id
        self._icon = 'mdi:cart-outline'
        self.entity_id = self.to_entity_id(product.id)

    @property
    def entity_picture(self):
        """Return the picture of the sensor."""
        return self._entity_picture

    @property
    def should_poll(self):
        return False

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        _LOGGER.debug(f"Update product: {self._name}")
        # Get the grocy product
        for product in self.hass.data[DOMAIN_DATA][PRODUCTS_NAME]:
            if product.id == self._product_id:
                break
        if not product:
            return
        # Update state (amount)
        self._state = 0
        for item in self.hass.data[DOMAIN_DATA][SHOPPING_LIST_NAME]:
            if item.product_id == product.id:
                self._state = item.amount
                break
        # Set attributes (remove leading '_')
        product_attributes = vars(product)
        for key in product_attributes.keys():
            self._attributes[key[1:]] = product_attributes[key]
        # Flatten userfields
        userfields = self._attributes['userfields']
        for key in userfields.keys():
            self._attributes[key] = userfields[key]
        del self._attributes['userfields']
        # Update extra attributes
        self._attributes['product_group_name'] = 'Other'
        self._attributes['location_name'] = 'Other'
        self._attributes['qu_purchase_name'] = 'Other'
        for item in self.hass.data[DOMAIN_DATA][PRODUCT_GROUPS_NAME]:
            if item.id == product.product_group_id:
                self._attributes['product_group_name'] = item.name
                break
        for item in self.hass.data[DOMAIN_DATA][LOCATIONS_NAME]:
            if item.id == product.location_id:
                self._attributes['location_name'] = item.name
                break
        for item in self.hass.data[DOMAIN_DATA][QUANTITY_UNITS_NAME]:
            if item.id == product.qu_id_purchase:
                self._attributes['qu_purchase_name'] = item.name
                break

    @staticmethod
    def to_entity_id(id):
        """Convert product id to entity unique id"""
        return "sensor.product{}".format(id)


class ShoppingListSensor(GrocySensorEntity):
    """Shopping list sensor class."""

    def __init__(self, hass, shopping_list) -> None:
        super().__init__(hass)
        self._state = 0
        self._shopping_list_id = shopping_list.id
        self._attributes = {
            "description": shopping_list.description
        }
        self._name = "ShoopingList{}".format(shopping_list.id)
        self._icon = 'mdi:cart-outline'
        self.entity_id = self.to_entity_id(shopping_list.id)

    @property
    def should_poll(self):
        return False

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        _LOGGER.debug(f"Update shopping list: {self._name}")
        self._state = 0
        self._attributes['total_amount'] = 0
        self._attributes['total_price'] = 0
        for item in self.hass.data[DOMAIN_DATA][SHOPPING_LIST_NAME]:
            if item.shopping_list_id == self._shopping_list_id:
                self._state += 1
                self._attributes['total_amount'] += item.amount
                for product in self.hass.data[DOMAIN_DATA][PRODUCTS_NAME]:
                    if product.id == item.product_id:
                        self._attributes['total_price'] += (product.price * item.amount)
                        break

    @staticmethod
    def to_entity_id(id):
        """Convert shopping list id to entity unique id"""
        return "sensor.shopping_list{}".format(id)


class GrocySensor(GrocySensorEntity):
    """Grocy sensor class."""

    def __init__(self, hass) -> None:
        super().__init__(hass)
        self._state = None
        self._attributes = {
            'total_products': 0,
            'integration_version': VERSION,
            'grocy_version': '2.6.1'
        }
        self._name = 'Grocy'
        self._icon = 'mdi:cart'

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        _LOGGER.debug("Update grocy sensor")
        self._state = 'connected'
        self._attributes['total_products'] = len(self.hass.data[DOMAIN_DATA][DATA_ENTITIES].async_get_all_by_class_name('ProductSensor'))