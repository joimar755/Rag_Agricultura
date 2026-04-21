from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# 📄 1. Cargar PDF
loader = PyPDFLoader("manual_agricola.pdf")  # <-- cambia por tu ruta
documents = loader.load()

# ✂️ 2. Dividir en chunks (MUY IMPORTANTE)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,     # tamaño recomendado
    chunk_overlap=50    # evita cortar ideas
)

documents = text_splitter.split_documents(documents)

# 🧠 3. Embeddings con Ollama
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"  # o mxbai-embed-large
)

# 🗄️ 4. Crear base vectorial (Chroma)
vector_store = Chroma(
    collection_name="rag_db",
    embedding_function=embeddings,
    persist_directory="./chroma_db"  # guarda en disco
)

# ➕ 5. Agregar documentos
vector_store.add_documents(documents)

# 🔍 6. Crear retriever
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}  # top 3 resultados
)