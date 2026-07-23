"""Load the raw local documents used by the CareerPath RAG application."""
from pathlib import Path
from typing import Dict, List

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


def load_documents(documents_dir: str = "documents") -> List[Dict[str, str]]:
    """Return raw documents with source filename and text.

    Markdown and text are read directly. PDF support is included for easy corpus
    expansion; add PDFs only when their text can be extracted.
    """
    folder = Path(documents_dir)
    if not folder.exists():
        raise FileNotFoundError(f"Documents folder not found: {folder.resolve()}")

    docs: List[Dict[str, str]] = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            docs.append({"source": path.name, "text": text})
    return docs


if __name__ == "__main__":
    loaded = load_documents()
    print(f"Loaded {len(loaded)} documents")
    for doc in loaded:
        print(f"- {doc['source']}: {len(doc['text'])} characters")
