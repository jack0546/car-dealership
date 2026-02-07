import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'dealership.db')

def get_conn():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        import psycopg2
        return psycopg2.connect(database_url, sslmode='require')
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    
    # Use SERIAL for PostgreSQL and AUTOINCREMENT for SQLite
    is_postgres = os.environ.get('DATABASE_URL') is not None
    id_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    text_type = "TEXT" 
    
    # Create Cars table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS cars (
            id {id_type},
            make {text_type} NOT NULL,
            model {text_type} NOT NULL,
            year INTEGER NOT NULL,
            price REAL NOT NULL,
            mileage INTEGER,
            transmission {text_type},
            fuel_type {text_type},
            description {text_type},
            image_url {text_type},
            featured BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Create Inquiries table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS inquiries (
            id {id_type},
            car_id INTEGER,
            name {text_type} NOT NULL,
            email {text_type} NOT NULL,
            phone {text_type},
            message {text_type},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES cars (id)
        )
    ''')
    
    # Insert some sample data
    cursor.execute('SELECT COUNT(*) FROM cars')
    if cursor.fetchone()[0] == 0: 
        sample_cars = [
            ('Mercedes-Benz', 'S-Class', 2023, 110000, 5000, 'Automatic', 'Petrol', 'The pinnacle of luxury and technology.', 'https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8', True),
            ('BMW', 'M4 Competition', 2024, 85000, 1200, 'Automatic', 'Petrol', 'Unrivaled performance and precision.', 'https://images.unsplash.com/photo-1555215695-3004980ad54e', True),
            ('Audi', 'RS7 Sportback', 2023, 125000, 3500, 'Automatic', 'Petrol', 'Elegance meets everyday usability.', 'https://images.unsplash.com/photo-1606148632349-5509e51121d5', True),
            ('Porsche', '911 Carrera S', 2024, 135000, 800, 'Manual', 'Petrol', 'The eternal sports car icon.', 'https://images.unsplash.com/photo-1503376780353-7e6692767b70', True),
            ('Tesla', 'Model S Plaid', 2023, 95000, 10000, 'Automatic', 'Electric', 'Beyond fast. 0-60 in 1.99s.', 'https://images.unsplash.com/photo-1617788138017-80ad40651399', False),
            ('Range Rover', 'Sport', 2024, 115000, 2000, 'Automatic', 'Hybrid', 'Capable luxury for any terrain.', 'https://images.unsplash.com/photo-1550064824-8f993041ffee', False),
            ('Ferrari', 'F8 Tributo', 2023, 280000, 500, 'Automatic', 'Petrol', 'A celebration of the excellence of the V8 engine.', 'https://images.unsplash.com/photo-1592198084033-aade902d1aae', True),
            ('Lamborghini', 'Huracan Evo', 2024, 260000, 300, 'Automatic', 'Petrol', 'Designed to amplify your emotions.', 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b', True),
            ('Aston Martin', 'DB11', 2023, 205000, 1500, 'Automatic', 'Petrol', 'The most efficient and powerful DB production model.', 'https://images.unsplash.com/photo-1619405399517-d7fce0f13302', True),
            ('Bentley', 'Continental GT', 2024, 240000, 200, 'Automatic', 'Petrol', 'Unrivaled craftsmanship and breathtaking performance.', 'https://images.unsplash.com/photo-1580273916550-e323be2ae537', False),
            ('Mclaren', '720S', 2023, 299000, 900, 'Automatic', 'Petrol', 'Lighter, stronger, and faster than its predecessor.', 'https://images.unsplash.com/photo-1621135802920-133df287f89c', False),
            ('Rolls-Royce', 'Ghost', 2024, 350000, 100, 'Automatic', 'Petrol', 'The most technologically advanced Rolls-Royce yet.', 'https://images.unsplash.com/photo-1631215106517-57945d98ca57', True),
            ('Bugatti', 'Chiron Pur Sport', 2023, 3600000, 50, 'Automatic', 'Petrol', 'The purest expression of driving performance.', 'https://images.unsplash.com/photo-1517524008436-bbdb53c54434', False),
            ('Maserati', 'MC20', 2023, 215000, 1200, 'Automatic', 'Petrol', 'A state-of-the-art super sports car.', 'https://images.unsplash.com/photo-1614200187524-dc4b892acf16', False),
            ('Jaguar', 'F-Type SVR', 2024, 105000, 4000, 'Automatic', 'Petrol', 'Performance that takes your breath away.', 'https://images.unsplash.com/photo-1589133446549-c189c426e831', False),
            ('Lexus', 'LC 500', 2023, 98000, 5000, 'Automatic', 'Petrol', 'The ultimate combination of design and engineering.', 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d', False),
            ('Audi', 'R8 V10 Plus', 2023, 195000, 1000, 'Automatic', 'Petrol', 'A race car for the road.', 'https://images.unsplash.com/photo-1511919884226-fd3cad34687c', True),
            ('BMW', 'M8 Competition', 2024, 130000, 500, 'Automatic', 'Petrol', 'The peak of BMW performance.', 'https://images.unsplash.com/photo-1603386349600-b69677353f4d', False),
            ('Porsche', 'Taycan Turbo S', 2024, 185000, 100, 'Automatic', 'Electric', 'Soul, electrified.', 'https://images.unsplash.com/photo-1594502184342-2e12f877aa73', True),
            ('Lamborghini', 'Urus', 2023, 230000, 2500, 'Automatic', 'Petrol', 'The soul of a super sports car and the functionality of an SUV.', 'https://images.unsplash.com/photo-1549399542-7e3f8b79cce9', False),
            ('Mercedes-AMG', 'GT R', 2023, 160000, 1500, 'Automatic', 'Petrol', 'Born on the Nurburgring.', 'https://images.unsplash.com/photo-1617469767053-d3b508a0d825', True),
            ('Ferrari', 'SF90 Stradale', 2024, 510000, 50, 'Automatic', 'Hybrid', 'Pushing the boundaries of performance.', 'https://images.unsplash.com/photo-1592198084033-aade902d1aae', False),
            ('Koenigsegg', 'Jesko', 2024, 3000000, 10, 'Automatic', 'Petrol', 'The ultimate megacar.', 'https://images.unsplash.com/photo-1621135802920-133df287f89c', True),
            ('Pagani', 'Huayra', 2023, 2600000, 100, 'Automatic', 'Petrol', 'Art on wheels.', 'https://images.unsplash.com/photo-1627454820516-dc707994646a', False),
            ('Ford', 'GT', 2022, 500000, 200, 'Automatic', 'Petrol', 'The culmination of Ford specialized engineering.', 'https://images.unsplash.com/photo-1593414220436-13004940562e', True),
            ('Chevrolet', 'Corvette Z06', 2024, 110000, 50, 'Automatic', 'Petrol', 'The mid-engine icon redefined.', 'https://images.unsplash.com/photo-1632766348421-3a05fced4f5e', False)
        ]
        
        # Placeholders for bulk insert
        placeholders = "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" if is_postgres else "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        query = f"INSERT INTO cars (make, model, year, price, mileage, transmission, fuel_type, description, image_url, featured) VALUES {placeholders}"
        
        if is_postgres:
            from psycopg2.extras import execute_values
            execute_values(cursor, "INSERT INTO cars (make, model, year, price, mileage, transmission, fuel_type, description, image_url, featured) VALUES %s", sample_cars)
        else:
            cursor.executemany(query, sample_cars)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
