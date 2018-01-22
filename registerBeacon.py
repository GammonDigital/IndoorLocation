from bluepy.btle import Scanner, DefaultDelegate
import csv

# Variables
beaconThres = -35  # Set threshold for beacon registration, recommend -35 for beacons touching the Pi
startingAddr = "ac:23"  # Filter out starting MAC Addr


# BLE scanner def
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)


# Take starting beacon number that does not duplicate with anything on the existing list
def inputNewBeaconNum():
    global beaconNum
    tryNumi = int(input("Please input starting beacon number for this batch (number must be an integer that does not start with 0): "))
    while True:
        if tryNumi in beaconNum:
            tryNumi = int(input("Starting beacon number is already in the current registry, please select another starting beacon number: "))
        else:
            return tryNumi


# Start reading and recording until keyboard interruption
try:
    with open('/home/pi/Documents/Python/20180119_BeaconReg/beaconReg.csv', 'r') as f:  # Import current list
        beaconListFull = list(csv.reader(f))
        beaconAddr = [item[1] for item in beaconListFull]
        beaconNum = [item[0] for item in beaconListFull]

    # Input starting beacon number for the list
    beaconNumi = inputNewBeaconNum()

    while True:
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan()
        for dev in devices:
            if dev.rssi > beaconThres and not (dev.addr in beaconAddr) and dev.addr[:len(
                    startingAddr)] == startingAddr:  # Add to list only if the RSSI is larger than the threshold and the Addr is not already on the list
                beaconAddr.append(dev.addr)
                beaconNum.append(beaconNumi)
                print('Beacon {} is added to the list as {}'.format(dev.addr, beaconNumi))
                beaconNumi += 1
except KeyboardInterrupt:  # Write to file at keyboard interrupt
    with open('/home/pi/Documents/Python/20180119_BeaconReg/beaconReg.csv', 'w') as g:
        for i in range(len(beaconAddr)):
            g.write('{},{}\n'.format(beaconNum[i], beaconAddr[i]))
            print('{},{}\n'.format(beaconNum[i], beaconAddr[i]))
    quit()
