import os
import json
import re
from importlib import import_module
import streamlit as st

create_module = import_module("05_create_chroma_store")
create_chroma_store, store_is_current = create_module.create_chroma_store, create_module.store_is_current
retrieve_context = import_module("06_retrieve_context").retrieve_context
rag = import_module("07_prompting")
resume_tools = import_module("08_resume_builder")

st.set_page_config(page_title="Digilians Career Path AI", page_icon="🎯", layout="wide")

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
if "resume_experience" not in st.session_state: st.session_state.resume_experience = [{}]
if "resume_education" not in st.session_state: st.session_state.resume_education = [{}]
if "resume_projects" not in st.session_state: st.session_state.resume_projects = [{}]
if "resume_links" not in st.session_state: st.session_state.resume_links = [{}]
if "generated_cv" not in st.session_state: st.session_state.generated_cv = None

with st.sidebar:
    st.title("🎯 Digilians Career Path AI")
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
st.title(f"{role['icon']} Digilians Career Path AI")
st.caption("Made By Ahmed Zoghli For Digilians")
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
    st.subheader("CV Builder Pro — منشئ سيرة ذاتية احترافية")
    st.caption("املأ معلوماتك الحقيقية فقط. سيعيد المساعد تنظيمها وتخصيصها للمسار المختار دون اختلاق خبرات أو إنجازات.")
    cv_personal, cv_exp, cv_edu, cv_skills, cv_projects, cv_links, cv_theme = st.tabs(["👤 Personal", "💼 Experience", "🎓 Education", "✨ Skills", "📁 Projects", "🔗 Links", "🎨 Theme"])
    with cv_personal:
        a, b = st.columns(2)
        with a:
            st.text_input("Full name / الاسم الكامل", key="cv_name")
            st.text_input("Email", key="cv_email")
            st.text_input("Location / الموقع", key="cv_location", placeholder="Al Mansurah, Egypt")
        with b:
            st.text_input("Target title / المسمى المستهدف", value=st.session_state.selected_role, key="cv_title")
            st.text_input("Phone / الهاتف", key="cv_phone")
            st.text_input("Website / Portfolio", key="cv_website")
        st.text_area("About you / نبذة أولية", key="cv_about", height=120, placeholder="اكتب ملخصًا حقيقيًا عن دراستك، اهتماماتك، وخبراتك أو تدريباتك…")
    with cv_exp:
        st.caption("أضف الخبرات الحقيقية. استخدم الوصف لذكر مسؤولياتك أو إنجازاتك، وسيتولى المساعد تحسين الصياغة.")
        for i, _ in enumerate(st.session_state.resume_experience):
            with st.expander(f"Experience {i+1}", expanded=True):
                x, y = st.columns(2)
                x.text_input("Role", key=f"exp_role_{i}"); y.text_input("Company", key=f"exp_company_{i}")
                x, y = st.columns(2)
                x.text_input("Start", key=f"exp_start_{i}", placeholder="2024"); y.text_input("End", key=f"exp_end_{i}", placeholder="Present or 2025")
                st.text_area("Description / achievements", key=f"exp_desc_{i}", height=90)
        if st.button("＋ Add experience", key="add_exp"): st.session_state.resume_experience.append({}); st.rerun()
    with cv_edu:
        for i, _ in enumerate(st.session_state.resume_education):
            with st.expander(f"Education {i+1}", expanded=True):
                st.text_input("School / University", key=f"edu_school_{i}")
                x, y = st.columns(2); x.text_input("Degree", key=f"edu_degree_{i}"); y.text_input("Field of study", key=f"edu_field_{i}")
                x, y = st.columns(2); x.text_input("Start", key=f"edu_start_{i}"); y.text_input("End", key=f"edu_end_{i}")
        if st.button("＋ Add education", key="add_edu"): st.session_state.resume_education.append({}); st.rerun()
    with cv_skills:
        st.text_area("Skills (comma separated) / المهارات", key="cv_skills", height=150, placeholder="Python, SQL, Excel, Power BI, Communication…")
        st.caption("ضع المهارات التي تمتلكها فعلًا فقط. سيقوم المساعد بترتيب الأكثر ارتباطًا بالوظيفة المستهدفة.")
    with cv_projects:
        for i, _ in enumerate(st.session_state.resume_projects):
            with st.expander(f"Project {i+1}", expanded=True):
                x, y = st.columns(2); x.text_input("Project name", key=f"project_name_{i}"); y.text_input("Project link (optional)", key=f"project_link_{i}")
                st.text_area("Description", key=f"project_desc_{i}", height=80)
        if st.button("＋ Add project", key="add_project"): st.session_state.resume_projects.append({}); st.rerun()
    with cv_links:
        for i, _ in enumerate(st.session_state.resume_links):
            x, y = st.columns(2); x.text_input("Platform", key=f"link_label_{i}", placeholder="LinkedIn"); y.text_input("URL", key=f"link_url_{i}")
        if st.button("＋ Add link", key="add_link"): st.session_state.resume_links.append({}); st.rerun()
    with cv_theme:
        cv_language = st.radio("CV language / لغة السيرة", ["English", "Arabic"], horizontal=True)
        accent = st.selectbox("Accent color", ["#4f46e5", "#0f766e", "#be185d", "#b45309"], format_func=lambda x: {"#4f46e5":"Indigo", "#0f766e":"Teal", "#be185d":"Rose", "#b45309":"Amber"}[x])
        st.caption("تنسيق ATS بسيط وواضح. يوصى بالإنجليزية لملف PDF إذا كانت الجهة المستهدفة تستخدم الإنجليزية.")

    def nonempty(value): return str(value or "").strip()
    def profile_data():
        experiences=[]
        for i in range(len(st.session_state.resume_experience)):
            item={"role":nonempty(st.session_state.get(f"exp_role_{i}")), "company":nonempty(st.session_state.get(f"exp_company_{i}")), "start":nonempty(st.session_state.get(f"exp_start_{i}")), "end":nonempty(st.session_state.get(f"exp_end_{i}")), "description":nonempty(st.session_state.get(f"exp_desc_{i}"))}
            if any(item.values()): experiences.append(item)
        education=[]
        for i in range(len(st.session_state.resume_education)):
            item={"school":nonempty(st.session_state.get(f"edu_school_{i}")), "degree":nonempty(st.session_state.get(f"edu_degree_{i}")), "field":nonempty(st.session_state.get(f"edu_field_{i}")), "start":nonempty(st.session_state.get(f"edu_start_{i}")), "end":nonempty(st.session_state.get(f"edu_end_{i}"))}
            if any(item.values()): education.append(item)
        projects=[]
        for i in range(len(st.session_state.resume_projects)):
            item={"name":nonempty(st.session_state.get(f"project_name_{i}")), "link":nonempty(st.session_state.get(f"project_link_{i}")), "description":nonempty(st.session_state.get(f"project_desc_{i}"))}
            if any(item.values()): projects.append(item)
        links=[]
        for i in range(len(st.session_state.resume_links)):
            item={"platform":nonempty(st.session_state.get(f"link_label_{i}")), "url":nonempty(st.session_state.get(f"link_url_{i}"))}
            if any(item.values()): links.append(item)
        return {"name":nonempty(st.session_state.get("cv_name")), "target_title":nonempty(st.session_state.get("cv_title")), "email":nonempty(st.session_state.get("cv_email")), "phone":nonempty(st.session_state.get("cv_phone")), "location":nonempty(st.session_state.get("cv_location")), "website":nonempty(st.session_state.get("cv_website")), "about":nonempty(st.session_state.get("cv_about")), "skills":nonempty(st.session_state.get("cv_skills")), "experience":experiences, "education":education, "projects":projects, "links":links}

    st.divider()
    if st.button("✨ Generate / Regenerate Professional CV", type="primary", use_container_width=True):
        profile = profile_data()
        if not profile["name"]:
            st.warning("أدخل الاسم الكامل أولًا / Please enter your full name first.")
        else:
            try:
                with st.spinner("Generating an ATS-friendly CV using the selected career context…"):
                    resume_sources = retrieve_context(f"CV skills and responsibilities for {st.session_state.selected_role}", career_path=st.session_state.selected_role)
                    st.session_state.generated_cv = resume_tools.generate_resume(rag, profile, st.session_state.selected_role, resume_sources, cv_language)
                    st.session_state.generated_cv_accent = accent
                st.success("Your professional CV is ready. Review the live preview and download it below.")
            except Exception as exc: st.error(str(exc))
    if st.session_state.generated_cv:
        st.markdown("### Live CV Preview")
        st.html(resume_tools.resume_html(st.session_state.generated_cv, st.session_state.get("generated_cv_accent", "#4f46e5")))
        p1, p2, p3 = st.columns(3)
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state.generated_cv.get("name", "CV"))
        p1.download_button("⬇ Download PDF", resume_tools.export_pdf(st.session_state.generated_cv), f"{safe_name}_CV.pdf", "application/pdf", use_container_width=True)
        p2.download_button("⬇ Download DOCX", resume_tools.export_docx(st.session_state.generated_cv), f"{safe_name}_CV.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        p3.download_button("⬇ Download CV JSON", json.dumps(st.session_state.generated_cv, ensure_ascii=False, indent=2), f"{safe_name}_CV.json", "application/json", use_container_width=True)

