import requests
from newspaper import Article

from dotenv import load_dotenv
import os
load_dotenv()
# Remplace par ta propre clé API (obtenue sur https://newsdata.io)
API_KEY = os.getenv("NEWSDATA_IO")



def extract_article(url):
    #url = "https://www.example.com/article.html"
    article = Article(url, language="fr")
    article.download()
    article.parse()
    titre = article.title
    auteurs = article.authors
    date_publication = article.publish_date
    texte = article.text[:500]
    return texte

def get_news(requete: str):
    """
    permet de recupérer les informations , les nouvelles ou les actualités
    :param requete: les informations ou nouvelles ou actualités à rechercher
    :return: les informations , les nouvelles ou les actualités sur le sujet passé en paramètres
    """
    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": API_KEY,
        "q": requete,   # mot-clé
        "language": "fr",                   # langue des articles
        "country": "fr",                    # pays     # catégori                         # pagination
    }
    response = requests.get(url,params=params)
    responses = []
    if response.status_code == 200:
        data = response.json()

        for article in data.get("results", []):
            titre =article.get("title")
            lien = article.get("link")
            contenu = extract_article(lien)
            date_publication = article.get("pubDate")
            art = {"Titre":titre,"Lien":lien,"Contenu":contenu,"Date de publication":date_publication}
            responses.append(art)
    else:
        print("Erreur:", response.status_code, response.text)
    return responses