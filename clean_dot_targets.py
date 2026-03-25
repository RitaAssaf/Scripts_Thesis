#!/usr/bin/env python3
import re
from pathlib import Path

# List of target graph IDs
targets = [
    "gt-08252025091213","gt-08252025091214","gt-08252025091215",
    "gt-08252025091216","gt-08252025091217","gt-08252025091218",
    "gt-08252025091219","gt-08252025091220","gt-08252025091221",
    "gt-08252025091221","gt-08252025091222","gt-08252025091223",
    "gt-08252025091224","gt-08252025091225","gt-08252025091226",
    "gt-08252025091227","gt-08252025091228","gt-08252025091229",
    "gt-08252025091230","gt-08252025091231"
]

def clean_dot_file(src_path: Path, dst_path: Path):
    """Remove large block (matrix of -1 etc.) from a .dot file and save to new folder."""
    try:
        text = src_path.read_text()

        # Regex to remove ONLY the // [[ ... ]] block
        cleaned = re.sub(r"//\s*\[\[.*?\]\]", "", text, flags=re.DOTALL)

        # Remove leftover empty lines
        cleaned = re.sub(r"\n\s*\n", "\n", cleaned)

        dst_path.write_text(cleaned)
        print(f"✔ Cleaned {src_path} -> {dst_path}")
    except FileNotFoundError:
        print(f"⚠ File not found: {src_path}")



if __name__ == "__main__":
    datadir = Path("/home/etud/Bureau/projet/fichiers/csp/dat/")
    cleaned_dir = datadir / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    for target in targets:
        src_file = datadir / f"{target}.dot"
        dst_file = cleaned_dir / f"{target}.dot"
        clean_dot_file(src_file, dst_file)
