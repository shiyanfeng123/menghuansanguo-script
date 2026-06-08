# -*- coding: utf-8 -*-
"""
梦幻三国 - 脚本工厂 (v7.0: 深度易用性改造)
"""

import os, json, time, threading, datetime, re, copy, shutil
import wx
import wx.lib.scrolledpanel as scrolled

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVE_SCRIPT = os.path.join(SCRIPT_DIR, "serveScript.py")
USER_SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "user_scripts")
REGISTRY_FILE = os.path.join(USER_SCRIPTS_DIR, "registry.json")
SERVE_ASSETS = os.path.join(SCRIPT_DIR, "serveAssets")
os.makedirs(USER_SCRIPTS_DIR, exist_ok=True)

TAG_DISPATCH_START = "        # === AUTO_SCRIPTS_DISPATCH_START ==="
TAG_DISPATCH_END = "        # === AUTO_SCRIPTS_DISPATCH_END ==="
TAG_METHODS_START = "    # === AUTO_SCRIPTS_METHODS_START ==="
TAG_METHODS_END = "    # === AUTO_SCRIPTS_METHODS_END ==="

_resource_index = None

def _build_resource_index():
    global _resource_index
    if _resource_index is not None:
        return _resource_index
    _resource_index = {"images": [], "fonts": []}
    img_dir = os.path.join(SERVE_ASSETS, "images")
    if os.path.exists(img_dir):
        for root, dirs, files in os.walk(img_dir):
            for f in files:
                if f.lower().endswith(('.bmp', '.png', '.jpg')):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, SCRIPT_DIR).replace('\\', '/')
                    _resource_index["images"].append({
                        "name": f, "path": rel,
                        "folder": os.path.basename(os.path.dirname(full)),
                    })
    _resource_index["images"].sort(key=lambda x: x["name"])
    return _resource_index


def search_resources(query):
    if not query: return []
    idx = _build_resource_index()
    q = query.lower()
    results = []
    for img in idx["images"]:
        if q in img["name"].lower() or q in img["folder"].lower():
            results.append({"label": f"{img['name']}  [{img['folder']}]",
                            "value": img["path"],
                            "name": img["name"], "folder": img["folder"]})
    results.sort(key=lambda r: r["name"])
    return results[:20]


KNOWN_CITIES = ["洛阳", "襄阳", "涿郡", "许昌", "官渡", "徐州", "城西"]
AREA_LABELS = {
    "屏幕下半部分": "gameBottomLocation",
    "屏幕左半部分": "gameLeftLocation",
    "屏幕右半部分": "gameRightLocation",
    "右上角小地图": "dituLocation",
    "全屏": "gameLocation",
}
AREA_REVERSE = {v: k for k, v in AREA_LABELS.items()}
KNOWN_KEYS = ["tab", "A", "D", "W", "S", "1", "2", "3"]
FB_NAMES = ["副本曹操", "副本老仙", "副本南华老人", "副本分身", "副本猎鼠人",
            "副本挑战赛", "副本魔镜使者", "副本典韦", "副本龙天啸"]
FALLBACK_CHOICES = ["官渡", "魔镜", "黑风"]


TEMPLATES = {
    "魔镜使者": {
        "desc": "洛阳出发，飞副本魔镜使者，3层打怪",
        "icon": "🪞",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "洛阳", "yizhan": "驿站城西", "npc_image": "",
                      "fb_name": "副本魔镜使者", "is_elite": False, "is_fei": True},
            "confirm_map": "镜像地层",
            "sub_maps": ["镜像地层", "遗迹镜像", "迷幻境"],
            "exit_map": "城西",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [
                {"map_name": "镜像地层", "monsters": [
                    {"detect_mode": "text", "name": "魔镜使者", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {"click_map_name": "遗迹镜像",
                                  "click_region_proportion": "0.1,0.12"}},
                {"map_name": "遗迹镜像", "monsters": [
                    {"detect_mode": "text", "name": "魔镜使者", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {"click_map_name": "迷幻境",
                                  "click_region_proportion": "0.1,0.12"}},
                {"map_name": "迷幻境", "monsters": [
                    {"detect_mode": "text", "name": "魔镜使者", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {}}
            ],
            "fallback": "官渡",
        }
    },
    "曹操副本": {
        "desc": "许昌出发，飞副本曹操，单层打怪",
        "icon": "⚔️",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "许昌", "yizhan": "驿站城西", "npc_image": "",
                      "fb_name": "副本曹操", "is_elite": False, "is_fei": True},
            "confirm_map": "曹操大帐",
            "sub_maps": ["曹操大帐"],
            "exit_map": "城西",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [
                {"map_name": "曹操大帐", "monsters": [
                    {"detect_mode": "text", "name": "曹操", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {}}
            ],
            "fallback": "官渡",
        }
    },
    "典韦副本": {
        "desc": "洛阳出发，飞副本典韦，单层打怪",
        "icon": "🛡️",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "洛阳", "yizhan": "驿站城西", "npc_image": "",
                      "fb_name": "副本典韦", "is_elite": False, "is_fei": True},
            "confirm_map": "典韦",
            "sub_maps": ["典韦"],
            "exit_map": "城西",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [
                {"map_name": "典韦", "monsters": [
                    {"detect_mode": "text", "name": "典韦", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {}}
            ],
            "fallback": "官渡",
        }
    },
    "龙天啸副本": {
        "desc": "洛阳出发，飞副本龙天啸，单层打怪",
        "icon": "🐉",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "洛阳", "yizhan": "驿站城西", "npc_image": "",
                      "fb_name": "副本龙天啸", "is_elite": False, "is_fei": True},
            "confirm_map": "龙天啸",
            "sub_maps": ["龙天啸"],
            "exit_map": "城西",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [
                {"map_name": "龙天啸", "monsters": [
                    {"detect_mode": "text", "name": "龙天啸", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {}}
            ],
            "fallback": "官渡",
        }
    },
    "老仙副本": {
        "desc": "洛阳出发，飞副本老仙，单层打怪",
        "icon": "🧙",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "洛阳", "yizhan": "驿站城西", "npc_image": "",
                      "fb_name": "副本老仙", "is_elite": False, "is_fei": True},
            "confirm_map": "老仙",
            "sub_maps": ["老仙"],
            "exit_map": "城西",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [
                {"map_name": "老仙", "monsters": [
                    {"detect_mode": "text", "name": "老仙", "images": "",
                     "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
                     "region": "gameBottomLocation", "repeat": 3, "move_key": "tab",
                     "move_region": "0.038,0.134"}
                ], "transition": {}}
            ],
            "fallback": "官渡",
        }
    },
    "空白脚本": {
        "desc": "从零开始，自己配置所有内容",
        "icon": "📝",
        "config": {
            "type": "dungeon_run", "name": "",
            "entry": {"city": "洛阳", "yizhan": "", "npc_image": "",
                      "fb_name": "", "is_elite": False, "is_fei": True},
            "confirm_map": "",
            "sub_maps": [],
            "exit_map": "",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [],
            "fallback": "官渡",
        }
    },
}


_font_index = None

def _build_font_index():
    global _font_index
    if _font_index is not None:
        return _font_index
    _font_index = []
    font_dir = os.path.join(SERVE_ASSETS, "fonts")
    if not os.path.exists(font_dir):
        return _font_index
    seen = set()
    for fname in os.listdir(font_dir):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(font_dir, fname)
        for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
            try:
                with open(fpath, "r", encoding=enc) as f:
                    for line in f:
                        line = line.strip()
                        if not line or "$" not in line:
                            continue
                        parts = line.split("$")
                        if len(parts) >= 2 and parts[1]:
                            text = parts[1].strip()
                            if text and text not in seen:
                                seen.add(text)
                                _font_index.append(text)
                break
            except (UnicodeDecodeError, IOError):
                continue
    _font_index.sort()
    return _font_index


def search_fonts(query):
    if not query:
        return []
    idx = _build_font_index()
    q = query.lower()
    results = []
    for text in idx:
        if q in text.lower():
            results.append({"label": text, "value": text})
    return results[:20]


# ============================================================
# 搜索选择对话框
# ============================================================
class SearchDialog(wx.Dialog):
    def __init__(self, parent, title, results):
        super().__init__(parent, title=title, size=(500, 400), style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(wx.Colour(225, 228, 235))
        self.result_value = None
        self._results = results

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.lb = wx.ListBox(self, style=wx.LB_SINGLE)
        self.lb.SetBackgroundColour(wx.Colour(240, 242, 246))
        self.lb.SetForegroundColour(wx.Colour(40, 42, 50))
        self.lb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                faceName="Consolas"))
        for r in results:
            self.lb.Append(r["label"], r["value"])
        if results:
            self.lb.SetSelection(0)
        self.lb.Bind(wx.EVT_LISTBOX_DCLICK, self._on_dclick)
        sizer.Add(self.lb, 1, wx.EXPAND | wx.ALL, 8)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self, wx.ID_OK, "选择")
        btn_ok.SetBackgroundColour(wx.Colour(39, 174, 96))
        btn_ok.SetForegroundColour(wx.Colour(255, 255, 255))
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "取消")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(btn_ok, 0, wx.RIGHT, 4)
        btn_sizer.Add(btn_cancel, 0)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self._on_ok, btn_ok)

    def _on_ok(self, e):
        sel = self.lb.GetSelection()
        if 0 <= sel < len(self._results):
            self.result_value = self._results[sel]["value"]
        self.EndModal(wx.ID_OK)

    def _on_dclick(self, e):
        self._on_ok(None)


# ============================================================
# 图片检索输入框
# ============================================================
class SearchInput(wx.Panel):
    def __init__(self, parent, value="", hint="输入关键词搜索图片..."):
        super().__init__(parent, size=(-1, 28))
        self._search_func = search_resources
        self._hint = hint
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tc = wx.TextCtrl(self, size=(-1, 28))
        self.tc.SetValue(str(value))
        self.tc.SetHint(hint)
        self.tc.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.tc.SetForegroundColour(wx.Colour(40, 42, 50))
        sizer.Add(self.tc, 1, wx.EXPAND | wx.RIGHT, 2)
        self.btn = wx.Button(self, label="🔍", size=(32, 28), style=wx.BORDER_NONE)
        self.btn.SetBackgroundColour(wx.Colour(215, 218, 226))
        self.btn.SetForegroundColour(wx.Colour(60, 65, 75))
        self.btn.Bind(wx.EVT_BUTTON, self._on_search)
        sizer.Add(self.btn, 0)
        self.SetSizer(sizer)

    def _on_search(self, e):
        q = self.tc.GetValue().strip()
        results = self._search_func(q) if q else []
        if not results:
            wx.MessageBox(f"未找到匹配项: '{q}'", "搜索结果")
            return
        dlg = SearchDialog(self.GetTopLevelParent(), f"搜索结果: {q}", results)
        if dlg.ShowModal() == wx.ID_OK and dlg.result_value:
            self.tc.SetValue(dlg.result_value)
            evt = wx.CommandEvent(wx.wxEVT_TEXT, self.tc.GetId())
            wx.PostEvent(self.tc, evt)
        dlg.Destroy()

    def GetValue(self):
        return self.tc.GetValue()

    def SetValue(self, v):
        self.tc.SetValue(str(v))

    def Bind(self, event, handler, *args, **kwargs):
        self.tc.Bind(event, handler, *args, **kwargs)


