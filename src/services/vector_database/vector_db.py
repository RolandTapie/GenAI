from dotenv import load_dotenv
import os
from abc import ABC
from sentence_transformers import SentenceTransformer
from src.services.vectorization.vectorization import Vectorization
import chromadb
from src.services.logs.loggers import log

load_dotenv()
model=os.getenv("model_path")

class InterfaceEmbedding(ABC):
    def create_collection(self,collection_name):
        pass

    def embed_texts(self,texts):
        pass

    def add_to_collection(self, texts):
        pass

    def query(self,query):
        pass

    def get_client(self):
        pass

class ChromaEmbedding(InterfaceEmbedding):
    def __init__(self,vector_model, db_name, context_extend=False, limit=2):
        self.embedding_model=Vectorization(vector_model)
        self.vector_model = vector_model
        self.client = chromadb.PersistentClient(path=f"./{db_name}")
        self.context_extend = context_extend
        self.collection= None
        self.limit=limit

    def create_collection(self,collection_name):
        pass

    def embed_texts(self,texts):
        return self.embedding_model.transform(texts)

    def get_client(self):
        return self.client

    def add_to_collection(self, texts):
        metadata = [{'source':f'metadata{i}','auteur': 'auteur', 'type': 'types'} for i, text in enumerate(texts)]
        collection_name=self.vector_model
        try:
            # Essaye de récupérer la collection
            collection = self.client.get_collection(name=collection_name)
            log(f"La collection '{collection_name}' existe ✅")

            # Si elle existe, on peut la supprimer
            self.client.delete_collection(name=collection_name)
            log(f"Collection '{collection_name}' supprimée ❌")

            log("Création d'une nouvelle collection")
            collection = self.client.get_or_create_collection(name=collection_name,metadata={"hnsw:space": "cosine"})
            self.collection =  collection
            emb = self.embed_texts(texts)
            for t,e in zip(texts,emb):
                print(t)
                print(e)
            self.collection.add(documents=texts,embeddings=emb,metadatas= metadata,ids=[str(i) for i in range(len(texts))])
        except Exception as e:

            print(f"La collection '{collection_name}' n'existe pas.")
            print("Création d'une nouvelle collection")
            collection = self.client.get_or_create_collection(name=collection_name,metadata={"hnsw:space": "cosine"})
            self.collection =  collection

            emb = self.embed_texts(texts)
            for t,e in zip(texts,emb):
                print(t)
                print(e)
            self.collection.add(documents=texts,embeddings=emb,metadatas= metadata,ids=[str(i) for i in range(len(texts))])
    #
    # try:
    #     self.collection = self.client.get_collection(name=collection_name)
    #     print("La collection existe")
    # except Exception:
    #     collection = self.client.get_or_create_collection(name=collection_name)
    #     self.collection =  collection
    #     print("La collection n'existe pas")
    #
    #     self.collection.add(
    #     documents=texts,
    #     embeddings=self.embed_texts(texts),
    #     ids=[str(i) for i in range(len(texts))]
    #     )

    def query(self,query):

        results = self.collection.query(
            query_embeddings=self.embed_texts(query),
            n_results=self.limit
        )

        final_res = results['documents'][0]
        meta_res = results['metadatas'][0]
        print("la cible")
        k=0
        for doc,dis,id in zip(results['documents'][0],results['distances'][0],results['ids'][0]):
            print(k,":",id,":",dis,":",doc)
            k=k+1
        # print("la distance")
        # for dis in results['distances'][0]:
        #     print(dis)
        # print("l'indice'")
        # for id in results['ids'][0]:
        #     print(id)

        if self.context_extend == True:

            result = self.collection.get()  # sans ids, récupère tous
            ids_max = max([int(i) for i in result['ids']])
            resultok = results['documents'][0]
            indices = results['ids'][0]
            mix = []
            for i in indices:
                mix.append(self.collection.get(ids=[str(i)])['documents'][0])
                if int(i)+1<=ids_max:
                    mix.append(self.collection.get(ids=[str(int(i)+1)])['documents'][0])
                if int(i)-1>=0:
                    mix.append(self.collection.get(ids=[str(int(i)-1)])['documents'][0])

            final_set= set()
            final_res = []
            for document in mix:
                print(document)
                if document not in final_set:
                    final_res.append(document)
                    final_set.add(document)

        return final_res, meta_res

class FaissEmbedding(InterfaceEmbedding):
    def __init__(self, db_name, context_extend=False,model_path=os.getenv("model_path"), limit=2):
        self.embedding_model=SentenceTransformer(model_path)
        self.client = chromadb.PersistentClient(path=f"./{db_name}")
        self.context_extend = context_extend
        self.collection= None
        self.limit=limit

    def create_collection(self,collection_name):
        collection = self.client.get_or_create_collection(name="docs")
        self.collection =  collection

    def embed_texts(self,texts):
        return [self.embedding_model.encode(t).tolist() for t in texts]

    def add_to_collection(self, texts):
        self.collection.add(
            documents=texts,
            embeddings=self.embed_texts(texts),
            ids=[str(i) for i in range(len(texts))]
        )

    def query(self,query):

        results = self.collection.query(
            query_embeddings=[self.embedding_model.encode(query).tolist()],
            n_results=self.limit
        )

        final_res= results['documents'][0]

        if self.context_extend == True:

            result = self.collection.get()  # sans ids, récupère tous
            ids_max = max([int(i) for i in result['ids']])
            resultok = results['documents'][0]
            indices = results['ids'][0]
            mix = []
            for i in indices:
                mix.append(self.collection.get(ids=[str(i)])['documents'][0])
                if int(i)+1<=ids_max:
                    mix.append(self.collection.get(ids=[str(int(i)+1)])['documents'][0])
                if int(i)-1>=0:
                    mix.append(self.collection.get(ids=[str(int(i)-1)])['documents'][0])

            final_set= set()
            final_res = []
            for document in mix:
                print(document)
                if document not in final_set:
                    final_res.append(document)
                    final_set.add(document)

        return final_res

#
# texts = [
#     "Bonjour le monde",
#     "SentenceTransformers fonctionne très bien localement",
#     "ChromaDB peut stocker les embeddings sur disque"
# ]
#
# db=ChromaEmbedding("testdbx")
# db.create_collection("docs")
# db.add_to_collection(texts)
# db.query("Bonjour comment ca va?")