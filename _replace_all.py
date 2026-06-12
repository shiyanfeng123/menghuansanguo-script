"""全量替换 ya_game_scripts.py 中所有中文文字→图片路径"""
FILE = r"c:\Users\syf\Desktop\project\menghuansanguo-script\ya_game_scripts.py"

TEXT_MAP = {}
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
                TEXT_MAP[text] = f"ya_assets/images/text/{img_name}"

EXTRA = {
    "队伍": "ya_assets/images/text/duiwu.bmp",
    "不存在小字": "ya_assets/images/text/bucunzaixiaozi.bmp",
    "挑战小字": "ya_assets/images/text/tiaozhanxiaozi.bmp",
    "点击继续背景": "ya_assets/images/text/dianjijixubeijing.bmp",
    "黑风山寨|山寨本营|山寨内堂": "ya_assets/images/text/heifengshanzhai.bmp|ya_assets/images/text/shanzhaibenying.bmp|ya_assets/images/text/shanzaineitang.bmp",
    "曹操大帐|曹袁战场|鸟巢粮仓|魂殿": "ya_assets/images/text/caocaodazhang.bmp|ya_assets/images/text/caoyuanzhanchang.bmp|ya_assets/images/text/niaochaoliangcang.bmp|ya_assets/images/text/hundian.bmp",
    "镜像地层|遗迹镜像|迷幻境|狱境|炎冰境|印魔殿|北境|西境|南境|东境": "ya_assets/images/text/jingxiangdiceng.bmp|ya_assets/images/text/yijijingxiang.bmp|ya_assets/images/text/mihuanjing.bmp|ya_assets/images/text/yujing.bmp|ya_assets/images/text/yanbingjing.bmp|ya_assets/images/text/yinmodian.bmp|ya_assets/images/text/beijing.bmp|ya_assets/images/text/xijing.bmp|ya_assets/images/text/nanjing.bmp|ya_assets/images/text/dongjing.bmp",
}
TEXT_MAP.update(EXTRA)

print(f"映射: {len(TEXT_MAP)} 条")

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

count = 0
for text, img_path in sorted(TEXT_MAP.items(), key=lambda x: -len(x[0])):
    for quote in ['"', "'"]:
        old = f'{quote}{text}{quote}'
        c = content.count(old)
        if c > 0:
            content = content.replace(old, f'"{img_path}"')
            count += c

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print(f"替换: {count} 处")
