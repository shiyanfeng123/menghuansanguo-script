# -*- coding: utf-8 -*-
"""
梦幻三国 - 可视化脚本工厂
功能: 录制/编排/生成用户自定义脚本
"""

import os
import json
import time
import threading
import datetime
import wx
import wx.lib.scrolledpanel as scrolled

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_SCRIPTS_DIR = os.path.join(SCRIPT_DIR, "user_scripts")
REGISTRY_FILE = os.path.join(USER_SCRIPTS_DIR, "registry.json")

if not os.path.exists(USER_SCRIPTS_DIR):
    os.makedirs(USER_SCRIPTS_DIR)


# ============================================================
#  区域预设
# ============================================================
REGION_PRESETS = {
    "全屏": (0, 0, 900, 580),
    "左半屏": (0, 0, 450, 580),
    "右半屏": (450, 0, 900, 580),
    "上半屏": (0, 0, 900, 290),
    "下半屏": (0, 290, 900, 580),
    "左侧三分之一": (0, 0, 300, 580),
    "右侧三分之一": (600, 0, 900, 580),
    "中间区域": (150, 100, 750, 480),
    "左上角": (0, 0, 300, 200),
    "右上角": (600, 0, 900, 200),
    "底部": (0, 400, 900, 580),
    "自定义框选...": None,
}

COLOR_PRESETS = {
    "通用游戏字体(白绿黄青红黑底)":
        "ffffff-000000|00ff00-000000|ffff00-000000|0ff000-000000|"
        "ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|"
        "ff1c13-000000|00ef0b-000000",
    "白色字体": "ffffff-000000",
    "金色字体": "ffff00-000000|ffcc00-000000",
    "绿色字体": "00ff00-000000",
    "红色字体": "ff0000-000000",
}

MAP_LIST = ["洛阳", "襄阳", "官渡", "涿郡", "徐州", "龙岛", "许昌", "长安", "邺城"]

BUILTIN_TEMPLATES = {
    "刷活动副本": {
        "description": "飞到活动地图，找到Boss，打N次",
        "params": ["活动名称", "活动入口图标", "Boss图标", "战斗结束标志", "循环次数"],
    },
    "刷地图精英怪": {
        "description": "飞到指定地图，找到精英怪，打N次",
        "params": ["目的地", "精英怪图标", "循环次数"],
    },
}


# ============================================================
#  脚本注册表
# ============================================================
class ScriptRegistry:
    @staticmethod
    def load():
        if not os.path.exists(REGISTRY_FILE):
            return {}
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save(registry):
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

    @staticmethod
    def add(name, script_data):
        registry = ScriptRegistry.load()
        registry[name] = {
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "steps": len(script_data.get("steps", [])),
            "script_path": os.path.join(USER_SCRIPTS_DIR, name, "script.py"),
        }
        ScriptRegistry.save(registry)

    @staticmethod
    def remove(name):
        registry = ScriptRegistry.load()
        if name in registry:
            del registry[name]
            ScriptRegistry.save(registry)

    @staticmethod
    def list_names():
        return list(ScriptRegistry.load().keys())


