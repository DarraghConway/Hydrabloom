# import time
# import threading
# import board
# import adafruit_dht
# import adafruit_tsl2561
# from pubnub.pnconfiguration import PNConfiguration
# from pubnub.pubnub import PubNub
# from pubnub.callbacks import SubscribeCallback
# from dotenv import load_dotenv
# import os
# import uuid

# user_id = "Jack-device"

# load_dotenv()

# # Setup for sensors
# i2c = board.I2C()
# tsl2561 = adafruit_tsl2561.TSL2561(i2c, address=0x29)
# tsl2561.enabled = True
# dht_device = adafruit_dht.DHT22(board.D4)

# # PubNub configuration
# pnconfig = PNConfiguration()
# pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
# pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
# pnconfig.user_id = user_id
# pubnub = PubNub(pnconfig)

# app_channel = "sensors-pi-channel"

# LED_PIN = 15  # GPIO pin where the LED is connected

# # Initialize GPIO
# import RPi.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(LED_PIN, GPIO.OUT)

# # Lock to prevent DHT22 sensor race conditions
# sensor_lock = threading.Lock()

# def log_dht22_data():
#     """Logs temperature and humidity data from the DHT22 sensor."""
#     try:
#         with sensor_lock:
#             # Wait for sensor to stabilize
#             temperature_c = dht_device.temperature
#             humidity = dht_device.humidity
#             if temperature_c is not None and humidity is not None:
#                 message = {
#                     "temperature": temperature_c,
#                     "humidity": humidity
#                 }
#                 pubnub.publish().channel(app_channel).message(message).sync()
#                 print(f"Published DHT22 data: {message}")
#             else:
#                 print("Failed to read from DHT22")
#     except Exception as e:
#         print(f"Error with DHT22 sensor: {e}")
#     time.sleep(2)  # Wait 2 seconds between readings to ensure accuracy

# def log_tsl2561_data():
#     """Logs light level data from the TSL2561 sensor."""
#     try:
#         lux = tsl2561.lux
#         broadband = tsl2561.broadband  # Full spectrum (visible + IR)
#         infrared = tsl2561.infrared    # Infrared only
#         if lux is not None:
#             message = {
#                 "broadband": broadband,
#                 "lux": lux,
#                 "infrared": infrared
#             }
#             pubnub.publish().channel(app_channel).message(message).sync()
#             print(f"Published TSL2561 data: {message}")
#     except Exception as e:
#         print(f"Error with TSL2561 sensor: {e}")

# def log_sensor_data():
#     """Logs both DHT22 and TSL2561 sensor data."""
#     while True:
#         log_dht22_data()
#         log_tsl2561_data()
#         time.sleep(5)  # Delay before the next reading

# def turn_led_on(pin):
#     """Turn LED on."""
#     GPIO.output(pin, GPIO.HIGH)
#     print(f"LED turned ON")

# def turn_led_off(pin):
#     """Turn LED off."""
#     GPIO.output(pin, GPIO.LOW)
#     print(f"LED turned OFF")

# class LEDControlCallback(SubscribeCallback):
#     def message(self, pubnub, message):
#         command = message.message.get("command")
#         print(f"Received command: {command}")

#         if command == "LED_ON":
#             turn_led_on(LED_PIN)
#         elif command == "LED_OFF":
#             turn_led_off(LED_PIN)
#         else:
#             print("Unknown command received")

# # Function to handle LED control in a thread
# def led_control():
#     pubnub.add_listener(LEDControlCallback())
#     pubnub.subscribe().channels("led-pi-channel").execute()

# def start_threads():
#     # Create a thread for logging sensor data
#     sensor_thread = threading.Thread(target=log_sensor_data)

#     # Create a thread for LED control (PubNub listener)
#     led_thread = threading.Thread(target=led_control)

#     # Start both threads
#     sensor_thread.start()
#     led_thread.start()

#     sensor_thread.join()
#     led_thread.join()

# if __name__ == "__main__":
#     start_threads()
