import tinytuya
from homeassistant.core import HomeAssistant
from .const import DISCOVERY_TIMEOUT

async def discover_tuya_devices(hass: HomeAssistant):
    """Run TinyTuya discovery in a worker thread (avoids blocking HA loop)."""
    return await hass.async_add_executor_job(
        tinytuya.deviceScan, DISCOVERY_TIMEOUT, True
    )

def validate_device_key(device_id, ip, key):
    """Return True if we can connect & decrypt with the provided key."""

    d = tinytuya.Device(device_id, ip, key)
    d.set_version(3.3)

    try:
        data = d.status()   # Try querying the device
        return data is not None and "dps" in data
    except Exception:
        return False
