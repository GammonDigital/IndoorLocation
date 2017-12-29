from bluepy.btle import Scanner, DefaultDelegate
import time
import datetime
import csv
import paho.mqtt.client as mqtt

# Variables
beaconThres = -50
scannerId = "P0JT"

# MQTT
# Define event callbacks

def on_subscribe(client, userdata, mid, granted_qos):   #create function for callback
   print("subscribed with qos",granted_qos, "\n")
   pass
def on_message(client, userdata, message):
    print("message received  "  ,str(message.payload.decode("utf-8")))
def on_publish(client,userdata,mid):   #create function for callback
   print("data published mid=",mid, "\n")
   pass
def on_disconnect(client, userdata, rc):
   print("client disconnected ok")

# Initiate client
# mqttclient = mqtt.Client("streamlinegammon", transport='websockets')
mqttclient = mqtt.Client(transport='websockets')

# Assign event callbacks
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe
mqttclient.on_message = on_message
mqttclient.on_disconnect = on_disconnect

# Connect
mqttclient.connect("broker.hivemq.com", port=8000)

# Beacon id
beaconRegFile = open('beaconReg.csv')
beaconRegReader = csv.reader(beaconRegFile)
beaconRegData = list(beaconRegReader)

beaconNum = [row[0] for row in beaconRegData][1:]
beaconAddr = [row[1] for row in beaconRegData][1:]

# Output file
outputFile = open('scanLog.csv', 'a', newline='')
outputWriter = csv.writer(outputFile)

# BLE Scanning
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device {}, RSSI={} dB".format(dev.addr, dev.rssi))
            outputWriter.writerow(['{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()), dev.addr, dev.rssi])
            outputFile.flush()
        elif isNewData:
            print("Received new data from", dev.addr)

# Check device proximity
while True:
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(0.5) # Scans for 0.5 seconds
    for dev in devices: 
        #for i in range(0,1): # check for i in beaconAddr syntax
        for i in range(len(beaconAddr)):
            if dev.addr == beaconAddr[i] and dev.rssi > beaconThres:
                mqttclient.publish("J3628", scannerId+", "+"{:%Y-%m-%d %H:%M:%S}, ".format(datetime.datetime.now())+str(beaconNum[i])+", "+str(dev.rssi))
    # Send sensor heartbeat
    if int("{:%M}".format(datetime.datetime.now()))%10 == 0 and int("{:%S}".format(datetime.datetime.now())) == 0:
        mqttclient.publish("J3628/heartbeat", scannerId+", "+"{:%Y-%m-%d %H:%M:%S}, ".format(datetime.datetime.now()))
                  
for dev in devices:
    print("Device {} ({}), RSSI={} dB".format(dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        print("  {} = {}".format(desc, value))

outputFile.close()
