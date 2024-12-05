import time
import adafruit_dht
import board
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
from dotenv import load_dotenv
import os
import uuid
user_id = "Jack-device"


# Load environment variables from .env file
load_dotenv()

def log_sensor_data():
    # Initialize the DHT22 sensor
    dht_device = adafruit_dht.DHT22(board.D4)

    # Configure PubNub using environment variables
    pnconfig = PNConfiguration()
    pnconfig.publish_key = os.getenv('PUBNUB_PUBLISH_KEY')
    pnconfig.subscribe_key = os.getenv('PUBNUB_SUBSCRIBE_KEY')
    pnconfig.user_id = user_id  # Use the user ID from .env
    pubnub = PubNub(pnconfig)
    
    # Set the timeout explicitly
    pubnub.config.timeout = 30  # Increase timeout to 30 seconds (default is 10)

    app_channel = "sensors-pi-channel"

    while True:
        try:
            # Read temperature and humidity from DHT22 sensor
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            if temperature_c is not None and humidity is not None:
                message = {
                    "temperature": temperature_c,
                    "humidity": humidity
                }
                # Attempt to publish the message
                attempt = 0
                max_attempts = 5  # Maximum retry attempts

                while attempt < max_attempts:
                    try:
                        pubnub.publish().channel(app_channel).message(message).sync()
                        print(f"Published: {message}")
                        break  # Exit retry loop if successful
                    except PubNubException as e:
                        print(f"Error publishing message: {e}")
                        attempt += 1
                        if attempt < max_attempts:
                            print(f"Retrying... Attempt {attempt}/{max_attempts}")
                            time.sleep(10)  # Retry after 10 seconds
                        else:
                            print("Max retry attempts reached. Skipping this data point.")
                            break

        except RuntimeError as err:
            print(f"Sensor error: {err.args[0]}")

        # Sleep for 5 seconds before reading the sensor again
        time.sleep(5)

