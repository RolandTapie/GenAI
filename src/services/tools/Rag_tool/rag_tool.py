from src.services.RAG.rag import rag_api

def get_rag_response(query: str) -> str :
    """
    Permet de consulter le RAG et de récupérer les informations.

    Args:
        query (str): il s'agit de la question à poser au RAG

    Returns:
        str: le contexte pour que llm génère la réponse finale.s
    """
    return rag_api("localhost",8000,"/query",query)