'''Custom component services'''

import logging
import requests

from homeassistant.core import callback

from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, CONF_ENTITY_ID

from .store import Store

from .sensor import ProductSensor, ShoppingListSensor
from .utils import contains

from .const import (DOMAIN, DOMAIN_DATA, DOMAIN_EVENT,
                    DATA_GROCY, DATA_DATA, DATA_ENTITIES, 
                    CONF_APIKEY, CONF_AMOUNT, CONF_SHOPPING_LIST_ID,
                    CONF_BARCODE, CONF_STORE, CONF_PRODUCT_GROUP_ID, CONF_UNIT_OF_MEASUREMENT,
                    CONF_PRODUCT_LOCATION_ID, CONF_PRODUCT_DESCRIPTION,
                    SYNC_GROCY_SERVICE, ADD_TO_LIST_SERVICE, SUBTRACT_FROM_LIST_SERVICE,
                    ADD_PRODUCT_SERVICE, UPDATE_PRODUCT_SERVICE, REMOVE_PRODUCT_SERVICE,
                    PRODUCTS_NAME, SHOPPING_LIST_NAME,
                    EVENT_ADDED_TO_LIST, EVENT_SUBTRACT_FROM_LIST, EVENT_PRODUCT_ADDED,
                    EVENT_PRODUCT_REMOVED, EVENT_PRODUCT_UPDATED, EVENT_SYNC_DONE, EVENT_GROCY_ERROR)
from .schema import (CONFIG_SCHEMA,
                    ADD_TO_LIST_SERVICE_SCHEMA, SUBTRACT_FROM_LIST_SERVICE_SCHEMA,
                    ADD_PRODUCT_SERVICE_SCHEMA, REMOVE_PRODUCT_SERVICE_SCHEMA)

_LOGGER = logging.getLogger(__name__)


def setup_services(hass):

    @callback
    def handle_add_to_list_service(call):
        hass.async_add_job(async_add_to_list(hass, call.data))
    hass.services.async_register(
        DOMAIN, ADD_TO_LIST_SERVICE, handle_add_to_list_service, schema=ADD_TO_LIST_SERVICE_SCHEMA
        )

    @callback
    def handle_subtract_from_list_service(call):
        hass.async_add_job(async_subtract_from_list(hass, call.data))
    hass.services.async_register(
        DOMAIN, SUBTRACT_FROM_LIST_SERVICE, handle_subtract_from_list_service, schema=SUBTRACT_FROM_LIST_SERVICE_SCHEMA
        )

    @callback
    def handle_add_product_service(call):
        hass.async_add_job(async_add_product(hass, call.data))
    hass.services.async_register(
        DOMAIN, ADD_PRODUCT_SERVICE, handle_add_product_service, schema=ADD_PRODUCT_SERVICE_SCHEMA
        )

    @callback
    def handle_remove_product_service(call):
        hass.async_add_job(async_remove_product(hass, call.data))
    hass.services.async_register(
        DOMAIN, REMOVE_PRODUCT_SERVICE, handle_remove_product_service, schema=REMOVE_PRODUCT_SERVICE_SCHEMA
        )

    @callback
    def handle_sync_grocy_service(call):
        hass.async_add_job(async_sync_grocy(hass, call.data))
    hass.services.async_register(
        DOMAIN, SYNC_GROCY_SERVICE, handle_sync_grocy_service
        )


async def async_subtract_from_list(hass, data):
    domain_data = hass.data[DOMAIN_DATA]
    # Can be product or barcode sensor
    entity_id = data[CONF_ENTITY_ID][0]
    entity = domain_data[DATA_ENTITIES].async_get(entity_id)
    if entity:
        resp = domain_data[DATA_GROCY].remove_product_in_shopping_list(
            entity.device_state_attributes['id'], data[CONF_SHOPPING_LIST_ID], data[CONF_AMOUNT]
            )
        if resp.status_code == 204:
            _LOGGER.debug(f"Product was subtarcted from list {entity_id}")
            await domain_data[DATA_DATA].async_update_data([SHOPPING_LIST_NAME], True)
            entity.async_schedule_update_ha_state(True)
            shopping_list_entity_id = domain_data[DATA_ENTITIES].async_get(ShoppingListSensor.to_entity_id(data[CONF_SHOPPING_LIST_ID]))
            shopping_list_entity_id.async_schedule_update_ha_state(True)
            hass.bus.fire(DOMAIN_EVENT, {
                "event": EVENT_SUBTRACT_FROM_LIST,
                "entity_id": entity_id
            })
        else:
            _LOGGER.debug("Failed to subtarct product from list {}".format(entity_id))


