from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up integration from Config Entry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": entry.data.get("device_id"),
        "device_ip": entry.data.get("device_ip"),
        "device_key": entry.data.get("device_key"),
    }

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

