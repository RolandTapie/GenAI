from dotenv import load_dotenv
import os
from abc import ABC
from sentence_transformers import SentenceTransformer
from src.services.logs.loggers import log

import chromadb
load_dotenv()
local_model=os.getenv("model_path")
local_model=r"C:\Users\tallar\Documents\PROJETS\GenAI\LLM_Model\Embedding\models--sentence-transformers--all-MiniLM-L6-v2"
openai_key = os.getenv("openai_key")
from openai import OpenAI
import numpy as np
import json


MODEL = "text-embedding-3-small"

class Vectorization():

    def __init__(self, vector_model):
        self.vector_model=vector_model
        if self.vector_model == "all-MiniLM-L6-v2":
            log(f"Génération du model de vectorization {self.vector_model}")
            self.embedding_model=SentenceTransformer(local_model)

        elif self.vector_model == "openai":
            self.embedding_model = OpenAI(api_key=openai_key)

    def transform(self, texts):
        if self.vector_model == "all-MiniLM-L6-v2":
            self.result = [self.embedding_model.encode(t) for t in texts]  #.to_list()
        elif self.vector_model == "openai":
            resp = self.embedding_model.embeddings.create(
                model=MODEL,
                input=texts
            )
            self.result = [d.embedding for d in resp.data]
        return self.result

    def get_vectors(self):
        return self.result