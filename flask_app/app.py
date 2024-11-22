import threading
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, db, User, PlantType, Location, Plant, TempAndHumidityData  # Import models and init_db
from datetime import datetime 
from seed import seed_data

#Comment
''' 
import time
import adafruit_dht
import board
dht_device = adafruit_dht.DHT22(board.D4)
'''


# from sensors import log_sensor_data

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.secret_key = 'Richy123'

# Initialize database
init_db(app)

# Routes
@app.route('/')
def home():
    plant_types = PlantType.query.all() 
    return render_template('register.html', plant_types=plant_types)

@app.route('/main_page')
def main_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    plants = Plant.query.filter_by(user_id=user.id).all()
    return render_template('main_page.html', user=user, plants=plants)

@app.route('/add_plant.html', methods=['GET', 'POST'])
def add_plant():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        plant_type_id = request.form['plant_type']
        location_id = request.form['location']
        date_planted = request.form['date_planted']
        user_id = session['user_id']

        try:
            date_planted = datetime.strptime(date_planted, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        new_plant = Plant(
            name=name,
            plant_type_id=plant_type_id,
            location_id=location_id,
            date_planted=date_planted,  
            user_id=user_id
        )

        db.session.add(new_plant)
        db.session.commit()

        return redirect(url_for('main_page'))

    plant_types = PlantType.query.all()
    locations = Location.query.all()
    return render_template('add_plant.html', plant_types=plant_types, locations=locations)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  

        new_user = User(name=name, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        return redirect(url_for('main_page')) 

    return render_template('register.html')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id 
            return redirect(url_for('main_page'))

        return "Invalid credentials, please try again."

    return render_template('login.html')  

@app.route('/tables')
def list_tables():
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    return {"tables": tables}

@app.route('/data')
def display_temp_and_humidity():
    # Query all data from the temp_and_humidity_data table
    data = TempAndHumidityData.query.all()

    # Pass the data to a template to display it
    return render_template('display_data.html', data=data)


@app.route('/seed')
def seed():
    # Call the seed_data function to populate the database
    seed_data()
    return "Seed data has been created!"

#Comment
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

#         time.sleep(5)  # Log every 15 minutes (900 seconds)


if __name__ == "__main__":
    #Comment
    # sensor_thread = threading.Thread(target=log_sensor_data, daemon=True)
    # sensor_thread.start()
    app.run(debug=True)
