import yfinance as yf

def f_get_yahoo_rate(ticker="^TNX"):
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

