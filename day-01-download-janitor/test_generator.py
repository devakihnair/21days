"""Helper script to generate a realistic test_downloads/ folder for safe testing."""

import sys
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

SAMPLE_FILES = [
    # Documents
    "OS_Unit_3_Lecture_Notes.pdf",
    "DBMS_Lab_Manual.docx",
    "Internship_Resume_v2.pdf",
    "Expense_Report_Sept.xlsx",
    "AI_Seminar_Slides.pptx",
    "quick_notes.txt",
    
    # Images
    "college_fest_poster.png",
    "profile_picture.jpg",
    "architecture_diagram.webp",
    
    # Code
    "binary_search_tree.py",
    "matrix_multiplication.cpp",
    "portfolio_index.html",
    "api_response.json",
    
    # Media
    "ambient_study_music.mp3",
    "class_recording_part1.mp4",
    
    # Archives & Installers
    "semester_project_assets.zip",
    "vscode_setup.exe",
    
    # In-progress / Temporary (should be ignored by Janitor)
    "big_movie_download.mp4.crdownload",
    "temp_cache_data.tmp",
]

def generate_test_sandbox(target_dir: Path):
    """Creates a sandbox directory and populates it with dummy files."""
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{Fore.CYAN}--- Creating Sample Messy Downloads Folder ---{Style.RESET_ALL}")
    print(f"Location: {Fore.YELLOW}{target_dir.resolve()}{Style.RESET_ALL}\n")
    
    created_count = 0
    for filename in SAMPLE_FILES:
        filepath = target_dir / filename
        # Create a small dummy file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Sample test content for {filename}\nCreated for 21-Days Vibecoding Day 01.")
        print(f"  {Fore.GREEN}+ Created:{Style.RESET_ALL} {filename}")
        created_count += 1
        
    print(f"\n{Fore.GREEN}Done! Generated {created_count} test files.{Style.RESET_ALL}")
    print(f"You can now run: {Fore.YELLOW}python organizer.py --target {target_dir.name} --dry-run{Style.RESET_ALL}\n")

if __name__ == "__main__":
    current_dir = Path(__file__).parent
    sandbox_dir = current_dir / "test_downloads"
    generate_test_sandbox(sandbox_dir)
