"""
梦幻三国战斗自动操作脚本
功能：自动执行主角和武将的战斗操作
"""

import sys
import os
import time
import random
import threading
import wx
import wx.lib.scrolledpanel as scrolled
from datetime import datetime


# ==================== 常量定义 ====================
class CombatConstants:
    """战斗脚本常量定义"""

    # 屏幕尺寸限制
    MAX_SCREEN_WIDTH = 2000
    MAX_SCREEN_HEIGHT = 2000

    # 图片识别相似度
    DEFAULT_SIMILARITY = 0.7

    # 超时时间（秒）
    DEFAULT_TIMEOUT = 3
    QUICK_TIMEOUT = 1
    PANEL_WAIT_TIMEOUT = 0.5

    # 检测间隔（秒）
    DEFAULT_CHECK_INTERVAL = 0.08

    # 回合超时时间（秒）
    TURN_TIMEOUT = 25

    # 错误处理
    MAX_ERRORS_PER_TURN = 5
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5

    # 窗口绑定重试
    MAX_BATTLE_DIALOG_RETRIES = 10
    BATTLE_DIALOG_RETRY_DELAY = 1.0

    # 坐标检测半径（像素）
    TOMBSTONE_DETECTION_RADIUS = 30
    STATUS_DETECTION_RADIUS = 40

    # 操作延迟（秒）
    CLICK_DELAY = 0.001
    MOVE_DELAY = 0.2
    ACTION_DELAY = 0.1
    SKILL_CLICK_VERIFY_DELAY = 0.4  # 技能点击后验证等待时间

    # 战斗循环配置
    MAX_COMBAT_ATTEMPTS = 1000000
    COMBAT_PAGE_CHECK_INTERVAL = 20
    STATUS_CHECK_INTERVAL = 4
    WAIT_MSG_INTERVAL = 100
    INIT_WAIT_TIME = 2.0
    MAX_BIND_WAIT_ATTEMPTS = 10
    BIND_WAIT_DELAY = 1.5


# 修复：避免循环引用，移除直接导入
# from serveScript import MyThread  # 不再需要直接导入


# 定义 ResXy 类（避免循环引用）
class ResXy:
    """坐标结果类"""

    # 初始化坐标对象
    # :param x: X坐标
    # :param y: Y坐标
    def __init__(self, x, y):
        self.x = x
        self.y = y


class BattleReportDialog(wx.Frame):
    """战斗实时播报窗口（状态面板 + 彩色日志）"""

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
            parent, title="战斗实时播报", size=(520, 500), pos=(450, 50),
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        )
        self.SetBackgroundColour(self.C_BG)
        self._start_time = None
        self._timer = None
        self.log_lock = threading.Lock()
        self._log_line_count = 0
        self._max_log_lines = 5000
        self._trim_keep_lines = 4000

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        root = wx.BoxSizer(wx.VERTICAL)

        title_bar = wx.Panel(panel)
        title_bar.SetBackgroundColour(self.C_TITLE_BG)
        ts = wx.BoxSizer(wx.HORIZONTAL)
        title_lbl = wx.StaticText(title_bar, label="  战斗实时播报", style=wx.ALIGN_LEFT)
        title_lbl.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        title_lbl.SetForegroundColour(self.C_WHITE)
        ts.Add(title_lbl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        self._status_dot = wx.StaticText(title_bar, label="  \u25cf 就绪  ", style=wx.ALIGN_RIGHT)
        self._status_dot.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
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
        self.log_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.log_text.SetBackgroundColour(self.C_LOG_BG)
        ls.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 2)
        log_panel.SetSizer(ls)
        root.Add(log_panel, 1, wx.EXPAND | wx.TOP, 1)

        btn_bar = wx.Panel(panel)
        btn_bar.SetBackgroundColour(self.C_SURFACE)
        bs = wx.BoxSizer(wx.HORIZONTAL)
        btn_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.export_button = wx.Button(btn_bar, label="导出日志", size=(80, 26))
        self.export_button.SetFont(btn_font)
        self.export_button.SetBackgroundColour(self.C_ACCENT)
        self.export_button.SetForegroundColour(self.C_WHITE)
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export_txt)
        self.clear_button = wx.Button(btn_bar, label="清空日志", size=(80, 26))
        self.clear_button.SetFont(btn_font)
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
        lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        lbl.SetForegroundColour(self.C_MUTED)
        return lbl

    def _create_account_panel(self, parent, idx, name):
        panel = wx.Panel(parent)
        panel.SetBackgroundColour(self.C_SURFACE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        header = wx.StaticText(panel, label=f"账号{idx}({name})")
        header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        header.SetForegroundColour(self.C_ACCENT)
        sizer.Add(header, 0, wx.ALIGN_CENTER | wx.TOP, 4)
        lbl_main = wx.StaticText(panel, label="主角: --")
        lbl_main.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        lbl_main.SetForegroundColour(self.C_TEXT)
        sizer.Add(lbl_main, 0, wx.LEFT, 8)
        lbl_gen = wx.StaticText(panel, label="武将: --")
        lbl_gen.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        lbl_gen.SetForegroundColour(self.C_TEXT)
        sizer.Add(lbl_gen, 0, wx.LEFT, 8)
        lbl_lb = wx.StaticText(panel, label="刘备: --")
        lbl_lb.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
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
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write("战斗播报日志\n")
                        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 60 + "\n\n")
                        f.write(log_content)
                    wx.MessageBox(f"日志已成功导出到:\n{filepath}", "导出成功", wx.OK | wx.ICON_INFORMATION)
                    self.add_log(f"日志已导出到: {filepath}", "system")
                except Exception as e:
                    wx.MessageBox(f"导出日志时出错:\n{str(e)}", "导出失败", wx.OK | wx.ICON_ERROR)
                    self.add_log(f"导出日志失败: {str(e)}", "error")
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


class CombatAutoScript:
    # 初始化战斗自动操作
    # :param thread_instance: MyThread 实例，用于访问大漠对象和区域定义
    # :param enemy_keys_to_detect: 需要检测状态的敌军单位 key 列表，例如 ["诸葛亮", "赵云29"]，如果为None则不检测
    def __init__(self, thread_instance, enemy_keys_to_detect=None):
        self.thread = thread_instance
        self.battle_report_dialog = None  # 战斗播报窗口
        self._dialog_closed = False  # 标记窗口是否已被关闭，防止重新创建

        # 需要检测的敌军单位 key 列表
        self.keep_support_general = False
        self.enemy_keys_to_detect = enemy_keys_to_detect if enemy_keys_to_detect else []

        # 线程安全锁（保护共享状态变量）
        self._state_lock = threading.Lock()

        # 定时器引用（用于清理）
        self._timer_refs = []

        # 回合超时和错误追踪（在__init__中初始化，避免未定义错误）
        self.turn_timeout = CombatConstants.TURN_TIMEOUT
        self.turn_start_time = None  # 回合开始时间
        self.account_error_count = {}  # {account_index: error_count} 追踪每个账号的错误次数（字典类型）
        self.max_errors_per_turn = CombatConstants.MAX_ERRORS_PER_TURN

        # 创建并显示战斗播报窗口（延迟创建，确保wx应用已初始化）
        # 【关键修复】添加重试计数，避免无限重试
        self._battle_dialog_retry_count = 0
        self._max_battle_dialog_retries = CombatConstants.MAX_BATTLE_DIALOG_RETRIES

        try:
            # 使用定时器延迟创建，确保wx应用程序已经运行
            timer = threading.Timer(0.3, self._create_battle_report_dialog)
            self._timer_refs.append(timer)
            timer.start()
        except Exception as e:
            # 静默处理，不打印错误（避免在没有wx环境时打印大量错误）
            pass

        # 初始化战斗区域和配置
        self._init_combat_regions()

        # 初始化新的数据结构
        self.unit_info = {}  # 单位信息字典
        self.dead_units = {}  # 阵亡单位记录（按账号分开存储，但统一管理）
        self.global_dead_units = {
            "main_chars": [],
            "generals": [],
        }  # 全局阵亡单位记录（所有账号共享，保持列表格式以兼容）
        self.global_enemies_need_clear = []
        self._claimed_clear_target = {}
        self.enemy_status_reported = {}  # 已播报的敌军状态标记：{enemy_key: True}，防止重复播报
        self.current_turn = 0  # 当前回合数
        self.skill_cd = {}  # 技能CD追踪：{account_index: {skill_name: last_used_turn}}
        self.pending_liubei_summon = (
            {}
        )  # 待召唤刘备记录：{target_account_index: {'target_char_index': int, 'target_char_info': dict}}
        self.has_liubei_on_field = True  # 场上是否有刘备（全局标志，所有账号共享），在我方回合通过图片检测
        self.liubei_missing_count = 0  # 连续未找到刘备的次数，用于判断场上是否有刘备
        self.low_hp_units = (
            {}
        )  # 血量低的单位记录：{account_index: [{'unit_type': 'main_char'/'general', 'unit_name': str, 'position': (x, y), 'region_index': int}, ...]}
        self.zhugeliang_found = (
            {}
        )  # 诸葛亮单位标记：{account_index: bool}，记录是否已找到状态1和状态2同时存在的诸葛亮单位
        # 跟踪诸葛亮连续未找到状态1的检测次数：{account_index: count}
        self.zhugeliang_status1_missing_count = {}  # 格式：{account_index: count}
        # 跟踪诸葛亮连续未找到状态2的检测次数：{account_index: count}
        self.zhugeliang_status2_missing_count = {}  # 格式：{account_index: count}
        # 跟踪每个单位连续未找到蓝条的操作回合数：{(account_index, region_idx): count}
        self.lantiao_missing_rounds = {}  # 格式：{(account_index, region_idx): count}
        # 我方武将免死被动追踪 + 轮转预替换
        # ally_undead_rounds: key=(account_index, region_idx), value=免死计数
        #   0 = 被动未触发(安全), 1~3 = 被动已触发(越来越危险), >=4 = 被动耗尽(需替换), -1 = 已死亡
        # ally_undead_last_increment_turn: key同上, value=上次递增时的回合数(防止同回合多次递增)
        self.ally_undead_rounds = {}
        self.ally_undead_last_increment_turn = {}
        self.caocao_passive_missing_rounds = {}
        self.undead_threshold = 4  # count>=4时认为被动耗尽, 不再计入安全武将数
        self.proactive_replace_account = 0
        self.need_proactive_replace = False
        self._proactive_replace_in_progress = False
        self._liubei_summon_in_progress = {}
        self._zhugeliang_low_hp = False
        self._last_kicked_info = None
        self.liubei_verify_image = None
        self.xingcai_verify_image = None
        self.SKILL_TO_GENERAL = {
            "剑阵灭杀": "曹操", "曹操单攻": "曹操",
            "武神一怒": "魔化关羽",
            "星彩群攻": "张星彩", "星彩单攻": "张星彩",
        }
        # 不再记录第一回合武将数量，默认每个账号有2个武将

        # 刘备技能释放顺序和冷却记录
        self.liubei_skill_sequence = ["控制", "加攻击", "加血"]  # 刘备技能释放顺序（循环）
        self.liubei_skill_index = {}  # {account_index: current_index} 记录每个账号当前技能索引
        self.liubei_skill_cd = {}  # {account_index: {skill_name: last_used_turn}} 记录每个账号的技能冷却时间
        self._last_clear_attempt = {}  # {account_index: {"enemy_name": str, "turn": int}} 记录清除技能尝试

        # 复活任务分配：{执行账号索引: 目标死亡主角账号索引}
        # 在我方回合开始时统一分配，优先级：其他账号主角 > 随机账号武将
        self.revive_assignments = {}  # 格式：{account_index: target_dead_account_index}

        # 目标点位存储（每回合开始时由大漠对象0识别）
        self.enemy_target_positions = []
        self.ally_target_positions = []
        self.enemy_target_index = 0
        self.ally_target_index = 0
        self.enemy_count = 0
        self.enemy_single_rounds = 0
        self.account_last_target_type = {}
        self.target_positions_detected = False
        # 战斗场景标识（如"四象"），用于区分不同副本的点位偏移等差异
        self.combat_scene = None

        # 轮询监听控制
        self.polling_running = False  # 轮询监听运行标志
        self.polling_thread = None  # 轮询监听线程
        self.account_threads = {}  # 账户处理线程引用：{account_index: thread}

        # 三个账号是否有武将
        self.has_general = {i: True for i in range(3)}
        # 三个账号是否有刘备
        self.liubei_counts = {0: 0, 1: 0, 2: 0}
        self.liubei_remaining = {0: 0, 1: 0, 2: 0}  # 背包剩余可召唤刘备数量（开局上场/召唤成功时扣减，死亡不返还）
        self.has_liubei = {0: True, 1: False, 2: False}
        # 刘备被动回合
        self.beidong_huihe = 0
        # 召唤刘备的账号index
        self.zhaohuan_index = 0
        # 清除诸葛亮标志
        self.clear_zhugeliang = False
        # 开始召唤刘备标志
        self.start_summon_liubei = False
        # 刘备是否常驻（True=死了重召，False=一次性模式，清完状态回6曹操）
        self.enable_persistent_liubei = True

        # 战斗策略引擎（优先级排序的技能释放策略）
        self.skill_strategies = {
            "main_char": [
                {"priority": 80, "skill": "锁魂",       "condition": "always"},
                {"priority": 60, "skill": "寂灭神劫",    "condition": "always"},
                {"priority": 50, "skill": "天灾",        "condition": "always"},
            ],
            "attack": [
                {"priority": 90, "skill": "曹操单攻",    "condition": "enemy_single"},
                {"priority": 86, "skill": "星彩单攻",    "condition": "enemy_single"},
                {"priority": 85, "skill": "星彩群攻",    "condition": "always"},
                {"priority": 80, "skill": "剑阵灭杀",    "condition": "always"},
                {"priority": 70, "skill": "曹操单攻",    "condition": "always"},
                {"priority": 50, "skill": "武神一怒",    "condition": "always"},
                {"priority": -1, "skill": "防御",        "condition": "always"},
            ],
            "support": [
                {"priority": 100, "skill": "清除状态",   "condition": "has_claimed_clear_target"},
                {"priority": 90,  "skill": "加血",       "condition": "ally_hp_low"},
                {"priority": 85,  "skill": "加攻击",     "condition": "attack_buff_expired"},
                {"priority": 80,  "skill": "控制",       "condition": "always"},
                {"priority": 70,  "skill": "加血",       "condition": "ally_hp_critical"},
                {"priority": 10,  "skill": None,         "condition": "always",
                 "sequence": ["控制", "加攻击", "加血"]},
                {"priority": -1,  "skill": "防御",       "condition": "always"},
            ],
            "xingcai_support": [
                {"priority": 100, "skill": "星彩辅助",   "condition": "always"},
                {"priority": 95,  "skill": "星彩单攻",   "condition": "enemy_single"},
                {"priority": 90,  "skill": "星彩群攻",   "condition": "always"},
                {"priority": 70,  "skill": "星彩辅助",   "condition": "always"},
                {"priority": -1,  "skill": "防御",       "condition": "always"},
            ],
        }
        self.attack_buff_tracker = {}  # {account_index: remaining_turns} 加攻击buff剩余回合
        self.low_hp_accounts = {}      # {account_index: count} 血量低单位计数
        self.replace_fail_count = {}   # {account_index: count} 替换失败计数
        self.replace_fail_cooldown = {} # {account_index: cooldown_turn} 替换冷却回合

        # 血量检测区域→账号映射（hp_bar_regions的顺序: 1主角 0主角 2主角 1将1 0将1 2将1 1将2 0将2 2将2）
        self.hp_region_to_account = {0: 1, 1: 0, 2: 2, 3: 1, 4: 0, 5: 2, 6: 1, 7: 0, 8: 2}
    # 创建战斗播报窗口（在主线程中调用）
    def _create_battle_report_dialog(self):
        # 【关键修复】如果窗口已被关闭，不再创建
        if self._dialog_closed:
            return

        # 【关键修复】检查重试次数，避免无限重试
        if self._battle_dialog_retry_count >= self._max_battle_dialog_retries:
            # 超过最大重试次数，停止尝试
            return

        try:
            # 【关键修复】首先检查 wx.App 是否存在
            try:
                app = wx.GetApp()
                if app is None:
                    # wx.App 不存在，增加重试计数并延迟重试
                    self._battle_dialog_retry_count += 1
                    if self._battle_dialog_retry_count < self._max_battle_dialog_retries:
                        timer = threading.Timer(1.0, self._create_battle_report_dialog)
                        self._timer_refs.append(timer)
                        timer.start()
                    return
            except (AttributeError, RuntimeError):
                # wx 未初始化，增加重试计数并延迟重试
                self._battle_dialog_retry_count += 1
                if self._battle_dialog_retry_count < self._max_battle_dialog_retries:
                    timer = threading.Timer(1.0, self._create_battle_report_dialog)
                    self._timer_refs.append(timer)
                    timer.start()
                return

            # wx.App 存在，尝试创建窗口
            if self.battle_report_dialog is None:
                # 确保在主线程中创建
                if threading.current_thread() == threading.main_thread():
                    self.battle_report_dialog = BattleReportDialog(parent=None)
                    self.battle_report_dialog.Show()
                    self.report_battle_info("战斗播报系统已初始化", "system")
                else:
                    # 如果不在主线程，使用wx.CallAfter
                    try:
                        wx.CallAfter(self._create_battle_report_dialog)
                    except Exception:
                        # 如果 CallAfter 失败，增加重试计数并延迟重试
                        self._battle_dialog_retry_count += 1
                        if self._battle_dialog_retry_count < self._max_battle_dialog_retries:
                            timer = threading.Timer(1.0, self._create_battle_report_dialog)
                            self._timer_refs.append(timer)
                            timer.start()
        except Exception as e:
            # 【关键修复】静默处理错误，避免重复打印错误信息
            # 只有在重试次数较少时才打印错误（避免刷屏）
            if self._battle_dialog_retry_count < 3:
                pass  # 前3次重试时静默处理
            # 增加重试计数
            self._battle_dialog_retry_count += 1
            # 如果还有重试机会，延迟重试
            if self._battle_dialog_retry_count < self._max_battle_dialog_retries:
                timer = threading.Timer(1.0, self._create_battle_report_dialog)
                self._timer_refs.append(timer)
                timer.start()

    # 播报战斗信息
    # :param message: 消息内容
    # :param msg_type: 消息类型 ("info", "success", "warning", "error", "system", "turn", "action")
    def report_battle_info(self, message, msg_type="info"):
        # 如果窗口已被关闭，不再尝试创建
        if self._dialog_closed:
            # print(f"[战斗] {message}")
            return

        # 如果窗口还未创建，尝试创建
        if self.battle_report_dialog is None:
            try:
                if hasattr(wx, "GetApp") and wx.GetApp() and not self._dialog_closed:
                    wx.CallAfter(self._create_battle_report_dialog)
            except (AttributeError, RuntimeError) as e:
                # 忽略wx未初始化或已销毁的错误
                pass

        if self.battle_report_dialog:
            try:
                self.battle_report_dialog.add_log(message, msg_type)
            except Exception as e:
                print(f"report_battle_info出错: {e}, 消息: {message[:50]}")
        # else:
            # 如果窗口不存在，至少打印到控制台
            # print(f"[战斗播报-{msg_type}] {message}")

    # 获取资源文件路径
    def get_resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # 初始化战斗区域和配置（从__init__中分离出来，避免代码过长）
    def _init_combat_regions(self):
        # 战斗相关区域定义（已根据游戏截图固定配置，900x580窗口）
        # 战斗区域配置（基于900x580游戏界面）
        # 格式：(x, y, w, h) - 左上角坐标和宽高（w, h是结束坐标）
        self.enemy_region = (38, 151, 375, 541)  # 敌军区域（左侧，覆盖整个左侧区域）
        self.ally_region = (450, 162, 900, 580)  # 己方区域（右侧，覆盖整个右侧区域）
        self.main_char_region = (706, 167, 900, 580)  # 主角区域（最右侧，三个主角位置）
        self.general_region = (491, 164, 772, 522)  # 武将区域（主角前方，武将位置）

        # 右侧按钮区域（操作按钮区域）
        self.right_button_region = self.ally_region  # 右侧按钮区域（中间偏右，包含操作按钮）

        # 面板区域（点击按钮后弹出的面板）
        self.skill_panel_region = self.ally_region  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = self.ally_region  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (0, 0, 900, 580)  # 道具面板区域（点击道具按钮后弹出的面板）

        # 账号区域定义（用于区分不同账号的主角位置，避免重复复活）
        # 账号1在上排，账号0在中间排，账号2在下排
        # 格式：(x, y, w, h) - 左上角坐标和宽高
        self.account_main_char_regions = {
            1: (708, 170, 830, 340),  # 账号1主角区域（上排）
            0: (749, 281, 836, 409),  # 账号0主角区域（中间排）
            2: (775, 395, 862, 542),  # 账号2主角区域（下排）
        }

        # 武将图片路径
        self.general_images = {
            "刘备": self.get_resource_path("serveAssets/images/auto/miankong1.bmp"),
            "魔化关羽": f"{self.get_resource_path('serveAssets/images/auto/gangqi1.bmp')}|{self.get_resource_path('serveAssets/images/auto/shenyou1.bmp')}",
            "曹操": f"{self.get_resource_path('serveAssets/images/auto/bawang1.bmp')}|{self.get_resource_path('serveAssets/images/auto/luanshi1.bmp')}",
            "张星彩": f"{self.get_resource_path('serveAssets/images/auto/zhangxingcai.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhangxingcai1.bmp')}",
        }

        # 技能图片路径（需要根据实际技能图标添加）
        self.skill_images = {
            # 主角技能
            "寂灭神劫": f"{self.get_resource_path('serveAssets/images/auto/jimie1.bmp')}|{self.get_resource_path('serveAssets/images/auto/jimie2.bmp')}",
            "锁魂": f"{self.get_resource_path('serveAssets/images/auto/suohun1.bmp')}|{self.get_resource_path('serveAssets/images/auto/suohun2.bmp')}",
            "天灾": f"{self.get_resource_path('serveAssets/images/auto/tianzai1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tianzai2.bmp')}",
            # 辅助武将技能
            "加血": f"{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan2.bmp')}",
            "加攻击": f"{self.get_resource_path('serveAssets/images/auto/liubeizengshang1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubeizengshang2.bmp')}",
            "控制": f"{self.get_resource_path('serveAssets/images/auto/liubeikong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubeikong2.bmp')}",
            "清除状态": f"{self.get_resource_path('serveAssets/images/auto/liubeijie1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubeijie2.bmp')}",
            # 输出武将技能
            "剑阵灭杀": f"{self.get_resource_path('serveAssets/images/auto/caocaoqun3.bmp')}|{self.get_resource_path('serveAssets/images/auto/caocaoqun2.bmp')}",
            "武神一怒": f"{self.get_resource_path('serveAssets/images/auto/moguqun1.bmp')}|{self.get_resource_path('serveAssets/images/auto/moguqun2.bmp')}",
            "曹操单攻": f"{self.get_resource_path('serveAssets/images/auto/caocaodan1.bmp')}",
            # 张星彩技能
            "星彩群攻": f"{self.get_resource_path('serveAssets/images/auto/xingcaiqun.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaiqun1.bmp')}",
            "星彩单攻": f"{self.get_resource_path('serveAssets/images/auto/xingcaidan.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaidan1.bmp')}",
            "星彩辅助": f"{self.get_resource_path('serveAssets/images/auto/xingcaifuzhu.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaifuzhu1.bmp')}",
        }

        self.gray_skill_images = {
            "寂灭神劫": f"{self.get_resource_path('serveAssets/images/auto/jimie_gray.bmp')}",
            "剑阵灭杀": f"{self.get_resource_path('serveAssets/images/auto/caocaoqun_gray.bmp')}|{self.get_resource_path('serveAssets/images/auto/caocaodan_gray.bmp')}",
            "武神一怒": f"{self.get_resource_path('serveAssets/images/auto/moguanqun_gray.bmp')}|{self.get_resource_path('serveAssets/images/auto/moguandan_gray.bmp')}",
            "星彩群攻": f"{self.get_resource_path('serveAssets/images/auto/xingcaiqun_gray.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaidan_gray.bmp')}",
            "控制":     f"{self.get_resource_path('serveAssets/images/auto/liubeikong_gray.bmp')}|{self.get_resource_path('serveAssets/images/auto/jiasu_gray.bmp')}",
        }

        # 物品图片
        self.item_images = {
            "恢复药": f"{self.get_resource_path('serveAssets/images/auto/yao.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao2.bmp')}",
            # 恢复药（加血又加蓝，2回合CD）
            "复活药": f"{self.get_resource_path('serveAssets/images/auto/fuhuo.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuo1.bmp')}",
            "蓝药":   f"{self.get_resource_path('serveAssets/images/auto/yao.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao2.bmp')}",
            # 复活药（复活阵亡单位）
        }

        # 刘备辅助技能目标图片（用于选择目标）
        # self.liubei_target_image = f"{self.get_resource_path('serveAssets/images/auto/jifangliubei.bmp')}|{self.get_resource_path('serveAssets/images/auto/jifangmoguan.bmp')}|{self.get_resource_path('serveAssets/images/auto/jifangcaocao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhangxingcai3.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubeixuruo.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaixuruo.bmp')}"
        self.liubei_target_image = f"{self.get_resource_path('serveAssets/images/auto/lantiao.bmp')}"
        # 敌军技能目标图片（用于选择目标）
        self.enemy_target_image = f"{self.get_resource_path('serveAssets/images/auto/lantiao.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/zhaoyunlantiao.bmp')}"

        # 技能目标选择图片（蓝色条）
        self.target_lantiao_image = f"{self.get_resource_path('serveAssets/images/auto/lantiao.bmp')}|{self.get_resource_path('serveAssets/images/auto/lantiao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/xuetiao.bmp')}"
        self.target_fuhuobeidong_image = f"{self.get_resource_path('serveAssets/images/auto/fuhuobeidong.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuobeidong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zengjiagongjili1.bmp')}"
        self.target_fuhuohuo_image = self.get_resource_path("serveAssets/images/auto/fuhuohuo.bmp")  # 复活目标图片
        self.liubei_image = f"{self.get_resource_path('serveAssets/images/auto/miankong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/miankong2.bmp')}"  # 刘备图片路径（用于检测场上是否有刘备）
        self.tiandihudun_image = self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp")
        self.caocaobusi_image = f"{self.get_resource_path('serveAssets/images/auto/bumiexiongxin1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugeliangbeidong.bmp')}"
        self.caocao_alive_image = self.get_resource_path("serveAssets/images/auto/caocaobusi.bmp")
        self.moguan_miansi_image = self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp")
        self.moguan_verify_image = self.get_resource_path("serveAssets/images/auto/miansi1.bmp")
        # 刘备技能目标图片,需要重新截图
        self.liubei_verify_image = f"{self.get_resource_path('serveAssets/images/auto/miankong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/miankong2.bmp')}"
        self.xingcai_verify_image = f"{self.get_resource_path('serveAssets/images/auto/xingcaibeidong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaibeidong2.bmp')}|{self.get_resource_path('serveAssets/images/auto/xingcaibeidong3.bmp')}"
        self.zhugexuetiao_image = f"{self.get_resource_path('serveAssets/images/auto/zhugexuetiao.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugexuetiao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugexuetiao2.bmp')}"
        # 技能CD配置（回合数）
        self.skill_cd_config = {
            # 刘备技能
            "加血": 2,  # 2回合CD
            "清除状态": 5,  # 5回合CD
            "加攻击": 0,  # 无CD
            "控制": 0,  # 无CD
            # 主角技能
            "寂灭神劫": 3,  # 3回合CD
            "锁魂": 2,  # 2回合CD
            "天灾": 2,  # 2回合CD
            # 武将技能
            "剑阵灭杀": 0,  # 无CD
            "武神一怒": 0,  # 无CD
            "曹操单攻": 0,  # 无CD
            "星彩群攻": 0,  # 无CD
            "星彩单攻": 0,  # 无CD
            "星彩辅助": 0,  # 无CD
        }

        # 药品CD配置
        self.item_cd_config = {
            "恢复药": 3,  # 3回合CD（红药，加血又加蓝）
            "复活药": 0,  # 无CD（复活药通常无CD限制）
            "蓝药":   3,  # 3回合CD（蓝药，回蓝）
        }

        # 技能CD追踪 {account_index: {skill_name: last_used_turn}}
        self.skill_cd_tracking = {}

        # 药品CD追踪 {account_index: {item_name: last_used_turn}}
        self.item_cd_tracking = {}

        self._no_heal_item_missing_turn = {}
        self._no_mana_item_missing_turn = {}
        self._current_our_turn_call = 0

        # 武将追踪信息（存储每个账号的武将信息）
        self.general_tracking = (
            {}
        )  # {account_index: {general_name: {'type': 'support/dps', 'deployed_turn': turn_number, 'position': (x, y)}}}
        # 注意：current_turn 已在 __init__ 中初始化，这里不再重复初始化

        # 墓碑图片路径（用于检测单位死亡状态）
        # 单位死亡后会在原地显示墓碑，通过检测墓碑来判断死亡
        self.tombstone_image = f"{self.get_resource_path('serveAssets/images/auto/duiyou2mubei1.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei4.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei1.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei3.bmp')}"  # 墓碑图片

        # 墓碑检测区域大小（以单位位置为中心的区域）
        # 用于在单位位置附近检测墓碑，避免位置偏移导致的检测失败
        self.tombstone_detection_radius = CombatConstants.TOMBSTONE_DETECTION_RADIUS

        # 敌人固定位置（已根据游戏截图固定配置）
        # 格式：{(account_index, enemy_index): (x, y)} - 敌人的中心点坐标
        # 根据截图，左侧3个敌人中心点大约在：(97, 246), (104, 344), (115, 446)
        self.fixed_enemy_positions = {
            # 账号0的敌人位置
            (0, 0): (97, 246),  # 敌人1中心点（上，最左侧）
            (0, 1): (104, 344),  # 敌人2中心点（中，最左侧）
            (0, 2): (115, 446),  # 敌人3中心点（下，最左侧）
            # 账号1的敌人位置（如果多开窗口布局一致）
            (1, 0): (97, 246),
            (1, 1): (104, 344),
            (1, 2): (115, 446),
            # 账号2的敌人位置（如果多开窗口布局一致）
            (2, 0): (97, 246),
            (2, 1): (104, 344),
            (2, 2): (115, 446),
        }

        # 背包武将图片（用于检测背包中是否有可用武将）
        self.bag_general_images = {
            "刘备": f"{self.get_resource_path('serveAssets/images/auto/liubei1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubei2.bmp')}",
            "魔化关羽": f"{self.get_resource_path('serveAssets/images/auto/mogu2.bmp')}|{self.get_resource_path('serveAssets/images/auto/mogu1.bmp')}",
            "曹操": f"{self.get_resource_path('serveAssets/images/auto/caocao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/caocao2.bmp')}",
            "张星彩": f"{self.get_resource_path('serveAssets/images/auto/zhangxingcai.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhangxingcai1.bmp')}",
        }

        # 血量条图片（用于检测血量低的单位）
        # 识别到这张图片说明单位血量低，需要加血
        self.low_hp_indicator_image = f"{self.get_resource_path('serveAssets/images/auto/xueliangbuzu1.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei2.bmp')}|{self.get_resource_path('serveAssets/images/auto/xueliangbuzu2.bmp')}"  # 血量低的标识图片

        # 9个血量条检测区域（3个账号，每个账号1个主角+2个武将）
        # 顺序：账号1主角、账号0主角、账号2主角、账号1武将1(后排)、账号0武将1(后排)、账号2武将1(后排)、账号1武将2(前排)、账号0武将2(前排)、账号2武将2(前排)
        # 格式：[(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
        # 基于900x580游戏界面，血量条通常显示在角色头顶上方
        # 账号1在上排，账号0在中间排，账号2在下排
        self.hp_bar_regions = [
            (721, 159, 801, 219),  # 账号1主角血量条（上排）
            (750, 251, 829, 315),  # 账号0主角血量条（中间排）
            (784, 359, 859, 420),  # 账号2主角血量条（下排）
            (631, 151, 710, 219),  # 账号1武将1血量条（后排）
            (656, 251, 737, 316),  # 账号0武将1血量条（后排）
            (680, 361, 762, 418),  # 账号2武将1血量条（后排）
            (544, 159, 621, 220),  # 账号1武将2血量条（前排）
            (559, 252, 639, 319),  # 账号0武将2血量条（前排）
            (581, 363, 664, 419),  # 账号2武将2血量条（前排）
        ]  # 9个血量条区域列表

        # 血量条区域到单位的映射关系
        # {account_index: {region_index: (unit_type, unit_name, heal_position)}}
        # unit_type: 'main_char' 或 'general'
        # region_index: 0-8 (对应9个区域：0-2主角，3-8武将)
        # heal_position: (x, y) 加血点位
        self.hp_bar_unit_mapping = {}  # 血量条区域到单位的映射

        # 右侧按钮区域定义（根据实际游戏，操作按钮在右侧）
        # 按钮包括：攻击(A)、技能(S)、道具(E)、防御(D)、重复(R)、召唤(C)、自动(W)、逃跑(P)
        self.right_button_region = (610, 203, 680, 436)  # 右侧按钮区域（中间偏右，包含操作按钮）
        self.skill_panel_region = (472, 155, 607, 550)  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = (480, 167, 607, 550)  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (472, 155, 607, 550)  # 道具面板区域（点击道具按钮后弹出的面板）

        # 主角、武将、敌人的确切点位存储（单位外观中心位置，用于点击）
        # {account_index: {'main_char': (x, y), 'generals': [(general_name, x, y), ...], 'enemies': [(enemy_name, x, y), ...]}}
        # 坐标基于之前配置的站位区域中心点计算
        # 格式：单位名称和中心坐标 (x, y)
        # 账号1在上排，账号0在中间排，账号2在下排
        self.unit_positions = {
            # 账号0（中间排）
            0: {
                "main_char": (795, 389),  # 账号0主角中心点（中间排）
                "generals": [
                    ("武将1", 691, 381),  # 账号0武将1中心点（后排）
                    ("武将2", 611, 390),  # 账号0武将2中心点（前排）
                ],
                "enemies": [
                    # 敌人中心点需要通过set_fixed_enemy_positions设置
                    # 一般敌人的中心点位置在左侧，x约150-350, y约300-450
                ],
            },
            # 账号1（上排）
            1: {
                "main_char": (764, 288),  # 账号1主角中心点（上排）
                "generals": [
                    ("武将1", 674, 282),  # 账号1武将1中心点（后排）
                    ("武将2", 580, 278),  # 账号1武将2中心点（前排）
                ],
                "enemies": [],
            },
            # 账号2（下排）
            2: {
                "main_char": (824, 494),  # 账号2主角中心点（下排）
                "generals": [
                    ("武将1", 719, 487),  # 账号2武将1中心点（后排）
                    ("武将2", 624, 496),  # 账号2武将2中心点（前排）
                ],
                "enemies": [],
            },
        }

        # 敌人的固定点位配置（三个敌人外观中心位置，用于点击）
        # {(account_index, enemy_index): (x, y)} 或 {(account_index, enemy_name): (x, y)}
        # 基于900x580游戏界面，敌人位于左侧，三个敌人垂直排列
        # 坐标基于最左侧三个敌人外观中心（根据图片描述，最左侧敌人x约150）
        self.fixed_enemy_positions = {
            # 账号0的三个敌人固定点位（最左侧三个敌人外观中心）
            (0, 0): (97, 246),  # 敌人1中心点（上，最左侧）
            (0, 1): (104, 344),  # 敌人2中心点（中，最左侧）
            (0, 2): (115, 446),  # 敌人3中心点（下，最左侧）
            (0, 3): (202, 337),  # 敌人4中心点（中，最中间一排）
            # 账号1的三个敌人固定点位
            (1, 0): (97, 246),
            (1, 1): (104, 344),
            (1, 2): (115, 446),
            (1, 3): (202, 337),  # 敌人4中心点（中，最中间一排）
            # 账号2的三个敌人固定点位
            (2, 0): (97, 246),
            (2, 1): (104, 344),
            (2, 2): (115, 446),
            (2, 3): (202, 337),  # 敌人4中心点（中，最中间一排）
        }

        # 敌军武将配置（每个武将的检测状态图片、检测状态区域、施法点位）
        # 格式：{武将名称: {'status_images': {...}, 'status_region': (x, y, w, h), 'cast_position': (x, y)}}
        self.enemy_general_config = {
            "刘备": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp")
                },
                "status_region": (165, 258, 246, 291),
                "cast_position": (203, 346),
                "status_duration": 4,
            },
            "诸葛亮": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/bumiexiongxin.bmp')}|{self.get_resource_path('serveAssets/images/auto/bumiexiongxin1.bmp')}",
                    "状态2": f"{self.get_resource_path('serveAssets/images/auto/duci.bmp')}|{self.get_resource_path('serveAssets/images/auto/gangqi1.bmp')}",
                },
                "status_region": (61, 236, 146, 315),
                "cast_position": (104, 344),
                "status_duration": 4,
            },
            "赵云29": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
                },
                "status_region": (54, 360, 174, 541),
                "cast_position": (115, 446),
                "status_duration": 4,
            },
            "龙": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (61, 257, 145, 312),
                "cast_position": (112, 372),
                "status_duration": 4,
            },
            "羊人参娃": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (174, 382, 224, 426),
                "cast_position": (222, 472),
                "status_duration": 4,
            },
            "龙上龙": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (48, 169, 141, 216),
                "cast_position": (97, 246),
                "status_duration": 4,
            },
            "猴子": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (61, 257, 145, 312),
                "cast_position": (112, 372),
                "status_duration": 4,
            },
            "猴子狮": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (146, 177, 227, 225),
                "cast_position": (150, 300),
                "status_duration": 4,
            },
            "赵云28": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
                },
                "status_region": (156, 235, 242, 319),
                "cast_position": (202, 337),
                "status_duration": 4,
            },
            "蛇": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/shejineng.bmp')}|{self.get_resource_path('serveAssets/images/auto/shejineng1.bmp')}",
                },
                "status_region": (60, 155, 147, 224),
                "cast_position": (123, 350),
                "status_duration": 1,
            },
            "玄武": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/shengsijing.bmp')}|{self.get_resource_path('serveAssets/images/auto/shengsijing1.bmp')}",
                },
                "status_region": (55, 232, 137, 314),
                "cast_position": (98, 360),
                "status_duration": 3,
            },
        }

        # 按钮图片路径
        self.button_images = {
            "技能按钮": f"{self.get_resource_path('serveAssets/images/auto/jineng.bmp')}|{self.get_resource_path('serveAssets/images/auto/jineng1.bmp')}",
            "召唤按钮": f"{self.get_resource_path('serveAssets/images/auto/zhaohuan.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhaohuan1.bmp')}",
            "道具按钮": f"{self.get_resource_path('serveAssets/images/auto/yaopin.bmp')}|{self.get_resource_path('serveAssets/images/auto/yaopin1.bmp')}",
            "防御按钮": f"{self.get_resource_path('serveAssets/images/auto/fangyu.bmp')}",  # 防御按钮
            "操作按钮": f"{self.get_resource_path('serveAssets/images/auto/jineng.bmp')}|{self.get_resource_path('serveAssets/images/auto/jineng1.bmp')}",  # 操作按钮(检测是否在战斗页面)
            "重复按钮": f"{self.get_resource_path('serveAssets/images/auto/chongfu1.bmp')}|{self.get_resource_path('serveAssets/images/auto/chongfu2.bmp')}",  # 重复按钮(重复上回合操作)
            "取消按钮": self.get_resource_path("serveAssets/images/quxiaozdzd.bmp"),  # 取消按钮
        }

        # zdzd图片路径（需要检测并点击取消的弹窗）
        self.zdzd_image = self.get_resource_path("serveAssets/images/zdzd111.bmp")

        # zdzd检测区域（全屏检测）
        self.zdzd_region = (0, 0, 900, 580)  # 全屏区域

    # ==================== 重写后的核心战斗逻辑 ====================

    # 获取账号数量
    def get_account_count(self):
        """获取账号数量（根据实际可用的大漠对象）"""
        count = 0
        if self.thread.dm:
            count += 1
        if getattr(self.thread, "win1_dm", None):
            count += 1
        if getattr(self.thread, "win2_dm", None):
            count += 1
        return max(count, 1)  # 至少返回1（主账号）

    def is_account_active(self, account_index):
        """判断指定账号是否参战（对应的大漠对象是否存在）"""
        if account_index == 0:
            return bool(self.thread.dm)
        elif account_index == 1:
            return bool(getattr(self.thread, "win1_dm", None))
        elif account_index == 2:
            return bool(getattr(self.thread, "win2_dm", None))
        return False

    # 获取指定账号的dm对象
    def get_account_dm(self, account_index):
        """获取指定账号的dm对象
        account_index: 0=dm, 1=win1_dm, 2=win2_dm
        """
        if account_index == 0:
            return self.thread.dm
        elif account_index == 1:
            return getattr(self.thread, "win1_dm", None)
        elif account_index == 2:
            return getattr(self.thread, "win2_dm", None)
        return self.thread.dm  # 默认返回主账号

    # 查找图片(封装thread的方法，支持多账号)
    def find_image(self, account_index, image_path, region, find_dir=0, use_lower_confidence=False):
        """查找图片，支持多账号，支持识别率递减
        :param account_index: 账号索引
        :param image_path: 图片路径（支持多个路径用|分隔）
        :param region: 搜索区域 (x, y, w, h)
        :param find_dir: 查找方向
        :param use_lower_confidence: 是否使用更低的识别率（用于难以识别的图片，如道具）
        :return: ResXy对象或None
        """
        dm = self.get_account_dm(account_index)
        if not dm:
            return None

        # 直接使用dm对象，避免修改共享状态（线程安全）
        # 大漠插件本身是线程安全的，可以直接在子线程中使用
        try:
            x, y, w, h = region
            # 验证坐标有效性（w和h是结束坐标）
            if w <= x or h <= y:
                return None

            # 识别率递减：如果use_lower_confidence为True，使用更低的识别率
            if use_lower_confidence:
                confidence_levels = [0.9, 0.8, 0.7]
            else:
                confidence_levels = [0.9, 0.8, 0.7]

            for confidence in confidence_levels:
                pos = dm.FindPicEx(int(x), int(y), int(w), int(h), image_path, "", confidence, find_dir)
                if pos:
                    # 找到图片，解析坐标
                    pos = pos.split("|")
                    pos_res = pos[0].split(",")
                    pics = image_path.split("|")
                    picSize = dm.GetPicSize(pics[int(pos_res[0])])
                    picSize = picSize.split(",")
                    picW, picH = picSize[0], picSize[1]
                    posX = int(pos_res[1]) + (int(picW) * 0.5)
                    posY = int(pos_res[2]) + (int(picH) * 0.5)
                    return ResXy(int(posX), int(posY))
                time.sleep(0.02)
            # 所有识别率都未找到，返回None
            return None
        except Exception:
            return None

    def _find_all_lantiao(self, account_index, region, image_path=None):
        dm = self.get_account_dm(account_index)
        if not dm:
            return []
        x, y, w, h = region
        if w <= x or h <= y:
            return []
        target_image = image_path if image_path is not None else self.enemy_target_image
        pics = target_image.split("|")
        for confidence in [0.9, 0.8, 0.7]:
            try:
                result = dm.FindPicEx(int(x), int(y), int(w), int(h), target_image, "", confidence, 0)
            except Exception:
                time.sleep(0.02)
                continue
            if result:
                positions = []
                for item in result.split("|"):
                    parts = item.split(",")
                    if len(parts) >= 3:
                        try:
                            pic_idx = int(parts[0])
                            pic_size = dm.GetPicSize(pics[pic_idx]).split(",")
                            pw, ph = int(pic_size[0]), int(pic_size[1])
                            cx = int(parts[1]) + int(pw * 0.5)
                            cy = int(parts[2]) + int(ph * 0.5)
                            positions.append((cx, cy))
                        except Exception:
                            continue
                if positions:
                    # 去重：同一敌军的蓝条匹配多张图片时距离很近，用欧氏距离区分
                    deduped = []
                    for pos in sorted(positions):
                        if not deduped or ((pos[0] - deduped[-1][0]) ** 2 + (pos[1] - deduped[-1][1]) ** 2) ** 0.5 > 5:
                            deduped.append(pos)
                    return deduped
            time.sleep(0.02)
        return []

    def find_target_text(self, account_index, search_region, timeout=3.0):
        """查找复活目标图片（fuhuohuo）
        :param account_index: 账号索引
        :param search_region: 搜索区域，可以是单个区域或区域列表
        :param timeout: 超时时间（秒）
        :return: ResXy对象或None
        """
        target_pos = None
        start_time = time.time()
        confidence_levels = [0.9, 0.8, 0.7, 0.6, 0.5]  # 识别率递减

        # 如果search_region是单个区域，转换为列表
        if isinstance(search_region, tuple) and len(search_region) == 4:
            search_regions = [search_region]
        else:
            search_regions = search_region if isinstance(search_region, list) else [search_region]

        while time.time() - start_time < timeout:
            # 尝试多个区域
            for search_reg in search_regions:
                if time.time() - start_time >= timeout:
                    break
                # 尝试多个识别率
                for confidence in confidence_levels:
                    if time.time() - start_time >= timeout:
                        break

                    target_pos = self.find_image(account_index, self.target_fuhuohuo_image, search_reg, 0)
                    if target_pos:
                        break
                    time.sleep(0.05)  # 短暂延迟后重试
                if target_pos:
                    break
            if target_pos:
                break
            time.sleep(0.1)  # 每次循环后稍作延迟

        return target_pos

    # 点击坐标
    def click_position(self, account_index, x, y):
        """点击指定坐标"""
        dm = self.get_account_dm(account_index)
        dm.MoveTo(int(x), int(y))
        time.sleep(CombatConstants.CLICK_DELAY)
        dm.LeftClick()
        # time.sleep(CombatConstants.ACTION_DELAY)

    def click_with_verification(
        self, account_index, image_path, pos, region, item_name="物品", max_retries=2, verify_delay=0.8
    ):
        """通用点击验证方法：点击后检查图片是否消失，如果未消失则重试
        :param account_index: 账号索引
        :param image_path: 图片路径
        :param pos: 位置（ResXy对象）
        :param region: 搜索区域
        :param item_name: 物品名称（用于日志）
        :param max_retries: 最大重试次数（默认2次，即首次点击+1次重试）
        :param verify_delay: 验证延迟时间（秒）
        :return: True表示点击成功，False表示点击失败
        """
        if not pos:
            return False

        for attempt in range(max_retries):
            # 点击
            self.click_position(account_index, pos.x, pos.y)
            time.sleep(verify_delay)

            # 验证图片是否消失
            verify_pos = self.find_image(account_index, image_path, region, 0)
            if verify_pos is None:
                # 图片已消失，点击成功
                if attempt > 0:
                    self.report_battle_info(f"账号{account_index} {item_name}点击成功（第{attempt + 1}次尝试）", "info")
                return True
            else:
                # 图片还在，需要重试
                if attempt < max_retries - 1:
                    self.report_battle_info(
                        f"账号{account_index} {item_name}点击后未消失，进行第{attempt + 2}次点击", "warning"
                    )
                    pos = verify_pos  # 更新位置（可能位置有变化）
                    time.sleep(0.2)  # 短暂延迟后重试
                else:
                    # 最后一次尝试也失败
                    self.report_battle_info(
                        f"账号{account_index} {item_name}点击失败（已重试{max_retries - 1}次，图片仍未消失）", "error"
                    )

        return False

    def _try_release_skill(self, account_index, skill_name, caller_hint=""):
        if skill_name == "防御":
            defense_btn = self.find_image(
                account_index, self.button_images.get("防御按钮"), self.right_button_region, 0
            )
            if defense_btn:
                self.click_position(account_index, defense_btn.x, defense_btn.y)
                self.report_battle_info(f"账号{account_index} {caller_hint}执行防御", "action")
                time.sleep(CombatConstants.ACTION_DELAY)
                return True
            return False
        skill_path = self.skill_images.get(skill_name)
        if not skill_path:
            return False
        _find_start = time.time()
        skill_pos = self.find_image(account_index, skill_path, self.skill_panel_region, 0)
        _find_cost = round(time.time() - _find_start, 3)
        if not skill_pos:
            return False
        return self.release_skill_with_target(account_index, skill_name, skill_pos, caller_hint)

    def _evaluate_condition(self, account_index, cond):
        if cond == "always":
            return True
        elif cond == "has_claimed_clear_target":
            return self._claimed_clear_target.get(account_index) is not None
        elif cond == "ally_hp_critical":
            return self.low_hp_accounts.get(account_index, 0) >= 1
        elif cond == "ally_hp_low":
            return sum(self.low_hp_accounts.values()) >= 2
        elif cond == "attack_buff_expired":
            return self.attack_buff_tracker.get(account_index, 0) <= 0
        elif cond == "enemy_single":
            return self.enemy_single_rounds >= 2
        elif cond == "first_turn":
            return self.current_turn <= 1
        return True

    def _execute_best_strategy(self, account_index, unit_type):
        if unit_type not in self.skill_strategies:
            return False
        strategies = sorted(self.skill_strategies[unit_type], key=lambda s: s["priority"], reverse=True)
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

    def release_skill_with_target(self, account_index, skill_name, skill_pos, skill_type="main_char"):
        """释放技能并选择目标
        :param account_index: 账号索引
        :param skill_name: 技能名称
        :param skill_pos: 技能位置（ResXy对象）
        :param skill_type: 技能类型（"main_char"主角技能, "attack"攻击武将技能, "support"辅助武将技能）
        :return: True表示释放成功，False表示释放失败
        """
        try:
            skill_image_path = self.skill_images.get(skill_name)
            if not skill_image_path:
                return False

            # 点击技能并验证
            if not self.click_with_verification(
                account_index, skill_image_path, skill_pos, self.skill_panel_region, skill_name, max_retries=2
            ):
                return False

            # 等待技能选择界面出现（避免点击目标时界面未准备好）
            time.sleep(0.05)

            # 根据技能类型选择目标
            if skill_type == "main_char" or skill_type == "attack":
                positions = self.enemy_target_positions
                target_pos = positions[self.enemy_target_index] if self.enemy_target_index < len(positions) else (104, 344)
                self.account_last_target_type[account_index] = "enemy"
                self.click_position(account_index, target_pos[0], target_pos[1])
                char_type = "主角" if skill_type == "main_char" else "武将"
                self.report_battle_info(
                    f"账号{account_index} {char_type}释放{skill_name}，目标位置: {target_pos}", "action"
                )
            elif skill_type == "support" or skill_type == "xingcai_support":
                if skill_name in ["加攻击", "加血", "星彩辅助"]:
                    positions = self.ally_target_positions
                    target_pos = positions[self.ally_target_index] if self.ally_target_index < len(positions) else (764, 380)
                    self.account_last_target_type[account_index] = "ally"
                    self.click_position(account_index, target_pos[0], target_pos[1])
                    self.report_battle_info(
                        f"账号{account_index} 释放{skill_name}，目标位置: {target_pos}", "action"
                    )
                elif skill_name in ["星彩群攻", "星彩单攻"]:
                    positions = self.enemy_target_positions
                    target_pos = positions[self.enemy_target_index] if self.enemy_target_index < len(positions) else (104, 344)
                    self.account_last_target_type[account_index] = "enemy"
                    self.click_position(account_index, target_pos[0], target_pos[1])
                    self.report_battle_info(
                        f"账号{account_index} 张星彩释放{skill_name}，目标位置: {target_pos}", "action"
                    )
                elif skill_name == "控制":
                    positions = self.enemy_target_positions
                    target_pos = positions[self.enemy_target_index] if self.enemy_target_index < len(positions) else (104, 344)
                    self.account_last_target_type[account_index] = "enemy"
                    self.click_position(account_index, target_pos[0], target_pos[1])
                    self.report_battle_info(
                        f"账号{account_index} 刘备释放{skill_name}，目标位置: {target_pos}", "action"
                    )
                elif skill_name == "清除状态":
                    self.account_last_target_type[account_index] = "enemy"
                    target = self._claimed_clear_target.get(account_index)
                    if target is not None:
                        target_pos = target.get("position") or (104, 344)
                        self.click_position(account_index, target_pos[0], target_pos[1])
                        enemy_name = target.get("enemy_name", "敌军")
                        self._last_clear_attempt[account_index] = {
                            "enemy_name": enemy_name,
                            "turn": self.current_turn
                        }
                        with self._state_lock:
                            self.global_enemies_need_clear = [
                                e for e in self.global_enemies_need_clear if e is not target
                            ]
                            self._claimed_clear_target[account_index] = None
                        if enemy_name in self.enemy_status_reported:
                            del self.enemy_status_reported[enemy_name]
                        # 诸葛亮一旦检测到需要清除，永久跳过后续检测（直到新一轮战斗reset_state）
                        # 不再在此处重置 clear_zhugeliang = False
                        self.report_battle_info(
                            f"账号{account_index} 刘备释放{skill_name}清除{enemy_name}状态，目标位置: {target_pos}",
                            "action",
                        )
                        if not self.enable_persistent_liubei:
                            if not self.global_enemies_need_clear:
                                self.keep_support_general = False
                                self._zhugeliang_low_hp = False
                                self.report_battle_info(
                                    "所有敌军状态清除完毕，恢复6曹操模式", "system"
                                )
                    else:
                        positions = self.enemy_target_positions
                        target_pos = positions[self.enemy_target_index] if self.enemy_target_index < len(positions) else (104, 344)
                        self.click_position(account_index, target_pos[0], target_pos[1])
                        self.report_battle_info(
                            f"账号{account_index} 刘备释放{skill_name}，目标位置: {target_pos}", "action"
                        )

            if skill_name == "加攻击" and skill_type == "support":
                self.attack_buff_tracker[account_index] = 3

            if skill_name == "清除状态" and skill_type == "support":
                if account_index not in self.liubei_skill_cd:
                    self.liubei_skill_cd[account_index] = {}
                self.liubei_skill_cd[account_index]["清除状态"] = self.current_turn
                self.report_battle_info(
                    f"账号{account_index} 刘备清除状态技能已使用，CD{self.skill_cd_config.get('清除状态', 5)}回合（当前回合: {self.current_turn}）",
                    "system",
                )

            time.sleep(CombatConstants.ACTION_DELAY)
            return True
        except Exception as e:
            self.report_battle_info(f"账号{account_index} 释放技能{skill_name}时发生异常: {e}", "error")
            return False

    # 召唤武将
    def summon_general_with_verification(self, account_index, general_name, force_replace=False, replace_position=None):
        """召唤武将并验证是否成功
        :param account_index: 账号索引
        :param general_name: 武将名称
        :param force_replace: 是否强制替换
        :param replace_position: 指定替换位置的武将(position元组), 优先踢该位置的武将
        :return: True表示召唤成功，False表示召唤失败
        """
        # 1. 点击召唤按钮
        summon_btn = self.find_image(account_index, self.button_images["召唤按钮"], self.right_button_region, 0)
        if not summon_btn:
            self.report_battle_info(f"账号{account_index} 未找到召唤按钮", "warning")
            return False

        self.click_position(account_index, summon_btn.x, summon_btn.y)
        time.sleep(0.1)

        # 2. 查找武将图片
        general_path = self.bag_general_images.get(general_name)
        if not general_path:
            self.report_battle_info(f"账号{account_index} 武将'{general_name}'图片路径未配置", "error")
            return False

        general_pos = None
        start_time = time.time()
        while time.time() - start_time < 1.0:
            general_pos = self.find_image(account_index, general_path, self.summon_panel_region, 0)
            if general_pos:
                break
            time.sleep(0.1)

        if not general_pos:
            self.report_battle_info(f"账号{account_index} 查找武将{general_name}图片超时", "warning")
            return False

        # 3. 点击武将并验证（背包武将消失即表示召唤成功）
        if not self.click_with_verification(
            account_index, general_path, general_pos, self.summon_panel_region, f"武将{general_name}", max_retries=2
        ):
            return False
        time.sleep(0.1)
        # 4. 更新武将信息（背包武将已消失，但施法可能被取消，需延迟确认）
        char_info = self.unit_info[account_index]["main_char"]

        alive_generals = [g for g in char_info.get("generals", [])
                          if g.get("alive", True)
                          and not g.get("replacing", False)
                          and not g.get("pending_kick", False)]
        general_count = len(alive_generals)

        # 被动替换：场上武将已满2个时, 踢掉一个旧武将腾出位置给新武将
        # 张星彩保护: replace_position指向张星彩时跳过, REPLACE_PRIORITY不含张星彩, 全张星彩时拒绝替换
        is_replacement = force_replace
        if is_replacement:
            if general_count < 2:
                is_replacement = False
        kicked = None
        if is_replacement:
            # 替换优先级: 刘备 > 魔化关羽 > 曹操 (张星彩永远不在替换列表中)
            REPLACE_PRIORITY = ["魔化关羽", "刘备", "曹操"]
            if replace_position is not None:
                for g in alive_generals:
                    if (abs(g["position"][0] - replace_position[0]) < 50
                            and abs(g["position"][1] - replace_position[1]) < 50):
                        if g.get("name") == "张星彩":
                            self.report_battle_info(
                                f"账号{account_index} 被动替换：replace_position指向张星彩，跳过该位置",
                                "warning",
                            )
                            break
                        kicked = g
                        break
            if kicked is None:
                for priority_name in REPLACE_PRIORITY:
                    for g in alive_generals:
                        if g.get("name") == priority_name:
                            kicked = g
                            break
                    if kicked:
                        break
            if kicked:
                summon_target_pos = kicked["position"]
                self.report_battle_info(
                    f"账号{account_index} 被动替换：踢掉{kicked['name']}(槽位{summon_target_pos})，腾出位置给{general_name} [replace_position={replace_position}]",
                    "action",
                )
            else:
                all_xingcai = all(g.get("name") == "张星彩" for g in alive_generals)
                if all_xingcai:
                    self.report_battle_info(
                        f"账号{account_index} 被动替换：所有存活武将均为张星彩，拒绝替换，取消召唤{general_name}",
                        "warning",
                    )
                    return False
                summon_target_pos = self.unit_positions[account_index]["generals"][0][1:]
                self.report_battle_info(
                    f"账号{account_index} 被动替换：无可替换武将，使用兜底槽位{summon_target_pos}",
                    "warning",
                )
            self.click_position(account_index, summon_target_pos[0], summon_target_pos[1])
        else:
            self.click_position(account_index, 12, 12)
            # 确定召唤位置: 检查已有武将position判断空位, 避免position重叠
            _existing_positions = [g.get("position") for g in alive_generals if g.get("position")]
            _slot1 = self.unit_positions[account_index]["generals"][0][1:]
            _slot2 = self.unit_positions[account_index]["generals"][1][1:]
            _slot1_occupied = any(abs(p[0]-_slot1[0]) < 50 and abs(p[1]-_slot1[1]) < 50 for p in _existing_positions)
            _slot2_occupied = any(abs(p[0]-_slot2[0]) < 50 and abs(p[1]-_slot2[1]) < 50 for p in _existing_positions)
            if _slot1_occupied and not _slot2_occupied:
                summon_target_pos = _slot2
            else:
                summon_target_pos = _slot1

        # 新武将标记为replacing(替换中), 等待非我方回合轮询验证后才确认上场
        # replacing与reviving的区别: replacing需要验证图片确认, reviving由蓝条检测确认
        new_general = {
            "name": general_name,
            "position": summon_target_pos,
            "alive": False,
            "replacing": True,
            "reviving": False,
            "deployed_turn": self.current_turn,
            "account_index": account_index,
        }
        char_info["generals"].append(new_general)

        # 旧武将标记为pending_kick(待踢出), 保留在列表中, 确认成功后再移除
        # 如果施法被取消(武将回到背包), 需要恢复旧武将
        if kicked is not None:
            kicked["pending_kick"] = True
            self._last_kicked_info = {
                "account_index": account_index,
                "general": dict(kicked),
            }
        else:
            self._last_kicked_info = None
        # 清理幽灵条目：alive=False且非reviving且非replacing的条目已不在场上
        char_info["generals"][:] = [g for g in char_info["generals"]
            if g.get("alive", True) or g.get("reviving", False) or g.get("replacing", False)]

        # 注意: 以下操作延迟到_track_ally_undead确认替换成功后再执行:
        # - global_dead_units清理
        # - liubei_skill_cd重置
        # - ally_undead_rounds更新
        # - has_liubei/has_general更新
        # 如果替换超时失败, 武将回到背包, 这些都不需要更新

        alive_count = sum(1 for g in char_info.get("generals", [])
                          if g.get("alive", True) and not g.get("pending_kick", False))
        self.report_battle_info(
            f"账号{account_index} 召唤{general_name}操作完成（状态：替换中，当前存活武将数: {alive_count}）",
            "action",
        )
        return True

    def use_item_with_verification(self, account_index, item_name, target_position=None):
        """使用药品并验证是否成功
        :param account_index: 账号索引
        :param item_name: 药品名称（"恢复药"或"复活药"）
        :param target_position: 目标位置（元组(x, y)），如果为None则使用默认位置
        :return: True表示使用成功，False表示使用失败
        """
        # 1. 点击道具按钮
        item_btn = None
        start_time = time.time()
        while time.time() - start_time < 1.5:
            item_btn = self.find_image(account_index, self.button_images["道具按钮"], self.right_button_region, 0)
            if item_btn:
                break
            time.sleep(0.1)

        if not item_btn:
            self.report_battle_info(f"账号{account_index} 查找道具按钮超时（1.5秒）", "warning")
            return False

        self.click_position(account_index, item_btn.x, item_btn.y)

        # 2. 查找药品图片
        item_path = self.item_images.get(item_name)
        if not item_path:
            self.report_battle_info(f"账号{account_index} 药品'{item_name}'图片路径未配置", "error")
            return False

        item_pos = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            item_pos = self.find_image(account_index, item_path, self.item_panel_region, 0)
            if item_pos:
                break
            time.sleep(0.1)

        if not item_pos:
            self.report_battle_info(f"账号{account_index} 查找{item_name}图片超时（3秒）", "warning")
            return False

        # 3. 点击药品并验证
        if not self.click_with_verification(
            account_index, item_path, item_pos, self.item_panel_region, item_name, max_retries=2
        ):
            return False

        # 4. 点击目标位置
        if target_position:
            self.click_position(account_index, target_position[0], target_position[1])
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"账号{account_index} 使用{item_name}，目标位置: {target_position}", "action")
        else:
            # 如果没有指定目标位置，使用默认位置
            default_pos = (764, 380)
            self.click_position(account_index, default_pos[0], default_pos[1])
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"账号{account_index} 使用{item_name}，使用默认位置: {default_pos}", "action")

        return True

    # 按坐标+状态优先级查找武将（不依赖列表索引，支持列表含多条目）
    # 优先级: replacing(替换中) > reviving(复活中) > alive(存活)
    def _find_general_by_position(self, generals, target_position):
        candidates = [g for g in generals
                      if abs(g["position"][0] - target_position[0]) < 50
                      and abs(g["position"][1] - target_position[1]) < 50]
        for g in candidates:
            if g.get("replacing", False):
                return g
        for g in candidates:
            if g.get("reviving", False):
                return g
        for g in candidates:
            if g.get("alive", True) and not g.get("pending_kick", False):
                return g
        return candidates[-1] if candidates else None

    # 初始化单位信息
    def init_unit_info(self):
        """初始化单位信息数据结构
        每个账号只有1个主角，最多2个武将
        账号0在中间排，账号1在上排，账号2在下排
        """
        account_count = self.get_account_count()
        for i in range(account_count):
            # 根据账号索引确定主角位置
            if i == 0:
                # 账号0：中间排
                main_char_position = (793, 380)
                main_char_name = "主角"
            elif i == 1:
                # 账号1：上排
                main_char_position = (764, 278)
                main_char_name = "主角"
            else:  # i == 2
                # 账号2：下排
                main_char_position = (825, 490)
                main_char_name = "主角"

            self.unit_info[i] = {
                "main_char": {
                    "name": main_char_name,
                    "position": main_char_position,
                    "alive": True,
                    "need_revive": False,
                    "revive_pending_verification": False,  # 复活待验证标记
                    "reviving": False,  # 复活中标记，默认False
                    "generals": [],
                    "deployed_turn": 0,
                },
            }
            self.dead_units[i] = {
                "main_char": None,  # 格式: {'name': '主角', 'position': (x, y), 'account_index': i} 或 None
                "generals": [],
            }  # 格式: {'main_char': {...} 或 None, 'generals': [...]}
            self.skill_cd[i] = {}
            self.pending_liubei_summon[i] = (
                None  # 待召唤刘备记录：None 或 {'target_account_index': int, 'target_char_index': int, 'target_char_info': dict}
            )
            self.liubei_skill_index[i] = 0  # 初始化刘备技能索引
            self.liubei_skill_cd[i] = {}  # 初始化刘备技能冷却记录
            self.liubei_remaining[i] = self.liubei_counts.get(i, 0)
            self.has_liubei[i] = self.liubei_remaining.get(i, 0) > 0
            self.low_hp_units[i] = []  # 初始化血量低的单位列表
            self.zhugeliang_found[i] = False  # 初始化诸葛亮单位标记
            self.zhugeliang_status1_missing_count[i] = 0  # 初始化诸葛亮状态1缺失计数
            self.zhugeliang_status2_missing_count[i] = 0  # 初始化诸葛亮状态2缺失计数
            # 初始化账号区域映射(每个账号检测自己主角和武将的区域)
            if i not in self.hp_bar_unit_mapping:
                self.hp_bar_unit_mapping[i] = {}
                # 映射9个血量条区域到单位
                # 区域索引映射：账号1主角(0), 账号0主角(1), 账号2主角(2),
                #               账号1武将1(3,后排), 账号0武将1(4,后排), 账号2武将1(5,后排),
                #               账号1武将2(6,前排), 账号0武将2(7,前排), 账号2武将2(8,前排)
                if i == 0:
                    # 账号0（中间排）：主角在region 1，武将1在region 4（后排），武将2在region 7（前排）
                    self.hp_bar_unit_mapping[i][1] = ("main_char", "主角", self.unit_positions[i]["main_char"])
                    self.hp_bar_unit_mapping[i][4] = (
                        "general",
                        "武将1",
                        (
                            self.unit_positions[i]["generals"][0][1:]
                            if len(self.unit_positions[i]["generals"]) > 0
                            else (0, 0)
                        ),
                    )
                    self.hp_bar_unit_mapping[i][7] = (
                        "general",
                        "武将2",
                        (
                            self.unit_positions[i]["generals"][1][1:]
                            if len(self.unit_positions[i]["generals"]) > 1
                            else (0, 0)
                        ),
                    )
                elif i == 1:
                    # 账号1（上排）：主角在region 0，武将1在region 3（后排），武将2在region 6（前排）
                    self.hp_bar_unit_mapping[i][0] = ("main_char", "主角", self.unit_positions[i]["main_char"])
                    self.hp_bar_unit_mapping[i][3] = (
                        "general",
                        "武将1",
                        (
                            self.unit_positions[i]["generals"][0][1:]
                            if len(self.unit_positions[i]["generals"]) > 0
                            else (0, 0)
                        ),
                    )
                    self.hp_bar_unit_mapping[i][6] = (
                        "general",
                        "武将2",
                        (
                            self.unit_positions[i]["generals"][1][1:]
                            if len(self.unit_positions[i]["generals"]) > 1
                            else (0, 0)
                        ),
                    )
                else:  # i == 2
                    # 账号2（下排）：主角在region 2，武将1在region 5（后排），武将2在region 8（前排）
                    self.hp_bar_unit_mapping[i][2] = ("main_char", "主角", self.unit_positions[i]["main_char"])
                    self.hp_bar_unit_mapping[i][5] = (
                        "general",
                        "武将1",
                        (
                            self.unit_positions[i]["generals"][0][1:]
                            if len(self.unit_positions[i]["generals"]) > 0
                            else (0, 0)
                        ),
                    )
                    self.hp_bar_unit_mapping[i][8] = (
                        "general",
                        "武将2",
                        (
                            self.unit_positions[i]["generals"][1][1:]
                            if len(self.unit_positions[i]["generals"]) > 1
                            else (0, 0)
                        ),
                    )

    # ==================== 轮询监听核心功能 ====================
    def check_tombstones_all(self, detect_account_index=0):
        """一次性扫描全部9个区域，对号入座更新对应账号的unit_info"""
        dead_list = []
        for region_idx, region in enumerate(self.hp_bar_regions):
            acct = self.hp_region_to_account.get(region_idx)
            if acct is None:
                continue
            if not self.is_account_active(acct):
                continue
            lantiao_pos = self.find_image(detect_account_index, self.target_lantiao_image, region, 0)

            is_first_turn = self.current_turn == 0 or self.current_turn == 1
            should_track_missing = (not is_first_turn)

            key = (acct, region_idx)
            if lantiao_pos:
                if key in self.lantiao_missing_rounds:
                    del self.lantiao_missing_rounds[key]
                if acct in self.hp_bar_unit_mapping:
                    if region_idx in self.hp_bar_unit_mapping[acct]:
                        unit_type, unit_name, position = self.hp_bar_unit_mapping[acct][region_idx]
                        if unit_type == "main_char":
                            with self._state_lock:
                                if acct in self.unit_info:
                                    char_info = self.unit_info[acct]["main_char"]
                                    if not char_info.get("alive", False):
                                        char_info["alive"] = True
                                        char_info["revive_pending_verification"] = False
                                        char_info["reviving"] = False
                                        char_info["need_revive"] = False
                                        for dead_char in self.global_dead_units["main_chars"][:]:
                                            if dead_char.get("account_index") == acct:
                                                self.global_dead_units["main_chars"].remove(dead_char)
                                                break
                                    elif char_info.get("revive_pending_verification", False) or char_info.get("reviving", False):
                                        self._confirm_revive_success_unlocked(acct)
                        elif unit_type == "general":
                            with self._state_lock:
                                if acct not in self.unit_info:
                                    continue
                                char_info = self.unit_info[acct]["main_char"]
                                generals = char_info.get("generals", [])
                                gen = self._find_general_by_position(generals, position)
                                if gen:
                                    if gen.get("replacing", False):
                                        pass
                                    elif not gen.get("alive", True):
                                        gen["alive"] = True
                                        gen["reviving"] = False
                                        gen_name = gen.get("name", unit_name)
                                        gen_pos = gen.get("position", position)
                                        for dead_gen in self.global_dead_units["generals"][:]:
                                            if dead_gen.get("account_index") == acct and (dead_gen.get("name") == gen_name or dead_gen.get("position") == gen_pos):
                                                self.global_dead_units["generals"].remove(dead_gen)
                                                break
                                    elif gen.get("reviving", False):
                                        gen["alive"] = True
                                        gen["reviving"] = False
            else:
                if should_track_missing:
                    if key not in self.lantiao_missing_rounds:
                        self.lantiao_missing_rounds[key] = 0
                    self.lantiao_missing_rounds[key] += 1
                    if self.lantiao_missing_rounds[key] >= 3:
                        if acct in self.hp_bar_unit_mapping and region_idx in self.hp_bar_unit_mapping[acct]:
                            unit_type, unit_name, position = self.hp_bar_unit_mapping[acct][region_idx]
                            fuhuobeidong_pos = self.find_image(detect_account_index, self.target_fuhuobeidong_image, region, 0)
                            if fuhuobeidong_pos:
                                if key in self.lantiao_missing_rounds:
                                    del self.lantiao_missing_rounds[key]
                                continue
                            if unit_type == "main_char":
                                with self._state_lock:
                                    if acct not in self.unit_info:
                                        continue
                                    char_info = self.unit_info[acct]["main_char"]
                                    if char_info.get("reviving", False) or char_info.get("revive_pending_verification", False):
                                        self._confirm_revive_failure(acct)
                                    elif char_info.get("alive", True):
                                        char_info["reviving"] = False
                                        char_info["revive_pending_verification"] = False
                                        char_info["alive"] = False
                                        char_info["need_revive"] = True
                                        already_in_global = any(d.get("account_index") == acct for d in self.global_dead_units["main_chars"])
                                        if not already_in_global:
                                            self.global_dead_units["main_chars"].append({"name": char_info.get("name", "主角"), "position": char_info.get("position", (793, 380)), "account_index": acct})
                                        self.dead_units[acct]["main_char"] = {"name": char_info.get("name", "主角"), "position": char_info.get("position", (793, 380)), "account_index": acct}
                                        self.report_battle_info(f"账号{acct} 主角死亡", "warning")
                            elif unit_type == "general":
                                with self._state_lock:
                                    if acct not in self.unit_info:
                                        continue
                                    char_info = self.unit_info[acct]["main_char"]
                                    generals = char_info.get("generals", [])
                                    gen = self._find_general_by_position(generals, position)
                                    if gen:
                                        gen_name = gen.get("name", unit_name)
                                        if gen.get("replacing", False):
                                            if key in self.lantiao_missing_rounds:
                                                del self.lantiao_missing_rounds[key]
                                            pending_kick_gen = None
                                            for g in generals:
                                                if (g.get("pending_kick", False)
                                                    and abs(g["position"][0] - position[0]) < 50
                                                    and abs(g["position"][1] - position[1]) < 50):
                                                    pending_kick_gen = g
                                                    break
                                            if pending_kick_gen and pending_kick_gen.get("alive", True):
                                                pending_kick_gen["alive"] = False
                                                old_gen_name = pending_kick_gen.get("name", gen_name)
                                                old_region_idx = self._find_region_by_position(acct, pending_kick_gen.get("position"))
                                                dead_general_info = {"name": old_gen_name, "position": pending_kick_gen.get("position", position), "account_index": acct, "region_idx": old_region_idx}
                                                already_in_global = any(d.get("account_index") == acct and d.get("region_idx") == old_region_idx for d in self.global_dead_units["generals"])
                                                if not already_in_global:
                                                    self.global_dead_units["generals"].append(dead_general_info)
                                                if acct not in self.dead_units:
                                                    self.dead_units[acct] = {"main_char": None, "generals": []}
                                                self.dead_units[acct]["generals"].append(dead_general_info)
                                                if old_region_idx is not None:
                                                    old_key = (acct, old_region_idx)
                                                    self.ally_undead_rounds[old_key] = -1
                                                    if old_key in self.ally_undead_last_increment_turn:
                                                        del self.ally_undead_last_increment_turn[old_key]
                                                self.report_battle_info(f"账号{acct} 旧武将{old_gen_name}死亡(replacing期间,蓝条缺失)", "warning")
                                            continue
                                        elif gen.get("reviving", False):
                                            gen["alive"] = False
                                            gen["reviving"] = False
                                        elif gen.get("alive", True):
                                            gen["alive"] = False
                                            dead_general_info = {"name": gen_name, "position": gen.get("position", position), "account_index": acct, "region_idx": region_idx}
                                            already_in_global = any(d.get("account_index") == acct and d.get("region_idx") == region_idx for d in self.global_dead_units["generals"])
                                            if not already_in_global:
                                                self.global_dead_units["generals"].append(dead_general_info)
                                            self.dead_units[acct]["generals"].append(dead_general_info)
                                            self.report_battle_info(f"账号{acct} 武将{gen_name}死亡", "warning")
                                            if gen_name == "刘备":
                                                _target = self._claimed_clear_target.get(acct)
                                                if _target is not None and _target.get("claimed_by") == acct:
                                                    _target["claimed_by"] = None
                                                self._claimed_clear_target[acct] = None
                                    else:
                                        dead_general_info = {"name": unit_name, "position": position, "account_index": acct, "region_idx": region_idx}
                                        already_in_global = any(d.get("account_index") == acct and d.get("region_idx") == region_idx for d in self.global_dead_units["generals"])
                                        if not already_in_global:
                                            self.global_dead_units["generals"].append(dead_general_info)
                                        self.dead_units[acct]["generals"].append(dead_general_info)
                            
                            already_added = any(d["account_index"] == acct and d["region_index"] == region_idx for d in dead_list)
                            if not already_added:
                                dead_list.append({"account_index": acct, "unit_type": unit_type, "unit_name": unit_name, "position": position, "region_index": region_idx})

            if lantiao_pos:
                continue
            x, y, w, h = region
            tombstone_search_region = (x, int(y + 40), w, int(h + 110))
            tombstone_pos = self.find_image(detect_account_index, self.tombstone_image, tombstone_search_region, 0)
            if tombstone_pos:
                if acct in self.hp_bar_unit_mapping and region_idx in self.hp_bar_unit_mapping[acct]:
                    unit_type, unit_name, position = self.hp_bar_unit_mapping[acct][region_idx]
                    fuhuobeidong_pos = self.find_image(detect_account_index, self.target_fuhuobeidong_image, region, 0)
                    if fuhuobeidong_pos:
                        if key in self.lantiao_missing_rounds:
                            del self.lantiao_missing_rounds[key]
                        continue
                    if unit_type == "general" and acct in self.unit_info:
                        has_replacing = any(
                            g.get("replacing", False)
                            and abs(g.get("position", (0,0))[0] - position[0]) < 50
                            and abs(g.get("position", (0,0))[1] - position[1]) < 50
                            for g in self.unit_info[acct]["main_char"].get("generals", [])
                        )
                        if has_replacing:
                            continue
                    already_added = any(d["account_index"] == acct and d["region_index"] == region_idx for d in dead_list)
                    if not already_added:
                        dead_list.append({"account_index": acct, "unit_type": unit_type, "unit_name": unit_name, "position": position, "region_index": region_idx})
            time.sleep(0.03)
        return dead_list

    # 检测操作按钮(检测是否在战斗页面且可以操作)
    def check_action_button(self, account_index):
        """检测指定账号是否在战斗页面且可以操作(通过检测操作按钮)
        需要同时检测多个按钮来确认真的在战斗页面
        """
        # 检查操作按钮图片是否存在
        action_button_image = self.button_images.get("操作按钮")
        if not action_button_image:
            return False

        # 在右侧按钮区域查找操作按钮
        button_pos = self.find_image(account_index, action_button_image, self.right_button_region, 0)
        if button_pos:
            return True

        # 额外验证：检查是否在战斗页面（通过检测其他战斗相关的元素）
        # 例如：检测技能按钮或召唤按钮是否存在（战斗页面特有的按钮）
        skill_button_pos = self.find_image(
            account_index, self.button_images.get("技能按钮"), self.right_button_region, 0
        )
        summon_button_pos = self.find_image(
            account_index, self.button_images.get("召唤按钮"), self.right_button_region, 0
        )

        # 如果操作按钮存在，且至少有一个其他战斗按钮存在，才认为在战斗页面
        if skill_button_pos or summon_button_pos:
            return True

        return False

    def detect_target_positions(self):
        if self.target_positions_detected:
            return

        dm_index = 0
        dm = self.get_account_dm(dm_index)
        if not dm:
            return

        self.enemy_target_index = 0
        self.ally_target_index = 0

        # 多次采样取最大值，避免回合开始瞬间蓝条未刷新导致漏检
        max_raw_positions = []
        for _ in range(2):
            raw_positions = self._find_all_lantiao(dm_index, self.enemy_region, self.enemy_target_image)
            if len(raw_positions) > len(max_raw_positions):
                max_raw_positions = raw_positions
            if len(max_raw_positions) >= 3:
                break
            time.sleep(0.15)
        # 四象副本的敌军蓝条与实际点击位置Y偏移不同（四象+48，其他+70）
        _enemy_y_offset = 48 if self.combat_scene == "四象" else 70
        self.enemy_target_positions = [(x + 26, y + _enemy_y_offset) for x, y in max_raw_positions]
        if not self.enemy_target_positions:
            self.enemy_target_positions = [(104, 344)]
        self.enemy_count = len(self.enemy_target_positions)
        if self.enemy_count <= 1:
            self.enemy_single_rounds += 1
        else:
            self.enemy_single_rounds = 0

        # 我方点位：从unit_positions取存活单位的固定点位，不依赖蓝条检测
        # 避免技能面板打开时lantiao.bmp误识别导致点位不可靠
        self.ally_target_positions = []
        for acct in range(self.get_account_count()):
            if acct not in self.unit_info:
                continue
            char_info = self.unit_info[acct]["main_char"]
            if char_info.get("alive", False):
                self.ally_target_positions.append(self.unit_positions[acct]["main_char"])
            for gen in char_info.get("generals", []):
                if gen.get("alive", False) and not gen.get("replacing", False):
                    gen_pos = gen.get("position")
                    if gen_pos:
                        self.ally_target_positions.append(gen_pos)
        if not self.ally_target_positions:
            self.ally_target_positions = [(764, 380)]

        self.target_positions_detected = True

    def _detect_liubei_on_field(self):
        """在我方回合开始时，由大漠对象0检测场上是否有刘备
        在我方区域检测self.liubei_image，如果超过10次没有找到，则设置has_liubei_on_field为False
        """
        account_index = 0  # 使用大漠对象0进行检测
        dm = self.get_account_dm(account_index)
        if not dm:
            return

        # 在我方区域检测刘备图片
        liubei_pos = self.find_image(account_index, self.liubei_image, self.ally_region, 0)

        with self._state_lock:
            if liubei_pos:
                # 找到刘备，重置计数器并设置标志为True
                self.liubei_missing_count = 0
                self.has_liubei_on_field = True
            else:
                # 未找到刘备，增加计数器
                self.liubei_missing_count += 1

                # 如果连续10次未找到，设置标志为False
                if self.liubei_missing_count >= 6:
                    if self.has_liubei_on_field:
                        self.has_liubei_on_field = False

    def _track_ally_undead(self, dm_index):
        """非我方回合追踪我方武将免死被动轮次 + 替换中验证

        替换中验证(replacing):
          召唤操作完成后新武将标记为replacing=True, 等待验证图片确认
          曹操→caocaobusi_image, 魔化关羽→moguan_verify_image, 刘备→liubei_verify_image
          确认成功→更新所有延迟状态; 超时2回合→回滚, 武将回到背包

        三态模型(所有武将统一):
          状态A(被动可用): count=0, 被动还没触发, 最安全
          状态B(被动已触发): count=1~3, 护盾持续中, 越来越危险
          状态C(被动耗尽): count>=4, 护盾消失, 随时可被打死, 需要替换

        各武将检测图片:
          曹操:   不灭雄心(bumiexiongxin) → 被动可用标记
                  不死护盾(caocaobusi)     → 被动已触发护盾
          魔化关羽: miansi1               → 被动可用标记
                  mianyisiwang1           → 被动已触发护盾
          刘备:   天地护盾(tiandihudun1)  → 被动已触发护盾(无"被动可用"图片)

        每回合只递增一次, 通过 ally_undead_last_increment_turn 控制,
        防止轮询循环中一回合多次调用导致count暴涨
        """
        current_turn = self.current_turn
        for region_idx in range(3, 9):
            # region 3-8 对应6个武将血条区域
            acct = self.hp_region_to_account.get(region_idx)
            if acct is None:
                continue
            unit_info = self.hp_bar_unit_mapping.get(acct, {}).get(region_idx)
            if not unit_info:
                continue
            _, _, position = unit_info
            if acct not in self.unit_info:
                continue
            char_info = self.unit_info[acct]["main_char"]
            gen = self._find_general_by_position(char_info.get("generals", []), position)
            if not gen:
                continue
            gen_name = gen.get("name", "")
            key = (acct, region_idx)

            # === 替换中验证: replacing武将等待验证图片确认 ===
            if gen.get("replacing", False):
                # 前置判断: 被替换武将(pending_kick)是否还在场上
                # 游戏机制: 被替换武将下场时机取决于速度, 可能1~2回合才下场
                # 召唤武将在主角操作时施法直接上场, 但要等被替换武将下场后
                # 若pending_kick武将还在场, 说明替换流程未推进到新武将上场,
                # 不递增超时计数, 持续等待
                pending_kick_gen = next(
                    (g for g in char_info.get("generals", []) if g.get("pending_kick", False)),
                    None
                )
                if pending_kick_gen:
                    pk_name = pending_kick_gen.get("name", "")
                    pk_region_idx = self._find_region_by_position(acct, pending_kick_gen.get("position"))
                    pk_still_on_field = False
                    if pk_region_idx is not None:
                        pk_region = self.hp_bar_regions[pk_region_idx]
                        if pk_name == "曹操":
                            pk_still_on_field = bool(self.find_image(dm_index, self.caocaobusi_image, pk_region, 0))
                        elif pk_name == "魔化关羽":
                            pk_still_on_field = bool(self.find_image(dm_index, self.moguan_verify_image, pk_region, 0))
                        elif pk_name == "刘备":
                            if self.liubei_verify_image:
                                pk_still_on_field = bool(self.find_image(dm_index, self.liubei_verify_image, pk_region, 0))
                        elif pk_name == "张星彩":
                            if self.xingcai_verify_image:
                                pk_still_on_field = bool(self.find_image(dm_index, self.xingcai_verify_image, pk_region, 0))
                    if pk_still_on_field:
                        # 被替换武将还在场, 重置超时起点, 继续等待
                        gen["deployed_turn"] = current_turn
                        continue

                region = self.hp_bar_regions[region_idx]
                verify_found = False
                if gen_name == "曹操":
                    verify_found = bool(self.find_image(dm_index, self.caocaobusi_image, region, 0))
                elif gen_name == "魔化关羽":
                    verify_found = bool(self.find_image(dm_index, self.moguan_verify_image, region, 0))
                elif gen_name == "刘备":
                    if self.liubei_verify_image:
                        verify_found = bool(self.find_image(dm_index, self.liubei_verify_image, region, 0))
                elif gen_name == "张星彩":
                    if self.xingcai_verify_image:
                        verify_found = bool(self.find_image(dm_index, self.xingcai_verify_image, region, 0))

                if verify_found:
                    if acct not in self.unit_info:
                        continue
                    gen["replacing"] = False
                    gen["alive"] = True
                    char_info["generals"][:] = [
                        g for g in char_info["generals"]
                        if not g.get("pending_kick", False)
                    ]
                    # 更新免死计数
                    _prev_verify = self.ally_undead_rounds.get(key, 0)
                    self.ally_undead_rounds[key] = 0
                    self.ally_undead_last_increment_turn[key] = -1
                    # 清理global_dead_units中该账号被确认上场武将(acct+region_idx)的死亡记录
                    with self._state_lock:
                        for dead_gen in self.global_dead_units["generals"][:]:
                            if (dead_gen.get("account_index") == acct
                                and dead_gen.get("region_idx") == region_idx):
                                self.global_dead_units["generals"].remove(dead_gen)
                                break
                    # 刘备特有: 重置技能CD
                    if gen_name == "刘备":
                        self.liubei_skill_cd[acct] = {}
                        self._last_clear_attempt.pop(acct, None)
                    # 注意: has_liubei/has_general不在此处更新
                    # 它们表示背包里是否还有对应武将, 只有召唤操作失败时才设为False
                    self.need_proactive_replace = False
                    self._proactive_replace_in_progress = False
                    if gen_name == "刘备":
                        self._liubei_summon_in_progress[acct] = False
                        if not gen.get("_lb_counted", False):
                            gen["_lb_counted"] = True
                            if self.liubei_remaining.get(acct, 0) > 0:
                                self.liubei_remaining[acct] -= 1
                            self.has_liubei[acct] = self.liubei_remaining.get(acct, 0) > 0
                    self._last_kicked_info = None
                    self.replace_fail_count[acct] = 0
                    if acct in self.replace_fail_cooldown:
                        del self.replace_fail_cooldown[acct]
                    self.report_battle_info(
                        f"账号{acct} 替换验证成功: {gen_name}已上场(region={region_idx})", "success")
                else:
                    # 未检测到验证图片, 检查超时
                    deployed_turn = gen.get("deployed_turn", current_turn)
                    if current_turn - deployed_turn >= 2:
                        if acct not in self.unit_info:
                            continue
                        char_info["generals"][:] = [
                            g for g in char_info["generals"]
                            if not (g.get("replacing", False) and g.get("name") == gen_name)
                        ]
                        restored_old_gen = None
                        for g in char_info.get("generals", []):
                            if g.get("pending_kick", False):
                                g["pending_kick"] = False
                                restored_old_gen = g
                        # 回滚后验证旧武将实际存活状态(蓝条检测)
                        if restored_old_gen and restored_old_gen.get("alive", True):
                            restored_region_idx = self._find_region_by_position(acct, restored_old_gen.get("position"))
                            if restored_region_idx is not None:
                                restored_region = self.hp_bar_regions[restored_region_idx]
                                lantiao_pos = self.find_image(dm_index, self.target_lantiao_image, restored_region, 0)
                                if not lantiao_pos:
                                    restored_old_gen["alive"] = False
                                    old_gen_name = restored_old_gen.get("name", "")
                                    dead_info = {"name": old_gen_name, "position": restored_old_gen.get("position"), "account_index": acct, "region_idx": restored_region_idx}
                                    already_in_global = any(
                                        d.get("account_index") == acct and d.get("region_idx") == restored_region_idx
                                        for d in self.global_dead_units["generals"]
                                    )
                                    if not already_in_global:
                                        self.global_dead_units["generals"].append(dead_info)
                                    if acct not in self.dead_units:
                                        self.dead_units[acct] = {"main_char": None, "generals": []}
                                    self.dead_units[acct]["generals"].append(dead_info)
                                    old_key = (acct, restored_region_idx)
                                    self.ally_undead_rounds[old_key] = -1
                                    if old_key in self.ally_undead_last_increment_turn:
                                        del self.ally_undead_last_increment_turn[old_key]
                                    self.report_battle_info(
                                        f"账号{acct} 回滚后检测到{old_gen_name}已死亡(蓝条缺失)", "warning")
                        # need_proactive_replace保持True, 推进到下一个账号
                        self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                        self._proactive_replace_in_progress = False
                        if gen_name == "刘备":
                            self._liubei_summon_in_progress[acct] = False
                        self._last_kicked_info = None
                        self.replace_fail_count[acct] = self.replace_fail_count.get(acct, 0) + 1
                        if self.replace_fail_count[acct] >= 3:
                            self.replace_fail_cooldown[acct] = self.current_turn + 2
                            self.report_battle_info(
                                f"账号{acct} 连续{self.replace_fail_count[acct]}次替换失败，暂停召唤2回合", "warning")
                        # has_liubei/has_general保持True(武将回到背包了)
                        self.report_battle_info(
                            f"账号{acct} 替换超时失败: {gen_name}回到背包, "
                            f"下次替换账号{self.proactive_replace_account}", "warning")
                # replacing武将不做免死追踪, 继续下一个region
                continue

            # 张星彩等无免死被动的武将: 清理旧数据, 不追踪
            if gen_name not in ("曹操", "刘备", "魔化关羽"):
                if key in self.ally_undead_rounds:
                    del self.ally_undead_rounds[key]
                if key in self.ally_undead_last_increment_turn:
                    del self.ally_undead_last_increment_turn[key]
                if key in self.caocao_passive_missing_rounds:
                    del self.caocao_passive_missing_rounds[key]
                continue

            # 召唤中(reviving)的武将: 跳过, 等上场后再追踪
            if gen.get("reviving", False):
                continue

            # 已死亡的武将: count=-1, 清理递增记录
            if not gen.get("alive", True):
                _prev_dead = self.ally_undead_rounds.get(key, 0)
                self.ally_undead_rounds[key] = -1
                if key in self.ally_undead_last_increment_turn:
                    del self.ally_undead_last_increment_turn[key]
                if key in self.caocao_passive_missing_rounds:
                    del self.caocao_passive_missing_rounds[key]
                continue

            region = self.hp_bar_regions[region_idx]
            prev = self.ally_undead_rounds.get(key, 0)
            last_turn = self.ally_undead_last_increment_turn.get(key, -1)
            # 本回合是否还能递增(同一回合只递增一次)
            can_increment = (last_turn != current_turn)

            # === 曹操: 检测不灭雄心(被动可用), 连续6次未识别到判定被动触发 ===
            # 前置条件: 必须先识别到曹操技能图片(霸王/乱世), 确认曹操在场上
            if gen_name == "曹操":
                busi_found = self.find_image(dm_index, self.caocaobusi_image, region, 0)
                if busi_found:
                    # 不灭雄心还在 → 被动可用, count=0, 缺失计数重置
                    self.ally_undead_rounds[key] = 0
                    self.caocao_passive_missing_rounds[key] = 0
                else:
                    # 不灭雄心未识别到 → 先检查曹操是否在场（识别技能图片）
                    caocao_on_field = self.find_image(dm_index, self.general_images["曹操"], region, 0)
                    if caocao_on_field:
                        # 曹操在场 → 缺失计数+1
                        self.caocao_passive_missing_rounds[key] = self.caocao_passive_missing_rounds.get(key, 0) + 1
                        # 连续3次未识别到不灭雄心 + 曹操在场 → 判定被动触发
                        if self.caocao_passive_missing_rounds[key] >= 3:
                            if prev == 0:
                                # 首次触发: count 0→1
                                self.ally_undead_rounds[key] = 1
                                self.ally_undead_last_increment_turn[key] = current_turn
                            elif can_increment:
                                # 后续每回合+1
                                self.ally_undead_rounds[key] = prev + 1
                                self.ally_undead_last_increment_turn[key] = current_turn
                    else:
                        # 曹操不在场（或识别失败）→ 不递增 missing_rounds, 避免误判
                        pass

            # === 魔化关羽: 检测miansi1(被动可用) + mianyisiwang(已触发) ===
            elif gen_name == "魔化关羽":
                verify_found = self.find_image(dm_index, self.moguan_verify_image, region, 0)
                miansi_found = self.find_image(dm_index, self.moguan_miansi_image, region, 0)
                if verify_found:
                    # 状态A: miansi1还在 → 被动可用, count=0
                    self.ally_undead_rounds[key] = 0
                    self.ally_undead_last_increment_turn[key] = -1
                elif miansi_found:
                    # 状态B: miansi1消失 + mianyisiwang出现 → 被动已触发
                    if prev == 0:
                        self.ally_undead_rounds[key] = 1
                        self.ally_undead_last_increment_turn[key] = current_turn
                    elif can_increment:
                        self.ally_undead_rounds[key] = prev + 1
                        self.ally_undead_last_increment_turn[key] = current_turn
                else:
                    # 状态C: 两个都没了 → 被动耗尽
                    if prev > 0 and can_increment:
                        self.ally_undead_rounds[key] = prev + 1
                        self.ally_undead_last_increment_turn[key] = current_turn

            # === 刘备: 只有天地护盾(已触发), 无"被动可用"图片 ===
            elif gen_name == "刘备":
                hudun_found = self.find_image(dm_index, self.tiandihudun_image, region, 0)
                if hudun_found:
                    # 状态B: 天地护盾出现 → 被动已触发
                    if prev == 0:
                        # 首次触发: count从0变为1
                        self.ally_undead_rounds[key] = 1
                        self.ally_undead_last_increment_turn[key] = current_turn
                    elif can_increment:
                        self.ally_undead_rounds[key] = prev + 1
                        self.ally_undead_last_increment_turn[key] = current_turn
                else:
                    # 天地护盾消失
                    if prev > 0 and can_increment:
                        # 状态C: 之前触发过 → 被动耗尽, 继续递增
                        self.ally_undead_rounds[key] = prev + 1
                        self.ally_undead_last_increment_turn[key] = current_turn
                    # else: prev==0 → 被动还没触发(新刘备刚上场), count保持0

    def _find_region_by_position(self, account_index, position):
        """根据武将position坐标找到对应的血条区域索引(region_idx)
        用于将武将对象和ally_undead_rounds的key关联起来"""
        for region_idx, (_, _, pos) in self.hp_bar_unit_mapping.get(account_index, {}).items():
            if abs(pos[0] - position[0]) < 50 and abs(pos[1] - position[1]) < 50:
                return region_idx
        return None

    def _get_general_name_by_region(self, account_index, region_idx):
        """根据region_idx获取该位置上的武将类型名(曹操/刘备/魔化关羽/张星彩)
        用于预替换时确定要召唤哪个武将"""
        unit_info = self.hp_bar_unit_mapping.get(account_index, {}).get(region_idx)
        if not unit_info:
            return None
        _, _, position = unit_info
        char_info = self.unit_info[account_index]["main_char"]
        gen = self._find_general_by_position(char_info.get("generals", []), position)
        return gen.get("name") if gen else None

    def _find_best_replace_position(self, account_index):
        """找到当前账号最适合被替换的武将position

        选择规则:
          1. 永不替换张星彩(任何情况下都不踢)
          2. 优先替换免死count最高(最危险)的武将
          3. count=0的武将(刚召唤/被动未触发)不会被优先选中

        Returns: 武将position元组 或 None(所有武将都是张星彩时)
        """
        char_info = self.unit_info[account_index]["main_char"]
        alive_generals = [g for g in char_info.get("generals", [])
                          if g.get("alive", True)
                          and not g.get("replacing", False)
                          and not g.get("pending_kick", False)]
        if not alive_generals:
            return None
        best_pos = None
        best_score = -1
        for region_idx, (_, unit_name, slot_pos) in self.hp_bar_unit_mapping.get(account_index, {}).items():
            if unit_name == "主角":
                continue
            gen = self._find_general_by_position(alive_generals, slot_pos)
            if not gen:
                continue
            if gen.get("name") == "张星彩":
                continue
            count = self.ally_undead_rounds.get((account_index, region_idx), 0)
            score = count
            if score > best_score:
                best_score = score
                best_pos = slot_pos
        return best_pos

    def _undo_failed_replace(self, account_index, general_name):
        """回退失败的force_replace: 移除replacing新将 + 恢复pending_kick旧将"""
        char_info = self.unit_info[account_index]["main_char"]
        # 移除replacing中的新武将
        char_info["generals"][:] = [g for g in char_info["generals"]
            if not (g.get("name") == general_name and g.get("replacing", False))]
        # 恢复旧武将: 清除pending_kick标记(旧武将仍在列表中, 只需清除标记)
        for g in char_info.get("generals", []):
            if g.get("pending_kick", False):
                g["pending_kick"] = False
        self._last_kicked_info = None

    def detect_enemies_need_clear(self, dm_index):
        """检测需要清除状态的敌军（只检测传入的敌军单位 key）
        参考Kanloong_combat_script.py的实现
        :param dm_index: 大漠对象索引（使用0）
        """
        # 只检测传入的敌军单位 key
        if not self.enemy_keys_to_detect:
            return

        # 检查是否在第一回合之后的非我方回合（与check_tombstones的逻辑一致）
        is_first_turn = self.current_turn == 0 or self.current_turn == 1
        if is_first_turn:
            # 第一回合不检测，直接返回
            return

        for enemy_key in self.enemy_keys_to_detect:
            # 跳过"诸葛亮"的检测
            if self.clear_zhugeliang and enemy_key == "诸葛亮":
                continue
            # 从配置中获取敌军信息
            if enemy_key not in self.enemy_general_config:
                continue

            config = self.enemy_general_config[enemy_key]
            status_region = config["status_region"]
            status_images = config["status_images"]
            cast_position = config["cast_position"]

            # 诸葛亮特殊处理：先检测状态2，如果找到状态2，再检测状态1
            # 如果连续10次没有找到状态1（在找到状态2的前提下），说明需要清除状态
            if enemy_key == "诸葛亮":
                # 6曹操阵容，检测到诸葛亮血量低，开始召唤刘备准备清除状态
                if not self._zhugeliang_low_hp:
                    xuetiao_is_found = self.find_image(dm_index, self.zhugexuetiao_image, status_region, 0)
                    if xuetiao_is_found:
                        self._zhugeliang_low_hp = True
                status1_image = status_images.get("状态1")
                status2_image = status_images.get("状态2")

                # 先检测状态2
                status2_found = False
                if status2_image:
                    status2_pos = self.find_image(dm_index, status2_image, status_region, 0)
                    status2_found = status2_pos is not None

                # 更新所有账号的计数
                for account_idx in range(self.get_account_count()):
                    # 初始化计数（如果不存在）
                    if account_idx not in self.zhugeliang_status1_missing_count:
                        self.zhugeliang_status1_missing_count[account_idx] = 0

                    # 如果找到状态2，才检测状态1
                    if status2_found:
                        # 检测状态1
                        status1_found = False
                        if status1_image:
                            status1_pos = self.find_image(dm_index, status1_image, status_region, 0)
                            status1_found = status1_pos is not None

                        # 更新状态1计数
                        if status1_found:
                            # 找到状态1，重置计数
                            self.zhugeliang_status1_missing_count[account_idx] = 0
                        else:
                            # 没找到状态1，增加计数
                            self.zhugeliang_status1_missing_count[account_idx] += 1

                        # 判断条件：状态1连续10次未找到（在找到状态2的前提下）
                        if self.zhugeliang_status1_missing_count[account_idx] >= 2:
                            self.clear_zhugeliang = True
                            if not self.keep_support_general:
                                self.keep_support_general = True
                            with self._state_lock:
                                already_recorded = any(
                                    e["enemy_name"] == enemy_key for e in self.global_enemies_need_clear
                                )
                                if not already_recorded:
                                    self.global_enemies_need_clear.insert(
                                        0,
                                        {
                                            "enemy_name": enemy_key,
                                            "position": cast_position,
                                            "status_name": "状态1",
                                            "claimed_by": None,
                                            "detected_turn": self.current_turn,
                                        }
                                    )
                                # 只在第一次检测到时播报
                                if enemy_key not in self.enemy_status_reported:
                                    self.report_battle_info(
                                        f"检测到敌军{enemy_key}需要清除状态",
                                        "warning",
                                    )
                                    self.enemy_status_reported[enemy_key] = True
                    # else:
                    #     self.zhugeliang_status1_missing_count[account_idx] = 0
            else:
                # 其他武将：找到状态图片就返回需要清除
                for status_name, status_image in status_images.items():
                    status_pos = self.find_image(dm_index, status_image, status_region, 0)
                    if status_pos:
                        # 检测到状态，在6曹操阵容下需要开始召唤刘备
                        if not self.keep_support_general:
                            self.keep_support_general = True
                        with self._state_lock:
                            already_recorded = any(
                                e["enemy_name"] == enemy_key for e in self.global_enemies_need_clear
                            )
                            if not already_recorded:
                                self.global_enemies_need_clear = [
                                    e for e in self.global_enemies_need_clear
                                    if e.get("enemy_name") != enemy_key
                                ]
                                self.global_enemies_need_clear.insert(
                                    0,
                                    {
                                        "enemy_name": enemy_key,
                                        "position": cast_position,
                                        "status_name": status_name,
                                        "claimed_by": None,
                                        "detected_turn": self.current_turn,
                                    }
                                )
                            # 只在第一次检测到时播报
                            if enemy_key not in self.enemy_status_reported:
                                self.report_battle_info(
                                    f"检测到敌军{enemy_key}需要清除状态",
                                    "warning",
                                )
                                self.enemy_status_reported[enemy_key] = True
                        # Part1: 检查是否有账号上回合清除失败
                        for acct_idx, attempt in list(self._last_clear_attempt.items()):
                            if attempt["enemy_name"] == enemy_key and \
                               self.current_turn - attempt["turn"] <= 2:
                                if acct_idx in self.liubei_skill_cd:
                                    self.liubei_skill_cd[acct_idx].pop("清除状态", None)
                                self.report_battle_info(
                                    f"账号{acct_idx} 上回合清除{enemy_key}失败，CD已重置为0",
                                    "warning"
                                )
                                del self._last_clear_attempt[acct_idx]
                        break

    def _get_liubei_clear_cd_remaining(self, account_index):
        """获取指定账号刘备清除状态技能的CD剩余回合数"""
        cd_info = self.liubei_skill_cd.get(account_index, {})
        last_use = cd_info.get("清除状态", -999)
        cd_total = self.skill_cd_config.get("清除状态", 5)
        remaining = cd_total - (self.current_turn - last_use)
        return max(0, remaining)

    def _cleanup_expired_clear_targets(self):
        """清理已过期的清除任务（状态持续回合已到，自然消失）"""
        if not self.global_enemies_need_clear:
            return
        remaining = []
        expired = []
        for e in self.global_enemies_need_clear:
            enemy_name = e.get("enemy_name", "")
            config = self.enemy_general_config.get(enemy_name, {})
            duration = config.get("status_duration", 999)
            if self.current_turn - e.get("detected_turn", 0) >= duration:
                expired.append(e)
            else:
                remaining.append(e)
        if not expired:
            return
        with self._state_lock:
            self.global_enemies_need_clear = remaining
            for e in expired:
                if e.get("claimed_by") is not None:
                    acct = e["claimed_by"]
                    if self._claimed_clear_target.get(acct) is e:
                        self._claimed_clear_target[acct] = None
                enemy_name = e.get("enemy_name", "")
                if enemy_name in self.enemy_status_reported:
                    del self.enemy_status_reported[enemy_name]
                # 诸葛亮一旦检测到需要清除，永久跳过后续检测（直到新一轮战斗reset_state）
                # 不再在此处重置 clear_zhugeliang = False
                duration = self.enemy_general_config.get(enemy_name, {}).get("status_duration", 999)
                self.report_battle_info(
                    f"敌军{enemy_name}状态已过期（持续{duration}回合），从清除列表移除",
                    "system",
                )
            if not self.global_enemies_need_clear and not self.enable_persistent_liubei:
                self.keep_support_general = False
                self._zhugeliang_low_hp = False
                self.report_battle_info("所有敌军状态已过期，恢复6曹操模式", "system")


    # 更新单位信息(根据墓碑检测结果)
    def update_unit_info_from_tombstones(self, dead_list):
        """根据墓碑检测结果更新单位信息（统一存储到全局记录）"""
        # 第一个回合开始时，将所有单位默认为存活状态
        # 只在current_turn == 0时清空（真正的第一个回合初始化）
        # 之后不再清空，避免清空已检测到的阵亡单位
        if self.current_turn == 0:
            account_count = self.get_account_count()
            for account_idx in range(account_count):
                if account_idx not in self.unit_info:
                    continue

                # 将主角设置为存活
                char_info = self.unit_info[account_idx]["main_char"]
                char_info["alive"] = True
                char_info["need_revive"] = False

                # 将所有武将设置为存活
                for general_info in char_info.get("generals", []):
                    general_info["alive"] = True

                # 清空阵亡记录（本地和全局）
                self.dead_units[account_idx]["main_char"] = None
                self.dead_units[account_idx]["generals"] = []
            # 清空全局阵亡记录
            self.global_dead_units["main_chars"] = []
            self.global_dead_units["generals"] = []
            # 将current_turn设置为1，避免后续再次清空
            self.current_turn = 1

        # 根据墓碑检测结果，将检测到墓碑的单位设置为死亡状态
        for dead_unit in dead_list:
            account_idx = dead_unit["account_index"]
            unit_type = dead_unit["unit_type"]
            unit_name = dead_unit["unit_name"]
            position = dead_unit["position"]

            if unit_type == "main_char":
                # 主角阵亡（检测到墓碑）- 统一处理死亡逻辑
                with self._state_lock:
                    # 先检查全局记录，避免重复
                    already_in_global = False
                    for dead_char in self.global_dead_units["main_chars"]:
                        if dead_char.get("name") == unit_name and dead_char.get("account_index") == account_idx:
                            already_in_global = True
                            break

                    # 如果已经在全局记录中，说明已经处理过了，直接返回
                    # 但需要确保状态正确（清除reviving标志）
                    if already_in_global:
                        if account_idx not in self.unit_info:
                            continue
                        char_info = self.unit_info[account_idx]["main_char"]
                        old_reviving = char_info.get("reviving", False)
                        if old_reviving:
                            char_info["reviving"] = False
                            if "reviving_timestamp" in char_info:
                                del char_info["reviving_timestamp"]
                        continue

                    # 更新单位信息（每个账号只有1个主角）
                    if account_idx not in self.unit_info:
                        continue
                    char_info = self.unit_info[account_idx]["main_char"]

                    # 检测到墓碑，强制清除所有复活相关标记（无论之前是什么状态）
                    # 必须在锁内原子操作，确保其他线程看到一致的状态
                    old_reviving = char_info.get("reviving", False)
                    old_alive = char_info.get("alive", True)
                    old_revive_pending = char_info.get("revive_pending_verification", False)
                    char_info["reviving"] = False
                    if "reviving_timestamp" in char_info:
                        del char_info["reviving_timestamp"]
                    char_info["revive_pending_verification"] = False
                    char_info["alive"] = False
                    char_info["need_revive"] = True

                    # 之前是存活的,现在阵亡了，添加到全局记录
                    # 添加到全局阵亡记录（所有账号共享）- 必须在清除reviving之后立即添加，保证原子性
                    dead_char_info = {"name": unit_name, "position": position, "account_index": account_idx}
                    self.global_dead_units["main_chars"].append(dead_char_info)

                    # 也添加到本地记录（用于兼容旧代码）
                    self.dead_units[account_idx]["main_char"] = dead_char_info

                    self.report_battle_info(f"账号{account_idx} {unit_name}阵亡（检测到墓碑）", "warning")
            elif unit_type == "general":
                # 武将阵亡（检测到墓碑）- 按坐标+优先级匹配
                with self._state_lock:
                    if account_idx not in self.unit_info:
                        continue
                    char_info = self.unit_info[account_idx]["main_char"]
                    generals = char_info.get("generals", [])
                    gen = self._find_general_by_position(generals, position)
                    if gen:
                        gen_name = gen.get("name", unit_name)
                        if gen.get("replacing", False):
                            if account_idx not in self.unit_info:
                                continue
                            char_info["generals"][:] = [
                                g for g in char_info["generals"]
                                if not (g.get("replacing", False) and g.get("name") == gen_name)
                            ]
                            for g in char_info.get("generals", []):
                                if g.get("pending_kick", False):
                                    g["pending_kick"] = False
                                    g["alive"] = False
                                    old_gen_name = g.get("name", gen_name)
                                    old_region_idx = self._find_region_by_position(account_idx, g.get("position"))
                                    dead_general_info = {
                                        "name": old_gen_name,
                                        "position": g.get("position", position),
                                        "account_index": account_idx,
                                        "region_idx": old_region_idx,
                                    }
                                    already_in_global = any(
                                        d.get("account_index") == account_idx and d.get("region_idx") == old_region_idx
                                        for d in self.global_dead_units["generals"]
                                    )
                                    if not already_in_global:
                                        self.global_dead_units["generals"].append(dead_general_info)
                                    if account_idx not in self.dead_units:
                                        self.dead_units[account_idx] = {"main_char": None, "generals": []}
                                    self.dead_units[account_idx]["generals"].append(dead_general_info)
                                    if old_region_idx is not None:
                                        old_key = (account_idx, old_region_idx)
                                        self.ally_undead_rounds[old_key] = -1
                                        if old_key in self.ally_undead_last_increment_turn:
                                            del self.ally_undead_last_increment_turn[old_key]
                            self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                            self._proactive_replace_in_progress = False
                            if gen_name == "刘备":
                                self._liubei_summon_in_progress[account_idx] = False
                            self._last_kicked_info = None
                            self.report_battle_info(
                                f"账号{account_idx} {gen_name}替换失败(墓碑检测), 旧武将已阵亡, "
                                f"下次替换账号{self.proactive_replace_account}", "warning")
                        else:
                            gen_alive = gen.get("alive", True)
                            if gen_alive:
                                gen["alive"] = False
                                if gen.get("reviving", False):
                                    gen["reviving"] = False
                                dead_general_info = {
                                    "name": gen_name,
                                    "position": gen.get("position", position),
                                    "account_index": account_idx,
                                    "region_idx": dead_unit.get("region_index"),
                                }
                                already_in_global = any(
                                    d.get("account_index") == account_idx and d.get("region_idx") == dead_unit.get("region_index")
                                    for d in self.global_dead_units["generals"]
                                )
                                if not already_in_global:
                                    self.global_dead_units["generals"].append(dead_general_info)
                                self.dead_units[account_idx]["generals"].append(dead_general_info)
                                self.report_battle_info(f"账号{account_idx} {gen_name}阵亡（检测到墓碑）", "warning")
                    else:
                        # 判断当前账号存活武将数是否已满（武将位上限2）
                        # 若已满，说明该墓碑为force_replace被踢武将的历史残留，不需要补位，跳过录入
                        alive_general_count = sum(
                            1 for _g in char_info.get("generals", [])
                            if _g.get("alive", True) and not _g.get("replacing", False)
                            and not _g.get("pending_kick", False)
                        )
                        if alive_general_count >= 2:
                            continue
                        _region_idx = dead_unit.get("region_index")
                        dead_general_info = {
                            "name": unit_name,
                            "position": position,
                            "account_index": account_idx,
                            "region_idx": _region_idx,
                        }
                        already_in_global = any(
                            d.get("account_index") == account_idx and d.get("region_idx") == _region_idx
                            for d in self.global_dead_units["generals"]
                        )
                        if not already_in_global:
                            self.global_dead_units["generals"].append(dead_general_info)
                            self.dead_units[account_idx]["generals"].append(dead_general_info)
                            self.report_battle_info(
                                f"账号{account_idx} 武将{unit_name}阵亡（检测到墓碑，槽位为空）", "warning"
                            )

    # 使用恢复药
    def use_heal_item(self, account_index, target_unit_info):
        """使用恢复药给目标单位加血
        :param account_index: 账号索引
        :param target_unit_info: 目标单位信息 {'unit_type': str, 'unit_name': str, 'position': (x, y)}
        :return: True/False
        """
        try:
            # 检查恢复药CD
            item_cd_config = self.item_cd_config.get("恢复药", 3)
            last_used_turn = self.item_cd_tracking.get(account_index, {}).get("恢复药", -999)
            if (self.current_turn - last_used_turn) < item_cd_config:
                # 恢复药在冷却中
                return False

            # 1. 点击道具按钮（5秒内找到，否则返回False）
            start_time = time.time()
            timeout = 1.5
            item_button_pos = None

            while time.time() - start_time < timeout:
                item_button_pos = self.find_image(
                    account_index, self.button_images["道具按钮"], self.right_button_region, 0
                )
                if item_button_pos:
                    break
                time.sleep(0.1)  # 每次查找间隔0.2秒

            if not item_button_pos:
                self.report_battle_info(f"账号{account_index} 未找到道具按钮（2秒超时）", "error")
                return False

            self.click_position(account_index, item_button_pos.x, item_button_pos.y)
            # 增加等待时间，确保道具面板完全弹出
            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)

            # 2. 等待恢复药出现并点击（5秒内找到，否则返回False）
            heal_item_image = self.item_images.get("恢复药")
            if not heal_item_image:
                self.report_battle_info(f"账号{account_index} 未找到恢复药图片配置", "error")
                return False

            # 5秒内循环查找恢复药，使用更大的搜索区域
            start_time = time.time()
            timeout = 3.0
            heal_item_pos = None

            # 尝试多个搜索区域：先尝试道具面板区域，如果找不到则尝试全屏
            search_regions = [
                self.item_panel_region,  # 道具面板区域
                self.ally_region,  # 己方区域（作为备选）
            ]

            while time.time() - start_time < timeout:
                for search_region in search_regions:
                    # 使用更低的识别率查找恢复药（道具可能较难识别）
                    heal_item_pos = self.find_image(
                        account_index, heal_item_image, search_region, 0, use_lower_confidence=True
                    )
                    if heal_item_pos:
                        break
                    time.sleep(0.05)  # 每个区域查找间隔0.1秒
                if heal_item_pos:
                    break
                time.sleep(0.05)  # 每次循环间隔0.2秒

            if not heal_item_pos:
                self.report_battle_info(
                    f"账号{account_index} 道具面板中未找到恢复药（2秒超时）", "error"
                )
                self._no_heal_item_missing_turn[account_index] = self.current_turn
                return False

            self.click_position(account_index, heal_item_pos.x, heal_item_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)

            # 3. 点击目标单位的位置
            target_position = target_unit_info["position"]
            self.click_position(account_index, target_position[0], target_position[1])
            time.sleep(CombatConstants.ACTION_DELAY)

            # 4. 记录恢复药使用和冷却时间
            if account_index not in self.item_cd_tracking:
                self.item_cd_tracking[account_index] = {}
            self.item_cd_tracking[account_index]["恢复药"] = self.current_turn

            # 5. 从血量低单位列表中移除（如果存在）
            if account_index in self.low_hp_units:
                for unit_info in self.low_hp_units[account_index][:]:
                    if (
                        unit_info["unit_type"] == target_unit_info["unit_type"]
                        and unit_info["unit_name"] == target_unit_info["unit_name"]
                    ):
                        self.low_hp_units[account_index].remove(unit_info)
                        break

            self.report_battle_info(f"账号{account_index} 使用恢复药给{target_unit_info['unit_name']}加血", "success")
            self.click_position(account_index,12,12)
            self._no_heal_item_missing_turn.pop(account_index, None)
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 使用恢复药失败: {e}", "error")
            return False

    def _try_use_heal_for_low_hp(self, account_index):
        """主角没技能时，尝试用恢复药给低血单位加血
        
        优先级：主角 > 武将
        use_heal_item 内部已有 CD 检查 + 2s 超时，找不到自动返回 False
        """
        last_miss = self._no_heal_item_missing_turn.get(account_index, -999)
        if self.current_turn - last_miss < 3:
            return False
        low_units = self.low_hp_units.get(account_index, [])
        if not low_units:
            return False
        
        for u in low_units:
            if u["unit_type"] == "main_char":
                return self.use_heal_item(account_index, u)
        
        return self.use_heal_item(account_index, low_units[0])

    def _use_mana_item(self, account_index, target_unit_info):
        last_used = self.item_cd_tracking.get(account_index, {}).get("蓝药", -999)
        cd_config = self.item_cd_config.get("蓝药", 3)
        if (self.current_turn - last_used) < cd_config:
            return False

        last_miss = self._no_mana_item_missing_turn.get(account_index, -999)
        if self.current_turn - last_miss < 2:
            return False

        start_time = time.time()
        timeout = 1.5
        item_btn = None
        while time.time() - start_time < timeout:
            item_btn = self.find_image(
                account_index, self.button_images["道具按钮"], self.right_button_region, 0
            )
            if item_btn:
                break
            time.sleep(0.1)
        if not item_btn:
            return False
        self.click_position(account_index, item_btn.x, item_btn.y)
        time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)

        mana_item_img = self.item_images.get("蓝药")
        if not mana_item_img:
            return False

        start_time = time.time()
        timeout = 3.0
        mana_pos = None
        search_regions = [
            self.item_panel_region,
            self.ally_region,
        ]
        while time.time() - start_time < timeout:
            for search_region in search_regions:
                mana_pos = self.find_image(
                    account_index, mana_item_img, search_region, 0, use_lower_confidence=True
                )
                if mana_pos:
                    break
                time.sleep(0.05)
            if mana_pos:
                break
            time.sleep(0.05)
        if not mana_pos:
            self._no_mana_item_missing_turn[account_index] = self.current_turn
            return False
        self.click_position(account_index, mana_pos.x, mana_pos.y)
        time.sleep(CombatConstants.ACTION_DELAY)

        target_pos = target_unit_info["position"]
        self.click_position(account_index, target_pos[0], target_pos[1])
        time.sleep(CombatConstants.ACTION_DELAY)

        if account_index not in self.item_cd_tracking:
            self.item_cd_tracking[account_index] = {}
        self.item_cd_tracking[account_index]["蓝药"] = self.current_turn
        self._no_mana_item_missing_turn.pop(account_index, None)

        self.report_battle_info(
            f"账号{account_index} 使用蓝药恢复 {target_unit_info['unit_name']} 蓝量", "success"
        )
        return True

    def _detect_gray_and_recover(self, account_index):
        gray_icon_map = [
            ("寂灭神劫", "main_char",        None),
            ("剑阵灭杀", "attack",           "曹操"),
            ("武神一怒", "attack",           "魔化关羽"),
            ("星彩群攻", "xingcai_support",  "张星彩"),
            ("控制",     "support",          "刘备"),
        ]

        for skill_name, unit_type, general_name in gray_icon_map:
            gray_path = self.gray_skill_images.get(skill_name)
            if not gray_path:
                continue
            pos = self.find_image(account_index, gray_path, self.skill_panel_region, 0)
            if not pos:
                continue

            self.report_battle_info(
                f"账号{account_index} 检测到 [{skill_name}] 灰色图标，蓝量耗尽，单位=[{general_name or '主角'}]",
                "warning"
            )

            if general_name is None:
                target_info = {
                    "unit_type": "main_char",
                    "unit_name": "主角",
                    "position": self.unit_positions[account_index]["main_char"],
                }
            else:
                char_info = self.unit_info[account_index]["main_char"]
                call_idx = self._current_our_turn_call
                matching = sorted(
                    [g for g in char_info.get("generals", [])
                     if g.get("name") == general_name and g.get("alive", True)],
                    key=lambda g: g.get("position", (0, 0))[0],
                    reverse=True
                )
                target_gen = matching[call_idx] if call_idx < len(matching) else (matching[0] if matching else None)
                if not target_gen:
                    self.report_battle_info(
                        f"账号{account_index} 未找到 {general_name} 的位置信息", "error"
                    )
                    return False
                target_info = {
                    "unit_type": "general",
                    "unit_name": general_name,
                    "position": target_gen.get("position"),
                }

            if self._use_mana_item(account_index, target_info):
                return True
            else:
                self.report_battle_info(
                    f"账号{account_index} 蓝药不可用(CD中/找不到)，降级到防御", "warning"
                )
                return False

        return False

    # ==================== 复活相关函数 ====================
    def _assign_revive_tasks(self):
        """在我方回合开始时，分配复活任务
        优先级：
        1. 其他账号的主角（如果主角存活）
        2. 随机账号的武将（如果武将存活）

        返回：{执行账号索引: 目标死亡主角账号索引}
        """
        assignments = {}

        # 收集所有需要复活的主角（过滤掉已经复活或正在待验证的）
        dead_main_chars = []
        with self._state_lock:
            for dead_char in self.global_dead_units["main_chars"]:
                dead_char_account = dead_char.get("account_index")
                if dead_char_account in self.unit_info:
                    char_info = self.unit_info[dead_char_account]["main_char"]
                    # 如果主角已经存活或正在待验证复活，跳过
                    if char_info.get("alive", False) or char_info.get("revive_pending_verification", False):
                        continue
                dead_main_chars.append(dead_char)

        if not dead_main_chars:
            # 没有需要复活的主角
            return assignments

        # 收集所有可用的执行单位
        available_main_chars = []  # [(account_index, char_info), ...]
        available_generals = []  # [(account_index, general_info), ...]

        account_count = self.get_account_count()
        for account_index in range(account_count):
            if account_index not in self.unit_info:
                continue

            # 检查主角是否可用（存活且不在复活中）
            char_info = self.unit_info[account_index]["main_char"]
            if (
                char_info.get("alive", False)
                and not char_info.get("reviving", False)
                and not char_info.get("revive_pending_verification", False)
            ):
                available_main_chars.append((account_index, char_info))

            # 检查武将是否可用（存活且不在复活中）
            for general_info in char_info.get("generals", []):
                if general_info.get("alive", False) and not general_info.get("reviving", False):
                    available_generals.append((account_index, general_info))

        # 为每个需要复活的主角分配执行单位
        for dead_char in dead_main_chars:
            target_dead_account_idx = dead_char.get("account_index")

            # 优先级1：寻找其他账号的主角（不能是自己）
            assigned = False
            for account_index, char_info in available_main_chars:
                if account_index != target_dead_account_idx:
                    # 检查该账号是否已经有分配任务
                    if account_index not in assignments:
                        assignments[account_index] = target_dead_account_idx
                        self.report_battle_info(
                            f"分配复活任务：账号{account_index}的主角 -> 账号{target_dead_account_idx}的主角", "info"
                        )
                        assigned = True
                        break

            # 优先级2：如果没有找到其他账号的主角，寻找随机账号的武将
            # ============================================================
            # 【预留改造方案（暂未实施）】同账号武将复活同账号主角
            # ------------------------------------------------------------
            # 游戏机制前提：同账号内存活武将可以复活本账号阵亡主角（已确认）。
            # 现状问题：assignments 是 {执行账号: 目标账号} 结构，一个账号只能
            #   承接一个复活任务。当账号A、B主角同时阵亡、且只有账号A有存活武将时，
            #   账号A的武将会被分配去复活账号B主角，导致账号A主角本轮无人复活
            #   （见日志 警告：无法为账号X的主角分配复活任务）。
            # 改造目标：允许同一账号的多个武将分别承接多个复活任务，使账号A的
            #   武将1复活账号B主角、武将2复活账号A主角能同时发生。
            # 改造要点：
            #   1. revive_assignments 结构由 {account: target} 改为 {(account, slot): target}，
            #      slot 区分同账号不同武将槽位。
            #   2. 本循环去重逻辑需同步改造：
            #      - 执行去重：由 `account_index not in assignments` 改为
            #        `(account_index, slot) not in assignments`（按槽位去重，非按账号去重）。
            #      - 目标去重（必须新增）：维护 assigned_targets 集合，确保同一目标账号
            #        只被分配一次，避免两个武将被分配去复活同一个主角。
            #   3. handle_our_turn 执行侧（main_char分支的"4.3 执行分配的复活任务" /
            #      support分支的"4.1 执行分配的复活任务"）需改为按 (account, slot) 取任务，
            #      且需解决"武将身份识别"难题：
            #      identify_unit_type 只能识别主角/攻击武将/辅助武将，无法识别具体槽位，
            #      同名武将+相同技能+相同面板时无法路由任务到指定武将。
            #   4. 运行时防重复无需改动：_check_and_mark_reviving / revive_main_char_with_target
            #      按目标主角的 alive/revive_pending/reviving/still_in_dead_list 状态判断，
            #      与执行账号数量无关，reviving 标志存在目标主角维度上，天然防重复。
            # 风险：武将身份无法精确路由是核心障碍，改造收益有限、复杂度高。
            # 决策：本次不实施，保留现状（资源不足时下一轮自动补救）。
            # ============================================================
            if not assigned:
                # 随机打乱武将列表，实现随机分配
                random.shuffle(available_generals)

                for account_index, general_info in available_generals:
                    # 检查该账号是否已经有分配任务
                    if account_index not in assignments:
                        assignments[account_index] = target_dead_account_idx
                        self.report_battle_info(
                            f"分配复活任务：账号{account_index}的武将{general_info.get('name', '未知')} -> 账号{target_dead_account_idx}的主角",
                            "info",
                        )
                        assigned = True
                        break

            if not assigned:
                self.report_battle_info(
                    f"警告：无法为账号{target_dead_account_idx}的主角分配复活任务（没有可用的执行单位）", "warning"
                )

        return assignments

    # 检查是否可以复活主角（不设置reviving标志，只检查状态）
    def _check_and_mark_reviving(self, target_account_index, char_name):
        """检查是否可以复活主角（只检查状态，不设置reviving标志）
        :param target_account_index: 目标账号索引（阵亡主角所属的账号）
        :param char_name: 主角名称
        :return: True表示可以复活，False表示不能复活
        """
        # 第一步：快速获取需要的数据（锁内，时间短）
        with self._state_lock:
            # 获取主角状态信息
            char_info = None
            alive = False
            revive_pending = False
            reviving = False
            need_revive = False
            if target_account_index in self.unit_info:
                char_info = self.unit_info[target_account_index]["main_char"]
                alive = char_info.get("alive", False)
                revive_pending = char_info.get("revive_pending_verification", False)
                reviving = char_info.get("reviving", False)
                need_revive = char_info.get("need_revive", False)

            # 快速检查是否在全局阵亡记录中（只检查一次，合并所有检查）
            still_in_dead_list = False
            for dead_char in self.global_dead_units["main_chars"]:
                if dead_char.get("account_index") == target_account_index:
                    still_in_dead_list = True
                    break

            # 如果reviving=True，检查是否需要清除
            if reviving:
                if not still_in_dead_list:
                    # 不在全局阵亡记录中，但reviving=True，状态异常，清除reviving标志
                    if char_info:
                        char_info["reviving"] = False
                        if "reviving_timestamp" in char_info:
                            del char_info["reviving_timestamp"]
                        self.report_battle_info(
                            f"账号{target_account_index} 主角状态异常：reviving=True但不在全局阵亡记录中，清除reviving标志",
                            "warning",
                        )
                        reviving = False
                else:
                    # 在全局阵亡记录中，但reviving=True
                    # 这说明主角已经阵亡，但reviving标志没有被清除（可能是之前设置的但复活操作失败了）
                    # 应该清除reviving标志，允许重新尝试复活
                    if char_info:
                        char_info["reviving"] = False
                        if "reviving_timestamp" in char_info:
                            del char_info["reviving_timestamp"]
                        self.report_battle_info(
                            f"账号{target_account_index} 主角已阵亡但reviving=True，清除reviving标志，允许重新尝试复活",
                            "warning",
                        )
                        reviving = False

        # 第二步：在锁外进行大部分检查逻辑（不持有锁）
        if alive or revive_pending or reviving:
            return False

        # 如果不在全局阵亡记录中，说明已经被其他线程复活了
        if not still_in_dead_list:
            return False

        # 额外检查：如果主角是死亡状态（alive=False）且不在全局阵亡记录中，说明刚检测到墓碑，不应该设置reviving
        if not alive and not need_revive:
            # 如果alive=False但need_revive=False，说明状态异常，不应该复活
            self.report_battle_info(
                f"账号{target_account_index} 主角状态异常：alive=False但need_revive=False，不能复活", "warning"
            )
            return False

        # 第三步：最后在锁内进行原子性检查（确保状态一致）
        with self._state_lock:
            # 再次检查状态（防止在检查过程中状态被其他线程修改）
            if target_account_index in self.unit_info:
                char_info = self.unit_info[target_account_index]["main_char"]
                # 再次检查所有状态，确保在检查过程中没有被其他线程修改
                if (
                    char_info.get("alive", False)
                    or char_info.get("revive_pending_verification", False)
                    or char_info.get("reviving", False)
                ):
                    # 在检查过程中，状态被其他线程修改了，不能复活
                    return False

                # 再次检查是否在全局阵亡记录中（防止在检查过程中被移除）
                still_in_dead_list_now = False
                for dead_char in self.global_dead_units["main_chars"]:
                    if dead_char.get("account_index") == target_account_index:
                        still_in_dead_list_now = True
                        break
                if not still_in_dead_list_now:
                    # 在检查过程中，主角被其他线程从全局阵亡记录中移除了，不能复活
                    return False

                # 再次确认主角状态：必须是死亡状态且需要复活
                if not (char_info.get("alive", True) == False and char_info.get("need_revive", False) == True):
                    # 状态不一致，不应该设置reviving
                    return False

                # 所有检查都通过，可以复活（但不在这里设置reviving，由revive_main_char_with_target在真正开始吃药时设置）
                return True
            else:
                # 如果账号不在unit_info中，不能复活
                return False

    # 更新复活状态（复活操作成功后调用）
    def _update_revive_status(self, target_dead_account_idx):
        """更新复活状态（复活操作成功后调用）
        :param target_dead_account_idx: 被复活的主角账号索引
        """
        # 先获取主角名称（在状态锁内获取，避免后续访问问题）
        char_name = "主角"
        with self._state_lock:
            # 获取主角名称（从单位信息中获取，如果没有则使用默认值"主角"）
            if target_dead_account_idx in self.unit_info:
                char_info = self.unit_info[target_dead_account_idx]["main_char"]
                char_name = char_info.get("name", "主角")

            # 从全局阵亡记录中移除（立即移除，确保其他线程能及时看到）
            for dead_char in self.global_dead_units["main_chars"][:]:
                if dead_char.get("account_index") == target_dead_account_idx:
                    self.global_dead_units["main_chars"].remove(dead_char)
                    break

            # 更新单位信息（标记为复活中，数量不动，等待下一回合检测蓝条确认）
            if target_dead_account_idx in self.unit_info:
                char_info = self.unit_info[target_dead_account_idx]["main_char"]
                char_info["alive"] = False  # 暂时标记为死亡，等待下一回合检测蓝条确认
                char_info["need_revive"] = False
                char_info["revive_pending_verification"] = True  # 标记为"待验证"，下个回合验证是否真的复活成功
                char_info["reviving"] = True  # 标记为复活中，数量不动

            # 清除本地记录
            if target_dead_account_idx in self.dead_units:
                self.dead_units[target_dead_account_idx]["main_char"] = None

            # 清除主角相关的蓝条缺失计数，以便后续能够重新检测死亡
            if target_dead_account_idx in self.hp_bar_unit_mapping:
                # 根据账号索引确定主角对应的region_idx
                if target_dead_account_idx == 0:
                    main_char_region_idx = 1
                elif target_dead_account_idx == 1:
                    main_char_region_idx = 0
                else:  # target_dead_account_idx == 2
                    main_char_region_idx = 2
                key = (target_dead_account_idx, main_char_region_idx)
                if key in self.lantiao_missing_rounds:
                    del self.lantiao_missing_rounds[key]

        self.report_battle_info(
            f"账号{target_dead_account_idx} 主角复活操作完成，状态已更新（下个回合通过主角操作或蓝条检测确认是否成功）",
            "info",
        )

    # 确认复活成功（在主角操作或蓝条检测时调用）
    def _confirm_revive_success(self, account_index):
        """确认复活成功（检测到蓝条）（带锁，供外部调用）
        :param account_index: 主角账号索引
        """
        with self._state_lock:
            self._confirm_revive_success_unlocked(account_index)

    def _confirm_revive_success_unlocked(self, account_index):
        """确认复活成功（检测到蓝条）（不带锁，供锁内调用）
        :param account_index: 主角账号索引
        """
        if account_index in self.unit_info:
            char_info = self.unit_info[account_index]["main_char"]
            if char_info.get("revive_pending_verification", False) or char_info.get("reviving", False):
                char_info["revive_pending_verification"] = False
                char_info["reviving"] = False
                char_info["alive"] = True  # 主角数量从0到1（alive=True表示数量为1）
                # 清除主角相关的蓝条缺失计数，以便后续能够重新检测死亡
                if account_index in self.hp_bar_unit_mapping:
                    # 根据账号索引确定主角对应的region_idx
                    if account_index == 0:
                        main_char_region_idx = 1
                    elif account_index == 1:
                        main_char_region_idx = 0
                    else:  # account_index == 2
                        main_char_region_idx = 2
                    key = (account_index, main_char_region_idx)
                    if key in self.lantiao_missing_rounds:
                        del self.lantiao_missing_rounds[key]
                self.report_battle_info(f"账号{account_index} 主角复活成功（检测到蓝条），数量: 0 -> 1", "success")

    # 确认复活失败（如果待验证但下个回合没有操作也没有蓝条）
    def _confirm_revive_failure(self, account_index):
        """确认复活失败（下一回合没检测到蓝条）
        :param account_index: 主角账号索引
        """
        with self._state_lock:
            if account_index in self.unit_info:
                char_info = self.unit_info[account_index]["main_char"]
                if char_info.get("revive_pending_verification", False) or char_info.get("reviving", False):
                    char_info["revive_pending_verification"] = False
                    char_info["reviving"] = False
                    char_info["alive"] = False  # 状态更新为死亡，数量不动（保持0）
                    char_info["need_revive"] = True
                    # 重新添加到全局阵亡记录
                    dead_char_info = {
                        "name": char_info.get("name", "主角"),
                        "position": char_info.get("position", (793, 380)),
                        "account_index": account_index,
                    }
                    if dead_char_info not in self.global_dead_units["main_chars"]:
                        self.global_dead_units["main_chars"].append(dead_char_info)
                    self.dead_units[account_index]["main_char"] = dead_char_info
                    self.report_battle_info(
                        f"账号{account_index} 主角复活失败（下一回合未检测到蓝条），状态更新为死亡，数量不变", "warning"
                    )

    # 复活主角
    def revive_main_char(self, account_index, dead_char_info):
        """复活主角"""
        try:
            # 获取目标账号索引（被复活的主角所属的账号）
            target_dead_account_idx = dead_char_info.get("account_index", account_index)

            # 1. 点击道具按钮（5秒内找到，否则返回False）
            # 5秒内循环查找道具按钮
            start_time = time.time()
            timeout = 5.0
            item_button_pos = None

            while time.time() - start_time < timeout:
                item_button_pos = self.find_image(
                    account_index, self.button_images["道具按钮"], self.right_button_region, 0
                )
                if item_button_pos:
                    break
                time.sleep(0.05)  # 每次查找间隔0.2秒

            if not item_button_pos:
                self.report_battle_info(f"账号{account_index} 未找到道具按钮（5秒超时）", "error")
                return False

            # 找到道具按钮，开始执行复活操作，设置reviving=True
            with self._state_lock:
                if target_dead_account_idx in self.unit_info:
                    char_info = self.unit_info[target_dead_account_idx]["main_char"]
                    # 再次检查状态，确保还没有被其他线程复活
                    if char_info.get("alive", False) or char_info.get("revive_pending_verification", False):
                        self.report_battle_info(
                            f"账号{account_index} 准备复活账号{target_dead_account_idx}的主角，但主角状态已改变，取消操作",
                            "warning",
                        )
                        return False
                    # 检查是否还在全局阵亡记录中
                    still_in_dead_list = False
                    for dead_char in self.global_dead_units["main_chars"]:
                        if dead_char.get("account_index") == target_dead_account_idx:
                            still_in_dead_list = True
                            break
                    if not still_in_dead_list:
                        self.report_battle_info(
                            f"账号{account_index} 准备复活账号{target_dead_account_idx}的主角，但主角已不在全局阵亡记录中，取消操作",
                            "warning",
                        )
                        return False
                    # 所有检查通过，设置reviving=True（真正开始吃药）
                    # char_info["reviving"] = True
                    self.report_battle_info(
                        f"账号{account_index} 开始复活账号{target_dead_account_idx}的主角，设置reviving=True", "info"
                    )

            self.click_position(account_index, item_button_pos.x, item_button_pos.y)
            # 增加等待时间，确保道具面板完全弹出
            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT + 0.5)

            # 2. 等待复活药出现并点击（5秒内找到，否则返回False）
            revive_item_image = self.item_images.get("复活药")
            if not revive_item_image:
                self.report_battle_info(f"账号{account_index} 未找到复活药图片配置", "error")
                # 清除复活中标记
                with self._state_lock:
                    if target_dead_account_idx in self.unit_info:
                        char_info = self.unit_info[target_dead_account_idx]["main_char"]
                        if char_info.get("reviving", False):
                            char_info["reviving"] = False
                return False

            # 5秒内循环查找复活药，使用更大的搜索区域
            start_time = time.time()
            timeout = 5.0
            revive_item_pos = None

            # 尝试多个搜索区域：先尝试道具面板区域，如果找不到则尝试全屏
            search_regions = [
                self.item_panel_region,  # 道具面板区域
                (0, 0, 900, 580),  # 全屏区域（作为备选）
                self.ally_region,  # 己方区域（作为备选）
            ]

            while time.time() - start_time < timeout:
                for search_region in search_regions:
                    # 使用更低的识别率查找复活药（道具可能较难识别）
                    revive_item_pos = self.find_image(
                        account_index, revive_item_image, search_region, 0, use_lower_confidence=True
                    )
                    if revive_item_pos:
                        break
                    time.sleep(0.1)  # 每个区域查找间隔0.1秒
                if revive_item_pos:
                    break
                time.sleep(0.1)  # 每次循环间隔0.2秒

            if not revive_item_pos:
                self.report_battle_info(
                    f"账号{account_index} 道具面板中未找到复活药（5秒超时），图片路径：{revive_item_image}", "error"
                )
                # 清除复活中标记
                with self._state_lock:
                    if target_dead_account_idx in self.unit_info:
                        char_info = self.unit_info[target_dead_account_idx]["main_char"]
                        if char_info.get("reviving", False):
                            char_info["reviving"] = False
                return False

            self.click_position(account_index, revive_item_pos.x, revive_item_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)

            # 2.5. 使用find_target_text查找目标，找到后在x+35, y+116位置点击
            target_pos = self.find_target_text(account_index, (0, 0, 900, 580), timeout=3.0)
            if target_pos:
                click_x = target_pos.x + 35
                click_y = target_pos.y + 116
                self.click_position(account_index, click_x, click_y)
                time.sleep(CombatConstants.ACTION_DELAY)

            # 3. 点击阵亡主角的位置
            else:
                char_position = dead_char_info["position"]
                self.click_position(account_index, char_position[0], char_position[1])
                time.sleep(CombatConstants.ACTION_DELAY)

            # 4. 更新单位信息（每个账号只有1个主角）
            char_name = dead_char_info["name"]
            char_info = self.unit_info[account_index]["main_char"]
            char_info["alive"] = True
            char_info["need_revive"] = False

            # 从全局和本地阵亡记录中移除
            if dead_char_info in self.global_dead_units["main_chars"]:
                self.global_dead_units["main_chars"].remove(dead_char_info)
            self.dead_units[account_index]["main_char"] = None

            self.report_battle_info(f"账号{account_index} {char_name}复活成功", "success")
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 复活{dead_char_info['name']}失败: {e}", "error")
            # 清除复活中标记
            target_dead_account_idx = dead_char_info.get("account_index", account_index)
            with self._state_lock:
                if target_dead_account_idx in self.unit_info:
                    char_info = self.unit_info[target_dead_account_idx]["main_char"]
                    if char_info.get("reviving", False):
                        char_info["reviving"] = False
            return False

    def identify_unit_type(self, account_index, timeout=2.0):
        """识别当前操作的单位类型（同步判断）
        :param account_index: 账号索引
        :param timeout: 超时时间（秒）
        :return: ("main_char", None) 或 ("attack", skill_name) 或 ("support", skill_name) 或 ("xingcai_support", skill_name) 或 (None, None)
        """
        start_time = time.time()

        # 准备攻击武将技能列表（曹操/魔化关羽的攻击技能）
        attack_skills = ["剑阵灭杀", "武神一怒", "曹操单攻"]
        attack_skill_paths = {}
        for skill_name in attack_skills:
            skill_path = self.skill_images.get(skill_name)
            if skill_path:
                attack_skill_paths[skill_name] = skill_path

        # 准备张星彩攻击技能列表（星彩群攻/星彩单攻，归类为xingcai_support）
        xingcai_attack_skills = ["星彩群攻", "星彩单攻"]
        xingcai_attack_skill_paths = {}
        for skill_name in xingcai_attack_skills:
            skill_path = self.skill_images.get(skill_name)
            if skill_path:
                xingcai_attack_skill_paths[skill_name] = skill_path

        # 准备刘备控制技能路径
        control_skill_path = self.skill_images.get("控制")

        # 准备张星彩辅助技能路径
        xingcai_support_skill_path = self.skill_images.get("星彩辅助")

        # 同步查找：先检查技能面板中的技能，最后才查召唤按钮
        # 避免召唤按钮常驻导致武将回合被误判为主角
        while time.time() - start_time < timeout:
            # 1. 查找攻击武将技能（曹操/魔化关羽）
            for skill_name, skill_path in attack_skill_paths.items():
                skill_pos = self.find_image(account_index, skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("attack", skill_name)

            # 2. 第一回合优先检测张星彩辅助技能（确保第一回合走辅助策略）
            if self.current_turn <= 1 and xingcai_support_skill_path:
                skill_pos = self.find_image(account_index, xingcai_support_skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("xingcai_support", "星彩辅助")

            # 3. 查找张星彩攻击技能（星彩群攻/星彩单攻，归类为xingcai_support）
            for skill_name, skill_path in xingcai_attack_skill_paths.items():
                skill_pos = self.find_image(account_index, skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("xingcai_support", skill_name)

            # 4. 检测张星彩辅助技能（群攻CD中时兜底）
            if xingcai_support_skill_path:
                skill_pos = self.find_image(account_index, xingcai_support_skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("xingcai_support", "星彩辅助")

            # 5. 查找刘备的控制技能（用于识别刘备）
            if control_skill_path:
                skill_pos = self.find_image(account_index, control_skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("support", "控制")

            # 6. 查找召唤按钮（主角特有）—— 兜底，技能都没找到才认为是主角
            summon_btn = self.find_image(account_index, self.button_images["召唤按钮"], self.right_button_region, 0)
            if summon_btn:
                return ("main_char", None)

            time.sleep(0.1)  # 每次循环间隔0.1秒

        return (None, None)

    def revive_main_char_with_target(self, account_index, target_dead_account_idx):
        """尝试复活主角（参考Kanloong_combat_script.py的try_revive_main_char方法）
        :param account_index: 执行操作的大漠对象索引
        :param target_dead_account_idx: 需要被复活的主角账号索引（大漠对象下标）
        :return: True表示成功，False表示失败
        """
        # 第一步：快速检查状态（锁内，时间短）
        char_name = "主角"
        with self._state_lock:
            # 获取主角名称和状态
            char_info = None
            alive = False
            revive_pending = False
            reviving = False
            if target_dead_account_idx in self.unit_info:
                char_info = self.unit_info[target_dead_account_idx]["main_char"]
                char_name = char_info.get("name", "主角")
                alive = char_info.get("alive", False)
                revive_pending = char_info.get("revive_pending_verification", False)
                reviving = char_info.get("reviving", False)

            # 快速检查是否在全局阵亡记录中
            still_in_dead_list = False
            for dead_char in self.global_dead_units["main_chars"]:
                if dead_char.get("account_index") == target_dead_account_idx:
                    still_in_dead_list = True
                    break

            # 第二步：在锁外进行状态判断
            # 如果主角已经存活或正在待验证复活，不能复活
            if alive or revive_pending:
                self.report_battle_info(
                    f"账号{account_index} 尝试复活账号{target_dead_account_idx}的主角，但主角状态：alive={alive}, revive_pending={revive_pending}，跳过",
                    "warning",
                )
                return False

            # 如果已经在复活中，说明其他线程正在处理，不能重复执行
            if reviving:
                self.report_battle_info(
                    f"账号{account_index} 尝试复活账号{target_dead_account_idx}的主角，但主角已在复活中（reviving=True），跳过",
                    "warning",
                )
                return False

            # 如果不在全局阵亡记录中，说明已经被其他线程复活了
            if not still_in_dead_list:
                self.report_battle_info(
                    f"账号{account_index} 尝试复活账号{target_dead_account_idx}的主角，但主角已不在全局阵亡记录中，跳过",
                    "warning",
                )
                return False

        # 使用复活药 - 在循环中查找道具按钮（超时1.5秒）
        item_btn = None
        start_time = time.time()
        while time.time() - start_time < 1.5:
            item_btn = self.find_image(account_index, self.button_images["道具按钮"], self.right_button_region, 0)
            if item_btn:
                break
            time.sleep(0.1)

        if not item_btn:
            self.report_battle_info(f"账号{account_index} 查找道具按钮超时（1.5秒）", "warning")
            return False

        # 找到道具按钮，开始执行复活操作，设置reviving=True
        with self._state_lock:
            if target_dead_account_idx in self.unit_info:
                char_info = self.unit_info[target_dead_account_idx]["main_char"]
                # 再次检查状态，确保还没有被其他线程复活
                if char_info.get("alive", False) or char_info.get("revive_pending_verification", False):
                    self.report_battle_info(
                        f"账号{account_index} 准备复活账号{target_dead_account_idx}的主角，但主角状态已改变，取消操作",
                        "warning",
                    )
                    return False
                # 检查是否还在全局阵亡记录中
                still_in_dead_list = False
                for dead_char in self.global_dead_units["main_chars"]:
                    if dead_char.get("account_index") == target_dead_account_idx:
                        still_in_dead_list = True
                        break
                if not still_in_dead_list:
                    self.report_battle_info(
                        f"账号{account_index} 准备复活账号{target_dead_account_idx}的主角，但主角已不在全局阵亡记录中，取消操作",
                        "warning",
                    )
                    return False
                # 所有检查通过，设置reviving=True（真正开始吃药）

                self.report_battle_info(
                    f"账号{account_index} 开始复活账号{target_dead_account_idx}的主角，设置reviving=True", "info"
                )

        self.click_position(account_index, item_btn.x, item_btn.y)
        time.sleep(0.1)

        # 查找复活药 - 在循环中查找复活药图片（超时3秒）
        revive_path = self.item_images.get("复活药")
        if not revive_path:
            # 清除复活中标记
            with self._state_lock:
                if target_dead_account_idx in self.unit_info:
                    char_info = self.unit_info[target_dead_account_idx]["main_char"]
                    char_info["reviving"] = False
            return False

        revive_pos = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            revive_pos = self.find_image(account_index, revive_path, self.item_panel_region, 0)
            if revive_pos:
                break
            time.sleep(0.1)

        if not revive_pos:
            # 清除复活中标记
            with self._state_lock:
                if target_dead_account_idx in self.unit_info:
                    char_info = self.unit_info[target_dead_account_idx]["main_char"]
                    char_info["reviving"] = False
            return False

        # 点击复活药，并验证是否点击成功（最多重试2次）
        max_retries = 2
        click_success = False
        for attempt in range(max_retries):
            # 点击复活药
            self.click_position(account_index, revive_pos.x, revive_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)

            # 验证复活药是否消失（点击成功）
            verify_pos = self.find_image(account_index, revive_path, self.item_panel_region, 0)
            if verify_pos is None:
                # 复活药已消失，点击成功
                click_success = True
                if attempt > 0:
                    self.report_battle_info(f"账号{account_index} 复活药点击成功（第{attempt + 1}次尝试）", "info")
                break
            else:
                # 复活药还在，需要重试
                if attempt < max_retries - 1:
                    self.report_battle_info(
                        f"账号{account_index} 复活药点击后未消失，进行第{attempt + 2}次点击", "warning"
                    )
                    revive_pos = verify_pos  # 更新位置（可能位置有变化）
                    time.sleep(0.2)  # 短暂延迟后重试
                else:
                    # 最后一次尝试也失败
                    self.report_battle_info(
                        f"账号{account_index} 复活药点击失败（已重试{max_retries - 1}次，复活药仍未消失）", "error"
                    )
                    # 清除复活中标记
                    with self._state_lock:
                        if target_dead_account_idx in self.unit_info:
                            char_info = self.unit_info[target_dead_account_idx]["main_char"]
                            char_info["reviving"] = False
                    return False

        if not click_success:
            # 清除复活中标记
            with self._state_lock:
                if target_dead_account_idx in self.unit_info:
                    char_info = self.unit_info[target_dead_account_idx]["main_char"]
                    char_info["reviving"] = False
            return False

        # 在指定账号的主角区域查找复活目标图片（fuhuohuo）
        # 大漠对象0对应中间，大漠对象1对应上面，大漠对象2对应下面
        search_region = None
        if target_dead_account_idx in self.account_main_char_regions:
            search_region = self.account_main_char_regions[target_dead_account_idx]
            self.report_battle_info(
                f"账号{account_index} 在账号{target_dead_account_idx}的主角区域查找复活目标", "info"
            )
        else:
            # 如果账号区域不存在，使用整个道具面板区域
            search_region = self.item_panel_region
            self.report_battle_info(
                f"账号{account_index} 账号{target_dead_account_idx}的区域不存在，使用整个道具面板区域", "warning"
            )

        # 在执行复活操作前，再次检查状态（确保还没有被其他线程复活）
        # with self._state_lock:
        #     if target_dead_account_idx in self.unit_info:
        #         char_info = self.unit_info[target_dead_account_idx]["main_char"]
        #         if (char_info.get("alive", False) or
        #             char_info.get("revive_pending_verification", False) or
        #             not char_info.get("reviving", False)):  # 如果没有复活中标记，说明被其他线程抢占了
        #             self.report_battle_info(f"账号{account_index} 在执行复活操作前，发现账号{target_dead_account_idx}的主角状态已变化，取消复活", "warning")
        #             # 清除复活中标记（如果存在）
        #             if char_info.get("reviving", False):
        #                 char_info["reviving"] = False
        #             return False

        #     still_in_dead_list = False
        #     for dead_char in self.global_dead_units["main_chars"]:
        #         if dead_char.get("account_index") == target_dead_account_idx:
        #             still_in_dead_list = True
        #             break

        #     if not still_in_dead_list:
        #         self.report_battle_info(f"账号{account_index} 在执行复活操作前，发现账号{target_dead_account_idx}的主角已不在全局阵亡记录中，取消复活", "warning")
        #         # 清除复活中标记
        #         if target_dead_account_idx in self.unit_info:
        #             char_info = self.unit_info[target_dead_account_idx]["main_char"]
        #             char_info["reviving"] = False
        #         return False

        # 使用复活药（在锁外执行操作，但状态更新在锁内）
        target_pos = self.find_target_text(account_index, search_region, timeout=3.0)

        if target_pos:
            # 找到后，将坐标 y+80 进行施法
            cast_x = target_pos.x
            cast_y = target_pos.y + 80
            self.click_position(account_index, cast_x, cast_y)
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(
                f"账号{account_index} 使用复活药复活账号{target_dead_account_idx}的主角，找到目标图片位置: ({target_pos.x}, {target_pos.y})，施法位置: ({cast_x}, {cast_y})",
                "action",
            )
            # 使用复活药后，立即更新状态为复活中（在锁内更新）
            self._update_revive_status(target_dead_account_idx)
            return True
        else:
            target_pos = self.find_target_text(account_index, self.item_panel_region, timeout=3.0)
            if target_pos:
                # 找到后，将坐标 y+80 进行施法
                cast_x = target_pos.x
                cast_y = target_pos.y + 80
                self.click_position(account_index, cast_x, cast_y)
                time.sleep(CombatConstants.ACTION_DELAY)
                self.report_battle_info(
                    f"账号{account_index} 使用复活药复活账号{target_dead_account_idx}的主角，找到目标图片位置: ({target_pos.x}, {target_pos.y})，施法位置: ({cast_x}, {cast_y})",
                    "action",
                )
                # 使用复活药后，立即更新状态为复活中（在锁内更新）
                self._update_revive_status(target_dead_account_idx)
                return True
            else:
                # 如果找不到目标图片，使用默认位置（根据被复活的主角账号索引）
                # 根据账号索引使用不同的默认位置
                default_main_char_positions = {
                    0: (793, 380),  # 大漠对象0主角默认位置（中间）
                    1: (764, 278),  # 大漠对象1主角默认位置（上面）
                    2: (825, 490),  # 大漠对象2主角默认位置（下面）
                }
                default_pos = default_main_char_positions.get(target_dead_account_idx, (793, 380))
                self.click_position(account_index, default_pos[0], default_pos[1])
                time.sleep(CombatConstants.ACTION_DELAY)
                self.report_battle_info(
                    f"账号{account_index} 使用复活药复活账号{target_dead_account_idx}的主角（未找到目标图片，使用默认位置: {default_pos}）",
                    "warning",
                )
                # 使用复活药后，立即更新状态为复活中（在锁内更新）
                self._update_revive_status(target_dead_account_idx)
                return True

    # 处理单个账号的完整操作流程（主角→第一个武将→第二个武将）
    def _handle_account_turn(self, account_index):
        """处理单个账号的完整操作流程（主角→第一个武将→第二个武将）
        每个账号独立处理，不需要等待其他账号
        :param account_index: 账号索引
        """
        try:
            # 第一步：识别操作类型（主角/武将）
            summon_btn = self.find_image(account_index, self.button_images["召唤按钮"], self.right_button_region, 0)

            if summon_btn:
                # 主角操作
                self.report_battle_info(f"主角操作阶段：账号 [{account_index}]", "turn")
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
                # 等待操作按钮出现（确保进入武将操作阶段）
                is_finded = False
                start_time = time.time()
                while time.time() - start_time < 3.0 and self.polling_running:
                    if self.check_action_button(account_index):
                        is_finded = True
                        break
                    time.sleep(0.05)
                if not is_finded:
                    return False
                # 进入第一个武将操作
                self.report_battle_info(f"武将操作阶段：账号 [{account_index}]", "turn")
                self._current_our_turn_call = 0
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False

                # 等待第二个武将操作
                is_finded = False
                start_time = time.time()
                while time.time() - start_time < 2.0:
                    if self.check_action_button(account_index):
                        is_finded = True
                        break
                    time.sleep(0.1)
                if not is_finded:
                    return False
                self._current_our_turn_call = 1
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
            else:
                # 武将操作
                self.report_battle_info(f"武将操作阶段：账号 [{account_index}]", "turn")
                self._current_our_turn_call = 0
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
                # 等待第二个武将操作
                time.sleep(0.03)
                self._current_our_turn_call = 1
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
                time.sleep(0.03)
                self._current_our_turn_call = 2
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False

            # 阶段1：切换点位 retry（每个剩余点位试3次，覆盖3个单位）
            while True:
                # 先检测操作面板是否仍存在
                wait_start = time.time()
                action_found = False
                while time.time() - wait_start < 1.0 and self.polling_running:
                    if self.check_action_button(account_index):
                        action_found = True
                        break
                    time.sleep(0.05)
                if not action_found:
                    return

                # 检查是否还有备选点位
                # retry的3次尝试覆盖账号内3个不同单位(主角/武将1/武将2)，可能同时涉及enemy和ally点位，
                # 无法预先确定该递增哪个，故两个都递增；各自独立检查是否耗尽
                enemy_can_advance = self.enemy_target_index + 1 < len(self.enemy_target_positions)
                ally_can_advance = self.ally_target_index + 1 < len(self.ally_target_positions)
                if not enemy_can_advance and not ally_can_advance:
                    break
                if enemy_can_advance:
                    self.enemy_target_index += 1
                if ally_can_advance:
                    self.ally_target_index += 1
                _enemy_pos = self.enemy_target_positions[self.enemy_target_index] if enemy_can_advance else None
                _ally_pos = self.ally_target_positions[self.ally_target_index] if ally_can_advance else None

                self.report_battle_info(
                    f"账号{account_index} 操作面板仍存在，切换到备选点位[敌军={_enemy_pos}, 我方={_ally_pos}]", "warning"
                )

                # 该点位试3次，覆盖3个单位
                for attempt in range(3):
                    wait_start = time.time()
                    action_found = False
                    while time.time() - wait_start < 1.0 and self.polling_running:
                        if self.check_action_button(account_index):
                            action_found = True
                            break
                        time.sleep(0.05)
                    if not action_found:
                        return
                    self.handle_our_turn(account_index, skip_side_effects=True)

            # 阶段2：点位耗尽后，使用重复按钮 retry（3次，重复上回合操作）
            self.report_battle_info(
                f"账号{account_index} 点位已耗尽，使用重复按钮重试", "warning"
            )
            for attempt in range(3):
                wait_start = time.time()
                chongfu_btn = None
                while time.time() - wait_start < 1.0 and self.polling_running:
                    chongfu_btn = self.find_image(
                        account_index, self.button_images["重复按钮"], self.right_button_region, 0
                    )
                    if chongfu_btn:
                        break
                    time.sleep(0.05)
                if not chongfu_btn:
                    return
                self.click_position(account_index, chongfu_btn.x, chongfu_btn.y)
                self.report_battle_info(
                    f"账号{account_index} 点击重复按钮(第{attempt+1}次)，重复上回合操作", "action"
                )
                time.sleep(0.5)

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 处理操作流程出错: {e}", "error")

    # 处理我方回合操作
    def handle_our_turn(self, account_index, skip_side_effects=False):
        """处理我方回合的操作（重构版）
        操作顺序：
        1. 判断是否需要刘备
        2. 判断是否需要召唤其他武将
        3. 判断是否需要复活主角
        4. 技能操作（简化流程：循环查找召唤按钮、攻击技能、刘备控制技能）
        5. 加血操作
        6. 防御
        """
        try:
            turn_start_time = time.time()
            turn_timeout = CombatConstants.TURN_TIMEOUT  # 25秒超时

            # 清理generals列表中的幽灵条目
            # 幽灵条目: alive=False且非replacing且非reviving
            # 注意: 不对同名武将去重, 游戏允许同名武将同时在场(如两个曹操在不同槽位)
            with self._state_lock:
                char_info_clean = self.unit_info[account_index]["main_char"]
                generals_list = char_info_clean.get("generals", [])
                if generals_list:
                    # 移除幽灵条目: alive=False且非replacing且非reviving
                    cleaned = [g for g in generals_list
                               if g.get("alive", True) or g.get("reviving", False) or g.get("replacing", False)]
                    if len(cleaned) != len(generals_list):
                        char_info_clean["generals"] = cleaned

            # 预替换检查：场上所有免死武将count>=4时, 按轮转账号踢旧召新
            # 轮转规则: proactive_replace_account依次0→1→2→0, 每次只有匹配的账号执行替换
            # 有replacing武将时跳过(等确认结果)
            if self.need_proactive_replace and not skip_side_effects:
                has_own_replacing = False
                char_info_check = self.unit_info[account_index]["main_char"]
                for g in char_info_check.get("generals", []):
                    if g.get("replacing", False):
                        has_own_replacing = True
                        break
                my_turn = False
                if not has_own_replacing:
                    # 跳过背包中无可用武将的账号，避免浪费预替换轮转
                    if not self.has_general.get(account_index, False):
                        if self.need_proactive_replace and account_index == self.proactive_replace_account:
                            with self._state_lock:
                                self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                    else:
                        with self._state_lock:
                            if (self.need_proactive_replace
                                and not self._proactive_replace_in_progress
                                and account_index == self.proactive_replace_account):
                                self._proactive_replace_in_progress = True
                                my_turn = True
                if my_turn:
                    char_info = self.unit_info[account_index]["main_char"]
                    if not char_info.get("alive", True):
                        with self._state_lock:
                            self._proactive_replace_in_progress = False
                            self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                        self.report_battle_info(
                            f"账号{account_index} 预替换跳过(主角阵亡), 下次替换账号{self.proactive_replace_account}", "action")
                    else:
                        replace_pos = self._find_best_replace_position(account_index)
                        if replace_pos is None:
                            with self._state_lock:
                                self._proactive_replace_in_progress = False
                                self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                            self.report_battle_info(
                                f"账号{account_index} 预替换跳过(无可替换位置), 下次替换账号{self.proactive_replace_account}", "action")
                        else:
                            # 查找免死耗尽最严重的武将
                            worst_key = None
                            worst_count = -1
                            for key, count in self.ally_undead_rounds.items():
                                if key[0] != account_index:
                                    continue
                                if count > worst_count:
                                    worst_count = count
                                    worst_key = key
                            if worst_key:
                                summon_name = self._get_general_name_by_region(account_index, worst_key[1])
                            else:
                                summon_name = None
                            # summon_name为None时(本账号无免死记录或武将已阵亡), 跳过预替换
                            if summon_name is None:
                                # 只有主角操作才有意义推进，武将操作保持等待主角Call
                                _find_start = time.time()
                                _btn = None
                                while time.time() - _find_start < 0.5 and not _btn:
                                    _btn = self.find_image(account_index, self.button_images["召唤按钮"],
                                                            self.right_button_region, 0)
                                    if _btn:
                                        break
                                    time.sleep(0.005)
                                if _btn:
                                    with self._state_lock:
                                        self._proactive_replace_in_progress = False
                                        self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                                    self.report_battle_info(
                                        f"账号{account_index} 预替换跳过(无可替换武将), 下次替换账号{self.proactive_replace_account}", "info")
                                else:
                                    with self._state_lock:
                                        self._proactive_replace_in_progress = False
                            else:
                                # 仅主角操作有召唤按钮，非主角阶段不推进，保持当前proactive等主角Call
                                _find_start = time.time()
                                summon_btn = None
                                while time.time() - _find_start < 0.5 and not summon_btn:
                                    summon_btn = self.find_image(account_index, self.button_images["召唤按钮"],
                                                                  self.right_button_region, 0)
                                    if summon_btn:
                                        break
                                    time.sleep(0.005)
                                if not summon_btn:
                                    with self._state_lock:
                                        self._proactive_replace_in_progress = False
                                elif self.summon_general_with_verification(
                                    account_index, summon_name, force_replace=True,
                                    replace_position=replace_pos):
                                    self.report_battle_info(
                                        f"账号{account_index} 预替换{summon_name}操作完成, 等待验证确认", "action")
                                    return True
                                else:
                                    with self._state_lock:
                                        self._proactive_replace_in_progress = False
                                        self.proactive_replace_account = (self.proactive_replace_account + 1) % 3
                                    self.report_battle_info(
                                        f"账号{account_index} 预替换{summon_name}操作失败, "
                                        f"下次替换账号{self.proactive_replace_account}", "warning")

            # 确保技能面板已打开（重试查找并点击技能按钮，避免一次识别失败）
            find_jineng_time = time.time()
            skill_btn = None
            while time.time() - find_jineng_time < 1.0 and not skill_btn:
                skill_btn = self.find_image(
                    account_index, self.button_images["技能按钮"], self.right_button_region, 0
                )
                if skill_btn:
                    break
                time.sleep(0.005)
            if skill_btn:
                self.click_position(account_index, skill_btn.x, skill_btn.y)
                time.sleep(0.2)

            # 检查是否有分配到的复活任务
            # 复活任务在我方回合开始时已统一分配，这里只需要检查当前账号是否有任务
            assigned_revive_target = self.revive_assignments.get(account_index)

            # 4. 识别单位类型并执行相应操作
            unit_type, detected_skill = self.identify_unit_type(account_index, timeout=3.0)

            if unit_type == "main_char":
                # 主角操作
                # 识别到主角操作，说明该主角存活，确认复活成功（如果有待验证的复活）
                self._confirm_revive_success(account_index)
                # === 召唤判断（仅主角操作执行） ===
                char_info = self.unit_info[account_index]["main_char"]
                need_liubei = False
                need_summon_general = False
                need_self_liubei = False
                is_first_turn = self.current_turn == 0 or self.current_turn == 1

                if not is_first_turn and not skip_side_effects:
                    has_dead_general_in_account = False
                    with self._state_lock:
                        for dead_gen in self.global_dead_units["generals"]:
                            if dead_gen.get("account_index") == account_index:
                                has_dead_general_in_account = True
                                break

                    has_dead_general_in_list = False
                    for gen_info in char_info.get("generals", []):
                        if not gen_info.get("alive", True) and not gen_info.get("replacing", False):
                            has_dead_general_in_list = True
                            break

                    alive_generals_count = 0
                    for gen_info in char_info.get("generals", []):
                        if gen_info.get("alive", True) and not gen_info.get("replacing", False) and not gen_info.get("pending_kick", False):
                            alive_generals_count += 1

                    has_replacing_general = any(
                        g.get("replacing", False)
                        for g in char_info.get("generals", [])
                    )
                    in_cooldown = (account_index in self.replace_fail_cooldown
                                   and self.current_turn <= self.replace_fail_cooldown[account_index])
                    if char_info.get("alive", True):
                        need_summon = (has_dead_general_in_list or alive_generals_count < 2) and not has_replacing_general and not in_cooldown
                    else:
                        need_summon = False

                    if need_summon:
                        with self._state_lock:
                            field_liubei_count_for_summon = 0
                            for _acct in range(self.get_account_count()):
                                if _acct not in self.unit_info:
                                    continue
                                for _g in self.unit_info[_acct]["main_char"].get("generals", []):
                                    if (_g.get("name") == "刘备" and _g.get("alive", True)
                                        and not _g.get("replacing", False) and not _g.get("pending_kick", False)):
                                        field_liubei_count_for_summon += 1
                            summoning_count_for_summon = sum(
                                1 for _v in self._liubei_summon_in_progress.values() if _v
                            )
                            field_has_liubei = (field_liubei_count_for_summon + summoning_count_for_summon) > 0
                            if (not field_has_liubei and self.keep_support_general
                                    and self.has_liubei.get(account_index, False)
                                    and self.has_general.get(account_index, False)
                                    and not self._liubei_summon_in_progress.get(account_index, False)):
                                self._liubei_summon_in_progress[account_index] = True

                        has_liubei_in_account = False
                        for gen_info in char_info.get("generals", []):
                            if (gen_info.get("name") == "刘备" and gen_info.get("alive", True)
                                and not gen_info.get("replacing", False) and not gen_info.get("pending_kick", False)):
                                has_liubei_in_account = True
                                break

                        if not field_has_liubei and not has_liubei_in_account and self.keep_support_general:
                            need_liubei = True
                            need_summon_general = True
                            self.report_battle_info(
                                f"账号{account_index} 判断需要召唤刘备（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 场上无刘备={not field_has_liubei}, 账号无刘备={not has_liubei_in_account}, 背包有刘备={self.has_liubei.get(account_index, False)}, 主角存活={char_info.get('alive', True)}）",
                                "info",
                            )
                        else:
                            need_summon_general = True
                            self.report_battle_info(
                                f"账号{account_index} 判断需要召唤其他武将（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 场上有刘备={field_has_liubei}, 账号有刘备={has_liubei_in_account}, 主角存活={char_info.get('alive', True)}）",
                                "info",
                            )
                    else:
                        self.report_battle_info(
                            f"账号{account_index} 判断不需要召唤（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 主角存活={char_info.get('alive', True)}）",
                            "info",
                        )
                else:
                    if skip_side_effects:
                        self.report_battle_info(f"账号{account_index} [retry] 跳过召唤判断（skip_side_effects）", "info")
                    else:
                        self.report_battle_info(f"账号{account_index} 第一回合，跳过召唤判断", "info")

                # 多刘备并行
                if not skip_side_effects:
                  with self._state_lock:
                    has_liubei_in_account_for_clear = False
                    for gen_info in char_info.get("generals", []):
                        if (gen_info.get("name") == "刘备" and gen_info.get("alive", True)
                            and not gen_info.get("replacing", False) and not gen_info.get("pending_kick", False)):
                            if self._get_liubei_clear_cd_remaining(account_index) > 2:
                                continue
                            has_liubei_in_account_for_clear = True
                            break

                    unclaimed_count = sum(1 for e in self.global_enemies_need_clear if e.get("claimed_by") is None)

                    field_liubei_count = 0
                    claimed_liubei_count = 0
                    for i in range(self.get_account_count()):
                        if i not in self.unit_info:
                            continue
                        for g in self.unit_info[i].get("main_char", {}).get("generals", []):
                            if (g.get("name") == "刘备" and g.get("alive", True)
                                and not g.get("replacing", False) and not g.get("pending_kick", False)):
                                if self._get_liubei_clear_cd_remaining(i) > 2:
                                    continue
                                field_liubei_count += 1
                                if any(e.get("claimed_by") == i for e in self.global_enemies_need_clear):
                                    claimed_liubei_count += 1

                    effective_available = field_liubei_count - claimed_liubei_count
                    summoning_count = sum(1 for v in self._liubei_summon_in_progress.values() if v)
                    need_summon_count = unclaimed_count - effective_available - summoning_count

                    snake_unclaimed = sum(
                        1 for e in self.global_enemies_need_clear
                        if e.get("claimed_by") is None and e.get("enemy_name") == "蛇"
                    )
                    if snake_unclaimed > 0:
                        field_any_liubei = any(
                            g.get("name") == "刘备" and g.get("alive", True)
                            and not g.get("replacing", False) and not g.get("pending_kick", False)
                            for i in range(self.get_account_count())
                            for g in self.unit_info[i].get("main_char", {}).get("generals", [])
                        )
                        if field_any_liubei:
                            need_summon_count -= snake_unclaimed
                            need_summon_count = max(0, need_summon_count)

                    self.report_battle_info(
                        f"账号{account_index} 多刘备并行: need_cnt={need_summon_count} "
                        f"unclaimed={unclaimed_count} field_lb={field_liubei_count} "
                        f"avail={effective_available} summoning={summoning_count} "
                        f"no_own_lb={not has_liubei_in_account_for_clear} "
                        f"alive={char_info.get('alive', True)} "
                        f"has_lb={self.has_liubei.get(account_index)} "
                        f"has_gen={self.has_general.get(account_index)} "
                        f"in_progress={self._liubei_summon_in_progress}",
                        "info",
                    )
                    if (need_summon_count > 0
                        and not has_liubei_in_account_for_clear
                        and char_info.get("alive", True)
                        and self.has_liubei.get(account_index, False)
                        and self.has_general.get(account_index, False)):
                        if not self._liubei_summon_in_progress.get(account_index, False):
                            self._liubei_summon_in_progress[account_index] = True
                            need_self_liubei = True
                            if not self.keep_support_general:
                                self.keep_support_general = True

                    any_account_has_liubei = field_liubei_count > 0 or summoning_count > 0
                    if (not need_self_liubei
                        and (self.keep_support_general or self._zhugeliang_low_hp)
                        and self.global_enemies_need_clear
                        and not any_account_has_liubei
                        and not has_liubei_in_account_for_clear
                        and char_info.get("alive", True)
                        and self.has_liubei.get(account_index, False)
                        and self.has_general.get(account_index, False)):
                        if not self._liubei_summon_in_progress.get(account_index, False):
                            self._liubei_summon_in_progress[account_index] = True
                            need_self_liubei = True
                # === 召唤判断结束 ===

                # 可以加一个开关，如果需要清除状态，开关打开，召唤刘备 通过zhaohuan_index去控制召唤账号
                # (self.beidong_huihe >= 5 and self.zhaohuan_index == account_index) 刘备没免死了
                # need_liubei 场上没有刘备
                # 另外一个需要召唤的条件：
                # self.has_liubei.get(account_index, False)
                #  and (time.time() - turn_start_time) < turn_timeout
                #  and self.has_general[account_index]
                # and self.keep_support_general == False
                # and self.enemies_need_clear[account_index][account_index] and self.enemies_need_clear[account_index][account_index].has_zhaohuan==False
                # 4.1 召唤刘备（如果需要）
                if ( self.has_liubei.get(account_index, False)
                    and (time.time() - turn_start_time) < turn_timeout
                    and self.has_general[account_index]
                    and (need_liubei
                        or (self.keep_support_general and need_self_liubei))
                    and not skip_side_effects
                ):
                    self.report_battle_info(
                        f"账号{account_index} 多刘备触发召唤: need_liubei={need_liubei} "
                        f"need_self_liubei={need_self_liubei} "
                        f"keep_support={self.keep_support_general}",
                        "info",
                    )
                    # 需要force_replace时, 用_find_best_replace_position选择被踢武将
                    # 该方法会跳过张星彩, 选择count最高的武将位置
                    replace_pos = None
                    if need_self_liubei:
                        replace_pos = self._find_best_replace_position(account_index)
                    if self.summon_general_with_verification(account_index, "刘备", force_replace=need_self_liubei, replace_position=replace_pos):
                        time.sleep(0.1)
                        return True
                    # 召唤失败不设has_liubei=False/liubei_remaining=0，武将回到背包，下回合可重试
                    self._liubei_summon_in_progress[account_index] = False
                    # 确保技能面板已打开（点击技能按钮）
                    find_jineng_time = time.time()
                    skill_btn = None
                    while time.time() - find_jineng_time < 2.0 and not skill_btn:
                        skill_btn = self.find_image(
                            account_index, self.button_images["技能按钮"], self.right_button_region, 0
                        )
                        if skill_btn:
                            break
                        time.sleep(0.005)
                    if skill_btn:
                        self.click_position(account_index, skill_btn.x, skill_btn.y)
                        time.sleep(0.1)

                # 4.2 召唤其他武将（如果需要）
                if (
                    need_summon_general
                    and time.time() - turn_start_time < turn_timeout
                    and self.has_general[account_index]
                    and not skip_side_effects
                ):
                    general_order = ["曹操", "魔化关羽", "张星彩", "刘备"]
                    _summon_not_found_count = 0
                    for general_name in general_order:
                        _summon_result = self.summon_general_with_verification(account_index, general_name)
                        if _summon_result:
                            # ally_undead_rounds更新延迟到_track_ally_undead确认成功后
                            time.sleep(0.1)
                            return True
                        else:
                            self.click_position(account_index, 12, 12)
                            _summon_not_found_count += 1
                    if _summon_not_found_count == len(general_order):
                        self.has_general[account_index] = False
                        self.report_battle_info(
                            f"账号{account_index} 背包已无可用武将（{len(general_order)}个武将均召唤失败），本战斗不再尝试召唤",
                            "warning",
                        )
                elif need_summon_general:
                    # 确保技能面板已打开（点击技能按钮）
                    find_jineng_time = time.time()
                    skill_btn = None
                    while time.time() - find_jineng_time < 2.0 and not skill_btn:
                        skill_btn = self.find_image(
                            account_index, self.button_images["技能按钮"], self.right_button_region, 0
                        )
                        if skill_btn:
                            break
                        time.sleep(0.005)
                    if skill_btn:
                        self.click_position(account_index, skill_btn.x, skill_btn.y)
                        time.sleep(0.1)

                # 4.3 执行分配的复活任务（如果当前账号有分配任务）
                if assigned_revive_target is not None and time.time() - turn_start_time < turn_timeout and not skip_side_effects:
                    if self._check_and_mark_reviving(assigned_revive_target, "主角"):
                        if self.revive_main_char_with_target(account_index, assigned_revive_target):
                            # 复活任务完成，从分配列表中移除
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]
                            time.sleep(0.1)
                            return True
                        else:
                            # 复活失败，清除reviving标记
                            with self._state_lock:
                                if assigned_revive_target in self.unit_info:
                                    char_info = self.unit_info[assigned_revive_target]["main_char"]
                                    if char_info.get("reviving", False):
                                        char_info["reviving"] = False
                                        self.report_battle_info(
                                            f"账号{account_index} 复活账号{assigned_revive_target}的主角失败，清除reviving标记",
                                            "warning",
                                        )
                            # 从分配列表中移除，允许重新分配
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]

                # 4.4 释放主角技能（策略引擎）
                if self._execute_best_strategy(account_index, "main_char"):
                    return True

                # 4.5 蓝耗尽检测（仅四象模式）
                if self.combat_scene == "四象" and self._detect_gray_and_recover(account_index):
                    return True

                # 4.6 主角没技能时，尝试用恢复药给低血单位加血（四象模式禁用）
                _heal_enabled = getattr(self, 'enable_main_heal', False)
                _low_hp_for_acct = self.low_hp_units.get(account_index, [])
                if _heal_enabled and self.combat_scene != "四象" and self._try_use_heal_for_low_hp(account_index):
                    return True

                # 4.6 防御（策略引擎已包含防御兜底，此处保底兼容）
                defense_btn = self.find_image(
                    account_index, self.button_images.get("防御按钮"), self.right_button_region, 0
                )
                if defense_btn:
                    self.click_position(account_index, defense_btn.x, defense_btn.y)
                    self.report_battle_info(f"账号{account_index} 主角执行防御", "action")
                    time.sleep(CombatConstants.ACTION_DELAY)
                    return True

            elif unit_type == "attack":
                # 攻击武将操作
                # 识别武将并添加到列表（如果不在列表中）
                char_info = self.unit_info[account_index]["main_char"]
                general_name = self.SKILL_TO_GENERAL.get(detected_skill, detected_skill) if detected_skill else "攻击武将"
                generals = char_info.get("generals", [])
                if self.current_turn <= 1:
                    found_general = len(generals) >= 2
                else:
                    found_general = any(g.get("name") == general_name for g in generals)

                if not found_general:
                    # 武将不在列表中，添加到列表（可能是第一回合初始武将或召唤后检测到蓝条）
                    # 根据账号索引确定武将位置: 检查已有武将position判断空位, 避免position重叠
                    _existing_positions = [g.get("position") for g in char_info.get("generals", []) if g.get("position")]
                    _slot1 = self.unit_positions[account_index]["generals"][0][1:]
                    _slot2 = self.unit_positions[account_index]["generals"][1][1:]
                    _slot1_occupied = any(abs(p[0]-_slot1[0]) < 50 and abs(p[1]-_slot1[1]) < 50 for p in _existing_positions)
                    general_position = _slot2 if _slot1_occupied else _slot1

                    new_general = {
                        "name": general_name,
                        "position": general_position,
                        "alive": True,
                        "reviving": False,
                        "deployed_turn": self.current_turn,
                        "account_index": account_index,
                    }
                    if "generals" not in char_info:
                        char_info["generals"] = []
                    char_info["generals"].append(new_general)
                    # 武将通过技能识别被动添加(非召唤流程), 需清理global_dead_units中该账号同名死亡记录
                    # 否则has_dead_general_in_account永久为True, 导致每回合重复召唤
                    with self._state_lock:
                        for dead_gen in self.global_dead_units["generals"][:]:
                            if (dead_gen.get("account_index") == account_index
                                    and dead_gen.get("name") == general_name):
                                self.global_dead_units["generals"].remove(dead_gen)
                                break
                else:
                    # 武将已在列表中，检查是否正在复活中或替换中
                    # 优先找replacing的武将（避免pending_kick旧武将干扰确认）
                    target_gen = None
                    for gen_info in char_info.get("generals", []):
                        if gen_info.get("name") == general_name:
                            if gen_info.get("replacing", False):
                                target_gen = gen_info
                                break
                            elif gen_info.get("reviving", False) and target_gen is None:
                                target_gen = gen_info
                    # 没有replacing/reviving的，找第一个普通同名的
                    if target_gen is None:
                        for gen_info in char_info.get("generals", []):
                            if gen_info.get("name") == general_name:
                                target_gen = gen_info
                                break
                    if target_gen is not None:
                        gen_info = target_gen
                        if gen_info.get("replacing", False):
                            # 检测到技能, 替换确认成功
                            gen_info["replacing"] = False
                            gen_info["alive"] = True
                            # 移除旧武将(pending_kick)
                            char_info["generals"][:] = [
                                g for g in char_info["generals"]
                                if not g.get("pending_kick", False)
                            ]
                            # 更新免死计数
                            region_idx_for_undead = self._find_region_by_position(account_index, gen_info.get("position"))
                            if region_idx_for_undead is not None:
                                self.ally_undead_rounds[(account_index, region_idx_for_undead)] = 0
                                self.ally_undead_last_increment_turn[(account_index, region_idx_for_undead)] = -1
                            # 清理global_dead_units
                            _gen_name_for_clean = gen_info.get("name")
                            _gen_position_for_clean = gen_info.get("position")
                            with self._state_lock:
                                for dead_gen in self.global_dead_units["generals"][:]:
                                    if dead_gen.get("account_index") == account_index:
                                        if (dead_gen.get("name") == _gen_name_for_clean) or (
                                            _gen_position_for_clean and dead_gen.get("position") == _gen_position_for_clean):
                                            self.global_dead_units["generals"].remove(dead_gen)
                                            break
                            if general_name == "刘备":
                                self.liubei_skill_cd[account_index] = {}
                            # 注意: has_liubei/has_general不在此处更新
                            # 它们表示背包里是否还有对应武将, 只有召唤操作失败时才设为False
                            self.need_proactive_replace = False
                            self._proactive_replace_in_progress = False
                            if general_name == "刘备":
                                self._liubei_summon_in_progress[account_index] = False
                            self._last_kicked_info = None
                            self.report_battle_info(
                                f"账号{account_index} 武将{general_name}替换验证成功（识别到技能）", "success"
                            )
                        elif gen_info.get("reviving", False):
                            # 检测到蓝条（识别到技能），确认复活成功
                            gen_info["alive"] = True
                            gen_info["reviving"] = False

                            # 从global_dead_units中移除对应记录
                            gen_name = gen_info.get("name")
                            gen_position = gen_info.get("position")
                            with self._state_lock:
                                for dead_gen in self.global_dead_units["generals"][:]:
                                    if dead_gen.get("account_index") == account_index:
                                        # 优先使用name匹配，如果name不一致则使用position匹配
                                        if (dead_gen.get("name") == gen_name) or (
                                            gen_position and dead_gen.get("position") == gen_position
                                        ):
                                            self.global_dead_units["generals"].remove(dead_gen)
                                            break

                            self.report_battle_info(
                                f"账号{account_index} 武将{general_name}复活成功（识别到技能）", "success"
                            )

                # 4.1 执行分配的复活任务（如果当前账号有分配任务）
                if assigned_revive_target is not None and time.time() - turn_start_time < turn_timeout:
                    if self._check_and_mark_reviving(assigned_revive_target, "主角"):
                        if self.revive_main_char_with_target(account_index, assigned_revive_target):
                            # 复活任务完成，从分配列表中移除
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]
                            time.sleep(0.1)
                            return True
                        else:
                            # 复活失败，清除reviving标记
                            with self._state_lock:
                                if assigned_revive_target in self.unit_info:
                                    char_info = self.unit_info[assigned_revive_target]["main_char"]
                                    if char_info.get("reviving", False):
                                        char_info["reviving"] = False
                                        self.report_battle_info(
                                            f"账号{account_index} 复活账号{assigned_revive_target}的主角失败，清除reviving标记",
                                            "warning",
                                        )
                            # 从分配列表中移除，允许重新分配
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]

                # 4.2 释放攻击技能（策略引擎）
                if self._execute_best_strategy(account_index, "attack"):
                    return True

            elif unit_type == "support":
                # 刘备操作
                # 修改点8: 检查清除技能是否可用（技能图标可见说明不在CD中）
                clear_skill_pos = self.find_image(account_index, self.skill_images.get("清除状态"), self.skill_panel_region, 0)
                if clear_skill_pos:
                    cd_remaining_check = self._get_liubei_clear_cd_remaining(account_index)
                    if cd_remaining_check > 0:
                        if account_index in self.liubei_skill_cd:
                            self.liubei_skill_cd[account_index].pop("清除状态", None)
                        self.report_battle_info(
                            f"账号{account_index} 清除技能可用但CD记录错误，已重置为0",
                            "warning"
                        )
                # 修改点7: Part2 - 检查上回合清除是否失败
                if account_index in self._last_clear_attempt:
                    last = self._last_clear_attempt[account_index]
                    if self.current_turn - last["turn"] <= 2:
                        enemy_still_in_queue = any(
                            e.get("enemy_name") == last["enemy_name"]
                            for e in self.global_enemies_need_clear
                        )
                        if enemy_still_in_queue:
                            if account_index in self.liubei_skill_cd:
                                self.liubei_skill_cd[account_index].pop("清除状态", None)
                            self.report_battle_info(
                                f"账号{account_index} 确认清除{last['enemy_name']}失败，CD重置为0",
                                "warning"
                            )
                    self._last_clear_attempt.pop(account_index, None)
                # 认领清除任务
                claimed_target = None
                cd_remaining = self._get_liubei_clear_cd_remaining(account_index)
                if cd_remaining <= 2:
                    # 如果其他账号有CD更短的刘备，让位
                    should_defer = False
                    if cd_remaining > 0:
                        for i in range(self.get_account_count()):
                            if i == account_index:
                                continue
                            if i not in self.unit_info:
                                continue
                            other_cd = self._get_liubei_clear_cd_remaining(i)
                            if other_cd < cd_remaining:
                                char_i = self.unit_info[i]["main_char"]
                                has_lb = any(
                                    g.get("name") == "刘备" and g.get("alive", True)
                                    and not g.get("replacing", False) and not g.get("pending_kick", False)
                                    for g in char_i.get("generals", [])
                                )
                                if has_lb:
                                    should_defer = True
                                    break
                    if not should_defer:
                        with self._state_lock:
                            for e in self.global_enemies_need_clear:
                                if e.get("claimed_by") is None and e.get("enemy_name") == "诸葛亮":
                                    claimed_target = e
                                    break
                            if claimed_target is None:
                                for e in self.global_enemies_need_clear:
                                    if e.get("claimed_by") is None:
                                        claimed_target = e
                                        break
                            if claimed_target is not None:
                                claimed_target["claimed_by"] = account_index
                self._claimed_clear_target[account_index] = claimed_target

                # 识别刘备并添加到列表（如果不在列表中）
                char_info = self.unit_info[account_index]["main_char"]
                # 检查刘备是否已在列表中
                found_liubei = False
                replacing_liubei = None
                for gen_info in char_info.get("generals", []):
                    if gen_info.get("name") == "刘备":
                        found_liubei = True
                        if gen_info.get("replacing", False):
                            replacing_liubei = gen_info
                        break

                # support分支识别到刘备技能, 说明已上场, 确认replacing→alive
                # 避免验证图片识别失败导致超时回退已上场的武将
                if replacing_liubei is not None:
                    replacing_liubei["replacing"] = False
                    replacing_liubei["alive"] = True
                    # 移除旧武将(pending_kick)
                    char_info["generals"][:] = [
                        g for g in char_info["generals"]
                        if not g.get("pending_kick", False)
                    ]
                    # 更新免死计数
                    _region_idx_lb = self._find_region_by_position(account_index, replacing_liubei.get("position"))
                    if _region_idx_lb is not None:
                        self.ally_undead_rounds[(account_index, _region_idx_lb)] = 0
                        self.ally_undead_last_increment_turn[(account_index, _region_idx_lb)] = -1
                    # 清理global_dead_units中该账号的刘备死亡记录
                    with self._state_lock:
                        for dead_gen in self.global_dead_units["generals"][:]:
                            if dead_gen.get("account_index") == account_index:
                                if dead_gen.get("name") == "刘备" or dead_gen.get("position") == replacing_liubei.get("position"):
                                    self.global_dead_units["generals"].remove(dead_gen)
                                    break
                    self._liubei_summon_in_progress[account_index] = False
                    self._last_clear_attempt.pop(account_index, None)
                    self.need_proactive_replace = False
                    self._proactive_replace_in_progress = False
                    if not replacing_liubei.get("_lb_counted", False):
                        replacing_liubei["_lb_counted"] = True
                        if self.liubei_remaining.get(account_index, 0) > 0:
                            self.liubei_remaining[account_index] -= 1
                        self.has_liubei[account_index] = self.liubei_remaining.get(account_index, 0) > 0
                    self._last_kicked_info = None
                    self.replace_fail_count[account_index] = 0
                    if account_index in self.replace_fail_cooldown:
                        del self.replace_fail_cooldown[account_index]
                    self.report_battle_info(
                        f"账号{account_index} 刘备替换确认成功(support识别到技能)", "success")

                if not found_liubei:
                    # 刘备不在列表中，添加到列表
                    # 根据账号索引确定刘备位置: 检查已有武将position判断空位, 避免position重叠
                    _existing_positions = [g.get("position") for g in char_info.get("generals", []) if g.get("position")]
                    _slot1 = self.unit_positions[account_index]["generals"][0][1:]
                    _slot2 = self.unit_positions[account_index]["generals"][1][1:]
                    _slot1_occupied = any(abs(p[0]-_slot1[0]) < 50 and abs(p[1]-_slot1[1]) < 50 for p in _existing_positions)
                    liubei_position = _slot2 if _slot1_occupied else _slot1

                    new_general = {
                        "name": "刘备",
                        "position": liubei_position,
                        "alive": True,
                        "deployed_turn": self.current_turn,
                        "account_index": account_index,
                        "_lb_counted": True,
                    }
                    if "generals" not in char_info:
                        char_info["generals"] = []
                    char_info["generals"].append(new_general)
                    # 武将通过技能识别被动添加(非召唤流程), 需清理global_dead_units中该账号同名死亡记录
                    # 否则has_dead_general_in_account永久为True, 导致每回合重复召唤
                    with self._state_lock:
                        for dead_gen in self.global_dead_units["generals"][:]:
                            if (dead_gen.get("account_index") == account_index
                                    and dead_gen.get("name") == "刘备"):
                                self.global_dead_units["generals"].remove(dead_gen)
                                break
                    if self.liubei_remaining.get(account_index, 0) > 0:
                        self.liubei_remaining[account_index] -= 1
                    self.has_liubei[account_index] = self.liubei_remaining.get(account_index, 0) > 0

                # 4.1 执行分配的复活任务（如果当前账号有分配任务）
                if assigned_revive_target is not None and time.time() - turn_start_time < turn_timeout and not skip_side_effects:
                    if self._check_and_mark_reviving(assigned_revive_target, "主角"):
                        if self.revive_main_char_with_target(account_index, assigned_revive_target):
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]
                            time.sleep(0.5)
                            return True
                        else:
                            with self._state_lock:
                                if assigned_revive_target in self.unit_info:
                                    char_info = self.unit_info[assigned_revive_target]["main_char"]
                                    if char_info.get("reviving", False):
                                        char_info["reviving"] = False
                                        self.report_battle_info(
                                            f"账号{account_index} 复活账号{assigned_revive_target}的主角失败，清除reviving标记",
                                            "warning",
                                        )
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]

                # 4.2 释放技能（策略引擎：清除状态 > 加血(重伤) > 控制 > 加攻击(buff过期) > 加血 > 循环 > 防御）
                _claimed_before = self._claimed_clear_target.get(account_index)
                if self._execute_best_strategy(account_index, "support"):
                    # 清除状态成功时 _claimed_clear_target 会被设为 None（release_skill_with_target中L1408）
                    # 若仍不为None，说明降级释放了其他技能(加血/控制)，认领未消耗，需立即释放让其他账号接手
                    if _claimed_before is not None and self._claimed_clear_target.get(account_index) is not None:
                        with self._state_lock:
                            if _claimed_before.get("claimed_by") == account_index:
                                _claimed_before["claimed_by"] = None
                        self._claimed_clear_target[account_index] = None
                    return True
                 # 安全释放认领：如果认领了但没清除，释放认领（CD没好时保留认领，下回合再试）
                if self._claimed_clear_target.get(account_index) is not None:
                    _cd_rem = self._get_liubei_clear_cd_remaining(account_index)
                    if _cd_rem <= 0:
                        with self._state_lock:
                            target = self._claimed_clear_target[account_index]
                            if target.get("claimed_by") == account_index:
                                target["claimed_by"] = None
                        self._claimed_clear_target[account_index] = None

            elif unit_type == "xingcai_support":
                # 张星彩操作（第一回合辅助，后续群攻）
                char_info = self.unit_info[account_index]["main_char"]
                found_xingcai = any(g.get("name") == "张星彩" for g in char_info.get("generals", []))

                if not found_xingcai:
                    _existing_positions = [g.get("position") for g in char_info.get("generals", []) if g.get("position")]
                    _slot1 = self.unit_positions[account_index]["generals"][0][1:]
                    _slot2 = self.unit_positions[account_index]["generals"][1][1:]
                    _slot1_occupied = any(abs(p[0]-_slot1[0]) < 50 and abs(p[1]-_slot1[1]) < 50 for p in _existing_positions)
                    xingcai_position = _slot2 if _slot1_occupied else _slot1

                    new_general = {
                        "name": "张星彩",
                        "position": xingcai_position,
                        "alive": True,
                        "reviving": False,
                        "deployed_turn": self.current_turn,
                        "account_index": account_index,
                    }
                    if "generals" not in char_info:
                        char_info["generals"] = []
                    char_info["generals"].append(new_general)

                # 4.1 执行分配的复活任务（如果当前账号有分配任务）
                if assigned_revive_target is not None and time.time() - turn_start_time < turn_timeout:
                    if self._check_and_mark_reviving(assigned_revive_target, "主角"):
                        if self.revive_main_char_with_target(account_index, assigned_revive_target):
                            # 复活任务完成，从分配列表中移除
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]
                            time.sleep(0.1)
                            return True
                        else:
                            # 复活失败，清除reviving标记
                            with self._state_lock:
                                if assigned_revive_target in self.unit_info:
                                    char_info_revive = self.unit_info[assigned_revive_target]["main_char"]
                                    if char_info_revive.get("reviving", False):
                                        char_info_revive["reviving"] = False
                                        self.report_battle_info(
                                            f"账号{account_index} 复活账号{assigned_revive_target}的主角失败，清除reviving标记",
                                            "warning",
                                        )
                            # 从分配列表中移除，允许重新分配
                            if account_index in self.revive_assignments:
                                del self.revive_assignments[account_index]

                # 4.2 释放技能（策略引擎）
                if self._execute_best_strategy(account_index, "xingcai_support"):
                    return True

                # 4.3 防御（保底兼容）
                defense_btn = self.find_image(
                    account_index, self.button_images.get("防御按钮"), self.right_button_region, 0
                )
                if defense_btn:
                    self.click_position(account_index, defense_btn.x, defense_btn.y)
                    self.report_battle_info(f"账号{account_index} 张星彩执行防御", "action")
                    time.sleep(CombatConstants.ACTION_DELAY)
                    return True
            
            # 未识别到单位类型，进入兜底决策链
            # ① 灰图标检测 → 蓝耗尽恢复（仅四象模式）
            if self.combat_scene == "四象" and self._detect_gray_and_recover(account_index):
                return True

            # ② 防御兜底
            defense_btn = None
            find_defense_time = time.time()
            while time.time() - find_defense_time < 1.0 and not defense_btn:
                defense_btn = self.find_image(
                    account_index, self.button_images.get("防御按钮"), self.right_button_region, 0
                )
                if defense_btn:
                    break
                time.sleep(0.005)
            if defense_btn:
                self.click_position(account_index, defense_btn.x, defense_btn.y)
                self.report_battle_info(f"账号{account_index} 未识别单位类型，执行防御兜底", "action")
                time.sleep(CombatConstants.ACTION_DELAY)
                return True

            return False

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 处理回合操作失败: {e}", "error")
            return False

    # 轮询监听主循环
    def start_polling_loop(self):
        """启动轮询监听循环(在新线程中运行)"""
        if self.polling_running:
            self.report_battle_info("轮询监听已在运行中", "warning")
            return

        self.polling_running = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        self.report_battle_info("轮询监听线程已启动", "system")

    # 轮询监听循环(内部方法)
    def _polling_loop(self):
        """轮询监听循环(内部实现)"""
        self.report_battle_info("开始轮询监听战斗状态", "system")
        account_count = self.get_account_count()

        # 初始化单位信息
        self.init_unit_info()

        # 第零步（前置循环）：三个号进入循环，检测操作按钮或zdzd弹窗，等待进入监听环节
        step0_completed = False
        while not step0_completed and self.polling_running:
            # 检测所有账号
            for account_index in range(self.get_account_count()):
                if not self.polling_running:
                    break

                dm = self.get_account_dm(account_index)
                if not dm:
                    continue

                # 优先检测操作按钮：如果等待到了操作按钮，就退出循环进入监听环节
                if self.check_action_button(account_index):
                    step0_completed = True
                    break

                # 检测zdzd图片：如果等待到了zdzd_image图片，等待取消按钮出现并点击
                zdzd_pos = self.find_image(account_index, self.zdzd_image, self.zdzd_region, 0)
                if zdzd_pos:
                    # 找到zdzd图片，等待取消按钮出现并点击
                    cancel_button_pos = None
                    wait_start_time = time.time()
                    while not cancel_button_pos and (time.time() - wait_start_time) < 3.0:  # 最多等待3秒
                        if not self.polling_running:
                            break
                        cancel_button_pos = self.find_image(
                            account_index, self.button_images["取消按钮"], self.zdzd_region, 0
                        )
                        if cancel_button_pos:
                            self.click_position(account_index, cancel_button_pos.x, cancel_button_pos.y)
                            self.report_battle_info(f"账号{account_index} 检测到zdzd弹窗，已点击取消", "warning")
                            step0_completed = True
                            break
                        time.sleep(0.1)  # 每次检测间隔0.1秒

            # 如果还没完成，等待一小段时间再继续检测
            if not step0_completed:
                time.sleep(0.1)

        # 进入监听循环
        while self.polling_running:
            try:
                # 开启六曹操
                # if not self.keep_support_general and not self.start_summon_liubei and 0 in self.enemies_need_clear and self.enemies_need_clear[0]:
                #     self.start_summon_liubei = True
                #     self.beidong_huihe = 5
                # 第一步：循环检测三个账号是否有zdzd弹窗，如果有则点击取消按钮
                for account_index in range(self.get_account_count()):
                    if not self.polling_running:
                        break

                    dm = self.get_account_dm(account_index)
                    if not dm:
                        continue

                    # 检测zdzd图片
                    zdzd_pos = self.find_image(account_index, self.zdzd_image, self.zdzd_region, 0)
                    if zdzd_pos:
                        # 找到zdzd图片，点击取消按钮
                        cancel_button_pos = self.find_image(
                            account_index, self.button_images["取消按钮"], self.zdzd_region, 0
                        )
                        if cancel_button_pos:
                            self.click_position(account_index, cancel_button_pos.x, cancel_button_pos.y)
                            self.report_battle_info(f"账号{account_index} 检测到zdzd弹窗，已点击取消", "warning")
                            time.sleep(0.5)  # 等待弹窗关闭

                # 第二步：检测三个大漠对象是否出现了操作按钮
                # 任意一个大漠对象识别到操作按钮，说明到了我方回合
                has_action_button = False
                for account_index in range(self.get_account_count()):
                    if not self.polling_running:
                        break
                    dm = self.get_account_dm(account_index)
                    if not dm:
                        continue
                    if self.check_action_button(account_index):
                        has_action_button = True
                        break

                # 第三步：如果任意一个大漠对象检测到操作按钮，说明是我方回合，进行对应的操作
                if has_action_button:
                    # 清理已过期的清除任务
                    self._cleanup_expired_clear_targets()

                    # 重置目标点位识别标志（只识别一次）
                    if (
                        not hasattr(self, "_target_positions_detected_this_round")
                        or not self._target_positions_detected_this_round
                    ):
                        self.target_positions_detected = False
                        self._target_positions_detected_this_round = True
                        # 在我方回合开始时，由大漠对象0识别目标点位
                        self.detect_target_positions()

                    # 在我方回合开始时，分配复活任务（优先级：其他账号主角 > 随机账号武将）
                    self.revive_assignments = self._assign_revive_tasks()

                    # 统计全场免死安全的武将数(count<4的视为安全), 决定是否需要预替换
                    # ally_undead_rounds为空(全张星彩等) → 不需要预替换
                    # 所有武将count>=4 → undead_active=0 → 触发预替换
                    # 有replacing武将正在进行时 → 不触发新的预替换(等确认结果)
                    has_replacing_general = False
                    for acct_idx in range(self.get_account_count()):
                        if acct_idx not in self.unit_info:
                            continue
                        for g in self.unit_info[acct_idx]["main_char"].get("generals", []):
                            if g.get("replacing", False):
                                has_replacing_general = True
                                break
                        if has_replacing_general:
                            break
                    if has_replacing_general:
                        pass  # 有替换中的武将, 保持当前need_proactive_replace状态不变
                    elif not self.ally_undead_rounds:
                        self.need_proactive_replace = False
                    else:
                        undead_active = sum(
                            1 for k, v in self.ally_undead_rounds.items()
                            if v >= 0 and v < self.undead_threshold)

                        # 检查场上是否有免死被动武将未被追踪（被动未触发）
                        # 如果有，说明被动还没触发，不应该触发预替换
                        has_untracked_undead = False
                        undead_generals = ("曹操", "刘备", "魔化关羽")
                        _debug_untracked_details = []
                        for acct_idx in range(self.get_account_count()):
                            if acct_idx not in self.unit_info:
                                continue
                            for g in self.unit_info[acct_idx]["main_char"].get("generals", []):
                                g_name = g.get("name", "")
                                g_alive = g.get("alive", False) and not g.get("replacing", False)
                                if g_alive and g_name in undead_generals:
                                    # 检查该武将是否在 ally_undead_rounds 中
                                    # 通过 position 反查 region_idx，再核对 ally_undead_rounds 是否有该 key
                                    found_in_tracking = False
                                    g_position = g.get("position")
                                    _debug_match_attempts = []
                                    if g_position:
                                        for k in self.ally_undead_rounds:
                                            if k[0] == acct_idx:
                                                region_idx = k[1]
                                                unit_info = self.hp_bar_unit_mapping.get(acct_idx, {}).get(region_idx)
                                                if unit_info:
                                                    _, _, pos = unit_info
                                                    _dx = abs(pos[0] - g_position[0])
                                                    _dy = abs(pos[1] - g_position[1])
                                                    _matched = _dx < 50 and _dy < 50
                                                    _debug_match_attempts.append(
                                                        f"region{region_idx}:map_pos={pos},g_pos={g_position},dx={_dx},dy={_dy},matched={_matched}")
                                                    if _matched:
                                                        found_in_tracking = True
                                                        break
                                    _debug_untracked_details.append(
                                        f"账号{acct_idx} {g_name} g_pos={g_position} found_in_tracking={found_in_tracking} "
                                        f"attempts=[{'|'.join(_debug_match_attempts) if _debug_match_attempts else '无同账号key'}]")
                                    if not found_in_tracking:
                                        has_untracked_undead = True
                                        break
                            if has_untracked_undead:
                                break

                        if has_untracked_undead:
                            self.need_proactive_replace = False  # 有未触发被动的武将，不触发
                        else:
                            self.need_proactive_replace = (undead_active == 0)
                            if self.need_proactive_replace:
                                _debug_undead = {str(k): v for k, v in self.ally_undead_rounds.items()}
                        # 汇总日志
                        _active_summary = {str(k): v for k, v in self.ally_undead_rounds.items()}

                    # 为每个账号创建独立的处理线程
                    # 主账号已确认是我方回合，直接创建线程，_handle_account_turn内部会自己检测和等待操作按钮
                    account_threads = {}
                    for account_index in range(self.get_account_count()):
                        if not self.polling_running:
                            break

                        dm = self.get_account_dm(account_index)
                        if not dm:
                            continue

                        # 直接创建处理线程，_handle_account_turn内部会自己检测和等待操作按钮
                        thread = threading.Thread(target=self._handle_account_turn, args=(account_index,), daemon=False)
                        thread.start()
                        account_threads[account_index] = thread
                        # 保存到实例变量，用于 cleanup 时强制停止
                        self.account_threads[account_index] = thread

                    # 如果有账号需要操作，记录日志
                    if account_threads:
                        accounts_list = list(account_threads.keys())
                        self.report_battle_info(f"检测到账号 {accounts_list} 操作按钮，开始操作", "turn")

                    # 等待所有账号操作完成（最多等待25秒）
                    for account_index, thread in account_threads.items():
                        thread.join(timeout=CombatConstants.TURN_TIMEOUT)
                        # 线程完成后，从实例变量中移除引用
                        if account_index in self.account_threads:
                            del self.account_threads[account_index]
                    # 输出所有账号的存活状态和全局死亡列表
                    account_count = self.get_account_count()
                    status_info = []
                    with self._state_lock:
                        for account_idx in range(account_count):
                            if account_idx not in self.unit_info:
                                continue
                            
                            char_info = self.unit_info[account_idx]["main_char"]
                            main_char_status = "存活" if char_info.get("alive", True) else "死亡"
                            
                            # 获取武将列表（最多2个）
                            generals = char_info.get("generals", [])
                            general1_status = "无"
                            general2_status = "无"
                            
                            if len(generals) > 0:
                                gen1 = generals[0]
                                gen1_name = gen1.get("name", "未知")
                                gen1_alive = gen1.get("alive", True)
                                general1_status = f"{gen1_name}({'存活' if gen1_alive else '死亡'})"
                            
                            if len(generals) > 1:
                                gen2 = generals[1]
                                gen2_name = gen2.get("name", "未知")
                                gen2_alive = gen2.get("alive", True)
                                general2_status = f"{gen2_name}({'存活' if gen2_alive else '死亡'})"
                            
                            status_info.append(
                                f"账号{account_idx}: 主角({main_char_status}), 武将一({general1_status}), 武将二({general2_status})"
                            )
                        
                        # 获取全局死亡列表
                        dead_main_chars = []
                        for dead_char in self.global_dead_units["main_chars"]:
                            account_idx = dead_char.get("account_index", -1)
                            name = dead_char.get("name", "未知")
                            dead_main_chars.append(f"账号{account_idx}主角({name})")
                        
                        dead_generals = []
                        for dead_gen in self.global_dead_units["generals"]:
                            account_idx = dead_gen.get("account_index", -1)
                            name = dead_gen.get("name", "未知")
                            position = dead_gen.get("position", (0, 0))
                            dead_generals.append(f"账号{account_idx}武将({name}, 位置{position})")
                    
                    # 输出存活状态
                    for status_line in status_info:
                        self.report_battle_info(status_line, "info")
                    
                    # 输出全局死亡列表
                    if dead_main_chars or dead_generals:
                        dead_info = "全局死亡列表: "
                        if dead_main_chars:
                            dead_info += f"主角[{', '.join(dead_main_chars)}] "
                        if dead_generals:
                            dead_info += f"武将[{', '.join(dead_generals)}]"
                        self.report_battle_info(dead_info, "info")
                    else:
                        self.report_battle_info("全局死亡列表: 无", "info")
                    self.report_battle_info(f"我方回合结束")
                    # 清空复活任务分配，为下一回合准备
                    self.revive_assignments = {}
                    # 重置目标点位识别标志，为下一轮准备
                    self._target_positions_detected_this_round = False

                    # 操作完成后，更新回合数（第一回合后，每回合递增）
                    # 注意：每个账号独立处理，但回合数只需要更新一次
                    if account_threads:
                        if self.current_turn <= 1:
                            self.current_turn = 2  # 第一回合后，设置为2
                        else:
                            self.current_turn += 1  # 之后每回合递增
                            # 加攻击buff回合递减
                            for acct in list(self.attack_buff_tracker.keys()):
                                self.attack_buff_tracker[acct] -= 1
                                if self.attack_buff_tracker[acct] <= 0:
                                    del self.attack_buff_tracker[acct]

                        self.update_status_panel()

                # 非我方回合：检测场上的墓碑和敌军状态
                # 使用主账号（账号0）检测所有账号的状态
                main_account_index = 0
                dm = self.get_account_dm(main_account_index)
                if dm:
                    # 第一步：一次性扫描全部9个区域检测墓碑
                    dead_list = self.check_tombstones_all(detect_account_index=main_account_index)
                    if dead_list:
                        self.update_unit_info_from_tombstones(dead_list)

                    # 第二步：检测敌军需要清除的状态
                    if self.enemy_keys_to_detect:
                        self.detect_enemies_need_clear(main_account_index)

                    # 非我方回合时，由大漠对象0检测场上是否有刘备
                    self._detect_liubei_on_field()

                    # 追踪我方武将免死被动轮次
                    self._track_ally_undead(main_account_index)

                    # 检测血量低单位（每轮只扫一个账号，3轮扫完一轮）
                    if not hasattr(self, '_hp_scan_round'):
                        self._hp_scan_round = 0
                    acct = self._hp_scan_round % 3
                    self._hp_scan_round += 1
                    cnt = 0
                    self.low_hp_units[acct] = []
                    for ridx, ac in self.hp_region_to_account.items():
                        if ac == acct:
                            reg = self.hp_bar_regions[ridx]
                            if self.find_image(acct, self.low_hp_indicator_image, reg, 0):
                                cnt += 1
                                unit_map = self.hp_bar_unit_mapping.get(acct, {})
                                if ridx in unit_map:
                                    unit_type, unit_name, position = unit_map[ridx]
                                    self.low_hp_units[acct].append({
                                        "unit_type": unit_type,
                                        "unit_name": unit_name,
                                        "position": position
                                    })
                    self.low_hp_accounts[acct] = cnt
                # 轮询间隔（非我方回合时）
                if self.polling_running:
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

            except KeyboardInterrupt:
                self.polling_running = False
                self.report_battle_info("轮询监听已停止(KeyboardInterrupt)", "system")
                break
            except Exception as e:
                import traceback
                self.report_battle_info(f"轮询监听出错: {type(e).__name__}: {e}", "error")
                try:
                    traceback.print_exc()
                except Exception:
                    pass
                if self.polling_running:
                    if isinstance(e, KeyError) and not self.unit_info:
                        self.init_unit_info()
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

        self.report_battle_info("轮询监听循环已结束", "system")

    # 停止轮询监听
    def stop_polling_loop(self):
        """停止轮询监听"""
        if not self.polling_running:
            return

        self.polling_running = False
        self.report_battle_info("正在停止轮询监听...", "system")

        # 等待线程结束(最多等待2秒)
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2.0)

        self.report_battle_info("轮询监听已停止", "system")

    # 兼容方法：run_combat_loop (供newMain.py调用)
    def run_combat_loop(self):
        """运行战斗循环(兼容方法名，在当前线程中运行轮询循环)"""
        self.current_turn = 0
        self.polling_running = True
        self._polling_loop()

    # ==================== 三态自动战斗系统新增方法 ====================

    def run_single_skill_round(self):
        """Mode 1: 执行一轮完整技能释放（等待操作按钮 → 处理所有账号回合）
        阻塞方法，会等待操作按钮出现后执行技能释放
        """
        try:
            # 递增回合数（用于CD判断和状态过期逻辑）
            self.current_turn += 1

            # 等待操作按钮出现（最多等待15秒）
            action_found = False
            start_time = time.time()
            while time.time() - start_time < 15.0:
                for account_index in range(self.get_account_count()):
                    dm = self.get_account_dm(account_index)
                    if not dm:
                        continue
                    if self.check_action_button(account_index):
                        action_found = True
                        break
                if action_found:
                    break
                time.sleep(0.3)

            if not action_found:
                return

            # 检测zdzd弹窗并取消
            for account_index in range(self.get_account_count()):
                dm = self.get_account_dm(account_index)
                if not dm:
                    continue
                zdzd_pos = self.find_image(account_index, self.zdzd_image, self.zdzd_region, 0)
                if zdzd_pos:
                    cancel_button_pos = self.find_image(
                        account_index, self.button_images["取消按钮"], self.zdzd_region, 0
                    )
                    if cancel_button_pos:
                        self.click_position(account_index, cancel_button_pos.x, cancel_button_pos.y)
                        time.sleep(0.5)

            # 为每个账号执行技能释放
            account_threads = {}
            for account_index in range(self.get_account_count()):
                dm = self.get_account_dm(account_index)
                if not dm:
                    continue
                if not self.check_action_button(account_index):
                    continue
                thread = threading.Thread(
                    target=self._handle_account_turn,
                    args=(account_index,),
                    daemon=True
                )
                thread.start()
                account_threads[account_index] = thread

            # 等待所有账号操作完成（最多等待30秒）
            for thread in account_threads.values():
                thread.join(timeout=30.0)

        except Exception as e:
            print(f"run_single_skill_round 出错: {e}")

    def check_any_action_button(self):
        """检测任意账号是否可见操作按钮（技能/召唤/道具/防御/操作/重复）
        :return: True 如果任意账号有操作按钮可见
        """
        for account_index in range(self.get_account_count()):
            dm = self.get_account_dm(account_index)
            if not dm:
                continue
            if self.check_action_button(account_index):
                return True
        return False

    def exit_system_auto(self):
        """退出系统自动战斗（点击取消自动按钮）"""
        try:
            for account_index in range(self.get_account_count()):
                dm = self.get_account_dm(account_index)
                if not dm:
                    continue
                cancel_pos = self.find_image(
                    account_index,
                    self.button_images["取消按钮"],
                    self.zdzd_region,
                    0
                )
                if cancel_pos:
                    self.click_position(account_index, cancel_pos.x, cancel_pos.y)
                    time.sleep(0.5)
        except Exception as e:
            print(f"exit_system_auto 出错: {e}")

    def detect_enemy_status_for_hybrid(self, enemy_keys):
        """Mode 3: 检测指定敌方状态列表，返回第一个检测到的敌方key
        :param enemy_keys: 需要检测的敌方状态key列表，例如 ["羊人参娃", "诸葛亮"]
        :return: 检测到的敌方key，或None
        """
        if not enemy_keys:
            return None

        for enemy_key in enemy_keys:
            if enemy_key not in self.enemy_general_config:
                continue

            config = self.enemy_general_config[enemy_key]
            status_region = config["status_region"]
            status_images = config["status_images"]

            for status_name, status_image in status_images.items():
                # 使用主账号(dm_index=0)检测
                status_pos = self.find_image(0, status_image, status_region, 0)
                if status_pos:
                    return enemy_key

        return None

    # 清理资源
    def cleanup(self, join_timeout: float = 2.0):
        """
        强制停止本实例内的所有线程并重置状态（最佳努力）。
        说明：
        - Python 无法强制杀死线程，这里只做“通知停止 + 等待 join + 清理引用”的最佳努力。
        - 保证设置所有常用停止标志、取消定时器、等待线程结束并清空内部数据结构。
        - 如果某些线程内部存在长时间阻塞或不响应停止标志，仍可能无法立即结束（会打印警告）。
        """
        try:
            # 1) 通知停止：设置主控制标志与常见停止事件/标志
            try:
                self.polling_running = False
            except Exception:
                pass
            try:
                if hasattr(self, "stop_event") and isinstance(getattr(self, "stop_event"), threading.Event):
                    self.stop_event.set()
            except Exception:
                pass
            for flag in ("stop_flag", "running", "should_stop", "shutdown"):
                if hasattr(self, flag):
                    try:
                        setattr(self, flag, False)
                    except Exception:
                        pass

            # 2) 取消并清理所有定时器
            try:
                for timer in list(self._timer_refs):
                    try:
                        timer.cancel()
                    except Exception:
                        pass
                self._timer_refs.clear()
            except Exception:
                pass

            # 3) 强制等待并清理 account_threads（每个账户的处理线程）
            try:
                if getattr(self, "account_threads", None):
                    for acct_idx, th in list(self.account_threads.items()):
                        try:
                            if isinstance(th, threading.Thread) and th.is_alive():
                                th.join(timeout=join_timeout)
                                if th.is_alive():
                                    print(f"警告: 账户线程 {acct_idx} 未能在 {join_timeout}s 内停止")
                        except Exception as e:
                            print(f"等待账户线程 {acct_idx} 时出错: {e}")
                    self.account_threads.clear()
            except Exception:
                pass

            # 4) 停止并等待主轮询线程
            try:
                if getattr(self, "polling_thread", None) and isinstance(self.polling_thread, threading.Thread):
                    if self.polling_thread.is_alive():
                        self.polling_thread.join(timeout=join_timeout)
                        if self.polling_thread.is_alive():
                            print(f"警告: 主轮询线程未能在 {join_timeout}s 内停止")
                    self.polling_thread = None
            except Exception as e:
                print(f"等待主轮询线程时出错: {e}")

            # 5) 尝试 join 对象中其它可能的线程属性（名称中包含 'thread'）
            try:
                for name in list(dir(self)):
                    if name in ("polling_thread", "account_threads", "_timer_refs"):
                        continue
                    if "thread" in name.lower():
                        try:
                            t = getattr(self, name)
                            if isinstance(t, threading.Thread):
                                if t is threading.current_thread():
                                    continue
                                if t.is_alive():
                                    t.join(timeout=join_timeout)
                                    if t.is_alive():
                                        print(f"警告: 线程属性 {name} 未能在 {join_timeout}s 内停止")
                                try:
                                    setattr(self, name, None)
                                except Exception:
                                    pass
                        except Exception:
                            pass
            except Exception:
                pass

            # 6) 关闭/销毁 GUI 窗口（如果存在），并给主线程机会处理事件
            try:
                if getattr(self, "battle_report_dialog", None):
                    try:
                        self.battle_report_dialog.close_safely()
                    except Exception:
                        pass
                    try:
                        self.battle_report_dialog = None
                    except Exception:
                        pass
                self._dialog_closed = True
                # 在主线程时让 wx 处理关闭事件
                if threading.current_thread() == threading.main_thread():
                    try:
                        import wx
                        wx.Yield()
                    except Exception:
                        pass
            except Exception:
                pass

            # 7) 重置/清空所有运行时数据结构（恢复到初始状态）
            try:
                # 基本控制字段
                self.turn_timeout = CombatConstants.TURN_TIMEOUT
                self.turn_start_time = None
                self.account_error_count = {}
                self.max_errors_per_turn = CombatConstants.MAX_ERRORS_PER_TURN

                self._battle_dialog_retry_count = 0

                # 清空战斗状态数据
                self.unit_info = {}
                self.dead_units = {}
                self.global_dead_units = {"main_chars": [], "generals": []}
                self.global_enemies_need_clear = []
                self._claimed_clear_target = {}
                self._liubei_summon_in_progress = {}
                self.enemy_status_reported = {}
                self.current_turn = 0
                self.skill_cd = {}
                self.pending_liubei_summon = {}
                self.has_liubei_on_field = True
                self.liubei_missing_count = 0
                self.low_hp_units = {}
                self._no_heal_item_missing_turn = {}
                self._no_mana_item_missing_turn = {}
                self.item_cd_tracking = {}
                self._current_our_turn_call = 0
                self.zhugeliang_found = {}
                self.zhugeliang_status1_missing_count = {}
                self.zhugeliang_status2_missing_count = {}
                self.lantiao_missing_rounds = {}

                self.liubei_skill_sequence = ["控制", "加攻击", "加血"]
                self.liubei_skill_index = {}
                self.liubei_skill_cd = {}
                self._last_clear_attempt = {}

                self.revive_assignments = {}

                self.enemy_target_positions = []
                self.ally_target_positions = []
                self.enemy_target_index = 0
                self.ally_target_index = 0
                self.enemy_count = 0
                self.enemy_single_rounds = 0
                self.account_last_target_type = {}
                self.target_positions_detected = False
                self._target_positions_detected_this_round = False

                self.has_general = {i: True for i in range(3)}
                self.liubei_remaining = {i: self.liubei_counts.get(i, 0) for i in range(3)}
                self.has_liubei = {i: self.liubei_remaining.get(i, 0) > 0 for i in range(3)}
                self.beidong_huihe = 0
                self.zhaohuan_index = 0
                self.clear_zhugeliang = False
                self.enable_persistent_liubei = True
                self._last_kicked_info = None
                self.ally_undead_rounds = {}
                self.ally_undead_last_increment_turn = {}
                self.need_proactive_replace = False
                self.proactive_replace_account = 0
                self.attack_buff_tracker = {}
                self.low_hp_accounts = {}
                self.start_summon_liubei = False
                self._hp_scan_round = 0
            except Exception:
                pass

            print("cleanup: 已通知停止，尝试等待并清理线程/资源（最佳努力）")
        except Exception as e:
            print(f"cleanup 出错: {e}")
            import traceback
            traceback.print_exc()

    def reset_state(self):
        try:
            self.polling_running = False
            try:
                if hasattr(self, "stop_event") and isinstance(getattr(self, "stop_event"), threading.Event):
                    self.stop_event.set()
            except Exception:
                pass

            try:
                for timer in list(self._timer_refs):
                    try:
                        timer.cancel()
                    except Exception:
                        pass
                self._timer_refs.clear()
            except Exception:
                pass

            try:
                if getattr(self, "account_threads", None):
                    for acct_idx, th in list(self.account_threads.items()):
                        try:
                            if isinstance(th, threading.Thread) and th.is_alive():
                                th.join(timeout=2.0)
                        except Exception:
                            pass
                    self.account_threads.clear()
            except Exception:
                pass

            try:
                if getattr(self, "polling_thread", None) and isinstance(self.polling_thread, threading.Thread):
                    if self.polling_thread.is_alive():
                        self.polling_thread.join(timeout=2.0)
                    self.polling_thread = None
            except Exception:
                pass

            self.turn_timeout = CombatConstants.TURN_TIMEOUT
            self.turn_start_time = None
            self.account_error_count = {}
            self._battle_dialog_retry_count = 0

            self.unit_info = {}
            self.dead_units = {}
            self.global_dead_units = {"main_chars": [], "generals": []}
            self.global_enemies_need_clear = []
            self._claimed_clear_target = {}
            self._liubei_summon_in_progress = {}
            self.enemy_status_reported = {}
            self.current_turn = 0
            self.skill_cd = {}
            self.pending_liubei_summon = {}
            self.has_liubei_on_field = True
            self.liubei_missing_count = 0
            self.keep_support_general = False
            self.low_hp_units = {}
            self._no_heal_item_missing_turn = {}
            self._no_mana_item_missing_turn = {}
            self.item_cd_tracking = {}
            self._current_our_turn_call = 0
            self.zhugeliang_found = {}
            self.zhugeliang_status1_missing_count = {}
            self.zhugeliang_status2_missing_count = {}
            self.lantiao_missing_rounds = {}

            self.liubei_skill_sequence = ["控制", "加攻击", "加血"]
            self.liubei_skill_index = {}
            self.liubei_skill_cd = {}
            self._last_clear_attempt = {}

            self.revive_assignments = {}

            self.enemy_target_positions = []
            self.ally_target_positions = []
            self.enemy_target_index = 0
            self.enemy_single_rounds = 0
            self.ally_target_index = 0
            self.enemy_count = 0
            self.account_last_target_type = {}
            self.target_positions_detected = False
            self._target_positions_detected_this_round = False

            self.has_general = {i: True for i in range(3)}
            self.liubei_remaining = {i: self.liubei_counts.get(i, 0) for i in range(3)}
            self.has_liubei = {i: self.liubei_remaining.get(i, 0) > 0 for i in range(3)}
            self.beidong_huihe = 0
            self.zhaohuan_index = 0
            self.clear_zhugeliang = False
            self.attack_buff_tracker = {}
            self.low_hp_accounts = {}
            self._zhugeliang_low_hp = False
            self.ally_undead_rounds = {}
            self.ally_undead_last_increment_turn = {}
            self.caocao_passive_missing_rounds = {}
            self.proactive_replace_account = 0
            self.need_proactive_replace = False
            self._proactive_replace_in_progress = False
            self._last_kicked_info = None
            self.replace_fail_count = {}
            self.replace_fail_cooldown = {}
            self.start_summon_liubei = False
            self._hp_scan_round = 0

            if self.battle_report_dialog:
                try:
                    self.battle_report_dialog.reset_status()
                    self.battle_report_dialog.add_log("── 新一轮战斗 ──", "system")
                except Exception:
                    pass
        except Exception as e:
            print(f"reset_state 出错: {e}")

    def reconfigure(self, enemy_keys_to_detect=None, keep_support_general=None,
                    enable_main_heal=None, enable_main_summon=None,
                    enable_persistent_liubei=None, liubei_counts=None,
                    combat_scene=None):
        try:
            if enemy_keys_to_detect is not None:
                self.enemy_keys_to_detect = enemy_keys_to_detect if enemy_keys_to_detect else []
            if keep_support_general is not None:
                self.keep_support_general = keep_support_general
            if enable_main_heal is not None:
                self.enable_main_heal = enable_main_heal
            if enable_main_summon is not None:
                self.enable_main_summon = enable_main_summon
            if enable_persistent_liubei is not None:
                self.enable_persistent_liubei = enable_persistent_liubei
            if liubei_counts is not None:
                self.liubei_counts = liubei_counts
                self.liubei_remaining = dict(self.liubei_counts)
                self.has_liubei = {i: self.liubei_remaining.get(i, 0) > 0 for i in range(3)}
            self.combat_scene = combat_scene
            self.current_turn = 0
            self.clear_zhugeliang = False
            self.global_enemies_need_clear = []
            self._claimed_clear_target = {}
            self._last_clear_attempt = {}
            self._liubei_summon_in_progress = {}
            self.enemy_status_reported = {}
            self.zhugeliang_status1_missing_count = {}
            self._zhugeliang_low_hp = False
            self.replace_fail_count = {}
            self.replace_fail_cooldown = {}
            self._dialog_closed = False
            self._battle_dialog_retry_count = 0
            if self.battle_report_dialog:
                try:
                    self.battle_report_dialog.Show()
                    self.battle_report_dialog.Raise()
                except Exception:
                    pass
        except Exception as e:
            print(f"reconfigure 出错: {e}")

    def update_status_panel(self):
        try:
            if not self.battle_report_dialog:
                return
            dlg = self.battle_report_dialog
            dlg.update_turn(self.current_turn)
            for i in range(3):
                main_alive = True
                main_status = "正常"
                general_alive = -1
                general_total = 2
                has_lb = self.has_liubei.get(i, False)
                if i in self.unit_info:
                    mc = self.unit_info[i].get("main_char", {})
                    main_alive = mc.get("alive", True)
                    if not main_alive:
                        main_status = "阵亡"
                    elif mc.get("need_revive", False) or mc.get("reviving", False):
                        main_status = "复活中"
                    elif i in self.low_hp_units and self.low_hp_units[i]:
                        main_status = "低血"
                    generals = mc.get("generals", [])
                    general_alive = sum(1 for g in generals if g.get("alive", True))
                    general_total = min(max(len(generals), 2), 2)
                dlg.update_account_status(i, main_alive, main_status,
                                          general_alive, general_total, has_lb)
        except Exception:
            pass


# 示例使用
if __name__ == "__main__":
    # 这个脚本需要在 MyThread 的上下文中运行
    # 使用方式：
    # 1. 在 MyFrame 中添加新的脚本选项 "战斗中自动"
    # 2. 在 MyThread.run() 方法中添加对应的脚本执行分支
    # 3. 调用 CombatAutoScript 的功能

    print("战斗自动操作脚本已就绪")