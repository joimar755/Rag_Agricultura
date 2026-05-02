import os
from ollama import Client
from ollama import web_search, web_fetch

# RAG
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# =========================
# 🔐 CONFIG OLLAMA
# =========================
ollama_api_key = os.getenv('OLLAMA_API_KEY')

client = Client(
    host='http://localhost:11434/',
    headers={'Authorization': f'Bearer {ollama_api_key}'}
)

available_tools = {
    'web_fetch': web_fetch,
    'web_search': web_search
}


loader = PyPDFLoader("manual_agricola.pdf")
documents = loader.load()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

documents = text_splitter.split_documents(documents)


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

vector_store = Chroma(
    collection_name="rag_db",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Solo agrega si está vacío (evita duplicados)
if len(vector_store.get()['ids']) == 0:
    vector_store.add_documents(documents)


retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)




#funcion para el llamadao de la ruta
def agronomy_query_rag(user_input: str):
    docs = retriever.invoke(user_input)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
Eres un experto agrónomo especializado en buenas prácticas agrícolas.

Usa SOLO esta información del manual:
{context}

Responde de forma clara y técnica.

Pregunta:
{user_input}
"""
    messages = [
        {
            "role": "system",
            "content": "Eres un agrónomo experto. Responde solo con base en el contexto proporcionado."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        result = client.chat(
            model="gpt-oss:120b-cloud",
            messages=messages,
            tools=[web_fetch, web_search]
        )
    except Exception as e:
        return {"error": str(e)}

    if result.message.content:
        return result.message.content

    return "No se obtuvo respuesta"