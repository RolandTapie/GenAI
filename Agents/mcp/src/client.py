import asyncio
from functions.agent import Agent
from dotenv import load_dotenv
import os
# Charger les variables depuis le fichier .env
load_dotenv()
# Lire les variables d'environnement
openai_api_key = os.getenv("openai_key")
pdf_path = os.getenv("business_file")
model_path = os.getenv("model_path")
mcp_server = os.getenv("mcp_serveur_path")
transport=os.getenv("mcp_transport")

agent=Agent("Mistral",mcp_server)

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


