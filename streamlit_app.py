import os
from importlib import import_module
import streamlit as st

create_module = import_module("05_create_chroma_store")
create_chroma_store, store_is_current = create_module.create_chroma_store, create_module.store_is_current
retrieve_context = import_module("06_retrieve_context").retrieve_context
rag = import_module("07_prompting")

st.set_page_config(page_title="CareerPath AI", page_icon="🎯", layout="wide")

try:
    rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", rag.OPENROUTER_MODEL))
except Exception:
    pass

ROLES = {
    "Software Developer": {"icon": "💻", "ar": "مطور برمجيات", "summary": "Builds and improves software applications and services.", "skills": ["Programming", "Problem solving", "Software design"], "questions": ["What skills should I learn first for this career path?", "How can I write a CV for a junior Software Developer role?", "What projects should I add to my portfolio?", "Create a 3-month learning plan for this role."]},
    "AI & Data Analyst": {"icon": "📊", "ar": "محلل بيانات وذكاء اصطناعي", "summary": "Turns data into reports and insights that support decisions.", "skills": ["SQL", "Python / R", "Power BI / Tableau"], "questions": ["ما المهارات الأساسية لمسار AI & Data Analyst؟", "كيف أكتب CV مناسبًا لمحلل بيانات مبتدئ؟", "ما الأدوات التي أتعلمها أولًا؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "AI & Data Scientist": {"icon": "🧠", "ar": "عالم بيانات وذكاء اصطناعي", "summary": "Uses data, models, and experimentation to discover patterns and solve problems.", "skills": ["Statistics", "Machine learning", "Python"], "questions": ["ما الفرق بين Data Scientist وData Analyst؟", "ما المهارات التي أضعها في CV لعالم بيانات؟", "ما المشاريع المناسبة لبورتفوليو Data Scientist؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "Cybersecurity Specialist": {"icon": "🛡️", "ar": "أخصائي أمن سيبراني", "summary": "Helps protect systems, networks, and information from security risks.", "skills": ["Network security", "Risk analysis", "Security controls"], "questions": ["ما المهارات الأساسية للأمن السيبراني؟", "كيف أكتب CV لمبتدئ في Cybersecurity؟", "ما مسؤوليات Cybersecurity Specialist؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "Digital Marketing Specialist": {"icon": "📣", "ar": "أخصائي تسويق رقمي", "summary": "Improves online visibility, engagement, and marketing outcomes.", "skills": ["SEO", "Content strategy", "Analytics"], "questions": ["ما المهارات الأساسية للتسويق الرقمي؟", "كيف أكتب CV لوظيفة Digital Marketing Specialist؟", "ما مسؤوليات أخصائي التسويق الرقمي؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "UX/UI Designer": {"icon": "🎨", "ar": "مصمم تجربة وواجهة المستخدم", "summary": "Designs usable, accessible, and visually clear digital interfaces.", "skills": ["User experience", "Interface design", "Usability testing"], "questions": ["ما الفرق بين UX وUI؟", "ما الذي أضعه في Portfolio لمصمم UX/UI؟", "كيف أكتب CV لمبتدئ UX/UI Designer؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "Business Analyst": {"icon": "📈", "ar": "محلل أعمال", "summary": "Analyzes business needs and helps improve processes and decisions.", "skills": ["Requirements analysis", "Communication", "Data visualization"], "questions": ["ما مسؤوليات Business Analyst؟", "ما الفرق بين Business Analyst وData Analyst؟", "كيف أكتب CV لوظيفة محلل أعمال؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
    "Cloud Engineer": {"icon": "☁️", "ar": "مهندس حوسبة سحابية", "summary": "Supports cloud-based infrastructure, networks, and technical services.", "skills": ["Cloud platforms", "Networking", "Troubleshooting"], "questions": ["ما المهارات الأساسية لـ Cloud Engineer؟", "كيف أكتب CV لمهندس Cloud مبتدئ؟", "ما مسؤوليات Cloud Engineer؟", "اقترح خطة تعلم لمدة 3 أشهر لهذا المسار."]},
}
SOURCE_LABELS = {"01_harvard_resume_and_cover_letter.md": "Harvard — Resume & Cover Letter Guide", "02_careeronestop_cover_letters.md": "CareerOneStop — Cover Letters"}

if "selected_role" not in st.session_state: st.session_state.selected_role = "AI & Data Analyst"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "pending_question" not in st.session_state: st.session_state.pending_question = None

with st.sidebar:
    st.title("🎯 CareerPath AI")
    interface_language = st.radio("Language / اللغة", ["العربية", "English"], horizontal=True)
    st.divider()
    st.subheader("اختر المسار الوظيفي" if interface_language == "العربية" else "Choose a career path")
    st.session_state.selected_role = st.selectbox("Career path", list(ROLES), index=list(ROLES).index(st.session_state.selected_role), label_visibility="collapsed")
    if st.button("🔄 إعادة بناء قاعدة المعرفة" if interface_language == "العربية" else "🔄 Rebuild knowledge base", use_container_width=True):
        with st.spinner("Building embeddings…"):
            try: st.success(f"{create_chroma_store()} chunks are ready.")
            except Exception as exc: st.error(str(exc))
    st.divider()
    st.caption("🔒 لا تكتب بيانات شخصية حساسة. الإرشاد معلوماتي ولا يضمن الحصول على وظيفة." if interface_language == "العربية" else "🔒 Do not enter sensitive personal data. Guidance is informational and does not guarantee employment.")

if not store_is_current():
    with st.spinner("Preparing the knowledge base…"):
        try: create_chroma_store()
        except Exception as exc: st.error(f"Knowledge-base error: {exc}")

role = ROLES[st.session_state.selected_role]
page_title = "مساعدك المهني الذكي" if interface_language == "العربية" else "Your smart career assistant"
st.title(f"{role['icon']} CareerPath AI")
st.caption("مساعد مهني يعتمد على مصادر مسترجعة مع citations واضحة." if interface_language == "العربية" else "A source-grounded career assistant with clear citations.")

# Compact dynamic role card
st.markdown(f"### {role['icon']} {role['ar']} — {st.session_state.selected_role}")
st.info(("نبذة: " if interface_language == "العربية" else "Overview: ") + role['summary'])
with st.expander("المهارات والمحاور الرئيسية" if interface_language == "العربية" else "Key skills and focus areas"):
    st.markdown(" · ".join(f"`{skill}`" for skill in role["skills"]))
    st.caption("هذه البطاقة للتوجيه السريع؛ الإجابة التفصيلية تعتمد على الوثائق المسترجعة.")

tab_chat, tab_explore, tab_cv = st.tabs(["💬 اسأل المساعد" if interface_language == "العربية" else "💬 Ask assistant", "🧭 استكشف المسارات" if interface_language == "العربية" else "🧭 Explore paths", "📄 CV & Cover Letter"])

with tab_chat:
    st.subheader("أسئلة مقترحة" if interface_language == "العربية" else "Suggested questions")
    cols = st.columns(2)
    for i, question in enumerate(role["questions"]):
        if cols[i % 2].button(question, key=f"suggested_{i}", use_container_width=True):
            st.session_state.pending_question = question
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]): st.markdown(message["content"])
    typed = st.chat_input("اكتب سؤالك عن المسار أو الـCV…" if interface_language == "العربية" else "Ask about this career path or your CV…")
    question = st.session_state.pending_question or typed
    if question:
        st.session_state.pending_question = None
        with st.chat_message("user"): st.markdown(question)
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("assistant"):
            try:
                with st.spinner("جاري البحث في المصادر…" if interface_language == "العربية" else "Retrieving trusted context…"):
                    sources = retrieve_context(question, career_path=st.session_state.selected_role)
                    answer = rag.generate_answer(question, sources, "Arabic" if interface_language == "العربية" else "English")
                st.markdown(answer)
                with st.expander("📚 المصادر المستخدمة" if interface_language == "العربية" else "📚 Retrieved sources"):
                    for index, item in enumerate(sources, 1):
                        label = SOURCE_LABELS.get(item["source"], item["career_path"])
                        st.markdown(f"**[{index}] {label} — chunk {item['chunk_number']}**")
                        st.caption(item["text"][:380] + ("…" if len(item["text"]) > 380 else ""))
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            except Exception as exc: st.error(str(exc))

with tab_explore:
    st.subheader("استكشف المسارات الثمانية" if interface_language == "العربية" else "Explore the eight career paths")
    for name, data in ROLES.items():
        with st.expander(f"{data['icon']} {data['ar']} — {name}"):
            st.write(data["summary"])
            st.write(" · ".join(data["skills"]))
            if st.button("اختيار هذا المسار" if interface_language == "العربية" else "Choose this path", key=f"role_{name}"):
                st.session_state.selected_role = name
                st.rerun()

with tab_cv:
    st.subheader("CV & Cover Letter Assistant")
    st.caption("اكتب معلومات عامة فقط ولا تضف أرقام هوية أو عناوين أو بيانات حساسة." if interface_language == "العربية" else "Use general information only; do not add IDs, addresses, or sensitive personal data.")
    level = st.selectbox("المستوى" if interface_language == "العربية" else "Level", ["Beginner", "Intermediate", "Experienced"])
    skills = st.text_area("مهاراتك الحالية" if interface_language == "العربية" else "Your current skills", placeholder="SQL, Excel, Python, Power BI…")
    experience = st.text_area("التعليم أو الخبرة ذات الصلة" if interface_language == "العربية" else "Relevant education or experience", placeholder="University projects, internship, volunteer work…")
    c1, c2 = st.columns(2)
    if c1.button("إنشاء Professional Summary" if interface_language == "العربية" else "Create Professional Summary", use_container_width=True):
        st.session_state.pending_question = f"Write a concise professional summary for a {level} {st.session_state.selected_role} candidate. Current skills: {skills}. Relevant education or experience: {experience}. Keep it truthful and use only the supplied details."
        st.session_state.active_tab = "chat"
        st.info("انتقل إلى تبويب اسأل المساعد لرؤية النتيجة." if interface_language == "العربية" else "Go to Ask assistant to see the result.")
    if c2.button("إنشاء Cover Letter" if interface_language == "العربية" else "Create Cover Letter", use_container_width=True):
        st.session_state.pending_question = f"Draft a concise cover letter for a {level} {st.session_state.selected_role} role. Skills: {skills}. Relevant education or experience: {experience}. Use placeholders for company and hiring manager. Keep it truthful."
        st.info("انتقل إلى تبويب اسأل المساعد لرؤية النتيجة." if interface_language == "العربية" else "Go to Ask assistant to see the result.")
