from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

# Ton import RagModel
from src.services.RAG.extraction.document_extraction import DoclingExtractor
from src.services.RAG.vectorization.vectorization import Vectorization
from src.services.RAG.embeddings.db_embeddings import ChromaEmbedding
from src.services.RAG.rag import RagModelV2



app = FastAPI(title="RAG API", description="API pour effectuer des requêtes RAG", version="1.0.0")

# Instance globale du modèle
rag_instance = None

class QueryRequest(BaseModel):
    query: str


from dotenv import load_dotenv
import os
load_dotenv()


def load_document(document: str):
    global rag_instance

    # Init du modèle

    document= os.getenv("business_file")
    extractor = DoclingExtractor(r"C:\Users\tallar\Documents\PROJETS\GenAI\docs\files\Roland TALLA Data & Finance ENG.pdf","\n")
    vectorizer = Vectorization("all-MiniLM-L6-v2")
    embedding = ChromaEmbedding("rag",False,3)

    rag_instance = RagModelV2(extractor,vectorizer,embedding)

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
    load_document("")
    uvicorn.run(app, host="0.0.0.0", port=8000)
