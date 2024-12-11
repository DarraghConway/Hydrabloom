import RPi.GPIO as GPIO
import time
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub,SubscribeListener
from pubnub.callbacks import SubscribeCallback
from dotenv import load_dotenv

load_dotenv()

app_channel = "led-pi-channel"
LED_PIN = 15  # GPIO pin where the LED is connected

GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering:
GPIO.setup(LED_PIN, GPIO.OUT)  # Set pin as output

class Listener(SubscribeListener):
    def status(self,pubnub,status):
        print(f"Status:\n{status.category.name}")

pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")  # Replace with your Subscribe Key
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")      # Replace with your Publish Key
pnconfig.user_id = os.getenv("PUBNUB_PI_USER")  # Unique identifier for this client

pubnub = PubNub(pnconfig)
pubnub.add_listener(Listener())

class LEDControlCallback(SubscribeCallback):
    def message(self, pubnub, message):
        command = message.message.get("command")
        print(f"Received command: {command}")

        if command == "LED_ON":
            GPIO.output(LED_PIN, GPIO.HIGH)
            print(f"LED turned ON, GPIO state: {GPIO.input(LED_PIN)}")
        elif command == "LED_OFF":
            GPIO.output(LED_PIN, GPIO.LOW)
            print(f"LED turned OFF, GPIO state: {GPIO.input(LED_PIN)}")
        else:
            print("Unknown command received")


pubnub.add_listener(LEDControlCallback())
pubnub.subscribe().channels(app_channel).execute()

try:
    print(f"Listening for commands on PubNub channel: {app_channel}")
    while True:
        time.sleep(1)  

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()
    pubnub.unsubscribe_all()