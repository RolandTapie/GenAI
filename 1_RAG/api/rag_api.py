from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from src.services.RAG.rag import RagModel

tools_path = os.getenv("tools")
tools_lists = list_of_tools(tools_path)
# Ton import RagModel
#from rag import RagModel  # <-- ton fichier contenant la classe RagModel

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

    rag_instance = RagModel(document,"all-MiniLM-L6-v2","all-MiniLM-L6-v2",10)

    return {"status": "Document chargé et embeddings créés", "filename": document}


@app.post("/query")
async def query_rag(request: str):
    if rag_instance is None:
        return JSONResponse(status_code=400, content={"error": "Aucun document chargé"})

    results, meta = rag_instance.rag_query(request)
    print (results)
    #return {"results": results }
    return results,meta


if __name__ == "__main__":
    import uvicorn
    load_document(document)
    uvicorn.run(app, host="0.0.0.0", port=8000)
