from bluepy.btle import Scanner, DefaultDelegate
import datetime
import csv
import json


# BLE Scanning
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)


def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial


# Variables
with open("/home/pi/Documents/Python/IndoorLocation/beaconReg.csv", "r") as fBeacon:  # Import registered beacons
    beaconListFull = list(csv.reader(fBeacon))
    beaconNum = [item[0] for item in beaconListFull]
    beaconAddr = [item[1] for item in beaconListFull]

with open("/home/pi/Documents/Python/IndoorLocation/parameters.csv", "r") as fParameters:
    projectNum, beaconThres = list(csv.reader(fParameters))

scannerId = getserial()


# TODO Heartbeat, csv to Github, JSON to IoTHub

# Check device proximity
while True:
    timenow = datetime.datetime.now()
    if timenow.minute%15 == 0 and timenow.second < 10: # Heartbeat
        print("thump") # TODO send heartbeat
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10)  # Scans for n seconds, note that the minew beacons broadcasts every 2 seconds
    scanSummary = []
    for dev in devices:
        if dev.addr in beaconAddr and dev.rssi > beaconThres: # Find max within scan time.  TODO mean?
            scanAddr = list(item[0] for item in scanSummary)
            if dev.addr not in scanAddr:
                scanSummary.append([dev.addr, dev.rssi])
            else:
                rownum = scanAddr.index(dev.addr)
                if dev.rssi > scanSummary[rownum][1]:
                    scanSummary[rownum][1] = dev.rssi
    if len(scanSummary) > 0:  # Write result in CSV locally and send result in JSON to Azure
        for eachitem in scanSummary:
            with open("/home/pi/Documents/Python/IndoorLocation/scanlog.csv", "a") as fscanlog:
                fscanlog.write("{},{},{:%Y-%m-%d %H:%M:%S},{},{}".format(projectNum, scannerId, timenow, eachitem[0], eachitem[1]))
            scanResultJSON = json.dumps({"project": projectNum,
                              "scannerId": scannerId,
                              "datetime": "{:%Y-%m-%d %H:%M:%S}".format(timenow),
                              "beaconAddr": eachitem[0],
                              "beaconRssi": eachitem[1]})
            # TODO send scanResultJSON to Azure