class FontSearchInput(wx.Panel):
    def __init__(self, parent, value="", hint="输入文字搜索字库..."):
        super().__init__(parent, size=(-1, 28))
        self._search_func = search_fonts
        self._hint = hint
        self._hint_label = None
        self._game_btn = None
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tc = wx.TextCtrl(self, size=(-1, 28))
        self.tc.SetValue(str(value))
        self.tc.SetHint(hint)
        self.tc.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.tc.SetForegroundColour(wx.Colour(40, 42, 50))
        self.tc.Bind(wx.EVT_TEXT, self._on_text)
        sizer.Add(self.tc, 1, wx.EXPAND | wx.RIGHT, 2)
        self.btn = wx.Button(self, label="🔍", size=(32, 28), style=wx.BORDER_NONE)
        self.btn.SetBackgroundColour(wx.Colour(215, 218, 226))
        self.btn.SetForegroundColour(wx.Colour(60, 65, 75))
        self.btn.Bind(wx.EVT_BUTTON, self._on_search)
        sizer.Add(self.btn, 0)
        self.SetSizer(sizer)

    def set_hint_label(self, label):
        self._hint_label = label

    def set_game_button(self, btn):
        self._game_btn = btn

    def _on_text(self, e):
        q = self.tc.GetValue().strip()
        self._update_hint(q)
        e.Skip()

    def _on_search(self, e):
        q = self.tc.GetValue().strip()
        results = self._search_func(q) if q else []
        if not results:
            wx.MessageBox(f"未找到匹配项: '{q}'", "搜索结果")
            return
        dlg = SearchDialog(self.GetTopLevelParent(), f"字库搜索: {q}", results)
        if dlg.ShowModal() == wx.ID_OK and dlg.result_value:
            self.tc.SetValue(dlg.result_value)
            self._update_hint(dlg.result_value)
            evt = wx.CommandEvent(wx.wxEVT_TEXT, self.tc.GetId())
            wx.PostEvent(self.tc, evt)
        dlg.Destroy()

    def _update_hint(self, q):
        if not self._hint_label:
            return
        if not q:
            self._hint_label.SetLabel("")
            self._hint_label.SetForegroundColour(wx.Colour(70, 75, 85))
            return
        idx = _build_font_index()
        if q in idx:
            self._hint_label.SetLabel("✅ 可以识别这个文字")
            self._hint_label.SetForegroundColour(wx.Colour(34, 153, 84))
        else:
            matched = [t for t in idx if q.lower() in t.lower()]
            if matched:
                self._hint_label.SetLabel(f"💡 找到 {len(matched)} 个相似文字，点击🔍选择")
                self._hint_label.SetForegroundColour(wx.Colour(160, 120, 0))
            else:
                self._hint_label.SetLabel("⚠️ 脚本还不认识这个字，点🎮从游戏画面框选录入")
                self._hint_label.SetForegroundColour(wx.Colour(192, 57, 43))

    def GetValue(self):
        return self.tc.GetValue()

    def SetValue(self, v):
        self.tc.SetValue(str(v))

    def Bind(self, event, handler, *args, **kwargs):
        self.tc.Bind(event, handler, *args, **kwargs)


