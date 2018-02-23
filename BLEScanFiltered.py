from bluepy.btle import Scanner, DefaultDelegate
import datetime
import csv
import json
import paho.mqtt.client as mqtt
import ssl
import os
import requests

# from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage, IoTHubMessageDispositionResult

# Get serial number (to be used as scannerId)
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


# Parameters
with open("/home/pi/Documents/Python/IndoorLocation/beaconReg.csv", "r") as fBeacon:  # Import registered beacons
    beaconListFull = list(csv.reader(fBeacon))
    beaconNum = [item[0] for item in beaconListFull]
    beaconAddr = [item[1] for item in beaconListFull]

with open("/home/pi/Documents/Python/IndoorLocation/parameters.csv", "r") as fParameters:
    paramData = list(csv.reader(fParameters))
    projectNum = str(paramData[0][0])
    beaconThres = int(paramData[1][0])
    domain = str(paramData[2][0])
    CONNECTION_STRING = str(paramData[3][0])
    sas_token = str(paramData[4][0])
    botToken = str(paramData[5][0])
    chatId = str(paramData[6][0])

scannerId = getserial()

# For Azure
path_to_root_cert = "/home/pi/Documents/Python/IndoorLocation/root.cer"
device_id = "DTT-RPI"
login_username = domain + "/" + device_id
topic_heartbeat = "devices/" + device_id + "/messages/events/heartbeat"
topic_beacon = "devices/" + device_id + "/messages/events/beacon"
topic_subscriber = "devices/" + device_id + "/messages/devicebound/#"


# Classes and Functions
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

def on_connect(client, p2, p3, p4):
    print("Connected with result code " + str(p4))
    client.subscribe(topic_subscriber)

def on_publish(p1, p2, p3):
    print("...message sent successfully")

def on_message(client, userdata, msg):
    print("Received Message: %s" % msg.payload)

def on_subscribe(p1, p2, p3, p4):
    print("Subscribed")

def client_init():
    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(username=login_username, password=sas_token)
    client.tls_set(ca_certs=path_to_root_cert, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
    client.tls_insecure_set(False)
    return client


# TODO Heartbeat, csv to Github, JSON to IoTHub
client = client_init()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.on_subscribe = on_subscribe

client.connect(domain, port = 8883)
# client.loop_start()

# Check device proximity
requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text=" + str(scannerId) + "started")
while True:
    timenow = datetime.datetime.now()
    if timenow.minute%15 == 0 and timenow.second < 10: # Heartbeat
        # heartbeat = IoTHubMessage("1")
        # client.send_event_async(heartbeat, send_message_callback, 0)
        client.publish(topic_heartbeat, payload="HEARTBEAT", qos=0, retain=False)
        print("thump") # TODO send heartbeat
    scanner = Scanner().withDelegate(ScanDelegate())
    try:
        devices = scanner.scan(10)  # Scans for n seconds, note that the minew beacons broadcasts every 2 seconds
    except:
        requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text=" + str(
            scannerId) + "rebooted")
        os.system("sudo reboot")
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
            with open("/home/pi/Documents/Python/IndoorLocation/IndoorLocationRecords/scanlog_{}.csv".format(scannerId), "a") as fscanlog:
                fscanlog.write("{},{},{:%Y-%m-%d %H:%M:%S},{},{}\n".format(projectNum, scannerId, timenow, eachitem[0], eachitem[1]))
            scanResultJSON = json.dumps({"project": projectNum,
                              "scannerId": scannerId,
                              "datetime": "{:%Y-%m-%d %H:%M:%S}".format(timenow),
                              "beaconAddr": eachitem[0],
                              "beaconRssi": eachitem[1]})
            client.publish(topic_beacon, payload=scanResultJSON, qos=0, retain=False)
            print(scanResultJSON)
        requests.get("https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatId + "&text=" + str(scanSummary))
