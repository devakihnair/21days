"""AI Study Material Generator using Google Gemini API with fallback mock engine."""

import os
import json
from typing import Dict, List, Optional

SYSTEM_PROMPT = """You are an expert college professor and exam prep tutor.
Given lecture notes or textbook material, generate a comprehensive exam prep package containing:
1. "summary": A well-structured Markdown summary with:
   - 📌 Core Concepts & Theoretical Foundations
   - 🔑 Key Definitions & Terminology
   - ⚡ Key Algorithms, Rules, or Formulas
   - ⚠️ Common Exam Traps / Viva Pitfalls
2. "flashcards": A list of active-recall flashcards, each with "front" (concise question or concept prompt) and "back" (clear, high-yield explanation).
3. "quiz": A list of multiple-choice questions testing deep conceptual understanding. Each item must have:
   - "id": integer starting from 1
   - "question": text
   - "options": list of 4 distinct choices
   - "correct_index": integer (0, 1, 2, or 3) indicating the correct option
   - "explanation": brief explanation of why the correct option is right and others are wrong

Format your entire response as a valid JSON object matching this schema:
{
  "summary": "markdown string",
  "flashcards": [
    {"front": "...", "back": "..."}
  ],
  "quiz": [
    {
      "id": 1,
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0,
      "explanation": "..."
    }
  ]
}
"""

SAMPLE_OS_PRESETS = {
    "summary": """### 📌 Core Concepts & Theoretical Foundations
* **Process vs. Program:** A program is a passive executable file stored on disk; a process is an active entity with a Program Counter (PC), registers, and execution stack.
* **Process Memory Layout:** Consists of 4 discrete segments:
  * **Text Section:** Compiled binary machine code instructions.
  * **Data Section:** Global and static variables.
  * **Heap:** Memory dynamically allocated during runtime (e.g., `malloc()`).
  * **Stack:** Stack frames containing local variables, return addresses, and function parameters.

---

### 🔑 Key Definitions & Terminology
* **PCB (Process Control Block):** The data structure in the OS kernel that tracks all metadata for a process (PID, State, Program Counter, CPU registers, memory limits, and open file descriptors).
* **Convoy Effect:** A scheduling bottleneck in FCFS where short I/O-bound processes wait behind a massive CPU-bound process, drastically increasing average waiting time.
* **Context Switch:** The state save of the currently executing process and restoration of the state of another process. Pure overhead because the CPU does no useful work during switching.

---

### ⚡ Critical Section & Semaphores
* Any valid solution to the Critical Section problem **must** satisfy:
  1. **Mutual Exclusion:** Only one process inside the critical section at a time.
  2. **Progress:** Processes outside the remainder section decide who enters next without deadlocking.
  3. **Bounded Waiting:** A process will not be starved indefinitely.
* **Semaphore:** Integer variable modified atomically only via:
  * `wait()` / `P()`: decrements value, blocks if negative.
  * `signal()` / `V()`: increments value, unblocks waiting process.

---

### ⚠️ The 4 Coffman Deadlock Conditions (Memorize for Exams!)
Deadlock occurs **if and only if** all four conditions hold simultaneously:
1. **Mutual Exclusion** (at least one non-shareable resource)
2. **Hold and Wait** (holding one resource while requesting another)
3. **No Preemption** (resources cannot be forcibly taken)
4. **Circular Wait** (closed chain of circular dependencies)""",
    "flashcards": [
        {
            "front": "What is the difference between a Program and a Process?",
            "back": "A Program is a passive collection of instructions stored on disk. A Process is an active running instance with memory (stack, heap, text, data) and a program counter."
        },
        {
            "front": "What are the 4 segments in a process's memory layout?",
            "back": "1. Text (code instructions)\n2. Data (global & static variables)\n3. Heap (dynamic runtime memory)\n4. Stack (local variables, function calls)"
        },
        {
            "front": "Name the 5 standard states in a Process Life Cycle.",
            "back": "1. New (being created)\n2. Ready (waiting for CPU)\n3. Running (executing on CPU)\n4. Waiting / Blocked (waiting for I/O)\n5. Terminated (finished)"
        },
        {
            "front": "What is the 'Convoy Effect' in CPU Scheduling?",
            "back": "A problem in FCFS scheduling where multiple short processes get delayed behind one long, CPU-intensive process, reducing CPU utilization."
        },
        {
            "front": "Which CPU scheduling algorithm is mathematically optimal for minimum average waiting time?",
            "back": "Shortest Job First (SJF). However, it is difficult to implement in practice because the next CPU burst length cannot be predicted with 100% certainty."
        },
        {
            "front": "What are the 3 criteria a valid Critical Section solution MUST satisfy?",
            "back": "1. Mutual Exclusion\n2. Progress\n3. Bounded Waiting"
        },
        {
            "front": "List the 4 Coffman conditions required for Deadlock.",
            "back": "1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait"
        }
    ],
    "quiz": [
        {
            "id": 1,
            "question": "Which segment of process memory is dynamically allocated at runtime using functions like malloc() in C?",
            "options": ["Text Section", "Data Section", "Heap", "Stack"],
            "correct_index": 2,
            "explanation": "The Heap is the pool of free memory used for dynamic memory allocation during execution."
        },
        {
            "id": 2,
            "question": "Which CPU scheduling algorithm associates each process with its next CPU burst length and guarantees minimum average waiting time?",
            "options": ["First-Come, First-Served (FCFS)", "Shortest Job First (SJF)", "Round Robin (RR)", "Priority Scheduling"],
            "correct_index": 1,
            "explanation": "SJF is provably optimal in terms of minimizing average waiting time for a given set of processes."
        },
        {
            "id": 3,
            "question": "In Round Robin scheduling, what happens if the time quantum is chosen to be extremely large?",
            "options": ["It causes severe starvation", "It behaves identically to FCFS", "Context switch overhead reaches 100%", "The system deadlocks immediately"],
            "correct_index": 1,
            "explanation": "If the time quantum exceeds the longest CPU burst, every process finishes before preemption, degrading the behavior to standard FCFS."
        },
        {
            "id": 4,
            "question": "Which of the following is NOT one of the 4 Coffman conditions necessary for a deadlock?",
            "options": ["Hold and Wait", "No Preemption", "Starvation", "Circular Wait"],
            "correct_index": 2,
            "explanation": "Starvation is a scheduling anomaly (indefinite postponement), not one of Coffman's 4 formal conditions for deadlock."
        },
        {
            "id": 5,
            "question": "What is the primary drawback of a Context Switch between two processes?",
            "options": ["It deletes the PCB from RAM", "It is pure overhead where the CPU executes no useful user work", "It violates mutual exclusion", "It resets the operating system kernel"],
            "correct_index": 1,
            "explanation": "During a context switch, the OS must save registers and flush caches. The CPU does zero useful application processing during this period."
        }
    ]
}


