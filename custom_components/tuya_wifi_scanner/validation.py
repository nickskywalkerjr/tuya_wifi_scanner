import tinytuya

DEVICE_CLASSES = [
    tinytuya.Device,       # Generic device
    tinytuya.OutletDevice, # Common for plugs/outlets
    tinytuya.BulbDevice,   # Bulbs / LED controllers
]

VERSIONS = [3.3, 3.1]

def validate_device_key(dev_id, ip, key):
    """
    Validate a Tuya LAN device key.
    
    Tries multiple TinyTuya classes and versions until a successful connection.
    Returns True if device responds with valid DPS, False otherwise.
    """
    for cls in DEVICE_CLASSES:
        device = cls(dev_id, ip, key)
        for version in VERSIONS:
            try:
                device.set_version(version)
                status = device.status()
                if isinstance(status, dict) and "dps" in status and status["dps"]:
                    return True
            except Exception:
                continue
    return False
