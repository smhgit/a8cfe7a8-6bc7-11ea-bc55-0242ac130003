'''Helpers related to hass'''

import logging
import os

from .const import (DOMAIN, REQUIRED_FILES)

_LOGGER = logging.getLogger(__name__)


async def async_check_files(hass):
    """Return bool that indicates if all files are present."""

    # Verify that the user downloaded all files.
    base = "{}/custom_components/{}/".format(hass.config.path(), DOMAIN)
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue