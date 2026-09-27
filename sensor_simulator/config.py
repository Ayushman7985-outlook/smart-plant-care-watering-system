API_URL = "http://127.0.0.1:8000/api/sensors/data"

DEVICE_ID = "PLANT-001"

# How often the simulator sends a reading.
# We will use 5 seconds for development/testing.
SIMULATION_INTERVAL = 5

# Initial sensor values
INITIAL_SOIL_MOISTURE = 55.0
INITIAL_TEMPERATURE = 27.0
INITIAL_HUMIDITY = 65.0
INITIAL_LIGHT_LEVEL = 70.0

# Soil behaviour
SOIL_DRYING_RATE = 1.0
WATERING_INCREASE = 6.0

# Safety limits
MIN_SOIL_MOISTURE = 0.0
MAX_SOIL_MOISTURE = 100.0