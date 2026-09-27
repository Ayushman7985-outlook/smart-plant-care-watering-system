from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.firebase_config import db
from automation.watering_engine import (
    activate_virtual_pump,
    process_reading,
)


app = FastAPI(
    title="Cloud-Connected Smart Plant Care API",
    description="REST API for the Smart Plant Care and Watering System.",
    version="1.0.0",
)


# Allow the React dashboard to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SensorReading(BaseModel):
    device_id: str = Field(min_length=1)
    soil_moisture: float = Field(ge=0, le=100)
    temperature: float = Field(ge=-20, le=60)
    humidity: float = Field(ge=0, le=100)
    light_level: float = Field(ge=0, le=100)
    timestamp: datetime


class ThresholdUpdate(BaseModel):
    threshold: float = Field(ge=0, le=100)


@app.get("/")
def root():
    return {
        "message": "Smart Plant Care API is running",
        "status": "online",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/sensors/data")
def receive_sensor_data(reading: SensorReading):
    reading_data = reading.model_dump()

    device_ref = db.collection("devices").document(
        reading.device_id
    )

    device_ref.set(
        {
            "device_id": reading.device_id,
            "last_seen": reading.timestamp,
            "last_reading": reading_data,
        },
        merge=True,
    )

    device_ref.collection("readings").add(
        reading_data
    )

    watering_result = process_reading(
        reading.device_id,
        reading.soil_moisture,
    )

    return {
        "message": "Sensor reading stored in Firestore",
        "device_id": reading.device_id,
        "timestamp": reading.timestamp,
        "watering": watering_result,
    }


@app.get("/api/devices")
def get_devices():
    devices = []

    for document in db.collection("devices").stream():
        device = document.to_dict()
        device["device_id"] = document.id

        devices.append(device)

    return {
        "count": len(devices),
        "devices": devices,
    }


@app.get("/api/devices/{device_id}/latest")
def get_latest_reading(device_id: str):
    device = (
        db.collection("devices")
        .document(device_id)
        .get()
    )

    if not device.exists:
        return {
            "message": "No readings found for this device",
            "device_id": device_id,
        }

    return device.to_dict().get(
        "last_reading",
        {
            "message": "No latest reading available",
            "device_id": device_id,
        },
    )


@app.get("/api/devices/{device_id}/pump-status")
def get_pump_status(device_id: str):
    device = (
        db.collection("devices")
        .document(device_id)
        .get()
    )

    if not device.exists:
        return {
            "device_id": device_id,
            "pump_status": "OFF",
        }

    return {
        "device_id": device_id,
        "pump_status": device.to_dict().get(
            "pump_status",
            "OFF",
        ),
    }


@app.get("/api/devices/{device_id}/auto-status")
def get_auto_status(device_id: str):
    device = (
        db.collection("devices")
        .document(device_id)
        .get()
    )

    if not device.exists:
        return {
            "device_id": device_id,
            "auto_watering_enabled": False,
        }

    return {
        "device_id": device_id,
        "auto_watering_enabled": device.to_dict().get(
            "auto_watering_enabled",
            True,
        ),
    }


@app.put("/api/devices/{device_id}/auto-water")
def set_auto_watering(
    device_id: str,
    enabled: bool,
):
    device_ref = db.collection("devices").document(
        device_id
    )

    device = device_ref.get()

    if not device.exists:
        return {
            "device_id": device_id,
            "message": "Device not found",
        }

    device_ref.set(
        {
            "auto_watering_enabled": enabled,
        },
        merge=True,
    )

    return {
        "device_id": device_id,
        "auto_watering_enabled": enabled,
        "message": (
            "Automatic watering enabled"
            if enabled
            else "Automatic watering disabled"
        ),
    }


@app.get("/api/devices/{device_id}/threshold")
def get_threshold(device_id: str):
    device = (
        db.collection("devices")
        .document(device_id)
        .get()
    )

    if not device.exists:
        return {
            "device_id": device_id,
            "moisture_threshold": 30,
        }

    return {
        "device_id": device_id,
        "moisture_threshold": device.to_dict().get(
            "moisture_threshold",
            30,
        ),
    }


@app.put("/api/devices/{device_id}/threshold")
def update_threshold(
    device_id: str,
    threshold_data: ThresholdUpdate,
):
    device_ref = db.collection("devices").document(
        device_id
    )

    device = device_ref.get()

    if not device.exists:
        return {
            "device_id": device_id,
            "message": "Device not found",
        }

    device_ref.set(
        {
            "moisture_threshold": threshold_data.threshold,
        },
        merge=True,
    )

    return {
        "device_id": device_id,
        "moisture_threshold": threshold_data.threshold,
        "message": "Moisture threshold updated",
    }


@app.get("/api/devices/{device_id}/history")
def get_reading_history(device_id: str):
    device_ref = db.collection("devices").document(
        device_id
    )

    readings = []

    for document in (
        device_ref
        .collection("readings")
        .order_by("timestamp")
        .stream()
    ):
        reading = document.to_dict()

        if isinstance(
            reading.get("timestamp"),
            datetime,
        ):
            reading["timestamp"] = (
                reading["timestamp"].isoformat()
            )

        readings.append(reading)

    return {
        "device_id": device_id,
        "count": len(readings),
        "readings": readings,
    }


@app.get("/api/devices/{device_id}/watering-history")
def get_watering_history(device_id: str):
    device_ref = db.collection("devices").document(
        device_id
    )

    events = []

    for document in (
        device_ref
        .collection("watering_events")
        .stream()
    ):
        event = document.to_dict()

        for field in [
            "timestamp",
            "completed_at",
        ]:
            if isinstance(
                event.get(field),
                datetime,
            ):
                event[field] = (
                    event[field].isoformat()
                )

        events.append(event)

    events.sort(
        key=lambda item: item.get(
            "timestamp",
            "",
        )
    )

    return {
        "device_id": device_id,
        "count": len(events),
        "events": events,
    }


@app.post("/api/devices/{device_id}/water")
def manual_water(device_id: str):
    device_ref = db.collection("devices").document(
        device_id
    )

    device = device_ref.get()

    if not device.exists:
        return {
            "device_id": device_id,
            "pump_status": "OFF",
            "message": "Device not found",
        }

    device_data = device.to_dict()

    current_reading = device_data.get(
        "last_reading",
        {},
    )

    current_moisture = current_reading.get(
        "soil_moisture",
        0,
    )

    if device_data.get(
        "pump_status",
        "OFF",
    ) == "ON":
        return {
            "device_id": device_id,
            "pump_status": "ON",
            "message": "Pump is already running",
        }

    watering_result = activate_virtual_pump(
        device_id,
        current_moisture,
        trigger_type="manual",
    )

    return {
        "device_id": device_id,
        "watering_type": "manual",
        "moisture_before": current_moisture,
        "watering": watering_result,
    }


@app.get("/api/devices/{device_id}/alerts")
def get_alerts(device_id: str):
    device_ref = db.collection("devices").document(
        device_id
    )

    device = device_ref.get()

    if not device.exists:
        return {
            "device_id": device_id,
            "alerts": [],
        }

    data = device.to_dict()
    latest = data.get("last_reading", {})

    alerts = []

    moisture = latest.get("soil_moisture")
    temperature = latest.get("temperature")

    threshold = data.get(
        "moisture_threshold",
        30,
    )

    if moisture is not None and moisture < threshold:
        alerts.append({
            "type": "low_moisture",
            "message": (
                f"Soil moisture is low: {moisture}%"
            ),
            "severity": "warning",
        })

    if temperature is not None and temperature > 35:
        alerts.append({
            "type": "high_temperature",
            "message": (
                f"Temperature is high: {temperature}°C"
            ),
            "severity": "warning",
        })

    last_seen = data.get("last_seen")

    if isinstance(last_seen, datetime):
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(
                tzinfo=timezone.utc
            )

        elapsed = (
            datetime.now(timezone.utc)
            - last_seen
        )

        if elapsed.total_seconds() > 60:
            alerts.append({
                "type": "device_offline",
                "message": (
                    "Device has not sent data "
                    "for more than 60 seconds."
                ),
                "severity": "critical",
            })

    return {
        "device_id": device_id,
        "count": len(alerts),
        "alerts": alerts,
    }


@app.get("/api/devices/{device_id}/analytics")
def get_analytics(device_id: str):
    device_ref = db.collection("devices").document(
        device_id
    )

    readings = []

    for document in (
        device_ref
        .collection("readings")
        .stream()
    ):
        readings.append(document.to_dict())

    watering_events = list(
        device_ref
        .collection("watering_events")
        .stream()
    )

    if not readings:
        return {
            "device_id": device_id,
            "reading_count": 0,
            "average_soil_moisture": 0,
            "minimum_soil_moisture": 0,
            "maximum_soil_moisture": 0,
            "average_temperature": 0,
            "average_humidity": 0,
            "watering_events": len(
                watering_events
            ),
        }

    moisture_values = [
        float(r.get("soil_moisture", 0))
        for r in readings
        if r.get("soil_moisture") is not None
    ]

    temperature_values = [
        float(r.get("temperature", 0))
        for r in readings
        if r.get("temperature") is not None
    ]

    humidity_values = [
        float(r.get("humidity", 0))
        for r in readings
        if r.get("humidity") is not None
    ]

    return {
        "device_id": device_id,
        "reading_count": len(readings),
        "average_soil_moisture": round(
            sum(moisture_values)
            / len(moisture_values),
            2,
        ),
        "minimum_soil_moisture": min(
            moisture_values
        ),
        "maximum_soil_moisture": max(
            moisture_values
        ),
        "average_temperature": round(
            sum(temperature_values)
            / len(temperature_values),
            2,
        ),
        "average_humidity": round(
            sum(humidity_values)
            / len(humidity_values),
            2,
        ),
        "watering_events": len(
            watering_events
        ),
    }