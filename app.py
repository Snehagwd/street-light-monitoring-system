from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="********",
        database="street_light_monitoring"
    )
    return connection


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# GET ALL STREET LIGHTS
# =====================================================

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
            sl.status,

            (
                SELECT COUNT(*)
                FROM fault_history fh
                WHERE fh.light_id = sl.light_id
                AND fh.new_status = 'Faulty'
            ) AS fault_count

        FROM street_lights sl

        JOIN locations l
        ON sl.location_id = l.location_id
    """)

    lights = cursor.fetchall()

    for light in lights:

        fault_count = light["fault_count"]

        # Risk Level
        if light["status"] == "Faulty":
            risk_level = "High"

        elif fault_count >= 5:
            risk_level = "High"

        elif fault_count >= 2:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        # Prediction Score
        prediction_score = 0

        if light["status"] == "Faulty":
            prediction_score += 50

        prediction_score += min(fault_count * 10, 40)

        if light["wattage"] >= 100:
            prediction_score += 10

        prediction_score = min(prediction_score, 100)

        # Prediction Level
        if prediction_score >= 70:
            prediction_level = "High"
            prediction = "High chance of failure"

        elif prediction_score >= 40:
            prediction_level = "Medium"
            prediction = "Monitor closely"

        else:
            prediction_level = "Low"
            prediction = "Stable performance"

        light["risk_level"] = risk_level
        light["prediction_score"] = prediction_score
        light["prediction_level"] = prediction_level
        light["prediction"] = prediction

    cursor.close()
    connection.close()

    return jsonify(lights)


# =====================================================
# UPDATE STREET LIGHT STATUS
# =====================================================

@app.route("/update-status/<int:light_id>", methods=["PUT"])
def update_status(light_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    new_status = data.get("status")

    allowed_statuses = [
        "Working",
        "Faulty",
        "Under Maintenance"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get current light
    cursor.execute("""
        SELECT
            sl.status,
            sl.light_code,
            l.area_name,
            l.street_name

        FROM street_lights sl

        JOIN locations l
        ON sl.location_id = l.location_id

        WHERE sl.light_id = %s
    """, (light_id,))

    light = cursor.fetchone()

    if not light:

        cursor.close()
        connection.close()

        return jsonify({
            "error": "Street light not found"
        }), 404

    previous_status = light["status"]

    # Update status
    cursor.execute("""
        UPDATE street_lights
        SET status = %s
        WHERE light_id = %s
    """, (
        new_status,
        light_id
    ))

    # Store event history
    cursor.execute("""
        INSERT INTO fault_history
        (
            light_id,
            previous_status,
            new_status,
            event_time
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """, (
        light_id,
        previous_status,
        new_status,
        datetime.now()
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Street light status updated successfully",
        "light_code": light["light_code"],
        "previous_status": previous_status,
        "new_status": new_status
    })


# =====================================================
# GET FAULTY LIGHTS
# =====================================================

@app.route("/faulty-lights", methods=["GET"])
def get_faulty_lights():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sl.light_id,
            sl.light_code,
            sl.status,
            sl.wattage,
            l.area_name,
            l.street_name,
            l.latitude,
            l.longitude

        FROM street_lights sl

        JOIN locations l
        ON sl.location_id = l.location_id

        WHERE sl.status = 'Faulty'
    """)

    lights = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(lights)


# =====================================================
# FAULT HISTORY
# =====================================================

