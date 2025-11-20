import tinytuya
from homeassistant.core import HomeAssistant
from .const import DISCOVERY_TIMEOUT

async def discover_tuya_devices(hass: HomeAssistant):
    """Run TinyTuya discovery in a worker thread (avoids blocking HA loop)."""
    return await hass.async_add_executor_job(
        tinytuya.deviceScan, DISCOVERY_TIMEOUT, True
    )
