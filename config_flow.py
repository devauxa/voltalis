# custom_components/voltalis/config_flow.py
from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN
from .voltalis import Voltalis

class VoltalisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Voltalis."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        hass: HomeAssistant = self.hass

        if user_input is not None:
            voltalis = Voltalis(user_input['username'], user_input['password'])
            try:
                await voltalis.login()
                return self.async_create_entry(title="Voltalis", data=user_input)
            except Exception as e:
                errors['base'] = f'login_failed {e}'
        # Utilisez le package voluptuous pour créer le schéma de données pour le formulaire
        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

class VoltalisOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Voltalis options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the Voltalis options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Handle the user options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Utilisez le package voluptuous pour créer le schéma de données pour le formulaire
        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )
