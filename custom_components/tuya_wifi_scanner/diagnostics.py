async def async_get_config_entry_diagnostics(hass, entry):
    return {
        "device_id": entry.data.get("device_id"),
        "device_ip": entry.data.get("device_ip"),
    }
