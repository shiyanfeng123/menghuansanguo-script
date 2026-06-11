"""测试图片匹配优先方案 - OCR自动截图 + 图片匹配速度验证"""
import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ya_engine import GameEngine, GameWindow
import cv2
import numpy as np


def main():
    engine = GameEngine()
    engine.condition = threading.Condition()
    engine.stopped = False
    engine.overed = False
    engine.scriptName = "魔镜"
    engine.mojingFloor = "mihuan"

    hwnd = engine.find_window("111")
    if not hwnd:
        print("ERROR: 未找到游戏窗口 '111'")
        return
    print(f"找到游戏窗口: hwnd={hwnd}")

    win = GameWindow(hwnd)
    engine.main_win = win
    engine.windows["main"] = win

    text_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "ya_assets", "images", "text")
    print(f"文字图片目录: {text_dir}")
    print(f"目录存在: {os.path.isdir(text_dir)}")

    existing = [f for f in os.listdir(text_dir) if f.endswith(('.bmp', '.png', '.jpg'))] if os.path.isdir(text_dir) else []
    print(f"已有文字图片: {existing}")

    print("\n" + "=" * 60)
    print("第一步: OCR自动截图 (首次会慢，OCR找到后自动保存图片)")
    print("=" * 60)

    test_targets = [
        ("城西", engine.dituLocation, None),
        ("洛阳", engine.dituLocation, None),
    ]

    for text, region, color in test_targets:
        print(f"\n--- 查找 '{text}' ---")
        t0 = time.time()
        result = engine.find_str(text, region, color, 0.5, "main")
        elapsed = (time.time() - t0) * 1000
        if result:
            print(f"  找到! x={result.x}, y={result.y}, conf={result.confidence:.3f}, 耗时{elapsed:.1f}ms")
            img_path = os.path.join(text_dir, text + ".bmp")
            if os.path.isfile(img_path):
                img = cv2.imread(img_path)
                print(f"  自动截图已保存: {img_path} ({img.shape})")
            else:
                print(f"  自动截图未保存 (可能OCR匹配不是精确匹配)")
        else:
            print(f"  未找到, 耗时{elapsed:.1f}ms")

    print("\n" + "=" * 60)
    print("第二步: 验证图片匹配速度 (应该30-50ms)")
    print("=" * 60)

    existing = [f for f in os.listdir(text_dir) if f.endswith(('.bmp', '.png', '.jpg'))] if os.path.isdir(text_dir) else []
    print(f"当前文字图片: {existing}")

    for text, region, color in test_targets:
        img_path = os.path.join(text_dir, text + ".bmp")
        if not os.path.isfile(img_path):
            print(f"\n  [{text}] 无图片模板，跳过")
            continue

        print(f"\n--- 图片匹配 '{text}' ---")
        for i in range(5):
            t0 = time.time()
            result = engine.find_str(text, region, color, 0.5, "main")
            elapsed = (time.time() - t0) * 1000
            status = f"x={result.x},y={result.y},conf={result.confidence:.3f}" if result else "未找到"
            print(f"  第{i+1}轮: {elapsed:.1f}ms - {status}")

    print("\n" + "=" * 60)
    print("第三步: 找图速度对比")
    print("=" * 60)

    print("\n--- find_pic 速度 ---")
    for i in range(3):
        t0 = time.time()
        result = engine.find_pic("ya_assets/images/mojing/mojingshizhe.bmp", engine.gameLocation, 0.9, "main")
        elapsed = (time.time() - t0) * 1000
        status = f"x={result.x},y={result.y}" if result else "未找到"
        print(f"  find_pic 第{i+1}轮: {elapsed:.1f}ms - {status}")

    print("\n--- find_str(图片匹配) 速度 ---")
    for text, region, color in test_targets:
        img_path = os.path.join(text_dir, text + ".bmp")
        if not os.path.isfile(img_path):
            continue
        for i in range(3):
            t0 = time.time()
            result = engine.find_str(text, region, color, 0.5, "main")
            elapsed = (time.time() - t0) * 1000
            status = f"x={result.x},y={result.y}" if result else "未找到"
            print(f"  find_str({text}) 第{i+1}轮: {elapsed:.1f}ms - {status}")

    print("\n测试完成!")


if __name__ == "__main__":
    main()
