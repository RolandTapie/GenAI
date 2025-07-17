from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv
import os

# Charger les variables depuis le fichier .env
load_dotenv()

# Lire les variables d'environnement
pdf_path = os.getenv("business_file")

# 1. Lire le PDF
def extract_text_from_pdf(pdf_path):
    full_text = extract_text(pdf_path)
    raw_paragraphs = full_text.split('\n\n')  # Double saut de ligne = paragraphes
    # Nettoyage des paragraphes vides ou très courts
    paragraphs = [p.strip().replace('\n', ' ') for p in raw_paragraphs if len(p.strip()) > 40]
    return paragraphs

# 2. Indexer les textes avec TF-IDF
def build_index(chunks):
    vectorizer = TfidfVectorizer(stop_words=None)
    vectors = vectorizer.fit_transform(chunks)
    return vectorizer, vectors

# 3. Trouver les passages les plus proches d'une question
def search(query, vectorizer, vectors, chunks, k=3):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, vectors).flatten()
    top_k = np.argsort(similarities)[-k:][::-1]
    return [chunks[i] for i in top_k]

# === MAIN ===

chunks = extract_text_from_pdf(pdf_path)
vectorizer, vectors = build_index(chunks)

# Boucle interactive
while True:
    question = input("Pose ta question : ")
    results = search(question, vectorizer, vectors, chunks)
    print("\n--- Passages les plus pertinents ---\n")
    for i, passage in enumerate(results):
        print(f"[{i+1}] {passage.strip()}\n")
