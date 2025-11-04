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


# 修复：避免循环引用，移除直接导入
# from serveScript import MyThread  # 不再需要直接导入

# 定义 ResXy 类（避免循环引用）
class ResXy:
    """坐标结果类"""

    def __init__(self, x, y):
        self.x = x
        self.y = y


class BattleReportDialog(wx.Frame):
    """战斗实时播报窗口"""

    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="战斗实时播报",
            size=(800, 600),
            pos=(450, 50),
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
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

        title_text = wx.StaticText(title_panel, label="战斗实时播报",
                                   style=wx.ALIGN_CENTER)
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
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
            scroll_panel,  # 父窗口改为scroll_panel
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            size=(-1, -1)
        )
        # 设置字体
        log_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
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

        self.clear_button = wx.Button(button_panel, label="清空日志",
                                      size=(100, 35))
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
        self.add_log(
            f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            wx.Colour(100, 100, 100))
        self.add_log("=" * 60, wx.Colour(100, 100, 100))
        self.add_log("")

    def add_log(self, message, color=None):
        """添加日志消息（线程安全）"""
        # 确保color有默认值
        if color is None:
            color = wx.Colour(0, 0, 0)  # 默认黑色

        def _add_log():
            try:
                if not self or not hasattr(self,
                                           'log_text') or not self.log_text:
                    print(f"警告：无法添加日志，log_text不存在 - {message[:50]}")
                    return

                with self.log_lock:
                    # 添加时间戳
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    full_message = f"[{timestamp}] {message}\n"

                    # 设置文本颜色并追加
                    self.log_text.SetDefaultStyle(wx.TextAttr(color))
                    self.log_text.AppendText(full_message)

                    # 自动滚动到底部
                    try:
                        self.log_text.ShowPosition(
                            self.log_text.GetLastPosition())
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
                if hasattr(wx, 'CallAfter'):
                    wx.CallAfter(_add_log)
                else:
                    # 如果wx未初始化，直接尝试在主线程执行
                    _add_log()
        except Exception as e:
            # 打印错误以便调试
            print(f"CallAfter调用时出错: {e}")

    def on_clear(self, event):
        """清空日志"""
        self.log_text.Clear()
        self.add_log("日志已清空", wx.Colour(100, 100, 100))

    def close_safely(self):
        """安全关闭窗口"""
        if self:
            wx.CallAfter(self.Close)


