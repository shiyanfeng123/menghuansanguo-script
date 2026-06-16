import os

long_images = [
    ("serveAssets/images/zhengdian/newlong.bmp", "serveAssets/images/zhengdian/newlong2.bmp"),
    ("serveAssets/images/zhengdian/long-head-1.bmp", "serveAssets/images/zhengdian/long-head-2.bmp"),
    ("serveAssets/images/zhengdian/long-body-1.bmp", "serveAssets/images/zhengdian/long-body-2.bmp"),
    ("serveAssets/images/zhengdian/long-foot-1.bmp", "serveAssets/images/zhengdian/long-foot-2.bmp"),
]

base = os.path.abspath(".")

print("=== 模拟 find_zd_walk_v3 的 backup_images 处理 ===\n")

for pair in long_images:
    print(f"pair type: {type(pair).__name__}")
    print(f"pair value: {pair}")

    # 不加保护（原代码）
    print("\n  不加保护 for p in pair:")
    for p in pair:
        print(f"    p = {p}")

    # 加保护后
    items = pair if isinstance(pair, tuple) else (pair,)
    print("\n  加保护后:")
    for p in items:
        print(f"    p = {p}")

    # 拼接后的路径
    pic_path = "|".join(os.path.join(base, p) for p in items)
    print(f"\n  pic_path = {pic_path[:80]}...")

    # split 后
    pics = pic_path.split("|")
    print(f"  pics count: {len(pics)}")
    for i, p in enumerate(pics):
        exists = os.path.exists(p)
        print(f"  pics[{i}] exists={exists} -> {os.path.basename(p)}")
    print()

print("=== 模拟字符串被当成元组的情况 ===")
bad = "serveAssets/images/zhengdian/long-head-1.bmp"
print(f"bad type: {type(bad).__name__}")
print("不加保护 for p in bad:")
for p in bad:
    print(f"  p = '{p}'")
print("  -> 这就是字符迭代！每个字符会被当成文件名给 get_resource_path")
print("  -> 于是出现 E:\\project\\python\\l, E:\\project\\python\\o, E:\\project\\python\\n, ...")
