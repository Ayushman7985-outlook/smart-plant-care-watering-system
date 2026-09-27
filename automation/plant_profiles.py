PLANT_PROFILES = {
    "succulent": {
        "moisture_threshold": 20,
        "description": "Low-water plant",
    },
    "tomato": {
        "moisture_threshold": 40,
        "description": "High-water vegetable plant",
    },
    "herb": {
        "moisture_threshold": 35,
        "description": "Moderate-water herb",
    },
    "indoor": {
        "moisture_threshold": 30,
        "description": "General indoor plant",
    },
}


def get_profile(profile_name: str):
    return PLANT_PROFILES.get(
        profile_name,
        PLANT_PROFILES["indoor"],
    )