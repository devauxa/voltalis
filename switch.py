# switch.py
from homeassistant.components.switch import SwitchEntity
from . import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Voltalis switch from a config entry."""
    voltalis = hass.data[DOMAIN]
    switches = [VoltalisSwitch(voltalis, device) for device in voltalis.get_modulators()]
    async_add_entities(switches)

class VoltalisSwitch(SwitchEntity):
    def __init__(self, voltalis, device):
        self._voltalis = voltalis
        self._state = None
        self._device_id = device["csLinkId"]
        self._name = device["name"]

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
