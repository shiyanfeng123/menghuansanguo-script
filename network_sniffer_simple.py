"""
Flash Game Sniffer - 管理员运行此文件
    python network_sniffer_simple.py
持续运行, 结果写 captures/sniff_live.json
"""

import os, sys, time, json, ctypes
from datetime import datetime

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "captures", "sniff_live.json")
GAME_TITLE = "111"

try: import psutil
except ImportError: print("pip install psutil"); input(); sys.exit(1)

try: import pydivert
except ImportError: print("pip install pydivert"); input(); sys.exit(1)


def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False


def find_window(title):
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, title)
    if hwnd: return hwnd
    result = []
    WEP = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    def cb(h, _):
        l = user32.GetWindowTextLengthW(h)
        if l == 0: return True
        b = ctypes.create_unicode_buffer(l + 1)
        user32.GetWindowTextW(h, b, l + 1)
        if title.lower() in b.value.lower():
            result.append(h); return False
        return True
    user32.EnumWindows(WEP(cb), 0)
    return result[0] if result else None


def get_pid(hwnd):
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_connections(pid):
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


def write_result(result):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    if not is_admin():
        print("Need admin. Re-launching...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{__file__}"',
            os.path.dirname(__file__), 1)
        return

    print("=" * 60)
    print("Flash Game Network Sniffer")
    print(f"Window='{GAME_TITLE}' Output={OUTPUT_FILE}")
    print("=" * 60)

    hwnd = find_window(GAME_TITLE)
    if not hwnd:
        print("Window not found")
        write_result({"status": "error", "msg": "window not found"})
        input(); return

    pid = get_pid(hwnd)
    print(f"PID={pid} {psutil.Process(pid).name()}")

    conns = get_connections(pid)
    if not conns:
        print("No connections")
        write_result({"status": "error", "msg": "no connections"})
        input(); return

    for i, c in enumerate(conns):
        print(f"  [{i}] -> {c['remote_ip']}:{c['remote_port']}")

    remote = [c for c in conns
              if not any(c['remote_ip'].startswith(p)
                         for p in ["192.168.", "10.", "172.", "127."])]
    game = [c for c in remote if c['remote_port'] not in (80,443,8080,8443)]
    if not game: game = remote
    srv_ip, srv_port = game[0]['remote_ip'], game[0]['remote_port']

    print(f"\nTarget: {srv_ip}:{srv_port}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Close window to stop.\n")

    result = {
        "status": "running",
        "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "server": f"{srv_ip}:{srv_port}",
        "total": 0, "amf3": 0, "amf": 0, "text": 0,
        "sizes": [], "recent_text": [], "recent_amf": [],
        "last_write": datetime.now().strftime("%H:%M:%S")
    }
    write_result(result)

    filter_str = (
        f"tcp and (ip.SrcAddr == {srv_ip} or ip.DstAddr == {srv_ip})"
        f" and (tcp.SrcPort == {srv_port} or tcp.DstPort == {srv_port})")
    print(f"Filter: {filter_str}\n")

    consecutive_errors = 0
    last_write = time.time()

    KWS = ["怪物","monster","整点","火焰帝","寒冰帝","生肖","龙","蛇",
           "refresh","spawn","BOSS","npc","NPC","SpawnMonster","CreateMonster"]

    while True:
        try:
            with pydivert.WinDivert(filter_str) as w:
                consecutive_errors = 0
                print("Connected. Capturing...")
                while True:
                    packet = w.recv()
                    now = time.time()
                    if now - last_write >= 30:
                        result["last_write"] = datetime.now().strftime("%H:%M:%S")
                        result["sizes"] = result["sizes"][-5000:]
                        write_result(result)
                        last_write = now
                        print(f"  [{result['last_write']}] total={result['total']} "
                              f"AMF3={result['amf3']} AMF={result['amf']} TEXT={result['text']}")

                    try:
                        raw = packet.raw
                        if hasattr(raw, 'tcp_payload'):
                            data = raw.tcp_payload
                        else:
                            data = raw
                        if isinstance(data, memoryview):
                            data = bytes(data)
                    except Exception:
                        w.send(packet)
                        continue

                    if not data or len(data) < 8:
                        w.send(packet)
                        continue

                    try:
                        direction = "S->C" if packet.ipv4_srcaddr == srv_ip else "C->S"
                    except Exception:
                        direction = "?"
                    result["total"] += 1
                    result["sizes"].append(len(data))

                    if data[:3] == b'\x00\x03\x00':
                        result["amf3"] += 1
                        info = {"size": len(data), "dir": direction,
                                "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                                "hex": data[:80].hex()}
                        if len(result["recent_amf"]) < 50:
                            result["recent_amf"].append(info)
                        print(f"  AMF3 sz={len(data)} [{direction}]")

                    elif data[:1] == b'\x00':
                        result["amf"] += 1
                        info = {"size": len(data), "dir": direction,
                                "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                                "hex": data[:80].hex()}
                        if len(result["recent_amf"]) < 50:
                            result["recent_amf"].append(info)

                    else:
                        txt = data.decode("utf-8", errors="replace")
                        if any(kw in txt for kw in KWS):
                            result["text"] += 1
                            info = {"size": len(data), "dir": direction,
                                    "ts": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                                    "txt": txt[:500]}
                            result["recent_text"].append(info)
                            if len(result["recent_text"]) > 100:
                                result["recent_text"] = result["recent_text"][-100:]
                            print(f"\n*** TEXT *** sz={len(data)} [{direction}]")
                            print(f"    {txt[:400]}\n")

                    w.send(packet)
        except KeyboardInterrupt:
            print("\nStopped.")
            result["status"] = "stopped_by_user"
            result["ended"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_result(result)
            return
        except Exception as e:
            consecutive_errors += 1
            print(f"Error ({consecutive_errors}/10): {e}")
            result["status"] = f"reconnecting ({consecutive_errors})"
            write_result(result)
            if consecutive_errors >= 10:
                result["status"] = f"stopped: max retries"
                result["ended"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                write_result(result)
                input("Max retries. Press Enter...")
                return
            time.sleep(5)


if __name__ == "__main__":
    main()
