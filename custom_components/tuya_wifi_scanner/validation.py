"""Validate Tuya device keys."""
import tinytuya

def validate_device_key(dev_id, ip, key):
    """Validate that the device responds with DPS using the provided key."""
    try:
        device = tinytuya.OutletDevice(dev_id, ip, key)
        device.set_version(3.3)
        status = device.status()
        return isinstance(status, dict) and "dps" in status and status["dps"]
    except Exception:
        return False
