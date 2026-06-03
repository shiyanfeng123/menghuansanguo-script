import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r"c:\Users\syf\Desktop\project\menghuansanguo-script\captures\sniff_live.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"total={d['total']} text={d['text']} status={d['status']} last={d['last_write']}")

# 1. 所有SWF路径
swfs = {}
for p in d["recent_text"]:
    for s in re.findall(r'lib/[^\x00]*\.swf[^\x00]*', p["txt"]):
        swfs[s] = swfs.get(s, 0) + 1
print("\n=== SWF paths ===")
for s, c in sorted(swfs.items(), key=lambda x: -x[1]):
    name = s.split("/")[-1].split("?")[0]
    folder = s.split("/")[2] if len(s.split("/")) > 2 else "?"
    print(f"  [{c}x] [{folder}] {name}")

# 2. 坐标
print("\n=== Coordinates ===")
coords = set()
for p in d["recent_text"]:
    for m in re.finditer(r'\[(\d+\.\d+),\s*(\d+\.\d+)\]', p["txt"]):
        coords.add(f"({m.group(1)}, {m.group(2)})")
for c in sorted(coords):
    print(f"  {c}")
if not coords:
    print("  None found")

# 3. 所有可读文本字段 (清理后)
print("\n=== All text fields (deduplicated) ===")
all_texts = set()
for p in d["recent_text"]:
    txt = p["txt"]
    fields = txt.split("\x00")
    for fld in fields:
        clean = "".join(c for c in fld if ord(c) >= 32)
        if len(clean) >= 2:
            all_texts.add(clean)
for t in sorted(all_texts)[:60]:
    print(f"  {t[:120]}")
if len(all_texts) > 60:
    print(f"  ... and {len(all_texts)-60} more")

# 4. 包大小分布
print("\n=== Packet sizes ===")
from collections import Counter
sc = Counter(d["sizes"])
for sz, cnt in sc.most_common(20):
    if cnt >= 3:
        print(f"  sz={sz}: {cnt}x")

# 5. 最大的包
print("\n=== Largest TEXT packets ===")
big = sorted(d["recent_text"], key=lambda x: -x["size"])[:10]
for p in big:
    clean = "".join(c for c in p["txt"] if ord(c) >= 32)
    print(f"\n  [{p['ts']}] sz={p['size']}")
    print(f"  {clean[:400]}")

# 6. 统计
print(f"\n=== Summary ===")
print(f"Packets: {d['total']}")
print(f"Text packets: {d['text']}")
print(f"Unique SWF models: {len(swfs)}")
print(f"Unique coordinates: {len(coords)}")
print(f"Unique text fields: {len(all_texts)}")
print(f"Data types found:")
for s in sorted(swfs.keys()):
    parts = s.split("/")
    if len(parts) >= 3:
        print(f"  lib/{parts[1]}/{parts[2]}")