@app.route("/fault-history", methods=["GET"])
def get_fault_history():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            fh.event_id,
            sl.light_code,
            fh.previous_status,
            fh.new_status,

            DATE_FORMAT(
                fh.event_time,
                '%Y-%m-%d %H:%i:%s'
            ) AS event_time

        FROM fault_history fh

        JOIN street_lights sl
        ON fh.light_id = sl.light_id

        ORDER BY fh.event_time DESC
    """)

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(history)


# =====================================================
# ANALYTICS
# =====================================================

@app.route("/analytics", methods=["GET"])
def analytics():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Total Fault Events
    cursor.execute("""
        SELECT COUNT(*) AS total_fault_events
        FROM fault_history
        WHERE new_status = 'Faulty'
    """)

    result = cursor.fetchone()

    total_fault_events = result["total_fault_events"]

    # Faults by Street Light
    cursor.execute("""
        SELECT
            sl.light_code,

            COUNT(fh.event_id) AS fault_count

        FROM street_lights sl

        LEFT JOIN fault_history fh
        ON sl.light_id = fh.light_id
        AND fh.new_status = 'Faulty'

        GROUP BY
            sl.light_id,
            sl.light_code

        ORDER BY fault_count DESC
    """)

    faults_by_light = cursor.fetchall()

    # Faults by Area
    cursor.execute("""
        SELECT
            l.area_name,

            COUNT(fh.event_id) AS fault_count

        FROM locations l

        JOIN street_lights sl
        ON l.location_id = sl.location_id

        LEFT JOIN fault_history fh
        ON sl.light_id = fh.light_id
        AND fh.new_status = 'Faulty'

        GROUP BY
            l.area_name

        ORDER BY fault_count DESC
    """)

    faults_by_area = cursor.fetchall()

    most_faulty_light = None
    most_affected_area = None

    if faults_by_light:
        most_faulty_light = faults_by_light[0]

    if faults_by_area:
        most_affected_area = faults_by_area[0]

    cursor.close()
    connection.close()

    return jsonify({
        "total_fault_events": total_fault_events,
        "faults_by_light": faults_by_light,
        "faults_by_area": faults_by_area,
        "most_faulty_light": most_faulty_light,
        "most_affected_area": most_affected_area
    })


# =====================================================
# SMART MAINTENANCE PRIORITY
# =====================================================

@app.route("/maintenance-priority", methods=["GET"])
def maintenance_priority():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sl.light_id,
            sl.light_code,
            sl.status,
            sl.wattage,

            l.area_name,
            l.street_name,
            l.latitude,
            l.longitude,

            COUNT(fh.event_id) AS fault_count

        FROM street_lights sl

        JOIN locations l
        ON sl.location_id = l.location_id

        LEFT JOIN fault_history fh
        ON sl.light_id = fh.light_id
        AND fh.new_status = 'Faulty'

        GROUP BY
            sl.light_id,
            sl.light_code,
            sl.status,
            sl.wattage,
            l.area_name,
            l.street_name,
            l.latitude,
            l.longitude
    """)

    lights = cursor.fetchall()

    for light in lights:

        fault_count = light["fault_count"]

        # -----------------------------------------
        # RISK LEVEL
        # -----------------------------------------

        if light["status"] == "Faulty":
            risk_level = "High"

        elif fault_count >= 5:
            risk_level = "High"

        elif fault_count >= 2:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        # -----------------------------------------
        # PRIORITY SCORE
        # -----------------------------------------

        priority_score = fault_count * 20

        if light["status"] == "Faulty":
            priority_score += 50

        if light["wattage"] >= 100:
            priority_score += 10

        priority_score = min(priority_score, 100)

        # -----------------------------------------
        # PRIORITY LEVEL
        # -----------------------------------------

        if priority_score >= 80:
            priority_level = "Critical"

        elif priority_score >= 60:
            priority_level = "High"

        elif priority_score >= 30:
            priority_level = "Medium"

        else:
            priority_level = "Low"

        # -----------------------------------------
        # PREDICTION SCORE
        # -----------------------------------------

        prediction_score = fault_count * 10

        if light["status"] == "Faulty":
            prediction_score += 50

        if light["wattage"] >= 100:
            prediction_score += 10

        prediction_score = min(prediction_score, 100)

        # -----------------------------------------
        # FAILURE PREDICTION
        # -----------------------------------------

        if prediction_score >= 70:
            prediction_level = "High"
            prediction = "High chance of failure"

        elif prediction_score >= 40:
            prediction_level = "Medium"
            prediction = "Monitor closely"

        else:
            prediction_level = "Low"
            prediction = "Stable performance"

        # Add calculated values
        light["risk_level"] = risk_level
        light["priority_score"] = priority_score
        light["priority_level"] = priority_level
        light["prediction_score"] = prediction_score
        light["prediction_level"] = prediction_level
        light["prediction"] = prediction

    # Sort highest priority first
    lights.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    # Add ranking
    for index, light in enumerate(lights):
        light["rank"] = index + 1

    cursor.close()
    connection.close()

    return jsonify(lights)


# =====================================================
# SMART NOTIFICATIONS
# =====================================================

@app.route("/notifications", methods=["GET"])
def get_notifications():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            fh.event_id,
            sl.light_code,
            l.area_name,
            l.street_name,
            fh.previous_status,
            fh.new_status,

            DATE_FORMAT(
                fh.event_time,
                '%Y-%m-%d %H:%i:%s'
            ) AS event_time

        FROM fault_history fh

        JOIN street_lights sl
        ON fh.light_id = sl.light_id

        JOIN locations l
        ON sl.location_id = l.location_id

        ORDER BY fh.event_time DESC

        LIMIT 10
    """)

    notifications = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(notifications)


# =====================================================
# API HEALTH CHECK
# =====================================================

@app.route("/api-status", methods=["GET"])
def api_status():

    return jsonify({
        "status": "success",
        "message": "Street Light Monitoring System API is running"
    })


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
