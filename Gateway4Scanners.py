# import serial
import re
import datetime
import json
import csv

with open("beaconReg.csv", "r") as fBeacon:
    beaconListFull = list(csv.reader(fBeacon))
    beaconNum = [item[0] for item in beaconListFull]
    beaconAddr = [item[1] for item in beaconListFull]

serialin0 = "00000000:00000000000000000000000000000000:0000000000:FC176623BE92:-071"
serialin1 = "4C000215:B9407F30F5F8466EAFF925556B57FE6D:AE44AC93B4:F9B5352BDBFB:-084"

# beaconRegex = re.compile(r'([\d|A-G]+):([\d|A-G]+):([\d|A-G]+):([\d|A-G]+):(-\d+)')
beaconRegex = re.compile(r'([\d|A-G]{8}):([\d|A-G]{32}):([\d|A-G]{4})([\d|A-G]{4})([\d|A-G]{2}):([\d|A-G]{12}):(-\d{3})')
beaconData = beaconRegex.match(serialin1)

beaconMAC = ""
for i in range(0, len(beaconData.group(6)), 2):
    beaconMAC += beaconData.group(6).lower()[i:i+2]+":"
beaconMAC = beaconMAC[0:-1]

beaconDataDict = {}
if True: #beaconMAC in beaconAddr:
    beaconDataDict = {"devicegroup": "beaconGateway",
                      "topic": "scannerStatus",
                      "project": "J3628",
                      "scannerId": "DTT-ARD-TST",
                      "datetime": datetime.datetime.now().isoformat(),
                      "factoryId": beaconData.group(1),
                      "ibeaconUuid": beaconData.group(2),
                      "major": int(beaconData.group(3), 16),
                      "minor": int(beaconData.group(4), 16),
                      "measuredPower": int(beaconData.group(5), 16),
                      "beaconAddr": beaconMAC,
                      "beaconRssi": beaconData.group(7)
                      }

beaconDataJSON = json.dumps(beaconDataDict)

print(beaconDataJSON)
# print(beaconAddr)

'''
Keanu Leung, [21.03.18 19:15]
P0: Factory ID
P1: iBeacon UUID
P2: Major Value
Minor Value
Measured Power
P3: MAC
P4: RSSI

Keanu Leung, [21.03.18 19:16]
P0 length is 8 Bytes; P1 length is 32 Bytes; P2 length is 10 Bytes; P3 length is 12
Bytes, P4 length is 4 Bytes, Those values all is ASCII mode.
P2 include Major Value (length 4 Bytes);
Minor Value (length 4 Bytes);
Measured Power (length 2 Bytes)
'''