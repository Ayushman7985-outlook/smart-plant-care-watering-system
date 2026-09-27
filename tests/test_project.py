
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from automation.plant_profiles import get_profile
from automation.watering_engine import (
    should_water,
    process_reading,
)


client = TestClient(app)


# ============================================================
# BASIC API TESTS
# ============================================================

def test_01_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_02_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_03_devices_endpoint():
    response = client.get("/api/devices")
    assert response.status_code == 200
    assert "devices" in response.json()


def test_04_pump_status_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/pump-status"
    )
    assert response.status_code == 200
    assert "pump_status" in response.json()


def test_05_auto_status_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/auto-status"
    )
    assert response.status_code == 200
    assert "auto_watering_enabled" in response.json()


def test_06_threshold_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/threshold"
    )
    assert response.status_code == 200
    assert "moisture_threshold" in response.json()


def test_07_latest_reading_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/latest"
    )
    assert response.status_code == 200


def test_08_history_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/history"
    )
    assert response.status_code == 200
    assert "readings" in response.json()


def test_09_watering_history_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/watering-history"
    )
    assert response.status_code == 200
    assert "events" in response.json()


def test_10_alerts_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/alerts"
    )
    assert response.status_code == 200
    assert "alerts" in response.json()


def test_11_analytics_endpoint():
    response = client.get(
        "/api/devices/PLANT-001/analytics"
    )
    assert response.status_code == 200
    assert "reading_count" in response.json()


# ============================================================
# PLANT PROFILE TESTS
# ============================================================

def test_12_succulent_profile():
    profile = get_profile("succulent")

    assert profile["moisture_threshold"] == 20


def test_13_tomato_profile():
    profile = get_profile("tomato")

    assert profile["moisture_threshold"] == 40


def test_14_herb_profile():
    profile = get_profile("herb")

    assert profile["moisture_threshold"] == 35


def test_15_indoor_profile():
    profile = get_profile("indoor")

    assert profile["moisture_threshold"] == 30


def test_16_unknown_profile_uses_indoor():
    profile = get_profile("unknown")

    assert profile["moisture_threshold"] == 30


# ============================================================
# WATERING ENGINE TESTS
# ============================================================

def test_17_watering_not_required_when_moisture_is_high():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "OFF",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = should_water(
            "PLANT-001",
            50,
        )

    assert result is False


def test_18_watering_required_when_moisture_is_low():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "OFF",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = should_water(
            "PLANT-001",
            20,
        )

    assert result is True


def test_19_watering_disabled():
    fake_device = {
        "auto_watering_enabled": False,
        "pump_status": "OFF",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = should_water(
            "PLANT-001",
            20,
        )

    assert result is False


def test_20_watering_not_started_when_pump_already_on():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "ON",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = should_water(
            "PLANT-001",
            20,
        )

    assert result is False


def test_21_cooldown_prevents_repeated_watering():
    recent_time = (
        datetime.now(timezone.utc)
        - timedelta(seconds=30)
    )

    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "OFF",
        "moisture_threshold": 30,
        "last_watered_at": recent_time,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = should_water(
            "PLANT-001",
            20,
        )

    assert result is False


def test_22_process_reading_keeps_pump_off_when_moisture_is_high():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "OFF",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ):
        result = process_reading(
            "PLANT-001",
            50,
        )

    assert result["pump_status"] == "OFF"


def test_23_process_reading_activates_pump_when_moisture_is_low():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "OFF",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ), patch(
        "automation.watering_engine.activate_virtual_pump",
        return_value={
            "pump_status": "ON",
            "message": "Virtual pump activated",
        },
    ) as mock_activate:

        result = process_reading(
            "PLANT-001",
            20,
        )

    mock_activate.assert_called_once()
    assert result["pump_status"] == "ON"


def test_24_process_reading_stops_pump_after_target():
    fake_device = {
        "auto_watering_enabled": True,
        "pump_status": "ON",
        "moisture_threshold": 30,
    }

    with patch(
        "automation.watering_engine.get_device",
        return_value=fake_device,
    ), patch(
        "automation.watering_engine.deactivate_virtual_pump",
        return_value={
            "pump_status": "OFF",
            "message": "Virtual pump deactivated",
        },
    ) as mock_deactivate:

        result = process_reading(
            "PLANT-001",
            48,
        )

    mock_deactivate.assert_called_once()
    assert result["pump_status"] == "OFF"


def test_25_unknown_device_does_not_start_watering():
    with patch(
        "automation.watering_engine.get_device",
        return_value=None,
    ):
        result = process_reading(
            "UNKNOWN-DEVICE",
            10,
        )

    assert result["pump_status"] == "OFF"
    assert result["message"] == "Device not found"