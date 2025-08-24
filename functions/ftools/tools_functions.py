import requests

def get_weather(latitude, longitude) -> str:
    """
    Récupère la météo actuelle en fonction de la latitude et longitude.

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
            f"🌥 Code météo: {weather_code}"
        )
    except Exception as e:
        return f"Erreur lors de la récupération de la météo : {e}"

def get_bank_transaction() -> str:
    """
    Permet de récupérer la liste des transactions bancaires
    Returns:
         str: la liste des transactions bancaires.
    """
    transactions="""01/08/2025 Salaire – Entreprise XYZ +2500,00 € Solde : 2500,00 €
        03/08/2025 Paiement carte – Supermarché -75,60 € Solde : 2424,40 €
        05/08/2025 Virement reçu – Amis +150,00 € Solde : 2574,40 €
        07/08/2025 Prélèvement automatique – Électricité -120,45 € Solde : 2453,95 €
        10/08/2025 Retrait DAB -200,00 € Solde : 2253,95 €
        12/08/2025 Paiement carte – Restaurant -45,80 € Solde : 2208,15 €
        15/08/2025 Virement vers compte épargne -500,00 € Solde : 1708,15 €
        18/08/2025 Paiement carte – Boutique en ligne -89,99 € Solde : 1618,16 €
        21/08/2025 Prélèvement automatique – Internet -35,00 € Solde : 1583,16 €
        23/08/2025 Remboursement prêt personnel +300,00 € Solde : 1883,16 €"""
    return transactions

def set_meeting(nom, jour) -> str:
    """
    Permet de fixer ou d'enregistres les rendez-vous dans l'agenda.

    Args:
        nom (str): nom de la personne avec qui j'ai rendez-vous.
        jour (str): jour du rendez-vous.

    Returns:
        str: fixe le rendez-vous et retourne une confirmation.
    """
    confirmation = f"un rendez-vous a bien été fixé avec {nom} le {jour}"
    return confirmation
