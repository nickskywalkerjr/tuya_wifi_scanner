"""Tuya WiFi Scanner integration."""

from .const import DOMAIN
import tinytuya

async def async_setup_entry(hass, entry):
    """Set up integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    device_id = entry.data.get("device_id")
    device_ip = entry.data.get("device_ip")
    device_key = entry.data.get("device_key")

    # Create TinyTuya device
    device = tinytuya.OutletDevice(device_id, device_ip, device_key)
    device.set_version(3.3)

    # Test connection
    try:
        status = await hass.async_add_executor_job(device.status)
        if not status or "dps" not in status:
            raise Exception("Device did not respond correctly")
    except Exception as err:
        raise RuntimeError(f"Failed to connect to device {device_id}: {err}")

    # Store device instance
    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "device_id": device_id,
        "device_ip": device_ip,
        "device_key": device_key,
    }

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
