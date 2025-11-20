from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN
import voluptuous as vol

class TuyaWifiScannerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for existing config entry."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Initial options step."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Optional("device_key", default=self.config_entry.data["device_key"]): str
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema
        )


@callback
def async_get_options_flow(config_entry):
    return TuyaWifiScannerOptionsFlowHandler(config_entry)
