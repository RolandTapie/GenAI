import requests
from src.services.logs.loggers import log

def rag_api(host,port,root,question):
    log(f"http://{host}:{port}/{root}?request={question}")
    response = requests.post(f"http://{host}:{port}/{root}?request={question}")
    return response.text

def f_get_rag_response(query: str) -> str :
    """
    permet de consulter le RAG afin d'obtenir les informations du RAG

    Args:
        query (str): la question a analyser par le RAG

    Returns:
        str: le contexte pour que llm génère la réponse finale
    """
    return rag_api("localhost",8000,"/query",query)