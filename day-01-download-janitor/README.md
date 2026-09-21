# 🧹 Day 01: DownloadJanitor
> **Part of the 21-Days Vibecoding Challenge**

DownloadJanitor is a safe, intelligent file organizer built with Python. It categorizes messy files into organized directories like `Documents`, `Images`, `Code`, `Media`, `Archives`, and `Installers`.

---

## ⚡ Features
- **100% Safe (Undo Built-in)**: Every move is logged. You can reverse changes instantly with `--undo`.
- **Dry-Run Preview**: Inspect planned moves before touching any file.
- **Collision Protection**: Never overwrites files. If `notes.pdf` exists, it renames to `notes (1).pdf`.
- **Ignores In-Progress Downloads**: Skips `.crdownload`, `.part`, `.tmp` files.
- **Live Watch Mode**: Background daemon that auto-sorts new downloads as they arrive.
- **Interactive Terminal Menu**: Choose actions with simple number keys (1–6).

---

## 🚀 Quick Start (Testing in Sandbox)

1. **Generate sample files**:
   ```bash
   .\.venv\Scripts\python.exe test_generator.py
   ```

2. **Preview moves (Dry-Run)**:
   ```bash
   .\.venv\Scripts\python.exe organizer.py --target test_downloads --dry-run
   ```

3. **Organize the folder**:
   ```bash
   .\.venv\Scripts\python.exe organizer.py --target test_downloads --run
   ```

4. **Undo anytime**:
   ```bash
   .\.venv\Scripts\python.exe organizer.py --target test_downloads --undo
   ```

5. **Clean your real Windows Downloads folder**:
   ```bash
   # Preview first
   .\.venv\Scripts\python.exe organizer.py --target "$HOME\Downloads" --dry-run

   # Organize when ready
   .\.venv\Scripts\python.exe organizer.py --target "$HOME\Downloads" --run
   ```
