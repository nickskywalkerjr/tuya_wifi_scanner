from homeassistant.components.diagnostics import async_redact_data
from .const import DOMAIN

TO_REDACT = ["device_key"]

async def async_get_config_entry_diagnostics(hass, config_entry):
    """Return diagnostics for the config entry."""
    data = dict(config_entry.data)
    data = async_redact_data(data, TO_REDACT)
    return {"config_entry": data}
