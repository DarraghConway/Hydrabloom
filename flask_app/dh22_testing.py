import time
import adafruit_dht
import board


dht_device = adafruit_dht.DHT22(board.D4)

print("Starting DHT22 Sensor Test. Press Ctrl+C to exit.\n")

while True:
    try:
        temperature_c = dht_device.temperature
        temperature_f = temperature_c * (9 / 5) + 32

        humidity = dht_device.humidity

        if temperature_c is not None and humidity is not None:
            print(f"Temperature: {temperature_c:.1f}°C / {temperature_f:.1f}°F, Humidity: {humidity:.1f}%")
        else:
            print("Failed to read data from the sensor. Retrying...")

    except RuntimeError as error:
        print(f"RuntimeError: {error.args[0]}")

    except Exception as error:
        print(f"An error occurred: {error}")
        dht_device.exit()
        break

    time.sleep(2.0)
