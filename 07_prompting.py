"""Prompt construction and OpenRouter generation for grounded answers."""
import html
import os
import re
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """You are CareerPath AI, a career guidance assistant. Answer in the language requested by the user interface.
Use ONLY the supplied retrieved context for factual claims about roles, skills, tasks, resumes, and cover letters. If the context is insufficient, say so clearly. Do not invent salaries, local labor-law requirements, certificates, or job-market facts. Do not guarantee employment.
Write clean Markdown only: headings, bullets, numbered lists, and Markdown tables are allowed. Never write HTML tags such as <br>, <table>, or <div>.
Cite factual claims using [1], [2], etc., exactly as supplied in the context."""


def build_prompt(question: str, retrieved_chunks: list[dict], response_language: str) -> str:
    context = "\n\n".join(
        f"[{i}] Source: {item['source']} | Career path: {item.get('career_path', '')} | Chunk: {item['chunk_number']}\n{item['text']}"
        for i, item in enumerate(retrieved_chunks, start=1)
    )
    return f"Response language: {response_language}\n\nRetrieved context:\n{context}\n\nUser question: {question}\n\nAnswer with citations."


def clean_answer(answer: str) -> str:
    """Keep an accidental HTML line break from appearing literally in the UI."""
    answer = html.unescape(answer)
    answer = re.sub(r"<br\s*/?>", "\n", answer, flags=re.IGNORECASE)
    return re.sub(r"</?(?:div|p)\b[^>]*>", "\n", answer, flags=re.IGNORECASE).strip()


def generate_answer(question: str, retrieved_chunks: list[dict], response_language: str = "Arabic") -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY. Add it to Streamlit secrets or your environment.")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={"model": OPENROUTER_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_prompt(question, retrieved_chunks, response_language)}], "temperature": 0.2},
        timeout=60,
    )
    response.raise_for_status()
    return clean_answer(response.json()["choices"][0]["message"]["content"])
