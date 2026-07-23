"""Build a persistent Chroma vector store from the project documents."""
from pathlib import Path
import chromadb
from chromadb.config import Settings
from importlib import import_module

load_documents = import_module("01_documents").load_documents
preprocess_documents = import_module("02_preprocessing").preprocess_documents
chunk_documents = import_module("03_chunking").chunk_documents
embed_texts = import_module("04_vector_representation").embed_texts

COLLECTION_NAME = "careerpath_documents"


def create_chroma_store(documents_dir: str = "documents", persist_dir: str = "chroma_db") -> int:
    raw_documents = load_documents(documents_dir)
    chunks = chunk_documents(preprocess_documents(raw_documents))
    if not chunks:
        raise ValueError("No usable chunks were created from the documents.")

    client = chromadb.PersistentClient(path=str(Path(persist_dir)), settings=Settings(anonymized_telemetry=False))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        collection.add(
            ids=[str(x["id"]) for x in batch],
            documents=[str(x["text"]) for x in batch],
            metadatas=[{"source": str(x["source"]), "chunk_number": int(x["chunk_number"])} for x in batch],
            embeddings=embed_texts([str(x["text"]) for x in batch]),
        )
    return len(chunks)


if __name__ == "__main__":
    print(f"Created Chroma store with {create_chroma_store()} chunks.")
