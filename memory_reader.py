# -*- coding: utf-8 -*-
"""
梦幻三国 - 内存实时数据读取器 v3 (磁盘缓存版)
=============================================
策略: 首次全扫描(30-60s) → 存磁盘缓存 → 后续秒读(10-50ms)
     缓存的地址数据在游戏重启后才需重新扫描
"""

import ctypes
from ctypes import wintypes, byref, sizeof, create_string_buffer, c_void_p
import ctypes.wintypes as w
import psutil
import struct
import re
import time
import json
import os

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "memory_cache.json")

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
MEM_PRIVATE = 0x20000

BUF_SIZE = 256 * 1024


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", c_void_p), ("AllocationBase", c_void_p),
        ("AllocationProtect", w.DWORD), ("RegionSize", ctypes.c_size_t),
        ("State", w.DWORD), ("Protect", w.DWORD), ("Type", w.DWORD),
    ]


def _open_process(pid):
    return kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)


def _read_mem(hProcess, address, size):
    buf = create_string_buffer(size)
    bytes_read = ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(hProcess, c_void_p(address), buf, size, byref(bytes_read)):
        return buf.raw[:bytes_read.value]
    return None


def _find_main_pid():
    """找包含游戏数据的 360Game.exe 进程"""
    hwnd = user32.FindWindowW(None, "111")
    window_pid = None
    if hwnd:
        pid = w.DWORD()
        user32.GetWindowThreadProcessId(hwnd, byref(pid))
        window_pid = pid.value

    # 收集所有 360Game.exe, 按内存从大到小
    candidates = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"].lower() == "360game.exe":
                mem = proc.memory_info().rss
                candidates.append((proc.info["pid"], mem))
        except:
            pass
    candidates.sort(key=lambda x: -x[1])

    # 按内存从大到小逐个试探, 找包含游戏数据的进程
    for pid, mem in candidates:
        if mem < 50 * 1024 * 1024:  # 放过太小的
            continue
        h = _open_process(pid)
        if not h:
            continue
        # 快速试探: 搜 playerInfo.swf
        found = False
        addr = 0
        max_addr = 0x7FFFFFFF
        mbi = MEMORY_BASIC_INFORMATION()
        pattern = b"playerInfo.swf"
        while addr < max_addr:
            sz = kernel32.VirtualQueryEx(h, c_void_p(addr), byref(mbi), sizeof(mbi))
            if sz == 0:
                break
            base = mbi.BaseAddress or 0
            rsz = mbi.RegionSize
            if mbi.State == MEM_COMMIT:
                for cs in range(base, base + rsz, BUF_SIZE):
                    buf = create_string_buffer(min(BUF_SIZE, base + rsz - cs))
                    br = ctypes.c_size_t(0)
                    if kernel32.ReadProcessMemory(h, c_void_p(cs), buf, min(BUF_SIZE, base + rsz - cs), byref(br)):
                        if pattern in buf.raw[:br.value]:
                            found = True
                            break
                if found:
                    break
            addr = base + rsz
        kernel32.CloseHandle(h)
        if found:
            return pid

    # 兜底: 返回内存最大的
    return candidates[0][0] if candidates else None


def _full_scan_boss_addrs(hProcess):
    """全内存扫描 BOSS 数据 (30-60秒, 仅首次做)"""
    print("  [全扫描] 搜索 BOSS 数据锚点... (首次, 约30-60秒)")
    addrs = []
    addr = 0
    max_addr = 0x7FFFFFFF
    mbi = MEMORY_BASIC_INFORMATION()
    pattern = b"isWobao"
    plen = len(pattern)
    scanned_mb = 0

    while addr < max_addr:
        sz = kernel32.VirtualQueryEx(hProcess, c_void_p(addr), byref(mbi), sizeof(mbi))
        if sz == 0:
            break
        base = mbi.BaseAddress or 0
        region_size = mbi.RegionSize
        if mbi.State == MEM_COMMIT:
            for chunk_start in range(base, base + region_size, BUF_SIZE):
                chunk_size = min(BUF_SIZE, base + region_size - chunk_start)
                data = _read_mem(hProcess, chunk_start, chunk_size)
                if not data:
                    continue
                scanned_mb += len(data)
                pos = 0
                while True:
                    idx = data.find(pattern, pos)
                    if idx < 0:
                        break
                    addrs.append(chunk_start + idx)
                    pos = idx + plen
                    if len(addrs) >= 200:
                        print(f"  [全扫描] 完成! 找到 {len(addrs)} 个锚点 (扫描 {scanned_mb//(1024*1024)}MB)")
                        return addrs
        addr = base + region_size
    print(f"  [全扫描] 完成! 找到 {len(addrs)} 个锚点 (扫描 {scanned_mb//(1024*1024)}MB)")
    return addrs


