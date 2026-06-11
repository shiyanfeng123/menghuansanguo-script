"""自动战斗脚本 - CombatAutoScript 完整实现"""
import time
import threading
import wx
from datetime import datetime

_e = None
_combat_thread = None
_combat_running = False
_report_dialog = None
_auto_script = None


# ==================== 常量定义 ====================
class CombatConstants:
    DEFAULT_SIMILARITY = 0.7
    DEFAULT_TIMEOUT = 3
    DEFAULT_CHECK_INTERVAL = 0.08
    TURN_TIMEOUT = 25
    CLICK_DELAY = 0.05
    ACTION_DELAY = 0.1
    SKILL_CLICK_VERIFY_DELAY = 0.4


# ==================== 战斗播报窗口 ====================
class BattleReportDialog(wx.Frame):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_TITLE_BG = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(100, 105, 115)
    C_WHITE = wx.Colour(255, 255, 255)
    C_GREEN = wx.Colour(39, 174, 96)
    C_RED = wx.Colour(192, 57, 43)
    C_BLUE = wx.Colour(41, 128, 185)
    C_ORANGE = wx.Colour(230, 160, 50)
    C_LOG_BG = wx.Colour(250, 250, 255)
    C_DIVIDER = wx.Colour(215, 218, 226)
    C_ACCENT = wx.Colour(50, 80, 140)

    def __init__(self, parent=None):
        super().__init__(
            parent, title="战斗实时播报", size=(520, 500),
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        )
        self.SetBackgroundColour(self.C_BG)
        self._start_time = None
        self._timer = None
        self.log_lock = threading.Lock()
        self._log_line_count = 0
        self._max_log_lines = 500
        self._trim_keep_lines = 300

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        root = wx.BoxSizer(wx.VERTICAL)

        title_bar = wx.Panel(panel)
        title_bar.SetBackgroundColour(self.C_TITLE_BG)
        ts = wx.BoxSizer(wx.HORIZONTAL)
        title_lbl = wx.StaticText(title_bar, label="  战斗实时播报", style=wx.ALIGN_LEFT)
        title_lbl.SetForegroundColour(self.C_WHITE)
        ts.Add(title_lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        self._status_dot = wx.StaticText(title_bar, label="  \u25cf 就绪  ", style=wx.ALIGN_RIGHT)
        self._status_dot.SetForegroundColour(wx.Colour(180, 180, 190))
        ts.Add(self._status_dot, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        title_bar.SetSizer(ts)
        root.Add(title_bar, 0, wx.EXPAND)

        summary_bar = wx.Panel(panel)
        summary_bar.SetBackgroundColour(self.C_SURFACE)
        ss = wx.BoxSizer(wx.HORIZONTAL)
        self._lbl_turn = self._make_summary_label(summary_bar, "回合: 0")
        self._lbl_time = self._make_summary_label(summary_bar, "运行: --:--")
        self._lbl_state = self._make_summary_label(summary_bar, "状态: 等待中")
        ss.Add(self._lbl_turn, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        ss.Add(self._lbl_time, 1, wx.ALIGN_CENTER_VERTICAL)
        ss.Add(self._lbl_state, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        summary_bar.SetSizer(ss)
        root.Add(summary_bar, 0, wx.EXPAND | wx.TOP, 1)

        status_card = wx.Panel(panel)
        status_card.SetBackgroundColour(self.C_WHITE)
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._account_panels = {}
        for idx, name in [(0, "中排"), (1, "上排"), (2, "下排")]:
            ap = self._create_account_panel(status_card, idx, name)
            status_sizer.Add(ap, 1, wx.EXPAND | wx.ALL, 3)
        status_card.SetSizer(status_sizer)
        root.Add(status_card, 0, wx.EXPAND | wx.TOP, 1)

        log_panel = wx.Panel(panel)
        log_panel.SetBackgroundColour(self.C_LOG_BG)
        ls = wx.BoxSizer(wx.VERTICAL)
        self.log_text = wx.TextCtrl(
            log_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        self.log_text.SetBackgroundColour(self.C_LOG_BG)
        ls.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 2)
        log_panel.SetSizer(ls)
        root.Add(log_panel, 1, wx.EXPAND | wx.TOP, 1)

        btn_bar = wx.Panel(panel)
        btn_bar.SetBackgroundColour(self.C_SURFACE)
        bs = wx.BoxSizer(wx.HORIZONTAL)
        self.export_button = wx.Button(btn_bar, label="导出日志", size=(80, 26))
        self.export_button.SetBackgroundColour(self.C_ACCENT)
        self.export_button.SetForegroundColour(self.C_WHITE)
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export_txt)
        self.clear_button = wx.Button(btn_bar, label="清空日志", size=(80, 26))
        self.clear_button.SetBackgroundColour(self.C_DIVIDER)
        self.clear_button.SetForegroundColour(self.C_MUTED)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)
        bs.AddStretchSpacer()
        bs.Add(self.export_button, 0, wx.ALL, 3)
        bs.Add(self.clear_button, 0, wx.ALL, 3)
        btn_bar.SetSizer(bs)
        root.Add(btn_bar, 0, wx.EXPAND)

        panel.SetSizer(root)
        self.add_log("战斗播报系统已启动", "system")
        self.add_log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "action")

    def _make_summary_label(self, parent, text):
        lbl = wx.StaticText(parent, label=text)
        lbl.SetForegroundColour(self.C_MUTED)
        return lbl

    def _create_account_panel(self, parent, idx, name):
        panel = wx.Panel(parent)
        panel.SetBackgroundColour(self.C_SURFACE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        header = wx.StaticText(panel, label=f"账号{idx}({name})")
        header.SetForegroundColour(self.C_ACCENT)
        sizer.Add(header, 0, wx.ALIGN_CENTER | wx.TOP, 4)
        lbl_main = wx.StaticText(panel, label="主角: --")
        lbl_main.SetForegroundColour(self.C_TEXT)
        sizer.Add(lbl_main, 0, wx.LEFT, 8)
        lbl_gen = wx.StaticText(panel, label="武将: --")
        lbl_gen.SetForegroundColour(self.C_TEXT)
        sizer.Add(lbl_gen, 0, wx.LEFT, 8)
        lbl_lb = wx.StaticText(panel, label="刘备: --")
        lbl_lb.SetForegroundColour(self.C_TEXT)
        sizer.Add(lbl_lb, 0, wx.LEFT | wx.BOTTOM, 4)
        panel.SetSizer(sizer)
        self._account_panels[idx] = {
            "panel": panel, "main": lbl_main, "general": lbl_gen, "liubei": lbl_lb
        }
        return panel

    def set_running(self, running=True):
        def _update():
            try:
                if running:
                    self._status_dot.SetLabel("  \u25cf 战斗中  ")
                    self._status_dot.SetForegroundColour(self.C_GREEN)
                    self._lbl_state.SetLabel("状态: 战斗中")
                    self._start_time = datetime.now()
                    self._ensure_timer()
                else:
                    self._status_dot.SetLabel("  \u25cf 已停止  ")
                    self._status_dot.SetForegroundColour(self.C_RED)
                    self._lbl_state.SetLabel("状态: 已停止")
                    self._stop_timer()
            except Exception:
                pass
        self._safe_call_after(_update)

    def _ensure_timer(self):
        self._stop_timer()
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick, self._timer)
        self._timer.Start(1000)

    def _stop_timer(self):
        if self._timer:
            try:
                self._timer.Stop()
            except Exception:
                pass
            self._timer = None

    def _on_tick(self, event):
        if self._start_time:
            elapsed = datetime.now() - self._start_time
            mins, secs = divmod(int(elapsed.total_seconds()), 60)
            hrs, mins = divmod(mins, 60)
            if hrs > 0:
                self._lbl_time.SetLabel(f"运行: {hrs}:{mins:02d}:{secs:02d}")
            else:
                self._lbl_time.SetLabel(f"运行: {mins}:{secs:02d}")

    def update_turn(self, turn_num):
        def _update():
            try:
                self._lbl_turn.SetLabel(f"回合: {turn_num}")
            except Exception:
                pass
        self._safe_call_after(_update)

    def update_account_status(self, idx, main_alive=True, main_status="正常",
                               general_alive=0, general_total=2, has_liubei=False):
        def _update():
            try:
                if idx not in self._account_panels:
                    return
                ap = self._account_panels[idx]
                if main_alive:
                    color = self.C_GREEN if main_status == "正常" else self.C_ORANGE
                    ap["main"].SetLabel(f"主角: \u25cf {main_status}")
                    ap["main"].SetForegroundColour(color)
                else:
                    ap["main"].SetLabel("主角: \u25cb 阵亡")
                    ap["main"].SetForegroundColour(self.C_RED)
                if general_alive < 0:
                    ap["general"].SetLabel("武将: --")
                    ap["general"].SetForegroundColour(self.C_MUTED)
                else:
                    gc = self.C_GREEN if general_alive == general_total else (self.C_ORANGE if general_alive > 0 else self.C_RED)
                    ap["general"].SetLabel(f"武将: {general_alive}/{general_total}")
                    ap["general"].SetForegroundColour(gc)
                if has_liubei:
                    ap["liubei"].SetLabel("刘备: \u25cf 在场")
                    ap["liubei"].SetForegroundColour(self.C_GREEN)
                else:
                    ap["liubei"].SetLabel("刘备: -")
                    ap["liubei"].SetForegroundColour(self.C_MUTED)
            except Exception:
                pass
        self._safe_call_after(_update)

    def reset_status(self):
        def _update():
            try:
                self._lbl_turn.SetLabel("回合: 0")
                self._lbl_time.SetLabel("运行: --:--")
                self._lbl_state.SetLabel("状态: 等待中")
                self._status_dot.SetLabel("  \u25cf 就绪  ")
                self._status_dot.SetForegroundColour(wx.Colour(180, 180, 190))
                self._start_time = None
                for idx in self._account_panels:
                    ap = self._account_panels[idx]
                    ap["main"].SetLabel("主角: --")
                    ap["main"].SetForegroundColour(self.C_TEXT)
                    ap["general"].SetLabel("武将: --")
                    ap["general"].SetForegroundColour(self.C_TEXT)
                    ap["liubei"].SetLabel("刘备: --")
                    ap["liubei"].SetForegroundColour(self.C_TEXT)
            except Exception:
                pass
        self._safe_call_after(_update)

    def add_log(self, message, color=None):
        if color is None:
            color = "info"
        if isinstance(color, str):
            color_map = {
                "info": self.C_TEXT,
                "success": self.C_GREEN,
                "warning": self.C_ORANGE,
                "error": self.C_RED,
                "system": self.C_ACCENT,
                "turn": self.C_BLUE,
                "action": self.C_MUTED,
            }
            color = color_map.get(color, self.C_TEXT)
        def _add_log():
            try:
                if not self or not hasattr(self, "log_text") or not self.log_text:
                    return
                with self.log_lock:
                    self._log_line_count += 1
                    if self._log_line_count > self._max_log_lines:
                        self._trim_log()
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] {message}\n"
                    self.log_text.SetDefaultStyle(wx.TextAttr(color))
                    self.log_text.AppendText(full_message)
                    try:
                        self.log_text.ShowPosition(self.log_text.GetLastPosition())
                        self.log_text.Refresh()
                    except (AttributeError, RuntimeError):
                        pass
            except Exception:
                pass
        self._safe_call_after(_add_log)

    def _trim_log(self):
        try:
            content = self.log_text.GetValue()
            lines = content.split("\n")
            if len(lines) > self._trim_keep_lines:
                keep = lines[-self._trim_keep_lines:]
                self.log_text.SetValue("\n".join(keep))
                self._log_line_count = len(keep)
        except Exception:
            pass

    def _safe_call_after(self, func):
        try:
            if threading.current_thread() == threading.main_thread():
                func()
            else:
                if hasattr(wx, "CallAfter"):
                    wx.CallAfter(func)
                else:
                    func()
        except Exception:
            pass

    def on_clear(self, event):
        self.log_text.Clear()
        self._log_line_count = 0
        self.add_log("日志已清空", "action")

    def on_export_txt(self, event):
        try:
            with wx.FileDialog(
                self, "保存日志文件", wildcard="文本文件 (*.txt)|*.txt",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            ) as fileDialog:
                default_filename = f"战斗播报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                fileDialog.SetFilename(default_filename)
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                filepath = fileDialog.GetPath()
                with self.log_lock:
                    log_content = self.log_text.GetValue()
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write("战斗播报日志\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(log_content)
                wx.MessageBox(f"日志已成功导出到:\n{filepath}", "导出成功", wx.OK | wx.ICON_INFORMATION)
                self.add_log(f"日志已导出到: {filepath}", "system")
        except Exception as e:
            print(f"导出日志时发生异常: {e}")

    def close_safely(self):
        try:
            if not self:
                return
            def _close_window():
                try:
                    self._stop_timer()
                    if self and hasattr(self, "IsBeingDeleted") and not self.IsBeingDeleted():
                        self.Destroy()
                except Exception as e:
                    print(f"关闭战斗播报窗口时出错: {e}")
            if threading.current_thread() == threading.main_thread():
                _close_window()
            else:
                if hasattr(wx, "CallAfter"):
                    wx.CallAfter(_close_window)
                else:
                    _close_window()
        except Exception as e:
            print(f"close_safely调用时出错: {e}")


# ==================== 战斗自动操作脚本 ====================
class CombatAutoScript:
    def __init__(self, engine, enemy_keys_to_detect=None):
        self.engine = engine
        self.enemy_keys_to_detect = enemy_keys_to_detect if enemy_keys_to_detect else []
        self.battle_report_dialog = None
        self._dialog_closed = False
        self._state_lock = threading.Lock()
        self.current_turn = 0
        self.turn_start_time = None
        self.polling_running = False
        self.polling_thread = None
        self.skill_cd = {}
        self.attack_buff_tracker = {}
        self.low_hp_accounts = {}
        self.account_error_count = {}
        self.enemies_need_clear = {}
        self.enemy_status_reported = {}
        self.liubei_skill_index = {}
        self.liubei_skill_cd = {}
        self.revive_assignments = {}
        self.has_liubei = {0: True, 1: False, 2: False}
        self.has_general = {0: True, 1: True, 2: True}
        self._timer_refs = []
        self.skill_strategies = {
            "main_char": [
                {"priority": 80, "skill": "锁魂",       "condition": "always"},
                {"priority": 60, "skill": "寂灭神劫",    "condition": "always"},
                {"priority": 50, "skill": "天灾",        "condition": "always"},
                {"priority": -1, "skill": "防御",        "condition": "always"},
            ],
            "attack": [
                {"priority": 80, "skill": "剑阵灭杀",    "condition": "always"},
                {"priority": 50, "skill": "武神一怒",    "condition": "always"},
                {"priority": -1, "skill": "防御",        "condition": "always"},
            ],
            "support": [
                {"priority": 100, "skill": "清除状态",   "condition": "enemies_need_clear"},
                {"priority": 90,  "skill": "加血",       "condition": "ally_hp_critical"},
                {"priority": 80,  "skill": "控制",       "condition": "always"},
                {"priority": 75,  "skill": "加攻击",     "condition": "attack_buff_expired"},
                {"priority": 70,  "skill": "加血",       "condition": "ally_hp_low"},
                {"priority": 10,  "skill": None,         "condition": "always",
                 "sequence": ["控制", "加攻击", "加血"]},
                {"priority": -1,  "skill": "防御",       "condition": "always"},
            ],
        }

        try:
            timer = threading.Timer(0.3, self._create_battle_report_dialog)
            self._timer_refs.append(timer)
            timer.start()
        except Exception:
            pass

        self._init_combat_regions()
        self.unit_info = {}
        self.dead_units = {}
        self.global_dead_units = {"main_chars": [], "generals": []}
        self._init_unit_info()

    def _init_combat_regions(self):
        self.enemy_region = (54, 168, 370, 541)
        self.ally_region = (450, 162, 900, 580)
        self.right_button_region = (610, 203, 680, 436)
        self.skill_panel_region = (480, 167, 607, 550)
        self.summon_panel_region = (480, 167, 607, 550)
        self.item_panel_region = (0, 0, 900, 550)
        self.zdzd_region = (0, 0, 900, 580)

        self.general_images = {
            "刘备": "serveAssets/images/auto/miankong1.bmp",
            "魔化关羽": "serveAssets/images/auto/gangqi1.bmp|serveAssets/images/auto/shenyou1.bmp",
            "曹操": "serveAssets/images/auto/bawang1.bmp|serveAssets/images/auto/luanshi1.bmp",
        }

        self.skill_images = {
            "寂灭神劫": "serveAssets/images/auto/jimie1.bmp|serveAssets/images/auto/jimie2.bmp",
            "锁魂": "serveAssets/images/auto/suohun1.bmp|serveAssets/images/auto/suohun2.bmp",
            "天灾": "serveAssets/images/auto/tianzai1.bmp|serveAssets/images/auto/tianzai2.bmp",
            "剑阵灭杀": "serveAssets/images/auto/jimie1.bmp|serveAssets/images/auto/jimie2.bmp",
            "武神一怒": "serveAssets/images/auto/suohun1.bmp|serveAssets/images/auto/suohun2.bmp",
            "加血": "serveAssets/images/auto/fuhuo1.bmp|serveAssets/images/auto/fuhuo.bmp",
            "清除状态": "serveAssets/images/auto/liubeijie1.bmp|serveAssets/images/auto/liubeijie2.bmp",
            "控制": "serveAssets/images/auto/liubeikong1.bmp|serveAssets/images/auto/liubeikong2.bmp",
            "加攻击": "serveAssets/images/auto/liubeizengshang1.bmp|serveAssets/images/auto/liubeizengshang2.bmp",
            "复活": "serveAssets/images/auto/fuhuo1.bmp|serveAssets/images/auto/fuhuo.bmp",
        }

        self.button_images = {
            "技能按钮": "serveAssets/images/auto/jineng.bmp|serveAssets/images/auto/jineng1.bmp",
            "召唤按钮": "serveAssets/images/auto/zhaohuan.bmp|serveAssets/images/auto/zhaohuan1.bmp",
            "道具按钮": "serveAssets/images/auto/yaopin.bmp|serveAssets/images/auto/yaopin1.bmp",
            "防御按钮": "serveAssets/images/auto/fangyu.bmp",
            "操作按钮": "serveAssets/images/auto/jineng.bmp|serveAssets/images/auto/jineng1.bmp",
            "取消按钮": "ya_assets/images/closeJJ.bmp",
        }

        self.zdzd_image = "ya_assets/images/zdzd.bmp|ya_assets/images/zdzd111.bmp"
        self.liubei_image = "serveAssets/images/auto/liubei2.bmp|serveAssets/images/auto/liubei3.bmp|ya_assets/images/zhanhun/liubei.bmp"
        self.tiandihudun_image = "serveAssets/images/auto/tiandihudun1.bmp"

        self.hp_bar_regions = [
            (755, 229, 786, 279),
            (795, 319, 827, 374),
            (835, 437, 870, 491),
            (690, 221, 722, 278),
            (722, 319, 757, 376),
            (760, 437, 793, 491),
            (627, 218, 657, 277),
            (660, 318, 690, 375),
            (695, 434, 727, 490),
        ]

        self.tombstone_images = [
            "serveAssets/images/auto/mubei.bmp",
            "serveAssets/images/auto/mubei1.bmp",
            "serveAssets/images/auto/mubei2.bmp",
            "serveAssets/images/auto/mubei3.bmp",
            "serveAssets/images/auto/mubei4.bmp",
            "serveAssets/images/auto/mubei5.bmp",
        ]

        self.low_hp_indicator_image = "serveAssets/images/auto/xueliangbuzu1.bmp|serveAssets/images/auto/xueliangbuzu2.bmp"

        self.enemy_general_config = {
            "诸葛亮": {
                "status_images": {
                    "状态1": "serveAssets/images/auto/bumiexiongxin1.bmp",
                    "状态2": "serveAssets/images/auto/gangqi1.bmp",
                },
                "status_region": (61, 257, 158, 318),
                "cast_position": (104, 344),
            },
            "赵云29": {
                "status_images": {
                    "状态1": "serveAssets/images/auto/longdan1.bmp|serveAssets/images/auto/longdan2.bmp",
                },
                "status_region": (54, 168, 280, 541),
                "cast_position": (115, 446),
            },
        }

        self.skill_cd_config = {
            "加血": 2,
            "清除状态": 4,
            "加攻击": 0,
            "控制": 0,
            "寂灭神劫": 3,
            "锁魂": 2,
            "天灾": 2,
            "剑阵灭杀": 0,
            "武神一怒": 0,
        }

    def _init_unit_info(self):
        for i in range(3):
            if i == 0:
                main_char_position = (793, 380)
            elif i == 1:
                main_char_position = (764, 278)
            else:
                main_char_position = (825, 490)

            self.unit_info[i] = {
                "main_char": {
                    "name": "主角",
                    "position": main_char_position,
                    "alive": True,
                    "need_revive": False,
                    "generals": [],
                },
            }
            self.dead_units[i] = {"main_char": None, "generals": []}
            self.enemies_need_clear[i] = []
            self.skill_cd[i] = {}
            self.liubei_skill_index[i] = 0
            self.liubei_skill_cd[i] = {}
            self.low_hp_accounts[i] = 0

    def _create_battle_report_dialog(self):
        if self._dialog_closed:
            return
        try:
            app = wx.GetApp()
            if app is None:
                return
        except (AttributeError, RuntimeError):
            return
        try:
            self.battle_report_dialog = BattleReportDialog()
            self.battle_report_dialog.Show()
        except Exception:
            pass

    def report_battle_info(self, message, msg_type="info"):
        if self._dialog_closed:
            return
        if self.battle_report_dialog is None:
            try:
                if hasattr(wx, "GetApp") and wx.GetApp() and not self._dialog_closed:
                    wx.CallAfter(self._create_battle_report_dialog)
            except (AttributeError, RuntimeError):
                pass
        if self.battle_report_dialog:
            try:
                self.battle_report_dialog.add_log(message, msg_type)
            except Exception:
                pass

    def find_image(self, image_path, region, threshold=None):
        if threshold is None:
            threshold = CombatConstants.DEFAULT_SIMILARITY
        return self.engine.find_pic(image_path, region, threshold)

    def click_position(self, x, y):
        self.engine.click(int(x), int(y))
        time.sleep(CombatConstants.CLICK_DELAY)

    def get_running(self):
        return self.polling_running

    def start_polling_loop(self):
        if self.polling_running:
            return
        self.polling_running = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()

    def stop_polling_loop(self):
        self.polling_running = False
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2.0)
        self.polling_thread = None

    def _polling_loop(self):
        self.report_battle_info("开始轮询监听战斗状态", "system")
        if self.battle_report_dialog:
            self.battle_report_dialog.set_running(True)

        step0_completed = False
        while not step0_completed and self.polling_running:
            zdzd = self.find_image(self.zdzd_image, self.zdzd_region)
            if zdzd:
                cancel = self.find_image(self.button_images["取消按钮"], self.zdzd_region)
                if cancel:
                    self.click_position(cancel.x, cancel.y)
                    self.report_battle_info("检测到zdzd弹窗，已点击取消", "warning")
                    step0_completed = True
                    break
            if self.find_image(self.button_images["操作按钮"], self.right_button_region):
                step0_completed = True
                break
            time.sleep(0.1)

        while self.polling_running:
            try:
                zdzd = self.find_image(self.zdzd_image, self.zdzd_region)
                if zdzd:
                    cancel = self.find_image(self.button_images["取消按钮"], self.zdzd_region)
                    if cancel:
                        self.click_position(cancel.x, cancel.y)
                        self.report_battle_info("检测到zdzd弹窗，已点击取消", "warning")
                        time.sleep(0.5)

                has_action = self.find_image(self.button_images["操作按钮"], self.right_button_region)

                if has_action:
                    for acc in [0, 1, 2]:
                        if not self.polling_running:
                            break
                        self.handle_our_turn(acc)

                    if self.current_turn <= 1:
                        self.current_turn = 2
                    else:
                        self.current_turn += 1

                    for acct in list(self.attack_buff_tracker.keys()):
                        self.attack_buff_tracker[acct] -= 1
                        if self.attack_buff_tracker[acct] <= 0:
                            del self.attack_buff_tracker[acct]

                    if self.battle_report_dialog:
                        self.battle_report_dialog.update_turn(self.current_turn)
                    self.report_battle_info(f"回合 {self.current_turn} 结束", "turn")
                    time.sleep(0.1)

                for acc in [0, 1, 2]:
                    if not self.polling_running:
                        break
                    self.check_tombstones(acc)

                if self.enemy_keys_to_detect:
                    self.detect_enemies_need_clear()

                self._detect_liubei_on_field()

                self.low_hp_accounts = {}
                for acct in [0, 1, 2]:
                    cnt = 0
                    for ridx, region in enumerate(self.hp_bar_regions):
                        if self.low_hp_indicator_image and self.find_image(
                            self.low_hp_indicator_image, region
                        ):
                            cnt += 1
                    self.low_hp_accounts[acct] = cnt

                if self.polling_running:
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

            except Exception as e:
                self.report_battle_info(f"轮询监听出错: {e}", "error")
                if self.polling_running:
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

        self.report_battle_info("轮询监听循环已结束", "system")
        if self.battle_report_dialog:
            self.battle_report_dialog.set_running(False)

    def handle_our_turn(self, account_index):
        try:
            skill_btn = self.find_image(self.button_images["技能按钮"], self.right_button_region)
            if skill_btn:
                self.click_position(skill_btn.x, skill_btn.y)
                time.sleep(0.1)

            char_info = self.unit_info[account_index]["main_char"]
            is_first_turn = self.current_turn <= 1
            need_liubei = False
            need_summon_general = False

            if not is_first_turn:
                has_dead_general = False
                for dead_gen in self.global_dead_units["generals"]:
                    if dead_gen.get("account_index") == account_index:
                        has_dead_general = True
                        break

                for gen_info in char_info.get("generals", []):
                    if not gen_info.get("alive", True):
                        has_dead_general = True
                        break

                if char_info.get("alive", True) and has_dead_general:
                    has_liubei_on_field = self.has_liubei.get(account_index, False)

                    has_liubei_in_account = False
                    for gen_info in char_info.get("generals", []):
                        if gen_info.get("name") == "刘备" and gen_info.get("alive", True):
                            has_liubei_in_account = True
                            break

                    if not has_liubei_on_field and not has_liubei_in_account:
                        need_liubei = True
                    else:
                        need_summon_general = True

            need_self_liubei = False
            if (self.enemies_need_clear.get(account_index)
                    and not any(g.get("name") == "刘备" and g.get("alive", True)
                               for g in char_info.get("generals", []))
                    and char_info.get("alive", True)):
                need_self_liubei = True

            if need_liubei or need_self_liubei:
                if self._try_summon_general(account_index, "刘备"):
                    time.sleep(0.1)
                    return

            if need_summon_general:
                for gen_name in ["曹操", "魔化关羽", "刘备"]:
                    if self._try_summon_general(account_index, gen_name):
                        time.sleep(0.1)
                        return

            assigned_revive = self.revive_assignments.get(account_index)
            if assigned_revive is not None:
                if self._try_revive(account_index, assigned_revive):
                    time.sleep(0.1)
                    return

            unit_type = "main_char"
            self._execute_best_strategy(account_index, unit_type)

        except Exception as e:
            self.report_battle_info(f"账号{account_index}回合处理出错: {e}", "error")

    def _try_summon_general(self, account_index, general_name):
        summon_btn = self.find_image(self.button_images["召唤按钮"], self.right_button_region)
        if not summon_btn:
            return False
        self.click_position(summon_btn.x, summon_btn.y)
        time.sleep(CombatConstants.ACTION_DELAY)

        general_img = self.general_images.get(general_name)
        if not general_img:
            return False

        target = self.find_image(general_img, self.summon_panel_region)
        if target:
            self.click_position(target.x, target.y)
            self.report_battle_info(f"账号{account_index} 召唤{general_name}", "success")

            if account_index == 0:
                pos = (572, 380)
            elif account_index == 1:
                pos = (530, 278)
            else:
                pos = (520, 490)

            time.sleep(0.3)
            self.click_position(pos[0], pos[1])

            char_info = self.unit_info[account_index]["main_char"]
            char_info["generals"].append({
                "name": general_name,
                "alive": True,
                "position": pos,
                "account_index": account_index,
            })
            return True
        return False

    def _try_revive(self, account_index, target_account):
        item_btn = self.find_image(self.button_images["道具按钮"], self.right_button_region)
        if not item_btn:
            return False
        self.click_position(item_btn.x, item_btn.y)
        time.sleep(CombatConstants.ACTION_DELAY)

        revive_img = self.skill_images.get("复活")
        if not revive_img:
            return False

        target = self.find_image(revive_img, self.item_panel_region)
        if target:
            self.click_position(target.x, target.y)
            time.sleep(0.3)
            target_pos = self.unit_info[target_account]["main_char"]["position"]
            self.click_position(target_pos[0], target_pos[1])
            self.report_battle_info(f"账号{account_index} 复活账号{target_account}主角", "success")
            return True
        return False

    def _execute_best_strategy(self, account_index, unit_type):
        if unit_type not in self.skill_strategies:
            return False
        strategies = sorted(
            self.skill_strategies[unit_type], key=lambda s: s["priority"], reverse=True
        )
        for st in strategies:
            if not self._evaluate_condition(account_index, st["condition"]):
                continue
            skill = st["skill"]
            if skill is None and "sequence" in st:
                idx = self.liubei_skill_index.get(account_index, 0)
                seq = st["sequence"]
                skill = seq[idx % len(seq)]
                self.liubei_skill_index[account_index] = (idx + 1) % len(seq)
            if self._try_release_skill(account_index, skill, unit_type):
                return True
        return False

    def _evaluate_condition(self, account_index, cond):
        if cond == "always":
            return True
        elif cond == "enemies_need_clear":
            return (account_index in self.enemies_need_clear
                    and bool(self.enemies_need_clear[account_index]))
        elif cond == "ally_hp_critical":
            return self.low_hp_accounts.get(account_index, 0) >= 1
        elif cond == "ally_hp_low":
            return self.low_hp_accounts.get(account_index, 0) >= 2
        elif cond == "attack_buff_expired":
            return self.attack_buff_tracker.get(account_index, 0) <= 0
        return True

    def _try_release_skill(self, account_index, skill_name, caller_hint=""):
        if skill_name == "防御":
            defense = self.find_image(self.button_images["防御按钮"], self.right_button_region)
            if defense:
                self.click_position(defense.x, defense.y)
                self.report_battle_info(f"账号{account_index} {caller_hint}执行防御", "action")
                time.sleep(CombatConstants.ACTION_DELAY)
                return True
            return False

        skill_path = self.skill_images.get(skill_name)
        if not skill_path:
            return False

        skill_pos = self.find_image(skill_path, self.skill_panel_region)
        if not skill_pos:
            return False

        self.click_position(skill_pos.x, skill_pos.y)
        self.report_battle_info(f"账号{account_index} 释放{skill_name}", "action")
        time.sleep(CombatConstants.SKILL_CLICK_VERIFY_DELAY)

        cd = self.skill_cd_config.get(skill_name, 0)
        if cd > 0:
            self.skill_cd[account_index] = self.skill_cd.get(account_index, {})
            self.skill_cd[account_index][skill_name] = self.current_turn

        return True

    def check_tombstones(self, account_index):
        dead_list = []
        for region_idx, region in enumerate(self.hp_bar_regions):
            for tomb_path in self.tombstone_images:
                tomb_pos = self.find_image(tomb_path, region)
                if tomb_pos:
                    dead_list.append((account_index, region_idx, tomb_pos))
                    break
        return dead_list

    def detect_enemies_need_clear(self):
        is_first_turn = self.current_turn <= 1
        if is_first_turn:
            return

        for acc in [0, 1, 2]:
            if acc not in self.enemies_need_clear:
                self.enemies_need_clear[acc] = []

        for enemy_key in self.enemy_keys_to_detect:
            if enemy_key not in self.enemy_general_config:
                continue
            config = self.enemy_general_config[enemy_key]
            status_region = config["status_region"]
            status_images = config["status_images"]
            cast_position = config["cast_position"]

            for status_name, status_path in status_images.items():
                if self.find_image(status_path, status_region):
                    enemy_name = enemy_key
                    if enemy_name not in self.enemy_status_reported:
                        self.report_battle_info(f"检测到敌军{enemy_name}在场({status_name})", "warning")
                        self.enemy_status_reported[enemy_name] = True

    def _detect_liubei_on_field(self):
        liubei_pos = self.find_image(self.liubei_image, self.ally_region)
        with self._state_lock:
            if liubei_pos:
                self.has_liubei[0] = True
            tiandihudun_pos = self.find_image(self.tiandihudun_image, self.ally_region)
            if tiandihudun_pos:
                self.has_liubei[0] = True

    def cleanup(self, join_timeout=2.0):
        try:
            self.polling_running = False
        except Exception:
            pass
        for timer in list(self._timer_refs):
            try:
                timer.cancel()
            except Exception:
                pass
        self._timer_refs.clear()
        try:
            if self.polling_thread and self.polling_thread.is_alive():
                self.polling_thread.join(timeout=join_timeout)
            self.polling_thread = None
        except Exception:
            pass
        try:
            if self.battle_report_dialog:
                self.battle_report_dialog.close_safely()
                self.battle_report_dialog = None
            self._dialog_closed = True
        except Exception:
            pass


# ==================== 入口函数 ====================
def zidongzhandou(engine):
    global _e, _combat_running, _report_dialog, _auto_script
    _e = engine
    _combat_running = True
    engine.beginFun()

    try:
        app = wx.GetApp()
        if app is None:
            pass
    except (AttributeError, RuntimeError):
        pass

    try:
        _report_dialog = BattleReportDialog()
        _report_dialog.Show()
    except Exception as e:
        print(f"创建播报窗口失败: {e}")
        _report_dialog = None

    _auto_script = CombatAutoScript(engine)

    if _report_dialog:
        _auto_script.battle_report_dialog = _report_dialog
        _report_dialog.set_running(True)

    _auto_script.polling_running = True
    engine.beginFun()

    try:
        _auto_script._polling_loop()
    except Exception as e:
        print(f"战斗脚本异常: {e}")
    finally:
        _combat_running = False
        _auto_script.cleanup()
        if _report_dialog:
            _report_dialog.set_running(False)


def stop_combat():
    global _combat_running, _auto_script
    _combat_running = False
    if _auto_script:
        _auto_script.stop_polling_loop()
