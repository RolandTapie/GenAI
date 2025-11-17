from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

# Ton import RagModel
from src.services.RAG.extraction.document_extraction import DoclingExtractor
from src.services.RAG.vectorization.vectorization import Vectorization
from src.services.RAG.embeddings.db_embeddings import ChromaEmbedding
from src.services.logs.loggers import log
from src.services.RAG.rag import RagModelV2



app = FastAPI(title="RAG API", description="API pour effectuer des requêtes RAG", version="1.0.0")

# Instance globale du modèle
rag_instance = None

class QueryRequest(BaseModel):
    query: str


from dotenv import load_dotenv
import os
load_dotenv()



def load_document(document: str, vectorization_model, db_embedding):

    log(f"Chargement du document {document} via le modele {vectorization_model} pour la DB d'embedding {db_embedding}")
    global rag_instance

    log("Instanciation de l'extractor")
    extractor = DoclingExtractor(document,1000)

    log("Instanciation du vectorizer")
    vectorizer = Vectorization(vectorization_model)

    log("Instanciation de l'embedding")
    embedding = ChromaEmbedding(db_embedding,False,3)

    log("Injection des dépendances dans le model de RAG")
    rag_instance = RagModelV2(extractor,vectorizer,embedding)

    log("Document chargé et embeddings créés")
    return {"status": "Document chargé et embeddings créés"}


@app.post("/query")
async def query_rag(request: str):
    if rag_instance is None:
        return JSONResponse(status_code=400, content={"error": "Aucun document chargé"})

    results = rag_instance.rag_query(request)
    print(results)
    return {"results": results }


if __name__ == "__main__":
    import uvicorn
    load_document(r"C:\Users\tallar\Documents\PROJETS\GenAI\docs\files\Aresbal.pdf","all-MiniLM-L6-v2","rag")
    uvicorn.run(app, host="0.0.0.0", port=8000)
