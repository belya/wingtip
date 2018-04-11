import requests
from time import sleep

import random
import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

import numpy as np
from datetime import datetime

# String containing Hostname, Device Id & Device Key in the format
CONNECTION_STRING = "HostName=IoTHack9976.azure-devices.net;DeviceId=TestDeviceID;SharedAccessKey=IEo/aS2AHBpB6LW1gODJsjc67Gb5hnUhKQFIi+j9sNA="
# choose HTTP, AMQP or MQTT as transport protocol
PROTOCOL = IoTHubTransportProvider.HTTP
MESSAGE_TIMEOUT = 10000
AVG_WIND_SPEED = 10.0
SEND_CALLBACKS = 0
MAX_ID = 1000000

def generate_message(prop_map, ticketId, entryTime):
  prop_map.add("ticketId", str(ticketId))
  prop_map.add("entryTime", str(entryTime))

def generate_ticket_id():
  return np.random.randint(MAX_ID)

def send_confirmation_callback(message, result, user_context):
  global SEND_CALLBACKS
  print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
  map_properties = message.properties()
  print ( "    message_id: %s" % message.message_id )
  print ( "    correlation_id: %s" % message.correlation_id )
  key_value_pair = map_properties.get_internals()
  print ( "    Properties: %s" % key_value_pair )
  SEND_CALLBACKS += 1
  print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )

def iothub_client_init():
  # prepare iothub client
  client = IoTHubClient(CONNECTION_STRING, PROTOCOL)
  # set the time until a message times out
  client.set_option("messageTimeout", MESSAGE_TIMEOUT)
  client.set_option("logtrace", 0)
  client.set_option("product_info", "HappyPath_Simulated-Python")
  return client

def iothub_client_telemetry_sample_run():
  try:
    client = iothub_client_init()
    print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )
    message_counter = 0

    while True:
      msg_txt_formatted = "Event!"
      # messages can be encoded as string or bytearray
      if (message_counter & 1) == 1:
          message = IoTHubMessage(bytearray(msg_txt_formatted, 'utf8'))
      else:
          message = IoTHubMessage(msg_txt_formatted)
      # optional: assign ids
      message.message_id = "message_%d" % message_counter
      message.correlation_id = "correlation_%d" % message_counter
      # optional: assign properties
      prop_map = message.properties()
      generate_message(prop_map, generate_ticket_id(), datetime.now())
      client.send_event_async(message, send_confirmation_callback, message_counter)
      print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % message_counter )
      message_counter += 1
      sleep(np.random.randint(10))

  except IoTHubError as iothub_error:
    print ( "Unexpected error %s from IoTHub" % iothub_error )
    return

  except KeyboardInterrupt:
    print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
  iothub_client_telemetry_sample_run()