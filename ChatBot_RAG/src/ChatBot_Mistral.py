import os
import numpy as np
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import requests

# === 1. Extraction du texte du PDF ===
def extract_paragraphs(pdf_path):
    text = extract_text(pdf_path)
    raw_paragraphs = text.split('\n\n')
    return [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]

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


def generate_answer_with_ollama(question, context_chunks, model_name="mistral"):
    context = "\n\n".join(context_chunks)
    prompt = f"""Tu es un assistant expert.
        
        Voici des extraits d'un document. Utilise-les pour répondre à la question.
        
        Contexte :
        {context}
        
        Question :
        {question}
        
        Réponse limité au contexte, claire et concise en français :
        """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False  # True = streaming, False = réponse complète
        }
    )
    response.raise_for_status()
    return response.json()["response"].strip()

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

# === MAIN ===
if __name__ == "__main__":
    if test_llm_server():

        print("🚀 Chargement du moodèle de vectorisation")
        model_emb = SentenceTransformer(
            r"C:\Users\tallar\Documents\PROJETS\GenAI\LLM_Model\Embedding\models--sentence-transformers--all-MiniLM-L6-v2"
        )

        print("Mistral...")
        print("🚀 Serveur génératif : UP")

        print("⏳ Chargement du modèle d'embedding et du PDF...")
        pdf_path = r"C:\Users\tallar\Documents\PROJETS\GenAI\ChatBot\files\IntroML_Azencott.pdf"
        chunks = extract_paragraphs(pdf_path)
        embeddings = encode_chunks(chunks, model_emb)



        while True:

            question = input("Pose ta question : ")
            if question.lower() in ['exit', 'quit']:
                break
            top_chunks = retrieve_top_k(question, chunks, embeddings, model_emb, k=3)

            print("\n📚 Extraits sélectionnés :\n")
            for c in top_chunks:
                print("- " + c + "\n")

            print("💬 Génération de la réponse...\n")
            answer = generate_answer_with_ollama(question,top_chunks)

            print("\n🧠 Mistral répond :\n")
            print(answer)
    else:
        print("le modèle mistral est down")