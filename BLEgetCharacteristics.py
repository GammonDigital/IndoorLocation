from bluepy.btle import Scanner, DefaultDelegate

# BLE Scan Class
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
while True:        
    try:
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(2)  # Scans for n seconds, note that the minew beacons broadcasts every 2 seconds
    except Exception:
        pass

    if devices != None:
        for dev in devices:
            if dev.addr == "ac:23:3f:23:c7:a6":
                print(dev.getScanData())
                #print(dev.getValueText(64))
                #print(dev.getValueText(255))
                #print(len(dev.getValueText(255)))
