import requests

def get_weather(latitude, longitude) -> str:
    """
    Récupère la météo actuelle en fonction de la latitude et longitude via l'API Open-Meteo.

    Args:
        latitude (float): Latitude de la position.
        longitude (float): Longitude de la position.

    Returns:
        str: Description simple de la météo (température, conditions).
    """

    latitude = str(latitude)
    longitude = str(longitude)
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&current_weather=true"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather = data.get("current_weather", {})
        temperature = weather.get("temperature")
        windspeed = weather.get("windspeed")
        weather_code = weather.get("weathercode")

        return (
            f"🌡 Température: {temperature}°C\n"
            f"💨 Vent: {windspeed} km/h\n"
            f"🌥 Code météo: {weather_code} (voir documentation Open-Meteo)"
        )
    except Exception as e:
        return f"Erreur lors de la récupération de la météo : {e}"
