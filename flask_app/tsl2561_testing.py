import time
import board
import adafruit_tsl2561

# Set up I2C communication
i2c = board.I2C()
A
# Initialize the TSL2561 sensor with the correct I2C address (0x29)
tsl2561 = adafruit_tsl2561.TSL2561(i2c, address=0x29)

# Enable the sensor
tsl2561.enabled = True

# Start reading data from the sensor
while True:
    try:
        # Read lux value from the sensor
        lux = tsl2561.lux

        if lux is not None:
            print(f"Light Level: {lux:.2f} lux")
        else:
            print("Failed to read sensor data")

        time.sleep(1)

    except KeyboardInterrupt:
        print("Program interrupted by user.")
        break
