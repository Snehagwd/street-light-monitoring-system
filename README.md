# 💡 Centralized Monitoring System for Street Light Fault Detection and Location Tracking

A centralized web-based monitoring system designed to manage street lights, detect faults, track locations, analyze fault history, and prioritize maintenance activities.

The system provides a single dashboard for monitoring multiple street lights and supports smart maintenance decision-making using fault history, risk levels, prediction scores, and maintenance priority.

---

## 📌 Project Overview

Street lighting infrastructure requires regular monitoring and maintenance. In traditional systems, faults are often reported manually, which can increase maintenance response time and make it difficult to track recurring faults.

This project provides a centralized monitoring platform that allows administrators to:

- Monitor the operational status of street lights.
- Simulate and record street light faults.
- Track street light locations using stored latitude and longitude coordinates.
- Analyze historical fault events.
- Identify frequently faulty street lights and affected areas.
- Calculate risk and prediction levels.
- Prioritize maintenance activities.
- Maintain an event and notification history.

---

# ✨ Key Features

## 📊 Centralized Dashboard

Provides an overview of the complete street light monitoring system.

Displays:

- Total Street Lights
- Working Lights
- Faulty Lights
- Lights Under Maintenance

---

## 🚨 Fault Detection and Simulation

Street light status can be updated through the dashboard.

Supported statuses:

- 🟢 Working
- 🔴 Faulty
- 🟠 Under Maintenance

When a status is changed, the system records the event in the fault history database.

---

## 🔍 Smart Search and Filtering

Users can search and filter street lights based on:

- Light Code
- Area
- Street
- Status
- Risk Level
- Prediction Level

---

## 📍 Location Tracking

Each street light is associated with a location containing:

- Area Name
- Street Name
- Latitude
- Longitude

The dashboard provides a visual representation of monitored street light locations.

---

## ⚠️ Risk Assessment

The system automatically calculates a risk level for each street light.

Risk levels include:

- Low
- Medium
- High

The calculation considers factors such as:

- Current street light status
- Number of previous fault events

---

## 🤖 Smart Fault Prediction

A rule-based prediction score is calculated for each street light.

The prediction considers:

- Current operational status
- Historical fault count
- Street light wattage

Prediction levels include:

- Low — Stable Performance
- Medium — Monitor Closely
- High — High Chance of Failure

---

## 🥇 Smart Maintenance Priority

The system ranks street lights according to maintenance priority.

Priority calculation considers:

- Fault Count
- Current Status
- Wattage
- Historical Fault Events

Priority levels include:

- Low
- Medium
- High
- Critical

This helps maintenance teams identify which street lights require immediate attention.

---

## 📊 Fault Analytics

The system provides analytics for:

### Fault Events by Street Light

Identifies street lights with the highest number of recorded faults.

### Fault Events by Area

Identifies geographical areas with a higher concentration of street light faults.

---

## 🔔 Smart Notification Center

The notification system displays recent street light status changes.

Each notification includes:

- Street Light Code
- Previous Status
- New Status
- Area
- Street
- Event Time

---

## 📜 Fault History and Event Log

Every status update is recorded in the database.

The event log stores:

- Event ID
- Street Light Code
- Previous Status
- New Status
- Event Time

This creates a maintenance history for each monitored street light.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │     Web Dashboard       │
                    │                         │
                    │ HTML | CSS | JavaScript │
                    └────────────┬────────────┘
                                 │
                                 │ HTTP / REST API
                                 ▼
                    ┌─────────────────────────┐
                    │      Flask Backend      │
                    │                         │
                    │ Fault Detection         │
                    │ Risk Calculation        │
                    │ Prediction              │
                    │ Maintenance Priority    │
                    │ Analytics               │
                    └────────────┬────────────┘
                                 │
                                 │ SQL Queries
                                 ▼
                    ┌─────────────────────────┐
                    │     MySQL Database      │
                    │                         │
                    │ Locations               │
                    │ Street Lights           │
                    │ Fault History           │
                    └─────────────────────────┘
