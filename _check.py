# -*- coding: utf-8 -*-
"""深度解析全部192个包 - 协议逆向"""

import json, struct, re, sys, os
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

p = r"c:\Users\syf\Desktop\project\menghuansanguo-script\captures\sniff_now.json"
with open(p, encoding="utf-8") as f:
    d = json.load(f)

pkts = d.get("packets", [])
print(f"总包数: {len(pkts)}")

# ============================================
# 1. 协议格式分析
# ============================================
print("\n" + "=" * 70)
print("  1. 协议头部分析 (前8字节)")
print("=" * 70)

header_types = Counter()
for pkt in pkts:
    hx = pkt.get("hex_head", "")
    hx_bytes = re.findall(r'[0-9a-f]{2}', hx.replace(" ", ""))
    if len(hx_bytes) >= 8:
        b0 = int(hx_bytes[0], 16)
        b1 = int(hx_bytes[1], 16)
        b2 = int(hx_bytes[2], 16)
        b3 = int(hx_bytes[3], 16)
        b4 = int(hx_bytes[4], 16)
        b5 = int(hx_bytes[5], 16)
        b6 = int(hx_bytes[6], 16)
        b7 = int(hx_bytes[7], 16)
        tag = f"{b0:02x} {b1:02x} {b2:02x} {b3:02x} {b4:02x} {b5:02x} {b6:02x} {b7:02x}"
        header_types[tag] += 1

print(f"头部模式 (top 20):")
for tag, cnt in header_types.most_common(20):
    print(f"  [{tag}] ... = {cnt}x")

# ============================================
# 2. 按包大小分类
# ============================================
print("\n" + "=" * 70)
print("  2. 按包大小和内容分类")
print("=" * 70)

# 提取每个包的可读文本
all_texts = []
for pkt in pkts:
    pt = pkt.get("decoded", {}).get("printable", "")
    # 清理: 只保留连续的可打印字符(>=4个)
    words = re.findall(r'[ -~]{4,}', pt)
    all_texts.append({"ts": pkt["ts"], "dir": pkt["dir"], "sz": pkt["size"], "words": words, "hex": pkt.get("hex_head", "")})

# 按大小分组
size_groups = defaultdict(list)
for t in all_texts:
    sz = t["sz"]
    if sz < 60: g = "tiny"
    elif sz < 120: g = "small"
    elif sz < 250: g = "medium"
    elif sz < 600: g = "large"
    else: g = "xlarge"
    size_groups[g].append(t)

for g in ["tiny", "small", "medium", "large", "xlarge"]:
    items = size_groups.get(g, [])
    print(f"\n--- {g} ({len(items)}个) ---")
    # 找出代表性的
    by_content = {}
    for t in items:
        key = "|".join(t["words"][:4]) if t["words"] else "(binary)"
        if key not in by_content:
            by_content[key] = []
        by_content[key].append(t)
    
    for key, texts in sorted(by_content.items(), key=lambda x: -len(x[1]))[:8]:
        t = texts[0]
        print(f"  [{len(texts)}x] sz={t['sz']} {t['dir']} {', '.join(t['words'][:8])}")

# ============================================
# 3. 提取所有数据结构和值
# ============================================
print("\n" + "=" * 70)
print("  3. 提取结构化数据字段")
print("=" * 70)

# 从可打印文本中提取有意义的值
game_values = defaultdict(list)  # category -> list of values

for pkt in pkts:
    pt = pkt.get("decoded", {}).get("printable", "")
    
    # 提取 JSON-like 数组: [数字,数字,数字]
    arrays = re.findall(r'\[([\d\.,\s\[\]]+)\]', pt)
    for arr in arrays:
        nums = [v for v in re.findall(r'\d+\.?\d*', arr)]
        if len(nums) >= 2:
            game_values["arrays"].append({"ts": pkt["ts"], "dir": pkt["dir"], "sz": pkt["size"], "arr": nums})
    
    # 提取 SWF 路径
    swfs = re.findall(r'lib/[^\x00]*?\.swf[^\x00]*', pt)
    for s in swfs:
        game_values["swfs"].append({"ts": pkt["ts"], "dir": pkt["dir"], "swf": s})
    
    # 提取纯数字序列 (可能是 IDs)
    big_nums = re.findall(r'\b(\d{6,12})\b', pt)
    for n in big_nums:
        game_values["ids"].append({"ts": pkt["ts"], "dir": pkt["dir"], "sz": pkt["size"], "id": n})
    
    # 提取 "xxx_yyy" 格式的 session/token
    tokens = re.findall(r'([0-9a-f]{32})', pt, re.IGNORECASE)
    for t in tokens:
        game_values["tokens_md5"].append({"ts": pkt["ts"], "dir": pkt["dir"], "token": t})

