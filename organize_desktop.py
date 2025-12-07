#!/usr/bin/env python3
"""
organize_desktop.py
Simple organizer: move files from source dir into category folders.
Usage examples:
  python organize_desktop.py --source ~/Desktop --dry-run
  python organize_desktop.py --source ~/Downloads
  python organize_desktop.py --undo
"""

import argparse
from pathlib import Path
import shutil
import json
import datetime
import sys

CATEGORIES = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"},
    "Documents": {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt", ".md"},
    "Archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".html", ".css", ".json"},
    "Audio": {".mp3", ".wav", ".flac", ".aac"},
    "Video": {".mp4", ".mkv", ".mov", ".avi"},
}

LOG_FILE = ".organize_log.json"

def category_for(ext: str):
    ext = ext.lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Others"

def load_log(target_dir: Path):
    p = target_dir / LOG_FILE
    if p.exists():
        return json.loads(p.read_text())
    return {"moves": []}

def save_log(target_dir: Path, data):
    p = target_dir / LOG_FILE
    p.write_text(json.dumps(data, indent=2))

def ensure_folder(path: Path, name: str):
    folder = path / name
    folder.mkdir(exist_ok=True)
    return folder

def safe_move(src: Path, dest: Path):
    # if destination filename exists, append timestamp
    if dest.exists():
        stem = dest.stem
        suf = dest.suffix
        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dest = dest.with_name(f"{stem}_{ts}{suf}")
    shutil.move(str(src), str(dest))
    return dest

def organize(source: Path, dry_run=False):
    source = source.expanduser().resolve()
    if not source.exists() or not source.is_dir():
        print("Source folder does not exist:", source)
        return False
    log = load_log(source)
    moved = []
    for item in source.iterdir():
        if item.name == LOG_FILE:  # skip our log
            continue
        if item.is_dir():
            continue
        ext = item.suffix
        cat = category_for(ext)
        dest_folder = ensure_folder(source, cat)
        dest = dest_folder / item.name
        print(f"{'DRY:' if dry_run else ''} -> {item.name} -> {cat}/")
        if not dry_run:
            newpath = safe_move(item, dest)
            moved.append({"from": str(item), "to": str(newpath)})
    if not dry_run and moved:
        log["moves"].extend(moved)
        log["last_run"] = datetime.datetime.utcnow().isoformat() + "Z"
        save_log(source, log)
        (source / "report.json").write_text(json.dumps({
            "moved_count": len(moved),
            "moved": moved,
            "timestamp": log["last_run"]
        }, indent=2))
    return True

def undo(source: Path):
    source = source.expanduser().resolve()
    log = load_log(source)
    if not log.get("moves"):
        print("No recorded moves to undo.")
        return
    # reverse moves in LIFO order
    for mv in reversed(log["moves"]):
        src = Path(mv["to"])
        dst = Path(mv["from"])
        if src.exists():
            print(f"Undo: {src} -> {dst}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            safe_move(src, dst)
        else:
            print("Skipped (target gone):", src)
    # clear log
    (source / LOG_FILE).write_text(json.dumps({"moves": []}, indent=2))
    print("Undo complete.")

def main():
    parser = argparse.ArgumentParser(description="Organize cluttered desktop.")
    parser.add_argument("--source", "-s", default="~/Desktop", help="Source directory (default: ~/Desktop)")
    parser.add_argument("--dry-run", action="store_true", help="Show actions but do not move")
    parser.add_argument("--undo", action="store_true", help="Undo last moves recorded in log")
    parser.add_argument("--preview", action="store_true", help="Show summary preview only")
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    if args.undo:
        undo(source)
        return
    if args.preview:
        print("Preview:")
        organize(source, dry_run=True)
        return
    organize(source, dry_run=args.dry_run)

if __name__ == "__main__":
    main()