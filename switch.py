# switch.py
from homeassistant.components.switch import SwitchEntity
from . import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Voltalis switch from a config entry."""
    _LOGGER.debug("Setup voltalis switches")
    voltalis = hass.data[DOMAIN][config_entry.entry_id]
    switches = [VoltalisSwitch(voltalis, device) for device in voltalis.get_modulators()]
    async_add_entities(switches)

class VoltalisSwitch(SwitchEntity):
    def __init__(self, voltalis, device):
        self._voltalis = voltalis
        self._state = None
        self._device_id = device["csLinkId"]
        self._name = device["name"]

    @property
    def unique_id(self):
        return f"voltalis_{self._device_id}"

    @property
    def name(self):
        return f"Voltalis {self._name}[{self._device_id}]"

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        await self._voltalis.switch_turn_on_off_device(self._device_id, True)
        self._state = True

    async def async_turn_off(self, **kwargs):
        await self._voltalis.switch_turn_on_off_device(self._device_id, False)
        self._state = False

    async def async_update(self):
        self._state = await self._voltalis.fetch_switch_device_status(self._device_id)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._name,
            "manufacturer": "Voltalis",
    }