"""
梦幻三国战斗自动操作脚本（重写版）
功能：基于全局状态管理的战斗系统
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
    DEFAULT_CHECK_INTERVAL = 0.1
    ACTION_DELAY = 0.3
    SKILL_CLICK_VERIFY_DELAY = 0.8
    PANEL_WAIT_TIMEOUT = 3
    MAIN_CHAR_SKILL_WAIT_TIMEOUT = 2.0  # 主角技能等待超时
    GENERAL_SKILL_WAIT_TIMEOUT = 3.0  # 武将技能等待超时
    ACTION_BUTTON_WAIT_TIMEOUT = 3.0  # 攻击按钮等待超时
    SUMMON_BUTTON_WAIT_TIMEOUT = 2.0  # 召唤按钮等待超时
    SUMMON_BUTTON_INITIAL_DELAY = 0.3  # 召唤按钮初始等待时间


# 定义 ResXy 类
class ResXy:
    """坐标结果类"""
    def __init__(self, x, y):
        self.x = x
        self.y = y


# 战斗播报窗口（保留原有UI）
class BattleReportDialog(wx.Frame):
    """战斗实时播报窗口"""
    def __init__(self, parent=None):
        super().__init__(
            parent, title="战斗实时播报", size=(800, 600), pos=(450, 50), 
            style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        )
        self.SetBackgroundColour(wx.Colour(245, 245, 250))
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.log_text = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        self.log_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox.Add(self.log_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        clear_btn = wx.Button(panel, label="清空日志")
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        vbox.Add(clear_btn, flag=wx.ALL, border=5)
        panel.SetSizer(vbox)
        self.log_lock = threading.Lock()
        self.Show()
        self.add_log("=" * 60, wx.Colour(100, 100, 100))
        self.add_log("战斗播报系统已启动", wx.Colour(0, 150, 0))
        self.add_log(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", wx.Colour(0, 150, 0))
        self.add_log("=" * 60, wx.Colour(100, 100, 100))
        self.add_log("")
        self.add_log("战斗播报系统已初始化", wx.Colour(0, 150, 0))

    def add_log(self, message, color=None):
        if color is None:
            color = wx.Colour(0, 0, 0)
        def _add_log():
            try:
                if not self or not hasattr(self, "log_text") or not self.log_text:
                    return
                with self.log_lock:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] {message}\n"
                    self.log_text.SetDefaultStyle(wx.TextAttr(color))
                    self.log_text.AppendText(full_message)
                    try:
                        self.log_text.ShowPosition(self.log_text.GetLastPosition())
                        self.log_text.Refresh()
                    except:
                        pass
            except Exception as e:
                print(f"添加日志时出错: {e}")
        try:
            if threading.current_thread() == threading.main_thread():
                _add_log()
            else:
                if hasattr(wx, "CallAfter"):
                    wx.CallAfter(_add_log)
                else:
                    _add_log()
        except Exception as e:
            print(f"CallAfter调用时出错: {e}")

    def on_clear(self, event):
        self.log_text.Clear()

    def close_safely(self):
        if self:
            wx.CallAfter(self.Close)


# ==================== 全局状态Map结构 ====================
class UnitStatus:
    """单位状态类"""
    def __init__(self):
        self.alive = True  # 存活状态
        self.position = None  # 固定点位 (x, y)
        self.need_heal = False  # 是否需要加血
        self.revive_assigned = None  # 复活对象（默认为空，如果有死亡，按优先顺序安排单位去复活）
        self.general_type = None  # 武将类型（仅武将）："attack" 或 "support"
        self.reviving = False  # 是否正在复活中


class AccountStatus:
    """账号状态类"""
    def __init__(self):
        self.main_char = UnitStatus()  # 主角
        self.general1 = UnitStatus()  # 武将1
        self.general2 = UnitStatus()  # 武将2
    
    def get_active_generals(self):
        """获取实际存在的武将列表（根据general_type是否为None判断）"""
        generals = []
        if self.general1.general_type is not None:
            generals.append(("general1", self.general1))
        if self.general2.general_type is not None:
            generals.append(("general2", self.general2))
        return generals
    
    def get_general_count(self):
        """获取实际拥有的武将数量"""
        count = 0
        if self.general1.general_type is not None:
            count += 1
        if self.general2.general_type is not None:
            count += 1
        return count


class GlobalStateMap:
    """全局状态Map"""
    def __init__(self):
        # 三个大漠对象，每个包含主角、武将1、武将2
        self.dm0 = AccountStatus()  # 第一个大漠对象
        self.dm1 = AccountStatus()  # 第二个大漠对象
        self.dm2 = AccountStatus()  # 第三个大漠对象
        self.dead_main_char_count = 0  # 死亡主角数量
        self.enemy_target_position = None  # 敌军攻击目标点位
        self.ally_support_target_position = None  # 我军辅助技能施法点位
        self.low_hp_units = []  # 血量低的单位列表
        self.enemies_need_clear = []  # 需要清除状态的敌军列表
        self.dead_main_char_account_indices = set()  # 需要被复活的主角账号索引集合（可能有多个）
        self.all_dead_account_indices = set()  # 全部阵亡的账号索引集合
        # 待复活点位记录：key为施法坐标元组(cast_x, cast_y)，value为正在复活的账号索引和施法坐标
        # 格式：{(cast_x, cast_y): {"target_account_idx": int, "reviver_dm_index": int, "target_pos": (x, y)}}
        self.pending_revive_positions = {}
    
    def get_account(self, dm_index):
        """获取指定大漠对象的账号状态"""
        if dm_index == 0:
            return self.dm0
        elif dm_index == 1:
            return self.dm1
        elif dm_index == 2:
            return self.dm2
        return self.dm0
    
    def get_all_accounts(self):
        """获取所有账号状态"""
        return [self.dm0, self.dm1, self.dm2]


# ==================== 战斗自动操作脚本 ====================
class CombatAutoScript:
    """战斗自动操作脚本（重写版）"""
    
    def __init__(self, thread_instance, enemy_keys_to_detect=None):
        """
        初始化战斗自动操作脚本
        :param thread_instance: MyThread 实例
        :param enemy_keys_to_detect: 需要检测状态的敌军单位 key 列表，例如 ["诸葛亮", "赵云29"]
        """
        self.thread = thread_instance
        self.battle_report_dialog = None
        self._state_lock = threading.Lock()
        self.polling_running = False
        self.polling_thread = None
        
        # 全局状态Map
        self.state_map = GlobalStateMap()
        self.is_first_turn = True  # 是否第一回合
        self.enemy_target_detected_this_turn = False  # 当前非我方回合是否已识别敌军攻击点位
        self.ally_support_target_detected_this_turn = False  # 当前非我方回合是否已识别我军辅助技能施法点位
        
        # 需要检测的敌军单位 key 列表
        self.enemy_keys_to_detect = enemy_keys_to_detect if enemy_keys_to_detect else []
        
        # 初始化资源路径和区域
        self._init_resources()
        
        # 创建战斗播报窗口
        try:
            timer = threading.Timer(0.3, self._create_battle_report_dialog)
            timer.start()
        except:
            pass
    
    def _create_battle_report_dialog(self):
        try:
            if wx.GetApp():
                self.battle_report_dialog = BattleReportDialog()
        except:
            pass
    
    def report_battle_info(self, message, msg_type="info"):
        """报告战斗信息"""
        if self.battle_report_dialog:
            color_map = {
                "info": wx.Colour(0, 0, 0),
                "success": wx.Colour(0, 150, 0),
                "warning": wx.Colour(255, 165, 0),
                "error": wx.Colour(255, 0, 0),
                "action": wx.Colour(0, 0, 255),
                "system": wx.Colour(100, 100, 100),
            }
            self.battle_report_dialog.add_log(message, color_map.get(msg_type, wx.Colour(0, 0, 0)))
        print(f"[战斗] {message}")
    
    def get_resource_path(self, relative_path):
        """获取资源文件路径"""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def _init_resources(self):
        """初始化资源路径和区域"""
        # 区域定义
        self.enemy_region = (54, 168, 370, 541)
        self.ally_region = (450, 162, 900, 580)
        self.right_button_region = (610, 203, 680, 436)
        self.skill_panel_region = (480, 167, 607, 550)
        self.summon_panel_region = (480, 167, 607, 550)
        self.item_panel_region = (0, 0, 900, 550)
        
        # 账号区域定义（用于区分不同账号的主角位置，避免重复复活）
        # 账号1在上排，账号0在中间排，账号2在下排
        # 格式：(x, y, w, h) - 左上角坐标和宽高
        self.account_main_char_regions = {
            1: (708, 170, 830, 340),  # 账号1主角区域（上排）
            0: (749, 281, 836, 409),  # 账号0主角区域（中间排）
            2: (775, 395, 862, 542),  # 账号2主角区域（下排）
        }
        
        # 按钮图片
        self.button_images = {
            "技能按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),
            "召唤按钮": self.get_resource_path("serveAssets/images/auto/zhaohuan.bmp"),
            "道具按钮": self.get_resource_path("serveAssets/images/auto/yaopin.bmp"),
            "操作按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),
            "取消按钮": self.get_resource_path("serveAssets/images/quxiaozdzd.bmp"),  # 取消按钮
            "防御按钮": self.get_resource_path("serveAssets/images/auto/fangyu.bmp"),  # 防御按钮
        }
        
        # zdzd图片路径（需要检测并点击取消的弹窗）
        self.zdzd_image = self.get_resource_path("serveAssets/images/zdzd111.bmp")
        
        # zdzd检测区域（全屏检测）
        self.zdzd_region = (0, 0, 900, 580)  # 全屏区域
        
        # 技能图片
        self.skill_images = {
            # 主角技能
            "寂灭神劫": f"{self.get_resource_path('serveAssets/images/auto/cehsi.bmp')}|{self.get_resource_path('serveAssets/images/auto/jimie2.bmp')}",
            "锁魂": f"{self.get_resource_path('serveAssets/images/auto/zhanshiqun.bmp')}|{self.get_resource_path('serveAssets/images/auto/suohun2.bmp')}",
            "天灾": f"{self.get_resource_path('serveAssets/images/auto/tianzai1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tianzai2.bmp')}",
            # 辅助武将技能（刘备）
            "加血": f"{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan1.bmp')}|{self.get_resource_path('serveAssets/images/auto/tuanjiezhiquan2.bmp')}",
            "加攻击": self.get_resource_path("serveAssets/images/auto/liubeizengshang1.bmp"),
            "控制": self.get_resource_path("serveAssets/images/auto/liubeikong1.bmp"),
            "清除状态": self.get_resource_path("serveAssets/images/auto/liubeijie1.bmp"),
            # 攻击武将技能
            "剑阵灭杀": f"{self.get_resource_path('serveAssets/images/auto/caocaoqun3.bmp')}|{self.get_resource_path('serveAssets/images/auto/caocaoqun2.bmp')}",
            "武神一怒": f"{self.get_resource_path('serveAssets/images/auto/moguqun1.bmp')}|{self.get_resource_path('serveAssets/images/auto/moguqun2.bmp')}",
        }

        # 物品图片
        self.item_images = {
            "恢复药": f"{self.get_resource_path('serveAssets/images/auto/yao.bmp')}|{self.get_resource_path('serveAssets/images/auto/yao1.bmp')}",
            "复活药": f"{self.get_resource_path('serveAssets/images/auto/fuhuo.bmp')}|{self.get_resource_path('serveAssets/images/auto/fuhuo1.bmp')}",
        }
        
        # 背包武将图片
        self.bag_general_images = {
            "刘备": f"{self.get_resource_path('serveAssets/images/auto/liubei1.bmp')}|{self.get_resource_path('serveAssets/images/auto/liubei2.bmp')}",
            "魔化关羽": f"{self.get_resource_path('serveAssets/images/auto/mogu2.bmp')}|{self.get_resource_path('serveAssets/images/auto/mogu1.bmp')}",
            "曹操": self.get_resource_path("serveAssets/images/auto/caocao1.bmp"),
        }

        # 目标选择图片
        self.target_lantiao_image = self.get_resource_path("serveAssets/images/auto/lantiao.bmp")
        self.target_fuhuohuo_image = self.get_resource_path("serveAssets/images/auto/fuhuohuo.bmp")
        
        # 默认敌军目标位置（当未检测到敌军攻击目标时使用）
        # 根据游戏截图，左侧敌人中心点大约在：(97, 246), (104, 344), (115, 446)
        # 这里使用中间位置的敌人作为默认目标
        self.default_enemy_target_position = (104, 344)
        
        # 敌军武将配置（所有可检测的敌军单位配置）
        self.enemy_general_config = {
            "刘备": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/tiandihudun1.bmp")
                },
                "status_region": (165, 258, 246, 291),
                "cast_position": (203, 346),
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

        # 技能分类
        self.main_char_skills = ["寂灭神劫", "锁魂", "天灾"]
        self.attack_general_skills = ["剑阵灭杀", "武神一怒"]  # 曹操、魔关
        self.support_general_skills = ["加血", "加攻击", "控制", "清除状态"]  # 刘备
        
        # 刘备技能顺序
        self.liubei_skill_sequence = ["加攻击", "加血", "控制"]
        self.liubei_skill_index = {}  # {dm_index: current_index}
    
    def get_account_dm(self, dm_index):
        """获取指定大漠对象"""
        if dm_index == 0:
            return self.thread.dm
        elif dm_index == 1:
            return getattr(self.thread, 'win1_dm', None)
        elif dm_index == 2:
            return getattr(self.thread, 'win2_dm', None)
        return self.thread.dm

    def find_image(self, dm_index, image_path, region, find_dir=0, use_lower_confidence=False):
        """查找图片"""
        dm = self.get_account_dm(dm_index)
        if not dm:
            return None
        try:
            x, y, w, h = region
            if w <= x or h <= y:
                return None
            confidence_levels = [0.9, 0.8, 0.7, 0.6, 0.5] if use_lower_confidence else [0.9, 0.8, 0.7]
            for confidence in confidence_levels:
                pos = dm.FindPicEx(int(x), int(y), int(w), int(h), image_path, "", confidence, find_dir)
                if pos:
                    pos = pos.split("|")
                    pos_res = pos[0].split(",")
                    pics = image_path.split("|")
                    picSize = dm.GetPicSize(pics[int(pos_res[0])])
                    picSize = picSize.split(",")
                    picW, picH = picSize[0], picSize[1]
                    posX = int(pos_res[1]) + (int(picW) * 0.5)
                    posY = int(pos_res[2]) + (int(picH) * 0.5)
                    return ResXy(int(posX), int(posY))
            return None
        except:
            return None

    def find_text(self, dm_index, text, region, find_dir=0, confidence=None):
        """查找文字"""
        dm = self.get_account_dm(dm_index)
        if not dm:
            return None
        try:
            x, y, w, h = region
            if w <= x or h <= y:
                return None
            conf = confidence if confidence else 0.8
            pos = dm.FindStrEx(int(x), int(y), int(w), int(h), text, "", conf)
            if pos:
                pos_res = pos.split("|")[0].split(",")
                return ResXy(int(pos_res[1]), int(pos_res[2]))
            return None
        except:
            return None
        
    def find_target_text(self, dm_index, search_region, timeout=3.0):
        """在指定区域查找复活目标图片（fuhuohuo）
        :param dm_index: 大漠对象索引
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
                    
                    target_pos = self.find_image(dm_index, self.target_fuhuohuo_image, search_reg, 0)
                    if target_pos:
                        break
                    time.sleep(0.05)  # 短暂延迟后重试
                if target_pos:
                    break
            if target_pos:
                break
            time.sleep(0.1)  # 每次循环后稍作延迟
        
        return target_pos

    def click_position(self, dm_index, x, y):
        """点击位置"""
        dm = self.get_account_dm(dm_index)
        if dm:
            dm.MoveTo(int(x), int(y))
            time.sleep(0.05)
            dm.LeftClick()
            time.sleep(CombatConstants.ACTION_DELAY)

    def wait_for_action_button(self, dm_index, timeout=3.0):
        """等待攻击按钮出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_image(dm_index, self.button_images["操作按钮"], self.right_button_region, 0):
                return True
            time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)
            return False
        
    def check_summon_button(self, dm_index):
        """检查召唤按钮（判断是主角还是武将）"""
        return self.find_image(dm_index, self.button_images["召唤按钮"], self.right_button_region, 0) is not None
    
    def find_skill_in_panel(self, dm_index, skill_names, timeout=2.0):
        """在技能面板中查找技能（支持多图片）"""
        start_time = time.time()
        dm = self.get_account_dm(dm_index)
        if not dm:
            return None, None
        
        # 准备所有技能路径（展开每个技能的多图片路径）
        all_skill_paths = []  # 所有图片路径的列表
        skill_name_map = {}  # 图片路径索引到技能名称的映射
        skill_path_index = 0
        
        for skill_name in skill_names:
            skill_path = self.skill_images.get(skill_name)
            if skill_path:
                # 如果技能路径包含多个图片（用|分隔），需要展开
                individual_paths = skill_path.split("|")
                for path in individual_paths:
                    all_skill_paths.append(path)
                    skill_name_map[skill_path_index] = skill_name
                    skill_path_index += 1
        
        if not all_skill_paths:
            return None, None
        
        combined_path = "|".join(all_skill_paths)
        x, y, w, h = self.skill_panel_region
        
        while time.time() - start_time < timeout:
            for confidence in [0.9, 0.8, 0.7]:
                pos = dm.FindPicEx(int(x), int(y), int(w), int(h), combined_path, "", confidence, 0)
                if pos:
                    # FindPicEx 返回格式: "图片索引,x,y|图片索引,x,y"
                    pos_results = pos.split("|")
                    if pos_results:
                        pos_res = pos_results[0].split(",")
                        if len(pos_res) >= 3:
                            pic_index = int(pos_res[0])
                            if pic_index in skill_name_map:
                                found_skill = skill_name_map[pic_index]
                                # 获取图片尺寸
                                pics = combined_path.split("|")
                                if pic_index < len(pics):
                                    picSize = dm.GetPicSize(pics[pic_index])
                                    picSize = picSize.split(",")
                                    if len(picSize) >= 2:
                                        picW, picH = int(picSize[0]), int(picSize[1])
                                        posX = int(pos_res[1]) + (picW * 0.5)
                                        posY = int(pos_res[2]) + (picH * 0.5)
                                        return found_skill, ResXy(int(posX), int(posY))
            time.sleep(0.1)
        return None, None
    
    def click_skill(self, dm_index, skill_name, skill_pos):
        """点击技能"""
        skill_path = self.skill_images.get(skill_name)
        if not skill_path:
            return False
        self.click_position(dm_index, skill_pos.x, skill_pos.y)
        time.sleep(CombatConstants.SKILL_CLICK_VERIFY_DELAY)
        # 验证技能是否消失
        verify_pos = self.find_image(dm_index, skill_path, self.skill_panel_region, 0)
        return verify_pos is None
    
    def release_skill(self, dm_index, skill_name, skill_pos, target_position):
        """释放技能"""
        if not self.click_skill(dm_index, skill_name, skill_pos):
            return False
        if target_position:
            self.click_position(dm_index, target_position[0], target_position[1])
        return True
    
    # ==================== 第一回合初始化 ====================
    def init_first_turn(self):
        """第一回合初始化：识别所有单位类型和状态"""
        self.report_battle_info("开始第一回合初始化", "system")
        
        for dm_index in [0, 1, 2]:
            dm = self.get_account_dm(dm_index)
            if not dm:
                continue
            
            account = self.state_map.get_account(dm_index)
            
            # 等待攻击按钮
            if not self.wait_for_action_button(dm_index, timeout=5.0):
                self.report_battle_info(f"大漠对象{dm_index} 未找到攻击按钮，跳过初始化", "warning")
                continue
            
            # 判断是主角还是武将
            is_main_char = self.check_summon_button(dm_index)
            
            if is_main_char:
                # 主角：识别主角技能
                skill_name, skill_pos = self.find_skill_in_panel(dm_index, self.main_char_skills, timeout=2.0)
                if skill_name:
                    account.main_char.alive = True
                    account.main_char.position = (764, 380)  # 默认位置，后续可优化
                    self.report_battle_info(f"大漠对象{dm_index} 识别到主角技能: {skill_name}", "success")
                else:
                    account.main_char.alive = False
                    self.report_battle_info(f"大漠对象{dm_index} 未识别到主角技能", "warning")
            else:
                # 武将：识别武将技能类型
                # 先查找攻击武将技能
                skill_name, skill_pos = self.find_skill_in_panel(dm_index, self.attack_general_skills, timeout=2.0)
                if skill_name:
                    # 攻击武将：分配给第一个未使用的武将位置
                    if account.general1.general_type is None:
                        account.general1.alive = True
                        account.general1.general_type = "attack"
                        account.general1.position = (572, 380)  # 默认位置
                        self.report_battle_info(f"大漠对象{dm_index} 识别到攻击武将（第1个）技能: {skill_name}", "success")
                    elif account.general2.general_type is None:
                        account.general2.alive = True
                        account.general2.general_type = "attack"
                        account.general2.position = (667, 380)  # 默认位置
                        self.report_battle_info(f"大漠对象{dm_index} 识别到攻击武将（第2个）技能: {skill_name}", "success")
                    else:
                        # 如果两个武将位置都已使用，说明是已存在的武将
                        self.report_battle_info(f"大漠对象{dm_index} 识别到已存在的攻击武将技能: {skill_name}", "info")
                else:
                    # 查找辅助武将技能
                    skill_name, skill_pos = self.find_skill_in_panel(dm_index, self.support_general_skills, timeout=2.0)
                    if skill_name:
                        # 辅助武将：分配给第一个未使用的武将位置
                        if account.general1.general_type is None:
                            account.general1.alive = True
                            account.general1.general_type = "support"
                            account.general1.position = (572, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将（第1个）技能: {skill_name}", "success")
                        elif account.general2.general_type is None:
                            account.general2.alive = True
                            account.general2.general_type = "support"
                            account.general2.position = (667, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将（第2个）技能: {skill_name}", "success")
                        else:
                            # 如果两个武将位置都已使用，说明是已存在的武将
                            self.report_battle_info(f"大漠对象{dm_index} 识别到已存在的辅助武将技能: {skill_name}", "info")
                    else:
                        # 第一回合初始化时，如果没有识别到任何武将技能，说明这个回合不是武将回合
                        # 或者武将还没有出现，不设置任何武将信息
                        self.report_battle_info(f"大漠对象{dm_index} 第一回合初始化未识别到武将技能", "info")
        
        # 第一回合初始化完成后，检查并记录未识别的武将（不添加到全局信息中）
        for dm_index in [0, 1, 2]:
            account = self.state_map.get_account(dm_index)
            # 如果general2没有被初始化（general_type为None），不会被get_active_generals()包含
            if account.general2.general_type is None:
                self.report_battle_info(f"大漠对象{dm_index} 第一回合初始化：武将2未识别，不添加到全局信息中（general_type为None）", "info")
        
        self.is_first_turn = False
        self.report_battle_info("第一回合初始化完成", "system")
    
    # ==================== 我方回合主流程 ====================
    def handle_our_turn(self):
        """处理我方回合"""
        self.report_battle_info("进入我方回合", "turn")
        
        # 重置敌军攻击点位识别标志，以便下一轮非我方回合重新识别
        self.enemy_target_detected_this_turn = False
        # 重置我军辅助技能施法点位识别标志，以便本轮重新识别
        self.ally_support_target_detected_this_turn = False
        
        # 检测我军辅助技能施法点位（在我方回合开始时检测，因为敌军回合可能阵亡）
        dm_index = 0
        dm = self.get_account_dm(dm_index)
        if dm:
            # 在我军区域内识别辅助技能施法点位（使用 lantiao 图片）
            ally_target_pos = self.find_image(dm_index, self.target_lantiao_image, self.ally_region, 0)
            if ally_target_pos:
                # 调整坐标（根据实际游戏情况调整）
                ally_target_pos.x = ally_target_pos.x + 18
                ally_target_pos.y = ally_target_pos.y + 83
                self.state_map.ally_support_target_position = (ally_target_pos.x, ally_target_pos.y)
                self.ally_support_target_detected_this_turn = True
                self.report_battle_info(f"我方回合，检测到我军辅助技能施法点位: {self.state_map.ally_support_target_position}", "info")
            else:
                # 如果没找到，使用默认位置
                if not self.state_map.ally_support_target_position:
                    self.state_map.ally_support_target_position = (764, 380)  # 默认我军中心位置
                    self.report_battle_info(f"我方回合，未检测到我军辅助技能施法点位，使用默认位置: {self.state_map.ally_support_target_position}", "warning")
            
            # 检测敌军攻击目标点位（在我方回合开始时检测）
            if not self.enemy_target_detected_this_turn:
                # 在敌军区域内识别攻击目标点位
                target_pos = self.find_image(dm_index, self.target_lantiao_image, self.enemy_region, 0)
                if target_pos:
                    # 调整坐标（根据实际游戏情况调整）
                    target_pos.x = target_pos.x + 21
                    target_pos.y = target_pos.y + 80
                    self.state_map.enemy_target_position = (target_pos.x, target_pos.y)
                    self.enemy_target_detected_this_turn = True
                    self.report_battle_info(f"我方回合，检测到攻击目标点位: {self.state_map.enemy_target_position}", "info")
                else:
                    # 如果没找到，使用默认位置
                    if not self.state_map.enemy_target_position:
                        self.state_map.enemy_target_position = self.default_enemy_target_position
                        self.report_battle_info(f"我方回合，未检测到攻击目标，使用默认位置: {self.default_enemy_target_position}", "warning")
        
        # 主角操作阶段（初始化在战斗中完成）
        self.handle_main_char_phase()
        
        # 等待攻击按钮（3秒）
        time.sleep(0.1)
        for dm_index in [0, 1, 2]:
            self.wait_for_action_button(dm_index, timeout=3.0)
        
        # 武将操作阶段（根据实际武将数量循环，最多2次）
        # 获取最大武将数量
        max_general_count = 0
        for dm_index in [0, 1, 2]:
            account = self.state_map.get_account(dm_index)
            general_count = account.get_general_count()
            if general_count > max_general_count:
                max_general_count = general_count
        
        # 根据实际武将数量循环（至少循环1次，最多2次）
        loop_count = max(1, min(2, max_general_count))
        for round_num in range(1, loop_count + 1):
            self.report_battle_info(f"武将操作阶段 - 第{round_num}轮（共{loop_count}轮）", "info")
            self.handle_general_phase()
            if round_num < loop_count:  # 如果不是最后一轮，等待下一轮
                time.sleep(0.3)
                for dm_index in [0, 1, 2]:
                    self.wait_for_action_button(dm_index, timeout=1.0)
        
        # 更新全局状态
        self.update_global_state()
        
        # 第一回合结束后，标记初始化完成
        if self.is_first_turn:
            self.is_first_turn = False
            self.report_battle_info("第一回合初始化完成（在战斗中完成）", "system")
        
        # 统计并播报阵亡数量
        dead_main_char_count = 0
        dead_general_count = 0
        for dm_index in [0, 1, 2]:
            account = self.state_map.get_account(dm_index)
            # 统计阵亡的主角
            if not account.main_char.alive:
                dead_main_char_count += 1
            # 统计阵亡的武将
            for gen_name, gen in account.get_active_generals():
                if not gen.alive:
                    dead_general_count += 1
        
        # 播报阵亡数量
        self.report_battle_info(f"我方回合结束 - 阵亡主角: {dead_main_char_count}个, 阵亡武将: {dead_general_count}个", "turn")
    
    def check_summon_success(self, dm_index, account):
        """检查上一回合召唤的武将是否成功（在武将操作阶段会检查，这里作为备用检查）
        如果召唤超时（超过一定回合数仍未识别到），则标记为失败
        """
        # 检查是否有正在复活中的武将
        for gen_name, gen in account.get_active_generals():
            if gen.reviving:
                # 有正在复活中的武将，检查是否超时（这里简化处理，在武将操作阶段会详细检查）
                # 如果超过2个回合仍未识别到，视为失败
                return False
        return True
    
    def _handle_single_main_char(self, dm_index):
        """处理单个大漠对象的主角操作（用于多线程）"""
        try:
            dm = self.get_account_dm(dm_index)
            if not dm:
                return
            
            account = self.state_map.get_account(dm_index)
            
            # 等待召唤按钮出现（我方操作回合开始时，召唤按钮可能需要一些时间才出现）
            # 先等待一段时间，确保召唤按钮已经出现
            # time.sleep(CombatConstants.SUMMON_BUTTON_INITIAL_DELAY)
            
            # 检查召唤按钮判断是主角（循环查找，超时等待）
            has_summon_button = False
            start_time = time.time()
            while time.time() - start_time < CombatConstants.SUMMON_BUTTON_WAIT_TIMEOUT:
                has_summon_button = self.check_summon_button(dm_index)
                if has_summon_button:
                    break
                time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)
            
            # 在非第一回合，如果没有识别到召唤按钮或主角技能，视为主角死亡
            if not self.is_first_turn:
                if not has_summon_button:
                    # 没有召唤按钮，尝试查找主角技能确认（增加超时时间，并尝试打开技能面板）
                    # 先尝试打开技能面板
                    skill_btn = self.find_image(dm_index, self.button_images["技能按钮"], self.right_button_region, 0)
                    if skill_btn:
                        self.click_position(dm_index, skill_btn.x, skill_btn.y)
                        time.sleep(0.3)  # 等待技能面板打开
                    
                    skill_name, skill_pos = self.find_skill_in_panel(
                        dm_index, self.main_char_skills, timeout=1.5  # 增加超时时间从0.5秒到1.5秒
                    )
                    if not skill_name:
                        # 没有召唤按钮且没有主角技能，视为主角死亡
                        with self._state_lock:
                            if account.main_char.alive or account.main_char.reviving:
                                account.main_char.alive = False
                                account.main_char.reviving = False
                                self.state_map.dead_main_char_count += 1
                                self.state_map.dead_main_char_account_indices.add(dm_index)  # 记录死亡主角的大漠对象下标
                                self.report_battle_info(f"大漠对象{dm_index} 非第一回合未识别到召唤按钮和主角技能，标记主角为死亡", "warning")
                else:
                    # 有召唤按钮，尝试查找主角技能（先确保技能面板已打开）
                    # 先尝试打开技能面板
                    skill_btn = self.find_image(dm_index, self.button_images["技能按钮"], self.right_button_region, 0)
                    if skill_btn:
                        self.click_position(dm_index, skill_btn.x, skill_btn.y)
                        time.sleep(0.3)  # 等待技能面板打开
                    
                    skill_name, skill_pos = self.find_skill_in_panel(
                        dm_index, self.main_char_skills, timeout=CombatConstants.MAIN_CHAR_SKILL_WAIT_TIMEOUT
                    )
                    if not skill_name:
                        # 有召唤按钮但没有主角技能，视为主角死亡
                        with self._state_lock:
                            if account.main_char.alive or account.main_char.reviving:
                                account.main_char.alive = False
                                account.main_char.reviving = False
                                self.state_map.dead_main_char_count += 1
                                self.state_map.dead_main_char_account_indices.add(dm_index)  # 记录死亡主角的大漠对象下标
                                self.report_battle_info(f"大漠对象{dm_index} 非第一回合有召唤按钮但未识别到主角技能，标记主角为死亡", "warning")
                    else:
                        # 识别到主角技能，说明主角存活
                        with self._state_lock:
                            # 如果是第一回合且位置未设置，进行初始化
                            if self.is_first_turn and account.main_char.position is None:
                                account.main_char.position = (764, 380)  # 默认位置
                                self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到主角技能: {skill_name}", "success")
                            
                            # 如果之前是死亡状态或正在复活中，说明复活成功
                            if not account.main_char.alive or account.main_char.reviving:
                                account.main_char.alive = True
                                account.main_char.reviving = False
                                if self.state_map.dead_main_char_count > 0:
                                    self.state_map.dead_main_char_count -= 1
                                # 清除死亡标记
                                if dm_index in self.state_map.dead_main_char_account_indices:
                                    self.state_map.dead_main_char_account_indices.discard(dm_index)
                                self.report_battle_info(f"大漠对象{dm_index} 主角复活成功", "success")
                            else:
                                # 正常存活状态，确保状态正确
                                account.main_char.alive = True
                                account.main_char.reviving = False
                        
                        # 注意：这里不直接return，继续执行后续的召唤武将和复活检查逻辑
                        # 技能释放会在最后执行
            
            # 第一回合或正常情况下的处理
            if not has_summon_button:
                # 如果没有召唤按钮，可能是武将回合，跳过主角操作
                return
            
            # ==================== 第一步：检查是否需要召唤武将 ====================
            # 1. 首先检查是否需要召唤武将（非第一回合）
            if not self.is_first_turn:
                need_summon = self.has_dead_general(account)
                self.report_battle_info(f"大漠对象{dm_index} 检查是否需要召唤武将: {need_summon} (general1: type={account.general1.general_type}, alive={account.general1.alive}, reviving={account.general1.reviving}; general2: type={account.general2.general_type}, alive={account.general2.alive}, reviving={account.general2.reviving})", "info")
                
                if need_summon:
                    # 检查上一回合是否有召唤中的武将（直接检查general1和general2，不依赖get_active_generals）
                    has_reviving_general = False
                    if account.general1.reviving or account.general2.reviving:
                        has_reviving_general = True
                        # 召唤中的武将会在武将操作阶段检查是否成功，这里不处理
                        self.report_battle_info(f"大漠对象{dm_index} 上一回合召唤的武将仍在处理中，跳过召唤", "info")
                    
                    # 如果没有正在召唤中的武将，且需要召唤，则进行召唤
                    if not has_reviving_general:
                        self.report_battle_info(f"大漠对象{dm_index} 检查到需要召唤武将，开始召唤", "info")
                        if self.try_summon_general(dm_index, account):
                            # 召唤操作完成，等待一下让武将出现
                            time.sleep(1.0)
                            self.report_battle_info(f"大漠对象{dm_index} 召唤武将操作完成", "success")
                            return
                        else:
                            # 召唤失败，继续后续操作
                            self.report_battle_info(f"大漠对象{dm_index} 召唤武将失败，继续后续操作", "warning")
                else:
                    self.report_battle_info(f"大漠对象{dm_index} 不需要召唤武将（所有武将位置都已使用且存活）", "info")
            
            # ==================== 第二步：检查是否需要复活其他账号的主角 ====================
            # 2. 检查其他账号是否全账号阵亡需要协助复活主角（优先级：主角 > 武将）
            # 注意：这里需要先检查主角是否存活，如果主角存活，优先让主角去复活
            # 在非第一回合，如果识别到召唤按钮，说明主角存活
            if has_summon_button:
                # 确保主角状态为存活（如果之前没有更新）
                with self._state_lock:
                    if not account.main_char.alive:
                        account.main_char.alive = True
                        account.main_char.reviving = False
                
                # 检查是否需要复活其他账号的主角（主角优先级最高）
                # 使用更严格的加锁机制，确保同一时间只有一个主角分配复活任务
                if not account.main_char.revive_assigned:
                    assigned_target = None
                    # 在锁内获取所有需要被复活的账号列表并分配任务
                    with self._state_lock:
                        all_dead_accounts = list(self.state_map.all_dead_account_indices)
                        dead_main_char_accounts = list(self.state_map.dead_main_char_account_indices)
                        
                        # 检查当前主角是否已经被其他主角"抢占"了任务（双重检查）
                        if account.main_char.revive_assigned is not None:
                            # 已经被分配了任务，跳过
                            pass
                        else:
                            # 优先处理全员阵亡的账号，按账号索引顺序分配，避免多个主角同时分配
                            for dead_acc_idx in sorted(all_dead_accounts):
                                if dead_acc_idx == dm_index:
                                    continue
                                
                                dead_account = self.state_map.get_account(dead_acc_idx)
                                
                                # 检查目标是否已经在复活中
                                if dead_account.main_char.reviving:
                                    continue
                                
                                # 检查是否有其他主角已经分配了复活任务（严格检查）
                                already_assigned = False
                                for other_dm_idx in [0, 1, 2]:
                                    if other_dm_idx == dm_index:
                                        continue
                                    other_acc = self.state_map.get_account(other_dm_idx)
                                    # 检查其他主角是否已分配复活任务（包括当前正在检查的主角）
                                    if other_acc.main_char.alive and other_acc.main_char.revive_assigned == dead_acc_idx:
                                        already_assigned = True
                                        break
                                
                                if not already_assigned:
                                    # 找到第一个未被分配的目标，立即分配（在锁内完成分配）
                                    account.main_char.revive_assigned = dead_acc_idx
                                    assigned_target = dead_acc_idx
                                    self.report_battle_info(f"大漠对象{dm_index} 主角检测到账号{dead_acc_idx}全部阵亡，优先分配主角进行跨账号复活", "info")
                                    break
                            
                            # 如果没有找到全员阵亡的账号，再处理主角死亡但武将可能存活的账号
                            if assigned_target is None:
                                for dead_acc_idx in sorted(dead_main_char_accounts):
                                    if dead_acc_idx == dm_index or dead_acc_idx in all_dead_accounts:
                                        continue
                                    
                                    dead_account = self.state_map.get_account(dead_acc_idx)
                                    
                                    # 检查目标是否已经在复活中
                                    if dead_account.main_char.reviving:
                                        continue
                                    
                                    # 检查是否有其他主角已经分配了复活任务
                                    already_assigned = False
                                    for other_dm_idx in [0, 1, 2]:
                                        if other_dm_idx == dm_index:
                                            continue
                                        other_acc = self.state_map.get_account(other_dm_idx)
                                        if other_acc.main_char.alive and other_acc.main_char.revive_assigned == dead_acc_idx:
                                            already_assigned = True
                                            break
                                    
                                    if already_assigned:
                                        continue
                                    
                                    # 检查目标账号是否有存活的武将
                                    has_alive_general = False
                                    for gen_name, gen in dead_account.get_active_generals():
                                        if gen.alive:
                                            has_alive_general = True
                                            break
                                    
                                    if not has_alive_general:
                                        # 目标账号的主角死亡且没有存活的武将，分配当前账号的主角进行跨账号复活
                                        account.main_char.revive_assigned = dead_acc_idx
                                        assigned_target = dead_acc_idx
                                        self.report_battle_info(f"大漠对象{dm_index} 主角检测到账号{dead_acc_idx}主角死亡且武将全部死亡，优先分配主角进行跨账号复活", "info")
                                        break
                    
                    # 执行复活操作（在锁外执行，避免长时间持有锁）
                    if assigned_target is not None:
                        dead_account = self.state_map.get_account(assigned_target)
                        if self.try_revive_main_char(dm_index, account, assigned_target):
                            # 复活操作完成，标记目标主角为复活中
                            with self._state_lock:
                                dead_account.main_char.reviving = True
                            self.report_battle_info(f"大漠对象{dm_index} 主角使用复活药复活账号{assigned_target}的主角", "action")
                            return
                        else:
                            # 复活失败，清除任务分配
                            with self._state_lock:
                                account.main_char.revive_assigned = None
                            self.report_battle_info(f"大漠对象{dm_index} 主角跨账号复活账号{assigned_target}的主角失败", "warning")
            
            # ==================== 第三步：正常的技能释放 ====================
            # 3. 等待主角技能（2秒超时）
            # 先确保技能面板已打开
            skill_btn = self.find_image(dm_index, self.button_images["技能按钮"], self.right_button_region, 0)
            if skill_btn:
                self.click_position(dm_index, skill_btn.x, skill_btn.y)
                time.sleep(0.3)  # 等待技能面板打开
            
            skill_name, skill_pos = self.find_skill_in_panel(
                dm_index, self.main_char_skills, timeout=CombatConstants.MAIN_CHAR_SKILL_WAIT_TIMEOUT
            )
            
            if skill_name and skill_pos:
                # 识别到主角技能，说明主角存活
                with self._state_lock:
                    # 如果是第一回合且位置未设置，进行初始化
                    if self.is_first_turn and account.main_char.position is None:
                        account.main_char.position = (764, 380)  # 默认位置
                        self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到主角技能: {skill_name}", "success")
                    
                    # 如果之前是死亡状态或正在复活中，说明复活成功（在下一个回合更新具体复活状态）
                    if not account.main_char.alive or account.main_char.reviving:
                        account.main_char.alive = True
                        account.main_char.reviving = False
                        if self.state_map.dead_main_char_count > 0:
                            self.state_map.dead_main_char_count -= 1
                        # 清除死亡标记
                        if dm_index in self.state_map.dead_main_char_account_indices:
                            self.state_map.dead_main_char_account_indices.discard(dm_index)
                        self.report_battle_info(f"大漠对象{dm_index} 主角复活成功", "success")
                    else:
                        # 正常存活状态，确保状态正确
                        account.main_char.alive = True
                        account.main_char.reviving = False
                
                # 释放技能
                target_pos = self.state_map.enemy_target_position or self.default_enemy_target_position
                if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                    self.report_battle_info(f"大漠对象{dm_index} 主角释放{skill_name}", "action")
            else:
                # 未识别到主角技能，再次尝试（可能技能面板还没完全打开）
                # 再次尝试打开技能面板并查找
                skill_btn = self.find_image(dm_index, self.button_images["技能按钮"], self.right_button_region, 0)
                if skill_btn:
                    self.click_position(dm_index, skill_btn.x, skill_btn.y)
                    time.sleep(0.5)  # 等待技能面板打开
                    # 再次查找技能
                    skill_name, skill_pos = self.find_skill_in_panel(
                        dm_index, self.main_char_skills, timeout=1.0
                    )
                    if skill_name and skill_pos:
                        # 第二次找到了技能，说明主角存活
                        with self._state_lock:
                            if not account.main_char.alive or account.main_char.reviving:
                                account.main_char.alive = True
                                account.main_char.reviving = False
                                if self.state_map.dead_main_char_count > 0:
                                    self.state_map.dead_main_char_count -= 1
                                if dm_index in self.state_map.dead_main_char_account_indices:
                                    self.state_map.dead_main_char_account_indices.discard(dm_index)
                                self.report_battle_info(f"大漠对象{dm_index} 主角复活成功（第二次查找）", "success")
                            else:
                                account.main_char.alive = True
                                account.main_char.reviving = False
                        
                        # 释放技能
                        target_pos = self.state_map.enemy_target_position or self.default_enemy_target_position
                        if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                            self.report_battle_info(f"大漠对象{dm_index} 主角释放{skill_name}", "action")
                        return
                
                # 两次都没找到技能，标记为死亡
                with self._state_lock:
                    # 如果正在复活中但没识别到技能，说明复活失败，标记为死亡
                    if account.main_char.reviving:
                        account.main_char.alive = False
                        account.main_char.reviving = False
                        self.state_map.dead_main_char_count += 1
                        self.state_map.dead_main_char_account_indices.add(dm_index)  # 记录死亡主角的大漠对象下标
                        self.report_battle_info(f"大漠对象{dm_index} 主角复活失败（未识别到技能），标记为死亡", "warning")
                    elif not self.is_first_turn and account.main_char.alive:
                        # 非第一回合且之前存活，现在没识别到技能，标记为死亡
                        account.main_char.alive = False
                        account.main_char.reviving = False
                        self.state_map.dead_main_char_count += 1
                        self.state_map.dead_main_char_account_indices.add(dm_index)  # 记录死亡主角的大漠对象下标
                        self.report_battle_info(f"大漠对象{dm_index} 非第一回合未识别到主角技能（已重试），标记主角为死亡", "warning")
                
                # 如果没找到技能，进行加血操作（如果主角需要加血）
                if not skill_name and account.main_char.need_heal:
                    heal_success = self.try_heal_main_char(dm_index, account)
                    # 如果没找到恢复药图片，点击防御按钮进行防御操作
                    if not heal_success:
                        defense_btn = self.find_image(dm_index, self.button_images["防御按钮"], self.right_button_region, 0)
                        if defense_btn:
                            self.click_position(dm_index, defense_btn.x, defense_btn.y)
                            time.sleep(CombatConstants.ACTION_DELAY)
                            self.report_battle_info(f"大漠对象{dm_index} 未找到恢复药，执行防御操作", "action")
                        else:
                            self.report_battle_info(f"大漠对象{dm_index} 未找到恢复药且未找到防御按钮", "warning")
        except Exception as e:
            self.report_battle_info(f"大漠对象{dm_index} 主角操作出错: {e}", "error")
    
    def handle_main_char_phase(self):
        """处理主角操作阶段（同步执行）"""
        threads = []
        for dm_index in [0, 1, 2]:
            thread = threading.Thread(target=self._handle_single_main_char, args=(dm_index,))
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    
    def _handle_single_general(self, dm_index):
        """处理单个大漠对象的武将操作（用于多线程）"""
        try:
            dm = self.get_account_dm(dm_index)
            if not dm:
                return
            
            account = self.state_map.get_account(dm_index)
            
            # 检查召唤按钮判断是武将（没有召唤按钮）
            if self.check_summon_button(dm_index):
                self.report_battle_info(f"大漠对象{dm_index} 检测到召唤按钮，跳过武将操作", "info")
                return
            
            # 等待操作按钮出现（确保技能面板已显示）
            if not self.wait_for_action_button(dm_index, timeout=2.0):
                self.report_battle_info(f"大漠对象{dm_index} 武将操作阶段未检测到操作按钮", "warning")
                # 检测不到操作按钮，可能是武将已死亡，进行死亡判定
                with self._state_lock:
                    if not self.is_first_turn:
                        # 非第一回合，标记为死亡
                        self.mark_general_dead(account)
                    else:
                        # 第一回合：如果之前已经识别过武将，现在没找到，也应该标记为死亡
                        # 优先处理正在复活中的武将（处理多个武将同时死亡的情况）
                        for gen_name, gen in account.get_active_generals():
                            if gen.reviving:
                                # 正在复活中但没识别到，说明召唤失败，标记为死亡
                                gen.alive = False
                                gen.reviving = False
                                self.report_battle_info(f"大漠对象{dm_index} 第一回合武将{gen_name}召唤失败（未检测到操作按钮），标记为死亡", "warning")
                        # 再处理正常存活的武将
                        for gen_name, gen in account.get_active_generals():
                            if gen.alive and not gen.reviving:
                                # 之前识别过但现在没找到，标记为死亡
                                gen.alive = False
                                self.report_battle_info(f"大漠对象{dm_index} 第一回合武将{gen_name}未检测到操作按钮，标记为死亡", "warning")
                
                # 即使当前账号没有武将，也要检查是否需要复活其他账号的主角
                # 检查当前账号的主角是否存活，如果存活，可以用主角来复活其他账号
                if account.main_char.alive and not account.main_char.revive_assigned:
                    # 查找需要被复活的其他账号的主角
                    for dead_acc_idx in list(self.state_map.dead_main_char_account_indices):
                        if dead_acc_idx == dm_index:
                            # 跳过当前账号
                            continue
                        
                        # 加锁检查并分配复活任务
                        with self._state_lock:
                            dead_account = self.state_map.get_account(dead_acc_idx)
                            
                            # 检查目标是否已经在复活中或被其他单位分配了复活任务
                            if dead_account.main_char.reviving:
                                # 已经在复活中，跳过
                                continue
                            
                            # 检查是否有其他单位已经分配了复活任务
                            already_assigned = False
                            for other_dm_idx in [0, 1, 2]:
                                if other_dm_idx == dm_index:
                                    continue
                                other_acc = self.state_map.get_account(other_dm_idx)
                                if (other_acc.main_char.revive_assigned == dead_acc_idx or
                                    other_acc.general1.revive_assigned == dead_acc_idx or
                                    other_acc.general2.revive_assigned == dead_acc_idx):
                                    already_assigned = True
                                    break
                            
                            if already_assigned:
                                continue
                            
                            # 检查是否需要跨账号复活
                            if dead_acc_idx in self.state_map.all_dead_account_indices:
                                # 目标账号全部阵亡，分配当前账号的主角进行跨账号复活
                                account.main_char.revive_assigned = dead_acc_idx
                                self.report_battle_info(f"大漠对象{dm_index} 主角检测到账号{dead_acc_idx}全部阵亡（武将操作阶段），尝试跨账号复活", "info")
                            else:
                                continue
                        
                        # 执行复活操作（在锁外执行）
                        if account.main_char.revive_assigned == dead_acc_idx:
                            if self.try_revive_main_char(dm_index, account, dead_acc_idx):
                                # 复活操作完成，标记目标主角为复活中
                                with self._state_lock:
                                    dead_account.main_char.reviving = True
                                self.report_battle_info(f"大漠对象{dm_index} 主角使用复活药复活账号{dead_acc_idx}的主角", "action")
                                return
                            else:
                                # 复活失败，清除任务分配
                                with self._state_lock:
                                    account.main_char.revive_assigned = None
                                self.report_battle_info(f"大漠对象{dm_index} 主角跨账号复活账号{dead_acc_idx}的主角失败", "warning")
                
                return
            
            # 确保技能面板已打开（点击技能按钮）
            skill_btn = self.find_image(dm_index, self.button_images["技能按钮"], self.right_button_region, 0)
            if skill_btn:
                self.click_position(dm_index, skill_btn.x, skill_btn.y)
                time.sleep(CombatConstants.ACTION_DELAY)
            
            # 1. 优先判断是否需要复活当前账号的主角（必须在查找武将技能之前）
            if dm_index in self.state_map.dead_main_char_account_indices:
                # 当前账号的主角死亡，尝试复活
                dead_account = self.state_map.get_account(dm_index)
                if not dead_account.main_char.reviving:
                    # 检查当前账号是否有存活的武将
                    has_alive_general = False
                    for gen_name, gen in account.get_active_generals():
                        if gen.alive:
                            has_alive_general = True
                            break
                    
                    if has_alive_general:
                        # 当前账号有存活的武将，直接使用当前账号的武将进行复活
                        self.report_battle_info(f"大漠对象{dm_index} 当前账号主角死亡，使用当前账号武将进行复活", "info")
                        if self.try_revive_main_char(dm_index, account, dm_index):
                            # 复活操作完成，标记主角为复活中
                            with self._state_lock:
                                dead_account.main_char.reviving = True
                            self.report_battle_info(f"大漠对象{dm_index} 使用当前账号武将复活主角", "action")
                            return
                    else:
                        # 当前账号武将全部死亡，分配其他账号去复活这个主角
                        self.report_battle_info(f"大漠对象{dm_index} 当前账号武将全部死亡，分配其他账号进行复活", "info")
                        revive_assigned = self.assign_revive_task_cross_account(dm_index, account, dm_index)
                        if revive_assigned:
                            if self.try_revive_main_char(dm_index, account, dm_index):
                                # 复活操作完成，标记主角为复活中
                                with self._state_lock:
                                    dead_account.main_char.reviving = True
                                self.report_battle_info(f"大漠对象{dm_index} 使用其他账号单位复活主角", "action")
                                return
                            else:
                                # 跨账号复活失败，清除所有账号的复活任务分配
                                with self._state_lock:
                                    self._clear_all_revive_assignments()
                                self.report_battle_info(f"大漠对象{dm_index} 跨账号复活失败，已清除所有复活任务分配", "warning")
                        else:
                            self.report_battle_info(f"大漠对象{dm_index} 未能分配跨账号复活任务", "warning")
            
            # 2. 检查是否需要复活其他账号的主角或武将（即使当前账号的主角死亡，武将也可以复活其他账号）
            # 遍历所有需要被复活的账号
            for target_acc_idx in list(self.state_map.dead_main_char_account_indices):
                if target_acc_idx == dm_index:
                    # 跳过当前账号（已经在上面处理了）
                    continue
                
                # 加锁检查并分配复活任务
                with self._state_lock:
                    target_account = self.state_map.get_account(target_acc_idx)
                    
                    # 检查目标是否已经在复活中或被其他单位分配了复活任务
                    if target_account.main_char.reviving:
                        # 已经在复活中，跳过
                        continue
                    
                    # 检查是否有其他单位已经分配了复活任务
                    already_assigned = False
                    for other_dm_idx in [0, 1, 2]:
                        if other_dm_idx == dm_index:
                            continue
                        other_acc = self.state_map.get_account(other_dm_idx)
                        if (other_acc.main_char.revive_assigned == target_acc_idx or
                            other_acc.general1.revive_assigned == target_acc_idx or
                            other_acc.general2.revive_assigned == target_acc_idx):
                            already_assigned = True
                            break
                    
                    if already_assigned:
                        continue
                    
                    # 检查当前账号是否有存活的武将可以执行复活
                    has_alive_general = False
                    available_general = None
                    for gen_name, gen in account.get_active_generals():
                        if gen.alive and not gen.revive_assigned:
                            has_alive_general = True
                            available_general = (gen_name, gen)
                            break
                    
                    if has_alive_general:
                        # 当前账号有存活的武将，尝试分配复活任务
                        gen_name, gen = available_general
                        # 检查是否应该由当前账号的武将来复活
                        if target_acc_idx in self.state_map.all_dead_account_indices:
                            # 目标账号全部阵亡，分配当前账号的武将进行跨账号复活
                            gen.revive_assigned = target_acc_idx
                            self.report_battle_info(f"大漠对象{dm_index} 武将{gen_name}检测到账号{target_acc_idx}全部阵亡，尝试跨账号复活", "info")
                        else:
                            continue
                
                # 执行复活操作（在锁外执行）
                if has_alive_general and available_general:
                    gen_name, gen = available_general
                    if gen.revive_assigned == target_acc_idx:
                        if self.try_revive_main_char(dm_index, account, target_acc_idx):
                            # 复活操作完成，标记目标主角为复活中
                            with self._state_lock:
                                target_account.main_char.reviving = True
                            self.report_battle_info(f"大漠对象{dm_index} 武将{gen_name}使用复活药复活账号{target_acc_idx}的主角", "action")
                            return
                        else:
                            # 复活失败，清除任务分配
                            with self._state_lock:
                                gen.revive_assigned = None
                            self.report_battle_info(f"大漠对象{dm_index} 武将{gen_name}跨账号复活账号{target_acc_idx}的主角失败", "warning")
            
            # 2. 查找武将技能（3秒超时）
            self.report_battle_info(f"大漠对象{dm_index} 开始查找武将技能", "info")
            
            # 前置快速判断：先快速查找控制技能（0.5秒），如果是辅助武将，可以跳过攻击武将的3秒查找
            control_skill_found = False
            control_skill_name = None
            control_skill_pos = None
            
            # 快速查找控制技能（"控制"）
            control_skill_name, control_skill_pos = self.find_skill_in_panel(
                dm_index, ["控制"], timeout=0.5
            )
            if control_skill_name and control_skill_pos:
                control_skill_found = True
                self.report_battle_info(f"大漠对象{dm_index} 前置判断：识别到辅助武将技能（控制），跳过攻击武将查找", "info")
            
            # 如果前置判断没找到控制技能，再查找攻击武将技能
            skill_name = None
            skill_pos = None
            if not control_skill_found:
                # 先查找攻击武将技能
                skill_name, skill_pos = self.find_skill_in_panel(
                    dm_index, self.attack_general_skills, timeout=CombatConstants.GENERAL_SKILL_WAIT_TIMEOUT
                )
            
            if skill_name and skill_pos:
                # 识别到攻击武将技能
                self.report_battle_info(f"大漠对象{dm_index} 识别到攻击武将技能: {skill_name}", "success")
                with self._state_lock:
                    # 如果是第一回合且武将类型未设置，进行初始化
                    if self.is_first_turn:
                        # 分配给第一个未使用的武将位置
                        if account.general1.general_type is None:
                            account.general1.alive = True
                            account.general1.general_type = "attack"
                            account.general1.position = (572, 380)  # 默认位置
                            self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到攻击武将（第1个）技能: {skill_name}", "success")
                        elif account.general2.general_type is None:
                            account.general2.alive = True
                            account.general2.general_type = "attack"
                            account.general2.position = (667, 380)  # 默认位置
                            self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到攻击武将（第2个）技能: {skill_name}", "success")
                    
                    self.update_general_status(account, "attack", skill_name)
                target_pos = self.state_map.enemy_target_position or self.default_enemy_target_position
                if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                    self.report_battle_info(f"大漠对象{dm_index} 攻击武将释放{skill_name}", "action")
                return
            
            # 查找辅助武将技能
            # 重置技能名称和位置，准备按顺序查找
            skill_name = None
            skill_pos = None
            
            # 1. 优先检查是否需要清除状态
            with self._state_lock:
                has_enemies_need_clear = bool(self.state_map.enemies_need_clear)
            
            if has_enemies_need_clear:
                # 优先查找清除状态技能（如果前置判断找到了控制技能，需要重新查找清除状态技能）
                if control_skill_found:
                    skill_name = None
                    skill_pos = None
                skill_name, skill_pos = self.find_skill_in_panel(
                    dm_index, ["清除状态"], timeout=CombatConstants.GENERAL_SKILL_WAIT_TIMEOUT
                )
                if skill_name and skill_pos:
                    # 识别到清除状态技能
                    self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将技能: {skill_name}（优先清除状态）", "success")
                    with self._state_lock:
                        # 如果是第一回合且武将类型未设置，进行初始化
                        if self.is_first_turn:
                            # 分配给第一个未使用的武将位置
                            if account.general1.general_type is None:
                                account.general1.alive = True
                                account.general1.general_type = "support"
                                account.general1.position = (572, 380)
                                self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到辅助武将（第1个）技能: {skill_name}", "success")
                            elif account.general2.general_type is None:
                                account.general2.alive = True
                                account.general2.general_type = "support"
                                account.general2.position = (667, 380)
                                self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到辅助武将（第2个）技能: {skill_name}", "success")
                        
                        self.update_general_status(account, "support", skill_name)
                        
                        # 清除状态：对需要清除的敌军释放（使用固定点位）
                        if self.state_map.enemies_need_clear:
                            enemy_info = self.state_map.enemies_need_clear[0]  # 取第一个
                            target_pos = enemy_info.get("cast_position") or enemy_info.get("position")  # 使用固定点位
                            if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                                self.report_battle_info(f"大漠对象{dm_index} 辅助武将释放{skill_name}清除{enemy_info['enemy_name']}状态，固定点位: {target_pos}", "action")
                                # 移除已清除的敌军
                                self.state_map.enemies_need_clear.pop(0)
                    return
            
            # 2. 如果不需要清除状态，按照顺序查找技能：["加攻击", "加血", "控制"]
            # 始终按照顺序查找技能，不管前置判断是否找到控制技能
            if not skill_name:
                # 获取当前技能索引
                if dm_index not in self.liubei_skill_index:
                    self.liubei_skill_index[dm_index] = 0
                
                current_index = self.liubei_skill_index[dm_index]
                sequence_length = len(self.liubei_skill_sequence)
                
                # 按照顺序尝试查找技能（从当前索引开始，循环查找）
                for attempt in range(sequence_length):
                    skill_to_find = self.liubei_skill_sequence[(current_index + attempt) % sequence_length]
                    skill_name, skill_pos = self.find_skill_in_panel(
                        dm_index, [skill_to_find], timeout=CombatConstants.GENERAL_SKILL_WAIT_TIMEOUT
                    )
                    if skill_name and skill_pos:
                        # 找到技能，更新索引到下一个
                        self.liubei_skill_index[dm_index] = (current_index + attempt + 1) % sequence_length
                        break
            
            if skill_name and skill_pos:
                # 识别到辅助武将技能
                self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将技能: {skill_name}（顺序: {self.liubei_skill_index[dm_index] % len(self.liubei_skill_sequence) + 1}/{len(self.liubei_skill_sequence)}）", "success")
                with self._state_lock:
                    # 如果是第一回合且武将类型未设置，进行初始化
                    if self.is_first_turn:
                        # 分配给第一个未使用的武将位置
                        if account.general1.general_type is None:
                            account.general1.alive = True
                            account.general1.general_type = "support"
                            account.general1.position = (572, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到辅助武将（第1个）技能: {skill_name}", "success")
                        elif account.general2.general_type is None:
                            account.general2.alive = True
                            account.general2.general_type = "support"
                            account.general2.position = (667, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 初始化：识别到辅助武将（第2个）技能: {skill_name}", "success")
                    
                    self.update_general_status(account, "support", skill_name)
                
                # 按技能顺序释放
                self.release_support_skill(dm_index, account, skill_name, skill_pos)
            else:
                # 未识别到武将技能
                self.report_battle_info(f"大漠对象{dm_index} 未识别到武将技能", "warning")
                # 标记为死亡（第一回合可能还没召唤武将，但如果不是第一回合，应该标记为死亡）
                with self._state_lock:
                    if not self.is_first_turn:
                        self.mark_general_dead(account)
                    else:
                        # 第一回合：如果之前已经识别过武将，现在没找到，也应该标记为死亡
                        # 优先处理正在复活中的武将（处理多个武将同时死亡的情况）
                        for gen_name, gen in account.get_active_generals():
                            if gen.reviving:
                                # 正在复活中但没识别到，说明召唤失败，标记为死亡
                                gen.alive = False
                                gen.reviving = False
                                self.report_battle_info(f"大漠对象{dm_index} 第一回合武将{gen_name}召唤失败（未识别到技能），标记为死亡", "warning")
                        # 再处理正常存活的武将
                        for gen_name, gen in account.get_active_generals():
                            if gen.alive and not gen.reviving:
                                # 之前识别过但现在没找到，标记为死亡
                                gen.alive = False
                                self.report_battle_info(f"大漠对象{dm_index} 第一回合武将{gen_name}未识别到技能，标记为死亡", "warning")
        except Exception as e:
            self.report_battle_info(f"大漠对象{dm_index} 武将操作出错: {e}", "error")
    
    def handle_general_phase(self):
        """处理武将操作阶段（同步执行）"""
        threads = []
        for dm_index in [0, 1, 2]:
            thread = threading.Thread(target=self._handle_single_general, args=(dm_index,))
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
    
    def has_dead_general(self, account):
        """检查是否有武将死亡（只检查已初始化的武将是否死亡，不检查空位）
        注意：空位（general_type为None）不应该被视为需要召唤的情况，
        因为账号可能只有1个武将，这是正常的
        """
        # 只检查已初始化的武将是否死亡
        for gen_name, gen in account.get_active_generals():
            if not gen.alive:
                return True
        
        # 不检查空位，因为空位可能是正常的（账号只有1个武将）
        return False

    def try_summon_general(self, dm_index, account):
        """尝试召唤武将"""
        # 召唤顺序：刘备（如果不存在存活的辅助武将）→ 曹操 → 魔化关羽
        has_support = False
        for gen in [account.general1, account.general2]:
            if gen.alive and gen.general_type == "support":
                has_support = True
                break
        
        general_order = ["刘备", "曹操", "魔化关羽"] if not has_support else ["曹操", "魔化关羽"]
        
        for general_name in general_order:
            if self.summon_general(dm_index, general_name):
                # 确定要召唤的武将类型
                target_type = "support" if general_name == "刘备" else "attack"
                
                # 更新武将状态为复活中（优先分配给已死亡且类型匹配的位置，然后是已死亡的位置，最后是空位）
                assigned = False
                
                # 1. 优先分配给已死亡且类型匹配的位置
                if account.general1.general_type == target_type and not account.general1.alive:
                    account.general1.reviving = True
                    account.general1.alive = False  # 保持死亡状态，直到下一回合确认复活成功
                    self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给已死亡的武将1位置（类型匹配）", "info")
                    assigned = True
                elif account.general2.general_type == target_type and not account.general2.alive:
                    account.general2.reviving = True
                    account.general2.alive = False  # 保持死亡状态，直到下一回合确认复活成功
                    self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给已死亡的武将2位置（类型匹配）", "info")
                    assigned = True
                
                # 2. 如果没有类型匹配的已死亡位置，分配给其他已死亡的位置
                if not assigned:
                    if account.general1.general_type is not None and not account.general1.alive:
                        account.general1.reviving = True
                        account.general1.alive = False
                        account.general1.general_type = target_type  # 更新类型
                        self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给已死亡的武将1位置（更新类型）", "info")
                        assigned = True
                    elif account.general2.general_type is not None and not account.general2.alive:
                        account.general2.reviving = True
                        account.general2.alive = False
                        account.general2.general_type = target_type  # 更新类型
                        self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给已死亡的武将2位置（更新类型）", "info")
                        assigned = True
                
                # 3. 如果没有已死亡的位置，分配给空位
                if not assigned:
                    if account.general1.general_type is None:
                        account.general1.reviving = True
                        account.general1.position = (572, 380)  # 默认位置
                        account.general1.general_type = target_type
                        self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给武将1位置（新武将）", "info")
                        assigned = True
                    elif account.general2.general_type is None:
                        account.general2.reviving = True
                        account.general2.position = (667, 380)  # 默认位置
                        account.general2.general_type = target_type
                        self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}，分配给武将2位置（新武将）", "info")
                        assigned = True
                
                if not assigned:
                    # 如果两个位置都已使用且都存活，不应该召唤（这种情况不应该发生）
                    self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}失败：所有武将位置都已使用且存活", "warning")
                    return False
                
                return True
        return False

    def summon_general(self, dm_index, general_name):
        """召唤武将"""
        # 点击召唤按钮 - 在循环中查找召唤按钮（超时3秒）
        summon_btn = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            summon_btn = self.find_image(dm_index, self.button_images["召唤按钮"], self.right_button_region, 0)
            if summon_btn:
                break
            time.sleep(0.1)
        
        if not summon_btn:
            self.report_battle_info(f"大漠对象{dm_index} 查找召唤按钮超时（3秒）", "warning")
            return False

        self.click_position(dm_index, summon_btn.x, summon_btn.y)
        time.sleep(0.1)

        # 查找武将图片 - 在循环中查找武将图片（超时3秒）
        general_path = self.bag_general_images.get(general_name)
        if not general_path:
            return False

        general_pos = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            general_pos = self.find_image(dm_index, general_path, self.summon_panel_region, 0)
            if general_pos:
                break
            time.sleep(0.1)
        
        if general_pos:
            self.click_position(dm_index, general_pos.x, general_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}成功", "action")
            return True
        else:
            self.report_battle_info(f"大漠对象{dm_index} 查找武将{general_name}图片超时（3秒）", "warning")
            return False

    def _clear_all_revive_assignments(self):
        """清除所有账号的复活任务分配"""
        for acc in self.state_map.get_all_accounts():
            acc.main_char.revive_assigned = None
            acc.general1.revive_assigned = None
            acc.general2.revive_assigned = None

    def assign_revive_task_cross_account(self, current_dm_index, current_account, target_dead_account_idx):
        """跨账号分配复活任务（优先主角，然后是武将）
        :param current_dm_index: 当前大漠对象索引（需要被复活的主角账号）
        :param current_account: 当前账号状态
        :param target_dead_account_idx: 需要被复活的主角账号索引
        """
        # 检查需要被复活的主角是否已经在复活中
        dead_account = self.state_map.get_account(target_dead_account_idx)
        if dead_account.main_char.reviving:
            # 已经在复活中，避免重复复活
            return False

        # 检查当前账号是否已经有单位被分配了复活任务
        if (current_account.main_char.revive_assigned is not None or 
            current_account.general1.revive_assigned is not None or 
            current_account.general2.revive_assigned is not None):
                return False

        # 遍历所有账号，按优先级分配：主角 > 辅助武将 > 攻击武将
        for acc_idx in range(3):
            if acc_idx == target_dead_account_idx:
                # 跳过需要被复活的账号（该账号全部阵亡）
                continue
            
            acc = self.state_map.get_account(acc_idx)
            
            # 检查账号是否真的全部阵亡（主角和所有武将都死亡）
            # 即使账号在 all_dead_account_indices 中，也要检查是否有存活的武将
            if acc_idx in self.state_map.all_dead_account_indices:
                # 检查是否真的有存活的武将（可能状态更新不及时）
                has_alive_general = False
                for gen_name, gen in acc.get_active_generals():
                    if gen.alive:
                        has_alive_general = True
                        break
                
                if not has_alive_general:
                    # 确实全部阵亡，跳过
                    continue
                # 如果有存活的武将，继续处理（即使主角死亡，武将也可以执行复活）
            
            # 优先检查主角
            if acc.main_char.alive and not acc.main_char.revive_assigned:
                acc.main_char.revive_assigned = target_dead_account_idx
                self.report_battle_info(f"分配账号{acc_idx}的主角进行跨账号复活账号{target_dead_account_idx}的主角", "info")
                return True
            
            # 再检查辅助武将
            for gen_name, gen in acc.get_active_generals():
                if gen.alive and gen.general_type == "support" and not gen.revive_assigned:
                    gen.revive_assigned = target_dead_account_idx
                    self.report_battle_info(f"分配账号{acc_idx}的辅助武将{gen_name}进行跨账号复活账号{target_dead_account_idx}的主角", "info")
                    return True
            
            # 最后检查攻击武将
            for gen_name, gen in acc.get_active_generals():
                if gen.alive and gen.general_type == "attack" and not gen.revive_assigned:
                    gen.revive_assigned = target_dead_account_idx
                    self.report_battle_info(f"分配账号{acc_idx}的攻击武将{gen_name}进行跨账号复活账号{target_dead_account_idx}的主角", "info")
                    return True

        return False

    def try_revive_main_char(self, dm_index, account, target_dead_account_idx):
        """尝试复活主角
        :param dm_index: 执行操作的大漠对象索引
        :param account: 当前账号状态
        :param target_dead_account_idx: 需要被复活的主角账号索引（大漠对象下标）
        """
        # 使用复活药 - 在循环中查找道具按钮（超时1.5秒）
        item_btn = None
        start_time = time.time()
        while time.time() - start_time < 1.5:
            item_btn = self.find_image(dm_index, self.button_images["道具按钮"], self.right_button_region, 0)
            if item_btn:
                break
            time.sleep(0.1)
        
        if not item_btn:
            self.report_battle_info(f"大漠对象{dm_index} 查找道具按钮超时（1.5秒）", "warning")
            return False
        
        self.click_position(dm_index, item_btn.x, item_btn.y)
        time.sleep(0.5)
        
        # 查找复活药 - 在循环中查找复活药图片（超时3秒）
        revive_path = self.item_images.get("复活药")
        if not revive_path:
            return False
        
        revive_pos = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            revive_pos = self.find_image(dm_index, revive_path, self.item_panel_region, 0)
            if revive_pos:
                break
            time.sleep(0.1)
        
        if not revive_pos:
            self.report_battle_info(f"大漠对象{dm_index} 查找复活药图片超时（3秒）", "warning")
            return False
        
        self.click_position(dm_index, revive_pos.x, revive_pos.y)
        time.sleep(CombatConstants.ACTION_DELAY)
        
        # 在指定账号的主角区域查找复活目标图片（fuhuohuo）
        # 大漠对象0对应中间，大漠对象1对应上面，大漠对象2对应下面
        search_region = None
        if target_dead_account_idx in self.account_main_char_regions:
            search_region = self.account_main_char_regions[target_dead_account_idx]
            self.report_battle_info(f"大漠对象{dm_index} 在账号{target_dead_account_idx}的主角区域查找复活目标", "info")
        else:
            # 如果账号区域不存在，使用整个道具面板区域
            search_region = self.item_panel_region
            self.report_battle_info(f"大漠对象{dm_index} 账号{target_dead_account_idx}的区域不存在，使用整个道具面板区域", "warning")
        
        target_pos = self.find_target_text(dm_index, search_region, timeout=3.0)
        
        if target_pos:
            # 找到后，将坐标 y+80 进行施法
            cast_x = target_pos.x
            cast_y = target_pos.y + 80
            self.click_position(dm_index, cast_x, cast_y)
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"大漠对象{dm_index} 使用复活药复活账号{target_dead_account_idx}的主角，找到目标图片位置: ({target_pos.x}, {target_pos.y})，施法位置: ({cast_x}, {cast_y})", "action")
            return True
        else:
            target_pos = self.find_target_text(dm_index, self.item_panel_region, timeout=3.0)
            if target_pos:
                # 找到后，将坐标 y+80 进行施法
                cast_x = target_pos.x
                cast_y = target_pos.y + 80
                self.click_position(dm_index, cast_x, cast_y)
                time.sleep(CombatConstants.ACTION_DELAY)
                self.report_battle_info(f"大漠对象{dm_index} 使用复活药复活账号{target_dead_account_idx}的主角，找到目标图片位置: ({target_pos.x}, {target_pos.y})，施法位置: ({cast_x}, {cast_y})", "action")
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
                self.click_position(dm_index, default_pos[0], default_pos[1])
                time.sleep(CombatConstants.ACTION_DELAY)
                self.report_battle_info(f"大漠对象{dm_index} 使用复活药复活账号{target_dead_account_idx}的主角（未找到目标图片，使用默认位置: {default_pos}）", "warning")
                return True

    def update_general_status(self, account, general_type, skill_name):
        """更新武将状态（只更新实际存在的武将）"""
        # 如果识别到武将技能，说明武将存活
        # 优先匹配相同类型的武将
        matched = False
        for gen_name, gen in account.get_active_generals():
            if gen.general_type == general_type:
                if not gen.alive or gen.reviving:
                    # 如果之前是死亡或正在复活中，说明复活成功
                    gen.alive = True
                    gen.reviving = False
                    self.report_battle_info(f"{general_type}武将（{gen_name}）复活成功", "success")
                else:
                    gen.alive = True
                    gen.reviving = False
                matched = True
                break
        
        # 如果没有匹配到，检查是否有正在复活中的武将（处理多个武将同时死亡的情况）
        if not matched:
            for gen_name, gen in account.get_active_generals():
                if gen.reviving:
                    # 如果正在复活中，更新类型
                    gen.alive = True
                    gen.reviving = False
                    gen.general_type = general_type
                    self.report_battle_info(f"武将（{gen_name}）复活成功，类型: {general_type}", "success")
                    break
                
    def mark_general_dead(self, account):
        """标记武将死亡（只标记实际存在的武将，处理多个武将同时死亡的情况）"""
        # 先处理正在复活中的武将（优先处理，因为召唤失败需要立即标记）
        for gen_name, gen in account.get_active_generals():
            if gen.reviving:
                # 正在复活中但没识别到，说明召唤失败，标记为死亡
                gen.alive = False
                gen.reviving = False
                gen.revive_assigned = None  # 清除复活任务分配
                self.report_battle_info(f"武将（{gen_name}）召唤失败（未识别到技能），标记为死亡", "warning")
                return  # 处理完一个就返回，避免重复处理
        
        # 再处理正常存活的武将
        for gen_name, gen in account.get_active_generals():
            if gen.alive and not gen.reviving:
                gen.alive = False
                gen.revive_assigned = None  # 清除复活任务分配
                self.report_battle_info(f"武将（{gen_name}）未识别到技能，标记为死亡", "warning")
                break
    
    def release_support_skill(self, dm_index, account, skill_name, skill_pos):
        """释放辅助技能（直接释放识别到的技能，不检查技能顺序）"""
        # 选择目标
        if skill_name in ["加攻击", "加血"]:
            # 辅助技能：使用非我方回合检测到的我军辅助技能施法点位
            target_pos = self.state_map.ally_support_target_position
            if not target_pos:
                # 如果未检测到，使用默认位置
                target_pos = (764, 380)  # 默认我军中心位置
                self.report_battle_info(f"大漠对象{dm_index} 未检测到辅助技能施法点位，使用默认位置", "warning")
        elif skill_name == "控制":
            # 攻击技能：使用敌军目标
            target_pos = self.state_map.enemy_target_position or self.default_enemy_target_position
        else:
            # 清除状态技能：使用检测到的敌军固定点位
            if skill_name == "清除状态" and self.state_map.enemies_need_clear:
                # 使用第一个需要清除的敌军固定点位
                enemy_info = self.state_map.enemies_need_clear[0]
                target_pos = enemy_info.get("cast_position") or enemy_info.get("position")
            else:
                # 其他情况使用敌军目标
                target_pos = self.state_map.enemy_target_position or self.default_enemy_target_position
        
        # 直接释放识别到的技能
        # 注意：技能索引已经在_handle_single_general中更新，这里不需要再次更新
        if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
            self.report_battle_info(f"大漠对象{dm_index} 辅助武将释放{skill_name}，目标: {target_pos}", "action")
        else:
            self.report_battle_info(f"大漠对象{dm_index} 辅助武将释放{skill_name}失败", "error")
    
    def select_alive_ally(self, dm_index):
        """选择存活的友军单位（只考虑实际存在的武将）"""
        # 收集所有存活单位位置
        ally_positions = []
        
        # 根据账号索引的默认位置配置（主角位置）
        default_main_char_positions = {
            0: (764, 380),  # 账号0主角默认位置
            1: (764, 340),  # 账号1主角默认位置（根据游戏布局调整）
            2: (764, 300),  # 账号2主角默认位置（根据游戏布局调整）
        }
        
        # 根据账号索引的默认位置配置（武将位置）
        default_general_positions = {
            0: [(572, 380), (667, 380)],  # 账号0武将默认位置
            1: [(572, 340), (667, 340)],  # 账号1武将默认位置
            2: [(572, 300), (667, 300)],  # 账号2武将默认位置
        }
        
        for account_idx, account in enumerate(self.state_map.get_all_accounts()):
            # 收集主角位置
            if account.main_char.alive:
                if account.main_char.position:
                    ally_positions.append(account.main_char.position)
                else:
                    # 如果位置不存在，使用默认位置
                    default_pos = default_main_char_positions.get(account_idx, (764, 380))
                    ally_positions.append(default_pos)
                    self.report_battle_info(f"账号{account_idx}主角位置未设置，使用默认位置: {default_pos}", "info")
            
            # 只处理实际存在的武将
            general_idx = 0
            for gen_name, gen in account.get_active_generals():
                if gen.alive:
                    if gen.position:
                        ally_positions.append(gen.position)
                    else:
                        # 如果位置不存在，使用默认位置
                        default_gen_positions = default_general_positions.get(account_idx, [(572, 380), (667, 380)])
                        if general_idx < len(default_gen_positions):
                            default_pos = default_gen_positions[general_idx]
                            ally_positions.append(default_pos)
                            self.report_battle_info(f"账号{account_idx}武将{gen_name}位置未设置，使用默认位置: {default_pos}", "info")
                general_idx += 1
        
        if ally_positions:
            selected_pos = random.choice(ally_positions)
            self.report_battle_info(f"大漠对象{dm_index} 选择存活单位位置: {selected_pos}（共{len(ally_positions)}个可选单位）", "info")
            return selected_pos
        else:
            # 如果没有任何存活单位，使用第一个账号的默认位置
            default_pos = default_main_char_positions.get(0, (764, 380))
            self.report_battle_info(f"大漠对象{dm_index} 未找到存活单位，使用默认位置: {default_pos}", "warning")
            return default_pos
    
    def try_heal_main_char(self, dm_index, account):
        """尝试给主角加血"""
        if not account.main_char.need_heal:
            return False
        
        # 使用恢复药 - 在循环中查找道具按钮（超时3秒）
        item_btn = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            item_btn = self.find_image(dm_index, self.button_images["道具按钮"], self.right_button_region, 0)
            if item_btn:
                break
            time.sleep(0.1)
        
        if not item_btn:
            self.report_battle_info(f"大漠对象{dm_index} 查找道具按钮超时（3秒）", "warning")
            return False
        
        self.click_position(dm_index, item_btn.x, item_btn.y)
        time.sleep(0.1)
        
        # 查找恢复药 - 在循环中查找恢复药图片（超时3秒）
        heal_path = self.item_images.get("恢复药")
        if not heal_path:
            return False

        heal_pos = None
        start_time = time.time()
        while time.time() - start_time < 3.0:
            heal_pos = self.find_image(dm_index, heal_path, self.item_panel_region, 0)
            if heal_pos:
                break
            time.sleep(0.1)
        
        if not heal_pos:
            self.report_battle_info(f"大漠对象{dm_index} 查找恢复药图片超时（3秒）", "warning")
            return False

        self.click_position(dm_index, heal_pos.x, heal_pos.y)
        time.sleep(CombatConstants.ACTION_DELAY)
        
        # 点击主角位置
        target_pos = account.main_char.position or (764, 380)
        self.click_position(dm_index, target_pos[0], target_pos[1])
        time.sleep(CombatConstants.ACTION_DELAY)
        account.main_char.need_heal = False
        self.report_battle_info(f"大漠对象{dm_index} 给主角加血", "action")
        return True
    
    def update_global_state(self):
        """更新全局状态（回合结束时）"""
        # 更新所有单位的状态
        for account in self.state_map.get_all_accounts():
            # 重置需要加血标记（下一回合重新检测）
            account.main_char.need_heal = False
            # 只重置实际存在的武将的加血标记
            for gen_name, gen in account.get_active_generals():
                gen.need_heal = False
            
            # 清除复活任务分配（下一回合重新分配）
            account.main_char.revive_assigned = None
            # 只清除实际存在的武将的复活任务分配
            for gen_name, gen in account.get_active_generals():
                gen.revive_assigned = None
            
            # 如果武将正在复活中，且下一回合识别到了，状态已在handle_general_phase中更新
            # 如果下一回合没识别到，保持reviving状态
        
        # 如果主角复活成功，清除死亡标记（遍历所有账号检查）
        for acc_idx in list(self.state_map.dead_main_char_account_indices):
            acc = self.state_map.get_account(acc_idx)
            if acc.main_char.alive and not acc.main_char.reviving:
                # 主角已复活，清除标记
                self.state_map.dead_main_char_account_indices.discard(acc_idx)
                if self.state_map.dead_main_char_count > 0:
                    self.state_map.dead_main_char_count -= 1
        
        # 检查并更新全部阵亡的账号标记
        for acc_idx in range(3):
            acc = self.state_map.get_account(acc_idx)
            # 检查账号是否全部阵亡（主角和所有武将都死亡）
            if not acc.main_char.alive:
                # 主角死亡，检查是否有存活的武将
                has_alive_general = False
                for gen_name, gen in acc.get_active_generals():
                    if gen.alive:
                        has_alive_general = True
                        break
                
                if not has_alive_general:
                    # 主角和所有武将都死亡，添加到全部阵亡账号集合
                    if acc_idx not in self.state_map.all_dead_account_indices:
                        self.state_map.all_dead_account_indices.add(acc_idx)
                        self.report_battle_info(f"账号{acc_idx}全部阵亡（主角和武将都死亡）", "warning")
                else:
                    # 有存活的武将，移除标记
                    if acc_idx in self.state_map.all_dead_account_indices:
                        self.state_map.all_dead_account_indices.discard(acc_idx)
            else:
                # 主角存活，移除标记
                if acc_idx in self.state_map.all_dead_account_indices:
                    self.state_map.all_dead_account_indices.discard(acc_idx)
            
        # 回合结束，进行全局状态更新
        self.report_battle_info("全局状态已更新", "system")
    
    # ==================== 非我方回合检测 ====================
    def handle_enemy_turn(self):
        """处理非我方回合"""
        # 0. 检测所有账号是否有zdzd弹窗，如果有则点击取消按钮（三个大漠对象都需要检测）
        for dm_index in [0, 1, 2]:
            dm = self.get_account_dm(dm_index)
            if not dm:
                continue
            
            # 检测zdzd图片
            zdzd_pos = self.find_image(dm_index, self.zdzd_image, self.zdzd_region, 0)
            if zdzd_pos:
                # 找到zdzd图片，点击取消按钮
                cancel_button_pos = self.find_image(
                    dm_index, self.button_images["取消按钮"], self.zdzd_region, 0
                )
                if cancel_button_pos:
                    self.click_position(dm_index, cancel_button_pos.x, cancel_button_pos.y)
                    self.report_battle_info(f"大漠对象{dm_index} 检测到zdzd弹窗，已点击取消", "warning")
                    time.sleep(0.5)  # 等待弹窗关闭
        
        # 等待一下，确保弹窗处理完成
        time.sleep(2)
        
        # 使用第一个大漠对象进行检测
        dm_index = 0
        dm = self.get_account_dm(dm_index)
        if not dm:
            return
        
        # 1. 检测需要清除状态的敌军（只检测传入的敌军单位 key）
        self.detect_enemies_need_clear(dm_index)
        
        # 4. 检测血量低的单位
        self.detect_low_hp_units(dm_index)
    
    def detect_enemies_need_clear(self, dm_index):
        """检测需要清除状态的敌军（只检测传入的敌军单位 key）"""
        # 只检测传入的敌军单位 key
        if not self.enemy_keys_to_detect:
            return
        
        self.state_map.enemies_need_clear = []
        for enemy_key in self.enemy_keys_to_detect:
            # 从配置中获取敌军信息
            if enemy_key not in self.enemy_general_config:
                self.report_battle_info(f"警告：敌军单位 '{enemy_key}' 不在配置中，跳过检测", "warning")
                continue
                
            config = self.enemy_general_config[enemy_key]
            status_region = config["status_region"]
            status_images = config["status_images"]
            cast_position = config["cast_position"]
            
            # 检测状态图片（针对性识别）
            for status_name, status_image in status_images.items():
                status_pos = self.find_image(dm_index, status_image, status_region, 0)
                if status_pos:
                    # 检查是否已记录（避免重复）
                    already_recorded = False
                    for enemy_info in self.state_map.enemies_need_clear:
                        if enemy_info["enemy_name"] == enemy_key:
                            already_recorded = True
                            break
                    
                    if not already_recorded:
                        self.state_map.enemies_need_clear.append({
                            "enemy_name": enemy_key,
                            "position": cast_position,
                            "status_name": status_name,
                        })
                        self.report_battle_info(f"检测到敌军{enemy_key}需要清除状态: {status_name}，固定点位: {cast_position}", "warning")
                        break

    def detect_low_hp_units(self, dm_index):
        """检测血量低的单位并记录点位"""
        # 血量低标识图片
        low_hp_image = f"{self.get_resource_path('serveAssets/images/auto/xueliangbuzu1.bmp')}|{self.get_resource_path('serveAssets/images/auto/xueliangbuzu2.bmp')}"
        
        # 血量条区域（需要根据实际游戏调整）
        hp_regions = [
            (775, 395, 862, 542),  # 账号0主角
            (520, 387, 658, 542),  # 账号0武将1
            (626, 387, 768, 542),  # 账号0武将2
            (749, 281, 836, 409),  # 账号1主角
            (520, 270, 634, 409),  # 账号1武将1
            (626, 270, 744, 409),  # 账号1武将2
            (708, 170, 830, 340),  # 账号2主角
            (530, 170, 616, 340),  # 账号2武将1
            (626, 170, 744, 340),  # 账号2武将2
        ]
        
        self.state_map.low_hp_units = []
        for region_idx, region in enumerate(hp_regions):
            low_hp_pos = self.find_image(dm_index, low_hp_image, region, 0)
            if low_hp_pos:
                # 确定是哪个账号的哪个单位
                account_idx = region_idx // 3
                unit_idx = region_idx % 3
                account = self.state_map.get_account(account_idx)
                
                if unit_idx == 0:
                    # 主角
                    if account.main_char.alive:
                        account.main_char.need_heal = True
                        self.state_map.low_hp_units.append({
                            "account_idx": account_idx,
                            "unit_type": "main_char",
                            "position": account.main_char.position or (764, 380),
                        })
                elif unit_idx == 1:
                    # 武将1（只检查实际存在的武将）
                    if account.general1.general_type is not None and account.general1.alive:
                        account.general1.need_heal = True
                        self.state_map.low_hp_units.append({
                            "account_idx": account_idx,
                            "unit_type": "general1",
                            "position": account.general1.position or (572, 380),
                        })
                elif unit_idx == 2:
                    # 武将2（只检查实际存在的武将）
                    if account.general2.general_type is not None and account.general2.alive:
                        account.general2.need_heal = True
                        self.state_map.low_hp_units.append({
                            "account_idx": account_idx,
                            "unit_type": "general2",
                            "position": account.general2.position or (667, 380),
                        })
    
    # ==================== 主循环 ====================
    def run_combat_loop(self):
        """运行战斗循环"""
        self.polling_running = True
        self.report_battle_info("战斗循环已启动", "system")
        
        while self.polling_running:
            try:
                # 检查是否在我方回合
                action_button_found = False
                for dm_index in [0, 1, 2]:
                    if self.wait_for_action_button(dm_index, timeout=0.5):
                        action_button_found = True
                        break
                
                if action_button_found:
                    # 我方回合
                    self.handle_our_turn()
                else:
                    # 非我方回合
                    self.handle_enemy_turn()
                    time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

            except KeyboardInterrupt:
                self.polling_running = False
                break
            except Exception as e:
                self.report_battle_info(f"战斗循环出错: {e}", "error")
                time.sleep(CombatConstants.DEFAULT_CHECK_INTERVAL)

        self.report_battle_info("战斗循环已结束", "system")
    
    def cleanup(self):
        """清理资源"""
        self.polling_running = False
        if self.battle_report_dialog:
            try:
                self.battle_report_dialog.close_safely()
            except:
                pass
            self.battle_report_dialog = None

