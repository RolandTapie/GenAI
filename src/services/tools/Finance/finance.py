import yfinance as yf
import pandas as pd

def get_yahoo_rate(ticker="^TNX"):
    """
    Récupère le dernier taux disponible pour un ticker Yahoo Finance.
    :param ticker:
    :return: le dernier taux disponible
    """

    data = yf.Ticker(ticker)
    info = data.history(period="1d")

    if info.empty:
        return None

    # Le taux est généralement dans la colonne 'Close'
    latest_rate = info["Close"].iloc[-1]

    # Pour certains tickers, Yahoo donne le taux *x10* (ex : ^TNX = 4.35 => 43.5)
    # Ajustement si nécessaire (cas le plus fréquent)
    if latest_rate > 20:
        latest_rate /= 10

    return latest_rate

def f_analyze_rate(ticker="^TNX", period="1y"):
    """
    Récupère un taux sur Yahoo Finance, analyse son évolution et produit une synthèse textuelle.

    Arguments :
        ticker : str  — ex: "^TNX" (Taux US 10 ans)
        period : str — période Yahoo Finance ("1mo", "3mo", "6mo", "1y", "5y")

    Retour :
        dict contenant :
            - raw_data : DataFrame historique
            - analysis : dict d’évolution
            - summary : texte prêt à intégrer dans un prompt
    """

    # --- 1. Récupération des données ---
    data = yf.Ticker(ticker).history(period=period)

    if data.empty:
        return {"error": f"Aucune donnée disponible pour {ticker}"}

    # Nettoyage (certains taux sont *10, ex: TNX)
    close = data["Close"]
    if close.mean() > 20:
        close = close / 10

    data["Rate"] = close

    # --- 2. Analyse de l’évolution ---
    def pct_change(days):
        if len(data) < days:
            return None
        return round(((data["Rate"].iloc[-1] / data["Rate"].iloc[-days]) - 1) * 100, 3)

    evol_7d  = pct_change(7)
    evol_30d = pct_change(30)
    evol_90d = pct_change(90)
    evol_1y  = pct_change(len(data))  # sur toute la période

    # --- 3. Synthèse en texte ---
    latest = round(data["Rate"].iloc[-1], 3)

    def fmt(val):
        return "N/A" if val is None else f"{val}%"

    summary = f"""
        Analyse du taux {ticker} :

        • Taux actuel : {latest}%
        • Évolution sur 7 jours : {fmt(evol_7d)}
        • Évolution sur 30 jours : {fmt(evol_30d)}
        • Évolution sur 90 jours : {fmt(evol_90d)}
        • Évolution sur la période totale ({period}) : {fmt(evol_1y)}

        Conclusion automatisée :
        Le taux {ticker} est actuellement de {latest}%. Sur les dernières semaines, 
        il a évolué de {fmt(evol_7d)} (7j) et {fmt(evol_30d)} (30j). 
        Sur un horizon plus long, la variation est de {fmt(evol_90d)} (90j) 
        et {fmt(evol_1y)} sur la période "{period}".
        """

    return {
        #"raw_data": data,
        "analysis": {
            "current_rate": latest,
            "evol_7d": evol_7d,
            "evol_30d": evol_30d,
            "evol_90d": evol_90d,
            "evol_period": evol_1y,
        },
        "summary": summary.strip()
    }