async def async_add_to_list(hass, data):
    domain_data = hass.data[DOMAIN_DATA]
    try:
        # Can be product or barcode sensor
        entity_id = data[CONF_ENTITY_ID][0]
        entity = domain_data[DATA_ENTITIES].async_get(entity_id)
        if not entity:
            barcode = hass.states.get(entity_id)
            if barcode:
                product = domain_data[DATA_GROCY].get_product_by_barcode(barcode.state)
                if product:
                    entity_id = 'sensor.product' + str(product.id)
                    entity = domain_data[DATA_ENTITIES].async_get(entity_id)
        if entity:
            # Product was found, add it to shopping list
            domain_data[DATA_GROCY].add_product_to_shopping_list(entity.device_state_attributes['id'], data[CONF_SHOPPING_LIST_ID], data[CONF_AMOUNT])
            await domain_data[DATA_DATA].async_update_data([SHOPPING_LIST_NAME], True)
            entity.async_schedule_update_ha_state(True)
            shopping_list_entity_id = domain_data[DATA_ENTITIES].async_get(ShoppingListSensor.to_entity_id(data[CONF_SHOPPING_LIST_ID]))
            shopping_list_entity_id.async_schedule_update_ha_state(True)    
            hass.bus.fire(DOMAIN_EVENT, {
                "event": EVENT_ADDED_TO_LIST,
                "entity_id": entity_id,
            })
    except requests.exceptions.HTTPError:
        _LOGGER.debug(f"Failed to add product: barcode {data[CONF_BARCODE]}")
    except requests.exceptions.ReadTimeout:
        _LOGGER.debug(f"Read timeout")

async def async_add_product(hass, data):
    domain_data = hass.data[DOMAIN_DATA]
    try:
        entity = domain_data[DATA_ENTITIES].async_get_by_barcode(data[CONF_BARCODE])
        # If entity (product) exists, update it, otherwise, add new entity (product)
        if entity:
            id = entity.device_state_attributes['id']
            domain_data[DATA_GROCY].update_product(id, product_group_id = data[CONF_PRODUCT_GROUP_ID],
                location_id = data[CONF_PRODUCT_LOCATION_ID])
            # Sync with grocy
            await domain_data[DATA_DATA].async_update_data([PRODUCTS_NAME], True)
            entity.async_schedule_update_ha_state(True)
            hass.bus.fire(DOMAIN_EVENT, {
                "event": EVENT_PRODUCT_UPDATED,
                "entity_id": entity.entity_id
            })
        else:
            # Search store for product
            store_product = Store(data[CONF_STORE]).get_product_by_barcode(data[CONF_BARCODE])
            if not store_product:
                _LOGGER.debug(f"Product was not found: {data[CONF_BARCODE]}")
                hass.bus.fire(DOMAIN_EVENT, {
                    "event": EVENT_GROCY_ERROR,
                    "message": f"{data[CONF_BARCODE]} wasn't found at {data[CONF_STORE]} store"
                })
                return True
            _LOGGER.debug(f"Found product: {store_product.name}")
            # Add product to grocy
            domain_data[DATA_GROCY].add_product(store_product.id, store_product.name,
                store_product.barcode, data[CONF_PRODUCT_DESCRIPTION], data[CONF_PRODUCT_GROUP_ID],
                store_product.qu_id_purchase, data[CONF_PRODUCT_LOCATION_ID], store_product.picture
            )
            domain_data[DATA_GROCY].set_userfields('products', store_product.id, {
                'price': store_product.price,
                'store': data[CONF_STORE].lower()
            })
            # Sync with grocy
            await domain_data[DATA_DATA].async_update_data([PRODUCTS_NAME], userfields=True)
            # Add product sensor
            for product in domain_data[PRODUCTS_NAME]:
                if product.id == store_product.id:
                    entity_id = ProductSensor.to_entity_id(product.id)
                    if not domain_data[DATA_ENTITIES].is_exists(entity_id):
                        hass.add_job(ProductSensor(hass, product).async_add())
                        _LOGGER.debug(f"Product {product.name} was added")
                        hass.bus.fire(DOMAIN_EVENT, {
                            "event": EVENT_PRODUCT_ADDED,
                            "entity_id": entity_id
                        })
    except requests.exceptions.HTTPError:
        _LOGGER.debug(f"Failed to add product: barcode {data[CONF_BARCODE]}")
    except requests.exceptions.ReadTimeout:
        _LOGGER.debug(f"Read timeout")


