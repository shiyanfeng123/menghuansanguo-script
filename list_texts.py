# -*- coding: utf-8 -*-
"""按副本列出需要截图的文字 — 不遗漏"""
import sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(BASE, "ya_assets", "images", "text", "文字图片替换清单.txt")
TEXT_DIR = os.path.join(BASE, "ya_assets", "images", "text")

entries = []
with open(TXT, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|--") or line.startswith("| 游戏"):
            continue
        if ".bmp" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5 and parts[2].endswith(".bmp"):
            entries.append({
                "text": parts[1],
                "file": parts[2],
                "scene": parts[3],
                "region": parts[4],
                "method": parts[5] if len(parts) > 5 else "",
            })

dungeon = sys.argv[1] if len(sys.argv) > 1 else None

print("=" * 70)
print(f"  {dungeon or 'ALL'} - TEXT IMAGES NEEDED")
print("=" * 70)

existing = 0
missing = 0
for e in entries:
    abs_path = os.path.join(TEXT_DIR, e["file"])
    exists = os.path.isfile(abs_path)
    if exists:
        existing += 1
    else:
        missing += 1
        print(f"  [ ] {e['text']:<14} -> {e['file']:<35} ({e['region']})")

print(f"\n  OK: {existing} | MISSING: {missing} | TOTAL: {existing+missing}")
