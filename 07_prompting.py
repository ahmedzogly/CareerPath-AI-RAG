"""Prompt construction and OpenRouter generation for grounded answers."""
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """You are CareerPath AI, a career guidance assistant. Answer in the same language as the user.
Use ONLY the supplied retrieved context for factual claims about roles, skills, tasks, resumes, and cover letters.
If the context is insufficient, say so clearly and suggest what information is needed. Do not invent salaries, local labor-law requirements, certificates, or job-market facts.
Give practical, concise advice. Do not claim guaranteed employment. Cite sources using [1], [2], etc. exactly as supplied in the context."""


def build_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{i}] Source: {item['source']} | Chunk: {item['chunk_number']}\n{item['text']}"
        for i, item in enumerate(retrieved_chunks, start=1)
    )
    return f"Retrieved context:\n{context}\n\nUser question: {question}\n\nAnswer with citations."


def generate_answer(question: str, retrieved_chunks: list[dict]) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY. Add it to Streamlit secrets or your environment.")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        json={"model": OPENROUTER_MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_prompt(question, retrieved_chunks)}], "temperature": 0.2},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
