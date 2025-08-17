from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os

# Ton import RagModel
from rag import RagModel  # <-- ton fichier contenant la classe RagModel

app = FastAPI(title="RAG API", description="API pour effectuer des requêtes RAG", version="1.0.0")

# Instance globale du modèle
rag_instance = None

class QueryRequest(BaseModel):
    query: str


from dotenv import load_dotenv
import os
load_dotenv()
document= os.getenv("business_file")

print(f"chargement du fichier: \n {document}")

def load_document(document: str):
    global rag_instance

    # Init du modèle

    rag_instance = RagModel(document,"all-MiniLM-L6-v2")

    return {"status": "Document chargé et embeddings créés", "filename": document}


@app.post("/query")
async def query_rag(request: str):
    if rag_instance is None:
        return JSONResponse(status_code=400, content={"error": "Aucun document chargé"})

    results = rag_instance.rag_query(request)
    print(results)
    return {"results": results }


if __name__ == "__main__":
    import uvicorn
    load_document(document)
    uvicorn.run(app, host="0.0.0.0", port=8000)
