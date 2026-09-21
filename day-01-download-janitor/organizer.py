"""DownloadJanitor - Day 01: 21-Days Vibecoding Challenge
Smart, safe, and automated file organizer with dry-run, undo, and watch mode.
"""

import os
import sys
import json
import time
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from colorama import init, Fore, Style

from config import (
    EXTENSIONS_MAP,
    IGNORED_EXTENSIONS,
    IGNORED_FILES,
    HISTORY_FILENAME,
    get_category_for_extension,
    get_default_downloads_dir,
)

init(autoreset=True)


def resolve_collision(dest_dir: Path, filename: str) -> Path:
    """Ensures no file is ever overwritten by adding numbers like (1), (2)."""
    dest_path = dest_dir / filename
    if not dest_path.exists():
        return dest_path

    stem = dest_path.stem
    suffix = dest_path.suffix
    counter = 1

    while dest_path.exists():
        new_filename = f"{stem} ({counter}){suffix}"
        dest_path = dest_dir / new_filename
        counter += 1

    return dest_path


def load_history(target_dir: Path) -> List[Dict]:
    """Loads the history stack from .janitor_history.json."""
    history_file = target_dir / HISTORY_FILENAME
    if not history_file.exists():
        return []
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(target_dir: Path, history: List[Dict]):
    """Saves the history stack to .janitor_history.json."""
    history_file = target_dir / HISTORY_FILENAME
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def is_file_eligible(file_path: Path) -> bool:
    """Checks if a file is ready to be moved and not ignored."""
    if not file_path.is_file():
        return False

    name_lower = file_path.name.lower()
    if name_lower in IGNORED_FILES or name_lower.startswith("~$"):
        return False

    for ignored_ext in IGNORED_EXTENSIONS:
        if name_lower.endswith(ignored_ext):
            return False

    return True


def organize_directory(target_dir: Path, dry_run: bool = False) -> Dict[str, List[Tuple[str, str]]]:
    """Organizes files in target_dir into category folders."""
    target_dir = target_dir.resolve()
    if not target_dir.exists():
        print(f"{Fore.RED}[Error] Directory not found: {target_dir}{Style.RESET_ALL}")
        return {}

    mode_label = f"{Fore.YELLOW}[DRY-RUN / PREVIEW]{Style.RESET_ALL}" if dry_run else f"{Fore.GREEN}[LIVE EXECUTION]{Style.RESET_ALL}"
    print(f"\n{Fore.CYAN}===================================================={Style.RESET_ALL}")
    print(f"  DownloadJanitor: {mode_label}")
    print(f"  Target: {Fore.WHITE}{target_dir}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}===================================================={Style.RESET_ALL}\n")

    # Collect candidate files (only root files in target_dir, not subdirectories)
    items = list(target_dir.iterdir())
    files_to_move = [item for item in items if is_file_eligible(item)]

    if not files_to_move:
        print(f"{Fore.YELLOW}Everything is already clean! No loose files to organize.{Style.RESET_ALL}\n")
        return {}

    planned_moves: Dict[str, List[Tuple[Path, Path]]] = {}
    total_files = len(files_to_move)

    for file_path in files_to_move:
        category = get_category_for_extension(file_path.suffix)
        category_dir = target_dir / category
        destination_path = resolve_collision(category_dir, file_path.name)

        if category not in planned_moves:
            planned_moves[category] = []
        planned_moves[category].append((file_path, destination_path))

    # Print summary table
    for category, moves in planned_moves.items():
        print(f"{Fore.MAGENTA}📁 {category}/ ({len(moves)} file{'s' if len(moves) > 1 else ''}){Style.RESET_ALL}")
        for src, dest in moves:
            print(f"   ↳ {Fore.WHITE}{src.name}{Style.RESET_ALL} -> {Fore.LIGHTBLUE_EX}{dest.parent.name}/{dest.name}{Style.RESET_ALL}")

    if dry_run:
        print(f"\n{Fore.YELLOW}Preview complete! {total_files} files would be organized.{Style.RESET_ALL}")
        print(f"To perform the actual move, run: {Fore.GREEN}python organizer.py --target \"{target_dir}\" --run{Style.RESET_ALL}\n")
        return planned_moves

    # Perform actual moves
    executed_moves = []
    for category, moves in planned_moves.items():
        category_dir = target_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        for src, dest in moves:
            try:
                shutil.move(str(src), str(dest))
                executed_moves.append({
                    "original_path": str(src),
                    "moved_path": str(dest),
                    "filename": src.name,
                    "category": category,
                })
            except Exception as e:
                print(f"   {Fore.RED}✗ Failed to move {src.name}: {e}{Style.RESET_ALL}")

    # Record to history for undo
    if executed_moves:
        history = load_history(target_dir)
        history.append({
            "timestamp": datetime.now().isoformat(),
            "count": len(executed_moves),
            "moves": executed_moves,
        })
        save_history(target_dir, history)

    print(f"\n{Fore.GREEN}✓ Successfully organized {len(executed_moves)} files!{Style.RESET_ALL}")
    print(f"Tip: Made a mistake? Undo anytime using: {Fore.YELLOW}python organizer.py --target \"{target_dir}\" --undo{Style.RESET_ALL}\n")
    return planned_moves


