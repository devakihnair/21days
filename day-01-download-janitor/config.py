"""Configuration for DownloadJanitor file categorization."""

import os
from pathlib import Path

# Mapping of category folders to file extensions (all lowercase)
EXTENSIONS_MAP = {
    "Documents": [
        ".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt",
        ".xlsx", ".xls", ".csv", ".odt", ".rtf", ".md"
    ],
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
        ".bmp", ".ico", ".tiff", ".psd"
    ],
    "Code": [
        ".py", ".ipynb", ".cpp", ".c", ".h", ".java", ".html",
        ".css", ".js", ".ts", ".json", ".sql", ".rs", ".dart",
        ".sh", ".ps1"
    ],
    "Media": [
        ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv",
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"
    ],
    "Archives": [
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"
    ],
    "Installers": [
        ".exe", ".msi", ".msix", ".iso", ".dmg", ".apk"
    ],
}

# Temporary or system files that should NEVER be moved while downloading
IGNORED_EXTENSIONS = {
    ".crdownload",  # Chrome in-progress download
    ".part",        # Firefox in-progress download
    ".tmp",         # General temporary file
    ".download",    # Safari in-progress download
    ".swp",         # Vim swap file
}

# Files and directories that should be skipped completely
IGNORED_FILES = {
    ".janitor_history.json",
    "desktop.ini",
    ".ds_store",
    "thumbs.db",
}

# File name for undo tracking
HISTORY_FILENAME = ".janitor_history.json"

def get_category_for_extension(extension: str) -> str:
    """Returns the matching category name for a given extension, or 'Others'."""
    ext = extension.lower()
    for category, ext_list in EXTENSIONS_MAP.items():
        if ext in ext_list:
            return category
    return "Others"

def get_default_downloads_dir() -> Path:
    """Detects the default user Downloads directory on Windows/Linux/Mac."""
    home = Path.home()
    downloads = home / "Downloads"
    if downloads.exists():
        return downloads
    return home
