# Organize Desktop

**I hate seeing my Desktop cluttered — so I built this.**

## What it does
- Moves files from Desktop (or any folder) into categorized folders by extension.
- Supports `--dry-run`, `--preview`, and `--undo`.
- Generates `report.json` and a `.organize_log.json` to undo operations.

## Quickstart
```bash
git clone https://github.com/Thejalm/organize_desktop.git
cd organize_desktop
python organize_desktop.py --source ~/Desktop --dry-run   # preview changes
python organize_desktop.py --source ~/Desktop             # actually move
python organize_desktop.py --source ~/Desktop --undo     # undo last moves