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
from typing import Optional, Tuple, List, Dict, Any, Union


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
    PANEL_WAIT_TIMEOUT = 3

    # 检测间隔（秒）
    DEFAULT_CHECK_INTERVAL = 0.1

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
    CLICK_DELAY = 0.2
    MOVE_DELAY = 0.2
    ACTION_DELAY = 0.3
    SKILL_CLICK_VERIFY_DELAY = 0.8  # 技能点击后验证等待时间

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
            parent, title="战斗实时播报", size=(800, 600), pos=(450, 50), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
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
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(wx.Colour(255, 255, 255))

        title_sizer.Add(title_text, 1, wx.ALIGN_CENTER | wx.ALL, 10)
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
        log_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.log_text.SetFont(log_font)
        self.log_text.SetBackgroundColour(wx.Colour(250, 250, 255))

        # 设置滚动面板的布局
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        scroll_panel.SetSizer(scroll_sizer)

        vbox.Add(scroll_panel, 1, wx.EXPAND | wx.ALL, 5)

        # 底部按钮区域
        button_panel = wx.Panel(panel)
        button_panel.SetBackgroundColour(wx.Colour(245, 245, 250))
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.clear_button = wx.Button(button_panel, label="清空日志", size=(100, 35))
        self.clear_button.SetFont(log_font)
        self.clear_button.SetBackgroundColour(wx.Colour(144, 144, 153))
        self.clear_button.SetForegroundColour(wx.Colour(255, 255, 255))
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear)

        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.clear_button, 0, wx.ALL, 5)
        button_panel.SetSizer(button_sizer)

        vbox.Add(button_panel, 0, wx.EXPAND)

        panel.SetSizer(vbox)

        # 日志锁（线程安全）
        self.log_lock = threading.Lock()

        # 初始化消息
        self.add_log("=" * 60, wx.Colour(100, 100, 100))
        self.add_log("战斗播报系统已启动", wx.Colour(20, 180, 168))
        self.add_log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", wx.Colour(100, 100, 100))
        self.add_log("=" * 60, wx.Colour(100, 100, 100))
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

    # 安全关闭窗口
    def close_safely(self):
        if self:
            wx.CallAfter(self.Close)


