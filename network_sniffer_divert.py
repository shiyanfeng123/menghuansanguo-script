"""
Flash 游戏网络包嗅探器 (pydivert)
pip install pydivert psutil

使用: 以管理员身份运行
    python network_sniffer_divert.py
"""

import os, sys, time, json, ctypes, subprocess
from datetime import datetime

CAPTURES_DIR = os.path.join(os.path.dirname(__file__), "captures")
os.makedirs(CAPTURES_DIR, exist_ok=True)

GAME_TITLE = "111"
SNIFF_DURATION = 120
SKIP_ADMIN = os.environ.get("SKIP_ADMIN", "0") == "1"

try: import psutil
except ImportError: print("pip install psutil"); sys.exit(1)

try: import pydivert
except ImportError: print("pip install pydivert"); sys.exit(1)


def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False


def find_window_by_title(title):
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, title)
    if hwnd: return hwnd
    result = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    def cb(h, _):
        l = user32.GetWindowTextLengthW(h)
        if l == 0: return True
        b = ctypes.create_unicode_buffer(l + 1)
        user32.GetWindowTextW(h, b, l + 1)
        if title.lower() in b.value.lower():
            result.append(h); return False
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return result[0] if result else None


def get_pid_from_hwnd(hwnd):
    user32 = ctypes.windll.user32
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_all_connections(pid):
    visited, all_conns = set(), []
    def _collect(target_pid, depth=0):
        if target_pid in visited or depth > 4: return
        visited.add(target_pid)
        try:
            proc = psutil.Process(target_pid)
            try: name = proc.name() or "?"
            except: name = "?"
            try: conns = proc.net_connections()
            except: conns = []
            for c in conns:
                if c.status == 'ESTABLISHED' and c.raddr:
                    all_conns.append({"pid": target_pid, "name": name,
                                      "remote_ip": c.raddr.ip,
                                      "remote_port": c.raddr.port,
                                      "local_port": c.laddr.port})
            for child in proc.children(recursive=True):
                _collect(child.pid, depth + 1)
            parent = proc.parent()
            if parent: _collect(parent.pid, depth + 1)
        except: pass
    _collect(pid)
    return all_conns


def analyze_payload(data, pkt_id, direction):
    r = {"id": pkt_id, "size": len(data),
         "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3],
         "fmt": "?", "txt": "", "sum": "", "dir": direction,
         "hex40": data[:40].hex()}
    try:
        r["txt"] = "".join(c if c.isprintable() or c in "\r\n\t" else "."
                           for c in data.decode("utf-8", errors="replace"))[:500]
    except: pass
    if data[:3] == b'\x00\x03\x00':
        r["fmt"] = "AMF"; r["sum"] += "[AMF3]"
    elif data[:1] == b'\x00':
        r["fmt"] = "AMF"; r["sum"] += "[AMF]"
    kws = ["怪物","monster","整点","火焰帝","寒冰帝","生肖","龙","蛇",
           "refresh","spawn","BOSS","npc","NPC","SpawnMonster","CreateMonster"]
    try:
        t = data.decode("utf-8", errors="ignore")
        f = [kw for kw in kws if kw in t]
        if f: r["fmt"] = "TXT!"; r["sum"] += f"[{','.join(f)}]"
    except: pass
    return r


def sniff_game(srv_ip, srv_port):
    col = {"start": datetime.now().strftime("%H:%M:%S"),
           "server": f"{srv_ip}:{srv_port}", "cnt": 0, "pkts": [], "sizes": []}

    filter_str = (f"tcp and (ip.SrcAddr == {srv_ip} or ip.DstAddr == {srv_ip})"
                  f" and (tcp.SrcPort == {srv_port} or tcp.DstPort == {srv_port})")

    print(f"Filter: {filter_str}")
    print(f"Sniffing {SNIFF_DURATION}s ...\n")

    try:
        with pydivert.WinDivert(filter_str) as w:
            t_end = time.time() + SNIFF_DURATION
            while time.time() < t_end:
                try:
                    packet = w.recv()
                except Exception:
                    packet = None
                    time.sleep(0.001)
                if packet is None:
                    continue
                try:
                    data = packet.raw.tcp_payload
                    if isinstance(data, memoryview):
                        data = bytes(data)
                    if not data or len(data) < 8:
                        w.send(packet)
                        continue

                    col["cnt"] += 1
                    col["sizes"].append(len(data))
                    direction = "S->C" if packet.ipv4_srcaddr == srv_ip else "C->S"
                    info = analyze_payload(data, col["cnt"], direction)
                    info["src"] = f"{packet.ipv4_srcaddr}:{packet.tcp_srcport}"
                    info["dst"] = f"{packet.ipv4_dstaddr}:{packet.tcp_dstport}"
                    col["pkts"].append(info)
                    show = (col["cnt"] <= 10 or info["size"] > 100
                            or info["fmt"] in ("TXT!","AMF")
                            or col["cnt"] % 100 == 0)
                    if show:
                        prefix = ">>>" if info["fmt"] in ("TXT!",) else "   "
                        print(f"  {prefix} [{info['ts']}] #{col['cnt']} "
                              f"sz={info['size']} {info['fmt']}"
                              f" [{info['dir']}] {info['sum'][:100]}")
                except:
                    pass
                w.send(packet)
    except OSError as e:
        msg = str(e)
        if "WinError 5" in msg:
            print(f"\nERROR: Need Administrator privileges!")
            print("Please run: python network_sniffer_divert.py (as admin)")
        else:
            print(f"\nERROR: {e}")
        return col

    return col


