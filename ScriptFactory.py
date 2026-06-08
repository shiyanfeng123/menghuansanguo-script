# -*- coding: utf-8 -*-
"""
梦幻三国 - 脚本工厂 (v4.0: PopupWindow检索 + 滚动编辑器)
"""

import os, json, time, threading, datetime, re
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

# ============================================================
# 资源索引
# ============================================================
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


KNOWN_CITIES = ["洛阳", "襄阳", "涿郡", "许昌", "官渡", "徐州"]
KNOWN_AREAS = ["gameBottomLocation (下半屏)", "gameLeftLocation (左半屏)",
               "gameRightLocation (右半屏)", "dituLocation (地图区域)",
               "gameLocation (全屏)"]
KNOWN_KEYS = ["tab", "A", "D", "W", "S", "1", "2", "3"]
FB_NAMES = ["副本曹操", "副本老仙", "副本南华老人", "副本分身", "副本猎鼠人",
            "副本挑战赛", "副本魔镜使者", "副本典韦", "副本龙天啸"]


# ============================================================
# 浮动下拉面板 (PopupWindow - 浏览器风格搜索建议)
# ============================================================
class SearchPopup(wx.PopupWindow):
    """悬停在输入框下方的搜索结果列表"""
    def __init__(self, parent, owner_txt, on_select_callback):
        super().__init__(parent, wx.BORDER_SIMPLE)
        self.owner_txt = owner_txt
        self.on_select_callback = on_select_callback
        self._results = []
        self._build()

    def _build(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(28, 28, 36))
        self.lb = wx.ListBox(panel, size=(380, 200), style=wx.LB_SINGLE | wx.NO_BORDER)
        self.lb.SetBackgroundColour(wx.Colour(28, 28, 36))
        self.lb.SetForegroundColour(wx.Colour(200, 220, 230))
        self.lb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                faceName="微软雅黑"))
        self.lb.Bind(wx.EVT_LISTBOX, self._on_select)
        self.lb.Bind(wx.EVT_KEY_DOWN, self._on_key)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lb, 1, wx.EXPAND)
        panel.SetSizer(sizer)

    def show_results(self, results):
        self._results = results
        self.lb.Clear()
        if not results:
            self.Hide()
            return
        for r in results:
            self.lb.Append(r["label"])
        self.lb.SetSelection(0)
        tw, th = self.owner_txt.GetSize()
        tx, ty = self.owner_txt.ClientToScreen(0, th)
        self.SetPosition((tx, ty))
        self.SetSize((max(380, tw), min(200, len(results) * 22 + 4)))
        self.Show()

    def _on_select(self, e):
        sel = self.lb.GetSelection()
        if 0 <= sel < len(self._results):
            self.on_select_callback(self._results[sel]["value"])
        self.Hide()

    def _on_key(self, e):
        key = e.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.Hide()
            self.owner_txt.SetFocus()
        elif key == wx.WXK_RETURN:
            self._on_select(None)
        elif key == wx.WXK_UP and self.lb.GetSelection() > 0:
            self.lb.SetSelection(self.lb.GetSelection() - 1)
        elif key == wx.WXK_DOWN:
            sel = self.lb.GetSelection()
            if sel < self.lb.GetCount() - 1:
                self.lb.SetSelection(sel + 1)
        else:
            self.owner_txt.SetFocus()
            self.owner_txt.EmulateKeyPress(wx.KeyEvent(wx.wxEVT_KEY_DOWN, key))


