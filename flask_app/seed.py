from werkzeug.security import generate_password_hash
from db import db, User, PlantType, Location, Plant, TempAndHumidityData
from datetime import datetime  # Import datetime module

def seed_data():
    # Clear existing data (be cautious in production!)
    db.session.query(Plant).delete()
    db.session.query(User).delete()
    db.session.query(Location).delete()
    db.session.query(PlantType).delete()
    db.session.query(TempAndHumidityData).delete()
    db.session.commit()  # Commit deletions first

    # Create new seed data
    plant_type_1 = PlantType(name='Succulent', water_requirement='Low')
    plant_type_2 = PlantType(name='Cactus', water_requirement='Low')
    plant_type_3 = PlantType(name='Fern', water_requirement='High')

    location_1 = Location(name='Living Room')
    location_2 = Location(name='Bedroom')
    location_3 = Location(name='Balcony')

    user_1 = User(name='Alice', email='alice@example.com', password=generate_password_hash('password123'))
    user_2 = User(name='Bob', email='bob@example.com', password=generate_password_hash('password456'))

    # Add seed data to session and commit
    db.session.add_all([plant_type_1, plant_type_2, plant_type_3, location_1, location_2, location_3, user_1, user_2])
    db.session.commit()  # Commit after adding users, locations, and plant types

    # Convert string dates to datetime.date objects
    date_1 = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
    date_2 = datetime.strptime('2024-02-01', '%Y-%m-%d').date()
    date_3 = datetime.strptime('2024-03-01', '%Y-%m-%d').date()

    # Create plants with the correct foreign keys and date objects
    plant_1 = Plant(name='Aloe Vera', plant_type_id=plant_type_1.id, location_id=location_1.id, date_planted=date_1, user_id=user_1.id)
    plant_2 = Plant(name='Cactus', plant_type_id=plant_type_2.id, location_id=location_2.id, date_planted=date_2, user_id=user_2.id)
    plant_3 = Plant(name='Boston Fern', plant_type_id=plant_type_3.id, location_id=location_3.id, date_planted=date_3, user_id=user_1.id)

    # Add the plants to the session and commit
    db.session.add_all([plant_1, plant_2, plant_3])
    db.session.commit()

    print("Seed data has been created.")