# ============================================================
#  代码生成器
# ============================================================
class CodeGenerator:
    def __init__(self, steps, script_name):
        self.steps = steps
        self.script_name = script_name
        self.material_dir = f"user_scripts/{script_name}"

    def generate(self):
        lines = [
            "# -*- coding: utf-8 -*-",
            f"# 自动生成脚本: {self.script_name}",
            f"# 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# 总步骤: {len(self.steps)}",
            "",
            "import time",
            "",
            "",
            f"class Script_{self._safe_name()}:",
            "    def __init__(self, thread):",
            "        self.thread = thread",
            "        self.dm = thread.dm",
            f"        self.base = '{self.material_dir}'",
            "",
            "    def run(self):",
            f"        print('[{self.script_name}] 开始执行')",
            "",
        ]

        for i, step in enumerate(self.steps):
            step_id = i + 1
            stype = step.get("type", "")
            label = step.get("label", f"步骤{step_id}")
            lines.append(f"        # === {label} ===")
            code = self._gen_step(step_id, step)
            if code:
                lines.append(code)
            lines.append("")

        lines.extend([
            f"        print('[{self.script_name}] 执行完成')",
        ])
        return "\n".join(lines)

    def _safe_name(self):
        safe = ""
        for c in self.script_name:
            if c.isalnum() or c == "_":
                safe += c
            else:
                safe += "_"
        return safe or "UserScript"

    def _gen_step(self, sid, step):
        stype = step.get("type", "")
        params = step.get("params", {})

        if stype == "click_image":
            img = params.get("image", f"s{sid}.png")
            region = params.get("region", "全屏")
            conf = params.get("confidence", 0.8)
            account = params.get("account", "dm")
            offset = params.get("offset", "center")
            wait = params.get("wait_after", 2.0)
            return self._gen_click_image(sid, img, region, conf, account, offset, wait)

        elif stype == "find_and_click":
            img = params.get("image", f"s{sid}.png")
            region = params.get("region", "全屏")
            wait = params.get("wait_after", 2.0)
            confirm = params.get("confirm_image")
            conf_region = params.get("confirm_region", "全屏")
            timeout = params.get("confirm_timeout", 30)
            return self._gen_find_and_click(sid, img, region, wait, confirm,
                                            conf_region, timeout)

        elif stype == "click_text":
            text = params.get("text", "")
            region = params.get("region", "全屏")
            color = params.get("color", "ffffff-000000")
            conf = params.get("confidence", 0.9)
            account = params.get("account", "dm")
            wait = params.get("wait_after", 2.0)
            return self._gen_click_text(sid, text, region, color, conf, account, wait)

        elif stype == "wait_image":
            img = params.get("image", f"s{sid}.png")
            region = params.get("region", "全屏")
            timeout = params.get("timeout", 30)
            return self._gen_wait_image(sid, img, region, timeout)

        elif stype == "go_ditu":
            city = params.get("city", "洛阳")
            return self._gen_go_ditu(city)

        elif stype == "loop":
            count = params.get("count", 5)
            children = params.get("children", [])
            return self._gen_loop(count, children)

        elif stype == "delay":
            seconds = params.get("seconds", 3.0)
            return f"        time.sleep({seconds})"

        return ""

    def _gen_click_image(self, sid, img, region, conf, account, offset, wait):
        reg = self._region_code(region)
        dm = self._dm_code(account)
        return (
            f"        path = self.thread.get_resource_path("
            f"f'{{self.base}}/{img}')\n"
            f"        pos = {dm}.FindPicE({reg[0]},{reg[1]},{reg[2]},{reg[3]},"
            f"path, '000000', {conf}, 0)\n"
            f"        if pos[0] >= 0:\n"
            f"            {dm}.MoveTo(int(pos[1]) + {offset}, int(pos[2]) + {offset})\n"
            f"            time.sleep(0.3)\n"
            f"            {dm}.LeftClick()\n"
            f"            time.sleep({wait})\n"
            f"            print('点击成功')\n"
            f"        else:\n"
            f"            print('未找到目标图片, 跳过')"
        )

    def _gen_find_and_click(self, sid, img, region, wait, confirm_img, conf_region, timeout):
        reg = self._region_code(region)
        cfg = self._region_code(conf_region)
        return (
            f"        target = self.thread.get_resource_path("
            f"f'{{self.base}}/{img}')\n"
            f"        confirm = self.thread.get_resource_path("
            f"f'{{self.base}}/{confirm_img}')\n"
            f"        # 找目标并点击\n"
            f"        tpos = self.dm.FindPicE({reg[0]},{reg[1]},{reg[2]},{reg[3]},"
            f"target, '000000', 0.8, 0)\n"
            f"        if tpos[0] < 0:\n"
            f"            print('未找到目标')\n"
            f"            return\n"
            f"        self.dm.MoveTo(int(tpos[1])+15, int(tpos[2])+15)\n"
            f"        time.sleep(0.3)\n"
            f"        self.dm.LeftClick()\n"
            f"        time.sleep({wait})\n"
            f"        # 等待确认图出现\n"
            f"        import time as _t\n"
            f"        _start = _t.time()\n"
            f"        while _t.time() - _start < {timeout}:\n"
            f"            cpos = self.dm.FindPicE({cfg[0]},{cfg[1]},"
            f"{cfg[2]},{cfg[3]}, confirm, '000000', 0.8, 0)\n"
            f"            if cpos[0] >= 0:\n"
            f"                print('确认成功')\n"
            f"                return\n"
            f"            _t.sleep(0.5)\n"
            f"        print('等待确认超时')"
        )

    def _gen_click_text(self, sid, text, region, color, conf, account, wait):
        reg = self._region_code(region)
        dm = self._dm_code(account)
        return (
            f"        result = {dm}.FindStrFastE({reg[0]},{reg[1]},"
            f"{reg[2]},{reg[3]}, '{text}', '{color}', {conf})\n"
            f"        parts = result.split('|')\n"
            f"        if int(parts[0]) >= 0:\n"
            f"            {dm}.MoveTo(int(parts[1])+15, int(parts[2])+15)\n"
            f"            time.sleep(0.3)\n"
            f"            {dm}.LeftClick()\n"
            f"            time.sleep({wait})\n"
            f"            print(f'点击文字\\'{text}\\'成功')\n"
            f"        else:\n"
            f"            print(f'未找到文字\\'{text}\\', 跳过')"
        )

    def _gen_wait_image(self, sid, img, region, timeout):
        reg = self._region_code(region)
        return (
            f"        path = self.thread.get_resource_path("
            f"f'{{self.base}}/{img}')\n"
            f"        result = self.thread.waitFor(path, "
            f"({reg[0]},{reg[1]},{reg[2]},{reg[3]}), timeout={timeout})"
            f"\n        if not result:\n"
            f"            print('等待超时, 跳过')"
        )

    def _gen_go_ditu(self, city):
        return f"        print('飞往{city}...')\n" \
               f"        # TODO: 调用 go_in_ditu"

    def _gen_loop(self, count, children):
        lines = [f"        for _i in range({count}):"]
        for child in children:
            child_code = self._gen_step(0, child)
            if child_code:
                for cl in child_code.split("\n"):
                    lines.append(f"            {cl}")
        return "\n".join(lines)

    def _region_code(self, region_name):
        if isinstance(region_name, (list, tuple)) and len(region_name) == 4:
            return region_name
        preset = REGION_PRESETS.get(region_name, REGION_PRESETS["全屏"])
        if preset:
            return preset
        return (0, 0, 900, 580)

    def _dm_code(self, account):
        if account in ("队友1", "win1"):
            return "self.thread.win1_dm"
        elif account in ("队友2", "win2"):
            return "self.thread.win2_dm"
        return "self.dm"


