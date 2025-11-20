import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN
from .scanner import discover_tuya_devices


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya WiFi Scanner."""

    VERSION = 1

    def __init__(self):
        self.devices = {}
        self.selected_device_id = None

    async def async_step_user(self, user_input=None):
        """First step: discover devices + let user pick one."""

        # Submit selected device → go to key step
        if user_input is not None:
            self.selected_device_id = user_input["device"]
            return await self.async_step_key()

        # Scan network
        self.devices = await discover_tuya_devices(self.hass)

        if not self.devices:
            return self.async_abort(reason="no_devices_found")

        # Prepare dropdown list
        device_list = {}

        for dev_id, info in self.devices.items():
        
            # Extract fields safely
            name = info.get("name") or "Unknown Name"
            ip = info.get("ip") or info.get("address") or "Unknown IP"
            model = info.get("productKey") or info.get("dev_type") or "Unknown model"
            rssi = info.get("rssi")
        
            # Format signal strength
            if rssi is None:
                signal_text = "N/A"
            else:
                signal_text = f"{rssi} dBm"
        
            # Display string
            display_text = (
                f"{name} ({dev_id}) ({ip})\n"
                f"Model: {model}\n"
                f"Signal: {signal_text}"
            )

            device_list[dev_id] = display_text


        data_schema = vol.Schema({vol.Required("device"): vol.In(device_list)})


        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={}
        )

    async def async_step_key(self, user_input=None):
    """Second step: ask user for device local key."""

        # If user submitted a key, validate it
        if user_input is not None:
            dev_info = self.devices.get(self.selected_device_id, {})
            ip = dev_info.get("ip")
    
            # Validate the provided key
            valid = await self.hass.async_add_executor_job(
                validate_device_key,
                self.selected_device_id,
                ip,
                user_input["key"]
            )
    
            if not valid:
                # Key invalid → show form again with error
                return self.async_show_form(
                    step_id="key",
                    data_schema=vol.Schema({vol.Required("key"): str}),
                    errors={"key": "invalid_key"},
                    description_placeholders={
                        "device_id": self.selected_device_id
                    }
                )
    
            # Key is valid → create entry
            return self.async_create_entry(
                title=f"{self.selected_device_id}",
                data={
                    "device_id": self.selected_device_id,
                    "device_ip": ip,
                    "device_key": user_input["key"]
                }
            )
    
        # First time opening the step → show form
        return self.async_show_form(
            step_id="key",
            data_schema=vol.Schema({vol.Required("key"): str}),
            description_placeholders={
                "device_id": self.selected_device_id
            }
        )



    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import async_get_options_flow
        return async_get_options_flow(config_entry)
