from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

# 1. Charger les documents
loader = PyMuPDFLoader(r"C:\Users\tallar\Documents\PROJETS\GenAI\ChatBot\files\IntroML_Azencott.pdf") # remplacez par vos documents
docs = loader.load()

# 2. Découper les documents
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 3. Embedding + stockage dans Chroma
embedding_model = SentenceTransformerEmbeddings(model_name=r"C:\Users\tallar\Documents\PROJETS\GenAI\LLM_Model\Embedding\models--sentence-transformers--all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(chunks, embedding_model, persist_directory="./db")

# 4. LLM local via Ollama
llm = Ollama(model="mistral")  # ou "mistral", "gemma", etc.

# 5. Chaîne RAG avec Retriever
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    chain_type="stuff"
)

# 6. Poser une question
query = "Quels sont les points clés du document ?"
result = qa_chain.run(query)

print("\n💬 Réponse générée :\n", result)
