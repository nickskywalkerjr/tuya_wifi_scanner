import tinytuya

def validate_device_key(dev_id, ip, key):
    """Try connecting with provided key. Returns True/False."""
    try:
        d = tinytuya.OutletDevice(dev_id, ip, key)
        d.set_version(3.3)
        d.status()   # will fail if key incorrect
        return True
    except Exception:
        return False
