import time
import threading
import board
import adafruit_dht
import adafruit_tsl2561
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.crypto import AesCbcCryptoModule
from dotenv import load_dotenv
import os
import Adafruit_ADS1x15  # Library for the ADS1115 ADC (used with soil moisture sensor)
import RPi.GPIO as GPIO

# Load environment variables
load_dotenv()

# User-specific identifier
user_id = "raspberrypi400"

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
pnconfig.auth_key = os.getenv("PUBNUB_AUTH_KEY")
pnconfig.cipher_key = os.getenv("PUBNUB_CIPHER_KEY")
pnconfig.crypto_module = AesCbcCryptoModule(pnconfig)
pubnub = PubNub(pnconfig)

# Channel name
channel_name = "pi-hardware-channel"

# GPIO setup for LED and Pump
LED_PIN = 15  # GPIO pin where the LED is connected
PUMP_PIN = 17  # GPIO pin for pump control
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(PUMP_PIN, GPIO.OUT)

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
                pubnub.publish().channel(channel_name).message(message).sync()
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
            pubnub.publish().channel(channel_name).message(message).sync()
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
            pubnub.publish().channel(channel_name).message(message).sync()
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


def turn_led_on():
    """Turn LED on."""
    GPIO.output(LED_PIN, GPIO.HIGH)
    print("LED turned ON")


def turn_led_off():
    """Turn LED off."""
    GPIO.output(LED_PIN, GPIO.LOW)
    print("LED turned OFF")


def turn_pump_on():
    """Turn pump on."""
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    print("Pump turned ON")


def turn_pump_off():
    """Turn pump off."""
    GPIO.output(PUMP_PIN, GPIO.LOW)
    print("Pump turned OFF")


def turn_pump_on_with_duration(duration):
    """Turn pump on for a specific duration and notify UI when it turns off."""
    print(f"Pump turned ON for {duration} seconds")
    turn_pump_on()
    # Publish PUMP_ON message
    pubnub.publish().channel(channel_name).message({"command": "PUMP_ON"}).sync()

    def auto_turn_off():
        turn_pump_off()
        # Publish PUMP_OFF message when pump turns off
        pubnub.publish().channel(channel_name).message({"command": "PUMP_OFF"}).sync()
        print("Pump turned OFF automatically after duration")

    threading.Timer(duration, auto_turn_off).start()


class HardwareControlCallback(SubscribeCallback):
    def message(self, pubnub, message):
        """Handle incoming PubNub messages."""
        payload = message.message

        if isinstance(payload, dict):
            command = payload.get("command")
            duration = payload.get("duration")  # Optional duration parameter
            print(f"Received message: {payload}")

            if command == "LED_ON":
                turn_led_on()
            elif command == "LED_OFF":
                turn_led_off()
            elif command == "PUMP_ON":
                if duration and isinstance(duration, (int, float)):
                    turn_pump_on_with_duration(duration)
                else:
                    turn_pump_on()
            elif command == "PUMP_OFF":
                turn_pump_off()
            else:
                print(f"Unknown command: {command}")
        else:
            print(f"Message format error: Expected a dictionary, got {type(payload)}")


def hardware_control():
    """Listens for hardware control messages via PubNub."""
    pubnub.add_listener(HardwareControlCallback())
    pubnub.subscribe().channels(channel_name).execute()


def start_threads():
    """Starts threads for sensor data logging and hardware control."""
    sensor_thread = threading.Thread(target=log_sensor_data)
    hardware_thread = threading.Thread(target=hardware_control)

    sensor_thread.start()
    hardware_thread.start()

    sensor_thread.join()
    hardware_thread.join()


if __name__ == "__main__":
    try:
        start_threads()
    except KeyboardInterrupt:
        print("Stopping program...")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")