def undo_last_operation(target_dir: Path):
    """Reverses the last organization operation."""
    target_dir = target_dir.resolve()
    history = load_history(target_dir)

    if not history:
        print(f"{Fore.YELLOW}No organization history found in {target_dir}. Nothing to undo!{Style.RESET_ALL}\n")
        return

    last_run = history.pop()
    moves = last_run.get("moves", [])
    run_time = last_run.get("timestamp", "Unknown time")

    print(f"\n{Fore.CYAN}--- Undoing Organization from {run_time} ---{Style.RESET_ALL}")
    print(f"Restoring {len(moves)} file(s) back to root...\n")

    restored = 0
    for item in moves:
        current_loc = Path(item["moved_path"])
        original_loc = Path(item["original_path"])

        if current_loc.exists():
            dest = resolve_collision(original_loc.parent, original_loc.name)
            try:
                shutil.move(str(current_loc), str(dest))
                print(f"  {Fore.GREEN}↩ Restored:{Style.RESET_ALL} {dest.name}")
                restored += 1
            except Exception as e:
                print(f"  {Fore.RED}✗ Failed to restore {current_loc.name}: {e}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ File not found at {current_loc} (may have been moved or deleted manually).{Style.RESET_ALL}")

    save_history(target_dir, history)

    # Clean up empty category folders if left behind
    for category in list(EXTENSIONS_MAP.keys()) + ["Others"]:
        cat_dir = target_dir / category
        if cat_dir.exists() and cat_dir.is_dir():
            if not any(cat_dir.iterdir()):
                try:
                    cat_dir.rmdir()
                except Exception:
                    pass

    print(f"\n{Fore.GREEN}✓ Undo complete! Restored {restored} files.{Style.RESET_ALL}\n")


def run_watch_mode(target_dir: Path):
    """Watches the target directory in real-time and auto-organizes newly completed downloads."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print(f"{Fore.RED}[Error] 'watchdog' library not found. Run pip install watchdog.{Style.RESET_ALL}")
        return

    target_dir = target_dir.resolve()
    print(f"\n{Fore.CYAN}===================================================={Style.RESET_ALL}")
    print(f"  DownloadJanitor: {Fore.GREEN}[WATCH MODE ACTIVE]{Style.RESET_ALL}")
    print(f"  Monitoring: {Fore.WHITE}{target_dir}{Style.RESET_ALL}")
    print(f"  Press {Fore.YELLOW}Ctrl + C{Style.RESET_ALL} to stop watching anytime.")
    print(f"{Fore.CYAN}===================================================={Style.RESET_ALL}\n")

    class DownloadHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            self.handle_file(Path(event.src_path))

        def handle_file(self, file_path: Path):
            if file_path.parent.resolve() != target_dir:
                return  # Skip files created inside subdirectories

            # Wait briefly in case a download has just finished
            time.sleep(1.5)

            if not is_file_eligible(file_path):
                return

            category = get_category_for_extension(file_path.suffix)
            category_dir = target_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            dest = resolve_collision(category_dir, file_path.name)

            try:
                shutil.move(str(file_path), str(dest))
                print(f"{Fore.GREEN}[Auto-Organized]{Style.RESET_ALL} {file_path.name} -> {Fore.CYAN}{category}/{dest.name}{Style.RESET_ALL}")
            except Exception as e:
                pass

    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(target_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}Watch mode stopped.{Style.RESET_ALL}\n")
    observer.join()


def interactive_menu(default_target: Path):
    """Displays a clean terminal menu for students to pick an action with 1 keypress."""
    while True:
        print(f"\n{Fore.CYAN}--- DownloadJanitor: Day 01 Vibecoding ---{Style.RESET_ALL}")
        print(f"Active Folder: {Fore.YELLOW}{default_target.resolve()}{Style.RESET_ALL}")
        print("1. Preview organization (Dry-Run)")
        print("2. Clean & organize folder now")
        print("3. Undo last clean")
        print("4. Start live Watch Mode (background auto-sorting)")
        print("5. Switch target folder")
        print("6. Exit")

        choice = input(f"\n{Fore.GREEN}Choose an option (1-6): {Style.RESET_ALL}").strip()

        if choice == "1":
            organize_directory(default_target, dry_run=True)
        elif choice == "2":
            organize_directory(default_target, dry_run=False)
        elif choice == "3":
            undo_last_operation(default_target)
        elif choice == "4":
            run_watch_mode(default_target)
        elif choice == "5":
            new_path = input("Enter new folder path (e.g. C:\\Users\\USER\\Downloads or test_downloads): ").strip()
            if new_path:
                candidate = Path(new_path)
                if candidate.exists():
                    default_target = candidate
                else:
                    print(f"{Fore.RED}Folder does not exist!{Style.RESET_ALL}")
        elif choice == "6":
            print(f"{Fore.CYAN}Happy coding! See you in Day 02! 👋{Style.RESET_ALL}\n")
            break
        else:
            print(f"{Fore.RED}Invalid selection. Please choose 1 to 6.{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="DownloadJanitor - Organize files cleanly and safely.")
    parser.add_argument("--target", "-t", type=str, default=None, help="Directory to organize (defaults to test_downloads or Downloads)")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview moves without touching files")
    parser.add_argument("--run", "-r", action="store_true", help="Perform organization immediately")
    parser.add_argument("--undo", "-u", action="store_true", help="Undo the last organization run")
    parser.add_argument("--watch", "-w", action="store_true", help="Watch folder in real-time")

    args = parser.parse_args()

    # Determine target directory
    if args.target:
        target_path = Path(args.target)
    else:
        # Default to local test_downloads if present, otherwise system downloads
        script_dir = Path(__file__).parent
        test_dir = script_dir / "test_downloads"
        if test_dir.exists():
            target_path = test_dir
        else:
            target_path = get_default_downloads_dir()

    if args.dry_run:
        organize_directory(target_path, dry_run=True)
    elif args.run:
        organize_directory(target_path, dry_run=False)
    elif args.undo:
        undo_last_operation(target_path)
    elif args.watch:
        run_watch_mode(target_path)
    else:
        # Interactive mode if no flags provided
        interactive_menu(target_path)


if __name__ == "__main__":
    main()
