"""Config flow for Tuya WiFi Scanner integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import tinytuya

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TuyaWifiScannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Scanner."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.devices = []
        self.selected_device = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step - scan for devices."""
        errors = {}

        if user_input is None:
            # Show the scan button
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "info": "Click Submit to scan for Tuya devices on your network."
                },
            )

        # Perform the scan
        try:
            _LOGGER.info("Starting Tuya device scan...")
            
            # Use deviceScan() instead of tinytuya.scanner.scan()
            # deviceScan() returns a dictionary of discovered devices
            devices = await self.hass.async_add_executor_job(
                lambda: tinytuya.deviceScan(verbose=False, maxretries=10)
            )
            
            if not devices:
                errors["base"] = "no_devices_found"
            else:
                self.devices = devices
                _LOGGER.info(f"Found {len(devices)} Tuya device(s)")
                return await self.async_step_select_device()

        except Exception as e:
            _LOGGER.error(f"Scan failed: {e}", exc_info=True)
            errors["base"] = "scan_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    async def async_step_select_device(self, user_input=None):
        """Let the user select a discovered device."""
        if user_input is not None:
            device_id = user_input["device"]
            self.selected_device = self.devices[device_id]
            return await self.async_step_device_key()

        # Create a list of devices for selection
        device_options = {}
        for dev_id, dev_info in self.devices.items():
            ip = dev_info.get("ip", "Unknown IP")
            version = dev_info.get("version", "Unknown")
            device_options[dev_id] = f"{dev_id} ({ip}) - v{version}"

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device"): vol.In(device_options),
                }
            ),
        )

    async def async_step_device_key(self, user_input=None):
        """Ask the user for the device key."""
        errors = {}

        if user_input is not None:
            # Store the configuration
            device_id = self.selected_device.get("gwId") or self.selected_device.get("id")
            
            return self.async_create_entry(
                title=f"Tuya Device {device_id[:8]}...",
                data={
                    "device_id": device_id,
                    "ip": self.selected_device.get("ip"),
                    "local_key": user_input["local_key"],
                    "version": self.selected_device.get("version", "3.3"),
                },
            )

        return self.async_show_form(
            step_id="device_key",
            data_schema=vol.Schema(
                {
                    vol.Required("local_key"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "device_id": self.selected_device.get("gwId") or self.selected_device.get("id"),
                "ip": self.selected_device.get("ip"),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TuyaOptionsFlowHandler(config_entry)


class TuyaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tuya WiFi Scanner."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.options.get("scan_interval", 30),
                    ): int,
                }
            ),
        )
