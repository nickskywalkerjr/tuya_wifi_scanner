from .const import DOMAIN
import tinytuya

async def async_setup_entry(hass, entry):
    """Set up Tuya WiFi Scanner from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    device_id = entry.data.get("device_id")
    device_ip = entry.data.get("device_ip")
    local_key = entry.data.get("device_key")
    product_name = entry.data.get("product_name", "Unknown")

    device = tinytuya.Device(device_id, device_ip, local_key)
    device.set_version(3.3)

    try:
        status = await hass.async_add_executor_job(device.status)
        if not status or "dps" not in status:
            raise Exception("Device did not respond correctly")
    except Exception as err:
        raise RuntimeError(f"Failed to connect to device {device_id}: {err}")

    hass.data[DOMAIN][entry.entry_id] = {
        "device": device,
        "id": device_id,
        "ip": device_ip,
        "product_name": product_name,
        "local_key": local_key,
    }

    return True
