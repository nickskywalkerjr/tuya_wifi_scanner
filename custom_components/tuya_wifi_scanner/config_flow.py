"""Config flow for Tuya WiFi Local integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .discovery import discover_devices
from .validation import validate_device_key


class TuyaLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Local."""

    VERSION = 1

    def __init__(self) -> None:
        self.devices = {}
        self.selected_device_id = None

    async def async_step_user(self, user_input=None):
        """Step 1 — scan Wi-Fi LAN for Tuya devices."""
        errors = {}

        # First run: discover devices
        self.devices = await self.hass.async_add_executor_job(discover_devices)

        if not self.devices:
            errors["base"] = "no_devices_found"

        # Format device list for dropdown
        device_list = {}
        for dev_id, info in self.devices.items():
            name = info.get("name") or "Unknown Name"
            ip = info.get("ip") or info.get("address") or "Unknown IP"
            model = info.get("productKey") or info.get("dev_type") or "Unknown model"
            rssi = info.get("rssi")

            signal_text = "N/A" if rssi is None else f"{rssi} dBm"

            device_list[dev_id] = (
                f"{name} ({dev_id}) ({ip})\n"
                f"Model: {model}\n"
                f"Signal: {signal_text}"
            )

        # First selection
        if user_input is not None:
            self.selected_device_id = user_input["device"]
            return await self.async_step_key()

        # Show device picker
        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_list)
            })
        )

    async def async_step_key(self, user_input=None):
        """Step 2 — ask user for local key."""
        dev_info = self.devices.get(self.selected_device_id, {})
        ip = dev_info.get("ip")

        if user_input is not None:
            key = user_input["key"]

            # Validate key before saving
            valid = await self.hass.async_add_executor_job(
                validate_device_key,
                self.selected_device_id,
                ip,
                key
            )

            if not valid:
                return self.async_show_form(
                    step_id="key",
                    errors={"key": "invalid_key"},
                    data_schema=vol.Schema({vol.Required("key"): str}),
                    description_placeholders={"device_id": self.selected_device_id}
                )

            # All good → create config entry
            return self.async_create_entry(
                title=f"{self.selected_device_id}",
                data={
                    "device_id": self.selected_device_id,
                    "device_ip": ip,
                    "device_key": key
                }
            )

        # First time viewing the key prompt
        return self.async_show_form(
            step_id="key",
            data_schema=vol.Schema({vol.Required("key"): str}),
            description_placeholders={"device_id": self.selected_device_id}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TuyaLocalOptionsFlowHandler(config_entry)


class TuyaLocalOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow — not used yet, but required by HA."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(step_id="init")
