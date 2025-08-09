from sentence_transformers import SentenceTransformer
from functions.rag import extract_paragraphs,encode_chunks,retrieve_top_k,generate_answer_with_llm,test_llm_server,reformulation
from dotenv import load_dotenv
import os
# Charger les variables depuis le fichier .env
load_dotenv()
# Lire les variables d'environnement
openai_api_key = os.getenv("openai_key")
pdf_path = os.getenv("business_file")
model_path = os.getenv("model_path")


# === MAIN ===
if __name__ == "__main__":
    if test_llm_server():

        print("🚀 Chargement du moodèle de vectorisation")
        model_emb = SentenceTransformer(model_path)

        print("Mistral...")
        print("🚀 Serveur génératif : UP")


        print(f"⏳ Chargement des documents...\n{pdf_path}")

        print(" 📑-Extractions des chunks")
        chunks = extract_paragraphs(pdf_path)
        #for chunk in chunks:
            #print(chunk + "\n")

        print(" 🔢-Vectorisation des chunks")
        embeddings = encode_chunks(chunks, model_emb)

        contexts=[]

        while True:

            question = input("Quelle est votre question : ")
            if question.lower() in ['exit', 'quit']:
                break

            print("\n🔁 Reformulation des questions :\n")
            questions = reformulation(question, 3, model_name="mistral")
            print(questions)
            all_chunks=[]
            for question in questions:
                top_chunks = retrieve_top_k(question, chunks, embeddings, model_emb, k=5)
                for chunk in top_chunks:
                    all_chunks.append(chunk)

            contexts.append(top_chunks)

            print("\n📚 Extraits sélectionnés :\n")
            #for c in top_chunks:
                #print("- " + c + "\n")

            print("la question")
            print(question)
            print("les reformulations")
            print(questions)
            print("le contexte")
            print(all_chunks)
            print("🤖💬 Génération de la réponse...\n")
            answer = generate_answer_with_llm(questions,all_chunks)

            contexts.append(answer)

            print("\n🧠 Mistral répond :\n")
            print(answer)
    else:
        print("le modèle mistral est down")