# ============================================================
# 搜索输入框控件 (轻量, 仅 TextCtrl)
# ============================================================
class SearchInput(wx.TextCtrl):
    """输入时弹出 SearchPopup 进行图片检索"""
    def __init__(self, parent, value="", hint="输入关键词搜索图片..."):
        super().__init__(parent, size=(-1, 28), style=0)
        self.SetValue(str(value))
        self.SetHint(hint)
        self.SetBackgroundColour(wx.Colour(18, 18, 22))
        self.SetForegroundColour(wx.Colour(230, 230, 238))
        self._popup = None
        self._results = []
        self.Bind(wx.EVT_TEXT, self._on_text)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_lost)

    def _ensure_popup(self):
        if self._popup is None:
            self._popup = SearchPopup(self.GetTopLevelParent(), self, self._on_popup_select)

    def _on_text(self, e):
        e.Skip()
        q = self.GetValue().strip()
        if len(q) < 1:
            if self._popup:
                self._popup.Hide()
            return
        self._ensure_popup()
        self._results = search_resources(q)
        self._popup.show_results(self._results)

    def _on_key(self, e):
        key = e.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            if self._popup and self._popup.IsShown():
                self._popup.Hide()
                return
        elif key == wx.WXK_DOWN:
            if self._popup and self._popup.IsShown():
                self._popup._on_key(e)
                return
        elif key == wx.WXK_RETURN:
            if self._popup and self._popup.IsShown():
                self._popup._on_key(e)
                return
        e.Skip()

    def _on_focus_lost(self, e):
        wx.CallLater(150, self._delayed_hide)
        e.Skip()

    def _delayed_hide(self):
        if self._popup and self._popup.IsShown():
            fw = wx.Window.FindFocus()
            if fw != self._popup.lb and fw != self and fw != self._popup:
                self._popup.Hide()

    def _on_popup_select(self, value):
        self.SetValue(value)
        evt = wx.CommandEvent(wx.wxEVT_TEXT, self.GetId())
        wx.PostEvent(self, evt)


# ============================================================
# 代码生成器 + 注入器
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
LOOP_MODES = ["🔄 无限循环", "🔢 指定次数"]

