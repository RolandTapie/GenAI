from dotenv import load_dotenv
import os
from abc import ABC
from sentence_transformers import SentenceTransformer
import chromadb
load_dotenv()
local_model=os.getenv("model_path")
openai_key = os.getenv("openai_key")
from openai import OpenAI
import numpy as np
import json


MODEL = "text-embedding-3-small"

class Vectorization():

    def __init__(self, vector_model):
        self.vector_model=vector_model
        if self.vector_model == "all-MiniLM-L6-v2":
            self.embedding_model=SentenceTransformer(local_model)

        elif self.vector_model == "openai":
            self.embedding_model = OpenAI(api_key=openai_key)

    def transform(self, texts):
        if self.vector_model == "all-MiniLM-L6-v2":
            self.result = [self.embedding_model.encode(t).tolist() for t in texts]
        elif self.vector_model == "openai":
            resp = self.embedding_model.embeddings.create(
                model=MODEL,
                input=texts
            )
            self.result = [d.embedding for d in resp.data]
        return self.result

    def get_vectors(self):
        return self.result