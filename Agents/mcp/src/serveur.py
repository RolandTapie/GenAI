from mcp.server.fastmcp import FastMCP
#from tools.weather import get_weather
from dotenv import load_dotenv
import os
import requests

# Charger les variables depuis le fichier .env
load_dotenv()

# Lire les variables d'environnement
openai_api_key = os.getenv("openai_key")
server_name = os.getenv("name")
server_host = os.getenv("host")
server_port=os.getenv("port")
transport=os.getenv("mcp_transport")

server = FastMCP(
    name=server_name, #"serveur_mcp_test",
    host=server_host, #"0.0.0.0",  # only used for SSE transport (localhost)
    port=server_port, #8050,  # only used for SSE transport (set this to any port)
    stateless_http=True)

@server.tool()
def print_test(data: str):
    """
    il s'agit d'un tool test
    :param data:
    :return:
    """
    return ("Merci " + data)



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

@server.tool()
def mcp_get_weather(latitude, longitude):
    """
    il s'agit d'un outil qui permet d'obtenir les conditions météorologiques
    :param latitude:
    :param longitude:
    :return: la temperature
    """
    return get_weather(latitude,longitude)


if __name__ == "__main__":

   server.run(transport=transport)