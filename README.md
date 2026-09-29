# 🌱 Cloud-Connected Smart Plant Care & Watering System

A cloud-connected IoT plant monitoring and automated watering system using a virtual sensor simulator, FastAPI backend, Firebase Firestore, React dashboard, and a virtual pump.

The project demonstrates an end-to-end IoT-to-cloud workflow without requiring physical IoT hardware.

## 🚀 Live Application

**Live Dashboard:** https://smart-plant-care-watering-system.vercel.app

**Backend API:** https://smart-plant-care-watering-system.onrender.com

**API Documentation:** https://smart-plant-care-watering-system.onrender.com/docs


## 📌 Overview

The Smart Plant Care & Watering System monitors plant conditions using simulated IoT sensor data.

The virtual sensor simulator generates soil moisture, temperature, humidity, light level, timestamp, and device ID data.

The sensor readings are sent to a cloud-hosted FastAPI backend through REST APIs.

The backend stores sensor data in Firebase Firestore and applies automated watering logic based on configurable soil-moisture thresholds.

A React dashboard provides remote monitoring of the plant and displays sensor history, watering events, alerts, analytics, device status, and pump status.

## 🎯 Objectives

- Demonstrate IoT-to-cloud communication
- Simulate IoT sensors without physical hardware
- Store sensor readings in a cloud database
- Provide REST APIs for sensor communication
- Implement automated watering decisions
- Monitor plant conditions remotely
- Maintain historical sensor data
- Track watering events
- Provide alerts and analytics
- Deploy the application using cloud platforms
- Demonstrate cloud computing concepts through an end-to-end project

## ✨ Features

### 🌱 Virtual IoT Sensor

The Python simulator generates realistic environmental readings and sends them to the cloud backend.

### ☁️ Cloud Backend

FastAPI provides REST APIs for sensor data, device information, latest readings, historical readings, pump status, automatic watering status, moisture threshold, manual watering, watering history, alerts, and analytics.

### 💧 Automated Watering

The system continuously evaluates soil moisture.

When soil moisture falls below the configured threshold:

Soil Moisture < Threshold → Automatic Watering Triggered → Virtual Pump ON → Moisture Increases → Target Moisture Reached → Virtual Pump OFF

### 📊 Monitoring Dashboard

The React dashboard displays soil moisture, temperature, humidity, light level, plant status, pump status, automatic watering status, moisture threshold, historical moisture data, watering history, alerts, analytics, and device information.

### 🔔 Alerts

The system supports monitoring conditions such as low soil moisture, device status, sensor activity, and other configurable plant conditions.

## 🏗️ Architecture

Virtual Plant / Sensor Simulator
        │
        │ HTTPS / REST API
        ▼
FastAPI Backend
        │
   ┌────┴────┐
   ▼         ▼
Firebase   Watering
Firestore  Automation
   │         │
   │         ▼
   │      Virtual Pump
   │
   ▼
React Dashboard
   │
   ▼
User

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Sensor Simulation | Python |
| Backend | FastAPI |
| Database | Firebase Firestore |
| Frontend | React |
| Build Tool | Vite |
| Communication | REST API / HTTPS |
| Backend Deployment | Render |
| Frontend Deployment | Vercel |
| Testing | Pytest |
| Version Control | Git & GitHub |

## 📡 Sensor Simulation

The project does not require physical IoT hardware.

The Python simulator generates synthetic sensor readings and sends them to the backend.

Example sensor data:

{
  "device_id": "PLANT-001",
  "soil_moisture": 29,
  "temperature": 27.4,
  "humidity": 64,
  "light_level": 72,
  "timestamp": "2026-09-26T10:00:00Z"
}

The simulator also models gradual environmental changes rather than generating completely random values.

## 💾 Cloud Database

Firebase Firestore stores device information, current sensor data, pump status, moisture threshold, automatic watering status, sensor readings, and watering events.

Example structure:

devices
└── PLANT-001
    ├── Device information
    ├── Current sensor data
    ├── Pump status
    ├── Moisture threshold
    ├── Automatic watering status
    ├── readings/
    └── watering_events/

Sensor readings and watering events are stored in the cloud for historical monitoring and analysis.

## 🔌 REST API

Important API endpoints include:

POST   /api/sensors/data

GET    /api/devices

GET    /api/devices/{device_id}/latest

GET    /api/devices/{device_id}/history

GET    /api/devices/{device_id}/pump-status

GET    /api/devices/{device_id}/auto-status

