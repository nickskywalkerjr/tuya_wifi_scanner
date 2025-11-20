import tinytuya

def validate_device_key(dev_id, ip, key):
    """Validate the key using generic Tuya Device."""
    try:
        device = tinytuya.Device(dev_id, ip, key)  # generic Device
        device.set_version(3.3)
        status = device.status()
        return isinstance(status, dict) and "dps" in status and status["dps"]
    except Exception:
        return False
