import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN
from .scanner import discover_tuya_devices

class TuyaWifiScannerFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Tuya WiFi Scanner."""

    def __init__(self):
        self.devices = None
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Initial step: scan network for Tuya WiFi devices."""

        if user_input is not None:
            self.selected_device = user_input["device"]
            return await self.async_step_key()

        # --- discover devices ---
        self.devices = await discover_tuya_devices()

        if not self.devices:
            return self.async_abort(reason="no_devices_found")

        device_list = {
            dev_id: f"{dev_id} ({info.get('ip')})"
            for dev_id, info in self.devices.items()
        }

        schema = vol.Schema({
            vol.Required("device"): vol.In(device_list)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={}
        )

    async def async_step_key(self, user_input=None):
        """Ask user for device key."""

        if user_input is not None:
            dev_info = self.devices[self.selected_device]

            return self.async_create_entry(
                title=f"Tuya Device {self.selected_device}",
                data={
                    "device_id": self.selected_device,
                    "device_ip": dev_info.get("ip"),
                    "device_key": user_input["key"]
                },
            )

        schema = vol.Schema({
            vol.Required("key"): str
        })

        return self.async_show_form(
            step_id="key",
            data_schema=schema,
            description_placeholders={"device_id": self.selected_device}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return None
