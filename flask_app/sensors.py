import time
import board
import adafruit_dht
import adafruit_tsl2561
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
from dotenv import load_dotenv
import os
import uuid
user_id = "Jack-device"

load_dotenv()

# Setup for sensors
i2c = board.I2C()
tsl2561 = adafruit_tsl2561.TSL2561(i2c, address=0x29)
tsl2561.enabled = True
dht_device = adafruit_dht.DHT22(board.D4)

# PubNub configuration
pnconfig = PNConfiguration()
pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
pnconfig.user_id = user_id  
pubnub = PubNub(pnconfig)



app_channel = "sensors-pi-channel"

def log_dht22_data():
    """Logs temperature and humidity data from the DHT22 sensor."""
    try:
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity
        if temperature_c is not None and humidity is not None:
            message = {
                    "temperature": temperature_c,
                    "humidity": humidity
                }
            pubnub.publish().channel(app_channel).message(message).sync()
            print(f"Published DHT22 data: {message}")
    except Exception as e:
        print(f"Error with DHT22 sensor: {e}")

def log_tsl2561_data():
    """Logs light level data from the TSL2561 sensor."""
    try:
        lux = tsl2561.lux
        broadband = tsl2561.broadband  # Full spectrum (visible + IR)
        infrared = tsl2561.infrared    # Infrared only
        if lux is not None:
            message = {
                "broadband": broadband,
                "lux": lux,
                "infrared": infrared
            }
            pubnub.publish().channel(app_channel).message(message).sync()
            print(f"Published TSL2561 data: {message}")
    except Exception as e:
        print(f"Error with TSL2561 sensor: {e}")

def log_sensor_data():
    """Logs both DHT22 and TSL2561 sensor data."""
    while True:
        log_dht22_data()
        log_tsl2561_data()
        time.sleep(5)  # Delay before the next reading

if __name__ == "__main__":
    log_sensor_data()  # Start logging sensor data
