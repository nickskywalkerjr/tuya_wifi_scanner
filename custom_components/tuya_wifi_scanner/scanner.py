import tinytuya
from .const import DISCOVERY_TIMEOUT

def discover_tuya_devices():
    """Discover Tuya LAN devices and return selected fields."""
    raw_devices = tinytuya.deviceScan(DISCOVERY_TIMEOUT, True) or {}
    devices = {}

    for dev_id, info in raw_devices.items():
        devices[dev_id] = {
            "id": dev_id,
            "ip": info.get("ip") or info.get("address"),
            "product_name": info.get("productName") or info.get("name") or "Unknown",
            "local_key": info.get("localKey")  # may be None at discovery
        }
    return devices
