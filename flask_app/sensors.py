import time
import threading
import board
import adafruit_dht
import adafruit_tsl2561
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from dotenv import load_dotenv
import os
import uuid
import Adafruit_ADS1x15  # Library for the ADS1115 ADC (used with soil moisture sensor)

# Load environment variables
load_dotenv()

# User-specific identifier
user_id = "Jack-device"

# Setup for sensors
i2c = board.I2C()
tsl2561 = adafruit_tsl2561.TSL2561(i2c, address=0x29)
tsl2561.enabled = True
dht_device = adafruit_dht.DHT22(board.D4)

# Soil moisture sensor setup
adc = Adafruit_ADS1x15.ADS1115(address=0x29)
GAIN = 1  # Gain setting for the ADS1115
MOISTURE_CHANNEL = 0  # ADC channel connected to the soil moisture sensor

# PubNub configuration
pnconfig = PNConfiguration()
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.user_id = user_id
pubnub = PubNub(pnconfig)

# Channel names
app_channel = "sensors-pi-channel"
led_channel = "led-pi-channel"

# GPIO setup for LED
LED_PIN = 15  # GPIO pin where the LED is connected
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Lock to prevent race conditions with the DHT22 sensor
sensor_lock = threading.Lock()


def read_moisture():
    """Reads soil moisture data from the sensor."""
    try:
        value = adc.read_adc(MOISTURE_CHANNEL, gain=GAIN)
        return value
    except Exception as e:
        print(f"Error reading soil moisture: {e}")
        return None


def log_dht22_data():
    """Logs temperature and humidity data from the DHT22 sensor."""
    try:
        with sensor_lock:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity
            if temperature_c is not None and humidity is not None:
                message = {
                    "temperature": temperature_c,
                    "humidity": humidity,
                }
                pubnub.publish().channel(app_channel).message(message).sync()
                print(f"Published DHT22 data: {message}")
            else:
                print("Failed to read from DHT22")
    except Exception as e:
        print(f"Error with DHT22 sensor: {e}")
    time.sleep(2)


def log_tsl2561_data():
    """Logs light level data from the TSL2561 sensor."""
    try:
        lux = tsl2561.lux
        broadband = tsl2561.broadband
        infrared = tsl2561.infrared
        if lux is not None:
            message = {
                "broadband": broadband,
                "lux": lux,
                "infrared": infrared,
            }
            pubnub.publish().channel(app_channel).message(message).sync()
            print(f"Published TSL2561 data: {message}")
    except Exception as e:
        print(f"Error with TSL2561 sensor: {e}")


def log_soil_moisture_data():
    """Logs soil moisture data from the sensor."""
    try:
        moisture_level = read_moisture()
        if moisture_level is not None:
            message = {
                "soil_moisture": moisture_level,
            }
            pubnub.publish().channel(app_channel).message(message).sync()
            print(f"Published soil moisture data: {message}")
    except Exception as e:
        print(f"Error logging soil moisture data: {e}")


def log_sensor_data():
    """Logs data from all sensors."""
    while True:
        log_dht22_data()
        log_tsl2561_data()
        log_soil_moisture_data()
        time.sleep(20)


def turn_led_on(pin):
    """Turn LED on."""
    GPIO.output(pin, GPIO.HIGH)
    print("LED turned ON")


def turn_led_off(pin):
    """Turn LED off."""
    GPIO.output(pin, GPIO.LOW)
    print("LED turned OFF")


class LEDControlCallback(SubscribeCallback):
    def message(self, pubnub, message):
        command = message.message.get("command")
        print(f"Received command: {command}")

        if command == "LED_ON":
            turn_led_on(LED_PIN)
        elif command == "LED_OFF":
            turn_led_off(LED_PIN)
        else:
            print("Unknown command received")


def led_control():
    """Listens for LED control messages via PubNub."""
    pubnub.add_listener(LEDControlCallback())
    pubnub.subscribe().channels(led_channel).execute()


def start_threads():
    """Starts threads for sensor data logging and LED control."""
    sensor_thread = threading.Thread(target=log_sensor_data)
    led_thread = threading.Thread(target=led_control)

    sensor_thread.start()
    led_thread.start()

    sensor_thread.join()
    led_thread.join()


if __name__ == "__main__":
    start_threads()
