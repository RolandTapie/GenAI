import os
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

import openai
import requests

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

#from src.services.llm_generation.llm import model
from src.services.vector_database.vector_db import ChromaEmbedding
from src.services.extract_documents.document_extraction import DoclingExtractor
from src.services.vectorization.vectorization import Vectorization


def rag_api(host,port,root,question):
    print(f"http://{host}:{port}/{root}?request={question}")
    response = requests.post(f"http://{host}:{port}/{root}?request={question}")
    print(response.text)
    return response.text

class RagModel:
    def __init__(self, doc_path,vector_model="all-MiniLM-L6-v2", embedding_model="all-MiniLM-L6-v2"):
        self.vectors_db=None
        self.vector_model = vector_model
        self.embedding_model=embedding_model
        self.document_path = doc_path
        self.local_embedding=vector_model
        self.local_embeddings=None
        self.local_model=vector_model
        self.paragraphs=None
        self.embeddings()

    def embeddings(self):
        self.paragraphs=DoclingExtractor(self.document_path).run()
        self.vectors_db = ChromaEmbedding(self.vector_model,"rag",True)
        self.vectors_db.create_collection("docs")
        self.vectors_db.add_to_collection(self.paragraphs)

    def rag_query(self,query):
        print(f"la question est : {query}")
        return self.vectors_db.query(query)
        # if self.local_embedding == "Mistral":
        #     print(f"la question est : {query}")
        #     return self.vectors_db.query(query)
        # else:
        #     return self.vectors_db.similarity_search(query, k=5)

from src.services.RAG.extraction.document_extraction import DoclingExtractor
from src.services.RAG.vectorization.vectorization import Vectorization
from src.services.RAG.embeddings.db_embeddings import ChromaEmbedding
from src.services.logs.loggers import log

class RagModelV2:
    def __init__(self, extractor: DoclingExtractor, vector: Vectorization, embedding: ChromaEmbedding):

        log("Injection de l'extracteur")
        self.extractor = extractor
        log("Injection du vectorizer")
        self.vector = vector
        log("Injection de l'embedding")
        self.embedding = embedding
        log(f"Extraction des chunks : {extractor.get_document()}")
        self.chunks, self.meta = extractor.run()
        log(f" {len(self.chunks)} chunks extraits")
        log(f"Vectorisation des chunks")
        self.vectors = vector.transform(self.chunks)
        log(f" {len(self.vectors )} chunks vectorisés")
        log(f"Embedding des vecteurs")
        self.embedded = embedding.add_to_collection(self.chunks,self.vectors)
        log(f"RAG constitué")

    def rag_query(self,query):
        log(f"consulation du RAG : {query}")
        print(f"la question est : {query}")
        query_vector = self.vector.transform(query)
        result = self.embedding.query(query_vector)
        log(f"reponse du RAG : {result}")
        return result