def generate_study_materials(content_text: str, api_key: Optional[str] = None, num_questions: int = 5) -> Dict:
    """Generates summary, flashcards, and quiz using Gemini API, or fallback if key not supplied."""
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    if not resolved_key or resolved_key.strip() in ("", "DEMO", "SAMPLE"):
        # Return high-quality curated sample material
        return SAMPLE_OS_PRESETS

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=resolved_key)
        
        user_prompt = f"""Generate exam prep materials for the following lecture notes.
Create a summary, 6-8 flashcards, and {num_questions} multiple-choice questions.

LECTURE NOTES:
\"\"\"
{content_text[:30000]}
\"\"\"
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.3,
            )
        )
        
        data = json.loads(response.text)
        # Ensure all required keys exist
        if "summary" in data and "flashcards" in data and "quiz" in data:
            return data
        else:
            raise ValueError("Incomplete schema returned by Gemini API.")
            
    except Exception as e:
        # Fall back to sample presets if API call failed, but attach error note
        fallback = dict(SAMPLE_OS_PRESETS)
        fallback["error_notice"] = str(e)
        return fallback


def export_summary_to_pdf(summary_text: str) -> bytes:
    """Generates a downloadable PDF binary of the generated revision summary."""
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
    title_style = ParagraphStyle(
        "T",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "H",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "B",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )

    story = [Paragraph("ExamPrep AI — Fast Revision Summary", title_style), Spacer(1, 8)]
    for line in summary_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            story.append(Spacer(1, 4))
        elif cleaned.startswith("### "):
            safe = cleaned[4:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, h2_style))
        elif cleaned.startswith("## "):
            safe = cleaned[3:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, title_style))
        else:
            safe = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", "")
            story.append(Paragraph(safe, body_style))

    doc.build(story)
    return buf.getvalue()
