# -*- coding: utf-8 -*-
"""深入分析 HP+MP 所在的玩家数据结构"""
import ctypes,struct,os,sys,time,psutil
from ctypes import wintypes,byref,sizeof,create_string_buffer,c_void_p
import ctypes.wintypes as w
sys.stdout.reconfigure(encoding="utf-8",errors="replace")

kernel32=ctypes.WinDLL("kernel32",use_last_error=True)

def open_proc(pid):return kernel32.OpenProcess(0x0010|0x0400,False,pid)
def read(h,a,s):
    buf=create_string_buffer(s);br=ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h,c_void_p(a),buf,s,byref(br)):return buf.raw[:br.value]
    return None

def find_pid():
    for p in psutil.process_iter(["pid","name","memory_info"]):
        try:
            if p.info["name"].lower()!="360game.exe":continue
            if p.memory_info().rss<50*1024*1024:continue
            h=open_proc(p.info["pid"])
            if not h:continue
            addr=0
            class MEMORY_BASIC_INFORMATION(ctypes.Structure):
                _fields_=[("BaseAddress",c_void_p),("AllocationBase",c_void_p),("AllocationProtect",w.DWORD),("RegionSize",ctypes.c_size_t),("State",w.DWORD),("Protect",w.DWORD),("Type",w.DWORD)]
            mbi=MEMORY_BASIC_INFORMATION()
            while addr<0x7FFFFFFF:
                sz=kernel32.VirtualQueryEx(h,c_void_p(addr),byref(mbi),sizeof(mbi))
                if sz==0:break
                base=mbi.BaseAddress or 0
                if mbi.State==0x1000:
                    for cs in range(base,base+mbi.RegionSize,256*1024):
                        buf=create_string_buffer(min(256*1024,base+mbi.RegionSize-cs));br2=ctypes.c_size_t(0)
                        if kernel32.ReadProcessMemory(h,c_void_p(cs),buf,min(256*1024,base+mbi.RegionSize-cs),byref(br2)):
                            if b"playerInfo.swf" in buf.raw[:br2.value]:
                                kernel32.CloseHandle(h);return p.info["pid"]
                addr=base+mbi.RegionSize
            kernel32.CloseHandle(h)
        except:pass
    return None

pid=find_pid()
if not pid:print("FAIL");sys.exit(1)
print(f"PID={pid}")
h=open_proc(pid)

# 读 0x15ab3462 周围 1024 字节完整数据
# HP=29805 @ +0, MP=1387 @ +4
# currentHP=21825 @ -76, ?=95573 @ -80, ?=39 @ -20, ?=6400 @ +20
ADDR=0x15ab3462
ctx=read(h,ADDR-256,1024)

print(f"\n完整数据 @ {hex(ADDR)}:")
print(f"  已知: HP(max)={struct.unpack_from('<I',ctx,256)[0]} @ +0")
print(f"        MP(max)={struct.unpack_from('<I',ctx,260)[0]} @ +4")
print(f"  HP(current)={struct.unpack_from('<I',ctx,256-76)[0]} @ -76")

# Hex dump with annotations
print(f"\n{'offset':>6s}  {'hex':<48s}  {'ascii':<16s}")
print(f"{'':->80}")

annotations = {
    256-80: "large_val",
    256-76: "curHP?" if struct.unpack_from('<I',ctx,256-76)[0]==21825 else "",
    256-20: "?" if struct.unpack_from('<I',ctx,256-20)[0]==39 else "",
    256: "maxHP=29805",
    260: "maxMP=1387",
    276: "6400",
}

for i in range(0,min(len(ctx),800),16):
    ck=ctx[i:i+16];hx=" ".join(f"{bb:02x}" for bb in ck)
    asc="".join(chr(bb) if 32<=bb<127 else "." for bb in ck)
    tags=[]
    for off,label in annotations.items():
        if i<=off<i+16:tags.append(label)
    offset=i-256
    tag_str=" <-- "+", ".join(tags) if tags else ""
    print(f"  {offset:+5d}: {hx:<48s}  {asc}{tag_str}")

# Extract all int32 values
print(f"\n所有int32值:")
for off in range(0,len(ctx)-3,4):
    v=struct.unpack_from("<i",ctx,off)[0]
    if -100000<v<100000000:print(f"  {off-256:+5d}: {v}")

# Also check the 2nd and 3rd addresses for consistency
print(f"\n\n对比三个地址的数据一致性:")
for addr in [0x15ab3462,0x25c2c503,0x263cf048]:
    d=read(h,addr-80,160)
    if d:
        vals=[struct.unpack_from("<I",d,i)[0] for i in range(0,min(140,len(d)),4)]
        print(f"  {hex(addr)}: {vals[:15]}")

# Monitor changes: read HP current vs max 
print(f"\n\n实时监控 HP 变化 (10次, 每秒):")
for i in range(10):
    d=read(h,ADDR-80,160)
    if d:
        vals={}
        for off,name in [(0,"val0"),(4,"curHP?"),(44,"(HP-20)"),(64,"?"),(76,"(HP-4)"),(80,"maxHP=29805"),(84,"maxMP=1387")]:
            v=struct.unpack_from("<I",d,off)[0]
            vals[name]=v
        print(f"  [{time.strftime('%H:%M:%S')}] curHP={vals.get('curHP?','?')} maxHP={vals.get('maxHP=29805','?')} maxMP={vals.get('maxMP=1387','?')}")
    time.sleep(1)

kernel32.CloseHandle(h)
print("\nDone.")
