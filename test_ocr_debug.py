# -*- coding: utf-8 -*-
"""快速诊断：OCR 能否在当前画面找到指定文字"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ya_engine import GameEngine, GameWindow
from rapidocr_onnxruntime import RapidOCR

engine = GameEngine()
hwnd = engine.find_window("111")
if not hwnd:
    print("找不到窗口111")
    sys.exit(1)

win = GameWindow(hwnd)
engine.main_win = win

# 截 gameBottomLocation
region = (0, 500, 900, 580)
screenshot = win.capture.capture(region)
import cv2
cv2.imwrite("test_debug.png", screenshot)
print(f"截图已保存: test_debug.png ({screenshot.shape[1]}x{screenshot.shape[0]})")

ocr = RapidOCR()
ocr_result, _ = ocr(screenshot)
print(f"OCR 找到 {len(ocr_result) if ocr_result else 0} 个文字:")
if ocr_result:
    for box, txt, conf in ocr_result:
        print(f"  [{conf:.2f}] '{txt}' at ({int(box[0][0])},{int(box[0][1])})")

    targets = ["进入五行", "进入", "五行", "进五行", "五行圣殿"]
    for t in targets:
        found = any(t in txt for _, txt, _ in ocr_result)
        print(f"  '{t}': {'OK 找到了' if found else '没找到'}")
