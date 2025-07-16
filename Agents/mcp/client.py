import asyncio
from functions.agent import Agent

agent=Agent("Mistral")

transport="stdio"
if __name__ == "__main__":
    if transport == "stdio":
        # changer le mode de transport dans le serveur mcp
        # stdio lance automatiquement le serveur grace au serveur_path
        asyncio.run(agent.main_stdio())
    elif transport == "sse":
        # changer le mode de transport dans le serveur mcp
        # le serveur doit être lancer manuellement (python serveur.py) avant
        asyncio.run(agent.main_sse())
    else:
        raise Exception("la méthode de transfert est incorrecte")