# ============================================================
# 游戏交互工具 — 坐标拾取 / 区域截图 / 文字框选
# ============================================================
class TextInputDialog(wx.Dialog):
    """让用户输入在游戏画面中看到的文字，并尝试录入字库"""
    def __init__(self, parent, detected_color="", captured_bmp_path=""):
        super().__init__(parent, title="输入你看到的文字", size=(440, 320),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.SetBackgroundColour(wx.Colour(225, 228, 235))

        sizer = wx.BoxSizer(wx.VERTICAL)

        info = wx.StaticText(self, label="请在下方输入你在框选区域中看到的文字：")
        info.SetForegroundColour(wx.Colour(40, 42, 50))
        info.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(info, 0, wx.ALL, 10)

        if detected_color:
            color_row = wx.BoxSizer(wx.HORIZONTAL)
            color_lbl = wx.StaticText(self, label="自动检测到的文字颜色: ")
            color_lbl.SetForegroundColour(wx.Colour(70, 75, 85))
            color_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            color_row.Add(color_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            try:
                main_color = detected_color.split("|")[0].split("-")[0]
                r = int(main_color[0:2], 16)
                g = int(main_color[2:4], 16)
                b = int(main_color[4:6], 16)
                color_box = wx.Panel(self, size=(20, 20))
                color_box.SetBackgroundColour(wx.Colour(r, g, b))
                color_row.Add(color_box, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            except Exception:
                pass
            color_val = wx.StaticText(self, label=detected_color)
            color_val.SetForegroundColour(wx.Colour(34, 153, 84))
            color_val.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            color_row.Add(color_val, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(color_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        if captured_bmp_path and os.path.exists(captured_bmp_path):
            try:
                img = wx.Image(captured_bmp_path, wx.BITMAP_TYPE_BMP)
                if img.IsOk():
                    max_w, max_h = 400, 80
                    w, h = img.GetWidth(), img.GetHeight()
                    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0)
                    img.Rescale(int(w * scale), int(h * scale))
                    bmp = wx.Bitmap(img)
                    img_ctrl = wx.StaticBitmap(self, bitmap=bmp)
                    sizer.Add(img_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
            except Exception:
                pass

        self.tc = wx.TextCtrl(self, size=(-1, 32))
        self.tc.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.tc.SetForegroundColour(wx.Colour(40, 42, 50))
        self.tc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.tc.SetHint("输入文字，如：魔镜使者")
        sizer.Add(self.tc, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        hint = wx.StaticText(self, label="💡 输入后点确认，系统会自动检查字库并尝试录入")
        hint.SetForegroundColour(wx.Colour(160, 120, 0))
        hint.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(hint, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_ok = wx.Button(self, wx.ID_OK, "确认录入")
        btn_ok.SetBackgroundColour(wx.Colour(39, 174, 96))
        btn_ok.SetForegroundColour(wx.Colour(255, 255, 255))
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "取消")
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(btn_ok, 0, wx.RIGHT, 4)
        btn_sizer.Add(btn_cancel, 0)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.tc.SetFocus()

    def GetText(self):
        return self.tc.GetValue().strip()


class GameCaptureDialog(wx.Dialog):
    """全屏覆盖层，用于从游戏画面拾取坐标、截图、框选文字"""
    def __init__(self, parent, dm, parent_frame, mode="coord"):
        """
        mode:
          "coord" — 点击拾取坐标，返回游戏窗口内坐标
          "image" — 框选区域截图保存为bmp，返回文件路径
          "text"  — 框选区域检测颜色+截图，返回颜色和区域信息
        """
        super().__init__(parent, title="游戏交互 — 按ESC取消", style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR,
                         size=(1, 1), pos=(0, 0))
        self.dm = dm
        self.parent_frame = parent_frame
        self.mode = mode
        self.result = None
        self._start_pos = None
        self._dragging = False

        self._game_left = 0
        self._game_top = 0
        self._game_width = 900
        self._game_height = 580
        self._init_game_rect()

        screen = wx.GetDisplaySize()
        self.SetSize(screen)

        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._overlay_bmp = None
        self._capture_screen()

    def _init_game_rect(self):
        try:
            hwnd = getattr(self.parent_frame, 'click_hwnd', None)
            if hwnd and self.dm:
                rect = self.dm.GetWindowRect(int(hwnd))
                if rect and rect != 0:
                    left, top, right, bottom, found = rect
                    if int(found) == 1:
                        self._game_left = int(left)
                        self._game_top = int(top)
                        self._game_width = int(right) - int(left)
                        self._game_height = int(bottom) - int(top)
                        return
        except Exception:
            pass
        try:
            self._game_width = int(getattr(self.parent_frame, 'locationWidth', 900))
            self._game_height = int(getattr(self.parent_frame, 'locationHeight', 580))
        except Exception:
            pass

    def _screen_to_game(self, sx, sy):
        gx = int(sx - self._game_left)
        gy = int(sy - self._game_top)
        return max(0, min(gx, self._game_width - 1)), max(0, min(gy, self._game_height - 1))

    def _capture_screen(self):
        try:
            screen = wx.GetDisplaySize()
            self._overlay_bmp = wx.Bitmap(screen.x, screen.y)
            mem = wx.MemoryDC(self._overlay_bmp)
            mem.Blit(0, 0, screen.x, screen.y, wx.ScreenDC(), 0, 0)
            mem.SelectObject(wx.NullBitmap)
            del mem
        except Exception:
            self._overlay_bmp = None

    def _on_paint(self, e):
        dc = wx.PaintDC(self)
        if self._overlay_bmp:
            dc.DrawBitmap(self._overlay_bmp, 0, 0)
            dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 120)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(0, 0, *self.GetSize())

        if self._game_width > 0 and self._game_height > 0:
            dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 0)))
            dc.SetPen(wx.Pen(wx.Colour(0, 255, 100), 2))
            dc.DrawRectangle(self._game_left, self._game_top,
                             self._game_width, self._game_height)

        mode_hints = {"coord": "🖱 点击拾取坐标", "image": "🖱 框选区域截图", "text": "🖱 框选文字区域"}
        dc.SetTextForeground(wx.Colour(255, 255, 100))
        dc.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.DrawText(mode_hints.get(self.mode, ""), 20, 10)
        dc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        dc.SetTextForeground(wx.Colour(200, 200, 200))
        dc.DrawText("按 ESC 取消", 20, 35)

        if self._dragging and self._start_pos:
            cur = wx.GetMousePosition()
            dc.SetPen(wx.Pen(wx.Colour(0, 200, 255), 2, wx.PENSTYLE_SHORT_DASH))
            dc.SetBrush(wx.Brush(wx.Colour(0, 200, 255, 30)))
            x1, y1 = self._start_pos
            x2, y2 = cur.x, cur.y
            rx, ry = min(x1, x2), min(y1, y2)
            rw, rh = abs(x2 - x1), abs(y2 - y1)
            dc.DrawRectangle(rx, ry, rw, rh)
            dc.SetTextForeground(wx.Colour(0, 200, 255))
            dc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.DrawText(f"{rw} × {rh}", rx + 5, ry - 18)

        if self.mode == "coord":
            cur = wx.GetMousePosition()
            gx, gy = self._screen_to_game(cur.x, cur.y)
            dc.SetTextForeground(wx.Colour(255, 255, 0))
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            dc.DrawText(f"游戏坐标: x={gx}  y={gy}", cur.x + 15, cur.y - 25)

    def _on_left_down(self, e):
        pos = e.GetPosition()
        if self.mode == "coord":
            gx, gy = self._screen_to_game(pos.x, pos.y)
            self.result = {"type": "coord", "x": gx, "y": gy}
            self.EndModal(wx.ID_OK)
        else:
            self._start_pos = (pos.x, pos.y)
            self._dragging = True

    def _on_left_up(self, e):
        if not self._dragging or not self._start_pos:
            return
        self._dragging = False
        end = e.GetPosition()
        x1, y1 = self._start_pos
        x2, y2 = end.x, end.y
        left, top = min(x1, x2), min(y1, y2)
        right, bottom = max(x1, x2), max(y1, y2)
        if right - left < 5 or bottom - top < 5:
            return
        gx1, gy1 = self._screen_to_game(left, top)
        gx2, gy2 = self._screen_to_game(right, bottom)
        try:
            if self.mode == "image":
                self._do_capture_image(gx1, gy1, gx2, gy2)
            elif self.mode == "text":
                self._do_capture_text(gx1, gy1, gx2, gy2)
        except Exception:
            self.result = None
            self.EndModal(wx.ID_CANCEL)
            return
        self.EndModal(wx.ID_OK)

    def _on_motion(self, e):
        self.Refresh()

    def _on_key(self, e):
        if e.GetKeyCode() == wx.WXK_ESCAPE:
            self.result = None
            self.EndModal(wx.ID_CANCEL)

    def _do_capture_image(self, x1, y1, x2, y2):
        img_dir = os.path.join(SERVE_ASSETS, "images", "custom")
        os.makedirs(img_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%H%M%S")
        fname = f"capture_{ts}.bmp"
        fpath = os.path.join(img_dir, fname)
        rel_path = f"serveAssets/images/custom/{fname}"
        try:
            ret = self.dm.Capture(x1, y1, x2, y2, fpath)
            if ret == 1 or os.path.exists(fpath):
                self.result = {"type": "image", "path": rel_path, "abs_path": fpath}
            else:
                self._fallback_capture(x1, y1, x2, y2, fpath, rel_path)
        except Exception:
            self._fallback_capture(x1, y1, x2, y2, fpath, rel_path)

    def _fallback_capture(self, x1, y1, x2, y2, fpath, rel_path):
        try:
            if self._overlay_bmp:
                sx1 = x1 + self._game_left
                sy1 = y1 + self._game_top
                w, h = x2 - x1, y2 - y1
                sub_bmp = wx.Bitmap(w, h)
                src_dc = wx.MemoryDC(self._overlay_bmp)
                dst_dc = wx.MemoryDC(sub_bmp)
                dst_dc.Blit(0, 0, w, h, src_dc, sx1, sy1)
                dst_dc.SelectObject(wx.NullBitmap)
                src_dc.SelectObject(wx.NullBitmap)
                del src_dc, dst_dc
                sub_bmp.SaveFile(fpath, wx.BITMAP_TYPE_BMP)
                self.result = {"type": "image", "path": rel_path, "abs_path": fpath}
            else:
                self.result = {"type": "image", "path": rel_path, "abs_path": fpath, "error": "截图失败"}
        except Exception as ex:
            self.result = {"type": "image", "path": rel_path, "abs_path": fpath, "error": str(ex)}

    def _do_capture_text(self, x1, y1, x2, y2):
        color = self._auto_detect_color(x1, y1, x2, y2)
        temp_dir = os.path.join(SERVE_ASSETS, "images", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"_text_capture_{int(time.time()*1000)}.bmp")
        try:
            self.dm.Capture(x1, y1, x2, y2, temp_path)
        except Exception:
            temp_path = ""
        self.result = {
            "type": "text",
            "text": "",
            "color": color,
            "region": (x1, y1, x2, y2),
            "capture_path": temp_path if os.path.exists(temp_path) else "",
        }

    def _auto_detect_color(self, x1, y1, x2, y2):
        try:
            colors = {}
            step_x = max(1, (x2 - x1) // 12)
            step_y = max(1, (y2 - y1) // 6)
            for px in range(x1, x2, step_x):
                for py in range(y1, y2, step_y):
                    try:
                        c = self.dm.GetColor(int(px), int(py))
                        if c and len(str(c)) >= 6:
                            cs = str(c).upper()
                            r = int(cs[0:2], 16)
                            g = int(cs[2:4], 16)
                            b = int(cs[4:6], 16)
                            brightness = (r * 299 + g * 587 + b * 114) / 1000
                            if brightness > 40:
                                colors[cs] = colors.get(cs, 0) + 1
                    except Exception:
                        pass
            if colors:
                sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
                top_colors = [c for c, _ in sorted_colors[:4]]
                color_parts = [f"{c}-0A0A0A" for c in top_colors]
                return "|".join(color_parts)
        except Exception:
            pass
        return "ffffff-000000|ffff00-000000|00ff00-000000"


# ============================================================
# 代码生成器 + 注入器 (保留备用)
# ============================================================
class CodeInjector:
    def __init__(self, name, config):
        self.name = name
        self.cfg = config
        self.safe = re.sub(r'[^\w]', '_', name).rstrip('_') or "custom"

    def generate_methods(self):
        lines = []; ind = "    "
        entry = self.cfg.get("entry", {})
        city = entry.get("city", "洛阳")
        yizhan = entry.get("yizhan", "驿站城西")
        npc_img = entry.get("npc_image", "")
        fb_name = entry.get("fb_name", "")

        map_img = "serveAssets/images/zhengdian/luoyang.bmp"
        if "涿郡" in city: map_img = "serveAssets/images/zhengdian/zhuojun.bmp"
        elif "襄阳" in city: map_img = "serveAssets/images/zhengdian/xiangyang.bmp"
        elif "许昌" in city: map_img = "serveAssets/images/zhengdian/xuchang.bmp"

        lines.append(f'{ind}def _auto_{self.safe}_entry(self):')
        lines.append(f'{ind}    """自动生成: {self.name} - 入口"""')
        lines.append(f'{ind}    if not self.find_str({repr(city)}, self.dituLocation, 0):')
        lines.append(f'{ind}        self.go_in_ditu(')
        lines.append(f'{ind}            f"地图{city}",')
        lines.append(f'{ind}            self.get_resource_path({repr(map_img)}),')
        lines.append(f'{ind}            {repr(city)}, "", {repr(yizhan) if yizhan else ""}, True)')

        if fb_name:
            lines.append(f'{ind}    self.feiFb({repr(fb_name)}, True)')
            lines.append(f'{ind}    time.sleep(1)')
        elif npc_img:
            lines.append(f'{ind}    self.findAndClickPic(')
            lines.append(f'{ind}        {repr(city)},')
            lines.append(f'{ind}        self.get_resource_path({repr(npc_img)}),')
            lines.append(f'{ind}        self.get_resource_path({repr(npc_img)}),')
            lines.append(f'{ind}        self.gameBottomLocation,')
            lines.append(f'{ind}        "进入", self.gameBottomLocation,')
            lines.append(f'{ind}        "0.1,0.1", "tab")')

        lines.append(f'{ind}    return True')
        lines.append("")

        lines.append(f'{ind}def _auto_{self.safe}_loop(self):')
        lines.append(f'{ind}    """自动生成: {self.name} - 主循环"""')
        lines.append(f'{ind}    if self.check_stop_or_over(): return')
        lines.append(f'{ind}    with condition:')
        lines.append(f'{ind}        if self.stoped: condition.wait()')
        lines.append("")

        for si, stage in enumerate(self.cfg.get("stages", [])):
            map_name = stage.get("map_name", f"地图{si+1}")
            lines.append(f'{ind}    # ── 第{si+1}层: {map_name} ──')
            for m in stage.get("monsters", []):
                lines.extend(self._gen_monster(ind, map_name, m))
            trans = stage.get("transition", {})
            if trans and si < len(self.cfg["stages"]) - 1:
                click = trans.get("click_map_name", "")
                if click:
                    lines.append(f'{ind}    self.waitForAAndClickB1(')
                    lines.append(f'{ind}        {repr(click)}, {repr(click)},')
                    lines.append(f'{ind}        self.dituLocation, self.gameLeftLocation)')
                    lines.append("")
            lines.append("")
        return "\n".join(lines)

    def _gen_monster(self, ind, map_name, m):
        name = m.get("name", "?")
        images = m.get("images", "")
        region = m.get("region", "gameBottomLocation")
        if not region.startswith("self."): region = f"self.{region}"
        battle_end = m.get("battle_end", "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp")
        repeat = max(1, int(m.get("repeat", 3)))
        move_region = m.get("move_region", "0.1,0.12")
        move_key = m.get("move_key", "tab")

        if images:
            parts = [p.strip() for p in images.split("|") if p.strip()]
            if len(parts) > 1:
                img_code = "f\"" + "|".join(f"{{self.get_resource_path('{p}')}}" for p in parts) + "\""
            else:
                img_code = f"self.get_resource_path('{images}')"
        else:
            img_code = repr(name)

        be_parts = [p.strip() for p in battle_end.split("|") if p.strip()]
        if len(be_parts) > 1:
            be_code = "f\"" + "|".join(f"{{self.get_resource_path('{p}')}}" for p in be_parts) + "\""
        else:
            be_code = f"self.get_resource_path('{battle_end}')"

        lines = []
        for _ in range(repeat):
            lines.append(f"{ind}    self.findAndClickPic(")
            lines.append(f"{ind}        {repr(map_name)},")
            lines.append(f"{ind}        {repr(name)},")
            lines.append(f"{ind}        {img_code},")
            lines.append(f"{ind}        {region},")
            lines.append(f"{ind}        {be_code},")
            lines.append(f"{ind}        self.gameBottomLocation,")
            lines.append(f"{ind}        {repr(move_region)},")
            lines.append(f"{ind}        {repr(move_key)})")
        return lines

    def generate_dispatch(self, loop_mode):
        loop = self.cfg.get("loop", {})
        mode = loop.get("mode", "infinite")
        count = loop.get("count", 1)
        clear_every = loop.get("clear_bag_every", 0)

        lines = [f"        elif self.scriptName == {repr(self.name)}:",
                 f"            if not self._auto_{self.safe}_entry(): return"]
        if mode == "infinite":
            lines.append(f"            count = 0")
            lines.append(f"            while True:")
            lines.append(f"                if self.check_stop_or_over(): return")
            lines.append(f"                self._auto_{self.safe}_loop()")
            if clear_every:
                lines.append(f"                count += 1")
                lines.append(f"                if count % {clear_every} == 0:")
                lines.append(f"                    self.clearBag()")
        else:
            lines.append(f"            for _i in range({count}):")
            lines.append(f"                if self.check_stop_or_over(): return")
            lines.append(f"                self._auto_{self.safe}_loop()")
        lines.append("")
        return "\n".join(lines)

    def inject(self, loop_mode):
        with open(SERVE_SCRIPT, "r", encoding="utf-8") as f: content = f.read()
        content = _replace_between(content, TAG_METHODS_START, TAG_METHODS_END, self.generate_methods())
        content = _replace_between(content, TAG_DISPATCH_START, TAG_DISPATCH_END, self.generate_dispatch(loop_mode))
        backup = SERVE_SCRIPT + ".bak"
        if not os.path.exists(backup):
            with open(backup, "w", encoding="utf-8") as f:
                f.write(open(SERVE_SCRIPT, "r", encoding="utf-8").read())
        with open(SERVE_SCRIPT, "w", encoding="utf-8") as f: f.write(content)
        return True

    def remove(self):
        with open(SERVE_SCRIPT, "r", encoding="utf-8") as f: content = f.read()
        content = _replace_between(content, TAG_METHODS_START, TAG_METHODS_END, "")
        content = _replace_between(content, TAG_DISPATCH_START, TAG_DISPATCH_END, "")
        with open(SERVE_SCRIPT, "w", encoding="utf-8") as f: f.write(content)

def _replace_between(content, start_tag, end_tag, new_content):
    i0 = content.find(start_tag); i1 = content.find(end_tag)
    if i0 < 0 or i1 < 0: return content
    return content[:i0 + len(start_tag)] + "\n" + new_content + "\n" + content[i1:]


# ============================================================
# 注册表
# ============================================================
class ScriptRegistry:
    @staticmethod
    def load():
        if not os.path.exists(REGISTRY_FILE): return {}
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f: return json.load(f)
    @staticmethod
    def save(reg):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f: json.dump(reg, f, ensure_ascii=False, indent=2)
    @staticmethod
    def add(name, config):
        reg = ScriptRegistry.load()
        reg[name] = {"created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "config": config}
        ScriptRegistry.save(reg)
    @staticmethod
    def remove(name):
        reg = ScriptRegistry.load(); reg.pop(name, None); ScriptRegistry.save(reg)
    @staticmethod
    def list_names():
        return list(ScriptRegistry.load().keys())


# ============================================================
# GUI
# ============================================================
LOOP_MODES = ["🔄 一直打（无限循环）", "🔢 跑几轮就停"]

class ScriptFactoryDialog(wx.Frame):
    def __init__(self, parent_frame):
        super().__init__(None, title="脚本工厂", size=(1100, 750),
                         pos=(70, 30), style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(wx.Colour(243, 244, 248))
        icon_path = os.path.join(SERVE_ASSETS, "images", "menu_factory.png")
        if os.path.exists(icon_path):
            icon = wx.Icon(wx.Bitmap(wx.Image(icon_path).Scale(32, 32, wx.IMAGE_QUALITY_HIGH)))
            self.SetIcon(icon)
        self.parent_frame = parent_frame
        self.dm = getattr(parent_frame, "dm", None)
        self.selected_stage_index = -1
        self.selected_monster_index = -1
        self._template_applied = False
        self.config = {
            "type": "dungeon_run",
            "name": "",
            "entry": {"city": "洛阳", "yizhan": "", "npc_image": "", "fb_name": "", "is_elite": False, "is_fei": True},
            "confirm_map": "",
            "sub_maps": [],
            "exit_map": "",
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [],
            "fallback": "官渡",
        }
        self._build()

    def _get_dm(self):
        if self.dm:
            return self.dm
        if self.parent_frame and hasattr(self.parent_frame, "dm"):
            self.dm = self.parent_frame.dm
            return self.dm
        return None

    def _build(self):
        panel = wx.Panel(self); panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        ms = wx.BoxSizer(wx.VERTICAL)

        hdr = wx.Panel(panel, size=(-1, 36)); hdr.SetBackgroundColour(wx.Colour(225, 228, 235))
        hs = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(hdr, label="脚本工厂 — 选模板，填配置，一键保存")
        t.SetForegroundColour(wx.Colour(50, 80, 140))
        t.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        hs.Add(t, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        hs.AddStretchSpacer()
        self.btn_save = wx.Button(hdr, label="💾 保存脚本", size=(120, 28), style=wx.BORDER_NONE)
        self.btn_save.SetBackgroundColour(wx.Colour(39, 174, 96))
        self.btn_save.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_save.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        hs.Add(self.btn_save, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self.btn_trial = wx.Button(hdr, label="▶ 试运行", size=(90, 28), style=wx.BORDER_NONE)
        self.btn_trial.SetBackgroundColour(wx.Colour(41, 128, 185))
        self.btn_trial.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_trial.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.btn_trial.Bind(wx.EVT_BUTTON, self._on_trial_run)
        hs.Add(self.btn_trial, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        hdr.SetSizer(hs); ms.Add(hdr, 0, wx.EXPAND)

        body = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.Panel(panel, size=(300, -1)); left.SetBackgroundColour(wx.Colour(232, 235, 240))
        self._build_tree(left); body.Add(left, 0, wx.EXPAND | wx.RIGHT, 2)

        self.editor_panel = scrolled.ScrolledPanel(panel, -1)
        self.editor_panel.SetBackgroundColour(wx.Colour(248, 249, 252))
        self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        body.Add(self.editor_panel, 1, wx.EXPAND)
        ms.Add(body, 1, wx.EXPAND | wx.ALL, 4)

        btm = wx.Panel(panel, size=(-1, 36)); btm.SetBackgroundColour(wx.Colour(225, 228, 235))
        bs = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(wx.StaticText(btm, label="脚本名字:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        self.txt_name = wx.TextCtrl(btm, size=(140, 26)); self.txt_name.SetHint("如: 觉醒")
        bs.Add(self.txt_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        bs.AddStretchSpacer()
        btn_open = wx.Button(btm, label="📂 打开已有", size=(90, 26), style=wx.BORDER_NONE)
        btn_open.SetBackgroundColour(wx.Colour(215, 218, 226)); btn_open.SetForegroundColour(wx.Colour(60, 65, 75))
        btn_open.Bind(wx.EVT_BUTTON, self._on_open_existing)
        bs.Add(btn_open, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        btm.SetSizer(bs); ms.Add(btm, 0, wx.EXPAND)
        panel.SetSizer(ms); self._refresh_all()

    # ========== 左侧流程树 ==========
    def _build_tree(self, parent):
        sz = wx.BoxSizer(wx.VERTICAL)
        l = wx.StaticText(parent, label="📋 脚本流程")
        l.SetForegroundColour(wx.Colour(50, 80, 140))
        l.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sz.Add(l, 0, wx.ALL, 8)
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        for lbl, h in [("+ 加楼层", self._add_stage), ("🗑 删楼层", self._del_stage)]:
            b = wx.Button(parent, label=lbl, size=(75, 28), style=wx.BORDER_NONE)
            b.SetBackgroundColour(wx.Colour(215, 218, 226)); b.SetForegroundColour(wx.Colour(60, 65, 75))
            b.Bind(wx.EVT_BUTTON, h); btn_row.Add(b, 0, wx.LEFT | wx.RIGHT, 2)
        sz.Add(btn_row, 0, wx.LEFT | wx.BOTTOM, 6)
        self.tp = scrolled.ScrolledPanel(parent, -1)
        self.tp.SetBackgroundColour(wx.Colour(232, 235, 240)); self.tp.SetupScrolling(scroll_y=True, rate_y=20)
        self.ts = wx.BoxSizer(wx.VERTICAL); self.tp.SetSizer(self.ts); sz.Add(self.tp, 1, wx.EXPAND)
        parent.SetSizer(sz)

    def _refresh_tree(self):
        self.ts.Clear(True)
        e = self.config["entry"]
        city = e.get("city","?"); fb = e.get("fb_name",""); npc = e.get("npc_image","")
        el = f"📍 去副本: {city} → "
        if fb:
            el += f"{fb}"
        elif npc:
            el += os.path.basename(npc)
        else:
            el += e.get("yizhan", "?")
        entry_card = self._card(el, (41,128,185))
        entry_card.Bind(wx.EVT_LEFT_DOWN, lambda e: self._select_stage(-1))
        self._make_clickable(entry_card)
        self.ts.Add(entry_card, 0, wx.EXPAND | wx.BOTTOM, 3)
        for i, s in enumerate(self.config["stages"]):
            sel = (i == self.selected_stage_index)
            bg = (231,76,60) if sel else (41,128,185)
            c = wx.Panel(self.tp, size=(-1,-1)); c.SetBackgroundColour(wx.Colour(232, 235, 240))
            sv = wx.BoxSizer(wx.VERTICAL)
            h = wx.Panel(c, size=(-1,26)); h.SetBackgroundColour(bg)
            hs2 = wx.BoxSizer(wx.HORIZONTAL)
            hl = wx.StaticText(h, label=f"🗺️ {s.get('map_name',f'第{i+1}层')}  ›")
            hl.SetForegroundColour((255,255,255)); hl.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            hs2.Add(hl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8); h.SetSizer(hs2)
            h.Bind(wx.EVT_LEFT_DOWN, lambda e,si=i: self._select_stage(si))
            self._make_clickable(h)
            sv.Add(h, 0, wx.EXPAND)
            for mi, m in enumerate(s.get("monsters",[])):
                mc = wx.Panel(c, size=(-1,24)); mc.SetBackgroundColour((238, 240, 244))
                ms2 = wx.BoxSizer(wx.HORIZONTAL)
                mname = m.get("name","?") if m.get("detect_mode","text") == "text" else os.path.basename(m.get("images","?"))
                ml = wx.StaticText(mc, label=f"  ✏️ {mname} ×{m.get('repeat',1)}")
                ml.SetForegroundColour((180,80,10)); ml.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                ms2.Add(ml, 1, wx.ALIGN_CENTER_VERTICAL); mc.SetSizer(ms2)
                mc.Bind(wx.EVT_LEFT_DOWN, lambda e,si=i,mi2=mi: self._select_monster(si,mi2))
                self._make_clickable(mc)
                sv.Add(mc, 0, wx.EXPAND | wx.LEFT, 16)
            trans = s.get("transition",{})
            if trans and trans.get("click_map_name"):
                tc = wx.Panel(c, size=(-1,20)); tc.SetBackgroundColour((235, 238, 242))
                tt = wx.StaticText(tc, label=f"  ◆ 下一层→{trans.get('click_map_name','?')}")
                tt.SetForegroundColour((70,75,85)); tt.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                tc_s = wx.BoxSizer(wx.HORIZONTAL); tc_s.Add(tt, 1, wx.ALIGN_CENTER_VERTICAL)
                tc.SetSizer(tc_s); sv.Add(tc, 0, wx.EXPAND | wx.LEFT, 16)
            sv.AddSpacer(2); c.SetSizer(sv); self.ts.Add(c, 0, wx.EXPAND | wx.BOTTOM, 2)
        loop = self.config["loop"]
        mode_str = "一直打" if loop.get("mode","infinite") == "infinite" else f"跑{loop.get('count',1)}轮"
        ll = f"🏁 {mode_str}"
        if loop.get("clear_bag_every"): ll += f" | 每{loop['clear_bag_every']}次清包"
        self.ts.Add(self._card(ll, (39,174,96)), 0, wx.EXPAND | wx.BOTTOM, 3)
        self.ts.Layout(); self.tp.SetupScrolling(scroll_y=True, rate_y=20); self.tp.Refresh()

    def _make_clickable(self, panel):
        panel.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        panel._original_bg = panel.GetBackgroundColour()
        panel.Bind(wx.EVT_ENTER_WINDOW, lambda e, p=panel: self._on_hover_enter(p))
        panel.Bind(wx.EVT_LEAVE_WINDOW, lambda e, p=panel: self._on_hover_leave(p))
        for child in panel.GetChildren():
            if isinstance(child, wx.StaticText):
                child.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def _on_hover_enter(self, panel):
        orig = panel._original_bg
        r, g, b = orig.Red(), orig.Green(), orig.Blue()
        panel.SetBackgroundColour(wx.Colour(max(r-12, 0), max(g-12, 0), max(b-12, 0)))
        panel.Refresh()

    def _on_hover_leave(self, panel):
        panel.SetBackgroundColour(panel._original_bg)
        panel.Refresh()

    def _card(self, text, color):
        c = wx.Panel(self.tp, size=(-1,28)); c.SetBackgroundColour(color)
        s = wx.BoxSizer(wx.HORIZONTAL)
        l = wx.StaticText(c, label=text); l.SetForegroundColour((255,255,255))
        l.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        s.Add(l, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8); c.SetSizer(s); return c

    # ========== 右侧编辑器 ==========
    def _refresh_editor(self):
        self.editor_sizer.Clear(True)
        self.editor_panel.Freeze()
        self._render_breadcrumb()
        if self.selected_stage_index < 0: self._render_entry()
        elif self.selected_monster_index >= 0: self._render_monster()
        else: self._render_stage()
        self.editor_sizer.Layout()
        self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        self.editor_panel.Thaw()
        self.editor_panel.Refresh()

    def _render_breadcrumb(self):
        bar = wx.Panel(self.editor_panel, size=(-1, 32))
        bar.SetBackgroundColour(wx.Colour(225, 228, 235))
        bs = wx.BoxSizer(wx.HORIZONTAL)

        if self.selected_stage_index < 0:
            lbl = wx.StaticText(bar, label="📋 入口配置")
            lbl.SetForegroundColour(wx.Colour(50, 80, 140))
            lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            bs.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        elif self.selected_monster_index >= 0:
            btn_back = wx.Button(bar, label="← 返回楼层", size=(-1, 24), style=wx.BORDER_NONE)
            btn_back.SetBackgroundColour(wx.Colour(215, 218, 226))
            btn_back.SetForegroundColour(wx.Colour(60, 65, 75))
            btn_back.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            btn_back.Bind(wx.EVT_BUTTON, lambda e: self._go_back())
            bs.Add(btn_back, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
            sep1 = wx.StaticText(bar, label="  ›  ")
            sep1.SetForegroundColour(wx.Colour(140, 145, 155))
            bs.Add(sep1, 0, wx.ALIGN_CENTER_VERTICAL)
            s = self.config["stages"][self.selected_stage_index]
            lbl1 = wx.StaticText(bar, label=f"🗺️ 第{self.selected_stage_index+1}层")
            lbl1.SetForegroundColour(wx.Colour(60, 65, 75))
            lbl1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            lbl1.Bind(wx.EVT_LEFT_DOWN, lambda e: self._go_back())
            bs.Add(lbl1, 0, wx.ALIGN_CENTER_VERTICAL)
            sep2 = wx.StaticText(bar, label="  ›  ")
            sep2.SetForegroundColour(wx.Colour(140, 145, 155))
            bs.Add(sep2, 0, wx.ALIGN_CENTER_VERTICAL)
            m = s["monsters"][self.selected_monster_index]
            mname = m.get("name", "?") if m.get("detect_mode", "text") == "text" else os.path.basename(m.get("images", "?"))
            lbl2 = wx.StaticText(bar, label=f"🎯 {mname}")
            lbl2.SetForegroundColour(wx.Colour(50, 80, 140))
            lbl2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            bs.Add(lbl2, 0, wx.ALIGN_CENTER_VERTICAL)
        else:
            btn_back = wx.Button(bar, label="← 返回入口", size=(-1, 24), style=wx.BORDER_NONE)
            btn_back.SetBackgroundColour(wx.Colour(215, 218, 226))
            btn_back.SetForegroundColour(wx.Colour(60, 65, 75))
            btn_back.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            btn_back.Bind(wx.EVT_BUTTON, lambda e: self._go_back())
            bs.Add(btn_back, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
            sep1 = wx.StaticText(bar, label="  ›  ")
            sep1.SetForegroundColour(wx.Colour(140, 145, 155))
            bs.Add(sep1, 0, wx.ALIGN_CENTER_VERTICAL)
            s = self.config["stages"][self.selected_stage_index]
            lbl1 = wx.StaticText(bar, label=f"🗺️ 第{self.selected_stage_index+1}层: {s.get('map_name', '')}")
            lbl1.SetForegroundColour(wx.Colour(50, 80, 140))
            lbl1.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            bs.Add(lbl1, 0, wx.ALIGN_CENTER_VERTICAL)

        bs.AddStretchSpacer()
        bar.SetSizer(bs)
        self.editor_sizer.Add(bar, 0, wx.EXPAND | wx.BOTTOM, 2)

    def _go_back(self):
        if self.selected_monster_index >= 0:
            self.selected_monster_index = -1
        elif self.selected_stage_index >= 0:
            self.selected_stage_index = -1
        self._refresh_all()

    def _render_step_indicator(self, current_step):
        bar = wx.Panel(self.editor_panel, size=(-1, 34))
        bar.SetBackgroundColour(wx.Colour(225, 228, 235))
        bs = wx.BoxSizer(wx.HORIZONTAL)
        steps = ["1.选模板", "2.配入口", "3.配楼层", "4.配怪物", "5.保存"]
        for i, label in enumerate(steps):
            step_num = i + 1
            if step_num < current_step:
                prefix = "✅ "
                color = wx.Colour(39, 174, 96)
            elif step_num == current_step:
                prefix = "📍 "
                color = wx.Colour(41, 128, 185)
            else:
                prefix = "○ "
                color = wx.Colour(150, 155, 165)
            lbl = wx.StaticText(bar, label=f"{prefix}{label}")
            lbl.SetForegroundColour(color)
            lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            bs.Add(lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
            if i < len(steps) - 1:
                arrow = wx.StaticText(bar, label="›")
                arrow.SetForegroundColour(wx.Colour(140, 145, 155))
                arrow.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                bs.Add(arrow, 0, wx.ALIGN_CENTER_VERTICAL)
        bar.SetSizer(bs)
        self.editor_sizer.Add(bar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 4)

    def _title(self, text):
        l = wx.StaticText(self.editor_panel, label=text)
        l.SetForegroundColour(wx.Colour(50, 80, 140))
        l.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.editor_sizer.Add(l, 0, wx.ALL, 8)

    def _lbl(self, text, tip=""):
        label_text = text if not tip else f"{text}  (💡 {tip})"
        l = wx.StaticText(self.editor_panel, label=label_text)
        l.SetForegroundColour(wx.Colour(70, 75, 85))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.editor_sizer.Add(l, 0, wx.LEFT | wx.TOP, 8)

    def _required_lbl(self, text, tip=""):
        label_text = f"❗ {text}" if not tip else f"❗ {text}  (💡 {tip})"
        l = wx.StaticText(self.editor_panel, label=label_text)
        l.SetForegroundColour(wx.Colour(160, 120, 0))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.editor_sizer.Add(l, 0, wx.LEFT | wx.TOP, 8)

    def _txt(self, value="", hint=""):
        t = wx.TextCtrl(self.editor_panel, size=(-1, 28))
        t.SetValue(str(value)); t.SetBackgroundColour(wx.Colour(255, 255, 255)); t.SetForegroundColour(wx.Colour(40, 42, 50))
        if hint: t.SetHint(hint)
        self.editor_sizer.Add(t, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return t

    def _combo(self, choices, value=""):
        c = wx.ComboBox(self.editor_panel, size=(-1, 28), choices=choices, style=wx.CB_DROPDOWN)
        c.SetValue(str(value)); c.SetBackgroundColour(wx.Colour(255, 255, 255)); c.SetForegroundColour(wx.Colour(40, 42, 50))
        self.editor_sizer.Add(c, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return c

    def _search(self, value="", hint="输入关键词搜索图片..."):
        si = SearchInput(self.editor_panel, value=value, hint=hint)
        self.editor_sizer.Add(si, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return si

    def _raw_lbl(self, parent, text, tip=""):
        label_text = text if not tip else f"{text}  (💡 {tip})"
        l = wx.StaticText(parent, label=label_text)
        l.SetForegroundColour(wx.Colour(70, 75, 85))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        return l

    def _raw_required_lbl(self, parent, text, tip=""):
        label_text = f"❗ {text}" if not tip else f"❗ {text}  (💡 {tip})"
        l = wx.StaticText(parent, label=label_text)
        l.SetForegroundColour(wx.Colour(160, 120, 0))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        return l

    def _raw_txt(self, parent, value="", hint=""):
        t = wx.TextCtrl(parent, size=(-1, 28))
        t.SetValue(str(value)); t.SetBackgroundColour(wx.Colour(255, 255, 255)); t.SetForegroundColour(wx.Colour(40, 42, 50))
        if hint: t.SetHint(hint)
        return t

    def _raw_combo(self, parent, choices, value=""):
        c = wx.ComboBox(parent, size=(-1, 28), choices=choices, style=wx.CB_DROPDOWN)
        c.SetValue(str(value)); c.SetBackgroundColour(wx.Colour(255, 255, 255)); c.SetForegroundColour(wx.Colour(40, 42, 50))
        return c

    def _game_btn(self, label, callback):
        b = wx.Button(self.editor_panel, label=label, size=(-1, 28), style=wx.BORDER_NONE)
        b.SetBackgroundColour(wx.Colour(155, 89, 182))
        b.SetForegroundColour(wx.Colour(255, 255, 255))
        b.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        b.Bind(wx.EVT_BUTTON, callback)
        self.editor_sizer.Add(b, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return b

    def _do_game_capture(self, mode, callback):
        dm = self._get_dm()
        if not dm:
            wx.MessageBox("未连接到游戏窗口，请先启动游戏并绑定窗口", "提示")
            return
        try:
            dlg = GameCaptureDialog(self, dm, self.parent_frame, mode=mode)
            result = None
            if dlg.ShowModal() == wx.ID_OK:
                result = dlg.result
            dlg.Destroy()
            if result:
                callback(result)
        except Exception as ex:
            wx.MessageBox(f"游戏交互失败: {ex}", "错误")

    # ========== 模板选择 ==========
    def _render_template_picker(self):
        self._title("📋 第一步：选一个模板")
        tip = wx.StaticText(self.editor_panel, label="选一个最像你要打的副本，自动填好大部分配置 👇")
        tip.SetForegroundColour(wx.Colour(50, 80, 140))
        tip.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.editor_sizer.Add(tip, 0, wx.LEFT | wx.BOTTOM, 8)

        grid = wx.FlexGridSizer(rows=0, cols=3, hgap=8, vgap=6)
        for tname, tpl in TEMPLATES.items():
            card = wx.Panel(self.editor_panel, size=(-1, 52))
            card.SetBackgroundColour(wx.Colour(228, 232, 245))
            cs = wx.BoxSizer(wx.VERTICAL)
            h_row = wx.BoxSizer(wx.HORIZONTAL)
            h_lbl = wx.StaticText(card, label=f"{tpl['icon']} {tname}")
            h_lbl.SetForegroundColour(wx.Colour(40, 42, 50))
            h_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            h_row.Add(h_lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
            cs.Add(h_row, 0, wx.EXPAND | wx.TOP, 4)
            d_lbl = wx.StaticText(card, label=f"  {tpl['desc']}")
            d_lbl.SetForegroundColour(wx.Colour(60, 65, 75))
            d_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            cs.Add(d_lbl, 0, wx.EXPAND | wx.BOTTOM, 4)
            card.SetSizer(cs)
            card.Bind(wx.EVT_LEFT_DOWN, lambda e, n=tname: self._apply_template(n))
            h_lbl.Bind(wx.EVT_LEFT_DOWN, lambda e, n=tname: self._apply_template(n))
            d_lbl.Bind(wx.EVT_LEFT_DOWN, lambda e, n=tname: self._apply_template(n))
            grid.Add(card, 1, wx.EXPAND)
        grid.AddGrowableCol(0); grid.AddGrowableCol(1); grid.AddGrowableCol(2)
        self.editor_sizer.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        sep = wx.StaticLine(self.editor_panel, size=(-1, 1))
        sep.SetBackgroundColour(wx.Colour(205, 208, 218))
        self.editor_sizer.Add(sep, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

    def _apply_template(self, template_name):
        tpl = TEMPLATES.get(template_name)
        if not tpl:
            return
        if self.config.get("stages"):
            if wx.MessageBox("当前已有配置，应用模板会覆盖所有内容，确定吗？", "确认", wx.YES_NO) != wx.YES:
                return
        new_config = copy.deepcopy(tpl["config"])
        name = self.txt_name.GetValue().strip()
        if name:
            new_config["name"] = name
        self.config = new_config
        self._template_applied = True
        self.selected_stage_index = -1
        self.selected_monster_index = -1
        self._refresh_all()

    # ========== 入口配置 ==========
    def _render_entry(self):
        self._render_template_picker()

        if not self.config.get("stages") and not self._template_applied:
            tip = wx.StaticText(self.editor_panel, label="👆 先选一个模板吧！选完后下面的配置会自动展开")
            tip.SetForegroundColour(wx.Colour(160, 120, 0))
            tip.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.editor_sizer.Add(tip, 0, wx.ALL, 16)
            return

        e = self.config["entry"]
        self._render_step_indicator(2)
        self._title("📍 第二步：怎么去副本")
        self._lbl("从哪个城市出发", "可以选文字或图片")
        self._render_dual_input("city", e.get("city", "洛阳"),
                                e.get("city_mode", "text"),
                                "搜字库: 洛阳 / 许昌 / 城西 ...",
                                "搜图片: luoyang / xuchang ...",
                                lambda v: self._set_entry("city", v),
                                get_value=lambda: self.config["entry"].get("city", ""),
                                on_mode_change=lambda m: self._set_entry("city_mode", m))
        self._lbl("副本名字（直接飞过去的，不用走路）", "填了这个就不用填下面NPC，可以选文字或图片")
        self._render_dual_input("fb_name", e.get("fb_name", ""),
                                e.get("fb_name_mode", "text"),
                                "搜字库: 曹操大帐 / 魔镜 ...",
                                "搜图片: caocao / mojing ...",
                                lambda v: self._set_entry("fb_name", v),
                                get_value=lambda: self.config["entry"].get("fb_name", ""),
                                on_mode_change=lambda m: self._set_entry("fb_name_mode", m))
        self._lbl("是不是精英副本")
        c_elite = wx.ComboBox(self.editor_panel, size=(-1, 28), choices=["否", "是"], style=wx.CB_READONLY)
        c_elite.SetValue("是" if e.get("is_elite", False) else "否")
        c_elite.SetBackgroundColour(wx.Colour(255, 255, 255)); c_elite.SetForegroundColour(wx.Colour(40, 42, 50))
        c_elite.Bind(wx.EVT_COMBOBOX, lambda ev: self._set_entry("is_elite", c_elite.GetSelection() == 1))
        self.editor_sizer.Add(c_elite, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        self._lbl("找哪个NPC进副本", "不飞副本时用，可以选文字或图片")
        self._render_dual_input("npc_image", e.get("npc_image", ""),
                                e.get("npc_image_mode", "image"),
                                "搜字库: 传送 / 入口 / NPC名字 ...",
                                "搜图片: caocao / xiao / hbj ...",
                                lambda v: self._set_entry("npc_image", v),
                                get_value=lambda: self.config["entry"].get("npc_image", ""),
                                on_mode_change=lambda m: self._set_entry("npc_image_mode", m))

        self._title("🚪 进副本和出副本的判断")
        self._required_lbl("怎么确认已经进副本了", "右上角小地图上显示的字或图，脚本靠它判断进副本成功")
        self._render_dual_input("confirm_map", self.config.get("confirm_map", ""),
                                self.config.get("confirm_map_mode", "text"),
                                "搜字库: 镜像地层 / 曹操大帐 ...",
                                "搜图片: jingxiang / caocao_map ...",
                                lambda v: self._set_config("confirm_map", v))

        self._required_lbl("出副本后等什么地图", "出副本后脚本会等这个地图出现，如: 城西、官渡")
        self._render_dual_input("exit_map", self.config.get("exit_map", ""),
                                self.config.get("exit_map_mode", "text"),
                                "搜字库: 城西 / 官渡 ...",
                                "搜图片: chengxi / guandu ...",
                                lambda v: self._set_config("exit_map", v))

        self._lbl("打完了去哪里", "通常填官渡")
        c8 = self._combo(FALLBACK_CHOICES, self.config.get("fallback", "官渡"))
        def on_fallback_change(ev):
            self._set_config("fallback", c8.GetValue().strip())
        c8.Bind(wx.EVT_COMBOBOX, on_fallback_change)
        c8.Bind(wx.EVT_KILL_FOCUS, on_fallback_change)

        loop_toggle = wx.Button(self.editor_panel, label="▶ ⚙️ 循环和清包（一般不用改，点我展开）", size=(-1, 26), style=wx.BORDER_NONE)
        loop_toggle.SetBackgroundColour(wx.Colour(215, 218, 226))
        loop_toggle.SetForegroundColour(wx.Colour(60, 65, 75))
        loop_toggle.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.editor_sizer.Add(loop_toggle, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        loop_panel = wx.Panel(self.editor_panel)
        loop_panel.SetBackgroundColour(wx.Colour(240, 242, 246))
        loop_sizer = wx.BoxSizer(wx.VERTICAL)
        loop = self.config["loop"]
        cbo = wx.ComboBox(loop_panel, size=(-1, 28), choices=LOOP_MODES, style=wx.CB_READONLY)
        cbo.SetValue(LOOP_MODES[0] if loop.get("mode", "infinite") == "infinite" else LOOP_MODES[1])
        cbo.SetBackgroundColour(wx.Colour(255, 255, 255)); cbo.SetForegroundColour(wx.Colour(40, 42, 50))
        loop_sizer.Add(cbo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        count_lbl = self._raw_lbl(loop_panel, "跑几轮")
        t5 = self._raw_txt(loop_panel, str(loop.get("count", 1)))
        t5.Bind(wx.EVT_TEXT, lambda ev: self._set_loop("count", int(ev.GetString() or "1")))
        loop_sizer.Add(count_lbl, 0, wx.LEFT | wx.TOP, 8)
        loop_sizer.Add(t5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        if loop.get("mode") == "infinite":
            count_lbl.Hide()
            t5.Hide()
        loop_sizer.Add(self._raw_lbl(loop_panel, "打几轮清一次背包（0=不清）"), 0, wx.LEFT | wx.TOP, 8)
        t6b = self._raw_txt(loop_panel, str(loop.get("clear_bag_every", 15)))
        t6b.Bind(wx.EVT_TEXT, lambda ev: self._set_loop("clear_bag_every", int(ev.GetString() or "0")))
        loop_sizer.Add(t6b, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        loop_panel.SetSizer(loop_sizer)
        loop_panel.Hide()
        self.editor_sizer.Add(loop_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        def on_loop_mode_change(e):
            new_mode = ["infinite", "custom_count"][min(cbo.GetSelection(), 1)]
            self.config["loop"]["mode"] = new_mode
            if new_mode == "infinite":
                count_lbl.Hide()
                t5.Hide()
            else:
                count_lbl.Show()
                t5.Show()
            loop_sizer.Layout()
            loop_panel.Layout()
        cbo.Bind(wx.EVT_COMBOBOX, on_loop_mode_change)

        def toggle_loop(e):
            if loop_panel.IsShown():
                loop_panel.Hide()
                loop_toggle.SetLabel("▶ ⚙️ 循环和清包（一般不用改，点我展开）")
            else:
                loop_panel.Show()
                loop_toggle.SetLabel("▼ ⚙️ 循环和清包（点我收起）")
            self.editor_sizer.Layout()
            self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        loop_toggle.Bind(wx.EVT_BUTTON, toggle_loop)

        nav = wx.Panel(self.editor_panel, size=(-1, 40))
        nav.SetBackgroundColour(wx.Colour(248, 249, 252))
        ns = wx.BoxSizer(wx.HORIZONTAL)
        ns.AddStretchSpacer()
        next_btn = wx.Button(nav, label="下一步：配置楼层 →", size=(-1, 36), style=wx.BORDER_NONE)
        next_btn.SetBackgroundColour(wx.Colour(41, 128, 185))
        next_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        next_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        next_btn.Bind(wx.EVT_BUTTON, lambda e: self._go_to_stages())
        ns.Add(next_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        nav.SetSizer(ns)
        self.editor_sizer.Add(nav, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 12)

    def _render_dual_input(self, config_key, value, mode, text_hint, image_hint, on_change, get_value=None, on_mode_change=None):
        mode_row = wx.Panel(self.editor_panel, size=(-1, 28))
        mode_row.SetBackgroundColour(wx.Colour(240, 242, 246))
        mode_rs = wx.BoxSizer(wx.HORIZONTAL)
        btn_text = wx.Button(mode_row, label="📝 文字", size=(70, 24), style=wx.BORDER_NONE)
        btn_image = wx.Button(mode_row, label="🖼️ 图片", size=(70, 24), style=wx.BORDER_NONE)

        def update_mode_btns(active):
            if active == "text":
                btn_text.SetBackgroundColour(wx.Colour(41, 128, 185))
                btn_text.SetForegroundColour(wx.Colour(255, 255, 255))
                btn_image.SetBackgroundColour(wx.Colour(215, 218, 226))
                btn_image.SetForegroundColour(wx.Colour(60, 65, 75))
            else:
                btn_image.SetBackgroundColour(wx.Colour(41, 128, 185))
                btn_image.SetForegroundColour(wx.Colour(255, 255, 255))
                btn_text.SetBackgroundColour(wx.Colour(215, 218, 226))
                btn_text.SetForegroundColour(wx.Colour(60, 65, 75))

        update_mode_btns(mode)
        btn_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        btn_image.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        mode_rs.Add(btn_text, 0, wx.RIGHT, 2)
        mode_rs.Add(btn_image, 0)
        mode_rs.AddStretchSpacer()
        mode_row.SetSizer(mode_rs)
        self.editor_sizer.Add(mode_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        input_row = wx.Panel(self.editor_panel, size=(-1, 28))
        input_row.SetBackgroundColour(wx.Colour(240, 242, 246))
        input_rs = wx.BoxSizer(wx.HORIZONTAL)
        input_row.SetSizer(input_rs)

        def get_current_value():
            if get_value:
                return get_value()
            return self.config.get(config_key, value)

        def build_input(new_mode):
            for child in input_row.GetChildren():
                child.Destroy()
            input_rs.Clear()
            cur_val = get_current_value()
            if new_mode == "text":
                fi = FontSearchInput(input_row, value=cur_val, hint=text_hint)
                input_rs.Add(fi, 1, wx.EXPAND | wx.RIGHT, 2)
                gb = wx.Button(input_row, label="🎮", size=(32, 28), style=wx.BORDER_NONE)
                gb.SetBackgroundColour(wx.Colour(155, 89, 182))
                gb.SetForegroundColour(wx.Colour(255, 255, 255))
                gb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                gb.SetToolTip("从游戏画面框选文字并录入字库")
                gb.Bind(wx.EVT_BUTTON, lambda e: self._do_game_capture("text", lambda r: self._fill_font_result(r, fi)))
                input_rs.Add(gb, 0)
                fi.Bind(wx.EVT_TEXT, lambda ev: on_change(fi.GetValue()))
            else:
                si = SearchInput(input_row, value=cur_val, hint=image_hint)
                input_rs.Add(si, 1, wx.EXPAND | wx.RIGHT, 2)
                gb = wx.Button(input_row, label="🎮", size=(32, 28), style=wx.BORDER_NONE)
                gb.SetBackgroundColour(wx.Colour(155, 89, 182))
                gb.SetForegroundColour(wx.Colour(255, 255, 255))
                gb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                gb.SetToolTip("从游戏画面框选区域截图")
                gb.Bind(wx.EVT_BUTTON, lambda e: self._do_game_capture("image", lambda r: self._fill_image_result(r, si)))
                input_rs.Add(gb, 0)
                si.Bind(wx.EVT_TEXT, lambda ev: on_change(si.GetValue()))
            input_row.Layout()
            input_row.Refresh()

        build_input(mode)

        def switch_to_text(e):
            if on_mode_change:
                on_mode_change("text")
            else:
                self._set_config(config_key + "_mode", "text")
            update_mode_btns("text")
            build_input("text")

        def switch_to_image(e):
            if on_mode_change:
                on_mode_change("image")
            else:
                self._set_config(config_key + "_mode", "image")
            update_mode_btns("image")
            build_input("image")

        btn_text.Bind(wx.EVT_BUTTON, switch_to_text)
        btn_image.Bind(wx.EVT_BUTTON, switch_to_image)
        self.editor_sizer.Add(input_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

    def _go_to_stages(self):
        if not self.config.get("stages"):
            self._add_stage()
        else:
            self.selected_stage_index = 0
            self.selected_monster_index = -1
        self._refresh_all()

    def _fill_font_result(self, result, font_input):
        global _font_index
        color = result.get("color", "ffffff-0A0A0A")
        capture_path = result.get("capture_path", "")
        region = result.get("region", (0, 0, 0, 0))

        dlg = TextInputDialog(self, detected_color=color, captured_bmp_path=capture_path)
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetText()
            if text:
                font_idx = _build_font_index()
                if text not in font_idx:
                    self._try_add_font_entry(text, color, region, capture_path)
                    _font_index = None
                font_input.SetValue(text)
                evt = wx.CommandEvent(wx.wxEVT_TEXT, font_input.tc.GetId())
                wx.PostEvent(font_input.tc, evt)
        dlg.Destroy()

    # ========== 楼层配置 ==========
    def _render_stage(self):
        s = self.config["stages"][self.selected_stage_index]
        self._render_step_indicator(3)
        self._title(f"🗺️ 第{self.selected_stage_index+1}层")
        self._required_lbl("这一层叫什么（屏幕右上角显示的字或图）", "可以选文字或图片")
        self._render_dual_input("map_name", s.get("map_name", ""),
                                s.get("map_name_mode", "text"),
                                "搜字库: 曹操大帐 / 镜像地层 ...",
                                "搜图片: caocao_map / jingxiang ...",
                                lambda v: self._set_stage("map_name", v),
                                get_value=lambda: self.config["stages"][self.selected_stage_index].get("map_name", ""),
                                on_mode_change=lambda m: self._set_stage("map_name_mode", m))

        self._title("🎯 这一层打什么怪")
        for mi, m in enumerate(s.get("monsters", [])):
            c = wx.Panel(self.editor_panel, size=(-1, 32)); c.SetBackgroundColour(wx.Colour(240, 242, 246))
            cs = wx.BoxSizer(wx.HORIZONTAL)
            mname = m.get("name","?") if m.get("detect_mode","text") == "text" else os.path.basename(m.get("images","?"))
            edit_icon = wx.StaticText(c, label="✏️")
            edit_icon.SetForegroundColour(wx.Colour(155, 89, 182))
            edit_icon.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            cs.Add(edit_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
            label_text = f" {mname} ×{m.get('repeat',1)}"
            cl = wx.StaticText(c, label=label_text)
            cl.SetForegroundColour(wx.Colour(180, 80, 10))
            cl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            cs.Add(cl, 1, wx.ALIGN_CENTER_VERTICAL)
            db = wx.Button(c, label="✕", size=(22, 22), style=wx.BORDER_NONE)
            db.SetBackgroundColour(wx.Colour(225, 228, 235)); db.SetForegroundColour(wx.Colour(90, 95, 105))
            db.Bind(wx.EVT_BUTTON, lambda e, mi2=mi: self._del_monster(mi2))
            cs.Add(db, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4); c.SetSizer(cs)
            c.Bind(wx.EVT_LEFT_DOWN, lambda e, mi3=mi: self._select_monster(self.selected_stage_index, mi3))
            self._make_clickable(c)
            self.editor_sizer.Add(c, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        ab = wx.Button(self.editor_panel, label="+ 添加怪物", size=(-1, 28), style=wx.BORDER_NONE)
        ab.SetBackgroundColour(wx.Colour(215, 218, 226)); ab.SetForegroundColour(wx.Colour(60, 65, 75))
        ab.Bind(wx.EVT_BUTTON, lambda e: self._add_monster())
        self.editor_sizer.Add(ab, 0, wx.EXPAND | wx.TOP, 4)

        self._title("◆ 打完怎么去下一层")
        trans = s.get("transition", {})
        self._lbl("点什么进下一层", "可以选文字或图片，脚本会自动识别")
        self._render_dual_input("transition_click", trans.get("click_map_name", ""),
                                trans.get("click_map_name_mode", "text"),
                                "搜字库: 曹袁战场 / 传送 / 入口 ...",
                                "搜图片: chuansong / entrance ...",
                                lambda v: self._set_transition("click_map_name", v),
                                get_value=lambda: self.config["stages"][self.selected_stage_index].get("transition", {}).get("click_map_name", ""),
                                on_mode_change=lambda m: self._set_transition("click_map_name_mode", m))
        self._lbl("点击位置（从左上角算的坐标）", "基于900×580分辨率，自动算比例")
        trans_coord = trans.get("click_region_proportion", "0.1,0.12")
        try:
            tp = trans_coord.split(",")
            tc_display_x = str(900 - int(float(tp[0]) * 900))
            tc_display_y = str(int(float(tp[1]) * 580))
            trans_coord_display = f"{tc_display_x},{tc_display_y}"
        except (ValueError, IndexError):
            trans_coord_display = "810,70"
        trans_coord_row = wx.Panel(self.editor_panel, size=(-1, 28))
        trans_coord_row.SetBackgroundColour(wx.Colour(240, 242, 246))
        trans_coord_rs = wx.BoxSizer(wx.HORIZONTAL)
        t3 = wx.TextCtrl(trans_coord_row, size=(-1, 28), style=wx.TE_PROCESS_ENTER)
        t3.SetValue(trans_coord_display)
        t3.SetHint("如: 34,78 (从左上角算的坐标)")
        t3.SetBackgroundColour(wx.Colour(255, 255, 255))
        t3.SetForegroundColour(wx.Colour(40, 42, 50))
        trans_coord_rs.Add(t3, 1, wx.EXPAND | wx.RIGHT, 2)
        gb_c = wx.Button(trans_coord_row, label="🎮", size=(32, 28), style=wx.BORDER_NONE)
        gb_c.SetBackgroundColour(wx.Colour(155, 89, 182))
        gb_c.SetForegroundColour(wx.Colour(255, 255, 255))
        gb_c.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        gb_c.SetToolTip("从游戏画面点击拾取坐标")
        gb_c.Bind(wx.EVT_BUTTON, lambda e: self._do_game_capture("coord", lambda r: self._fill_coord_result(r, t3)))
        trans_coord_rs.Add(gb_c, 0)
        trans_coord_row.SetSizer(trans_coord_rs)
        self.editor_sizer.Add(trans_coord_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        def on_trans_coord_change(e):
            raw = t3.GetValue().strip()
            try:
                parts = raw.split(",")
                display_x = int(parts[0])
                display_y = int(parts[1])
                ratio_x = round((900 - display_x) / 900, 4)
                ratio_y = round(display_y / 580, 4)
                self._set_transition("click_region_proportion", f"{ratio_x},{ratio_y}")
            except (ValueError, IndexError):
                pass
        t3.Bind(wx.EVT_KILL_FOCUS, on_trans_coord_change)
        t3.Bind(wx.EVT_TEXT_ENTER, on_trans_coord_change)

        nav = wx.Panel(self.editor_panel, size=(-1, 40))
        nav.SetBackgroundColour(wx.Colour(248, 249, 252))
        ns = wx.BoxSizer(wx.HORIZONTAL)
        prev_btn = wx.Button(nav, label="← 上一步：配入口", size=(-1, 32), style=wx.BORDER_NONE)
        prev_btn.SetBackgroundColour(wx.Colour(215, 218, 226))
        prev_btn.SetForegroundColour(wx.Colour(60, 65, 75))
        prev_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        prev_btn.Bind(wx.EVT_BUTTON, lambda e: self._go_back())
        ns.Add(prev_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        ns.AddStretchSpacer()
        monsters = s.get("monsters", [])
        if monsters:
            next_btn = wx.Button(nav, label=f"下一步：配怪物 →", size=(-1, 32), style=wx.BORDER_NONE)
            next_btn.SetBackgroundColour(wx.Colour(41, 128, 185))
            next_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            next_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            next_btn.Bind(wx.EVT_BUTTON, lambda e: self._select_monster(self.selected_stage_index, 0))
            ns.Add(next_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        else:
            next_btn2 = wx.Button(nav, label="下一步：保存脚本 →", size=(-1, 32), style=wx.BORDER_NONE)
            next_btn2.SetBackgroundColour(wx.Colour(39, 174, 96))
            next_btn2.SetForegroundColour(wx.Colour(255, 255, 255))
            next_btn2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            next_btn2.Bind(wx.EVT_BUTTON, lambda e: self._on_save())
            ns.Add(next_btn2, 0, wx.ALIGN_CENTER_VERTICAL)
        nav.SetSizer(ns)
        self.editor_sizer.Add(nav, 0, wx.EXPAND | wx.TOP, 12)

    def _fill_coord_result(self, result, coord_input):
        pf = self.parent_frame
        try:
            game_w = int(getattr(pf, 'locationWidth', 900))
            game_h = int(getattr(pf, 'locationHeight', 580))
            gx = result["x"]
            gy = result["y"]
            display_x = int(gx * 900 / game_w)
            display_y = int(gy * 580 / game_h)
            coord_input.SetValue(f"{display_x},{display_y}")
            evt = wx.CommandEvent(wx.wxEVT_TEXT, coord_input.GetId())
            wx.PostEvent(coord_input, evt)
        except Exception:
            coord_input.SetValue(f"{result.get('x', 0)},{result.get('y', 0)}")

    def _try_add_font_entry(self, text, color, region, capture_path=""):
        global _font_index
        dm = self._get_dm()
        if not dm:
            return False
        x1, y1, x2, y2 = region
        color_format = getattr(self.parent_frame, 'color_format', color)

        try:
            verify = dm.FindStrFastE(x1, y1, x2, y2, text, color_format, 0.9)
            if verify and int(str(verify).split("|")[0]) >= 0:
                _font_index = None
                return True
        except Exception:
            pass

        try:
            verify = dm.FindStrFastE(x1, y1, x2, y2, text, color, 0.9)
            if verify and int(str(verify).split("|")[0]) >= 0:
                _font_index = None
                return True
        except Exception:
            pass

        try:
            result = dm.FetchWord(x1, y1, x2, y2, color, text)
            if result and str(result).strip():
                _font_index = None
                return True
        except Exception:
            pass

        font_file = os.path.join(SERVE_ASSETS, "fonts", "common.txt")
        if not os.path.exists(font_file):
            wx.MessageBox(
                f"文字「{text}」不在字库中，且字库文件不存在。\n\n"
                f"检测到的颜色: {color}\n"
                f"请使用大漠综合工具手动添加字库条目。",
                "字库录入提示")
            return False

        entry = self._generate_font_entry(text, color, capture_path, region)
        if not entry:
            wx.MessageBox(
                f"文字「{text}」不在字库中，自动生成字库条目失败。\n\n"
                f"检测到的颜色: {color}\n"
                f"截图已保存: {capture_path}\n\n"
                f"请使用大漠综合工具手动添加字库条目：\n"
                f"1. 打开大漠综合工具\n"
                f"2. 选择「字库制作」功能\n"
                f"3. 截取文字区域\n"
                f"4. 输入文字「{text}」并生成条目\n"
                f"5. 将条目追加到 common.txt",
                "字库录入提示")
            return False

        enc = self._detect_font_file_encoding(font_file)
        backup = font_file + ".bak"
        if not os.path.exists(backup):
            try:
                shutil.copy2(font_file, backup)
            except Exception:
                pass

        try:
            with open(font_file, "a", encoding=enc) as f:
                f.write(entry + "\n")
        except Exception:
            try:
                with open(font_file, "a", encoding="utf-8") as f:
                    f.write(entry + "\n")
            except Exception as ex:
                wx.MessageBox(f"写入字库文件失败: {ex}", "错误")
                return False

        try:
            dm.SetDict(0, font_file)
        except Exception:
            pass

        try:
            verify = dm.FindStrFastE(x1, y1, x2, y2, text, color, 0.9)
            if verify and int(str(verify).split("|")[0]) >= 0:
                _font_index = None
                wx.MessageBox(f"✅ 文字「{text}」已成功录入字库！", "字库录入成功")
                return True
        except Exception:
            pass

        try:
            with open(font_file, "r", encoding=enc) as f:
                lines = f.readlines()
            if lines:
                lines = lines[:-1]
                with open(font_file, "w", encoding=enc) as f:
                    f.writelines(lines)
        except Exception:
            pass

        wx.MessageBox(
            f"文字「{text}」自动录入字库后验证失败，已回滚。\n\n"
            f"检测到的颜色: {color}\n"
            f"截图已保存: {capture_path}\n\n"
            f"请使用大漠综合工具手动添加字库条目。",
            "字库录入提示")
        return False

    def _generate_font_entry(self, text, color, bmp_path, region):
        if not bmp_path or not os.path.exists(bmp_path):
            if region and len(region) == 4:
                dm = self._get_dm()
                if dm:
                    temp_dir = os.path.join(SERVE_ASSETS, "images", "temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    bmp_path = os.path.join(temp_dir, f"_font_{int(time.time())}.bmp")
                    try:
                        dm.Capture(region[0], region[1], region[2], region[3], bmp_path)
                    except Exception:
                        return None
                    if not os.path.exists(bmp_path):
                        return None
            else:
                return None

        try:
            img = wx.Image(bmp_path, wx.BITMAP_TYPE_BMP)
            if not img.IsOk():
                return None

            w = img.GetWidth()
            h = img.GetHeight()
            if w == 0 or h == 0:
                return None

            color_list = []
            for color_part in color.split("|"):
                main_color = color_part.split("-")[0]
                try:
                    r = int(main_color[0:2], 16)
                    g = int(main_color[2:4], 16)
                    b = int(main_color[4:6], 16)
                    color_list.append((r, g, b))
                except (ValueError, IndexError):
                    continue

            if not color_list:
                color_list = [(255, 255, 255)]

            threshold = 60
            bitmap_data = []
            for y in range(h):
                row_bits = []
                for x in range(w):
                    pr = img.GetRed(x, y)
                    pg = img.GetGreen(x, y)
                    pb = img.GetBlue(x, y)
                    is_text = False
                    for cr, cg, cb in color_list:
                        if (abs(pr - cr) + abs(pg - cg) + abs(pb - cb)) < threshold * 3:
                            is_text = True
                            break
                    row_bits.append(1 if is_text else 0)
                bitmap_data.append(row_bits)

            min_x, min_y = w, h
            max_x, max_y = 0, 0
            for y in range(h):
                for x in range(w):
                    if bitmap_data[y][x]:
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)

            if min_x > max_x or min_y > max_y:
                return None

            crop_w = max_x - min_x + 1
            crop_h = max_y - min_y + 1

            hex_parts = []
            for y in range(min_y, max_y + 1):
                row_val = 0
                for x in range(min_x, max_x + 1):
                    row_val = (row_val << 1) | bitmap_data[y][x]
                hex_len = (crop_w + 3) // 4
                hex_parts.append(f"{row_val:0{hex_len * 2}X}")

            hex_string = "".join(hex_parts)
            entry = f"{hex_string}${text}${min_x}.{min_y}.{crop_w}${crop_h}"
            return entry
        except Exception:
            return None

    def _detect_font_file_encoding(self, filepath):
        for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    f.read(4096)
                return enc
            except (UnicodeDecodeError, IOError):
                continue
        return "utf-8"

    # ========== 怪物配置 ==========
    def _render_monster(self):
        m = self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index]
        current_mode = m.get("detect_mode", "text")
        display_name = m.get("name", "") if current_mode == "text" else m.get("images", "")
        self._render_step_indicator(4)
        self._title(f"🎯 打怪设置: {display_name or '新怪物'}")

        self._lbl("用什么方式找怪")
        self._render_dual_input("monster_detect", m.get("name", "") if current_mode == "text" else m.get("images", ""),
                                current_mode,
                                "搜字库: 曹 / 赵云 / 小兵 ...",
                                "搜图片: hbj / dao / boss / caocao ...",
                                lambda v: self._set_monster_detect(v),
                                get_value=lambda: self._get_monster_detect_value(),
                                on_mode_change=lambda m: self._set_monster("detect_mode", m))

        be_toggle = wx.Button(self.editor_panel, label="▶ 战斗结束图（一般不用改，点我展开）", size=(-1, 26), style=wx.BORDER_NONE)
        be_toggle.SetBackgroundColour(wx.Colour(215, 218, 226))
        be_toggle.SetForegroundColour(wx.Colour(60, 65, 75))
        be_toggle.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.editor_sizer.Add(be_toggle, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        be_panel = wx.Panel(self.editor_panel)
        be_panel.SetBackgroundColour(wx.Colour(240, 242, 246))
        be_sizer = wx.BoxSizer(wx.VERTICAL)
        be_row = wx.Panel(be_panel, size=(-1, 28))
        be_row.SetBackgroundColour(wx.Colour(240, 242, 246))
        be_rs = wx.BoxSizer(wx.HORIZONTAL)
        bt_end = SearchInput(be_row, value=m.get("battle_end", "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp"),
                             hint="搜: zdzd / battle ...")
        be_rs.Add(bt_end, 1, wx.EXPAND | wx.RIGHT, 2)
        gb_be = wx.Button(be_row, label="🎮", size=(32, 28), style=wx.BORDER_NONE)
        gb_be.SetBackgroundColour(wx.Colour(155, 89, 182))
        gb_be.SetForegroundColour(wx.Colour(255, 255, 255))
        gb_be.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        gb_be.SetToolTip("从游戏画面截图作为战斗结束标志")
        gb_be.Bind(wx.EVT_BUTTON, lambda e: self._do_game_capture("image", lambda r: self._fill_image_result(r, bt_end)))
        be_rs.Add(gb_be, 0)
        be_row.SetSizer(be_rs)
        be_sizer.Add(be_row, 0, wx.EXPAND)
        be_panel.SetSizer(be_sizer)
        be_panel.Hide()
        self.editor_sizer.Add(be_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        bt_end.Bind(wx.EVT_TEXT, lambda ev: self._set_monster("battle_end", bt_end.GetValue()))

        def toggle_battle_end(e):
            if be_panel.IsShown():
                be_panel.Hide()
                be_toggle.SetLabel("▶ 战斗结束图（一般不用改，点我展开）")
            else:
                be_panel.Show()
                be_toggle.SetLabel("▼ 战斗结束图（点我收起）")
            self.editor_sizer.Layout()
            self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        be_toggle.Bind(wx.EVT_BUTTON, toggle_battle_end)

        self._lbl("在屏幕哪里找怪")
        area_labels = list(AREA_LABELS.keys())
        current_region = m.get("region", "gameBottomLocation")
        current_label = AREA_REVERSE.get(current_region, "屏幕下半部分")
        c4 = self._combo(area_labels, current_label)
        def on_area_change(e):
            sel_label = c4.GetValue()
            region_val = AREA_LABELS.get(sel_label, "gameBottomLocation")
            self._set_monster("region", region_val)
        c4.Bind(wx.EVT_COMBOBOX, on_area_change)

        self._lbl("打几只")
        t5 = self._txt(str(m.get("repeat", 3)), "1 / 2 / 3 ...")
        t5.Bind(wx.EVT_TEXT, lambda e: self._set_monster("repeat", int(e.GetString() or "3")))

        self._lbl("怎么走过去", "tab=清怪  A=左走  D=右走")
        c6 = self._combo(KNOWN_KEYS, m.get("move_key", "tab"))
        c6.Bind(wx.EVT_COMBOBOX, lambda e: self._set_monster("move_key", e.GetString()))

        self._lbl("走路点到哪（从左上角算的坐标）", "基于900×580分辨率，自动算比例")
        coord_val = m.get("move_region", "0.038,0.134")
        try:
            parts = coord_val.split(",")
            display_x = str(900 - int(float(parts[0]) * 900))
            display_y = str(int(float(parts[1]) * 580))
            coord_display = f"{display_x},{display_y}"
        except (ValueError, IndexError):
            coord_display = "866,78"
        coord_row = wx.Panel(self.editor_panel, size=(-1, 28))
        coord_row.SetBackgroundColour(wx.Colour(240, 242, 246))
        coord_rs = wx.BoxSizer(wx.HORIZONTAL)
        t7 = wx.TextCtrl(coord_row, size=(-1, 28), style=wx.TE_PROCESS_ENTER)
        t7.SetValue(coord_display)
        t7.SetHint("如: 34,78 (从左上角算的坐标)")
        t7.SetBackgroundColour(wx.Colour(255, 255, 255))
        t7.SetForegroundColour(wx.Colour(40, 42, 50))
        coord_rs.Add(t7, 1, wx.EXPAND | wx.RIGHT, 2)
        gb3 = wx.Button(coord_row, label="🎮", size=(32, 28), style=wx.BORDER_NONE)
        gb3.SetBackgroundColour(wx.Colour(155, 89, 182))
        gb3.SetForegroundColour(wx.Colour(255, 255, 255))
        gb3.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        gb3.SetToolTip("从游戏画面点击拾取坐标")
        gb3.Bind(wx.EVT_BUTTON, lambda e: self._do_game_capture("coord", lambda r: self._fill_coord_result(r, t7)))
        coord_rs.Add(gb3, 0)
        coord_row.SetSizer(coord_rs)
        self.editor_sizer.Add(coord_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        def on_coord_change(e):
            raw = t7.GetValue().strip()
            try:
                parts = raw.split(",")
                display_x = int(parts[0])
                display_y = int(parts[1])
                ratio_x = round((900 - display_x) / 900, 4)
                ratio_y = round(display_y / 580, 4)
                self._set_monster("move_region", f"{ratio_x},{ratio_y}")
            except (ValueError, IndexError):
                pass
        t7.Bind(wx.EVT_KILL_FOCUS, on_coord_change)
        t7.Bind(wx.EVT_TEXT_ENTER, on_coord_change)

        nav = wx.Panel(self.editor_panel, size=(-1, 40))
        nav.SetBackgroundColour(wx.Colour(248, 249, 252))
        ns = wx.BoxSizer(wx.HORIZONTAL)
        prev_btn = wx.Button(nav, label="← 上一步：配楼层", size=(-1, 32), style=wx.BORDER_NONE)
        prev_btn.SetBackgroundColour(wx.Colour(215, 218, 226))
        prev_btn.SetForegroundColour(wx.Colour(60, 65, 75))
        prev_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        prev_btn.Bind(wx.EVT_BUTTON, lambda e: self._go_back())
        ns.Add(prev_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        ns.AddStretchSpacer()
        monsters = self.config["stages"][self.selected_stage_index].get("monsters", [])
        next_mi = self.selected_monster_index + 1
        if next_mi < len(monsters):
            next_btn = wx.Button(nav, label=f"下一个怪物 →", size=(-1, 32), style=wx.BORDER_NONE)
            next_btn.SetBackgroundColour(wx.Colour(41, 128, 185))
            next_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            next_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            next_btn.Bind(wx.EVT_BUTTON, lambda e: self._select_monster(self.selected_stage_index, next_mi))
            ns.Add(next_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        else:
            save_btn = wx.Button(nav, label="下一步：保存脚本 →", size=(-1, 32), style=wx.BORDER_NONE)
            save_btn.SetBackgroundColour(wx.Colour(39, 174, 96))
            save_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            save_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            save_btn.Bind(wx.EVT_BUTTON, lambda e: self._on_save())
            ns.Add(save_btn, 0, wx.ALIGN_CENTER_VERTICAL)
        nav.SetSizer(ns)
        self.editor_sizer.Add(nav, 0, wx.EXPAND | wx.TOP, 12)

    def _fill_image_result(self, result, search_input):
        global _resource_index
        if result.get("path"):
            current = search_input.GetValue()
            if current:
                search_input.SetValue(f"{current}|{result['path']}")
            else:
                search_input.SetValue(result["path"])
            evt = wx.CommandEvent(wx.wxEVT_TEXT, search_input.tc.GetId())
            wx.PostEvent(search_input.tc, evt)
            _resource_index = None
        else:
            wx.MessageBox("截图失败", "提示")

    # ========== 数据操作 ==========
    def _set_entry(self, k, v): self.config["entry"][k] = v
    def _set_loop(self, k, v): self.config["loop"][k] = v
    def _set_config(self, k, v): self.config[k] = v
    def _set_stage(self, k, v): self.config["stages"][self.selected_stage_index][k] = v
    def _set_transition(self, k, v): self.config["stages"][self.selected_stage_index].setdefault("transition", {})[k] = v
    def _set_monster(self, k, v): self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index][k] = v

    def _set_monster_detect(self, v):
        m = self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index]
        mode = m.get("detect_mode", "text")
        if mode == "text":
            m["name"] = v
        else:
            m["images"] = v

    def _get_monster_detect_value(self):
        m = self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index]
        mode = m.get("detect_mode", "text")
        return m.get("name", "") if mode == "text" else m.get("images", "")
    def _select_stage(self, i): self.selected_stage_index = i; self.selected_monster_index = -1; self._refresh_all()
    def _select_monster(self, si, mi): self.selected_stage_index = si; self.selected_monster_index = mi; self._refresh_editor()
    def _add_stage(self, e=None):
        existing = {s.get("map_name", "") for s in self.config["stages"]}
        idx = len(self.config["stages"]) + 1
        default_name = f"地图{idx}"
        while default_name in existing:
            idx += 1
            default_name = f"地图{idx}"
        self.config["stages"].append({"map_name": default_name, "monsters": [], "transition": {}})
        self.selected_stage_index = len(self.config["stages"]) - 1; self.selected_monster_index = -1; self._refresh_all()
    def _del_stage(self, e=None):
        if self.selected_stage_index >= 0: del self.config["stages"][self.selected_stage_index]; self.selected_stage_index = -1; self._refresh_all()
    def _add_monster(self):
        if self.selected_stage_index < 0: return
        self.config["stages"][self.selected_stage_index]["monsters"].append(
            {"detect_mode": "text", "name": "新怪物", "images": "", "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
             "region": "gameBottomLocation", "repeat": 3, "move_key": "tab", "move_region": "0.038,0.134"})
        self.selected_monster_index = len(self.config["stages"][self.selected_stage_index]["monsters"]) - 1; self._refresh_all()
    def _del_monster(self, mi):
        if self.selected_stage_index < 0: return
        monsters = self.config["stages"][self.selected_stage_index]["monsters"]
        if 0 <= mi < len(monsters):
            del monsters[mi]
        self.selected_monster_index = -1; self._refresh_all()
    def _refresh_all(self): self._refresh_tree(); self._refresh_editor()

    # ========== 保存 ==========
    def _on_save(self, e=None):
        name = self.txt_name.GetValue().strip()
        if not name:
            wx.MessageBox("请先填一个脚本名字", "提示"); return
        if not self.config.get("confirm_map"):
            wx.MessageBox("请填写「进副本后右上角显示什么字」，不然脚本不知道有没有成功进副本", "提示"); return
        if not self.config.get("exit_map"):
            wx.MessageBox("请填写「出副本后等什么地图」，不然脚本出副本后不知道在哪", "提示"); return
        if not self.config.get("stages"):
            wx.MessageBox("请至少添加一个楼层并配置怪物", "提示"); return
        for i, s in enumerate(self.config["stages"]):
            if not s.get("monsters"):
                wx.MessageBox(f"第{i+1}层还没有添加怪物", "提示"); return
        sd = os.path.join(USER_SCRIPTS_DIR, name); os.makedirs(sd, exist_ok=True)
        self.config["name"] = name
        self.config["type"] = "dungeon_run"
        with open(os.path.join(sd, "config.json"), "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        ScriptRegistry.add(name, self.config)
        summary = f"✅ 脚本保存成功！\n\n📁 路径: {sd}/config.json\n📝 脚本名: 📝 {name}\n\n在主程序下拉框选择「📝 {name}」即可运行\n无需改代码，无需重启！"
        wx.MessageBox(summary, "保存成功")

    def _on_trial_run(self, e=None):
        name = self.txt_name.GetValue().strip()
        if not name:
            wx.MessageBox("请先填一个脚本名字并保存", "提示"); return
        sd = os.path.join(USER_SCRIPTS_DIR, name)
        config_path = os.path.join(sd, "config.json")
        if not os.path.exists(config_path):
            self._on_save()
            if not os.path.exists(config_path):
                return
        try:
            pf = self.parent_frame
            if pf and hasattr(pf, 'scriptName'):
                try:
                    if hasattr(pf, 'script_choice'):
                        choices = pf.script_choice.GetItems()
                        target = f"📝 {name}"
                        if target in choices:
                            pf.script_choice.SetValue(target)
                        pf.scriptName = name
                    else:
                        pf.scriptName = name
                except Exception:
                    pass
            wx.MessageBox(f"✅ 脚本「{name}」已保存并设为当前脚本！\n\n👉 回到主程序点「开始」即可运行", "试运行准备就绪")
        except Exception as ex:
            wx.MessageBox(f"设置试运行失败: {ex}\n\n请手动在主程序下拉框选择「📝 {name}」", "提示")

    def _on_open_existing(self, e=None):
        names = ScriptRegistry.list_names()
        if not names:
            wx.MessageBox("还没有保存过任何脚本", "提示"); return
        dlg = wx.SingleChoiceDialog(self, "选择要打开的脚本", "打开已有脚本", names)
        if dlg.ShowModal() == wx.ID_OK:
            sel = dlg.GetStringSelection()
            config_path = os.path.join(USER_SCRIPTS_DIR, sel, "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        self.config = json.load(f)
                    self.txt_name.SetValue(sel)
                    self.selected_stage_index = -1
                    self.selected_monster_index = -1
                    self._template_applied = True
                    self._refresh_all()
                except Exception as ex:
                    wx.MessageBox(f"读取脚本失败: {ex}", "错误")
            else:
                reg = ScriptRegistry.load()
                if sel in reg and "config" in reg[sel]:
                    self.config = copy.deepcopy(reg[sel]["config"])
                    self.txt_name.SetValue(sel)
                    self.selected_stage_index = -1
                    self.selected_monster_index = -1
                    self._template_applied = True
                    self._refresh_all()
                else:
                    wx.MessageBox(f"找不到脚本配置: {sel}", "错误")
        dlg.Destroy()


def get_user_script_choices():
    return [f"📝 {n}" for n in ScriptRegistry.list_names()]

if __name__ == "__main__":
    app = wx.App(); frame = ScriptFactoryDialog(None); frame.Show(); app.MainLoop()
