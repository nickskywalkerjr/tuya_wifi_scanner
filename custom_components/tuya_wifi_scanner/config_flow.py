"""Config flow for Tuya WiFi Scanner integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN
from .scanner import discover_tuya_devices  # your existing scanner.py
from .validation import validate_device_key


class TuyaWifiScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Scanner."""

    VERSION = 1

    def __init__(self):
        self.devices: dict = {}
        self.selected_device_id: str | None = None

    async def async_step_user(self, user_input=None):
        """Step 1 — scan Wi-Fi LAN for Tuya devices."""
        errors = {}

        # Discover devices in background thread
        self.devices = await self.hass.async_add_executor_job(discover_tuya_devices)

        if not self.devices:
            errors["base"] = "no_devices_found"

        # Build dropdown: Name (ID) (IP), Model, Signal
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

        if user_input is not None:
            self.selected_device_id = user_input["device"]
            return await self.async_step_key()

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema({vol.Required("device"): vol.In(device_list)})
        )

    async def async_step_key(self, user_input=None):
        """Step 2 — ask user for local key."""
        dev_info = self.devices.get(self.selected_device_id, {})
        ip = dev_info.get("ip")

        if user_input is not None:
            key = user_input["key"]

            # Validate key in background thread
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

            # Key is valid → create config entry
            return self.async_create_entry(
                title=f"{self.selected_device_id}",
                data={
                    "device_id": self.selected_device_id,
                    "device_ip": ip,
                    "device_key": key
                }
            )

        # First time showing key prompt
        return self.async_show_form(
            step_id="key",
            data_schema=vol.Schema({vol.Required("key"): str}),
            description_placeholders={"device_id": self.selected_device_id}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        from .options_flow import async_get_options_flow
        return async_get_options_flow(config_entry)
