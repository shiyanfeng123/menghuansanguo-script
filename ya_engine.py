"""
游戏自动化引擎 - 替代大漠插件
基于Win32 GDI截图 + OpenCV模板匹配 + RapidOCR文字识别
"""
import os
import sys
import time
import random
import ctypes
import threading
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

import cv2
import numpy as np
import win32gui
import win32ui
import win32con

user32 = ctypes.windll.user32


@dataclass
class MatchResult:
    x: int = 0
    y: int = 0
    confidence: float = 0.0
    width: int = 0
    height: int = 0
    left: int = 0
    top: int = 0


class ScreenCapture:

    PW_RENDERFULLCONTENT = 2

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self._width = 0
        self._height = 0
        self._use_print_window = False
        self._src_dc = None
        self._mem_dc = None
        self._bitmap = None
        self._setup_dc()

    def _setup_dc(self):
        hdc_int = win32gui.GetDC(self.hwnd)
        self._src_dc = win32ui.CreateDCFromHandle(hdc_int)
        self._mem_dc = self._src_dc.CreateCompatibleDC()
        self._recreate_bitmap()

    def _recreate_bitmap(self):
        rect = win32gui.GetClientRect(self.hwnd)
        w = rect[2]
        h = rect[3]
        if w == self._width and h == self._height and self._bitmap is not None:
            return
        self._width = w
        self._height = h
        if self._bitmap is not None:
            self._mem_dc.SelectObject(win32ui.CreateBitmap())
            win32gui.DeleteObject(self._bitmap.GetHandle())
        self._bitmap = win32ui.CreateBitmap()
        self._bitmap.CreateCompatibleBitmap(self._src_dc, w, h)
        self._mem_dc.SelectObject(self._bitmap)

    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        try:
            self._recreate_bitmap()
            if self._width <= 0 or self._height <= 0:
                return np.zeros((1, 1, 3), dtype=np.uint8)
            if self._use_print_window:
                hdc_int = self._mem_dc.GetSafeHdc()
                ctypes.windll.user32.PrintWindow(self.hwnd, hdc_int, self.PW_RENDERFULLCONTENT)
            else:
                self._mem_dc.BitBlt((0, 0), (self._width, self._height), self._src_dc, (0, 0), win32con.SRCCOPY)
        except Exception:
            return np.zeros((1, 1, 3), dtype=np.uint8)
        bmp_info = self._bitmap.GetInfo()
        bmp_str = self._bitmap.GetBitmapBits(True)
        img = np.frombuffer(bmp_str, dtype=np.uint8)
        img = img.reshape((bmp_info['bmHeight'], bmp_info['bmWidth'], 4))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        if not self._use_print_window:
            if img.shape[0] > 0 and img.shape[1] > 0:
                if np.mean(img) < 5:
                    self._use_print_window = True
                    return self.capture(region)
        if region:
            left, top, right, bottom = region
            img = img[top:bottom, left:right]
        return img

    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        img = self.capture(region=(x, y, x + 1, y + 1))
        return (int(img[0, 0, 0]), int(img[0, 0, 1]), int(img[0, 0, 2]))

    def __del__(self):
        try:
            if self._bitmap is not None:
                self._mem_dc.SelectObject(win32ui.CreateBitmap())
                win32gui.DeleteObject(self._bitmap.GetHandle())
            if self._mem_dc is not None:
                self._mem_dc.DeleteDC()
            if self._src_dc is not None:
                hdc_int = self._src_dc.GetSafeHdc()
                win32gui.ReleaseDC(self.hwnd, hdc_int)
        except Exception:
            pass