PUT    /api/devices/{device_id}/auto-water

GET    /api/devices/{device_id}/threshold

PUT    /api/devices/{device_id}/threshold

POST   /api/devices/{device_id}/water

GET    /api/devices/{device_id}/watering-history

GET    /api/devices/{device_id}/alerts

GET    /api/devices/{device_id}/analytics

Interactive API documentation:

https://smart-plant-care-watering-system.onrender.com/docs

## 🌿 Plant Watering Logic

The system uses a configurable soil-moisture threshold.

For the demonstration configuration:

Threshold = 30%

Example flow:

55% → Healthy
50% → Moisture decreasing
45% → Moisture decreasing
39% → Moisture decreasing
34% → Moisture decreasing
29% → Below threshold
     ↓
Virtual Pump ON
     ↓
35% → 42% → 48%
     ↓
Virtual Pump OFF

The watering event is recorded in Firestore.

## 📊 Dashboard

The dashboard provides a centralized view of the plant system.

It includes current sensor values, plant health status, pump status, automatic watering controls, moisture threshold configuration, historical moisture chart, watering history, alerts, analytics, device status, and backend status.

## 🧪 Testing

The backend was tested using automated tests covering core system functionality.

Testing includes sensor simulator behavior, API communication, sensor data validation, database operations, latest readings, historical readings, watering logic, threshold handling, pump activation, pump deactivation, watering history, alerts, and device monitoring.

Automated test result:

25 passed

## ☁️ Cloud Deployment

### Frontend

The React + Vite frontend is deployed using Vercel.

React + Vite → Vercel → Live Dashboard

### Backend

The FastAPI backend is deployed using Render.

FastAPI → Render → Cloud REST API

### Database

Firebase Firestore is used as the cloud database.

## 🔐 Security Considerations

The project follows basic cloud security practices including environment variables for configuration, service-account credentials excluded from Git, .env files excluded through .gitignore, input validation using Pydantic, HTTPS communication for deployed services, cloud database access through the backend, and secret credentials not committed to GitHub.

## 📈 Scalability

The architecture can be extended from a single virtual plant to multiple devices.

A larger production architecture could introduce IoT gateways, MQTT brokers, API gateways, serverless functions, managed databases, message queues, event streams, caching, autoscaling, time-series databases, and monitoring systems.

## 📁 Project Structure

Cloud-Connected Smart Plant Care and Watering System/
│
├── sensor_simulator/
│   ├── config.py
│   └── simulator.py
│
├── backend/
│   └── app/
│       ├── main.py
│       └── firebase_config.py
│
├── automation/
│   ├── plant_profiles.py
│   └── watering_engine.py
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── tests/
├── docs/
├── reports/
├── sample_data/
├── screenshots/
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md

## ▶️ Running Locally

### 1. Clone the repository

git clone https://github.com/Ayushman7985-outlook/smart-plant-care-watering-system.git

cd smart-plant-care-watering-system

### 2. Create Python environment

python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1

### 3. Install backend dependencies

pip install -r requirements.txt

### 4. Start backend

uvicorn backend.app.main:app --reload

### 5. Start frontend

cd frontend

npm install

npm run dev

### 6. Start sensor simulator

Open another terminal:

cd sensor_simulator

python simulator.py

## 🧑‍💻 Project Demonstration

The complete demonstration follows this workflow:

Virtual Sensor
      ↓
Generate Sensor Reading
      ↓
REST API
      ↓
FastAPI Backend
      ↓
Firebase Firestore
      ↓
Watering Automation
      ↓
Virtual Pump
      ↓
React Dashboard
      ↓
User

This demonstrates the complete flow from simulated IoT data to cloud storage, automated decision-making, and remote monitoring.

## 🔮 Future Improvements

Possible future enhancements include ESP32 hardware integration, real soil moisture sensors, real temperature/humidity sensors, physical water pump integration, MQTT communication, user authentication, multiple plant management, email/SMS/push notifications, advanced plant-specific watering models, machine-learning-based watering prediction, advanced cloud monitoring, and a mobile application.

## 📚 Learning Outcomes

This project provided practical exposure to cloud computing, IoT architecture, Python, FastAPI, REST APIs, Firebase Firestore, React, Vite, cloud deployment, sensor simulation, automation logic, database design, testing, Git and GitHub, and cloud-based monitoring.

## 👨‍💻 Author

**Ayushman Dubey**

B.Tech Information Technology

