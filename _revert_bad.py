"""精准还原: 只还原 self.scriptName / self.zhengdianFloor 等逻辑变量的比较和赋值"""
FILE = r"c:\Users\syf\Desktop\project\menghuansanguo-script\ya_game_scripts.py"

REV_MAP = {}
with open(r"c:\Users\syf\Desktop\project\menghuansanguo-script\ya_assets\images\text\文字图片替换清单.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|--") or line.startswith("| 游戏"):
            continue
        if "bmp" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            text = parts[1]
            img_name = parts[2]
            if img_name and text and ".bmp" in img_name and text != "拼音文件名":
                REV_MAP[f"ya_assets/images/text/{img_name}"] = text

# 这些变量的值不应该替换
PROTECT_VARS = [
    "self.scriptName =",
    "self.scriptName ==",
    "self.scriptName !=",
    "self.zhengdianFloor =",
    "self.zhengdianFloor ==",
    "self.zhengdianFloor !=",
    "self.zhanhunFloor =",
    "self.zhanhunFloor ==",
    "self.mojingFloor =",
    "self.mojingFloor ==",
    "self.heifengFloor =",
    "self.heifengFloor ==",
    "self.qingyuan_count =",
    "self.zhanhun_count =",
]

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

reverted = 0
for i, line in enumerate(lines):
    if line.strip().startswith("#"):
        continue
    # 检查这行是否包含保护变量
    if any(v in line for v in PROTECT_VARS):
        for img_path, text in sorted(REV_MAP.items(), key=lambda x: -len(x[0])):
            old = f'"{img_path}"'
            if old in line:
                lines[i] = line.replace(old, f'"{text}"')
                reverted += 1
                line = lines[i]

with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"还原 {reverted} 处")
