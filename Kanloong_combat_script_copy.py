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
    DEFAULT_CHECK_INTERVAL = 0.06

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
    """战斗实时播报窗口"""

    # 初始化战斗播报窗口
    # :param parent: 父窗口，默认为None
    def __init__(self, parent=None):
        super().__init__(
            parent, title="战斗实时播报", size=(500, 350), pos=(450, 50), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        )
        self.SetBackgroundColour(wx.Colour(245, 245, 250))

        # 创建主面板
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        # 创建布局
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 标题区域
        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(wx.Colour(20, 180, 168))
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        title_text = wx.StaticText(title_panel, label="战斗实时播报", style=wx.ALIGN_CENTER)
        title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))

        title_sizer.Add(title_text, 1, wx.ALIGN_CENTER | wx.ALL, 5)
        title_panel.SetSizer(title_sizer)
        vbox.Add(title_panel, 0, wx.EXPAND)

        # 创建滚动面板（先创建滚动面板）
        scroll_panel = scrolled.ScrolledPanel(panel, -1)
        scroll_panel.SetupScrolling()

        # 在滚动面板中创建文本区域（父窗口必须是scroll_panel）
        self.log_text = wx.TextCtrl(
            scroll_panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size=(-1, -1)  # 父窗口改为scroll_panel
        )
        # 设置字体
        log_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.log_text.SetFont(log_font)
        self.log_text.SetBackgroundColour(wx.Colour(250, 250, 255))

        # 设置滚动面板的布局
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 3)
        scroll_panel.SetSizer(scroll_sizer)

        vbox.Add(scroll_panel, 1, wx.EXPAND | wx.ALL, 3)

        # 底部按钮区域
        button_panel = wx.Panel(panel)
        button_panel.SetBackgroundColour(wx.Colour(245, 245, 250))
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.clear_button = wx.Button(button_panel, label="清空日志", size=(80, 28))
        self.clear_button.SetFont(log_font)
        self.clear_button.SetBackgroundColour(wx.Colour(144, 144, 153))
        self.clear_button.SetForegroundColour(wx.Colour(255, 255, 255))
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        self.export_button = wx.Button(button_panel, label="生成txt", size=(80, 28))
        self.export_button.SetFont(log_font)
        self.export_button.SetBackgroundColour(wx.Colour(20, 180, 168))
        self.export_button.SetForegroundColour(wx.Colour(255, 255, 255))
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export_txt)

        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.export_button, 0, wx.ALL, 3)
        button_sizer.Add(self.clear_button, 0, wx.ALL, 3)
        button_panel.SetSizer(button_sizer)

        vbox.Add(button_panel, 0, wx.EXPAND)

        panel.SetSizer(vbox)

        # 日志锁（线程安全）
        self.log_lock = threading.Lock()

        # 初始化消息
        self.add_log("=" * 40, wx.Colour(100, 100, 100))
        self.add_log("战斗播报系统已启动", wx.Colour(20, 180, 168))
        self.add_log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", wx.Colour(100, 100, 100))
        self.add_log("=" * 40, wx.Colour(100, 100, 100))
        self.add_log("")

    # 添加日志消息（线程安全）
    def add_log(self, message, color=None):
        # 确保color有默认值
        if color is None:
            color = wx.Colour(0, 0, 0)  # 默认黑色

        # 内部函数：在主线程中添加日志消息
        def _add_log():
            try:
                if not self or not hasattr(self, "log_text") or not self.log_text:
                    print(f"警告：无法添加日志，log_text不存在 - {message[:50]}")
                    return

                with self.log_lock:
                    # 添加时间戳
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] {message}\n"

                    # 设置文本颜色并追加
                    self.log_text.SetDefaultStyle(wx.TextAttr(color))
                    self.log_text.AppendText(full_message)

                    # 自动滚动到底部
                    try:
                        self.log_text.ShowPosition(self.log_text.GetLastPosition())
                        self.log_text.Refresh()
                    except (AttributeError, RuntimeError) as e:
                        # 忽略窗口已关闭或对象已销毁的错误
                        pass
            except Exception as e:
                # 打印错误以便调试
                print(f"添加日志时出错: {e}, 消息: {message[:50]}")

        # 确保在主线程中执行GUI操作
        try:
            if threading.current_thread() == threading.main_thread():
                _add_log()
            else:
                # 如果在其他线程，使用CallAfter确保在主线程执行
                if hasattr(wx, "CallAfter"):
                    wx.CallAfter(_add_log)
                else:
                    # 如果wx未初始化，直接尝试在主线程执行
                    _add_log()
        except Exception as e:
            # 打印错误以便调试
            print(f"CallAfter调用时出错: {e}")

    # 清空日志
    def on_clear(self, event):
        self.log_text.Clear()
        self.add_log("日志已清空", wx.Colour(100, 100, 100))

    # 导出日志到txt文件
    def on_export_txt(self, event):
        """导出所有日志内容到txt文件"""
        try:
            # 创建文件保存对话框
            with wx.FileDialog(
                self, "保存日志文件", wildcard="文本文件 (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            ) as fileDialog:
                # 设置默认文件名（包含时间戳）
                default_filename = f"战斗播报_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                fileDialog.SetFilename(default_filename)

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # 用户取消了保存

                # 获取用户选择的文件路径
                filepath = fileDialog.GetPath()

                # 获取所有日志内容
                with self.log_lock:
                    log_content = self.log_text.GetValue()

                # 写入文件
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("=" * 60 + "\n")
                        f.write("战斗播报日志\n")
                        f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 60 + "\n\n")
                        f.write(log_content)

                    # 显示成功消息
                    wx.MessageBox(f"日志已成功导出到:\n{filepath}", "导出成功", wx.OK | wx.ICON_INFORMATION)
                    self.add_log(f"日志已导出到: {filepath}", wx.Colour(20, 180, 168))
                except Exception as e:
                    # 显示错误消息
                    wx.MessageBox(f"导出日志时出错:\n{str(e)}", "导出失败", wx.OK | wx.ICON_ERROR)
                    self.add_log(f"导出日志失败: {str(e)}", wx.Colour(255, 0, 0))
        except Exception as e:
            # 处理异常
            print(f"导出日志时发生异常: {e}")
            try:
                wx.MessageBox(f"导出日志时发生异常:\n{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
            except:
                pass

    # 安全关闭窗口
    def close_safely(self):
        """安全关闭窗口，确保窗口立即关闭"""
        try:
            if not self:
                return

            # 定义关闭函数
            def _close_window():
                try:
                    if self and hasattr(self, "IsBeingDeleted") and not self.IsBeingDeleted():
                        # 使用Destroy()而不是Close()，确保窗口立即销毁
                        self.Destroy()
                except Exception as e:
                    print(f"关闭战斗播报窗口时出错: {e}")

            # 确保在主线程中执行
            if threading.current_thread() == threading.main_thread():
                _close_window()
            else:
                # 如果不在主线程，使用CallAfter
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
        self.keep_support_general = True
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
        # 如果需要同时清除多个，那么就需要多个召唤，根据self.enemies_need_clear[0][account_index]来判断
        # 如果self.enemies_need_clear[0][account_index]有值，在召唤刘备的地方通过if self.enemies_need_clear[0][account_index]
        # 来判断对应的账号进行召唤，需要做替换操作，清除状态enemy_info =self.enemies_need_clear[account_index][account_index]
        self.enemies_need_clear = {}  # 需要清除状态的敌军列表
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
        # 不再记录第一回合武将数量，默认每个账号有2个武将

        # 刘备技能释放顺序和冷却记录
        self.liubei_skill_sequence = ["控制", "加攻击", "加血"]  # 刘备技能释放顺序（循环）
        self.liubei_skill_index = {}  # {account_index: current_index} 记录每个账号当前技能索引
        self.liubei_skill_cd = {}  # {account_index: {skill_name: last_used_turn}} 记录每个账号的技能冷却时间

        # 复活任务分配：{执行账号索引: 目标死亡主角账号索引}
        # 在我方回合开始时统一分配，优先级：其他账号主角 > 随机账号武将
        self.revive_assignments = {}  # 格式：{account_index: target_dead_account_index}

        # 目标点位存储（每回合开始时由大漠对象0识别）
        self.enemy_target_position = None  # 敌军攻击目标点位
        self.ally_support_target_position = None  # 我军辅助技能施法点位
        self.target_positions_detected = False  # 是否已识别目标点位（本回合）

        # 轮询监听控制
        self.polling_running = False  # 轮询监听运行标志
        self.polling_thread = None  # 轮询监听线程
        self.account_threads = {}  # 账户处理线程引用：{account_index: thread}

        # 三个账号是否有武将
        self.has_general = {0: True, 1: True, 2: True}
        # 三个账号是否有刘备
        self.has_liubei = {0: True, 1: True, 2: True}
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
        self.attack_buff_tracker = {}  # {account_index: remaining_turns} 加攻击buff剩余回合
        self.low_hp_accounts = {}      # {account_index: count} 血量低单位计数

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
                color_map = {
                    "info": wx.Colour(0, 0, 0),  # 黑色 - 普通信息
                    "success": wx.Colour(103, 194, 58),  # 绿色 - 成功操作
                    "warning": wx.Colour(226, 96, 95),  # 红色 - 警告
                    "error": wx.Colour(255, 0, 0),  # 深红 - 错误
                    "system": wx.Colour(20, 180, 168),  # 青色 - 系统消息
                    "turn": wx.Colour(0, 102, 204),  # 蓝色 - 回合信息
                    "action": wx.Colour(144, 144, 153),  # 灰色 - 动作信息
                }
                color = color_map.get(msg_type, wx.Colour(0, 0, 0))
                self.battle_report_dialog.add_log(message, color)
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
        self.enemy_region = (54, 168, 370, 541)  # 敌军区域（左侧，覆盖整个左侧区域）
        self.ally_region = (450, 162, 900, 580)  # 己方区域（右侧，覆盖整个右侧区域）
        self.main_char_region = (706, 167, 900, 580)  # 主角区域（最右侧，三个主角位置）
        self.general_region = (491, 164, 772, 522)  # 武将区域（主角前方，武将位置）

        # 回合数识别区域（"23"显示的区域，屏幕上方中间）
        self.turn_indicator_region = (378, 88, 502, 155)  # 回合数显示区域（上方中间，显示"23"等数字）

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
        }

        # 物品图片
        self.item_images = {
            "恢复药": f"{self.get_resource_path('serveAssets/images/auto/yao.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao1.bmp')}",
            # 恢复药（加血又加蓝，2回合CD）
            "复活药": f"{self.get_resource_path('serveAssets/images/auto/fuhuo.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuo1.bmp')}",
            # 复活药（复活阵亡单位）
        }

        # 刘备辅助技能目标图片（用于选择目标）
        self.liubei_target_image = f"{self.get_resource_path('serveAssets/images/auto/jifangliubei.bmp')}|{self.get_resource_path('serveAssets/images/auto/jifangmoguan.bmp')}|{self.get_resource_path('serveAssets/images/auto/jifangcaocao.bmp')}"

        # 技能目标选择图片（蓝色条）
        self.target_lantiao_image = self.get_resource_path("serveAssets/images/auto/lantiao.bmp")
        self.target_fuhuobeidong_image = f"{self.get_resource_path('serveAssets/images/auto/fuhuobeidong.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuobeidong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zengjiagongjili1.bmp')}"
        self.target_fuhuohuo_image = self.get_resource_path("serveAssets/images/auto/fuhuohuo.bmp")  # 复活目标图片
        self.liubei_image = f"{self.get_resource_path('serveAssets/images/auto/miankong1.bmp')}|{self.get_resource_path('serveAssets/images/auto/miankong2.bmp')}"  # 刘备图片路径（用于检测场上是否有刘备）
        self.tiandihudun_image = self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp")
        self.caocaobusi_image = f"{self.get_resource_path('serveAssets/images/auto/bumiexiongxin1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugeliangbeidong.bmp')}"
        self.zhugexuetiao_image = f"{self.get_resource_path('serveAssets/images/auto/zhugexuetiao.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugexuetiao1.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhugexuetiao2.bmp')}"
        # 技能CD配置（回合数）
        self.skill_cd_config = {
            # 刘备技能
            "加血": 2,  # 2回合CD
            "清除状态": 4,  # 4回合CD
            "加攻击": 0,  # 无CD
            "控制": 0,  # 无CD
            # 主角技能
            "寂灭神劫": 3,  # 3回合CD
            "锁魂": 2,  # 2回合CD
            "天灾": 2,  # 2回合CD
            # 武将技能
            "剑阵灭杀": 0,  # 无CD
            "武神一怒": 0,  # 无CD
        }

        # 药品CD配置
        self.item_cd_config = {
            "恢复药": 3,  # 3回合CD（红药，加血又加蓝）
            "复活药": 0,  # 无CD（复活药通常无CD限制）
        }

        # 技能CD追踪 {account_index: {skill_name: last_used_turn}}
        self.skill_cd_tracking = {}

        # 药品CD追踪 {account_index: {item_name: last_used_turn}}
        self.item_cd_tracking = {}

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
        }

        # 血量条图片（用于检测血量低的单位）
        # 识别到这张图片说明单位血量低，需要加血
        self.low_hp_indicator_image = f"{self.get_resource_path('serveAssets/images/auto/xueliangbuzu1.bmp')}|{self.get_resource_path('serveAssets/images/auto/mubei2.bmp')}|{self.get_resource_path('serveAssets/images/auto/xueliangbuzu2.bmp')}"  # 血量低的标识图片

        # 9个血量条检测区域（3个账号，每个账号1个主角+2个武将）
        # 顺序：账号1主角、账号0主角、账号2主角、账号1武将1、账号0武将1、账号2武将1、账号1武将2、账号0武将2、账号2武将2
        # 格式：[(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
        # 基于900x580游戏界面，血量条通常显示在角色头顶上方
        # 账号1在上排，账号0在中间排，账号2在下排
        self.hp_bar_regions = [
            (721, 159, 801, 219),  # 账号1主角血量条（上排）
            (750, 251, 829, 315),  # 账号0主角血量条（中间排）
            (784, 359, 859, 420),  # 账号2主角血量条（下排）
            (544, 159, 621, 220),  # 账号1武将1血量条（上排）
            (564, 252, 639, 319),  # 账号0武将1血量条（中间排）
            (581, 363, 664, 419),  # 账号2武将1血量条（下排）
            (631, 151, 710, 219),  # 账号1武将2血量条（上排）
            (656, 251, 737, 316),  # 账号0武将2血量条（中间排）
            (680, 361, 762, 418),  # 账号2武将2血量条（下排）
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
        self.skill_panel_region = (480, 167, 607, 550)  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = (480, 167, 607, 550)  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (0, 0, 900, 550)  # 道具面板区域（点击道具按钮后弹出的面板）

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
                    ("武将1", 597, 383),  # 账号0武将1中心点（中间排，前排）
                    ("武将2", 691, 381),  # 账号0武将2中心点（中间排，后排）
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
                    ("武将1", 576, 278),  # 账号1武将1中心点（上排，前排）
                    ("武将2", 666, 282),  # 账号1武将2中心点（上排，后排）
                ],
                "enemies": [],
            },
            # 账号2（下排）
            2: {
                "main_char": (824, 494),  # 账号2主角中心点（下排）
                "generals": [
                    ("武将1", 624, 496),  # 账号2武将1中心点（下排，前排）
                    ("武将2", 719, 487),  # 账号2武将2中心点（下排，后排）
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
                    # 可以添加多个状态图片路径，用|分隔
                    "状态1": self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp")
                },
                "status_region": (165, 258, 246, 291),  # 检测状态区域（x, y, w, h），w和h是结束坐标
                "cast_position": (203, 346),  # 施法点位（x, y）
            },
            "诸葛亮": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/bumiexiongxin1.bmp"),
                    "状态2": self.get_resource_path("serveAssets/images/auto/gangqi1.bmp"),
                },
                "status_region": (61, 257, 158, 318),
                "cast_position": (104, 344),
            },
            "赵云29": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
                },
                "status_region": (54, 168, 280, 541),
                "cast_position": (115, 446),
            },
            "龙": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (61, 257, 145, 312),
                "cast_position": (112, 372),
            },
            "人参娃": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (174, 382, 224, 426),
                "cast_position": (222, 472),
            },
            "上龙": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (48, 169, 141, 216),
                "cast_position": (97, 246),
            },
            "猴子": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (61, 257, 145, 312),
                "cast_position": (112, 372),
            },
            "猴子狮": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/mianyisiwang1.bmp"),
                },
                "status_region": (146, 177, 227, 225),
                "cast_position": (150, 300),
            },
            "赵云28": {
                "status_images": {
                    "状态1": f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
                },
                "status_region": (156, 235, 242, 319),
                "cast_position": (202, 337),
            },
            "蛇": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/shejineng.bmp"),
                },
                "status_region": (59, 162, 146, 224),
                "cast_position": (123, 350),
            },
        }

        # 按钮图片路径
        self.button_images = {
            "技能按钮": f"{self.get_resource_path('serveAssets/images/auto/jineng.bmp')}|{self.get_resource_path('serveAssets/images/auto/jineng1.bmp')}",
            "召唤按钮": f"{self.get_resource_path('serveAssets/images/auto/zhaohuan.bmp')}|{self.get_resource_path('serveAssets/images/auto/zhaohuan1.bmp')}",
            "道具按钮": f"{self.get_resource_path('serveAssets/images/auto/yaopin.bmp')}|{self.get_resource_path('serveAssets/images/auto/yaopin1.bmp')}",
            "防御按钮": f"{self.get_resource_path('serveAssets/images/auto/fangyu.bmp')}",  # 防御按钮
            "操作按钮": f"{self.get_resource_path('serveAssets/images/auto/jineng.bmp')}|{self.get_resource_path('serveAssets/images/auto/jineng1.bmp')}",  # 操作按钮(检测是否在战斗页面)
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

    # 查找文字(封装thread的方法，支持动态识别率)
    def find_text(self, account_index, text, region, find_dir=0, confidence=None):
        """查找文字，支持动态识别率
        confidence: 识别率，如果为None则使用默认值
        """
        dm = self.get_account_dm(account_index)
        if not dm:
            return None

        # 获取默认识别率和颜色格式
        default_confidence = getattr(self.thread, "confidenceNum", 0.9)
        color_format = "ffff00-000000|fff200-000000|fdfd06-000000"

        # 使用指定的识别率或默认值
        use_confidence = confidence if confidence is not None else default_confidence
        # 直接使用dm对象，避免修改共享的confidenceNum（线程安全）
        # 大漠插件本身是线程安全的，可以直接在子线程中使用
        x, y, w, h = region
        find_str_result = dm.FindStrFastE(int(x), int(y), int(w), int(h), text, color_format, use_confidence)
        return self._parse_find_str_result(find_str_result, find_dir)

    # 解析FindStrFastE的结果
    def _parse_find_str_result(self, find_str_result, find_dir):
        """解析FindStrFastE的结果"""
        if not find_str_result:
            return None
        find_str_result = find_str_result.split("|")
        if int(find_str_result[0]) >= 0:
            pos_res = None
            if len(find_str_result) == 3:
                pos_res = find_str_result
            elif len(find_str_result) > 3:
                if int(find_str_result[1]) < int(find_str_result[4]) and find_dir in [0, 1]:
                    pos_res = find_str_result[:3]
                else:
                    pos_res = find_str_result[3:6]
            if pos_res:
                posX = pos_res[1]
                posY = pos_res[2]
                return ResXy(int(posX), int(posY))
        return None

    # 检查敌军场上是否有配置的敌军单位
    def find_enemy_unit_on_field(self, account_index):
        """检查敌军场上是否有配置的敌军单位，返回第一个找到的单位的cast_position
        :param account_index: 账号索引
        :return: (x, y) 坐标元组或None
        """
        for enemy_name, config in self.enemy_general_config.items():
            status_images = config.get("status_images", {})
            status_region = config.get("status_region")

            if not status_region:
                continue

            # 检查该敌军是否有状态图片（说明在场）
            for status_name, status_image_path in status_images.items():
                if status_image_path:
                    # 检查状态图片是否存在
                    status_pos = self.find_image(account_index, status_image_path, status_region, 0)
                    if status_pos:
                        # 找到敌军单位，返回其cast_position
                        cast_position = config.get("cast_position")
                        if cast_position:
                            return cast_position
                        break

        return None

    # 查找技能目标选择图片（lantiao）
    def find_target_lantiao(self, account_index, search_region, timeout=3.0):
        """查找技能目标选择图片（lantiao）
        :param account_index: 账号索引
        :param search_region: 搜索区域
        :param timeout: 超时时间（秒）
        :return: ResXy对象或None
        """
        if not self.target_lantiao_image:
            return None

        dm = self.get_account_dm(account_index)
        if not dm:
            return None

        confidence_levels = [0.9, 0.8, 0.7]  # 识别率递减
        target_pos = None
        start_time = time.time()

        try:
            x, y, w, h = search_region
            # 验证坐标有效性（w和h是结束坐标）
            if w <= x or h <= y:
                return None

            while time.time() - start_time < timeout:
                # 尝试多个识别率
                for confidence in confidence_levels:
                    if time.time() - start_time >= timeout:
                        break

                    pos = dm.FindPicEx(int(x), int(y), int(w), int(h), self.target_lantiao_image, "", confidence, 0)
                    if pos:
                        # 找到图片，解析坐标
                        pos = pos.split("|")
                        pos_res = pos[0].split(",")
                        pics = self.target_lantiao_image.split("|")
                        picSize = dm.GetPicSize(pics[int(pos_res[0])])
                        picSize = picSize.split(",")
                        picW, picH = picSize[0], picSize[1]
                        posX = int(pos_res[1]) + (int(picW) * 0.5)
                        posY = int(pos_res[2]) + (int(picH) * 0.5)
                        target_pos = ResXy(int(posX), int(posY))
                        break
                    time.sleep(0.05)  # 短暂延迟后重试

                if target_pos:
                    break
                time.sleep(0.1)  # 每次循环后稍作延迟
        except Exception:
            return None

        # 如果找到目标，将坐标偏移 x+30, y+60
        if target_pos:
            target_pos.x = target_pos.x + random.randint(25, 30)
            target_pos.y = target_pos.y + random.randint(45, 60)

        return target_pos

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

    # 点击技能并验证是否成功
    def click_skill_with_verification(
        self, account_index, skill_image_path, skill_pos, skill_name="技能", max_retries=1
    ):
        """点击技能并验证是否成功
        :param account_index: 账号索引
        :param skill_image_path: 技能图片路径
        :param skill_pos: 技能位置（ResXy对象）
        :param skill_name: 技能名称（用于日志）
        :param max_retries: 最大重试次数（默认1次）
        :return: True表示点击成功（技能图标已消失），False表示点击失败
        """
        if not skill_pos:
            return False

        # 第一次点击
        self.click_position(account_index, skill_pos.x, skill_pos.y)
        time.sleep(CombatConstants.SKILL_CLICK_VERIFY_DELAY)

        # 验证点击是否成功
        verify_skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
        if not verify_skill_pos:
            # 技能图标已消失，点击成功
            return True

        # 技能图标还在，说明点击失败，进行重试
        for retry_count in range(max_retries):
            self.report_battle_info(
                f"账号{account_index} 释放{skill_name}失败（技能图标仍在），第{retry_count + 1}次重试", "warning"
            )
            self.click_position(account_index, verify_skill_pos.x, verify_skill_pos.y)
            time.sleep(CombatConstants.SKILL_CLICK_VERIFY_DELAY)

            # 再次验证
            verify_skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
            if not verify_skill_pos:
                # 技能图标已消失，点击成功
                return True

        # 所有重试都失败
        self.report_battle_info(
            f"账号{account_index} 释放{skill_name}失败（重试{max_retries}次后技能图标仍在），跳过", "warning"
        )
        return False

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
        skill_pos = self.find_image(account_index, skill_path, self.skill_panel_region, 0)
        if not skill_pos:
            return False
        return self.release_skill_with_target(account_index, skill_name, skill_pos, caller_hint)

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
                # 主角技能和攻击武将技能：使用敌军目标点位
                target_pos = self.enemy_target_position or (104, 344)
                self.click_position(account_index, target_pos[0], target_pos[1])
                char_type = "主角" if skill_type == "main_char" else "武将"
                self.report_battle_info(
                    f"账号{account_index} {char_type}释放{skill_name}，目标位置: {target_pos}", "action"
                )
            elif skill_type == "support":
                # 辅助武将技能：根据技能名称选择目标
                if skill_name in ["加攻击", "加血"]:
                    # 辅助技能：使用友军目标点位
                    target_pos = self.ally_support_target_position or (764, 380)
                    self.click_position(account_index, target_pos[0], target_pos[1])
                    self.report_battle_info(
                        f"账号{account_index} 刘备释放{skill_name}，目标位置: {target_pos}", "action"
                    )
                elif skill_name == "控制":
                    # 控制技能：使用敌军目标点位
                    target_pos = self.enemy_target_position or (104, 344)
                    self.click_position(account_index, target_pos[0], target_pos[1])
                    self.report_battle_info(
                        f"账号{account_index} 刘备释放{skill_name}，目标位置: {target_pos}", "action"
                    )
                elif skill_name == "清除状态":
                    # 清除状态技能：使用需要清除的敌军固定点位
                    if self.enemies_need_clear.get(account_index):
                        # 这个地方需要换成if self.keep_support_general==False:enemy_info = self.enemies_need_clear[account_index][account_index]
                        enemy_info = self.enemies_need_clear[account_index][0]
                        target_pos = enemy_info.get("position") or (104, 344)
                        self.click_position(account_index, target_pos[0], target_pos[1])
                        # 从所有账号的需要清除列表中移除（因为敌军是全局的，一个账号清除后，其他账号就不需要再清除了）
                        # 这里不能清除，而是置为空，需要占位
                        enemy_name = enemy_info.get("enemy_name", "敌军")
                        for account_idx in [0, 1, 2]:
                            if account_idx in self.enemies_need_clear:
                                # 查找并删除匹配的敌军记录（通过enemy_name匹配）
                                self.enemies_need_clear[account_idx] = [
                                    e for e in self.enemies_need_clear[account_idx]
                                    if e.get("enemy_name") != enemy_name
                                ]
                        # 重置播报标记，允许下次检测到时重新播报
                        if enemy_name in self.enemy_status_reported:
                            del self.enemy_status_reported[enemy_name]
                        self.report_battle_info(
                            f"账号{account_index} 刘备释放{skill_name}清除{enemy_name}状态，目标位置: {target_pos}（已从所有账号清除列表中移除）",
                            "action",
                        )
                        # 一次性模式：检查是否所有敌军都清完了，是则关开关回6曹操
                        if not self.enable_persistent_liubei:
                            all_cleared = True
                            for i in [0, 1, 2]:
                                if self.enemies_need_clear.get(i):
                                    all_cleared = False
                                    break
                            if all_cleared:
                                self.keep_support_general = False
                                self.report_battle_info(
                                    "所有敌军状态清除完毕，恢复6曹操模式", "system"
                                )
                    else:
                        # 没有需要清除的敌军，使用默认位置
                        target_pos = self.enemy_target_position or (104, 344)
                        self.click_position(account_index, target_pos[0], target_pos[1])
                        self.report_battle_info(
                            f"账号{account_index} 刘备释放{skill_name}，目标位置: {target_pos}", "action"
                        )

            if skill_name == "加攻击" and skill_type == "support":
                self.attack_buff_tracker[account_index] = 3

            time.sleep(CombatConstants.ACTION_DELAY)
            return True
        except Exception as e:
            self.report_battle_info(f"账号{account_index} 释放技能{skill_name}时发生异常: {e}", "error")
            return False

    def summon_general_with_verification(self, account_index, general_name):
        """召唤武将并验证是否成功
        :param account_index: 账号索引
        :param general_name: 武将名称
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
        while time.time() - start_time < 2.0:
            general_pos = self.find_image(account_index, general_path, self.summon_panel_region, 0)
            if general_pos:
                break
            time.sleep(0.1)

        if not general_pos:
            self.report_battle_info(f"账号{account_index} 查找武将{general_name}图片超时（2秒）", "warning")
            return False

        # 3. 点击武将并验证（背包武将消失即表示召唤成功）
        if not self.click_with_verification(
            account_index, general_path, general_pos, self.summon_panel_region, f"武将{general_name}", max_retries=2
        ):
            return False
        time.sleep(0.1)
        if self.beidong_huihe >= 5 and self.zhaohuan_index == account_index:
            pos = self.unit_positions[account_index]["generals"][0][1:]
            self.click_position(account_index, pos[0], pos[1])
            self.beidong_huihe = 0
            if self.zhaohuan_index < 2:
                self.zhaohuan_index += 1
            else:
                self.zhaohuan_index = 0
        else:
            self.click_position(account_index, 12, 12)
        # 4. 更新武将信息（召唤成功后，背包武将已消失）
        char_info = self.unit_info[account_index]["main_char"]

        # 检查武将数量是否已经达到上限（2个）
        alive_generals = [g for g in char_info.get("generals", []) if g.get("alive", True)]
        # if len(alive_generals) >= 2:
        #     self.report_battle_info(f"账号{account_index} 武将数量已达上限（2个），不允许召唤", "warning")
        #     return False

        general_count = len(alive_generals)

        # 确定召唤位置（根据当前存活武将数量）
        if general_count == 0:
            # 第一个武将位置
            if account_index == 0:
                summon_target_pos = (572, 380)  # 账号0武将1位置（中间排）
            elif account_index == 1:
                summon_target_pos = (530, 278)  # 账号1武将1位置（上排）
            else:  # account_index == 2
                summon_target_pos = (520, 490)  # 账号2武将1位置（下排）
        else:
            # 第二个武将位置
            if account_index == 0:
                summon_target_pos = (667, 380)  # 账号0武将2位置（中间排）
            elif account_index == 1:
                summon_target_pos = (626, 278)  # 账号1武将2位置（上排）
            else:  # account_index == 2
                summon_target_pos = (626, 490)  # 账号2武将2位置（下排）

        new_general = {
            "name": general_name,
            "position": summon_target_pos,
            "alive": False,  # 召唤后标记为死亡，等待下一回合检测蓝条确认
            "reviving": True,  # 标记为复活中，数量不变
            "deployed_turn": self.current_turn,
            "account_index": account_index,
        }
        char_info["generals"].append(new_general)
        # 召唤后状态为复活中，数量不变（不更新general_count）
        self.unit_info[account_index]["generals"].append(new_general)

        # 召唤成功后，从全局阵亡记录中移除当前账号的所有武将记录（避免重复召唤）
        # 因为召唤成功意味着可以替换阵亡的武将，所以移除该账号的所有武将记录
        with self._state_lock:
            for dead_gen in self.global_dead_units["generals"][:]:
                if dead_gen.get("account_index") == account_index:
                    # 移除该账号的所有武将记录（因为召唤成功意味着可以替换阵亡的武将）
                    self.global_dead_units["generals"].remove(dead_gen)

        self.report_battle_info(
            f"账号{account_index} 召唤{general_name}成功（状态：复活中，武将数量不变: {char_info.get('general_count', 2)}）",
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
                    "general_count": 2,  # 默认每个账号有2个武将
                    "generals": [],
                    "deployed_turn": 0,
                },
                "generals": [],  # 格式: [{'name': '刘备', 'position': (x, y), 'alive': True, 'deployed_turn': 0, 'account_index': i}, ...]
            }
            self.dead_units[i] = {
                "main_char": None,  # 格式: {'name': '主角', 'position': (x, y), 'account_index': i} 或 None
                "generals": [],
            }  # 格式: {'main_char': {...} 或 None, 'generals': [...]}
            self.enemies_need_clear[i] = (
                []
            )  # 格式: [{'enemy_name': '刘备', 'position': (x, y), 'account_index': i}, ...]
            self.skill_cd[i] = {}
            self.pending_liubei_summon[i] = (
                None  # 待召唤刘备记录：None 或 {'target_account_index': int, 'target_char_index': int, 'target_char_info': dict}
            )
            self.liubei_skill_index[i] = 0  # 初始化刘备技能索引
            self.liubei_skill_cd[i] = {}  # 初始化刘备技能冷却记录
            self.low_hp_units[i] = []  # 初始化血量低的单位列表
            self.zhugeliang_found[i] = False  # 初始化诸葛亮单位标记
            self.zhugeliang_status1_missing_count[i] = 0  # 初始化诸葛亮状态1缺失计数
            self.zhugeliang_status2_missing_count[i] = 0  # 初始化诸葛亮状态2缺失计数
            # 初始化账号区域映射(每个账号检测自己主角和武将的区域)
            if i not in self.hp_bar_unit_mapping:
                self.hp_bar_unit_mapping[i] = {}
                # 映射9个血量条区域到单位
                # 区域索引映射：账号1主角(0), 账号0主角(1), 账号2主角(2),
                #               账号1武将1(3), 账号0武将1(4), 账号2武将1(5),
                #               账号1武将2(6), 账号0武将2(7), 账号2武将2(8)
                if i == 0:
                    # 账号0（中间排）：主角在region 1，武将1在region 4，武将2在region 7
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
                    # 账号1（上排）：主角在region 0，武将1在region 3，武将2在region 6
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
                    # 账号2（下排）：主角在region 2，武将1在region 5，武将2在region 8
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

    # 检测墓碑(检测阵亡)
    def check_tombstones(self, account_index, is_operation_round=False, detect_account_index=None):
        """检测指定账号的墓碑,返回阵亡单位列表
        判定死亡需要同时满足两个条件：
        1. 检测到墓碑
        2. 在对应区域找不到lantiao.bmp图片（说明单位确实不在场）

        新增逻辑：如果连续十五次检测没有找到蓝条图片，也判定为死亡（按检测次数，而非回合）

        :param account_index: 账号索引（要检测的账号）
        :param is_operation_round: 是否在操作回合中（默认False）
        :param detect_account_index: 用于检测的大漠对象索引（如果为None则使用account_index）
        """
        # 如果未指定检测账号，使用account_index
        if detect_account_index is None:
            detect_account_index = account_index
        dead_list = []
        # 遍历9个血量条区域检测墓碑
        # 默认每个账号有2个武将，检测所有区域
        for region_idx, region in enumerate(self.hp_bar_regions):
            # 在对应区域查找lantiao.bmp图片（使用detect_account_index进行检测）
            lantiao_pos = self.find_image(detect_account_index, self.target_lantiao_image, region, 0)

            # 跟踪连续未找到蓝条的检测次数（按检测次数，而非回合）
            # 条件：需要在第一个回合之后，并且在非我方操作回合才检测
            is_first_turn = self.current_turn == 0 or self.current_turn == 1
            should_track_missing = (not is_first_turn) and (not is_operation_round)

            key = (account_index, region_idx)
            if lantiao_pos:
                # 找到蓝条，重置计数
                if key in self.lantiao_missing_rounds:
                    del self.lantiao_missing_rounds[key]
                # 如果找到蓝条，立即更新单位状态为存活（无论之前是什么状态）
                if account_index in self.hp_bar_unit_mapping:
                    if region_idx in self.hp_bar_unit_mapping[account_index]:
                        unit_type, unit_name, position = self.hp_bar_unit_mapping[account_index][region_idx]
                        if unit_type == "main_char":
                            # 主角：检测到蓝条，立即更新为存活
                            with self._state_lock:
                                if account_index in self.unit_info:
                                    char_info = self.unit_info[account_index]["main_char"]
                                    old_alive = char_info.get("alive", False)
                                    # 如果之前是死亡状态，现在检测到蓝条，立即更新为存活
                                    if not old_alive:
                                        char_info["alive"] = True
                                        char_info["revive_pending_verification"] = False
                                        char_info["reviving"] = False
                                        char_info["need_revive"] = False
                                        # 从全局阵亡记录中移除（如果存在）
                                        for dead_char in self.global_dead_units["main_chars"][:]:
                                            if dead_char.get("account_index") == account_index:
                                                self.global_dead_units["main_chars"].remove(dead_char)
                                                break
                                        self.report_battle_info(
                                            f"账号{account_index} 主角检测到蓝条，状态更新为存活", "success"
                                        )
                                    # 如果之前在复活中，确认复活成功（已在锁内，使用无锁版本）
                                    elif char_info.get("revive_pending_verification", False) or char_info.get(
                                        "reviving", False
                                    ):
                                        self._confirm_revive_success_unlocked(account_index)
                        elif unit_type == "general":
                            # 武将：检测到蓝条，立即更新为存活
                            with self._state_lock:
                                char_info = self.unit_info[account_index]["main_char"]
                                for gen in char_info.get("generals", []):
                                    if gen.get("name") == unit_name or gen.get("position") == position:
                                        old_alive = gen.get("alive", True)
                                        # 如果之前是死亡状态，现在检测到蓝条，立即更新为存活
                                        if not old_alive:
                                            gen["alive"] = True
                                            gen["reviving"] = False
                                            # 加数量（已在锁内，使用无锁版本）
                                            self._update_general_count_on_revive_success_unlocked(account_index)
                                            # 从全局阵亡记录中移除（如果存在）
                                            for dead_gen in self.global_dead_units["generals"][:]:
                                                if (
                                                    dead_gen.get("name") == unit_name
                                                    and dead_gen.get("account_index") == account_index
                                                    and dead_gen.get("position") == position
                                                ):
                                                    self.global_dead_units["generals"].remove(dead_gen)
                                                    break
                                            self.report_battle_info(
                                                f"账号{account_index} 武将{unit_name}检测到蓝条，状态更新为存活",
                                                "success",
                                            )
                                        # 如果之前在复活中，确认复活成功
                                        elif gen.get("reviving", False):
                                            gen["alive"] = True
                                            gen["reviving"] = False
                                            # 加数量（已在锁内，使用无锁版本）
                                            self._update_general_count_on_revive_success_unlocked(account_index)
                                            self.report_battle_info(
                                                f"账号{account_index} 武将{unit_name}复活成功（检测到蓝条）", "success"
                                            )
                                        break
            else:
                # 没找到蓝条，只有在满足条件时才增加计数
                if should_track_missing:
                    if key not in self.lantiao_missing_rounds:
                        self.lantiao_missing_rounds[key] = 0
                    self.lantiao_missing_rounds[key] += 1

                    # 如果连续十五次检测没有找到蓝条，判定为死亡
                    if self.lantiao_missing_rounds[key] >= 4:
                        # 根据区域索引确定是哪个单位
                        if account_index in self.hp_bar_unit_mapping:
                            if region_idx in self.hp_bar_unit_mapping[account_index]:
                                unit_type, unit_name, position = self.hp_bar_unit_mapping[account_index][region_idx]

                                # 检查该区域内是否有被动复活图片，如果有则说明正在被动复活，不标记为死亡
                                fuhuobeidong_pos = self.find_image(
                                    detect_account_index, self.target_fuhuobeidong_image, region, 0
                                )
                                if fuhuobeidong_pos:
                                    # 找到被动复活图片，说明单位正在被动复活，不标记为死亡，重置计数
                                    if key in self.lantiao_missing_rounds:
                                        del self.lantiao_missing_rounds[key]
                                    continue

                                # 统一处理死亡逻辑（主角和武将都一样）
                                if unit_type == "main_char":
                                    # 主角：超过15次未检测到蓝条，视为死亡
                                    with self._state_lock:
                                        char_info = self.unit_info[account_index]["main_char"]
                                        # 如果正在复活中，下一回合没检测到蓝条，状态更新为死亡
                                        if char_info.get("reviving", False) or char_info.get(
                                            "revive_pending_verification", False
                                        ):
                                            self._confirm_revive_failure(account_index)
                                        # 如果之前是存活的，现在判定为死亡
                                        elif char_info.get("alive", True):
                                            # 清除所有复活相关标记（确保状态正确）
                                            old_reviving = char_info.get("reviving", False)
                                            old_revive_pending = char_info.get("revive_pending_verification", False)
                                            char_info["reviving"] = False
                                            if "reviving_timestamp" in char_info:
                                                del char_info["reviving_timestamp"]
                                            char_info["revive_pending_verification"] = False
                                            char_info["alive"] = False
                                            char_info["need_revive"] = True

                                            # 如果之前reviving为True，记录警告信息
                                            if old_reviving or old_revive_pending:
                                                self.report_battle_info(
                                                    f"账号{account_index} 主角死亡（超过15次未检测到蓝条，清除reviving标记，之前状态：reviving={old_reviving}, revive_pending={old_revive_pending}）",
                                                    "warning",
                                                )

                                            # 添加到全局阵亡记录
                                            dead_char_info = {
                                                "name": char_info.get("name", "主角"),
                                                "position": char_info.get("position", (793, 380)),
                                                "account_index": account_index,
                                            }
                                            # 检查是否已在全局记录中
                                            already_in_global = False
                                            for dead_char in self.global_dead_units["main_chars"]:
                                                if dead_char.get("account_index") == account_index:
                                                    already_in_global = True
                                                    break
                                            if not already_in_global:
                                                self.global_dead_units["main_chars"].append(dead_char_info)
                                            self.dead_units[account_index]["main_char"] = dead_char_info
                                            self.report_battle_info(
                                                f"账号{account_index} 主角死亡", "warning"
                                            )
                                elif unit_type == "general":
                                    # 武将：如果正在复活中，下一回合没检测到蓝条，状态更新为死亡，数量不变
                                    with self._state_lock:
                                        char_info = self.unit_info[account_index]["main_char"]
                                        found_general = False
                                        for gen in char_info.get("generals", []):
                                            if gen.get("name") == unit_name or gen.get("position") == position:
                                                found_general = True
                                                if gen.get("reviving", False):
                                                    gen["alive"] = False
                                                    gen["reviving"] = False
                                                    self.report_battle_info(
                                                        f"账号{account_index} 武将{unit_name}复活失败（下一回合未检测到蓝条），状态更新为死亡，数量不变",
                                                        "warning",
                                                    )
                                                # 如果之前是存活的，现在判定为死亡
                                                elif gen.get("alive", True):
                                                    gen["alive"] = False
                                                    # 添加到全局阵亡记录
                                                    dead_general_info = {
                                                        "name": unit_name,
                                                        "position": position,
                                                        "account_index": account_index,
                                                    }
                                                    # 检查是否已在全局记录中
                                                    already_in_global = False
                                                    for dead_gen in self.global_dead_units["generals"]:
                                                        if (
                                                            dead_gen.get("name") == unit_name
                                                            and dead_gen.get("account_index") == account_index
                                                            and dead_gen.get("position") == position
                                                        ):
                                                            already_in_global = True
                                                            break
                                                    if not already_in_global:
                                                        self.global_dead_units["generals"].append(dead_general_info)
                                                    self.dead_units[account_index]["generals"].append(dead_general_info)
                                                    # 武将死亡，立即减数量（已在锁内，使用无锁版本）
                                                    self._update_general_count_on_death_unlocked(account_index)
                                                    self.report_battle_info(
                                                        f"账号{account_index} 武将{unit_name}死亡",
                                                        "warning",
                                                    )
                                                break

                                        # 如果武将在列表中不存在，也要添加到死亡记录中（可能是第一回合的初始武将还没有被识别）
                                        if not found_general:
                                            # 检查是否已在全局记录中
                                            already_in_global = False
                                            for dead_gen in self.global_dead_units["generals"]:
                                                if (
                                                    dead_gen.get("name") == unit_name
                                                    and dead_gen.get("account_index") == account_index
                                                    and dead_gen.get("position") == position
                                                ):
                                                    already_in_global = True
                                                    break

                                            if not already_in_global:
                                                # 添加到全局阵亡记录
                                                dead_general_info = {
                                                    "name": unit_name,
                                                    "position": position,
                                                    "account_index": account_index,
                                                }
                                                self.global_dead_units["generals"].append(dead_general_info)
                                                self.dead_units[account_index]["generals"].append(dead_general_info)
                                                # 武将死亡，立即减数量（已在锁内，使用无锁版本）
                                                self._update_general_count_on_death_unlocked(account_index)
                                                self.report_battle_info(
                                                    f"账号{account_index} 武将{unit_name}死亡（超过7次未检测到蓝条，武将不在列表中）",
                                                    "warning",
                                                )

                                # 检查是否已经在dead_list中（避免重复添加）
                                already_added = False
                                for dead_unit in dead_list:
                                    if (
                                        dead_unit["account_index"] == account_index
                                        and dead_unit["region_index"] == region_idx
                                    ):
                                        already_added = True
                                        break
                                if not already_added:
                                    dead_list.append(
                                        {
                                            "account_index": account_index,
                                            "unit_type": unit_type,
                                            "unit_name": unit_name,
                                            "position": position,
                                            "region_index": region_idx,
                                        }
                                    )

            # 原有逻辑：检测墓碑
            # 在区域内查找墓碑图片（使用detect_account_index进行检测）
            x, y, w, h = region
            tombstone_pos = self.find_image(
                detect_account_index, self.tombstone_image, (x, int(y + 40), w, int(h + 110)), 0
            )
            if tombstone_pos:
                # 找到墓碑，还需要检查对应区域是否找不到lantiao.bmp图片
                # 如果找不到lantiao图片，说明单位确实不在场，判定为死亡
                if not lantiao_pos:
                    # 找到墓碑且找不到lantiao图片,根据区域索引确定是哪个单位
                    if account_index in self.hp_bar_unit_mapping:
                        if region_idx in self.hp_bar_unit_mapping[account_index]:
                            unit_type, unit_name, position = self.hp_bar_unit_mapping[account_index][region_idx]

                            # 检查该区域内是否有被动复活图片，如果有则说明正在被动复活，不标记为死亡
                            fuhuobeidong_pos = self.find_image(
                                detect_account_index, self.target_fuhuobeidong_image, region, 0
                            )
                            if fuhuobeidong_pos:
                                # 找到被动复活图片，说明单位正在被动复活，不标记为死亡
                                # 同时重置蓝条缺失计数（如果存在）
                                if key in self.lantiao_missing_rounds:
                                    del self.lantiao_missing_rounds[key]
                                continue

                            # 检查是否已经在dead_list中（避免重复添加）
                            already_added = False
                            for dead_unit in dead_list:
                                if (
                                    dead_unit["account_index"] == account_index
                                    and dead_unit["region_index"] == region_idx
                                ):
                                    already_added = True
                                    break
                            if not already_added:
                                dead_list.append(
                                    {
                                        "account_index": account_index,
                                        "unit_type": unit_type,
                                        "unit_name": unit_name,
                                        "position": position,
                                        "region_index": region_idx,
                                    }
                                )
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
        """在我方回合开始时，由大漠对象0识别攻击目标点位和友军辅助技能目标点位"""
        # 如果已经检测过，直接返回（避免重复检测）
        if self.target_positions_detected:
            return

        dm_index = 0
        dm = self.get_account_dm(dm_index)
        if not dm:
            return

        # 1. 检测敌军攻击目标点位（在敌军区域内识别）
        target_pos = self.find_image(dm_index, self.target_lantiao_image, self.enemy_region, 0)
        if target_pos:
            # 调整坐标（根据实际游戏情况调整）
            target_pos.x = target_pos.x + 25
            target_pos.y = target_pos.y + 80
            self.enemy_target_position = (target_pos.x, target_pos.y)
        else:
            # 如果没找到，使用默认位置
            if not self.enemy_target_position:
                self.enemy_target_position = (104, 344)  # 默认位置

        # 2. 检测我军辅助技能施法点位（在我军区域内识别）
        ally_target_pos = self.find_image(dm_index, self.target_lantiao_image, self.ally_region, 0)
        if ally_target_pos:
            # 调整坐标（根据实际游戏情况调整）
            ally_target_pos.x = ally_target_pos.x + 18
            ally_target_pos.y = ally_target_pos.y + 83
            self.ally_support_target_position = (ally_target_pos.x, ally_target_pos.y)
            # self.report_battle_info(f"我方回合，检测到我军辅助技能施法点位: {self.ally_support_target_position}", "info")
        else:
            # 如果没找到，使用默认位置
            if not self.ally_support_target_position:
                self.ally_support_target_position = (764, 380)  # 默认我军中心位置
                

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
                if self.liubei_missing_count >= 4:
                    if self.has_liubei_on_field:
                        self.has_liubei_on_field = False
        if self.beidong_huihe == 0:
            liubei_beidong = self.find_image(account_index, self.tiandihudun_image, self.ally_region, 0)
            if liubei_beidong:
                self.beidong_huihe = 1

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

        # 初始化记录字典（不清空已有记录，避免清除操作前记录被清空）
        for account_idx in [0, 1, 2]:
            if account_idx not in self.enemies_need_clear:
                self.enemies_need_clear[account_idx] = []

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
                if not self.keep_support_general:
                    xuetiao_is_found = self.find_image(dm_index, self.zhugexuetiao_image, status_region, 0)
                    if xuetiao_is_found:
                        self.keep_support_general = True
                        self.beidong_huihe = 5
                status1_image = status_images.get("状态1")
                status2_image = status_images.get("状态2")

                # 先检测状态2
                status2_found = False
                if status2_image:
                    status2_pos = self.find_image(dm_index, status2_image, status_region, 0)
                    status2_found = status2_pos is not None

                # 更新所有账号的计数
                for account_idx in [0, 1, 2]:
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
                        if self.zhugeliang_status1_missing_count[account_idx] >= 4:
                            self.clear_zhugeliang = True
                            # if not self.keep_support_general:
                            #     self.keep_support_general = True
                            #     self.beidong_huihe = 5
                            # 检查是否已记录（避免重复）
                            already_recorded = False
                            if account_idx in self.enemies_need_clear:
                                for enemy_info in self.enemies_need_clear[account_idx]:
                                    if enemy_info["enemy_name"] == enemy_key:
                                        already_recorded = True
                                        break

                            if not already_recorded:
                                if account_idx not in self.enemies_need_clear:
                                    self.enemies_need_clear[account_idx] = []
                                self.enemies_need_clear[account_idx].insert(
                                    0,
                                    {
                                        "enemy_name": enemy_key,
                                        "position": cast_position,
                                        "status_name": "状态1",
                                    }
                                )
                                # 只在第一次检测到时播报
                                if enemy_key not in self.enemy_status_reported:
                                    self.report_battle_info(
                                        f"检测到敌军{enemy_key}需要清除状态",
                                        "warning",
                                    )
                                    self.enemy_status_reported[enemy_key] = True
                            # already_recorded = False
                            # if account_idx in self.enemies_need_clear:
                            #     for enemy_info in self.enemies_need_clear[account_idx]:
                            #         if enemy_info["enemy_name"] == enemy_key:
                            #             already_recorded = True
                            #             break

                            # # 确保把最新检测到的条目放在首位（移除已有同名记录后插入）
                            # if account_idx not in self.enemies_need_clear:
                            #     self.enemies_need_clear[account_idx] = []
                            # # 删除同名记录（若存在）
                            # self.enemies_need_clear[account_idx] = [
                            #     e for e in self.enemies_need_clear[account_idx]
                            #     if e.get("enemy_name") != enemy_key
                            # ]
                            # # 插入到首位
                            # self.enemies_need_clear[account_idx].insert(
                            #     0,
                            #     {
                            #         "enemy_name": enemy_key,
                            #         "position": cast_position,
                            #         "status_name": "状态1",
                            #     }
                            # )
                            # # 只在第一次检测到时播报
                            # if enemy_key not in self.enemy_status_reported:
                            #     self.report_battle_info(
                            #         f"检测到敌军{enemy_key}需要清除状态，固定点位: {cast_position}",
                            #         "warning",
                            #     )
                            #     self.enemy_status_reported[enemy_key] = True
                    else:
                        # 没找到状态2，重置状态1计数（不检测状态1）
                        self.zhugeliang_status1_missing_count[account_idx] = 0
            else:
                # 其他武将：找到状态图片就返回需要清除
                for status_name, status_image in status_images.items():
                    status_pos = self.find_image(dm_index, status_image, status_region, 0)
                    if status_pos:
                        # 检测到状态，在6曹操阵容下需要开始召唤刘备
                        if not self.keep_support_general:
                            self.keep_support_general = True
                            self.beidong_huihe = 5
                        # 检查是否已记录（避免重复）
                        already_recorded = False
                        # 检查所有账号是否已记录
                        for account_idx in [0, 1, 2]:
                            if account_idx in self.enemies_need_clear:
                                for enemy_info in self.enemies_need_clear[account_idx]:
                                    if enemy_info["enemy_name"] == enemy_key:
                                        already_recorded = True
                                        break
                            if already_recorded:
                                break

                        if not already_recorded:
                            # 记录到所有账号（因为敌军是全局的），并确保最新在首位（去重后插入）
                            for account_idx in [0, 1, 2]:
                                if account_idx not in self.enemies_need_clear:
                                    self.enemies_need_clear[account_idx] = []
                                # 删除同名记录
                                self.enemies_need_clear[account_idx] = [
                                    e for e in self.enemies_need_clear[account_idx]
                                    if e.get("enemy_name") != enemy_key
                                ]
                                # 插入到首位
                                self.enemies_need_clear[account_idx].insert(
                                    0,
                                    {
                                        "enemy_name": enemy_key,
                                        "position": cast_position,
                                        "status_name": status_name,
                                    }
                                )
                            # 只在第一次检测到时播报
                            if enemy_key not in self.enemy_status_reported:
                                self.report_battle_info(
                                    f"检测到敌军{enemy_key}需要清除状态",
                                    "warning",
                                )
                                self.enemy_status_reported[enemy_key] = True
                        break
        # 多敌军并行清除：按存活账号分配清除任务
        self._distribute_enemies_to_accounts()

    def _distribute_enemies_to_accounts(self):
        """将需要清除的敌军按存活账号平均分配，实现多刘备并行清除"""
        all_enemies = []
        seen = set()
        for i in [0, 1, 2]:
            if i in self.enemies_need_clear:
                for e in self.enemies_need_clear[i]:
                    name = e.get("enemy_name", "")
                    if name and name not in seen:
                        seen.add(name)
                        all_enemies.append(e)

        if len(all_enemies) <= 1:
            return

        available = []
        for i in [0, 1, 2]:
            if i in self.unit_info:
                char = self.unit_info[i]["main_char"]
                if char.get("alive", False) and self.has_liubei.get(i, False):
                    available.append(i)

        if not available:
            self.enemies_need_clear[0] = list(all_enemies)
            for i in [1, 2]:
                self.enemies_need_clear[i] = []
            return

        for i in [0, 1, 2]:
            self.enemies_need_clear[i] = []

        for idx, enemy in enumerate(all_enemies):
            account = available[idx % len(available)]
            self.enemies_need_clear[account].append(enemy)

        self.report_battle_info(
            f"敌军清除任务已分配: " + ", ".join(
                f"账号{i}: {[e['enemy_name'] for e in self.enemies_need_clear[i]]}"
                for i in available
            ),
            "system",
        )

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
                for general_info in self.unit_info[account_idx]["generals"]:
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
                        char_info = self.unit_info[account_idx]["main_char"]
                        old_reviving = char_info.get("reviving", False)
                        if old_reviving:
                            # 已经在全局记录中，但reviving=True，说明状态异常，清除reviving标志
                            char_info["reviving"] = False
                            if "reviving_timestamp" in char_info:
                                del char_info["reviving_timestamp"]
                        continue

                    # 更新单位信息（每个账号只有1个主角）
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

                    # 如果之前reviving为True，记录警告信息
                    if old_reviving:
                        self.report_battle_info(
                            f"账号{account_idx} {unit_name}阵亡（检测到墓碑，强制清除reviving标记）",
                            "warning",
                        )

                    # 之前是存活的,现在阵亡了，添加到全局记录
                    # 添加到全局阵亡记录（所有账号共享）- 必须在清除reviving之后立即添加，保证原子性
                    dead_char_info = {"name": unit_name, "position": position, "account_index": account_idx}
                    self.global_dead_units["main_chars"].append(dead_char_info)

                    # 也添加到本地记录（用于兼容旧代码）
                    self.dead_units[account_idx]["main_char"] = dead_char_info

                    self.report_battle_info(f"账号{account_idx} {unit_name}阵亡（检测到墓碑）", "warning")
            elif unit_type == "general":
                # 武将阵亡（检测到墓碑）- 统一处理死亡逻辑
                with self._state_lock:
                    # 先检查全局记录，避免重复
                    already_in_global = False
                    for dead_general in self.global_dead_units["generals"]:
                        if (
                            dead_general.get("name") == unit_name
                            and dead_general.get("account_index") == account_idx
                            and dead_general.get("position") == position
                        ):
                            already_in_global = True
                            break

                    # 更新单位信息
                    found_general = False
                    for general_info in self.unit_info[account_idx]["generals"]:
                        if general_info.get("name") == unit_name or general_info.get("position") == position:
                            found_general = True
                            if general_info.get("alive", True):
                                general_info["alive"] = False

                                # 如果武将正在复活中，说明召唤失败，清除复活中状态
                                if general_info.get("reviving", False):
                                    general_info["reviving"] = False

                                # 如果已经在全局记录中，确保状态正确，但不重复添加
                                if already_in_global:
                                    # 从对应主角的武将列表中移除（每个账号只有1个主角）
                                    char_info = self.unit_info[account_idx]["main_char"]
                                    found_in_char = False
                                    # 使用更宽松的匹配方式：通过name或position匹配
                                    for gen in char_info["generals"]:
                                        if (
                                            gen.get("name") == general_info.get("name", unit_name)
                                            or gen.get("position") == position
                                        ):
                                            # 如果武将正在复活中，说明召唤失败，清除复活中状态
                                            if gen.get("reviving", False):
                                                gen["reviving"] = False
                                            char_info["generals"].remove(gen)
                                            # 武将死亡，立即减数量（已在锁内，使用无锁版本）
                                            self._update_general_count_on_death_unlocked(account_idx)
                                            found_in_char = True
                                            break

                                    if not found_in_char:
                                        self.report_battle_info(
                                            f"账号{account_idx} 警告：武将{general_info.get('name', unit_name)}再次阵亡，但未在主角的武将列表中找到，无法更新general_count",
                                            "warning",
                                        )

                                    # 从武将列表中移除
                                    if general_info in self.unit_info[account_idx]["generals"]:
                                        self.unit_info[account_idx]["generals"].remove(general_info)

                                    self.report_battle_info(
                                        f"账号{account_idx} {general_info.get('name', unit_name)}再次阵亡（已在全局记录中）",
                                        "warning",
                                    )
                                else:
                                    # 不在全局记录中，正常添加
                                    # 添加到全局阵亡记录（所有账号共享）
                                    dead_general_info = {
                                        "name": general_info.get("name", unit_name),
                                        "position": position,
                                        "account_index": account_idx,
                                    }
                                    self.global_dead_units["generals"].append(dead_general_info)

                                    # 也添加到本地记录（用于兼容旧代码）
                                    self.dead_units[account_idx]["generals"].append(dead_general_info)

                                    self.report_battle_info(
                                        f"账号{account_idx} {general_info.get('name', unit_name)}阵亡（检测到墓碑）",
                                        "warning",
                                    )

                                    # 从对应主角的武将列表中移除（每个账号只有1个主角）
                                    char_info = self.unit_info[account_idx]["main_char"]
                                    found_in_char = False
                                    # 使用更宽松的匹配方式：通过name或position匹配
                                    for gen in char_info["generals"]:
                                        if (
                                            gen.get("name") == general_info.get("name", unit_name)
                                            or gen.get("position") == position
                                        ):
                                            # 如果武将正在复活中，说明召唤失败，清除复活中状态
                                            if gen.get("reviving", False):
                                                gen["reviving"] = False
                                            char_info["generals"].remove(gen)
                                            # 武将死亡，立即减数量（已在锁内，使用无锁版本）
                                            self._update_general_count_on_death_unlocked(account_idx)
                                            found_in_char = True
                                            break

                                    if not found_in_char:
                                        self.report_battle_info(
                                            f"账号{account_idx} 警告：武将{general_info.get('name', unit_name)}阵亡，但未在主角的武将列表中找到，无法更新general_count",
                                            "warning",
                                        )

                                    # 从武将列表中移除
                                    if general_info in self.unit_info[account_idx]["generals"]:
                                        self.unit_info[account_idx]["generals"].remove(general_info)
                            break

                    # 如果武将在列表中不存在，也要添加到死亡记录中（可能是第一回合的初始武将还没有被识别）
                    if not found_general and not already_in_global:
                        # 添加到全局阵亡记录
                        dead_general_info = {
                            "name": unit_name,
                            "position": position,
                            "account_index": account_idx,
                        }
                        self.global_dead_units["generals"].append(dead_general_info)

                        # 也添加到本地记录
                        self.dead_units[account_idx]["generals"].append(dead_general_info)

                        # 武将死亡，立即减数量（已在锁内，使用无锁版本）
                        self._update_general_count_on_death_unlocked(account_idx)

                        self.report_battle_info(
                            f"账号{account_idx} 武将{unit_name}阵亡（检测到墓碑，武将不在列表中）", "warning"
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
            timeout = 2.0
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
            timeout = 2.0
            heal_item_pos = None

            # 尝试多个搜索区域：先尝试道具面板区域，如果找不到则尝试全屏
            search_regions = [
                self.item_panel_region,  # 道具面板区域
                (0, 0, 900, 580),  # 全屏区域（作为备选）
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
                    time.sleep(0.1)  # 每个区域查找间隔0.1秒
                if heal_item_pos:
                    break
                time.sleep(0.1)  # 每次循环间隔0.2秒

            if not heal_item_pos:
                self.report_battle_info(
                    f"账号{account_index} 道具面板中未找到恢复药（2秒超时），图片路径：{heal_item_image}", "error"
                )
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
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 使用恢复药失败: {e}", "error")
            return False

    # ==================== 武将数量管理函数 ====================
    def _update_general_count_on_death(self, account_index):
        """武将死亡时更新数量：减1（带锁，供外部调用）
        :param account_index: 账号索引
        """
        with self._state_lock:
            self._update_general_count_on_death_unlocked(account_index)

    def _update_general_count_on_death_unlocked(self, account_index):
        """武将死亡时更新数量：减1（不带锁，供锁内调用）
        :param account_index: 账号索引
        """
        if account_index in self.unit_info:
            char_info = self.unit_info[account_index]["main_char"]
            current_count = char_info.get("general_count", 2)
            if current_count > 0:
                char_info["general_count"] = current_count - 1
                self.report_battle_info(
                    f"账号{account_index} 武将死亡，武将数量: {current_count} -> {char_info['general_count']}", "info"
                )

    def _update_general_count_on_revive_success(self, account_index):
        """检测到蓝条确认复活成功时更新数量：加1（带锁，供外部调用）
        :param account_index: 账号索引
        """
        with self._state_lock:
            self._update_general_count_on_revive_success_unlocked(account_index)

    def _update_general_count_on_revive_success_unlocked(self, account_index):
        """检测到蓝条确认复活成功时更新数量：加1（不带锁，供锁内调用）
        :param account_index: 账号索引
        """
        if account_index in self.unit_info:
            char_info = self.unit_info[account_index]["main_char"]
            current_count = char_info.get("general_count", 0)
            if current_count < 2:
                char_info["general_count"] = current_count + 1
                self.report_battle_info(
                    f"账号{account_index} 武将复活成功（检测到蓝条），武将数量: {current_count} -> {char_info['general_count']}",
                    "info",
                )

    def _update_main_char_count_on_revive_success(self, account_index):
        """主角复活成功时更新数量：加1（主角数量从0到1）
        :param account_index: 账号索引
        """
        # 主角数量逻辑：alive=True表示数量为1，alive=False表示数量为0
        # 这里不需要单独的数量字段，因为主角只有1个
        # 但为了统一管理，可以添加一个标记
        pass  # 主角数量固定为0或1，不需要单独管理

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

    def _try_revive_main_chars(self, account_index, dead_main_chars, turn_start_time, turn_timeout, sleep_time=0.1):
        """尝试复活主角（辅助函数，避免代码重复）
        :param account_index: 当前操作的账号索引
        :param dead_main_chars: 需要复活的主角列表（已经在函数开头过滤过，不需要再次检查）
        :param turn_start_time: 回合开始时间
        :param turn_timeout: 回合超时时间
        :param sleep_time: 成功后的等待时间
        :return: True表示成功复活了一个主角，False表示没有复活
        """
        if not dead_main_chars or time.time() - turn_start_time >= turn_timeout:
            return False

        for dead_char in dead_main_chars:
            if time.time() - turn_start_time >= turn_timeout:
                break
            dead_char_account = dead_char.get("account_index", account_index)
            # 直接尝试复活（状态检查在 _check_and_mark_reviving 内部处理，保证线程安全）
            if self._check_and_mark_reviving(dead_char_account, dead_char["name"]):
                if self.revive_main_char_with_target(account_index, dead_char_account):
                    time.sleep(sleep_time)
                    return True
                else:
                    # 复活失败，清除reviving标记（防止reviving标志残留）
                    with self._state_lock:
                        if dead_char_account in self.unit_info:
                            char_info = self.unit_info[dead_char_account]["main_char"]
                            if char_info.get("reviving", False):
                                char_info["reviving"] = False
                                self.report_battle_info(
                                    f"账号{account_index} 复活账号{dead_char_account}的主角失败，清除reviving标记",
                                    "warning",
                                )
        return False

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
            # 添加调试信息
            self.report_battle_info(
                f"账号{target_account_index} 主角状态检查：alive={alive}, revive_pending={revive_pending}, reviving={reviving}，不能复活",
                "debug",
            )
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
        :return: ("main_char", None) 或 ("attack", skill_name) 或 ("support", skill_name) 或 (None, None)
        """
        start_time = time.time()

        # 准备攻击武将技能列表
        attack_skills = ["剑阵灭杀", "武神一怒"]
        attack_skill_paths = {}
        for skill_name in attack_skills:
            skill_path = self.skill_images.get(skill_name)
            if skill_path:
                attack_skill_paths[skill_name] = skill_path

        # 准备刘备控制技能路径
        control_skill_path = self.skill_images.get("控制")

        # 同步查找：在循环中同时查找召唤按钮、攻击武将技能、刘备控制技能
        while time.time() - start_time < timeout:
            # 1. 查找召唤按钮（主角特有）
            summon_btn = self.find_image(account_index, self.button_images["召唤按钮"], self.right_button_region, 0)
            if summon_btn:
                return ("main_char", None)

            # 2. 查找攻击武将技能
            for skill_name, skill_path in attack_skill_paths.items():
                skill_pos = self.find_image(account_index, skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("attack", skill_name)

            # 3. 查找刘备的控制技能（用于识别刘备）
            if control_skill_path:
                skill_pos = self.find_image(account_index, control_skill_path, self.skill_panel_region, 0)
                if skill_pos:
                    return ("support", "控制")

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
            self.report_battle_info(f"账号{account_index} 查找复活药图片超时（3秒）", "warning")
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
                while time.time() - start_time < 4.0 and self.polling_running:
                    if self.check_action_button(account_index):
                        is_finded = True
                        break
                    time.sleep(0.05)
                if not is_finded:
                    return False
                # 进入第一个武将操作
                self.report_battle_info(f"武将操作阶段：账号 [{account_index}]", "turn")
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False

                # 等待第二个武将操作
                is_finded = False
                start_time = time.time()
                while time.time() - start_time < 3.0:
                    if self.check_action_button(account_index):
                        is_finded = True
                        break
                    time.sleep(0.1)
                if not is_finded:
                    return False
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
            else:
                # 武将操作
                self.report_battle_info(f"武将操作阶段：账号 [{account_index}]", "turn")
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
                # 等待第二个武将操作
                time.sleep(0.03)
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False
                time.sleep(0.03)
                is_action = self.handle_our_turn(account_index)
                if not is_action:
                    return False

            # 注意：不在每个账号操作完成后检测墓碑，而是在主循环中统一检测
            # 原因：1. 操作回合中墓碑可能还没出现 2. 主循环中已经会在所有操作完成后统一检测

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 处理操作流程出错: {e}", "error")

    # 处理我方回合操作
    def handle_our_turn(self, account_index):
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

            # 确保技能面板已打开（点击技能按钮）
            skill_btn = self.find_image(account_index, self.button_images["技能按钮"], self.right_button_region, 0)
            if skill_btn:
                self.click_position(account_index, skill_btn.x, skill_btn.y)

            # 第一回合跳过召唤判断（第一回合武将还没有出现，不需要召唤）
            is_first_turn = self.current_turn == 0 or self.current_turn == 1

            char_info = self.unit_info[account_index]["main_char"]
            need_liubei = False
            need_summon_general = False
            need_self_liubei = False

            # 默认每个账号有2个武将，不需要第一回合检测
            # 第一回合不召唤
            if not is_first_turn:
                # 检查当前账号是否有武将处于死亡状态（召唤的必要条件）
                # 方法1：检查global_dead_units中是否有当前账号的武将
                has_dead_general_in_account = False
                with self._state_lock:
                    for dead_gen in self.global_dead_units["generals"]:
                        if dead_gen.get("account_index") == account_index:
                            has_dead_general_in_account = True
                            break

                # 方法2：检查武将列表中是否有死亡状态的武将
                has_dead_general_in_list = False
                for gen_info in char_info.get("generals", []):
                    if not gen_info.get("alive", True):
                        has_dead_general_in_list = True
                        break

                # 方法3：检查实际存活的武将数量
                alive_generals_count = 0
                for gen_info in char_info.get("generals", []):
                    if gen_info.get("alive", True):
                        alive_generals_count += 1
                # 判断是否需要召唤：
                # 1. 主角必须存活
                # 2. 实际存活武将数量必须小于2
                # 3. 账号下有武将处于死亡状态（在global_dead_units中或alive=False）
                if char_info.get("alive", True):
                    # 只要有任何死亡状态的武将，且实际存活数量小于2，就需要召唤
                    need_summon =  has_dead_general_in_account
                else:
                    need_summon = False

                if need_summon:
                    # 第二步：判断场上有无刘备（通过图片识别判断）
                    # has_liubei_on_field 是在我方回合通过图片识别检测的，表示整个场上是否有刘备（全局标志）
                    with self._state_lock:
                        has_liubei_on_field = self.has_liubei_on_field

                    # 检查当前账号是否有存活的刘备
                    has_liubei_in_account = False
                    for gen_info in char_info.get("generals", []):
                        if gen_info.get("name") == "刘备" and gen_info.get("alive", True):
                            has_liubei_in_account = True
                            break

                    # 第三步：根据场上有无刘备决定召唤什么武将
                    # 如果场上没有刘备（所有账号共享同一个屏幕，只要有一个账号有刘备，场上就有刘备）
                    # 且当前账号没有存活的刘备，优先召唤刘备
                    if not has_liubei_on_field and not has_liubei_in_account:
                        need_liubei = True
                        self.report_battle_info(
                            f"账号{account_index} 判断需要召唤刘备（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 场上无刘备={not has_liubei_on_field}, 账号无刘备={not has_liubei_in_account}, 主角存活={char_info.get('alive', True)}）",
                            "info",
                        )
                    else:
                        # 场上有刘备或当前账号有刘备，召唤其他武将
                        need_summon_general = True
                        self.report_battle_info(
                            f"账号{account_index} 判断需要召唤其他武将（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 场上有刘备={has_liubei_on_field}, 账号有刘备={has_liubei_in_account}, 主角存活={char_info.get('alive', True)}）",
                            "info",
                        )
                else:
                    self.report_battle_info(
                        f"账号{account_index} 判断不需要召唤（有武将死亡={has_dead_general_in_account or has_dead_general_in_list}, 主角存活={char_info.get('alive', True)}）",
                        "info",
                    )
            else:
                self.report_battle_info(f"账号{account_index} 第一回合，跳过召唤判断", "info")

            # 多刘备并行：该账号被分配了清除任务但没有刘备，需要召唤
            # （不依赖need_summon，即使武将齐全也需要刘备来清状态）
            with self._state_lock:
                has_liubei_in_account_for_clear = False
                for gen_info in char_info.get("generals", []):
                    if gen_info.get("name") == "刘备" and gen_info.get("alive", True):
                        has_liubei_in_account_for_clear = True
                        break
            if (self.enemies_need_clear.get(account_index) 
                and not has_liubei_in_account_for_clear 
                and char_info.get("alive", True)):
                need_self_liubei = True
                if not self.keep_support_general:
                    self.keep_support_general = True
                    self.beidong_huihe = 5

            # 3. 检查是否有分配到的复活任务
            # 复活任务在我方回合开始时已统一分配，这里只需要检查当前账号是否有任务
            assigned_revive_target = self.revive_assignments.get(account_index)

            # 4. 识别单位类型并执行相应操作
            unit_type, detected_skill = self.identify_unit_type(account_index, timeout=4.0)

            if unit_type == "main_char":
                # 主角操作
                # 识别到主角操作，说明该主角存活，确认复活成功（如果有待验证的复活）
                self._confirm_revive_success(account_index)
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
                if ( self.keep_support_general
                    and self.has_liubei.get(account_index, False)
                    and (time.time() - turn_start_time) < turn_timeout
                    and self.has_general[account_index]
                    and (need_liubei
                        or need_self_liubei
                        or (self.beidong_huihe >= 5 and self.zhaohuan_index == account_index))
                ):
                    if self.summon_general_with_verification(account_index, "刘备"):
                        time.sleep(0.1)
                        return True
                    self.has_liubei[account_index] = False
                    if self.beidong_huihe >= 5 and self.zhaohuan_index == account_index:
                        if self.zhaohuan_index < 2:
                            self.zhaohuan_index += 1
                        else:
                            self.zhaohuan_index = 0
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
                ):
                    general_order = ["曹操", "魔化关羽", "刘备"]
                    for general_name in general_order:
                        if self.summon_general_with_verification(account_index, general_name):
                            time.sleep(0.1)
                            return True
                    self.has_general[account_index] = False
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

                # 4.4 释放主角技能（策略引擎）
                if self._execute_best_strategy(account_index, "main_char"):
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
                # 检查该武将是否已在列表中
                general_name = detected_skill or "攻击武将"
                found_general = False
                for gen_info in char_info.get("generals", []):
                    # 通过技能名称或位置匹配（攻击武将技能：剑阵灭杀、武神一怒）
                    if gen_info.get("name") == general_name or detected_skill in ["剑阵灭杀", "武神一怒"]:
                        found_general = True
                        break

                if not found_general:
                    # 武将不在列表中，添加到列表（可能是第一回合初始武将或召唤后检测到蓝条）
                    # 根据账号索引确定武将位置
                    if account_index == 0:
                        general_position = (572, 380) if len(char_info.get("generals", [])) == 0 else (667, 380)
                    elif account_index == 1:
                        general_position = (530, 278) if len(char_info.get("generals", [])) == 0 else (626, 278)
                    else:  # account_index == 2
                        general_position = (520, 490) if len(char_info.get("generals", [])) == 0 else (626, 490)

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
                    # 第一回合初始武将：数量已经是2，不需要更新
                    # 如果是召唤后检测到蓝条，数量会在蓝条检测时更新
                    self.unit_info[account_index]["generals"].append(new_general)
                else:
                    # 武将已在列表中，检查是否正在复活中
                    for gen_info in char_info.get("generals", []):
                        if gen_info.get("name") == general_name or detected_skill in ["剑阵灭杀", "武神一怒"]:
                            if gen_info.get("reviving", False):
                                # 检测到蓝条（识别到技能），确认复活成功
                                gen_info["alive"] = True
                                gen_info["reviving"] = False
                                # 加数量
                                self._update_general_count_on_revive_success(account_index)

                                # 从global_dead_units中移除对应记录（通过name和account_index匹配，如果name不一致则使用position匹配）
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
                            break

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
                # 识别到刘备操作，更新场上是否有刘备的状态（通过图片检测已处理，这里不再重复设置）

                # 识别刘备并添加到列表（如果不在列表中）
                char_info = self.unit_info[account_index]["main_char"]
                # 检查刘备是否已在列表中
                found_liubei = False
                for gen_info in char_info.get("generals", []):
                    if gen_info.get("name") == "刘备":
                        found_liubei = True
                        break

                if not found_liubei:
                    # 刘备不在列表中，添加到列表
                    # 根据账号索引确定刘备位置
                    if account_index == 0:
                        liubei_position = (572, 380) if len(char_info.get("generals", [])) == 0 else (667, 380)
                    elif account_index == 1:
                        liubei_position = (530, 278) if len(char_info.get("generals", [])) == 0 else (626, 278)
                    else:  # account_index == 2
                        liubei_position = (520, 490) if len(char_info.get("generals", [])) == 0 else (626, 490)

                    new_general = {
                        "name": "刘备",
                        "position": liubei_position,
                        "alive": True,
                        "deployed_turn": self.current_turn,
                        "account_index": account_index,
                    }
                    if "generals" not in char_info:
                        char_info["generals"] = []
                    char_info["generals"].append(new_general)
                    # 第一回合初始武将：数量已经是2，不需要更新
                    # 如果是召唤后检测到蓝条，数量会在蓝条检测时更新
                    self.unit_info[account_index]["generals"].append(new_general)

                # 4.1 执行分配的复活任务（如果当前账号有分配任务）
                if assigned_revive_target is not None and time.time() - turn_start_time < turn_timeout:
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
                if self._execute_best_strategy(account_index, "support"):
                    return True

            # 如果未识别到单位类型，返回False
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
            for account_index in [0, 1, 2]:
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
                for account_index in [0, 1, 2]:
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
                for account_index in [0, 1, 2]:
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
                    if self.beidong_huihe > 0:
                        self.beidong_huihe += 1
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

                    # 为每个账号创建独立的处理线程
                    # 主账号已确认是我方回合，直接创建线程，_handle_account_turn内部会自己检测和等待操作按钮
                    account_threads = {}
                    for account_index in [0, 1, 2]:
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

                        # 操作完成后，短暂延迟
                        time.sleep(0.1)

                # 非我方回合：检测场上的墓碑和敌军状态
                # 使用主账号（账号0）检测所有账号的状态
                main_account_index = 0
                dm = self.get_account_dm(main_account_index)
                if dm:
                    # 第一步：检测场上的墓碑
                    # self.report_battle_info(f"检测场上的墓碑", "info")
                    for account_index in [0, 1, 2]:
                        if not self.polling_running:
                            break
                        dead_list = self.check_tombstones(account_index, detect_account_index=main_account_index)
                        if dead_list:
                            self.update_unit_info_from_tombstones(dead_list)

                    # 第二步：检测敌军需要清除的状态
                    if self.enemy_keys_to_detect:
                        self.detect_enemies_need_clear(main_account_index)

                    # 非我方回合时，由大漠对象0检测场上是否有刘备
                    self._detect_liubei_on_field()

                    # 检测各账号血量低单位数量
                    self.low_hp_accounts = {}
                    for acct in [0, 1, 2]:
                        cnt = 0
                        for ridx, ac in self.hp_region_to_account.items():
                            if ac == acct:
                                reg = self.hp_bar_regions[ridx]
                                if self.find_image(acct, self.low_hp_indicator_image, reg, 0):
                                    cnt += 1
                        self.low_hp_accounts[acct] = cnt
                # 轮询间隔（非我方回合时）
                if self.polling_running:
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

            except KeyboardInterrupt:
                self.polling_running = False
                self.report_battle_info("轮询监听已停止(KeyboardInterrupt)", "system")
                break
            except Exception as e:
                self.report_battle_info(f"轮询监听出错: {e}", "error")
                if self.polling_running:
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
        # 注意：这个方法会在调用它的线程中运行，不需要再启动新线程
        self.polling_running = True
        self._polling_loop()

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
                self.enemies_need_clear = {}
                self.enemy_status_reported = {}
                self.current_turn = 0
                self.skill_cd = {}
                self.pending_liubei_summon = {}
                self.has_liubei_on_field = True
                self.liubei_missing_count = 0
                self.low_hp_units = {}
                self.zhugeliang_found = {}
                self.zhugeliang_status1_missing_count = {}
                self.zhugeliang_status2_missing_count = {}
                self.lantiao_missing_rounds = {}

                self.liubei_skill_sequence = ["控制", "加攻击", "加血"]
                self.liubei_skill_index = {}
                self.liubei_skill_cd = {}

                self.revive_assignments = {}

                self.enemy_target_position = None
                self.ally_support_target_position = None
                self.target_positions_detected = False
                self._target_positions_detected_this_round = False

                self.has_general = {0: True, 1: True, 2: True}
                self.has_liubei = {0: True, 1: True, 2: True}
                self.beidong_huihe = 0
                self.zhaohuan_index = 0
                self.clear_zhugeliang = False
                self.enable_persistent_liubei = True
                self.attack_buff_tracker = {}
                self.low_hp_accounts = {}
            except Exception:
                pass

            print("cleanup: 已通知停止，尝试等待并清理线程/资源（最佳努力）")
        except Exception as e:
            print(f"cleanup 出错: {e}")
            import traceback
            traceback.print_exc()


# 示例使用
if __name__ == "__main__":
    # 这个脚本需要在 MyThread 的上下文中运行
    # 使用方式：
    # 1. 在 MyFrame 中添加新的脚本选项 "战斗中自动"
    # 2. 在 MyThread.run() 方法中添加对应的脚本执行分支
    # 3. 调用 CombatAutoScript 的功能

    print("战斗自动操作脚本已加载")