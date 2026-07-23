"""Split documents into overlapping word chunks while keeping citation metadata."""
from typing import Dict, List


def chunk_documents(documents: List[Dict[str, str]], chunk_size: int = 220, overlap: int = 40) -> List[Dict[str, object]]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks: List[Dict[str, object]] = []
    for doc in documents:
        words = doc["text"].split()
        step = chunk_size - overlap
        for number, start in enumerate(range(0, len(words), step), start=1):
            piece = words[start:start + chunk_size]
            if len(piece) < 20:  # do not embed tiny trailing fragments
                continue
            chunks.append({
                "id": f"{doc['source']}::chunk::{number}",
                "text": " ".join(piece),
                "source": doc["source"],
                "chunk_number": number,
            })
    return chunks
