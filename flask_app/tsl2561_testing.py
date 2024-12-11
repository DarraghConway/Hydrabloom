import time
import board
import adafruit_dht
import adafruit_tsl2561
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException

# Set up I2C communication for TSL2561 (Light Sensor)
i2c = board.I2C()
tsl2561 = adafruit_tsl2561.TSL2561(i2c, address=0x29)
tsl2561.enabled = True

# Set up DHT22 (Temperature and Humidity Sensor)
dht_device = adafruit_dht.DHT22(board.D4)

# Configure PubNub
pnconfig = PNConfiguration()
pnconfig.publish_key = "your_publish_key"
pnconfig.subscribe_key = "your_subscribe_key"
pnconfig.user_id = "your_user_id"
pubnub = PubNub(pnconfig)
pubnub.config.timeout = 30  # Set the timeout to 30 seconds

app_channel = "sensor-pi-channel"

def log_dht22_data():
    """Logs temperature and humidity data from the DHT22 sensor."""
    try:
        # Read data from DHT22 sensor
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        if temperature_c is not None and humidity is not None:
            message = {
                "temperature": temperature_c,
                "humidity": humidity
            }
            try:
                pubnub.publish().channel(app_channel).message(message).sync()
                print(f"Published DHT22 data: {message}")
            except PubNubException as e:
                print(f"Error publishing DHT22 message: {e}")
                time.sleep(10)  # Retry after 10 seconds if there's an error
        else:
            print("Failed to read DHT22 sensor data.")
    except RuntimeError as err:
        print(f"Sensor error: {err.args[0]}")

def log_tsl2561_data():
    """Logs light level data from the TSL2561 sensor."""
    try:
        # Read lux value from the TSL2561 sensor
        lux = tsl2561.lux

        if lux is not None:
            message = {
                "lux": lux
            }
            try:
                pubnub.publish().channel(app_channel).message(message).sync()
                print(f"Published TSL2561 data: {message}")
            except PubNubException as e:
                print(f"Error publishing TSL2561 message: {e}")
                time.sleep(10)  # Retry after 10 seconds if there's an error
        else:
            print("Failed to read TSL2561 sensor data.")
    except Exception as e:
        print(f"Error with TSL2561 sensor: {e}")

def log_sensor_data():
    """Logs both DHT22 and TSL2561 sensor data."""
    while True:
        log_dht22_data()  # Log temperature and humidity data
        # log_tsl2561_data()  # Log light level data
        time.sleep(5)  # Delay before next iteration

if __name__ == "__main__":
    log_sensor_data()  # Start logging sensor data
