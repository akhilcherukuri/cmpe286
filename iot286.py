from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import threading
import argparse
import json
import smbus
import blynklib
import random
from uptime import uptime

i2c_channel = 1
i2c_address = 0x48
tmp102_register_temperature = 0x00

host = "a1ii3qlfr1qukw-ats.iot.us-east-1.amazonaws.com"
certPath = "/home/pi/certs_east/"
clientId = "iot295bthing"
topic = "iot/temperature"

BLYNK_AUTH = 'AMR7MumjzdyfhEdW0y0xWoCYmwibKuV_'
blynk = blynklib.Blynk(BLYNK_AUTH)

def twos_complement(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def read_temperature():
    val = bus.read_i2c_block_data(i2c_address, tmp102_register_temperature, 2)
    temperature_c = (val[0] << 4) | (val[1] >> 4)
    temperature_c = twos_complement(temperature_c, 12)
    temperature_c = temperature_c * 0.0625
    return temperature_c

bus = smbus.SMBus(i2c_channel)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, 8883)
myAWSIoTMQTTClient.configureCredentials("{}Amazon-root-CA-1.pem".format(certPath), "{}private.pem.key".format(certPath), "{}device.pem.crt".format(certPath))

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myAWSIoTMQTTClient.connect()

READ_PRINT_MSG = "[READ_VIRTUAL_PIN_EVENT] Pin: V{}"

@blynk.handle_event('read V11')
def read_virtual_pin_handler(pin):
    print(READ_PRINT_MSG.format(pin))
    temperature = read_temperature()
    blynk.virtual_write(pin, round(temperature,2))
    humidity = random.uniform(34.00,35.00)
    lat = 37.3409
    lng = -121.8981
    index = 0
    blynk.virtual_write(10, round(humidity,2))
    blynk.virtual_write(9, index, lat, lng, "Rasp. Weather Station")
    time_turned_on = round(uptime(),2)
    blynk.virtual_write(8, time_turned_on)
    
    critical_temperature_value = 35
    
    if temperature >= critical_temperature_value:
        
        blynk.set_property(pin, 'color', '#FF0000')
        blynk.notify('Warning temperature exceeds critical value')

def aws_communication(): 
    time.sleep(10)
    aws_temperature = read_temperature()
    message = {}
    message['temperature'] = aws_temperature
    # message['sequence'] = loopCount
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish(topic, messageJson, 1)
    print('Published topic %s: %s\n' % (topic, messageJson))
myAWSIoTMQTTClient.disconnect()


while True:
    blynk.run()
    aws_communication()