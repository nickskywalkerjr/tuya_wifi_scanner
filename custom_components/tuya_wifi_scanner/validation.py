import tinytuya

def validate_device_key(dev_id, ip, key):
    """Validate device key by checking that status() returns valid DPS."""
    try:
        d = tinytuya.OutletDevice(dev_id, ip, key)
        d.set_version(3.3)
        status = d.status()

        # Must be a dict with "dps" containing at least one item
        if isinstance(status, dict) and "dps" in status and status["dps"]:
            return True
        return False
    except Exception:
        return False
