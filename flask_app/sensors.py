# import time
# import adafruit_dht
# import board
# import app
# import db
# from db import TempAndHumidityData


# dht_device = adafruit_dht.DHT22(board.D4)

# def log_sensor_data():
#     while True:
#         try:
#             temperature_c = dht_device.temperature
#             humidity = dht_device.humidity

#             # Save to the database
#             if temperature_c is not None and humidity is not None:
#                 new_reading = TempAndHumidityData(
#                     temperature=temperature_c,
#                     humidity=humidity
#                 )
#                 with app.app_context():  # Ensure Flask app context for database operations
#                     db.session.add(new_reading)
#                     db.session.commit()

#                 print(f"Logged: Temp={temperature_c}°C, Humidity={humidity}%")

#         except RuntimeError as err:
#             print(f"Sensor error: {err.args[0]}")

#         time.sleep(900)  # Log every 15 minutes (900 seconds)


while True:
    try:
        temperature_c = dht_device.temperature
        temperature_f = temperature_c * (9 / 5) + 32

        humidity = dht_device.humidity

        print("Temp:{:.1f} C / {:.1f} F    Humidity: {}%".format(temperature_c, temperature_f, humidity))
    except RuntimeError as err:
        print(err.args[0])

    time.sleep(2.0) 


