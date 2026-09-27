"""ExamPrep AI — Day 02: 21 Days of Vibecoding Challenge
Bespoke White & Crimson Red Theme | Strictly Grounded on User Documents.
"""

import os
import streamlit as st
from pathlib import Path
from pdf_extractor import extract_from_uploaded_file, clean_extracted_text
from ai_engine import generate_study_materials, export_summary_to_pdf

# Page configuration
st.set_page_config(
    page_title="ExamPrep AI",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Bespoke White & Crimson Red Design System
st.markdown("""
<style>
    /* Global Reset & Typography */
    .stApp {
        background-color: #FFFFFF;
        color: #0F172A;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide default Streamlit decoration */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Brand Header */
    .brand-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .brand-title span {
        color: #DC2626; /* Crimson Red */
    }
    .brand-subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    /* Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .badge-offline {
        background-color: #FEF2F2;
        color: #DC2626;
        border: 1px solid #FCA5A5;
    }
    .badge-ai {
        background-color: #F0FDF4;
        color: #166534;
        border: 1px solid #86EFAC;
    }
    
    /* Cards & Containers */
    .content-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Flashcard Modern Red Design */
    .flashcard-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #DC2626;
        border-radius: 8px;
        padding: 28px;
        margin: 16px 0;
        min-height: 150px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.05);
    }
    .flashcard-q {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.4;
    }
    .flashcard-a {
        font-size: 1.05rem;
        color: #1E293B;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #FEE2E2;
        line-height: 1.5;
    }
    
    /* Quiz Cards */
    .quiz-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #DC2626;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .quiz-num {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #DC2626;
        margin-bottom: 4px;
    }
    .quiz-question {
        font-size: 1rem;
        font-weight: 600;
        color: #0F172A;
    }
    
    /* Primary Red Button Override */
    div.stButton > button[kind="primary"] {
        background-color: #DC2626 !important;
        border-color: #DC2626 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        transition: all 0.15s ease-in-out;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #B91C1C !important;
        border-color: #B91C1C !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25) !important;
    }
    
    /* Tabs Underline Accent */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #DC2626 !important;
        border-bottom-color: #DC2626 !important;
    }
    
    /* Score Box */
    .score-box {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-radius: 8px;
        padding: 16px 20px;
        color: #991B1B;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Session States
if "study_data" not in st.session_state:
    st.session_state["study_data"] = None
if "current_card" not in st.session_state:
    st.session_state["current_card"] = 0
if "card_flipped" not in st.session_state:
    st.session_state["card_flipped"] = False
if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False
if "user_answers" not in st.session_state:
    st.session_state["user_answers"] = {}
if "extracted_doc_text" not in st.session_state:
    st.session_state["extracted_doc_text"] = ""

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    api_key_input = st.text_input(
        "Gemini API Key (Optional)",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Paste a free key from Google AI Studio (aistudio.google.com). If empty, the app uses the built-in Local Document Extractor.",
    )
    
    has_api_key = bool(api_key_input and api_key_input.strip() not in ("", "DEMO", "OFFLINE"))
    
    if has_api_key:
        st.markdown('<div class="status-badge badge-ai">🟢 Gemini AI Active (Strict Grounding)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge badge-offline">🔴 Local Document Extractor Active</div>', unsafe_allow_html=True)
        st.caption("Zero external dependencies. Content is 100% strictly extracted from your uploaded file.")

    st.divider()
    num_questions = st.slider("Practice Questions", min_value=3, max_value=8, value=4)
    
    st.divider()
    st.caption("Day 02 • 21 Days of Vibecoding\nAuthor: Devaki Harish Nair")


# --- MAIN HEADER ---
st.markdown('<div class="brand-title">ExamPrep <span>AI</span></div>', unsafe_allow_html=True)
st.markdown('<div class="brand-subtitle">Strictly document-grounded revision sheets, active-recall flashcards, and practice quizzes for college students.</div>', unsafe_allow_html=True)

# --- UPLOAD SECTION ---
col_upload, col_text = st.columns([1, 1], gap="medium")

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Course Material (.pdf, .txt, .md)",
        type=["pdf", "txt", "md"],
        help="Upload lecture slide deck, syllabus, or lab manual",
    )
    if uploaded_file is not None:
        try:
            raw_extracted = extract_from_uploaded_file(uploaded_file)
            st.session_state["extracted_doc_text"] = raw_extracted
            st.success(f"✓ Parsed '{uploaded_file.name}' ({len(raw_extracted):,} characters)")
        except Exception as e:
            st.error(f"Error parsing file: {e}")

with col_text:
    pasted_text = st.text_area(
        "Or paste lecture text / syllabus directly:",
        value=st.session_state.get("extracted_doc_text", ""),
        height=140,
        placeholder="Paste lecture notes, syllabus module, or textbook excerpt...",
    )
    if pasted_text != st.session_state.get("extracted_doc_text", ""):
        st.session_state["extracted_doc_text"] = pasted_text

# Text Inspector Expander (Transparency)
doc_content = st.session_state.get("extracted_doc_text", "").strip()
if doc_content:
    with st.expander("🔍 Inspect Extracted Document Text (Confirm what is being analyzed)"):
        st.text(doc_content[:1500] + ("\n... [truncated for preview]" if len(doc_content) > 1500 else ""))

# Generate Button
st.write("")
btn_generate = st.button("⚡ Generate Study Materials from Document", type="primary", use_container_width=True)

if btn_generate:
    if not doc_content:
        st.error("Please upload a PDF file or paste lecture notes first!")
    else:
        with st.spinner("Analyzing document and extracting core concepts..."):
            study_result = generate_study_materials(
                content_text=doc_content,
                api_key=api_key_input if has_api_key else None,
                num_questions=num_questions,
            )
            st.session_state["study_data"] = study_result
            st.session_state["quiz_submitted"] = False
            st.session_state["user_answers"] = {}
            st.session_state["current_card"] = 0
            st.session_state["card_flipped"] = False
            st.rerun()

# --- STUDY MATERIALS DISPLAY ---
data = st.session_state.get("study_data")

if data:
    st.write("")
    st.divider()
    
    # Engine Used Header
    engine_label = data.get("engine_used", "Document Extractor")
    if "Gemini" in engine_label:
        st.markdown(f'<div class="status-badge badge-ai">🟢 Grounded by {engine_label}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-badge badge-offline">🔴 Strictly Grounded by {engine_label}</div>', unsafe_allow_html=True)
        
    if "error_notice" in data:
        st.warning(data["error_notice"])

    tab_summary, tab_flashcards, tab_quiz = st.tabs([
        "📌 Fast Revision Sheet",
        "🎴 Digital Flashcards",
        "📝 Self-Grading Quiz",
    ])

    # --- TAB 1: REVISION SHEET ---
    with tab_summary:
        st.markdown(data.get("summary", "No summary extracted."))
        st.divider()
        col_dl1, col_dl2 = st.columns([1, 1])
        with col_dl1:
            st.download_button(
                label="📥 Download Markdown (.md)",
                data=data.get("summary", ""),
                file_name="Revision_Sheet.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_dl2:
            try:
                pdf_data = export_summary_to_pdf(data.get("summary", ""))
                st.download_button(
                    label="📄 Download Printable PDF (.pdf)",
                    data=pdf_data,
                    file_name="Revision_Sheet.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF export note: {e}")

    # --- TAB 2: FLASHCARDS ---
    with tab_flashcards:
        cards = data.get("flashcards", [])
        if not cards:
            st.info("No definitions or flashcards could be extracted from this specific text.")
        else:
            total_cards = len(cards)
            c_idx = st.session_state["current_card"]
            current = cards[c_idx]
            
            st.caption(f"Card {c_idx + 1} of {total_cards}")
            st.progress((c_idx + 1) / total_cards)
            
            # Flashcard Box
            is_flipped = st.session_state["card_flipped"]
            answer_html = f'<div class="flashcard-a"><b>Definition / Concept:</b><br/>{current.get("back", "").replace(chr(10), "<br/>")}</div>' if is_flipped else '<div style="color:#94A3B8; margin-top:14px; font-size:0.9rem; font-style:italic;">Click "Reveal Answer" to test your recall</div>'
            
            st.markdown(f"""
            <div class="flashcard-box">
                <div class="flashcard-q">{current.get('front', '')}</div>
                {answer_html}
            </div>
            """, unsafe_allow_html=True)
            
            col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
            with col_c1:
                if st.button("⬅ Previous Card", disabled=(c_idx == 0), use_container_width=True):
                    st.session_state["current_card"] -= 1
                    st.session_state["card_flipped"] = False
                    st.rerun()
            with col_c2:
                btn_label = "🙈 Hide Answer" if is_flipped else "👁 Reveal Answer"
                if st.button(btn_label, type="primary", use_container_width=True):
                    st.session_state["card_flipped"] = not is_flipped
                    st.rerun()
            with col_c3:
                if st.button("Next Card ➡", disabled=(c_idx == total_cards - 1), use_container_width=True):
                    st.session_state["current_card"] += 1
                    st.session_state["card_flipped"] = False
                    st.rerun()

    # --- TAB 3: QUIZ ---
    with tab_quiz:
        quiz_items = data.get("quiz", [])
        if not quiz_items:
            st.info("No quiz questions could be formed from the provided text.")
        else:
            st.markdown(f"**Practice Mock Test** — {len(quiz_items)} Questions Grounded on Your Document")
            st.write("")
            
            for item in quiz_items:
                qid = str(item.get("id"))
                q_text = item.get("question", "")
                opts = item.get("options", [])
                c_idx = item.get("correct_index", 0)
                exp = item.get("explanation", "")
                
                st.markdown(f"""
                <div class="quiz-card">
                    <div class="quiz-num">Question {qid}</div>
                    <div class="quiz-question">{q_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                selected = st.radio(
                    f"Options for {qid}",
                    opts,
                    index=st.session_state["user_answers"].get(qid),
                    key=f"q_radio_{qid}",
                    label_visibility="collapsed",
                    disabled=st.session_state["quiz_submitted"],
                )
                
                if selected in opts:
                    st.session_state["user_answers"][qid] = opts.index(selected)
                    
                if st.session_state["quiz_submitted"]:
                    chosen_idx = st.session_state["user_answers"].get(qid)
                    if chosen_idx == c_idx:
                        st.success(f"✓ **Correct!** {exp}")
                    else:
                        st.error(f"✗ **Incorrect.** Correct: **{opts[c_idx]}**\n\n*{exp}*")
                st.write("")

            col_q1, col_q2 = st.columns([1, 1])
            with col_q1:
                if not st.session_state["quiz_submitted"]:
                    if st.button("Submit Quiz & Check Score", type="primary", use_container_width=True):
                        st.session_state["quiz_submitted"] = True
                        st.rerun()
                else:
                    if st.button("🔄 Retake Quiz", use_container_width=True):
                        st.session_state["quiz_submitted"] = False
                        st.session_state["user_answers"] = {}
                        st.rerun()
                        
            if st.session_state["quiz_submitted"]:
                correct_count = sum(
                    1 for item in quiz_items
                    if st.session_state["user_answers"].get(str(item.get("id"))) == item.get("correct_index")
                )
                tot = len(quiz_items)
                pct = int((correct_count / tot) * 100) if tot > 0 else 0
                
                st.markdown(f'<div class="score-box">Your Score: {correct_count} / {tot} ({pct}%)</div>', unsafe_allow_html=True)
                if pct == 100:
                    st.balloons()
                    st.success("🎉 Perfect Score! You mastered this document completely.")
