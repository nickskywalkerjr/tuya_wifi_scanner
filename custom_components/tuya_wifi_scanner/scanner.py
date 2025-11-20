"""Device discovery for Tuya WiFi Scanner."""
import tinytuya
from .const import DISCOVERY_TIMEOUT

def discover_tuya_devices():
    """Discover Tuya LAN devices (blocking, call via executor)."""
    devices = tinytuya.deviceScan(DISCOVERY_TIMEOUT, True)
    return devices or {}
