import threading
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, db, User, PlantType, Location, Plant, dht22Data, tsl2561Data  # Import models and init_db
from datetime import datetime 
from seed import seed_data
from functools import wraps
# from sensors import log_sensor_data

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/Hydrabloom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.secret_key = 'Richy123'

init_db(app)

@app.route('/')
def index():
    return render_template('index.html')  # Render the home page

@app.route('/')
def home():
    plant_types = PlantType.query.all() 
    return render_template('register.html', plant_types=plant_types)

@app.route('/about')
def about():
    return render_template('about.html')  

@app.route('/sign')
def sign():
    return render_template('sign.html') 

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
        
        new_user = User(name=name, email=email, password=password, is_admin=False)

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
    return render_template('display_data.html')


@app.route('/seed')
def seed():
    seed_data()
    return "Seed data has been created!"

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login')) 
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return redirect(url_for('main_page'))  
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/user/<int:user_id>/details')
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    plants = Plant.query.filter_by(user_id=user.id).all()
    return render_template('user_details.html', user=user, plants=plants)

@app.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

  
    new_user_id = 1  
    plants = Plant.query.filter_by(user_id=user.id).all()
    for plant in plants:
        plant.user_id = new_user_id  
    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()  # Clear the session data
    return redirect(url_for('login'))  # Redirect to the login page or home page


@app.route('/register_plant', methods=['GET', 'POST'])
@admin_required  
def register_plant():
    if request.method == 'POST':
        user_id = request.form['user_id']  
        name = request.form['name']  
        plant_type_id = request.form['plant_type']  
        location_id = request.form['location'] 
        date_planted = request.form['date_planted']  
        
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
    users = User.query.all()  
    return render_template('register_plant.html', plant_types=plant_types, locations=locations, users=users)


@app.route('/api/store_dht22_data', methods=['POST'])
def store_dht22_data():
    data = request.get_json()
    
    if 'temperature' not in data or 'humidity' not in data:
        return jsonify({'error': 'Missing temperature or humidity data'}), 400
    
    # Store DHT22 data
    new_data = dht22Data(
        temperature=data['temperature'],
        humidity=data['humidity']
    )
    
    db.session.add(new_data)
    db.session.commit()
    
    return jsonify({'message': 'DHT22 data stored successfully'}), 201


@app.route('/api/store_tsl2561_data', methods=['POST'])
def store_tsl2561_data():
    data = request.get_json()
    
    if 'lux' not in data:
        return jsonify({'error': 'Missing lux data'}), 400
    
    # Store TSL2561 data
    new_data = tsl2561Data(
        lux=data['lux']
    )
    
    db.session.add(new_data)
    db.session.commit()
    
    return jsonify({'message': 'TSL2561 data stored successfully'}), 201

if __name__ == "__main__":
    # sensor_thread = threading.Thread(target=log_sensor_data, daemon=True)
    # sensor_thread.start()

    app.run(debug=True)