def _extract_json_block(hProcess, address, max_len=4096):
    start = max(0, address - 256)
    data = _read_mem(hProcess, start, max_len)
    if not data:
        return None
    offset = address - start
    brace_start = data.rfind(b"{", 0, offset)
    if brace_start < 0:
        return None
    depth = 0
    for i in range(brace_start, len(data)):
        if data[i:i+1] == b"{":
            depth += 1
        elif data[i:i+1] == b"}":
            depth -= 1
            if depth == 0:
                return data[brace_start:i + 1]
    return None


BOSS_HOURS = {3, 7, 11, 15, 19, 23}


class MemoryReader:
    def __init__(self):
        self._pid = None
        self._handle = None
        self._boss_addrs = []
        self._last_boss_scan = 0
        self._cache = {"bosses": [], "map_id": None, "in_battle": False}
        self._initialized = False

    def connect(self):
        if self._handle:
            return True
        pid = _find_main_pid()
        if not pid:
            print("[MemoryReader] 未找到游戏进程")
            return False
        try:
            self._handle = _open_process(pid)
            self._pid = pid
            if not self._handle:
                return False
            mem = psutil.Process(pid).memory_info().rss // (1024 * 1024)
            print(f"[MemoryReader] 已连接 PID={pid} ({mem}MB)")

            # 加载缓存
            self._load_cache()
            self._initialized = True
            return True
        except Exception as e:
            print(f"[MemoryReader] 连接失败: {e}")
            self.disconnect()
            return False

    def disconnect(self):
        if self._handle:
            kernel32.CloseHandle(self._handle)
            self._handle = None
            self._pid = None

    # -------------------------------------------------------
    # 磁盘缓存
    # -------------------------------------------------------
    def _save_cache(self):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "pid": self._pid,
                    "boss_addrs": [hex(a) for a in self._boss_addrs],
                    "saved_at": time.time(),
                }, f, ensure_ascii=False)
        except Exception as e:
            print(f"  [缓存] 保存失败: {e}")

    def _load_cache(self):
        if not os.path.exists(CACHE_FILE):
            print("[MemoryReader] 无缓存, 将进行首次全扫描...")
            return

        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 检查 PID 是否还活着 + 进程是否重开过
            cached_pid = data.get("pid", 0)
            try:
                proc = psutil.Process(cached_pid)
                if proc.name().lower() == "360game.exe":
                    if cached_pid == self._pid:
                        addrs = [int(a, 16) for a in data.get("boss_addrs", [])]
                        self._boss_addrs = addrs
                        print(f"[MemoryReader] 磁盘缓存加载: {len(addrs)} 个锚点 (PID匹配)")
                        return
            except psutil.NoSuchProcess:
                pass

            # PID 不匹配或进程已死 -> 如果当前 PID 存在, 复用旧地址试探
            addrs = [int(a, 16) for a in data.get("boss_addrs", [])]
            if addrs and self._handle:
                valid = 0
                for addr in addrs[:20]:
                    block = _extract_json_block(self._handle, addr)
                    if block and b'"isWobao"' in block:
                        valid += 1
                if valid > 0:
                    self._boss_addrs = addrs
                    print(f"[MemoryReader] 磁盘缓存加载: {len(addrs)} 个锚点 (复用, {valid}/{min(20,len(addrs))} 有效)")
                    return

            print("[MemoryReader] 缓存失效, 将重新扫描...")

        except Exception as e:
            print(f"[MemoryReader] 缓存读取失败: {e}")

    # -------------------------------------------------------
    # BOSS 数据
    # -------------------------------------------------------
    def get_boss_positions(self):
        if not self._handle:
            return []

        # 首次: 扫描 + 缓存
        if not self._boss_addrs:
            self._boss_addrs = _full_scan_boss_addrs(self._handle)
            if self._boss_addrs:
                self._save_cache()
            self._last_boss_scan = time.time()
        else:
            # 已有缓存: 只解析, 不重新扫 (避免战斗中扫出0覆盖缓存)
            pass

        results = []
        seen = set()
        field_pat = re.compile(rb'"(\w+)"\s*:\s*(-?[\d.]+|true|false)')

        for addr in self._boss_addrs:
            block = _extract_json_block(self._handle, addr)
            if not block:
                continue

            fields = {}
            for m in field_pat.finditer(block):
                key = m.group(1).decode()
                val = m.group(2).decode()
                if val == "true":
                    fields[key] = True
                elif val == "false":
                    fields[key] = False
                elif "." in val:
                    fields[key] = float(val)
                else:
                    fields[key] = int(val)

            obj_id = fields.get("id")
            if obj_id is None or obj_id in seen:
                continue
            seen.add(obj_id)

            results.append({
                "id": obj_id,
                "monId": fields.get("monId", 0),
                "x": fields.get("x", 0),
                "y": fields.get("y", 0),
                "mapId": fields.get("mapId", 0),
                "isWobao": fields.get("isWobao", False),
                "time": fields.get("time", 0),
            })

        self._cache["bosses"] = results
        return results

    # -------------------------------------------------------
    # 当前地图
    # -------------------------------------------------------
    def get_current_map_id(self):
        if not self._handle:
            return None
        for addr in self._boss_addrs:
            ctx = _read_mem(self._handle, max(0, addr - 64), 256)
            if ctx:
                txt = ctx.decode("utf-8", errors="replace")
                m = re.search(r'"mapId"\s*:\s*(\d+)', txt)
                if m:
                    map_id = int(m.group(1))
                    self._cache["map_id"] = map_id
                    return map_id
        return self._cache.get("map_id")

    def is_in_battle(self):
        if not self._handle:
            return False
        # 简单判断: 如果没有 BOSS 数据返回, 可能是在战斗中 (地图切了)
        # 更可靠的方式: 找 FightStateData 关键字
        addr = 0
        max_addr = 0x7FFFFFFF
        mbi = MEMORY_BASIC_INFORMATION()
        pattern = b'FightStateData'
        plen = len(pattern)

        while addr < max_addr:
            sz = kernel32.VirtualQueryEx(self._handle, c_void_p(addr), byref(mbi), sizeof(mbi))
            if sz == 0:
                break
            base = mbi.BaseAddress or 0
            region_size = mbi.RegionSize
            if mbi.State == MEM_COMMIT:
                for chunk_start in range(base, base + region_size, BUF_SIZE):
                    chunk_size = min(BUF_SIZE, base + region_size - chunk_start)
                    data = _read_mem(self._handle, chunk_start, chunk_size)
                    if not data:
                        continue
                    if data.find(pattern) >= 0:
                        self._cache["in_battle"] = True
                        return True
            addr = base + region_size

        self._cache["in_battle"] = False
        return False

    # -------------------------------------------------------
    # 综合快照
    # -------------------------------------------------------
    def get_full_status(self):
        t0 = time.time()
        if not self._handle:
            try:
                self.connect()
            except:
                return {"timestamp": t0, "error": "not connected"}

        bosses = self.get_boss_positions()
        map_id = self.get_current_map_id()
        in_battle = self.is_in_battle()
        hour = time.localtime().tm_hour

        return {
            "timestamp": t0,
            "map_id": map_id,
            "in_battle": in_battle,
            "is_integrity_hour": hour in BOSS_HOURS,
            "bosses": bosses,
            "boss_count": len(bosses),
            "elapsed_ms": round((time.time() - t0) * 1000),
        }

    def dump_snapshot(self):
        t0 = time.time()
        s = self.get_full_status()

        print(f"\n{'='*60}")
        print(f"  游戏状态 ({time.strftime('%H:%M:%S')}) 耗时={s.get('elapsed_ms')}ms")
        print(f"{'='*60}")
        print(f"  地图ID: {s.get('map_id', '?')}")
        print(f"  战斗中: {'YES' if s.get('in_battle') else 'NO'}")
        print(f"  整点: {'YES' if s.get('is_integrity_hour') else 'NO'}")
        bosses = s.get("bosses", [])
        print(f"  BOSS: {len(bosses)} 个")
        for b in bosses[:10]:
            wobao = "[窝宝]" if b.get("isWobao") else ""
            print(f"    monId={b['monId']} ({b['x']},{b['y']}) mapId={b['mapId']} 剩余{b['time']}s {wobao}")
        if len(bosses) > 10:
            print(f"    ... +{len(bosses) - 10}")
        return s


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print("  MemoryReader v3 - 磁盘缓存 · 实时监控")
    print("=" * 60)

    reader = MemoryReader()
    if not reader.connect():
        print("请确保游戏(标题'111')正在运行!")
        sys.exit(1)

    print("\n实时监控中... (Ctrl+C 停止)\n")

    try:
        while True:
            t0 = time.time()
            s = reader.get_full_status()
            elapsed = time.time() - t0

            bosses = s.get("bosses", [])
            boss_str = ",".join(f"m{b['monId']}@{b['x']},{b['y']}" for b in bosses[:3]) if bosses else "-"

            print(
                f"[{time.strftime('%H:%M:%S')}] "
                f"map={s.get('map_id','?')} "
                f"battle={'YES' if s.get('in_battle') else 'NO'} "
                f"BOSS({len(bosses)}):{boss_str} "
                f"({elapsed*1000:.0f}ms)"
            )
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n停止。")
    finally:
        reader.disconnect()
