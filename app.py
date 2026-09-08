from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# MySQL Database Connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root12345",
        database="street_light_monitoring"
    )
    return connection


# Test API
@app.route("/")
def home():
    return jsonify({
        "message": "Street Light Monitoring System API is running successfully!"
    })


# Get all street lights
@app.route("/streetlights", methods=["GET"])
def get_street_lights():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            sl.light_id,
            sl.light_code,
            l.area_name,
            l.street_name,
            l.latitude,
            l.longitude,
            sl.light_type,
            sl.wattage,
            sl.status
        FROM street_lights sl
        JOIN locations l ON sl.location_id = l.location_id
    """)

    street_lights = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(street_lights)


if __name__ == "__main__":
    app.run(debug=True)