async def async_remove_product(hass, data):
    domain_data = hass.data[DOMAIN_DATA]
    try:
        # Can be product or barcode sensor
        entity_id = data[CONF_ENTITY_ID][0]
        # Search for product by entity id
        entity = domain_data[DATA_ENTITIES].async_get(entity_id)
        if not entity:
            # Search for product by barcode (sensor state)
            barcode = hass.states.get(entity_id)
            if barcode:
                product = domain_data[DATA_GROCY].get_product_by_barcode(barcode.state)
                if product:
                    entity_id = 'sensor.product' + str(product.id)
                    entity = domain_data[DATA_ENTITIES].async_get(entity_id)
        if entity:
            _LOGGER.debug(f"Remove product {entity.entity_id}")
            # Remove from grocy ERP
            product_id = entity.device_state_attributes['id']
            domain_data[DATA_GROCY].remove_product(product_id)
            # Remove entity from home assisatnt
            hass.add_job(entity.async_remove)
            # Remove from local entity registry
            domain_data[DATA_ENTITIES].async_remove(entity.entity_id)
            # Sync products with grocy
            await domain_data[DATA_DATA].async_update_data([PRODUCTS_NAME], True)
            # Send event
            hass.bus.fire(DOMAIN_EVENT, {
                "event": EVENT_PRODUCT_REMOVED,
                "entity_id": entity_id
            })
    except requests.exceptions.HTTPError:
        _LOGGER.debug(f"Failed to remove product from grocy {entity_id}")
    except requests.exceptions.ReadTimeout:
        _LOGGER.debug(f"Read timeout")


async def async_sync_grocy(hass, data):
    domain_data = hass.data[DOMAIN_DATA]
    try:
        # Force update from grocy
        await domain_data[DATA_DATA].async_update_data(force=True, userfields=True)
        # Add missing products
        for product in domain_data[PRODUCTS_NAME]:
            entity_id = ProductSensor.to_entity_id(product.id)
            if not domain_data[DATA_ENTITIES].is_exists(entity_id):
                hass.add_job(ProductSensor(hass, product).async_add())
                _LOGGER.debug(f"Sync add product: {entity_id}")
        # Remove floating products
        for entity in domain_data[DATA_ENTITIES].async_get_all_by_class_name('ProductSensor'):
            if not contains(domain_data[PRODUCTS_NAME], lambda p: p.id == entity.device_state_attributes['id']):
                hass.add_job(entity.async_remove)
                _LOGGER.debug(f"Remove product: {entity.entity_id}")
        # Update products userfields
        for product in domain_data[PRODUCTS_NAME]:
            store_product = Store(product.store).get_product_by_barcode(product.barcodes[0])
            if store_product:
                domain_data[DATA_GROCY].set_userfield('products', product.id, 'price', store_product.price)
        # Force update to get userfieldss
        await domain_data[DATA_DATA].async_update_data(force=True, userfields=True)
        # Update all products
        for entity in domain_data[DATA_ENTITIES].async_get_all():
            entity.async_schedule_update_ha_state(True)
        # Send event
        hass.bus.fire(DOMAIN_EVENT, {
            "event": EVENT_SYNC_DONE
        })
        _LOGGER.debug('Sync done')
    except requests.exceptions.HTTPError:
        _LOGGER.debug(f"Grocy sync failed")
    except requests.exceptions.ReadTimeout:
        _LOGGER.debug(f"Read timeout")
