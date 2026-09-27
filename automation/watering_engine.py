from datetime import datetime, timedelta, timezone

from backend.app.firebase_config import db


DEFAULT_THRESHOLD = 30.0
WATERING_TARGET = 45.0
MAX_WATERING_SECONDS = 15
COOLDOWN_MINUTES = 2


def get_device(device_id: str):
    device_ref = db.collection("devices").document(device_id)
    device = device_ref.get()

    if not device.exists:
        return None

    return device.to_dict()


def should_water(device_id: str, soil_moisture: float) -> bool:
    device = get_device(device_id)

    if not device:
        return False

    if device.get("auto_watering_enabled", True) is False:
        return False

    if device.get("pump_status", "OFF") == "ON":
        return False

    threshold = float(
        device.get(
            "moisture_threshold",
            DEFAULT_THRESHOLD,
        )
    )

    if soil_moisture >= threshold:
        return False

    last_watered = device.get("last_watered_at")

    if last_watered:
        if isinstance(last_watered, datetime):
            current_time = datetime.now(timezone.utc)

            if last_watered.tzinfo is None:
                last_watered = last_watered.replace(
                    tzinfo=timezone.utc
                )

            elapsed = current_time - last_watered

            if elapsed < timedelta(
                minutes=COOLDOWN_MINUTES
            ):
                return False

    return True


def activate_virtual_pump(
    device_id: str,
    moisture_before: float,
    trigger_type: str = "automatic",
):
    now = datetime.now(timezone.utc)

    device_ref = db.collection("devices").document(device_id)

    device_ref.set(
        {
            "pump_status": "ON",
            "last_watered_at": now,
            "watering_started_at": now,
        },
        merge=True,
    )

    event_ref = (
        device_ref
        .collection("watering_events")
        .document()
    )

    event_ref.set(
        {
            "device_id": device_id,
            "trigger_type": trigger_type,
            "moisture_before": moisture_before,
            "moisture_after": None,
            "duration_seconds": 0,
            "timestamp": now,
            "status": "running",
        }
    )

    return {
        "pump_status": "ON",
        "message": "Virtual pump activated",
    }


def deactivate_virtual_pump(
    device_id: str,
    moisture_after: float,
):
    now = datetime.now(timezone.utc)

    device_ref = db.collection("devices").document(device_id)

    device_ref.set(
        {
            "pump_status": "OFF",
        },
        merge=True,
    )

    events = (
        device_ref
        .collection("watering_events")
        .stream()
    )

    latest_running_event = None
    latest_timestamp = None

    for event in events:
        event_data = event.to_dict()

        if event_data.get("status") != "running":
            continue

        event_timestamp = event_data.get("timestamp")

        if (
            latest_timestamp is None
            or (
                event_timestamp
                and event_timestamp > latest_timestamp
            )
        ):
            latest_running_event = event
            latest_timestamp = event_timestamp

    if latest_running_event:
        latest_running_event.reference.update(
            {
                "moisture_after": moisture_after,
                "duration_seconds": MAX_WATERING_SECONDS,
                "status": "completed",
                "completed_at": now,
            }
        )

    return {
        "pump_status": "OFF",
        "message": "Virtual pump deactivated",
    }


def process_reading(
    device_id: str,
    soil_moisture: float,
):
    device = get_device(device_id)

    if not device:
        return {
            "pump_status": "OFF",
            "message": "Device not found",
        }

    pump_status = device.get(
        "pump_status",
        "OFF",
    )

    if pump_status == "ON":
        if soil_moisture >= WATERING_TARGET:
            return deactivate_virtual_pump(
                device_id,
                soil_moisture,
            )

        return {
            "pump_status": "ON",
            "message": "Virtual pump is running",
        }

    if should_water(
        device_id,
        soil_moisture,
    ):
        return activate_virtual_pump(
            device_id,
            soil_moisture,
            trigger_type="automatic",
        )

    return {
        "pump_status": "OFF",
        "message": "Watering not required",
    }