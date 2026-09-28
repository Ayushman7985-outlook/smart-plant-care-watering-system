import random
import time
from datetime import datetime, timezone

import requests

import config


soil_moisture = config.INITIAL_SOIL_MOISTURE
temperature = config.INITIAL_TEMPERATURE
humidity = config.INITIAL_HUMIDITY
light_level = config.INITIAL_LIGHT_LEVEL

pump_status = "OFF"


def keep_in_range(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def get_backend_base_url():
    """
    Extract the backend base URL from the sensor API URL.

    Example:
    https://example.com/api/sensors/data
    becomes:
    https://example.com
    """
    return config.API_URL.split("/api/")[0]


def get_pump_status():
    try:
        backend_base_url = get_backend_base_url()

        url = (
            f"{backend_base_url}"
            f"/api/devices/{config.DEVICE_ID}/pump-status"
        )

        response = requests.get(
            url,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "pump_status",
            "OFF",
        )

    except requests.RequestException as error:
        print(
            f"[WARNING] Could not get pump status: {error}"
        )

        return "OFF"


def generate_sensor_values():
    global soil_moisture
    global temperature
    global humidity
    global light_level
    global pump_status

    # Apply the effect of the pump from the PREVIOUS
    # backend decision.
    if pump_status == "ON":
        soil_moisture += config.WATERING_INCREASE
    else:
        soil_moisture -= config.SOIL_DRYING_RATE

    # Other environmental values change gradually.
    temperature += random.uniform(
        -0.4,
        0.4,
    )

    humidity += random.uniform(
        -1.5,
        1.5,
    )

    light_level += random.uniform(
        -8,
        8,
    )

    soil_moisture = keep_in_range(
        soil_moisture,
        config.MIN_SOIL_MOISTURE,
        config.MAX_SOIL_MOISTURE,
    )

    temperature = keep_in_range(
        temperature,
        15,
        40,
    )

    humidity = keep_in_range(
        humidity,
        30,
        90,
    )

    light_level = keep_in_range(
        light_level,
        0,
        100,
    )

    return {
        "device_id": config.DEVICE_ID,
        "soil_moisture": round(
            soil_moisture,
            2,
        ),
        "temperature": round(
            temperature,
            2,
        ),
        "humidity": round(
            humidity,
            2,
        ),
        "light_level": round(
            light_level,
            2,
        ),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "pump_status": pump_status,
    }


def send_sensor_data(sensor_data):
    try:
        response = requests.post(
            config.API_URL,
            json={
                "device_id": sensor_data["device_id"],
                "soil_moisture": sensor_data["soil_moisture"],
                "temperature": sensor_data["temperature"],
                "humidity": sensor_data["humidity"],
                "light_level": sensor_data["light_level"],
                "timestamp": sensor_data["timestamp"],
            },
            timeout=10,
        )

        response.raise_for_status()

        print(
            f"[SENT] "
            f"Soil={sensor_data['soil_moisture']}% | "
            f"Temp={sensor_data['temperature']}°C | "
            f"Humidity={sensor_data['humidity']}% | "
            f"Light={sensor_data['light_level']}% | "
            f"Pump={sensor_data['pump_status']}"
        )

        return True

    except requests.RequestException as error:
        print(
            f"[ERROR] Could not send sensor data: {error}"
        )

        return False


def run_simulator():
    global pump_status

    print("=" * 60)
    print("SMART PLANT VIRTUAL SENSOR SIMULATOR")
    print("=" * 60)

    print(
        f"Device ID: {config.DEVICE_ID}"
    )

    print(
        f"API URL: {config.API_URL}"
    )

    print(
        f"Interval: {config.SIMULATION_INTERVAL} seconds"
    )

    print(
        "Press Ctrl+C to stop."
    )

    print("=" * 60)

    # Get the initial pump state once before starting.
    pump_status = get_pump_status()

    print(
        f"Initial Pump Status: {pump_status}"
    )

    while True:
        sensor_data = generate_sensor_values()

        sent_successfully = send_sensor_data(
            sensor_data
        )

        # IMPORTANT:
        # Check the backend AFTER sending the reading.
        #
        # Example:
        # 29% is sent while pump is OFF.
        # Backend detects 29% < 30% and activates pump.
        # We then read the new pump state.
        if sent_successfully:
            pump_status = get_pump_status()

        time.sleep(
            config.SIMULATION_INTERVAL
        )


if __name__ == "__main__":
    try:
        run_simulator()

    except KeyboardInterrupt:
        print(
            "\nSimulator stopped."
        )