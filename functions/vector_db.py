from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer
import chromadb
load_dotenv()
model=os.getenv("model_path")
class ChromaEmbedding:
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