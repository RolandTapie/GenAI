import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pdfminer.high_level import extract_text
from openai import OpenAI
from colorama import Fore, Style, init

from dotenv import load_dotenv
import os
# Charger les variables depuis le fichier .env
load_dotenv()
# Lire les variables d'environnement
cle = os.getenv("openai_key")
pdf_path = os.getenv("business_file")
model_path = os.getenv("model_path")

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


# === 4. Génération de réponse via GPT-3.5 ===
def generate_answer(cle,question, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = f"""Tu es un assistant expert.

    Voici des extraits d'un document. Utilise uniquement les informations du contexte ci-dessous pour répondre à la question.
    
    Contexte :
    {context}
    
    Question :
    {question}
    
    Réponse claire et concise en français :
    """

    client = OpenAI(api_key=cle)
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=400,
        )
    return response.choices[0].message.content.strip()

print("⏳ Chargement du modèle et du PDF...")
model = SentenceTransformer(model_path)

chunks = extract_paragraphs(pdf_path)
embeddings = encode_chunks(chunks, model)

# === MAIN ===
if __name__ == "__main__":
    nom = input(f"{Fore.BLUE}🤖 : Bonjour, comment t'appelles tu ? \n👤 : {Style.RESET_ALL}")
    while True:

        question = input(f"{Fore.BLUE}🤖 : comment puis-je t'aider {nom} : \n👤 {nom} : {Style.RESET_ALL}")
        if question.lower() in ['exit', 'quit',"bye"]:
            print(f"🤖 : je suis ravi de t'avoir aidé {nom}, à la prochaine...")
            break


        top_chunks = retrieve_top_k(question, chunks, embeddings, model, k=3)

        print("\n💬 Réponse générée :\n")

        print(top_chunks)

        answer = generate_answer(cle, question, top_chunks)
        print(answer)