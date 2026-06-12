"""还原 == != = 模式中不应替换的图片路径"""
FILE = r"c:\Users\syf\Desktop\project\menghuansanguo-script\ya_game_scripts.py"

# 构建反向映射
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

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

reverted = 0
for i, line in enumerate(lines):
    if line.strip().startswith("#"):
        continue
    
    # 还原 == "img_path" 和 != "img_path"
    for img_path, text in sorted(REV_MAP.items(), key=lambda x: -len(x[0])):
        for pat in [f'== "{img_path}"', f'!= "{img_path}"']:
            if pat in line:
                lines[i] = line.replace(pat, pat.replace(img_path, text))
                reverted += 1

with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"还原 {reverted} 处 ==/!= 比较")
