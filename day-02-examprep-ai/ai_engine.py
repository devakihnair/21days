"""AI Study Material Generator with Strict Document Grounding.
Supports Gemini API and an intelligent Local Document NLP Extractor (zero hallucination offline mode).
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple

STRICT_SYSTEM_PROMPT = """You are an academic exam prep tutor.
STRICT GROUNDING MANDATE:
- You must generate all summaries, flashcards, and quizzes SOLELY AND STRICTLY from the text provided by the user below.
- Do NOT bring in outside knowledge or default to other subjects.
- If the user provides notes on Electronics, every question and card MUST be about Electronics. If about Biology, every item MUST be about Biology.
- Every definition and quiz question must be directly verifiable in the source text.

Generate a valid JSON object matching this schema:
{
  "summary": "Comprehensive Markdown summary organized by the document's actual headings, definitions, and key takeaways.",
  "flashcards": [
    {"front": "Concise active-recall prompt or 'What is [Term]?'", "back": "Direct definition and explanation from the document."}
  ],
  "quiz": [
    {
      "id": 1,
      "question": "Clear conceptual question directly based on the text.",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Why this is correct according to the provided text."
    }
  ]
}
"""

def extract_sentences(text: str) -> List[str]:
    """Splits text into clean sentences."""
    clean = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    return [s.strip() for s in sentences if len(s.strip()) > 20]

def extract_keywords_from_text(text: str) -> List[str]:
    """Extracts prominent capitalized terms, nouns, and bold headers to use as distractors."""
    bold_terms = re.findall(r'\*\*([^*]+)\*\*', text)
    title_terms = re.findall(r'\b[A-Z][a-zA-Z0-9_-]{2,25}\b', text)
    
    candidates = []
    seen = set()
    stopwords = {"The", "This", "That", "These", "Those", "What", "When", "Where", "Which", "Why", "How", "And", "For", "With", "From", "Module", "Chapter", "Unit", "Section", "Page"}
    
    for term in bold_terms + title_terms:
        cleaned = term.strip(": ,.-")
        if cleaned and len(cleaned) > 2 and cleaned not in seen and cleaned not in stopwords:
            seen.add(cleaned)
            candidates.append(cleaned)
    return candidates

def extract_local_study_materials(content_text: str, num_questions: int = 5) -> Dict:
    """Intelligently extracts summary, flashcards, and quiz directly from the user's document without external APIs."""
    lines = [line.strip() for line in content_text.splitlines() if line.strip()]
    sentences = extract_sentences(content_text)
    keywords = extract_keywords_from_text(content_text)
    
    # 1. Parse Headings & Sections
    sections = {}
    current_section = "General Overview"
    sections[current_section] = []
    
    for line in lines:
        if line.startswith(("#", "##", "###", "Module", "Chapter", "Unit", "SECTION", "PART")) or (len(line) < 60 and line.endswith(":")):
            heading = line.lstrip("# ").strip(": ")
            if heading:
                current_section = heading
                sections[current_section] = []
        else:
            sections[current_section].append(line)
            
    # 2. Build Structured Markdown Summary from the Document
    summary_parts = []
    summary_parts.append(f"### 📋 Key Topics from Document ({len(sections)} Main Sections Identified)")
    
    for sec_title, sec_lines in sections.items():
        if not sec_lines and sec_title == "General Overview":
            continue
        summary_parts.append(f"#### 📌 {sec_title}")
        # Take key bullet points or sentences
        bullet_count = 0
        for l in sec_lines:
            if bullet_count >= 4:
                break
            if len(l) > 25 and not l.startswith("---"):
                clean_l = l.lstrip("-*• ")
                summary_parts.append(f"* **{clean_l[:80]}{'...' if len(clean_l)>80 else ''}** — {clean_l[80:] if len(clean_l)>80 else ''}")
                bullet_count += 1
        if bullet_count == 0 and sec_lines:
            summary_parts.append(f"* {sec_lines[0]}")
        summary_parts.append("")
        
    summary_parts.append("---")
    summary_parts.append("### 🔑 Document Takeaways & Critical Concepts")
    # Extract top definition sentences
    def_sentences = []
    def_pattern = re.compile(r'(\b[A-Za-z0-9\s_-]{2,35}\b)\s+(?:is defined as|is a|refers to|consists of|represents|functions as|means)\s+(.+)', re.IGNORECASE)
    
    for s in sentences:
        match = def_pattern.search(s)
        if match:
            def_sentences.append((match.group(1).strip(), s))
            if len(def_sentences) >= 6:
                break
                
    for term, full_s in def_sentences:
        summary_parts.append(f"* **{term.title()}:** {full_s}")
        
    if not def_sentences:
        for s in sentences[:5]:
            summary_parts.append(f"* {s}")
            
    summary_text = "\n".join(summary_parts)
    
    # 3. Build Flashcards from Actual Document Definitions & Concepts
    flashcards = []
    used_fronts = set()
    
    # Priority 1: Extracted definitions
    for term, full_s in def_sentences:
        front = f"What is {term.strip().title()}?"
        if front not in used_fronts:
            used_fronts.add(front)
            flashcards.append({
                "front": front,
                "back": full_s
            })
            
    # Priority 2: Key sections
    for sec_title, sec_lines in sections.items():
        if sec_title != "General Overview" and sec_lines:
            front = f"Key concept under '{sec_title}'?"
            if front not in used_fronts and len(flashcards) < 8:
                used_fronts.add(front)
                flashcards.append({
                    "front": front,
                    "back": " • " + "\n • ".join(sec_lines[:3])
                })
                
    # Fallback fill
    for s in sentences:
        if len(flashcards) >= 6:
            break
        words = s.split()
        if len(words) > 8:
            key_term = " ".join(words[:3])
            front = f"Explain the principle regarding: '{key_term}'"
            if front not in used_fronts:
                used_fronts.add(front)
                flashcards.append({
                    "front": front,
                    "back": s
                })
                
    # 4. Build Multiple-Choice Quiz from the Document
    quiz = []
    fallback_distractors = ["None of the above", "All mentioned components", "Varies based on context", "Static state"]
    candidate_distractors = keywords if len(keywords) >= 8 else (keywords + fallback_distractors)
    
    target_q_count = min(num_questions, max(3, len(sentences)))
    selected_sentences = [s for s in sentences if len(s) > 40][:target_q_count * 2]
    
    qid = 1
    for s in selected_sentences:
        if qid > num_questions:
            break
            
        # Try to identify a key noun/term in this sentence
        found_target = None
        for kw in keywords:
            if f" {kw.lower()} " in f" {s.lower()} " and len(kw) > 3:
                found_target = kw
                break
                
        if found_target:
            # Create a fill-in/identifying question
            question_text = f"According to the provided document, which concept matches this statement:\n\"{s.replace(found_target, '______')}\"?"
            correct_answer = found_target
            
            # Select 3 distinct distractors from other document keywords
            other_kw = [k for k in candidate_distractors if k.lower() != found_target.lower()]
            distractors = other_kw[:3]
            while len(distractors) < 3:
                distractors.append(f"Alternative Concept {len(distractors)+1}")
                
            options = [correct_answer] + distractors[:3]
            # Simple deterministic shuffle based on sentence length
            rot = len(s) % 4
            options = options[rot:] + options[:rot]
            correct_index = options.index(correct_answer)
            
            quiz.append({
                "id": qid,
                "question": question_text,
                "options": options,
                "correct_index": correct_index,
                "explanation": f"Found directly in document: \"{s}\""
            })
            qid += 1
            
    # If not enough quiz questions could be formed, generate structured comprehension questions
    while qid <= min(num_questions, max(3, len(sentences))):
        s = sentences[(qid - 1) % len(sentences)]
        quiz.append({
            "id": qid,
            "question": f"Which of the following statements is directly asserted in the text?",
            "options": [
                s,
                "This concept is entirely deprecated in modern systems.",
                "The text indicates this is strictly optional and unsupported.",
                "None of the statements are supported by the notes."
            ],
            "correct_index": 0,
            "explanation": f"The document states: \"{s}\""
        })
        qid += 1
        
    return {
        "summary": summary_text,
        "flashcards": flashcards,
        "quiz": quiz,
        "engine_used": "Local Document NLP Extractor (100% Grounded Offline Mode)"
    }