class ScriptFactoryDialog(wx.Frame):
    def __init__(self, parent_frame):
        super().__init__(None, title="脚本工厂 V4.0 — Popup检索 · 滚动编辑器", size=(1100, 750),
                         pos=(70, 30), style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(wx.Colour(18, 18, 22))
        self.selected_stage_index = -1
        self.selected_monster_index = -1
        self.config = {
            "entry": {"city": "洛阳", "yizhan": "驿站城西", "npc_image": "", "fb_name": ""},
            "loop": {"mode": "infinite", "count": 1, "clear_bag_every": 15},
            "stages": [],
        }
        self._build()

    def _build(self):
        panel = wx.Panel(self); panel.SetBackgroundColour(wx.Colour(18, 18, 22))
        ms = wx.BoxSizer(wx.VERTICAL)

        # ── 标题栏 ──
        hdr = wx.Panel(panel, size=(-1, 36)); hdr.SetBackgroundColour(wx.Colour(26, 26, 32))
        hs = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(hdr, label="脚本工厂 — 填写配置 → 注入代码到 serveScript.py")
        t.SetForegroundColour(wx.Colour(230, 200, 110))
        t.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        hs.Add(t, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        hs.AddStretchSpacer()
        self.btn_inject = wx.Button(hdr, label="💉 注入到 serveScript.py", size=(160, 28), style=wx.BORDER_NONE)
        self.btn_inject.SetBackgroundColour(wx.Colour(192, 57, 43))
        self.btn_inject.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_inject.Bind(wx.EVT_BUTTON, self._on_inject)
        hs.Add(self.btn_inject, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        hdr.SetSizer(hs); ms.Add(hdr, 0, wx.EXPAND)

        # ── 主体: 左树 + 右编辑器(可滚动) ──
        body = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.Panel(panel, size=(300, -1)); left.SetBackgroundColour(wx.Colour(22, 22, 28))
        self._build_tree(left); body.Add(left, 0, wx.EXPAND | wx.RIGHT, 2)

        self.editor_panel = scrolled.ScrolledPanel(panel, -1)
        self.editor_panel.SetBackgroundColour(wx.Colour(22, 22, 28))
        self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        self.editor_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor_panel.SetSizer(self.editor_sizer)
        body.Add(self.editor_panel, 1, wx.EXPAND)
        ms.Add(body, 1, wx.EXPAND | wx.ALL, 4)

        # ── 底部栏 ──
        btm = wx.Panel(panel, size=(-1, 36)); btm.SetBackgroundColour(wx.Colour(26, 26, 32))
        bs = wx.BoxSizer(wx.HORIZONTAL)
        bs.Add(wx.StaticText(btm, label="脚本名称:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        self.txt_name = wx.TextCtrl(btm, size=(120, 26)); self.txt_name.SetHint("如: 觉醒")
        bs.Add(self.txt_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        bs.AddStretchSpacer()
        for lbl, hdl in [("💾 保存配置", self._on_save_json), ("🗑 移除注入", self._on_remove)]:
            btn = wx.Button(btm, label=lbl, size=(90, 28), style=wx.BORDER_NONE)
            btn.SetBackgroundColour(wx.Colour(32, 32, 40)); btn.SetForegroundColour(wx.Colour(200, 210, 220))
            btn.Bind(wx.EVT_BUTTON, hdl); bs.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        btm.SetSizer(bs); ms.Add(btm, 0, wx.EXPAND)
        panel.SetSizer(ms); self._refresh_all()

    # ========== 左侧流程树 ==========
    def _build_tree(self, parent):
        sz = wx.BoxSizer(wx.VERTICAL)
        l = wx.StaticText(parent, label="📐 脚本结构")
        l.SetForegroundColour(wx.Colour(230, 200, 110))
        l.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sz.Add(l, 0, wx.ALL, 8)
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        for lbl, h in [("+ 加楼层", self._add_stage), ("🗑 删楼层", self._del_stage)]:
            b = wx.Button(parent, label=lbl, size=(75, 28), style=wx.BORDER_NONE)
            b.SetBackgroundColour(wx.Colour(32, 32, 40)); b.SetForegroundColour(wx.Colour(200, 210, 220))
            b.Bind(wx.EVT_BUTTON, h); btn_row.Add(b, 0, wx.LEFT | wx.RIGHT, 2)
        sz.Add(btn_row, 0, wx.LEFT | wx.BOTTOM, 6)
        self.tp = scrolled.ScrolledPanel(parent, -1)
        self.tp.SetBackgroundColour(wx.Colour(22, 22, 28)); self.tp.SetupScrolling(scroll_y=True, rate_y=20)
        self.ts = wx.BoxSizer(wx.VERTICAL); self.tp.SetSizer(self.ts); sz.Add(self.tp, 1, wx.EXPAND)
        parent.SetSizer(sz)

    def _refresh_tree(self):
        self.ts.Clear(True)
        e = self.config["entry"]
        city = e.get("city","?"); fb = e.get("fb_name",""); npc = e.get("npc_image","")
        el = f"📍 入口: {city} → "
        if fb:
            el += f"{fb}"
        elif npc:
            el += os.path.basename(npc)
        else:
            el += e.get("yizhan", "?")
        self.ts.Add(self._card(el, (41,128,185)), 0, wx.EXPAND | wx.BOTTOM, 3)
        for i, s in enumerate(self.config["stages"]):
            sel = (i == self.selected_stage_index)
            bg = (231,76,60) if sel else (41,128,185)
            c = wx.Panel(self.tp, size=(-1,-1)); c.SetBackgroundColour((18,18,22))
            sv = wx.BoxSizer(wx.VERTICAL)
            h = wx.Panel(c, size=(-1,26)); h.SetBackgroundColour(bg)
            hs2 = wx.BoxSizer(wx.HORIZONTAL)
            hl = wx.StaticText(h, label=f"🗺️ {s.get('map_name',f'第{i+1}层')}")
            hl.SetForegroundColour((255,255,255)); hl.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            hs2.Add(hl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8); h.SetSizer(hs2)
            h.Bind(wx.EVT_LEFT_DOWN, lambda e,si=i: self._select_stage(si)); sv.Add(h, 0, wx.EXPAND)
            for mi, m in enumerate(s.get("monsters",[])):
                mc = wx.Panel(c, size=(-1,22)); mc.SetBackgroundColour((26,26,32))
                ms2 = wx.BoxSizer(wx.HORIZONTAL)
                ml = wx.StaticText(mc, label=f"  🎯 {m.get('name','?')} ×{m.get('repeat',1)}")
                ml.SetForegroundColour((230,126,34)); ml.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                ms2.Add(ml, 1, wx.ALIGN_CENTER_VERTICAL); mc.SetSizer(ms2)
                mc.Bind(wx.EVT_LEFT_DOWN, lambda e,si=i,mi2=mi: self._select_monster(si,mi2))
                sv.Add(mc, 0, wx.EXPAND | wx.LEFT, 16)
            trans = s.get("transition",{})
            if trans:
                tc = wx.Panel(c, size=(-1,20)); tc.SetBackgroundColour((22,22,28))
                tt = wx.StaticText(tc, label=f"  ◆ 换图→{trans.get('click_map_name','?')}")
                tt.SetForegroundColour((149,165,166)); tt.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                tc_s = wx.BoxSizer(wx.HORIZONTAL); tc_s.Add(tt, 1, wx.ALIGN_CENTER_VERTICAL)
                tc.SetSizer(tc_s); sv.Add(tc, 0, wx.EXPAND | wx.LEFT, 16)
            sv.AddSpacer(2); c.SetSizer(sv); self.ts.Add(c, 0, wx.EXPAND | wx.BOTTOM, 2)
        loop = self.config["loop"]
        ll = f"🏁 {loop.get('mode','?')}"
        if loop.get("clear_bag_every"): ll += f" | 清包每{loop['clear_bag_every']}次"
        self.ts.Add(self._card(ll, (39,174,96)), 0, wx.EXPAND | wx.BOTTOM, 3)
        self.ts.Layout(); self.tp.SetupScrolling(scroll_y=True, rate_y=20); self.tp.Refresh()

    def _card(self, text, color):
        c = wx.Panel(self.tp, size=(-1,28)); c.SetBackgroundColour(color)
        s = wx.BoxSizer(wx.HORIZONTAL)
        l = wx.StaticText(c, label=text); l.SetForegroundColour((255,255,255))
        l.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        s.Add(l, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8); c.SetSizer(s); return c

    # ========== 右侧编辑器 (ScrolledPanel) ==========
    def _refresh_editor(self):
        self.editor_sizer.Clear(True)
        self.editor_panel.Freeze()
        if self.selected_stage_index < 0: self._render_entry()
        elif self.selected_monster_index >= 0: self._render_monster()
        else: self._render_stage()
        self.editor_sizer.Layout()
        self.editor_panel.SetupScrolling(scroll_y=True, rate_y=20)
        self.editor_panel.Thaw()
        self.editor_panel.Refresh()

    def _title(self, text):
        l = wx.StaticText(self.editor_panel, label=text)
        l.SetForegroundColour(wx.Colour(230, 200, 110))
        l.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.editor_sizer.Add(l, 0, wx.ALL, 8)

    def _lbl(self, text, tip=""):
        label_text = text if not tip else f"{text}  (💡 {tip})"
        l = wx.StaticText(self.editor_panel, label=label_text)
        l.SetForegroundColour(wx.Colour(150, 160, 170))
        l.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.editor_sizer.Add(l, 0, wx.LEFT | wx.TOP, 8)

    def _txt(self, value="", hint=""):
        t = wx.TextCtrl(self.editor_panel, size=(-1, 28))
        t.SetValue(str(value)); t.SetBackgroundColour(wx.Colour(18, 18, 22)); t.SetForegroundColour(wx.Colour(230, 230, 238))
        if hint: t.SetHint(hint)
        self.editor_sizer.Add(t, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return t

    def _combo(self, choices, value=""):
        c = wx.ComboBox(self.editor_panel, size=(-1, 28), choices=choices, style=wx.CB_DROPDOWN)
        c.SetValue(str(value)); c.SetBackgroundColour(wx.Colour(18, 18, 22)); c.SetForegroundColour(wx.Colour(230, 230, 238))
        self.editor_sizer.Add(c, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return c

    def _search(self, value="", hint="输入关键词搜索图片..."):
        si = SearchInput(self.editor_panel, value=value, hint=hint)
        self.editor_sizer.Add(si, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        return si

    def _render_entry(self):
        e = self.config["entry"]
        self._title("📍 入口配置")
        self._lbl("城市名, 如: 洛阳")
        c1 = self._combo(KNOWN_CITIES, e.get("city", "洛阳"))
        c1.Bind(wx.EVT_TEXT, lambda ev: self._set_entry("city", ev.GetString()))
        self._lbl("驿站名 (从哪个驿站出发)")
        t2 = self._txt(e.get("yizhan", ""), "必填, 如: 驿站城西")
        t2.Bind(wx.EVT_TEXT, lambda ev: self._set_entry("yizhan", ev.GetString()))
        self._lbl("副本名 (直接飞副本, 填此项可不填NPC图)", "如: 副本曹操")
        c3 = self._combo(FB_NAMES, e.get("fb_name", ""))
        c3.Bind(wx.EVT_TEXT, lambda ev: self._set_entry("fb_name", ev.GetString()))
        self._lbl("或 NPC入口图片 (不飞副本时用)", "输入关键词搜索, 如 'caocao'")
        s4 = self._search(e.get("npc_image", ""), "搜图片: caocao / xiao / hbj ...")
        s4.Bind(wx.EVT_TEXT, lambda ev: self._set_entry("npc_image", s4.GetValue()))

        self._title("⚙️ 循环与清包")
        loop = self.config["loop"]
        cbo = wx.ComboBox(self.editor_panel, size=(-1, 28), choices=LOOP_MODES, style=wx.CB_READONLY)
        cbo.SetValue(LOOP_MODES[0] if loop.get("mode", "infinite") == "infinite" else LOOP_MODES[1])
        cbo.SetBackgroundColour(wx.Colour(18, 18, 22)); cbo.SetForegroundColour(wx.Colour(230, 230, 238))
        cbo.Bind(wx.EVT_COMBOBOX, lambda e: self._set_loop_mode(cbo.GetSelection()))
        self.editor_sizer.Add(cbo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        if loop.get("mode") != "infinite":
            self._lbl("循环次数")
            t5 = self._txt(str(loop.get("count", 1)))
            t5.Bind(wx.EVT_TEXT, lambda ev: self._set_loop("count", int(ev.GetString() or "1")))
        self._lbl("每运行多少次清一次包 (0=不清)")
        t6 = self._txt(str(loop.get("clear_bag_every", 15)))
        t6.Bind(wx.EVT_TEXT, lambda ev: self._set_loop("clear_bag_every", int(ev.GetString() or "0")))

    def _render_stage(self):
        s = self.config["stages"][self.selected_stage_index]
        self._title(f"🗺️ 第{self.selected_stage_index+1}层配置")
        self._lbl("本地图名字 (屏幕上显示的, 用于判断是否到达)")
        t1 = self._txt(s.get("map_name", ""), "如: 曹操大帐")
        t1.Bind(wx.EVT_TEXT, lambda e: self._set_stage("map_name", e.GetString()))

        self._title("🎯 怪物列表")
        for mi, m in enumerate(s.get("monsters", [])):
            c = wx.Panel(self.editor_panel, size=(-1, 28)); c.SetBackgroundColour(wx.Colour(26, 26, 32))
            cs = wx.BoxSizer(wx.HORIZONTAL)
            label_text = f"  {m.get('name','?')} ×{m.get('repeat',1)}  [{m.get('region','gameBottomLocation')}]"
            cl = wx.StaticText(c, label=label_text)
            cl.SetForegroundColour(wx.Colour(230, 126, 34))
            cl.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            cs.Add(cl, 1, wx.ALIGN_CENTER_VERTICAL)
            db = wx.Button(c, label="✕", size=(22, 22), style=wx.BORDER_NONE)
            db.SetBackgroundColour(wx.Colour(40, 40, 46)); db.SetForegroundColour(wx.Colour(180, 180, 190))
            db.Bind(wx.EVT_BUTTON, lambda e, mi2=mi: self._del_monster(mi2))
            cs.Add(db, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4); c.SetSizer(cs)
            c.Bind(wx.EVT_LEFT_DOWN, lambda e, mi3=mi: self._select_monster(self.selected_stage_index, mi3))
            self.editor_sizer.Add(c, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        ab = wx.Button(self.editor_panel, label="+ 添加怪物", size=(-1, 28), style=wx.BORDER_NONE)
        ab.SetBackgroundColour(wx.Colour(32, 32, 40)); ab.SetForegroundColour(wx.Colour(200, 210, 220))
        ab.Bind(wx.EVT_BUTTON, lambda e: self._add_monster())
        self.editor_sizer.Add(ab, 0, wx.EXPAND | wx.TOP, 4)

        self._title("◆ 打完换图")
        trans = s.get("transition", {})
        self._lbl("换图时点击的目标文字/地图名")
        t2 = self._txt(trans.get("click_map_name", ""), "如: 曹袁战场")
        t2.Bind(wx.EVT_TEXT, lambda e: self._set_transition("click_map_name", e.GetString()))
        self._lbl("点击坐标比例 (屏幕百分比)")
        t3 = self._txt(trans.get("click_region_proportion", "0.1,0.12"), "如: 0.078,0.127")
        t3.Bind(wx.EVT_TEXT, lambda e: self._set_transition("click_region_proportion", e.GetString()))

    def _render_monster(self):
        m = self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index]
        self._title(f"🎯 怪物配置: {m.get('name','?')}")

        self._lbl("怪物名字 (屏幕上找字用)")
        t1 = self._txt(m.get("name", ""))
        t1.Bind(wx.EVT_TEXT, lambda e: self._set_monster("name", e.GetString()))

        self._lbl("怪物图片 (用于找图, 多图用|分隔)", "输入关键词搜索 → 选择 → 自动填入")
        s2 = self._search(m.get("images", ""), "搜图片: hbj / dao / boss / caocao ...")
        s2.Bind(wx.EVT_TEXT, lambda ev: self._set_monster("images", s2.GetValue()))

        self._lbl("战斗结束判断图 (多图用|分隔)")
        bt_end = self._search(m.get("battle_end", "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp"),
                              "搜: zdzd / battle ...")
        bt_end.Bind(wx.EVT_TEXT, lambda ev: self._set_monster("battle_end", bt_end.GetValue()))

        self._lbl("搜索区域 (在屏幕哪块找怪)")
        c4 = self._combo(KNOWN_AREAS, m.get("region", "gameBottomLocation"))
        c4.Bind(wx.EVT_TEXT, lambda e: self._set_monster("region", e.GetString().split(" ")[0]))

        self._lbl("打几次")
        t5 = self._txt(str(m.get("repeat", 3)), "1 / 2 / 3 ...")
        t5.Bind(wx.EVT_TEXT, lambda e: self._set_monster("repeat", int(e.GetString() or "3")))

        self._lbl("走路键 (tab清怪/A左走/D右走)")
        c6 = self._combo(KNOWN_KEYS, m.get("move_key", "tab"))
        c6.Bind(wx.EVT_TEXT, lambda e: self._set_monster("move_key", e.GetString()))

        self._lbl("走路时点击坐标比例 (屏幕百分比)")
        t7 = self._txt(m.get("move_region", "0.1,0.12"), "如: 0.165,0.124")
        t7.Bind(wx.EVT_TEXT, lambda e: self._set_monster("move_region", e.GetString()))

    # ========== 数据操作 ==========
    def _set_entry(self, k, v): self.config["entry"][k] = v
    def _set_loop(self, k, v): self.config["loop"][k] = v
    def _set_stage(self, k, v): self.config["stages"][self.selected_stage_index][k] = v
    def _set_transition(self, k, v): self.config["stages"][self.selected_stage_index].setdefault("transition", {})[k] = v
    def _set_monster(self, k, v): self.config["stages"][self.selected_stage_index]["monsters"][self.selected_monster_index][k] = v
    def _set_loop_mode(self, s): self.config["loop"]["mode"] = ["infinite", "custom_count"][min(s, 1)]; self._refresh_editor()
    def _select_stage(self, i): self.selected_stage_index = i; self.selected_monster_index = -1; self._refresh_all()
    def _select_monster(self, si, mi): self.selected_stage_index = si; self.selected_monster_index = mi; self._refresh_editor()
    def _add_stage(self, e=None):
        self.config["stages"].append({"map_name": f"地图{len(self.config['stages'])+1}", "monsters": [], "transition": {}})
        self.selected_stage_index = len(self.config["stages"]) - 1; self.selected_monster_index = -1; self._refresh_all()
    def _del_stage(self, e=None):
        if self.selected_stage_index >= 0: del self.config["stages"][self.selected_stage_index]; self.selected_stage_index = -1; self._refresh_all()
    def _add_monster(self):
        if self.selected_stage_index < 0: return
        self.config["stages"][self.selected_stage_index]["monsters"].append(
            {"name": "新怪物", "images": "", "battle_end": "serveAssets/images/zdzd.bmp|serveAssets/images/zdzd111.bmp",
             "region": "gameBottomLocation", "repeat": 3, "move_key": "tab", "move_region": "0.1,0.12"})
        self.selected_monster_index = len(self.config["stages"][self.selected_stage_index]["monsters"]) - 1; self._refresh_all()
    def _del_monster(self, mi):
        del self.config["stages"][self.selected_stage_index]["monsters"][mi]; self.selected_monster_index = -1; self._refresh_all()
    def _refresh_all(self): self._refresh_tree(); self._refresh_editor()

    # ========== 注入 ==========
    def _on_inject(self, e=None):
        name = self.txt_name.GetValue().strip()
        if not name: wx.MessageBox("请输入脚本名称"); return
        if not self.config["stages"]: wx.MessageBox("请至少添加一个楼层"); return
        try:
            CodeInjector(name, self.config).inject(self.config["loop"].get("mode", "infinite"))
            ScriptRegistry.add(name, self.config)
            wx.MessageBox(f"✅ 已注入 serveScript.py!\n\n脚本: {name}\n重启主程序, 下拉框选 '{name}' 运行\n\n已自动备份 serveScript.py.bak", "注入成功")
        except Exception as ex:
            wx.MessageBox(f"注入失败: {ex}", "错误")

    def _on_save_json(self, e=None):
        name = self.txt_name.GetValue().strip()
        if not name: return
        sd = os.path.join(USER_SCRIPTS_DIR, name); os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "config.json"), "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        ScriptRegistry.add(name, self.config)
        wx.MessageBox(f"已保存: {sd}/config.json", "OK")

    def _on_remove(self, e=None):
        name = self.txt_name.GetValue().strip()
        if not name: return
        if wx.MessageBox(f"移除 {name} 注入的代码?", "确认", wx.YES_NO) == wx.YES:
            CodeInjector(name, self.config).remove()
            ScriptRegistry.remove(name)
            wx.MessageBox(f"已移除 {name}。重启主程序生效。", "OK")


def get_user_script_choices():
    return [f"📝 {n}" for n in ScriptRegistry.list_names()]

if __name__ == "__main__":
    app = wx.App(); frame = ScriptFactoryDialog(None); frame.Show(); app.MainLoop()
