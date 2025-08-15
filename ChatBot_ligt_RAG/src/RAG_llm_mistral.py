from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from dotenv import load_dotenv
import os
# Charger les variables depuis le fichier .env
load_dotenv()
# Lire les variables d'environnement

pdf_path = os.getenv("business_file")
model_path = os.getenv("model_path")


# 1. Extraire les paragraphes du PDF
def extract_paragraphs_from_pdf(pdf_path):
    full_text = extract_text(pdf_path)
    raw_paragraphs = full_text.split('\n\n')  # Découpe en paragraphes
    paragraphs = [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]
    return paragraphs

# 2. Construire les embeddings
def build_embeddings(paragraphs, model_name):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(paragraphs, normalize_embeddings=True)
    return model, embeddings

# 3. Recherche des passages pertinents
def search(query, model, embeddings, paragraphs, top_k=3):
    query_embedding = model.encode([query], normalize_embeddings=True)
    similarities = cosine_similarity(query_embedding, embeddings).flatten()
    top_k_indices = np.argsort(similarities)[-top_k:][::-1]
    return [paragraphs[i] for i in top_k_indices]

# === MAIN ===

paragraphs = extract_paragraphs_from_pdf(pdf_path)

print(f"Nombre de paragraphes extraits : {len(paragraphs)}")

model, embeddings = build_embeddings(paragraphs,model_path)

print("Modèle chargé et embeddings calculés.")

# Boucle interactive
while True:
    question = input("\nPose ta question (ou 'exit' pour quitter) : ")
    if question.lower() in ['exit', 'quit']:
        break
    results = search(question, model, embeddings, paragraphs)
    print("\n--- Passages les plus pertinents ---\n")
    for i, (passage, score) in enumerate(results):
        print(f"[{i+1}] (score: {score:.4f}) {passage.strip()}...\n", flush=True)