# ============================================================
#  脚本工厂主窗口
# ============================================================
class ScriptFactoryDialog(wx.Frame):
    """脚本工厂 - 可视化脚本编排器"""

    def __init__(self, parent_frame):
        super().__init__(None, title="脚本工厂", size=(900, 650),
                         pos=(100, 50),
                         style=wx.DEFAULT_FRAME_STYLE)
        self.parent_frame = parent_frame
        self.SetBackgroundColour(wx.Colour(18, 18, 22))

        self.script_name = ""
        self.steps = []
        self.selected_step_index = -1
        self.recording = False
        self.recorder = None

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(18, 18, 22))
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # ── 标题栏 ──
        hdr = wx.Panel(panel, size=(-1, 36))
        hdr.SetBackgroundColour(wx.Colour(26, 26, 32))
        hs = wx.BoxSizer(wx.HORIZONTAL)
        t = wx.StaticText(hdr, label="脚本工厂 - 可视化脚本编排器")
        t.SetForegroundColour(wx.Colour(230, 200, 110))
        t.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                          wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        hs.Add(t, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        hs.AddStretchSpacer()

        self.btn_record = wx.Button(hdr, label="⏺ 录制", size=(70, 28),
                                    style=wx.BORDER_NONE)
        self.btn_record.SetBackgroundColour(wx.Colour(180, 50, 40))
        self.btn_record.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_record.Bind(wx.EVT_BUTTON, self._on_record)
        hs.Add(self.btn_record, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.btn_generate = wx.Button(hdr, label="📋 生成脚本", size=(80, 28),
                                      style=wx.BORDER_NONE)
        self.btn_generate.SetBackgroundColour(wx.Colour(230, 200, 110))
        self.btn_generate.SetForegroundColour(wx.Colour(18, 18, 22))
        self.btn_generate.Bind(wx.EVT_BUTTON, self._on_generate)
        hs.Add(self.btn_generate, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        hdr.SetSizer(hs)
        main_sizer.Add(hdr, 0, wx.EXPAND)

        # ── 主体: 三栏布局 ──
        body = wx.BoxSizer(wx.HORIZONTAL)

        # 左栏: 积木面板
        left_panel = wx.Panel(panel, size=(160, -1))
        left_panel.SetBackgroundColour(wx.Colour(22, 22, 28))
        self._build_block_palette(left_panel)
        body.Add(left_panel, 0, wx.EXPAND | wx.RIGHT, 2)

        # 中栏: 步骤列表
        mid_panel = wx.Panel(panel)
        mid_panel.SetBackgroundColour(wx.Colour(18, 18, 22))
        self._build_step_list(mid_panel)
        body.Add(mid_panel, 1, wx.EXPAND | wx.RIGHT, 2)

        # 右栏: 属性面板
        right_panel = wx.Panel(panel, size=(280, -1))
        right_panel.SetBackgroundColour(wx.Colour(22, 22, 28))
        self._build_props_panel(right_panel)
        body.Add(right_panel, 0, wx.EXPAND)

        main_sizer.Add(body, 1, wx.EXPAND | wx.ALL, 4)

        # ── 底部 ──
        btm = wx.Panel(panel, size=(-1, 36))
        btm.SetBackgroundColour(wx.Colour(26, 26, 32))
        bs = wx.BoxSizer(wx.HORIZONTAL)

        lb_name = wx.StaticText(btm, label="脚本名称:")
        lb_name.SetForegroundColour(wx.Colour(180, 180, 190))
        bs.Add(lb_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)

        self.txt_name = wx.TextCtrl(btm, size=(160, 26))
        self.txt_name.SetBackgroundColour(wx.Colour(18, 18, 22))
        self.txt_name.SetForegroundColour(wx.Colour(230, 230, 238))
        self.txt_name.SetHint("输入脚本名称")
        bs.Add(self.txt_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        bs.AddStretchSpacer()

        self.btn_save = wx.Button(btm, label="💾 保存", size=(70, 28),
                                  style=wx.BORDER_NONE)
        self.btn_save.SetBackgroundColour(wx.Colour(50, 140, 70))
        self.btn_save.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        bs.Add(self.btn_save, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.btn_run = wx.Button(btm, label="▶ 运行", size=(60, 28),
                                 style=wx.BORDER_NONE)
        self.btn_run.SetBackgroundColour(wx.Colour(0, 150, 136))
        self.btn_run.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_run.Bind(wx.EVT_BUTTON, self._on_run)
        bs.Add(self.btn_run, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        btm.SetSizer(bs)
        main_sizer.Add(btm, 0, wx.EXPAND)

        panel.SetSizer(main_sizer)
        self._refresh_step_list()

    # ============================================================
    #  积木面板 (左侧)
    # ============================================================
    def _build_block_palette(self, parent):
        sz = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(parent, label="🧩 操作积木")
        title.SetForegroundColour(wx.Colour(230, 200, 110))
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        sz.Add(title, 0, wx.ALL, 8)

        blocks = [
            ("📷 点击此图", "click_image", "框选一个图标 → 自动找图并点击"),
            ("📷 点击并确认", "find_and_click",
             "框选目标+确认图 → 点击后等待确认 ⭐"),
            ("📝 点击此字", "click_text", "输入要查找的文字 → 自动找字并点击"),
            ("⏳ 等待出现", "wait_image", "框选图标 → 等到它出现为止"),
            ("🗺️ 飞到这里", "go_ditu", "选目的地 → 自动传送并等待到达"),
            ("⏱️ 纯等待", "delay", "等待指定秒数"),
            ("🔁 重复N次", "loop", "将子步骤重复执行"),
        ]

        for label, btype, tip in blocks:
            btn = wx.Button(parent, label=label, size=(140, 33),
                            style=wx.BORDER_NONE)
            btn.SetBackgroundColour(wx.Colour(32, 32, 40))
            btn.SetForegroundColour(wx.Colour(200, 200, 210))
            btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            btn.SetToolTip(tip)
            btn.Bind(wx.EVT_BUTTON, lambda e, t=btype: self._add_step(t))
            sz.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        sz.AddSpacer(12)

        title2 = wx.StaticText(parent, label="📋 模板")
        title2.SetForegroundColour(wx.Colour(230, 200, 110))
        title2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        sz.Add(title2, 0, wx.ALL, 8)

        for tname in BUILTIN_TEMPLATES:
            btn = wx.Button(parent, label=f"📄 {tname}", size=(140, 33),
                            style=wx.BORDER_NONE)
            btn.SetBackgroundColour(wx.Colour(32, 32, 40))
            btn.SetForegroundColour(wx.Colour(200, 200, 210))
            btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            btn.Bind(wx.EVT_BUTTON, lambda e, tn=tname: self._use_template(tn))
            sz.Add(btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        parent.SetSizer(sz)

    # ============================================================
    #  步骤列表 (中间)
    # ============================================================
    def _build_step_list(self, parent):
        sz = wx.BoxSizer(wx.VERTICAL)

        hrow = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(parent, label="📐 流程步骤")
        title.SetForegroundColour(wx.Colour(230, 200, 110))
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        hrow.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        hrow.AddStretchSpacer()
        hint = wx.StaticText(parent, label="点击步骤可查看/编辑参数")
        hint.SetForegroundColour(wx.Colour(120, 120, 130))
        hint.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        hrow.Add(hint, 0, wx.ALIGN_CENTER_VERTICAL)
        sz.Add(hrow, 0, wx.EXPAND | wx.ALL, 8)

        self.step_list_panel = scrolled.ScrolledPanel(parent, -1)
        self.step_list_panel.SetBackgroundColour(wx.Colour(18, 18, 22))
        self.step_list_panel.SetupScrolling(scroll_y=True, rate_y=20)
        self.step_list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.step_list_panel.SetSizer(self.step_list_sizer)
        sz.Add(self.step_list_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        parent.SetSizer(sz)

    def _refresh_step_list(self):
        self.step_list_sizer.Clear(True)
        icons = {
            "click_image": "📷", "find_and_click": "📷✅",
            "click_text": "📝", "wait_image": "⏳",
            "go_ditu": "🗺️", "delay": "⏱️", "loop": "🔁",
        }

        if not self.steps:
            empty = wx.StaticText(self.step_list_panel,
                                  label="还没有步骤\n\n点击左侧积木添加\n或点 ⏺ 录制")
            empty.SetForegroundColour(wx.Colour(100, 100, 110))
            empty.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            self.step_list_sizer.Add(empty, 0, wx.ALL | wx.ALIGN_CENTER, 60)
        else:
            for i, step in enumerate(self.steps):
                self._add_step_card(i, step, icons)

        self.step_list_sizer.Layout()
        self.step_list_panel.SetupScrolling(scroll_y=True, rate_y=20)
        if hasattr(self, "step_list_panel"):
            self.step_list_panel.Refresh()

    def _add_step_card(self, index, step, icons):
        stype = step.get("type", "click_image")
        label = step.get("label", f"步骤{index + 1}")
        icon = icons.get(stype, "📷")

        card = wx.Panel(self.step_list_panel, size=(-1, 38))
        bg = wx.Colour(26, 26, 32) if index != self.selected_step_index \
            else wx.Colour(40, 40, 50)
        card.SetBackgroundColour(bg)

        rs = wx.BoxSizer(wx.HORIZONTAL)

        num = wx.StaticText(card, label=f"{icon} {index + 1}. {label}")
        num.SetForegroundColour(wx.Colour(200, 200, 210)
                                if index != self.selected_step_index
                                else wx.Colour(230, 200, 110))
        num.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        rs.Add(num, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)

        if stype == "loop":
            children = step.get("params", {}).get("children", [])
            cnt = step.get("params", {}).get("count", 1)
            info = wx.StaticText(card, label=f"循环{cnt}次, {len(children)}子步骤")
            info.SetForegroundColour(wx.Colour(140, 140, 150))
            info.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                 wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            rs.Add(info, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        # 操作按钮
        for action, act_label in [("▲", "上移"), ("▼", "下移"), ("✕", "删除")]:
            a_btn = wx.Button(card, label=action, size=(26, 26),
                              style=wx.BORDER_NONE)
            a_btn.SetBackgroundColour(wx.Colour(40, 40, 46))
            a_btn.SetForegroundColour(wx.Colour(180, 180, 190))
            a_btn.SetToolTip(act_label)
            a_btn.Bind(wx.EVT_BUTTON,
                       lambda e, idx=index, act=action: self._step_action(idx, act))
            rs.Add(a_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)

        card.SetSizer(rs)
        card.Bind(wx.EVT_LEFT_DOWN, lambda e, idx=index: self._select_step(idx))
        self.step_list_sizer.Add(card, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)

    # ============================================================
    #  属性面板 (右侧)
    # ============================================================
    def _build_props_panel(self, parent):
        self.props_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(parent, label="⚙ 步骤属性")
        title.SetForegroundColour(wx.Colour(230, 200, 110))
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.props_sizer.Add(title, 0, wx.ALL, 8)

        hint = wx.StaticText(parent,
                             label="点击左侧步骤查看/编辑参数\n\n"
                                   "🎯 = 在游戏画面上框选区域")
        hint.SetForegroundColour(wx.Colour(120, 120, 130))
        hint.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.props_sizer.Add(hint, 0, wx.ALL, 8)

        parent.SetSizer(self.props_sizer)
        self.props_parent = parent

    def _refresh_props_panel(self):
        self.props_sizer.Clear(True)

        if self.selected_step_index < 0 or self.selected_step_index >= len(
                self.steps):
            hint = wx.StaticText(self.props_parent,
                                 label="点击左侧步骤\n查看/编辑参数")
            hint.SetForegroundColour(wx.Colour(120, 120, 130))
            hint.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT,
                                 wx.FONTSTYLE_NORMAL,
                                 wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            self.props_sizer.Add(hint, 0, wx.ALL, 20)
            self.props_sizer.Layout()
            return

        step = self.steps[self.selected_step_index]
        stype = step.get("type", "click_image")
        params = step.get("params", {})

        title = wx.StaticText(self.props_parent,
                              label=f"步骤{self.selected_step_index + 1}属性")
        title.SetForegroundColour(wx.Colour(230, 200, 110))
        title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                              wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.props_sizer.Add(title, 0, wx.ALL, 8)

        # 步骤标签
        self._add_prop_label("步骤名称")
        txt_label = wx.TextCtrl(self.props_parent, size=(-1, 26))
        txt_label.SetValue(step.get("label", ""))
        txt_label.SetBackgroundColour(wx.Colour(18, 18, 22))
        txt_label.SetForegroundColour(wx.Colour(230, 230, 238))
        txt_label.Bind(wx.EVT_TEXT, lambda e: self._update_param("label",
                                                                 e.GetString()))
        self.props_sizer.Add(txt_label, 0, wx.EXPAND | wx.ALL, 4)

        # 类型特定参数
        if stype == "click_image":
            self._add_prop_label("目标图片 (🎯框选)")
            img = params.get("image", "")
            txt_img = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_img.SetValue(img)
            txt_img.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_img.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_img.SetHint("素材文件名.png")
            txt_img.Bind(wx.EVT_TEXT, lambda e: self._update_param("image",
                                                                   e.GetString()))
            self.props_sizer.Add(txt_img, 0, wx.EXPAND | wx.ALL, 4)

            self._add_region_selector(params.get("region", "全屏"))

            self._add_prop_label("匹配精度")
            txt_conf = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_conf.SetValue(str(params.get("confidence", 0.8)))
            txt_conf.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_conf.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_conf.Bind(wx.EVT_TEXT, lambda e: self._update_param("confidence",
                                                                    float(
                                                                        e.GetString() or "0.8")))
            self.props_sizer.Add(txt_conf, 0, wx.EXPAND | wx.ALL, 4)

            self._add_prop_label("点击后等待(秒)")
            txt_wait = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_wait.SetValue(str(params.get("wait_after", 2.0)))
            txt_wait.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_wait.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_wait.Bind(wx.EVT_TEXT, lambda e: self._update_param("wait_after",
                                                                    float(
                                                                        e.GetString() or "2")))
            self.props_sizer.Add(txt_wait, 0, wx.EXPAND | wx.ALL, 4)

        elif stype == "find_and_click":
            self._add_prop_label("目标图片 (🎯框选)")
            txt_img = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_img.SetValue(params.get("image", ""))
            txt_img.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_img.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_img.Bind(wx.EVT_TEXT, lambda e: self._update_param("image",
                                                                   e.GetString()))
            self.props_sizer.Add(txt_img, 0, wx.EXPAND | wx.ALL, 4)

            self._add_prop_label("确认图片 (🎯框选)")
            txt_conf = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_conf.SetValue(params.get("confirm_image", ""))
            txt_conf.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_conf.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_conf.Bind(wx.EVT_TEXT, lambda e: self._update_param("confirm_image",
                                                                    e.GetString()))
            self.props_sizer.Add(txt_conf, 0, wx.EXPAND | wx.ALL, 4)

            self._add_prop_label("确认超时(秒)")
            txt_to = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_to.SetValue(str(params.get("confirm_timeout", 30)))
            txt_to.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_to.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_to.Bind(wx.EVT_TEXT, lambda e: self._update_param("confirm_timeout",
                                                                  float(
                                                                      e.GetString() or "30")))
            self.props_sizer.Add(txt_to, 0, wx.EXPAND | wx.ALL, 4)

        elif stype == "click_text":
            self._add_prop_label("查找文字")
            txt_text = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_text.SetValue(params.get("text", ""))
            txt_text.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_text.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_text.SetHint("如: 一键恢复")
            txt_text.Bind(wx.EVT_TEXT, lambda e: self._update_param("text",
                                                                    e.GetString()))
            self.props_sizer.Add(txt_text, 0, wx.EXPAND | wx.ALL, 4)

            self._add_region_selector(params.get("region", "全屏"))

        elif stype == "wait_image":
            self._add_prop_label("等待图片 (🎯框选)")
            txt_img = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_img.SetValue(params.get("image", ""))
            txt_img.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_img.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_img.Bind(wx.EVT_TEXT, lambda e: self._update_param("image",
                                                                   e.GetString()))
            self.props_sizer.Add(txt_img, 0, wx.EXPAND | wx.ALL, 4)

            self._add_prop_label("超时(秒)")
            txt_to = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt_to.SetValue(str(params.get("timeout", 30)))
            txt_to.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt_to.SetForegroundColour(wx.Colour(230, 230, 238))
            txt_to.Bind(wx.EVT_TEXT, lambda e: self._update_param("timeout",
                                                                  float(
                                                                      e.GetString() or "30")))
            self.props_sizer.Add(txt_to, 0, wx.EXPAND | wx.ALL, 4)

        elif stype == "go_ditu":
            self._add_prop_label("目的地")
            cbo = wx.ComboBox(self.props_parent, size=(-1, 28),
                              choices=MAP_LIST, style=wx.CB_READONLY)
            cbo.SetValue(params.get("city", "洛阳"))
            cbo.SetBackgroundColour(wx.Colour(18, 18, 22))
            cbo.SetForegroundColour(wx.Colour(230, 230, 238))
            cbo.Bind(wx.EVT_COMBOBOX, lambda e: self._update_param("city",
                                                                   e.GetString()))
            self.props_sizer.Add(cbo, 0, wx.EXPAND | wx.ALL, 4)

        elif stype == "delay":
            self._add_prop_label("等待秒数")
            txt = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt.SetValue(str(params.get("seconds", 3.0)))
            txt.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt.SetForegroundColour(wx.Colour(230, 230, 238))
            txt.Bind(wx.EVT_TEXT, lambda e: self._update_param("seconds",
                                                               float(
                                                                   e.GetString() or "3")))
            self.props_sizer.Add(txt, 0, wx.EXPAND | wx.ALL, 4)

        elif stype == "loop":
            self._add_prop_label("循环次数")
            txt = wx.TextCtrl(self.props_parent, size=(-1, 26))
            txt.SetValue(str(params.get("count", 5)))
            txt.SetBackgroundColour(wx.Colour(18, 18, 22))
            txt.SetForegroundColour(wx.Colour(230, 230, 238))
            txt.Bind(wx.EVT_TEXT, lambda e: self._update_param("count",
                                                               int(e.GetString() or "5")))
            self.props_sizer.Add(txt, 0, wx.EXPAND | wx.ALL, 4)

            self._add_prop_label("子步骤")
            children = params.get("children", [])
            child_text = "、".join(
                [c.get("label", "?") for c in children]) if children else "(空)"
            info = wx.StaticText(self.props_parent,
                                 label=f"包含: {child_text}\n\n添加子步骤: 选中循环→再点积木")
            info.SetForegroundColour(wx.Colour(140, 140, 150))
            info.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                 wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            self.props_sizer.Add(info, 0, wx.ALL, 8)

        # 通用参数: 账号
        self._add_prop_label("操作账号")
        acc = wx.ComboBox(self.props_parent, size=(-1, 28),
                          choices=["队长", "队友1", "队友2"],
                          style=wx.CB_READONLY)
        acc.SetValue(params.get("account", "队长"))
        acc.SetBackgroundColour(wx.Colour(18, 18, 22))
        acc.SetForegroundColour(wx.Colour(230, 230, 238))
        acc.Bind(wx.EVT_COMBOBOX, lambda e: self._update_param("account",
                                                               e.GetString()))
        self.props_sizer.Add(acc, 0, wx.EXPAND | wx.ALL, 4)

        self.props_sizer.Layout()

    def _add_prop_label(self, text):
        lb = wx.StaticText(self.props_parent, label=text)
        lb.SetForegroundColour(wx.Colour(160, 160, 170))
        lb.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.props_sizer.Add(lb, 0, wx.LEFT | wx.TOP, 6)

    def _add_region_selector(self, current):
        self._add_prop_label("搜索区域")
        cbo = wx.ComboBox(self.props_parent, size=(-1, 28),
                          choices=list(REGION_PRESETS.keys()),
                          style=wx.CB_READONLY)
        cbo.SetValue(current if current in REGION_PRESETS else "全屏")
        cbo.SetBackgroundColour(wx.Colour(18, 18, 22))
        cbo.SetForegroundColour(wx.Colour(230, 230, 238))
        cbo.Bind(wx.EVT_COMBOBOX, lambda e: self._update_param("region",
                                                               e.GetString()))
        self.props_sizer.Add(cbo, 0, wx.EXPAND | wx.ALL, 4)

    # ============================================================
    #  事件处理
    # ============================================================
    def _add_step(self, step_type, parent_loop=False):
        if self.selected_step_index >= 0 and not parent_loop:
            step = self.steps[self.selected_step_index]
            if step.get("type") == "loop":
                parent_loop = True

        defaults = {
            "click_image": {"label": "点击图片", "image": "",
                            "region": "全屏", "confidence": 0.8,
                            "wait_after": 2.0, "account": "队长",
                            "offset": "center"},
            "find_and_click": {"label": "点击并确认", "image": "",
                               "confirm_image": "", "region": "全屏",
                               "confirm_region": "全屏",
                               "wait_after": 2.0, "confirm_timeout": 30,
                               "account": "队长"},
            "click_text": {"label": "点击文字", "text": "",
                           "region": "全屏", "confidence": 0.9,
                           "color": "通用游戏字体(白绿黄青红黑底)",
                           "wait_after": 2.0, "account": "队长"},
            "wait_image": {"label": "等待出现", "image": "",
                           "region": "全屏", "timeout": 30},
            "go_ditu": {"label": "传送到地图", "city": "洛阳"},
            "delay": {"label": "等待", "seconds": 3.0},
            "loop": {"label": "循环", "count": 5, "children": []},
        }

        new_step = {"type": step_type,
                    "label": defaults.get(step_type, {}).get("label", "新步骤"),
                    "params": defaults.get(step_type, {})}

        if parent_loop:
            self.steps[self.selected_step_index]["params"].setdefault("children",
                                                                      []).append(
                new_step)
        else:
            insert_at = self.selected_step_index + 1 if self.selected_step_index >= 0 else len(
                self.steps)
            self.steps.insert(insert_at, new_step)
            self.selected_step_index = insert_at

        self._refresh_step_list()
        self._refresh_props_panel()

    def _select_step(self, index):
        self.selected_step_index = index
        self._refresh_step_list()
        self._refresh_props_panel()

    def _step_action(self, index, action):
        if action == "✕":
            del self.steps[index]
            if self.selected_step_index >= len(self.steps):
                self.selected_step_index = len(self.steps) - 1
            self._refresh_step_list()
            self._refresh_props_panel()
        elif action == "▲" and index > 0:
            self.steps[index], self.steps[index - 1] = \
                self.steps[index - 1], self.steps[index]
            if self.selected_step_index == index:
                self.selected_step_index = index - 1
            self._refresh_step_list()
        elif action == "▼" and index < len(self.steps) - 1:
            self.steps[index], self.steps[index + 1] = \
                self.steps[index + 1], self.steps[index]
            if self.selected_step_index == index:
                self.selected_step_index = index + 1
            self._refresh_step_list()

    def _update_param(self, key, value):
        if self.selected_step_index >= 0:
            self.steps[self.selected_step_index]["params"][key] = value

    def _use_template(self, tname):
        if tname == "刷活动副本":
            self.steps = [
                {"type": "go_ditu", "label": "飞往活动地图",
                 "params": {"city": "洛阳"}},
                {"type": "wait_image", "label": "等待活动入口出现",
                 "params": {"image": "模板_活动入口.png", "region": "全屏",
                            "timeout": 15}},
                {"type": "find_and_click", "label": "点击活动入口",
                 "params": {"image": "模板_活动入口.png",
                            "confirm_image": "模板_进入确认.png",
                            "region": "全屏", "confirm_region": "全屏",
                            "wait_after": 2.0, "confirm_timeout": 30}},
                {"type": "loop", "label": "打Boss循环",
                 "params": {"count": 5, "children": [
                     {"type": "find_and_click", "label": "点击Boss",
                      "params": {"image": "模板_Boss.png",
                                 "confirm_image": "模板_战斗画面.png",
                                 "region": "左侧三分之一",
                                 "confirm_region": "全屏",
                                 "wait_after": 2.0, "confirm_timeout": 30}},
                     {"type": "wait_image", "label": "等待战斗结束",
                      "params": {"image": "模板_结束标志.png",
                                 "region": "全屏", "timeout": 90}},
                 ]}},
            ]
        elif tname == "刷地图精英怪":
            self.steps = [
                {"type": "go_ditu", "label": "飞往目的地",
                 "params": {"city": "洛阳"}},
                {"type": "loop", "label": "打精英怪循环",
                 "params": {"count": 10, "children": [
                     {"type": "find_and_click", "label": "点击精英怪",
                      "params": {"image": "素材_精英怪.png",
                                 "confirm_image": "素材_战斗.png",
                                 "region": "左侧三分之一",
                                 "confirm_region": "全屏",
                                 "wait_after": 2.0, "confirm_timeout": 30}},
                     {"type": "wait_image", "label": "等待战斗结束",
                      "params": {"image": "素材_结束.png",
                                 "region": "全屏", "timeout": 90}},
                 ]}},
            ]
        self.selected_step_index = -1
        self._refresh_step_list()
        self._refresh_props_panel()

    def _on_record(self, event):
        if self.recording:
            self.recording = False
            self.btn_record.SetLabel("⏺ 录制")
            self.btn_record.SetBackgroundColour(wx.Colour(180, 50, 40))
            wx.MessageBox("录制已停止", "提示", wx.OK)
        else:
            self.recording = True
            self.btn_record.SetLabel("⏹ 停止")
            self.btn_record.SetBackgroundColour(wx.Colour(200, 50, 40))
            wx.MessageBox(
                "录制已启动\n请在游戏窗口中操作\n完成后点⏹停止",
                "录制中", wx.OK)
            # TODO: 启动hook监听

    def _on_generate(self, event):
        name = self.txt_name.GetValue().strip()
        if not name:
            wx.MessageBox("请先输入脚本名称", "提示", wx.OK | wx.ICON_WARNING)
            return
        if not self.steps:
            wx.MessageBox("请先添加至少一个步骤", "提示", wx.OK | wx.ICON_WARNING)
            return

        gen = CodeGenerator(self.steps, name)
        code = gen.generate()

        script_dir = os.path.join(USER_SCRIPTS_DIR, name)
        if not os.path.exists(script_dir):
            os.makedirs(script_dir)

        script_path = os.path.join(script_dir, "script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        ScriptRegistry.add(name,
                           {"steps": self.steps, "code": code})

        self.script_name = name
        wx.MessageBox(
            f"脚本已生成!\n\n📁 {script_path}\n\n"
            f"请在主窗口下拉框中选择 \"📝 {name}\" 运行",
            "生成成功", wx.OK | wx.ICON_INFORMATION)

    def _on_save(self, event):
        name = self.txt_name.GetValue().strip()
        if not name:
            wx.MessageBox("请先输入脚本名称", "提示", wx.OK | wx.ICON_WARNING)
            return
        if not self.steps:
            wx.MessageBox("请先添加至少一个步骤", "提示", wx.OK | wx.ICON_WARNING)
            return

        self._on_generate(None)

    def _on_run(self, event):
        wx.MessageBox(
            "请在主窗口下拉框选择脚本后点▶开始运行\n\n"
            "脚本工厂仅用于制作脚本，运行通过主窗口。",
            "提示", wx.OK | wx.ICON_INFORMATION)


# ============================================================
#  集成到主窗口
# ============================================================
def get_user_script_choices():
    """获取用户脚本列表，用于主窗口下拉框"""
    names = ScriptRegistry.list_names()
    return [f"📝 {n}" for n in names]
