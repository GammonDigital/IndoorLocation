from bluepy.btle import Scanner, DefaultDelegate
import datetime
import csv
import json
import os
import requests
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage, IoTHubMessageDispositionResult

# Function def
def getserial():
    """Extract serial from cpuinfo file"""
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


def message_callback(message, result, user_context):
  print('message sent')


def createMsg(dictionary):
    return IoTHubMessage(json.dumps(dictionary, sort_keys=True, default=str))


# gspread access spreadsheet
# scope = ['https://spreadsheets.google.com/feeds']
# credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/Documents/Python/IndoorLocation/drive_client_secret.json', scope)  # Check path
# gc = gspread.authorize(credentials)
# googlesheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1_WNIUIbjUZLGD12NHjAdFNUvOSIsxqUqZMFxPZHBeRo").sheet1

# Parameters  #TODO: add connStr to parameters
with open("/home/pi/Documents/Python/IndoorLocation/beaconReg.csv", "r") as fBeacon:  # Import registered beacons
    beaconListFull = list(csv.reader(fBeacon))
    beaconNum = [item[0] for item in beaconListFull]
    beaconAddr = [item[1] for item in beaconListFull]

with open("/home/pi/Documents/Python/IndoorLocation/parameters.csv", "r") as fParameters:
    paramData = list(csv.reader(fParameters))
    projectNum = str(paramData[0][0])
    beaconThres = int(paramData[1][0])
    # domain = str(paramData[2][0])
    connection_string = str(paramData[3][0])
    # sas_token = str(paramData[4][0])
    botToken = str(paramData[5][0])
    chatId = str(paramData[6][0])

scannerId = getserial()

# BLE Scan Class
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

# Check device proximity
try:
    client = IoTHubClient(connection_string, IoTHubTransportProvider.MQTT)
except Exception:
    os.system("wait $" + str(
        os.getpid()) + "; sudo python3 /home/pi/Documents/Python/IndoorLocation/BLEScanFiltered.py")  # Check path
    quit()
msg_counter = 0 # Arbitrary
requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} started".format(scannerId))  # Boot notification to Telegram

bootMsgDict = {"devicegroup": "beaconScanner",
               "topic": "scannerStatus",
               "project": projectNum,
               "scannerId": scannerId,
               "datetime": str(datetime.datetime.now().isoformat()),
               "status": 0}
try:
    client.send_event_async(createMsg(bootMsgDict), message_callback, msg_counter)  # Boot notification to IoTHub
except  Exception:
    requests.get(
        "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} IoTHub error {}".format(
            scannerId, iothub_error))
    os.system("wait $" + str(
        os.getpid()) + "; sudo python3 /home/pi/Documents/Python/IndoorLocation/BLEScanFiltered.py")

while True:
    timenow = datetime.datetime.now()
    if timenow.minute%15 == 0 and timenow.second < 10: # Heartbeat
        requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} 1".format(scannerId))  # send heartbeat TODO: disable?

        heartbeatDict = {"devicegroup": "beaconScanner",
                       "topic": "scannerStatus",
                       "project": projectNum,
                       "scannerId": scannerId,
                       "datetime": str(datetime.datetime.now().isoformat()),
                       "status": 1}
        client.send_event_async(createMsg(heartbeatDict), message_callback, msg_counter)  # Heartbeat notification to IoTHub

    try:
        scanner = Scanner().withDelegate(ScanDelegate())
        devices = scanner.scan(10)  # Scans for n seconds, note that the minew beacons broadcasts every 2 seconds
    except Exception:
        requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} scanX >reboot".format(scannerId))
        os.system("sudo reboot")
        # os.system("wait $" + str(os.getpid()) + "; python /home/pi/Documents/Python/IndoorLocation/BLEScanFiltered.py")  # Check path
        quit()
    scanSummary = []
    
    for dev in devices:
        if dev.addr in beaconAddr and dev.rssi > beaconThres:  # Find max within scan time.  TODO mean?
            scanAddr = list(item[0] for item in scanSummary)
            if dev.addr not in scanAddr:
                scanSummary.append([dev.addr, dev.rssi])
            else:
                rownum = scanAddr.index(dev.addr)
                if dev.rssi > scanSummary[rownum][1]:
                    scanSummary[rownum][1] = dev.rssi
    if len(scanSummary) > 0:  # Write result in CSV locally and send result in JSON to Azure
        for eachitem in scanSummary:
            # Output1 console log
            print(eachitem)

            # Output2 local log
            with open("/home/pi/Documents/Python/IndoorLocation/IndoorLocationRecords/scanlog_{}_{}.csv".format(scannerId, str(datetime.datetime.now().date())), "a") as fscanlog:  # Log to individual file
                fscanlog.write("{},{},{},{},{}\n".format(str(timenow), projectNum, scannerId, eachitem[1], eachitem[0]))

            # Output3 telegram
            # requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={},{},{}".format(scannerId,eachitem[0],eachitem[1]))

            # Output4 gspread  #TODO disable?
            # try:
            #     gc.login()
            #     googlesheet.append_row(["NA", str(timenow), projectNum, scannerId, eachitem[1], eachitem[0]])
            #     #requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text=GSpreadSuccess")
            # except Exception:
            #     requests.get(
            #         "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} gspreadX >killprocess".format(scannerId))
            #     #os.system("sudo reboot")
            #     os.system("wait $" + str(os.getpid()) + "; sudo python3 /home/pi/Documents/Python/IndoorLocation/BLEScanFiltered.py")  # Check path
            #     quit()
            
            # Output5 MQTT to IoT Hub
            scanResultDict = {"devicegroup": "beaconScanner",
                              "topic": "beaconScanResult",
                              "project": projectNum,
                              "scannerId": scannerId,
                              "datetime": str(timenow.isoformat()),
                              "beaconAddr": eachitem[0],
                              "beaconRssi": eachitem[1]}
            try:
                client.send_event_async(createMsg(scanResultDict), message_callback, msg_counter)
            except Exception:  #IoTHubError as iothub_error
                requests.get(
                    "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text={} IoTHub error {}".format(
                        scannerId, iothub_error))
                os.system("wait $" + str(
                    os.getpid()) + "; sudo python3 /home/pi/Documents/Python/IndoorLocation/BLEScanFiltered.py")
                quit()