class CombatAutoScript:
    def __init__(self, thread_instance):
        """
        初始化战斗自动操作
        :param thread_instance: MyThread 实例，用于访问大漠对象和区域定义
        """
        self.thread = thread_instance
        self.battle_report_dialog = None  # 战斗播报窗口
        
        # 线程安全锁（保护共享状态变量）
        self._state_lock = threading.Lock()
        
        # 定时器引用（用于清理）
        self._timer_refs = []
        
        # 回合超时和错误追踪（在__init__中初始化，避免未定义错误）
        self.turn_timeout = 25  # 每个回合最大操作时间（秒）
        self.turn_start_time = None  # 回合开始时间
        self.account_error_count = {}  # {account_index: error_count} 追踪每个账号的错误次数（字典类型）
        self.max_errors_per_turn = 5  # 每个回合最多允许的错误次数，超过则跳过回合
        
        # 创建并显示战斗播报窗口（延迟创建，确保wx应用已初始化）
        try:
            # 使用定时器延迟创建，确保wx应用程序已经运行
            timer = threading.Timer(0.3, self._create_battle_report_dialog)
            self._timer_refs.append(timer)
            timer.start()
        except Exception as e:
            print(f"创建战斗播报窗口失败: {e}")
        
        # 初始化战斗区域和配置
        self._init_combat_regions()

    def _create_battle_report_dialog(self):
        """创建战斗播报窗口（在主线程中调用）"""
        try:
            if self.battle_report_dialog is None:
                # 确保在主线程中创建
                if threading.current_thread() == threading.main_thread():
                    self.battle_report_dialog = BattleReportDialog(parent=None)
                    self.battle_report_dialog.Show()
                    self.report_battle_info("战斗播报系统已初始化", "system")
                else:
                    # 如果不在主线程，使用wx.CallAfter
                    wx.CallAfter(self._create_battle_report_dialog)
        except Exception as e:
            print(f"创建战斗播报窗口时出错: {e}")
            # 如果wx还未初始化，再次尝试延迟创建
            if "wx" in str(e).lower() or "app" in str(e).lower():
                timer = threading.Timer(0.5, self._create_battle_report_dialog)
                self._timer_refs.append(timer)
                timer.start()

    def report_battle_info(self, message, msg_type="info"):
        """
        播报战斗信息
        :param message: 消息内容
        :param msg_type: 消息类型 ("info", "success", "warning", "error", "system", "turn", "action")
        """
        # 如果窗口还未创建，尝试创建
        if self.battle_report_dialog is None:
            try:
                if hasattr(wx, 'GetApp') and wx.GetApp():
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

    def get_resource_path(self, relative_path):
        """获取资源文件路径"""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def _init_combat_regions(self):
        """初始化战斗区域和配置（从__init__中分离出来，避免代码过长）"""
        # 战斗相关区域定义（已根据游戏截图固定配置，900x580窗口）
        # 战斗区域配置（基于900x580游戏界面）
        # 格式：(x, y, w, h) - 左上角坐标和宽高（w, h是结束坐标）
        self.enemy_region = (0, 200, 500, 580)  # 敌军区域（左侧，覆盖整个左侧区域）
        self.ally_region = (500, 200, 900, 580)  # 己方区域（右侧，覆盖整个右侧区域）
        self.main_char_region = (680, 250, 900, 550)  # 主角区域（最右侧，三个主角位置）
        self.general_region = (480, 250, 700, 550)  # 武将区域（主角前方，武将位置）

        # 回合数识别区域（"23"显示的区域，屏幕上方中间）
        self.turn_indicator_region = (400, 0, 500,
                                      50)  # 回合数显示区域（上方中间，显示"23"等数字）

        # 右侧按钮区域（操作按钮区域）
        self.right_button_region = (400, 450, 600, 580)  # 右侧按钮区域（中间偏右，包含操作按钮）

        # 面板区域（点击按钮后弹出的面板）
        self.skill_panel_region = (200, 300, 500, 550)  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = (200, 300, 500, 550)  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (200, 300, 500, 550)  # 道具面板区域（点击道具按钮后弹出的面板）

        # 武将图片路径
        self.general_images = {
            '刘备': self.get_resource_path(
                'serveAssets/images/auto/miankong1.bmp'),
            '魔化关羽': f"{self.get_resource_path('serveAssets/images/auto/gangqi1.bmp')}|{self.get_resource_path('serveAssets/images/auto/shenyou1.bmp')}",
            '曹操': f"{self.get_resource_path('serveAssets/images/auto/bawang1.bmp')}|{self.get_resource_path('serveAssets/images/auto/luanshi1.bmp')}"
        }

        # 技能图片路径（需要根据实际技能图标添加）
        self.skill_images = {
            # 主角技能
            '主角群体攻击1': self.get_resource_path(
                'serveAssets/images/auto/lei1.bmp'),
            '主角群体攻击2': self.get_resource_path(
                'serveAssets/images/auto/jimie1.bmp'),
            '主角群体攻击3': self.get_resource_path(
                'serveAssets/images/auto/suohun1.bmp'),
            '主角群体攻击4': self.get_resource_path(
                'serveAssets/images/auto/tianzai2.bmp'),
            '主角群体攻击5': self.get_resource_path(
                'serveAssets/images/auto/tianzai1.bmp'),

            # 辅助武将技能
            '加血': self.get_resource_path(
                'serveAssets/images/auto/tuanjiezhiquan1.bmp'),
            '加攻击': self.get_resource_path(
                'serveAssets/images/auto/liubeizengshang1.bmp'),
            '控制': self.get_resource_path(
                'serveAssets/images/auto/liubeikong1.bmp'),
            '清除状态': self.get_resource_path(
                'serveAssets/images/auto/liubeijie1.bmp'),

            # 输出武将技能
            '武将群体攻击1': f"{self.get_resource_path('serveAssets/images/auto/caocaoqun3.bmp')}|{self.get_resource_path('serveAssets/images/auto/caocaoqun2.bmp')}",
            '武将群体攻击2': f"{self.get_resource_path('serveAssets/images/auto/moguqun1.bmp')}|{self.get_resource_path('serveAssets/images/auto/moguqun2.bmp')}"
        }

        # 物品图片
        self.item_images = {
            '恢复药': f"{self.get_resource_path('serveAssets/images/auto/yao.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao1.bmp')}",
            # 恢复药（加血又加蓝，2回合CD）
            '复活药': f"{self.get_resource_path('serveAssets/images/auto/fuhuo.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuo1.bmp')}",
            # 复活药（复活阵亡单位）
        }

        # 控制开关
        self.keep_support_general = False  # 是否保证辅助武将在场
        self.enable_main_heal = True  # 主角加血开关
        self.enable_main_summon = True  # 主角召唤开关

        # 刘备辅助技能释放顺序（移除加速技能）
        self.support_skill_sequence = ['加攻击', '加血', '控制', '清除状态']
        self.current_skill_index = 0  # 当前技能索引

        # 技能CD配置（回合数）
        self.skill_cd_config = {
            # 刘备技能
            '加血': 2,  # 2回合CD
            '清除状态': 4,  # 4回合CD
            '加攻击': 0,  # 无CD
            '控制': 0,  # 无CD
            # 主角技能
            '主角群体攻击1': 2,  # 2回合CD
            '主角群体攻击2': 3,  # 3回合CD
            '主角群体攻击3': 2,  # 2回合CD
            '主角群体攻击4': 2,  # 2回合CD
            '主角群体攻击5': 2,  # 2回合CD
            # 武将技能
            '武将群体攻击1': 0,  # 无CD
            '武将群体攻击2': 0,  # 无CD
        }

        # 药品CD配置
        self.item_cd_config = {
            '恢复药': 2,  # 2回合CD（红药，加血又加蓝）
            '复活药': 0,  # 无CD（复活药通常无CD限制）
        }

        # 技能CD追踪 {account_index: {skill_name: last_used_turn}}
        self.skill_cd_tracking = {}

        # 药品CD追踪 {account_index: {item_name: last_used_turn}}
        self.item_cd_tracking = {}

        # 武将追踪信息（存储每个账号的武将信息）
        self.general_tracking = {}  # {account_index: {general_name: {'type': 'support/dps', 'deployed_turn': turn_number, 'position': (x, y)}}}
        self.current_turn = 0  # 当前回合数
        self.support_general_account = None  # 哪个账号有辅助武将（场上）
        self.turn_processed = False  # 当前回合是否已处理（防止重复更新回合数）
        self._last_turn_state = {}  # 每个账号的上一回合状态 {account_index: bool}（用于检测回合变化）

        # 敌军状态图片路径（需要检测的四种状态）
        self.enemy_status_images = {
            '状态1': f"{self.get_resource_path('serveAssets/images/auto/longdan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/longdan2.bmp')}",
            '状态2': self.get_resource_path(
                'serveAssets/images/auto/tiandihudun1.bmp'),
            '状态3': self.get_resource_path(
                'serveAssets/images/auto/bumiexiongxin1.bmp'),
            '状态4': self.get_resource_path(
                'serveAssets/images/auto/gangqi1.bmp'),
        }

        # 敌人图片路径（用于识别敌人的位置）
        self.enemy_images = {
            '敌人1': self.get_resource_path(
                'serveAssets/images/auto/enemy1.bmp'),
            '敌人2': self.get_resource_path(
                'serveAssets/images/auto/enemy2.bmp'),
            '敌人3': self.get_resource_path(
                'serveAssets/images/auto/enemy3.bmp'),
            # 可以添加更多敌人的图片路径
        }

        # 主角图片路径（用于检测主角位置，存活状态通过墓碑检测）
        self.main_char_images = {
            '主角1': self.get_resource_path(
                'serveAssets/images/auto/zengjiagongjili1.bmp'),
            '主角2': self.get_resource_path(
                'serveAssets/images/auto/zengjiagongjili1.bmp'),
            '主角3': self.get_resource_path(
                'serveAssets/images/auto/zengjiagongjili1.bmp'),
        }

        # 墓碑图片路径（用于检测单位死亡状态）
        # 单位死亡后会在原地显示墓碑，通过检测墓碑来判断死亡
        self.tombstone_image = self.get_resource_path(
            'serveAssets/images/auto/duiyou2mubei1.bmp')  # 墓碑图片

        # 墓碑检测区域大小（以单位位置为中心的区域）
        # 用于在单位位置附近检测墓碑，避免位置偏移导致的检测失败
        self.tombstone_detection_radius = 30  # 墓碑检测半径（像素）

        # 敌人固定位置（已根据游戏截图固定配置）
        # 格式：{(account_index, enemy_index): (x, y)} - 敌人的中心点坐标
        # 根据截图，左侧3个敌人中心点大约在：(150, 300), (150, 375), (150, 450)
        self.fixed_enemy_positions = {
            # 账号0的敌人位置
            (0, 0): (150, 300),  # 敌人1中心点（上，最左侧）
            (0, 1): (150, 375),  # 敌人2中心点（中，最左侧）
            (0, 2): (150, 450),  # 敌人3中心点（下，最左侧）
            # 账号1的敌人位置（如果多开窗口布局一致）
            (1, 0): (150, 300),
            (1, 1): (150, 375),
            (1, 2): (150, 450),
            # 账号2的敌人位置（如果多开窗口布局一致）
            (2, 0): (150, 300),
            (2, 1): (150, 375),
            (2, 2): (150, 450),
        }

        # 背包武将图片（用于检测背包中是否有可用武将）
        self.bag_general_images = {
            '刘备': f"{self.get_resource_path('serveAssets/images/auto/liubei1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubei2.bmp')}",
            '魔化关羽': self.get_resource_path(
                'serveAssets/images/auto/mogu1.bmp'),
            '曹操': self.get_resource_path(
                'serveAssets/images/auto/caocao1.bmp'),
        }

        # 血量条图片（用于检测血量低的单位）
        # 识别到这张图片说明单位血量低，需要加血
        self.low_hp_indicator_image = self.get_resource_path(
            'serveAssets/images/auto/xueliangbuzu1.bmp')  # 血量低的标识图片

        # 9个血量条检测区域（每个角色和武将都有专门的区域）
        # 顺序：主角1、主角2、主角3、武将1、武将2、武将3、武将4、武将5、武将6
        # 格式：[(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
        # 基于900x580游戏界面，血量条通常显示在角色头顶上方
        self.hp_bar_regions = [
            (700, 250, 850, 280),  # 主角1血量条（上方）
            (700, 320, 850, 350),  # 主角2血量条（中间）
            (700, 390, 850, 420),  # 主角3血量条（下方）
            (520, 250, 670, 280),  # 武将1血量条（上，前排）
            (520, 320, 670, 350),  # 武将2血量条（中，前排）
            (520, 390, 670, 420),  # 武将3血量条（下，前排）
            (610, 250, 700, 280),  # 武将4血量条（上，后排）
            (610, 320, 700, 350),  # 武将5血量条（中，后排）
            (610, 390, 700, 420),  # 武将6血量条（下，后排）
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
        self.right_button_region = (400, 450, 600, 580)  # 右侧按钮区域（中间偏右，包含操作按钮）
        self.skill_panel_region = (200, 300, 500, 550)  # 技能面板区域（点击技能按钮后弹出的面板）
        self.summon_panel_region = (200, 300, 500, 550)  # 召唤面板区域（点击召唤按钮后弹出的面板）
        self.item_panel_region = (200, 300, 500, 550)  # 道具面板区域（点击道具按钮后弹出的面板）

        # 主角、武将、敌人的确切点位存储（单位外观中心位置，用于点击）
        # {account_index: {'main_chars': [(char_name, x, y), ...], 'generals': [(general_name, x, y), ...], 'enemies': [(enemy_name, x, y), ...]}}
        # 坐标基于之前配置的站位区域中心点计算
        # 格式：单位名称和中心坐标 (x, y)
        self.unit_positions = {
            # 默认配置（会在实际战斗中动态更新）
            # 中心点计算：区域中心 = (x1+x2)/2, (y1+y2)/2
            # 主角中心点（最右侧）
            0: {
                'main_chars': [
                    ('主角1', 775, 310),  # 主角1中心点 (700+850)/2, (280+340)/2
                    ('主角2', 775, 380),  # 主角2中心点 (700+850)/2, (350+410)/2
                    ('主角3', 775, 450),  # 主角3中心点 (700+850)/2, (420+480)/2
                ],
                'generals': [
                    # 武将中心点（会在战斗中动态更新，这里是初始参考值）
                    # 前排武将
                    ('武将1', 595, 310),  # 武将1中心点 (520+670)/2, (280+340)/2
                    ('武将2', 595, 380),  # 武将2中心点 (520+670)/2, (350+410)/2
                    ('武将3', 595, 450),  # 武将3中心点 (520+670)/2, (420+480)/2
                    # 后排武将
                    ('武将4', 655, 310),  # 武将4中心点 (610+700)/2, (280+340)/2
                    ('武将5', 655, 380),  # 武将5中心点 (610+700)/2, (350+410)/2
                    ('武将6', 655, 450),  # 武将6中心点 (610+700)/2, (420+480)/2
                ],
                'enemies': [
                    # 敌人中心点需要通过set_fixed_enemy_positions设置
                    # 一般敌人的中心点位置在左侧，x约150-350, y约300-450
                ]
            },
            1: {
                'main_chars': [
                    ('主角1', 775, 310),
                    ('主角2', 775, 380),
                    ('主角3', 775, 450),
                ],
                'generals': [
                    ('武将1', 595, 310),
                    ('武将2', 595, 380),
                    ('武将3', 595, 450),
                    ('武将4', 655, 310),
                    ('武将5', 655, 380),
                    ('武将6', 655, 450),
                ],
                'enemies': []
            },
            2: {
                'main_chars': [
                    ('主角1', 775, 310),
                    ('主角2', 775, 380),
                    ('主角3', 775, 450),
                ],
                'generals': [
                    ('武将1', 595, 310),
                    ('武将2', 595, 380),
                    ('武将3', 595, 450),
                    ('武将4', 655, 310),
                    ('武将5', 655, 380),
                    ('武将6', 655, 450),
                ],
                'enemies': []
            }
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
            (0, 0): (150, 300),  # 敌人1中心点（上，最左侧）
            (0, 1): (150, 375),  # 敌人2中心点（中，最左侧）
            (0, 2): (150, 450),  # 敌人3中心点（下，最左侧）
            # 账号1的三个敌人固定点位
            (1, 0): (150, 300),
            (1, 1): (150, 375),
            (1, 2): (150, 450),
            # 账号2的三个敌人固定点位
            (2, 0): (150, 300),
            (2, 1): (150, 375),
            (2, 2): (150, 450),
        }

        # 状态追踪（用于状态3和状态4的处理逻辑）
        # {account_index: {'status3_present': bool, 'status3_last_seen_turn': int, 'status4_present': bool}}
        self.enemy_status_tracking = {}

        # 己方异常状态图片路径（混乱、冰封、眩晕、嘲讽）
        self.ally_abnormal_status_images = {
            '冰封': self.get_resource_path(
                'serveAssets/images/auto/bingfeng1.bmp'),  # 冰封状态图片
        }

        # 己方单位异常状态追踪
        # {(account_index, unit_type, unit_name): ['状态1', '状态2', ...]}
        # unit_type: 'main_char' 或 'general'
        # unit_name: 主角名称（如'主角1'）或武将名称（如'刘备'）
        self.ally_status_tracking = {}

        # 异常状态检测区域大小（以单位位置为中心的区域）
        # 用于在单位位置附近检测异常状态图标
        self.status_detection_radius = 40  # 状态检测半径（像素）

        # 按钮图片路径
        self.button_images = {
            '技能按钮': self.get_resource_path(
                'serveAssets/images/auto/jineng.bmp'),
            '召唤按钮': self.get_resource_path(
                'serveAssets/images/auto/zhaohuan.bmp'),
            '道具按钮': self.get_resource_path(
                'serveAssets/images/auto/yaopin.bmp'),
        }

        # 三个账号的角色站位区域（基于900x580游戏界面）
        # 格式：(x, y, w, h) - 左上角坐标和宽高
        # 根据游戏截图：左侧是敌军，右侧是我军，最右侧是三个主角，前面是武将
        self.account_regions = [
                                   {
                                       # 主角位置（最右侧，x约750）
                                       'ally_char_1': (700, 280, 850, 340),
                                       # 主角1位置（上）
                                       'ally_char_2': (700, 350, 850, 410),
                                       # 主角2位置（中）
                                       'ally_char_3': (700, 420, 850, 480),
                                       # 主角3位置（下）

                                       # 武将位置（主角前方，x约550-650，分前后两列）
                                       # 前排武将（靠近中心）
                                       'ally_general_1': (520, 280, 670, 340),
                                       # 武将1位置（上，前排）
                                       'ally_general_2': (520, 350, 670, 410),
                                       # 武将2位置（中，前排）
                                       'ally_general_3': (520, 420, 670, 480),
                                       # 武将3位置（下，前排）
                                       # 后排武将（中间列，可选）
                                       'ally_general_4': (610, 280, 700, 340),
                                       # 武将4位置（上，后排）
                                       'ally_general_5': (610, 350, 700, 410),
                                       # 武将5位置（中，后排）
                                       'ally_general_6': (610, 420, 700, 480),
                                       # 武将6位置（下，后排）
                                   }
                               ] * 3  # 假设三个账号区域相同，如果不同需要分别定义

    def init_combat_tracking(self):
        """
        初始化战斗追踪（第一回合调用）
        检测所有账号的武将和主角情况并初始化追踪数据
        """
        self.general_tracking = {}
        self.unit_positions = {}
        self.dead_main_char_positions = {}  # 初始化阵亡主角位置存储
        self.skill_cd_tracking = {}
        self.item_cd_tracking = {}
        self.current_turn = 0
        self.support_general_account = None
        self.turn_processed = False  # 修复：初始化时重置回合处理标志
        self._last_turn_state = {}  # 修复：每个账号的回合状态 {account_index: bool}

        # 初始化己方状态追踪
        self.ally_status_tracking = {}

        # 注意：回合超时和错误追踪已在__init__中初始化，这里只需重置
        self.turn_start_time = None  # 重置回合开始时间
        self.account_error_count = {}  # 重置错误计数（清空所有账号的错误计数）

        # 检测每个账号的武将和主角
        account_count = self.get_account_count()
        for i in range(account_count):
            # 安全检查：确保account_dm已初始化且索引有效
            if not self.validate_account_index(i):
                continue

            self.general_tracking[i] = {}
            self.unit_positions[i] = {
                'main_chars': [],
                'generals': [],
                'enemies': []
            }

            # 检测武将
            generals = self.get_all_generals(i)
            for general in generals:
                general_name = general['name']
                general_pos = self.find_general(general_name, i)
                if general_pos:
                    self.general_tracking[i][general_name] = {
                        'type': general['type'],
                        'deployed_turn': self.current_turn,
                        'position': (general_pos.x, general_pos.y)
                    }
                    self.unit_positions[i]['generals'].append(
                        (general_name, general_pos.x, general_pos.y))

                    # 记录哪个账号有辅助武将
                    if general['type'] == 'support':
                        self.support_general_account = i

            # 检测主角
            team_status = self.get_team_status(i)
            if team_status:
                for char_name in team_status['main_chars']:
                    char_pos = self.find_main_char(char_name, i)
                    if char_pos:
                        self.unit_positions[i]['main_chars'].append(
                            (char_name, char_pos.x, char_pos.y))
                        print(
                            f"账号{i} 主角 {char_name} 位置: ({char_pos.x}, {char_pos.y})")

        # 检测敌人位置（需要在战斗开始后检测）
        # self.detect_enemy_positions(i)  # 注释掉，在auto_combat中实时检测

    def find_pic_with_timeout(self, dm_object, x, y, w, h, image_path,
                              timeout=3):
        """
        带超时的图片查找（包装FindPic）
        :param dm_object: 大漠对象
        :param x, y, w, h: 查找区域
        :param image_path: 图片路径（支持多个路径用|分隔）
        :param timeout: 超时时间（秒），默认3秒
        :return: FindPic返回的结果，如果超时返回None
        """
        if not dm_object or not image_path:
            return None

        start_time = time.time()

        # 处理多个图片路径（用|分隔）
        image_paths = image_path.split('|')
        if not image_paths:
            return None  # 如果路径列表为空，直接返回

        while time.time() - start_time < timeout:
            # 尝试所有图片路径
            for img_path in image_paths:
                try:
                    pos = dm_object.FindPic(int(x), int(y), int(w), int(h),
                                            img_path.strip(), "000000", 0.9, 0)
                    if pos and len(pos) > 0:
                        return pos
                except Exception as e:
                    # 单个图片查找失败，继续尝试下一个
                    continue

            # 短暂休眠，避免CPU占用过高
            time.sleep(0.1)

        # 超时返回None
        return None

    def wait_for_image(self, dm_object, x, y, w, h, image_path, timeout=3,
                       check_interval=0.1):
        """
        等待图片出现，图片出现立即返回，超时也退出
        :param dm_object: 大漠对象
        :param x, y, w, h: 查找区域（需要是宽度和高度格式）
        :param image_path: 图片路径（支持多个路径用|分隔）
        :param timeout: 超时时间（秒），默认3秒，建议2-3秒
        :param check_interval: 检测间隔（秒），默认0.1秒
        :return: (found, pos) - (是否找到, 位置信息) 如果找到返回(True, pos)，超时返回(False, None)
        """
        if not dm_object or not image_path:
            return (False, None)

        start_time = time.time()

        # 处理多个图片路径（用|分隔）
        image_paths = image_path.split('|')
        if not image_paths:
            return (False, None)  # 如果路径列表为空，直接返回

        while time.time() - start_time < timeout:
            # 尝试所有图片路径
            for img_path in image_paths:
                try:
                    pos = dm_object.FindPic(int(x), int(y), int(w), int(h),
                                            img_path.strip(), "000000", 0.9, 0)
                    if pos and len(pos) > 0:
                        # 图片出现，立即返回
                        return (True, pos)
                except Exception as e:
                    # 单个图片查找失败，继续尝试下一个
                    continue

            # 短暂休眠，避免CPU占用过高
            time.sleep(check_interval)

        # 超时，图片未出现
        return (False, None)

    def is_turn_timeout(self):
        """
        检查当前回合是否超时（25秒限制）
        :return: True if 超时, False otherwise
        """
        if self.turn_start_time is None:
            return False
        return time.time() - self.turn_start_time > self.turn_timeout

    def reset_turn_timer(self):
        """重置回合计时器（线程安全）"""
        with self._state_lock:
            self.turn_start_time = time.time()

    def get_panel_region(self, panel_type='skill'):
        """
        获取面板区域（统一处理面板区域获取）
        :param panel_type: 面板类型 ('skill', 'item', 'summon', 或其他使用right_button_region)
        :return: (panel_region, fallback_region) 或 (None, None) 如果都不可用
        """
        panel_region = None
        if panel_type == 'skill':
            panel_region = self.skill_panel_region
        elif panel_type == 'item':
            panel_region = self.item_panel_region
        elif panel_type == 'summon':
            panel_region = self.summon_panel_region

        fallback_region = self.right_button_region
        result_region = panel_region if panel_region else fallback_region

        return result_region, fallback_region

    def convert_region_coords(self, region):
        """
        转换区域坐标格式（从结束坐标转为宽度高度）
        :param region: 区域元组 (x, y, w, h) 其中w和h可能是结束坐标或宽度高度
        :return: (x, y, width, height) 或 None 如果格式错误
        """
        if not region:
            return None

        if not isinstance(region, (tuple, list)) or len(region) != 4:
            return None

        try:
            x, y, w, h = region
            # 判断w和h是结束坐标还是宽度高度
            # 如果w或h大于典型的屏幕尺寸（900或580），则认为是结束坐标
            if w > 900 or h > 580:
                width = w - x
                height = h - y
            else:
                width = w
                height = h

            # 验证转换后的值是否合理
            if width <= 0 or height <= 0:
                return None

            return (x, y, width, height)
        except (ValueError, TypeError) as e:
            return None

    def get_account_count(self):
        """
        获取账号数量（动态获取，替代硬编码的3）
        :return: 账号数量（只计算非None的账号）
        """
        account_dm_list = self.account_dm
        if not account_dm_list:
            return 0
        # 只计算非None的账号数量
        return sum(1 for dm in account_dm_list if dm is not None)

    def validate_account_index(self, account_index):
        """
        验证账号索引是否有效
        :param account_index: 账号索引
        :return: True if 有效, False otherwise
        """
        if not self.account_dm:
            return False
        if account_index < 0 or account_index >= len(self.account_dm):
            return False
        if not self.account_dm[account_index]:
            return False
        return True

    def safe_get_dict_value(self, dictionary, key, default=None):
        """
        安全获取字典值（处理嵌套字典和列表）
        :param dictionary: 字典对象
        :param key: 键
        :param default: 默认值
        :return: 值或默认值
        """
        if not dictionary:
            return default
        if not isinstance(dictionary, dict):
            return default
        return dictionary.get(key, default)

    def increment_error_count(self, account_index):
        """
        增加账号的错误计数（线程安全）
        :param account_index: 账号索引
        :return: 当前错误计数
        """
        with self._state_lock:
            if account_index not in self.account_error_count:
                self.account_error_count[account_index] = 0
            self.account_error_count[account_index] += 1
            return self.account_error_count[account_index]

    def reset_error_count(self, account_index):
        """重置账号的错误计数（线程安全）"""
        with self._state_lock:
            self.account_error_count[account_index] = 0

    def should_skip_turn(self, account_index):
        """
        判断是否应该跳过当前回合（错误过多或超时）
        :param account_index: 账号索引
        :return: True if 应该跳过, False otherwise
        """
        # 检查超时
        if self.is_turn_timeout():
            print(
                f"警告：账号{account_index} 回合操作超时（超过{self.turn_timeout}秒），跳过剩余操作")
            return True

        # 检查错误次数
        error_count = self.account_error_count.get(account_index, 0)
        if error_count >= self.max_errors_per_turn:
            print(
                f"警告：账号{account_index} 回合内错误次数过多（{error_count}次），跳过剩余操作")
            return True

        return False

    def execute_with_retry(self, func, max_retries=3, retry_delay=0.5,
                           account_index=None):
        """
        带重试的执行函数
        :param func: 要执行的函数（无参数）
        :param max_retries: 最大重试次数
        :param retry_delay: 重试间隔（秒）
        :param account_index: 账号索引（用于错误计数）
        :return: 函数执行结果，如果所有重试都失败返回None或False
        """
        for attempt in range(max_retries):
            try:
                result = func()
                if result:  # 如果返回True或非None，认为成功
                    return result
            except Exception as e:
                print(f"执行操作失败（尝试 {attempt + 1}/{max_retries}）: {e}")
            # 注意：异常时先不计数，等所有重试都失败后再计数

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        # 所有重试都失败，只计数一次
        if account_index is not None:
            self.increment_error_count(account_index)
        return None

    def set_combat_regions(self, enemy_region, ally_region, main_char_region,
                           general_region, turn_region,
                           right_button_region=None, hp_bar_regions=None):
        """
        设置战斗区域
        :param enemy_region: 敌军区域 (x, y, w, h)
        :param ally_region: 己方区域 (x, y, w, h)
        :param main_char_region: 主角区域 (x, y, w, h)
        :param general_region: 武将区域 (x, y, w, h)
        :param turn_region: 回合指示器区域 (x, y, w, h)
        :param right_button_region: 右侧按钮区域 (x, y, w, h)
        :param hp_bar_regions: 9个血量条检测区域列表 [(x1, y1, w1, h1), (x2, y2, w2, h2), ...]
        """
        self.enemy_region = enemy_region
        self.ally_region = ally_region
        self.main_char_region = main_char_region
        self.general_region = general_region
        self.turn_indicator_region = turn_region
        if right_button_region:
            self.right_button_region = right_button_region
        if hp_bar_regions:
            if len(hp_bar_regions) == 9:
                self.hp_bar_regions = hp_bar_regions
            else:
                print(
                    f"警告：血量条区域数量不正确，期望9个，实际{len(hp_bar_regions)}个")

    def set_fixed_enemy_positions(self, account_index, enemy_positions):
        """
        设置敌人的固定点位（三个点位）
        :param account_index: 账号索引
        :param enemy_positions: 敌人位置列表，格式为 [(x1, y1), (x2, y2), (x3, y3)]
        """
        if len(enemy_positions) >= 3:
            for i in range(3):
                self.fixed_enemy_positions[(account_index, i)] = \
                    enemy_positions[i]
            print(f"账号{account_index} 设置了3个固定敌人点位")
        else:
            print(f"警告：账号{account_index} 提供的敌人点位数量不足3个")

    def is_my_turn(self, dm_object):
        """
        判断是否是己方回合（通过检测右侧按钮区是否存在来判断）
        :param dm_object: 大漠对象
        :return: True if 己方回合, False otherwise
        """
        if not self.right_button_region:
            # 如果没有设置按钮区域，使用原来的方法检测回合指示器
            if self.turn_indicator_region:
                try:
                    x, y, w, h = self.turn_indicator_region
                    result = dm_object.FindStrEx(int(x), int(y), int(w), int(h),
                                                 "25", "ffffff-000000", 1.0)
                    if result and '|' in result:
                        return int(result.split('|')[0]) >= 0
                except Exception as e:
                    print(f"检测回合指示器时出错: {e}")
            return False

        # 通过检测右侧按钮区域是否存在来判断是否是我方回合
        # 如果按钮区域存在（可以识别到按钮），说明是我方回合
        try:
            if not isinstance(self.right_button_region, (tuple, list)) or len(
                    self.right_button_region) != 4:
                return False
            x, y, w, h = self.right_button_region
            # 检测任意一个按钮是否存在（技能按钮、召唤按钮、道具按钮）
            for button_name in ['技能按钮', '召唤按钮', '道具按钮']:
                image_path = self.button_images.get(button_name, '')
                if image_path:
                    try:
                        # 使用带超时的查找（快速检测，1秒超时）
                        pos = self.find_pic_with_timeout(dm_object, x, y, w, h,
                                                         image_path, timeout=1)
                        if pos and len(pos) > 0:
                            return True
                    except Exception as e:
                        print(f"检测按钮 {button_name} 时出错: {e}")
                        continue
        except (ValueError, TypeError) as e:
            print(f"判断回合状态时出错: {e}")
        return False

    def check_tombstone_at_position(self, dm_object, pos_x, pos_y):
        """
        检查指定位置是否有墓碑（判断单位是否死亡）
        :param dm_object: 大漠对象
        :param pos_x: 位置X坐标
        :param pos_y: 位置Y坐标
        :return: True if 检测到墓碑（死亡），False if 未检测到（存活）
        """
        if not dm_object or not self.tombstone_image:
            return False

        # 在单位位置附近检测墓碑（使用检测半径）
        radius = self.tombstone_detection_radius
        # 计算检测区域：左上角坐标和宽高
        # 注意：这里w和h应该是宽度和高度，不是结束坐标
        detection_region = (
            max(0, int(pos_x - radius)),  # 左上角x
            max(0, int(pos_y - radius)),  # 左上角y
            int(radius * 2),  # 宽度
            int(radius * 2)  # 高度
        )

        try:
            x, y, width, height = detection_region
            # FindPic参数：x, y, w, h 其中w和h是宽度和高度
            # 使用带超时的图片查找（1秒超时，墓碑检测应该很快）
            pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                             self.tombstone_image, timeout=1)
            # 如果找到墓碑，说明单位已死亡
            return pos and len(pos) > 0
        except Exception as e:
            print(f"检测墓碑时出错: {e}")
            return False

    def find_general(self, general_name, account_index):
        """
        在指定账号中查找武将
        :param general_name: 武将名称（'刘备', '魔化关羽', '曹操'）
        :param account_index: 账号索引（0=主账号, 1=账号1, 2=账号2）
        :return: ResXy 对象 or False
        """
        if not self.account_dm or account_index < 0 or account_index >= len(
                self.account_dm):
            return False

        dm_object = self.account_dm[account_index]
        if not dm_object:
            return False

        if not self.ally_region:
            return False

        x, y, w, h = self.ally_region
        # 根据注释，w和h是结束坐标，需要转换为宽度和高度用于FindPic
        width = w - x if w > 900 or h > 580 else w  # 判断是结束坐标还是宽度
        height = h - y if w > 900 or h > 580 else h

        image_path = self.general_images.get(general_name, '')
        if not image_path:
            return False

        pos = dm_object.FindPic(int(x), int(y), int(width), int(height),
                                image_path, "000000", 0.9999, 0)
        if pos and len(pos) > 0:
            try:
                # 修复：检查pos的类型，如果是tuple则直接解包，如果是字符串则split
                if isinstance(pos, tuple):
                    if len(pos) >= 2:
                        pos_x, pos_y = pos[0], pos[1]
                    else:
                        return False
                elif isinstance(pos, str):
                    pos_list = pos.split(',')
                    if len(pos_list) >= 2:
                        # 修复：验证是否为有效数字
                        pos_x = int(pos_list[0])
                        pos_y = int(pos_list[1])
                    else:
                        return False
                else:
                    return False
                # 检查该位置是否有墓碑
                if self.check_tombstone_at_position(dm_object, pos_x,
                                                    pos_y):
                    # 检测到墓碑，说明武将已死亡
                    print(
                        f"账号{account_index} 武将 {general_name} 位置 ({pos_x}, {pos_y}) 检测到墓碑，已死亡")
                    return False

                # 未检测到墓碑，说明武将存活
                return ResXy(pos_x, pos_y)
            except (ValueError, IndexError) as e:
                print(f"解析武将 {general_name} 位置失败: {pos}, 错误: {e}")
                return False

        # 如果未找到武将图片，检查之前保存的位置是否有墓碑
        if account_index in self.unit_positions:
            for saved_general_name, saved_x, saved_y in self.unit_positions[
                account_index].get('generals', []):
                if saved_general_name == general_name:
                    # 检查保存的位置是否有墓碑
                    if self.check_tombstone_at_position(dm_object, saved_x,
                                                        saved_y):
                        print(
                            f"账号{account_index} 武将 {general_name} 之前位置 ({saved_x}, {saved_y}) 检测到墓碑，已死亡")
                        return False
                    # 如果没有墓碑，可能还存活，但位置已改变，返回False让系统重新搜索
                    return False

        return False

    def find_main_char(self, char_name, account_index):
        """
        在指定账号中查找主角
        :param char_name: 主角名称（'主角1', '主角2', '主角3'）
        :param account_index: 账号索引（0=主账号, 1=账号1, 2=账号2）
        :return: ResXy 对象 or False
        """
        if account_index < 0 or account_index >= len(self.account_dm):
            return False
    def find_main_char(self, char_name, account_index):
        """
        在指定账号中查找主角
        :param char_name: 主角名称（'主角1', '主角2', '主角3'）
        :param account_index: 账号索引（0=主账号, 1=账号1, 2=账号2）
        :return: ResXy 对象 or False
        """
        if account_index < 0 or account_index >= len(self.account_dm):
            return False

        dm_object = self.account_dm[account_index]
        if not dm_object:
            return False

        if not self.main_char_region:
            return False

        x, y, w, h = self.main_char_region
        # 转换坐标格式
        width = w - x if w > 900 or h > 580 else w  # 判断是结束坐标还是宽度
        height = h - y if w > 900 or h > 580 else h

        image_path = self.main_char_images.get(char_name, '')
        if not image_path:
            return False

        # 使用带超时的图片查找（2秒超时）
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=2)
        if pos and len(pos) > 0:
            try:
                # 修复：检查pos的类型，如果是tuple则直接解包，如果是字符串则split
                if isinstance(pos, tuple):
                    if len(pos) >= 2:
                        pos_x, pos_y = pos[0], pos[1]
                    else:
                        return False
                elif isinstance(pos, str):
                    pos_list = pos.split(',')
                    if len(pos_list) >= 2:
                        # 修复：验证是否为有效数字
                        pos_x = int(pos_list[0])
                        pos_y = int(pos_list[1])
                    else:
                        return False
                else:
                    return False

                # 检查该位置是否有墓碑
                if self.check_tombstone_at_position(dm_object, pos_x,
                                                    pos_y):
                    # 检测到墓碑，说明主角已死亡
                    print(
                        f"账号{account_index} 主角 {char_name} 位置 ({pos_x}, {pos_y}) 检测到墓碑，已死亡")
                    return False

                # 未检测到墓碑，说明主角存活
                return ResXy(pos_x, pos_y)
            except (ValueError, IndexError) as e:
                print(f"解析主角 {char_name} 位置失败: {pos}, 错误: {e}")
                return False

        # 如果未找到主角图片，检查之前保存的位置是否有墓碑
        if account_index in self.unit_positions:
            for saved_char_name, saved_x, saved_y in self.unit_positions[
                account_index].get('main_chars', []):
                if saved_char_name == char_name:
                    # 检查保存的位置是否有墓碑
                    if self.check_tombstone_at_position(dm_object, saved_x,
                                                        saved_y):
                        print(
                            f"账号{account_index} 主角 {char_name} 之前位置 ({saved_x}, {saved_y}) 检测到墓碑，已死亡")
                        return False
                    # 如果没有墓碑，可能还存活，但位置已改变，返回False让系统重新搜索
                    return False

        return False
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return False

        if not self.main_char_region:
            return False

        x, y, w, h = self.main_char_region
        # 转换坐标格式
        width = w - x if w > 900 or h > 580 else w  # 判断是结束坐标还是宽度
        height = h - y if w > 900 or h > 580 else h

        image_path = self.main_char_images.get(char_name, '')
        if not image_path:
            return False

        # 使用带超时的图片查找（2秒超时）
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=2)
        if pos and len(pos) > 0:
            try:
                pos_list = pos.split(',')
                if len(pos_list) >= 2:
                    # 修复：验证是否为有效数字
                    pos_x = int(pos_list[0])
                    pos_y = int(pos_list[1])

                    # 检查该位置是否有墓碑
                    if self.check_tombstone_at_position(dm_object, pos_x,
                                                        pos_y):
                        # 检测到墓碑，说明主角已死亡
                        print(
                            f"账号{account_index} 主角 {char_name} 位置 ({pos_x}, {pos_y}) 检测到墓碑，已死亡")
                        return False

                    # 未检测到墓碑，说明主角存活
                    return ResXy(pos_x, pos_y)
            except (ValueError, IndexError) as e:
                print(f"解析主角 {char_name} 位置失败: {pos}, 错误: {e}")
                return False

        # 如果未找到主角图片，检查之前保存的位置是否有墓碑
        # 这样可以检测到已死亡但位置已知的主角
        if account_index in self.unit_positions:
            for saved_char_name, saved_x, saved_y in self.unit_positions[
                account_index].get('main_chars', []):
                if saved_char_name == char_name:
                    # 检查保存的位置是否有墓碑
                    if self.check_tombstone_at_position(dm_object, saved_x,
                                                        saved_y):
                        print(
                            f"账号{account_index} 主角 {char_name} 之前位置 ({saved_x}, {saved_y}) 检测到墓碑，已死亡")
                        return False
                    # 如果没有墓碑，可能还存活，但位置已改变，返回False让系统重新搜索
                    return False

        return False

    def detect_enemy_positions(self, account_index):
        """
        检测并记录敌人的确切位置
        :param account_index: 账号索引
        """
        if account_index not in self.unit_positions:
            self.unit_positions[account_index] = {'main_chars': [],
                                                  'generals': [], 'enemies': []}

        if not self.enemy_region or not self.account_dm or account_index >= len(
                self.account_dm) or not self.account_dm[account_index]:
            return

        dm_object = self.account_dm[account_index]
        # 修复：再次确认区域格式正确后再解包
        if not isinstance(self.enemy_region, (tuple, list)) or len(
                self.enemy_region) != 4:
            return
        x, y, w, h = self.enemy_region
        # 根据注释，w和h是结束坐标，需要转换为宽度和高度用于FindPic
        width = w - x  # 宽度 = 结束x - 开始x
        height = h - y  # 高度 = 结束y - 开始y

        # 检测所有敌人的位置
        enemy_positions = []
        for enemy_name, enemy_image_path in self.enemy_images.items():
            try:
                pos = dm_object.FindPic(int(x), int(y), int(width), int(height),
                                        enemy_image_path, "000000", 0.9999, 0)
                if pos and len(pos) > 0:
                    try:
                        pos_list = pos.split(',')
                        if len(pos_list) >= 2:
                            # 修复：验证是否为有效数字
                            enemy_x = int(pos_list[0])
                            enemy_y = int(pos_list[1])

                            # 检查该位置是否有墓碑
                            if self.check_tombstone_at_position(dm_object,
                                                                enemy_x,
                                                                enemy_y):
                                # 检测到墓碑，说明敌人已死亡，不添加到列表
                                print(
                                    f"账号{account_index} 敌人 {enemy_name} 位置 ({enemy_x}, {enemy_y}) 检测到墓碑，已死亡")
                                continue

                            # 未检测到墓碑，说明敌人存活
                            enemy_positions.append(
                                (enemy_name, enemy_x, enemy_y))
                            print(
                                f"账号{account_index} 检测到存活 {enemy_name} 位置: ({enemy_x}, {enemy_y})")
                    except (ValueError, IndexError) as e:
                        print(
                            f"解析敌人 {enemy_name} 位置失败: {pos}, 错误: {e}")
                        continue
            except Exception as e:
                print(f"检测敌人 {enemy_name} 时出错: {e}")
                continue

        # 更新敌人位置列表
        self.unit_positions[account_index]['enemies'] = enemy_positions

    def _get_account_dm(self):
        """
        获取账号大漠对象列表（延迟初始化）
        :return: [dm, win1_dm, win2_dm] 列表
        """
        if self._account_dm is None:
            # 延迟初始化，安全地获取账号对象
            try:
                self._account_dm = [
                    getattr(self.thread, 'dm', None) if self.thread else None,
                    # 主账号
                    getattr(self.thread, 'win1_dm',
                            None) if self.thread else None,  # 账号1
                    getattr(self.thread, 'win2_dm',
                            None) if self.thread else None  # 账号2
                ]
            except AttributeError as e:
                print(f"获取账号对象时出错: {e}")
                self._account_dm = [None, None, None]
        return self._account_dm

    @property
    def account_dm(self):
        """
        账号大漠对象列表属性（向后兼容）
        """
        return self._get_account_dm()

    def has_support_general_alive(self, account_index):
        """
        检查指定账号是否有辅助武将存活
        :param account_index: 账号索引
        :return: True if 刘备存活, False otherwise
        """
        result = self.find_general('刘备', account_index)
        return result is not False and result is not None

    def get_all_generals(self, account_index):
        """
        获取指定账号中所有在场的武将列表
        :param account_index: 账号索引
        :return: 武将列表，每个元素包含武将名称和类型
        """
        generals = []
        general_info = [
            ('刘备', 'support'),
            ('魔化关羽', 'dps'),
            ('曹操', 'dps')
        ]

        for general_name, general_type in general_info:
            if self.find_general(general_name, account_index):
                generals.append({
                    'name': general_name,
                    'type': general_type
                })

        return generals

    def update_general_tracking(self, account_index):
        """
        更新武将追踪信息（检测阵亡的武将和主角）
        """
        if account_index not in self.general_tracking:
            self.general_tracking[account_index] = {}
        if account_index not in self.unit_positions:
            self.unit_positions[account_index] = {'main_chars': [],
                                                  'generals': [], 'enemies': []}

        # 检测武将阵亡
        current_generals = self.get_all_generals(account_index)
        current_general_names = {g['name'] for g in current_generals}

        # 检测哪些武将阵亡了
        dead_generals = []
        for general_name in list(self.general_tracking[account_index].keys()):
            if general_name not in current_general_names:
                # 武将阵亡
                if self.general_tracking[account_index][general_name][
                    'type'] == 'support':
                    # 辅助武将阵亡
                    self.support_general_account = None
                dead_generals.append(general_name)
                print(f"账号{account_index}的武将{general_name}阵亡了")
                del self.general_tracking[account_index][general_name]

        # 修复：清空武将位置列表，重新填充所有存活武将的位置（与主角位置更新策略一致）
        self.unit_positions[account_index]['generals'] = []

        # 检测新上场的武将并更新所有存活武将的位置
        for general in current_generals:
            general_name = general['name']
            general_pos = self.find_general(general_name, account_index)
            # 防御性检查：确保general_pos不是None且是ResXy对象
            pos = (general_pos.x, general_pos.y) if general_pos and hasattr(general_pos, 'x') and hasattr(general_pos, 'y') else None

            if general_name not in self.general_tracking[account_index]:
                # 新武将上场
                self.general_tracking[account_index][general_name] = {
                    'type': general['type'],
                    'deployed_turn': self.current_turn,
                    'position': pos
                }
                if general['type'] == 'support':
                    self.support_general_account = account_index
            else:
                # 更新已存在武将的位置信息（位置可能发生变化）
                self.general_tracking[account_index][general_name][
                    'position'] = pos

            # 更新位置列表（所有存活武将）
            if general_pos:
                self.unit_positions[account_index]['generals'].append(
                    (general_name, general_pos.x, general_pos.y))

        # 检测主角阵亡（修复BUG：在清空列表前保存阵亡主角的位置）
        team_status = self.get_team_status(account_index)
        if team_status:
            current_main_chars = set(team_status['main_chars'])
            tracked_main_chars_dict = {}

            # 在清空列表前，保存所有追踪的主角位置
            for char_name, x, y in self.unit_positions[account_index][
                'main_chars']:
                tracked_main_chars_dict[char_name] = (x, y)

            tracked_main_chars = set(tracked_main_chars_dict.keys())

            # 检测阵亡的主角，并保存其位置信息（用于复活）
            dead_main_chars = tracked_main_chars - current_main_chars
            for char_name in dead_main_chars:
                death_msg = f"账号{account_index}的主角{char_name}阵亡了"
                print(death_msg)
                self.report_battle_info(death_msg, "warning")
                # 保存阵亡主角的位置到独立字典（用于后续复活）
                if account_index not in self.dead_main_char_positions:
                    self.dead_main_char_positions[account_index] = {}
                if char_name in tracked_main_chars_dict:
                    self.dead_main_char_positions[account_index][char_name] = \
                        tracked_main_chars_dict[char_name]

            # 更新主角位置列表
            self.unit_positions[account_index]['main_chars'] = []
            for char_name in current_main_chars:
                char_pos = self.find_main_char(char_name, account_index)
                if char_pos:
                    self.unit_positions[account_index]['main_chars'].append(
                        (char_name, char_pos.x, char_pos.y))
                    print(
                        f"账号{account_index} 主角 {char_name} 存活，位置: ({char_pos.x}, {char_pos.y})")

    def get_team_status(self, account_index):
        """
        获取指定账号的完整队伍状态
        :param account_index: 账号索引
        :return: 包含主角和武将状态的字典
        """
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return None

        # 检测主角存活状态
        main_chars = []
        # 修复：检查区域是否已设置
        if not self.main_char_region:
            # 区域未设置，返回空列表（不影响其他状态的检测）
            pass
        else:
            for char_name, char_image in self.main_char_images.items():
                try:
                    x, y, w, h = self.main_char_region
                    # 转换坐标格式
                    width = w - x if w > 900 or h > 580 else w
                    height = h - y if w > 900 or h > 580 else h
                    # 使用带超时的图片查找（2秒超时）
                    pos = self.find_pic_with_timeout(dm_object, x, y, width,
                                                     height, char_image,
                                                     timeout=2)
                    if pos and len(pos) > 0:
                        main_chars.append(char_name)
                except Exception as e:
                    print(f"检测主角 {char_name} 时出错: {e}")
                    continue

        # 获取在场武将
        generals = self.get_all_generals(account_index)

        # 检测是否有辅助武将
        has_support = any(g['type'] == 'support' for g in generals)

        return {
            'main_chars': main_chars,  # 存活的男主角列表
            'generals': generals,  # 在场武将列表
            'has_support': has_support,  # 是否有辅助武将
            'general_count': len(generals)  # 武将数量
        }

    def check_bag_for_general(self, account_index, general_name):
        """
        检查背包中是否有指定武将
        :param account_index: 账号索引
        :param general_name: 武将名称
        :return: True if 背包中有该武将
        """
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return False

        # 背包区域（需要根据实际游戏界面设置）
        # 修复：使用召唤面板区域或右侧按钮区域作为背包检测区域
        bag_region = self.summon_panel_region if self.summon_panel_region else (
            self.right_button_region if self.right_button_region else (0, 0,
                                                                       500,
                                                                       500))
        if isinstance(bag_region, tuple) and len(bag_region) == 4:
            pass  # 使用提供的区域
        else:
            bag_region = (0, 0, 500, 500)  # 备用默认区域

        image_path = self.bag_general_images.get(general_name, '')
        if not image_path:
            return False

        # 安全检查：确保bag_region格式正确
        if not isinstance(bag_region, (tuple, list)) or len(bag_region) != 4:
            return False

        x, y, w, h = bag_region
        # 根据注释，w和h是结束坐标，需要转换为宽度和高度用于FindPic
        width = w - x if w > 900 or h > 580 else w  # 判断是结束坐标还是宽度
        height = h - y if w > 900 or h > 580 else h

        # 使用带超时的图片查找（2秒超时），避免立即返回false
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=2)
        return pos and len(pos) > 0

    def check_bag_for_support_general(self, account_index):
        """
        检查背包中是否有辅助武将
        :param account_index: 账号索引
        :return: True if 背包中有辅助武将（刘备）
        """
        return self.check_bag_for_general(account_index, '刘备')

    def need_summon_support_general(self, account_index):
        """
        判断是否需要召唤辅助武将（刘备）
        :param account_index: 账号索引
        :return: True if 需要召唤刘备, False otherwise
        """
        if not self.keep_support_general:
            return False

        generals = self.get_all_generals(account_index)
        has_support = any(g['name'] == '刘备' for g in generals)

        # 如果没有辅助武将，需要召唤
        return not has_support

    def can_summon_general(self, account_index):
        """
        判断是否可以召唤武将（检查武将数量是否少于2个）
        :param account_index: 账号索引
        :return: True if 可以召唤（少于2个武将）, False otherwise
        """
        generals = self.get_all_generals(account_index)
        # 每个主角最多可以出战2个武将
        return len(generals) < 2

    def is_skill_ready(self, account_index, skill_name):
        """
        检查技能是否可以使用（不在CD中）
        :param account_index: 账号索引
        :param skill_name: 技能名称
        :return: True if 技能可以使用, False otherwise
        """
        cd_rounds = self.skill_cd_config.get(skill_name, 0)
        if cd_rounds == 0:
            return True  # 无CD技能

        if account_index not in self.skill_cd_tracking:
            self.skill_cd_tracking[account_index] = {}

        last_used_turn = self.skill_cd_tracking[account_index].get(skill_name,
                                                                   -999)
        turns_passed = self.current_turn - last_used_turn

        return turns_passed >= cd_rounds

    def is_skill_visible(self, account_index, skill_name, dm_object):
        """
        检测技能是否在技能面板中可见（不在CD中，技能图标可见）
        如果能找到技能图标，说明技能没有进入CD，可以使用
        如果找不到技能图标，说明技能在CD中或被控制状态影响
        :param account_index: 账号索引
        :param skill_name: 技能名称
        :param dm_object: 大漠对象
        :return: True if 技能可见（可用）, False otherwise
        """
        if not dm_object:
            return False

        panel_region, _ = self.get_panel_region('skill')
        if not panel_region:
            print(
                f"警告：账号{account_index} 未设置技能面板区域，无法检测技能可见性")
            return False

        # 先检查技能面板是否已经打开
        coords = self.convert_region_coords(panel_region)
        if not coords:
            print(f"警告：技能面板区域格式错误: {panel_region}")
            return False

        x, y, width, height = coords

        test_skill = self.skill_images.get('主角群体攻击1', '')
        panel_opened = False

        if test_skill:
            test_pos = self.find_pic_with_timeout(dm_object, x, y, width,
                                                  height, test_skill, timeout=2)
            panel_opened = test_pos and len(test_pos) > 0

        # 如果面板未打开，打开它
        if not panel_opened:
            if not self.click_right_button('技能按钮', dm_object):
                return False

            # 等待面板出现（最多等待3秒）
            if test_skill:
                found, test_pos = self.wait_for_image(dm_object, x, y, width,
                                                      height, test_skill,
                                                      timeout=3,
                                                      check_interval=0.1)
                if found and test_pos:
                    panel_opened = True
                else:
                    print(f"警告：技能面板可能未完全打开（已等待3秒）")
                    return False
            else:
                # 如果没有test_skill，假设面板已打开（理论上不应该发生）
                print(f"警告：账号{account_index} test_skill为空，假设面板已打开")
                panel_opened = True

        # 在技能面板中查找技能图标
        image_path = self.skill_images.get(skill_name, '')
        if not image_path:
            return False

        # 使用带超时的图片查找（2秒超时）
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=2)
        found = pos and len(pos) > 0

        # 如果能找到技能图标，说明技能可见（不在CD中）
        return found

    def is_item_ready(self, account_index, item_name):
        """
        检查药品是否可以使用（不在CD中）
        :param account_index: 账号索引
        :param item_name: 药品名称
        :return: True if 药品可以使用, False otherwise
        """
        cd_rounds = self.item_cd_config.get(item_name, 0)
        if cd_rounds == 0:
            return True  # 无CD药品

        if account_index not in self.item_cd_tracking:
            self.item_cd_tracking[account_index] = {}

        last_used_turn = self.item_cd_tracking[account_index].get(item_name,
                                                                  -999)
        turns_passed = self.current_turn - last_used_turn

        return turns_passed >= cd_rounds

    def mark_skill_used(self, account_index, skill_name):
        """
        标记技能已使用（更新CD追踪）
        :param account_index: 账号索引
        :param skill_name: 技能名称
        """
        if account_index not in self.skill_cd_tracking:
            self.skill_cd_tracking[account_index] = {}
        self.skill_cd_tracking[account_index][skill_name] = self.current_turn
        skill_msg = f"账号{account_index} 使用技能 {skill_name}，标记CD（回合{self.current_turn}）"
        print(skill_msg)
        self.report_battle_info(skill_msg, "success")

    def mark_item_used(self, account_index, item_name):
        """
        标记药品已使用（更新CD追踪）
        :param account_index: 账号索引
        :param item_name: 药品名称
        """
        if account_index not in self.item_cd_tracking:
            self.item_cd_tracking[account_index] = {}
        self.item_cd_tracking[account_index][item_name] = self.current_turn
        item_msg = f"账号{account_index} 使用药品 {item_name}，标记CD（回合{self.current_turn}）"
        print(item_msg)
        self.report_battle_info(item_msg, "success")

    def detect_ally_abnormal_status(self, account_index, unit_type, unit_name,
                                    unit_x, unit_y):
        """
        检测己方单位的异常状态（混乱、冰封、眩晕、嘲讽）
        :param account_index: 账号索引
        :param unit_type: 单位类型 'main_char' 或 'general'
        :param unit_name: 单位名称
        :param unit_x: 单位X坐标
        :param unit_y: 单位Y坐标
        :return: 异常状态列表，如 ['混乱', '冰封'] 或 []
        """
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return []

        # 在单位位置附近检测异常状态图标
        radius = self.status_detection_radius
        detection_region = (
            max(0, int(unit_x - radius)),
            max(0, int(unit_y - radius)),
            int(radius * 2),
            int(radius * 2)
        )

        detected_statuses = []

        try:
            x, y, w, h = detection_region
            for status_name, status_image_path in self.ally_abnormal_status_images.items():
                pos = dm_object.FindPic(x, y, w, h, status_image_path, "000000",
                                        0.9, 0)
                if pos and len(pos) > 0:
                    detected_statuses.append(status_name)
                    print(
                        f"账号{account_index} {unit_type} {unit_name} 检测到异常状态: {status_name}")
        except Exception as e:
            print(f"检测 {unit_type} {unit_name} 异常状态时出错: {e}")

        return detected_statuses

    def check_all_ally_status(self, account_index):
        """
        检测账号中所有存活单位（主角和武将）的异常状态
        :param account_index: 账号索引
        :return: 单位状态字典 {(unit_type, unit_name): [状态列表]}
        """
        if account_index not in self.unit_positions:
            return {}

        unit_statuses = {}

        # 检测主角异常状态
        main_chars = self.unit_positions[account_index].get('main_chars', [])
        for char_name, char_x, char_y in main_chars:
            statuses = self.detect_ally_abnormal_status(account_index,
                                                        'main_char', char_name,
                                                        char_x, char_y)
            if statuses:
                unit_statuses[('main_char', char_name)] = statuses

        # 检测武将异常状态
        generals = self.unit_positions[account_index].get('generals', [])
        for general_name, general_x, general_y in generals:
            statuses = self.detect_ally_abnormal_status(account_index,
                                                        'general', general_name,
                                                        general_x, general_y)
            if statuses:
                unit_statuses[('general', general_name)] = statuses

        # 更新状态追踪（初始化如果不存在）
        if account_index not in self.ally_status_tracking:
            self.ally_status_tracking[account_index] = {}
        self.ally_status_tracking[account_index] = unit_statuses

        return unit_statuses

    def has_unit_abnormal_status(self, account_index, unit_type, unit_name,
                                 status_name=None):
        """
        检查单位是否有异常状态
        :param account_index: 账号索引
        :param unit_type: 单位类型 'main_char' 或 'general'
        :param unit_name: 单位名称
        :param status_name: 特定状态名称（可选），如果不提供则检查是否有任何异常状态
        :return: True if 有异常状态, False otherwise
        """
        # 初始化状态追踪字典（如果不存在）
        if account_index not in self.ally_status_tracking:
            self.ally_status_tracking[account_index] = {}
            return False

        key = (unit_type, unit_name)
        if key not in self.ally_status_tracking[account_index]:
            return False

        statuses = self.ally_status_tracking[account_index][key]

        if status_name:
            # 检查是否有特定状态
            return status_name in statuses
        else:
            # 检查是否有任何异常状态
            return len(statuses) > 0

    def can_unit_use_skill(self, account_index, unit_type, unit_name):
        """
        判断单位是否可以使用技能
        :param account_index: 账号索引
        :param unit_type: 单位类型 'main_char' 或 'general'
        :param unit_name: 单位名称
        :return: True if 可以使用技能, False otherwise
        """
        # 如果有冰封状态，不能使用技能
        if self.has_unit_abnormal_status(account_index, unit_type, unit_name,
                                         '冰封'):
            return False

        # 其他异常状态（混乱、眩晕、嘲讽）不影响技能使用
        return True

    def can_unit_use_item(self, account_index, unit_type, unit_name):
        """
        判断单位是否可以使用药品
        :param account_index: 账号索引
        :param unit_type: 单位类型 'main_char' 或 'general'
        :param unit_name: 单位名称
        :return: True if 可以使用药品, False otherwise
        """
        # 冰封状态下可以使用药品
        # 其他异常状态也可以使用药品
        return True

    def can_unit_summon(self, account_index, unit_type, unit_name):
        """
        判断单位是否可以召唤武将
        :param account_index: 账号索引
        :param unit_type: 单位类型 'main_char' 或 'general'
        :param unit_name: 单位名称
        :return: True if 可以召唤, False otherwise
        """
        # 冰封状态下可以召唤武将
        # 其他异常状态也可以召唤
        return True

    def query_turn_status(self, account_index):
        """
        每回合开始时的查询机制：查询技能CD、场上武将等信息
        :param account_index: 账号索引
        :return: 查询结果字典
        """
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return {}

        query_result = {
            'skill_cd_status': {},  # 技能CD状态 {skill_name: bool} True表示可用（不在CD）
            'generals_on_field': [],  # 场上武将列表
            'has_liubei': False,  # 是否存在刘备
            'general_count': 0,  # 场上武将数量
        }

        # 1. 查询场上是否存在刘备等武将
        team_status = self.get_team_status(account_index)
        if team_status:
            query_result['generals_on_field'] = [g['name'] for g in
                                                 team_status['generals']]
            query_result['has_liubei'] = any(
                g['name'] == '刘备' for g in team_status['generals'])
            query_result['general_count'] = team_status['general_count']

        # 2. 查询技能CD状态（通过检测技能面板中技能是否可见）
        # 注意：查询完成后需要关闭技能面板，避免影响后续操作
        panel_region, _ = self.get_panel_region('skill')
        if not panel_region:
            # 如果没有设置面板区域，跳过技能CD查询
            print(f"警告：账号{account_index} 未设置技能面板区域，跳过技能CD查询")
        else:
            # 转换坐标格式（使用统一方法）
            coords = self.convert_region_coords(panel_region)
            if not coords:
                print(
                    f"警告：技能面板区域格式错误: {panel_region}，跳过技能CD查询")
            else:
                x, y, width, height = coords
                test_skill = self.skill_images.get('主角群体攻击1', '')
                panel_opened = False
                need_close_panel = False  # 标记是否需要关闭面板

                if test_skill:
                    test_pos = self.find_pic_with_timeout(dm_object, x, y,
                                                          width, height,
                                                          test_skill, timeout=2)
                    panel_opened = test_pos and len(test_pos) > 0

                # 如果面板未打开，打开它
                if not panel_opened:
                    if self.click_right_button('技能按钮', dm_object):
                        # 等待面板出现（最多等待3秒）
                        if test_skill:
                            found, test_pos = self.wait_for_image(dm_object, x,
                                                                  y, width,
                                                                  height,
                                                                  test_skill,
                                                                  timeout=3,
                                                                  check_interval=0.1)
                            if found and test_pos:
                                panel_opened = True
                                need_close_panel = True  # 标记需要关闭
                            else:
                                print(f"警告：技能面板可能未完全打开（已等待3秒）")
                        else:
                            # 如果没有test_skill，假设面板已打开（理论上不应该发生）
                            print(
                                f"警告：账号{account_index} test_skill为空，假设面板已打开")
                            panel_opened = True
                            need_close_panel = True  # 标记需要关闭

                # 如果面板已打开或刚刚打开，进行查询
                if panel_opened:
                    try:
                        # 查询主角技能CD（使用带超时的查找，快速查询）
                        main_char_skills = ['主角群体攻击1', '主角群体攻击2',
                                            '主角群体攻击3', '主角群体攻击4',
                                            '主角群体攻击5']
                        for skill_name in main_char_skills:
                            image_path = self.skill_images.get(skill_name, '')
                            if image_path:
                                # 使用带超时的查找，快速查询（1秒超时）
                                pos = self.find_pic_with_timeout(dm_object, x,
                                                                 y, width,
                                                                 height,
                                                                 image_path,
                                                                 timeout=1)
                                # 如果能找到技能图标，说明不在CD中，可用
                                query_result['skill_cd_status'][
                                    skill_name] = pos and len(pos) > 0

                        # 查询刘备技能CD（使用带超时的查找）
                        if query_result['has_liubei']:
                            liubei_skills = ['加血', '加攻击', '控制',
                                             '清除状态']
                            for skill_name in liubei_skills:
                                image_path = self.skill_images.get(skill_name,
                                                                   '')
                                if image_path:
                                    pos = self.find_pic_with_timeout(dm_object,
                                                                     x, y,
                                                                     width,
                                                                     height,
                                                                     image_path,
                                                                     timeout=1)
                                    query_result['skill_cd_status'][
                                        skill_name] = pos and len(pos) > 0

                        # 查询输出武将技能CD（使用带超时的查找）
                        output_generals = ['武将群体攻击1', '武将群体攻击2']
                        for skill_name in output_generals:
                            image_path = self.skill_images.get(skill_name, '')
                            if image_path:
                                # 使用带超时的查找，快速查询（1秒超时）
                                pos = self.find_pic_with_timeout(dm_object, x,
                                                                 y, width,
                                                                 height,
                                                                 image_path,
                                                                 timeout=1)
                                query_result['skill_cd_status'][
                                    skill_name] = pos and len(pos) > 0
                    finally:
                        # 如果是我们打开的面板，关闭它（通过按ESC键或点击空白处）
                        if need_close_panel:
                            try:
                                dm_object.KeyPressChar('esc')
                                time.sleep(0.1)
                            except:
                                pass  # 如果关闭失败，继续执行

        return query_result

    def print_turn_query_result(self, account_index, query_result):
        """
        打印回合查询结果
        :param account_index: 账号索引
        :param query_result: 查询结果字典
        """
        if not query_result:
            return

        print(f"\n【账号{account_index} 回合查询结果】")

        # 打印武将信息
        generals = query_result.get('generals_on_field', [])
        general_count = query_result.get('general_count', 0)
        has_liubei = query_result.get('has_liubei', False)

        if generals:
            print(f"  场上武将: {', '.join(generals)} ({general_count}个)")
        else:
            print(f"  场上武将: 无 ({general_count}个)")

        print(f"  是否存在刘备: {'是' if has_liubei else '否'}")

        # 打印技能CD状态
        skill_cd = query_result.get('skill_cd_status', {})
        if skill_cd:
            available_skills = [name for name, available in skill_cd.items() if
                                available]
            cd_skills = [name for name, available in skill_cd.items() if
                         not available]

            if available_skills:
                print(
                    f"  可用技能 ({len(available_skills)}个): {', '.join(available_skills)}")
            if cd_skills:
                print(
                    f"  CD中技能 ({len(cd_skills)}个): {', '.join(cd_skills)}")
        else:
            print(f"  技能CD状态: 未查询到")

        print("")

    def has_enemy_status(self, account_index):
        """
        检测敌军是否有需要清除的状态（四种状态之一）
        同时追踪状态3和状态4的变化，用于判断是否需要清除状态
        :param account_index: 账号索引
        :return: 状态检测结果字典，包含各种状态信息
        """
        dm_object = self.account_dm[account_index]
        if not dm_object or not self.enemy_region:
            return {'has_status': False, 'status3': False, 'status4': False}

        # 初始化状态追踪
        if account_index not in self.enemy_status_tracking:
            self.enemy_status_tracking[account_index] = {
                'status3_present': False,
                'status3_last_seen_turn': -1,
                'status4_present': False
            }

        # 在敌军区域检测四种状态
        if not self.enemy_region:
            return {'has_status': False, 'status3': False, 'status4': False,
                    'need_clear': False}

        if not isinstance(self.enemy_region, (tuple, list)) or len(
                self.enemy_region) != 4:
            return {'has_status': False, 'status3': False, 'status4': False,
                    'need_clear': False}

        x, y, w, h = self.enemy_region

        status3_found = False
        status4_found = False
        has_any_status = False

        for status_name, status_image_path in self.enemy_status_images.items():
            # 转换坐标格式
            width = w - x if w > 900 or h > 580 else w
            height = h - y if w > 900 or h > 580 else h
            # 使用带超时的图片查找（2秒超时）
            pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                             status_image_path, timeout=2)
            if pos and len(pos) > 0:
                has_any_status = True
                if status_name == '状态3':
                    status3_found = True
                elif status_name == '状态4':
                    status4_found = True

        # 更新状态追踪
        tracking = self.enemy_status_tracking[account_index]
        prev_status3 = tracking['status3_present']
        prev_status4 = tracking['status4_present']

        # 更新状态3
        if status3_found:
            if not prev_status3:
                # 状态3刚出现
                tracking['status3_present'] = True
                tracking['status3_last_seen_turn'] = self.current_turn
            else:
                # 状态3持续存在，更新最后见到的时间
                tracking['status3_last_seen_turn'] = self.current_turn
        else:
            if prev_status3:
                # 状态3消失
                tracking['status3_present'] = False

        # 更新状态4
        tracking['status4_present'] = status4_found

        # 判断是否需要清除状态
        need_clear = False
        if status3_found and status4_found:
            # 状态3出现且状态4存在：不清除
            need_clear = False
        elif not status3_found and status4_found and prev_status3:
            # 状态3消失后，状态4仍然存在：需要清除
            need_clear = True
        elif has_any_status and not (status3_found and status4_found):
            # 其他状态（不是状态3+状态4同时存在的情况）：需要清除
            need_clear = True

        return {
            'has_status': has_any_status,
            'status3': status3_found,
            'status4': status4_found,
            'need_clear': need_clear
        }

    def click_right_button(self, button_name, dm_object):
        """
        点击右侧操作按钮（技能/召唤/道具）
        :param button_name: 按钮名称
        :param dm_object: 大漠对象
        :return: True if 点击成功
        """
        image_path = self.button_images.get(button_name, '')
        if not image_path or not self.right_button_region:
            return False

        x, y, w, h = self.right_button_region
        # 转换坐标格式
        width = w - x if w > 900 or h > 580 else w
        height = h - y if w > 900 or h > 580 else h
        # 使用带超时的图片查找（3秒超时）
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=3)
        if pos and len(pos) > 0:
            try:
                pos_list = pos.split(',')
                if len(pos_list) >= 2:
                    # 修复：验证是否为有效数字
                    btn_x = int(pos_list[0])
                    btn_y = int(pos_list[1])
                    dm_object.MoveTo(btn_x, btn_y)
                    time.sleep(0.2)  # 增加移动后等待时间
                    dm_object.LeftClick()
                    time.sleep(0.3)  # 增加等待时间，确保点击生效
                    return True
            except (ValueError, IndexError) as e:
                print(f"解析按钮 {button_name} 位置失败: {pos}, 错误: {e}")
                return False
        return False

    def click_skill_icon(self, skill_name, dm_object, panel_region):
        """
        在技能面板中点击技能图标
        :param skill_name: 技能名称
        :param dm_object: 大漠对象
        :param panel_region: 技能面板区域
        :return: True if 点击成功
        """
        image_path = self.skill_images.get(skill_name, '')
        if not image_path:
            return False

        # 转换坐标格式（使用统一方法）
        coords = self.convert_region_coords(panel_region)
        if not coords:
            print(f"警告：技能面板区域格式错误: {panel_region}")
            return False

        x, y, width, height = coords
        # 使用带超时的图片查找（2秒超时）
        pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                         image_path, timeout=2)
        if pos and len(pos) > 0:
            try:
                pos_list = pos.split(',')
                if len(pos_list) >= 2:
                    # 修复：验证是否为有效数字
                    skill_x = int(pos_list[0])
                    skill_y = int(pos_list[1])
                    dm_object.MoveTo(skill_x, skill_y)
                    time.sleep(0.2)  # 增加移动后等待时间
                    dm_object.LeftClick()
                    time.sleep(0.3)  # 增加等待时间，确保进入选择目标状态
                    return True
            except (ValueError, IndexError) as e:
                print(f"解析技能 {skill_name} 位置失败: {pos}, 错误: {e}")
                return False
        return False

    def use_skill_workflow(self, skill_name, dm_object, target_type='enemy',
                           account_index=0, target_x=None, target_y=None,
                           enemy_index=0):
        """
        使用技能的完整流程：检测技能可见性 -> 点击按钮 -> 选择技能 -> 选择目标
        如果能找到技能图标，说明技能没有进入CD，可以使用（不受混乱/冰封/眩晕影响）
        :param skill_name: 技能名称
        :param dm_object: 大漠对象
        :param target_type: 目标类型 'enemy' or 'ally'
        :param account_index: 账号索引，用于获取目标的确切位置
        :param target_x: 目标X坐标（确切点位，可选）
        :param target_y: 目标Y坐标（确切点位，可选）
        :param enemy_index: 敌人索引（当target_type='enemy'时使用）
        :return: True if 成功
        """
        # 0. 检测技能是否可见（在技能面板中能找到，说明不在CD中且未被控制）
        # is_skill_visible 会打开技能面板并检测，如果技能可见则面板仍然打开
        skill_visible = self.is_skill_visible(account_index, skill_name,
                                              dm_object)

        if not skill_visible:
            print(
                f"账号{account_index} 技能 {skill_name} 不可见（可能CD中或被控制）")
            return False

        # 注意：is_skill_visible 已经检测了技能面板，如果可见则面板应该已打开
        # 1. 确保技能面板已打开，然后在技能面板中选择技能
        panel_region, _ = self.get_panel_region('skill')
        if not panel_region:
            print(f"警告：账号{account_index} 未设置技能面板区域，无法使用技能")
            return False

        # 检查面板是否打开
        coords = self.convert_region_coords(panel_region)
        if not coords:
            print(f"警告：技能面板区域格式错误: {panel_region}")
            return False

        x, y, width, height = coords
        test_skill = self.skill_images.get('主角群体攻击1', '')
        panel_opened = False

        if test_skill:
            test_pos = self.find_pic_with_timeout(dm_object, x, y, width,
                                                  height, test_skill, timeout=2)
            panel_opened = test_pos and len(test_pos) > 0

        # 如果面板未打开，打开它
        if not panel_opened:
            if not self.click_right_button('技能按钮', dm_object):
                return False

            # 等待面板出现（最多等待3秒）
            if test_skill:
                found, test_pos = self.wait_for_image(dm_object, x, y, width,
                                                      height, test_skill,
                                                      timeout=3,
                                                      check_interval=0.1)
                if found and test_pos:
                    panel_opened = True
                else:
                    print(f"警告：技能面板可能未完全打开（已等待3秒）")
                    return False
            else:
                # 如果没有test_skill，假设面板已打开（理论上不应该发生）
                print(f"警告：账号{account_index} test_skill为空，假设面板已打开")
                panel_opened = True

        # 在技能面板中选择技能
        if not self.click_skill_icon(skill_name, dm_object, panel_region):
            return False

        # 2. 选择目标（使用确切点位）
        click_success = False
        if target_type == 'enemy':
            # 确保 enemy_region 已设置
            if not self.enemy_region:
                print(
                    f"警告：账号{account_index} 未设置敌军区域，无法选择敌人目标")
                return False

            # 尝试点击敌人，如果敌人死亡则自动尝试下一个（最多尝试3个敌人）
            for attempt_index in range(3):
                current_index = (enemy_index + attempt_index) % 3
                if self.click_enemy_unit(dm_object, self.enemy_region,
                                         account_index, current_index):
                    click_success = True
                    break
                else:
                    # 当前敌人死亡，尝试下一个
                    if attempt_index < 2:  # 还有下一个可以尝试
                        print(
                            f"账号{account_index} 敌人{current_index + 1}已死亡，尝试下一个敌人")

            if not click_success:
                print(f"账号{account_index} 所有敌人都已死亡，无法选择目标")
        elif target_type == 'ally':
            # 如果提供了确切坐标，使用提供的坐标
            if target_x is not None and target_y is not None:
                click_success = self.click_ally_unit(dm_object, target_x,
                                                     target_y, account_index)
            else:
                # 从unit_positions获取友军位置
                if account_index in self.unit_positions:
                    main_chars = self.unit_positions[account_index].get(
                        'main_chars', [])
                    if main_chars:
                        # 使用第一个主角的位置
                        _, x, y = main_chars[0]
                        click_success = self.click_ally_unit(dm_object, x, y,
                                                             account_index)

        # 3. 只有成功完成所有步骤才标记技能已使用
        if click_success:
            self.mark_skill_used(account_index, skill_name)
            return True
        else:
            print(
                f"账号{account_index} 技能 {skill_name} 使用失败（目标选择失败）")
            return False

    def get_random_ally_position(self, account_index):
        """
        随机获取一个己方队友的确切坐标（包括主角和武将）
        :param account_index: 账号索引
        :return: (x, y) 坐标元组，如果没有队友则返回 None
        """
        if account_index not in self.unit_positions:
            return None

        all_allies = []
        # 获取所有主角位置
        all_allies.extend(
            self.unit_positions[account_index].get('main_chars', []))
        # 获取所有武将位置
        all_allies.extend(
            self.unit_positions[account_index].get('generals', []))

        if not all_allies:
            return None

        # 随机选择一个队友
        random_ally = random.choice(all_allies)
        # 返回 (name, x, y) 中的坐标
        _, x, y = random_ally
        return (x, y)

    def click_ally_unit(self, dm_object, target_x, target_y,
                        account_index=None):
        """
        点击友军单位（使用确切点位）
        :param dm_object: 大漠对象
        :param target_x: 目标X坐标（确切点位）
        :param target_y: 目标Y坐标（确切点位）
        :param account_index: 账号索引（可选，用于从unit_positions获取位置）
        :return: True if 点击成功
        """
        dm_object.MoveTo(int(target_x), int(target_y))
        time.sleep(0.2)  # 增加移动后等待时间
        dm_object.LeftClick()
        time.sleep(0.2)  # 增加点击后等待时间
        print(f"点击友军位置: ({target_x}, {target_y})")
        return True

    def click_enemy_unit(self, dm_object, enemy_region, account_index=0,
                         enemy_index=0):
        """
        点击一个敌军单位（优先使用固定的确切位置）
        :param dm_object: 大漠对象
        :param enemy_region: 敌军区域（备用，如果找不到确切位置则使用）
        :param account_index: 账号索引，用于获取敌人位置列表
        :param enemy_index: 敌人索引（0=第一个敌人，1=第二个敌人，2=第三个敌人）
        :return: True if 点击成功
        """
        # 1. 优先使用固定的配置位置（主要使用固定点位）
        enemy_key = (account_index, enemy_index)
        if enemy_key in self.fixed_enemy_positions:
            enemy_x, enemy_y = self.fixed_enemy_positions[enemy_key]

            # 点击前检查敌人是否存活（检测墓碑）
            if self.check_tombstone_at_position(dm_object, enemy_x, enemy_y):
                # 检测到墓碑，说明敌人已死亡
                print(
                    f"敌人{enemy_index + 1}位置 ({enemy_x}, {enemy_y}) 检测到墓碑，已死亡，跳过")
                return False

            # 敌人存活，点击敌人中心位置
            dm_object.MoveTo(int(enemy_x), int(enemy_y))
            time.sleep(0.2)  # 增加移动后等待时间
            dm_object.LeftClick()
            time.sleep(0.2)  # 增加点击后等待时间
            print(
                f"使用固定坐标点击敌人{enemy_index + 1}位置: ({enemy_x}, {enemy_y})")
            return True

        # 2. 使用检测到的敌人位置（通过图片识别，备用方案）
        if account_index in self.unit_positions:
            enemies = self.unit_positions[account_index].get('enemies', [])
            if enemies and enemy_index < len(enemies):
                enemy_name, enemy_x, enemy_y = enemies[enemy_index]

                # 点击前检查敌人是否存活（检测墓碑）
                if self.check_tombstone_at_position(dm_object, enemy_x,
                                                    enemy_y):
                    # 检测到墓碑，说明敌人已死亡
                    print(
                        f"敌人 {enemy_name} 位置 ({enemy_x}, {enemy_y}) 检测到墓碑，已死亡，跳过")
                    return False

                # 敌人存活，点击敌人位置
                dm_object.MoveTo(int(enemy_x), int(enemy_y))
                time.sleep(0.2)  # 增加移动后等待时间
                dm_object.LeftClick()
                time.sleep(0.2)  # 增加点击后等待时间
                print(f"点击敌人 {enemy_name} 位置: ({enemy_x}, {enemy_y})")
                return True

        # 3. 如果没有找到确切位置，使用区域中心位置（最后备用方案）
        # 注意：在使用区域中心前，应该先检测是否有存活的敌人
        try:
            if not isinstance(enemy_region, (tuple, list)) or len(
                    enemy_region) != 4:
                print(f"敌军区域格式错误: {enemy_region}")
                return False
            x, y, w, h = enemy_region
            # 根据初始化注释，enemy_region格式是(x, y, w, h)其中w和h是结束坐标
            # 但在FindPic中，w和h应该是宽度和高度
            # 这里统一处理：如果w和h超过屏幕尺寸（说明是结束坐标），需要转换为宽度和高度
            # 否则直接使用（已经是宽度和高度）
            if w > 900 or h > 580:  # 判断：w和h可能是结束坐标
                center_x = (x + w) // 2  # 结束坐标情况：中心点 = (开始 + 结束) / 2
                center_y = (y + h) // 2
            else:  # w和h是宽度和高度
                center_x = x + w // 2  # 宽度情况：中心点 = 开始 + 宽度/2
                center_y = y + h // 2

            # 检测区域中心是否有墓碑（如果中心点有墓碑，说明可能所有敌人都死了）
            if self.check_tombstone_at_position(dm_object, center_x, center_y):
                print(
                    f"使用备用方案，但区域中心 ({center_x}, {center_y}) 检测到墓碑，可能所有敌人已死亡")
                return False

            dm_object.MoveTo(center_x, center_y)
            time.sleep(0.2)  # 增加移动后等待时间
            dm_object.LeftClick()
            time.sleep(0.2)  # 增加点击后等待时间
            print(f"使用备用方案，点击敌军区域中心: ({center_x}, {center_y})")
            return True
        except (ValueError, TypeError) as e:
            print(f"使用备用方案点击敌军位置时出错: {e}")
            return False

    def use_item_workflow(self, item_name, dm_object, target_x, target_y,
                          account_index):
        """
        使用药品的完整流程：检查CD -> 点击按钮 -> 选择药品 -> 选择目标
        :param item_name: 药品名称
        :param dm_object: 大漠对象
        :param target_x: 目标X坐标（确切点位）
        :param target_y: 目标Y坐标（确切点位）
        :param account_index: 账号索引
        :return: True if 成功
        """
        # 0. 检查药品CD
        if not self.is_item_ready(account_index, item_name):
            print(f"账号{account_index} 药品 {item_name} 还在CD中")
            return False

        # 1. 获取药品图片路径
        item_image = self.item_images.get(item_name, '')
        if not item_image:
            print(f"未找到药品 {item_name} 图片")
            return False

        # 2. 点击道具按钮
        if not self.click_right_button('道具按钮', dm_object):
            return False

        # 等待道具面板出现（通过查找道具图标验证）
        # 获取面板区域（复用变量，避免重复获取）
        panel_region, _ = self.get_panel_region('item')
        if panel_region:
            coords = self.convert_region_coords(panel_region)
            if coords:
                x, y, width, height = coords
                # 等待道具图标出现（最多等待3秒）
                found, _ = self.wait_for_image(dm_object, x, y, width, height,
                                               item_image, timeout=3,
                                               check_interval=0.1)
                if not found:
                    print(f"警告：道具面板可能未完全打开（已等待3秒），继续尝试...")
            else:
                print(f"警告：道具面板区域格式错误: {panel_region}")

        # 3. 选择药品（在道具面板中查找药品图片）
        # 复用上面的panel_region，避免重复获取
        if not panel_region:
            print(f"警告：未设置道具面板区域")
            return False

        coords = self.convert_region_coords(panel_region)
        if not coords:
            print(f"警告：道具面板区域格式错误: {panel_region}")
            return False

        x, y, width, height = coords
        # 等待道具图标出现（最多等待3秒）
        found, pos = self.wait_for_image(dm_object, x, y, width, height,
                                         item_image, timeout=3,
                                         check_interval=0.1)
        if found and pos:
            try:
                pos_list = pos.split(',')
                if len(pos_list) >= 2:
                    # 修复：验证是否为有效数字
                    item_x = int(pos_list[0])
                    item_y = int(pos_list[1])
                    dm_object.MoveTo(item_x, item_y)
                    time.sleep(0.2)  # 增加移动后等待时间
                    dm_object.LeftClick()
                    time.sleep(0.3)  # 增加等待时间，确保进入选择目标状态

                    # 3. 点击目标位置（确切点位）
                    dm_object.MoveTo(int(target_x), int(target_y))
                    time.sleep(0.2)  # 增加移动后等待时间
                    dm_object.LeftClick()
                    time.sleep(0.2)  # 增加点击后等待时间
                    print(
                        f"使用药品 {item_name} 对位置 ({target_x}, {target_y}) 施放")

                    # 4. 标记药品已使用
                    self.mark_item_used(account_index, item_name)
                    return True
            except (ValueError, IndexError) as e:
                print(f"解析药品 {item_name} 位置失败: {pos}, 错误: {e}")
                return False
        return False

    def _update_hp_bar_unit_mapping(self, account_index):
        """
        更新血量条区域到单位的映射关系
        :param account_index: 账号索引
        """
        if account_index not in self.hp_bar_unit_mapping:
            self.hp_bar_unit_mapping[account_index] = {}

        if account_index not in self.unit_positions:
            return

        # 获取存活的主角列表
        main_chars = self.unit_positions[account_index].get('main_chars', [])
        # 获取存活的武将列表
        generals = self.unit_positions[account_index].get('generals', [])

        # 清除旧的映射
        self.hp_bar_unit_mapping[account_index] = {}

        # 映射主角（region_index 0-2）
        for idx, (char_name, x, y) in enumerate(main_chars[:3]):
            region_index = idx  # 0, 1, 2
            self.hp_bar_unit_mapping[account_index][region_index] = (
                'main_char', char_name, (x, y))

        # 映射武将（region_index 3-8）
        for idx, (general_name, x, y) in enumerate(generals[:6]):
            region_index = idx + 3  # 3, 4, 5, 6, 7, 8
            self.hp_bar_unit_mapping[account_index][region_index] = ('general',
                                                                     general_name,
                                                                     (x, y))

    def detect_low_hp_units(self, account_index):
        """
        检测账号中血量低的单位
        :param account_index: 账号索引
        :return: 列表，每个元素为 (unit_type, unit_name, heal_position)，按优先级排序
        """
        if not self.hp_bar_regions or len(self.hp_bar_regions) != 9:
            return []

        if account_index not in self.account_dm:
            return []

        dm_object = self.account_dm[account_index]
        if not dm_object:
            return []

        low_hp_units = []

        # 遍历9个血量条区域
        for region_index, hp_bar_region in enumerate(self.hp_bar_regions):
            try:
                if not isinstance(hp_bar_region, (tuple, list)) or len(
                        hp_bar_region) != 4:
                    continue

                x, y, w, h = hp_bar_region
                # 在血量条区域中查找血量低标识图片
                # 转换坐标格式
                width = w - x if w > 900 or h > 580 else w
                height = h - y if w > 900 or h > 580 else h
                # 使用带超时的图片查找（1秒超时）
                pos = self.find_pic_with_timeout(dm_object, x, y, width, height,
                                                 self.low_hp_indicator_image,
                                                 timeout=1)

                if pos and len(pos) > 0:
                    # 识别到血量低的标识，查找对应的单位
                    if account_index in self.hp_bar_unit_mapping:
                        mapping = self.hp_bar_unit_mapping[account_index]
                        if region_index in mapping:
                            unit_type, unit_name, heal_position = mapping[
                                region_index]
                            low_hp_units.append(
                                (unit_type, unit_name, heal_position))
                            print(
                                f"账号{account_index} 检测到 {unit_type} {unit_name} 血量低，加血位置: {heal_position}")
            except Exception as e:
                print(
                    f"账号{account_index} 检测血量条区域 {region_index} 时出错: {e}")
                continue

        return low_hp_units

    def main_char_action(self, account_index):
        """
        主角操作：优先检测血量低的单位并加血，否则尝试释放群体攻击，如果全部CD则给血量低的单位或武将加血
        注意：如果主角有冰封状态，不能使用技能，但可以使用药品和召唤
        :param account_index: 账号索引
        """
        # 添加边界检查
        if not self.account_dm or account_index < 0 or account_index >= len(
                self.account_dm):
            return

        dm_object = self.account_dm[account_index]
        if not dm_object:
            return

        # 检查主角是否有异常状态
        team_status = self.get_team_status(account_index)
        can_use_skill = True  # 默认可以使用技能
        # 安全检查：确保main_chars列表存在且有元素
        main_chars_list = team_status.get('main_chars',
                                          []) if team_status else []
        if main_chars_list and len(main_chars_list) > 0:
            # 检查第一个主角的状态（假设所有主角状态相同，或只控制第一个主角）
            main_char_name = main_chars_list[0]
            can_use_skill = self.can_unit_use_skill(account_index, 'main_char',
                                                    main_char_name)

        # 优先检测血量低的单位并加血（冰封状态下也可以使用药品）
        if self.enable_main_heal:
            low_hp_units = self.detect_low_hp_units(account_index)
            if low_hp_units:
                # 优先给主角加血，然后是武将
                low_hp_units.sort(
                    key=lambda x: (0 if x[0] == 'main_char' else 1, x[1]))

                for unit_type, unit_name, heal_position in low_hp_units:
                    heal_x, heal_y = heal_position
                    print(
                        f"账号{account_index} 检测到 {unit_type} {unit_name} 血量低，使用恢复药加血")
                    if self.use_item_workflow('恢复药', dm_object, heal_x,
                                              heal_y, account_index):
                        # 成功给一个单位加血后，等待一下再检查下一个
                        time.sleep(0.3)
                        return  # 每回合只给一个单位加血，避免占用过多时间

        # 尝试使用群体攻击（包括新增的第5个技能）
        # 注意：如果主角有冰封状态，不能使用技能
        skill_used = False
        if can_use_skill:
            group_attack_skills = ['主角群体攻击1', '主角群体攻击2',
                                   '主角群体攻击3', '主角群体攻击4',
                                   '主角群体攻击5']
            for skill_name in group_attack_skills:
                # 尝试使用技能，如果技能可见（不在CD且未被控制）则使用
                if self.use_skill_workflow(skill_name, dm_object,
                                           target_type='enemy',
                                           account_index=account_index):
                    skill_used = True
                    break
        else:
            frozen_msg = f"账号{account_index} 主角有冰封状态，无法使用技能"
            print(frozen_msg)
            self.report_battle_info(frozen_msg, "warning")

        # 如果所有技能都在CD，则检测血量并给血量低的单位加血
        if not skill_used and self.enable_main_heal:
            try:
                # 再次检测血量低的单位
                low_hp_units = self.detect_low_hp_units(account_index)
                if low_hp_units and len(low_hp_units) > 0:
                    # 给第一个血量低的单位加血
                    unit_type, unit_name, heal_position = low_hp_units[0]
                    # 安全检查：确保heal_position格式正确
                    if isinstance(heal_position, (tuple, list)) and len(
                            heal_position) >= 2:
                        heal_x, heal_y = heal_position[0], heal_position[1]
                        heal_msg = f"账号{account_index} 所有技能CD，给血量低的 {unit_type} {unit_name} 使用恢复药"
                        print(heal_msg)
                        self.report_battle_info(heal_msg, "success")
                        self.use_item_workflow('恢复药', dm_object, heal_x,
                                               heal_y, account_index)
                    else:
                        warn_msg = f"警告：治疗位置格式错误: {heal_position}，跳过加血操作"
                        print(warn_msg)
                        self.report_battle_info(warn_msg, "warning")
                elif account_index in self.unit_positions:
                    # 如果没有检测到血量低的单位，给随机武将使用恢复药（保持向后兼容）
                    generals = self.unit_positions[account_index].get(
                        'generals', [])
                    if generals:
                        random_general = random.choice(generals)
                        _, x, y = random_general
                        print(
                            f"账号{account_index} 所有技能CD，给随机武将使用恢复药")
                        self.use_item_workflow('恢复药', dm_object, x, y,
                                               account_index)
            except Exception as e:
                print(f"账号{account_index} 给单位使用恢复药时出错: {e}")

    def general_action(self, general_type, account_index, general_name=None):
        """
        武将操作
        :param general_type: 'support' 辅助武将 or 'dps' 输出武将
        :param account_index: 账号索引
        :param general_name: 武将名称（用于检测异常状态）
        """
        dm_object = self.account_dm[account_index]
        if not dm_object:
            return

        # 检查武将是否有异常状态
        can_use_skill = True
        if general_name:
            can_use_skill = self.can_unit_use_skill(account_index, 'general',
                                                    general_name)
            has_frozen = self.has_unit_abnormal_status(account_index, 'general',
                                                       general_name, '冰封')
            if has_frozen:
                print(
                    f"账号{account_index} 武将 {general_name} 有冰封状态，无法使用技能")

        if general_type == 'dps':
            # 输出武将：使用群体攻击（尝试两个技能，都是无CD）
            # 注意：如果武将有冰封状态，不能使用技能
            group_attack_skills = ['武将群体攻击1', '武将群体攻击2']
            skill_used = False

            if can_use_skill:
                for skill_name in group_attack_skills:
                    # 尝试使用技能（由于都是无CD，会尝试使用第一个可用的）
                    if self.use_skill_workflow(skill_name, dm_object,
                                               target_type='enemy',
                                               account_index=account_index):
                        skill_used = True
                        break  # 成功使用一个技能后退出
            else:
                print(
                    f"账号{account_index} 输出武将 {general_name} 有冰封状态，无法使用技能")

            # 如果所有技能都不可用（理论上不应该发生，因为都是无CD），打印信息
            if not skill_used and can_use_skill:
                print(f"账号{account_index} 输出武将的所有群体攻击技能都不可用")
        elif general_type == 'support':
            # 辅助武将（刘备）：按策略释放技能
            # 注意：如果武将有冰封状态，不能使用技能
            if not can_use_skill:
                print(f"账号{account_index} 刘备有冰封状态，无法使用技能")
                return

            status_info = self.has_enemy_status(account_index)

            if status_info['need_clear']:
                # 需要清除状态（状态3消失后状态4存在，或其他状态）
                # 检测清除状态技能是否可见
                if self.is_skill_visible(account_index, '清除状态', dm_object):
                    if self.use_skill_workflow('清除状态', dm_object,
                                               target_type='enemy',
                                               account_index=account_index):
                        # 成功使用清除状态技能
                        return
            # 如果清除状态技能不可用，尝试使用其他技能
            # 继续执行下面的逻辑，尝试使用其他可用技能

            # 尝试使用辅助技能，如果当前技能不可见则尝试其他技能
            skill_used = False
            if not self.support_skill_sequence or len(
                    self.support_skill_sequence) == 0:
                print(f"警告：账号{account_index} 辅助技能序列为空")
                return
            start_index = self.current_skill_index % len(
                self.support_skill_sequence)

            # 从当前索引开始，尝试所有技能直到找到可用的
            for i in range(len(self.support_skill_sequence)):
                skill_index = (start_index + i) % len(
                    self.support_skill_sequence)
                skill_name = self.support_skill_sequence[skill_index]

                # 判断技能目标类型（移除加速技能）
                target_type = 'ally' if skill_name in ['加攻击',
                                                       '加血'] else 'enemy'

                # 如果是己方目标，随机选择一个队友坐标
                target_x, target_y = None, None
                if target_type == 'ally':
                    ally_pos = self.get_random_ally_position(account_index)
                    if ally_pos:
                        target_x, target_y = ally_pos
                    else:
                        # 没有可用队友，跳过这个技能
                        continue

                # 尝试使用技能（会自动检测技能是否可见）
                if self.use_skill_workflow(skill_name, dm_object,
                                           target_type=target_type,
                                           account_index=account_index,
                                           target_x=target_x,
                                           target_y=target_y):
                    # 成功使用技能，切换到下一个技能
                    self.current_skill_index = (skill_index + 1) % len(
                        self.support_skill_sequence)
                    skill_used = True
                    break

            # 如果所有技能都不可用，打印信息
            if not skill_used:
                print(
                    f"账号{account_index} 刘备的所有技能都不可用（可能在CD中或被控制）")
        else:
            # 未知类型的武将，打印警告
            print(f"警告：账号{account_index} 武将类型未知: {general_type}")

    def use_heal_item(self, dm_object, account_index, target_x=None,
                      target_y=None):
        """
        使用加血道具（恢复药）
        :param dm_object: 大漠对象
        :param account_index: 账号索引
        :param target_x: 目标X坐标（可选，如果不提供则随机选择武将）
        :param target_y: 目标Y坐标（可选）
        """
        # 如果没有提供目标坐标，随机选择一个武将
        if target_x is None or target_y is None:
            if account_index in self.unit_positions:
                generals = self.unit_positions[account_index].get('generals',
                                                                  [])
                if generals:
                    random_general = random.choice(generals)
                    _, target_x, target_y = random_general
                else:
                    return False
            else:
                return False

        # 使用恢复药（恢复药是加血又加蓝的）
        return self.use_item_workflow('恢复药', dm_object, target_x, target_y,
                                      account_index)

    def check_and_revive_dead_main_chars(self, account_index):
        """
        检查并复活阵亡的主角
        :param account_index: 账号索引
        :return: True if 有复活操作
        """
        # 更新追踪信息
        self.update_general_tracking(account_index)

        has_revive_action = False  # 记录是否有任何复活操作

        # 检查每个账号是否有主角阵亡
        account_count = self.get_account_count()
        for i in range(account_count):
            # 安全检查：确保account_dm已初始化且索引有效
            if not self.validate_account_index(i):
                continue

            try:
                team_status = self.get_team_status(i)
                if not team_status:
                    continue

                # 获取阵亡的主角位置（从之前的记录中查找）
                current_main_chars = set(team_status.get('main_chars', []))
                # 安全地获取追踪的主角列表
                unit_pos = self.unit_positions.get(i, {})
                main_chars_list = unit_pos.get('main_chars', [])
                tracked_main_chars = {char_name for char_name, _, _ in
                                      main_chars_list if
                                      len(main_chars_list) > 0 and isinstance(
                                          main_chars_list[0],
                                          (tuple, list)) and len(
                                          main_chars_list[0]) >= 3}
                dead_main_chars = tracked_main_chars - current_main_chars

                if not dead_main_chars:
                    continue

                # 找到阵亡的主角位置（从dead_main_char_positions中获取）
                for dead_char_name in dead_main_chars:
                    # 从dead_main_char_positions中获取阵亡主角的位置
                    dead_char_pos = None
                    if i in self.dead_main_char_positions:
                        dead_char_pos = self.dead_main_char_positions[i].get(
                            dead_char_name)

                    if not dead_char_pos:
                        # 如果dead_main_char_positions中没有，尝试从unit_positions的旧数据中查找
                        # 这种情况应该很少发生，因为update_general_tracking会先保存位置
                        print(
                            f"警告：无法找到账号{i}的主角{dead_char_name}的位置，跳过复活")
                        continue

                    # 优先让队友账号的主角复活（如果队友账号的主角存活）
                    revive_success = False
                    account_count = self.get_account_count()
                    for ally_index in range(account_count):
                        if ally_index == i or not self.validate_account_index(
                                ally_index):
                            continue

                        try:
                            ally_status = self.get_team_status(ally_index)
                            if ally_status and len(
                                    ally_status['main_chars']) > 0:
                                # 队友账号有存活的主角，用主角复活
                                print(
                                    f"账号{ally_index}的主角复活账号{i}的主角{dead_char_name}")
                                # 使用复活药（通过use_item_workflow）
                                if self.use_item_workflow('复活药',
                                                          self.account_dm[
                                                              ally_index],
                                                          dead_char_pos[0],
                                                          dead_char_pos[1],
                                                          ally_index):
                                    revive_success = True
                                    has_revive_action = True
                                    break
                        except Exception as e:
                            print(
                                f"账号{ally_index}复活账号{i}的主角{dead_char_name}时出错: {e}")
                            continue

                    # 如果队友主角都死了，用武将复活
                    if not revive_success:
                        try:
                            # 检查当前账号是否有存活的武将
                            team_status = self.get_team_status(i)
                            if team_status and team_status['general_count'] > 0:
                                # 用武将复活
                                print(f"账号{i}的武将复活主角{dead_char_name}")
                                # 需要找到武将按钮的位置，然后点击药品按钮
                                # 这里需要武将也能点击药品按钮的逻辑
                                # 使用复活药（通过use_item_workflow）
                                if self.use_item_workflow('复活药',
                                                          self.account_dm[i],
                                                          dead_char_pos[0],
                                                          dead_char_pos[1], i):
                                    revive_success = True
                                    has_revive_action = True
                        except Exception as e:
                            print(
                                f"账号{i}的武将复活主角{dead_char_name}时出错: {e}")

                    if revive_success:
                        time.sleep(1.0)  # 增加等待时间，确保复活动画完成
                        # 更新追踪信息
                        self.update_general_tracking(i)
            except Exception as e:
                print(f"检查账号{i}的主角复活状态时出错: {e}")
                continue

        return has_revive_action

    def summon_general(self, exempt_account_index, target_account_index=None):
        """
        召唤武将
        :param exempt_account_index: 执行召唤的账号（当前回合的账号）
        :param target_account_index: 目标账号（为哪个账号召唤，None表示为自己召唤）
        """
        if target_account_index is None:
            target_account_index = exempt_account_index

        dm_object = self.account_dm[exempt_account_index]
        if not dm_object:
            return

        # 获取目标账号的队伍状态
        team_status = self.get_team_status(target_account_index)
        if not team_status:
            return

        # 检查是否可以召唤（武将数量少于2个，或者已经有2个但可以替换）
        # 注意：即使有2个武将，也可以替换，所以不在这里返回

        # 优先策略：检查是否需要辅助武将
        if self.keep_support_general and not team_status['has_support']:
            # 需要辅助武将，检查背包
            if self.check_bag_for_support_general(target_account_index):
                # 背包中有辅助武将，召唤刘备
                self._execute_summon(dm_object, '刘备', target_account_index)
                return

        # 如果没有辅助武将需求或背包中没有辅助武将，召唤输出武将
        output_generals = ['魔化关羽', '曹操']
        for general_name in output_generals:
            if self.check_bag_for_general(target_account_index, general_name):
                self._execute_summon(dm_object, general_name,
                                     target_account_index)
                return

    def _execute_summon(self, dm_object, general_name, account_index):
        """
        执行召唤操作
        :param dm_object: 大漠对象
        :param general_name: 要召唤的武将名称
        :param account_index: 目标账号索引
        """
        # 1. 点击召唤按钮
        if not self.click_right_button('召唤按钮', dm_object):
            print(f"无法点击召唤按钮，召唤失败")
            return False

        # 等待召唤面板出现（通过查找面板中的武将图片验证）
        # 获取面板区域（复用变量，避免重复获取）
        panel_region, _ = self.get_panel_region('summon')
        if panel_region:
            coords = self.convert_region_coords(panel_region)
            if coords:
                x, y, width, height = coords
                # 尝试查找任意一个武将图片来验证面板是否打开（最多等待3秒）
                test_general_image = self.safe_get_dict_value(
                    self.bag_general_images, '刘备', '')
                if test_general_image:
                    found, _ = self.wait_for_image(dm_object, x, y, width,
                                                   height, test_general_image,
                                                   timeout=3,
                                                   check_interval=0.1)
                    if not found:
                        print(
                            f"警告：召唤面板可能未完全打开（已等待3秒），继续尝试...")

        # 2. 在召唤面板左侧查找要召唤的武将图片（背包中的武将）
        general_bag_image = self.safe_get_dict_value(self.bag_general_images,
                                                     general_name, '')
        if not general_bag_image:
            print(f"未找到武将 {general_name} 的背包图片")
            return False

        # 在召唤面板区域查找武将图片（复用上面的panel_region）
        if not panel_region:
            print("未设置召唤面板区域")
            return False

        coords = self.convert_region_coords(panel_region)
        if not coords:
            print(f"警告：召唤面板区域格式错误: {panel_region}")
            return False

        x, y, width, height = coords
        # 等待武将图片出现（最多等待3秒）
        found, pos = self.wait_for_image(dm_object, x, y, width, height,
                                         general_bag_image, timeout=3,
                                         check_interval=0.1)
        if not found or not pos:
            print(f"在召唤面板中未找到武将 {general_name}（已等待3秒）")
            return False

        try:
            pos_list = pos.split(',')
            if len(pos_list) < 2:
                return False

            # 修复：验证是否为有效数字
            general_x = int(pos_list[0])
            general_y = int(pos_list[1])

            # 点击武将图片
            dm_object.MoveTo(general_x, general_y)
            time.sleep(0.2)  # 增加移动后等待时间
            dm_object.LeftClick()
            time.sleep(0.5)  # 增加点击后等待时间，确保响应完成
        except (ValueError, IndexError) as e:
            print(f"解析召唤武将 {general_name} 位置失败: {pos}, 错误: {e}")
            return False

        # 3. 检查是否需要替换武将（如果已有2个武将）
        team_status = self.get_team_status(account_index)
        if team_status and team_status['general_count'] >= 2:
            # 需要替换，找到出战时间最长的武将并点击其位置
            if account_index in self.general_tracking:
                # 找到出战回合最早的武将（出战时间最长）
                oldest_general = None
                oldest_turn = self.current_turn + 1

                for gen_name, gen_info in self.general_tracking[
                    account_index].items():
                    if gen_info.get('deployed_turn',
                                    self.current_turn) < oldest_turn:
                        oldest_turn = gen_info.get('deployed_turn',
                                                   self.current_turn)
                        oldest_general = (gen_name, gen_info.get('position'))

                if oldest_general and oldest_general[1]:
                    # 点击被替换武将的位置
                    try:
                        gen_name = oldest_general[0]
                        gen_position = oldest_general[1]
                        # 检查位置是否为元组格式 (x, y)
                        if isinstance(gen_position, (tuple, list)) and len(
                                gen_position) >= 2:
                            gen_x, gen_y = gen_position[0], gen_position[1]
                            replace_msg = f"账号{account_index} 需要替换武将 {gen_name}，点击位置 ({gen_x}, {gen_y})"
                            print(replace_msg)
                            self.report_battle_info(replace_msg, "action")
                            dm_object.MoveTo(int(gen_x), int(gen_y))
                            time.sleep(0.2)  # 增加移动后等待时间
                            dm_object.LeftClick()
                            time.sleep(0.5)  # 增加点击后等待时间，确保替换响应完成
                        else:
                            print(
                                f"武将 {gen_name} 的位置格式不正确: {gen_position}")
                    except (ValueError, TypeError, IndexError) as e:
                        print(f"解析武将位置失败: {e}")
        else:
            # 直接召唤，不需要替换
            summon_msg = f"账号{account_index} 直接召唤武将 {general_name}（武将数量少于2个）"
            print(summon_msg)
            self.report_battle_info(summon_msg, "action")

        # 召唤完成
        summon_success_msg = f"成功召唤武将 {general_name} 到账号 {account_index}"
        print(summon_success_msg)
        self.report_battle_info(summon_success_msg, "success")

        # 修复：召唤成功后立即更新武将追踪信息
        time.sleep(0.3)  # 等待召唤动画完成
        self.update_general_tracking(account_index)

        return True

    def check_and_summon_for_allies(self, current_account_index):
        """
        检查队友账号是否需要召唤武将，优先召唤辅助武将
        :param current_account_index: 当前执行回合的账号索引
        """
        # 检查所有账号
        account_count = self.get_account_count()
        for i in range(account_count):
            # 安全检查：确保account_dm已初始化且索引有效
            if i == current_account_index or not self.validate_account_index(i):
                continue

            # 获取该账号的队伍状态
            team_status = self.get_team_status(i)
            if not team_status:
                continue

            # 每个账号的武将数量少于2个时，尝试为其召唤
            # 3个 contributor 加起来最多6个武将（每个最多2个）
            if team_status['general_count'] < 2:
                # 优先召唤辅助武将
                if self.keep_support_general and not team_status['has_support']:
                    if self.check_bag_for_support_general(i):
                        self.summon_general(current_account_index,
                                            target_account_index=i)
                        return

                # 如果没有辅助武将，召唤输出武将
                output_generals = ['魔化关羽', '曹操']
                for general_name in output_generals:
                    if self.check_bag_for_general(i, general_name):
                        self.summon_general(current_account_index,
                                            target_account_index=i)
                        return

    def check_has_any_alive_units(self):
        """
        检查是否还有任何存活的主角或武将
        :return: True if 至少有一个主角或武将存活, False otherwise
        """
        account_count = self.get_account_count()
        for i in range(account_count):
            # 安全检查：确保account_dm已初始化且索引有效
            if not self.validate_account_index(i):
                continue

            team_status = self.get_team_status(i)
            if team_status:
                # 如果有存活的主角或武将，返回True
                if (team_status.get('main_chars') and len(
                        team_status['main_chars']) > 0) or team_status.get(
                    'general_count', 0) > 0:
                    return True

        return False

    def auto_combat(self, account_index):
        """
        自动战斗主循环
        :param account_index: 账号索引
        """
        # 添加边界检查
        if not self.account_dm or account_index < 0 or account_index >= len(
                self.account_dm):
            return

        dm_object = self.account_dm[account_index]
        if not dm_object:
            return

        # 检查线程是否已停止
        if self.thread:
            if hasattr(self.thread, 'overed') and self.thread.overed:
                return
            if hasattr(self.thread, 'stoped') and self.thread.stoped:
                return

        # 检查是否是己方回合
        is_current_turn = self.is_my_turn(dm_object)

        # 修复：如果从非己方回合转为己方回合，重置处理标志（每个账号独立判断）
        if account_index not in self._last_turn_state:
            self._last_turn_state[account_index] = False

        last_state = self._last_turn_state.get(account_index, False)

        # 如果从非己方回合转为己方回合（任意一个账号），重置处理标志
        # 这样可以确保至少有一个账号进入回合时执行查询和全局检测
        if is_current_turn and not last_state:
            # 刚切换到己方回合，重置处理标志（全局）
            self.turn_processed = False

        self._last_turn_state[account_index] = is_current_turn

        if not is_current_turn:
            return

        # 0. 更新回合数（修复BUG：防止重复更新，线程安全）
        # 如果当前回合还未处理，则更新回合数并标记为已处理
        # 注意：只有第一个进入回合的账号会执行这里的代码（因为turn_processed是全局的）
        with self._state_lock:
            if not self.turn_processed:
                self.current_turn += 1
                self.turn_processed = True
                turn_updated = True
            else:
                turn_updated = False
        
        if turn_updated:
            # 重置回合计时器和错误计数
            self.reset_turn_timer()
            account_count = self.get_account_count()
            for i in range(account_count):
                # 安全检查：确保索引有效
                if self.validate_account_index(i):
                    self.reset_error_count(i)
            turn_msg = f"{'=' * 50}\n回合 {self.current_turn} 开始（{self.turn_timeout}秒操作时间）\n{'=' * 50}"
            print(f"\n{turn_msg}\n")
            self.report_battle_info(turn_msg, "turn")

            # 0.1. 每回合开始时的查询机制：查询技能CD、场上武将等信息
            account_count = self.get_account_count()
            for i in range(account_count):
                # 安全检查：确保account_dm已初始化且索引有效
                if self.validate_account_index(i):
                    try:
                        query_result = self.query_turn_status(i)
                        if query_result:
                            self.print_turn_query_result(i, query_result)
                    except Exception as e:
                        # 查询错误不影响主要流程，但记录错误
                        self.increment_error_count(i)
                        print(
                            f"账号{i} 回合查询时出错: {e} (错误计数: {self.account_error_count.get(i, 0)})")

            # 0. 全局检测所有账号的队伍状态（包括主角和武将）
            # 注意：这部分代码应该只在第一个账号进入回合时执行一次（在turn_processed设置之前）
            account_count = self.get_account_count()
            for i in range(account_count):
                # 安全检查：确保account_dm已初始化且索引有效
                if self.validate_account_index(i):
                    try:
                        team_status = self.get_team_status(i)
                        if team_status:
                            # 更新追踪信息（检测阵亡的武将和主角）
                            self.update_general_tracking(i)
                            # 检测敌人位置
                            self.detect_enemy_positions(i)
                            # 更新血量条区域到单位的映射
                            self._update_hp_bar_unit_mapping(i)
                            # 检测所有存活单位的异常状态（只检测冰封）
                            unit_statuses = self.check_all_ally_status(i)
                            if unit_statuses:
                                print(
                                    f"账号{i} 检测到异常状态: {unit_statuses}")
                            main_char_count = len(
                                team_status.get('main_chars', []))
                            general_count = team_status.get('general_count', 0)
                            has_support = team_status.get('has_support', False)
                            enemy_count = len(
                                self.unit_positions.get(i, {'enemies': []})[
                                    'enemies'])
                            status_msg = f"账号{i} 状态: 主角{main_char_count}个存活, 武将{general_count}个存活, 有辅助{has_support}, 敌人{enemy_count}个"
                            print(status_msg)
                            self.report_battle_info(status_msg, "info")
                    except Exception as e:
                        # 检测错误记录但不中断流程
                        self.increment_error_count(i)
                        print(
                            f"账号{i} 检测队伍状态时出错: {e} (错误计数: {self.account_error_count.get(i, 0)})")
                        continue

            # 0.1. 检查是否还有存活的单位（主角或武将），如果没有则停止战斗
            # 注意：这个检查应该在全局检测之后，并且只在第一个账号进入回合时执行一次
            if not self.check_has_any_alive_units():
                end_msg = "所有账号的主角 and 武将全部阵亡，停止自动战斗"
                print(end_msg)
                self.report_battle_info(end_msg, "error")
                # 停止战斗自动操作
                if self.thread and hasattr(self.thread, '_stop_combat_auto'):
                    self.thread._stop_combat_auto()
                return

        # 开始执行操作前，先检查是否应该跳过
        if self.should_skip_turn(account_index):
            print(f"账号{account_index} 跳过当前回合操作")
            return

        # 1. 主角操作（只有在主角存活的情况下）
        try:
            # 再次检查（防止在检测阶段超时）
            if self.should_skip_turn(account_index):
                print(f"账号{account_index} 操作超时，跳过主角操作")
                return
            else:
                team_status = self.get_team_status(account_index)
                if team_status and team_status.get('main_chars') and len(
                        team_status['main_chars']) > 0:
                    self.main_char_action(account_index)
                else:
                    print(f"账号{account_index}的主角全部阵亡，跳过主角操作")
        except Exception as e:
            error_count = self.increment_error_count(account_index)
            print(
                f"账号{account_index} 主角操作出错: {e} (错误计数: {error_count})")
            if error_count >= self.max_errors_per_turn:
                print(f"账号{account_index} 错误过多，跳过剩余操作")
                return

        # 2. 检查是否需要召唤武将
        try:
            # 检查超时
            if self.should_skip_turn(account_index):
                print(f"账号{account_index} 操作超时，跳过召唤武将")
                return
            elif self.enable_main_summon:
                # 优先检查是否需要为队友召唤武将
                self.check_and_summon_for_allies(account_index)

                # 为自己召唤武将
                self.summon_general(account_index)
        except Exception as e:
            error_count = self.increment_error_count(account_index)
            print(
                f"账号{account_index} 召唤武将出错: {e} (错误计数: {error_count})")
            if error_count >= self.max_errors_per_turn:
                print(f"账号{account_index} 错误过多，跳过剩余操作")
                return

        # 3. 武将操作
        try:
            # 检查超时
            if self.should_skip_turn(account_index):
                print(f"账号{account_index} 操作超时，跳过武将操作")
                return
            else:
                # 获取所有在场的武将
                generals = self.get_all_generals(account_index)

                # 遍历每个武将，执行相应操作
                for general in generals:
                    # 每个武将操作前都检查超时和错误
                    if self.should_skip_turn(account_index):
                        print(f"账号{account_index} 操作超时，跳过剩余武将操作")
                        break

                    general_name = general['name']
                    general_type = general['type']

                    try:
                        # 根据武将类型执行相应操作（传递武将名称用于状态检测）
                        self.general_action(general_type, account_index,
                                            general_name=general_name)

                        # 短暂延时，避免操作过快
                        time.sleep(0.3)
                    except Exception as e:
                        error_count = self.increment_error_count(account_index)
                        print(
                            f"账号{account_index} 武将 {general_name} 操作出错: {e} (错误计数: {error_count})")
                        if error_count >= self.max_errors_per_turn:
                            print(f"账号{account_index} 错误过多，跳过剩余操作")
                            break
        except Exception as e:
            error_count = self.increment_error_count(account_index)
            print(
                f"账号{account_index} 武将操作出错: {e} (错误计数: {error_count})")

    def cleanup(self):
        """
        清理资源（停止定时器等）
        """
        # 取消所有定时器
        for timer in self._timer_refs:
            try:
                timer.cancel()
            except Exception:
                pass
        self._timer_refs.clear()
        
        # 安全关闭窗口
        if self.battle_report_dialog:
            try:
                self.battle_report_dialog.close_safely()
            except Exception:
                pass

    def run_combat_loop(self):
        """
        战斗循环（在多开场景下，对每个账号执行）
        """
        max_attempts = 100  # 最大执行次数
        attempt = 0

        try:
            while attempt < max_attempts:
                # 检查是否应该停止（修复：兼容多种状态管理方式）
                if self.thread:
                    # 优先检查 overed（停止标志）
                    if hasattr(self.thread, 'overed') and self.thread.overed:
                        break
                    # 检查 stoped（暂停标志），暂停时跳过当前循环但继续等待
                    if hasattr(self.thread, 'stoped') and self.thread.stoped:
                        time.sleep(0.5)
                        continue

                # 修复：不再在循环开始时重置标志，而是基于回合变化来重置（在auto_combat中处理）

                # 对每个有效的账号执行战斗操作
                account_count = self.get_account_count()
                for i in range(account_count):
                    # 安全检查：确保account_dm已初始化且索引有效
                    if self.validate_account_index(i):
                        self.auto_combat(i)

                # 如果当前回合已被处理，等待下一次循环
                # 这样确保每次循环只处理一次回合数更新
                time.sleep(0.5)  # 短暂延时
                attempt += 1
        finally:
            # 清理资源
            self.cleanup()


# 示例使用
if __name__ == "__main__":
    # 这个脚本需要在 MyThread 的上下文中运行
    # 使用方式：
    # 1. 在 MyFrame 中添加新的脚本选项 "战斗中自动"
    # 2. 在 MyThread.run() 方法中添加对应的脚本执行分支
    # 3. 调用 CombatAutoScript 的功能

    print("战斗自动操作脚本已加载")
    print("请将此功能集成到 serveScript.py 的 MyThread 类中")
