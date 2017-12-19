import paho.mqtt.client as mqtt

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
mqttclient = mqtt.Client("streamlinegammon", transport='websockets')

# Assign event callbacks
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe
mqttclient.on_message = on_message
mqttclient.on_disconnect = on_disconnect

# Connect
# mqttclient.username_pw_set("streamlinegammon@gmail.com", "")
mqttclient.connect("broker.hivemq.com", port=8000)

# Start subscription
mqttclient.subscribe("J3628/#")

# Publish a message
mqttclient.publish("J3628", "Initial test")

# Loop; exit on error
mqttclient.loop_forever()
'''
rc = 0
while rc == 0:
    rc = mqttclient.loop()
    print("rc: " + str(rc))
    '''