import httpx

URL = "https://api.open-meteo.com/v1/forecast"


def fetch_forecast(lat: float, lng: float) -> list[dict]:
    """7-day daily forecast from Open-Meteo (free, no API key)."""
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": "wind_speed_10m_max,precipitation_sum,temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
        "timezone": "auto",
    }
    data = httpx.get(URL, params=params, timeout=10).json()["daily"]
    days = []
    for i, date in enumerate(data["time"]):
        wind = data["wind_speed_10m_max"][i] or 0
        rain = data["precipitation_sum"][i] or 0
        tmax = data["temperature_2m_max"][i] or 0
        tmin = data["temperature_2m_min"][i] or 0
        days.append({"date": date, "wind": wind, "rain": rain, "temp": tmax,
                     "risk": score_day(wind, rain, tmax, tmin)})
    return days


def score_day(wind_kmh: float, rain_mm: float, tmax: float, tmin: float) -> float:
    """Weighted risk 0-100: wind (40) + rain (40) + temperature extremes (20)."""
    wind_pts = min(wind_kmh / 80, 1) * 40
    rain_pts = min(rain_mm / 50, 1) * 40
    heat = max(tmax - 32, 0) / 10
    cold = max(-tmin, 0) / 15
    temp_pts = min(max(heat, cold), 1) * 20
    return round(wind_pts + rain_pts + temp_pts, 1)


def level(score) -> str:
    if score is None:
        return "Unknown"
    return "High" if score >= 60 else "Medium" if score >= 30 else "Low"
