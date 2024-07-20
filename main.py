# This is a sample Python script.
import time

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import paho.mqtt.client as mqtt
import secretsMQTT
import time
import datetime
import logging
#import amshan
from han import (
    common as han_type,
    autodecoder,
    dlde,
    obis_map,
    hdlc,
    meter_connection,
)
import json
_LOGGER: logging.Logger = logging.getLogger(__name__)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def _json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return None

def _try_read_meter_message(payload: bytes) -> han_type.MeterMessageBase | None:
    """Try to parse HDLC-frame from payload."""
    if payload.startswith(b"/"):
        try:
            return dlde.DataReadout(payload)
        except ValueError as ex:
            _LOGGER.debug("Starts with '/', but not a valid P1 message: %s", ex)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    client.subscribe(secretsMQTT.mqttPower)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    decoder = autodecoder.AutoDecoder()
    #decoded_frame = msg.payload.decode("utf-8")
    #print(decoded_frame)
    message = _try_read_meter_message(msg.payload)
    if message is not None:
        if message.message_type == han_type.MeterMessageType.P1:
            if message.is_valid:
                _LOGGER.debug(
                    "Got valid P1 message from topic %s: %s",
                    msg.topic,
                    msg.payload.hex(),
                )
                decoded_frame = decoder.decode_message(message) # TODO add try etc.. as in line 599: amshan/sensor.py (https://github.com/toreamun/amshan-homeassistant/blob/master/custom_components/amshan/sensor.py)
                print(decoded_frame["meter_datetime"])
                for key in decoded_frame:
                    payload = {key: decoded_frame[key]}
                    #print(payload)
                    print(json.dumps(payload, default=str)) # TODO publish to MQTT
                return message

            _LOGGER.debug(
                "Got invalid P1 message from topic %s: %s",
                msg.topic,
                msg.payload.hex(),
            )

            return None



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    #logging.basicConfig(level=logging.DEBUG)
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.username_pw_set(username=secretsMQTT.userName, password=secretsMQTT.passWord)
    print("Connecting...")
    mqttc.connect("homeassistant", 1883, 10)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    #mqttc.loop_forever()
    mqttc.loop_start()
    for i in range(100):
        print("Seconds: ", i)
        #mqttc.loop_read()
        #mqttc.loop_write()
        #mqttc.loop_misc()
        time.sleep(1)
    mqttc.loop_stop()
    print_hi("Program end")