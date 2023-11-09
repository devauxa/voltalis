# __init__.py
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .voltalis import Voltalis

DOMAIN = "voltalis"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Voltalis from a config entry."""

    voltalis = Voltalis(entry.data['username'], entry.data['password'])
    await voltalis.login()

    # Stockage de l'objet Voltalis en utilisant entry.entry_id
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = voltalis

    _LOGGER.debug("Init switches")
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
#    hass.async_create_task(
#        hass.config_entries.async_forward_entry_setup(entry, "sensor")
#    )
    return True
