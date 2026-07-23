"""Retrieve the most relevant chunks and source metadata from Chroma."""
from pathlib import Path
from importlib import import_module
import chromadb
from chromadb.config import Settings

embed_texts = import_module("04_vector_representation").embed_texts
COLLECTION_NAME = "careerpath_documents"


def retrieve_context(question: str, persist_dir: str = "chroma_db", top_k: int = 4, career_path: str | None = None):
    if not Path(persist_dir).exists():
        raise FileNotFoundError("Vector store is missing. Build it first.")
    client = chromadb.PersistentClient(path=str(Path(persist_dir)), settings=Settings(anonymized_telemetry=False))
    collection = client.get_collection(COLLECTION_NAME)
    query_args = {
        "query_embeddings": embed_texts([question]),
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    # A role selection searches its occupation profile plus the CV/cover-letter guides.
    if career_path and career_path != "All Career Paths":
        query_args["where"] = {"career_path": {"$in": [career_path, "General Career & CV Guidance"]}}
    result = collection.query(**query_args)
    return [{
        "text": text,
        "source": metadata["source"],
        "chunk_number": metadata["chunk_number"],
        "career_path": metadata.get("career_path", "General Career & CV Guidance"),
        "distance": float(distance),
    } for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])]
