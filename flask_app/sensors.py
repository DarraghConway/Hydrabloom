import time
import adafruit_dht
import board
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import os

# Load environment variables for PubNub keys
load_dotenv()

# PubNub configuration
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "dht22-pi-0"

pubnub = PubNub(config)

# Initialize DHT22 sensor
dht_device = adafruit_dht.DHT22(board.D4)

# App channel for PubNub communication
app_channel = "dht22-pi-channel"

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f"Status: {status.category.name}")

pubnub.add_listener(Listener())
pubnub.subscribe().channels(app_channel).execute()

# Publish sensor data to PubNub
def publish_sensor_data(temp_c, humidity):
    message = {
        "temperature_c": temp_c,
        "temperature_f": temp_c * 9 / 5 + 32,
        "humidity": humidity,
    }
    pubnub.publish().channel(app_channel).message(message).sync()

# Main function to read sensor data
def main():
    print("Starting DHT22 Sensor with PubNub. Press Ctrl+C to exit.\n")
    try:
        while True:
            try:
                temperature_c = dht_device.temperature
                humidity = dht_device.humidity

                if temperature_c is not None and humidity is not None:
                    print(f"Temperature: {temperature_c:.1f}°C, Humidity: {humidity:.1f}%")
                    publish_sensor_data(temperature_c, humidity)
                else:
                    print("Failed to read data from the sensor. Retrying...")

            except RuntimeError as error:
                print(f"RuntimeError: {error.args[0]}")

            time.sleep(2.0)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        dht_device.exit()

if __name__ == "__main__":
    main()
