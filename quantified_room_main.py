# The MIT License (MIT)
# Copyright (c) 2019 Mark Koester
# https://opensource.org/licenses/MIT
# 
# Read Data from DHT11 Sensor (Temperature and Humidity)
# Publish data to a Thingspeak channel using the MQTT protocol
#
#
# prerequisites:
# - Arduino or Arduino-like Microcontroller Board, like ESP8266
# - Connected sensor(s) like DHT11 or DHT22
# - Thingspeak account
# - Thingspeak channel to publish data
# - Thingspeak Write API Key for the channel
# - Thingspeak MQTT API Key for the account
#
 
import network
from umqtt.robust import MQTTClient
import time
import os
import gc
from machine import Pin
from dht import DHT11

#
# WiFi connection information
#   
wifiSSID = "wifi-Router-Change"          # EDIT - enter name of WiFi connection point
wifiPassword = "Password-to-Change"  # EDIT - enter WiFi password 

#
# turn off the WiFi Access Point
# 
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

#
#   connect the ESP8266 device to the WiFi network
#
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(wifiSSID, wifiPassword)

#
# wait until the ESP8266 is connected to the WiFi network
# 
maxAttempts = 20
attemptCount = 0
while not wifi.isconnected() and attemptCount < maxAttempts:
  attemptCount +=1
  time.sleep(1)
  print('did not connect...trying again')
  
#
# create a random MQTT clientID 
#
randomNum = int.from_bytes(os.urandom(3), 'little')
myMqttClient = bytes("client_"+str(randomNum), 'utf-8')

#
# connect to Thingspeak MQTT broker
# connection uses unsecure TCP (port 1883)
# 
# To use a secure connection (encrypted) with TLS: 
#   set MQTTClient initializer parameter to "ssl=True"
#   Caveat: a secure connection uses about 9k bytes of the heap
#         (about 1/4 of the micropython heap on the ESP8266 platform)
thingspeakUrl = b"mqtt.thingspeak.com" 
thingspeakUserId = b"USERID"          # EDIT - enter Thingspeak User ID
thingspeakMqttApiKey = b"MQTT-API-KEY" # EDIT - enter Thingspeak MQTT API Key
client = MQTTClient(client_id=myMqttClient, 
                    server=thingspeakUrl, 
                    user=thingspeakUserId, 
                    password=thingspeakMqttApiKey, 
                    ssl=False)
                    
client.connect()

#
# publish temp / humidity from dht11 to Thingspeak using MQTT
#
d = DHT11(Pin(14))
thingspeakChannelId = b"CHANNEL-ID"             # EDIT - enter Thingspeak Channel ID
thingspeakChannelWriteApiKey = b"WRITE-API-KEY" # EDIT - enter Thingspeak Write API Key
publishPeriodInSec = 60 
while True:
    d.measure()
    temp = d.temperature()
    humid = d.humidity()
    credentials = bytes("channels/{:s}/publish/{:s}".format(thingspeakChannelId, thingspeakChannelWriteApiKey), 'utf-8')  
    payload = bytes("field1={:.1f}&field2={:.1f}\n".format(temp,humid), 'utf-8') 
    client.publish(credentials, payload)
    time.sleep(publishPeriodInSec)
  
client.disconnect()  
