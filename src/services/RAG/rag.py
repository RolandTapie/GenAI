import os
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

import openai
import requests

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from src.services.llm_generation.llm import model
from src.services.vector_database.vector_db import ChromaEmbedding
from src.services.extract_documents.document_extraction import DoclingExtractor
from src.services.vectorization.vectorization import Vectorization


def rag_api(host,port,root,question):
    print(f"http://{host}:{port}/{root}?request={question}")
    response = requests.post(f"http://{host}:{port}/{root}?request={question}")
    print(response.text)
    return response.text

class RagModel():
    def __init__(self, doc_path,vector_model="all-MiniLM-L6-v2", embedding_model="all-MiniLM-L6-v2"):
        self.vectors_db=None
        self.vector_model = vector_model
        self.embedding_model=embedding_model
        self.document_path = doc_path
        self.local_embedding=vector_model
        self.local_embeddings=None
        self.local_model=vector_model
        self.paragraphs=None
        self.embeddings()

    def embeddings(self):
        self.paragraphs=DoclingExtractor(self.document_path).run()
        self.vectors_db = ChromaEmbedding(self.vector_model,"rag",True)
        self.vectors_db.create_collection("docs")
        self.vectors_db.add_to_collection(self.paragraphs)

    def rag_query(self,query):
        print(f"la question est : {query}")
        return self.vectors_db.query(query)
        # if self.local_embedding == "Mistral":
        #     print(f"la question est : {query}")
        #     return self.vectors_db.query(query)
        # else:
        #     return self.vectors_db.similarity_search(query, k=5)

# === 1. Extraction du texte du PDF ===


# === 2. Encodage avec SentenceTransformer ===
def encode_chunks(chunks, model):
    return model.encode(chunks, normalize_embeddings=True)

# === 3. Recherche des top-k passages les plus proches ===
def retrieve_top_k(query, chunks, embeddings, model, k=3):
    query_vec = model.encode([query], normalize_embeddings=True)
    similarities = cosine_similarity(query_vec, embeddings).flatten()
    top_k_idx = np.argsort(similarities)[-k:][::-1]
    return [chunks[i] for i in top_k_idx]

# === 4. Chargement du modèle Mistral en local ===


# === 5. Génération locale avec Mistral ===

def reformulation(question, nombre, model_name="mistral"):
    prompt = f"""Tu es un assistant expert.
        
        reformule la question ci-dessous en {nombre} questions.
    
        Question :
        {question}
        
        """
    return send_prompt(prompt,model_name)



def send_prompt(prompt, model_name="mistral", api_key=None):
    print(test_llm_server())
    try:
        if model_name.lower() == "mistral":
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                #timeout=30  # Sécurité : éviter que ça tourne en boucle
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

        elif model_name.lower().startswith("gpt"):
            if api_key is None:
                raise ValueError("Vous devez fournir une clé API OpenAI via le paramètre 'api_key'.")

            openai.api_key = api_key

            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response['choices'][0]['message']['content'].strip()

        else:
            raise ValueError(f"Modèle non pris en charge : {model_name}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau avec le modèle local : {e}")
    except openai.error.OpenAIError as e:
        print(f"Erreur OpenAI : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

    return ""

def send_mistral(user , question , model_name="mistral", contexte = None, api_key=None):
    print(test_llm_server())
    try:
        if model_name.lower() == "mistral":
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": f"""
                              role: Tu es un assistant expert.
                              Contexte: {contexte}
                              Question : reponds à la question ci-dessous en utilisant exclusivement le contexte
                              {question}  
                              
                              
                              """,
                    "stream": False
                },
                #timeout=30  # Sécurité : éviter que ça tourne en boucle
            )
            response.raise_for_status()
            #debug = response.json()
            print(response.json().get("response", "").strip())
            return response.json().get("response", "").strip()

        else:
            raise ValueError(f"Modèle non pris en charge : {model_name}")

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau avec le modèle local : {e}")
    except openai.error.OpenAIError as e:
        print(f"Erreur OpenAI : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

    return ""

def generate_prompt(user_role,question,context):
    prompt=f"""
    -Tu es un {user_role} francophone.
    
    -[Langue de la réponse : français] Réponds uniquement en français:
    {question}
    
    -utilises uniquement le contexte suivant:
    {context}
    """
    return prompt

def generate_answer_with_llm(question, context_chunks, model_name="mistral"):
    context = "\n\n".join(context_chunks)
    prompt=generate_prompt("assistant expert",question,context)
    return send_prompt(prompt,model_name)


def test_llm_server():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        print(response.status_code)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False