def generate_study_materials(content_text: str, api_key: Optional[str] = None, num_questions: int = 5) -> Dict:
    """Generates study materials using Gemini with strict grounding, or local document extractor if no key."""
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    # If no API key provided, parse the user's specific document locally
    if not resolved_key or resolved_key.strip() in ("", "DEMO", "OFFLINE"):
        return extract_local_study_materials(content_text, num_questions=num_questions)

    # If API key is provided, use Google Gemini with strict grounding
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=resolved_key.strip())
        
        user_prompt = f"""STRICT GROUNDING INSTRUCTION:
Generate revision notes, {num_questions} quiz questions, and flashcards EXCLUSIVELY from the text below.
DO NOT introduce external knowledge, other subjects, or generic assumptions.

USER DOCUMENT:
\"\"\"
{content_text[:40000]}
\"\"\"
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=STRICT_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
            )
        )
        
        data = json.loads(response.text)
        if "summary" in data and "flashcards" in data and "quiz" in data:
            data["engine_used"] = "Google Gemini 2.5 Flash (Strict Document Grounding)"
            return data
        else:
            raise ValueError("Incomplete JSON schema returned by Gemini.")
            
    except Exception as e:
        # Fall back to our local document NLP extractor on the user's text
        local_data = extract_local_study_materials(content_text, num_questions=num_questions)
        local_data["error_notice"] = f"Gemini API Notice: {e}. Falling back to Local Document Extractor."
        return local_data


def export_summary_to_pdf(summary_text: str) -> bytes:
    """Generates a downloadable PDF binary of the revision summary using White & Red styling."""
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    
    crimson_color = colors.HexColor("#DC2626")
    dark_slate = colors.HexColor("#0F172A")
    ruby_dark = colors.HexColor("#991B1B")
    
    title_style = ParagraphStyle(
        "PDFTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=crimson_color,
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "PDFH2",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=ruby_dark,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "PDFBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=dark_slate,
        spaceAfter=4,
    )

    story = [
        Paragraph("ExamPrep AI — Revision Summary", title_style),
        Spacer(1, 8),
    ]
    
    for line in summary_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            story.append(Spacer(1, 4))
        elif cleaned.startswith("### "):
            safe = cleaned[4:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, title_style))
        elif cleaned.startswith("#### "):
            safe = cleaned[5:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, h2_style))
        else:
            safe = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, body_style))

    doc.build(story)
    return buf.getvalue()
