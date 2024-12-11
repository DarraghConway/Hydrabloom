import time
import Adafruit_ADS1x15

# Create an ADS1115 ADC with the detected I2C address (0x29)
adc = Adafruit_ADS1x15.ADS1115(address=0x29)

# Set the ADC gain to 1 (this determines the voltage range)
GAIN = 1  # You can adjust the gain as per your needs, gain 1 means ±4.096V

# Moisture sensor is connected to A0
MOISTURE_CHANNEL = 0

# Function to read soil moisture from the sensor
def read_moisture():
    # Read the value from the sensor (using ADC at channel 0)
    value = adc.read_adc(MOISTURE_CHANNEL, gain=GAIN)
    return value

def main():
    print("Soil Moisture Sensor Test")
    print("Reading sensor values...")

    try:
        while True:
            # Read the moisture level
            moisture_level = read_moisture()
            
            # Print the raw sensor value
            print(f"Moisture Value: {moisture_level}")
            
            # Add some delay between readings
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting program...")
        pass

if __name__ == "__main__":
    main()