def save_results(col):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fn = os.path.join(CAPTURES_DIR, f"sniff_{ts}.json")

    amf_packets = [p for p in col["pkts"] if p.get("fmt","") == "AMF"]
    text_packets = [p for p in col["pkts"] if p.get("fmt","") == "TXT!"]
    big_packets = [p for p in col["pkts"] if p["size"] > 200]

    susp = amf_packets + text_packets + big_packets
    seen = {}
    unique_susp = []
    for p in susp:
        key = p.get("hex40", "")
        if key not in seen:
            seen[key] = True
            unique_susp.append(p)

    size_dist = {}
    for s in col.get("sizes", []):
        bucket = (s // 50) * 50
        size_dist[str(bucket)] = size_dist.get(str(bucket), 0) + 1

    r = {
        "start": col["start"],
        "server": col["server"],
        "total": col["cnt"],
        "amf_count": len(amf_packets),
        "text_count": len(text_packets),
        "big_count": len(big_packets),
        "unique_suspicious": len(unique_susp),
        "size_distribution": dict(sorted(size_dist.items(), key=lambda x: int(x[0]))[:30]),
        "suspicious": unique_susp[:50],
    }
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"RESULTS: {col['cnt']} total pkts")
    print(f"  AMF packets: {len(amf_packets)}")
    print(f"  TEXT packets: {len(text_packets)}")
    print(f"  BIG packets (>200B): {len(big_packets)}")
    print(f"  Unique suspicious: {len(unique_susp)}")
    print(f"  Size distribution: {dict(sorted(size_dist.items(), key=lambda x: int(x[0]))[:10])}")
    print(f"Saved: {fn}")

    if text_packets:
        print(f"\n*** TEXT PACKETS FOUND - PROTOCOL IS PLAINTEXT! ***")
        for p in text_packets[:10]:
            print(f"  [{p['ts']}] sz={p['size']} [{p['dir']}]")
            print(f"    {p.get('txt','')[:300]}")
    elif amf_packets:
        print(f"\nAMF packets found - likely Flash AMF protocol")
        for p in amf_packets[:5]:
            print(f"  [{p['ts']}] sz={p['size']} [{p['dir']}] hex={p.get('hex40','')[:80]}")
    elif col["cnt"] > 0:
        print(f"\nNo AMF/TEXT packets. Protocol may be custom binary.")
        for p in col["pkts"][:5]:
            print(f"  [{p['ts']}] sz={p['size']} [{p['dir']}] hex={p.get('hex40','')[:80]}")
    else:
        print("\nNo packets captured. Check admin privileges and game connection.")


def main():
    if not SKIP_ADMIN and not is_admin():
        print("Re-launching with admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join([f'"{a}"' for a in sys.argv]),
            os.path.dirname(os.path.abspath(__file__)), 1
        )
        return

    print("=" * 60)
    print("Flash Game Network Sniffer")
    print(f"Window: '{GAME_TITLE}' | Sniff: {SNIFF_DURATION}s")
    print(f"Admin: {is_admin()}")
    print("=" * 60)

    print(f"\n[1] Find window '{GAME_TITLE}' ...")
    hwnd = find_window_by_title(GAME_TITLE)
    if not hwnd: print("Window not found"); return
    pid = get_pid_from_hwnd(hwnd)
    print(f"  PID={pid}  {psutil.Process(pid).name()}")

    print(f"\n[2] Find game connections...")
    conns = get_all_connections(pid)
    if not conns:
        print("Global scan..."); conns = []
        for p in psutil.process_iter(['pid','name']):
            try:
                for c in p.net_connections():
                    if c.status=='ESTABLISHED' and c.raddr:
                        conns.append({"pid":p.info['pid'],"name":p.info['name'] or "?",
                                      "remote_ip":c.raddr.ip,"remote_port":c.raddr.port,
                                      "local_port":c.laddr.port})
            except: continue
    if not conns: print("No connections found"); return

    for i,c in enumerate(conns):
        mark = f" local:{c['local_port']}" if c.get('local_port') else ""
        print(f"  [{i}] PID={c['pid']} {c['name']} -> {c['remote_ip']}:{c['remote_port']}{mark}")

    local_ips = ["192.168.", "10.", "172.", "127."]
    remote = [c for c in conns
              if not any(c['remote_ip'].startswith(p) for p in local_ips)]
    game_conns = [c for c in remote if c['remote_port'] not in (80, 443, 8080, 8443)]
    if not game_conns: game_conns = [c for c in remote if c['remote_port'] > 1024]
    if not game_conns: game_conns = remote

    selected = game_conns[0]
    srv_ip = selected['remote_ip']
    srv_port = selected['remote_port']
    print(f"\nTarget: {srv_ip}:{srv_port}")

    print(f"\n[3] Sniffing ({SNIFF_DURATION}s)...\n")
    col = sniff_game(srv_ip, srv_port)
    save_results(col)


if __name__ == "__main__":
    main()
