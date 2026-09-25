"""ExamPrep AI - Day 02: 21 Days of Vibecoding Challenge
Interactive Web App: Turn lecture PDFs and notes into revision sheets, flashcards, and quizzes.
"""

import os
import streamlit as st
from pathlib import Path
from pdf_extractor import extract_from_uploaded_file, clean_extracted_text
from ai_engine import generate_study_materials, export_summary_to_pdf, SAMPLE_OS_PRESETS

# Page configuration
st.set_page_config(
    page_title="ExamPrep AI — Study & Quiz Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern student-friendly aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .flashcard-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 2px solid #BFDBFE;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0px;
        min-height: 140px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .flashcard-q {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 8px;
    }
    .flashcard-a {
        font-size: 1.05rem;
        color: #0F172A;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px dashed #93C5FD;
    }
    .quiz-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .quiz-q {
        font-weight: 600;
        font-size: 1.05rem;
        color: #1E293B;
        margin-bottom: 10px;
    }
    .score-badge {
        font-size: 1.3rem;
        font-weight: 700;
        color: #166534;
        background-color: #DCFCE7;
        padding: 10px 18px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
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

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/graduation-cap.png", width=100)
    st.title("Settings & AI")
    
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Get a free key from Google AI Studio (aistudio.google.com). Leave blank to use Instant Demo Mode.",
    )
    
    if not api_key_input:
        st.info("💡 **Demo Mode Active**: No API key? No problem! The app will use curated college Operating Systems notes so you can test everything immediately.")
    
    num_questions = st.slider("Quiz Questions Count", min_value=3, max_value=10, value=5)
    
    st.divider()
    st.subheader("📚 Quick Sample Notes")
    if st.button("Load Sample OS Notes", use_container_width=True):
        sample_path = Path(__file__).parent / "sample_notes" / "os_process_notes.txt"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                st.session_state["input_text"] = f.read()
            st.success("Loaded Operating Systems lecture notes!")
            
    st.divider()
    st.caption("Day 02 • 21 Days of Vibecoding\nBuilt by Devaki Harish Nair")


# --- MAIN HEADER ---
st.markdown('<div class="main-header">🎓 ExamPrep AI — College Study Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your lecture slides or notes to instantly generate revision sheets, active-recall flashcards, and practice quizzes.</div>', unsafe_allow_html=True)

# --- INPUT SECTION ---
input_col1, input_col2 = st.columns([1, 1], gap="medium")

with input_col1:
    uploaded_file = st.file_uploader(
        "Upload Lecture PDF or Notes (.pdf, .txt)",
        type=["pdf", "txt", "md"],
        help="Upload lecture slide deck or syllabus module",
    )
    if uploaded_file is not None:
        try:
            extracted = extract_from_uploaded_file(uploaded_file)
            st.session_state["input_text"] = extracted
            st.success(f"✓ Extracted {len(extracted):,} characters from '{uploaded_file.name}'")
        except Exception as e:
            st.error(f"Error reading file: {e}")

with input_col2:
    notes_text = st.text_area(
        "Or paste your lecture notes here:",
        value=st.session_state.get("input_text", ""),
        height=180,
        placeholder="Paste syllabus contents, lecture slides text, or textbook sections...",
    )
    st.session_state["input_text"] = notes_text

# Action button
generate_clicked = st.button("⚡ Generate Study Materials", type="primary", use_container_width=True)

if generate_clicked:
    content_to_process = st.session_state.get("input_text", "").strip()
    if not content_to_process and not api_key_input:
        # Auto load sample notes if user just clicked generate
        sample_path = Path(__file__).parent / "sample_notes" / "os_process_notes.txt"
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8") as f:
                content_to_process = f.read()
                st.session_state["input_text"] = content_to_process
    
    if not content_to_process:
        st.warning("Please upload a file, paste notes, or click 'Load Sample OS Notes' in the sidebar!")
    else:
        with st.spinner("Analyzing document and generating high-yield exam materials..."):
            result = generate_study_materials(
                content_text=content_to_process,
                api_key=api_key_input,
                num_questions=num_questions,
            )
            st.session_state["study_data"] = result
            st.session_state["quiz_submitted"] = False
            st.session_state["user_answers"] = {}
            st.session_state["current_card"] = 0
            st.session_state["card_flipped"] = False
            st.rerun()

# --- DISPLAY TABS (If materials exist) ---
data = st.session_state.get("study_data")

if data:
    st.markdown("---")
    
    if "error_notice" in data:
        st.warning(f"Note: API call noticed an issue ({data['error_notice']}). Displaying curated high-yield sample material.")

    tab_summary, tab_flashcards, tab_quiz = st.tabs([
        "📌 Fast Revision Sheet",
        "🎴 Digital Flashcards",
        "📝 Self-Grading Mock Quiz",
    ])

    # --- TAB 1: REVISION SHEET ---
    with tab_summary:
        st.markdown(data.get("summary", "No summary generated."))
        st.divider()
        col_dl1, col_dl2 = st.columns([1, 1])
        with col_dl1:
            st.download_button(
                label="📥 Download Revision Sheet (.md)",
                data=data.get("summary", ""),
                file_name="ExamPrep_Revision_Sheet.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_dl2:
            try:
                pdf_bytes = export_summary_to_pdf(data.get("summary", ""))
                st.download_button(
                    label="📄 Download Revision Sheet (.pdf)",
                    data=pdf_bytes,
                    file_name="ExamPrep_Revision_Sheet.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF export unavailable: {e}")

    # --- TAB 2: FLASHCARDS ---
    with tab_flashcards:
        flashcards = data.get("flashcards", [])
        if not flashcards:
            st.info("No flashcards found.")
        else:
            view_mode = st.radio(
                "Flashcard Mode",
                ["Interactive Carousel", "Grid View (All at once)"],
                horizontal=True,
            )
            
            if view_mode == "Interactive Carousel":
                total_cards = len(flashcards)
                card_idx = st.session_state["current_card"]
                card = flashcards[card_idx]
                
                # Card progress
                st.caption(f"Flashcard {card_idx + 1} of {total_cards}")
                st.progress((card_idx + 1) / total_cards)
                
                # Card display box
                st.markdown(f"""
                <div class="flashcard-box">
                    <div class="flashcard-q">❓ {card.get('front', '')}</div>
                    {f'<div class="flashcard-a">💡 <b>Answer:</b><br/>{card.get("back", "").replace(chr(10), "<br/>")}</div>' if st.session_state["card_flipped"] else '<div style="color:#64748B; margin-top:10px; font-style:italic;">Click "Reveal Answer" below to test your recall</div>'}
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn1:
                    if st.button("⬅ Previous Card", disabled=(card_idx == 0), use_container_width=True):
                        st.session_state["current_card"] -= 1
                        st.session_state["card_flipped"] = False
                        st.rerun()
                with col_btn2:
                    flip_label = "🙈 Hide Answer" if st.session_state["card_flipped"] else "👁 Reveal Answer"
                    if st.button(flip_label, type="primary", use_container_width=True):
                        st.session_state["card_flipped"] = not st.session_state["card_flipped"]
                        st.rerun()
                with col_btn3:
                    if st.button("Next Card ➡", disabled=(card_idx == total_cards - 1), use_container_width=True):
                        st.session_state["current_card"] += 1
                        st.session_state["card_flipped"] = False
                        st.rerun()
            else:
                # Grid view
                for idx, c in enumerate(flashcards):
                    with st.expander(f"🎴 Flashcard {idx + 1}: {c.get('front', '')}"):
                        st.markdown(f"**Answer:**\n\n{c.get('back', '')}")

    # --- TAB 3: MOCK QUIZ ---
    with tab_quiz:
        quiz_list = data.get("quiz", [])
        if not quiz_list:
            st.info("No quiz questions available.")
        else:
            st.subheader(f"📝 Practice Mock Test ({len(quiz_list)} Questions)")
            st.caption("Select your answers and click 'Submit Quiz' at the bottom to see your score and explanations.")
            
            # Form for quiz
            for q in quiz_list:
                qid = str(q.get("id", ""))
                question_text = q.get("question", "")
                options = q.get("options", [])
                correct_idx = q.get("correct_index", 0)
                explanation = q.get("explanation", "")
                
                st.markdown(f"""
                <div class="quiz-card">
                    <div class="quiz-q">Question {qid}: {question_text}</div>
                </div>
                """, unsafe_allow_html=True)
                
                user_choice = st.radio(
                    f"Choose answer for Q{qid}:",
                    options,
                    index=None if not st.session_state["quiz_submitted"] else st.session_state["user_answers"].get(qid),
                    key=f"radio_{qid}",
                    label_visibility="collapsed",
                    disabled=st.session_state["quiz_submitted"],
                )
                
                if user_choice in options:
                    st.session_state["user_answers"][qid] = options.index(user_choice)
                    
                # Show results after submit
                if st.session_state["quiz_submitted"]:
                    chosen = st.session_state["user_answers"].get(qid)
                    if chosen == correct_idx:
                        st.success(f"✓ **Correct!** {explanation}")
                    else:
                        st.error(f"✗ **Incorrect.** Correct answer: **{options[correct_idx]}**\n\n*Why:* {explanation}")
                st.write("")

            col_sub1, col_sub2 = st.columns([1, 1])
            with col_sub1:
                if not st.session_state["quiz_submitted"]:
                    if st.button("Submit Quiz & Check Score", type="primary", use_container_width=True):
                        st.session_state["quiz_submitted"] = True
                        st.rerun()
                else:
                    if st.button("🔄 Retake Quiz", use_container_width=True):
                        st.session_state["quiz_submitted"] = False
                        st.session_state["user_answers"] = {}
                        st.rerun()
                        
            # Score summary
            if st.session_state["quiz_submitted"]:
                correct_count = sum(
                    1 for q in quiz_list
                    if st.session_state["user_answers"].get(str(q.get("id"))) == q.get("correct_index")
                )
                total_q = len(quiz_list)
                pct = int((correct_count / total_q) * 100) if total_q > 0 else 0
                
                st.divider()
                st.markdown(f'<div class="score-badge">Your Score: {correct_count} / {total_q} ({pct}%)</div>', unsafe_allow_html=True)
                if pct == 100:
                    st.balloons()
                    st.success("🎉 Outstanding! You mastered this topic completely!")
                elif pct >= 60:
                    st.info("👍 Solid score! Review the missed questions above before exam day.")
                else:
                    st.warning("⚠️ Review the Flashcards and Revision Sheet, then try again!")
