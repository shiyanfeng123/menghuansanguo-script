# -*- coding: utf-8 -*-
"""
TCP 抓包工具 - 必须以管理员身份运行!
右键 → 以管理员身份运行 PowerShell → python tcp_monitor.py

抓取游戏与服务器 139.199.3.89:30000 的所有通信
自动分析协议格式
"""

import pydivert
import time
import json
import os
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GAME_SERVER = "139.199.3.89"
GAME_PORT = 30000
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(SCRIPT_DIR, "captures", "sniff_now.json")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
DURATION = 60  # 抓60秒

captured = []
start_time = None

def analyze_payload(payload):
    info = {"size": len(payload), "patterns": [], "decoded": {}, "hex_head": ""}

    # hex 前64字节
    info["hex_head"] = " ".join(f"{b:02x}" for b in payload[:64])

    # 协议类型判断
    first_byte = payload[0] if payload else 0

    # Flash AMF 协议 (游戏常用)
    if first_byte == 0x00:
        info["patterns"].append("AMF0")
    elif first_byte == 0x11:
        info["patterns"].append("AMF3")
    elif first_byte == 0x08:
        info["patterns"].append("PROTOBUF-varint")

    # 文本特征
    if b"PlayerData" in payload: info["patterns"].append("PlayerData")
    if b"FuBenData" in payload: info["patterns"].append("FuBenData")
    if b"isWobao" in payload: info["patterns"].append("isWobao")
    if b"mapId" in payload: info["patterns"].append("mapId")
    if b"monId" in payload: info["patterns"].append("monId")
    if b"fight" in payload: info["patterns"].append("fight")
    if b"hp" in payload: info["patterns"].append("hp")
    if b"{" in payload and b"}" in payload: info["patterns"].append("JSON")

    # UTF-8 解码
    try:
        info["decoded"]["utf8"] = payload.decode("utf-8", errors="replace")[:500]
    except: pass

    # 可打印 ASCII
    info["decoded"]["printable"] = "".join(
        chr(b) if 32 <= b < 127 else "." for b in payload[:300]
    )

    return info


def main():
    global start_time, captured
    print("=" * 70)
    print("  游戏 TCP 抓包 — 请确保以管理员身份运行!")
    print(f"  服务器: {GAME_SERVER}:{GAME_PORT}")
    print(f"  抓包时长: {DURATION}秒")
    print("=" * 70)

    print(f"\n抓包中... 请在游戏中操作 (走路/战斗/打开界面)")
    print(f"(自动在 {DURATION}秒后停止)\n")

    start_time = time.time()
    filt = f"tcp and (tcp.DstPort == {GAME_PORT} or tcp.SrcPort == {GAME_PORT})"

    try:
        with pydivert.WinDivert(filt) as w:
            for pkt in w:
                payload = bytes(pkt.tcp.payload) if pkt.tcp.payload else b""
                w.send(pkt)

                if not payload or len(payload) < 2:
                    if time.time() - start_time > DURATION:
                        break
                    continue

                direction = ">>> 发送" if pkt.is_outbound else "<<< 接收"
                info = analyze_payload(payload)
                captured.append({
                    "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "dir": direction,
                    **info,
                })

                elapsed = time.time() - start_time
                if info["patterns"]:
                    print(f"[{elapsed:.0f}s] {direction} sz={info['size']:5d}  {info['patterns']}")
                    if info["decoded"].get("printable"):
                        print(f"         {info['decoded']['printable'][:120]}")
                    print(f"         {info['hex_head'][:120]}")

                if elapsed > DURATION:
                    break

    except PermissionError:
        print("\n" + "=" * 70)
        print("  权限不足! 必须以管理员身份运行!")
        print("  右键 PowerShell → 以管理员身份运行 → 执行:")
        print(f"    python \"{__file__}\"")
        print("=" * 70)
        input("按回车退出...")
        return

    # ======================
    # 分析结果
    # ======================
    print(f"\n{'=' * 70}")
    print(f"  抓包结束! 共 {len(captured)} 个有效数据包")
    print(f"{'=' * 70}")

    if not captured:
        print("\n未抓到任何包。可能原因:")
        print("  1. 游戏在60秒内没有与服务器通信")
        print("  2. 游戏使用了HTTP/WebSocket而非原生TCP")
        print("请操作游戏后重试")
        input("按回车退出...")
        return

    # 协议类型统计
    pattern_counts = {}
    for p in captured:
        for pat in p["patterns"]:
            pattern_counts[pat] = pattern_counts.get(pat, 0) + 1
    print(f"\n协议特征: {pattern_counts}")

    # 大小分布
    size_grp = {}
    for p in captured:
        sz = p["size"]
        if sz < 50: g = "<50B"
        elif sz < 200: g = "50-200B"
        elif sz < 500: g = "200-500B"
        elif sz < 1000: g = "500-1KB"
        else: g = ">1KB"
        size_grp[g] = size_grp.get(g, 0) + 1
    print(f"包大小: {size_grp}")

    # 方向统计
    out_count = sum(1 for p in captured if "发送" in p["dir"])
    in_count = len(captured) - out_count
    print(f"方向: 发送={out_count}, 接收={in_count}")

    # 特征包详情
    interesting = [p for p in captured if p["patterns"]]
    if interesting:
        print(f"\n{'=' * 70}")
        print(f"  包含游戏特征的包 ({len(interesting)}个)")
        print(f"{'=' * 70}")
        for p in interesting[:20]:
            print(f"\n[{p['ts']}] {p['dir']} sz={p['size']} {p['patterns']}")
            for enc, txt in p["decoded"].items():
                if txt.strip() and enc != "printable":
                    print(f"  [{enc}] {txt[:300]}")
            print(f"  PRINT: {p['decoded'].get('printable', '')[:200]}")
            print(f"  HEX: {p['hex_head'][:200]}")

    # 全部包
    print(f"\n{'=' * 70}")
    print(f"  全部 {len(captured)} 个包")
    print(f"{'=' * 70}")
    for p in captured:
        pat_str = f" [{', '.join(p['patterns'])}]" if p['patterns'] else ""
        print(f"[{p['ts']}] {p['dir']} sz={p['size']:5d}{pat_str}")
        if p["decoded"].get("printable"):
            print(f"  PRINT: {p['decoded']['printable'][:150]}")
        print(f"  HEX: {p['hex_head'][:120]}")

    # 保存
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "server": f"{GAME_SERVER}:{GAME_PORT}",
            "total": len(captured),
            "pattern_counts": pattern_counts,
            "size_groups": size_grp,
            "packets": captured,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n详细数据已保存到: {OUTPUT}")

    input("\n按回车退出...")


if __name__ == "__main__":
    main()
