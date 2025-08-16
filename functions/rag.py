import os
import numpy as np
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from docling.document_converter import DocumentConverter
from transformers import AutoTokenizer

from docling.chunking import HybridChunker
import openai
import requests
import re
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from llm import model
from vector_db import ChromaEmbedding


class RagModel():
    def __init__(self, doc_path,llm="openai", embedding_model="text-embedding-3-small"):
        self.vectors_db=None
        if llm=="Mistral":
            self.model=r"C:\Users\tallar\Documents\PROJETS\GenAI\LLM_Model\Embedding\models--sentence-transformers--all-MiniLM-L6-v2"
        else:
            self.model = model(llm)
        self.embedding_model=embedding_model
        self.document_path = doc_path
        self.local_embedding=llm
        self.local_embeddings=None
        self.local_model=llm
        self.paragraphs=None
        if self.local_model == "Mistral":
            self.vectors_db = ChromaEmbedding("rag",True)
            self.vectors_db.create_collection("docs")
        self.embeddings()

    def docling_extraction(self,document):
        #hf_tokenizer = AutoTokenizer.from_pretrained(self.model)
        converter = DocumentConverter()
        result = converter.convert(document)
        doc=result.document.export_to_text()

        return doc

    def extract_paragraphs(self, document):
        #text = extract_text(document)
        text = self.docling_extraction(document)
        #raw_paragraphs = text.split('\n\n')
        text = re.sub(r'-\n', '', text)
        text = re.sub(r'\n', '', text)
        raw_paragraphs = text.split('.')
        return [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]

    def embeddings(self):
        if self.local_embedding == "Mistral":
            self.paragraphs=self.extract_paragraphs(self.document_path)
            self.vectors_db.add_to_collection(self.paragraphs)
            #self.local_mistral_embeddings(self.paragraphs)

        elif self.local_embedding == "openai":
            embeddings_model = OpenAIEmbeddings(model=self.embedding_model,api_key=self.model.api_key)  # ou "text-embedding-3-large"
            # 2. Creer une base vectorielle (ici Chroma en mémoire)
            db = Chroma(collection_name="documents", embedding_function=embeddings_model,persist_directory="./vectordb")
            # 3. Ajouter des documents
            chunks = self.extract_paragraphs()
            db.add_texts(chunks)
            self.vectors_db = db

    def local_mistral_embeddings(self,paragraphs):
        """
            Fonction pour générer des embeddings avec Mistral local.
            texts : list[str]
            retourne : list[list[float]]
            """
        self.local_model= SentenceTransformer(self.model)
        self.local_embeddings = self.local_model.encode(paragraphs, normalize_embeddings=True)

    def rag_query(self,query):
        if self.local_embedding == "Mistral":
            print(f"la question est : {query}")
            return self.vectors_db.query(query)
            # query_embedding = self.local_model.encode([query], normalize_embeddings=True)
            # similarities = cosine_similarity(query_embedding, self.local_embeddings).flatten()
            # top_k_indices = np.argsort(similarities)[-5:][::-1]
            # return [self.paragraphs[i-1] + ";" +self.paragraphs[i] + ";" +self.paragraphs[i+1] for i in top_k_indices]
        else:
            return self.vectors_db.similarity_search(query, k=5)

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
