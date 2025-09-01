from src.services.RAG.rag import rag_api

def get_rag_response(query: str) -> str :
    """
    à définir.

    Args:
        query (str): à définir

    Returns:
        str: le contexte pour que llm génère la réponse finale.s
    """
    return rag_api("localhost",8000,"/query",query)