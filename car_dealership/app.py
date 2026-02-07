from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from database import DB_PATH, init_db

app = Flask(__name__)
CORS(app)

# Initialize DB on startup
if not os.path.exists(DB_PATH):
    init_db()

# Database Configuration - Detection between local and production
DATABASE_URL = os.environ.get('DATABASE_URL')

@app.route('/api/seed', methods=['GET'])
def manual_seed():
    try:
        init_db()
        return jsonify({"success": True, "message": "Database initialized and seeded"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def get_db_connection():
    if DATABASE_URL:
        # For production use with PostgreSQL (requires psycopg2)
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    else:
        # Use local SQLite for development
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

@app.route('/api/cars', methods=['GET'])
def get_cars():
    featured = request.args.get('featured')
    make = request.args.get('make')
    
    conn = get_db_connection()
    is_postgres = os.environ.get('DATABASE_URL') is not None
    placeholder = "%s" if is_postgres else "?"
    
    query = "SELECT * FROM cars WHERE 1=1"
    params = []
    
    if featured:
        query += f" AND featured = {placeholder}"
        params.append(True if featured.lower() == 'true' else False)
    
    if make:
        query += f" AND make LIKE {placeholder}"
        params.append(f"%{make}%")
        
    try:
        if is_postgres:
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query, params)
            cars = cursor.fetchall()
            results = [dict(ix) for ix in cars]
        else:
            cars = conn.execute(query, params).fetchall()
            results = [dict(ix) for ix in cars]
        
        conn.close()
        return jsonify(results)
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/cars/<int:car_id>', methods=['GET'])
def get_car(car_id):
    conn = get_db_connection()
    is_postgres = os.environ.get('DATABASE_URL') is not None
    placeholder = "%s" if is_postgres else "?"
    
    try:
        if is_postgres:
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(f"SELECT * FROM cars WHERE id = {placeholder}", (car_id,))
            car = cursor.fetchone()
        else:
            car = conn.execute(f"SELECT * FROM cars WHERE id = {placeholder}", (car_id,)).fetchone()
        
        conn.close()
        if car is None:
            return jsonify({"error": "Car not found"}), 404
        return jsonify(dict(car))
    except Exception as e:
        if conn: conn.close()
        return jsonify({"error": str(e)}), 500

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# EMAIL CONFIGURATION (Update these with your credentials)
SENDER_EMAIL = "narhsnazzisco@gmail.com"
# For local testing, your password remains. For production, the server will use an environment variable.
SENDER_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "Alfred0532340875194400") 

def send_email_notification(client_name, client_email, client_message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = SENDER_EMAIL  # Send the notification to yourself
        msg['Subject'] = f"New Car Inquiry from {client_name}"

        body = f"You have received a new message from your website:\n\n" \
               f"Name: {client_name}\n" \
               f"Email: {client_email}\n" \
               f"Message: {client_message}"
        
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/api/inquiry', methods=['POST'])
def submit_inquiry():
    data = request.json
    print(f"Received inquiry from: {data.get('email')}")
    car_id = data.get('car_id')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')
    
    if not all([name, email]):
        print("Error: Name and email are required")
        return jsonify({"error": "Name and email are required"}), 400
        
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO inquiries (car_id, name, email, phone, message)
        VALUES (?, ?, ?, ?, ?)
    ''', (car_id, name, email, phone, message))
    conn.commit()
    conn.close()
    print("Inquiry saved to database.")

    # Trigger Gmail Notification
    success = send_email_notification(name, email, message)
    if success:
        print("Email notification sent successfully.")
    else:
        print("Email notification failed. Check SENDER_PASSWORD and Gmail App Password settings.")
    
    return jsonify({"success": True, "message": "Inquiry received"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
