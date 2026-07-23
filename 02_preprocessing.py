"""Clean raw career-guide text before it is chunked and embedded."""
import re
from typing import Dict, List


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)
    return text.strip()


def preprocess_documents(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [{**doc, "text": clean_text(doc["text"])} for doc in documents if clean_text(doc["text"])]
