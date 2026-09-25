"""Generates a sample OS lecture PDF from sample notes for testing PDF extraction."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def create_sample_pdf():
    current_dir = Path(__file__).parent
    notes_txt = current_dir / "sample_notes" / "os_process_notes.txt"
    pdf_out = current_dir / "sample_notes" / "sample_os_lecture.pdf"
    
    with open(notes_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    doc = SimpleDocTemplate(
        str(pdf_out),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "PDFH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0284C7"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    
    story = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            story.append(Spacer(1, 4))
        elif cleaned.startswith("# "):
            story.append(Paragraph(cleaned[2:], title_style))
        elif cleaned.startswith("## "):
            story.append(Paragraph(cleaned[3:], h2_style))
        elif cleaned.startswith("### "):
            story.append(Paragraph(f"<b>{cleaned[4:]}</b>", body_style))
        else:
            # Escape XML entities for ReportLab
            safe_text = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_text, body_style))
            
    doc.build(story)
    print(f"Created sample PDF at: {pdf_out}")

if __name__ == "__main__":
    create_sample_pdf()
