from bluepy.btle import Scanner, DefaultDelegate
import datetime
import csv
import json
import paho.mqtt.client as mqtt
import ssl

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
    CONNECTION_STRING = str(paramData[2][0])

scannerId = getserial()

# For Azure
path_to_root_cert = "/home/pi/Documents/Python/IndoorLocation/root.cer"
device_id = "DTT-RPI"
sas_token = "SharedAccessSignature sr=gammon-iot-dev.azure-devices.net&sig=fGbHCFr5svdouyE92vdyGM6ohPXgc90XVMyj5y7ZM4I%3D&se=1549100826&skn=iothubowner"
domain = "gammon-iot-dev.azure-devices.net"
login_username = domain + "/" + device_id
topic_publisher = "devices/" + device_id + "/messages/events/heartbeat"
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
while True:
    timenow = datetime.datetime.now()
    if timenow.minute%15 == 0 and timenow.second < 10: # Heartbeat
        # heartbeat = IoTHubMessage("1")
        # client.send_event_async(heartbeat, send_message_callback, 0)
        client.publish(topic_publisher, payload="HEARTBEAT", qos=0, retain=False)
        print("thump") # TODO send heartbeat
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(10)  # Scans for n seconds, note that the minew beacons broadcasts every 2 seconds
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
            with open("/home/pi/Documents/Python/IndoorLocation/scanlog_{}.csv".format(scannerId), "a") as fscanlog:
                fscanlog.write("{},{},{:%Y-%m-%d %H:%M:%S},{},{}".format(projectNum, scannerId, timenow, eachitem[0], eachitem[1]))
            scanResultJSON = json.dumps({"project": projectNum,
                              "scannerId": scannerId,
                              "datetime": "{:%Y-%m-%d %H:%M:%S}".format(timenow),
                              "beaconAddr": eachitem[0],
                              "beaconRssi": eachitem[1]})
            client.publish(topic_publisher, payload=scanResultJSON, qos=0, retain=False)
            # TODO send scanResultJSON to Azure
