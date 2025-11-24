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


class GlobalStateMap:
    """全局状态Map"""
    def __init__(self):
        # 三个大漠对象，每个包含主角、武将1、武将2
        self.dm0 = AccountStatus()  # 第一个大漠对象
        self.dm1 = AccountStatus()  # 第二个大漠对象
        self.dm2 = AccountStatus()  # 第三个大漠对象
        self.dead_main_char_count = 0  # 死亡主角数量
        self.enemy_target_position = None  # 敌军攻击目标点位
        self.low_hp_units = []  # 血量低的单位列表
        self.enemies_need_clear = []  # 需要清除状态的敌军列表
    
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
    
    def __init__(self, thread_instance):
        self.thread = thread_instance
        self.battle_report_dialog = None
        self._state_lock = threading.Lock()
        self.polling_running = False
        self.polling_thread = None
        
        # 全局状态Map
        self.state_map = GlobalStateMap()
        self.is_first_turn = True  # 是否第一回合
        
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
        
        # 按钮图片
        self.button_images = {
            "技能按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),
            "召唤按钮": self.get_resource_path("serveAssets/images/auto/zhaohuan.bmp"),
            "道具按钮": self.get_resource_path("serveAssets/images/auto/yaopin.bmp"),
            "操作按钮": self.get_resource_path("serveAssets/images/auto/jineng.bmp"),
        }
        
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
        
        # 准备所有技能路径
        skill_paths = []
        skill_name_list = []
        for skill_name in skill_names:
            skill_path = self.skill_images.get(skill_name)
            if skill_path:
                skill_paths.append(skill_path)
                skill_name_list.append(skill_name)
        
        if not skill_paths:
            return None, None
        
        combined_path = "|".join(skill_paths)
        x, y, w, h = self.skill_panel_region
        
        while time.time() - start_time < timeout:
            for confidence in [0.9, 0.8, 0.7]:
                pos = dm.FindPicEx(int(x), int(y), int(w), int(h), combined_path, "", confidence, 0)
                if pos:
                    pos = pos.split("|")
                    pos_res = pos[0].split(",")
                    pic_index = int(pos_res[0])
                    if pic_index < len(skill_name_list):
                        found_skill = skill_name_list[pic_index]
                        pics = combined_path.split("|")
                        picSize = dm.GetPicSize(pics[pic_index])
                        picSize = picSize.split(",")
                        picW, picH = picSize[0], picSize[1]
                        posX = int(pos_res[1]) + (int(picW) * 0.5)
                        posY = int(pos_res[2]) + (int(picH) * 0.5)
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
                    # 攻击武将
                    if not account.general1.alive or account.general1.general_type is None:
                        account.general1.alive = True
                        account.general1.general_type = "attack"
                        account.general1.position = (572, 380)  # 默认位置
                        self.report_battle_info(f"大漠对象{dm_index} 识别到攻击武将1技能: {skill_name}", "success")
                    elif not account.general2.alive or account.general2.general_type is None:
                        account.general2.alive = True
                        account.general2.general_type = "attack"
                        account.general2.position = (667, 380)  # 默认位置
                        self.report_battle_info(f"大漠对象{dm_index} 识别到攻击武将2技能: {skill_name}", "success")
                else:
                    # 查找辅助武将技能
                    skill_name, skill_pos = self.find_skill_in_panel(dm_index, self.support_general_skills, timeout=2.0)
                    if skill_name:
                        # 辅助武将
                        if not account.general1.alive or account.general1.general_type is None:
                            account.general1.alive = True
                            account.general1.general_type = "support"
                            account.general1.position = (572, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将1技能: {skill_name}", "success")
                        elif not account.general2.alive or account.general2.general_type is None:
                            account.general2.alive = True
                            account.general2.general_type = "support"
                            account.general2.position = (667, 380)
                            self.report_battle_info(f"大漠对象{dm_index} 识别到辅助武将2技能: {skill_name}", "success")
        
        self.is_first_turn = False
        self.report_battle_info("第一回合初始化完成", "system")
    
    # ==================== 我方回合主流程 ====================
    def handle_our_turn(self):
        """处理我方回合"""
        self.report_battle_info("进入我方回合", "turn")
        
        # 第一回合初始化
        if self.is_first_turn:
            self.init_first_turn()
            # 初始化后需要等待攻击按钮再次出现
            time.sleep(0.5)
            for dm_index in [0, 1, 2]:
                self.wait_for_action_button(dm_index, timeout=3.0)
        
        # 主角操作阶段
        self.handle_main_char_phase()
        
        # 等待攻击按钮（3秒）
        time.sleep(0.5)
        for dm_index in [0, 1, 2]:
            self.wait_for_action_button(dm_index, timeout=3.0)
        
        # 武将操作阶段（循环两次）
        for round_num in [1, 2]:
            self.report_battle_info(f"武将操作阶段 - 第{round_num}轮", "info")
            self.handle_general_phase()
            if round_num == 1:
                time.sleep(0.5)
                for dm_index in [0, 1, 2]:
                    self.wait_for_action_button(dm_index, timeout=1.0)
        
        # 更新全局状态
        self.update_global_state()
        self.report_battle_info("我方回合结束", "turn")
    
    def handle_main_char_phase(self):
        """处理主角操作阶段"""
        for dm_index in [0, 1, 2]:
            dm = self.get_account_dm(dm_index)
            if not dm:
                continue
            
            account = self.state_map.get_account(dm_index)
            
            # 检查召唤按钮判断是主角
            if not self.check_summon_button(dm_index):
                continue
            
            # 1. 优先召唤武将（如果有武将死亡）
            if self.has_dead_general(account):
                if self.try_summon_general(dm_index, account):
                    # 召唤成功，等待一下让武将出现
                    time.sleep(1.0)
                    continue
            
            # 2. 检测主角阵亡数量
            if self.state_map.dead_main_char_count > 0:
                # 记录死亡数量，不需要记录具体单位
                pass
            
            # 3. 等待主角技能（2秒超时）
            skill_name, skill_pos = self.find_skill_in_panel(
                dm_index, self.main_char_skills, timeout=CombatConstants.MAIN_CHAR_SKILL_WAIT_TIMEOUT
            )
            
            if skill_name and skill_pos:
                # 识别到主角技能，说明主角存活
                if not account.main_char.alive:
                    # 如果之前是死亡状态，说明复活成功
                    account.main_char.alive = True
                    account.main_char.reviving = False
                    if self.state_map.dead_main_char_count > 0:
                        self.state_map.dead_main_char_count -= 1
                    self.report_battle_info(f"大漠对象{dm_index} 主角复活成功", "success")
                else:
                    account.main_char.alive = True
                    account.main_char.reviving = False
                
                # 释放技能
                target_pos = self.state_map.enemy_target_position or (104, 344)
                if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                    self.report_battle_info(f"大漠对象{dm_index} 主角释放{skill_name}", "action")
            else:
                # 未识别到主角技能
                if account.main_char.alive and not account.main_char.reviving:
                    # 之前存活且不在复活中，标记为死亡
                    account.main_char.alive = False
                    self.state_map.dead_main_char_count += 1
                    self.report_battle_info(f"大漠对象{dm_index} 主角未识别到技能，标记为死亡", "warning")
                elif account.main_char.reviving:
                    # 正在复活中但没识别到，保持reviving状态
                    pass
                
                # 如果没找到技能，进行加血操作（如果主角需要加血）
                if not skill_name and account.main_char.need_heal:
                    self.try_heal_main_char(dm_index, account)
                elif not skill_name and self.state_map.dead_main_char_count > 0:
                    # 如果主角没找到且没有识别到主角，直接使用其他存活单位进行复活
                    # 这个逻辑在下一轮会处理
                    pass
    
    def handle_general_phase(self):
        """处理武将操作阶段"""
        for dm_index in [0, 1, 2]:
            dm = self.get_account_dm(dm_index)
            if not dm:
                continue
            
            account = self.state_map.get_account(dm_index)
            
            # 检查召唤按钮判断是武将（没有召唤按钮）
            if self.check_summon_button(dm_index):
                continue
            
            # 1. 优先判断是否有需要复活的主角
            if self.state_map.dead_main_char_count > 0:
                # 分配复活任务（按优先级：主角、辅助武将、攻击武将）
                revive_assigned = self.assign_revive_task(account)
                if revive_assigned:
                    if self.try_revive_main_char(dm_index, account):
                        # 复活操作完成，标记主角为复活中
                        # 找到需要复活的主角账号（遍历所有账号找到死亡的）
                        for acc_idx in range(3):
                            acc = self.state_map.get_account(acc_idx)
                            if not acc.main_char.alive:
                                acc.main_char.reviving = True
                                break
                        continue
            
            # 2. 查找武将技能（3秒超时）
            # 先查找攻击武将技能
            skill_name, skill_pos = self.find_skill_in_panel(
                dm_index, self.attack_general_skills, timeout=CombatConstants.GENERAL_SKILL_WAIT_TIMEOUT
            )
            
            if skill_name and skill_pos:
                # 识别到攻击武将技能
                self.update_general_status(account, "attack", skill_name)
                target_pos = self.state_map.enemy_target_position or (104, 344)
                if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                    self.report_battle_info(f"大漠对象{dm_index} 攻击武将释放{skill_name}", "action")
                continue
            
            # 查找辅助武将技能
            skill_name, skill_pos = self.find_skill_in_panel(
                dm_index, self.support_general_skills, timeout=CombatConstants.GENERAL_SKILL_WAIT_TIMEOUT
            )
            
            if skill_name and skill_pos:
                # 识别到辅助武将技能
                self.update_general_status(account, "support", skill_name)
                
                # 辅助武将：判断是否需要清除状态
                if skill_name == "清除状态" and self.state_map.enemies_need_clear:
                    # 清除状态：对需要清除的敌军释放
                    enemy_info = self.state_map.enemies_need_clear[0]  # 取第一个
                    target_pos = enemy_info["position"]
                    if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                        self.liubei_skill_index[dm_index] = (self.liubei_skill_index.get(dm_index, 0) + 1) % len(self.liubei_skill_sequence)
                        self.report_battle_info(f"大漠对象{dm_index} 辅助武将释放{skill_name}清除{enemy_info['enemy_name']}状态", "action")
                        # 移除已清除的敌军
                        self.state_map.enemies_need_clear.pop(0)
                    continue
                
                # 按技能顺序释放
                self.release_support_skill(dm_index, account, skill_name, skill_pos)
            else:
                # 未识别到武将技能，标记为死亡
                self.mark_general_dead(account)
    
    def has_dead_general(self, account):
        """检查是否有武将死亡"""
        return not account.general1.alive or not account.general2.alive
    
    def try_summon_general(self, dm_index, account):
        """尝试召唤武将"""
        # 召唤顺序：刘备（如果不存在辅助武将）→ 曹操 → 魔关
        has_support = False
        for gen in [account.general1, account.general2]:
            if gen.alive and gen.general_type == "support":
                has_support = True
                break
        
        general_order = ["刘备", "曹操", "魔化关羽"] if not has_support else ["曹操", "魔化关羽"]
        
        for general_name in general_order:
            if self.summon_general(dm_index, general_name):
                # 更新武将状态为复活中
                if not account.general1.alive or account.general1.general_type is None:
                    account.general1.reviving = True
                    account.general1.position = (572, 380)  # 默认位置
                    # 根据武将名称确定类型
                    if general_name == "刘备":
                        account.general1.general_type = "support"
                    else:
                        account.general1.general_type = "attack"
                elif not account.general2.alive or account.general2.general_type is None:
                    account.general2.reviving = True
                    account.general2.position = (667, 380)  # 默认位置
                    # 根据武将名称确定类型
                    if general_name == "刘备":
                        account.general2.general_type = "support"
                    else:
                        account.general2.general_type = "attack"
                return True
        return False
    
    def summon_general(self, dm_index, general_name):
        """召唤武将"""
        # 点击召唤按钮
        summon_btn = self.find_image(dm_index, self.button_images["召唤按钮"], self.right_button_region, 0)
        if not summon_btn:
            return False
        
        self.click_position(dm_index, summon_btn.x, summon_btn.y)
        time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)
        
        # 查找武将图片
        general_path = self.bag_general_images.get(general_name)
        if not general_path:
            return False
        
        general_pos = self.find_image(dm_index, general_path, self.summon_panel_region, 0)
        if general_pos:
            self.click_position(dm_index, general_pos.x, general_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"大漠对象{dm_index} 召唤{general_name}成功", "action")
            return True
        return False
    
    def assign_revive_task(self, account):
        """分配复活任务（按优先级：主角、辅助武将、攻击武将）"""
        if self.state_map.dead_main_char_count <= 0:
            return False
        
        # 检查是否已经分配过复活任务（全局检查，避免重复分配）
        # 遍历所有账号，检查是否已经有单位被分配了复活任务
        already_assigned = False
        for acc in self.state_map.get_all_accounts():
            if (acc.main_char.revive_assigned or 
                acc.general1.revive_assigned or 
                acc.general2.revive_assigned):
                already_assigned = True
                break
        
        if already_assigned:
            return False
        
        # 按优先级分配：主角 > 辅助武将 > 攻击武将
        if account.main_char.alive and not account.main_char.revive_assigned:
            account.main_char.revive_assigned = True
            return True
        elif account.general1.alive and account.general1.general_type == "support" and not account.general1.revive_assigned:
            account.general1.revive_assigned = True
            return True
        elif account.general2.alive and account.general2.general_type == "support" and not account.general2.revive_assigned:
            account.general2.revive_assigned = True
            return True
        elif account.general1.alive and account.general1.general_type == "attack" and not account.general1.revive_assigned:
            account.general1.revive_assigned = True
            return True
        elif account.general2.alive and account.general2.general_type == "attack" and not account.general2.revive_assigned:
            account.general2.revive_assigned = True
            return True
        
        return False
    
    def try_revive_main_char(self, dm_index, account):
        """尝试复活主角"""
        if self.state_map.dead_main_char_count <= 0:
            return False
        
        # 使用复活药
        item_btn = self.find_image(dm_index, self.button_images["道具按钮"], self.right_button_region, 0)
        if not item_btn:
            return False
        
        self.click_position(dm_index, item_btn.x, item_btn.y)
        time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)
        
        # 查找复活药
        revive_path = self.item_images.get("复活药")
        if not revive_path:
            return False
        
        revive_pos = self.find_image(dm_index, revive_path, self.item_panel_region, 0)
        if not revive_pos:
            return False
        
        self.click_position(dm_index, revive_pos.x, revive_pos.y)
        time.sleep(CombatConstants.ACTION_DELAY)
        
        # 使用选择目标文字找对应的单位复活（记录区域避免重复）
        # 需要根据实际游戏中的文字来查找，这里使用多个可能的文字
        target_texts = ["主角", "主", "角色"]  # 根据实际游戏文字调整
        target_pos = None
        for text in target_texts:
            target_pos = self.find_text(dm_index, text, self.ally_region, 0)
            if target_pos:
                break
        
        if target_pos:
            self.click_position(dm_index, target_pos.x, target_pos.y)
            time.sleep(CombatConstants.ACTION_DELAY)
            # 不在这里减dead_main_char_count，等下一回合识别到主角技能时再减
            self.report_battle_info(f"大漠对象{dm_index} 使用复活药复活主角", "action")
            return True
        else:
            # 如果找不到文字，使用默认位置
            default_pos = (764, 380)  # 默认主角位置
            self.click_position(dm_index, default_pos[0], default_pos[1])
            time.sleep(CombatConstants.ACTION_DELAY)
            self.report_battle_info(f"大漠对象{dm_index} 使用复活药复活主角（使用默认位置）", "action")
            return True
    
    def update_general_status(self, account, general_type, skill_name):
        """更新武将状态"""
        # 如果识别到武将技能，说明武将存活
        for gen in [account.general1, account.general2]:
            if gen.general_type == general_type:
                if not gen.alive or gen.reviving:
                    # 如果之前是死亡或正在复活中，说明复活成功
                    gen.alive = True
                    gen.reviving = False
                    gen.general_type = general_type
                    self.report_battle_info(f"{general_type}武将复活成功", "success")
                else:
                    gen.alive = True
                    gen.reviving = False
                break
            elif gen.reviving:
                # 如果正在复活中，更新类型
                gen.alive = True
                gen.reviving = False
                gen.general_type = general_type
                break
    
    def mark_general_dead(self, account):
        """标记武将死亡"""
        for gen in [account.general1, account.general2]:
            if gen.alive and not gen.reviving:
                gen.alive = False
                gen.revive_assigned = None  # 清除复活任务分配
                self.report_battle_info("武将未识别到技能，标记为死亡", "warning")
                break
            elif gen.reviving:
                # 正在复活中但没识别到，保持reviving状态
                pass
    
    def release_support_skill(self, dm_index, account, skill_name, skill_pos):
        """释放辅助技能"""
        # 获取当前技能索引
        if dm_index not in self.liubei_skill_index:
            self.liubei_skill_index[dm_index] = 0
        
        current_index = self.liubei_skill_index[dm_index]
        expected_skill = self.liubei_skill_sequence[current_index % len(self.liubei_skill_sequence)]
        
        if skill_name == expected_skill:
            # 选择目标
            if skill_name in ["加攻击", "加血"]:
                # 选择存活的我方单位
                target_pos = self.select_alive_ally(dm_index)
            else:
                # 攻击技能，使用敌军目标
                target_pos = self.state_map.enemy_target_position or (104, 344)
            
            if self.release_skill(dm_index, skill_name, skill_pos, target_pos):
                self.liubei_skill_index[dm_index] = (current_index + 1) % len(self.liubei_skill_sequence)
                self.report_battle_info(f"大漠对象{dm_index} 辅助武将释放{skill_name}", "action")
    
    def select_alive_ally(self, dm_index):
        """选择存活的友军单位"""
        # 收集所有存活单位位置
        ally_positions = []
        for account in self.state_map.get_all_accounts():
            if account.main_char.alive and account.main_char.position:
                ally_positions.append(account.main_char.position)
            for gen in [account.general1, account.general2]:
                if gen.alive and gen.position:
                    ally_positions.append(gen.position)
        
        if ally_positions:
            return random.choice(ally_positions)
        return (764, 380)  # 默认位置
    
    def try_heal_main_char(self, dm_index, account):
        """尝试给主角加血"""
        if not account.main_char.need_heal:
            return False
        
        # 使用恢复药
        item_btn = self.find_image(dm_index, self.button_images["道具按钮"], self.right_button_region, 0)
        if not item_btn:
            return False
        
        self.click_position(dm_index, item_btn.x, item_btn.y)
        time.sleep(CombatConstants.PANEL_WAIT_TIMEOUT)
        
        # 查找恢复药
        heal_path = self.item_images.get("恢复药")
        if not heal_path:
            return False
        
        heal_pos = self.find_image(dm_index, heal_path, self.item_panel_region, 0)
        if not heal_pos:
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
            account.general1.need_heal = False
            account.general2.need_heal = False
            
            # 清除复活任务分配（下一回合重新分配）
            account.main_char.revive_assigned = None
            account.general1.revive_assigned = None
            account.general2.revive_assigned = None
            
            # 如果武将正在复活中，且下一回合识别到了，状态已在handle_general_phase中更新
            # 如果下一回合没识别到，保持reviving状态
            
        # 回合结束，进行全局状态更新
        self.report_battle_info("全局状态已更新", "system")
    
    # ==================== 非我方回合检测 ====================
    def handle_enemy_turn(self):
        """处理非我方回合"""
        # 使用第一个大漠对象进行检测
        dm_index = 0
        dm = self.get_account_dm(dm_index)
        if not dm:
            return
        
        # 1. 确定攻击单位（直接确定，不需要一个一个找）
        target_pos = self.find_image(dm_index, self.target_lantiao_image, self.enemy_region, 0)
        if target_pos:
            self.state_map.enemy_target_position = (target_pos.x, target_pos.y)
        
        # 2. 检测需要清除状态的敌军
        self.detect_enemies_need_clear(dm_index)
        
        # 3. 检测血量低的单位
        self.detect_low_hp_units(dm_index)
    
    def detect_enemies_need_clear(self, dm_index):
        """检测需要清除状态的敌军（针对性识别）"""
        # 敌军武将配置（可根据需要添加）
        enemy_configs = {
            "赵云29": {
                "status_images": {
                    "状态1": self.get_resource_path("serveAssets/images/auto/longdan1.bmp"),
                },
                "status_region": (54, 168, 280, 541),
                "cast_position": (115, 446),
            },
            # 可以添加更多敌军配置
        }
        
        self.state_map.enemies_need_clear = []
        for enemy_name, config in enemy_configs.items():
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
                        if enemy_info["enemy_name"] == enemy_name:
                            already_recorded = True
                            break
                    
                    if not already_recorded:
                        self.state_map.enemies_need_clear.append({
                            "enemy_name": enemy_name,
                            "position": cast_position,
                            "status_name": status_name,
                        })
                        self.report_battle_info(f"检测到敌军{enemy_name}需要清除状态: {status_name}", "warning")
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
                    # 武将1
                    if account.general1.alive:
                        account.general1.need_heal = True
                        self.state_map.low_hp_units.append({
                            "account_idx": account_idx,
                            "unit_type": "general1",
                            "position": account.general1.position or (572, 380),
                        })
                elif unit_idx == 2:
                    # 武将2
                    if account.general2.alive:
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

