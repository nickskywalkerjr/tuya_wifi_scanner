from homeassistant.components.diagnostics import async_redact_data
from .const import DOMAIN

# Fields to redact for privacy/security
TO_REDACT = ["device_key"]

async def async_get_config_entry_diagnostics(hass, config_entry):
    """Return diagnostics for the config entry."""
    data = dict(config_entry.data)

    # Redact sensitive fields
    data = async_redact_data(data, TO_REDACT)

    # Optionally, include current device status
    device_info = hass.data.get(DOMAIN, {}).get(config_entry.entry_id, {})
    device_status = None
    device = device_info.get("device")
    if device:
        try:
            # Run in executor to avoid blocking
            device_status = await hass.async_add_executor_job(device.status)
        except Exception:
            device_status = "Could not retrieve status"

    return {
        "config_entry": data,
        "device_status": device_status
    }
