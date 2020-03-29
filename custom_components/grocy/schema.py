"""Schemas for grocy."""

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, CONF_ENTITY_ID

from .const import (DOMAIN,
                    CONF_APIKEY, CONF_AMOUNT, CONF_SHOPPING_LIST_ID,
                    CONF_BARCODE, CONF_STORE, CONF_PRODUCT_GROUP_ID,
                    CONF_NAME, CONF_VALUE,
                    CONF_PRODUCT_LOCATION_ID, CONF_PRODUCT_DESCRIPTION,
                    DEFAULT_AMOUNT, DEFAULT_SHOPPING_LIST_ID, DEFAULT_STORE,
                    DEFAULT_PRODUCT_DESCRIPTION)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_APIKEY): cv.string
    })
}, extra=vol.ALLOW_EXTRA)

ADD_TO_LIST_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_ids,
    vol.Optional(CONF_AMOUNT, default=DEFAULT_AMOUNT): cv.positive_int,
    vol.Optional(CONF_SHOPPING_LIST_ID, default=DEFAULT_SHOPPING_LIST_ID): cv.positive_int
})

SUBTRACT_FROM_LIST_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_ids,
    vol.Optional(CONF_AMOUNT, default=DEFAULT_AMOUNT): cv.positive_int,
    vol.Optional(CONF_SHOPPING_LIST_ID, default=DEFAULT_SHOPPING_LIST_ID): cv.positive_int
})

ADD_PRODUCT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_BARCODE): cv.string,
    vol.Required(CONF_PRODUCT_GROUP_ID): cv.positive_int,
    vol.Required(CONF_PRODUCT_LOCATION_ID): cv.positive_int,
    vol.Required(CONF_STORE, default=DEFAULT_STORE): cv.string,
    vol.Optional(CONF_PRODUCT_DESCRIPTION, default=DEFAULT_PRODUCT_DESCRIPTION): cv.string
})

ADD_FAVORITE_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_ids
})

REMOVE_FAVORITE_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_ids
})

REMOVE_PRODUCT_SERVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): cv.entity_ids
})