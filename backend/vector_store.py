import chromadb
from chromadb.utils import embedding_functions
from backend.config import PERSIST_DIR, COLLECTION_NAME, EMBED_MODEL, OPENAI_API_KEY


def get_client():
    return chromadb.PersistentClient(path=PERSIST_DIR)


def get_embedding_function():
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBED_MODEL,
    )


def get_collection():
    client = get_client()
    ef = get_embedding_function()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def query_collection(collection, text, n_results=5):
    results = collection.query(query_texts=[text], n_results=n_results)
    return results
