import requests

def rag_api(host,port,root,question):
    print(f"http://{host}:{port}/{root}?request={question}")
    response = requests.post(f"http://{host}:{port}/{root}?request={question}")
    print(response.text)
    return response.text

def f_get_rag_response(query: str) -> str :
    """
    à définir.

    Args:
        query (str): à définir

    Returns:
        str: le contexte pour que llm génère la réponse finale.s
    """
    return rag_api("localhost",8000,"/query",query)