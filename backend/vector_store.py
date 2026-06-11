import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import PERSIST_DIR, COLLECTION_NAME, EMBED_MODEL, OPENAI_API_KEY


def get_client():
    return chromadb.PersistentClient(path=PERSIST_DIR)


def get_embedding_function():
    return OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model=EMBED_MODEL,
    )


def get_collection():
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=get_embedding_function(),
        collection_metadata={"hnsw:space": "cosine"},
    )


def query_collection(collection, text, n_results=5):
    results = collection.similarity_search_with_score(text, k=n_results)
    return [
        {"document": document.page_content, "metadata": document.metadata, "distance": distance}
        for document, distance in results
    ]
