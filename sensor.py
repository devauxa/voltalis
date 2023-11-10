# sensor.py
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import POWER_WATT, ENERGY_WATT_HOUR
from . import DOMAIN

SCAN_INTERVAL = timedelta(minutes=10)

async def async_setup_entry(hass, config_entry, async_add_entities):
    voltalis = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.entry_id  # ou un autre identifiant unique pertinent
    power_sensors = [VoltalisPowerSensor(voltalis, device) for device in voltalis.get_modulators()]
    async_add_entities(power_sensors)
    async_add_entities([
        VoltalisImmediateConsumptionSensor(voltalis, unique_id),
        VoltalisTotalConsumptionSensor(voltalis, unique_id)
    ])

class VoltalisPowerSensor(SensorEntity):
    def __init__(self, voltalis, device):
        self._voltalis = voltalis
        self._device_id = device["csLinkId"]
        self._name = device["name"]
        self._state = None
    @property
    def unique_id(self):
        return f"voltalis_{self._device_id}_power"
    @property
    def name(self):
        return f"Voltalis {self._name}[{self._device_id}] power"

    @property
    def unit_of_measurement(self):
        return POWER_WATT

    @property
    def state(self):
        return self._state

    async def async_update(self):
        data = await self._voltalis.fetch_immediate_consumption_in_kw()
        self._state = data["immediateConsumptionInkWByAppliance"].get(self._device_id, {}).get("consumption", 0) * 1000

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._name,
            "manufacturer": "Voltalis",
    }

class VoltalisImmediateConsumptionSensor(SensorEntity):
    def __init__(self, voltalis, unique_id):
        self._voltalis = voltalis
        self._state = None
        self._name = "Voltalis Immediate Consumption"
        self._unique_id = unique_id
    @property
    def unique_id(self):
        return f"voltalis_immediate_consumption_{self._unique_id}"

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return "mdi:home-lightning-bolt-outline"

    @property
    def unit_of_measurement(self):
        return POWER_WATT

    @property
    def device_class(self):
        return "power"

    @property
    def state_class(self):
        return "total_increasing"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Voltalis",
    }

    async def async_update(self):
        data = await self._voltalis.fetch_immediate_consumption_in_kw()
        self._state = data['immediateConsumptionInkW']['consumption'] * 1000

class VoltalisTotalConsumptionSensor(SensorEntity):
    def __init__(self, voltalis, unique_id):
        self._voltalis = voltalis
        self._state = None
        self._name = "Voltalis Consumption"
        self._unique_id = unique_id

    @property
    def unique_id(self):
        return f"voltalis_total_consumption_{self._unique_id}"
    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return "mdi:home-lightning-bolt-outline"

    @property
    def unit_of_measurement(self):
        return ENERGY_WATT_HOUR

    @property
    def device_class(self):
        return "energy"

    @property
    def state_class(self):
        return "total_increasing"

    @property
    def state(self):
        return self._state

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "manufacturer": "Voltalis",
    }

    async def async_update(self):
        data = await self._voltalis.fetch_immediate_consumption_in_kw()
        immediate_consumption = data['immediateConsumptionInkW']['consumption'] * 1000
        consumption_duration = data['immediateConsumptionInkW']['duration'] / 3600
        self._state = immediate_consumption * consumption_duration
