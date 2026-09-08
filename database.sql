CREATE DATABASE IF NOT EXISTS street_light_monitoring;

USE street_light_monitoring;

CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    area_name VARCHAR(100),
    street_name VARCHAR(150),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7)
);

CREATE TABLE IF NOT EXISTS street_lights (
    light_id INT AUTO_INCREMENT PRIMARY KEY,
    light_code VARCHAR(50) UNIQUE,
    location_id INT,
    installation_date DATE,
    light_type VARCHAR(50),
    wattage INT,
    status VARCHAR(30),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    light_id INT,
    voltage DECIMAL(10,2),
    current DECIMAL(10,2),
    power_consumption DECIMAL(10,2),
    reading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (light_id) REFERENCES street_lights(light_id)
);

CREATE TABLE IF NOT EXISTS faults (
    fault_id INT AUTO_INCREMENT PRIMARY KEY,
    light_id INT,
    fault_type VARCHAR(100),
    fault_severity VARCHAR(50),
    detected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fault_status VARCHAR(30),
    FOREIGN KEY (light_id) REFERENCES street_lights(light_id)
);

CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    light_id INT,
    maintenance_date DATE,
    technician_name VARCHAR(100),
    maintenance_status VARCHAR(50),
    remarks TEXT,
    FOREIGN KEY (light_id) REFERENCES street_lights(light_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(50)
);