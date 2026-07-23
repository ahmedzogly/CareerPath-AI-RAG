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
STORE_VERSION = "2"

# This mapping powers role-focused retrieval without changing source filenames.
CAREER_PATH_BY_SOURCE = {
    "03_onet_data_scientists.md": "AI & Data Scientist",
    "04_onet_software_developers.md": "Software Developer",
    "11_onet_ai_data_analyst_business_intelligence.md": "AI & Data Analyst",
    "12_onet_cybersecurity_specialist.md": "Cybersecurity Specialist",
    "13_onet_digital_marketing_specialist.md": "Digital Marketing Specialist",
    "14_onet_ux_ui_designer.md": "UX/UI Designer",
    "15_onet_business_analyst.md": "Business Analyst",
    "16_onet_cloud_engineer.md": "Cloud Engineer",
}


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
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine", "store_version": STORE_VERSION}
    )

    for start in range(0, len(chunks), 64):
        batch = chunks[start:start + 64]
        collection.add(
            ids=[str(x["id"]) for x in batch],
            documents=[str(x["text"]) for x in batch],
            metadatas=[{
                "source": str(x["source"]),
                "chunk_number": int(x["chunk_number"]),
                "career_path": CAREER_PATH_BY_SOURCE.get(str(x["source"]), "General Career & CV Guidance"),
            } for x in batch],
            embeddings=embed_texts([str(x["text"]) for x in batch]),
        )
    return len(chunks)


def store_is_current(persist_dir: str = "chroma_db") -> bool:
    try:
        client = chromadb.PersistentClient(path=str(Path(persist_dir)), settings=Settings(anonymized_telemetry=False))
        return client.get_collection(COLLECTION_NAME).metadata.get("store_version") == STORE_VERSION
    except Exception:
        return False


if __name__ == "__main__":
    print(f"Created Chroma store with {create_chroma_store()} chunks.")
