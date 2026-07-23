# Digilians Career Path AI — RAG Career & CV Assistant

Made By Ahmed Zoghli For Digilians.

A Python/Streamlit Retrieval-Augmented Generation project that answers career, CV, and cover-letter questions using a local document corpus and source citations.

## Covered career paths

- Software Developer
- AI & Data Analyst
- AI & Data Scientist
- Cybersecurity Specialist
- Digital Marketing Specialist
- UX/UI Designer
- Business Analyst
- Cloud Engineer

## Required project flow

`documents → preprocessing → chunking → embeddings → Chroma vector store → retrieval → grounded prompt → Streamlit UI`

## Run locally

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="your_key"       # Windows PowerShell: $env:OPENROUTER_API_KEY="your_key"
export OPENROUTER_MODEL="openai/gpt-4o-mini" # optional
streamlit run streamlit_app.py
```

The first run creates `chroma_db/` from the contents of `documents/`. This local generated folder is intentionally ignored by Git. Do not commit an API key or a `.env` file.

## Streamlit Cloud secrets

In **Manage app → Secrets**, use valid TOML:

```toml
OPENROUTER_API_KEY = "your_openrouter_key_here"
OPENROUTER_MODEL = "openai/gpt-4o-mini"
```

## Citation behavior

Each response receives retrieved chunks in its prompt and is instructed to cite them as `[1]`, `[2]`, etc. The interface also shows the source filename and chunk number in **Retrieved sources**.

## Corpus note

Occupation profiles use O*NET data. They are useful for role tasks, skills, and technology context, but are U.S.-oriented; the application should not present them as local Egypt salary, labor-law, or licensing advice.
