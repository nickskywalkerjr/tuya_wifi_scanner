import tinytuya
from .const import DISCOVERY_TIMEOUT

async def discover_tuya_devices():
    """Scan local network for Tuya devices."""
    devices = tinytuya.deviceScan(DISCOVERY_TIMEOUT, True)
    # returns dict: {id: {"ip": "", "gwId": "", "version": ""} }
    return devices