class CombatAutoScript:
    # 初始化战斗自动操作
    # :param thread_instance: MyThread 实例，用于访问大漠对象和区域定义
    def __init__(self, thread_instance):
        self.thread = thread_instance
        self.battle_report_dialog = None  # 战斗播报窗口

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
        self.global_dead_units = {"main_chars": [], "generals": []}  # 全局阵亡单位记录（所有账号共享）
        self.enemies_need_clear = {}  # 需要清除状态的敌军列表
        self.current_turn = 0  # 当前回合数
        self.skill_cd = {}  # 技能CD追踪：{account_index: {skill_name: last_used_turn}}
        self.pending_liubei_summon = {}  # 待召唤刘备记录：{target_account_index: {'target_char_index': int, 'target_char_info': dict}}
        self.has_liubei_on_field = {}  # 场上是否有刘备：{account_index: bool}，在非战斗回合检测
        self.low_hp_units = {}  # 血量低的单位记录：{account_index: [{'unit_type': 'main_char'/'general', 'unit_name': str, 'position': (x, y), 'region_index': int}, ...]}
        self.zhugeliang_found = {}  # 诸葛亮单位标记：{account_index: bool}，记录是否已找到状态1和状态2同时存在的诸葛亮单位

        # 刘备技能释放顺序和冷却记录
        self.liubei_skill_sequence = ["加攻击", "加血", "控制", "加血"]  # 刘备技能释放顺序（循环）
        self.liubei_skill_index = {}  # {account_index: current_index} 记录每个账号当前技能索引
        self.liubei_skill_cd = {}  # {account_index: {skill_name: last_used_turn}} 记录每个账号的技能冷却时间

        # 防止重复复活标记：记录正在被复活的主角
        # 格式：{(account_index, char_name): True} 或 {(account_index, char_name): timestamp}
        self.reviving_chars = {}  # 正在复活的主角标记
        self.revive_lock = threading.Lock()  # 复活操作的锁

        # 轮询监听控制
        self.polling_running = False  # 轮询监听运行标志
        self.polling_thread = None  # 轮询监听线程

    # 创建战斗播报窗口（在主线程中调用）
    def _create_battle_report_dialog(self):
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
        # 如果窗口还未创建，尝试创建
        if self.battle_report_dialog is None:
            try:
                if hasattr(wx, "GetApp") and wx.GetApp():
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
        else:
            # 如果窗口不存在，至少打印到控制台
            print(f"[战斗播报-{msg_type}] {message}")

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
        self.item_panel_region = self.ally_region  # 道具面板区域（点击道具按钮后弹出的面板）

        # 武将图片路径
        self.general_images = {
            "刘备": self.get_resource_path("serveAssets/images/auto/miankong1.bmp"),
            "魔化关羽": f"{self.get_resource_path('serveAssets/images/auto/gangqi1.bmp')}|{self.get_resource_path('serveAssets/images/auto/shenyou1.bmp')}",
            "曹操": f"{self.get_resource_path('serveAssets/images/auto/bawang1.bmp')}|{self.get_resource_path('serveAssets/images/auto/luanshi1.bmp')}",
        }

        # 技能图片路径（需要根据实际技能图标添加）
        self.skill_images = {
            # 主角技能
            "寂灭神劫": self.get_resource_path("serveAssets/images/auto/cehsi.bmp"),
            "锁魂": self.get_resource_path("serveAssets/images/auto/zhanshiqun.bmp"),
            "天灾": f"{self.get_resource_path('serveAssets/images/auto/tianzai1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tianzai2.bmp')}",
            # 辅助武将技能
            "加血": f"{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan2.bmp')}",
            "加攻击": self.get_resource_path("serveAssets/images/auto/liubeizengshang1.bmp"),
            "控制": self.get_resource_path("serveAssets/images/auto/liubeikong1.bmp"),
            "清除状态": self.get_resource_path("serveAssets/images/auto/liubeijie1.bmp"),
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
        self.liubei_target_image = f"{self.get_resource_path('serveAssets/images/auto/jifangliubei.bmp')}|{self.get_resource_path('serveAssets/images/auto/jifangmoguan.bmp')}"
        
        # 技能目标选择图片（蓝色条）
        self.target_lantiao_image = self.get_resource_path("serveAssets/images/auto/lantiao.bmp")
        self.has_liubei_on_field = self.get_resource_path("serveAssets/images/auto/miankong1.bmp")
        # 控制开关
        self.keep_support_general = False  # 是否保证辅助武将在场
        self.enable_main_heal = True  # 主角加血开关
        self.enable_main_summon = True  # 主角召唤开关

        # 刘备辅助技能释放顺序（"控制"是攻击技能，不在辅助技能序列中）
        self.support_skill_sequence = ["加攻击", "加血", "清除状态"]
        self.current_skill_index = 0  # 当前技能索引

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
        self.support_general_account = None  # 哪个账号有辅助武将（场上）
        self.turn_processed = False  # 当前回合是否已处理（防止重复更新回合数）
        self.account_turn_processed = {}  # 每个账号在当前回合是否已处理（防止重复执行操作）
        self._last_turn_state = {}  # 每个账号的上一回合状态 {account_index: bool}（用于检测回合变化）
        self._last_alive_units_check = True  # 上次检测是否有存活单位的结果（默认True，避免初始误判）

        # 当前战斗需要检测的敌军武将列表（可为每个账号单独设置）
        # 格式：{account_index: [武将名称列表]} 或 None（自动检测所有敌军武将）
        # 例如：{0: ['刘备', '诸葛亮'], 1: ['赵云29']} 或 None
        self.current_enemy_generals_to_detect = None  # None表示自动检测所有配置的敌军武将

        # 敌军状态图片路径（需要检测的四种状态）
        self.enemy_status_images = {
            "状态1": f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
            "状态2": self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp"),
            "状态3": self.get_resource_path("serveAssets/images/auto/bumiexiongxin1.bmp"),
            "状态4": self.get_resource_path("serveAssets/images/auto/gangqi1.bmp"),
        }

        # 敌人图片路径（用于识别敌人的位置）
        self.enemy_images = {
            "敌人1": self.get_resource_path("serveAssets/images/auto/lantiao1.bmp"),
            "敌人2": self.get_resource_path("serveAssets/images/auto/lantiao1.bmp"),
            "敌人3": self.get_resource_path("serveAssets/images/auto/lantiao1.bmp"),
            # 可以添加更多敌人的图片路径
        }

        # 主角图片路径（用于检测主角位置，存活状态通过墓碑检测）
        self.main_char_images = {
            "主角1": self.get_resource_path("serveAssets/images/auto/zengjiagongjili1.bmp"),
            "主角2": self.get_resource_path("serveAssets/images/auto/zengjiagongjili1.bmp"),
            "主角3": self.get_resource_path("serveAssets/images/auto/zengjiagongjili1.bmp"),
        }

        # 墓碑图片路径（用于检测单位死亡状态）
        # 单位死亡后会在原地显示墓碑，通过检测墓碑来判断死亡
        self.tombstone_image = self.get_resource_path("serveAssets/images/auto/duiyou2mubei1.bmp")  # 墓碑图片

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
            "曹操": self.get_resource_path("serveAssets/images/auto/caocao1.bmp"),
        }

        # 血量条图片（用于检测血量低的单位）
        # 识别到这张图片说明单位血量低，需要加血
        self.low_hp_indicator_image = f"{self.get_resource_path('serveAssets/images/auto/xueliangbuzu1.bmp')}|{self.get_resource_path('serveAssets/images/auto/xueliangbuzu2.bmp')}"  # 血量低的标识图片

        # 9个血量条检测区域（每个角色和武将都有专门的区域）
        # 顺序：主角1、主角2、主角3、武将1、武将2、武将3、武将4、武将5、武将6
        # 格式：[(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
        # 基于900x580游戏界面，血量条通常显示在角色头顶上方
        self.hp_bar_regions = [
            (708, 170, 830, 340),  # 主角1血量条（上方）
            (749, 281, 836, 409),  # 主角2血量条（中间）
            (775, 395, 862, 542),  # 主角3血量条（下方）
            (530, 170, 616, 340),  # 武将1血量条（上，前排）
            (520, 270, 634, 409),  # 武将2血量条（中，前排）
            (520, 387, 658, 542),  # 武将3血量条（下，前排）
            (626, 170, 723, 340),  # 武将4血量条（上，后排）
            (626, 270, 744, 409),  # 武将5血量条（中，后排）
            (626, 387, 768, 542),  # 武将6血量条（下，后排）
        ]  # 9个血量条区域列表

        # 血量条区域到单位的映射关系
        # {account_index: {region_index: (unit_type, unit_name, heal_position)}}
        # unit_type: 'main_char' 或 'general'
        # region_index: 0-8 (对应9个区域：0-2主角，3-8武将)
        # heal_position: (x, y) 加血点位
        self.hp_bar_unit_mapping = {}  # 血量条区域到单位的映射

        # 账号状态（延迟初始化，避免thread属性未设置时报错）
        # 注意：account_dm 会在首次使用时通过属性或方法来获取
        self._account_dm = None  # 延迟初始化的账号列表（在_get_account_dm中初始化）

        # 右侧按钮区域定义（根据实际游戏，操作按钮在右侧）
        # 按钮包括：攻击(A)、技能(S)、道具(E)、防御(D)、重复(R)、召唤(C)、自动(W)、逃跑(P)
        self.right_button_region = (610, 203, 680, 436)  # 右侧按钮区域（中间偏右，包含操作按钮）
        self.skill_panel_region = (480, 167, 607, 550)  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = (480, 167, 607, 550)  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (480, 167, 607, 550)  # 道具面板区域（点击道具按钮后弹出的面板）

        # 主角、武将、敌人的确切点位存储（单位外观中心位置，用于点击）
        # {account_index: {'main_chars': [(char_name, x, y), ...], 'generals': [(general_name, x, y), ...], 'enemies': [(enemy_name, x, y), ...]}}
        # 坐标基于之前配置的站位区域中心点计算
        # 格式：单位名称和中心坐标 (x, y)
        self.unit_positions = {
            # 默认配置（会在实际战斗中动态更新）
            # 中心点计算：区域中心 = (x1+x2)/2, (y1+y2)/2
            # 主角中心点（最右侧）
            0: {
                "main_chars": [
                    ("主角1", 764, 278),  # 主角1中心点 (700+850)/2, (280+340)/2
                    ("主角2", 793, 380),  # 主角2中心点 (700+850)/2, (350+410)/2
                    ("主角3", 825, 490),  # 主角3中心点 (700+850)/2, (420+480)/2
                ],
                "generals": [
                    # 武将中心点（会在战斗中动态更新，这里是初始参考值）
                    # 前排武将
                    ("武将1", 572, 288),  # 武将1中心点 (520+670)/2, (280+340)/2
                    ("武将2", 589, 389),  # 武将2中心点 (520+670)/2, (350+410)/2
                    ("武将3", 613, 491),  # 武将3中心点 (520+670)/2, (420+480)/2
                    # 后排武将
                    ("武将4", 667, 279),  # 武将4中心点 (610+700)/2, (280+340)/2
                    ("武将5", 688, 376),  # 武将5中心点 (610+700)/2, (350+410)/2
                    ("武将6", 722, 490),  # 武将6中心点 (610+700)/2, (420+480)/2
                ],
                "enemies": [
                    # 敌人中心点需要通过set_fixed_enemy_positions设置
                    # 一般敌人的中心点位置在左侧，x约150-350, y约300-450
                ],
            },
            1: {
                "main_chars": [
                    ("主角1", 764, 278),  # 主角1中心点 (700+850)/2, (280+340)/2
                    ("主角2", 793, 380),  # 主角2中心点 (700+850)/2, (350+410)/2
                    ("主角3", 825, 490),  # 主角3中心点 (700+850)/2, (420+480)/2
                ],
                "generals": [
                    # 武将中心点（会在战斗中动态更新，这里是初始参考值）
                    # 前排武将
                    ("武将1", 572, 288),  # 武将1中心点 (520+670)/2, (280+340)/2
                    ("武将2", 589, 389),  # 武将2中心点 (520+670)/2, (350+410)/2
                    ("武将3", 613, 491),  # 武将3中心点 (520+670)/2, (420+480)/2
                    # 后排武将
                    ("武将4", 667, 279),  # 武将4中心点 (610+700)/2, (280+340)/2
                    ("武将5", 688, 376),  # 武将5中心点 (610+700)/2, (350+410)/2
                    ("武将6", 722, 490),  # 武将6中心点 (610+700)/2, (420+480)/2
                ],
                "enemies": [],
            },
            2: {
                "main_chars": [
                    ("主角1", 764, 278),  # 主角1中心点 (700+850)/2, (280+340)/2
                    ("主角2", 793, 380),  # 主角2中心点 (700+850)/2, (350+410)/2
                    ("主角3", 825, 490),  # 主角3中心点 (700+850)/2, (420+480)/2
                ],
                "generals": [
                    # 武将中心点（会在战斗中动态更新，这里是初始参考值）
                    # 前排武将
                    ("武将1", 572, 288),  # 武将1中心点 (520+670)/2, (280+340)/2
                    ("武将2", 589, 389),  # 武将2中心点 (520+670)/2, (350+410)/2
                    ("武将3", 613, 491),  # 武将3中心点 (520+670)/2, (420+480)/2
                    # 后排武将
                    ("武将4", 667, 279),  # 武将4中心点 (610+700)/2, (280+340)/2
                    ("武将5", 688, 376),  # 武将5中心点 (610+700)/2, (350+410)/2
                    ("武将6", 722, 490),  # 武将6中心点 (610+700)/2, (420+480)/2
                ],
                "enemies": [],
            },
        }

        # 阵亡主角的位置存储（用于复活）
        # {account_index: {char_name: (x, y), ...}}
        self.dead_main_char_positions = {}

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

        # 状态追踪（用于状态3和状态4的处理逻辑）
        # {account_index: {'status3_present': bool, 'status3_last_seen_turn': int, 'status4_present': bool}}
        self.enemy_status_tracking = {}

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
                "status_region": (61, 257, 145, 312),
                "cast_position": (104, 344),
            },
            "赵云29": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/longdan1.bmp"),
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
                    "状态1": self.get_resource_path("serveAssets/images/auto/longdan1.bmp"),
                },
                "status_region": (165, 255, 207, 307),
                "cast_position": (202, 337),
            },
        }

        # 己方异常状态图片路径（混乱、冰封、眩晕、嘲讽）
        self.ally_abnormal_status_images = {
            "冰封": self.get_resource_path("serveAssets/images/auto/bingfeng1.bmp"),  # 冰封状态图片
        }

        # 己方单位异常状态追踪
        # {(account_index, unit_type, unit_name): ['状态1', '状态2', ...]}
        # unit_type: 'main_char' 或 'general'
        # unit_name: 主角名称（如'主角1'）或武将名称（如'刘备'）
        self.ally_status_tracking = {}

        # 异常状态检测区域大小（以单位位置为中心的区域）
        # 用于在单位位置附近检测异常状态图标
        self.status_detection_radius = CombatConstants.STATUS_DETECTION_RADIUS

        # 按钮图片路径
        self.button_images = {
            "技能按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),
            "召唤按钮": self.get_resource_path("serveAssets/images/auto/zhaohuan.bmp"),
            "道具按钮": self.get_resource_path("serveAssets/images/auto/yaopin.bmp"),
            "防御按钮": self.get_resource_path("serveAssets/images/auto/fangyu.bmp"),  # 防御按钮
            "操作按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),  # 操作按钮(检测是否在战斗页面)
            "取消按钮": self.get_resource_path("serveAssets/images/quxiaozdzd.bmp"),  # 取消按钮
        }
        
        # zdzd图片路径（需要检测并点击取消的弹窗）
        self.zdzd_image = self.get_resource_path("serveAssets/images/zdzd111.bmp")
        
        # zdzd检测区域（全屏检测）
        self.zdzd_region = (0, 0, 900, 580)  # 全屏区域

        # 三个账号的角色站位区域（基于900x580游戏界面）
        # 格式：(x, y, w, h) - 左上角坐标和宽高
        # 根据游戏截图：左侧是敌军，右侧是我军，最右侧是三个主角，前面是武将
        self.account_regions = [
            {
                # 主角位置（最右侧，x约750）
                "ally_char_1": (708, 168, 815, 329),
                # 主角1位置（上）
                "ally_char_2": (735, 251, 856, 426),
                # 主角2位置（中）
                "ally_char_3": (769, 348, 862, 527),
                # 主角3位置（下）
                # 武将位置（主角前方，x约550-650，分前后两列）
                # 前排武将（靠近中心）
                "ally_general_1": (530, 148, 616, 329),
                # 武将1位置（上，前排）
                "ally_general_2": (520, 251, 634, 426),
                # 武将2位置（中，前排）
                "ally_general_3": (520, 348, 658, 527),
                # 武将3位置（下，前排）
                # 后排武将（中间列，可选）
                "ally_general_4": (610, 148, 623, 329),
                # 武将4位置（上，后排）
                "ally_general_5": (610, 251, 644, 426),
                # 武将5位置（中，后排）
                "ally_general_6": (610, 348, 668, 527),
                # 武将6位置（下，后排）
            }
        ] * 3  # 假设三个账号区域相同，如果不同需要分别定义

    # ==================== 重写后的核心战斗逻辑 ====================

    # 获取账号数量
    def get_account_count(self):
        """获取账号数量（根据实际可用的大漠对象）"""
        count = 0
        if self.thread.dm:
            count += 1
        if getattr(self.thread, 'win1_dm', None):
            count += 1
        if getattr(self.thread, 'win2_dm', None):
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
            return getattr(self.thread, 'win1_dm', None)
        elif account_index == 2:
            return getattr(self.thread, 'win2_dm', None)
        return self.thread.dm  # 默认返回主账号

    # 查找图片(封装thread的方法，支持多账号)
    def find_image(self, account_index, image_path, region, find_dir=0):
        """查找图片，支持多账号，支持识别率递减（0.9 -> 0.8 -> 0.7）"""
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
            
            # 识别率递减：0.9 -> 0.8 -> 0.7
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
        default_confidence = getattr(self.thread, 'confidenceNum', 0.9)
        color_format = 'ffff00-000000|fff200-000000|fdfd06-000000'
        
        # 使用指定的识别率或默认值
        use_confidence = confidence if confidence is not None else default_confidence
        # 直接使用dm对象，避免修改共享的confidenceNum（线程安全）
        # 大漠插件本身是线程安全的，可以直接在子线程中使用
        x, y, w, h = region
        find_str_result = dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text, color_format, use_confidence
        )
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
    
    # 检测召唤成功文字
    def check_summon_success(self, account_index, timeout=3.0):
        """检测召唤是否成功（通过检测"召唤成功"文字）
        :param account_index: 账号索引
        :param timeout: 超时时间（秒）
        :return: True/False
        """
        success_text = "召唤武将"
        # 在全屏区域检测"召唤成功"文字
        search_region = (0, 0, 900, 580)  # 全屏区域
        confidence_levels = [0.9, 0.8, 0.7]  # 识别率递减
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 尝试多个识别率
            for confidence in confidence_levels:
                if time.time() - start_time >= timeout:
                    break
                
                success_pos = self.find_text(account_index, success_text, search_region, 0, confidence)
                if success_pos:
                    self.report_battle_info(
                        f"账号{account_index} 召唤操作成功", "success"
                    )
                    return True
                time.sleep(0.05)  # 短暂延迟后重试
            
            time.sleep(0.1)  # 每次循环后稍作延迟
        
        self.report_battle_info(
            f"账号{account_index} 召唤可能失败", "warning"
        )
        return False
    
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
    
    # 统一的查找"选择目标"文字方法（保留用于兼容）
    def find_target_text(self, account_index, search_region, timeout=3.0):
        """查找"选择目标"文字（已废弃，改用find_target_lantiao）
        :param account_index: 账号索引
        :param search_region: 搜索区域，可以是单个区域或区域列表
        :param timeout: 超时时间（秒）
        :return: ResXy对象或None
        """
        target_text = "选择目标"
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
                    
                    target_pos = self.find_text(account_index, target_text, search_reg, 0, confidence)
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
        time.sleep(CombatConstants.ACTION_DELAY)

    # 点击技能并验证是否成功
    def click_skill_with_verification(self, account_index, skill_image_path, skill_pos, skill_name="技能", max_retries=1):
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
                f"账号{account_index} 释放{skill_name}失败（技能图标仍在），第{retry_count + 1}次重试", 
                "warning"
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
            f"账号{account_index} 释放{skill_name}失败（重试{max_retries}次后技能图标仍在），跳过", 
            "warning"
        )
        return False

    # 初始化单位信息
    def init_unit_info(self):
        """初始化单位信息数据结构"""
        account_count = self.get_account_count()
        for i in range(account_count):
            self.unit_info[i] = {
                "main_chars": [
                    {
                        "name": "主角1",
                        "position": (763, 251),
                        "alive": True,
                        "need_revive": False,
                        "general_count": 0,
                        "generals": [],
                        "deployed_turn": 0,
                    },
                    {
                        "name": "主角2",
                        "position": (792, 346),
                        "alive": True,
                        "need_revive": False,
                        "general_count": 0,
                        "generals": [],
                        "deployed_turn": 0,
                    },
                    {
                        "name": "主角3",
                        "position": (823, 460),
                        "alive": True,
                        "need_revive": False,
                        "general_count": 0,
                        "generals": [],
                        "deployed_turn": 0,
                    },
                ],
                "generals": [],  # 格式: [{'name': '刘备', 'position': (x, y), 'alive': True, 'deployed_turn': 0, 'account_index': i, 'char_index': 0}, ...]
            }
            self.dead_units[i] = {
                "main_chars": [],
                "generals": [],
            }  # 格式: {'main_chars': [{'name': '主角1', 'position': (x, y), 'account_index': i}, ...], 'generals': [...]}
            self.enemies_need_clear[i] = (
                []
            )  # 格式: [{'enemy_name': '刘备', 'position': (x, y), 'account_index': i}, ...]
            self.skill_cd[i] = {}
            self.pending_liubei_summon[i] = None  # 待召唤刘备记录：None 或 {'target_account_index': int, 'target_char_index': int, 'target_char_info': dict}
            self.has_liubei_on_field[i] = False  # 初始化场上是否有刘备的状态
            self.liubei_skill_index[i] = 0  # 初始化刘备技能索引
            self.liubei_skill_cd[i] = {}  # 初始化刘备技能冷却记录
            self.low_hp_units[i] = []  # 初始化血量低的单位列表
            self.zhugeliang_found[i] = False  # 初始化诸葛亮单位标记
            # 初始化账号区域映射(每个账号检测自己主角和武将的区域)
            if i not in self.hp_bar_unit_mapping:
                self.hp_bar_unit_mapping[i] = {}
                # 映射9个血量条区域到单位
                for region_idx in range(9):
                    if region_idx < 3:  # 主角
                        char_idx = region_idx
                        unit_name = f"主角{char_idx + 1}"
                        position = self.unit_positions[i]["main_chars"][char_idx][1:]
                        self.hp_bar_unit_mapping[i][region_idx] = ("main_char", unit_name, position)
                    else:  # 武将
                        general_idx = region_idx - 3
                        unit_name = f"武将{general_idx + 1}"
                        if general_idx < len(self.unit_positions[i]["generals"]):
                            position = self.unit_positions[i]["generals"][general_idx][1:]
                        else:
                            position = (0, 0)  # 默认位置
                        self.hp_bar_unit_mapping[i][region_idx] = ("general", unit_name, position)

    # ==================== 轮询监听核心功能 ====================

    # 检测墓碑(检测阵亡)
    def check_tombstones(self, account_index):
        """检测指定账号的墓碑,返回阵亡单位列表
        判定死亡需要同时满足两个条件：
        1. 检测到墓碑
        2. 在对应区域找不到lantiao.bmp图片（说明单位确实不在场）
        """
        dead_list = []
        # 遍历9个血量条区域检测墓碑
        for region_idx, region in enumerate(self.hp_bar_regions):
            # 在区域内查找墓碑图片
            tombstone_pos = self.find_image(account_index, self.tombstone_image, region, 0)
            if tombstone_pos:
                # 找到墓碑，还需要检查对应区域是否找不到lantiao.bmp图片
                # 在对应区域查找lantiao.bmp图片
                lantiao_pos = self.find_image(account_index, self.target_lantiao_image, region, 0)
                # 如果找不到lantiao图片，说明单位确实不在场，判定为死亡
                if not lantiao_pos:
                    # 找到墓碑且找不到lantiao图片,根据区域索引确定是哪个单位
                    if account_index in self.hp_bar_unit_mapping:
                        if region_idx in self.hp_bar_unit_mapping[account_index]:
                            unit_type, unit_name, position = self.hp_bar_unit_mapping[account_index][region_idx]
                            dead_list.append(
                                {
                                    "account_index": account_index,
                                    "unit_type": unit_type,
                                    "unit_name": unit_name,
                                    "position": position,
                                    "region_index": region_idx,
                                }
                            )
        return dead_list

    # 检测敌军需要清除的状态
    def check_enemy_status(self, account_index):
        """检测指定账号的敌军是否需要清除状态"""
        need_clear_list = []
        # 遍历敌军武将配置
        for enemy_name, config in self.enemy_general_config.items():
            status_region = config["status_region"]
            status_images = config["status_images"]
            cast_position = config["cast_position"]

            # 诸葛亮特殊处理：需要先找到状态1和状态2同时存在，然后下次检测时如果状态2存在但状态1不存在，才需要清除
            if enemy_name == "诸葛亮":
                
                # 检测状态1和状态2
                status1_image = status_images.get("状态1")
                status2_image = status_images.get("状态2")
                
                status1_exists = False
                status2_exists = False
                
                if status1_image:
                    status1_pos = self.find_image(account_index, status1_image, status_region, 0)
                    status1_exists = (status1_pos is not None)
                
                if status2_image:
                    status2_pos = self.find_image(account_index, status2_image, status_region, 0)
                    status2_exists = (status2_pos is not None)
                
                # 检查是否已经找到过诸葛亮的单位（状态1和状态2同时存在）
                if not self.zhugeliang_found.get(account_index, False):
                    # 第一次检测：如果状态1和状态2同时存在，设置标记
                    if status1_exists and status2_exists:
                        self.zhugeliang_found[account_index] = True
                else:
                    # 标记已存在，处理各种情况
                    if status1_exists and status2_exists:
                        # 状态1和状态2又同时存在了，说明状态已恢复，重置标记
                        self.zhugeliang_found[account_index] = False
                    elif not status1_exists and not status2_exists:
                        # 状态1和状态2都消失了，重置标记
                        self.zhugeliang_found[account_index] = False
                    elif status1_exists and not status2_exists:
                        # 状态1存在但状态2不存在，可能是状态变化，重置标记
                        self.zhugeliang_found[account_index] = False
                    elif status2_exists and not status1_exists:
                        # 状态2存在，状态1不存在，说明需要清除状态
                        need_clear_list.append(
                            {
                                "account_index": account_index,
                                "enemy_name": enemy_name,
                                "status_name": "状态1",  # 需要清除状态1
                                "cast_position": cast_position,
                                "status_region": status_region,
                            }
                        )
            else:
                # 其他武将：找到状态图片就返回需要清除
                for status_name, status_image_path in status_images.items():
                    status_pos = self.find_image(account_index, status_image_path, status_region, 0)
                    if status_pos:
                        # 找到需要清除的状态
                        need_clear_list.append(
                            {
                                "account_index": account_index,
                                "enemy_name": enemy_name,
                                "status_name": status_name,
                                "cast_position": cast_position,
                                "status_region": status_region,
                            }
                        )
                        break  # 找到一个状态就够了
        return need_clear_list

    # 检测血量低的单位
    def check_low_hp_units(self, target_account_index, detect_account_index=None):
        """检测指定账号的血量低的单位,返回血量低单位列表
        :param target_account_index: 目标账号索引（要检测哪个账号的单位）
        :param detect_account_index: 检测账号索引（使用哪个账号的dm对象进行检测，默认为None表示使用target_account_index）
        """
        if detect_account_index is None:
            detect_account_index = target_account_index
        
        low_hp_list = []
        # 遍历9个血量条区域检测血量低标识
        for region_idx, region in enumerate(self.hp_bar_regions):
            # 在区域内查找血量低标识图片（使用detect_account_index的dm对象）
            low_hp_pos = self.find_image(detect_account_index, self.low_hp_indicator_image, region, 0)
            if low_hp_pos:
                # 找到血量低标识,根据区域索引确定是哪个单位（使用target_account_index确定单位信息）
                if target_account_index in self.hp_bar_unit_mapping:
                    if region_idx in self.hp_bar_unit_mapping[target_account_index]:
                        unit_type, unit_name, position = self.hp_bar_unit_mapping[target_account_index][region_idx]
                        # 检查单位是否存活（避免给已死亡的单位加血）
                        is_alive = False
                        if unit_type == "main_char":
                            for char_info in self.unit_info[target_account_index]["main_chars"]:
                                if char_info["name"] == unit_name and char_info.get("alive", True):
                                    is_alive = True
                                    break
                        elif unit_type == "general":
                            # 先检查武将是否在列表中
                            found_general = False
                            for general_info in self.unit_info[target_account_index]["generals"]:
                                if (general_info.get("name") == unit_name or 
                                    general_info.get("position") == position):
                                    found_general = True
                                    if general_info.get("alive", True):
                                        is_alive = True
                                    break
                            
                            # 如果武将不在列表中，说明是第一个回合的初始武将，将其添加到列表中（默认为存活）
                            if not found_general:
                                # 确定武将属于哪个主角（根据位置判断，武将位置在主角前方）
                                char_index = None
                                for idx, char_info in enumerate(self.unit_info[target_account_index]["main_chars"]):
                                    char_pos = char_info.get("position")
                                    if char_pos:
                                        # 武将位置在主角前方，通过y坐标判断（武将y坐标应该接近主角y坐标）
                                        if abs(position[1] - char_pos[1]) < 50:  # 允许50像素的误差
                                            char_index = idx
                                            break
                                
                                # 如果无法确定主角，默认使用第一个主角
                                if char_index is None:
                                    char_index = 0
                                
                                # 创建武将信息并添加到列表
                                new_general = {
                                    "name": unit_name,
                                    "position": position,
                                    "alive": True,
                                    "deployed_turn": self.current_turn if self.current_turn > 0 else 0,
                                    "account_index": target_account_index,
                                    "char_index": char_index,
                                }
                                self.unit_info[target_account_index]["generals"].append(new_general)
                                
                                # 同时添加到对应主角的武将列表中
                                char_info = self.unit_info[target_account_index]["main_chars"][char_index]
                                if new_general not in char_info["generals"]:
                                    char_info["generals"].append(new_general)
                                    char_info["general_count"] = len(char_info["generals"])
                                
                                is_alive = True
                        if is_alive:
                            low_hp_list.append(
                                {
                                    "account_index": target_account_index,
                                    "unit_type": unit_type,
                                    "unit_name": unit_name,
                                    "position": position,
                                    "region_index": region_idx,
                                }
                            )
        return low_hp_list

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
        if not button_pos:
            return False
        
        # 额外验证：检查是否在战斗页面（通过检测其他战斗相关的元素）
        # 例如：检测技能按钮或召唤按钮是否存在（战斗页面特有的按钮）
        skill_button_pos = self.find_image(account_index, self.button_images.get("技能按钮"), self.right_button_region, 0)
        summon_button_pos = self.find_image(account_index, self.button_images.get("召唤按钮"), self.right_button_region, 0)
        
        # 如果操作按钮存在，且至少有一个其他战斗按钮存在，才认为在战斗页面
        if skill_button_pos or summon_button_pos:
            return True
        
        return False

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
                
                # 将所有主角设置为存活
                for char_info in self.unit_info[account_idx]["main_chars"]:
                    char_info["alive"] = True
                    char_info["need_revive"] = False
                
                # 将所有武将设置为存活
                for general_info in self.unit_info[account_idx]["generals"]:
                    general_info["alive"] = True
                
                # 清空阵亡记录（本地和全局）
                self.dead_units[account_idx]["main_chars"] = []
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
                # 主角阵亡 - 先检查全局记录，避免重复
                already_in_global = False
                for dead_char in self.global_dead_units["main_chars"]:
                    if dead_char.get("name") == unit_name and dead_char.get("account_index") == account_idx:
                        already_in_global = True
                        break
                
                if already_in_global:
                    # 已经在全局记录中，跳过处理
                    continue
                
                # 更新单位信息
                for char_info in self.unit_info[account_idx]["main_chars"]:
                    if char_info["name"] == unit_name:
                        if char_info["alive"]:  # 之前是存活的,现在阵亡了
                            char_info["alive"] = False
                            char_info["need_revive"] = True
                            
                            # 添加到全局阵亡记录（所有账号共享）
                            dead_char_info = {"name": unit_name, "position": position, "account_index": account_idx}
                            self.global_dead_units["main_chars"].append(dead_char_info)
                            
                            # 也添加到本地记录（用于兼容旧代码）
                            self.dead_units[account_idx]["main_chars"].append(dead_char_info)
                            
                            self.report_battle_info(f"账号{account_idx} {unit_name}阵亡", "warning")
                        break
            elif unit_type == "general":
                # 武将阵亡 - 先检查全局记录，避免重复
                already_in_global = False
                for dead_general in self.global_dead_units["generals"]:
                    if (dead_general.get("name") == unit_name and 
                        dead_general.get("account_index") == account_idx and
                        dead_general.get("position") == position):
                        already_in_global = True
                        break
                
                if already_in_global:
                    # 已经在全局记录中，跳过处理
                    continue
                
                # 更新单位信息
                for general_info in self.unit_info[account_idx]["generals"]:
                    if general_info.get("name") == unit_name or general_info.get("position") == position:
                        if general_info.get("alive", True):
                            general_info["alive"] = False
                            
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
                                f"账号{account_idx} {general_info.get('name', unit_name)}阵亡", "warning"
                            )
                            
                            # 从对应主角的武将列表中移除
                            found_in_char = False
                            for char_info in self.unit_info[account_idx]["main_chars"]:
                                # 使用更宽松的匹配方式：通过name或position匹配
                                for gen in char_info["generals"]:
                                    if (gen.get("name") == general_info.get("name", unit_name) or 
                                        gen.get("position") == position):
                                        char_info["generals"].remove(gen)
                                        char_info["general_count"] = len(char_info["generals"])
                                        found_in_char = True
                                        break
                                if found_in_char:
                                    break
                            
                            if not found_in_char:
                                self.report_battle_info(
                                    f"账号{account_idx} 警告：武将{general_info.get('name', unit_name)}阵亡，但未在任何主角的武将列表中找到，无法更新general_count", "warning"
                                )
                            
                            # 从武将列表中移除
                            if general_info in self.unit_info[account_idx]["generals"]:
                                self.unit_info[account_idx]["generals"].remove(general_info)
                        break

    # 更新敌军状态记录
    def update_enemy_status(self, need_clear_list):
        """更新需要清除状态的敌军记录"""
        for status_info in need_clear_list:
            account_idx = status_info["account_index"]
            enemy_name = status_info["enemy_name"]
            cast_position = status_info["cast_position"]

            # 检查是否已记录
            already_recorded = False
            for recorded in self.enemies_need_clear[account_idx]:
                if recorded["enemy_name"] == enemy_name:
                    already_recorded = True
                    break

            if not already_recorded:
                self.enemies_need_clear[account_idx].append(
                    {"enemy_name": enemy_name, "position": cast_position, "account_index": account_idx}
                )
                self.report_battle_info(f"账号{account_idx} 敌军{enemy_name}需要清除状态", "warning")

    # 更新血量低的单位记录
    def update_low_hp_units(self, low_hp_list):
        """更新血量低的单位记录"""
        # 先清空所有账号的血量低单位记录
        account_count = self.get_account_count()
        for i in range(account_count):
            self.low_hp_units[i] = []
        
        # 更新新的血量低单位记录
        for unit_info in low_hp_list:
            account_idx = unit_info["account_index"]
            # 检查是否已记录（避免重复）
            already_recorded = False
            for recorded in self.low_hp_units[account_idx]:
                if (recorded["unit_type"] == unit_info["unit_type"] and 
                    recorded["unit_name"] == unit_info["unit_name"]):
                    already_recorded = True
                    break
            
            if not already_recorded:
                self.low_hp_units[account_idx].append(unit_info)

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
            timeout = 5.0
            item_button_pos = None
            
            while time.time() - start_time < timeout:
                item_button_pos = self.find_image(
                    account_index, self.button_images["道具按钮"], self.right_button_region, 0
                )
                if item_button_pos:
                    break
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if not item_button_pos:
                self.report_battle_info(f"账号{account_index} 未找到道具按钮（5秒超时）", "error")
                return False

            self.click_position(account_index, item_button_pos.x, item_button_pos.y)
            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)

            # 2. 等待恢复药出现并点击（5秒内找到，否则返回False）
            heal_item_image = self.item_images.get("恢复药")
            if not heal_item_image:
                self.report_battle_info(f"账号{account_index} 未找到恢复药图片配置", "error")
                return False

            # 5秒内循环查找恢复药
            start_time = time.time()
            timeout = 5.0
            heal_item_pos = None
            
            while time.time() - start_time < timeout:
                heal_item_pos = self.find_image(account_index, heal_item_image, self.item_panel_region, 0)
                if heal_item_pos:
                    break
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if not heal_item_pos:
                self.report_battle_info(f"账号{account_index} 道具面板中未找到恢复药（5秒超时）", "error")
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
                    if (unit_info["unit_type"] == target_unit_info["unit_type"] and 
                        unit_info["unit_name"] == target_unit_info["unit_name"]):
                        self.low_hp_units[account_index].remove(unit_info)
                        break

            self.report_battle_info(
                f"账号{account_index} 使用恢复药给{target_unit_info['unit_name']}加血", "success"
            )
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 使用恢复药失败: {e}", "error")
            return False

    # 召唤武将
    def summon_general(self, account_index, char_index, general_name):
        """召唤武将"""
        try:
            # 1. 点击召唤按钮
            summon_button_pos = self.find_image(
                account_index, self.button_images["召唤按钮"], self.right_button_region, 0
            )
            if not summon_button_pos:
                self.report_battle_info(f"账号{account_index} 未找到召唤按钮", "error")
                return False

            self.click_position(account_index, summon_button_pos.x, summon_button_pos.y)
            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)

            # 2. 等待召唤面板出现
            # 在召唤面板区域查找武将图片（5秒内找到，否则返回False）
            general_image_path = self.bag_general_images.get(general_name)
            if not general_image_path:
                self.report_battle_info(f"账号{account_index} 未找到武将{general_name}的图片配置", "error")
                return False

            # 5秒内循环查找武将图片
            start_time = time.time()
            timeout = 5.0
            general_pos = None
            
            while time.time() - start_time < timeout:
                general_pos = self.find_image(account_index, general_image_path, self.summon_panel_region, 0)
                if general_pos:
                    break
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if not general_pos:
                self.report_battle_info(f"账号{account_index} 召唤面板中未找到{general_name}（5秒超时）", "error")
                return False

            # 3. 点击武将图片
            self.click_position(account_index, general_pos.x, general_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)

            # 4. 如果是召唤刘备且当前角色两个武将全部存活,需要替换
            char_info = self.unit_info[account_index]["main_chars"][char_index]
            if general_name == "刘备" and char_info["general_count"] >= 2:
                # 找到上场回合更多的武将进行替换
                alive_generals = [g for g in char_info["generals"] if g.get("alive", True)]
                if len(alive_generals) >= 2:
                    # 找到上场回合最多的武将
                    oldest_general = max(alive_generals, key=lambda g: g.get("deployed_turn", 0))
                    # 点击该武将的位置进行替换
                    self.click_position(account_index, oldest_general["position"][0], oldest_general["position"][1])
                    time.sleep(CombatConstants.ACTION_DELAY)
                    # 更新武将信息
                    oldest_general["alive"] = False
                    if oldest_general in self.unit_info[account_index]["generals"]:
                        self.unit_info[account_index]["generals"].remove(oldest_general)
                    char_info["generals"].remove(oldest_general)

            # 5. 记录召唤的武将信息
            # 确定武将位置(根据char_index和当前武将数量)
            general_position = None
            if char_index == 0:  # 主角1
                if char_info["general_count"] == 0:
                    general_position = self.unit_positions[account_index]["generals"][0][1:]  # 武将1位置
                else:
                    general_position = self.unit_positions[account_index]["generals"][3][1:]  # 武将4位置
            elif char_index == 1:  # 主角2
                if char_info["general_count"] == 0:
                    general_position = self.unit_positions[account_index]["generals"][1][1:]  # 武将2位置
                else:
                    general_position = self.unit_positions[account_index]["generals"][4][1:]  # 武将5位置
            else:  # 主角3
                if char_info["general_count"] == 0:
                    general_position = self.unit_positions[account_index]["generals"][2][1:]  # 武将3位置
                else:
                    general_position = self.unit_positions[account_index]["generals"][5][1:]  # 武将6位置

            new_general = {
                "name": general_name,
                "position": general_position,
                "alive": True,
                "deployed_turn": self.current_turn,
                "account_index": account_index,
                "char_index": char_index,
            }

            char_info["generals"].append(new_general)
            char_info["general_count"] = len(char_info["generals"])
            self.unit_info[account_index]["generals"].append(new_general)

            self.report_battle_info(f"账号{account_index} {char_info['name']}召唤{general_name}成功", "success")
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 召唤{general_name}失败: {e}", "error")
            return False

    # 检查并标记正在复活的主角
    def _check_and_mark_reviving(self, target_account_index, char_name):
        """检查并标记正在复活的主角
        :param target_account_index: 目标账号索引（阵亡主角所属的账号）
        :param char_name: 主角名称
        :return: True表示可以复活（未被标记），False表示正在被其他账号复活
        """
        with self.revive_lock:
            # 使用 (target_account_index, char_name) 作为键
            revive_key = (target_account_index, char_name)
            
            # 检查是否正在被复活（检查所有账号）
            account_count = self.get_account_count()
            for acc_idx in range(account_count):
                check_key = (acc_idx, char_name)
                if check_key in self.reviving_chars:
                    # 正在被复活，返回False
                    return False
            
            # 没有被标记，标记为正在复活
            self.reviving_chars[revive_key] = time.time()
            return True
    
    # 清除正在复活的标记
    def _clear_reviving_mark(self, target_account_index, char_name):
        """清除正在复活的标记
        :param target_account_index: 目标账号索引（阵亡主角所属的账号）
        :param char_name: 主角名称
        """
        with self.revive_lock:
            revive_key = (target_account_index, char_name)
            if revive_key in self.reviving_chars:
                del self.reviving_chars[revive_key]
    
    # 清理过期的复活标记（防止标记永久存在）
    def _cleanup_expired_revive_marks(self):
        """清理过期的复活标记（超过10秒的标记视为过期）"""
        with self.revive_lock:
            current_time = time.time()
            expired_keys = []
            for key, timestamp in self.reviving_chars.items():
                if current_time - timestamp > 10.0:  # 10秒超时
                    expired_keys.append(key)
            for key in expired_keys:
                del self.reviving_chars[key]

    # 复活主角
    def revive_main_char(self, account_index, dead_char_info):
        """复活主角"""
        try:
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
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if not item_button_pos:
                self.report_battle_info(f"账号{account_index} 未找到道具按钮（5秒超时）", "error")
                return False

            self.click_position(account_index, item_button_pos.x, item_button_pos.y)
            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)

            # 2. 等待复活药出现并点击（5秒内找到，否则返回False）
            revive_item_image = self.item_images.get("复活药")
            if not revive_item_image:
                self.report_battle_info(f"账号{account_index} 未找到复活药图片配置", "error")
                return False

            # 5秒内循环查找复活药
            start_time = time.time()
            timeout = 5.0
            revive_item_pos = None
            
            while time.time() - start_time < timeout:
                revive_item_pos = self.find_image(account_index, revive_item_image, self.item_panel_region, 0)
                if revive_item_pos:
                    break
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if not revive_item_pos:
                self.report_battle_info(f"账号{account_index} 道具面板中未找到复活药（5秒超时）", "error")
                return False

            self.click_position(account_index, revive_item_pos.x, revive_item_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)

            # 3. 点击阵亡主角的位置
            char_position = dead_char_info["position"]
            self.click_position(account_index, char_position[0], char_position[1])
            time.sleep(CombatConstants.ACTION_DELAY)

            # 4. 更新单位信息
            char_name = dead_char_info["name"]
            for char_info in self.unit_info[account_index]["main_chars"]:
                if char_info["name"] == char_name:
                    char_info["alive"] = True
                    char_info["need_revive"] = False
                    break

            # 从全局和本地阵亡记录中移除
            if dead_char_info in self.global_dead_units["main_chars"]:
                self.global_dead_units["main_chars"].remove(dead_char_info)
            if dead_char_info in self.dead_units[account_index]["main_chars"]:
                self.dead_units[account_index]["main_chars"].remove(dead_char_info)

            self.report_battle_info(f"账号{account_index} {char_name}复活成功", "success")
            return True

        except Exception as e:
            self.report_battle_info(f"账号{account_index} 复活{dead_char_info['name']}失败: {e}", "error")
            return False

    # 检测背包中是否有指定武将（通过召唤面板）
    def has_general_in_bag(self, account_index, general_name):
        """检测背包中是否有指定武将
        :param account_index: 账号索引
        :param general_name: 武将名称（"刘备", "曹操", "魔化关羽"）
        :return: True/False
        """
        # 获取背包武将图片路径
        general_image_path = self.bag_general_images.get(general_name)
        if not general_image_path:
            return False
        
        # 处理多个图片路径
        if isinstance(general_image_path, str) and "|" in general_image_path:
            image_paths = general_image_path.split("|")
        else:
            image_paths = [general_image_path]
        
        # 点击召唤按钮打开召唤面板
        summon_button_pos = self.find_image(
            account_index, self.button_images["召唤按钮"], self.right_button_region, 0
        )
        if not summon_button_pos:
            return False
        
        self.click_position(account_index, summon_button_pos.x, summon_button_pos.y)
        time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)
        
        # 在召唤面板中查找武将图片（2秒内找到，否则返回False）
        start_time = time.time()
        timeout = 3.0
        found = False
        
        while time.time() - start_time < timeout:
            for image_path in image_paths:
                general_pos = self.find_image(account_index, image_path, self.summon_panel_region, 0)
                if general_pos:
                    found = True
                    break
            if found:
                break
            time.sleep(0.2)  # 每次查找间隔0.2秒
        
        # 关闭召唤面板（点击空白区域或ESC）
        # 这里简单处理，点击召唤按钮区域外的地方
        # self.click_position(account_index, 400, 300)  # 点击面板外的位置
        # time.sleep(0.3)
        
        return found

    # 处理我方回合操作
    def handle_our_turn(self, account_index):
        """处理我方回合的操作"""
        try:
            # 0. 优先处理待召唤刘备的记录（其他账号需要召唤刘备）
            if account_index in self.pending_liubei_summon and self.pending_liubei_summon[account_index]:
                pending_info = self.pending_liubei_summon[account_index]
                target_account = pending_info["target_account_index"]
                target_char_index = pending_info["target_char_index"]
                
                # 检查是否能找到召唤按钮（如果找不到，说明是武将在操作，无法召唤）
                summon_button_pos = self.find_image(
                    account_index, self.button_images["召唤按钮"], self.right_button_region, 0
                )
                if not summon_button_pos:
                    # 找不到召唤按钮，说明是武将在操作，清除记录，让目标账号自己处理
                    self.pending_liubei_summon[account_index] = None
                    self.report_battle_info(
                        f"账号{account_index} 当前是武将在操作，无法召唤，清除待召唤记录", "info"
                    )
                else:
                    # 检查当前账号是否有刘备可用
                    general_image_path = self.bag_general_images.get("刘备")
                    if general_image_path:
                        # 检查背包中是否有刘备
                        if self.has_general_in_bag(account_index, "刘备"):
                            # 检查当前账号是否有存活的主角
                            alive_chars = [c for c in self.unit_info[account_index]["main_chars"] if c["alive"]]
                            if alive_chars:
                                # 使用当前账号的第一个存活主角进行召唤
                                char_info = alive_chars[0]
                                char_index = self.unit_info[account_index]["main_chars"].index(char_info)
                                if self.summon_general(account_index, char_index, "刘备"):
                                    # 召唤成功，清除记录
                                    self.pending_liubei_summon[account_index] = None
                                    self.report_battle_info(
                                        f"账号{account_index} 为账号{target_account}召唤刘备成功", "success"
                                    )
                                    time.sleep(0.5)
                                    return True
                    
                    # 如果当前账号没有刘备或召唤失败，清除记录，让目标账号自己处理（继续尝试召唤其他武将）
                    self.pending_liubei_summon[account_index] = None
                    self.report_battle_info(
                        f"账号{account_index} 没有刘备，清除待召唤记录，目标账号将尝试召唤其他武将", "info"
                    )
            
            # 1. 检查是否有武将阵亡,优先召唤（使用全局记录）
            dead_generals = self.global_dead_units["generals"]
            if dead_generals:
                # 先检查是否能找到召唤按钮（如果找不到，说明是武将在操作，无法召唤）
                summon_button_pos = self.find_image(
                    account_index, self.button_images["召唤按钮"], self.right_button_region, 0
                )
                if not summon_button_pos:
                    # 找不到召唤按钮，说明是武将在操作，无法召唤，清空阵亡武将列表，继续执行技能释放
                    self.report_battle_info(
                        f"账号{account_index} 当前是武将在操作，无法召唤，继续执行技能释放", "info"
                    )
                    # 不清空全局记录，因为其他账号可能还需要召唤
                else:
                    # 使用轮询监听环节检测的结果（在非战斗回合检测，避免操作面板遮挡）
                    has_liubei_on_field = self.has_liubei_on_field.get(account_index, False)
                    
                    # 找到需要召唤武将的主角
                    need_summon = False
                    for char_info in self.unit_info[account_index]["main_chars"]:
                        if not char_info["alive"]:
                            continue

                        # 检查该主角是否需要召唤武将
                        if char_info["general_count"] < 2:
                            need_summon = True
                            char_index = self.unit_info[account_index]["main_chars"].index(char_info)
                            
                            # 点击召唤按钮（只点击一次）
                            self.click_position(account_index, summon_button_pos.x, summon_button_pos.y)
                            time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)
                            
                            summoned = False
                            
                            if not has_liubei_on_field:
                                # 场上没有刘备，优先等待刘备，然后曹操，然后魔化关羽
                                general_order = ["刘备", "曹操", "魔化关羽"]
                                for general_name in general_order:
                                    general_image_path = self.bag_general_images.get(general_name)
                                    if not general_image_path:
                                        continue
                                    # 3秒内等待武将图片出现
                                    start_time = time.time()
                                    timeout = 3.0
                                    general_pos = None
                                    
                                    while time.time() - start_time < timeout:
                                        general_pos = self.find_image(account_index, general_image_path, self.summon_panel_region, 0)
                                        if general_pos:
                                            break
                                        time.sleep(0.2)
                                    
                                    if general_pos:
                                        # 找到武将，点击召唤
                                        self.report_battle_info(
                                            f"账号{account_index} 在召唤面板中找到{general_name}，准备召唤", "info"
                                        )
                                        self.click_position(account_index, general_pos.x, general_pos.y)
                                        time.sleep(CombatConstants.ACTION_DELAY)
                                        
                                        # 如果需要替换武将，处理替换逻辑
                                        if char_info["general_count"] == 1:
                                            # 需要替换，找到上场回合更多的武将
                                            oldest_general = None
                                            oldest_turns = -1
                                            for gen_info in char_info["generals"]:
                                                if gen_info.get("alive", True):
                                                    turns = gen_info.get("deployed_turn", 0)
                                                    if turns > oldest_turns:
                                                        oldest_turns = turns
                                                        oldest_general = gen_info
                                            
                                            if oldest_general and oldest_general.get("position"):
                                                # 点击需要替换的武将位置
                                                replace_pos = oldest_general["position"]
                                                self.report_battle_info(
                                                    f"账号{account_index} 需要替换武将，点击位置: {replace_pos}", "info"
                                                )
                                                self.click_position(account_index, replace_pos[0], replace_pos[1])
                                        
                                        # 等待召唤操作完成，然后检测是否成功
                                        time.sleep(0.5)  # 等待游戏响应
                                        
                                        # 检测3秒内是否出现"召唤成功"文字
                                        if self.check_summon_success(account_index, timeout=3.0):
                                            # 召唤成功
                                            summoned = True
                                            self.report_battle_info(f"账号{account_index} 召唤{general_name}成功", "action")
                                            break
                                        else:
                                            # 召唤失败（可能是主角被控制），继续尝试下一个武将
                                            self.report_battle_info(
                                                f"账号{account_index} 召唤{general_name}失败（可能主角被控制）", "warning"
                                            )
                                            summoned = False
                                            continue
                            else:
                                # 场上有刘备，只召唤曹操或魔化关羽
                                general_order = ["曹操", "魔化关羽"]
                                for general_name in general_order:
                                    general_image_path = self.bag_general_images.get(general_name)
                                    if not general_image_path:
                                        continue
                                    # 3秒内等待武将图片出现
                                    start_time = time.time()
                                    timeout = 3.0
                                    general_pos = None
                                    
                                    while time.time() - start_time < timeout:
                                        general_pos = self.find_image(account_index, general_image_path, self.summon_panel_region, 0)
                                        if general_pos:
                                            break
                                        time.sleep(0.2)
                                    
                                    if general_pos:
                                        # 找到武将，点击召唤
                                        self.report_battle_info(
                                            f"账号{account_index} 在召唤面板中找到{general_name}，准备召唤", "info"
                                        )
                                        self.click_position(account_index, general_pos.x, general_pos.y)
                                        time.sleep(CombatConstants.ACTION_DELAY)
                                        
                                        # 如果需要替换武将，处理替换逻辑
                                        if char_info["general_count"] == 1:
                                            # 需要替换，找到上场回合更多的武将
                                            oldest_general = None
                                            oldest_turns = -1
                                            for gen_info in char_info["generals"]:
                                                if gen_info.get("alive", True):
                                                    turns = gen_info.get("deployed_turn", 0)
                                                    if turns > oldest_turns:
                                                        oldest_turns = turns
                                                        oldest_general = gen_info
                                            
                                            if oldest_general and oldest_general.get("position"):
                                                # 点击需要替换的武将位置
                                                replace_pos = oldest_general["position"]
                                                self.report_battle_info(
                                                    f"账号{account_index} 需要替换武将，点击位置: {replace_pos}", "info"
                                                )
                                                self.click_position(account_index, replace_pos[0], replace_pos[1])
                                        
                                        # 等待召唤操作完成，然后检测是否成功
                                        time.sleep(0.5)  # 等待游戏响应
                                        
                                        # 检测3秒内是否出现"召唤成功"文字
                                        if self.check_summon_success(account_index, timeout=3.0):
                                            # 召唤成功
                                            summoned = True
                                            self.report_battle_info(f"账号{account_index} 召唤{general_name}成功", "action")
                                            break
                                        else:
                                            # 召唤失败（可能是主角被控制），继续尝试下一个武将
                                            self.report_battle_info(
                                                f"账号{account_index} 召唤{general_name}失败（可能主角被控制）", "warning"
                                            )
                                            summoned = False
                                            continue
                            
                            if summoned:
                                # 召唤成功，从全局记录中移除已召唤的武将，避免重复召唤
                                # 注意：这里不清空所有，只移除当前账号的武将
                                for dead_gen in self.global_dead_units["generals"][:]:
                                    if dead_gen.get("account_index") == account_index:
                                        self.global_dead_units["generals"].remove(dead_gen)
                                # 也清空本地记录（兼容旧代码）
                                self.dead_units[account_index]["generals"] = []
                                return True
                            # 如果召唤失败（找不到武将图片），返回False，让下一轮再尝试
                            else:
                                self.report_battle_info(
                                    f"账号{account_index} 检测到武将阵亡，但召唤失败（找不到武将图片），下一轮再尝试", "info"
                                )
                                return False
                            break  # 只处理第一个需要召唤的主角
                    
                    # 如果检测到武将阵亡，但所有主角都不需要召唤（general_count都>=2），继续执行技能释放
                    if not need_summon:
                        self.report_battle_info(
                            f"账号{account_index} 检测到武将阵亡，但所有主角武将已满，继续执行技能释放", "info"
                        )
                        # 不清空全局记录，因为其他账号可能还需要召唤
                
                # 如果检测到武将阵亡，但找不到召唤按钮（武将在操作），继续执行技能释放
                # 这里不需要return，让代码继续执行到技能释放逻辑

            # 2. 检查是否有主角阵亡,进行复活（使用全局记录）
            dead_main_chars = self.global_dead_units["main_chars"]
            if dead_main_chars:
                # 使用其他账号的主角进行复活(如果当前账号主角都阵亡)
                alive_chars = [c for c in self.unit_info[account_index]["main_chars"] if c["alive"]]
                if not alive_chars:
                    # 当前账号所有主角都阵亡,先尝试使用其他账号的主角进行复活
                    account_count = self.get_account_count()
                    found_other_alive_char = False
                    for other_account in range(account_count):
                        if other_account == account_index:
                            continue
                        other_alive_chars = [c for c in self.unit_info[other_account]["main_chars"] if c["alive"]]
                        if other_alive_chars:
                            # 使用其他账号的主角进行复活
                            dead_char = dead_main_chars[0]
                            # 检查是否正在被其他账号复活
                            if self._check_and_mark_reviving(account_index, dead_char["name"]):
                                if self.revive_main_char(other_account, dead_char):
                                    self._clear_reviving_mark(account_index, dead_char["name"])
                                    time.sleep(1)
                                    return True
                                else:
                                    # 复活失败，清除标记
                                    self._clear_reviving_mark(account_index, dead_char["name"])
                            else:
                                # 正在被其他账号复活，跳过
                                self.report_battle_info(
                                    f"账号{account_index} {dead_char['name']}正在被其他账号复活，跳过", "info"
                                )
                            found_other_alive_char = True
                    
                    # 如果所有账号的主角都阵亡了，让武将使用复活药复活主角
                    if not found_other_alive_char:
                        # 所有主角都阵亡了，当前操作的一定是武将，直接让武将使用复活药
                        dead_char = dead_main_chars[0]
                        # 检查是否正在被其他账号复活
                        if self._check_and_mark_reviving(account_index, dead_char["name"]):
                            if self.revive_main_char(account_index, dead_char):
                                self._clear_reviving_mark(account_index, dead_char["name"])
                                self.report_battle_info(f"账号{account_index} 武将使用复活药复活{dead_char['name']}", "success")
                                time.sleep(1)
                                return True
                            else:
                                # 复活失败，清除标记
                                self._clear_reviving_mark(account_index, dead_char["name"])
                        else:
                            # 正在被其他账号复活，跳过
                            self.report_battle_info(
                                f"账号{account_index} {dead_char['name']}正在被其他账号复活，跳过", "info"
                            )
                else:
                    # 使用当前账号存活的主角进行复活
                    dead_char = dead_main_chars[0]
                    # 检查是否正在被其他账号复活
                    if self._check_and_mark_reviving(account_index, dead_char["name"]):
                        if self.revive_main_char(account_index, dead_char):
                            self._clear_reviving_mark(account_index, dead_char["name"])
                            time.sleep(1)
                            return True
                        else:
                            # 复活失败，清除标记
                            self._clear_reviving_mark(account_index, dead_char["name"])
                    else:
                        # 正在被其他账号复活，跳过
                        self.report_battle_info(
                            f"账号{account_index} {dead_char['name']}正在被其他账号复活，跳过", "info"
                        )

            # 3. 没有血量低的单位需要处理,进行技能释放
            # 由于无法区分是主角还是武将，直接检测技能面板中所有可用的技能
            
            # 先检测其他攻击技能（主角和武将）
            # 主角技能：根据技能名称判断（只保留三个技能）
            main_char_skill_names = ["寂灭神劫", "锁魂", "天灾"]
            # 武将攻击技能：根据技能名称判断
            general_attack_skill_names = ["剑阵灭杀", "武神一怒"]
            
            # 检测所有攻击技能（2秒内找到）
            start_time = time.time()
            timeout = 2.0
            found_skill = None
            skill_type = None  # "main_char" 或 "general"
            
            while time.time() - start_time < timeout:
                # 先检测武将攻击技能
                for skill_name in general_attack_skill_names:
                    skill_image_path = self.skill_images.get(skill_name)
                    if skill_image_path:
                        skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                        if skill_pos:
                            found_skill = skill_name
                            skill_type = "general"
                            break
                if found_skill:
                    break
                
                # 再检测主角攻击技能
                for skill_name in main_char_skill_names:
                    skill_image_path = self.skill_images.get(skill_name)
                    if skill_image_path:
                        skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                        if skill_pos:
                            found_skill = skill_name
                            skill_type = "main_char"
                            break
                if found_skill:
                    break
                
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            if found_skill:
                # 找到了攻击技能，进行对应的操作
                skill_image_path = self.skill_images.get(found_skill)
                if skill_image_path:
                    # 再次查找技能图片（确保还在）
                    skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                    if skill_pos:
                        time.sleep(0.2)
                        char_type = "主角" if skill_type == "main_char" else "武将"
                        # 使用统一的技能点击验证方法
                        if self.click_skill_with_verification(account_index, skill_image_path, skill_pos, f"{char_type}{found_skill}", max_retries=1):
                            # 技能点击成功，继续后续操作
                            # 攻击技能：在敌军区域找lantiao图片
                            target_pos = self.find_target_lantiao(account_index, self.enemy_region, timeout=3.0)
                            
                            if target_pos:
                                # 直接点击找到的图片位置
                                self.click_position(account_index, target_pos.x, target_pos.y)
                                char_type = "主角" if skill_type == "main_char" else "武将"
                                self.report_battle_info(f"账号{account_index} {char_type}释放{found_skill}", "action")
                                time.sleep(1)
                                return True
                            else:
                                # 未找到lantiao图片，检查敌军场上是否有配置的敌军单位
                                enemy_cast_position = self.find_enemy_unit_on_field(account_index)
                                if enemy_cast_position:
                                    # 找到敌军单位，使用其cast_position
                                    self.click_position(account_index, enemy_cast_position[0], enemy_cast_position[1])
                                    char_type = "主角" if skill_type == "main_char" else "武将"
                                    self.report_battle_info(f"账号{account_index} {char_type}释放{found_skill}（使用敌军单位位置）", "action")
                                    time.sleep(1)
                                    return True
                                else:
                                    # 没有找到敌军单位，使用默认点位
                                    default_position = (104, 344)
                                    self.click_position(account_index, default_position[0], default_position[1])
                                    char_type = "主角" if skill_type == "main_char" else "武将"
                                    self.report_battle_info(f"账号{account_index} {char_type}释放{found_skill}（使用默认点位）", "action")
                                    time.sleep(1)
                                    return True
            
            # 如果找不到其他攻击技能，则检测是否有刘备的技能
            liubei_skill_names = ["加攻击", "加血", "清除状态", "控制"]
            is_liubei = False
            
            # 检测是否有刘备的技能（2秒内找到）
            start_time = time.time()
            timeout = 2.0
            while time.time() - start_time < timeout:
                for skill_name in liubei_skill_names:
                    skill_image_path = self.skill_images.get(skill_name)
                    if skill_image_path:
                        skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                        if skill_pos:
                            is_liubei = True
                            break
                if is_liubei:
                    break
                time.sleep(0.2)  # 每次查找间隔0.2秒
            
            # 如果找到刘备的技能，说明当前武将是刘备
            if is_liubei:
                # 判断是否需要清除状态
                need_clear = (
                    account_index in self.enemies_need_clear 
                    and self.enemies_need_clear[account_index]
                )
                
                if need_clear:
                    # 需要清除状态，使用清除技能
                    skill_image_path = self.skill_images.get("清除状态")
                    if skill_image_path:
                        # 3秒内循环查找技能图片
                        start_time = time.time()
                        timeout = 3.0
                        skill_pos = None
                        
                        while time.time() - start_time < timeout:
                            skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                            if skill_pos:
                                break
                            time.sleep(0.2)  # 每次查找间隔0.2秒
                        
                        if skill_pos:
                            # 检查清除状态技能是否在冷却中
                            skill_cd_config = self.skill_cd_config.get("清除状态", 0)
                            last_used_turn = self.liubei_skill_cd.get(account_index, {}).get("清除状态", -999)
                            if (self.current_turn - last_used_turn) >= skill_cd_config:
                                # 使用统一的技能点击验证方法
                                if self.click_skill_with_verification(account_index, skill_image_path, skill_pos, "清除状态", max_retries=1):
                                    # 技能点击成功，继续后续操作
                                    # 点击需要清除状态对应单位的固定点位
                                    enemy_info = self.enemies_need_clear[account_index][0]
                                    cast_position = enemy_info["position"]
                                    self.click_position(account_index, cast_position[0], cast_position[1])
                                    # 从需要清除列表中移除
                                    self.enemies_need_clear[account_index].remove(enemy_info)
                                    # 如果是诸葛亮，清除完成后重置标记
                                    if enemy_info.get("enemy_name") == "诸葛亮":
                                        self.zhugeliang_found[account_index] = False
                                    # 记录技能释放和冷却时间
                                    if account_index not in self.liubei_skill_cd:
                                        self.liubei_skill_cd[account_index] = {}
                                    self.liubei_skill_cd[account_index]["清除状态"] = self.current_turn
                                    self.report_battle_info(
                                        f"账号{account_index} 刘备释放清除状态清除{enemy_info['enemy_name']}状态", "action"
                                    )
                                    time.sleep(1)
                                    return True
                
                # 不需要清除或清除技能不可用，按照技能顺序找技能
                # 获取当前账号的技能索引（如果不存在则初始化为0）
                if account_index not in self.liubei_skill_index:
                    self.liubei_skill_index[account_index] = 0
                
                # 按照顺序尝试释放技能，跳过冷却中的技能
                sequence_length = len(self.liubei_skill_sequence)
                
                for attempt in range(sequence_length):
                    # 获取当前应该释放的技能
                    current_index = self.liubei_skill_index[account_index]
                    skill_to_use = self.liubei_skill_sequence[current_index]
                    
                    # 检查技能是否在冷却中
                    skill_cd_config = self.skill_cd_config.get(skill_to_use, 0)
                    last_used_turn = self.liubei_skill_cd.get(account_index, {}).get(skill_to_use, -999)
                    if (self.current_turn - last_used_turn) < skill_cd_config:
                        # 技能在冷却中，移动到下一个技能
                        self.liubei_skill_index[account_index] = (current_index + 1) % sequence_length
                        continue
                    
                    # 尝试释放技能（2秒内找到）
                    skill_image_path = self.skill_images.get(skill_to_use)
                    if not skill_image_path:
                        # 技能图片路径不存在，移动到下一个技能
                        self.liubei_skill_index[account_index] = (current_index + 1) % sequence_length
                        continue
                    
                    # 2秒内循环查找技能图片
                    start_time = time.time()
                    timeout = 2.0
                    skill_pos = None
                    
                    while time.time() - start_time < timeout:
                        skill_pos = self.find_image(account_index, skill_image_path, self.skill_panel_region, 0)
                        if skill_pos:
                            break
                        time.sleep(0.2)  # 每次查找间隔0.2秒
                    
                    if not skill_pos:
                        # 找不到技能图片，移动到下一个技能
                        self.liubei_skill_index[account_index] = (current_index + 1) % sequence_length
                        continue
                    
                    # 使用统一的技能点击验证方法
                    if not self.click_skill_with_verification(account_index, skill_image_path, skill_pos, skill_to_use, max_retries=1):
                        # 技能点击失败，跳过这次技能释放
                        self.liubei_skill_index[account_index] = (current_index + 1) % sequence_length
                        continue  # 继续下一个技能
                    
                    # 根据技能类型选择目标
                    if skill_to_use in ["加攻击", "加血"]:
                        # 辅助技能：在我军区域找"jifangliubei"图片
                        target_start_time = time.time()
                        target_timeout = 5.0
                        target_pos = None
                        
                        while time.time() - target_start_time < target_timeout:
                            target_pos = self.find_image(account_index, self.liubei_target_image, self.ally_region, 0)
                            if target_pos:
                                break
                            time.sleep(0.2)  # 每次查找间隔0.2秒
                        
                        if target_pos:
                            # 点击找到的图片位置
                            self.click_position(account_index, target_pos.x, target_pos.y)
                        else:
                            # 未找到"jifangliubei"图片，在己方区域找蓝条（lantiao）
                            lantiao_pos = self.find_target_lantiao(account_index, self.ally_region, timeout=3.0)
                            if lantiao_pos:
                                # 找到蓝条，点击蓝条位置
                                self.click_position(account_index, lantiao_pos.x, lantiao_pos.y)
                                self.report_battle_info(f"账号{account_index} 未找到jifangliubei图片，使用蓝条位置释放{skill_to_use}", "info")
                            else:
                                # 未找到蓝条，在己方队伍固定点位中随机选一个点击
                                ally_positions = []
                                if account_index in self.unit_positions:
                                    # 添加主角位置
                                    for char_name, x, y in self.unit_positions[account_index].get("main_chars", []):
                                        ally_positions.append((x, y))
                                    # 添加武将位置
                                    for general_name, x, y in self.unit_positions[account_index].get("generals", []):
                                        ally_positions.append((x, y))
                                
                                if ally_positions:
                                    # 随机选择一个己方单位位置
                                    random_position = random.choice(ally_positions)
                                    self.click_position(account_index, random_position[0], random_position[1])
                                    self.report_battle_info(f"账号{account_index} 未找到jifangliubei和蓝条，使用随机己方单位位置释放{skill_to_use}", "info")
                                else:
                                    # 如果没有任何己方单位位置，点击原地
                                    self.click_position(account_index, skill_pos.x, skill_pos.y)
                                    self.report_battle_info(f"账号{account_index} 未找到jifangliubei、蓝条和己方单位位置，点击原地释放{skill_to_use}", "info")
                    
                    elif skill_to_use == "控制":
                        # 攻击技能：在敌军区域找lantiao图片
                        target_pos = self.find_target_lantiao(account_index, self.enemy_region, timeout=3.0)
                        
                        if target_pos:
                            # 直接点击找到的图片位置
                            self.click_position(account_index, target_pos.x, target_pos.y)
                        else:
                            # 未找到lantiao图片，检查敌军场上是否有配置的敌军单位
                            enemy_cast_position = self.find_enemy_unit_on_field(account_index)
                            if enemy_cast_position:
                                # 找到敌军单位，使用其cast_position
                                self.click_position(account_index, enemy_cast_position[0], enemy_cast_position[1])
                            else:
                                # 没有找到敌军单位，使用默认点位
                                default_position = (104, 344)
                                self.click_position(account_index, default_position[0], default_position[1])
                                self.report_battle_info(f"账号{account_index} 刘备释放{skill_to_use}（使用默认点位）", "info")
                    
                    # 技能释放成功，记录冷却时间并移动到下一个技能
                    if account_index not in self.liubei_skill_cd:
                        self.liubei_skill_cd[account_index] = {}
                    self.liubei_skill_cd[account_index][skill_to_use] = self.current_turn
                    # 移动到下一个技能
                    self.liubei_skill_index[account_index] = (current_index + 1) % sequence_length
                    self.report_battle_info(f"账号{account_index} 刘备释放{skill_to_use}", "action")
                    time.sleep(1)
                    return True
                
                # 如果所有刘备技能都无法释放，继续执行加血逻辑（不直接返回）
            
            # 4. 如果技能都在CD中，检查是否有血量低的单位，使用恢复药
            low_hp_target = None
            
            # 先检查当前账号是否有血量低的单位
            if account_index in self.low_hp_units and self.low_hp_units[account_index]:
                low_hp_target = self.low_hp_units[account_index][0]  # 取第一个血量低的单位
            else:
                # 检查其他账号是否有血量低的单位
                account_count = self.get_account_count()
                for other_account in range(account_count):
                    if other_account != account_index and other_account in self.low_hp_units:
                        if self.low_hp_units[other_account]:
                            low_hp_target = self.low_hp_units[other_account][0]
                            break
            # 如果有血量低的单位，使用恢复药
            if low_hp_target:
                # 确定使用恢复药的账号（优先使用当前账号，如果当前账号没有存活主角则使用其他账号）
                use_account = account_index
                alive_chars = [c for c in self.unit_info[account_index]["main_chars"] if c["alive"]]
                if not alive_chars:
                    # 当前账号所有主角都阵亡，尝试使用其他账号
                    account_count = self.get_account_count()
                    for other_account in range(account_count):
                        if other_account != account_index:
                            other_alive_chars = [c for c in self.unit_info[other_account]["main_chars"] if c["alive"]]
                            if other_alive_chars:
                                use_account = other_account
                                break
                
                # 使用恢复药
                if self.use_heal_item(use_account, low_hp_target):
                    time.sleep(1)
                    return True
            
            # 如果没找到主角的三个技能和刘备技能，尝试检测防御按钮
            if not found_skill and not is_liubei:
                defense_button_pos = self.find_image(
                    account_index, self.button_images.get("防御按钮"), self.right_button_region, 0
                )
                if defense_button_pos:
                    self.click_position(account_index, defense_button_pos.x, defense_button_pos.y)
                    self.report_battle_info(f"账号{account_index} 主角未找到技能，执行防御", "action")
                    time.sleep(1)
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

        while self.polling_running:
            try:
                # 第零步：检测所有账号是否有zdzd弹窗，如果有则点击取消按钮
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
                
                # 第二步：检测所有账号的操作按钮（同步检测）
                accounts_ready = []  # 记录需要操作的账号列表
                for account_index in [0, 1, 2]:
                    if not self.polling_running:
                        break
                    
                    dm = self.get_account_dm(account_index)
                    if not dm:
                        continue
                    
                    # 检测操作按钮（确认在战斗页面且可以操作）
                    if self.check_action_button(account_index):
                        accounts_ready.append(account_index)
                
                # 第三步：如果有账号需要操作，先处理操作，操作完成后再进行状态检测
                if accounts_ready:
                    self.report_battle_info(f"检测到账号 {accounts_ready} 操作按钮，开始操作", "turn")
                    
                    # 为每个账号启动操作线程（实现同步操作）
                    operation_threads = []  # 记录操作线程
                    for account_index in accounts_ready:
                        thread = threading.Thread(
                            target=self.handle_our_turn,
                            args=(account_index,),
                            daemon=False  # 改为False，确保等待完成
                        )
                        thread.start()
                        operation_threads.append(thread)
                    
                    # 等待所有操作线程完成
                    for thread in operation_threads:
                        thread.join(timeout=30)  # 最多等待30秒，避免无限等待
                    
                    # 操作完成后，短暂延迟
                    time.sleep(0.5)
                    # 跳过状态检测，直接进入下一轮循环
                    continue
                
                # 清理过期的复活标记
                self._cleanup_expired_revive_marks()
                
                # 第一步：检测所有账号的状态（墓碑、敌军状态、场上是否有刘备）
                # 只在没有操作时进行状态检测
                # 只处理实际存在的账号（0, 1, 2）
                for account_index in [0, 1, 2]:
                    if not self.polling_running:
                        break
                    
                    # 检查账号是否可用
                    dm = self.get_account_dm(account_index)
                    if not dm:
                        continue  # 跳过未设置的账号

                    # 1. 检测墓碑(阵亡)
                    dead_list = self.check_tombstones(account_index)
                    if dead_list:
                        self.update_unit_info_from_tombstones(dead_list)

                    # 2. 检测敌军状态(需要清除的状态)
                    need_clear_list = self.check_enemy_status(account_index)
                    if need_clear_list:
                        self.update_enemy_status(need_clear_list)
                    
                    # 3. 检测场上是否有刘备（在非战斗回合检测，避免操作面板遮挡）
                    # 2秒内循环查找刘备图片
                    has_liubei = False
                    liubei_pos = self.find_image(account_index, self.has_liubei_on_field, self.ally_region, 0)
                    if liubei_pos:
                        has_liubei = True
                    self.has_liubei_on_field[account_index] = has_liubei
                    
                    # 4. 检测血量低的单位（在非战斗回合检测，避免操作面板遮挡）
                    # 只使用主账号（account_index=0）去检测所有账号的血量低单位
                    all_low_hp_units = []
                    account_count = self.get_account_count()
                    main_account_index = 0  # 主账号索引
                    for acc_idx in range(account_count):
                        # 使用主账号的dm对象检测所有账号的血量低单位
                        acc_low_hp = self.check_low_hp_units(acc_idx, detect_account_index=main_account_index)
                        all_low_hp_units.extend(acc_low_hp)
                    # 更新所有账号的血量低单位记录
                    if all_low_hp_units:
                        self.update_low_hp_units(all_low_hp_units)
                        

                # 轮询间隔
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
    def cleanup(self):
        """清理战斗脚本资源"""
        try:
            self.stop_polling_loop()
            # 关闭战斗播报窗口
            if self.battle_report_dialog:
                try:
                    self.battle_report_dialog.close_safely()
                except Exception:
                    pass
                self.battle_report_dialog = None
            self.report_battle_info("战斗脚本资源已清理", "system")
        except Exception as e:
            print(f"清理战斗脚本资源时出错: {e}")


# 示例使用
if __name__ == "__main__":
    # 这个脚本需要在 MyThread 的上下文中运行
    # 使用方式：
    # 1. 在 MyFrame 中添加新的脚本选项 "战斗中自动"
    # 2. 在 MyThread.run() 方法中添加对应的脚本执行分支
    # 3. 调用 CombatAutoScript 的功能

    print("战斗自动操作脚本已加载")
    print("请将此功能集成到 serveScript.py 的 MyThread 类中")
