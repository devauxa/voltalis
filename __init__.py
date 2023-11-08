# __init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .voltalis import Voltalis

DOMAIN = "voltalis"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Voltalis component."""
    # Vous pouvez récupérer des données de configuration ici
    username = config[DOMAIN]["username"]
    password = config[DOMAIN]["password"]

    voltalis = Voltalis(username, password)
    await voltalis.login()

    # Stocker l'instance Voltalis pour l'utiliser dans les plateformes
    hass.data[DOMAIN] = voltalis

    # Setup des plateformes
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "switch")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Voltalis from a config entry."""
    # Appelé par le système de gestion des entrées de configuration
    # pour configurer une entrée de configuration
    return await async_setup(hass, {DOMAIN: entry.data})
