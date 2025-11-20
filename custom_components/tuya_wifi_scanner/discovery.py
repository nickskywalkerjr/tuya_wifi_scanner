import tinytuya

def discover_devices():
    """Return LAN-discovered Tuya devices using TinyTuya."""
    return tinytuya.deviceScan()  # returns dict