print(f"\n数组数据 (可能是坐标/属性): {len(game_values['arrays'])}")
for a in game_values["arrays"][:20]:
    print(f"  [{a['ts']}] {a['dir']} sz={a['sz']}: {a['arr']}")

print(f"\nSWF路径: {len(game_values['swfs'])}")
for s in game_values["swfs"][:10]:
    print(f"  [{s['ts']}] {s['dir']}: {s['swf'][:100]}")

print(f"\n玩家/怪物ID (6-12位数字): {len(game_values['ids'])}")
id_counter = Counter(v["id"] for v in game_values["ids"])
for uid, cnt in id_counter.most_common(15):
    print(f"  {uid}: {cnt}x")

print(f"\nMD5 tokens: {len(game_values['tokens_md5'])}")
for t in game_values["tokens_md5"][:10]:
    print(f"  [{t['ts']}] {t['dir']}: {t['token']}")

# ============================================
# 4. 消息类型识别 (通过特征字节模式)
# ============================================
print("\n" + "=" * 70)
print("  4. 按内容特征分类")
print("=" * 70)

feature_groups = defaultdict(list)
for pkt in pkts:
    pt = pkt.get("decoded", {}).get("printable", "")
    hx = pkt.get("hex_head", "")
    
    if "R120" in pt: feature_groups["玩家聊天(含R120)"].append(pkt)
    elif "lib/monster" in pt: feature_groups["怪物资源加载"].append(pkt)
    elif re.search(r'\[\["[^"]+","\d+",\d+', pt): feature_groups["玩家实时数据"].append(pkt)
    elif re.search(r'\b\d{9,}\b', pt) and pkt["size"] < 100: feature_groups["玩家ID请求"].append(pkt)
    elif pkt["size"] < 100: feature_groups["小包(心跳/控制)"].append(pkt)
    elif re.search(r'[0-9a-f]{32}', pt, re.I): feature_groups["认证/Token"].append(pkt)
    elif "38 00 00" in hx and pkt["size"] > 200: feature_groups["大数据包"].append(pkt)
    else: feature_groups["其他"].append(pkt)

for fg, items in sorted(feature_groups.items(), key=lambda x: -len(x[1])):
    print(f"\n  {fg}: {len(items)}个")
    for p in items[:3]:
        pt = p.get("decoded", {}).get("printable", "")
        words = re.findall(r'[ -~]{4,}', pt)
        print(f"    [{p['ts']}] {p['dir']} sz={p['size']} {' | '.join(words[:6])}")

# ============================================
# 5. 完整输出玩家实时数据包
# ============================================
print("\n" + "=" * 70)
print("  5. 玩家实时数据包 (完整解析)")
print("=" * 70)

for pkt in pkts:
    pt = pkt.get("decoded", {}).get("printable", "")
    if re.search(r'\[\["[^"]+","\d+",\d+', pt):
        print(f"\n[{pkt['ts']}] {pkt['dir']} sz={pkt['size']}")
        # 尝试解析格式: [["name","id",level,?,?,?],curHP,maxHP,[attack]]
        # 从打印字符中提取
        clean = pt
        for m in re.finditer(r'\[\["([^"]+)","(\d+)",(\d+),(\d+),(\d+),(\d+)\],([.\d]+),([.\d]+),\[([.\d]+)\]', clean):
            print(f"  名字={m.group(1)} ID={m.group(2)} 等级={m.group(3)} {m.group(4)} {m.group(5)} {m.group(6)}")
            print(f"  当前HP={m.group(7)} 最大HP={m.group(8)} 攻击={m.group(9)}")
        
        # HEX dump
        hx = pkt.get("hex_head", "")
        print(f"  HEX: {hx[:300]}")

# ============================================
# 6. 时间线分析
# ============================================
print("\n" + "=" * 70)
print("  6. 通信时间线")
print("=" * 70)

# 按时间排序
pkts_sorted = sorted(pkts, key=lambda x: x["ts"])
if pkts_sorted:
    start_ts = pkts_sorted[0]["ts"]
    end_ts = pkts_sorted[-1]["ts"]
    print(f"  时间范围: {start_ts} → {end_ts}")
    
    # 每秒包数
    sec_counts = Counter(p["ts"][:8] for p in pkts_sorted)
    for sec, cnt in sec_counts.most_common():
        print(f"    {sec}: {cnt}包")

# ============================================
# 7. 所有包的全文本解码
# ============================================
print("\n" + "=" * 70)
print("  7. 全部192包的文本内容 (时间顺序)")
print("=" * 70)

for i, pkt in enumerate(pkts_sorted):
    pt = pkt.get("decoded", {}).get("printable", "")
    # 找出所有连续可打印字符段
    segments = re.findall(r'[ -~]{4,}', pt)
    seg_str = " | ".join(segments[:8])
    print(f"[{i:3d}] {pkt['ts']} {pkt['dir']} sz={pkt['size']:5d} {seg_str[:200]}")
