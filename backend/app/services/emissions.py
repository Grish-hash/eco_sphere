from math import radians, sin, cos, asin, sqrt

# kg CO2 per ton-km
FACTORS = {"truck": 0.1, "rail": 0.03, "ship": 0.015, "air": 0.6}
# average speeds in km/h (used for the simulated fleet)
SPEEDS = {"truck": 60, "rail": 50, "ship": 30, "air": 800}


def haversine_km(lat1, lng1, lat2, lng2) -> float:
    r = 6371
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def emissions_kg(distance_km: float, load_tons: float, mode: str) -> float:
    return distance_km * load_tons * FACTORS.get(mode, 0.1)
