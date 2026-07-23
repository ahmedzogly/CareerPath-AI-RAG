import os
from pathlib import Path
from importlib import import_module
import streamlit as st

create_chroma_store = import_module("05_create_chroma_store").create_chroma_store
retrieve_context = import_module("06_retrieve_context").retrieve_context
rag = import_module("07_prompting")

st.set_page_config(page_title="CareerPath AI", page_icon="🎯", layout="wide")

# Streamlit Cloud secrets override local environment. No key is stored in this repository.
try:
    rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", rag.OPENROUTER_MODEL))
except Exception:
    pass

st.title("🎯 CareerPath AI")
st.caption("RAG Career & CV Assistant — answers are grounded in retrieved career documents.")
with st.sidebar:
    st.header("Career paths covered")
    st.write("Software Developer · AI & Data Analyst · AI & Data Scientist · Cybersecurity Specialist · Digital Marketing Specialist · UX/UI Designer · Business Analyst · Cloud Engineer")
    st.divider()
    if st.button("Rebuild knowledge base", use_container_width=True):
        with st.spinner("Reading documents and creating embeddings…"):
            try:
                count = create_chroma_store()
                st.success(f"Knowledge base rebuilt: {count} chunks.")
            except Exception as exc:
                st.error(str(exc))
    st.caption("Privacy: do not enter sensitive personal data. Guidance is informational and does not guarantee employment.")

if not Path("chroma_db").exists():
    with st.spinner("Preparing the career knowledge base for the first time…"):
        try:
            create_chroma_store()
        except Exception as exc:
            st.error(f"Unable to create the knowledge base: {exc}")

question = st.chat_input("Ask about careers, skills, CVs, or cover letters…")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Retrieving reliable context…"):
                sources = retrieve_context(question)
                answer = rag.generate_answer(question, sources)
            st.markdown(answer)
            with st.expander("Retrieved sources"):
                for index, item in enumerate(sources, start=1):
                    st.markdown(f"**[{index}] {item['source']} — chunk {item['chunk_number']}**")
                    st.caption(item["text"][:500] + ("…" if len(item["text"]) > 500 else ""))
        except Exception as exc:
            st.error(str(exc))