class ImageMatcher:
    """四层混合图像匹配引擎"""

    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self._template_cache: dict = {}
        self._last_screenshot: Optional[np.ndarray] = None
        self._last_screenshot_time: float = 0.0

    def _get_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """截图缓存，100ms内复用"""
        now = time.time()
        if region is None and self._last_screenshot is not None and (now - self._last_screenshot_time) < 0.1:
            return self._last_screenshot
        img = self.capture.capture(region)
        if region is None:
            self._last_screenshot = img
            self._last_screenshot_time = now
        return img

    def _load_image(self, image: str) -> Optional[np.ndarray]:
        """加载模板图片，支持BMP/PNG/JPG，自动搜索无后缀路径"""
        if image in self._template_cache:
            return self._template_cache[image]
        template = None
        for ext in ('', '.png', '.bmp', '.jpg', '.jpeg'):
            path = image + ext if ext else image
            if os.path.isfile(path):
                template = cv2.imread(path, cv2.IMREAD_COLOR)
                break
        if template is not None:
            self._template_cache[image] = template
        return template

    def find_pic(self, image: str, region: Optional[Tuple[int, int, int, int]] = None,
                 threshold: float = 0.9, find_dir: int = 0) -> Optional[MatchResult]:
        template = self._load_image(image)
        if template is None:
            return None
        screenshot = self._get_screenshot(region)
        if screenshot is None or screenshot.shape[0] < 10 or screenshot.shape[1] < 10:
            return None
        result = self._match_template(template, screenshot, threshold, find_dir)
        if result is None:
            result = self._find_by_multi_scale(template, screenshot, threshold, find_dir)
        if result is None:
            result = self._find_by_feature(template, screenshot, threshold)
        if result is not None and region:
            result.x += region[0]
            result.y += region[1]
            result.left += region[0]
            result.top += region[1]
        return result

    def find_pic_all(self, image: str, region: Optional[Tuple[int, int, int, int]] = None,
                     threshold: float = 0.9) -> List[MatchResult]:
        """多目标匹配+NMS"""
        template = self._load_image(image)
        if template is None:
            return []
        screenshot = self._get_screenshot(region)
        if screenshot is None or screenshot.shape[0] < 10 or screenshot.shape[1] < 10:
            return []
        th, tw = template.shape[:2]
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= threshold)
        boxes = []
        for pt in zip(*locs[::-1]):
            boxes.append([pt[0], pt[1], pt[0] + tw, pt[1] + th, res[pt[1], pt[0]]])
        boxes = self._nms(boxes)
        results = []
        for box in boxes:
            mr = MatchResult(
                x=box[0] + tw // 2, y=box[1] + th // 2,
                confidence=box[4], width=tw, height=th,
                left=box[0], top=box[1]
            )
            if region:
                mr.x += region[0]
                mr.y += region[1]
                mr.left += region[0]
                mr.top += region[1]
            results.append(mr)
        return results

    def find_pic_multi(self, image_paths: list, region: Optional[Tuple[int, int, int, int]] = None,
                       threshold: float = 0.9) -> Optional[MatchResult]:
        """多模板匹配，返回最佳结果"""
        best: Optional[MatchResult] = None
        for path in image_paths:
            result = self.find_pic(path, region, threshold)
            if result and (best is None or result.confidence > best.confidence):
                best = result
        return best

    def find_pic_min_x(self, image: str, region: Optional[Tuple[int, int, int, int]] = None,
                       threshold: float = 0.9) -> Optional[MatchResult]:
        """找最左边的匹配"""
        results = self.find_pic_all(image, region, threshold)
        if not results:
            return None
        return min(results, key=lambda r: r.x)

    def _match_template(self, template: np.ndarray, screenshot: np.ndarray,
                        threshold: float, find_dir: int = 0) -> Optional[MatchResult]:
        th, tw = template.shape[:2]
        sh, sw = screenshot.shape[:2]
        if th > sh or tw > sw:
            return None
        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        if find_dir == 0:
            locs = np.where(res >= threshold)
            if len(locs[0]) == 0:
                return None
            min_y_idx = np.argmin(locs[0])
            max_loc = (int(locs[1][min_y_idx]), int(locs[0][min_y_idx]))
            max_val = res[max_loc[1], max_loc[0]]
        elif find_dir == 1:
            _, max_val, _, _ = cv2.minMaxLoc(res)
            max_loc = self._find_rightmost(res, max_val, threshold)
            if max_loc is None:
                return None
            max_val = res[max_loc[1], max_loc[0]]
        elif find_dir == 2:
            _, max_val, _, _ = cv2.minMaxLoc(res)
            max_loc = self._find_topmost(res, max_val, threshold)
            if max_loc is None:
                return None
            max_val = res[max_loc[1], max_loc[0]]
        else:
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            return MatchResult(
                x=max_loc[0] + tw // 2, y=max_loc[1] + th // 2,
                confidence=float(max_val), width=tw, height=th,
                left=max_loc[0], top=max_loc[1]
            )
        return None

    @staticmethod
    def _find_rightmost(res: np.ndarray, max_val: float, threshold: float) -> Optional[Tuple[int, int]]:
        locs = np.where(res >= threshold)
        if len(locs[0]) == 0:
            return None
        max_x_idx = np.argmax(locs[1])
        return (int(locs[1][max_x_idx]), int(locs[0][max_x_idx]))

    @staticmethod
    def _find_topmost(res: np.ndarray, max_val: float, threshold: float) -> Optional[Tuple[int, int]]:
        locs = np.where(res >= threshold)
        if len(locs[0]) == 0:
            return None
        min_y_idx = np.argmin(locs[0])
        return (int(locs[1][min_y_idx]), int(locs[0][min_y_idx]))

    def _find_by_multi_scale(self, template: np.ndarray, screenshot: np.ndarray,
                             threshold: float, find_dir: int = 0) -> Optional[MatchResult]:
        best: Optional[MatchResult] = None
        th, tw = template.shape[:2]
        sh, sw = screenshot.shape[:2]
        for scale in [0.8, 0.9, 1.1, 1.2]:
            scaled = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            rh, rw = scaled.shape[:2]
            if rh > sh or rw > sw:
                continue
            res = cv2.matchTemplate(screenshot, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold * 0.9 and (best is None or max_val > best.confidence):
                best = MatchResult(
                    x=max_loc[0] + rw // 2, y=max_loc[1] + rh // 2,
                    confidence=max_val, width=rw, height=rh,
                    left=max_loc[0], top=max_loc[1]
                )
        if best is None and th <= sh and tw <= sw:
            edge_screenshot = cv2.Canny(cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY), 50, 150)
            edge_template = cv2.Canny(cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), 50, 150)
            res = cv2.matchTemplate(edge_screenshot, edge_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold * 0.85:
                best = MatchResult(
                    x=max_loc[0] + tw // 2, y=max_loc[1] + th // 2,
                    confidence=max_val, width=tw, height=th,
                    left=max_loc[0], top=max_loc[1]
                )
        return best

    def _find_by_feature(self, template: np.ndarray, screenshot: np.ndarray,
                         threshold: float) -> Optional[MatchResult]:
        """第三层：AKAZE特征匹配"""
        if screenshot is None or screenshot.shape[0] < 10 or screenshot.shape[1] < 10:
            return None
        
        akaze = cv2.AKAZE_create()
        kp1, des1 = akaze.detectAndCompute(template, None)
        kp2, des2 = akaze.detectAndCompute(screenshot, None)
        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return None
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = bf.knnMatch(des1, des2, k=2)
        good = []
        for m_pair in matches:
            if len(m_pair) == 2:
                m, n = m_pair
                if m.distance < 0.7 * n.distance:
                    good.append(m)
        if len(good) < 4:
            return None
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if mask is None:
            return None
        inlier_count = int(mask.sum())
        confidence = inlier_count / max(len(good), 1)
        if confidence < threshold * 0.5:
            return None
        th, tw = template.shape[:2]
        center = np.mean(dst_pts[mask.astype(bool).flatten()], axis=0).flatten()
        return MatchResult(
            x=int(center[0]), y=int(center[1]),
            confidence=confidence, width=tw, height=th,
            left=int(center[0] - tw // 2), top=int(center[1] - th // 2)
        )

    @staticmethod
    def _nms(boxes: list, iou_threshold: float = 0.3) -> list:
        """非极大值抑制"""
        if not boxes:
            return []
        boxes = sorted(boxes, key=lambda b: b[4], reverse=True)
        keep = []
        while boxes:
            best = boxes.pop(0)
            keep.append(best)
            boxes = [b for b in boxes if ImageMatcher._iou(best, b) < iou_threshold]
        return keep

    @staticmethod
    def _iou(a: list, b: list) -> float:
        """计算IoU"""
        x1 = max(a[0], b[0])
        y1 = max(a[1], b[1])
        x2 = min(a[2], b[2])
        y2 = min(a[3], b[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        return inter / max(area_a + area_b - inter, 1e-6)


class TextFinder:
    """三层混合文字查找引擎"""

    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self._ocr_engine = None
        self._text_template_cache: dict = {}
        self._last_screenshot: Optional[np.ndarray] = None
        self._last_screenshot_time: float = 0.0
        self._ocr_cache: Optional[list] = None
        self._ocr_cache_time: float = 0.0
        self._ocr_cache_region = None

    def _get_screenshot(self, region=None) -> np.ndarray:
        now = time.time()
        if self._last_screenshot is not None and (now - self._last_screenshot_time) < 1.0:
            if region is None:
                return self._last_screenshot
            else:
                left, top, right, bottom = region
                return self._last_screenshot[top:bottom, left:right]
        img = self.capture.capture(region if region else None)
        if region is None:
            self._last_screenshot = img
            self._last_screenshot_time = now
        return img

    @property
    def ocr_engine(self):
        """懒加载RapidOCR"""
        if self._ocr_engine is None:
            from rapidocr_onnxruntime import RapidOCR
            self._ocr_engine = RapidOCR()
        return self._ocr_engine

    def find_str(self, text: str, region=None, color: Optional[str] = None,
                 threshold: float = 0.9) -> Optional[MatchResult]:
        full_img = self._get_screenshot(None)
        now = time.time()
        if self._ocr_cache is None or (now - self._ocr_cache_time) > 2.0:
            self._ocr_cache = self._do_ocr(full_img)
            self._ocr_cache_time = now
        all_results = self._ocr_cache
        if not all_results:
            return None
        exact_match = None
        best_contains = None
        best_contains_len = 9999
        fuzzy_match = None
        for item in all_results:
            box, txt, conf = item
            if conf < threshold:
                continue
            pts = np.array(box)
            x_min, y_min = pts.min(axis=0).astype(int)
            x_max, y_max = pts.max(axis=0).astype(int)
            cx = (x_min + x_max) // 2
            cy = (y_min + y_max) // 2
            if region:
                if cx < region[0] or cy < region[1] or cx > region[2] or cy > region[3]:
                    continue
            t = txt.replace(' ', '').strip()
            nt = self._normalize_text(t)
            ntarget = self._normalize_text(text)
            mr = MatchResult(
                x=cx, y=cy, confidence=conf,
                width=x_max - x_min, height=y_max - y_min,
                left=x_min, top=y_min
            )
            if t == text or nt == ntarget:
                exact_match = mr
                break
            if (text in t or ntarget in nt) and len(t) < best_contains_len:
                best_contains = mr
                best_contains_len = len(t)
            if self._text_match(text, txt) and fuzzy_match is None:
                fuzzy_match = mr
        result = exact_match or best_contains or fuzzy_match
        if result and color:
            pixel = full_img[result.y, result.x]
            if not self._check_color_match(pixel, color, 0.7):
                return None
        return result

    def _do_ocr(self, image: np.ndarray) -> list:
        try:
            results, _ = self.ocr_engine(image)
            return results if results else []
        except Exception:
            return []

    def _check_color_match(self, pixel, color_str: str, sim: float) -> bool:
        color_str = color_str.strip()
        if color_str.startswith("b@"):
            color_str = color_str[2:]
        max_diff = int(255 * (1 - sim))
        for group in color_str.split("|"):
            group = group.strip()
            if not group:
                continue
            parts = group.split("-")
            main_hex = parts[0]
            main_color = tuple(int(main_hex[i:i + 2], 16) for i in (4, 2, 0))
            diff = np.abs(pixel.astype(np.int16) - np.array(main_color, dtype=np.int16))
            if np.all(diff <= max_diff):
                return True
        return False

    def find_str_all(self, text: str, region=None, threshold: float = 0.9) -> List[MatchResult]:
        """查找所有匹配文字"""
        screenshot = self._get_screenshot(region)
        results = self._ocr_region(screenshot)
        if not results:
            return []
        matched = []
        for item in results:
            box, txt, conf = item
            if text in txt and conf >= threshold:
                pts = np.array(box)
                x_min, y_min = pts.min(axis=0).astype(int)
                x_max, y_max = pts.max(axis=0).astype(int)
                mr = MatchResult(
                    x=(x_min + x_max) // 2, y=(y_min + y_max) // 2,
                    confidence=conf, width=x_max - x_min, height=y_max - y_min,
                    left=x_min, top=y_min
                )
                if region:
                    mr.x += region[0]
                    mr.y += region[1]
                    mr.left += region[0]
                    mr.top += region[1]
                matched.append(mr)
        return matched

    def _find_by_template(self, text: str, screenshot: np.ndarray, threshold: float) -> Optional[MatchResult]:
        """第一层：渲染文字为图片后模板匹配"""
        tmpl = self._get_text_template(text)
        if tmpl is None:
            return None
        th, tw = tmpl.shape[:2]
        sh, sw = screenshot.shape[:2]
        if th > sh or tw > sw:
            return None
        res = cv2.matchTemplate(screenshot, tmpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if max_val >= threshold:
            return MatchResult(
                x=max_loc[0] + tw // 2, y=max_loc[1] + th // 2,
                confidence=max_val, width=tw, height=th,
                left=max_loc[0], top=max_loc[1]
            )
        return None

    def _find_by_color_and_ocr(self, text: str, color_format: str, screenshot: np.ndarray,
                               threshold: float) -> Optional[MatchResult]:
        mask = self._color_filter(screenshot, color_format)
        filtered = cv2.bitwise_and(screenshot, screenshot, mask=mask)
        results = self._ocr_region(filtered)
        if not results:
            return None
        exact_match = None
        best_contains = None
        best_contains_len = 9999
        fuzzy_match = None
        for item in results:
            box, txt, conf = item
            if conf < threshold:
                continue
            t = txt.replace(' ', '').strip()
            nt = self._normalize_text(t)
            ntarget = self._normalize_text(text)
            pts = np.array(box)
            x_min, y_min = pts.min(axis=0).astype(int)
            x_max, y_max = pts.max(axis=0).astype(int)
            mr = MatchResult(
                x=(x_min + x_max) // 2, y=(y_min + y_max) // 2,
                confidence=conf, width=x_max - x_min, height=y_max - y_min,
                left=x_min, top=y_min
            )
            if t == text or nt == ntarget:
                exact_match = mr
                break
            if (text in t or ntarget in nt) and len(t) < best_contains_len:
                best_contains = mr
                best_contains_len = len(t)
            if self._text_match(text, txt) and fuzzy_match is None:
                fuzzy_match = mr
        return exact_match or best_contains or fuzzy_match

    CHAR_VARIANTS = {
        '镜': '境', '境': '镜',
        '己': '已', '已': '己',
        '战': '戰', '戰': '战',
        '闯': '闖', '闖': '闯',
        '关': '關', '關': '关',
        '闯关': '闖關', '闖關': '闯关',
    }

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        for k, v in cls.CHAR_VARIANTS.items():
            if len(k) == 1:
                text = text.replace(k, v)
        return text

    @staticmethod
    def _text_match(target: str, ocr_text: str) -> bool:
        t = ocr_text.replace(' ', '').strip()
        if t == target:
            return True
        nt = TextFinder._normalize_text(t)
        ntarget = TextFinder._normalize_text(target)
        if nt == ntarget:
            return True
        if target in t or ntarget in nt:
            return True
        if len(target) >= 2 and len(t) <= len(target) * 2:
            common = sum(1 for c in target if c in t)
            if common >= len(target) * 0.6:
                return True
            ncommon = sum(1 for c in ntarget if c in nt)
            if ncommon >= len(ntarget) * 0.6:
                return True
        return False

    def _find_by_ocr(self, text: str, screenshot: np.ndarray, threshold: float) -> Optional[MatchResult]:
        results = self._ocr_region(screenshot)
        if not results:
            return None
        exact_match = None
        best_contains = None
        best_contains_len = 9999
        fuzzy_match = None
        for item in results:
            box, txt, conf = item
            if conf < threshold:
                continue
            t = txt.replace(' ', '').strip()
            nt = self._normalize_text(t)
            ntarget = self._normalize_text(text)
            pts = np.array(box)
            x_min, y_min = pts.min(axis=0).astype(int)
            x_max, y_max = pts.max(axis=0).astype(int)
            mr = MatchResult(
                x=(x_min + x_max) // 2, y=(y_min + y_max) // 2,
                confidence=conf, width=x_max - x_min, height=y_max - y_min,
                left=x_min, top=y_min
            )
            if t == text or nt == ntarget:
                exact_match = mr
                break
            if (text in t or ntarget in nt) and len(t) < best_contains_len:
                best_contains = mr
                best_contains_len = len(t)
            if self._text_match(text, txt) and fuzzy_match is None:
                fuzzy_match = mr
        return exact_match or best_contains or fuzzy_match

    def _color_filter(self, image: np.ndarray, color_format: str) -> np.ndarray:
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        pairs = color_format.split('|')
        for pair in pairs:
            channel_mode = 'bgr'
            if pair.startswith('b@'):
                channel_mode = 'b'
                pair = pair[2:]
            parts = pair.split('-')
            hex_color = parts[0]
            if channel_mode == 'b':
                b_val = int(hex_color[0:2], 16)
                g_val = int(hex_color[2:4], 16)
                r_val = int(hex_color[4:6], 16)
                main_color = (b_val, g_val, r_val)
            else:
                main_color = tuple(int(hex_color[i:i + 2], 16) for i in (4, 2, 0))
            sub_color = (0, 0, 0)
            if len(parts) > 1 and parts[1]:
                hex_sub = parts[1]
                if channel_mode == 'b':
                    sub_color = (int(hex_sub[0:2], 16), int(hex_sub[2:4], 16), int(hex_sub[4:6], 16))
                else:
                    sub_color = tuple(int(hex_sub[i:i + 2], 16) for i in (4, 2, 0))
            if channel_mode == 'b':
                b_ch = image[:, :, 0].astype(np.int16)
                main_match = np.abs(b_ch - main_color[0]) <= 30
                sub_match = np.abs(b_ch - sub_color[0]) <= 30
            else:
                diff = np.abs(image.astype(np.int16) - np.array(main_color, dtype=np.int16))
                main_match = np.all(diff <= 30, axis=2)
                sub_diff = np.abs(image.astype(np.int16) - np.array(sub_color, dtype=np.int16))
                sub_match = np.all(sub_diff <= 30, axis=2)
            mask = cv2.bitwise_or(mask, (main_match & ~sub_match).astype(np.uint8) * 255)
        return mask

    def _ocr_region(self, image: np.ndarray) -> list:
        now = time.time()
        if self._ocr_cache is not None and (now - self._ocr_cache_time) < 0.5:
            return self._ocr_cache
        try:
            results, _ = self.ocr_engine(image)
            self._ocr_cache = results if results else []
            self._ocr_cache_time = now
            return self._ocr_cache
        except Exception:
            return []

    def _get_text_template(self, text: str) -> Optional[np.ndarray]:
        """预渲染文字为图片（带缓存）"""
        if text in self._text_template_cache:
            return self._text_template_cache[text]
        try:
            from PIL import Image, ImageDraw, ImageFont
            font_size = 24
            try:
                font = ImageFont.truetype("msyh.ttc", font_size)
            except Exception:
                font = ImageFont.load_default()
            img = Image.new('RGB', (len(text) * font_size + 10, font_size + 10), (0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((5, 3), text, fill=(255, 255, 255), font=font)
            template = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            self._text_template_cache[text] = template
            return template
        except Exception:
            return None


class ColorFinder:
    """numpy向量化颜色查找"""

    def __init__(self, capture: ScreenCapture):
        self.capture = capture

    def find_color(self, color: str, region: Optional[Tuple[int, int, int, int]] = None,
                   tolerance: int = 10) -> Optional[MatchResult]:
        """查找指定颜色，color为hex如"ffffff" """
        bgr = tuple(int(color[i:i + 2], 16) for i in (4, 2, 0))
        img = self.capture.capture(region)
        diff = np.abs(img.astype(np.int16) - np.array(bgr, dtype=np.int16))
        mask = np.all(diff <= tolerance, axis=2)
        coords = np.where(mask)
        if len(coords[0]) == 0:
            return None
        y, x = coords[0][0], coords[1][0]
        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0
        return MatchResult(x=x + offset_x, y=y + offset_y, confidence=1.0)

    def get_color(self, x: int, y: int) -> str:
        """获取指定位置hex颜色"""
        b, g, r = self.capture.get_pixel_color(x, y)
        return f"{r:02x}{g:02x}{b:02x}"


class InputController:
    """后台键鼠控制 - PostMessage/SendMessage实现"""

    VK_MAP = {
        'enter': 0x0D, 'esc': 0x1B, 'tab': 0x09, 'space': 0x20,
        'backspace': 0x08, 'delete': 0x2E, 'up': 0x26, 'down': 0x28,
        'left': 0x25, 'right': 0x27, 'home': 0x24, 'end': 0x23,
        'pageup': 0x21, 'pagedown': 0x22, 'f1': 0x70, 'f2': 0x71,
        'f3': 0x72, 'f4': 0x73, 'f5': 0x74, 'f6': 0x75,
        'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
        'f11': 0x7A, 'f12': 0x7B, 'shift': 0x10, 'ctrl': 0x11,
        'alt': 0x12, '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33,
        '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38,
        '9': 0x39, 'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44,
        'e': 0x45, 'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49,
        'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E,
        'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53,
        't': 0x54, 'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58,
        'y': 0x59, 'z': 0x5A,
    }

    WM_MOUSEMOVE = 0x0200
    WM_LBUTTONDOWN = 0x0201
    WM_LBUTTONUP = 0x0202
    WM_RBUTTONDOWN = 0x0204
    WM_RBUTTONUP = 0x0205
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    WM_CHAR = 0x0102
    WM_MOUSEWHEEL = 0x020A

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self._use_send = True

    @staticmethod
    def _make_lparam(x: int, y: int) -> int:
        return (y << 16) | (x & 0xFFFF)

    def _post_or_send(self, msg, wparam, lparam):
        wp = ctypes.c_ulong(wparam)
        lp = ctypes.c_ulong(lparam)
        if self._use_send:
            user32.SendMessageW(self.hwnd, msg, wp, lp)
        else:
            user32.PostMessageW(self.hwnd, msg, wp, lp)

    def move_to(self, x: int, y: int):
        self._post_or_send(self.WM_MOUSEMOVE, 0, self._make_lparam(x, y))

    def left_click(self, x: Optional[int] = None, y: Optional[int] = None):
        if x is not None and y is not None:
            self.move_to(x, y)
            time.sleep(0.02)
        lp = self._make_lparam(x or 0, y or 0)
        self._post_or_send(self.WM_LBUTTONDOWN, 1, lp)
        time.sleep(0.05)
        self._post_or_send(self.WM_LBUTTONUP, 0, lp)

    def left_down(self, x: int, y: int):
        self._post_or_send(self.WM_LBUTTONDOWN, 1, self._make_lparam(x, y))

    def left_up(self, x: int, y: int):
        self._post_or_send(self.WM_LBUTTONUP, 0, self._make_lparam(x, y))

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None):
        if x is not None and y is not None:
            self.move_to(x, y)
            time.sleep(0.02)
        lp = self._make_lparam(x or 0, y or 0)
        self._post_or_send(self.WM_RBUTTONDOWN, 2, lp)
        time.sleep(0.05)
        self._post_or_send(self.WM_RBUTTONUP, 0, lp)

    def scroll_up(self, x: int, y: int):
        wp = 120 << 16
        self._post_or_send(self.WM_MOUSEWHEEL, wp, self._make_lparam(x, y))

    def scroll_down(self, x: int, y: int):
        wp = ctypes.c_int(-120 << 16).value
        self._post_or_send(self.WM_MOUSEWHEEL, wp, self._make_lparam(x, y))

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """拖拽"""
        self.move_to(start_x, start_y)
        time.sleep(0.05)
        self.left_down(start_x, start_y)
        time.sleep(0.1)
        steps = 10
        for i in range(1, steps + 1):
            nx = int(start_x + (end_x - start_x) * i / steps)
            ny = int(start_y + (end_y - start_y) * i / steps)
            self.move_to(nx, ny)
            time.sleep(0.02)
        self.left_up(end_x, end_y)

    def click_with_offset(self, x: int, y: int, radius: int = 3):
        """随机偏移点击（防检测）"""
        ox = random.randint(-radius, radius)
        oy = random.randint(-radius, radius)
        self.left_click(x + ox, y + oy)

    def _get_vk(self, key: str) -> int:
        """获取虚拟键码"""
        key_lower = key.lower()
        if key_lower in self.VK_MAP:
            return self.VK_MAP[key_lower]
        if len(key) == 1:
            return ord(key.upper())
        return 0

    def _make_key_lparam(self, vk: int, is_down: bool = True) -> int:
        scan_code = user32.MapVirtualKeyW(vk, 0) & 0xFF
        repeat_count = 1
        extended_keys = {0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E}
        for i in range(0x70, 0x88):
            extended_keys.add(i)
        extended = 1 if vk in extended_keys else 0
        if is_down:
            return ctypes.c_int((repeat_count & 0xFFFF) | (scan_code << 16) | (extended << 24)).value
        else:
            val = (repeat_count & 0xFFFF) | (scan_code << 16) | (extended << 24) | (1 << 30) | (1 << 31)
            return ctypes.c_int(val & 0xFFFFFFFF).value

    def key_press(self, key: str):
        vk = self._get_vk(key)
        if vk:
            lp_down = self._make_key_lparam(vk, True)
            lp_up = self._make_key_lparam(vk, False)
            self._post_or_send(self.WM_KEYDOWN, vk, lp_down)
            time.sleep(0.05)
            self._post_or_send(self.WM_KEYUP, vk, lp_up)

    def key_down(self, key: str):
        vk = self._get_vk(key)
        if vk:
            lp = self._make_key_lparam(vk, True)
            self._post_or_send(self.WM_KEYDOWN, vk, lp)

    def key_up(self, key: str):
        vk = self._get_vk(key)
        if vk:
            lp = self._make_key_lparam(vk, False)
            self._post_or_send(self.WM_KEYUP, vk, lp)

    def type_text(self, text: str):
        for ch in text:
            self._post_or_send(self.WM_CHAR, ord(ch), 0)
            time.sleep(0.02)


class GameWindow:
    """单游戏窗口封装"""

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        self.capture = ScreenCapture(hwnd)
        self.matcher = ImageMatcher(self.capture)
        self.text_finder = TextFinder(self.capture)
        self.color_finder = ColorFinder(self.capture)
        self.input = InputController(hwnd)

    def find_pic(self, image: str, region=None, threshold: float = 0.9) -> Optional[MatchResult]:
        return self.matcher.find_pic(image, region, threshold)

    def click_image(self, image: str, region=None, threshold: float = 0.9) -> bool:
        result = self.find_pic(image, region, threshold)
        if result:
            self.input.left_click(result.x, result.y)
            return True
        return False

    def find_str(self, text: str, region=None, color: Optional[str] = None,
                 threshold: float = 0.9) -> Optional[MatchResult]:
        return self.text_finder.find_str(text, region, color, threshold)

    def screenshot(self, region=None) -> np.ndarray:
        return self.capture.capture(region)


class GameEngine:
    """主引擎 - 统一调度所有功能，逻辑对齐serveScript.py"""

    DEFAULT_COLOR_FORMAT = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"

    def __init__(self):
        self.main_win: Optional[GameWindow] = None
        self.team1_win: Optional[GameWindow] = None
        self.team2_win: Optional[GameWindow] = None
        self.windows: dict = {}
        self.stopped: bool = False
        self.overed: bool = False
        self.condition = threading.Condition()
        self._resource_path = self._detect_resource_path()
        self.locationX: int = 0
        self.locationY: int = 0
        self.locationWidth: int = 900
        self.locationHeight: int = 590
        self.confidenceNum: float = 0.9
        self.color_format: str = self.DEFAULT_COLOR_FORMAT
        self.scriptName: str = ""
        self.zhengdianFloor: str = ""
        self.zhengdianFb: list = ["官渡", "魔镜", "黑风", "战魂+红+整点", "战魂+红+魔镜+整点"]
        self.zhengdian_flag: bool = False
        self.hundianFlag: bool = False
        self.addBloudFlag: bool = False
        self.clickFlag: bool = False
        self.clickBTime: float = 0
        self.clickBX: int = 0
        self.clickBy: int = 0
        self.BisClick: bool = False
        self.click_delay: float = 0.5
        self.gameLocation: tuple = (0, 0, 900, 590)
        self.gameBottomLocation: tuple = (0, 177, 900, 590)
        self.gameLeftLocation: tuple = (0, 177, 630, 590)
        self.dituLocation: tuple = (720, 0, 900, 118)
        self.talkLocation: tuple = (0, 295, 450, 590)
        self.downTalkLocation = None
        self.guanDuCount: int = 0
        self.hasZhengDianCount: int = 0
        self.daZhengDianCount: int = 0
        self.heifengCount: int = 0
        self.qingyuanCount: int = 0
        self.zhanhunCount: int = 0
        self.lianyuCount: int = 0
        self.shihunCount: int = 0
        self.mojingFloor: str = ""
        self.heifengFloor: str = ""
        self.zhanhunFloor: str = ""
        self.zhanhunFloorNew: str = ""
        self.shihunFloor: str = ""
        self.afterZreo: str = ""
        self.richangSelection: list = []
        self.line: str = ""
        self.teammate1_pos: str = ""
        self.teammate2_pos: str = ""
        self.team_leader_pos: str = ""
        self.guajiLocation = None

    def init_regions(self):
        lx = self.locationX
        ly = self.locationY
        lw = self.locationWidth
        lh = self.locationHeight
        self.gameLocation = (lx, ly, lw, lh)
        self.gameBottomLocation = (lx, int(ly + lh * 0.3), lw, lh)
        self.gameLeftLocation = (lx, int(ly + lh * 0.3), int(lx + lw * 0.7), lh)
        rightTopX = lx + int(lw * 0.8)
        rightTopY = ly
        rightTopW = lw + lx
        rightTopH = ly + int(lh * 0.2)
        self.dituLocation = (rightTopX, rightTopY, rightTopW, rightTopH)
        self.talkLocation = (lx, int(ly + lh * 0.5), int(lw * 0.5 + lx), lh)

    @staticmethod
    def _detect_resource_path() -> str:
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    def get_resource_path(self, relative_path: str) -> str:
        return os.path.join(self._resource_path, relative_path)

    def find_window(self, title: str) -> Optional[int]:
        parent = win32gui.FindWindow(None, title)
        if not parent:
            return None
        child_hwnd = [None]

        def enum_callback(hwnd, _):
            cls = win32gui.GetClassName(hwnd)
            if cls == 'NativeWindowClass':
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                if left > 0 and right < 3000 and bottom < 2000:
                    child_hwnd[0] = hwnd
                    return False
            return True

        try:
            win32gui.EnumChildWindows(parent, enum_callback, None)
        except Exception:
            pass
        return child_hwnd[0] if child_hwnd[0] else parent

    def find_team_window(self, role: str, name: str) -> Optional[GameWindow]:
        hwnd = self.find_window(name)
        if hwnd:
            win = GameWindow(hwnd)
            if role == "team1":
                self.team1_win = win
            elif role == "team2":
                self.team2_win = win
            return win
        return None

    def refresh_window(self, role: str):
        win = self._get_window(role)
        if win:
            win.capture = ScreenCapture(win.hwnd)
            win.matcher = ImageMatcher(win.capture)
            win.text_finder = TextFinder(win.capture)
            win.color_finder = ColorFinder(win.capture)

    def _get_window(self, role: str = "main") -> Optional[GameWindow]:
        if role == "main":
            return self.main_win
        elif role == "team1":
            return self.team1_win
        elif role == "team2":
            return self.team2_win
        return self.main_win

    def screenshot(self, role: str = "main", region=None) -> Optional[np.ndarray]:
        win = self._get_window(role)
        if win:
            return win.screenshot(region)
        return None

    def find_pic(self, image: str, region=None, threshold: float = 0.9,
                 role: str = "main", find_dir: int = 0) -> Optional[MatchResult]:
        if "|" in image:
            for img in image.split("|"):
                img = img.strip()
                if not img:
                    continue
                result = self.find_pic(img, region, threshold, role, find_dir)
                if result:
                    return result
            return None
        win = self._get_window(role)
        if win:
            resolved = self._resolve_image_path(image)
            result = win.matcher.find_pic(resolved, region, threshold, find_dir)
            return result
        return None

    def find_pic_all(self, image: str, region=None, threshold: float = 0.9,
                     role: str = "main") -> List[MatchResult]:
        if "|" in image:
            all_results = []
            for img in image.split("|"):
                img = img.strip()
                if not img:
                    continue
                all_results.extend(self.find_pic_all(img, region, threshold, role))
            return all_results
        win = self._get_window(role)
        if win:
            resolved = self._resolve_image_path(image)
            return win.matcher.find_pic_all(resolved, region, threshold)
        return []

    def find_pic_min_x(self, image: str, region=None, threshold: float = 0.9,
                       role: str = "main") -> Optional[MatchResult]:
        if "|" in image:
            best = None
            for img in image.split("|"):
                img = img.strip()
                if not img:
                    continue
                result = self.find_pic_min_x(img, region, threshold, role)
                if result and (best is None or result.x < best.x):
                    best = result
            return best
        win = self._get_window(role)
        if win:
            resolved = self._resolve_image_path(image)
            return win.matcher.find_pic_min_x(resolved, region, threshold)
        return None

    def find_color(self, color: str, region=None, tolerance: int = 10,
                   role: str = "main") -> Optional[MatchResult]:
        win = self._get_window(role)
        if win:
            return win.color_finder.find_color(color, region, tolerance)
        return None

    def _resolve_image_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        abs_path = self.get_resource_path(path)
        if os.path.isfile(abs_path):
            return abs_path
        return path

    def _is_image_target(self, target: str) -> bool:
        exts = ('.png', '.bmp', '.jpg', '.jpeg')
        if any(target.lower().endswith(e) for e in exts):
            return True
        if os.path.sep in target or '/' in target:
            for ext in exts:
                if os.path.isfile(self._resolve_image_path(target + ext)):
                    return True
            if os.path.isfile(self._resolve_image_path(target)):
                return True
        return False

    def _cmp_color(self, x: int, y: int, color_str: str, sim: float = 0.7,
                   role: str = "main") -> bool:
        win = self._get_window(role)
        if not win:
            return False
        try:
            screenshot = win.capture.capture()
            if screenshot is None:
                return False
            h, w = screenshot.shape[:2]
            if y < 0 or y >= h or x < 0 or x >= w:
                return False
            pixel = screenshot[y, x]
            max_diff = int(255 * (1 - sim))
            color_str = color_str.strip()
            if color_str.startswith("b@"):
                color_str = color_str[2:]
            for group in color_str.split("|"):
                group = group.strip()
                if not group:
                    continue
                parts = group.split("-")
                main_color_hex = parts[0]
                main_color = tuple(int(main_color_hex[i:i + 2], 16) for i in (4, 2, 0))
                diff = np.abs(pixel.astype(np.int16) - np.array(main_color, dtype=np.int16))
                if not np.all(diff <= max_diff):
                    continue
                if len(parts) > 1 and parts[1] != "000000":
                    sub_color = tuple(int(parts[1][i:i + 2], 16) for i in (4, 2, 0))
                    sub_diff = np.abs(pixel.astype(np.int16) - np.array(sub_color, dtype=np.int16))
                    if np.all(sub_diff <= max_diff):
                        continue
                return True
            return False
        except Exception:
            return False

    def find_pic_or_str(self, target: str, region=None, find_dir: int = 0,
                        role: str = "main", threshold: float = None) -> Optional[MatchResult]:
        if self.overed:
            return None
        if threshold is None:
            threshold = self.confidenceNum
        if "|" in target:
            for t in target.split("|"):
                t = t.strip()
                if not t:
                    continue
                result = self.find_pic_or_str(t, region, find_dir, role, threshold)
                if result:
                    return result
            return None
        return self.find_pic(target, region, threshold, role, find_dir)

    def find(self, target: str, region=None, threshold: float = 0.9,
             color: Optional[str] = None, role: str = "main") -> Optional[MatchResult]:
        if "|" in target:
            for t in target.split("|"):
                t = t.strip()
                if not t:
                    continue
                result = self.find(t, region, threshold, color, role)
                if result:
                    return result
            return None
        return self.find_pic(target, region, threshold, role)

    def click(self, x: int, y: int, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.click_with_offset(x, y)

    def click_image(self, image: str, region=None, threshold: float = 0.9,
                    role: str = "main") -> bool:
        if self.overed:
            return False
        image_locations = self.find_pic_or_str(image, region, 0, role, threshold)
        if image_locations:
            with self.condition:
                if self.stopped:
                    self.condition.wait()
            win = self._get_window(role)
            if win:
                win.input.move_to(image_locations.x, image_locations.y)
                time.sleep(0.001)
                win.input.left_click(image_locations.x, image_locations.y)
            return True
        return False

    def click_image_with_min_x(self, image_path: str, image_region=None,
                               image_path2: str = "", role: str = "main") -> bool:
        if self.overed:
            return False
        is_image = self._is_image_target(image_path)
        target = None
        if not is_image:
            target = self.find_pic(image_path, image_region, self.confidenceNum, role)
            if target:
                target.x = target.x + random.randint(10, 32)
                target.y = target.y + 5
        else:
            target = self.find_pic(image_path, image_region, self.confidenceNum, role)
        if not target:
            return False
        yjian = random.randint(35, 55) if not is_image else 0
        win = self._get_window(role)
        if not win:
            return False
        if "zdzd" in image_path2:
            win.input.move_to(target.x, int(target.y - yjian))
            time.sleep(0.001)
            win.input.left_click(target.x, int(target.y - yjian))
            time.sleep(self.click_delay)
            win.input.move_to(1, 1)
        else:
            win.input.move_to(target.x, target.y)
            time.sleep(0.001)
            win.input.left_click(target.x, target.y)
            time.sleep(0.2)
            win.input.move_to(1, 1)
        self.clickBTime = time.time()
        self.clickBX = target.x
        self.clickBy = target.y
        return True

    def fing_fei_in_image_or_str(self, base: str, base_region: tuple,
                                 fei_region: tuple, fei_image: str,
                                 role: str = "main") -> Optional[MatchResult]:
        if self.overed:
            return None
        base_pos = self.find_pic_or_str(base, base_region, 0, role)
        if not base_pos:
            return None
        x, y, w, h = fei_region
        search_region = (
            int(base_pos.x - x),
            int(base_pos.y - y),
            int(base_pos.x + w),
            int(base_pos.y + h),
        )
        targets = fei_image.split("|")
        best: Optional[MatchResult] = None
        for t in targets:
            if not t:
                continue
            result = self.find_pic(t, search_region, 0.6, role)
            if result and (best is None or result.confidence > best.confidence):
                best = result
        return best

    def move_to(self, x: int, y: int, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.move_to(x, y)

    def left_click(self, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.left_click()

    def left_double_click(self, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.left_click()
            time.sleep(0.05)
            win.input.left_click()

    def key_press(self, key: str, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.key_press(key)

    def key_down(self, key: str, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.key_down(key)

    def key_up(self, key: str, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.key_up(key)

    def scroll_up(self, x: int = 0, y: int = 0, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.scroll_up(x, y)

    def scroll_down(self, x: int = 0, y: int = 0, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.scroll_down(x, y)

    def type_text(self, text: str, role: str = "main"):
        win = self._get_window(role)
        if win:
            win.input.type_text(text)

    def check_stop(self) -> bool:
        with self.condition:
            if self.overed:
                return True
            while self.stopped:
                self.condition.wait()
                if self.overed:
                    return True
        return self.overed

    def check_stop_internal(self) -> bool:
        return self.overed or self.stopped

    def print_and_speak(self, text: str):
        print(text)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    def waitFor(self, target: str, region=None, timeout: float = None,
                color: Optional[str] = None, role: str = "main"):
        if self.overed:
            return None
        if region is None:
            region = self.gameLocation
        start_time = time.time()
        while True:
            if self.check_stop():
                return None
            if color and not self._is_image_target(target):
                result = self.find_pic_or_str(target, region, 0, role)
            else:
                result = self.find_pic_or_str(target, region, 0, role)
            if result:
                return result
            if timeout is not None and time.time() - start_time > timeout:
                return None
            time.sleep(0.1)

    def waitForTwo(self, target1: str, target2: str, region=None, region2=None,
                   timeout: float = None, role: str = "main",
                   find_dir: int = 1) -> Optional[str]:
        if self.overed:
            return False
        if region is None:
            region = self.gameLocation
        if region2 is None:
            region2 = region
        start_time = time.time()
        while True:
            if self.check_stop():
                return False
            if self.find_pic_or_str(target1, region, find_dir, role):
                return "first"
            if self.find_pic_or_str(target2, region2, find_dir, role):
                return "second"
            if timeout is not None and time.time() - start_time > timeout:
                return False
            time.sleep(0.2)

    def waitForAAndClickB(self, target_a: str, target_b: str,
                          region_a=None, region_b=None,
                          target_a2: str = None, role: str = "main"):
        if self.overed:
            return
        if region_a is None:
            region_a = self.dituLocation
        if region_b is None:
            region_b = self.gameLocation
        while not self.find_pic_or_str(target_a, region_a, 0, role):
            if self.check_stop():
                return
            clickB = self.click_image(target_b, region_b, self.confidenceNum, role)
            if clickB:
                time.sleep(0.1)
                if target_a2 and self.find_pic_or_str(target_a2, self.gameBottomLocation, 0, role):
                    break
                time.sleep(0.2)
            time.sleep(0.1)
        win = self._get_window(role)
        if win:
            win.input.move_to(804, 74)
            time.sleep(0.001)
            win.input.left_click(804, 74)

    def waitForAAndClickB1(self, find_text: str, image_path_b: str,
                           find_region=None, image_region_b=None,
                           role: str = "main"):
        if self.overed:
            return
        if find_region is None:
            find_region = self.dituLocation
        if image_region_b is None:
            image_region_b = self.gameLocation
        while True:
            if self.check_stop():
                return
            clickB = self.click_image(image_path_b, image_region_b, self.confidenceNum, role)
            if clickB:
                break
            time.sleep(0.2)

    def findAndClickPic(self, area: str, target1: str, target2: str = "",
                        battle1: str = "", battle2: str = "",
                        assist: str = "", move_key: str = "",
                        move_key2: str = "", move_key2_time: float = 0.6,
                        role: str = "main"):
        if self.overed:
            return
        EIsDown = False
        self.BisClick = False
        self.clickBTime = 0
        self.clickBX = 0
        self.clickBy = 0

        with self.condition:
            if self.stopped:
                self.condition.wait()

        aIsOk = self.waitFor(area, self.dituLocation, role=role)
        if not aIsOk:
            return

        if time.localtime().tm_min == 58 and self.scriptName != "49整点" and not self.zhengdian_flag:
            if self.scriptName in ["官渡"]:
                time.sleep(1)
                self.clearBag(role)
                time.sleep(1)
            if self.scriptName in self.zhengdianFb:
                self.zhengdian_flag = True
                self.outScript(area)
                time.sleep(2)
                from ya_scripts.zhengdian import zhengdian
                zhengdian(self)
                return

        if self.overed:
            return

        if move_key2:
            self.key_down(move_key2, role)
            time.sleep(move_key2_time)
            self.key_up(move_key2, role)

        startTime = time.time()
        b2_region = self.gameLocation
        c2_region = self.gameBottomLocation
        find_dir = 2 if move_key == "left" else 0

        while not self.find_pic_or_str(battle1, c2_region, find_dir, role):
            if self.overed:
                return
            if self.check_stop():
                return

            if time.time() - startTime > 10 and self.hundianFlag:
                self.click_image("ya_assets/images/guandu/hundianchuansongmen.bmp", self.dituLocation, self.confidenceNum, role)

            if time.time() - startTime > 22:
                if self.scriptName in ("官渡", "魔镜", "黑风"):
                    print(f"超过22s没找到目标,重新进入{self.scriptName}")
                    self.outScript()
                    time.sleep(1)
                    from ya_scripts import SCRIPT_REGISTRY
                    fn = SCRIPT_REGISTRY.get(self.scriptName, (None,))[0]
                    if fn:
                        fn(self)
                    return

            if (assist and self.clickBTime == 0
                    and not self.find_pic_or_str(target1, b2_region, 0, role)
                    and not self.find_pic_or_str(target2, b2_region, 0, role)):
                if self.check_stop():
                    return
                if "," in assist:
                    d_pos = assist.split(",")
                    dx = (1000 - int(float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
                    dy = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
                    self.click(int(dx + self.locationX), int(dy + self.locationY), role)
                    time.sleep(0.6)
                else:
                    self.click_image(assist, b2_region, self.confidenceNum, role)
                    time.sleep(0.6)

            if self.find_pic_or_str(battle1, c2_region, find_dir, role):
                break

            while (move_key and not EIsDown
                   and not self.find_pic_or_str(target1, b2_region, find_dir, role)
                   and not self.find_pic_or_str(target2, b2_region, find_dir, role)):
                if self.check_stop():
                    return
                self.key_down(move_key, role)
                B1Location = self.waitForTwo(target1, target2, b2_region, timeout=10.0, role=role)
                if B1Location:
                    EIsDown = True
                    self.key_up(move_key, role)
                self.click_image_with_min_x(target1, b2_region, battle1, role)
                self.click_image_with_min_x(target2, b2_region, battle1, role)
                if self.find_pic_or_str(battle1, c2_region, find_dir, role):
                    EIsDown = True
                    time.sleep(0.1)
                    self.key_up(move_key, role)
                    break

            if self.check_stop():
                return

            self.BisClick = self.click_image_with_min_x(target1, b2_region, battle1, role)
            if self.find_pic_or_str(battle1, c2_region, find_dir, role):
                break
            self.BisClick = self.click_image_with_min_x(target2, b2_region, battle1, role)

            if self.clickBTime > 0 and time.time() - self.clickBTime > 4:
                win = self._get_window(role)
                if win:
                    win.input.move_to(self.clickBX, self.clickBy)
                    time.sleep(0.001)
                    win.input.left_click(self.clickBX, self.clickBy)
                    self.clickBTime = time.time()

    def _wait_battle_end(self, battle1: str = "", battle2: str = "",
                         role: str = "main", timeout: float = 120.0):
        battle_imgs = []
        if battle1:
            battle_imgs.extend(battle1.split("|"))
        if battle2:
            battle_imgs.extend(battle2.split("|"))
        if not battle_imgs:
            battle_imgs = ["ya_assets/images/zdzd.bmp", "ya_assets/images/zdzd111.bmp"]
        found = False
        start = time.time()
        while time.time() - start < 10:
            if self.check_stop():
                return
            for img in battle_imgs:
                if img and self.find_pic(img, role=role):
                    found = True
                    break
            if found:
                break
            time.sleep(0.5)
        if found:
            while time.time() - start < timeout:
                if self.check_stop():
                    return
                still_fighting = False
                for img in battle_imgs:
                    if img and self.find_pic(img, role=role):
                        still_fighting = True
                        break
                if not still_fighting:
                    return
                time.sleep(1.0)

    def clickDitu(self, xy: str, find_image: str, find_region,
                  break_image: str, role: str = "main"):
        with self.condition:
            if self.stopped:
                self.condition.wait()
        d_pos = xy.split(",")
        dx = (1000 - int(float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
        dy = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
        win = self._get_window(role)
        if win:
            win.input.click_with_offset(int(dx), int(dy))
        time.sleep(0.3)
        while not self.find_pic_or_str(break_image, self.gameBottomLocation, 0, role):
            self.waitFor(find_image, find_region, role=role)
            isFind = self.find_pic_or_str(find_image, find_region, 0, role)
            if isFind:
                if win:
                    win.input.move_to(isFind.x, isFind.y)
                    time.sleep(0.001)
                    win.input.left_click(isFind.x, isFind.y)
            time.sleep(0.5)

    def feiFb(self, fb_image: str, is_elite: bool = True, role: str = "main"):
        if self.overed:
            return
        outFbLocation = self.find_pic_or_str(
            "ya_assets/images/outFb.bmp|ya_assets/images/outFb1.bmp", self.gameLocation, 0, role
        )
        if outFbLocation:
            win = self._get_window(role)
            if win:
                win.input.move_to(outFbLocation.x, outFbLocation.y)
                time.sleep(0.001)
                win.input.left_click(outFbLocation.x, outFbLocation.y)
                time.sleep(0.001)
                win.input.left_click(outFbLocation.x, outFbLocation.y)
            time.sleep(2)

        time.sleep(1.5)
        begin_time = time.time()
        while not self.find_pic_or_str(
            "ya_assets/images/jingyin.bmp|ya_assets/images/jingyin1.bmp", self.gameLocation, 0, role
        ):
            if time.time() - begin_time > 600:
                break
            if self.check_stop():
                return
            self.key_press("z", role)
            time.sleep(0.5)

        if is_elite:
            is_click_fb = self.click_image(
                "ya_assets/images/jingyin.bmp|ya_assets/images/jingyin1.bmp",
                self.gameLocation, 0.7, role
            )
            if not is_click_fb:
                return self.feiFb(fb_image, is_elite, role)
            findPerTime = time.time()
            fei_pos = None
            while True:
                if time.time() - findPerTime > 10:
                    self.key_press("z", role)
                    return False
                if self.check_stop():
                    return
                fei_pos = self.fing_fei_in_image_or_str(
                    fb_image, self.gameLocation,
                    (0, 5, 120, 20),
                    "ya_assets/images/fubenfei.bmp|ya_assets/images/fubenfei1.bmp|ya_assets/images/fubenfei2.bmp",
                    role
                )
                if fei_pos:
                    break
            if fei_pos:
                while True:
                    if not self.find_pic_or_str(fb_image, self.gameLocation, 0, role):
                        break
                    win = self._get_window(role)
                    if win:
                        win.input.move_to(fei_pos.x, fei_pos.y)
                        time.sleep(0.001)
                        win.input.left_click(fei_pos.x, fei_pos.y)
                    time.sleep(1)
        else:
            self.click_image(
                "ya_assets/images/putong.bmp|ya_assets/images/putong1.bmp",
                self.gameLocation, 0.7, role
            )
            time.sleep(0.5)
            win = self._get_window(role)
            scroll_x = self.locationX + self.locationWidth // 2
            scroll_y = self.locationY + self.locationHeight // 3
            if win:
                win.input.move_to(scroll_x, scroll_y)
            while not self.find_pic(fb_image, self.gameLocation, self.confidenceNum, role):
                if self.check_stop():
                    return
                for _ in range(4):
                    self.scroll_down(scroll_x, scroll_y, role)
                    time.sleep(0.06)
                time.sleep(0.4)
            time.sleep(0.5)
            if win:
                win.input.move_to(scroll_x, scroll_y)
            for _ in range(4):
                self.scroll_down(scroll_x, scroll_y, role)
                time.sleep(0.06)
            time.sleep(1)
            findPerTime = time.time()
            fei_pos = None
            while True:
                if self.check_stop():
                    return
                if time.time() - findPerTime > 10:
                    return
                old_conf = self.confidenceNum
                self.confidenceNum = 0.6
                fei_pos = self.fing_fei_in_image_or_str(
                    fb_image, self.gameLocation,
                    (0, 5, 120, 20),
                    "ya_assets/images/fubenfei.bmp|ya_assets/images/fubenfei1.bmp|ya_assets/images/fubenfei2.bmp",
                    role
                )
                self.confidenceNum = old_conf
                if fei_pos:
                    break
            if fei_pos:
                while True:
                    if not self.find_pic_or_str(fb_image, self.gameLocation, 0, role):
                        break
                    if win:
                        win.input.move_to(fei_pos.x, fei_pos.y)
                        time.sleep(0.001)
                        win.input.left_click(fei_pos.x, fei_pos.y)
                    time.sleep(1)
        return True

    def feiZhengDian(self, fei_image: str, base_image: str = "",
                     scroll_flag: int = 0, last_base: str = "",
                     last_res: str = "", role: str = "main"):
        if self.overed:
            return
        win = self._get_window(role)
        if win:
            win.input.move_to(100, 100)
        time.sleep(0.001)
        findSmallFeiTime = time.time()
        old_color = self.color_format
        self.color_format = "b@0ff000-000000"
        while True:
            if self.check_stop():
                self.color_format = old_color
                return
            if self.find_pic_or_str(fei_image, self.talkLocation, 0, role):
                break
            if time.time() - findSmallFeiTime > 5:
                self.color_format = old_color
                return f"没找到{fei_image}"
            if self.downTalkLocation:
                self.scroll_up(self.downTalkLocation.x, self.downTalkLocation.y, role)
                time.sleep(0.001)
        findShengXiaoTime = time.time()
        while True:
            if self.check_stop():
                self.color_format = old_color
                return
            if time.time() - findShengXiaoTime > 5:
                self.color_format = old_color
                return "没找到飞鞋"
            shengxiaoLocation = self.fing_fei_in_image_or_str(
                fei_image, self.talkLocation,
                (70, 0, 230, 45),
                "ya_assets/images/fei3.bmp|ya_assets/images/fei.bmp|ya_assets/images/fei2.bmp|ya_assets/images/fei1.bmp",
                role
            )
            if shengxiaoLocation:
                break
        self.color_format = old_color
        if last_base and "没找到" not in str(last_res):
            self.waitFor(last_base, self.dituLocation, 330, role=role)
        if win:
            win.input.move_to(shengxiaoLocation.x, shengxiaoLocation.y)
            time.sleep(0.001)
            win.input.left_click(shengxiaoLocation.x, shengxiaoLocation.y)
        wait_base = self.waitFor(base_image, self.dituLocation, 6, role=role)
        if not wait_base:
            return f"没找到{base_image}"
        self.color_format = "b@ffff00-000000"
        hasZhengDian = self.waitFor("打就打1", self.gameBottomLocation, 1.6, role=role)
        self.color_format = old_color
        if not hasZhengDian:
            return f"飞过去没有{fei_image}"
        if win:
            win.input.move_to(int(hasZhengDian.x + 10), int(hasZhengDian.y + 5))
            time.sleep(0.001)
            win.input.left_click(int(hasZhengDian.x + 10), int(hasZhengDian.y + 5))
            time.sleep(0.001)
            win.input.left_click(int(hasZhengDian.x + 10), int(hasZhengDian.y + 5))
        queryTime = time.time()
        while hasZhengDian:
            if self.overed:
                return
            if self.check_stop():
                return
            if time.time() - queryTime > 5:
                return f"点了没找到{fei_image}"
            if self.find_pic("ya_assets/images/zdzd.bmp", self.gameLocation, self.confidenceNum, role):
                return f"打到了{fei_image}"
            yourendaLocation = self.find_pic("ya_assets/images/text/dianji.bmp", self.gameBottomLocation, self.confidenceNum, role)
            if yourendaLocation:
                if win:
                    win.input.move_to(yourendaLocation.x, yourendaLocation.y)
                    time.sleep(0.001)
                    win.input.left_click(yourendaLocation.x, yourendaLocation.y)
                return f"有人打{fei_image}"

    def feiCity(self, city_image: str, role: str = "main"):
        if self.overed:
            return
        self.click_image("ya_assets/images/fei.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(1.0)
        if self.click_image(city_image, self.gameLocation, self.confidenceNum, role):
            time.sleep(0.5)
            self.click_image("ya_assets/images/fei.bmp", self.gameLocation, self.confidenceNum, role)

    def beginFun(self, role: str = "main"):
        closeTalkXY = self.find_pic(
            "ya_assets/images/closeTalk.bmp", self.talkLocation, self.confidenceNum, role
        )
        with self.condition:
            if self.stopped:
                self.condition.wait()
        if closeTalkXY:
            win = self._get_window(role)
            if win:
                win.input.move_to(closeTalkXY.x, closeTalkXY.y)
                for _ in range(4):
                    time.sleep(0.2)
                    win.input.left_click(closeTalkXY.x, closeTalkXY.y)
        self.click_image("ya_assets/images/closeTalk.bmp", self.talkLocation, self.confidenceNum, role)
        time.sleep(0.2)
        self.click_image("ya_assets/images/closeTalk.bmp", self.talkLocation, self.confidenceNum, role)
        self.click_image("ya_assets/images/closeright.bmp", self.gameBottomLocation, self.confidenceNum, role)
        time.sleep(0.2)
        self.click_image("ya_assets/images/yincang.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(1)
        with self.condition:
            if self.stopped:
                self.condition.wait()
        self.click_image("ya_assets/images/yes.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.3)
        self.click_image("ya_assets/images/yes.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.5)

    def outScript(self, current: str = None, role: str = "main"):
        if self.overed:
            return
        if current is not None:
            self.waitFor(current, self.dituLocation, role=role)
        with self.condition:
            if self.stopped:
                self.condition.wait()
        time.sleep(0.1)
        find_queding_time = time.time()
        locationQueding = None
        win = self._get_window(role)
        while True:
            if self.scriptName == "官渡" and self.find_pic_or_str("官渡", self.dituLocation, 0, role):
                break
            if self.scriptName == "魔镜" and self.find_pic_or_str("城西", self.dituLocation, 0, role):
                break
            if self.scriptName == "黑风" and self.find_pic_or_str("五层", self.dituLocation, 0, role):
                break
            if time.time() - find_queding_time > 30:
                break
            if self.check_stop():
                return
            outX = 514 + self.locationX
            outY = 50 + self.locationY
            if win:
                win.input.move_to(int(outX), int(outY))
                time.sleep(0.1)
                win.input.left_click(int(outX), int(outY))
            locationQueding = self.waitFor(
                "ya_assets/images/outFb.bmp|ya_assets/images/outFb1.bmp",
                self.gameLocation, 3, role=role
            )
            if locationQueding:
                break
        time.sleep(0.1)
        while locationQueding:
            if not self.find_pic_or_str(
                "ya_assets/images/outFb.bmp|ya_assets/images/outFb1.bmp",
                self.gameLocation, 0, role
            ):
                break
            if win:
                win.input.move_to(locationQueding.x, locationQueding.y)
                time.sleep(0.1)
                win.input.left_click(locationQueding.x, locationQueding.y)
                time.sleep(0.1)
                win.input.left_click(locationQueding.x, locationQueding.y)
        huodetongbiLocation = self.waitFor("获得铜币", self.gameLeftLocation, 1, role=role)
        if huodetongbiLocation:
            if win:
                win.input.move_to(huodetongbiLocation.x, huodetongbiLocation.y)
                time.sleep(0.001)
                win.input.left_click(huodetongbiLocation.x, huodetongbiLocation.y)
        else:
            return

    def addBloud(self, count: int = 2, role: str = "main"):
        if self.overed:
            return
        self.confidenceNum = 0.7
        self.addBloudFlag = True
        for _ in range(count):
            self.click_image("ya_assets/images/addBloud.bmp", self.gameLocation, self.confidenceNum, role)
            time.sleep(0.1)
            self.click_image("ya_assets/images/addBloud1.bmp", self.gameLocation, self.confidenceNum, role)
            time.sleep(0.1)
            self.click_image("ya_assets/images/addBloud2.bmp", self.gameLocation, self.confidenceNum, role)
            time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue1.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue1.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue1.bmp", self.gameLocation, self.confidenceNum, role)
        time.sleep(0.1)
        self.click_image("ya_assets/images/addBlue1.bmp", self.gameLocation, self.confidenceNum, role)
        self.confidenceNum = 0.9
        self.addBloudFlag = False

    def clearBag(self, role: str = "main"):
        if self.overed:
            return
        self.clickFlag = True
        bagPos = self.waitFor(
            "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
        )
        if bagPos:
            win = self._get_window(role)
            if win:
                win.input.move_to(bagPos.x, bagPos.y)
                time.sleep(0.5)
                win.input.left_click(bagPos.x, bagPos.y)
        chushou = self.waitFor(
            "ya_assets/images/chushou.bmp|ya_assets/images/chushou1.bmp",
            self.gameBottomLocation, 5, role=role
        )
        if chushou:
            win = self._get_window(role)
            if win:
                win.input.move_to(chushou.x, chushou.y)
                time.sleep(0.5)
                win.input.left_click(chushou.x, chushou.y)
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(1)
        zise = self.waitFor("紫色", self.gameBottomLocation, 5, role=role)
        if zise:
            win = self._get_window(role)
            if win:
                win.input.move_to(int(zise.x + 3), int(zise.y + 3))
                time.sleep(0.5)
                win.input.left_click(int(zise.x + 3), int(zise.y + 3))
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(1)
        quedingchushou = self.waitFor(
            "ya_assets/images/quedingchushou.bmp", self.gameBottomLocation, 5, role=role
        )
        if quedingchushou:
            win = self._get_window(role)
            if win:
                win.input.move_to(quedingchushou.x, quedingchushou.y)
                time.sleep(0.5)
                win.input.left_click(quedingchushou.x, quedingchushou.y)
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(4)
        self.clickFlag = False
        bagPos = self.waitFor(
            "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
        )
        if bagPos:
            win = self._get_window(role)
            if win:
                win.input.move_to(bagPos.x, bagPos.y)
                time.sleep(0.5)
                win.input.left_click(bagPos.x, bagPos.y)

    def clear_hide_map(self, role: str = "main"):
        if self.overed:
            return
        self.clickFlag = True
        bagPos = self.waitFor(
            "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
        )
        if bagPos:
            win = self._get_window(role)
            if win:
                win.input.move_to(bagPos.x, bagPos.y)
                time.sleep(0.5)
                win.input.left_click(bagPos.x, bagPos.y)
        chushou = self.waitFor(
            "ya_assets/images/chushou.bmp|ya_assets/images/chushou1.bmp",
            self.gameBottomLocation, 5, role=role
        )
        if chushou:
            win = self._get_window(role)
            if win:
                win.input.move_to(chushou.x, chushou.y)
                time.sleep(0.5)
                win.input.left_click(chushou.x, chushou.y)
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(1)
        zise = self.waitFor("藏宝图", self.gameBottomLocation, 5, role=role)
        if zise:
            win = self._get_window(role)
            if win:
                win.input.move_to(zise.x, zise.y)
                time.sleep(0.5)
                win.input.left_click(zise.x, zise.y)
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(1)
        quedingchushou = self.waitFor(
            "ya_assets/images/quedingchushou.bmp", self.gameBottomLocation, 5, role=role
        )
        if quedingchushou:
            win = self._get_window(role)
            if win:
                win.input.move_to(quedingchushou.x, quedingchushou.y)
                time.sleep(0.5)
                win.input.left_click(quedingchushou.x, quedingchushou.y)
        else:
            bagPos = self.waitFor(
                "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
            )
            if bagPos:
                win = self._get_window(role)
                if win:
                    win.input.move_to(bagPos.x, bagPos.y)
                    time.sleep(0.5)
                    win.input.left_click(bagPos.x, bagPos.y)
            self.clickFlag = False
            return
        time.sleep(4)
        self.clickFlag = False
        bagPos = self.waitFor(
            "ya_assets/images/beibao.bmp", self.gameBottomLocation, 5, role=role
        )
        if bagPos:
            win = self._get_window(role)
            if win:
                win.input.move_to(bagPos.x, bagPos.y)
                time.sleep(0.5)
                win.input.left_click(bagPos.x, bagPos.y)

    def go_in_ditu(self, find_address: str, address_pos_city: str,
                   break_address: str, yizhan_name1: str = "",
                   yizhan_name2: str = "", is_fei: bool = False,
                   role: str = "main"):
        if self.overed:
            return
        outFbLocation = self.find_pic_or_str(
            "ya_assets/images/outFb.bmp|ya_assets/images/outFb1.bmp",
            self.gameLocation, 0, role
        )
        if outFbLocation:
            win = self._get_window(role)
            if win:
                win.input.move_to(outFbLocation.x, outFbLocation.y)
                time.sleep(0.001)
                win.input.left_click(outFbLocation.x, outFbLocation.y)
                time.sleep(0.001)
                win.input.left_click(outFbLocation.x, outFbLocation.y)
            time.sleep(2)
        time.sleep(0.5)
        address_pos_city_pos = None
        begin_time = time.time()
        while True:
            if time.time() - begin_time > 600:
                break
            self.confidenceNum = 0.8
            address_pos_city_pos = self.find_pic_or_str(
                address_pos_city, self.gameLocation, 0, role
            )
            if address_pos_city_pos:
                self.confidenceNum = 0.9
                break
            self.confidenceNum = 0.9
            self.key_press("m", role)
            time.sleep(0.5)
        self.confidenceNum = 0.9
        win = self._get_window(role)
        if win and address_pos_city_pos:
            win.input.move_to(address_pos_city_pos.x, address_pos_city_pos.y)
            time.sleep(0.3)
            win.input.left_click(address_pos_city_pos.x, address_pos_city_pos.y)
        if find_address in ["地图绿林路", "地图落日峰", "地图碧波潭", "地图祭坛"]:
            fei_pos = self.waitFor(
                "ya_assets/images/zhengdian/fei.bmp|ya_assets/images/zhengdian/fei1.bmp|ya_assets/images/zhengdian/fei2.bmp|ya_assets/images/zhengdian/fei3.bmp",
                self.gameBottomLocation, 5, role=role
            )
            if not fei_pos:
                self.key_press("m", role)
                return False
            if win:
                win.input.move_to(fei_pos.x, fei_pos.y)
            find_fei_time = time.time()
            while not self.find_pic_or_str(find_address, self.gameBottomLocation, 0, role):
                if self.overed:
                    return
                if time.time() - find_fei_time > 10:
                    self.key_press("m", role)
                    return False
                self.click_image(
                    "ya_assets/images/zhengdian/closezd.bmp|ya_assets/images/zhengdian/closezd1.bmp",
                    self.gameLocation, 0.7, role
                )
                for _ in range(4):
                    self.scroll_down(
                        self.locationX + self.locationWidth // 2,
                        self.locationY + self.locationHeight // 3, role
                    )
                    time.sleep(0.06)
                time.sleep(0.4)
            for _ in range(4):
                self.scroll_down(
                    self.locationX + self.locationWidth // 2,
                    self.locationY + self.locationHeight // 3, role
                )
                time.sleep(0.06)
            time.sleep(0.4)
        is_find_address = self.waitFor(find_address, self.gameLocation, 3, role=role)
        self.click_image(
            "ya_assets/images/zhengdian/closezd.bmp|ya_assets/images/zhengdian/closezd1.bmp",
            self.gameLocation, 0.7, role
        )
        if not is_find_address:
            self.click_image(address_pos_city, self.gameLocation, 0.8, role)
            is_find_address1 = self.waitFor(find_address, self.gameLocation, 3, role=role)
            if not is_find_address1 and find_address != "地图山洞三层":
                return False
        if not is_fei:
            go_pos = self.fing_fei_in_image_or_str(
                find_address, self.gameLocation,
                (0, 5, 150, 20),
                "ya_assets/images/zhengdian/qianwang.bmp|ya_assets/images/zhengdian/qianwang1.bmp|ya_assets/images/zhengdian/qianwang2.bmp|ya_assets/images/zhengdian/qianwang3.bmp",
                role
            )
            if go_pos:
                if win:
                    win.input.move_to(go_pos.x, go_pos.y)
                    time.sleep(0.001)
                    win.input.left_click(go_pos.x, go_pos.y)
                    time.sleep(0.05)
                    win.input.left_click(go_pos.x, go_pos.y)
                time.sleep(0.5)
            if yizhan_name1:
                self.confidenceNum = 0.6
                yizhan_name1_pos = self.waitFor(
                    yizhan_name1, self.gameBottomLocation, 80, role=role
                )
                self.confidenceNum = 0.9
                if yizhan_name1_pos:
                    if win:
                        win.input.move_to(yizhan_name1_pos.x, yizhan_name1_pos.y)
                        time.sleep(0.001)
                        win.input.left_click(yizhan_name1_pos.x, yizhan_name1_pos.y)
                    time.sleep(3)
            if yizhan_name2:
                self.confidenceNum = 0.6
                yizhan_name2_pos = self.waitFor(
                    yizhan_name2, self.gameBottomLocation, 80, role=role
                )
                self.confidenceNum = 0.9
                if yizhan_name2_pos:
                    if win:
                        win.input.move_to(yizhan_name2_pos.x, yizhan_name2_pos.y)
                        time.sleep(0.001)
                        win.input.left_click(yizhan_name2_pos.x, yizhan_name2_pos.y)
                    time.sleep(1)
            self.waitFor(break_address, self.dituLocation, 200, role=role)
        else:
            find_fei_time = time.time()
            region = (0, 5, 180, 20)
            actual_find_address = find_address
            if find_address == "地图徐州":
                actual_find_address = "地图官渡"
                region = (0, -18, 180, 38)
            if find_address == "地图山洞三层":
                actual_find_address = "地图恶龙洞"
                region = (0, 21, 180, 0)
            while True:
                if time.time() - find_fei_time > 10:
                    self.key_press("m", role)
                    return False
                fei_pos = self.fing_fei_in_image_or_str(
                    actual_find_address, self.gameLocation,
                    region,
                    "ya_assets/images/zhengdian/fei.bmp|ya_assets/images/zhengdian/fei1.bmp|ya_assets/images/zhengdian/fei2.bmp|ya_assets/images/zhengdian/fei3.bmp",
                    role
                )
                if fei_pos:
                    while True:
                        if self.find_pic_or_str(break_address, self.dituLocation, 0, role):
                            break
                        if win:
                            win.input.move_to(fei_pos.x, fei_pos.y)
                            time.sleep(0.05)
                            win.input.left_click(fei_pos.x, fei_pos.y)
                        time.sleep(1)
                        if time.time() - find_fei_time > 10:
                            self.key_press("m", role)
                            return False
                    return True

    def run_loop(self, func, loop_mode: str = "infinite", count: int = 1,
                 zhengdian_at: int = 0, clear_bag_every: int = 0,
                 fallback: Optional[str] = None, role: str = "main"):
        start_time = time.time()
        loop_count = 0
        last_min = [time.localtime().tm_min]
        while True:
            if self.check_stop():
                return
            current_min = time.localtime().tm_min
            if current_min != last_min[0]:
                self.zhengdian_flag = False
                last_min[0] = current_min
            if zhengdian_at and time.localtime().tm_min == zhengdian_at and not self.zhengdian_flag:
                if self.scriptName in self.zhengdianFb:
                    self.zhengdian_flag = True
                    if self.scriptName == "官渡":
                        self.clearBag(role)
                    self.outScript(role=role)
                    from ya_scripts.zhengdian import zhengdian
                    zhengdian(self)
                    return
            try:
                result = func()
                if result is False:
                    break
            except Exception:
                pass
            loop_count += 1
            if clear_bag_every and loop_count % clear_bag_every == 0:
                self.clearBag(role)
                self.clear_hide_map(role)
            if loop_mode == "count" and loop_count >= count:
                break
            elif loop_mode == "time" and time.time() - start_time >= count:
                break
            time.sleep(0.5)
        if fallback:
            from ya_scripts import SCRIPT_REGISTRY
            fn = SCRIPT_REGISTRY.get(fallback, (None,))[0]
            if fn:
                fn(self)

    def auto_move_and_click1(self, region: tuple, target: str,
                             interval: float = 0.5, timeout: float = 600,
                             role: str = "main"):
        x1, y1, x2, y2 = region
        win = self._get_window(role)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_stop():
                return False
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)
            if win:
                win.input.move_to(rand_x, rand_y)
                time.sleep(0.001)
                win.input.left_click(rand_x, rand_y)
            time.sleep(1.5)
            ret = self.find_pic_or_str(target, self.gameLocation, 0, role)
            if ret:
                if win:
                    win.input.move_to(ret.x, ret.y)
                    time.sleep(1)
                    win.input.left_click(ret.x, ret.y)
                return True
            time.sleep(interval)
        print("超时未找到图片")
        return False

    def press_keys_until_image_found(self, image_path: str,
                                     image_path2: str, region1=None,
                                     region2=None, find_text: str = "使用",
                                     role: str = "main"):
        if self.overed:
            return
        if region1 is None:
            region1 = self.gameLocation
        if region2 is None:
            region2 = self.gameLocation
        self.confidenceNum = 0.8
        image_path_pos = self.waitFor(image_path, region1, 5, role=role)
        self.confidenceNum = 0.9
        if not image_path_pos:
            return False
        win = self._get_window(role)
        while True:
            if self.check_stop():
                return
            if self.find_pic_or_str(image_path2, region2, 0, role):
                break
            time.sleep(0.001)
            if win:
                win.input.move_to(image_path_pos.x, int(image_path_pos.y))
                time.sleep(0.001)
                win.input.left_click(image_path_pos.x, int(image_path_pos.y))
            time.sleep(0.5)
            if win:
                win.input.move_to(image_path_pos.x, int(image_path_pos.y + 150))
            time.sleep(0.001)
            self.confidenceNum = 0.8
            chushou_pos = self.waitFor(find_text, self.gameLocation, 3, role=role)
            self.confidenceNum = 0.9
            if chushou_pos and win:
                win.input.move_to(chushou_pos.x, chushou_pos.y)
                time.sleep(0.001)
                win.input.left_click(chushou_pos.x, chushou_pos.y)
                time.sleep(0.001)
                win.input.left_click(chushou_pos.x, chushou_pos.y)
                time.sleep(0.5)
            if win:
                win.input.move_to(int(image_path_pos.x + 100), image_path_pos.y)
            if self.find_pic_or_str(image_path2, region2, 0, role):
                break
            time.sleep(1.5)
        return True

    def zhengdian_by_xiaolvren_for_gongcheng(self, base_image: str,
                                               find_dir: int,
                                               npc_posx=None,
                                               npc_possy=None,
                                               order: int = 1,
                                               role: str = "main"):
        if npc_posx is None:
            npc_posx = [0]
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 5, role=role)
        if not base_image_res:
            return
        xiaolvren_results = self.find_pic_all(
            "ya_assets/images/xiaolvren.bmp|ya_assets/images/zhengdian/xiaolvren2.bmp",
            self.dituLocation, 0.7, role
        )
        if not xiaolvren_results:
            return
        if order == 2:
            xiaolvren_results.sort(key=lambda r: r.y, reverse=True)
        else:
            xiaolvren_results.sort(key=lambda r: r.y)
        xiaolvren_pos_color = "07d307"
        for item in xiaolvren_results:
            if self.overed:
                return
            if npc_posx and npc_posx != [0]:
                skip = False
                for px, py in zip(npc_posx, npc_possy):
                    if abs(item.x - int(px)) < 20 and abs(item.y - int(py)) < 20:
                        skip = True
                        break
                if skip:
                    continue
            if self._cmp_color(item.x, item.y, xiaolvren_pos_color, 0.7, role):
                continue
            hasZhengDian = False
            change_color_time = 0
            find_zhengdian_time = time.time()
            win = self._get_window(role)
            if win:
                win.input.move_to(item.x, item.y)
                time.sleep(0.001)
                win.input.left_click(item.x, item.y)
                time.sleep(0.001)
                win.input.move_to(int(item.x - 200), item.y)
            time.sleep(0.1)
            while True:
                if time.time() - find_zhengdian_time > 10:
                    print("超时10s")
                    break
                if change_color_time == 0 and self._cmp_color(item.x, item.y, xiaolvren_pos_color, 0.7, role):
                    change_color_time = time.time()
                time.sleep(0.01)
                self.confidenceNum = 0.6
                time.sleep(0.001)
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/jixu.bmp|ya_assets/images/zhengdian/jixu1.bmp|ya_assets/images/zhengdian/jixu2.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    print("npc")
                    self.confidenceNum = 0.9
                    break
                self.confidenceNum = 0.9
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/tiaozhan.bmp|ya_assets/images/zhengdian/tiaozhan1.bmp|ya_assets/images/zhengdian/tiaozhan2.bmp|ya_assets/images/zhengdian/tiaozhan3.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    print("野外怪物")
                    self.click_image(
                        "ya_assets/images/zhengdian/tiaozhan.bmp|ya_assets/images/zhengdian/tiaozhan1.bmp|ya_assets/images/zhengdian/tiaozhan2.bmp|ya_assets/images/zhengdian/tiaozhan3.bmp",
                        self.gameBottomLocation, 0.6, role
                    )
                    self.confidenceNum = 0.9
                    break
                if self.find_pic("ya_assets/images/text/jinru.bmp", self.gameBottomLocation, self.confidenceNum, role):
                    print("副本npc")
                    self.confidenceNum = 0.9
                    break
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/liwu1.bmp|ya_assets/images/zhengdian/liwu.bmp|ya_assets/images/zhengdian/liwu2.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    print("财神爷")
                    self.click_image(
                        "ya_assets/images/zhengdian/liwu1.bmp|ya_assets/images/zhengdian/liwu.bmp|ya_assets/images/zhengdian/liwu2.bmp",
                        self.gameBottomLocation, 0.8, role
                    )
                    self.confidenceNum = 0.9
                    break
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/dengmi.bmp|ya_assets/images/zhengdian/dengmi1.bmp|ya_assets/images/zhengdian/dengmi2.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    print("灯谜")
                    self.click_image(
                        "ya_assets/images/zhengdian/dengmi.bmp|ya_assets/images/zhengdian/dengmi1.bmp|ya_assets/images/zhengdian/dengmi2.bmp",
                        self.gameBottomLocation, 0.8, role
                    )
                    time.sleep(1)
                    if win:
                        win.input.move_to(252, 346)
                        time.sleep(0.001)
                        win.input.left_click(252, 346)
                    self.confidenceNum = 0.9
                    break
                self.confidenceNum = 0.9
                time.sleep(0.01)
                if change_color_time > 0 and time.time() - change_color_time > 5:
                    print("超时")
                    break
                self.confidenceNum = 0.6
                time.sleep(0.6)
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/gongcheng.bmp|ya_assets/images/zhengdian/gongcheng1.bmp|ya_assets/images/zhengdian/gongcheng2.bmp|ya_assets/images/zhengdian/gongcheng3.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    self.confidenceNum = 0.9
                    hasZhengDian = True
                    break
                self.confidenceNum = 0.6
                is_zhengdian = self.waitFor("攻城", self.gameBottomLocation, 0.6, role=role)
                if is_zhengdian:
                    self.confidenceNum = 0.9
                    hasZhengDian = True
                    break
                is_zhengdian = self.waitFor("挑战", self.gameBottomLocation, 0.6, role=role)
                if is_zhengdian:
                    self.confidenceNum = 0.9
                    hasZhengDian = True
                    print("野外怪物")
                    break
            if hasZhengDian:
                find_time = time.time()
                dajiuda_pos = None
                while True:
                    dajiuda_pos = self.find_pic_or_str(
                        "ya_assets/images/zhengdian/gongcheng.bmp|ya_assets/images/zhengdian/gongcheng1.bmp|ya_assets/images/zhengdian/gongcheng2.bmp|ya_assets/images/zhengdian/gongcheng3.bmp",
                        self.gameBottomLocation, 0, role
                    )
                    if dajiuda_pos:
                        break
                    dajiuda_pos = self.find_pic("ya_assets/images/text/gongcheng.bmp", self.gameBottomLocation, self.confidenceNum, role)
                    if dajiuda_pos:
                        break
                    time.sleep(0.3)
                    if self.confidenceNum > 0.6:
                        self.confidenceNum -= 0.1
                    if time.time() - find_time > 4:
                        print("没找到打就打")
                        break
                self.confidenceNum = 0.9
                if dajiuda_pos and win:
                    win.input.move_to(int(dajiuda_pos.x + 10), int(dajiuda_pos.y + 3))
                    time.sleep(0.001)
                    win.input.left_click(int(dajiuda_pos.x + 10), int(dajiuda_pos.y + 3))
                    queryTime = time.time()
                    zhengdianHas = False
                    while True:
                        with self.condition:
                            if self.stopped:
                                self.condition.wait()
                        if time.time() - queryTime > 8:
                            zhengdianHas = False
                            break
                        if self.find_pic("ya_assets/images/zdzd.bmp", self.gameLocation, self.confidenceNum, role):
                            zhengdianHas = True
                            break
                        self.confidenceNum = 0.6
                        yourendaLocation = self.find_pic("ya_assets/images/text/dianji.bmp", self.gameBottomLocation, self.confidenceNum, role)
                        if yourendaLocation and win:
                            win.input.move_to(yourendaLocation.x, yourendaLocation.y)
                            time.sleep(0.001)
                            win.input.left_click(yourendaLocation.x, yourendaLocation.y)
                            zhengdianHas = False
                            break
                        yourendaLocation1 = self.find_pic_or_str(
                            "ya_assets/images/zhengdian/jixu.bmp|ya_assets/images/zhengdian/jixu1.bmp|ya_assets/images/zhengdian/jixu2.bmp",
                            self.gameBottomLocation, 0, role
                        )
                        if yourendaLocation1 and win:
                            win.input.move_to(yourendaLocation1.x, yourendaLocation1.y)
                            time.sleep(0.001)
                            win.input.left_click(yourendaLocation1.x, yourendaLocation1.y)
                            zhengdianHas = False
                            break
                        self.confidenceNum = 0.9
                    if zhengdianHas:
                        self.waitFor(base_image, self.dituLocation, 30, role=role)
                        time.sleep(0.1)
                        self.guanDuCount += 1
                        print(f"打完了{self.guanDuCount}个怪物")
                else:
                    print("没找到怪物")

    def guajiAndzhengdianScript(self, base_image=None, role: str = "main"):
        print("挂机+整点")
        if self.overed:
            return
        if self.check_stop():
            return
        if not self.guajiLocation:
            guaji_pos = self.waitFor("ya_assets/images/guaji/guaji1.bmp|ya_assets/images/guaji/guaji.bmp", self.gameLocation, 10, role=role)
            if guaji_pos:
                self.guajiLocation = guaji_pos
            else:
                print("未找到挂机")
                return
        else:
            time.sleep(1.5)
            self.click(int(self.locationX + 608), int(self.locationY + 45))
        self.click(self.guajiLocation.x, self.guajiLocation.y)
        time.sleep(0.001)
        self.click(self.guajiLocation.x, self.guajiLocation.y)
        time.sleep(0.001)
        self.click(self.guajiLocation.x, self.guajiLocation.y)
        time.sleep(5)
        if self.overed:
            return
        if self.check_stop():
            return
        while True:
            if self.check_stop():
                return
            current_time = time.localtime()
            if current_time.tm_min == 58:
                if self.find_pic_or_str("挂机中", self.gameBottomLocation, 0, role):
                    is_stop_guaji = self.click_image(
                        "ya_assets/images/closeJJ.bmp",
                        self.gameBottomLocation, self.confidenceNum, role
                    )
                    if is_stop_guaji:
                        break
            time.sleep(1)
        time.sleep(1)
        self.clearBag(role)
        time.sleep(1)
        self.outScript(role=role)
        time.sleep(2)
        self.zhengdian_flag = True
        from ya_scripts.zhengdian import zhengdian
        zhengdian(self)

    def zhengdian_by_xiaolvren(self, base_image: str, find_dir: int,
                                npc_posx=None, npc_possy=None,
                                order: int = 1, role: str = "main"):
        if npc_posx is None:
            npc_posx = 0
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_res = self.waitFor(base_image, self.dituLocation, 5, role=role)
        if not base_res:
            return
        xiaolvren_results = self.find_pic_all(
            "ya_assets/images/xiaolvren.bmp|ya_assets/images/zhengdian/xiaolvren2.bmp",
            self.dituLocation, 0.7, role
        )
        if not xiaolvren_results:
            return
        if order == 2:
            xiaolvren_results.sort(key=lambda r: r.y, reverse=True)
        else:
            xiaolvren_results.sort(key=lambda r: r.y)
        xiaolvren_pos_color = "07d307"
        for item in xiaolvren_results:
            if self.overed:
                return
            if npc_posx and npc_posx != 0:
                if isinstance(npc_posx, list):
                    skip = False
                    for px, py in zip(npc_posx, npc_possy):
                        if abs(item.x - int(px)) < 20 and abs(item.y - int(py)) < 20:
                            skip = True
                            break
                    if skip:
                        continue
            if self._cmp_color(item.x, item.y, xiaolvren_pos_color, 0.7, role):
                self.hasZhengDianCount -= 1
                continue
            hasZhengDian = False
            change_color_time = 0
            find_zhengdian_time = time.time()
            win = self._get_window(role)
            if win:
                win.input.move_to(item.x, item.y)
                time.sleep(0.001)
                win.input.left_click(item.x, item.y)
                time.sleep(0.001)
                win.input.move_to(int(item.x - 200), item.y)
            time.sleep(0.1)
            self.color_format = "b@ffff00-000000|fff200-000000"
            while True:
                if time.time() - find_zhengdian_time > 10:
                    print("超时10s")
                    break
                if change_color_time == 0 and self._cmp_color(item.x, item.y, xiaolvren_pos_color, 0.7, role):
                    change_color_time = time.time()
                time.sleep(0.01)
                self.confidenceNum = 0.8
                time.sleep(0.001)
                if self.find_pic_or_str(
                    "ya_assets/images/zhengdian/dianwei.bmp|ya_assets/images/zhengdian/dianwei1.bmp|ya_assets/images/zhengdian/jixu.bmp|ya_assets/images/zhengdian/jixu1.bmp|ya_assets/images/zhengdian/jixu2.bmp",
                    self.gameBottomLocation, 0, role
                ):
                    print("npc")
                    self.confidenceNum = 0.9
                    break
                self.confidenceNum = 0.9
                time.sleep(0.01)
                if change_color_time > 0 and time.time() - change_color_time > 5:
                    print("超时")
                    break
                is_zhengdian = self.find_pic("ya_assets/images/text/dajiuda1.bmp", self.gameBottomLocation, self.confidenceNum, role)
                if is_zhengdian:
                    self.hasZhengDianCount -= 1
                    if win:
                        win.input.move_to(int(is_zhengdian.x + 5), int(is_zhengdian.y + 5))
                        time.sleep(0.001)
                        win.input.left_click(int(is_zhengdian.x + 5), int(is_zhengdian.y + 5))
                    hasZhengDian = True
                    break
            if hasZhengDian:
                self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
                queryTime = time.time()
                zhengdianHas = False
                while True:
                    with self.condition:
                        if self.stopped:
                            self.condition.wait()
                    if time.time() - queryTime > 5:
                        zhengdianHas = False
                        break
                    self.confidenceNum = 0.6
                    if self.find_pic(
                        "ya_assets/images/zdzd111.bmp",
                        self.gameLocation, self.confidenceNum, role
                    ):
                        zhengdianHas = True
                        break
                    yourendaLocation = self.find_pic("ya_assets/images/text/beitiaozhan.bmp", self.gameBottomLocation, self.confidenceNum, role)
                    if yourendaLocation:
                        zhengdianHas = False
                        print("被挑战")
                        break
                    yourendaLocation1 = self.find_pic(
                        "ya_assets/images/zhengdian/beitiaozhan.bmp",
                        self.gameBottomLocation, self.confidenceNum, role
                    )
                    if yourendaLocation1:
                        zhengdianHas = False
                        print("被挑战")
                        break
                    bucunzai = self.find_pic(
                        "ya_assets/images/zhengdian/bucunzai.bmp",
                        self.gameBottomLocation, self.confidenceNum, role
                    )
                    if bucunzai:
                        zhengdianHas = False
                        print("不存在")
                        break
                    self.confidenceNum = 0.9
                if zhengdianHas:
                    self.waitFor(base_image, self.dituLocation, 30, role=role)
                    self.daZhengDianCount += 1
                    time.sleep(0.1)
                    print(f"打了第{self.daZhengDianCount}个整点")
                else:
                    print("没找到整点")
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
