# -*- coding: utf-8 -*-
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ya_engine import GameEngine, GameWindow

TEXT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ya_assets", "images", "text")

TEXT_MAP = {}
txt_file = os.path.join(TEXT_DIR, "文字图片替换清单.txt")
if os.path.isfile(txt_file):
    with open(txt_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("|--") or line.startswith("| 游戏"):
                continue
            if ".bmp" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[2].endswith(".bmp"):
                TEXT_MAP[parts[1]] = "ya_assets/images/text/" + parts[2]

MOJING_TEXTS = [
    "城西",
    "镜像地层", "遗迹镜像", "迷幻境", "狱境", "炎冰境", "印魔殿",
    "北境", "西境", "南境", "东境",
    "吃人妖", "狮王魂", "虚", "实",
    "黑无常之魂", "白无常之魂", "冰魔", "炎魔", "炎兄",
    "四神", "魔将",
    "副本魔镜使者",
    "进入", "知道了",
]


def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode('ascii', errors='replace').decode('ascii'))


def main():
    safe_print("=" * 60)
    safe_print("  Mojing Dungeon - Full Diagnostic (Image + OCR)")
    safe_print("=" * 60)

    safe_print("\n[1] TEXT_MAP status:")
    missing_images = []
    existing_images = []
    for text in MOJING_TEXTS:
        mapped = TEXT_MAP.get(text, "<NONE>")
        exists = os.path.isfile(mapped) if mapped != "<NONE>" else False
        if exists:
            existing_images.append((text, mapped))
        else:
            missing_images.append((text, mapped if mapped != "<NONE>" else None))
        status = "OK" if exists else "MISSING"
        safe_print(f"  {text} -> {mapped} [{status}]")
    safe_print(f"  Summary: {len(existing_images)} OK, {len(missing_images)} MISSING")

    safe_print("\n[2] Finding game window '111'...")
    engine = GameEngine()
    hwnd = engine.find_window("111")
    if hwnd:
        safe_print(f"  Found window: hwnd={hwnd}")
    else:
        safe_print("  [FAIL] Window '111' not found!")
        return

    win = GameWindow(hwnd)
    engine.main_win = win
    safe_print(f"  Window size: {win.capture._width}x{win.capture._height}")

    safe_print("\n[3] Full screenshot...")
    import cv2
    screenshot = win.capture.capture()
    if screenshot is None or screenshot.shape[0] < 10 or screenshot.shape[1] < 10:
        safe_print("  [FAIL] Screenshot failed!")
        return

    screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_screenshot.png")
    cv2.imwrite(screenshot_path, screenshot)
    safe_print(f"  Saved: test_screenshot.png ({screenshot.shape[1]}x{screenshot.shape[0]})")

    safe_print("\n[4] Image matching test (existing images only):")
    for text, path in existing_images:
        result = win.matcher.find_pic(path, threshold=0.85)
        if result:
            safe_print(f"  OK {text}: matched! conf={result.confidence:.3f}, pos=({result.x},{result.y})")
        else:
            safe_print(f"  -- {text}: not found in current screen")

    safe_print("\n[5] OCR fallback test (ALL texts):")
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    safe_print("  Initializing OCR engine... (first run is slow)")
    t0 = time.time()
    ocr_result, _ = ocr(screenshot)
    t1 = time.time()
    safe_print(f"  OCR scan completed in {t1-t0:.1f}s, found {len(ocr_result) if ocr_result else 0} text regions")
    if ocr_result:
        safe_print("  OCR detected texts:")
        for item in ocr_result[:30]:
            box, txt, conf = item
            if conf > 0.5:
                safe_print(f"    [{conf:.2f}] '{txt}' at ({int(box[0][0])},{int(box[0][1])})")

        safe_print("\n  Checking target texts:")
        for text in MOJING_TEXTS:
            found = False
            for item in ocr_result:
                _, txt, conf = item
                if conf > 0.5 and text in txt:
                    safe_print(f"  OK {text}: found via OCR! (in '{txt}')")
                    found = True
                    break
            if not found:
                safe_print(f"  -- {text}: not found via OCR")
    else:
        safe_print("  [WARN] OCR returned no results")

    safe_print("\n[6] Testing engine.find_pic with TEXT_MAP routing:")
    for text in ["城西", "狱境", "进入", "黑无常之魂"]:
        img_path = TEXT_MAP.get(text, text)
        result = engine.find_pic(img_path, threshold=0.85)
        if result:
            safe_print(f"  {text}: found at ({result.x},{result.y}) conf={result.confidence:.3f}")
        else:
            safe_print(f"  {text}: not found")

    safe_print("\n" + "=" * 60)
    safe_print("  Diagnostic Complete")
    safe_print("=" * 60)


if __name__ == "__main__":
    main()
