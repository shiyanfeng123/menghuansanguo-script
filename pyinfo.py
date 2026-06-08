import sys, struct
log = r"E:\project\python\pyinfo.txt"
with open(log, "w") as f:
    f.write(f"Version: {sys.version}\n")
    f.write(f"Platform: {sys.platform}\n")
    f.write(f"Maxsize: {sys.maxsize}\n")
    f.write(f"Arch: {struct.calcsize('P') * 8}-bit\n")
    f.write(f"Prefix: {sys.prefix}\n")
    f.write(f"Executable: {sys.executable}\n")
