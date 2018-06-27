from iothub_client import IoTHubClient, IoTHubTransportProvider, IoTHubMessage
import json

def createMsg(dictionary):
    return IoTHubMessage(json.dumps(dictionary, sort_keys=True, default=str))

def message_callback(message, result, user_context):
    print('message sent')

def send(dictionary, connection_string):
    msg_counter = 0  # Arbituary
    client = IoTHubClient(connection_string, IoTHubTransportProvider.MQTT)
    client.send_event_async(createMsg(dictionary), message_callback, msg_counter)