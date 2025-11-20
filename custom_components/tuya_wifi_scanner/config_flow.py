"""Config flow for Tuya WiFi Scanner."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

try:
    import tinytuya
except ImportError:
    tinytuya = None

DOMAIN = "tuya_wifi_scanner"

_LOGGER = logging.getLogger(__name__)


class TuyaScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Scanner."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.discovered_devices = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - start scanning."""
        if user_input is not None:
            # User clicked to start scan
            return await self.async_step_scan()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "info": "This will scan your local network for Tuya WiFi devices. Click Submit to start scanning."
            },
        )

    async def async_step_scan(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Scan for devices."""
        if tinytuya is None:
            return self.async_abort(reason="missing_library")

        errors = {}

        # Perform the scan
        try:
            devices = await self.hass.async_add_executor_job(self._scan_network)
            
            if not devices:
                return self.async_show_form(
                    step_id="scan",
                    errors={"base": "no_devices_found"},
                    description_placeholders={
                        "result": "No Tuya devices found on your network. Make sure devices are powered on and connected to WiFi."
                    },
                )

            self.discovered_devices = devices
            return await self.async_step_select_device()

        except Exception as err:
            _LOGGER.error(f"Scan failed: {err}")
            errors["base"] = "scan_failed"

        return self.async_show_form(
            step_id="scan",
            errors=errors,
            description_placeholders={"result": "Scanning failed. Check logs for details."},
        )

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let user select discovered device."""
        if user_input is not None:
            selected_ip = user_input["device"]
            
            # Find the selected device
            selected_device = None
            for device in self.discovered_devices:
                if device["ip"] == selected_ip:
                    selected_device = device
                    break

            if selected_device:
                # Create the config entry
                return self.async_create_entry(
                    title=f"Tuya Device ({selected_device['ip']})",
                    data={
                        "ip": selected_device["ip"],
                        "device_id": selected_device["device_id"],
                        "version": selected_device["version"],
                        "product_id": selected_device.get("product_id", ""),
                    },
                )

        # Build device selection options
        device_options = {}
        for device in self.discovered_devices:
            label = f"{device['ip']} - ID: {device['device_id'][:8]}... (v{device['version']})"
            if device.get("product_id"):
                label += f" [{device['product_id']}]"
            device_options[device["ip"]] = label

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_options),
            }),
            description_placeholders={
                "count": str(len(self.discovered_devices))
            },
        )

    def _scan_network(self) -> list[dict]:
        """Scan the network for Tuya devices."""
        _LOGGER.info("Starting Tuya device scan...")
        
        devices = []
        
        # Use tinytuya's built-in scanner
        scanner = tinytuya.scanner.TuyaScan()
        found = scanner.scan(maxretry=15)
        
        for device_id, device_info in found.items():
            device_data = {
                "device_id": device_id,
                "ip": device_info.get("ip", ""),
                "version": device_info.get("version", "3.3"),
                "product_id": device_info.get("product_id", ""),
            }
            
            # Only add devices with valid IP
            if device_data["ip"]:
                devices.append(device_data)
                _LOGGER.info(f"Found device: {device_data}")
        
        _LOGGER.info(f"Scan complete. Found {len(devices)} devices.")
        return devices
