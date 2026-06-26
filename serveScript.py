# 大漠插件
import random
import time
import keyboard
import threading
import wx
import wx.lib.scrolledpanel as scrolled
import psutil
import ctypes
import gc
from comtypes.client import CreateObject
import subprocess
from comtypes import CoInitialize
from datetime import datetime
from datetime import timedelta
import pyttsx3
import uuid
import requests
import json
import os
import sys
from collections import OrderedDict


def _get_ca_bundle():
    try:
        import certifi
        if getattr(sys, 'frozen', False):
            bundled = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
            if os.path.exists(bundled):
                return bundled
        return certifi.where()
    except Exception:
        return True


# 导入战斗自动操作脚本``
from Kanloong_combat_script import CombatAutoScript
# e:/project/python/.venv32/Scripts/pyinstaller.exe serveScript.spec
# 打包命令：pyinstaller -F -w --add-data "serveAssets;serveAssets" --add-data "user_scripts;user_scripts" --hidden-import Kanloong_combat_script --hidden-import ScriptEngine --hidden-import ScriptFactory --icon=serveAssets\images\script.ico .\serveScript.py
# pyinstaller serveScript.spec
condition = threading.Condition()

# Windows API 常量
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_SYSTEM = 0x4
FILE_ATTRIBUTE_READONLY = 0x1


def hide_temp_directory():
    """隐藏临时解压目录（PyInstaller打包后的_MEIPASS目录）"""
    try:
        if hasattr(sys, "_MEIPASS"):
            temp_dir = sys._MEIPASS
            # 使用 Windows API 设置目录为隐藏和系统属性
            kernel32 = ctypes.windll.kernel32
            # 将路径转换为宽字符串（Unicode）
            if isinstance(temp_dir, str):
                temp_dir_unicode = temp_dir
            else:
                temp_dir_unicode = str(temp_dir)

            # 设置文件属性：隐藏 + 系统
            # 注意：需要管理员权限才能设置系统属性
            try:
                # 尝试设置隐藏属性（不需要管理员权限）
                kernel32.SetFileAttributesW(temp_dir_unicode,
                                            FILE_ATTRIBUTE_HIDDEN)
            except:
                pass  # 如果失败，静默处理

            # 也隐藏父目录（如果存在）
            try:
                parent_dir = os.path.dirname(temp_dir)
                if parent_dir and os.path.exists(parent_dir):
                    # 只设置隐藏属性，不设置系统属性（避免权限问题）
                    kernel32.SetFileAttributesW(parent_dir,
                                                FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
    except Exception:
        pass  # 静默处理所有错误，避免影响程序启动


# 程序启动时自动隐藏临时目录
hide_temp_directory()

class ResXy:
    def __init__(resInit, x, y):
        resInit.x = x
        resInit.y = y

class MyThread(threading.Thread):
    def __init__(self, scriptName, userData):
        super().__init__()
        self.userData = userData
        self.riChangList = [
            {"name": "战", "count": 6, "time": 25},
            {"name": "镇", "count": 6, "time": 10},
            {"name": "噬", "count": 6, "time": 15},
            {"name": "帮", "count": 1, "time": 15},
            {"name": "英", "count": 7, "time": 10},
            {"name": "红", "count": 7, "time": 10},
            {"name": "渊", "count": 6, "time": 10},
            {"name": "溶", "count": 1, "time": 10},
            {"name": "庐", "count": 5, "time": 6},
            {"name": "八", "count": 1, "time": 5},
            {"name": "鼠", "count": 1, "time": 5},
            {"name": "官", "count": 1, "time": 4},
            {"name": "云", "count": 1, "time": 4},
            {"name": "名", "count": 8, "time": 4},
            {"name": "丹", "count": 5, "time": 4},
            {"name": "五", "count": 3, "time": 3},
            {"name": "四", "count": 35, "time": 10},
        ]
        self.riChang49List = [
            {"name": "战", "count": 6, "time": 25},
            {"name": "镇", "count": 6, "time": 10},
            {"name": "噬", "count": 6, "time": 15},
            {"name": "红", "count": 7, "time": 10},
            {"name": "帮", "count": 1, "time": 15},
            {"name": "渊", "count": 6, "time": 10},
            {"name": "溶", "count": 1, "time": 10},
            {"name": "名", "count": 8, "time": 4},
            {"name": "丹", "count": 5, "time": 4},
            {"name": "五", "count": 3, "time": 3},
            {"name": "四", "count": 35, "time": 10},
        ]
        self.zdList = None
        self.zd49List = None
        try:
            self.dm = CreateObject("dm.dmsoft")
        except:
            regPath = self.get_resource_path("serveAssets/plugins/RegDll.dll")
            dms = ctypes.windll.LoadLibrary(str(regPath))
            dmPath = self.get_resource_path("serveAssets/plugins/dm.dll")
            # 构建 regsvr32 命令，添加 /s 参数以静默运行
            command = ["regsvr32", "/s", dmPath]
            # 执行命令
            subprocess.run(command, check=True, capture_output=True, text=True)
            dms.DllRegisterServer(dmPath, 0)
            self.dm = CreateObject("dm.dmsoft")
        self.win1_dm = None
        self.win2_dm = None
        self.hasRefresh = False
        self.guajiFlag = False
        self.guajiFlag1 = False
        self.guajiFlag2 = False
        self.huifuFlag = False
        self._huifu_done = 0
        self.frame = None
        self.line = "二线"
        self.zhanhunFloor = ""
        self.lianyu_count = 21
        self.zhanhun_count = 21
        self.qingyuan_count = 21
        self.rongdong_count = 2
        self.liandan_count = 3
        self.wuxing_count = 2
        self.yinhun_count = 4
        self.sangumaolu_count = 3
        self.hong_count = 4
        self.yunyou_count = 1
        self.bamen_count = 1
        self.laoshu_count = 1
        self.guandujy_count = 1
        self.bangpai_enabled = True
        self.mingjiang_count = 8
        self.richang_zhengdian = False
        self.richang_mojing = False
        self.zhanhunFloorNew = ""
        self.heifengFloor = ""
        self.guajiLocation = None
        # 创建子线程
        self.child_thread = threading.Thread(target=self.child_task, daemon=True)
        self.win1_thread = threading.Thread(target=self.find_and_bing_windows1, daemon=True)
        self.win2_thread = threading.Thread(target=self.find_and_bing_windows2, daemon=True)
        self.guanDuCount = 0
        self.invalid_xiaolvren_dots = {}
        self.hasZhengDianCount = 0
        self.daZhengDianCount = 0
        self.mojingFloor = ""
        self.zhengdianFloor = ""
        self.shihun_count = 21
        self.shihun_floor = ""
        self.sixiang_count = 21
        self.sixiang_difficulty = ""
        self.richangFlag = ""
        self.after_zreo = ""
        self._zhengdian_early_waited = False
        self.teammate1_name = ""
        self.teammate2_name = ""
        self.teammate1_pos = ""
        self.teammate2_pos = ""
        self.team_leader_pos = ""
        self.teamFlag = False
        self.scriptName = scriptName
        self.confidenceNum = 0.9
        self.righttop1 = None
        self.leftbottom = None
        self.locationX = None
        self.locationY = None
        self.locationWidth = None
        self.locationHeight = None
        self.locationRightTopX = None
        self.locationRightTopY = None
        self.locationRightTopWidth = None
        self.locationRightTopHeight = None
        self.upTalkLocation = None
        self.downTalkLocation = None
        self.clickFlag = False
        self.addBloudFlag = False
        self.combat_auto_scenes = []
        self.liubeiCounts = {0: 1, 1: 0, 2: 0}
        self.use_heal_item = False
        self.independent_win1 = False
        self.independent_win2 = False
        self.stoped = False
        self.zdzdPath = self.get_resource_path("serveAssets/images/zdzd.bmp")
        self.BisClick = False
        self.clickBTime = 0
        self.clickBX = 0
        self.clickBy = 0
        self.shengxiaoLocation = None
        self.mojingCount = 0
        self.gameLocation = None
        self.gameLeftLocation = None
        self.gameRightLocation = None
        self.gameRightFullLocation = None
        self.gameBottomLocation = None
        self.dituLocation = None
        self.dituLeftLocation = None
        self.dituRightLocation = None
        self.dituCenterLocation = None
        self.talkLocation = None
        self.heifengCount = 0
        self.heifengWhileCount = 0
        self.richangSelection = []
        self.click_hwnd = 0
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.zhengdianFb = ["官渡", "魔镜", "黑风","龙珠","龙岛", "战魂+红+整点",
                            "战魂+红+魔镜+整点"]
        self.hundianFlag = False
        self.win1_hwnd = 0
        self.win2_hwnd = 0
        self.zhengdian_flag = False
        self.clearMapFlag = False
        self.mac_address = ""
        self.mac_address1 = ""
        self.has_script = None
        self.user_name = ""
        self.end_time = ""
        self.overed = False
        self.refreshFlag = False
        self.yaoqingFlag = False
        self.team_loc = (300, 310, 365, 350)
        self.team1_loc = (410, 310, 490, 350)
        self.team2_loc = (530, 310, 610, 350)
        # 战斗自动操作相关变量
        self.combat_auto_instance = None
        self.combat_auto_thread = None
        self.combat_auto_running = False
        # 副本统计：四象/噬魂 的成功、失败、已打、总次数
        self.sixiang_stats = {"win": 0, "fail": 0, "done": 0, "total": 0}
        self.shihun_stats = {"win": 0, "fail": 0, "done": 0, "total": 0}
        self.combat_loop_thread = None  # 循环战斗线程
        self.click_delay = 0.5  # 点击延迟（秒）
        # 初始化 pyttsx3 引擎
        self.engine = pyttsx3.init()
        # 获取可用声音列表
        voices = self.engine.getProperty("voices")

        # 打印所有可用声音及其索引
        # for index, voice in enumerate(voices):
        # 	print(f"Voice {index}: {voice.name} ({voice.id})")

        # 选择一个声音（例如，选择第一个声音）
        selected_voice_index = 0  # 你可以根据需要更改这个索引
        if 0 <= selected_voice_index < len(voices):
            self.engine.setProperty("voice", voices[selected_voice_index].id)
        else:
            print("Selected voice index is out of range.")

    def _update_dungeon_stats(self, dungeon, result):
        """更新副本统计并刷新UI
        :param dungeon: "四象" 或 "噬魂"
        :param result: "win" 或 "fail"
        """
        try:
            stats = self.sixiang_stats if dungeon == "四象" else self.shihun_stats
            stats[result] += 1
            stats["done"] += 1
            if self.frame and hasattr(self.frame, "_refresh_dungeon_stats"):
                wx.CallAfter(self.frame._refresh_dungeon_stats)
        except Exception:
            pass

    def _start_combat_auto(self, clear_enemy_keys=None, combat_scene=None):
        try:
            if self.combat_auto_running:
                return
            if self.frame.has_script == "free" and datetime.now() > datetime(2026, 9, 30):
                return
            _heal_on = self.frame.use_heal_item if hasattr(self.frame, 'use_heal_item') else False
            self.combat_auto_running = True

            if not self.combat_auto_instance:
                self.combat_auto_instance = CombatAutoScript(self, clear_enemy_keys)
                self.combat_auto_instance.keep_support_general = False
                self.combat_auto_instance.enable_main_heal = _heal_on
                self.combat_auto_instance.enable_main_summon = True
                self.combat_auto_instance.liubei_counts = self.frame.liubeiCounts if hasattr(self.frame, 'liubeiCounts') else {0: 1, 1: 0, 2: 0}
                if combat_scene is not None:
                    self.combat_auto_instance.combat_scene = combat_scene
            else:
                self.combat_auto_instance.reconfigure(
                    enemy_keys_to_detect=clear_enemy_keys,
                    liubei_counts=self.frame.liubeiCounts if hasattr(self.frame, 'liubeiCounts') else {0: 1, 1: 0, 2: 0},
                    enable_main_heal=_heal_on,
                    combat_scene=combat_scene,
                )

            if self.combat_auto_instance.battle_report_dialog:
                self.combat_auto_instance.battle_report_dialog.set_running(True)

            self.combat_auto_thread = threading.Thread(
                target=self.combat_auto_instance.run_combat_loop, daemon=True)
            self.combat_auto_thread.start()

        except Exception as e:
            print(f"启动战斗自动操作失败")
            import traceback
            traceback.print_exc()
            self.combat_auto_running = False

    def _stop_combat_auto(self):
        try:
            if not self.combat_auto_running:
                return
            self.combat_auto_running = False

            if self.combat_auto_instance:
                self.combat_auto_instance.polling_running = False
                if self.combat_auto_instance.battle_report_dialog:
                    self.combat_auto_instance.battle_report_dialog.set_running(False)

            if self.combat_auto_thread and self.combat_auto_thread.is_alive():
                self.combat_auto_thread.join(timeout=5)
            self.combat_auto_thread = None

            if self.combat_auto_instance:
                try:
                    self.combat_auto_instance.reset_state()
                except Exception as e:
                    print(f"重置战斗脚本状态时出错: {e}")

        except Exception as e:
            print(f"停止战斗自动操作失败")
            import traceback
            traceback.print_exc()

    def print_and_speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def check_stop_or_over(self):
        """检查是否停止或结束，精简的检查方法"""
        with condition:
            if self.overed:
                return True
            # 如果暂停，循环等待直到继续或结束
            while self.stoped:
                condition.wait()
                if self.overed:
                    return True
        return self.overed

    def run(self):
        # self.mac_address = self.get_mac_address()
        # self.mac_address1 = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])
        # is_pass = self.is_user_valid()
        # if not is_pass:
        # 	self.show_error_message('未注册用户，请联系管理员注册!')
        # 	return
        # print(f'{self.user_name}，你的脚本有效期为{self.end_time},能使用的脚本有：{self.has_script}')
        # if self.is_virtual_machine() and self.user_name not in ['关服就离开', 'RInoicc']:
        # 	print('虚拟机')
        # 	return False
        self.mac_address = self.frame.mac_address
        self.line = self.frame.choice_line
        self.mac_address1 = self.frame.mac_address1
        self.has_script = self.frame.has_script
        self.user_name = self.frame.user_name
        self.end_time = self.frame.end_time
        self.zhanhunFloor = self.frame.zhanhunFloor
        self.lianyu_count = int(
            self.frame.lianyu_count) if self.frame.lianyu_count else 21
        self.qingyuan_count = int(
            self.frame.qingyuan_count) if self.frame.qingyuan_count else 21
        self.zhanhun_count = int(
            self.frame.zhanhun_count) if self.frame.zhanhun_count else 21
        self.zhanhunFloorNew = self.frame.zhanhunFloorNew
        self.mojingFloor = self.frame.mojingFloor
        self.combat_auto_scenes = self.frame.combat_auto_scenes if hasattr(self.frame, 'combat_auto_scenes') else []
        self.teammate1_name = self.frame.teammate1_name
        self.teammate2_name = self.frame.teammate2_name
        self.zhengdianFloor = self.frame.zhengdianFloor
        self.shihun_floor = self.frame.shihun_floor
        self.zhanhun_start_floor = self.frame.zhanhun_start_floor if hasattr(self.frame, 'zhanhun_start_floor') else "1层"
        self.shihun_count = int(
            self.frame.shihun_count) if self.frame.shihun_count else 21
        self.sixiang_count = int(
            self.frame.sixiang_count) if self.frame.sixiang_count else 21
        self.sixiang_difficulty = self.frame.sixiang_difficulty if self.frame.sixiang_difficulty else "普通"
        self.rongdong_count = int(
            self.frame.rongdong_count) if self.frame.rongdong_count else 2
        self.liandan_count = int(
            self.frame.liandan_count) if self.frame.liandan_count else 3
        self.wuxing_count = int(
            self.frame.wuxing_count) if self.frame.wuxing_count else 2
        self.yinhun_count = int(
            self.frame.yinhun_count) if self.frame.yinhun_count else 4
        self.sangumaolu_count = int(
            self.frame.sangumaolu_count) if self.frame.sangumaolu_count else 3
        self.hong_count = int(
            self.frame.hong_count) if self.frame.hong_count else 4
        self.yunyou_count = int(
            self.frame.yunyou_count) if self.frame.yunyou_count else 1
        self.bamen_count = int(
            self.frame.bamen_count) if self.frame.bamen_count else 1
        self.laoshu_count = int(
            self.frame.laoshu_count) if self.frame.laoshu_count else 1
        self.guandujy_count = int(
            self.frame.guandujy_count) if self.frame.guandujy_count else 1
        self.bangpai_enabled = self.frame.bangpai_enabled if hasattr(self.frame, 'bangpai_enabled') else True
        self.mingjiang_count = int(
            self.frame.mingjiang_count) if self.frame.mingjiang_count else 8
        self.richang_zhengdian = self.frame.richang_zhengdian if hasattr(self.frame, 'richang_zhengdian') else False
        self.richang_mojing = self.frame.richang_mojing if hasattr(self.frame, 'richang_mojing') else False
        self.heifengFloor = self.frame.heifengFloor
        self.teammate1_pos = self.frame.teammate1_pos
        self.teammate2_pos = self.frame.teammate2_pos
        self.team_leader_pos = self.frame.team_leader_pos
        self.after_zreo = self.frame.afterZreo
        self.richangSelection = self.frame.richangSelection
        self.liubeiCounts = self.frame.liubeiCounts if hasattr(self.frame, "liubeiCounts") else {0: 1, 1: 0, 2: 0}
        self.independent_win1 = self.frame.independent_win1 if hasattr(self.frame, "independent_win1") else False
        self.independent_win2 = self.frame.independent_win2 if hasattr(self.frame, "independent_win2") else False
        self.heifengWhileCount = int(
            self.frame.heifengCount) if self.frame.heifengCount else 0
        # display = Display(visible=False, size=(1920, 1080))
        # display.start()
        isFindGame = self.findGame()
        if not isFindGame:
            return
        if not self.hasRefresh:
            self.child_thread.start()
            self.win1_thread.start()
            self.win2_thread.start()
        self.zdList = [
            {
                "ditu": "地图老虎",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "findAddress": "九黎族祭坛",
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图牛",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "findAddress": "魔魂山",
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图羊",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "findAddress": "魔谷西",
                "delX": [int(856 + self.locationX), int(857 + self.locationX)],
                "delY": [int(46 + self.locationY)],
            },
            {
                "ditu": "地图新野",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/sangumaolu/xinye.bmp"),
                "delX": [
                    int(812 + self.locationX),
                    int(768 + self.locationX),
                    int(841 + self.locationX),
                ],
                "delY": [
                    int(43 + self.locationY),
                    int(51 + self.locationY),
                    int(54 + self.locationY),
                ],
            },
            {
                "ditu": "地图徐州",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "findAddress": "徐州",
                "delX": [int(844 + self.locationX)],
                "delY": [int(49 + self.locationY)],
            },
            {
                "ditu": "地图碧波潭",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": "碧波潭",
                "delX": [int(735 + self.locationX)],
                "delY": [int(58 + self.locationY)],
            },
            {
                "ditu": "地图皇宫东院",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": "皇宫东院",
                "delX": [int(848 + self.locationX)],
                "delY": [int(49 + self.locationY)],
            },
            {
                "ditu": "地图乱葬岗",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/luanzanggang.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图落日峰",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/luorifeng.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图荒村",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/huangcun.bmp"),
                "delX": [int(744 + self.locationX), int(816 + self.locationX)],
                "delY": [int(52 + self.locationY)],
            },
            {
                "ditu": "地图明镜湖",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/mingjinghu.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图恶龙洞",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/elongdong.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图祭坛",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/jitan1.bmp"),
                "delX": [int(819 + self.locationX)],
                "delY": [int(51 + self.locationY)],
            },
            {
                "ditu": "地图山洞三层",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/shandongsanceng.bmp"),
                "delX": [],
                "delY": [],
            },
        ]
        self.zd49List = [
            {
                "ditu": "地图碧波潭",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": "碧波潭",
                "delX": [int(735 + self.locationX)],
                "delY": [int(58 + self.locationY)],
            },
            {
                "ditu": "地图皇宫东院",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": "皇宫东院",
                "delX": [int(848 + self.locationX)],
                "delY": [int(49 + self.locationY)],
            },
            {
                "ditu": "地图乱葬岗",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/luanzanggang.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图落日峰",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/luorifeng.bmp"),
                "delX": [],
                "delY": [],
            },
            {
                "ditu": "地图荒村",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/huangcun.bmp"),
                "delX": [int(744 + self.locationX), int(816 + self.locationX)],
                "delY": [int(52 + self.locationY)],
            },
            {
                "ditu": "地图恶龙洞",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/elongdong.bmp"),
                "delX": [],
                "delY": [],
            },
            # 有一个npc
            {
                "ditu": "地图祭坛",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/jitan1.bmp"),
                "delX": [int(819 + self.locationX)],
                "delY": [int(51 + self.locationY)],
            },
            {
                "ditu": "地图山洞三层",
                "city": self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "findAddress": self.get_resource_path(
                    "serveAssets/images/zhengdian/shandongsanceng.bmp"),
                "delX": [],
                "delY": [],
            },
        ]
        self.normal_zd_groups = {
            "虎生肖红": [
                "serveAssets/images/zhengdian/hu-head-1.bmp",
                "serveAssets/images/zhengdian/hu-head-2.bmp",
                "serveAssets/images/zhengdian/hu-body-1.bmp",
                "serveAssets/images/zhengdian/hu-body-2.bmp",
                "serveAssets/images/zhengdian/hu-foot-1.bmp",
            ],
            "牛生肖": [
                "serveAssets/images/zhengdian/niu-head-1.bmp",
                "serveAssets/images/zhengdian/niu-head-2.bmp",
                "serveAssets/images/zhengdian/niu-body-1.bmp",
                "serveAssets/images/zhengdian/niu-body-2.bmp",
                "serveAssets/images/zhengdian/niu-foot-1.bmp",
            ],
            "兔子": [
                "serveAssets/images/zhengdian/tu-head-1.bmp",
                "serveAssets/images/zhengdian/tu-head-2.bmp",
                "serveAssets/images/zhengdian/tu-body-1.bmp",
                "serveAssets/images/zhengdian/tu-body-2.bmp",
                "serveAssets/images/zhengdian/tu-foot-1.bmp",
            ],
            "猴生肖红": [
                "serveAssets/images/zhengdian/hou-head-1.bmp",
                "serveAssets/images/zhengdian/hou-head-2.bmp",
                "serveAssets/images/zhengdian/hou-body-1.bmp",
                "serveAssets/images/zhengdian/hou-body-2.bmp",
                "serveAssets/images/zhengdian/hou-foot-1.bmp",
            ],
            "羊生肖新": [
                "serveAssets/images/zhengdian/yang-head-1.bmp",
                "serveAssets/images/zhengdian/yang-head-2.bmp",
                "serveAssets/images/zhengdian/yang-body-1.bmp",
                "serveAssets/images/zhengdian/yang-body-2.bmp",
                "serveAssets/images/zhengdian/yang-foot-1.bmp",
            ],
            "火焰帝红": [
                "serveAssets/images/zhengdian/huoyan-head-1.bmp",
                "serveAssets/images/zhengdian/huoyan-head-2.bmp",
                "serveAssets/images/zhengdian/huoyan-body-1.bmp",
                "serveAssets/images/zhengdian/huoyan-body-2.bmp",
            ],
            "寒冰帝": [
                "serveAssets/images/zhengdian/hanbin-head-1.bmp",
                "serveAssets/images/zhengdian/hanbin-head-2.bmp",
                "serveAssets/images/zhengdian/hanbin-body-1.bmp",
                "serveAssets/images/zhengdian/hanbin-body-2.bmp",
                "serveAssets/images/zhengdian/hanbin-foot-1.bmp",
                "serveAssets/images/zhengdian/hanbin-foot-2.bmp",
            ],
        }
        self.normal_zd_groups_no_boss = {
            k: v for k, v in self.normal_zd_groups.items()
            if k not in ("火焰帝红", "寒冰帝")
        }
        self.she_groups = {
            "蛇生肖": [
                "serveAssets/images/zhengdian/sheshengxiao1.bmp",
                "serveAssets/images/zhengdian/sheshengxiao2.bmp",
                "serveAssets/images/zhengdian/she-head-1.bmp",
                "serveAssets/images/zhengdian/she-head-2.bmp",
                "serveAssets/images/zhengdian/she-body-1.bmp",
                "serveAssets/images/zhengdian/she-body-2.bmp",
            ],
        }
        self.long_groups = {
            "龙生肖红": [
                "serveAssets/images/zhengdian/newlong.bmp",
                "serveAssets/images/zhengdian/newlong2.bmp",
                "serveAssets/images/zhengdian/long-head-1.bmp",
                "serveAssets/images/zhengdian/long-head-2.bmp",
                "serveAssets/images/zhengdian/long-body-1.bmp",
                "serveAssets/images/zhengdian/long-body-2.bmp",
                "serveAssets/images/zhengdian/long-foot-1.bmp",
                "serveAssets/images/zhengdian/long-foot-2.bmp",
            ],
        }
        self.beginFun()
        # 用户脚本: 📝 开头
        # if self.scriptName.startswith("📝 "):
        #     self._run_user_script()
        #     return
        if self.scriptName == "官渡":
            # self.go_in_ditu('地图徐州', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '徐州', '', '', True)
            self.guanduWhile()
        elif self.scriptName =='清妖':
            self.clear_yao()
        elif self.scriptName == "抢龙":
            self.zhengdianFloor = "龙+全打"
            self.new_zhengdian()
        elif self.scriptName == "测试自动战斗":
            if self.combat_auto_scenes:
                self._start_combat_auto()
                time.sleep(5)
                self._stop_combat_auto()
        elif self.scriptName == "测试":
            # self.huifu_yijian_main()
            self.cangbaotuWhile()
            # self._start_combat_auto(clear_enemy_keys=["赵云29", "诸葛亮"])
            # time.sleep(5)
            # self._stop_combat_auto()
            # self._start_combat_auto(clear_enemy_keys=["赵云29", "诸葛亮"])
            # time.sleep(5)
            # self._stop_combat_auto()
            # self.new_zhengdian()
        elif self.scriptName == "四象":
            if not self.find_pic(self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"), self.dituLocation, 0):
                self.go_in_ditu(
                    "地图封魔遗迹",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    "",
                    "",
                    True,
                )
            self.sixiangWhile()
        elif self.scriptName == "青渊":
            if not self.find_pic(self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"), self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                    '虎牢关外',
                    "",
                    "",
                    True,
                )
                isInGuanDu = self.waitFor("虎牢关外", self.dituLocation, 5)
            self.qingyuanWhile()
        elif self.scriptName == "藏宝图":
            self.cangbaotuWhile()
        elif self.scriptName == "老鼠":
            if self.zhengdianFloor not in ["全打", "走路", "龙+全打", "蛇+全打",
                                           "49整点", "49蛇+全打", "49龙+全打"]:
                self.show_error_message("请选择整点！")
                return
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/bishuishuxue.bmp')}|{self.get_resource_path('serveAssets/images/guaji/bishuishuxue1.bmp')}"
            )
        elif self.scriptName == "倭寇":
            if not self.zhengdianFloor:
                self.show_error_message("请选择整点！")
                return
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/wokou.bmp')}|{self.get_resource_path('serveAssets/images/guaji/wokou1.bmp')}"
            )
        elif self.scriptName == "龙珠":
            self.longzhuWhile()
        elif self.scriptName == "森罗殿":
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/senluodian.bmp')}|{self.get_resource_path('serveAssets/images/guaji/senluodian1.bmp')}"
            )
        elif self.scriptName == "挂机+整点":
            if not self.zhengdianFloor:
                print("选择一个整点！")
                return
            self.guajiAndzhengdianScript()
        elif self.scriptName == "刷孙策":
            while True:
                if self.check_stop_or_over():
                    return
                self.shuasunceScript()
        elif self.scriptName == "嗜血战场(精英)":
            if not self.find_str("虎牢关外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            self.hongWhile()
        elif self.scriptName == "英魂秘境(精英)":
            if not self.find_pic(
                    self.get_resource_path(
                        "serveAssets/images/hong/luanshipo.bmp"),
                    self.dituLocation,
                    0,
            ):
                self.feiFb("副本老仙", True)
            time.sleep(1)
            self.yinghunWhile()
            time.sleep(1)
        elif self.scriptName == "战魂楼(精英)":
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            if not self.zhanhunFloor:
                self.zhanhunFloor = "25层"
                print("未选择层数，自动打25层")
            self.zhanhunWhile()
        elif self.scriptName == "战魂楼(镇魂)":
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            if not self.zhanhunFloorNew:
                self.zhanhunFloorNew = "27层"
                print("未选择层数，自动打27层")
            for i in range(self.lianyu_count):
                if self.check_stop_or_over():
                    return
                hongRes = self.zhenhun_lianyu_script()
                if not hongRes:
                    break
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "战魂楼(噬魂)":
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            if not self.shihun_floor:
                self.shihun_floor = "29层"
                print("未选择层数，自动打29层")
            self.shihun_stats = {"win": 0, "fail": 0, "done": 0, "total": self.shihun_count}
            if self.frame and hasattr(self.frame, "_refresh_dungeon_stats"):
                wx.CallAfter(self.frame._refresh_dungeon_stats)
            for i in range(self.shihun_count):
                if self.check_stop_or_over():
                    return
                hongRes = self.shihun_lianyu_script()
                if not hongRes:
                    break
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "整点":
            time.sleep(1)
            if self.zhengdianFloor in ["全打", "龙+全打", "蛇+全打"]:
                self.new_zhengdian()
            elif self.zhengdianFloor == "走路":
                self.go_zhengdian()
            elif self.zhengdianFloor in ["49整点", "49蛇+全打", "49龙+全打"]:
                self.go_zhengdian49()
        elif self.scriptName == "魔镜":
            self.mojingWhile()
        elif self.scriptName == "名将闯关":
            print("开始名将闯关")
            while True:
                has_mingjiang = self.mingjiangchuangguan()
                if not has_mingjiang:
                    break
            time.sleep(1)
            self.scriptName = "官渡"
            self.feiFb("副本曹操", True)
            time.sleep(1)
            self.guanduWhile()
        elif self.scriptName == "战魂+红+整点":
            if not self.zhanhunFloor:
                self.zhanhunFloor = "25层"
                print("未选择层数，自动打25层")
            self.guanduAndHongAndZd()
        elif self.scriptName == "日常":
            self.richangeScript()
        elif self.scriptName == "五行":
            self.wuxingWhile()
        elif self.scriptName == "怪物攻城":
            self.gongChengScript()
        elif self.scriptName == "溶洞":
            self.rongdongWhile()
        elif self.scriptName == "炼丹":
            self.liandanWhile()
        elif self.scriptName == "龙岛":
            while True:
                if self.check_stop_or_over():
                    return
                hasLongDao = self.longdaoScript()
                if not hasLongDao:
                    break
        elif self.scriptName == "黑风":
            self.heifengWhile()
        elif self.scriptName == "西瓜保卫战":
            isInGuanDu = self.waitFor("洛阳", self.dituLocation, 5)
            if not isInGuanDu:
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "驿站城西",
                    True,
                )
            self.xiguaScriptWhile()
        elif self.scriptName == "名将挑战赛":
            self.mingjiangtiaozhanWhile()
        elif self.scriptName == "战魂+红+魔镜+整点":
            if not self.zhanhunFloor:
                self.zhanhunFloor = "25层"
                print("未选择层数，自动打25层")
            self.mojingAndHongAndZd()
        elif self.scriptName == "官渡精英":
            self.guanduJyScript()
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "云游精英":
            self.yunyouJyScript()
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "80精英":
            self.bamenScript()
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "100精英":
            self.laoshuJyScript()
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "49日常":
            self.richang49Script()
        elif self.scriptName == "49一键":
            self.all49Script()
        elif self.scriptName == "49整点":
            while True:
                if self.check_stop_or_over():
                    return
                self.go_zhengdian49()
        elif self.scriptName == "49战魂":
            if not self.zhanhunFloor:
                self.zhanhunFloor = "25层"
                print("未选择层数，自动打25层")
            for i in range(int(self.zhanhun_count)):
                if self.check_stop_or_over():
                    return
                self.zhanhun49Script()
        elif self.scriptName == "矿产":
            for i in range(self.heifengWhileCount):
                if self.check_stop_or_over():
                    return
                if i > 0 and i % 15 == 0:
                    time.sleep(1)
                    self.clearBag()
                    time.sleep(1)
                    self.clear_hide_map()
                    time.sleep(1)
                self.kuangchanScript()
                if self.heifengCount == self.heifengWhileCount:
                    break
            print(f"{self.heifengWhileCount}次矿产已完成,去官渡")
            self.scriptName = "官渡"
            self.guanduWhile()
        elif self.scriptName == "龙王令":
            print("请前往洛阳大道")
            while True:
                if self.check_stop_or_over():
                    return
                self.longwanglingScript()
        elif self.scriptName == "引魔符":
            print("将引魔符放到背包当前页")
            while True:
                if self.check_stop_or_over():
                    return
                self.yinmofuScript()
        elif self.scriptName == "天外天传送符":
            print("将传送符放到背包当前页，洛阳大首启动")
            while True:
                if self.check_stop_or_over():
                    return
                self.chuansongfuScript()
        elif self.scriptName == "帮派任务":
            if not self.find_str("城西", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "",
                    "",
                    True,
                )
            # 进入帮派大本营
            self.findAndClickPic(
                "城西",
                f"{self.get_resource_path('serveAssets/images/longdao/bangpai.bmp')}|{self.get_resource_path('serveAssets/images/longdao/bangpai1.bmp')}",
                "帮派大本营",
                self.gameBottomLocation,
                self.get_resource_path(
                    "serveAssets/images/longdao/dabenying.bmp"),
                self.dituLocation,
                "0.107,0.156",
            )
            for i in range(22):
                if self.check_stop_or_over():
                    return
                # 根据循环次数传入不同的任务名称
                if i == 0:
                    rw_name = "抓捕异兽"
                elif i == 1:
                    rw_name = "挑战者黄"
                else:
                    rw_name = "帮派声誉"
                self.bangpaiRW(rw_name)

        # === AUTO_SCRIPTS_DISPATCH_START ===
        # 由 ScriptFactory 自动生成的脚本分发代码
        # === AUTO_SCRIPTS_DISPATCH_END ===

    def is_user_valid(self):
        if self.overed:
            return
        current_time = datetime.now()
        for user in self.userData:
            if self.mac_address in user["user_mac"] or self.mac_address1 in \
                    user["user_mac"]:
                # if user['has_script'] != 'all' and not self.scriptName in user['has_script']:
                # 	return False
                # if user['has_script'] != 'all' and self.frame.zhengdianFloor and not '整点' in user['has_script']:
                # 	return False
                expiration_time = datetime.strptime(user["end_time"],
                                                    "%Y-%m-%d %H:%M:%S")
                if current_time > expiration_time:
                    return False
                else:
                    self.user_name = user["user_name"]
                    self.end_time = user["end_time"]
                    self.has_script = user["has_script"]
                    return True
        return False

    def is_virtual_machine(self):
        """
        检测当前系统是否为虚拟机
        兼容 Windows 10 和 Windows 11
        """
        try:
            # 方法1：使用 PowerShell Get-CimInstance（Windows 10/11 兼容）
            try:
                # 创建启动信息，隐藏窗口（Windows 专用）
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creation_flags = subprocess.CREATE_NO_WINDOW
                else:
                    startupinfo = None
                    creation_flags = 0

                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                ]
                output = subprocess.check_output(
                    cmd,
                    shell=False,
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    startupinfo=startupinfo,
                    creationflags=creation_flags,
                )
            except (
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    subprocess.SubprocessError,
            ):
                # 方法2：回退到 Get-WmiObject（更兼容，但较慢）
                try:
                    # 创建启动信息，隐藏窗口（Windows 专用）
                    if sys.platform == "win32":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        creation_flags = subprocess.CREATE_NO_WINDOW
                    else:
                        startupinfo = None
                        creation_flags = 0

                    cmd = [
                        "powershell",
                        "-NoProfile",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        "Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                    ]
                    output = subprocess.check_output(
                        cmd,
                        shell=False,
                        text=True,
                        stderr=subprocess.DEVNULL,
                        timeout=5,
                        startupinfo=startupinfo,
                        creationflags=creation_flags,
                    )
                except (
                        subprocess.TimeoutExpired,
                        FileNotFoundError,
                        subprocess.SubprocessError,
                ):
                    # 方法3：使用 platform 模块（最简单，但信息较少）
                    import platform

                    output = f"{platform.system()} {platform.machine()}"

            vm_keywords = [
                "VMware",
                "VirtualBox",
                "KVM",
                "QEMU",
                "Xen",
                "Bochs",
                "Hyper-V",
                "Microsoft Corporation",
            ]  # Hyper-V 的制造商
            output_upper = output.upper()
            return any(
                keyword.upper() in output_upper for keyword in vm_keywords)
        except Exception as e:
            # 如果所有方法都失败，返回 False（非虚拟机）
            return False

    def findGame(self):
        ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int,
                                             ctypes.c_int)
        self.click_hwnd = 0

        # 定义回调函数
        def enum_child_windows_callback(hwnd, lParam):
            window_text = self.dm.GetWindowText(hwnd)
            class_name = self.dm.GetClassName(hwnd)
            return True  # 返回 True 继续枚举

        # 将回调函数转换为 ctypes 函数指针
        enum_child_windows_callback_func = ENUMWINDOWSPROC(
            enum_child_windows_callback)
        # 查找目标窗口句柄
        target_window_title = self.frame.game_name
        target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
        hwnds = self.dm.EnumWindow(0, target_window_title, target_window_class,
                                   1 + 2)
        hwnds = hwnds.split(",")
        hwnd = 0
        for item in hwnds:
            if self.overed:
                return
            if item and self.dm.GetWindowTitle(
                    int(item)) == target_window_title:
                hwnd = int(item)
                break
        if hwnd:
            # 使用 Windows API 的 EnumChildWindows
            user32 = ctypes.WinDLL("user32", use_last_error=True)

            # 获取屏幕分辨率
            screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度

            screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度
            if self.overed:
                return

            def enum_child_proc(hwnd, lParam):
                if self.overed:
                    return
                class_name = self.dm.GetWindowClass(hwnd)
                child_rect = self.dm.GetWindowRect(hwnd)
                if child_rect != 0:
                    left, top, right, bottom, isFind = child_rect
                    if (
                            class_name == "NativeWindowClass"
                            and left > 0
                            and right < screen_width
                            and bottom < screen_height
                    ):
                        # print(left, top, right, bottom)
                        self.click_hwnd = hwnd
                        return False
                # if class_name == 'Chrome_RenderWidgetHostHWND':
                # 	if left > 50:
                # 		print('请5s内关闭小号列表！')
                # 		time.sleep(5)
                #
                # 	self.click_hwnd = hwnd
                # 	return False
                return True

            enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
            user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
        else:
            print("未找到游戏窗口，请检查输入的游戏名称是否正确！")
        # 绑定窗口到后台模式
        bind_result = self.dm.BindWindow(self.click_hwnd, "dx2", "windows3",
                                         "windows", 0)
        if bind_result == 1:
            # print("窗口绑定成功")
            time.sleep(0.1)
        else:
            print("窗口绑定失败")
            return False
        location = self.dm.GetClientSize(self.click_hwnd)
        x, y, res = location
        if res == 1:
            # print('已找到游戏画面')
            time.sleep(0.1)
        else:
            self.show_error_message("未检测到游戏页面")
            return False
        if self.overed:
            return
        self.dm.SetDict(0, self.get_resource_path(
            "serveAssets/fonts/common.txt"))  # 字库文件路径
        current_rect = self.dm.GetWindowRect(self.click_hwnd)
        left, top, right, bottom, isFind = current_rect
        self.locationX = 0
        # xian_pos = self.dm.FindPicEx(left, top, right, bottom, self.get_resource_path("serveAssets/images/xian.bmp"), "", 0.8, 2)
        # if not xian_pos:
        # 	self.show_error_message('未找到游戏画面顶部，请重新启动脚本')
        # 	return
        # xian_pos = xian_pos.split(',')
        self.locationY = 0
        self.locationWidth = x
        self.locationHeight = y
        self.locationRightTopX = self.locationX + int(
            (self.locationWidth * 0.8))
        self.locationRightTopY = self.locationY
        self.locationRightTopWidth = self.locationWidth + self.locationX
        self.locationRightTopHeight = self.locationY + int(
            self.locationHeight * 0.2)
        self.gameLocation = (
            self.locationX,
            self.locationY,
            self.locationWidth,
            self.locationHeight,
        )
        self.gameLeftLocation = (
            self.locationX,
            int(self.locationY + (self.locationHeight * 0.3)),
            int(self.locationX + (self.locationWidth * 0.7)),
            self.locationHeight,
        )
        self.gameRightFullLocation = (
            int(self.locationX + int(self.locationWidth * 0.3)),
            80,
            self.locationWidth,
            self.locationHeight,
        )
        self.gameRightLocation = (
            int(self.locationX + int(self.locationWidth * 0.3)),
            int(self.locationY + (self.locationHeight * 0.3)),
            self.locationWidth,
            self.locationHeight,
        )
        self.gameBottomLocation = (
            self.locationX,
            int(self.locationY + (self.locationHeight * 0.3)),
            self.locationWidth,
            self.locationHeight,
        )
        self.dituLeftLocation = (
            self.locationRightTopX,
            self.locationRightTopY,
            int(self.locationRightTopX + (self.locationWidth * 0.1)),
            self.locationRightTopHeight,
        )
        self.dituCenterLocation = (
            int(self.locationRightTopX + (self.locationWidth * 0.2 * 0.3)),
            self.locationRightTopY,
            int(self.locationRightTopX + (self.locationWidth * 0.1) + (
                    self.locationWidth * 0.2 * 0.3)),
            self.locationRightTopHeight,
        )
        self.dituRightLocation = (
            int(self.locationRightTopX + (self.locationWidth * 0.1)),
            self.locationRightTopY,
            self.locationRightTopWidth,
            self.locationRightTopHeight,
        )
        self.talkLocation = (
            self.locationX,
            int(self.locationY + (self.locationHeight * 0.5)),
            int(int(self.locationWidth * 0.5) + self.locationX),
            self.locationHeight,
        )
        self.dituLocation = (
            self.locationRightTopX,
            self.locationRightTopY,
            self.locationRightTopWidth,
            self.locationRightTopHeight,
        )
        # if (
        #         self.scriptName in ["官渡", "黑风", "魔镜", "矿产", "测试"]
        #         and not self.refreshFlag
        #         and not self.hasRefresh
        #         and (self.teammate1_name or self.teammate2_name)
        # ):
        #     self.dm.KeyPressChar("t")
        #     time.sleep(2)
        #     self.dm.Capture(
        #         304,
        #         315,
        #         353,
        #         337,
        #         self.get_resource_path("serveAssets/images/team_mate.bmp"),
        #     )
        #     time.sleep(2)
        #     self.dm.Capture(
        #         426,
        #         315,
        #         461,
        #         337,
        #         self.get_resource_path("serveAssets/images/team_mate1.bmp"),
        #     )
        #     time.sleep(2)
        #     self.dm.Capture(
        #         538,
        #         315,
        #         587,
        #         337,
        #         self.get_resource_path("serveAssets/images/team_mate2.bmp"),
        #     )
        #     time.sleep(2)
        #     self.dm.KeyPressChar("t")
        return True

    def find_pic_or_str(self, find, region, find_dir):
        if self.overed:
            return
        types = "serveAssets" in find
        if not types:
            res = self.find_str(find, region, find_dir)
        else:
            res = self.find_pic(find, region, find_dir)
        return res

    def find_pic_or_str_team1(self, find, region, find_dir):
        if self.overed:
            return
        types = "serveAssets" in find
        if not types:
            res = self.find_str_team1(find, region, find_dir)
        else:
            res = self.find_pic_team1(find, region, find_dir)
        return res

    def find_pic_or_str_team2(self, find, region, find_dir):
        if self.overed:
            return
        types = "serveAssets" in find
        if not types:
            res = self.find_str_team2(find, region, find_dir)
        else:
            res = self.find_pic_team2(find, region, find_dir)
        return res

    # 找图方法
    def find_pic(self, image_path, image_region, find_dir):
        if self.overed:
            return
        find_path = image_path
        # picSize = self.dm.GetPicSize(image_path)
        # picSize = picSize.split(',')
        # picW, picH = picSize[0], picSize[1]
        x, y, w, h = image_region
        pos = self.dm.FindPicEx(int(x), int(y), int(w), int(h), find_path, "",
                                self.confidenceNum, find_dir)
        if not pos:
            # if self.confidenceNum == 0.9:
            # 	self.confidenceNum = 0.8
            # 	find_res = self.find_pic(image_path, image_region, find_dir)
            # 	self.confidenceNum = 0.9
            # 	return find_res
            return False
        pos = pos.split("|")
        # if len(pos) == 1:
        # 	pos_res = pos[0].split(',')
        # else:
        # 	# 初始化最小值和对应的项
        # 	min_x_value = float('inf')
        # 	min_item = None
        # 	# 遍历数组，找到第二个数值最小的那一项
        # 	for item in pos:
        # 		# 解析每一项
        # 		parts = item.split(',')
        # 		x_value = int(parts[1])
        # 		# 比较并更新最小值和对应的项
        # 		if x_value < min_x_value:
        # 			min_x_value = x_value
        # 			min_item = item
        # 	pos_res = min_item.split(',')
        pos_res = pos[0].split(",")
        pics = image_path.split("|")
        picSize = self.dm.GetPicSize(pics[int(pos_res[0])])
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        posX = int(pos_res[1]) + (int(picW) * 0.5)
        posY = int(pos_res[2]) + (int(picH) * 0.5)
        res = ResXy(int(posX), int(posY))
        self.dm.FreePic(image_path)
        return res

    # 找字方法
    def find_str(self, text, region, find_dir):
        if self.overed:
            return
        x, y, w, h = region
        find_str_result = self.dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text, self.color_format,
            self.confidenceNum
        )
        find_str_result = find_str_result.split("|")
        if int(find_str_result[0]) >= 0:
            pos_res = None
            if len(find_str_result) == 3:
                pos_res = find_str_result
            elif len(find_str_result) > 3:
                if int(find_str_result[1]) < int(
                        find_str_result[4]) and find_dir in [
                    0,
                    1,
                ]:
                    pos_res = find_str_result[:3]
                else:
                    pos_res = find_str_result[3:6]
            posX = pos_res[1]
            posY = pos_res[2]
            res = ResXy(int(posX), int(posY))
            return res
        else:
            # if self.confidenceNum == 0.9:
            # 	self.confidenceNum = 0.8
            # 	find_res = self.find_str(text, region, find_dir)
            # 	self.confidenceNum = 0.9
            # 	return find_res
            return False

    # 找图方法z
    def find_pic_team1(self, image_path, image_region, find_dir):
        if self.overed:
            return
        find_path = image_path
        # picSize = self.dm.GetPicSize(image_path)
        # picSize = picSize.split(',')
        # picW, picH = picSize[0], picSize[1]
        x, y, w, h = image_region
        pos = self.win1_dm.FindPicEx(int(x), int(y), int(w), int(h), find_path,
                                     "", self.confidenceNum, find_dir)
        if not pos:
            return False
        pos = pos.split("|")
        # if len(pos) == 1:
        # 	pos_res = pos[0].split(',')
        # else:
        # 	# 初始化最小值和对应的项
        # 	min_x_value = float('inf')
        # 	min_item = None
        # 	# 遍历数组，找到第二个数值最小的那一项
        # 	for item in pos:
        # 		# 解析每一项
        # 		parts = item.split(',')
        # 		x_value = int(parts[1])
        # 		# 比较并更新最小值和对应的项
        # 		if x_value < min_x_value:
        # 			min_x_value = x_value
        # 			min_item = item
        # 	pos_res = min_item.split(',')
        pos_res = pos[0].split(",")
        pics = image_path.split("|")
        picSize = self.win1_dm.GetPicSize(pics[int(pos_res[0])])
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        posX = int(pos_res[1]) + (int(picW) * 0.5)
        posY = int(pos_res[2]) + (int(picH) * 0.5)
        res = ResXy(int(posX), int(posY))
        return res

    # 找字方法
    def find_str_team1(self, text, region, find_dir):
        if self.overed:
            return
        x, y, w, h = region
        find_str_result = self.win1_dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text, self.color_format,
            self.confidenceNum
        )
        find_str_result = find_str_result.split("|")
        if int(find_str_result[0]) < 0:
            return False
        else:
            pos_res = None
            if len(find_str_result) == 3:
                pos_res = find_str_result
            elif len(find_str_result) > 3:
                if int(find_str_result[1]) < int(
                        find_str_result[4]) and find_dir in [
                    0,
                    1,
                ]:
                    pos_res = find_str_result[:3]
                else:
                    pos_res = find_str_result[3:6]
            posX = pos_res[1]
            posY = pos_res[2]
            res = ResXy(int(posX), int(posY))
            return res

    # 找图方法z
    def find_pic_team2(self, image_path, image_region, find_dir):
        if self.overed:
            return
        find_path = image_path
        # picSize = self.dm.GetPicSize(image_path)
        # picSize = picSize.split(',')
        # picW, picH = picSize[0], picSize[1]
        x, y, w, h = image_region
        pos = self.win2_dm.FindPicEx(int(x), int(y), int(w), int(h), find_path,
                                     "", self.confidenceNum, find_dir)
        if not pos:
            return False
        pos = pos.split("|")
        # if len(pos) == 1:
        # 	pos_res = pos[0].split(',')
        # else:
        # 	# 初始化最小值和对应的项
        # 	min_x_value = float('inf')
        # 	min_item = None
        # 	# 遍历数组，找到第二个数值最小的那一项
        # 	for item in pos:
        # 		# 解析每一项
        # 		parts = item.split(',')
        # 		x_value = int(parts[1])
        # 		# 比较并更新最小值和对应的项
        # 		if x_value < min_x_value:
        # 			min_x_value = x_value
        # 			min_item = item
        # 	pos_res = min_item.split(',')
        pos_res = pos[0].split(",")
        pics = image_path.split("|")
        picSize = self.win2_dm.GetPicSize(pics[int(pos_res[0])])
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        posX = int(pos_res[1]) + (int(picW) * 0.5)
        posY = int(pos_res[2]) + (int(picH) * 0.5)
        res = ResXy(int(posX), int(posY))
        return res

    # 找字方法
    def find_str_team2(self, text, region, find_dir):
        if self.overed:
            return
        x, y, w, h = region
        find_str_result = self.win2_dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text, self.color_format,
            self.confidenceNum
        )
        find_str_result = find_str_result.split("|")
        if int(find_str_result[0]) < 0:
            return False
        else:
            pos_res = None
            if len(find_str_result) == 3:
                pos_res = find_str_result
            elif len(find_str_result) > 3:
                if int(find_str_result[1]) < int(
                        find_str_result[4]) and find_dir in [
                    0,
                    1,
                ]:
                    pos_res = find_str_result[:3]
                else:
                    pos_res = find_str_result[3:6]
            posX = pos_res[1]
            posY = pos_res[2]
            res = ResXy(int(posX), int(posY))
            return res

    # 图中找图
    def fing_fei_in_image_or_str(self, base, base_region, fei_region,
                                 fei_image):
        if self.overed:
            return
        base_pos = self.find_pic_or_str(base, base_region, 0)
        if not base_pos:
            return False
        x, y, w, h = fei_region
        fei_pox = self.dm.FindPicEx(
            int(base_pos.x - x),
            int(base_pos.y - y),
            int(base_pos.x + w),
            int(base_pos.y + h),
            fei_image,
            "",
            0.6,
            0,
        )
        if not fei_pox or fei_pox is None:
            return False
        res_pos = fei_pox.split("|")
        res_pos = res_pos[0].split(",")
        pics = fei_image.split("|")
        picSize = self.dm.GetPicSize(pics[int(res_pos[0])])
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        posX = int(res_pos[1]) + (int(picW) * 0.5)
        posY = int(res_pos[2]) + (int(picH) * 0.5)
        res = ResXy(int(posX), int(posY))
        return res

    def child_task(self):

        # 怪物位置 205  389
        while True:
            if self.check_stop_or_over():
                return
            # 关闭右边
            if self.scriptName != "帮派任务":
                closeRight = self.click_image(
                    self.get_resource_path("serveAssets/images/closeRight.bmp"),
                    self.confidenceNum,
                    self.gameLocation,
                )
                if closeRight:
                    time.sleep(0.5)
            # 点击拒绝
            self.click_image(
                self.get_resource_path("serveAssets/images/jujue.bmp"),
                self.confidenceNum,
                self.gameBottomLocation,
            )
            if self.addBloudFlag:
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBloud.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBloud1.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBloud2.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBlue.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 80, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
            # 点击取消
            if self.find_pic_or_str(
                    f"{self.get_resource_path('serveAssets/images/jingji1.bmp')}|{self.get_resource_path('serveAssets/images/nohasfei.bmp')}",
                    self.gameBottomLocation,
                    0,
            ):
                self.click_image(
                    self.get_resource_path("serveAssets/images/closeJJ.bmp"),
                    self.confidenceNum,
                    self.gameBottomLocation,
                )
            # 点自动
            # if self.scriptName in ["官渡", "魔镜", "黑风", "矿产"]:
            # if not self.guajiFlag:
            #     print(111)
            #     # return
            #     # if self.find_pic(
            #     #     self.get_resource_path("serveAssets/images/zhaohuan.bmp"),
            #     #     self.gameBottomLocation,
            #     #     0,
            #     # ):
            #     #     self.click_image(
            #     #         self.get_resource_path("serveAssets/images/fangyu.bmp"),
            #     #         0.8,
            #     #         self.gameLocation,
            #     #     )
            #     # jineng = self.find_pic(
            #     #     f"{self.get_resource_path('serveAssets/images/caocao.bmp')}|{self.get_resource_path('serveAssets/images/moguan.bmp')}|{self.get_resource_path('serveAssets/images/zhuge.bmp')}|{self.get_resource_path('serveAssets/images/lvbu.bmp')}|{self.get_resource_path('serveAssets/images/daqiao.bmp')}||{self.get_resource_path('serveAssets/images/guojia.bmp')}||{self.get_resource_path('serveAssets/images/zhangliao.bmp')}",
            #     #     self.gameBottomLocation,
            #     #     0,
            #     # )
            #     # if jineng:
            #     #     self.dm.MoveTo(jineng.x, jineng.y)
            #     #     time.sleep(0.001)
            #     #     self.dm.LeftClick()
            #     #     time.sleep(0.5)
            #     #     # jineng = self.auto_move_and_click()
            #     #     if self.scriptName in ["官渡", "魔镜", "黑风"]:
            #     #         self.dm.MoveTo(196, 255)
            #     #     else:
            #     #         self.dm.MoveTo(190, 383)
            #     #     time.sleep(0.001)
            #     #     self.dm.LeftClick()
            #     #     time.sleep(2)
            #     # jineng1 = self.find_pic(
            #     #     f"{self.get_resource_path('serveAssets/images/caocao.bmp')}|{self.get_resource_path('serveAssets/images/moguan.bmp')}|{self.get_resource_path('serveAssets/images/zhuge.bmp')}|{self.get_resource_path('serveAssets/images/lvbu.bmp')}|{self.get_resource_path('serveAssets/images/daqiao.bmp')}||{self.get_resource_path('serveAssets/images/guojia.bmp')}||{self.get_resource_path('serveAssets/images/zhangliao.bmp')}",
            #     #     self.gameBottomLocation,
            #     #     0,
            #     # )
            #     # if jineng1:
            #     #     self.dm.MoveTo(jineng1.x, jineng1.y)
            #     #     time.sleep(0.001)
            #     #     self.dm.LeftClick()
            #     #     time.sleep(1.5)
            #     #     # jineng1 = self.auto_move_and_click()
            #     #     if self.scriptName in ["官渡", "魔镜", "黑风"]:
            #     #         self.dm.MoveTo(196, 255)
            #     #     else:
            #     #         self.dm.MoveTo(190, 383)
            #     #     time.sleep(0.001)
            #     #     self.dm.LeftClick()
            #     # if jineng1 or jineng:
            #     #     self.guajiFlag = True
            #     # # 193 294   190  383
            #     # self.click_image(
            #     #     self.get_resource_path("serveAssets/images/yes.bmp"),
            #     #     0.8,
            #     #     self.gameLocation,
            #     # )
            # else:
            if not self.combat_auto_running:
                self.click_image(
                    self.get_resource_path("serveAssets/images/zidong.bmp"),
                    0.8,
                    self.gameLocation,
                )
            time.sleep(2)

    # 绑定第一个窗口
    def find_and_bing_windows1(self):
        if not self.teammate1_name:
            return
        CoInitialize()
        self.win1_hwnd = 0
        self.win1_dm = CreateObject("dm.dmsoft")
        ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int,
                                             ctypes.c_int)

        # 定义回调函数
        def enum_child_windows_callback(hwnd, lParam):
            window_text = self.win1_dm.GetWindowText(hwnd)
            class_name = self.win1_dm.GetClassName(hwnd)
            return True  # 返回 True 继续枚举

        # 将回调函数转换为 ctypes 函数指针
        enum_child_windows_callback_func = ENUMWINDOWSPROC(
            enum_child_windows_callback)
        # 查找目标窗口句柄
        target_window_title = self.teammate1_name if self.independent_win1 else (self.teammate1_name + " | " + self.frame.game_name)
        target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
        hwnds = self.win1_dm.EnumWindow(0, target_window_title,
                                        target_window_class, 1 + 2)
        hwnds = hwnds.split(",")
        hwnd = 0
        for item in hwnds:
            if item and self.win1_dm.GetWindowTitle(
                    int(item)) == target_window_title:
                hwnd = int(item)
                break
        if hwnd:
            # 使用 Windows API 的 EnumChildWindows
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            # 获取屏幕分辨率
            screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
            screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度

            def enum_child_proc(hwnd, lParam):
                class_name = self.win1_dm.GetWindowClass(hwnd)
                child_rect = self.win1_dm.GetWindowRect(hwnd)
                if child_rect != 0:
                    left, top, right, bottom, isFind = child_rect
                    if (
                            class_name == "NativeWindowClass"
                            and left > 0
                            and right < screen_width
                            and bottom < screen_height
                    ):
                        self.win1_hwnd = hwnd
                        return False
                # if class_name == 'Chrome_RenderWidgetHostHWND':
                # 	self.win1_hwnd = hwnd
                # 	return False
                return True

            enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
            user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
        else:
            self.show_error_message(
                "未找到游戏窗口，请检查输入的队友1名称是否正确！")
        # 绑定窗口到后台模式
        bind_result = self.win1_dm.BindWindow(self.win1_hwnd, "gdi", "windows3",
                                              "windows", 0)
        if bind_result != 1:
            self.show_error_message("队友1绑定失败")
            return False
        self.win1_dm.SetDict(0, self.get_resource_path(
            "serveAssets/fonts/team1.txt"))
        time.sleep(0.5)
        if self.refreshFlag:
            return
        duiwu_pos = self.waitFor_team1("队伍", self.talkLocation, 3)
        if duiwu_pos:
            self.win1_dm.MoveTo(duiwu_pos.x, duiwu_pos.y)
            time.sleep(0.01)
            self.win1_dm.LeftClick()
            time.sleep(0.5)
            self.win1_dm.MoveTo(duiwu_pos.x, int(duiwu_pos.y + 28))
            time.sleep(0.01)
            self.win1_dm.LeftClick()
            time.sleep(0.3)
            self.win1_dm.KeyPressChar("1")
            time.sleep(1)
            self.win1_dm.KeyPressChar("enter")
        time.sleep(0.5)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/yincang.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        while True:
            if self.check_stop_or_over():
                return
            if self.clickFlag:
                self.clearBag_team1()
            if self.huifuFlag and self.win1_dm:
                self.huifu_yijian(self.win1_dm)
            if self.addBloudFlag:
                self.addBloud_team1()
            if self.clearMapFlag:
                self.clear_hide_map_team1()
            if self.addBloudFlag:
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBloud.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBloud1.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBloud2.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBlue.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 80, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
            if self.refreshFlag:
                self.refresh_view_team1()
            if not self.combat_auto_running:
                self.click_image_team1(
                    self.get_resource_path("serveAssets/images/zidong.bmp"),
                    0.8,
                    self.gameLocation,
                )
            time.sleep(1)

    def refresh_view_team1(self):
        self.guajiFlag1 = False
        gc.collect()
        self.win1_dm.ClearDict(0)
        self.win1_dm.UnBindWindow()
        self.win1_dm.DownCpu(30)
        target_window_title = self.teammate1_name if self.independent_win1 else (self.teammate1_name + " | " + self.frame.game_name)
        target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
        hwnds = self.win1_dm.EnumWindow(0, target_window_title,
                                        target_window_class, 1 + 2)
        hwnds = hwnds.split(",")
        hwnd = 0
        for item in hwnds:
            if self.overed:
                return
            if item and self.win1_dm.GetWindowTitle(
                    int(item)) == target_window_title:
                hwnd = int(item)
                break
        bind_result = self.win1_dm.BindWindow(hwnd, "gdi", "windows3",
                                              "windows", 0)
        if bind_result == 1:
            time.sleep(0.1)
        else:
            print("未找到主窗口，请检查输入的游戏名称是否正确！")
        self.confidenceNum = 0.6
        refresh_pos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/refresh.bmp"),
            (0, 0, 900, 200))
        self.confidenceNum = 0.9
        self.win1_dm.MoveTo(refresh_pos.x, refresh_pos.y)
        time.sleep(0.001)
        self.win1_dm.LeftClick()
        time.sleep(0.001)
        self.win1_dm.KeyPressChar("F5")
        time.sleep(0.1)
        self.win1_dm.KeyPress(116)
        time.sleep(5)
        self.win1_dm.UnBindWindow()
        time.sleep(5)
        self.find_and_bing_windows1()
        in_game_pos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/in_game.bmp"),
            self.gameBottomLocation,
        )
        self.win1_dm.MoveTo(in_game_pos.x, in_game_pos.y)
        time.sleep(2)
        self.win1_dm.LeftClick()
        self.waitFor_team1(
            self.get_resource_path("serveAssets/images/mhlogo.bmp"),
            self.gameLocation)
        time.sleep(6)
        checkRolePos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/checkRole.bmp"),
            self.gameLocation,
        )
        self.win1_dm.MoveTo(checkRolePos.x, checkRolePos.y)
        checkCount = int(self.teammate1_pos) - 1 if self.teammate1_pos else 0
        if checkCount > 0:
            for i in range(checkCount):
                time.sleep(1.5)
                self.win1_dm.LeftClick()
        time.sleep(1.5)
        self.win1_dm.MoveTo(440, 370)
        time.sleep(0.5)
        self.win1_dm.LeftClick()
        self.waitFor_team1(
            self.get_resource_path("serveAssets/images/xiulian.bmp"),
            self.gameLocation)
        time.sleep(3)
        self.check_line1(self.line)
        time.sleep(2)
        while not self.teamFlag:
            self.click_image_team1(
                self.get_resource_path("serveAssets/images/quxiao.bmp"),
                0.8,
                self.gameBottomLocation,
            )
            self.confidenceNum = 0.6
            in_team_pos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/in_team.bmp"),
                self.gameLocation,
                5,
            )
            self.confidenceNum = 0.9
            if in_team_pos:
                self.win1_dm.MoveTo(in_team_pos.x, in_team_pos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
            jieshou = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/jieshou.bmp"),
                self.gameLocation,
                5,
            )
            if jieshou:
                self.win1_dm.MoveTo(jieshou.x, jieshou.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
                time.sleep(2)
                self.win1_dm.KeyPressChar("t")
                my_team = self.waitFor_team1(
                    self.get_resource_path("serveAssets/images/myteam.bmp"),
                    self.gameLocation,
                    5,
                )
                if my_team:
                    team_mate = self.waitFor_team1(
                        self.get_resource_path(
                            "serveAssets/images/team_mate.bmp"),
                        self.team_loc,
                        5,
                    )
                    if team_mate:
                        self.win1_dm.KeyPressChar("t")
                        break
                    else:
                        self.win1_dm.KeyPressChar("t")

    # 绑定第二个窗口
    def find_and_bing_windows2(self):
        if not self.teammate2_name:
            return
        CoInitialize()
        self.win2_hwnd = 0
        self.win2_dm = CreateObject("dm.dmsoft")
        ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int,
                                             ctypes.c_int)

        # 定义回调函数
        def enum_child_windows_callback(hwnd, lParam):
            window_text = self.win2_dm.GetWindowText(hwnd)
            class_name = self.win2_dm.GetClassName(hwnd)
            return True  # 返回 True 继续枚举

        # 将回调函数转换为 ctypes 函数指针
        enum_child_windows_callback_func = ENUMWINDOWSPROC(
            enum_child_windows_callback)
        # 查找目标窗口句柄
        target_window_title = self.teammate2_name if self.independent_win2 else (self.teammate2_name + " | " + self.frame.game_name)
        target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
        hwnds = self.win2_dm.EnumWindow(0, target_window_title,
                                        target_window_class, 1 + 2)
        hwnds = hwnds.split(",")
        hwnd = 0
        for item in hwnds:
            if item and self.win2_dm.GetWindowTitle(
                    int(item)) == target_window_title:
                hwnd = int(item)
                break
        if hwnd:
            # 使用 Windows API 的 EnumChildWindows
            user32 = ctypes.WinDLL("user32", use_last_error=True)

            # 获取屏幕分辨率
            screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
            screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度

            def enum_child_proc(hwnd, lParam):
                class_name = self.win2_dm.GetWindowClass(hwnd)
                child_rect = self.win2_dm.GetWindowRect(hwnd)
                if child_rect != 0:
                    left, top, right, bottom, isFind = child_rect
                    if (
                            class_name == "NativeWindowClass"
                            and left > 0
                            and right < screen_width
                            and bottom < screen_height
                    ):
                        self.win2_hwnd = hwnd
                        return False
                # if class_name == 'Chrome_RenderWidgetHostHWND':
                # 	self.win2_hwnd = hwnd
                # 	return False
                return True

            enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
            user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
        else:
            self.show_error_message(
                "未找到游戏窗口，请检查输入的队友2名称是否正确！")
        # 绑定窗口到后台模式
        bind_result = self.win2_dm.BindWindow(self.win2_hwnd, "gdi", "windows3",
                                              "windows", 0)
        if bind_result != 1:
            self.show_error_message("队友2绑定失败")
            return False
        self.win2_dm.SetDict(0, self.get_resource_path(
            "serveAssets/fonts/team2.txt"))
        time.sleep(0.5)
        if self.refreshFlag:
            return
        duiwu_pos = self.waitFor_team2("队伍", self.talkLocation, 3)
        if duiwu_pos:
            self.win2_dm.MoveTo(duiwu_pos.x, duiwu_pos.y)
            time.sleep(0.01)
            self.win2_dm.LeftClick()
            time.sleep(0.5)
            self.win2_dm.MoveTo(duiwu_pos.x, int(duiwu_pos.y + 28))
            time.sleep(0.01)
            self.win2_dm.LeftClick()
            time.sleep(0.3)
            self.win2_dm.KeyPressChar("1")
            time.sleep(1)
            self.win2_dm.KeyPressChar("enter")
        time.sleep(0.5)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/yincang.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        while True:
            if self.check_stop_or_over():
                return
            time.sleep(1)
            if self.clickFlag:
                self.clearBag_team2()
            if self.huifuFlag and self.win2_dm:
                self.huifu_yijian(self.win2_dm)
            if self.addBloudFlag:
                self.addBloud_team2()
            if self.clearMapFlag:
                self.clear_hide_map_team2()
            if self.addBloudFlag:
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBloud.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBloud1.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBloud2.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBlue.bmp"),
                    0.6,
                    self.gameLocation,
                )
                time.sleep(0.1)
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 80, self.locationWidth,
                     self.locationHeight),
                )
                time.sleep(0.1)
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/addBlue1.bmp"),
                    0.6,
                    (self.locationX, 120, self.locationWidth,
                     self.locationHeight),
                )
            if not self.combat_auto_running:
                self.click_image_team2(
                    self.get_resource_path("serveAssets/images/zidong.bmp"),
                    0.8,
                    self.gameLocation,
                )
            if self.refreshFlag:
                self.refresh_view_team2()

    def refresh_view_team2(self):
        self.guajiFlag2 = False
        gc.collect()
        self.win2_dm.ClearDict(0)
        self.win2_dm.UnBindWindow()
        self.win2_dm.DownCpu(30)
        target_window_title = self.teammate2_name if self.independent_win2 else (self.teammate2_name + " | " + self.frame.game_name)
        target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
        hwnds = self.win2_dm.EnumWindow(0, target_window_title,
                                        target_window_class, 1 + 2)
        hwnds = hwnds.split(",")
        hwnd = 0
        for item in hwnds:
            if self.overed:
                return
            if item and self.win2_dm.GetWindowTitle(
                    int(item)) == target_window_title:
                hwnd = int(item)
                break
        bind_result = self.win2_dm.BindWindow(hwnd, "gdi", "windows3",
                                              "windows", 0)
        if bind_result == 1:
            time.sleep(0.1)
        else:
            print("未找到主窗口，请检查输入的游戏名称是否正确！")
        self.confidenceNum = 0.6
        refresh_pos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/refresh.bmp"),
            (0, 0, 900, 200))
        self.confidenceNum = 0.9
        self.win2_dm.MoveTo(refresh_pos.x, refresh_pos.y)
        time.sleep(0.001)
        self.win2_dm.LeftClick()
        time.sleep(0.001)
        self.win2_dm.KeyPressChar("F5")
        time.sleep(0.001)
        self.win2_dm.KeyPress(116)
        time.sleep(5)
        self.win2_dm.UnBindWindow()
        time.sleep(5)
        self.find_and_bing_windows2()
        in_game_pos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/in_game.bmp"),
            self.gameBottomLocation,
        )
        self.win2_dm.MoveTo(in_game_pos.x, in_game_pos.y)
        time.sleep(2)
        self.win2_dm.LeftClick()
        self.waitFor_team2(
            self.get_resource_path("serveAssets/images/mhlogo.bmp"),
            self.gameLocation)
        time.sleep(6)
        checkRolePos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/checkRole.bmp"),
            self.gameLocation,
        )
        self.win2_dm.MoveTo(checkRolePos.x, checkRolePos.y)
        checkCount = int(self.teammate2_pos) - 1 if self.teammate2_pos else 0
        if checkCount > 0:
            for i in range(checkCount):
                time.sleep(1.5)
                self.win2_dm.LeftClick()
        time.sleep(1.5)
        self.win2_dm.MoveTo(440, 370)
        time.sleep(0.5)
        self.win2_dm.LeftClick()
        self.waitFor_team2(
            self.get_resource_path("serveAssets/images/xiulian.bmp"),
            self.gameLocation)
        time.sleep(3)
        self.check_line2(self.line)
        time.sleep(2)
        while not self.teamFlag:
            self.click_image_team2(
                self.get_resource_path("serveAssets/images/quxiao.bmp"),
                0.8,
                self.gameBottomLocation,
            )
            self.confidenceNum = 0.6
            in_team_pos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/in_team.bmp"),
                self.gameLocation,
                5,
            )
            self.confidenceNum = 0.9
            if in_team_pos:
                self.win2_dm.MoveTo(in_team_pos.x, in_team_pos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
            jieshou = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/jieshou.bmp"),
                self.gameLocation,
                5,
            )
            if jieshou:
                self.win2_dm.MoveTo(jieshou.x, jieshou.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
                time.sleep(2)
                self.win2_dm.KeyPressChar("t")
                my_team = self.waitFor_team2(
                    self.get_resource_path("serveAssets/images/myteam.bmp"),
                    self.gameLocation,
                    5,
                )
                if my_team:
                    team_mate = self.waitFor_team2(
                        self.get_resource_path(
                            "serveAssets/images/team_mate.bmp"),
                        self.team_loc,
                        5,
                    )
                    if team_mate:
                        self.win2_dm.KeyPressChar("t")
                        break
                    else:
                        self.win2_dm.KeyPressChar("t")

    def addBloud(self):
        if self.overed:
            return
        self.confidenceNum = 0.7
        self.addBloudFlag = True
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        self.addBloudFlag = False
        self.confidenceNum = 0.9

    def addBloud_team1(self):
        if self.overed:
            return
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image_team1(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )

    def addBloud_team2(self):
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBloud2.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.1)
        self.click_image_team2(
            self.get_resource_path("serveAssets/images/addBlue1.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )

    def get_mac_address(self):
        # 使用 psutil 获取所有网络接口信息
        interfaces = psutil.net_if_addrs()

        # 遍历接口信息，找到MAC地址
        for interface_name, interface_addresses in interfaces.items():
            for address in interface_addresses:
                if str(address.family) == "AddressFamily.AF_LINK":
                    return address.address

        return "MAC address not found"

    def beginFun(self, check=False):
        closeTalkXY = self.find_pic(
            self.get_resource_path("serveAssets/images/closeTalk.bmp"),
            self.talkLocation,
            0,
        )
        with condition:
            if self.stoped:
                condition.wait()
        if closeTalkXY:
            self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
            for i in range(4):
                time.sleep(0.2)
                self.dm.LeftClick()
        self.click_image(
            self.get_resource_path("serveAssets/images/closeTalk.bmp"),
            self.confidenceNum,
            self.talkLocation,
        )
        time.sleep(0.2)
        self.click_image(
            self.get_resource_path("serveAssets/images/closeTalk.bmp"),
            self.confidenceNum,
            self.talkLocation,
        )
        # 关闭右边
        self.click_image(
            self.get_resource_path("serveAssets/images/closeright.bmp"),
            self.confidenceNum,
            self.gameBottomLocation,
        )
        time.sleep(0.2)
        self.click_image(
            self.get_resource_path("serveAssets/images/yincang.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(1)
        with condition:
            if self.stoped:
                condition.wait()
        self.click_image(
            self.get_resource_path("serveAssets/images/yes.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.3)
        self.click_image(
            self.get_resource_path("serveAssets/images/yes.bmp"),
            self.confidenceNum,
            self.gameLocation,
        )
        time.sleep(0.5)

    def show_error_message(self, message):
        app = wx.App()
        dlg = wx.MessageDialog(None, message, "Error",
                               style=wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        app.MainLoop()

    # def _run_user_script(self):
    #     """运行用户脚本：优先使用配置驱动引擎，回退到script.py"""
    #     script_name = self.scriptName.replace("📝 ", "")
    #
    #     from ScriptEngine import ScriptEngine
    #     config = ScriptEngine.load_config(script_name)
    #     if config:
    #         try:
    #             engine = ScriptEngine(self, config)
    #             engine.run()
    #             return
    #         except Exception as e:
    #             print(f"配置驱动脚本执行失败: {e}")
    #             import traceback
    #             traceback.print_exc()
    #             return
    #
    #     import importlib.util
    #     script_path = os.path.join(
    #         os.path.dirname(os.path.abspath(__file__)),
    #         "user_scripts", script_name, "script.py"
    #     )
    #     if not os.path.exists(script_path):
    #         print(f"用户脚本不存在: {script_path}")
    #         return
    #     try:
    #         spec = importlib.util.spec_from_file_location(
    #             f"user_script_{script_name}", script_path)
    #         mod = importlib.util.module_from_spec(spec)
    #         spec.loader.exec_module(mod)
    #         class_name = "Script_" + "".join(
    #             c if c.isalnum() or c == "_" else "_" for c in script_name
    #         )
    #         script_cls = getattr(mod, class_name)
    #         instance = script_cls(self)
    #         instance.run()
    #     except Exception as e:
    #         print(f"运行用户脚本失败: {e}")
    #         import traceback
    #         traceback.print_exc()

    # 找当前的路径
    def get_resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

    def huifu_yijian_main(self):
        self._huifu_done = 0
        self.huifuFlag = True
        self.huifu_yijian(self.dm)
        wait_start = time.time()
        while self.huifuFlag:
            if time.time() - wait_start > 30:
                self.huifuFlag = False
                self._huifu_done = 0
                break
            time.sleep(0.1)

    # 一键恢复
    def huifu_yijian(self, dm):
        self.huifuFlag = True
        try:
            time.sleep(1)
            if self.overed:
                return
            while True:
                if self.check_stop_or_over():
                    return
                find_res = dm.FindPicEx(0, 0, 900, 590,
                             f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                             "", self.confidenceNum, 0)
                if find_res:
                    # 找到图片，解析坐标
                    pos = find_res.split("|")
                    pos_res = pos[0].split(",")
                    pics = f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}".split("|")
                    picSize = dm.GetPicSize(pics[int(pos_res[0])])
                    picSize = picSize.split(",")
                    picW, picH = picSize[0], picSize[1]
                    posX = int(pos_res[1]) + (int(picW) * 0.5)
                    posY = int(pos_res[2]) + (int(picH) * 0.5)
                    dm.MoveTo(int(posX), int(posY))
                    time.sleep(0.005)
                    dm.LeftClick()
                    break
            query_time = time.time()
            while True:
                if self.check_stop_or_over():
                    return
                if time.time() - query_time > 10:
                    print("一键恢复超时")
                    return
                find_res = dm.FindStrFastE(0, 0, 900, 580, '一键恢复', self.color_format, self.confidenceNum)
                find_str_result = find_res.split("|")
                if int(find_str_result[0]) < 0:
                    continue
                pos_res = find_str_result
                posX = pos_res[1]
                posY = pos_res[2]
                dm.MoveTo(int(posX), int(posY))
                time.sleep(0.5)
                dm.LeftClick()
                break
            time.sleep(1)
            query_time = time.time()
            while True:
                if self.check_stop_or_over():
                    return
                if time.time() - query_time > 10:
                    print("一键恢复超时")
                    return
                find_res = dm.FindPicEx(0, 0, 900, 590,
                             f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}",
                             "", self.confidenceNum, 0)
                if find_res:
                    # 找到图片，解析坐标
                    pos = find_res.split("|")
                    pos_res = pos[0].split(",")
                    pics = f"{self.get_resource_path('serveAssets/images/wujiang1.bmp')}|{self.get_resource_path('serveAssets/images/wujiang2.bmp')}".split("|")
                    picSize = dm.GetPicSize(pics[int(pos_res[0])])
                    picSize = picSize.split(",")
                    picW, picH = picSize[0], picSize[1]
                    posX = int(pos_res[1]) + (int(picW) * 0.5)
                    posY = int(pos_res[2]) + (int(picH) * 0.5)
                    dm.MoveTo(int(posX), int(posY))
                    time.sleep(0.005)
                    dm.LeftClick()
                    break
        finally:
            self._huifu_done += 1
            _expected = 1 + (1 if self.win1_dm else 0) + (1 if self.win2_dm else 0)
            if self._huifu_done >= _expected:
                self.huifuFlag = False
                self._huifu_done = 0
        
    
    # 自动找怪 （69 237 346 492）
    def auto_move_and_click(self, interval=0.5, timeout=30):
        x1, y1, x2, y2 = (69, 237, 214, 416)
        pic_names = f"{self.get_resource_path('serveAssets/images/gongji.bmp')}|{self.get_resource_path('serveAssets/images/gongji1.bmp')}|{self.get_resource_path('serveAssets/images/gongji2.bmp')}|{self.get_resource_path('serveAssets/images/gongji3.bmp')}"
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 生成随机位置
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)

            # 移动鼠标到随机位置
            self.dm.MoveTo(rand_x, rand_y)
            time.sleep(0.5)  # 移动后稍作停顿

            # 在区域内查找图片
            ret = self.find_pic_or_str(pic_names, self.gameLeftLocation, 0)
            if ret:
                # 移动鼠标到图片位置并点击
                self.dm.MoveTo(ret.x, ret.y)
                time.sleep(1)
                self.dm.LeftClick()
                return True  # 成功找到并点击

            time.sleep(interval)  # 等待下次查找

        print("超时未找到图片")
        return False  # 超时未找到

    def auto_move_and_click_team1(self, interval=0.5, timeout=30):
        x1, y1, x2, y2 = (69, 237, 214, 416)
        pic_names = f"{self.get_resource_path('serveAssets/images/gongji.bmp')}|{self.get_resource_path('serveAssets/images/gongji1.bmp')}|{self.get_resource_path('serveAssets/images/gongji2.bmp')}|{self.get_resource_path('serveAssets/images/gongji3.bmp')}"
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 生成随机位置
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)

            # 移动鼠标到随机位置
            self.win1_dm.MoveTo(rand_x, rand_y)
            time.sleep(0.5)  # 移动后稍作停顿

            # 在区域内查找图片
            ret = self.find_pic_or_str_team1(pic_names, self.gameLeftLocation,
                                             0)
            if ret:
                # 移动鼠标到图片位置并点击
                self.win1_dm.MoveTo(ret.x, ret.y)
                time.sleep(1)
                self.win1_dm.LeftClick()
                return True  # 成功找到并点击

            time.sleep(interval)  # 等待下次查找

        print("超时未找到图片")
        return False  # 超时未找到

    def auto_move_and_click_team2(self, interval=0.5, timeout=30):
        x1, y1, x2, y2 = (69, 237, 214, 416)
        pic_names = f"{self.get_resource_path('serveAssets/images/gongji.bmp')}|{self.get_resource_path('serveAssets/images/gongji1.bmp')}|{self.get_resource_path('serveAssets/images/gongji2.bmp')}|{self.get_resource_path('serveAssets/images/gongji3.bmp')}"
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 生成随机位置
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)

            # 移动鼠标到随机位置
            self.win2_dm.MoveTo(rand_x, rand_y)
            time.sleep(0.5)  # 移动后稍作停顿

            # 在区域内查找图片
            ret = self.find_pic_or_str_team2(pic_names, self.gameLeftLocation,
                                             0)
            if ret:
                # 移动鼠标到图片位置并点击
                self.win2_dm.MoveTo(ret.x, ret.y)
                time.sleep(1)
                self.win2_dm.LeftClick()
                return True  # 成功找到并点击

            time.sleep(interval)  # 等待下次查找

        print("超时未找到图片")
        return False  # 超时未找到

    # 退出当前副本
    def outScript(self, current=None):
        if self.overed:
            return
        if current is not None:
            self.waitFor(current, self.dituLocation)
        with condition:
            if self.stoped:
                condition.wait()
        time.sleep(0.1)
        find_queding_time = time.time()
        locationQueding = None
        while True:
            if self.scriptName == "官渡" and self.find_pic_or_str("官渡",
                                                                  self.dituLocation,
                                                                  0):
                break
            if self.scriptName == "魔镜" and self.find_pic_or_str("城西",
                                                                  self.dituLocation,
                                                                  0):
                break
            if self.scriptName == "黑风" and self.find_pic_or_str("五层",
                                                                  self.dituLocation,
                                                                  0):
                break
            if time.time() - find_queding_time > 30:
                break
            outX = 514 + self.locationX
            outY = 50 + self.locationY
            self.dm.MoveTo(int(outX), int(outY))
            time.sleep(0.1)
            self.dm.LeftClick()
            locationQueding = self.waitFor(
                f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
                self.gameLocation,
                3,
            )
            if locationQueding:
                break
        time.sleep(0.1)
        while locationQueding:
            if not self.find_pic_or_str(
                    f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
                    self.gameLocation,
                    0,
            ):
                break
            self.dm.MoveTo(locationQueding.x, locationQueding.y)
            time.sleep(0.1)
            self.dm.LeftClick()
            time.sleep(0.1)
            self.dm.LeftClick()
        huodetongbiLocation = self.waitFor("获得铜币", self.gameLeftLocation, 1)
        if huodetongbiLocation:
            self.dm.MoveTo(huodetongbiLocation.x, huodetongbiLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
        else:
            return

    # 清包
    def clearBag_team1(self):
        if self.overed:
            return
        time.sleep(1)
        bagPos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win1_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        chushou = self.waitFor_team1(
            f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}",
            self.gameBottomLocation,
            5,
        )
        if chushou:
            self.win1_dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(0.5)
        zise = self.waitFor_team1("紫色", self.gameBottomLocation, 5)
        if zise:
            self.win1_dm.MoveTo(int(zise.x + 3), int(zise.y + 3))
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(0.5)
        quedingchushou = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.win1_dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(4)
        bagPos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win1_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()

    # 清包
    def clearBag_team2(self):
        if self.overed:
            return
        time.sleep(30)
        # self.win2_dm.KeyPressChar('e')
        bagPos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win2_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        chushou = self.waitFor_team2(
            f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}",
            self.gameBottomLocation,
            5,
        )
        if chushou:
            self.win2_dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(0.5)
        zise = self.waitFor_team2("紫色", self.gameBottomLocation, 5)
        if zise:
            self.win2_dm.MoveTo(int(zise.x + 3), int(zise.y + 3))
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(1)
        quedingchushou = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.win2_dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(2)
        self.clickFlag = False
        time.sleep(4)
        bagPos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win2_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()

    # 清包
    def clearBag(self):
        if self.overed:
            return
        self.clickFlag = True
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        chushou = self.waitFor(f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}", self.gameBottomLocation, 5)
        if chushou:
            self.dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(1)
        zise = self.waitFor("紫色", self.gameBottomLocation, 5)
        if zise:
            self.dm.MoveTo(int(zise.x + 3), int(zise.y + 3))
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(1)
        quedingchushou = self.waitFor(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(4)
        self.clickFlag = False
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()

    # 清藏宝图
    def clear_hide_map(self):
        if self.overed:
            return
        self.clickFlag = True
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        chushou = self.waitFor(f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}",  self.gameBottomLocation, 5)
        if chushou:
            self.dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(1)
        zise = self.waitFor("藏宝图", self.gameBottomLocation, 5)
        if zise:
            self.dm.MoveTo(zise.x, zise.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(1)
        quedingchushou = self.waitFor(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        else:
            bagPos = self.waitFor(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
            return
        time.sleep(4)
        self.clickFlag = False
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()

    # 清藏宝图1
    def clear_hide_map_team1(self):
        if self.overed:
            return
        time.sleep(1)
        bagPos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win1_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        chushou = self.waitFor_team1(f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}",  self.gameBottomLocation, 5)
        if chushou:
            self.win1_dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(0.5)
        zise = self.waitFor_team1("藏宝图", self.gameBottomLocation, 5)
        if zise:
            self.win1_dm.MoveTo(zise.x, zise.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(0.5)
        quedingchushou = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.win1_dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()
        else:
            bagPos = self.waitFor_team1(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win1_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win1_dm.LeftClick()
        time.sleep(4)
        bagPos = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win1_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win1_dm.LeftClick()

    # 清藏宝图2
    def clear_hide_map_team2(self):
        if self.overed:
            return
        time.sleep(30)
        # self.win2_dm.KeyPressChar('e')
        bagPos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win2_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        chushou = self.waitFor_team2(f"{self.get_resource_path('serveAssets/images/chushou.bmp')}|{self.get_resource_path('serveAssets/images/chushou1.bmp')}", self.gameBottomLocation, 5)
        if chushou:
            self.win2_dm.MoveTo(chushou.x, chushou.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(0.5)
        zise = self.waitFor_team2("藏宝图", self.gameBottomLocation, 5)
        if zise:
            self.win2_dm.MoveTo(zise.x, zise.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(1)
        quedingchushou = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/quedingchushou.bmp"),
            self.gameBottomLocation,
            5,
        )
        if quedingchushou:
            self.win2_dm.MoveTo(quedingchushou.x, quedingchushou.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()
        else:
            bagPos = self.waitFor_team2(
                self.get_resource_path("serveAssets/images/beibao.bmp"),
                self.gameBottomLocation,
                5,
            )
            if bagPos:
                self.win2_dm.MoveTo(bagPos.x, bagPos.y)
                time.sleep(0.5)
                self.win2_dm.LeftClick()
        time.sleep(2)
        self.clickFlag = False
        time.sleep(4)
        bagPos = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.win2_dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.win2_dm.LeftClick()

    # 虎牛兔猴羊
    def new_zhengdian(self):
        if self.overed:
            return None
        print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
        zhengdian_hour = int(time.localtime().tm_hour) + 1
        with condition:
            if self.stoped:
                condition.wait()
        self.clear_info()
        time.sleep(0.5)
        self.huifu_yijian_main()
        time.sleep(1)
        self._zhengdian_early_waited = False
        # 提前飞到第一张随机地图，在 zhengdian_all_inview 中等待整点并直接搜索
        # 蛇+全打/全打：蛇时辰走路搜索蛇
        if self.zhengdianFloor in ["蛇+全打"] and self._is_snake_hour(zhengdian_hour):
            self.zhengdian_all_inview(zd_groups=self.she_groups, auto_combat_key="蛇", early_first=True)
        # 龙+全打/蛇+全打/全打：龙时辰走路搜索龙
        if self.zhengdianFloor in ["龙+全打", "蛇+全打"] and self._is_dragon_hour(zhengdian_hour):
            self.zhengdian_all_inview(zd_groups=self.long_groups, early_first=True)
        # 龙/蛇时辰：视野搜索普通整点，避免小绿人误打龙/蛇
        self.zhengdian_all_inview(zd_groups=self.normal_zd_groups_no_boss, early_first=True)
        time.sleep(0.5)
        self.zhengdian_flag = False
        if self.scriptName == "抢龙":
            return None
        if int(time.localtime().tm_hour) == 0:
            if self.after_zreo == "官渡":
                self.scriptName = "官渡"
                time.sleep(1)
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
                is_in_guandu = self.waitFor("官渡", self.dituLocation, 5)
                if not is_in_guandu:
                    time.sleep(1)
                    self.go_in_ditu(
                        "地图官渡",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/xuchang.bmp"),
                        "官渡",
                        "驿站城西",
                        "驿站许昌",
                        True,
                    )
                time.sleep(1)
                self.guanduWhile()
                return None
            elif self.after_zreo == "魔镜":
                self.scriptName = "魔镜"
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "驿站城西",
                    "",
                    True,
                )
                time.sleep(1)
                self.mojingWhile()
                return None
            elif self.after_zreo == "日常":
                self.scriptName = "日常"
                time.sleep(1)
                self.richangeScript()
                return None
            elif self.after_zreo == "49日常":
                self.scriptName = "49日常"
                time.sleep(1)
                self.richang49Script()
                return None
            elif self.after_zreo == "战魂+红+整点":
                self.scriptName = "战魂+红+整点"
                time.sleep(1)
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "驿站城西",
                    True,
                )
                time.sleep(2)
                self.guanduAndHongAndZd()
                return None
            elif self.after_zreo == "战魂+红+魔镜+整点":
                self.scriptName = "战魂+红+魔镜+整点"
                time.sleep(1)
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "驿站城西",
                    True,
                )
                time.sleep(2)
                self.mojingAndHongAndZd()
                return None
        if int(time.localtime().tm_hour) in [15,
                                             21] and self.after_zreo == "名将闯关":
            self.scriptName = "名将闯关"
            time.sleep(1)
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
            time.sleep(1)
            print("开始名将闯关")
            while True:
                has_mingjiang = self.mingjiangchuangguan()
                if not has_mingjiang:
                    break
            time.sleep(1)
            self.scriptName = "官渡"
            self.feiFb("副本曹操", True)
            time.sleep(1)
            self.guanduWhile()
        if self.scriptName == "官渡":
            time.sleep(1)
            # self.feiFb('副本曹操', True)
            self.go_in_ditu(
                "地图官渡",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "官渡",
                "驿站城西",
                "驿站许昌",
                True,
            )
            is_in_guandu = self.waitFor("官渡", self.dituLocation, 5)
            if not is_in_guandu:
                time.sleep(1)
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
            time.sleep(1)
            self.guanduWhile()
            return None
        elif self.scriptName == "魔镜" or self.scriptName == "测试":
            time.sleep(2)
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
            time.sleep(1)
            self.mojingWhile()
            return None
        elif self.scriptName == "龙岛":
            time.sleep(2)
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
            time.sleep(1)
            while True:
                if self.check_stop_or_over():
                    return
                hasLongDao = self.longdaoScript()
                if not hasLongDao:
                    break
            return None
        elif self.scriptName == "黑风":
            time.sleep(1)
            self.go_in_ditu(
                "地图五层",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "五层",
                "驿站城西",
                "",
                True,
            )
            self.heifengWhile()
            return None
        elif self.scriptName == "倭寇":
            time.sleep(1)
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "驿站城西",
                True,
            )
            time.sleep(2)
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/wokou.bmp')}|{self.get_resource_path('serveAssets/images/guaji/wokou1.bmp')}"
            )
            return None
        elif self.scriptName == "龙珠":
            time.sleep(1)
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "驿站城西",
                True,
            )
            time.sleep(2)
            self.longzhuWhile()
            return None
        elif self.scriptName == "老鼠":
            time.sleep(1)
            self.go_in_ditu(
                "地图碧水地穴",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "碧水地穴",
                "驿站襄阳",
                "",
                True,
            )
            time.sleep(2)
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/bishuishuxue.bmp')}|{self.get_resource_path('serveAssets/images/guaji/bishuishuxue1.bmp')}"
            )
            return None
        elif self.scriptName == "森罗殿":
            time.sleep(1)
            self.go_in_ditu(
                "地图野外西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "野外西",
                "驿站城西",
                "",
                True,
            )
            time.sleep(2)
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/senluodian.bmp')}|{self.get_resource_path('serveAssets/images/guaji/senluodian1.bmp')}"
            )
            return None
        elif self.scriptName == "挂机+整点":
            time.sleep(1)
            self.guajiAndzhengdianScript()
            return None
        return None

    def _has_zd_in_map(self, map_item, zd_groups):
        npc_count = len(map_item["delX"])
        xiaolvren_img = f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}"
        self.confidenceNum = 0.9
        xiaolvren_list = self._find_all_pic(xiaolvren_img, self.dituLocation)
        has_extra_xiaolvren = len(xiaolvren_list) > npc_count
        search_text = "|".join(zd_groups.keys())
        all_img_paths = []
        for img_list in zd_groups.values():
            all_img_paths.extend(img_list)
        search_images = "|".join(self.get_resource_path(p) for p in all_img_paths)
        ZD_COLOR = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.color_format = ZD_COLOR
        self.confidenceNum = 0.7
        has_zd_in_view = self.find_pic_or_str(search_text, self.gameBottomLocation, 0)
        if not has_zd_in_view:
            has_zd_in_view = self.find_pic_or_str(search_images, self.gameBottomLocation, 0)
        self.confidenceNum = 0.9
        if not has_extra_xiaolvren and not has_zd_in_view:
            return False
        return True

    def _wait_for_zhengdian_time(self):
        """等待整点时刻：分钟=0，秒=0或1"""
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            ct = time.localtime()
            if ct.tm_min == 0 and ct.tm_sec in [0, 1]:
                break
            time.sleep(0.1)

    def zhengdian_all_inview(self, zd_list=None, zd_groups=None, auto_combat_key=None, early_first=False):
        if zd_list is None:
            zd_list = self.zdList
        if zd_groups is None:
            zd_groups = self.normal_zd_groups_no_boss
        self.clear_info()
        shuffled = zd_list.copy()
        random.shuffle(shuffled)
        for i in range(len(shuffled)):
            last_item = shuffled[-1]
            shuffled = shuffled[:-1]
            is_fei = self.go_in_ditu(
                last_item["ditu"],
                last_item["city"],
                last_item["findAddress"],
                "",
                "",
                True,
            )
            if is_fei:
                if early_first and i == 0 and not self._zhengdian_early_waited:
                    # 首次调用第一张随机地图：等待整点，跳过小绿人检测
                    self._wait_for_zhengdian_time()
                    self._zhengdian_early_waited = True
                elif not self._has_zd_in_map(last_item, zd_groups):
                    continue
                self.find_zd_in_view(
                    last_item["findAddress"], zd_groups, auto_combat_key, last_item["ditu"], last_item["city"]
                )

    # 跑整点120
    def go_zhengdian(self):
        if self.overed:
            return
        print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
        self.clear_info()
        self.confidenceNum = 0.6
        if self.scriptName == "官渡" or self.scriptName == "测试":
            self.go_in_ditu(
                "地图老虎遗迹",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "九黎族遗迹",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xuluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xuluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xuluo2.bmp')}",
                f"{self.get_resource_path('serveAssets/images/zhengdian/luoxiang.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxiang1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxiang2.bmp')}",
            )
        elif self.scriptName in ["魔镜", "倭寇", "森罗殿"]:
            self.go_in_ditu(
                "地图老虎遗迹",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "九黎族遗迹",
                f"{self.get_resource_path('serveAssets/images/zhengdian/luoxiang.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxiang1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxiang2.bmp')}",
                "",
            )
        else:
            self.go_in_ditu(
                "地图老虎遗迹",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "九黎族遗迹",
                "",
                "",
                True,
            )
        self.confidenceNum = 0.9
        # self.go_in_ditu('地图老虎遗迹', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '九黎族遗迹', '', '')
        # time.sleep(0.5)
        # gc.collect()
        self.dm.MoveTo(int(900 - 900 * 0.167), int(580 * 0.137))
        time.sleep(0.5)
        self.dm.LeftClick()
        time.sleep(0.5)
        self.dm.LeftClick()
        time.sleep(0.5)
        self.huifu_yijian_main()
        time.sleep(1)
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            current_time = time.localtime()
            if (current_time.tm_min == 59 and current_time.tm_sec == 59) or (
                    current_time.tm_min == 0 and current_time.tm_sec == 0
            ):
                break
            time.sleep(1)  # 每秒钟检查一次
        # 进祭坛
        self.findAndClickPic(
            "九黎族遗迹",
            "九黎族祭坛",
            "九黎族祭坛",
            self.dituLocation,
            "九黎族祭坛",
            self.dituLocation,
            "0.187,0.137",
        )
        # 打老虎
        time.sleep(1)
        # 走路模式：小绿人预检+走路搜索；非走路模式：小绿人导航
        if self.zhengdianFloor == "走路":
            self.find_zd_in_view("九黎族祭坛", self.normal_zd_groups_no_boss, None, "地图老虎遗迹", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        else:
            self.find_zd_xiaolvren_v3("九黎族祭坛", 0, [], None, "地图老虎", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        time.sleep(0.5)
        # 去魔魂山
        self.go_in_ditu(
            "地图牛",
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiangyang.bmp"),
            "魔魂山",
            "",
            "",
        )
        if self.zhengdianFloor == "走路":
            self.find_zd_in_view("魔魂山", self.normal_zd_groups_no_boss, None, "地图牛", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        else:
            self.find_zd_xiaolvren_v3("魔魂山", 0, [], None, "地图牛", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        # 去魔谷西
        self.go_in_ditu(
            "地图羊",
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiangyang.bmp"),
            "魔谷西",
            "",
            "",
        )
        # 打羊
        time.sleep(1)
        # 魔谷西有2个NPC，需传入npc_count和npc_zones
        if self.zhengdianFloor == "走路":
            self.find_zd_in_view("魔谷西", self.normal_zd_groups_no_boss, None, "地图羊", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        else:
            self.find_zd_xiaolvren_v3("魔谷西", 2, [(int(856 + self.locationX), int(46 + self.locationY)), (int(857 + self.locationX), int(46 + self.locationY))], None, "地图羊", self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"))
        time.sleep(0.5)
        self.zhengdian_flag = False
        gc.collect()
        if int(time.localtime().tm_hour) == 0:
            if self.after_zreo == "官渡":
                self.scriptName = "官渡"
                time.sleep(1)
                self.feiFb("副本曹操", True)
                is_in_guandu = self.waitFor("官渡", self.dituLocation, 5)
                if not is_in_guandu:
                    time.sleep(1)
                    self.go_in_ditu(
                        "地图官渡",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/xuchang.bmp"),
                        "官渡",
                        "驿站城西",
                        "驿站许昌",
                        True,
                    )
                time.sleep(1)
                self.guanduWhile()
                return
            elif self.after_zreo == "魔镜":
                self.scriptName = "魔镜"
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "驿站城西",
                    "",
                    True,
                )
                time.sleep(1)
                self.mojingWhile()
                return
            elif self.after_zreo == "日常":
                self.scriptName = "日常"
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
                time.sleep(1)
                self.richangeScript()
                return
            elif self.after_zreo == "49日常":
                self.scriptName = "49日常"
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
                time.sleep(1)
                self.richang49Script()
                return
            elif self.after_zreo == "战魂+红+整点":
                self.scriptName = "战魂+红+整点"
                time.sleep(1)
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "驿站城西",
                )
                time.sleep(2)
                self.guanduAndHongAndZd()
                return
            elif self.after_zreo == "战魂+红+魔镜+整点":
                self.scriptName = "战魂+红+魔镜+整点"
                time.sleep(1)
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "驿站城西",
                )
                time.sleep(2)
                self.mojingAndHongAndZd()
                return
        self.confidenceNum = 0.6
        if self.scriptName == "官渡":
            # 回官渡
            # self.go_in_ditu('地图襄阳', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'), "", '')
            # self.findAndClickPic(
            # 	self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'),
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxu2.bmp')}",
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoyangyizhan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoyangyizhan.bmp')}",
            # 	self.gameBottomLocation,
            # 	'许昌',
            # 	self.dituLocation,
            # 	'0.16,0.129'
            # )
            self.go_in_ditu(
                "地图官渡",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "官渡",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
                f"{self.get_resource_path('serveAssets/images/zhengdian/luoxu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/luoxu2.bmp')}",
            )
            time.sleep(1)
            self.confidenceNum = 0.9
            self.guanduWhile()
        elif self.scriptName == "魔镜" or self.scriptName == "测试":
            # 回洛阳城西
            # self.go_in_ditu('地图襄阳', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'), "", '')
            # self.findAndClickPic(
            # 	self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'),
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan1.bmp')}",
            # 	self.gameBottomLocation,
            # 	'城西',
            # 	self.dituLocation,
            # 	'0.16,0.129'
            # )
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
                "",
            )
            time.sleep(1)
            self.confidenceNum = 0.9
            self.mojingWhile()
        elif self.scriptName == "倭寇":
            # self.go_in_ditu('地图襄阳', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'), "", '')
            # self.findAndClickPic(
            # 	self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'),
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan1.bmp')}",
            # 	self.gameBottomLocation,
            # 	'城西',
            # 	self.dituLocation,
            # 	'0.16,0.129'
            # )
            time.sleep(1)
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
                "",
            )
            time.sleep(2)
            self.confidenceNum = 0.9
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/wokou.bmp')}|{self.get_resource_path('serveAssets/images/guaji/wokou1.bmp')}"
            )
        elif self.scriptName == "龙珠":
            # self.go_in_ditu('地图襄阳', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'), "", '')
            # self.findAndClickPic(
            # 	self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'),
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan1.bmp')}",
            #
            # 	self.gameBottomLocation,
            # 	'城西',
            # 	self.dituLocation,
            # 	'0.16,0.129'
            # )
            time.sleep(1)
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
                "",
            )
            time.sleep(2)
            self.confidenceNum = 0.9
            self.longzhuWhile()
        elif self.scriptName == "老鼠":
            time.sleep(1)
            self.go_in_ditu(
                "地图碧水地穴",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                "碧水地穴",
                "",
                "",
            )
            time.sleep(2)
            self.confidenceNum = 0.9
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/bishuishuxue.bmp')}|{self.get_resource_path('serveAssets/images/guaji/bishuishuxue1.bmp')}"
            )
        elif self.scriptName == "森罗殿":
            # self.go_in_ditu('地图襄阳', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'), "", '')
            # self.findAndClickPic(
            # 	self.get_resource_path('serveAssets/images/zhengdian/xiangyangcheng.bmp'),
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
            # 	f"{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangyangyizhan1.bmp')}",
            # 	self.gameBottomLocation,
            # 	'城西',
            # 	self.dituLocation,
            # 	'0.16,0.129'
            # )
            time.sleep(1)
            self.go_in_ditu(
                "地图野外西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "野外西",
                f"{self.get_resource_path('serveAssets/images/zhengdian/xiangluo.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiangluo3.bmp')}",
                "",
            )
            time.sleep(2)
            self.confidenceNum = 0.9
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/senluodian.bmp')}|{self.get_resource_path('serveAssets/images/guaji/senluodian1.bmp')}"
            )
        elif self.scriptName == "挂机+整点":
            time.sleep(1)
            self.guajiAndzhengdianScript()

    # 跑整点49
    def go_zhengdian49(self):
        if self.overed:
            return
        print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
        zhengdian_hour = int(time.localtime().tm_hour) + 1
        self.clear_info()
        self.huifu_yijian_main()
        time.sleep(1)
        self._zhengdian_early_waited = False
        # 提前飞到第一张随机地图，在 zhengdian_all_inview 中等待整点并直接搜索
        # 49蛇+全打/49整点/49龙+全打：蛇时辰走路搜索蛇
        if self.zhengdianFloor in ["49蛇+全打", "49整点", "49龙+全打"] and self._is_snake_hour(zhengdian_hour):
            self.zhengdian_all_inview(zd_list=self.zd49List, zd_groups=self.she_groups, auto_combat_key="蛇", early_first=True)
        # 49蛇+全打/49龙+全打/49整点：龙时辰走路搜索龙
        if self.zhengdianFloor in ["49蛇+全打", "49龙+全打", "49整点"] and self._is_dragon_hour(zhengdian_hour):
            self.zhengdian_all_inview(zd_list=self.zd49List, zd_groups=self.long_groups, early_first=True)
        # 全部选项：走路搜索普通整点
        self.zhengdian_all_inview(zd_list=self.zd49List, zd_groups=self.normal_zd_groups, early_first=True)
        self.zhengdian_flag = False
        gc.collect()
        if int(time.localtime().tm_hour) == 0:
            if self.after_zreo == "魔镜":
                self.scriptName = "魔镜"
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "驿站城西",
                    "",
                    True,
                )
                time.sleep(1)
                self.mojingWhile()
                return
            elif self.after_zreo == "49日常":
                self.scriptName = "49日常"
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
                time.sleep(1)
                self.richang49Script()
                return
            elif self.after_zreo == "官渡":
                self.scriptName = "官渡"
                time.sleep(1)
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
                is_in_guandu = self.waitFor("官渡", self.dituLocation, 5)
                if not is_in_guandu:
                    time.sleep(1)
                    self.go_in_ditu(
                        "地图官渡",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/xuchang.bmp"),
                        "官渡",
                        "驿站城西",
                        "驿站许昌",
                        True,
                    )
                time.sleep(1)
                self.guanduWhile()
        if self.scriptName in ["倭寇", "龙珠"]:
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "",
            )
            if self.scriptName == "倭寇":
                time.sleep(2)
                self.guajiAndzhengdianScript(
                    f"{self.get_resource_path('serveAssets/images/guaji/wokou.bmp')}|{self.get_resource_path('serveAssets/images/guaji/wokou1.bmp')}"
                )
            elif self.scriptName == "龙珠":
                time.sleep(2)
                self.longzhuWhile()
        elif self.scriptName == "龙岛":
            time.sleep(2)
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
            time.sleep(1)
            while True:
                if self.check_stop_or_over():
                    return
                hasLongDao = self.longdaoScript()
                if not hasLongDao:
                    break
            return None
        elif self.scriptName == "森罗殿":
            time.sleep(1)
            self.go_in_ditu(
                "地图野外西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "野外西",
                "",
                "",
            )
            time.sleep(2)
            self.guajiAndzhengdianScript(
                f"{self.get_resource_path('serveAssets/images/guaji/senluodian.bmp')}|{self.get_resource_path('serveAssets/images/guaji/senluodian1.bmp')}"
            )
        elif self.scriptName == "官渡":
            time.sleep(1)
            self.go_in_ditu(
                "地图官渡",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "官渡",
                "驿站城西",
                "驿站许昌",
                True,
            )
            time.sleep(1)
            self.guanduWhile()
            return
        elif self.scriptName == "黑风":
            time.sleep(1)
            self.go_in_ditu(
                "地图五层",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "五层",
                "驿站城西",
                "",
                True,
            )
            time.sleep(1)
            self.heifengWhile()
        elif self.scriptName == "挂机+整点":
            time.sleep(1)
            self.guajiAndzhengdianScript()
        else:
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "",
                "",
            )
            time.sleep(1)
            if self.scriptName == "魔镜":
                self.mojingWhile()

    def clear_info(self):
        gc.collect()
        self.daZhengDianCount = 0
        self.dm.ClearDict(0)
        self.dm.DownCpu(30)
        self.dm.UnBindWindow()
        self.dm.BindWindow(self.click_hwnd, "gdi", "windows3", "windows", 0)
        self.dm.SetDict(0,
                        self.get_resource_path("serveAssets/fonts/common.txt"))

    def find_zd_in_view(self, base_image, zd_groups, auto_combat_key=None, ditu_name=None, city_img=None):
        ZD_COLOR = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        find_left_flag = False
        challenged_positions = []
        current_map = base_image
        CHALLENGED_EXPIRE = 30
        THRESHOLD_X = 15
        THRESHOLD_Y = 10
        search_text = "|".join(zd_groups.keys())
        all_img_paths = []
        for img_list in zd_groups.values():
            all_img_paths.extend(img_list)
        search_images = "|".join(self.get_resource_path(p) for p in all_img_paths)
        time.sleep(0.7)  #等待页面刷新整点

        def _is_challenged(pos):
            if pos is None:
                return False
            now = time.time()
            for cx, cy, ct, cm in challenged_positions:
                if cm == current_map and abs(pos.x - cx) <= THRESHOLD_X and abs(pos.y - cy) <= THRESHOLD_Y:
                    return True
            return False

        def _find_zd_str(text, region, tag):
            if self.overed:
                return
            x, y, w, h = region
            find_str_result = self.dm.FindStrFastE(
                int(x), int(y), int(w), int(h), text, self.color_format,
                self.confidenceNum
            )
            find_str_result = find_str_result.split("|")
            if int(find_str_result[0]) >= 0:
                pos_res = None
                if len(find_str_result) == 3:
                    pos_res = find_str_result
                elif len(find_str_result) > 3:
                    if int(find_str_result[1]) < int(
                            find_str_result[4]) and 0 in [0, 1]:
                        pos_res = find_str_result[:3]
                    else:
                        pos_res = find_str_result[3:6]
                idx = int(pos_res[0])
                texts = text.split("|")
                hit_text = texts[idx] if 0 <= idx < len(texts) else f"索引{idx}越界"
                posX = int(pos_res[1]) + 18
                posY = int(pos_res[2]) - 94
                return ResXy(posX, posY)
            return False

        def _find_zd_pic(image_path, region, tag):
            if self.overed:
                return
            x, y, w, h = region
            pos = self.dm.FindPicEx(int(x), int(y), int(w), int(h), image_path, "",
                                    self.confidenceNum, 0)
            if not pos:
                return False
            pos = pos.split("|")
            pos_res = pos[0].split(",")
            pics = image_path.split("|")
            idx = int(pos_res[0])
            hit_pic = pics[idx] if 0 <= idx < len(pics) else f"索引{idx}越界"
            picSize = self.dm.GetPicSize(pics[idx])
            picSize = picSize.split(",")
            picW, picH = picSize[0], picSize[1]
            posX = int(pos_res[1]) + (int(picW) * 0.5)
            posY = int(pos_res[2]) + (int(picH) * 0.5)
            self.dm.FreePic(image_path)
            return ResXy(int(posX), int(posY))

        just_attacked = False
        while True:
            if self.overed:
                return
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            now = time.time()
            challenged_positions = [
                (x, y, t, m) for x, y, t, m in challenged_positions
                if now - t < CHALLENGED_EXPIRE
            ]
            self.color_format = ZD_COLOR
            find_region = self.gameLeftLocation if not find_left_flag else self.gameRightFullLocation
            has_zd = _find_zd_str(search_text, find_region, "首次扫描-找字")
            if not has_zd:
                self.confidenceNum = 0.8
                has_zd = _find_zd_pic(search_images, find_region, "首次扫描-找图兜底")
            self.confidenceNum = 0.9
            if has_zd and not _is_challenged(has_zd):
                self.dm.KeyPressChar("left")
                self.color_format = ZD_COLOR
                
                sx_pos = _find_zd_str(search_text, find_region, "二次确认-找字")
                if not sx_pos:
                    self.confidenceNum = 0.8
                    sx_pos = _find_zd_pic(search_images, find_region, "二次确认-找图兜底")
                self.confidenceNum = 0.9
                if sx_pos and not _is_challenged(sx_pos):
                    result = self._try_attack_zd(sx_pos, base_image, auto_combat_key)
                    if result == "success":
                        self.daZhengDianCount += 1
                        print(f"打了第{self.daZhengDianCount}个整点")
                        just_attacked = True
                    elif result == "challenged":
                        challenged_positions.append((sx_pos.x, sx_pos.y, time.time(), current_map))
            if ditu_name and city_img:
                self._ensure_on_map(ditu_name, city_img, base_image)
            if just_attacked:
                just_attacked = False
                time.sleep(0.3)
                continue
            self.confidenceNum = 0.8
            left_x = random.randint(742, 758)
            rand_y = 80
            right_x = random.randint(859, 870)
            self.color_format = ZD_COLOR
            if not find_left_flag:
                if self.find_pic_or_str(
                        f"{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen2.bmp')}",
                        (717, 46, 761, 94),
                        0,
                ):
                    self.dm.MoveTo(right_x, rand_y)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    find_left_flag = True
                else:
                    self.dm.MoveTo(left_x, rand_y)
                    time.sleep(0.001)
                    self.dm.LeftClick()
            else:
                if self.find_pic_or_str(
                        f"{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen2.bmp')}",
                        (859, 41, 899, 96),
                        0,
                ):
                    self.confidenceNum = 0.9
                    break
                else:
                    self.dm.MoveTo(right_x, rand_y)
                    time.sleep(0.001)
                    self.dm.LeftClick()
            self.confidenceNum = 0.9
            time.sleep(0.6)

    # 在地图通过小绿人打整点
    def zhengdian_by_xiaolvren(self, base_image, find_dir, npc_posx=[],
                               npc_possy=[], order=1):
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 3)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren.bmp")
        picSize = self.dm.GetPicSize(xiaolvren)
        # print(picSize, 'picSize')
        picSize = picSize.split(",")
        picW, picH = picSize[0], picSize[1]
        xiaolvren_pos = self.dm.FindPicEx(
            int(x),
            int(y),
            int(w),
            int(h),
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp"),
            "",
            0.9,
            find_dir,
        )
        # print(xiaolvren_pos, 'xiaolvren_pos')
        if xiaolvren_pos:
            xiaolvren_pos = xiaolvren_pos.split("|")
            # print(xiaolvren_pos, 'xiaolvren_pos')
            xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos,order)
            xiaolvren_pos_color = "07d307"
            for item in xiaolvren_pos:
                if self.overed:
                    return
                new_item = item.split(",")
                # print(new_item[1], new_item[2], base_image, 'new_item[1]')
                if npc_posx != 0 and int(new_item[1]) in npc_posx and int(
                        new_item[2]) in npc_possy:
                    continue
                item_x = int(new_item[1]) + int(int(picW) * 0.5)
                item_y = int(new_item[2]) + int(int(picH) * 0.5)
                if self.dm.CmpColor(item_x, item_y, xiaolvren_pos_color,
                                    0.7) == 1:
                    self.hasZhengDianCount -= 1
                    continue
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                self.dm.MoveTo(item_x, item_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.001)
                self.dm.MoveTo(int(item_x - 200), item_y)
                time.sleep(0.1)
                self.color_format = "b@ffff00-000000|fff200-000000"
                is_zhengdian = None
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and self.dm.CmpColor(item_x,
                                                                   item_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.8
                    time.sleep(0.001)
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/dianwei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dianwei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("npc")
                        self.confidenceNum = 0.9
                        break
                    self.confidenceNum = 0.9
                    time.sleep(0.01)
                    if change_color_time > 0 and time.time() - change_color_time > 5:
                        print("超时")
                        break
                    # self.confidenceNum = 0.7
                    # time.sleep(0.6)
                    # if self.find_pic(
                    # 		f"{self.get_resource_path('serveAssets/images/zhengdian/da.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da4.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da5.bmp')}",
                    # 		self.gameBottomLocation, 0):
                    # 	time.sleep(0.001)
                    # 	if self.zhengdianFloor != '龙' and self.find_pic(
                    # 			f"{self.get_resource_path('serveAssets/images/zhengdian/long.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long4.bmp')}",
                    # 			self.gameBottomLocation, 0):
                    # 		print('龙')
                    # 		self.confidenceNum = 0.9
                    # 		break
                    # 	else:
                    # 		self.confidenceNum = 0.9
                    # 		print('找到了打就打图片')
                    # 		hasZhengDian = True
                    # 		break
                    # self.confidenceNum = 0.9
                    is_zhengdian = self.find_str("打就打1",
                                                 self.gameBottomLocation, 1)
                    if is_zhengdian:
                        # print('找到了打就打1文字')
                        # print(is_zhengdian.x, is_zhengdian.y)
                        self.hasZhengDianCount -= 1
                        self.dm.MoveTo(int(is_zhengdian.x + 5),
                                       int(is_zhengdian.y + 5))
                        time.sleep(0.001)
                        self.dm.LeftClick()
                        hasZhengDian = True
                        break
                # is_zhengdian = self.find_str('打就打2', self.gameBottomLocation, 1)
                # if is_zhengdian:
                # 	print('找到了打就打2文字')
                # 	print(is_zhengdian.x, is_zhengdian.y)
                # 	self.hasZhengDianCount -= 1
                # 	self.dm.MoveTo(int(is_zhengdian.x + 5), int(is_zhengdian.y + 5))
                # 	time.sleep(0.001)
                # 	self.dm.LeftClick()
                # 	hasZhengDian = True
                # 	break
                if hasZhengDian:

                    # print(f"{base_image}有整点")
                    # find_time = time.time()
                    # dajiuda_pos = None
                    # self.color_format = 'b@0ff000-000000|ffff00-000000|00ff00-000000'
                    # while True:
                    # 	dajiuda_pos = self.find_pic(
                    # 		f"{self.get_resource_path('serveAssets/images/zhengdian/da.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da5.bmp')}",
                    # 		self.gameBottomLocation, 0)
                    # 	if dajiuda_pos:
                    # 		print('点了打就打图片')
                    # 		print(dajiuda_pos.x)
                    # 		print(dajiuda_pos.y)
                    # 		break
                    # 	dajiuda_pos = self.find_str('打就打1', self.gameBottomLocation, 0)
                    # 	if dajiuda_pos:
                    # 		dajiuda_pos.x = dajiuda_pos.x + 5
                    # 		dajiuda_pos.y = dajiuda_pos.y + 5
                    # 		print('点了打就打1文字')
                    # 		print(dajiuda_pos.x)
                    # 		print(dajiuda_pos.y)
                    # 		break
                    # 	dajiuda_pos = self.find_str('打就打2', self.gameBottomLocation, 0)
                    # 	if dajiuda_pos:
                    # 		dajiuda_pos.x = dajiuda_pos.x + 5
                    # 		dajiuda_pos.y = dajiuda_pos.y + 5
                    # 		print('点了打就打2文字')
                    # 		print(dajiuda_pos.x)
                    # 		print(dajiuda_pos.y)
                    # 		break
                    # 	time.sleep(0.1)
                    # 	if self.confidenceNum > 0.7:
                    # 		self.confidenceNum = self.confidenceNum - 0.1
                    # 	if time.time() - find_time > 4:
                    # 		print('没找到打就打')
                    # 		break
                    self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
                    # self.confidenceNum = 0.9
                    # if dajiuda_pos:
                    # 	self.dm.MoveTo(dajiuda_pos.x, dajiuda_pos.y)
                    # 	time.sleep(0.001)
                    # 	self.dm.LeftClick()
                    queryTime = time.time()
                    while True:
                        with condition:
                            if self.stoped:
                                condition.wait()
                        if time.time() - queryTime > 5:
                            zhengdianHas = False
                            break
                        self.confidenceNum = 0.6
                        if self.find_pic(
                                self.get_resource_path(
                                    "serveAssets/images/zdzd111.bmp"),
                                self.gameLocation,
                                0,
                        ):
                            zhengdianHas = True
                            break
                        yourendaLocation = self.find_str("被挑战",
                                                         self.gameBottomLocation,
                                                         0)
                        if yourendaLocation:
                            zhengdianHas = False
                            print("被挑战")
                            break
                        yourendaLocation1 = self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/beitiaozhan.bmp')}",
                            self.gameBottomLocation,
                            0,
                        )
                        if yourendaLocation1:
                            zhengdianHas = False
                            print("被挑战")
                            break
                        bucunzai = self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/bucunzai.bmp')}",
                            self.gameBottomLocation,
                            0,
                        )
                        if bucunzai:
                            zhengdianHas = False
                            print("不存在")
                            break
                        self.confidenceNum = 0.9
                    if zhengdianHas:
                        self.waitFor(base_image, self.dituLocation)
                        self.daZhengDianCount += 1
                        time.sleep(0.1)
                        print(f"打了第{self.daZhengDianCount}个整点")
                else:
                    print("没找到整点")
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            del xiaolvren_pos

        else:
            return

    def _find_all_str(self, text, region):
        x, y, w, h = region
        result = self.dm.FindStrFastE(
            int(x), int(y), int(w), int(h), text,
            self.color_format, self.confidenceNum
        )
        result = result.split("|")
        if int(result[0]) < 0:
            return []
        positions = []
        for i in range(0, len(result), 3):
            if i + 2 < len(result) and int(result[i]) >= 0:
                positions.append(ResXy(int(result[i + 1]), int(result[i + 2])))
        return positions

    def _find_all_pic(self, image_path, region):
        x, y, w, h = region
        result = self.dm.FindPicEx(
            int(x), int(y), int(w), int(h), image_path, "",
            self.confidenceNum, 0
        )
        if not result:
            return []
        items = result.split("|")
        pics = image_path.split("|")
        positions = []
        for item in items:
            parts = item.split(",")
            pic_idx = int(parts[0])
            pic_size = self.dm.GetPicSize(pics[pic_idx]).split(",")
            cx = int(parts[1]) + int(int(pic_size[0]) * 0.5)
            cy = int(parts[2]) + int(int(pic_size[1]) * 0.5)
            positions.append(ResXy(cx, cy))
        return positions

    def _merge_deduplicate_sort(self, positions, attacked_set, exclude_zones,
                                 threshold=20):
        screen_cx = self.locationX + 400
        screen_cy = self.locationY + 300
        merged = {}
        for p in positions:
            skip = False
            for ax, ay in attacked_set:
                if abs(p.x - ax) <= threshold and abs(p.y - ay) <= threshold:
                    skip = True
                    break
            if skip:
                continue
            for ex, ey in exclude_zones:
                if abs(p.x - ex) <= threshold and abs(p.y - ey) <= threshold:
                    skip = True
                    break
            if skip:
                continue
            key = (p.x // threshold, p.y // threshold)
            if key not in merged:
                merged[key] = p
        result = list(merged.values())
        result.sort(key=lambda p: (p.x - screen_cx) ** 2 + (p.y - screen_cy) ** 2)
        return result

    def _try_attack_zd(self, target, base_image, auto_combat_key):
        self.dm.MoveTo(int(target.x + 5), int(target.y + 5))
        time.sleep(0.001)
        self.dm.LeftClick()
        self.color_format = "b@ffff00-000000|fff200-000000"
        zhengdian_btn = self.waitFor("打就打1", self.gameBottomLocation, 3)
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        if not zhengdian_btn:
            zhengdian_btn = self.waitFor("打就打", self.gameBottomLocation, 0.3)
            if not zhengdian_btn:
                return "no_btn"
        self.dm.MoveTo(int(zhengdian_btn.x + 5), int(zhengdian_btn.y + 5))
        time.sleep(0.001)
        self.dm.LeftClick()
        if auto_combat_key is not None and auto_combat_key in self.combat_auto_scenes:
            self._start_combat_auto(clear_enemy_keys=[auto_combat_key])
        combat_result = self._wait_combat_result(base_image, auto_combat_key)
        if auto_combat_key is not None and auto_combat_key in self.combat_auto_scenes:
            self._stop_combat_auto()
        return combat_result

    def _wait_combat_result(self, base_image, auto_combat_key):
        query_time = time.time()
        while True:
            if self.check_stop_or_over():
                return "timeout"
            with condition:
                if self.stoped:
                    condition.wait()
            if time.time() - query_time > 5:
                return "timeout"
            if self.find_pic(
                    f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                    self.gameLocation, 0):
                self.waitFor(base_image, self.dituLocation, 600)
                time.sleep(0.1)
                self.confidenceNum = 0.9
                return "success"
            if self.find_pic(
                    f"{self.get_resource_path('serveAssets/images/zhengdian/beitiaozhan.bmp')}",
                    self.gameBottomLocation, 0) or self.find_str("挑战小字",
                                                         self.gameBottomLocation,
                                                         0):
                self.confidenceNum = 0.9
                print("被挑战")
                return "challenged"
            if self.find_str("不存在",self.gameBottomLocation,0):
                self.confidenceNum = 0.9
                print("不存在")
                return "not_exist"
            self.confidenceNum = 0.9

    def _is_dragon_hour(self, hour=None):
        if hour is None:
            hour = int(time.localtime().tm_hour)
        return hour in [3, 7, 11, 15, 19, 23]

    def _is_snake_hour(self, hour=None):
        if hour is None:
            hour = int(time.localtime().tm_hour)
        return hour in [2, 6, 10, 14, 18, 22]

    # V3辅助方法：统计小地图上小绿人数量
    def _count_xiaolvren(self):
        try:
            xiaolvren_bmp = f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}"
            dx, dy, dw, dh = self.dituLocation
            result = self.dm.FindPicEx(dx, dy, dw, dh, xiaolvren_bmp, "", 0.7, 0)
            if not result:
                return 0
            return len(result.split("|"))
        except:
            return 0

    # V3辅助方法：等小绿人计数稳定（连续两次一致）
    def _wait_xiaolvren_stable(self, max_attempts=5):
        prev = -1
        for _ in range(max_attempts):
            time.sleep(0.3)
            cur = self._count_xiaolvren()
            if cur == prev:
                return cur
            prev = cur
        return self._count_xiaolvren()

    # V3辅助方法：将delX/delY转换为NPC坐标列表（用于模糊排除）
    def _get_npc_zones_from_delxy(self, delX, delY):
        zones = []
        for i in range(len(delX)):
            x = delX[i]
            y = delY[i] if i < len(delY) else delY[-1]
            zones.append((x, y))
        return zones

    # V3辅助方法：判断坐标是否在NPC区域附近（模糊匹配，阈值threshold像素）
    def _is_near_npc_zone(self, x, y, npc_zones, threshold=2):
        for zx, zy in npc_zones:
            if abs(x - zx) <= threshold and abs(y - zy) <= threshold:
                return True
        return False

    # V3辅助方法：走路一步，返回(新方向flag, 是否到达右边界)
    def _walk_one_step(self, find_left_flag):
        left_x = random.randint(742, 758)
        rand_y = 80
        right_x = random.randint(859, 870)
        reached_edge = False
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.confidenceNum = 0.6
        if not find_left_flag:
            if self.find_pic_or_str(
                    f"{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen2.bmp')}",
                    (717, 46, 761, 94), 0):
                self.dm.MoveTo(right_x, rand_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                new_flag = True
            else:
                self.dm.MoveTo(left_x, rand_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                new_flag = False
        else:
            if self.find_pic_or_str(
                    f"{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaobairen1.bmp')}",
                    (859, 41, 899, 96), 0):
                reached_edge = True
                new_flag = find_left_flag
            else:
                self.dm.MoveTo(right_x, rand_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                new_flag = find_left_flag
        self.confidenceNum = 0.9
        time.sleep(0.6)
        return new_flag, reached_edge

    def _ensure_on_map(self, ditu_name, city_img, break_address):
        if self.waitFor(break_address, self.dituLocation, 0.5):
            return
        time.sleep(0.5)
        self.go_in_ditu(ditu_name, city_img, break_address, "", "", is_fei=False)

    # V3小绿人模式：小绿人计数预检+导航+攻击确认，用于普通整点
    # 点击小绿人导航到整点位置，等"打就打1"按钮确认可攻击（避免误打Boss）
    # npc_count：该地图固定NPC数量，小绿人<=npc_count时判定无整点
    # npc_zones：NPC坐标列表，用于模糊排除（左上角坐标）
    def find_zd_xiaolvren_v3(self, base_image, npc_count=0, npc_zones=None,
                              auto_combat_key=None,
                              ditu_name=None, city_img=None):
        if npc_zones is None:
            npc_zones = []
        self.confidenceNum = 0.6
        base_image_res = self.waitFor(base_image, self.dituLocation, 3)
        if not base_image_res:
            return
        attacked_set = set()
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren.bmp")
        pic_size = self.dm.GetPicSize(xiaolvren).split(",")
        pic_w, pic_h = int(pic_size[0]), int(pic_size[1])
        no_progress_rounds = 0
        max_no_progress = 3
        while True:
            if self.overed or self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            self.waitFor(base_image, self.dituLocation)
            green_count = self._count_xiaolvren()
            if green_count <= npc_count:
                time.sleep(0.5)
                if self._count_xiaolvren() <= npc_count:
                    self.confidenceNum = 0.9
                    return
            green_result = self.dm.FindPicEx(
                int(x), int(y), int(w), int(h), xiaolvren, "", 0.9, 0
            )
            target_dots = []
            if green_result:
                all_dots = green_result.split("|")
                for item in all_dots:
                    parts = item.split(",")
                    tl_x = int(parts[1])
                    tl_y = int(parts[2])
                    if self._is_near_npc_zone(tl_x, tl_y, npc_zones, threshold=10):
                        continue
                    skip = False
                    for ax, ay in attacked_set:
                        if abs(tl_x - ax) <= 20 and abs(tl_y - ay) <= 20:
                            skip = True
                            break
                    if skip:
                        continue
                    click_x = tl_x + pic_w // 2
                    click_y = tl_y + pic_h // 2
                    target_dots.append((click_x, click_y, tl_x, tl_y))
            if not target_dots:
                no_progress_rounds += 1
                if no_progress_rounds >= max_no_progress:
                    # print(f"{base_image}: 连续{max_no_progress}轮无目标小绿人，退出")
                    self.confidenceNum = 0.9
                    return
                time.sleep(0.5)
                continue
            no_progress_rounds = 0
            screen_cx = self.locationX + 400
            screen_cy = self.locationY + 300
            target_dots.sort(
                key=lambda d: (d[0] - screen_cx) ** 2 + (d[1] - screen_cy) ** 2)
            hit_any = False
            for click_x, click_y, tl_x, tl_y in target_dots:
                self.dm.MoveTo(click_x, click_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.3)
                self.dm.MoveTo(int(click_x - 200), click_y)
                time.sleep(0.1)
                if ditu_name and city_img:
                    self._ensure_on_map(ditu_name, city_img, base_image)

                start_time = time.time()
                change_color_time = 0
                found_btn = False
                npc_images = (
                    f"{self.get_resource_path('serveAssets/images/zhengdian/dianwei.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/dianwei1.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/liwu.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/liwu1.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/liwu2.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/dengmi.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/dengmi1.bmp')}"
                    f"|{self.get_resource_path('serveAssets/images/zhengdian/dengmi2.bmp')}"
                )

                while time.time() - start_time < 8:
                    if self.find_pic(npc_images, self.gameBottomLocation, 0):
                        print(f"点击到NPC，跳过")
                        break

                    if change_color_time == 0 and self.dm.CmpColor(
                            click_x, click_y, "07d307", 0.7) == 1:
                        change_color_time = time.time()
                    if change_color_time > 0 and time.time() - change_color_time > 5:
                        break

                    self.color_format = "b@ffff00-000000|fff200-000000"
                    zhengdian_btn = self.find_str("打就打1", self.gameBottomLocation, 1)
                    self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
                    if zhengdian_btn:
                        self.dm.MoveTo(int(zhengdian_btn.x + 5), int(zhengdian_btn.y + 5))
                        time.sleep(0.001)
                        self.dm.LeftClick()
                        found_btn = True
                        break
                    zhengdian_btn1 = self.find_str("打就打", self.gameBottomLocation, 1)
                    if zhengdian_btn1:
                        self.dm.MoveTo(int(zhengdian_btn1.x + 5), int(zhengdian_btn1.y + 5))
                        time.sleep(0.001)
                        self.dm.LeftClick()
                        found_btn = True
                        break

                    time.sleep(0.05)

                if not found_btn:
                    attacked_set.add((tl_x, tl_y))
                    continue
                if auto_combat_key is not None and auto_combat_key in self.combat_auto_scenes:
                    self._start_combat_auto(clear_enemy_keys=[auto_combat_key])
                combat_ok = self._wait_combat_result(base_image, auto_combat_key)
                if auto_combat_key is not None and auto_combat_key in self.combat_auto_scenes:
                    self._stop_combat_auto()
                if combat_ok == "success":
                    self.daZhengDianCount += 1
                    print(f"打了第{self.daZhengDianCount}个整点")
                    self.waitFor(base_image, self.dituLocation)
                    self._wait_xiaolvren_stable()
                    attacked_set.clear()
                    hit_any = True
                    break
                else:
                    attacked_set.add((tl_x, tl_y))
            if not hit_any:
                # print(f"{base_image}: 所有小绿人已尝试但未找到可打整点，退出")
                self.confidenceNum = 0.9
                return

    # 攻城开始
    def go_gongcheng(self):
        is_fei = self.go_in_ditu(
            "地图野外北",
            self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"),
            "野外北",
            "",
            "",
            True,
        )
        if is_fei:
            self.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                      [845, 794, 761, 740],
                                                      [48, 42, 44], 1)
            is_in_bibotan = self.waitFor("野外北", self.dituLocation, 5)
            if is_in_bibotan:
                self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                          [845, 794, 761, 740],
                                                          [48, 42, 44], 1)
                is_in_bibotan1 = self.waitFor("野外北", self.dituLocation, 5)
                if is_in_bibotan1:
                    self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(0.5)
                    self.zhengdian_by_xiaolvren_for_gongcheng("野外北", 0,
                                                              [845, 794, 761,
                                                               740],
                                                              [48, 42, 44], 1)
            time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图野外西",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            "野外西",
            "",
            "",
            True,
        )
        if is_fei:
            self.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0, [853], [45],
                                                      1)
            is_in_bibotan = self.waitFor("野外西", self.dituLocation, 5)
            if is_in_bibotan:
                self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0, [853],
                                                          [45], 1)
                is_in_bibotan1 = self.waitFor("野外西", self.dituLocation, 5)
                if is_in_bibotan1:
                    self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(0.5)
                    self.zhengdian_by_xiaolvren_for_gongcheng("野外西", 0,
                                                              [853], [45], 1)
            time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图万花谷",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            "万花谷",
            "",
            "",
            True,
        )
        if is_fei:
            self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
            is_in_bibotan = self.waitFor("万花谷", self.dituLocation, 5)
            if is_in_bibotan:
                self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
                is_in_bibotan1 = self.waitFor("万花谷", self.dituLocation, 5)
                if is_in_bibotan1:
                    self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(0.5)
                    self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0,
                                                              [], 1)
            time.sleep(0.5)
        while self.find_str("魔军", self.gameBottomLocation, 0):
            mojun_loc = self.find_str("魔军", self.gameBottomLocation, 0)
            if mojun_loc:
                self.dm.MoveTo(mojun_loc.x, mojun_loc.y)
                time.sleep(0.001)
                self.dm.LeftClick()
            gongcheng_loc = self.waitFor("攻城", self.gameBottomLocation, 5)
            if gongcheng_loc:
                self.dm.MoveTo(gongcheng_loc.x, gongcheng_loc.y)
                time.sleep(0.001)
                self.dm.LeftClick()
            zdzd_loc = self.waitFor(
                self.get_resource_path("serveAssets/images/zdzd111.bmp"),
                self.gameBottomLocation,
                5,
            )
            if zdzd_loc:
                self.waitFor("万花谷", self.dituLocation, 50)
                time.sleep(1)

    # 在地图通过小绿人打整点（循环检测版本）
    def zhengdian_by_xiaolvren_for_gongcheng(self, base_image, find_dir,
                                             npc_posx=[], npc_possy=[],
                                             order=1):
        if npc_posx is None:
            npc_posx = [0]
        if npc_possy is None:
            npc_possy = []
        if self.overed:
            return
        base_image_res = self.waitFor(base_image, self.dituLocation, 5)
        if not base_image_res:
            return f"不在{base_image}"
        x, y, w, h = self.dituLocation
        xiaolvren = self.get_resource_path(
            "serveAssets/images/zhengdian/xiaolvren2.bmp")
        picSize = self.dm.GetPicSize(xiaolvren)
        picSize = picSize.split(",")
        picW, picH = int(picSize[0]), int(picSize[1])
        xiaolvren_pos_color = "07d307"
        if base_image not in self.invalid_xiaolvren_dots:
            self.invalid_xiaolvren_dots[base_image] = set()
        attacked_set = self.invalid_xiaolvren_dots[base_image]
        no_progress_rounds = 0
        max_no_progress = 3

        while True:
            if self.overed:
                return
            with condition:
                if self.stoped:
                    condition.wait()
                if self.overed:
                    return

            self.waitFor(base_image, self.dituLocation)
            xiaolvren_pos = self.dm.FindPicEx(
                int(x),
                int(y),
                int(w),
                int(h),
                xiaolvren,
                "",
                0.7,
                find_dir,
            )

            target_dots = []
            if xiaolvren_pos:
                all_dots = xiaolvren_pos.split("|")
                all_dots = self.sort_array_by_second_value(all_dots, order)
                for item in all_dots:
                    parts = item.split(",")
                    tl_x = int(parts[1])
                    tl_y = int(parts[2])
                    if npc_posx != 0 and tl_x in npc_posx and tl_y in npc_possy:
                        continue
                    skip = False
                    for ax, ay in attacked_set:
                        if abs(tl_x - ax) <= 20 and abs(tl_y - ay) <= 20:
                            skip = True
                            break
                    if skip:
                        continue
                    click_x = tl_x + picW // 2
                    click_y = tl_y + picH // 2
                    if self.dm.CmpColor(click_x, click_y, xiaolvren_pos_color,
                                        0.7) == 1:
                        continue
                    target_dots.append((click_x, click_y, tl_x, tl_y))

            if not target_dots:
                no_progress_rounds += 1
                if no_progress_rounds >= max_no_progress:
                    self.confidenceNum = 0.9
                    return
                time.sleep(0.5)
                continue

            no_progress_rounds = 0
            hit_any = False
            for click_x, click_y, tl_x, tl_y in target_dots:
                if self.overed:
                    return
                hasZhengDian = False
                change_color_time = 0
                find_zhengdian_time = time.time()
                self.dm.MoveTo(click_x, click_y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.001)
                self.dm.MoveTo(int(click_x - 200), click_y)
                time.sleep(0.1)
                while True:
                    if time.time() - find_zhengdian_time > 10:
                        print("超时10s")
                        if base_image == "野外北":
                            self.check_line()
                        break
                    # if not self.find_str(base_image, self.dituLocation, 0):
                    # 	break
                    if change_color_time == 0 and self.dm.CmpColor(click_x,
                                                                   click_y,
                                                                   xiaolvren_pos_color,
                                                                   0.7) == 1:
                        change_color_time = time.time()
                    time.sleep(0.01)
                    self.confidenceNum = 0.6
                    time.sleep(0.001)
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("npc")
                        self.confidenceNum = 0.9
                        break
                    self.confidenceNum = 0.9
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan3.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):  
                        hasZhengDian = True
                        print("野外怪物")
                        self.confidenceNum = 0.9
                        break
                    if self.find_str("进入", self.gameBottomLocation, 0):
                        print("副本npc")
                        self.confidenceNum = 0.9
                        break
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/liwu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/liwu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/liwu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("财神爷")
                        self.click_image(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/liwu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/liwu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/liwu2.bmp')}",
                            0.8,
                            self.gameBottomLocation,
                        )
                        self.confidenceNum = 0.9
                        break
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/dengmi.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dengmi1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dengmi2.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        print("灯谜")
                        self.click_image(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/dengmi.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dengmi1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dengmi2.bmp')}",
                            0.8,
                            self.gameBottomLocation,
                        )
                        time.sleep(1)
                        self.dm.MoveTo(252, 346)
                        time.sleep(0.001)
                        self.dm.LeftClick()
                        self.confidenceNum = 0.9
                        break
                    self.confidenceNum = 0.9
                    time.sleep(0.01)
                    if change_color_time > 0 and time.time() - change_color_time > 5:
                        print("超时")
                        break
                    self.confidenceNum = 0.6
                    time.sleep(0.6)
                    if self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/gongcheng.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng3.bmp')}",
                            self.gameBottomLocation,
                            0,
                    ):
                        self.confidenceNum = 0.9
                        hasZhengDian = True
                        break
                    self.confidenceNum = 0.9
                    is_zhengdian = self.waitFor("攻城", self.gameBottomLocation,
                                                0.6)
                    if is_zhengdian:
                        self.confidenceNum = 0.9
                        hasZhengDian = True
                        break
                    is_zhengdian = self.waitFor("挑战", self.gameBottomLocation,
                                                0.6)
                    if is_zhengdian:
                        self.confidenceNum = 0.9
                        hasZhengDian = True
                        print("野外怪物")
                        break
                    del is_zhengdian
                if not hasZhengDian:
                    attacked_set.add((tl_x, tl_y))
                    continue
                find_time = time.time()
                dajiuda_pos = None
                while True:
                    dajiuda_pos = self.find_pic(
                        f"{self.get_resource_path('serveAssets/images/zhengdian/gongcheng.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/gongcheng3.bmp')}",
                        self.gameBottomLocation,
                        0,
                    )
                    if dajiuda_pos:
                        break
                    dajiuda_pos = self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/tiaozhan3.bmp')}",
                            self.gameBottomLocation,
                            0,
                    )
                    if dajiuda_pos:
                        break
                    dajiuda_pos = self.find_str("攻城",
                                                self.gameBottomLocation, 0)
                    if dajiuda_pos:
                        break
                    dajiuda_pos = self.find_str("挑战",
                                                self.gameBottomLocation, 0)
                    if dajiuda_pos:
                        break
                    time.sleep(0.3)
                    if self.confidenceNum > 0.7:
                        self.confidenceNum = self.confidenceNum - 0.1
                    if time.time() - find_time > 4:
                        print("没找到攻城怪物")
                        break
                self.confidenceNum = 0.9
                if dajiuda_pos:
                    self.dm.MoveTo(int(dajiuda_pos.x + 10),
                                   int(dajiuda_pos.y + 3))
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    queryTime = time.time()
                    while True:
                        with condition:
                            if self.stoped:
                                condition.wait()
                        if time.time() - queryTime > 8:
                            zhengdianHas = False
                            break
                        if self.find_pic(
                                self.get_resource_path(
                                    "serveAssets/images/zdzd.bmp"),
                                self.gameLocation,
                                0,
                        ):
                            zhengdianHas = True
                            break
                        self.confidenceNum = 0.6
                        yourendaLocation = self.find_str("点击",
                                                         self.gameBottomLocation,
                                                         0)
                        if yourendaLocation:
                            self.dm.MoveTo(yourendaLocation.x,
                                           yourendaLocation.y)
                            time.sleep(0.001)
                            self.dm.LeftClick()
                            zhengdianHas = False
                            break
                        yourendaLocation1 = self.find_pic(
                            f"{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
                            self.gameBottomLocation,
                            0,
                        )
                        if yourendaLocation1:
                            self.dm.MoveTo(yourendaLocation1.x,
                                           yourendaLocation1.y)
                            time.sleep(0.001)
                            self.dm.LeftClick()
                            zhengdianHas = False
                            break
                        self.confidenceNum = 0.9
                    del dajiuda_pos
                    if zhengdianHas:
                        self.waitFor(base_image, self.dituLocation)
                        time.sleep(0.1)
                        self.guanDuCount += 1
                        print(f"打完了{self.guanDuCount}个怪物")
                        hit_any = True
                    if hit_any:
                        break
                else:
                    attacked_set.add((tl_x, tl_y))

            if not hit_any:
                self.confidenceNum = 0.9
                return

    # 清妖
    def clear_yao(self):
        is_fei = self.go_in_ditu(
            "地图万花谷",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            "万花谷",
            "",
            "",
            True,
        )
        if is_fei:
            self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
            is_in_bibotan = self.waitFor("万花谷", self.dituLocation, 5)
            if is_in_bibotan:
                self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0, [], 1)
                is_in_bibotan1 = self.waitFor("万花谷", self.dituLocation, 5)
                if is_in_bibotan1:
                    self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(0.5)
                    self.zhengdian_by_xiaolvren_for_gongcheng("万花谷", 0, 0,
                                                              [], 1)
            time.sleep(0.5)
        self.findAndClickPic(
            "万花谷",
            "嵩山",
            "嵩山",
            self.dituLocation,
            "嵩山",
            self.dituLocation,
            "730,78",
        )
        self.zhengdian_by_xiaolvren_for_gongcheng("嵩山", 0,
                                                      [740,742],
                                                      [43], 1)
        is_in_bibotan = self.waitFor("嵩山", self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng("嵩山", 0,
                                                      [740,742],
                                                      [43], 1)
            is_in_bibotan1 = self.waitFor("嵩山", self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng("嵩山", 0,
                                                      [740,742],
                                                      [43], 1)
        time.sleep(0.5)
        self.findAndClickPic(
            "嵩山",
            self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"),
            self.dituLocation,
            "887,56",
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"), 0,
                                                      [865],
                                                      [52], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"), 0,
                                                      [865],
                                                      [52], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/songshanding.bmp"), 0,
                                                      [865],
                                                      [52], 1)
        time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图洛水河",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"),
            "",
            "",
            True,
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"), 0,
                                                      [],
                                                      [], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"), 0,
                                                      [],
                                                      [], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/luoshuihe.bmp"), 0,
                                                      [],
                                                      [], 1)
        time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图虎牢关内",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"),
            "",
            "",
            True,
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"), 0,
                                                      [785],
                                                      [43], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"), 0,
                                                      [785],
                                                      [43], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"), 0,
                                                      [785],
                                                      [43], 1)
        time.sleep(0.5)
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/qingyao/hulaoguannei.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"),
            self.dituLocation,
            "744,73",
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"), 0,
                                                      [832,764,856,826,828],
                                                      [50,52,53,61,], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"), 0,
                                                      [832,764,856],
                                                      [50,52,53], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"), 0,
                                                      [832,764,856],
                                                      [50,52,53], 1)
        time.sleep(0.5)
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/qingyao/hulaoguan.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/xiaocun.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/xiaocun.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/qingyao/xiaocun.bmp"),
            self.dituLocation,
            "750,65",
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(f"{self.get_resource_path('serveAssets/images/qingyao/xiaocun.bmp')}|{self.get_resource_path('serveAssets/images/qingyao/hulaoguan.bmp')}", 0,
                                                      [849,783],
                                                      [45,50], 1)
        is_in_bibotan = self.waitFor(f"{self.get_resource_path('serveAssets/images/qingyao/xiaocun.bmp')}|{self.get_resource_path('serveAssets/images/qingyao/hulaoguan.bmp')}", self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(f"{self.get_resource_path('serveAssets/images/qingyao/xiaocun.bmp')}|{self.get_resource_path('serveAssets/images/qingyao/hulaoguan.bmp')}", 0,
                                                      [849,783],
                                                      [45,50], 1)
            is_in_bibotan1 = self.waitFor(f"{self.get_resource_path('serveAssets/images/qingyao/xiaocun.bmp')}|{self.get_resource_path('serveAssets/images/qingyao/hulaoguan.bmp')}", self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/xiaocun.bmp"), 0,
                                                      [849,783],
                                                      [45,50], 1)
        time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图荒村",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"),
            "",
            "",
            True,
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"), 0,
                                                      [745,817],
                                                      [47], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"), 0,
                                                      [745,817],
                                                      [47], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/huangcun.bmp"), 0,
                                                      [745,817],
                                                      [47], 1)
        time.sleep(0.5)
        is_fei = self.go_in_ditu(
            "地图御花园",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"),
            "",
            "",
            True,
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"), 0,
                                                      [780,861],
                                                      [46], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"), 0,
                                                      [780,861],
                                                      [46], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"), 0,
                                                      [780,861],
                                                      [46], 1)
        time.sleep(0.5)
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/qingyao/yuhuayuan.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"),
            self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"),
            self.dituLocation,
            "808,59",
        )
        self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"), 0,
                                                      [756,765],
                                                      [48,49], 1)
        is_in_bibotan = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"), self.dituLocation, 5)
        if is_in_bibotan:
            self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"), 0,
                                                      [765],
                                                      [49], 1)
            is_in_bibotan1 = self.waitFor(self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"), self.dituLocation, 5)
            if is_in_bibotan1:
                self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.zhengdian_by_xiaolvren_for_gongcheng(self.get_resource_path("serveAssets/images/qingyao/mudanyuan.bmp"), 0,
                                                      [765],
                                                      [49], 1)
        time.sleep(0.5)
    # 换线
    def check_line(self, line="二线"):
        if not self.line:
            return
        print(f"换{line}")
        xian_loc = self.waitFor(
            self.get_resource_path("serveAssets/images/xian.bmp"),
            self.gameLocation)
        if xian_loc:
            self.dm.MoveTo(xian_loc.x, xian_loc.y)
            time.sleep(0.001)
            self.dm.LeftClick()
        self.dm.MoveTo(xian_loc.x, int(xian_loc.y + 30))
        while not self.find_str(line, self.gameLocation, 0):
            if self.overed:
                return
            for i in range(4):
                if line in ["一线", "二线", "三线", "四线", "五线"]:
                    self.dm.WheelUp()
                    time.sleep(0.06)
                else:
                    self.dm.WheelDown()
                    time.sleep(0.06)
            time.sleep(0.4)
        checkLine_loc = self.waitFor(line, self.gameLocation, 5)
        if checkLine_loc:
            self.dm.MoveTo(checkLine_loc.x, checkLine_loc.y)
            time.sleep(0.001)
            self.dm.LeftClick()

    def check_line1(self, line="二线"):
        if not self.line:
            return
        xian_loc = self.waitFor_team1(
            self.get_resource_path("serveAssets/images/xian.bmp"),
            self.gameLocation)
        if xian_loc:
            self.win1_dm.MoveTo(xian_loc.x, xian_loc.y)
            time.sleep(0.001)
            self.win1_dm.LeftClick()
        self.win1_dm.MoveTo(xian_loc.x, int(xian_loc.y + 30))
        while not self.find_str_team1(line, self.gameLocation, 0):
            if self.overed:
                return
            for i in range(4):
                if line in ["一线", "二线", "三线", "四线", "五线"]:
                    self.win1_dm.WheelUp()
                    time.sleep(0.06)
                else:
                    self.win1_dm.WheelDown()
                    time.sleep(0.06)
            time.sleep(0.4)
        checkLine_loc = self.waitFor_team1(line, self.gameLocation, 5)
        if checkLine_loc:
            self.win1_dm.MoveTo(checkLine_loc.x, checkLine_loc.y)
            time.sleep(0.001)
            self.win1_dm.LeftClick()

    def check_line2(self, line="二线"):
        if not self.line:
            return
        xian_loc = self.waitFor_team2(
            self.get_resource_path("serveAssets/images/xian.bmp"),
            self.gameLocation)
        if xian_loc:
            self.win2_dm.MoveTo(xian_loc.x, xian_loc.y)
            time.sleep(0.001)
            self.win2_dm.LeftClick()
        self.win2_dm.MoveTo(xian_loc.x, int(xian_loc.y + 30))
        while not self.find_str_team2(line, self.gameLocation, 0):
            if self.overed:
                return
            for i in range(4):
                if line in ["一线", "二线", "三线", "四线", "五线"]:
                    self.win2_dm.WheelUp()
                    time.sleep(0.06)
                else:
                    self.win2_dm.WheelDown()
                    time.sleep(0.06)
            time.sleep(0.4)
        checkLine_loc = self.waitFor_team2(line, self.gameLocation, 5)
        if checkLine_loc:
            self.win2_dm.MoveTo(checkLine_loc.x, checkLine_loc.y)
            time.sleep(0.001)
            self.win2_dm.LeftClick()

    # 重新设置大漠跟字库
    def set_dict(self):
        time.sleep(0.5)
        self.dm.SetDict(0, self.get_resource_path(
            "serveAssets/fonts/common.txt"))  # 字库文件路径
        time.sleep(0.5)

    def sort_array_by_second_value(self, arr, order):
        """
        根据数组中每个元素的第二个值进行排序。

        参数:
        arr (list): 包含字符串元素的数组，每个元素格式为"0,123,654"
        order (int): 排序方向，1表示降序，2表示升序

        返回:
        list: 排序后的数组
        """

        # 定义排序键函数，提取每个元素的第二个值
        def key_func(item):
            return int(item.split(",")[1])

        # 根据order参数决定排序顺序
        reverse_order = order == 1

        # 使用sorted函数进行排序
        sorted_arr = sorted(arr, key=key_func, reverse=reverse_order)
        return sorted_arr

    # 跑图
    def go_in_ditu(
            self,
            find_address,
            address_pos_city,
            break_address,
            yizhan_name1,
            yizhan_name2,
            is_fei=False,
    ):
        if self.overed:
            return
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        time.sleep(0.5)
        # self.dm.KeyPressChar('m')
        address_pos_city_pos = None
        begin_time = time.time()
        while True:
            if time.time() - begin_time > 600:
                break
            self.confidenceNum = 0.8
            address_pos_city_pos = self.find_pic_or_str(address_pos_city,
                                                        self.gameLocation, 0)
            if address_pos_city_pos:
                self.confidenceNum = 0.9
                break
            self.confidenceNum = 0.9
            self.dm.KeyPressChar("m")
            # self.waitFor(self.get_resource_path('serveAssets/images/tu.bmp'), self.gameLocation)
            # time.sleep(0.05)
            # self.dm.MoveTo(int(self.locationX + 736), int(self.locationY + 120))
            # time.sleep(0.05)
            # self.dm.LeftClick()
            time.sleep(0.5)
        # self.dm.MoveTo(int(self.locationX + 736), int(self.locationY + 120))
        # time.sleep(0.05)
        # self.dm.LeftClick()
        self.confidenceNum = 0.9
        self.dm.MoveTo(address_pos_city_pos.x, address_pos_city_pos.y)
        time.sleep(0.3)
        self.dm.LeftClick()
        if find_address in ["地图绿林路", "地图落日峰", "地图碧波潭",
                            "地图祭坛"]:
            fei_pos = self.waitFor(
                f"{self.get_resource_path('serveAssets/images/zhengdian/fei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei3.bmp')}",
                self.gameBottomLocation,
                5,
            )
            if not fei_pos:
                self.dm.KeyPressChar("m")
                return False
            self.dm.MoveTo(fei_pos.x, fei_pos.y)
            find_fei_time = time.time()
            while not self.find_pic_or_str(find_address,
                                           self.gameBottomLocation, 0):
                if self.overed:
                    return
                if time.time() - find_fei_time > 10:
                    self.dm.KeyPressChar("m")
                    return False
                self.click_image(
                    f"{self.get_resource_path('serveAssets/images/zhengdian/closezd.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/closezd1.bmp')}",
                    0.7,
                    self.gameLocation,
                )
                for i in range(4):
                    self.dm.WheelDown()
                    time.sleep(0.06)
                time.sleep(0.4)
            for i in range(4):
                self.dm.WheelDown()
                time.sleep(0.06)
            time.sleep(0.4)
        is_find_address = self.waitFor(find_address, self.gameLocation, 3)
        self.click_image(
            f"{self.get_resource_path('serveAssets/images/zhengdian/closezd.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/closezd1.bmp')}",
            0.7,
            self.gameLocation,
        )
        if not is_find_address:
            self.click_image(address_pos_city, 0.8, self.gameLocation)
            is_find_address1 = self.waitFor(find_address, self.gameLocation, 3)
            if not is_find_address1 and find_address != "地图山洞三层":
                return False
        if not is_fei:
            go_pos = self.fing_fei_in_image_or_str(
                find_address,
                self.gameLocation,
                (0, 5, 150, 20),
                f"{self.get_resource_path('serveAssets/images/zhengdian/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang3.bmp')}",
            )
            if go_pos:
                self.dm.MoveTo(go_pos.x, go_pos.y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.05)
                self.dm.LeftClick()
                time.sleep(0.5)
            if yizhan_name1:
                self.confidenceNum = 0.6
                yizhan_name1_pos = self.waitFor(yizhan_name1,
                                                self.gameBottomLocation, 80)
                self.confidenceNum = 0.9
                if yizhan_name1_pos:
                    self.dm.MoveTo((int(yizhan_name1_pos.x)),
                                   int(yizhan_name1_pos.y))
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(3)
            if yizhan_name2 != "":
                self.confidenceNum = 0.6
                yizhan_name2_pos = self.waitFor(yizhan_name2,
                                                self.gameBottomLocation, 80)
                self.confidenceNum = 0.9
                if yizhan_name2_pos:
                    self.dm.MoveTo((int(yizhan_name2_pos.x)),
                                   int(yizhan_name2_pos.y))
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(1)
            self.waitFor(break_address, self.dituLocation, 200)
        else:
            find_fei_time = time.time()
            region = (0, 5, 180, 20)
            if find_address == "地图徐州":
                find_address = "地图官渡"
                region = (0, -18, 180, 38)
            if find_address == "地图野外北":
                find_address = "地图毒龙潭"
                region = (0, -18, 180, 38)
            if find_address == "地图山洞三层":
                find_address = "地图恶龙洞"
                region = (0, 21, 180, 0)
            while True:
                if time.time() - find_fei_time > 10:
                    self.dm.KeyPressChar("m")
                    return False
                fei_pos = self.fing_fei_in_image_or_str(
                    find_address,
                    self.gameLocation,
                    region,
                    f"{self.get_resource_path('serveAssets/images/zhengdian/fei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei3.bmp')}",
                )
                if fei_pos:
                    while True:
                        if self.find_pic_or_str(break_address,
                                                self.dituLocation, 0):
                            break
                        self.dm.MoveTo(fei_pos.x, fei_pos.y)
                        time.sleep(0.05)
                        self.dm.LeftClick()
                        time.sleep(1)
                        if time.time() - find_fei_time > 10:
                            self.dm.KeyPressChar("m")
                            return False
                    return True

    # 飞副本
    def feiFb(self, image_path, isJy):
        if self.overed:
            return
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        # 打开副本
        time.sleep(1.5)
        # self.dm.KeyPressChar('z')
        begin_time = time.time()
        while not self.find_pic_or_str(
                f"{self.get_resource_path('serveAssets/images/jingyin.bmp')}|{self.get_resource_path('serveAssets/images/jingyin1.bmp')}",
                self.gameLocation,
                0,
        ):
            if time.time() - begin_time > 600:
                break
            self.dm.KeyPressChar("z")
            # self.waitFor(self.get_resource_path('serveAssets/images/tu.bmp'), self.gameLocation)
            # time.sleep(0.05)
            # self.dm.MoveTo(int(self.locationX + 607), int(self.locationY + 50))
            # time.sleep(0.5)
            # self.dm.LeftClick()
            time.sleep(0.5)
        # self.dm.MoveTo(int(self.locationX + 607), int(self.locationY + 50))
        # time.sleep(0.5)
        # self.dm.LeftClick()
        # time.sleep(1)
        if isJy:
            is_click_fb = self.click_image(
                f"{self.get_resource_path('serveAssets/images/jingyin.bmp')}|{self.get_resource_path('serveAssets/images/jingyin1.bmp')}",
                0.7,
                self.gameLocation,
            )
            if not is_click_fb:
                is_fei = self.feiFb(image_path, isJy)
                return is_fei
            findPerTime = time.time()
            while True:
                if time.time() - findPerTime > 10:
                    self.dm.KeyPressChar("z")
                    return False
                if self.overed:
                    return
                fei_pos = self.fing_fei_in_image_or_str(
                    image_path,
                    self.gameLocation,
                    (0, 5, 120, 20),
                    f"{self.get_resource_path('serveAssets/images/fubenfei.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei1.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei2.bmp')}",
                )
                if fei_pos:
                    break
            if fei_pos:
                while True:
                    if not self.find_pic_or_str(image_path, self.gameLocation,
                                                0):
                        break
                    self.dm.MoveTo(fei_pos.x, fei_pos.y)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(1)
        else:
            self.click_image(
                f"{self.get_resource_path('serveAssets/images/putong.bmp')}|{self.get_resource_path('serveAssets/images/putong1.bmp')}",
                0.7,
                self.gameLocation,
            )
            time.sleep(0.5)
            self.dm.MoveTo(449, 224)
            # downTalk = self.waitFor(
            # 	f"{self.get_resource_path('serveAssets/images/downFb.bmp')}|{self.get_resource_path('serveAssets/images/downFb1.bmp')}|{self.get_resource_path('serveAssets/images/downFb2.bmp')}|{self.get_resource_path('serveAssets/images/downFb3.bmp')}|{self.get_resource_path('serveAssets/images/downFb4.bmp')}",
            # 	(
            # 		self.locationX,
            # 		self.locationY,
            # 		int(self.locationX + int(self.locationWidth * 0.75)),
            # 		self.locationHeight,
            # 	),
            # 	10
            # )
            # if not downTalk:
            # 	return
            while not self.find_str(image_path, self.gameLocation, 0):
                if self.overed:
                    return
                for i in range(4):
                    self.dm.WheelDown()
                    time.sleep(0.06)

                time.sleep(0.4)
            time.sleep(0.5)
            self.dm.MoveTo(449, 224)
            for i in range(4):
                self.dm.WheelDown()
                time.sleep(0.06)
            time.sleep(1)
            findPerTime = time.time()
            while True:
                if self.check_stop_or_over():
                    return
                if time.time() - findPerTime > 10:
                    return
                self.confidenceNum = 0.6
                fei_pos = self.fing_fei_in_image_or_str(
                    image_path,
                    self.gameLocation,
                    (0, 5, 120, 20),
                    f"{self.get_resource_path('serveAssets/images/fubenfei.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei1.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei2.bmp')}",
                )
                self.confidenceNum = 0.9
                if fei_pos:
                    break
            if fei_pos:
                while True:
                    if not self.find_pic_or_str(image_path, self.gameLocation,
                                                0):
                        break
                    self.dm.MoveTo(fei_pos.x, fei_pos.y)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(1)
        return True

    # 找图并且点击
    def click_image(self, image_path, image_confidence, image_region,
                    find_dir=0):
        if self.overed:
            return
        image_locations = self.find_pic_or_str(image_path, image_region,
                                               find_dir)
        if image_locations:
            with condition:
                if self.stoped:
                    condition.wait()
                if self.overed:
                    return
            self.dm.MoveTo(image_locations.x, image_locations.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            return True
        else:
            return False

    def click_image_team1(self, image_path, image_confidence, image_region,
                          find_dir=0):
        if self.overed:
            return
        image_locations = self.find_pic_or_str_team1(image_path, image_region,
                                                     find_dir)
        if image_locations:
            with condition:
                if self.stoped:
                    condition.wait()
                if self.overed:
                    return
            self.win1_dm.MoveTo(image_locations.x, image_locations.y)
            time.sleep(0.001)
            self.win1_dm.LeftClick()
            return True
        else:
            return False

    def click_image_team2(self, image_path, image_confidence, image_region,
                          find_dir=0):
        if self.overed:
            return
        image_locations = self.find_pic_or_str_team2(image_path, image_region,
                                                     find_dir)
        if image_locations:
            with condition:
                if self.stoped:
                    condition.wait()
                if self.overed:
                    return
            self.win2_dm.MoveTo(image_locations.x, image_locations.y)
            time.sleep(0.001)
            self.win2_dm.LeftClick()
            return True
        else:
            return False

    # 找一样的字，点击最左边的图
    def click_image_with_min_x(self, image_path, image_region, image_path2,
                               find_dir=0):
        if self.overed:
            return
        types = "serveAssets" in image_path
        target = None
        if not types:
            target = self.find_str(image_path, image_region, find_dir)
            if target:
                target.x = target.x + random.randint(10, 35)
                target.y = target.y + 5
        else:
            target = self.find_pic(image_path, image_region, find_dir)
        if not target:
            return False
        yjian = random.randint(35, 55) if not types else 0
        if "zdzd" in image_path2:
            self.dm.MoveTo(target.x, int(target.y - yjian))
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(self.click_delay)
            self.dm.MoveTo(1, 1)
        else:
            self.dm.MoveTo(target.x, target.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.2)
            self.dm.MoveTo(1, 1)
        self.clickBTime = time.time()
        self.clickBX = target.x
        self.clickBy = target.y
        return True

    def click_image_with_min_x1(self, image_path, image_region, image_path2,
                                find_dir=0):
        if self.overed:
            return
        types = "serveAssets" in image_path
        target = None
        if not types:
            target = self.find_str(image_path, image_region, find_dir)
        else:
            target = self.find_pic(image_path, image_region, find_dir)
        if not target:
            return False
        target_x = target.x
        target_y = target.y
        if "zdzd" in image_path2:
            self.dm.MoveTo(target.x, target.y)
            time.sleep(0.001)
            self.dm.LeftDoubleClick()
            self.dm.MoveTo(target.x + 200, target.y + 200)
        else:
            self.dm.MoveTo(target.x, target.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            self.dm.MoveTo(target.x + 200, target.y + 200)
        self.clickBTime = time.time()
        self.clickBX = target.x
        self.clickBy = target.y
        return True

    # 等待图片出现
    def waitFor(self, image_path, image_region, timeout=None):
        if self.overed:
            return
        start_time = time.time()
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            target = self.find_pic_or_str(image_path, image_region, 0)
            if target:
                break
            if timeout is not None:
                if time.time() - start_time > timeout:
                    return False
            # if time.time() - start_time > 600:
            #     print(
            #         '等待时间超过十分钟')
            #     self.dm.Capture(
            #         0, 0,
            #         self.locationWidth,
            #         self.locationHeight,
            #         f"wait_for_{image_path}_more_than_10_minutes.png")
            #     self.refresh_view()
            #     start_time = time.time()
            time.sleep(0.1)
        return target

    # 刷新操作
    def refresh_view(self):
        if self.scriptName in ["官渡", "黑风", "魔镜", "矿产", "测试"]:
            print("开始刷新")
            self.guajiFlag = False
            self.refreshFlag = True
            self.teamFlag = False
            gc.collect()
            self.dm.ClearDict(0)
            self.dm.UnBindWindow()
            self.dm.DownCpu(30)
            target_window_title = self.frame.game_name
            target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
            hwnds = self.dm.EnumWindow(0, target_window_title,
                                       target_window_class, 1 + 2)
            hwnds = hwnds.split(",")
            hwnd = 0
            for item in hwnds:
                if self.overed:
                    return
                if item and self.dm.GetWindowTitle(
                        int(item)) == target_window_title:
                    hwnd = int(item)
                    break
            bind_result = self.dm.BindWindow(hwnd, "dx2", "windows3", "windows",
                                             0)
            if bind_result == 1:
                print("准备刷新")
                time.sleep(0.1)
            else:
                print("未找到主窗口，请检查输入的游戏名称是否正确！")
            self.confidenceNum = 0.6
            refresh_pos = self.waitFor(
                self.get_resource_path("serveAssets/images/refresh.bmp"),
                (0, 0, 900, 200),
            )
            self.confidenceNum = 0.9
            self.dm.MoveTo(refresh_pos.x, refresh_pos.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            # self.dm.SetWindowState(hwnd, 1)
            time.sleep(0.5)
            self.dm.KeyPressChar("F5")
            time.sleep(0.5)
            self.dm.KeyPress(116)
            time.sleep(5)
            self.dm.UnBindWindow()
            time.sleep(5)
            self.findGame()
            in_game_pos = self.waitFor(
                self.get_resource_path("serveAssets/images/in_game.bmp"),
                self.gameBottomLocation,
            )
            self.dm.MoveTo(in_game_pos.x, in_game_pos.y)
            time.sleep(2)
            self.dm.LeftClick()
            self.waitFor(
                self.get_resource_path("serveAssets/images/mhlogo.bmp"),
                self.gameLocation,
            )
            time.sleep(6)
            checkRolePos = self.waitFor(
                self.get_resource_path("serveAssets/images/checkRole.bmp"),
                self.gameLocation,
            )
            self.dm.MoveTo(checkRolePos.x, checkRolePos.y)
            checkCount = int(
                self.team_leader_pos) - 1 if self.team_leader_pos else 0
            if checkCount > 0:
                for i in range(checkCount):
                    time.sleep(1.5)
                    self.dm.LeftClick()
            time.sleep(1.5)
            self.dm.MoveTo(440, 370)
            time.sleep(0.5)
            self.dm.LeftClick()
            self.waitFor(
                self.get_resource_path("serveAssets/images/xiulian.bmp"),
                self.gameLocation,
            )
            time.sleep(3)
            self.check_line(self.line)
            time.sleep(2)
            if self.teammate1_name or self.teammate2_name:
                self.dm.KeyPressChar("t")
                self.check_team()
                print("组队完成")
                self.dm.KeyPressChar("t")
                self.teamFlag = True
            self.refreshFlag = False
            self.hasRefresh = True
            if self.scriptName == "测试":
                self.scriptName = "官渡"
            self.run()

    # 在两个区域找图，如果有一个区域没找到图片，就点击位置，请出队伍

    def check_team(self):
        self.click_image(
            self.get_resource_path("serveAssets/images/quxiao.bmp"),
            0.8,
            self.gameBottomLocation,
        )
        role_list_pos = self.waitFor(
            f"{self.get_resource_path('serveAssets/images/roleList.bmp')}|{self.get_resource_path('serveAssets/images/roleList1.bmp')}",
            self.gameLocation,
        )
        self.dm.MoveTo(role_list_pos.x, role_list_pos.y)
        time.sleep(1)
        self.dm.LeftClick()
        lv_pos = self.waitFor(
            self.get_resource_path("serveAssets/images/lv.bmp"),
            self.gameLocation)
        self.dm.MoveTo(lv_pos.x, lv_pos.y)
        time.sleep(1)
        self.dm.LeftClick()
        yaoqing_pos = self.waitFor(
            self.get_resource_path("serveAssets/images/yaoqing.bmp"),
            self.gameLocation)
        self.dm.MoveTo(yaoqing_pos.x, yaoqing_pos.y)
        for i in range(10):
            time.sleep(0.2)
            self.dm.LeftClick()
        time.sleep(5)
        self.yaoqingFlag = True
        myteam_pos = self.waitFor(
            self.get_resource_path("serveAssets/images/myteam.bmp"),
            self.gameLocation)
        self.dm.MoveTo(myteam_pos.x, myteam_pos.y)
        time.sleep(1)
        self.dm.LeftClick()
        time.sleep(2)
        team1_loc = self.waitForTwo(
            self.get_resource_path("serveAssets/images/team_mate1.bmp"),
            self.get_resource_path("serveAssets/images/team_mate2.bmp"),
            self.team1_loc,
            self.team1_loc,
            3,
        )
        if not team1_loc:
            self.dm.MoveTo(410, 310)
            time.sleep(1)
            self.dm.LeftClick()
            time.sleep(1)
            self.dm.MoveTo(yaoqing_pos.x, yaoqing_pos.y)
            time.sleep(0.2)
            self.dm.LeftClick()
        team2_loc = self.waitForTwo(
            self.get_resource_path("serveAssets/images/team_mate1.bmp"),
            self.get_resource_path("serveAssets/images/team_mate2.bmp"),
            self.team2_loc,
            self.team2_loc,
            3,
        )
        if not team2_loc:
            self.dm.MoveTo(410, 310)
            time.sleep(1)
            self.dm.LeftClick()
            time.sleep(1)
            self.dm.MoveTo(yaoqing_pos.x, yaoqing_pos.y)
            time.sleep(0.2)
            self.dm.LeftClick()
        if not team1_loc or not team2_loc:
            self.check_team()

    # 等待图片出现
    def waitFor_team1(self, image_path, image_region, timeout=None):
        if self.overed:
            return
        start_time = time.time()
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            target = self.find_pic_or_str_team1(image_path, image_region, 0)
            if target:
                break
            if timeout is not None:
                if time.time() - start_time > timeout:
                    return False
            time.sleep(0.1)
        return target

    # 等待图片出现
    def waitFor_team2(self, image_path, image_region, timeout=None):
        if self.overed:
            return
        start_time = time.time()
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            target = self.find_pic_or_str_team2(image_path, image_region, 0)
            if target:
                break
            if timeout is not None:
                if time.time() - start_time > timeout:
                    return False
            time.sleep(0.1)
        return target

    # 等待两张图片出现
    def waitForTwo(
            self,
            image1_path,
            image2_path,
            image_region1,
            image_region2=None,
            timeout=None,
            find_dir=1,
    ):
        if self.overed:
            return
        start_time = time.time()
        res = ""
        if image_region2 is None:
            image_region2 = image_region1
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            xy = self.find_pic_or_str(image1_path, image_region1, find_dir)
            if xy:
                res = "first"
                return res
            xy2 = self.find_pic_or_str(image2_path, image_region2, find_dir)
            if xy2:
                res = "second"
                return res
            if timeout is not None:
                if time.time() - start_time > timeout:
                    return False
            time.sleep(0.2)

    # 等待图片1出现，一直点击图2
    def waitForAAndClickB1(self, find_text, image_pathB, find_region,
                           image_regionB=None):
        if self.overed:
            return
        if image_regionB is None:
            image_regionB = self.gameLocation
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            clickB = self.click_image(
                image_pathB,
                self.confidenceNum,
                image_regionB,
            )
            if clickB:
                break
            time.sleep(0.2)

    # 等待图片1出现，一直点击图2
    def waitForAAndClickB(
            self,
            image_pathA,
            image_pathB,
            image_regionA,
            image_regionB=None,
            image_pathA2=None,
    ):
        if self.overed:
            return
        if not image_regionB:
            image_regionB = self.gameLocation
        while not self.find_pic_or_str(image_pathA, image_regionA, 0):
            if self.overed:
                return
            with condition:
                if self.stoped:
                    condition.wait()
            clickB = self.click_image(
                image_pathB,
                self.confidenceNum,
                image_regionB,
            )
            if clickB:
                time.sleep(0.1)
                if self.find_pic_or_str(image_pathA2, self.gameBottomLocation,
                                        0):
                    break
                time.sleep(0.2)
            time.sleep(0.1)
        self.dm.MoveTo(804, 74)
        time.sleep(0.001)
        self.dm.LeftClick()

    # 使用道具
    def press_keys_until_image_found(self, image_path, image_path2, region1,
                                     region2, find_text):
        if self.overed:
            return
        self.confidenceNum = 0.8
        image_path_pos = self.waitFor(image_path, region1, 5)
        self.confidenceNum = 0.9
        if not image_path_pos:
            return False
        while True:
            if self.check_stop_or_over():
                return
            if self.find_pic_or_str(image_path2, region2, 0):
                break
            time.sleep(0.001)
            self.dm.MoveTo(image_path_pos.x, int(image_path_pos.y))
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.5)
            self.dm.MoveTo(image_path_pos.x, int(image_path_pos.y + 150))
            time.sleep(0.001)
            self.confidenceNum = 0.8
            chushou_pos = self.waitFor(find_text, self.gameLocation, 3)
            self.confidenceNum = 0.9
            if chushou_pos:
                self.dm.MoveTo(chushou_pos.x, chushou_pos.y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
            self.dm.MoveTo(int(image_path_pos.x + 100), image_path_pos.y)
            if self.find_pic_or_str(image_path2, region2, 0):
                break
            time.sleep(1.5)
        return True

    def get_random_number(self):
        numbers = [-2, -1, 0, 1, 2]
        return random.choice(numbers)

    # 点小地图
    def clickDitu(self, xy, find_image, find_region, break_image):
        with condition:
            if self.stoped:
                condition.wait()
        d_pos = xy.split(",")
        d_pos[0] = (1000 - int(
            float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
        d_pos[1] = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
        self.dm.MoveToEx(int(d_pos[0]), int(d_pos[1]), 3, 2)
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(0.3)
        while not self.find_pic(break_image, self.gameBottomLocation, 0):
            self.waitFor(find_image, find_region)
            isFind = self.find_pic(find_image, find_region, 0)
            if isFind:
                self.dm.MoveToEx(isFind.x, isFind.y, 30, 15)
                time.sleep(0.001)
                self.dm.LeftClick()
            time.sleep(0.5)

    # 找图并且点击6
    def findAndClickPic(self, A, B, B1, B2, C1, C2, D, E="", E2=None,
                        E2DownTime=0.6):
        if self.overed:
            return
        # self.mac_address = self.get_mac_address()
        # is_pass = self.is_user_valid()
        # if not is_pass:
        #     self.show_error_message("未注册用户，请联系管理员注册!")
        #     time.sleep(1000000)
        EIsDown = False
        E2IsDown = False
        self.BisClick = False
        self.clickBTime = 0
        self.clickBX = 0
        self.clickBy = 0

        with condition:
            if self.stoped:
                condition.wait()
        try:
            aIsOk = self.waitFor(A, self.dituLocation)
            if not aIsOk:
                # self.show_error_message("未找到开始地点")
                return
            if time.localtime().tm_min == 58 and self.scriptName != "49整点" and not self.zhengdian_flag:
                if self.scriptName in ["官渡"]:
                    time.sleep(1)
                    self.clearBag()
                    time.sleep(1)
                if (
                        self.zhengdianFloor in ["全打", "龙+全打", "蛇+全打"]
                        and self.scriptName in self.zhengdianFb
                ):
                    # 打整点
                    self.zhengdian_flag = True
                    self.outScript(A)
                    time.sleep(2)
                    self.new_zhengdian()   
                    return
                elif self.zhengdianFloor == "走路" and self.scriptName in [
                    "官渡",
                    "魔镜",
                    "龙珠",
                    "倭寇",
                    "老鼠",
                    "森罗殿",
                ]:
                    # 打整点
                    self.zhengdian_flag = True
                    self.outScript(A)
                    time.sleep(2)
                    self.go_zhengdian()
                    return
                elif self.zhengdianFloor in ["49整点", "49蛇+全打", "49龙+全打"] and self.scriptName in [
                    "魔镜",
                    "黑风",
                    "官渡",
                    "龙珠",
                    "龙岛",
                ]:
                    # 打整点
                    self.zhengdian_flag = True
                    self.outScript(A)
                    time.sleep(2)
                    self.go_zhengdian49()
                    return
            if self.overed:
                return
            # 去除获得铜币黑框
            # self.click_image(
            # 	'获得铜币',
            # 	self.confidenceNum,
            # 	self.gameLeftLocation,
            # )
            # 按下E2
            if E2 and not E2IsDown:
                self.dm.KeyDownChar(E2)
                E2IsDown = True
                time.sleep(E2DownTime)
                self.dm.KeyUpChar(E2)
            # 开始找C的时间
            startTime = time.time()
            find_dir = 2 if E == "left" else 0
            while not self.find_pic_or_str(C1, C2, find_dir):
                if self.overed:
                    return
                if self.check_stop_or_over():
                    return
                if time.time() - startTime > 10 and self.hundianFlag:
                    self.click_image(
                        self.get_resource_path(
                            "serveAssets/images/guandu/hundianchuansongmen.bmp"),
                        self.confidenceNum,
                        self.dituLocation,
                    )
                if time.time() - startTime > 22:
                    self.dm.CapturePng(
                        0,
                        0,
                        self.locationWidth,
                        self.locationHeight,
                        f"wait_for_{C1}_more_than_22_seconds.png",
                    )
                    if self.scriptName == "官渡":
                        print("超过15s没找到目标,重新进入官渡")
                        time.sleep(1)
                        self.outScript()
                        time.sleep(1)
                        self.guanduWhile()
                        return
                    elif self.scriptName == "魔镜":
                        print("超过15s没找到目标,重新进入魔镜")
                        self.outScript()
                        time.sleep(1)
                        self.mojingWhile()
                        return
                    elif self.scriptName == "黑风":
                        print("超过15s没找到目标,重新进入黑风")
                        self.outScript()
                        time.sleep(1)
                        self.heifengWhile()
                        return

                #   D找图片D点击‘
                if (
                        D
                        and self.clickBTime == 0
                        and not self.find_pic_or_str(B, B2, 0)
                        and not self.find_pic_or_str(B1, B2, 0)
                ):
                    if self.overed:
                        return
                    with condition:
                        if self.stoped:
                            condition.wait()
                    d_pos = D.split(",")
                    if float(d_pos[0]) > 1 and float(d_pos[1]) > 1:
                        d_pos[0] = (900 - float(d_pos[0])) / 900
                        d_pos[1] = float(d_pos[1]) / 580
                    d_pos[0] = (1000 - int(
                        float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
                    d_pos[1] = (int(float(
                        d_pos[1]) * 1000)) / 1000 * self.locationHeight
                    self.dm.MoveToEx(
                        int(int(d_pos[0]) + self.locationX),
                        int(int(d_pos[1]) + self.locationY),
                        3,
                        2,
                    )
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    time.sleep(0.6)
                if self.find_pic_or_str(C1, C2, find_dir):
                    break
                while (
                        E != ""
                        and not EIsDown
                        and not self.find_pic_or_str(B, B2, find_dir)
                        and not self.find_pic_or_str(B1, B2, find_dir)
                ):
                    if self.overed:
                        return
                    with condition:
                        if self.stoped:
                            condition.wait()
                    self.dm.KeyDownChar(E)
                    B1Location = self.waitForTwo(
                        B,
                        B1,
                        B2,
                    )
                    if B1Location:
                        EIsDown = True
                        self.dm.KeyUpChar(E)
                    self.click_image_with_min_x(
                        B,
                        B2,
                        C1,
                    )
                    self.click_image_with_min_x(
                        B1,
                        B2,
                        C1,
                    )
                    if self.find_pic_or_str(C1, C2, find_dir):
                        EIsDown = True
                        time.sleep(0.1)
                        self.dm.KeyUpChar(E)
                        break
                if self.check_stop_or_over():
                    return

                # 点击B
                self.BisClick = self.click_image_with_min_x(
                    B,
                    B2,
                    C1,
                )
                if self.find_pic_or_str(C1, C2, find_dir):
                    break
                self.BisClick = self.click_image_with_min_x(
                    B1,
                    B2,
                    C1,
                )

                # 点过b之后如果过了4秒还没有找到C，重新点一次b的坐标
                if self.clickBTime > 0 and time.time() - self.clickBTime > 4:
                    # print('click')
                    self.dm.MoveTo(self.clickBX, self.clickBy)
                    time.sleep(0.001)
                    self.dm.LeftClick()
                    self.clickBTime = time.time()
        except Exception as e:
            self.show_error_message(f"发生错误: {e}")

    # 官渡脚本
    def guanduScript(self):
        if self.overed:
            return
        self.guanDuCount += 1
        print(f"第{self.guanDuCount}次官渡.")
        with condition:
            if self.stoped:
                condition.wait()
        # 进入官渡
        self.findAndClickPic(
            "官渡",
            self.get_resource_path("serveAssets/images/guandu/caocao1.bmp"),
            self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
            self.gameLocation,
            "进入",
            self.gameBottomLocation,
            "0.038,0.134",
        )
        if self.check_stop_or_over():
            return
        # 进入第一层
        self.color_format = "b@0ff000-000000|00ff00-000000|ffff00-000000|0ff000-000000|fff200-000000"
        self.waitForAAndClickB1(
            "曹操大帐",
            "进官渡1",
            self.dituLocation,
            self.gameBottomLocation,
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # self.dm.MoveTo(280, 370)
        # while not self.find_pic_or_str('曹操大帐', self.dituLocation, 0):
        # 	if self.find_pic_or_str('进入', self.gameBottomLocation, 0):
        # 		time.sleep(0.001)
        # 		self.dm.LeftClick()
        # 	time.sleep(0.5)
        # self.waitForAAndClickB1(
        # 	'曹操大帐',
        # 	'进入',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # is_in_guandu = self.waitFor('曹操大帐', self.dituLocation, 5)
        # if not is_in_guandu:
        # 	self.outScript()
        # 	time.sleep(1)
        # 	return True
        # self.outScript()
        # return True
        with condition:
            if self.stoped:
                condition.wait()
        # 0.078,0.127
        self.findAndClickPic(
            "曹操大帐",
            "曹袁战场",
            "曹袁战场",
            self.dituLocation,
            "曹袁战场",
            self.dituLocation,
            "0.078,0.127",
        )
        # self.waitForAAndClickB1(
        # 	'曹袁战场',
        # 	self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        with condition:
            if self.overed:
                return
            if self.stoped:
                condition.wait()
        # 第一个河北军
        hbjLocations = ["0.111,0.125", "0.085,0.125", "0.065,0.123"]
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "曹袁战场",
            "河北军",
            f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
            self.gameLeftLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.165,0.124",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            "曹袁战场",
            "河北军",
            "河北军",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.144,0.126",
            "",
        )
        for i in hbjLocations:
            self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
            # f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
            self.findAndClickPic(
                "曹袁战场",
                "河北军",
                "河北军",
                self.gameLeftLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                i,
                "",
            )
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "曹袁战场",
            "河北军",
            f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.052,0.125",
        )
        if self.overed:
            return
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 颜良
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        # 0.091,0.118  f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}"
        self.findAndClickPic(
            "曹袁战场",
            self.get_resource_path("serveAssets/images/guandu/yanliang.bmp"),
            f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.097,0.126",
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        with condition:
            if self.overed:
                return
            if self.stoped:
                condition.wait()
        # 文丑
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        # f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}"
        self.findAndClickPic(
            "曹袁战场",
            "官渡文丑",
            f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.081,0.122",
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        with condition:
            if self.overed:
                return
            if self.stoped:
                condition.wait()
        # 去大帐
        self.findAndClickPic(
            "曹袁战场",
            f"{self.get_resource_path('serveAssets/images/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/guandu/caochengxiang.bmp')}",
            "知道了",
            self.gameLocation,
            "鸟巢粮仓",
            self.dituLocation,
            "0.192,0.129",
            "",
        )
        # self.findAndClickPic(
        # 	'曹操大帐',
        # 	self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
        # 	'知道了',
        # 	self.gameLocation,
        # 	'鸟巢粮仓',
        # 	self.dituLocation,
        # 	"0.192,0.129",
        # 	"",
        # )
        # self.findAndClickPic(
        # 	'曹袁战场',
        # 	self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
        # 	self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
        # 	self.dituLocation,
        # 	'知道了',
        # 	self.gameLeftLocation,
        # 	"0.192,0.129",
        # 	"",
        # )
        # self.findAndClickPic(
        # 	'曹操大帐',
        # 	'知道了',
        # 	'知道了',
        # 	self.gameBottomLocation,
        # 	'鸟巢粮仓',
        # 	self.dituLocation,
        # 	"",
        # )
        self.findAndClickPic(
            "鸟巢粮仓",
            "魂殿",
            "魂殿",
            self.dituLocation,
            "魂殿",
            self.dituLocation,
            "0.184,0.134",
        )
        # self.waitForAAndClickB1(
        # 	'魂殿',
        # 	self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # self.waitFor('枯寂', self.dituLocation)
        self.findAndClickPic(
            "魂殿",
            "文丑之魂",
            f"{self.get_resource_path('serveAssets/images/guandu/wenchou3.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou4.bmp')}",
            self.gameRightFullLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.167,0.103",
        )
        self.hundianFlag = True
        self.findAndClickPic(
            "魂殿",
            "鸟巢粮仓",
            "鸟巢粮仓",
            self.dituLocation,
            "鸟巢粮仓",
            self.dituLocation,
            "0.138,0.12",
        )
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        # 打淳
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        # f"{self.get_resource_path('serveAssets/images/guandu/cyq1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq2.bmp')}",
        self.findAndClickPic(
            "鸟巢粮仓",
            f"{self.get_resource_path('serveAssets/images/guandu/cyq.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq3.bmp')}",
            "淳于琼",
            self.gameLeftLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameLeftLocation,
            "0.161,0.129",
            "",
        )
        self.hundianFlag = False
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        with condition:
            if self.stoped:
                condition.wait()
        if self.overed:
            return
        # 打袁绍
        if self.user_name == "运气就是好" and self.get_random_number() >= 1 and int(
                time.localtime().tm_hour) == 2:
            time.sleep(1080)
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "鸟巢粮仓",
            "官渡袁绍",
            f"{self.get_resource_path('serveAssets/images/guandu/yuanshao1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yuanshao2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameLeftLocation,
            "0.152,0.124",
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        # 退出副本
        self.outScript("鸟巢粮仓")

    # 红脚本
    def hongScript(self):
        print("开始打红")
        isInGuanDu = self.waitFor("虎牢关外", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图虎牢关外",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "虎牢关外",
                "",
                "",
                True,
            )
        with condition:
            if self.stoped:
                condition.wait()
        # 进入红
        time.sleep(1)
        d_pos = "0.127,0.129".split(",")
        d_pos[0] = (1000 - int(
            float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
        d_pos[1] = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
        self.dm.MoveToEx(
            int(int(d_pos[0]) + self.locationX),
            int(int(d_pos[1]) + self.locationY),
            3,
            2,
        )
        while True:
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.3)
            if self.find_pic_or_str(
                    self.get_resource_path(
                        "serveAssets/images/hong/xiaobairen.bmp"),
                    (773, 34, 827, 78),
                    0,
            ):
                break
        time.sleep(1)
        self.confidenceNum = 0.8
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            "虎牢关外",
            f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}",
            f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}",
            (773, 34, 827, 78),
            "进入|进精英",
            self.gameBottomLocation,
            "0.127,0.129",
        )
        time.sleep(1)
        self.waitForAAndClickB1(
            "军营",
            "进入|进精英",
            self.dituLocation,
            self.gameBottomLocation,
        )
        self.confidenceNum = 0.9
        if self.overed:
            return
        isInHong = self.waitFor("军营", self.dituLocation, 8)
        if not isInHong:
            print("红没次数了")
            return False
        # 第一层
        if self.overed:
            return
        gonbin_poss = ["0.121,0.125", "0.064,0.125", "0.036,0.12"]
        for i in range(3):
            if self.overed:
                return
            self.findAndClickPic(
                "军营",
                "弓兵",
                "弓兵",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                gonbin_poss[i],
            )

        # 进入军粮营
        self.findAndClickPic(
            "军营",
            "军粮营",
            "军粮营",
            self.dituLocation,
            "军粮营",
            self.dituLocation,
            "0.158,0.146",
            "",
            "down",
        )
        # 第二层
        huweibin_poss = ["0.144,0.124", "0.1,0.118", "0.035,0.124"]
        for i in range(2):
            if self.overed:
                return
            self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
            self.findAndClickPic(
                "军粮营",
                "护卫兵",
                f"{self.get_resource_path('serveAssets/images/hong/huweibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huweibin2.bmp')}",
                self.gameLeftLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                huweibin_poss[i],
            )
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.waitFor("军粮营", self.dituLocation)
        self.addBloud()
        self.findAndClickPic(
            "军粮营",
            "护粮将领",
            f"{self.get_resource_path('serveAssets/images/hong/huliangjianglin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huliangjianglin2.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            huweibin_poss[2],
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 进入训兵营
        self.findAndClickPic(
            "军粮营",
            "训兵营",
            "训兵营",
            self.dituLocation,
            "训兵营",
            self.dituLocation,
            "0.015,0.127",
        )
        # self.waitForAAndClickB1(
        # 	'训兵营',
        # 	self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituRightLocation,
        # )
        # 第3层
        qibin_poss = ["0.136,0.112", "0.104,0.148", "0.06,0.124", "0.121,0.131"]
        for i in range(3):
            self.findAndClickPic(
                "训兵营",
                "骑兵",
                f"{self.get_resource_path('serveAssets/images/hong/qibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/qibin2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                qibin_poss[i],
            )
        if self.overed:
            return
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.waitFor("训兵营", self.dituLocation)
        self.addBloud()
        self.findAndClickPic(
            "训兵营",
            "训兵将领",
            f"{self.get_resource_path('serveAssets/images/hong/shenjinxi1.bmp')}|{self.get_resource_path('serveAssets/images/hong/shenjinxi2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            qibin_poss[3],
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 进入军营
        self.findAndClickPic(
            "训兵营",
            "军营",
            "军营",
            self.dituLocation,
            "军营",
            self.dituLocation,
            "0.106,0.091",
        )
        if self.overed:
            return
        self.addBloud()
        # 进入帐篷
        self.findAndClickPic(
            "军营",
            self.get_resource_path("serveAssets/images/hong/chuansongmen3.bmp"),
            self.get_resource_path("serveAssets/images/hong/chuansongmen3.bmp"),
            self.dituCenterLocation,
            "帐篷",
            self.dituLocation,
            "",
        )
        # boss
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "帐篷",
            "控魂巫师",
            "控魂巫师",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameRightLocation,
            "0.09,0.127",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 退出副本
        self.outScript(
            "帐篷",
        )
        return True

    def qingyuanWhile(self):
        for i in range(int(self.qingyuan_count)):
            if self.overed:
                return
            qingyuanRes = self.qingyuanScript()
            if not qingyuanRes:
                print("青渊没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()
    
    # 青渊
    def qingyuanScript(self):
        print("青渊")
        isInGuanDu = self.waitFor("虎牢关外", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图虎牢关外",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "虎牢关外",
                "",
                "",
                True,
            )
        with condition:
            if self.stoped:
                condition.wait()
        # 63*67
        self.findAndClickPic(
            "虎牢关外",
            "孙坚",
            self.get_resource_path("serveAssets/images/hong/sunjian1.bmp"),
            self.gameLocation,
            "进入",
            self.gameBottomLocation,
            "0.07,0.125",
        )
        time.sleep(1)
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/hong/qingyuan1.bmp"),
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInHong = self.waitFor(
            self.get_resource_path("serveAssets/images/hong/qingyuan1.bmp"),
            self.dituLocation,
            8,
        )
        if not isInHong:
            print("青渊没次数了")
            return False
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/hong/qingyuan1.bmp"),
            "龙守卫",
            "龙守卫",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        self.addBloud()
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/hong/qingyuan1.bmp"),
            "冰龙王",
            "冰龙王",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        self.addBloud()
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/hong/qingyuan1.bmp"),
            self.get_resource_path("serveAssets/images/hong/chuansongmen.bmp"),
            self.get_resource_path("serveAssets/images/hong/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/hong/qingyuan2.bmp"),
            self.dituLocation,
            "",
        )
        self.addBloud()
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/hong/qingyuan2.bmp"),
            "青龙圣兽",
            "青龙圣兽",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        # 退出副本
        self.outScript(
            self.get_resource_path("serveAssets/images/hong/qingyuan2.bmp"),
        )
        return True

    # 英魂
    def yinhunScript(self):
        print("开始打英魂秘境")
        with condition:
            if self.stoped:
                condition.wait()
        if self.overed:
            return
        # 进入红
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/hong/luanshipo.bmp"),
            self.get_resource_path("serveAssets/images/hong/nanhualaoxian.bmp"),
            self.get_resource_path(
                "serveAssets/images/hong/nanhualaoxian1.bmp"),
            self.gameBottomLocation,
            "进入",
            self.gameBottomLocation,
            "0.022,0.138",
        )
        self.waitForAAndClickB1(
            "魂息平原",
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        if self.overed:
            return
        isInHong = self.waitFor(
            "魂息平原",
            self.dituLocation,
            8,
        )
        if not isInHong:
            print("英魂秘境没次数了")
            return False
        self.addBloud()
        self.findAndClickPic(
            "魂息平原",
            "怨灵",
            "怨灵",
            self.gameLeftLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "",
        )
        self.findAndClickPic(
            "魂息平原",
            "怨灵",
            "怨灵",
            self.gameLeftLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "",
        )
        self.waitFor(
            "魂息平原",
            self.dituLocation,
        )
        self.addBloud()
        self.findAndClickPic(
            "魂息平原",
            "秘境英魂|英魂之火|怨灵",
            f"{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo1.bmp')}|{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo2.bmp')}",
            self.gameLeftLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.072,0.146",
        )
        self.waitFor(
            "魂息平原",
            self.dituLocation,
        )
        self.addBloud()
        self.findAndClickPic(
            "魂息平原",
            "秘境英魂|英魂之火|怨灵",
            f"{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo1.bmp')}|{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo2.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.072,0.146",
        )
        self.findAndClickPic(
            "魂息平原",
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            self.dituLocation,
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            self.dituLocation,
            "0.014,0.16",
        )
        self.waitFor(
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            self.dituLocation,
        )
        self.addBloud()
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            "英魂之火",
            f"{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo1.bmp')}|{self.get_resource_path('serveAssets/images/richang/yinghunzhihuo2.bmp')}",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "",
        )
        self.waitFor(
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            self.dituLocation,
        )
        self.addBloud()
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
            "吕布英魂",
            "吕布英魂",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "",
        )
        # 退出副本
        self.outScript(
            self.get_resource_path(
                "serveAssets/images/hong/youyingshenyuan.bmp"),
        )
        return True

    #  战魂脚本
    def zhanhunScript(self):
        if not self.zhanhunFloor:
            self.zhanhunFloor = "25层"
            print("未选择层数，自动打25层")
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        if self.overed:
            return
        print("开始战魂")
        isInGuanDu = self.waitFor(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.dituLocation,
            5,
        )
        if not isInGuanDu:
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "",
                True,
            )
        # 进入战魂
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan1.bmp"),
            self.gameLocation,
            "进精英",
            self.gameBottomLocation,
            "0.067,0.132",
        )
        # 点击进入战魂
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zhanhun/1.bmp"),
            "进精英",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("战魂", self.dituLocation, 15)
        if not isInZhanhun:
            print("战魂没次数了")
            return False
        _start_floor = int(self.zhanhun_start_floor.replace("层", "")) if self.zhanhun_start_floor else 1
        # 1
        if _start_floor <= 1:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/1.bmp"),
                "张宝",
                "张宝",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "张梁",
        )
        # 2
        if _start_floor <= 2:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
                "张梁",
                f"{self.get_resource_path('serveAssets/images/zhanhun/zhangliang1.bmp')}|{self.get_resource_path('serveAssets/images/zhanhun/zhangliang2.bmp')}",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "张角",
        )
        # 3
        if _start_floor <= 3:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
                "张角",
                "张角",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "文丑",
        )
        # 4
        if _start_floor <= 4:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
                "文丑",
                "文丑",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "颜良",
        )
        # 5
        if _start_floor <= 5:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
                "颜良",
                "颜良",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "华雄",
        )
        # 6
        if _start_floor <= 6:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
                "华雄",
                "华雄",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "孙策",
        )
        # 7
        if _start_floor <= 7:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
                "孙策",
                "孙策",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "典韦",
        )
        # 8
        if _start_floor <= 8:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
                "典韦",
                "典韦",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "郭嘉",
        )
        # 9
        if _start_floor <= 9:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
                "郭嘉",
                "郭嘉",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "刘备",
        )
        # 10
        if _start_floor <= 10:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
                "刘备",
                f"{self.get_resource_path('serveAssets/images/zhanhun/liubei.bmp')}|{self.get_resource_path('serveAssets/images/zhanhun/liubei1.bmp')}",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "曹操",
        )
        # 11
        if _start_floor <= 11:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
                "曹操",
                "曹操",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "袁绍",
        )
        # 12
        if _start_floor <= 12:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
                "袁绍",
                "袁绍",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "张飞",
        )
        # 13
        if _start_floor <= 13:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
                "张飞",
                "张飞",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "大乔",
        )
        # 14
        if _start_floor <= 14:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
                "大乔",
                "大乔",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "关羽",
        )
        # 15
        if _start_floor <= 15:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
                "关羽",
                "关羽",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "吕布",
        )
        # 16
        if _start_floor <= 16:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
                "吕布",
                "吕布",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "张飞",
        )
        # 17
        if _start_floor <= 17:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
                "张飞",
                "张飞",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "关羽",
        )
        # 18
        if _start_floor <= 18:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
                "关羽",
                "关羽",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "吕布",
        )
        # 19
        if _start_floor <= 19:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
                "吕布",
                "吕布",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "吕布",
        )
        # 20
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            "吕布",
            "吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if self.zhanhunFloor == "20层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "刘备",
        )
        # 21
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            "刘备",
            "刘备",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("21层没打过")
            return True
        if self.zhanhunFloor == "21层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "袁绍",
        )
        # 22
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            "袁绍",
            "袁绍",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd111.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("22层没打过")
            return True
        if self.zhanhunFloor == "22层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "曹操",
        )
        # 23
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            "曹操",
            "曹操",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("23层没打过")
            return True
        if self.zhanhunFloor == "23层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "吕布",
        )
        # 24
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            "吕布",
            "吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("24层没打过")
            return True
        if self.zhanhunFloor == "24层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.waitForAAndClickB(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
            "吕布",
        )
        # 25
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            "吕布",
            "吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("25层没打过")
            return True
        if self.zhanhunFloor == "25层":
            # 退出副本
            self.outScript(
                self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            )
            return True
        # 退出副本
        self.outScript(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
        )
        return True

    def zhenhun_lianyu_script(self):
        if not self.zhanhunFloorNew:
            self.zhanhunFloorNew = "27层"
            print("未选择层数，自动打27层")
        print("开始镇魂")
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        if self.overed:
            return
        isInGuanDu = self.waitFor(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.dituLocation,
            5,
        )
        if not isInGuanDu:
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "",
                True,
            )
        # 进入战魂
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan1.bmp"),
            self.gameLocation,
            "镇魂",
            self.gameBottomLocation,
            "0.067,0.132",
        )
        # 点击进入战魂
        self.waitForAAndClickB1(
            "战魂",
            "镇魂",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("战魂", self.dituLocation, 15)
        if not isInZhanhun:
            print("战魂没次数了")
            return False
        self.huifu_yijian_main()
        time.sleep(1)
        if self.zhanhunFloorNew == "27层自动战斗":
            self._start_combat_auto()
        self.findAndClickPic(
            "战魂",
            "人参娃",
            "人参娃",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        self.addBloud()
        if self.zhanhunFloorNew == "27层自动战斗":
            self._stop_combat_auto()
        waitForTwoRes = self.waitForTwo(
            "战魂",
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("26层没打过")
            return True
        if self.zhanhunFloorNew == "26层":
            # 退出副本
            # self._stop_combat_auto()  # 停止战斗自动操作
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            "战魂",
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            "周瑜",
            self.gameBottomLocation,
            "",
        )
        self.huifu_yijian_main()
        time.sleep(1)
        if self.zhanhunFloorNew == "27层自动战斗":
            self._start_combat_auto()
        self.findAndClickPic(
            "魂",
            "周瑜",
            "周瑜",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if self.zhanhunFloorNew == "27层自动战斗":
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            "魂",
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("27层没打过")
            return True
            # 退出副本
        self.outScript(
            "魂",
        )
        return True

    def shihun_lianyu_script(self):
        if not self.shihun_floor:
            self.shihun_floor = "29层"
            print("未选择层数，自动打29层")
        print("开始噬魂")
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        if self.overed:
            return
        isInGuanDu = self.waitFor(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.dituLocation,
            5,
        )
        if not isInGuanDu:
            self.go_in_ditu(
                "地图洛阳大道",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "洛阳",
                "",
                "",
                True,
            )
        # 进入战魂
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/luoyang.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan1.bmp"),
            self.gameLocation,
            "噬魂",
            self.gameBottomLocation,
            "0.067,0.132",
        )
        # 点击进入战魂
        self.waitForAAndClickB1(
            "噬魂",
            "噬魂",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("噬魂", self.dituLocation, 15)
        if not isInZhanhun:
            print("战魂没次数了")
            return False
        self.huifu_yijian_main()
        time.sleep(1)
        if "战魂" in self.combat_auto_scenes:
            self._start_combat_auto(clear_enemy_keys=["赵云28"])
        self.findAndClickPic(
            "噬魂",
            "马超",
            "马超",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if "战魂" in self.combat_auto_scenes:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            "噬魂",
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("28层没打过")
            self._update_dungeon_stats("噬魂", "fail")
            return True
        if self.shihun_floor == "28层":
            # 退出副本
            self.outScript("噬魂")
            self._update_dungeon_stats("噬魂", "win")
            return True
        self.huifu_yijian_main()
        time.sleep(1)
        self.findAndClickPic(
            "噬魂",
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            "诸葛亮",
            self.gameBottomLocation,
            "",
        )
        if "战魂" in self.combat_auto_scenes:
            self._start_combat_auto(clear_enemy_keys=["赵云29", "诸葛亮"])
        self.findAndClickPic(
            "噬魂",
            "诸葛亮",
            "诸葛亮",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if "战魂" in self.combat_auto_scenes:
            self._stop_combat_auto()
        # self.addBloud()
        waitForTwoRes = self.waitForTwo(
            "噬魂",
            "洛阳",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("29层没打过")
            self._update_dungeon_stats("噬魂", "fail")
            return True
        # 退出副本
        self.outScript("噬魂")
        self._update_dungeon_stats("噬魂", "win")
        return True

    # 魔镜脚本
    def mojingScript(self):
        if self.overed:
            return
        self.mojingCount += 1
        print(f"第{self.mojingCount}次魔镜.")
        # 进入魔镜
        self.findAndClickPic(
            "城西",
            f"{self.get_resource_path('serveAssets/images/mojing/mojingshizhe.bmp')}|{self.get_resource_path('serveAssets/images/mojing/mojingshizhe1.bmp')}",
            "进入",
            self.gameBottomLocation,
            "镜像地层",
            self.dituLocation,
            "0.14,0.124",
        )
        # self.waitForAAndClickB1(
        # 	'镜像地层',
        # 	'进入',
        # 	self.dituLocation,
        # 	self.gameBottomLocation,
        # )
        # isInMojing = self.waitFor('镜像地层', self.dituLocation, 8)
        # if not isInMojing:
        # 	print('魔镜没了')
        # 	return False
        # 打一个第一层的怪
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "镜像地层",
            "吃人妖",
            "吃人妖",
            self.gameLeftLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.155,0.121",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 进入第二层

        self.findAndClickPic(
            "镜像地层",
            f"{self.get_resource_path('serveAssets/images/mojing/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/mojing/xiaolvren111.bmp')}",
            "进入|知道了",
            self.gameLocation,
            "遗迹镜像",
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	'进入|知道了',
        # 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
        # 	self.gameBottomLocation, self.dituLocation,
        # )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/mojing/111.bmp"),
        # 	'进入|知道了',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # 打狮王
        if self.user_name == "运气就是好" and self.get_random_number() >= 0 and 2 <= int(
                time.localtime().tm_hour) <= 5:
            time.sleep(100)
            self.outScript("镜像地层")
            return True
        self.findAndClickPic(
            "遗迹镜像",
            "狮王魂",
            "狮王魂",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.118,0.125",
        )
        # 进入第三层
        self.findAndClickPic(
            "遗迹镜像",
            f"{self.get_resource_path('serveAssets/images/mojing/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/mojing/xiaolvren111.bmp')}",
            "进入|知道了",
            self.gameLocation,
            "迷幻境",
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	'进入|知道了',
        # 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
        # 	self.gameBottomLocation, self.dituLocation,
        # )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/mojing/111.bmp"),
        # 	'进入|知道了',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # 打虚实
        self.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
        self.findAndClickPic(
            "迷幻境",
            "虚",
            "虚",
            self.gameRightLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.056,0.143",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            "迷幻境",
            "实",
            "实",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.152,0.132",
        )
        if self.mojingFloor == "迷幻境（虚实）":
            # 退出副本
            self.outScript("迷幻境")
            return True
        # 进入第四层
        self.findAndClickPic(
            "迷幻境",
            f"{self.get_resource_path('serveAssets/images/mojing/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/mojing/xiaolvren111.bmp')}",
            "进入|知道了",
            self.gameLocation,
            "狱境",
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	'进入|知道了',
        # 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
        # 	self.gameBottomLocation, self.dituLocation,
        # )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/mojing/111.bmp"),
        # 	'进入|知道了',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # 打黑白无常
        self.findAndClickPic(
            "狱境",
            "黑无常之魂",
            "黑无常之魂",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.11,0.12",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
        self.findAndClickPic(
            "狱境",
            "白无常之魂",
            "白无常之魂",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.163,0.116",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        if self.mojingFloor == "狱境（黑白无常）":
            # 退出副本
            self.outScript("狱境")
            return True
        # 进入第五层
        self.findAndClickPic(
            "狱境",
            f"{self.get_resource_path('serveAssets/images/mojing/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/mojing/xiaolvren111.bmp')}",
            "进入|知道了",
            self.gameLocation,
            "炎冰境",
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	'进入|知道了',
        # 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
        # 	self.gameBottomLocation, self.dituLocation,
        # )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/mojing/111.bmp"),
        # 	'进入|知道了',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # 打黑白无常
        self.findAndClickPic(
            "炎冰境",
            "冰魔",
            "冰魔",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.05,0.125",
        )
        if self.mojingFloor == "刷张辽":
            # 退出副本
            self.outScript("炎冰境")
            return True
        self.color_format = "ffffff-00000|00ff00-000000|ff0000-000000"
        self.findAndClickPic(
            "炎冰境",
            "炎魔",
            f"{self.get_resource_path('serveAssets/images/zhengdian/huoyan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huoyan2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.172,0.127",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            "炎冰境",
            "炎兄",
            f"{self.get_resource_path('serveAssets/images/zhengdian/huoyan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huoyan2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.156,0.127",
        )
        if self.mojingFloor == "炎冰境":
            # 退出副本
            self.outScript("炎冰境")
            return True
        # 进入第六层
        self.findAndClickPic(
            "炎冰境",
            f"{self.get_resource_path('serveAssets/images/mojing/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/mojing/xiaolvren111.bmp')}",
            "进入|知道了",
            self.gameLocation,
            "印魔殿",
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	'进入|知道了',
        # 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
        # 	self.gameBottomLocation, self.dituLocation,
        # )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/mojing/111.bmp"),
        # 	'进入|知道了',
        # 	self.dituLocation, self.gameBottomLocation,
        # )
        # 北境
        self.findAndClickPic(
            "印魔殿",
            "北境",
            "北境",
            self.dituLocation,
            "北境",
            self.dituLocation,
            "0.122,0.075",
        )
        self.findAndClickPic(
            "北境",
            "四神",
            "四神",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.098,0.125",
        )
        self.findAndClickPic(
            "北境",
            "印魔殿",
            "印魔殿",
            self.dituLocation,
            "印魔殿",
            self.dituLocation,
            "0.101,0.172",
        )
        # 西境
        self.findAndClickPic(
            "印魔殿",
            "西境",
            "西境",
            self.dituLocation,
            "西境",
            self.dituLocation,
            "0.182,0.115",
        )
        self.findAndClickPic(
            "西境",
            "四神",
            "四神",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.104,0.137",
        )
        # self.waitForAAndClickB1(
        # 	'印魔殿',
        # 	self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        self.findAndClickPic(
            "西境",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            "印魔殿",
            self.dituLocation,
            "",
        )
        # 南境
        self.findAndClickPic(
            "印魔殿",
            "南境",
            "南境",
            self.dituLocation,
            "南境",
            self.dituLocation,
            "0.123,0.153",
        )
        self.findAndClickPic(
            "南境",
            "四神",
            "四神",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.1,0.139",
        )
        self.findAndClickPic(
            "南境",
            "印魔殿",
            "印魔殿",
            self.dituLocation,
            "印魔殿",
            self.dituLocation,
            "0.102,0.113",
        )
        # 东境
        self.findAndClickPic(
            "印魔殿",
            "东境",
            "东境",
            self.dituLocation,
            "东境",
            self.dituLocation,
            "0.053,0.117",
        )
        self.findAndClickPic(
            "东境",
            "四神",
            "四神",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.107,0.137",
        )
        # self.waitForAAndClickB1(
        # 	'印魔殿',
        # 	self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        self.findAndClickPic(
            "东境",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            "印魔殿",
            self.dituLocation,
            "",
        )
        # boss
        self.findAndClickPic(
            "印魔殿",
            "魔将",
            "魔将",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.135,0.101",
        )
        # 退出副本
        self.outScript("印魔殿")
        return True

    # 炼丹脚本
    def liandanScript(self):
        if self.overed:
            return
        print("开始炼丹房")
        time.sleep(0.5)
        isInGuanDu = self.waitFor("五指峡谷", self.dituLocation, 5)
        if not isInGuanDu:
            self.feiFb("副本南华老人", False)
        # 进入炼丹
        # 0.164,0.131
        self.findAndClickPic(
            "五指峡谷",
            self.get_resource_path(
                "serveAssets/images/richang/nanhualaoren.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/nanhualaoren1.bmp"),
            self.gameLocation,
            "进入",
            self.gameBottomLocation,
            "0.164,0.131",
        )
        self.waitForAAndClickB1(
            "南天门",
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInHong = self.waitFor("南天门", self.dituLocation, 8)
        if not isInHong:
            print("炼丹没次数了")
            return False
        # 打门神 0.1111,0.131
        self.findAndClickPic(
            "南天门",
            "左门",
            "左门",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.111,0.131",
        )
        # 0.083,0.127
        self.findAndClickPic(
            "南天门",
            "右门",
            "右门",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.083,0.127",
        )
        # 进入第二层  0.103,0.115
        self.findAndClickPic(
            "南天门",
            "天宫小道",
            "天宫小道",
            self.dituLocation,
            "天宫小道",
            self.dituLocation,
            "0.103,0.115",
        )
        # 进入
        self.waitForAAndClickB1(
            "炼丹房",
            self.get_resource_path(
                "serveAssets/images/richang/liandanchuansongmen.bmp"),
            self.dituLocation,
            self.dituRightLocation,
        )
        # 开始打炼丹童子童女  0.155,0.151  0.135,0.12
        liandan1_poss = ["0.155,0.151", "0.135,0.12", "0.155,0.151",
                         "0.135,0.12"]
        # for i in range(2):
        # 	self.findAndClickPic(
        # 		'炼丹房',
        # 		'炼丹童',
        # 		'炼丹童',
        # 		self.gameLeftLocation,
        # 		self.get_resource_path("serveAssets/images/zdzd.bmp"),
        # 		self.gameBottomLocation,
        # 		liandan1_poss[i],
        # 	)
        self.waitFor("炼丹房", self.dituLocation)
        time.sleep(0.5)
        self.click_image(
            self.get_resource_path("serveAssets/images/guaji.bmp"),
            0.8,
            self.gameBottomLocation,
        )
        self.waitFor("五指峡谷", self.dituLocation)
        return True
        # 0.052,0.143   0.071,0.118
        liandan2_poss = [
            "0.071,0.118",
            "0.052,0.143",
            "0.071,0.118",
            "0.052,0.143",
            "0.071,0.118",
        ]
        for i in range(5):
            self.findAndClickPic(
                "炼丹房",
                "炼丹童",
                "炼丹童",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                liandan2_poss[i],
            )
        # 退出副本
        self.outScript("炼丹房")
        return True

    # 五行脚本
    def wuxingScript(self):
        if self.overed:
            return
        print("开始五行")
        isInGuanDu = self.waitFor("野外西", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图野外西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "野外西",
                "驿站城西",
                "",
                True,
            )
        # 进入五行
        self.findAndClickPic(
            "野外西",
            self.get_resource_path("serveAssets/images/richang/laoban1.bmp"),
            self.get_resource_path("serveAssets/images/richang/laoban.bmp"),
            self.gameLocation,
            "进五行",
            self.gameBottomLocation,
            "0.041,0.134",
        )
        time.sleep(0.5)
        self.waitForAAndClickB1(
            "五行圣殿",
            "进五行",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInMojing = self.waitFor("五行圣殿", self.dituLocation, 8)
        if not isInMojing:
            print("五行没次数了")
            return False
        # 0.082,0.117
        # self.findAndClickPic(
        # 	'五行圣殿',
        # 	'神火系',
        # 	f"{self.get_resource_path('serveAssets/images/richang/shenhuoxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenhuoxi2.bmp')}",
        # 	self.gameBottomLocation,
        # 	self.get_resource_path("serveAssets/images/zdzd.bmp"),
        # 	self.gameBottomLocation,
        # 	"0.082,0.117",
        # )
        time.sleep(0.5)
        self.click_image(
            self.get_resource_path("serveAssets/images/guaji.bmp"),
            self.confidenceNum,
            self.gameBottomLocation,
        )
        self.waitFor("野外西", self.dituLocation)
        return True
        # 打大乔  0.077,0.146
        self.findAndClickPic(
            "五行圣殿",
            self.get_resource_path(
                "serveAssets/images/richang/shenshuixi1.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/shenshuixi2.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.077,0.146",
        )

        # 0.104,0.125
        self.findAndClickPic(
            "五行圣殿",
            "神金系",
            f"{self.get_resource_path('serveAssets/images/richang/shenjinxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenjinxi2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.104,0.125",
        )
        # 0.148,0.151
        self.findAndClickPic(
            "五行圣殿",
            self.get_resource_path("serveAssets/images/richang/shentuxi.bmp"),
            f"{self.get_resource_path('serveAssets/images/richang/shentuxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shentuxi2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.148,0.151",
        )
        # 0.121,0.117
        self.findAndClickPic(
            "五行圣殿",
            self.get_resource_path("serveAssets/images/richang/shenmuxi.bmp"),
            f"{self.get_resource_path('serveAssets/images/richang/shenmuxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenmuxi2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.121,0.117",
        )
        self.outScript(
            "五行圣殿",
        )
        return True

    # 溶洞
    def rongdongScript(self):
        if self.overed:
            return
        print("开始溶洞")
        isInGuanDu = self.waitFor("绿林路", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图绿林路",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "绿林路",
                "驿站城西",
                "驿站许昌",
                True,
            )
        # self.feiFb('副本龙天啸', False)
        # self.feiFb('副本龙天啸', False)
        # 进入溶洞  0.065,0.124
        self.findAndClickPic(
            "绿林路",
            self.get_resource_path(
                "serveAssets/images/richang/longtianxiao2.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/longtianxiao.bmp"),
            self.gameLocation,
            "进入",
            self.gameBottomLocation,
            "0.065,0.124",
        )
        self.waitForAAndClickB1(
            "遗忘之林",
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInMojing = self.waitFor("遗忘之林", self.dituLocation, 8)
        if not isInMojing:
            print("溶洞没次数了")
            return False
        # 开始打第一层  0.054,0.113  0.086,0.129   0.121,0.113
        ganshi_pos = ["0.054,0.113", "0.096,0.129", "0.121,0.113"]
        self.findAndClickPic(
            "遗忘之林",
            "远古干尸",
            "远古干尸",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.054,0.113",
        )
        self.findAndClickPic(
            "遗忘之林",
            "远古干尸",
            "远古干尸",
            self.gameRightLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.096,0.129",
        )
        self.findAndClickPic(
            "遗忘之林",
            "远古干尸",
            "远古干尸",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.121,0.113",
        )

        # 0.162,0.132
        self.findAndClickPic(
            "遗忘之林",
            "暴力熊",
            "暴力熊",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.162,0.132",
        )
        # 进入第二层
        self.waitForAAndClickB1(
            "远古溶洞",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 0.176,0.124
        self.findAndClickPic(
            "远古溶洞",
            "永恒之火",
            "永恒之火",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.176,0.124",
        )
        # 退出副本
        self.outScript("远古溶洞")
        return True

    # 80精英
    def bamenScript(self):
        if self.overed:
            return
        print("开始80精英")
        isInGuanDu = self.waitFor("许昌", self.dituLocation, 5)
        if not isInGuanDu:
            self.feiFb("副本分身", True)
        # 进入80精英  0.108,0.134
        self.findAndClickPic(
            "许昌",
            self.get_resource_path(
                "serveAssets/images/richang/zuocifenshen.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/zuocifenshen1.bmp"),
            self.gameLocation,
            "进精英",
            self.gameBottomLocation,
            "0.108,0.134",
        )
        self.waitForAAndClickB1("魔岛入口", "进精英", self.dituLocation,
                                self.gameBottomLocation)
        isInMojing = self.waitFor("魔岛入口", self.dituLocation, 8)
        if not isInMojing:
            print("80精英没次数了")
            return False
        # 进入幻境凶  0.134,0.141
        self.findAndClickPic(
            "魔岛入口",
            "凶",
            "凶",
            self.dituLocation,
            "凶",
            self.dituLocation,
            "0.134,0.141",
        )
        # 打妖族之王 0.083.0.129
        self.findAndClickPic(
            "凶",
            "妖族",
            "妖族",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.083,0.129",
        )
        # 进入地牢  0.067,0.108
        self.waitForAAndClickB1(
            "地牢",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituRightLocation,
        )
        # 打穷奇   0.067,0.108
        self.findAndClickPic(
            "地牢",
            "穷奇",
            "穷奇",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.067,0.108",
        )
        # 进入二层
        self.findAndClickPic(
            "地牢",
            "地牢二层",
            "地牢二层",
            self.dituLocation,
            "地牢二层",
            self.dituLocation,
            "0.013,0.127",
        )
        # self.waitForAAndClickB1(
        # 	'地牢二层',
        # 	self.get_resource_path("serveAssets/images/richang/dilaochuansongmen.bmp"),
        # 	self.dituLocation,
        # 	self.dituRightLocation
        # )
        # 打吕布  0.127,0.113
        self.findAndClickPic(
            "地牢二层",
            "妖化",
            "妖化",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.127,0.113",
        )
        # 进入boss
        self.waitForAAndClickB1(
            "阵枢",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituRightLocation,
        )
        # 打boss
        self.findAndClickPic(
            "阵枢",
            "妖化",
            "妖化",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        # 退出副本
        self.outScript(
            "阵枢",
        )
        return True

    # 官渡精英
    def guanduJyScript(self):
        print("开始官渡精英")
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        isInGuanDu = self.waitFor("官渡", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图官渡",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xuchang.bmp"),
                "官渡",
                "驿站城西",
                "驿站许昌",
                True,
            )
        # 进入官渡
        self.findAndClickPic(
            "官渡",
            self.get_resource_path("serveAssets/images/guandu/caocao1.bmp"),
            self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
            self.gameLocation,
            "进精英",
            self.gameBottomLocation,
            "0.038,0.134",
            "",
        )
        # 进入第一层
        self.waitForAAndClickB1(
            "大帐",
            "进精英",
            self.dituLocation,
            self.gameLeftLocation,
        )
        isInMojing = self.waitFor("大帐", self.dituLocation, 5)
        if not isInMojing:
            print("官渡精英没次数了")
            return False
        self.waitForAAndClickB1(
            "战场",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 第一个河北军  0.153,0.122
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "战场",
            "河北军",
            f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.153,0.122",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 第二个河北军  0.117,0.124
        self.findAndClickPic(
            "战场",
            "河北军",
            f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.117,0.129",
        )
        # 颜良  0.097,0.124
        self.findAndClickPic(
            "战场",
            self.get_resource_path("serveAssets/images/guandu/yanliang.bmp"),
            f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.097,0.124",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 文丑  0.077,0.122
        self.findAndClickPic(
            "战场",
            self.get_resource_path("serveAssets/images/guandu/wenchou.bmp"),
            f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.077,0.122",
            "",
        )
        # 去大帐
        self.waitForAAndClickB1(
            "大帐",
            self.get_resource_path(
                "serveAssets/images/guandu/jy1chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        self.waitFor("大帐", self.dituLocation)
        # 找到曹操进入乌巢
        self.waitForAAndClickB1(
            "知道了",
            self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
            self.gameLeftLocation,
            self.dituLocation,
        )
        self.waitForAAndClickB1(
            "粮仓",
            "知道了",
            self.dituLocation,
            self.gameLeftLocation,
        )
        self.waitForAAndClickB1(
            "魂殿",
            self.get_resource_path(
                "serveAssets/images/guandu/jygohundianchuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        self.waitFor("魂殿", self.dituLocation)
        # 0.167,0.103
        self.findAndClickPic(
            "魂殿",
            "文丑之魂",
            "文丑之魂",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.167,0.103",
        )
        # 打董卓 0.142,0.115
        self.findAndClickPic(
            "魂殿",
            "董卓",
            "董卓",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.142,0.115",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 魂殿进乌巢
        self.waitForAAndClickB1(
            "粮仓",
            self.get_resource_path(
                "serveAssets/images/guandu/hundianchuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 打淳
        self.findAndClickPic(
            "粮仓",
            "淳于琼",
            f"{self.get_resource_path('serveAssets/images/guandu/cyq1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq2.bmp')}",
            self.gameLeftLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameLeftLocation,
            "0.161,0.129",
            "",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 打袁绍
        self.findAndClickPic(
            "粮仓",
            self.get_resource_path("serveAssets/images/guandu/yuanshao.bmp"),
            f"{self.get_resource_path('serveAssets/images/guandu/yuanshao1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yuanshao2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameLeftLocation,
            "0.152,0.124",
            "",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 退出副本
        self.outScript("粮仓")
        # time.sleep(0.5)
        # self.click_image(self.get_resource_path("serveAssets/images/guaji.bmp"), 0.7, self.gameBottomLocation)
        # self.waitFor('官渡', self.dituLocation)
        return True

    # 云游精英
    def yunyouJyScript(self):
        if self.overed:
            return
        print("开始云游精英")
        with condition:
            if self.stoped:
                condition.wait()
        isInGuanDu = self.waitFor("嵩山", self.dituLocation, 5)
        if not isInGuanDu:
            self.feiFb("副本仙人", True)
        # 进入云游  0.186,0.105
        self.findAndClickPic(
            "嵩山",
            "云游仙人",
            f"{self.get_resource_path('serveAssets/images/richang/yunyouxianren1.bmp')}|{self.get_resource_path('serveAssets/images/richang/yunyouxianren.bmp')}",
            self.gameLocation,
            "进精英",
            self.gameBottomLocation,
            "0.187,0.101",
        )
        # 进入第一层
        self.waitForAAndClickB1("东海之极", "进精英", self.dituLocation,
                                self.gameBottomLocation)
        isInMojing = self.waitFor("东海之极", self.dituLocation, 5)
        if not isInMojing:
            print("云游精英没次数了")
            return False
        # 进鬼气林
        # self.waitForAAndClickB1(
        # 	'鬼气林',
        # 	self.get_resource_path("serveAssets/images/richang/yunyou1chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        self.findAndClickPic(
            "东海之极",
            self.get_resource_path(
                "serveAssets/images/richang/yunyou1chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/yunyou1chuansongmen.bmp"),
            self.dituLocation,
            "鬼气林",
            self.dituLocation,
            "",
        )
        # 打黑无常 0.141,0.112
        self.findAndClickPic(
            "鬼气林",
            "黑无常",
            "黑无常",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.141,0.112",
        )
        # 进东海之极
        self.waitForAAndClickB1(
            "东海之极",
            self.get_resource_path(
                "serveAssets/images/richang/guiqilinchuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        self.confidenceNum = 0.8
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            "东海之极",
            f"{self.get_resource_path('serveAssets/images/richang/zixiaxianzi.bmp')}|{self.get_resource_path('serveAssets/images/richang/jintianti.bmp')}|{self.get_resource_path('serveAssets/images/richang/jintianti1.bmp')}|{self.get_resource_path('serveAssets/images/richang/jintianti2.bmp')}",
            "进天梯",
            self.gameBottomLocation,
            "天梯",
            self.dituLocation,
            "",
        )
        self.confidenceNum = 0.9
        # 打张辽 0.146,0.118
        self.findAndClickPic(
            "天梯",
            "天界",
            "天界",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.146,0.118",
        )
        # 进云端
        self.waitForAAndClickB1(
            "云端",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 进入第一个传送门 0.034,0.124
        self.findAndClickPic(
            "云端",
            "天界精英",
            "天界精英",
            self.dituLocation,
            "天界精英",
            self.dituLocation,
            "0.034,0.124",
        )
        # 0.054,0.122
        self.findAndClickPic(
            "天界精英",
            "天界分身新",
            "天界分身",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.054,0.122",
        )
        # 进云端
        self.findAndClickPic(
            "天界精英",
            "云端",
            "云端",
            self.dituLocation,
            "云端",
            self.dituLocation,
            "0.014,0.131",
        )
        # 进地狱打巨灵神  0.012,0.127
        self.findAndClickPic(
            "云端",
            "地狱",
            "地狱",
            self.dituLocation,
            "地狱",
            self.dituLocation,
            "0.012,0.127",
        )
        # 0.146,0.118
        self.findAndClickPic(
            "地狱",
            "地狱分",
            "地狱分",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.146,0.118",
        )
        # 进云端
        self.waitForAAndClickB1(
            "云端",
            self.get_resource_path(
                "serveAssets/images/richang/diyuchuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 进人界
        self.findAndClickPic(
            "云端",
            "人界",
            "人界",
            self.dituLocation,
            "人界",
            self.dituLocation,
            "0.012,0.127",
        )
        # 打人界巨灵神0.095,0.134
        self.findAndClickPic(
            "人界",
            "人间分身新",
            "天界分身新",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.095,0.134",
        )
        # 进云端
        self.waitForAAndClickB1(
            "云端",
            self.get_resource_path(
                "serveAssets/images/richang/renjiechuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 打boss  0.1,0.115
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.click_delay = 1
        self.findAndClickPic(
            "云端",
            "巨灵神",
            "巨灵神",
            self.gameLeftLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.1,0.134",
            "",
            "down",
        )
        self.click_delay = 0.5
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 退出副本
        self.outScript("云端")
        return True

    # 100精英
    def laoshuJyScript(self):
        if self.overed:
            return
        print("开始老鼠精英")
        with condition:
            if self.stoped:
                condition.wait()
        isInGuanDu = self.waitFor("碧水地穴", self.dituLocation, 5)
        if not isInGuanDu:
            self.feiFb("副本猎鼠人", True)
        # 进入老鼠  0.086,0.103
        self.findAndClickPic(
            "碧水地穴",
            self.get_resource_path("serveAssets/images/richang/lieshuren.bmp"),
            self.get_resource_path("serveAssets/images/richang/lieshuren1.bmp"),
            self.gameLocation,
            "进精英",
            self.gameBottomLocation,
            "0.086,0.103",
        )
        # 进入第一层
        self.waitForAAndClickB1(
            "鼠穴入口",
            "进精英",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInMojing = self.waitFor("鼠穴入口", self.dituLocation, 5)
        if not isInMojing:
            print("老鼠精英没次数了")
            return False
        # 打妖鼠头领  0.152,0.122
        self.findAndClickPic(
            "鼠穴入口",
            "妖鼠头领2",
            "妖鼠头领",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.152,0.122",
        )
        # 进入下一层
        self.findAndClickPic(
            "鼠穴入口",
            "鼠穴",
            "鼠穴",
            self.dituLocation,
            "鼠穴",
            self.dituLocation,
            "0.187,0.139",
        )
        # self.waitForAAndClickB1(
        # 	'鼠穴',
        # 	self.get_resource_path("serveAssets/images/richang/laoshu1chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 打猎杀鼠  0.097,0.124
        self.findAndClickPic(
            "鼠穴",
            "暗杀鼠2",
            "暗杀鼠2",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.097,0.124",
        )
        # 进入下一层
        self.findAndClickPic(
            "鼠穴",
            "鼠巢内",
            "鼠巢内",
            self.dituLocation,
            "鼠巢内",
            self.dituLocation,
            "0.187,0.127",
        )
        # self.waitForAAndClickB1(
        # 	'鼠巢内',
        # 	self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
        # 	self.dituLocation,
        # 	self.dituLocation,
        # )
        # 打鼠长老  0.143,0.112
        self.findAndClickPic(
            "鼠巢内",
            "鼠长老",
            "鼠长老",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.143,0.112",
        )
        self.findAndClickPic(
            "鼠巢内",
            self.get_resource_path(
                "serveAssets/images/richang/shuchaoneichuansongmen1.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/shuchaoneichuansongmen1.bmp"),
            self.dituLocation,
            "鼠大厅",
            self.dituLocation,
            "",
        )
        # 进入下一层
        # self.waitForAAndClickB1(
        # 	'鼠大厅',
        # 	self.get_resource_path("serveAssets/images/richang/shuchaoneichuansongmen1.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 打boss1  0.108,0.11
        self.findAndClickPic(
            "鼠大厅",
            "碧水鼠王",
            "碧水鼠王",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.108,0.11",
        )
        # 进入下一层
        self.waitForAAndClickB1(
            "鼠巢内",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        self.waitFor("鼠巢内", self.dituLocation)
        # 进入boss
        self.waitForAAndClickB1(
            "鼠殿",
            self.get_resource_path(
                "serveAssets/images/richang/shuchaoneichuansongmen2.bmp"),
            self.dituLocation,
            self.gameLocation,
        )
        # 打boss1
        self.findAndClickPic(
            "鼠殿",
            "碧水鼠王",
            "碧水鼠王",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        # 退出副本
        self.outScript("鼠殿")
        return True

    # 三顾茅庐
    def sangumaoluScript(self):
        print("开始三顾茅庐")
        isInGuanDu = self.waitFor(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            self.dituLocation,
            5,
        )
        if not isInGuanDu:
            self.go_in_ditu(
                "地图新野",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                self.get_resource_path(
                    "serveAssets/images/sangumaolu/xinye.bmp"),
                "",
                "",
                True,
            )
        with condition:
            if self.stoped:
                condition.wait()
        d_pos = "0.127,0.129".split(",")
        d_pos[0] = (1000 - int(
            float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
        d_pos[1] = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
        self.dm.MoveToEx(
            int(int(d_pos[0]) + self.locationX),
            int(int(d_pos[1]) + self.locationY),
            3,
            2,
        )
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(1)
        self.confidenceNum = 0.8
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}",
            f"{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/xiaolvren.bmp')}",
            (773, 34, 827, 78),
            "进入",
            self.gameBottomLocation,
            "0.127,0.129",
        )
        self.confidenceNum = 0.9
        time.sleep(1)
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        self.confidenceNum = 0.6
        self.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            f"{self.get_resource_path('serveAssets/images/sangumaolu/liubei3.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/liubei4.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang2.bmp')}",
            "前往茅庐",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sangumaolu/maolu.bmp"),
            self.dituLocation,
            "",
        )

        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/maolu.bmp"),
            f"{self.get_resource_path('serveAssets/images/sangumaolu/tongzi1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/tongzi2.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru2.bmp')}",
            "进入阵法",
            self.gameBottomLocation,
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            self.dituLocation,
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.confidenceNum = 0.9
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            "七星灯",
            "七星灯",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            "占卜币",
            f"{self.get_resource_path('serveAssets/images/richang/tongqian1.bmp')}|{self.get_resource_path('serveAssets/images/richang/tongqian2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            "巨石阵兽",
            "巨石阵兽",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.076,0.115",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            "占卜币",
            f"{self.get_resource_path('serveAssets/images/richang/tongqian1.bmp')}|{self.get_resource_path('serveAssets/images/richang/tongqian2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.076,0.115",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/yanminzhenfa.bmp"),
            "七星灯",
            "七星灯",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.076,0.115",
        )
        self.confidenceNum = 0.6
        self.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            f"{self.get_resource_path('serveAssets/images/sangumaolu/liubei3.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/liubei4.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang2.bmp')}",
            "再次前往茅庐",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sangumaolu/maolu.bmp"),
            self.dituLocation,
            "",
        )
        self.confidenceNum = 0.9
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/maolu.bmp"),
            f"{self.get_resource_path('serveAssets/images/sangumaolu/tongzi1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/tongzi2.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/jinru2.bmp')}",
            "进入阵法",
            self.gameBottomLocation,
            self.get_resource_path(
                "serveAssets/images/sangumaolu/baguaqunmozhen.bmp"),
            self.dituLocation,
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.confidenceNum = 0.9
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/baguaqunmozhen.bmp"),
            "七星灯",
            "七星灯",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.143,0.117",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/baguaqunmozhen.bmp"),
            "占卜币",
            f"{self.get_resource_path('serveAssets/images/richang/tongqian1.bmp')}|{self.get_resource_path('serveAssets/images/richang/tongqian2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.125,0.127",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/sangumaolu/baguaqunmozhen.bmp"),
            "八卦阵灵",
            "八卦阵灵",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.101,0.122",
        )
        # self.confidenceNum = 0.6
        self.color_format = "b@ffff00-000000|0ff000-000000|00ff00-000000|fff200-000000"
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/xinye.bmp"),
            f"{self.get_resource_path('serveAssets/images/sangumaolu/liubei3.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/liubei4.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/qianwang2.bmp')}",
            "再次前往茅庐",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sangumaolu/zhugelu.bmp"),
            self.dituLocation,
            "",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sangumaolu/zhugelu.bmp"),
            "孔明",
            self.get_resource_path(
                "serveAssets/images/sangumaolu/zhugeliang1.bmp"),
            self.gameLocation,
            # '一言为定',
            f"{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding2.bmp')}",
            self.gameBottomLocation,
            "0.076,0.16",
        )
        self.confidenceNum = 0.9
        self.dm.MoveTo(279, 347)
        while not self.find_pic_or_str(
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd11.bmp')}",
                self.gameBottomLocation,
                0,
        ):
            time.sleep(0.001)
            self.dm.LeftClick()
            self.click_image(
                f"{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding1.bmp')}|{self.get_resource_path('serveAssets/images/sangumaolu/yiyanweiding2.bmp')}",
                0.6,
                self.gameBottomLocation,
            )
            time.sleep(0.5)
        self.confidenceNum = 0.9
        self.outScript(
            self.get_resource_path("serveAssets/images/sangumaolu/zhugelu.bmp"))
        return True

    # 名将挑战赛
    def mingjiangtiaozhan(self):
        if self.overed:
            return
        print("名将挑战赛")
        with condition:
            if self.stoped:
                condition.wait()
        # 进入
        isInGuanDu = self.waitFor("洛阳", self.dituLocation, 5)
        if not isInGuanDu:
            self.feiFb("副本挑战赛", True)
        with condition:
            if self.stoped:
                condition.wait()
        # 进入战魂
        self.findAndClickPic(
            "洛阳",
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/zhanhuntiaozhanditu.bmp"),
            self.gameBottomLocation,
            "进名将挑战",
            self.gameBottomLocation,
            "0.067,0.132",
        )
        # 点击进入战魂
        self.waitForAAndClickB1(
            "武神殿",
            "进名将挑战",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("武神殿", self.dituLocation, 8)
        if not isInZhanhun:
            print("名将没次数了")
            return False
        # 打刘备
        self.findAndClickPic(
            "武神殿",
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangliubei2.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangliubei.bmp"),
            self.gameBottomLocation,
            "挑战",
            self.gameBottomLocation,
            "0.156,0.144",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            "挑战",
            self.gameBottomLocation,
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
        )
        # 打张飞
        self.findAndClickPic(
            "武神殿",
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangzhangfei1.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangzhangfei.bmp"),
            self.gameBottomLocation,
            "挑战",
            self.gameBottomLocation,
            "0.142,0.115",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            "挑战",
            self.gameBottomLocation,
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
        )
        # 打关羽
        self.findAndClickPic(
            "武神殿",
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangguanyu1.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/mingjiangguanyu.bmp"),
            self.gameBottomLocation,
            "挑战",
            self.gameBottomLocation,
            "0.043,0.144",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            "挑战",
            self.gameBottomLocation,
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
        )
        # 打吕布
        self.findAndClickPic(
            "武神殿",
            self.get_resource_path(
                "serveAssets/images/richang/mingjianglvbu1.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/mingjianglvbu.bmp"),
            self.gameBottomLocation,
            "挑战",
            self.gameBottomLocation,
            "0.063,0.113",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            "挑战",
            self.gameBottomLocation,
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
        )
        # 找守卫
        self.findAndClickPic(
            "武神殿",
            self.get_resource_path(
                "serveAssets/images/richang/tianwaitianshouwei.bmp"),
            self.get_resource_path(
                "serveAssets/images/richang/tianwaitianshouwei1.bmp"),
            self.gameLocation,
            "进天外",
            self.gameBottomLocation,
            "0.063,0.113",
        )
        self.waitForAAndClickB1(
            "天外天",
            "进天外",
            self.dituLocation,
            self.gameBottomLocation,
        )
        chanchu_pos = [
            "0.121,0.112",
            "0.104,0.103",
            "0.078,0.108",
            "0.067,0.118",
            "0.046,0.106",
            "0.038,0.113",
        ]
        self.findAndClickPic(
            "天外天",
            "地穴蟾蜍",
            self.get_resource_path("serveAssets/images/richang/chanchu.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.14,0.119",
        )
        for i in range(6):
            self.findAndClickPic(
                "天外天",
                "地穴蟾蜍",
                self.get_resource_path(
                    "serveAssets/images/richang/chanchu.bmp"),
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                chanchu_pos[i],
            )
        waitForTwoRes = self.waitForTwo(
            "出现",
            "运气太烂",
            self.gameBottomLocation,
        )
        if waitForTwoRes == "second":
            print("没有守财奴")
            return True
        time.sleep(0.5)
        self.dm.KeyPressChar("g")
        self.waitFor("洛阳", self.dituLocation)
        return True

    # 一直执行天外天
    def mingjiangtiaozhanWhile(self):
        for i in range(int(self.mingjiang_count)):
            if self.overed:
                return
            zhanhunRes = self.mingjiangtiaozhan()
            if not zhanhunRes:
                print("名将没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 名将闯关
    def mingjiangchuangguan(self):
        isInGuanDu = self.waitFor("城西", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
        # 进入魔镜
        self.findAndClickPic(
            "城西",
            "名将使者",
            f"{self.get_resource_path('serveAssets/images/mingjiangshizhe1.bmp')}|{self.get_resource_path('serveAssets/images/mingjiangshizhe2.bmp')}",
            self.gameBottomLocation,
            "进入",
            self.gameBottomLocation,
            "0.074,0.138",
        )
        self.waitForAAndClickB1(
            "名战殿",
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInHong = self.waitFor("名战殿", self.dituLocation, 8)
        if not isInHong:
            print("名将时间到了")
            return False
        time.sleep(0.5)
        self.dm.KeyPressChar("g")
        self.waitFor("城西", self.dituLocation)
        return True

    # 帮派任务
    def bangpaiRW(self, rw_name):
        """帮派任务自动化执行方法

        功能：
        1. 导航到帮派大本营
        2. 查找并点击任务目标（偷盗小贼、挑战者、谣言传播者、西凉马贼、灵宝凶兽）
        3. 处理对话框和交互按钮
        """
        # 常量定义
        TARGET_PATTERN = "偷盗小贼|挑战者|谣言传播者|西凉马贼|灵宝凶兽"
        BUTTON_COLOR = "ffff00-000000|fff200-000000"
        COLOR_SIM = 0.7
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/longdao/dabenying.bmp"),
            self.get_resource_path("serveAssets/images/longdao/guanjia1.bmp"),
            self.get_resource_path("serveAssets/images/longdao/guanjia.bmp"),
            self.gameLocation,
            "帮派大本营",
            self.gameBottomLocation,
            "0.107,0.156",
        )
        rw_name_pos = self.waitFor(rw_name, self.gameBottomLocation, 2)
        if not rw_name_pos:
            return
        self.dm.MoveTo(rw_name_pos.x, rw_name_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()
        # 处理"点击继续"对话框
        self._handle_continue_dialog()
        # 点击第二个按钮（可能需要双击）
        self._click_color_button(249, 340, 291, 352, BUTTON_COLOR, COLOR_SIM,
                                 double_click=True)
        # 判断是否在帮派大本营页面
        self.color_format = "00ffff-000000"
        if self.waitFor("帮派大本营1", (0, 100, 900, 580), 3):
            print("在大本营")
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            self._handle_in_camp_scenario(TARGET_PATTERN, BUTTON_COLOR,
                                          COLOR_SIM, rw_name)
        else:
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            self._handle_outside_camp_scenario(TARGET_PATTERN, BUTTON_COLOR,
                                               COLOR_SIM, rw_name)

    def _click_color_button(self, x1, y1, x2, y2, color, sim,
                            double_click=False, timeout=3):
        """点击指定区域内的颜色按钮

        Args:
            x1, y1, x2, y2: 查找区域坐标
            color: 颜色值
            sim: 相似度
            double_click: 是否双击
            timeout: 等待颜色出现的超时时间（秒），默认3秒
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            dm_ret = self.dm.FindColor(x1, y1, x2, y2, color, sim, 0)
            x, y, r = dm_ret
            if r == 1:
                self.dm.MoveTo(x, y)
                time.sleep(0.5)
                self.dm.LeftClick()
                if double_click:
                    time.sleep(0.5)
                    self.dm.LeftClick()
                return True
            time.sleep(0.1)  # 每次查找间隔0.1秒，避免CPU占用过高
        return False

    def _handle_continue_dialog(self):
        """处理"点击继续"对话框"""
        while True:
            self.color_format = "b@ffff00-000000|fff200-000000"
            jixu_pos = self.find_str("点击继续背景", self.gameBottomLocation, 0)
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            if jixu_pos:
                self.dm.MoveTo(jixu_pos.x, jixu_pos.y)
                time.sleep(0.001)
                self.dm.LeftClick()
                time.sleep(0.5)
                self.dm.LeftClick()
                return
            dm_ret = self.dm.FindColor(249, 340, 291, 352, "ffff00-000000", 0.7,
                                       0)
            x, y, r = dm_ret
            if r == 1:
                return
            time.sleep(0.1)

    def _click_feixie_with_wait(self, task_name, timeout=3):
        """在指定时间内等待并点击飞鞋

        Args:
            task_name: 任务名称，用于查找飞鞋
            timeout: 等待超时时间（秒），默认3秒

        Returns:
            bool: 是否成功找到并点击了飞鞋
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            feixie_pos = self.fing_fei_in_image_or_str(
                task_name,
                self.gameLocation,
                self.gameLocation,
                self.get_resource_path("serveAssets/images/fei3.bmp"),
            )
            if feixie_pos:
                self.dm.MoveTo(feixie_pos.x, feixie_pos.y)
                time.sleep(0.5)
                self.dm.LeftClick()
                break
            time.sleep(0.1)  # 每次查找间隔0.1秒，避免CPU占用过高
        if feixie_pos:
            return True
        else:
            return False

    def _find_and_click_target(self, target_pattern, search_region):
        """查找并点击任务目标

        Args:
            target_pattern: 目标匹配模式
            search_region: 搜索区域，默认为None时使用默认区域

        Returns:
            bool: 是否找到并点击了目标
        """
        find_mubiao = self.waitFor(target_pattern, search_region, 2)
        if find_mubiao:
            self.dm.MoveTo(int(find_mubiao.x + 5), int(find_mubiao.y + 5))
            time.sleep(0.5)
            find_mubiao1 = self.waitFor(target_pattern, search_region, 2)
            if find_mubiao1:
                self.dm.MoveTo(int(find_mubiao1.x + 5), int(find_mubiao1.y + 5))
                time.sleep(0.001)
                self.dm.LeftClick()
                return True
        return False

    def _find_target_with_movement(self, target_pattern):
        """通过移动来查找目标（左移->右移的顺序）

        Args:
            target_pattern: 目标匹配模式

        Returns:
            bool: 是否找到并点击了目标
        """
        # 首先尝试直接查找
        self.color_format = "ffff00-000000|fff200-000000|f4f400-000000"
        if self._find_and_click_target(target_pattern, self.gameBottomLocation):
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            return True

        # 尝试左移后查找
        left_x = random.randint(738, 748)
        rand_y = random.randint(61, 80)
        right_x = random.randint(871, 881)
        self.dm.MoveTo(left_x, rand_y)
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(2)
        if self._find_and_click_target(target_pattern, self.gameBottomLocation):
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            return True

        # 尝试右移后查找
        self.dm.MoveTo(right_x, rand_y)
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(4.5)
        if self._find_and_click_target(target_pattern, self.gameBottomLocation):
            self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
            return True
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        return False

    def _handle_in_camp_scenario(self, target_pattern, button_color, color_sim,
                                 rw_name):
        """处理在帮派大本营内的场景"""
        # 查找并点击目标
        if not self._find_target_with_movement(target_pattern):
            return

        time.sleep(0.5)
        # 处理继续对话框
        self._handle_continue_dialog()

        # 点击按钮
        time.sleep(0.5)
        self._click_color_button(249, 340, 291, 352, button_color, color_sim)

        # 返回管家
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/longdao/dabenying.bmp"),
            self.get_resource_path("serveAssets/images/longdao/guanjia1.bmp"),
            self.get_resource_path("serveAssets/images/longdao/guanjia.bmp"),
            self.gameLocation,
            "帮派大本营",
            self.gameBottomLocation,
            "0.107,0.156",
        )

        rw_name_pos = self.waitFor(rw_name, self.gameBottomLocation)
        self.dm.MoveTo(rw_name_pos.x, rw_name_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()
        # 双击确认按钮（可能需要进行两次）
        self.color_format = "ffff00-000000|fff200-000000"
        wancheng_name_pos = self.waitFor("完成", self.gameBottomLocation)
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.dm.MoveTo(wancheng_name_pos.x, wancheng_name_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()

    def _handle_outside_camp_scenario(self, target_pattern, button_color,
                                      color_sim, rw_name):
        """处理不在帮派大本营的场景（通过飞鞋传送）"""
        # 点击飞鞋（3秒内等待）
        self._click_feixie_with_wait("帮派任务", timeout=3)
        # 处理继续对话框
        self._handle_continue_dialog()
        # 点击按钮
        self._click_color_button(249, 340, 291, 352, button_color, color_sim)

        # 等待加载完成
        self.confidenceNum = 0.6
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd111.bmp"),
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/fei3.bmp"),
            self.gameBottomLocation,
        )
        self.confidenceNum = 0.9

        time.sleep(1)
        # 再次点击飞鞋（3秒内等待）
        self._click_feixie_with_wait("帮派任务", timeout=3)

        # 等待进入帮派大本营
        self.waitFor("帮派大本营", self.gameBottomLocation)
        # 双击确认按钮（可能需要进行两次）
        rw_name_pos = self.waitFor(rw_name, self.gameBottomLocation)
        self.dm.MoveTo(rw_name_pos.x, rw_name_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()
        # 双击确认按钮（可能需要进行两次）
        self.color_format = "ffff00-000000|fff200-000000"
        wancheng_name_pos = self.waitFor("完成", self.gameBottomLocation)
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        self.dm.MoveTo(wancheng_name_pos.x, wancheng_name_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()

    def auto_move_and_click1(self, region, pic_names, interval=0.5,
                             timeout=600):
        x1, y1, x2, y2 = region
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 生成随机位置
            rand_x = random.randint(x1, x2)
            rand_y = random.randint(y1, y2)
            # 移动鼠标到随机位置
            self.dm.MoveTo(rand_x, rand_y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(1.5)  # 移动后稍作停顿

            # 在区域内查找图片
            ret = self.find_pic_or_str(pic_names, self.gameLocation, 0)
            if ret:
                # 移动鼠标到图片位置并点击
                self.dm.MoveTo(ret.x, ret.y)
                time.sleep(1)
                self.dm.LeftClick()
                return True  # 成功找到并点击

            time.sleep(interval)  # 等待下次查找

        print("超时未找到图片")
        return False  # 超时未找到

    def xiguaScriptWhile(self):
        self.findAndClickPic(
            "洛阳",
            self.get_resource_path("serveAssets/images/longzhixintiao1.bmp"),
            self.get_resource_path("serveAssets/images/longzhixintiao.bmp"),
            self.gameBottomLocation,
            "进西瓜",
            self.gameBottomLocation,
            "0.077,0.143",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/xigua/nongshe.bmp"),
            "进西瓜",
            self.dituLocation,
            self.gameBottomLocation,
        )
        self.confidenceNum = 0.9
        if self.overed:
            return
        isInHong = self.waitFor(
            self.get_resource_path("serveAssets/images/xigua/nongshe.bmp"),
            self.dituLocation,
            8,
        )
        if not isInHong:
            print("活动结束了")
            return False
        while True:
            if self.check_stop_or_over():
                return
            overMojing = self.xiguaScript()
            if not overMojing:
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 西瓜保卫战
    def xiguaScript(self):
        self.heifengCount += 1
        print(f"第{self.heifengCount}次西瓜保卫战.")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/xigua/nongshe.bmp"),
            f"{self.get_resource_path('serveAssets/images/xiaolvren.bmp')}|{self.get_resource_path('serveAssets/images/xigua/guanong.bmp')}|{self.get_resource_path('serveAssets/images/xigua/guanong1.bmp')}",
            "进入",
            self.gameLocation,
            self.get_resource_path("serveAssets/images/xigua/xiguatian.bmp"),
            self.dituLocation,
            "0.083,0.113",
        )
        self.auto_move_and_click1(
            (735, 52, 894, 87),
            self.get_resource_path("serveAssets/images/xigua/xiaodao.bmp"),
        )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/xigua/xiaodao.bmp"),
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/xigua/nongshe.bmp"),
            self.dituLocation,
            "",
        )
        return True

    # 黑风
    def heifengScript(self):
        if self.overed:
            return
        isInGuanDu = self.waitFor("五层", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图五层",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "五层",
                "驿站城西",
                "",
                True,
            )
        self.heifengCount += 1
        print(f"第{self.heifengCount}次黑风.")
        with condition:
            if self.stoped:
                condition.wait()
        # 进入黑风
        self.findAndClickPic(
            "五层",
            self.get_resource_path("serveAssets/images/heifeng/11.bmp"),
            self.get_resource_path("serveAssets/images/heifeng/bashanhu.bmp"),
            self.gameLeftLocation,
            "黑风山寨",
            self.gameLeftLocation,
            "0.166,0.12",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 进入第一层
        self.waitForAAndClickB1(
            "黑风山寨",
            "黑风山寨",
            self.dituLocation,
            self.gameLeftLocation,
        )
        # 打刀贼
        daozei_poss = ["0.076,0.131", "0.096,0.121", "0.117,0.129"]
        self.findAndClickPic(
            "黑风山寨",
            "刀贼",
            f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.044,0.12",
        )
        for i in range(2):
            self.findAndClickPic(
                "黑风山寨",
                "刀贼",
                f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
                self.gameRightLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                daozei_poss[i],
            )
        self.findAndClickPic(
            "黑风山寨",
            "刀贼",
            f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
            self.gameRightLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            daozei_poss[2],
        )
        # 81  72
        self.findAndClickPic(
            "黑风山寨",
            "头目",
            "头目",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.153,0.123",
        )
        # 进入第二层
        self.findAndClickPic(
            "黑风山寨",
            self.get_resource_path(
                "serveAssets/images/heifeng/heifeng1chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/heifeng/heifeng1chuansongmen1.bmp"),
            self.dituLocation,
            "山寨本营",
            self.dituLocation,
            "",
        )
        # 50*74 65*83 109*80
        # self.waitForAAndClickB1(
        # 	'山寨本营',
        # 	self.get_resource_path("serveAssets/images/heifeng/heifeng1chuansongmen.bmp"),
        # 	self.dituLocation,
        # 	self.dituLocation
        # )
        # self.waitFor('山寨本营', self.dituLocation)
        #
        if "大" in self.heifengFloor:
            if self.heifengFloor == "大全程":
                quanshi_poss = ["0.055,0.127", "0.078,0.144", "0.121,0.138"]
                for item in quanshi_poss:
                    self.findAndClickPic(
                        "山寨本营",
                        "拳师",
                        "拳师",
                        self.gameRightLocation,
                        self.get_resource_path("serveAssets/images/zdzd.bmp"),
                        self.gameBottomLocation,
                        item,
                    )
            self.findAndClickPic(
                "山寨本营",
                "头目",
                "头目",
                self.gameBottomLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                "0.177,0.141",
            )
            self.findAndClickPic(
                "山寨本营",
                self.get_resource_path("serveAssets/images/heifeng/midong.bmp"),
                self.get_resource_path("serveAssets/images/heifeng/midong.bmp"),
                self.dituLocation,
                self.get_resource_path("serveAssets/images/heifeng/midong.bmp"),
                self.dituLocation,
                "0.177,0.103",
            )
            # 打二当家
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/heifeng/midong.bmp"),
                "当家",
                "当家",
                self.gameBottomLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                "0.142,0.11",
            )
            # 退出副本
            self.outScript(
                self.get_resource_path("serveAssets/images/heifeng/midong.bmp"),
            )
            return True
        else:
            # self.waitForAAndClickB1(
            # 	'山寨内堂',
            # 	self.get_resource_path("serveAssets/images/heifeng/chuansongmen2.bmp"),
            # 	self.dituLocation,
            # 	self.dituCenterLocation
            # )
            if self.heifengFloor == "二全程":
                quanshi_poss = ["0.055,0.127", "0.078,0.144", "0.121,0.138"]
                for item in quanshi_poss:
                    self.findAndClickPic(
                        "山寨本营",
                        "拳师",
                        "拳师",
                        self.gameRightLocation,
                        self.get_resource_path("serveAssets/images/zdzd.bmp"),
                        self.gameBottomLocation,
                        item,
                    )
                self.findAndClickPic(
                    "山寨本营",
                    "头目",
                    "头目",
                    self.gameBottomLocation,
                    self.get_resource_path("serveAssets/images/zdzd.bmp"),
                    self.gameBottomLocation,
                    "0.177,0.141",
                )
            self.findAndClickPic(
                "山寨本营",
                self.get_resource_path(
                    "serveAssets/images/heifeng/chuansongmen2.bmp"),
                self.get_resource_path(
                    "serveAssets/images/heifeng/chuansongmen2.bmp"),
                self.dituCenterLocation,
                "山寨内堂",
                self.dituLocation,
                "",
            )
            # 打二当家
            self.findAndClickPic(
                "山寨内堂",
                "当家",
                "当家",
                self.gameBottomLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                "0.127,0.141",
            )
            # 退出副本
            self.outScript("山寨内堂")
            return True

    # 矿产
    def kuangchanScript(self):
        if self.overed:
            return
        self.heifengCount += 1
        print(f"第{self.heifengCount}次矿产.")
        with condition:
            if self.stoped:
                condition.wait()
        isInGuanDu = self.waitFor("五层", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图五层",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "五层",
                "驿站城西",
                "",
                True,
            )
        # 进入矿产
        self.findAndClickPic(
            "五层",
            self.get_resource_path("serveAssets/images/heifeng/11.bmp"),
            self.get_resource_path("serveAssets/images/heifeng/bashanhu.bmp"),
            self.gameLeftLocation,
            "破旧矿产",
            self.gameLeftLocation,
            "0.166,0.12",
        )
        # 进入第一层
        self.waitForAAndClickB1(
            "矿场洞窟",
            "破旧矿产",
            self.dituLocation,
            self.gameLeftLocation,
        )
        # 打矿工凶灵
        chikuang_poss = [
            "0.044,0.134",
            "0.072,0.136",
            "0.102,0.131",
            "0.127,0.139",
            "0.154,0.134",
        ]
        for i1 in range(5):
            self.findAndClickPic(
                "矿场洞窟",
                "矿工凶灵",
                f"{self.get_resource_path('serveAssets/images/heifeng/xiongling1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/xiongling2.bmp')}",
                self.gameRightLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                chikuang_poss[i1],
            )
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "矿场洞窟",
            "吃矿小鬼",
            "吃矿小鬼",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.184,0.132",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 进入第二层
        self.waitForAAndClickB1(
            "矿场内",
            self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        # 打矿工凶灵
        chikuang_poss1 = [
            "0.125,0.127",
            "0.163,0.141",
            "0.188,0.12",
            "0.063,0.137",
            "0.032,0.139",
        ]
        self.findAndClickPic(
            "矿场内",
            "矿工凶灵",
            self.get_resource_path("serveAssets/images/heifeng/xiongling2.bmp"),
            self.gameRightLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.097,0.138",
        )
        for i in range(4):
            self.findAndClickPic(
                "矿场内",
                "矿工凶灵",
                f"{self.get_resource_path('serveAssets/images/heifeng/xiongling1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/xiongling2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                chikuang_poss1[i],
            )
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "矿场内",
            "吃矿小鬼",
            "吃矿小鬼",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            chikuang_poss1[4],
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 进入第三层  0.043,0.12
        self.findAndClickPic(
            "矿场内",
            "岩石洞",
            "岩石洞",
            self.dituLocation,
            "岩石洞",
            self.dituLocation,
            "0.043,0.12",
        )
        # 打炼矿小鬼
        liankuang_poss = ["0.144,0.132", "0.11,0.144", "0.087,0.131",
                          "0.066,0.139"]
        for i in range(4):
            self.findAndClickPic(
                "岩石洞",
                "炼矿小鬼",
                f"{self.get_resource_path('serveAssets/images/heifeng/liankuang1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/liankuang2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                liankuang_poss[i],
            )
        self.color_format = "ffffff-00000|00ff00-000000|00fe0d-000000"
        self.findAndClickPic(
            "岩石洞",
            "炎魔神",
            "炎魔神",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.05,0.127",
        )
        self.color_format = "ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000"
        # 退出副本
        self.outScript("岩石洞")
        return True

    # 龙岛
    def longdaoScript(self):
        if self.overed:
            return
        print(f"开始龙岛")
        isInGuanDu = self.waitFor("城西", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图城西",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/luoyang.bmp"),
                "城西",
                "驿站城西",
                "",
                True,
            )
        # 进入龙岛
        self.findAndClickPic(
            "城西",
            self.get_resource_path("serveAssets/images/longdao/bangpai.bmp"),
            self.get_resource_path("serveAssets/images/longdao/bangpai1.bmp"),
            self.gameBottomLocation,
            "进龙岛",
            self.gameBottomLocation,
            "0.123,0.139",
        )
        self.waitForAAndClickB1(
            "龙岛",
            "进龙岛",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("龙岛", self.dituLocation, 8)
        if not isInZhanhun:
            print("龙岛没次数了")
            return False
        # 打守门人
        self.findAndClickPic(
            "龙岛",
            self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
            self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
            self.dituLocation,
            "挑战龙族",
            self.gameBottomLocation,
            "",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            "挑战龙族",
            self.gameBottomLocation,
            self.gameBottomLocation,
        )
        self.waitFor(
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
        )
        self.findAndClickPic(
            "龙岛",
            "进入",
            "进入",
            self.gameBottomLocation,
            "密洞",
            self.dituLocation,
            "",
        )
        self.findAndClickPic(
            "密洞",
            "金龙王新",
            self.get_resource_path("serveAssets/images/richang/jinlongwang1.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.036,0.131",
        )
        if self.heifengFloor == "大/80":
            self.findAndClickPic(
                "密洞",
                "龙巢",
                "龙巢",
                self.dituLocation,
                "龙巢",
                self.dituLocation,
                "0.182,0.127",
            )
        else:
            self.findAndClickPic(
                "密洞",
                "龙巢",
                "龙巢",
                self.dituLocation,
                "龙巢",
                self.dituLocation,
                "0.18,0.158",
            )
        if self.heifengFloor == "刷龙珠":
            self.findAndClickPic(
                "龙巢",
                "地狱炎龙",
                "五爪金龙",
                self.gameBottomLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                "0.183,0.134",
            )
            self.outScript("龙巢")
            return True
        longchao_poss = [
            "0.02,0.113",
            "0.036,0.131",
            "0.048,0.117",
            "0.075,0.131",
            "0.091,0.122",
            "0.121,0.144",
            "0.142,0.143",
            "0.153,0.131",
        ]
        for index, item in enumerate(longchao_poss):
            self.findAndClickPic(
                "龙巢",
                "龙孙|龙孙一|龙子|龙子一",
                f"{self.get_resource_path('serveAssets/images/longdao/longsun.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longsun1.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longzi.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longzi1.bmp')}",
                self.gameRightLocation if index < 5 else self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                item,
            )
        self.findAndClickPic(
            "龙巢",
            "地狱炎龙",
            "五爪金龙",
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.183,0.134",
        )
        self.outScript("龙巢")
        return True

    # 龙珠
    def longzhuScript(self):
        self.heifengCount += 1
        print(f"第{self.heifengCount}次龙珠.")
        self.findAndClickPic(
            "洛阳",
            self.get_resource_path("serveAssets/images/longzhu/laoyufu.bmp"),
            self.get_resource_path("serveAssets/images/longzhu/laoyufu1.bmp"),
            self.gameBottomLocation,
            "龙巢",
            self.gameBottomLocation,
            "0.1,0.139",
        )
        self.waitForAAndClickB1(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaojingwai.bmp"),
            "龙巢",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaojingwai.bmp"),
            self.dituLocation,
            8,
        )
        if not isInZhanhun:
            print("龙巢没次数了")
            return False
        longzhuPos = [
            "0.161,0.127",
            "0.134,0.134",
            "0.094,0.12",
            "0.063,0.136",
            "0.028,0.122",
        ]
        for index, item in enumerate(longzhuPos):
            self.findAndClickPic(
                self.get_resource_path(
                    "serveAssets/images/longzhu/longchaojingwai.bmp"),
                "寻宝者",
                f"{self.get_resource_path('serveAssets/images/longzhu/xunbaozhe1.bmp')}|{self.get_resource_path('serveAssets/images/longzhu/xunbaozhe2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                item,
            )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaojingwai.bmp"),
            self.get_resource_path(
                "serveAssets/images/longzhu/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/longzhu/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaorukou.bmp"),
            self.dituLocation,
            "893,78",
        )
        longzhuPos1 = [
            "0.172,0.129",
            "0.15,0.122",
        ]
        for index, item in enumerate(longzhuPos1):
            self.findAndClickPic(
                self.get_resource_path(
                    "serveAssets/images/longzhu/longchaorukou.bmp"),
                "寻宝者",
                 f"{self.get_resource_path('serveAssets/images/longzhu/xunbaozhe1.bmp')}|{self.get_resource_path('serveAssets/images/longzhu/xunbaozhe2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                item,
            )
        longzhuPos2 = [
            "0.13,0.132",
            "0.094,0.122",
            "0.074,0.127",
        ]
        for index, item in enumerate(longzhuPos2):
            self.findAndClickPic(
                self.get_resource_path(
                    "serveAssets/images/longzhu/longchaorukou.bmp"),
                "挖宝人",
                 f"{self.get_resource_path('serveAssets/images/longzhu/wabaoren1.bmp')}|{self.get_resource_path('serveAssets/images/longzhu/wabaoren2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                item,
            )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaorukou.bmp"),
            self.get_resource_path(
                "serveAssets/images/longzhu/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/longzhu/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaojingnei.bmp"),
            self.dituLocation,
            "888,75",
        )
        longzhuPos3 = [
            "755,77",
            "779,72",
            "808,79",
            "829,77",
            "868,79",
        ]
        for index, item in enumerate(longzhuPos3):
            self.findAndClickPic(
                self.get_resource_path(
                    "serveAssets/images/longzhu/longchaojingnei.bmp"),
                "单龙|御剑仙女",
                f"{self.get_resource_path('serveAssets/images/longzhu/longhufa1.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/longhufa2.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yanlong1.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yanlong2.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yujianxiannv1.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yujianxiannv2.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yunlonghuwei1.bmp')}|"
                f"{self.get_resource_path('serveAssets/images/longzhu/yunlonghuwei2.bmp')}",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                item,
            )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaojingnei.bmp"),
            self.get_resource_path(
                "serveAssets/images/longzhu/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaoxue.bmp"),
            self.dituLocation,
            "891,79",
        )
        self.findAndClickPic(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaoxue.bmp"),
            '金龙君王|炎龙|神龙守护者',
            f'{self.get_resource_path("serveAssets/images/longzhu/jinlongjunwang1.bmp")}|{self.get_resource_path("serveAssets/images/longzhu/jinlongjunwang2.bmp")}|{self.get_resource_path("serveAssets/images/longzhu/shenlong1.bmp")}|{self.get_resource_path("serveAssets/images/longzhu/shenlong2.bmp")}',
            self.gameRightLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "881,88",
        )
        self.outScript(
            self.get_resource_path(
                "serveAssets/images/longzhu/longchaoxue.bmp"),
        )
        return True

    # 四象脚本
    def sixiangScript(self):
        print("四象脚本")
        with condition:
            if self.stoped:
                condition.wait()
        isInGuanDu = self.waitFor(self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"), self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图封魔遗迹",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/xiangyang.bmp"),
                self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                "",
                "",
                True,
            )
        # 进入四象
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            f"{self.get_resource_path('serveAssets/images/sixiang/sixiangshizhe1.bmp')}|{self.get_resource_path('serveAssets/images/sixiang/sixiangshizhe.bmp')}",
            self.get_resource_path('serveAssets/images/sixiang/xiaolvren.bmp'),
            self.gameLocation,
            self.sixiang_difficulty,
            self.gameBottomLocation,
            "862,66",
        )
        # 进入第一层
        self.waitForAAndClickB1(self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"), self.sixiang_difficulty, self.dituLocation,
                                self.gameBottomLocation)
        isInMojing = self.waitFor(self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"), self.dituLocation, 5)
        if not isInMojing:
            print("四象没次数了")
            return False
        self.huifu_yijian_main()
        time.sleep(1)
        _sixiang_auto_combat = "四象" in self.combat_auto_scenes and self.sixiang_difficulty in ("精英", "炼狱")
        if _sixiang_auto_combat:
            self._start_combat_auto(combat_scene="四象")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            '玄水龙马',
            '玄水龙马',
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if _sixiang_auto_combat:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("玄水马龙没打过")
            self._update_dungeon_stats("四象", "fail")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            self.dituLocation,
            "814,90",
        )
        self.huifu_yijian_main()
        time.sleep(1)
        if _sixiang_auto_combat:
            self._start_combat_auto(combat_scene="四象",clear_enemy_keys=["玄武"])
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            '玄武',
            '玄武',
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "858,64",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if _sixiang_auto_combat:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("玄武没打过")
            self._update_dungeon_stats("四象", "fail")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/hanyuanbindian.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.dituLocation,
            "748,71",
        )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            self.dituLocation,
            "855,65",
        )
        self.huifu_yijian_main()
        time.sleep(1)
        if _sixiang_auto_combat:
            self._start_combat_auto(combat_scene="四象")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            '朱雀',
            '朱雀',
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "851,68",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if _sixiang_auto_combat:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("朱雀没打过")
            self._update_dungeon_stats("四象", "fail")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/chiyantiangong.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.dituLocation,
            "755,83",
        )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            self.dituLocation,
            "810,52",
        )
        self.huifu_yijian_main()
        time.sleep(1)
        if _sixiang_auto_combat:
            self._start_combat_auto(combat_scene="四象")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            '青龙',
            '青龙',
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "857,88",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if _sixiang_auto_combat:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("青龙没打过")
            self._update_dungeon_stats("四象", "fail")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/cangleizhuhai.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.dituLocation,
            "752,73",
        )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/sixiangjitan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
            self.dituLocation,
            "768,70",
        )
        self.huifu_yijian_main()
        time.sleep(1)
        if _sixiang_auto_combat:
            self._start_combat_auto(combat_scene="四象")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
            '白虎',
            '白虎',
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "862,67",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)
        if _sixiang_auto_combat:
            self._stop_combat_auto()
        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
            self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("白虎没打过")
            self._update_dungeon_stats("四象", "fail")
            return True
        self.outScript(
            self.get_resource_path(
                "serveAssets/images/sixiang/xuezhanhuangyuan.bmp"),
        )
        self._update_dungeon_stats("四象", "win")
        return True

    # 藏宝图脚本
    def cangbaotuScript(self):
        # cangbaotu_pos = None
        # shiyong_pos = None
        # queding_pos = None
        # cangbaotu_pos = None
        while True:
            self.click_image(
                f"{self.get_resource_path('serveAssets/images/cangbaotu.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu1.bmp')}",
                0.8,
                self.gameLocation,
            )
            self.click_image(
                f"{self.get_resource_path('serveAssets/images/shiyong.bmp')}|{self.get_resource_path('serveAssets/images/shiyong1.bmp')}",
                0.8,
                self.gameLocation,
            )
            self.click_image(
                f"{self.get_resource_path('serveAssets/images/cangbaotuqueding.bmp')}",
                0.8,
                self.gameBottomLocation,
            )
            wabao_pos = self.waitFor(
                '挖宝',
                self.gameRightLocation,0.1
            )
            if not wabao_pos:
                continue
            fei_pos = self.waitFor(
                f"{self.get_resource_path('serveAssets/images/cangbaotufei.bmp')}",
                (wabao_pos.x, wabao_pos.y,wabao_pos.x+110,wabao_pos.y+40)
            )
            self.dm.MoveTo(fei_pos.x, fei_pos.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            self.dm.MoveTo(wabao_pos.x, wabao_pos.y)
            time.sleep(0.001)
            self.dm.LeftClick()

        # self.press_keys_until_image_found(
        #     f"{self.get_resource_path('serveAssets/images/cangbaotu.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu1.bmp')}",
        #     f"{self.get_resource_path('serveAssets/images/cangbaotuqueding.bmp')}",
        #     self.gameLocation,
        #     self.gameBottomLocation,
        #     "使用",
        # )
        # self.dm.MoveTo(447, 321)
        # time.sleep(0.001)
        # self.dm.LeftClick()
        # wabao_pos = self.waitFor(
        #     '挖宝',
        #     self.gameRightLocation
        # )
        # fei_pos = self.waitFor(
        #     f"{self.get_resource_path('serveAssets/images/cangbaotufei.bmp')}",
        #     (wabao_pos.x, wabao_pos.y,wabao_pos.x+110,wabao_pos.y+40)
        # )
        # self.dm.MoveTo(fei_pos.x, fei_pos.y)
        # time.sleep(0.001)
        # self.dm.LeftClick()
        # self.waitFor("挖宝", self.gameRightLocation)
        # self.dm.MoveTo(wabao_pos.x, wabao_pos.y)
        # time.sleep(0.001)
        # self.dm.LeftClick()

    # 藏宝图循环
    def cangbaotuWhile(self):
        while True:
            if self.overed:
                return
            self.cangbaotuScript()

    # 龙珠循环
    def longzhuWhile(self):
        while True:
            if self.overed:
                return
            longzhuRes = self.longzhuScript()
            if not longzhuRes:
                print("龙珠没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 黑风循环
    def heifengWhile(self):
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        isInGuanDu = self.waitFor("五层", self.dituLocation, 5)
        if not isInGuanDu:
            if self.find_str("黑风山寨|山寨本营|山寨内堂", self.dituLocation,
                             0):
                time.sleep(0.5)
                self.outScript()
                time.sleep(2)
            else:
                self.go_in_ditu(
                    "地图五层",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "五层",
                    "驿站城西",
                    "",
                    True,
                )
        for i in range(self.heifengWhileCount):
            if self.overed:
                return
            self.heifengScript()
            if self.heifengCount >= self.heifengWhileCount:
                break
        print(f"{self.heifengWhileCount}次黑风已完成,去官渡")
        if self.overed:
            return
        self.scriptName = "官渡"
        self.guanduWhile()

    # 一直执行官渡
    def guanduWhile(self):
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        isInGuanDu = self.waitFor("官渡", self.dituLocation, 3)
        if not isInGuanDu:
            if self.find_str("曹操大帐|曹袁战场|鸟巢粮仓|魂殿",
                             self.dituLocation, 0):
                time.sleep(0.5)
                self.outScript()
                time.sleep(2)
            else:
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
        while True:
            if self.check_stop_or_over():
                return
            self.guanduScript()

    # 一直执行英魂
    def hongWhile(self):
        for i in range(int(self.hong_count)):
            if self.overed:
                return
            hongRes = self.hongScript()
            if not hongRes:
                print("红没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 一直执行四象
    def sixiangWhile(self):
        self.sixiang_stats = {"win": 0, "fail": 0, "done": 0, "total": int(self.sixiang_count)}
        if self.frame and hasattr(self.frame, "_refresh_dungeon_stats"):
            wx.CallAfter(self.frame._refresh_dungeon_stats)
        for i in range(int(self.sixiang_count)):
            if self.overed:
                return
            sixiangRes = self.sixiangScript()
            if not sixiangRes:
                print("四象没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 一直执行英魂
    def yinghunWhile(self):
        for i in range(int(self.yinhun_count)):
            if self.overed:
                return
            hongRes = self.yinhunScript()
            if not hongRes:
                print("英魂没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 一直执行战魂
    def zhanhunWhile(self):
        outFbLocation = self.find_pic_or_str(
            f"{self.get_resource_path('serveAssets/images/outFb.bmp')}|{self.get_resource_path('serveAssets/images/outFb1.bmp')}",
            self.gameLocation,
            0,
        )
        if outFbLocation:
            self.dm.MoveTo(outFbLocation.x, outFbLocation.y)
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(0.001)
            self.dm.LeftClick()
            time.sleep(2)
        for i in range(int(self.zhanhun_count)):
            if self.overed:
                return
            zhanhunRes = self.zhanhunScript()
            if not zhanhunRes:
                print("战魂没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 一直执行魔镜
    def mojingWhile(self):
        isInGuanDu = self.waitFor("城西", self.dituLocation, 3)
        if not isInGuanDu:
            if self.find_str(
                    "镜像地层|遗迹镜像|迷幻境|狱境|炎冰境|印魔殿|北境|西境|南境|东境",
                    self.dituLocation,
                    0,
            ):
                time.sleep(0.5)
                self.outScript()
                time.sleep(2)
            else:
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "驿站城西",
                    "",
                    True,
                )
        isInGuanDu1 = self.waitFor("城西", self.dituLocation, 3)
        if not isInGuanDu1:
            if self.find_str(
                    "镜像地层|遗迹镜像|迷幻境|狱境|炎冰境|印魔殿|北境|西境|南境|东境",
                    self.dituLocation,
                    0,
            ):
                time.sleep(0.5)
                self.outScript()
                time.sleep(2)
            else:
                self.feiFb("副本魔镜使者", False)
        while True:
            if self.check_stop_or_over():
                return
            overMojing = self.mojingScript()
            if not overMojing:
                print("魔镜没次数")
                break
        self.scriptName = "官渡"
        self.guanduWhile()

    # 日常一条龙
    def richangeScript(self):
        print("日常")
        # 战魂
        if self.overed:
            return
        if self.richang_zhengdian:
            self.richangAndZhengDian()
        if int(self.zhanhun_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.zhanhun_count)):
                if self.overed:
                    return
                hongRes = self.zhanhunScript()
                if not hongRes:
                    break
        if int(self.lianyu_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.lianyu_count)):
                if self.overed:
                    return
                hongRes = self.zhenhun_lianyu_script()
                if not hongRes:
                    break
        if int(self.shihun_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.shihun_count)):
                if self.overed:
                    return
                hongRes = self.shihun_lianyu_script()
                if not hongRes:
                    break
        # 飞溶洞
        if self.overed:
            return
        if int(self.rongdong_count) > 0:
            if not self.find_str("绿林路", self.dituLocation, 0):
                # self.feiFb('副本龙天啸', False)
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.rongdong_count)):
                if self.overed:
                    return
                hasRongdong = self.rongdongScript()
                if not hasRongdong:
                    break
            time.sleep(1)
        # 飞炼丹
        if self.overed:
            return
        if int(self.liandan_count) > 0:
            if not self.find_str("五指峡谷", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图五指峡谷",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "五指峡谷",
                    "驿站五指峡谷",
                    "",
                    True,
                )
            for i in range(int(self.liandan_count)):
                if self.overed:
                    return
                liandanHas = self.liandanScript()
                if not liandanHas:
                    break
            time.sleep(1)
        # 飞五行
        if self.overed:
            return
        if int(self.wuxing_count) > 0:
            if not self.find_str("野外西", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图野外西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "野外西",
                    "驿站城西",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.wuxing_count)):
                if self.overed:
                    return
                hasWuxing = self.wuxingScript()
                if not hasWuxing:
                    break
            time.sleep(1)
        # 飞四象
        if self.overed:
            return
        if int(self.sixiang_count) > 0:
            if not self.find_pic(
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    self.dituLocation,
                    0,
            ):
                self.go_in_ditu(
                    "地图封魔遗迹",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.sixiang_count)):
                if self.overed:
                    return
                sixiangRes = self.sixiangScript()
                if not sixiangRes:
                    print("四象没次数")
                    break
            time.sleep(1)
        # 飞云游精英
        if int(self.yunyou_count) > 0:
            if self.overed:
                return
            if not self.find_str("嵩山", self.dituLocation, 0):
                # self.feiFb('副本仙人', True)
                self.go_in_ditu(
                    "地图嵩山",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "嵩山",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.yunyouJyScript()
            time.sleep(1)
        # 飞名将挑战赛
        if int(self.mingjiang_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.mingjiang_count)):
                if self.overed:
                    return
                zhanhunRes = self.mingjiangtiaozhan()
                if not zhanhunRes:
                    print("名将没次数")
                    break
            time.sleep(1)

        # 飞80精英
        if int(self.bamen_count) > 0:
            if self.overed:
                return
            if not self.find_str("许昌", self.dituLocation, 0):
                # self.feiFb('副本分身', True)
                self.go_in_ditu(
                    "地图许昌城",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "许昌",
                    "驿站许昌",
                    "",
                    True,
                )
            time.sleep(1)
            self.bamenScript()
            time.sleep(1)
        # 飞100精英
        if int(self.laoshu_count) > 0:
            if not self.find_str("碧水地穴", self.dituLocation, 0):
                # self.feiFb('副本猎鼠人', True)
                self.go_in_ditu(
                    "地图碧水地穴",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    "碧水地穴",
                    "驿站襄阳",
                    "",
                    True,
                )
            time.sleep(1)
            self.laoshuJyScript()
            time.sleep(1)
        # 飞100精英
        if int(self.yinhun_count) > 0:
            if not self.find_pic(
                    self.get_resource_path(
                        "serveAssets/images/hong/luanshipo.bmp"),
                    self.dituLocation,
                    0,
            ):
                # self.feiFb('副本老仙', True)
                self.go_in_ditu(
                    "地图乱石坡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path(
                        "serveAssets/images/hong/luanshipo.bmp"),
                    "驿站襄阳",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.yinhun_count)):
                if self.overed:
                    return
                hongRes = self.yinhunScript()
                if not hongRes:
                    break
        if int(self.sangumaolu_count) > 0:
            if not self.find_pic(
                    self.get_resource_path(
                        "serveAssets/images/sangumaolu/xinye.bmp"),
                    self.dituLocation,
                    0,
            ):
                self.go_in_ditu(
                    "地图新野",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path(
                        "serveAssets/images/sangumaolu/xinye.bmp"),
                    "驿站襄阳",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.sangumaolu_count)):
                if self.overed:
                    return
                hongRes = self.sangumaoluScript()
                if not hongRes:
                    break
        # 红
        if self.overed:
            return
        if int(self.hong_count) > 0:
            if not self.find_str("虎牢关外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.hong_count)):
                if self.overed:
                    return
                hongRes = self.hongScript()
                if not hongRes:
                    break
        if int(self.qingyuan_count) > 0:
            if not self.find_str("虎牢关外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.qingyuan_count)):
                if self.overed:
                    return
                hongRes = self.qingyuanScript()
                if not hongRes:
                    break
        if self.bangpai_enabled:
            if not self.find_str("城西", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            # 进入帮派大本营
            self.findAndClickPic(
                "城西",
                f"{self.get_resource_path('serveAssets/images/longdao/bangpai.bmp')}|{self.get_resource_path('serveAssets/images/longdao/bangpai1.bmp')}",
                "帮派大本营",
                self.gameBottomLocation,
                self.get_resource_path(
                    "serveAssets/images/longdao/dabenying.bmp"),
                self.dituLocation,
                "0.107,0.156",
            )
            for i in range(22):
                if self.check_stop_or_over():
                    return
                if i == 0:
                    rw_name = "抓捕异兽"
                elif i == 1:
                    rw_name = "挑战者黄"
                else:
                    rw_name = "帮派声誉"
                self.bangpaiRW(rw_name)
        # 飞官渡精英
        if int(self.guandujy_count) > 0:
            if self.overed:
                return
            if not self.find_str("官渡", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
            time.sleep(1)
            self.guanduJyScript()
            time.sleep(1)
        if self.overed:
            return
        if self.richang_mojing:
            self.scriptName = "魔镜"
            if self.overed:
                return
            self.mojingWhile()
        else:
            self.scriptName = "官渡"
            if self.overed:
                return
            self.guanduWhile()

    # 五行
    def wuxingWhile(self):
        for i in range(int(self.wuxing_count)):
            if self.overed:
                return
            hasWuxing = self.wuxingScript()
            if not hasWuxing:
                break
        if self.overed:
            return
        self.guanduWhile()

    # 溶洞
    def rongdongWhile(self):
        for i in range(int(self.rongdong_count)):
            if self.overed:
                return
            hasRongdong = self.rongdongScript()
            if not hasRongdong:
                break
        if self.overed:
            return
        self.guanduWhile()

    # 炼丹
    def liandanWhile(self):
        for i in range(int(self.liandan_count)):
            if self.overed:
                return
            liandanHas = self.liandanScript()
            if not liandanHas:
                break
        self.scriptName = "官渡"
        if self.overed:
            return
        self.guanduWhile()

    # 49日常
    def richang49Script(self):
        print("日常")
        if self.overed:
            return
        if self.richang_zhengdian:
            self.richangAndZhengDian()
        if int(self.zhanhun_count) > 0:
            if not self.find_str("涿郡野外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图野外东",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "涿郡野外",
                    "涿郡野外",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.zhanhun_count)):
                hongRes = self.zhanhun49Script()
                if not hongRes:
                    break
        if int(self.lianyu_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.lianyu_count)):
                if self.overed:
                    return
                hongRes = self.zhenhun_lianyu_script()
                if not hongRes:
                    break
        if int(self.shihun_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.shihun_count)):
                if self.overed:
                    return
                hongRes = self.shihun_lianyu_script()
                if not hongRes:
                    break
        # 飞溶洞
        if int(self.rongdong_count) > 0:
            if not self.find_str("绿林路", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.rongdong_count)):
                hasRongdong = self.rongdongScript()
                if not hasRongdong:
                    break
            time.sleep(1)
        # 飞炼丹
        if self.overed:
            return
        if int(self.liandan_count) > 0:
            if not self.find_str("五指峡谷", self.dituLocation, 0):
                if "飞" in self.richangSelection:
                    self.go_in_ditu(
                        "地图五指峡谷",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/zhuojun.bmp"),
                        "五指峡谷",
                        "驿站五指峡谷",
                        "驿站五指峡谷",
                        True,
                    )
            # 	self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '驿站五指峡谷', True)
            # else:
            # 	self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '')
            for i in range(int(self.liandan_count)):
                liandanHas = self.liandanScript()
                if not liandanHas:
                    break
            time.sleep(1)
        # 飞五行
        if self.overed:
            return
        if int(self.wuxing_count) > 0:
            if not self.find_str("野外西", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图野外西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "野外西",
                    "驿站城西",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '驿站城西', '', True)
            # else:
            # 	self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '驿站城西', '')
            time.sleep(1)
            for i in range(int(self.wuxing_count)):
                hasWuxing = self.wuxingScript()
                if not hasWuxing:
                    break
        time.sleep(1)
        # 飞四象
        if self.overed:
            return
        if int(self.sixiang_count) > 0:
            if not self.find_pic(
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    self.dituLocation,
                    0,
            ):
                self.go_in_ditu(
                    "地图封魔遗迹",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.sixiang_count)):
                if self.overed:
                    return
                sixiangRes = self.sixiangScript()
                if not sixiangRes:
                    print("四象没次数")
                    break
            time.sleep(1)
        # 飞名将挑战赛
        if self.overed:
            return
        if int(self.mingjiang_count) > 0:
            if not self.find_str("洛阳", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '', True)
            # else:
            # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '')
            time.sleep(1)
            for i in range(int(self.mingjiang_count)):
                zhanhunRes = self.mingjiangtiaozhan()
                if not zhanhunRes:
                    print("名将没次数")
                    break
            time.sleep(1)
        # 红
        if self.overed:
            return
        if int(self.hong_count) > 0:
            if not self.find_str("虎牢关外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.hong_count)):
                hongRes = self.hongScript()
                if not hongRes:
                    break
        if int(self.qingyuan_count) > 0:
            if not self.find_str("虎牢关外", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.qingyuan_count)):
                if self.overed:
                    return
                hongRes = self.qingyuanScript()
                if not hongRes:
                    break
        if self.bangpai_enabled:
            if not self.find_str("城西", self.dituLocation, 0):
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            # 进入帮派大本营
            self.findAndClickPic(
                "城西",
                f"{self.get_resource_path('serveAssets/images/longdao/bangpai.bmp')}|{self.get_resource_path('serveAssets/images/longdao/bangpai1.bmp')}",
                "帮派大本营",
                self.gameBottomLocation,
                self.get_resource_path(
                    "serveAssets/images/longdao/dabenying.bmp"),
                self.dituLocation,
                "0.107,0.156",
            )
            for i in range(22):
                if self.check_stop_or_over():
                    return
                if i == 0:
                    rw_name = "抓捕异兽"
                elif i == 1:
                    rw_name = "挑战者黄"
                else:
                    rw_name = "帮派声誉"
                self.bangpaiRW(rw_name)
        # 战魂
        if self.overed:
            return

        time.sleep(2)
        self.go_in_ditu(
            "地图城西",
            self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"),
            "城西",
            "驿站城西",
            "",
        )
        if self.richang_mojing:
            self.scriptName = "魔镜"
            if self.overed:
                return
            self.mojingWhile()
        else:
            if self.has_script != "all" and not "整点" in self.has_script:
                return
            print("开始整点")
            self.scriptName = "49整点"
            time.sleep(2)
            while True:
                if self.check_stop_or_over():
                    return
                self.go_zhengdian49()

    # 49战魂
    def zhanhun49Script(self):
        if not self.zhanhunFloor:
            self.zhanhunFloor = "25层"
            print("未选择层数，自动打25层")
        if self.overed:
            return
        print("开始49战魂")
        isInGuanDu = self.waitFor("涿郡野外", self.dituLocation, 5)
        if not isInGuanDu:
            self.go_in_ditu(
                "地图野外东",
                self.get_resource_path(
                    "serveAssets/images/zhengdian/zhuojun.bmp"),
                "涿郡野外",
                "涿郡野外",
                "驿站城西",
                True,
            )
        with condition:
            if self.stoped:
                condition.wait()
        # 进入战魂
        self.findAndClickPic(
            "涿郡野外",
            self.get_resource_path(
                "serveAssets/images/zhanhun/qinshoujiang1.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/qinshoujiang2.bmp"),
            self.gameBottomLocation,
            "战魂楼",
            self.gameBottomLocation,
            "0.181,0.124",
        )
        # 点击进入战魂
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/zhanhun/1.bmp"),
            "战魂楼",
            self.dituLocation,
            self.gameBottomLocation,
        )
        isInZhanhun = self.waitFor("战魂", self.dituLocation, 8)
        if not isInZhanhun:
            print("战魂没次数了")
            return False
        _start_floor = int(self.zhanhun_start_floor.replace("层", "")) if self.zhanhun_start_floor else 1
        # 1
        if _start_floor <= 1:
            self.findAndClickPic(
                "战魂",
                "张宝",
                "张宝",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            "战魂",
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 2
        if _start_floor <= 2:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
                "张梁",
                f"{self.get_resource_path('serveAssets/images/zhanhun/zhangliang1.bmp')}|{self.get_resource_path('serveAssets/images/zhanhun/zhangliang2.bmp')}",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 3
        if _start_floor <= 3:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
                "张角",
                "张角",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 4
        if _start_floor <= 4:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
                "文丑",
                "文丑",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 5
        if _start_floor <= 5:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
                "颜良",
                "颜良",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 6
        if _start_floor <= 6:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
                "华雄",
                "华雄",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 7
        if _start_floor <= 7:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
                "孙策",
                "孙策",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 8
        if _start_floor <= 8:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
                "典韦",
                "典韦",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 9
        if _start_floor <= 9:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
                "郭嘉",
                "郭嘉",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 10
        if _start_floor <= 10:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
                "刘备",
                f"{self.get_resource_path('serveAssets/images/zhanhun/liubei.bmp')}|{self.get_resource_path('serveAssets/images/zhanhun/liubei1.bmp')}",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 11
        if _start_floor <= 11:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
                "曹操",
                "曹操",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 12
        if _start_floor <= 12:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
                "袁绍",
                "袁绍",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 13
        if _start_floor <= 13:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
                "张飞",
                "张飞",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.confidenceNum = 0.7
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
            self.dituLocation,
            "",
        )
        self.confidenceNum = 0.9
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 14
        if _start_floor <= 14:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
                "大乔",
                "大乔",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 15
        if _start_floor <= 15:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
                "关羽",
                "关羽",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 16
        if _start_floor <= 16:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
                "吕布",
                "吕布",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 17
        if _start_floor <= 17:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
                "张飞",
                "张飞",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 18
        if _start_floor <= 18:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
                "关羽",
                "关羽",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 19
        if _start_floor <= 19:
            self.findAndClickPic(
                self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
                "吕布",
                "吕布",
                self.gameBottomLocation,
                f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
                self.gameBottomLocation,
                "0.098,0.113",
            )
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 20
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            "魔化吕布",
            "魔化吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("20层没打过")
            return True
        if self.zhanhunFloor == "20层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            self.dituLocation,
            "",
        )
        # 21
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            "刘备",
            "刘备",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("21层没打过")
            return True
        if self.zhanhunFloor == "21层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 22
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            "袁绍",
            "袁绍",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("22层没打过")
            return True
        if self.zhanhunFloor == "22层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 23
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            "曹操",
            "曹操",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("23层没打过")
            return True
        if self.zhanhunFloor == "23层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 24
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            "吕布",
            "吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )
        self.waitFor(self.get_resource_path("serveAssets/images/xiulian.bmp"),
                     self.gameLocation)

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("24层没打过")
            return True
        if self.zhanhunFloor == "24层":
            # 退出副本
            self.outScript("战魂")
            return True
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.get_resource_path(
                "serveAssets/images/zhanhun/chuansongmen.bmp"),
            self.dituLocation,
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            self.dituLocation,
            "",
        )
        # self.waitForAAndClickB1(
        # 	self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
        # 	self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
        # 	self.dituLocation, self.dituLocation,
        # )
        # 25
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            "魔化吕布",
            "魔化吕布",
            self.gameBottomLocation,
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
            "0.098,0.113",
        )

        self.addBloud()
        waitForTwoRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            "涿郡野外",
            self.dituLocation,
            self.dituLocation,
        )
        if waitForTwoRes == "second":
            print("25层没打过")
            return True
        if self.zhanhunFloor == "25层":
            # 退出副本
            self.outScript(
                self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
            )
            return True
        self.outScript(
            self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
        )
        return True

    # 龙王令
    def longwanglingScript(self):
        if self.overed:
            return
        print("开始打龙王令")
        time.sleep(0.5)
        self.findAndClickPic(
            "洛阳",
            self.get_resource_path("serveAssets/images/longzhixintiao1.bmp"),
            self.get_resource_path("serveAssets/images/longzhixintiao.bmp"),
            self.gameBottomLocation,
            "进龙王令",
            self.gameBottomLocation,
            "0.077,0.143",
        )
        in_pos = self.waitFor("进龙王令", self.gameBottomLocation)
        self.dm.MoveTo(in_pos.x, in_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()
        # self.waitFor('洛阳', self.dituLocation)
        # self.dm.MoveTo(831, 66)
        # time.sleep(0.001)
        # self.dm.LeftClick()
        # self.waitForAAndClickB1('挑战龙', f"{self.get_resource_path('serveAssets/images/longzhixintiao.bmp')}|{self.get_resource_path('serveAssets/images/longzhixintiao1.bmp')}", self.gameBottomLocation, self.gameBottomLocation)
        waitRes = self.waitForTwo(
            self.get_resource_path("serveAssets/images/queding.bmp"),
            "摘星楼",
            self.gameBottomLocation,
            self.dituLocation,
        )
        if waitRes == "first":
            queding_pos = self.waitFor(
                self.get_resource_path("serveAssets/images/queding.bmp"),
                self.gameBottomLocation,
            )
            self.dm.MoveTo(queding_pos.x, queding_pos.y)
            time.sleep(0.001)
            self.dm.LeftClick()
        # if bagPos:
        # 	self.dm.MoveTo(bagPos.x, bagPos.y)
        # 	time.sleep(0.5)
        # 	self.dm.LeftClick()
        # self.confidenceNum = 0.7
        # self.press_keys_until_image_found(
        # 	f"{self.get_resource_path('serveAssets/images/longwang.bmp')}|{self.get_resource_path('serveAssets/images/longwang1.bmp')}|{self.get_resource_path('serveAssets/images/longwang2.bmp')}|{self.get_resource_path('serveAssets/images/longwang3.bmp')}|{self.get_resource_path('serveAssets/images/longwang4.bmp')}",
        # 	'摘星楼',
        # 	self.gameLocation, self.dituLocation, '使用')
        # self.confidenceNum = 0.9
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        self.findAndClickPic(
            "摘星楼",
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp"),
            self.get_resource_path("serveAssets/images/queding.bmp"),
            self.gameLocation,
            "挑战龙",
            self.gameBottomLocation,
            "0.167,0.144",
        )
        self.waitForAAndClickB1("修罗级", "挑战龙", self.gameBottomLocation,
                                self.gameBottomLocation)
        # self.waitFor('修罗级', self.gameBottomLocation)
        self.waitForAAndClickB1("挑战龙", "修罗级", self.gameBottomLocation,
                                self.gameBottomLocation)
        self.waitFor(
            f"{self.get_resource_path('serveAssets/images/zdzd111.bmp')}|{self.get_resource_path('serveAssets/images/zdzd.bmp')}",
            self.gameBottomLocation,
        )
        self.waitForAAndClickB1(
            "修罗级",
            self.get_resource_path(
                "serveAssets/images/zhengdian/xiaolvren.bmp"),
            self.gameBottomLocation,
            self.dituLocation,
        )
        # self.findAndClickPic('摘星楼', self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.dituLocation, '离开', self.gameBottomLocation, '0.167,0.144')
        self.waitForAAndClickB1("修罗级", "离开", self.gameBottomLocation,
                                self.gameBottomLocation)

    # 49一键
    def all49Script(self):
        if self.overed:
            return
        self.richang49Script()
        time.sleep(1)
        self.go_in_ditu(
            "地图野外东",
            self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"),
            "涿郡野外",
            "涿郡野外|驿站城西",
            "",
            True,
        )
        time.sleep(1)
        for i in range(6):
            if self.overed:
                return
            self.zhanhun49Script()

    # 引魔符
    def yinmofuScript(self):
        if self.overed:
            return
        self.guanDuCount += 1
        print(f"开始打第{self.guanDuCount}张引魔符")
        if self.guanDuCount % 100 == 0:
            print("卖装备")
            self.clearBag()
            time.sleep(1)
        time.sleep(0.3)
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        time.sleep(0.1)
        self.confidenceNum = 0.7
        self.press_keys_until_image_found(
            f"{self.get_resource_path('serveAssets/images/ymf.bmp')}|{self.get_resource_path('serveAssets/images/ymf1.bmp')}|{self.get_resource_path('serveAssets/images/ymf2.bmp')}|{self.get_resource_path('serveAssets/images/ymf3.bmp')}|{self.get_resource_path('serveAssets/images/ymf4.bmp')}",
            f"{self.get_resource_path('serveAssets/images/zdzd.bmp')}|{self.get_resource_path('serveAssets/images/zdzd111.bmp')}",
            self.gameLocation,
            self.gameBottomLocation,
            "使用",
        )
        self.confidenceNum = 0.9
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        huodetongbi_pos = self.waitFor("获得铜币", self.gameBottomLocation)
        self.dm.MoveTo(huodetongbi_pos.x, huodetongbi_pos.y)
        time.sleep(0.001)
        self.dm.LeftClick()

    # 传送符
    def chuansongfuScript(self):
        if self.overed:
            return
        self.guanDuCount += 1
        print(f"开始打第{self.guanDuCount}张传送符")
        time.sleep(0.3)
        bagPos = self.waitFor(
            self.get_resource_path("serveAssets/images/beibao.bmp"),
            self.gameBottomLocation,
            5,
        )
        if bagPos:
            self.dm.MoveTo(bagPos.x, bagPos.y)
            time.sleep(0.5)
            self.dm.LeftClick()
        time.sleep(0.1)
        self.confidenceNum = 0.5
        self.press_keys_until_image_found(
            f"{self.get_resource_path('serveAssets/images/chuansongfu.bmp')}|{self.get_resource_path('serveAssets/images/chuansongfu1.bmp')}|{self.get_resource_path('serveAssets/images/chuansongfu2.bmp')}|{self.get_resource_path('serveAssets/images/chuansongfu3.bmp')}|{self.get_resource_path('serveAssets/images/chuansongfu4.bmp')}|{self.get_resource_path('serveAssets/images/chuansongfu5.bmp')}",
            "天外天",
            self.gameLocation,
            self.dituLocation,
            "使用",
        )
        self.confidenceNum = 0.9
        chanchu_pos = [
            "0.121,0.112",
            "0.104,0.103",
            "0.078,0.108",
            "0.067,0.118",
            "0.046,0.106",
            "0.038,0.113",
        ]
        self.dm.KeyPressChar("e")
        time.sleep(0.5)
        self.findAndClickPic(
            "天外天",
            "地穴蟾蜍",
            self.get_resource_path("serveAssets/images/richang/chanchu.bmp"),
            self.gameBottomLocation,
            self.get_resource_path("serveAssets/images/zdzd.bmp"),
            self.gameBottomLocation,
            "0.14,0.119",
        )
        for i in range(6):
            self.findAndClickPic(
                "天外天",
                "地穴蟾蜍",
                self.get_resource_path(
                    "serveAssets/images/richang/chanchu.bmp"),
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd.bmp"),
                self.gameBottomLocation,
                chanchu_pos[i],
            )
        waitForTwoRes = self.waitForTwo(
            "出现",
            "运气太烂",
            self.gameBottomLocation,
        )
        if waitForTwoRes == "second":
            print("没有守财奴")
            return True
        time.sleep(0.5)
        self.dm.KeyPressChar("g")
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        self.waitFor("洛阳", self.dituLocation)

    # 挂机+整点
    def guajiAndzhengdianScript(self, base_image=None):
        print("挂机+整点")
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        # 打开副本
        if not self.guajiLocation:
            guaji_pos = self.waitFor(
                self.get_resource_path("serveAssets/images/guaji/guaji1.bmp"),
                self.gameLocation,
                10,
            )
            if guaji_pos:
                self.guajiLocation = guaji_pos
            else:
                print("未找到挂机")
                return
        else:
            time.sleep(1.5)
            self.dm.MoveTo(int(self.locationX + 608), int(self.locationY + 45))
            time.sleep(0.05)
            self.dm.LeftClick()
        self.dm.MoveTo(self.guajiLocation.x, self.guajiLocation.y)
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(0.001)
        self.dm.LeftClick()
        time.sleep(5)
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        while True:
            if self.check_stop_or_over():
                return
            with condition:
                if self.stoped:
                    condition.wait()
            current_time = time.localtime()
            if current_time.tm_min == 58:
                if self.find_pic_or_str("挂机中", self.gameBottomLocation, 0):
                    is_stop_guaji = self.click_image(
                        self.get_resource_path(
                            "serveAssets/images/closeJJ.bmp"),
                        self.confidenceNum,
                        self.gameBottomLocation,
                    )
                    if is_stop_guaji:
                        break
            time.sleep(1)  # 每秒钟检查一次
        time.sleep(1)
        self.clearBag()
        time.sleep(1)
        self.outScript()
        time.sleep(2)
        if self.zhengdianFloor in ["全打", "龙+全打", "蛇+全打"]:
            # 打整点
            self.zhengdian_flag = True
            self.new_zhengdian()
            return
        elif self.zhengdianFloor == "走路":
            # 打整点
            self.zhengdian_flag = True
            self.go_zhengdian()
            return
        elif self.zhengdianFloor in ["49整点", "49蛇+全打", "49龙+全打"]:
            # 打整点
            self.zhengdian_flag = True
            self.go_zhengdian49()
            return

    # 刷孙策
    def shuasunceScript(self):
        print("刷孙策")
        self.findAndClickPic(
            self.get_resource_path("serveAssets/images/guaji/yuhuayuan.bmp"),
            self.get_resource_path("serveAssets/images/guaji/wangyun.bmp"),
            self.get_resource_path("serveAssets/images/guaji/wangyun1.bmp"),
            self.gameLocation,
            "进入",
            self.gameBottomLocation,
            "0.03,0.112",
        )
        self.waitForAAndClickB1(
            self.get_resource_path("serveAssets/images/guaji/zhanchang.bmp"),
            "进入",
            self.dituLocation,
            self.gameBottomLocation,
        )
        zhanchang_poss = [
            "0.183,0.117",
            "0.163,0.103",
            "0.141,0.12",
            "0.117,0.11",
            "0.094,0.115",
            "0.063,0.11",
            "0.047,0.118",
        ]
        for item in zhanchang_poss:
            self.findAndClickPic(
                self.get_resource_path(
                    "serveAssets/images/guaji/zhanchang.bmp"),
                "战场一",
                "战场一",
                self.gameLeftLocation,
                self.get_resource_path("serveAssets/images/zdzd111.bmp"),
                self.gameBottomLocation,
                item,
            )
        if self.overed:
            return
        with condition:
            if self.stoped:
                condition.wait()
        # 退出副本
        self.outScript(
            self.get_resource_path("serveAssets/images/guaji/zhanchang.bmp"))

    # 怪物攻城
    def gongChengScript(self):
        print("怪物攻城")

        def is_active_time(nowTime):
            """判断是否在有效时间段"""
            return (10 <= nowTime.hour <= 12) or (21 <= nowTime.hour <= 23)

        def get_minute_decade(time_obj):
            """获取分钟十位数 (e.g. 23 -> 2, 5 -> 0)"""
            return time_obj.minute // 10

        def calculate_next_trigger(last_time):
            """计算下次触发时间点"""
            current = datetime.now()

            # 情况1：当前已超出记录时间的小时段
            if current.hour > last_time.hour:
                return current.replace(second=0, microsecond=0) + timedelta(
                    seconds=1)

            # 情况2：需要等待分钟十位数变化
            current_decade = get_minute_decade(current)
            last_decade = get_minute_decade(last_time)

            if current_decade > last_decade:
                return current.replace(second=0, microsecond=0) + timedelta(
                    seconds=1)

            # 计算下一个十位数的起始分钟
            next_decade = (last_decade + 1) % 6  # 十位数循环0-5
            next_minute = next_decade * 10

            if next_minute >= 60 or next_minute == 0:
                return current.replace(hour=current.hour + 1, minute=0,
                                       second=0, microsecond=0)
            else:
                return current.replace(minute=next_minute, second=0,
                                       microsecond=0)

        def precise_wait(target):
            """高精度等待（误差<1ms）"""
            delta = (target - datetime.now()).total_seconds()
            if delta <= 0:
                return
            time.sleep(delta - 0.001)
            while datetime.now() < target:
                pass

        # 主控制逻辑
        while True:
            now = datetime.now()
            if self.overed:
                return
            with condition:
                if self.stoped:
                    condition.wait()
            # 阶段1：等待进入有效时间段
            if not is_active_time(now):
                # 计算最近的合法时间段起始点
                candidates = [
                    now.replace(hour=10, minute=0, second=0, microsecond=0),
                    now.replace(hour=21, minute=0, second=0, microsecond=0),
                ]
                valid_starts = [t for t in candidates if t > now]
                if not valid_starts:  # 处理跨天情况
                    next_day = now + timedelta(days=1)
                    valid_starts.append(
                        next_day.replace(hour=10, minute=0, second=0))

                next_start = min(valid_starts)
                precise_wait(next_start)

            # 阶段2：在有效时间段内执行
            last_exec_time = None
            while is_active_time(datetime.now()):
                # 记录执行前时间
                start_time = datetime.now()
                print(f"开始执行于 {start_time.strftime('%H:%M:%S')}")

                # 执行目标函数
                print("等待五秒开始，防止野外北怪物延迟出现")
                time.sleep(5)
                self.go_gongcheng()
                self.go_gongcheng()
                # 计算下次触发时间
                next_trigger = calculate_next_trigger(start_time)
                print(f"下次计划执行于 {next_trigger.strftime('%H:%M:%S')}")

                # 精确等待到触发点
                precise_wait(next_trigger)

    # 日常+整点
    def richangAndZhengDian(self):
        if not self.zhengdianFloor:
            self.show_error_message("请选择整点再启动!")
            return
        if self.has_script != "all" and not "整点" in self.has_script:
            self.show_error_message("没有整点脚本!")
            return
        filter_list = []
        for name, count in [("战", self.zhanhun_count), ("镇", self.lianyu_count),
                            ("噬", self.shihun_count), ("溶", self.rongdong_count),
                            ("丹", self.liandan_count), ("五", self.wuxing_count),
                            ("四", self.sixiang_count), ("云", self.yunyou_count), ("名", self.mingjiang_count),
                            ("八", self.bamen_count), ("鼠", self.laoshu_count), ("英", self.yinhun_count),
                            ("庐", self.sangumaolu_count), ("红", self.hong_count),
                            ("渊", self.qingyuan_count), ("帮", 22 if self.bangpai_enabled else 0),
                            ("官", self.guandujy_count), ("镜", 1)]:
            if int(count) > 0:
                filter_list.append(name)
        self.riChangList = (
            self.process_data(self.riChangList, filter_list)
            if self.scriptName == "日常"
            else self.process_data(self.riChang49List, filter_list)
        )
        while not self.richangIsOver():
            if self.overed:
                return
            with condition:
                if self.stoped:
                    condition.wait()
            remaining_minutes = self.get_remaining_minutes()
            result_item = self.find_optimal_item(remaining_minutes)
            if not result_item and not self.richangIsOver():
                if remaining_minutes >= 2:
                    print("等整点时打官渡")
                    self.guanduScript()
                    continue
                if self.richang_mojing and remaining_minutes >= 2:
                    print("等整点时打魔镜")
                    self.mojingScript()
                    continue
                print("打整点")
                if self.zhengdianFloor in ["龙+全打", "全打", "蛇+全打"]:
                    # 打整点
                    self.zhengdian_flag = True
                    time.sleep(2)
                    self.new_zhengdian()
                elif self.zhengdianFloor == "走路":
                    # 打整点
                    self.zhengdian_flag = True
                    time.sleep(2)
                    self.go_zhengdian()
                elif self.zhengdianFloor in ["49整点", "49蛇+全打", "49龙+全打"]:
                    # 打整点
                    self.zhengdian_flag = True
                    time.sleep(2)
                    self.go_zhengdian49()
            else:
                self.run_script(result_item)
        if self.richang_mojing:
            self.scriptName = "魔镜"
            if self.overed:
                return
            self.mojingWhile()
        elif self.scriptName == "49日常":
            print("开始整点")
            self.scriptName = "49整点"
            time.sleep(2)
            while True:
                if self.check_stop_or_over():
                    return
                self.go_zhengdian49()
        else:
            self.scriptName = "官渡"
            if self.overed:
                return
            self.guanduWhile()

    def richangIsOver(self):
        flag = True
        for item in self.riChangList:
            if item["count"] > 0:
                flag = False
                break
        return flag

    def run_script(self, result_item):
        print(f"{result_item['name']}{result_item['count']}")
        start_minute = datetime.now().minute
        if "战" == result_item["name"]:
            if self.scriptName == "日常":
                if not self.waitFor("洛阳", self.dituLocation, 2):
                    self.go_in_ditu(
                        "地图洛阳大道",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/luoyang.bmp"),
                        "洛阳",
                        "",
                        "",
                        True,
                    )
                # if '飞' in self.richangSelection:
                # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '', True)
                # else:
                # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '')
                time.sleep(1)
                self.zhanhunScript()
            else:
                if not self.waitFor("涿郡野外", self.dituLocation, 2):
                    self.go_in_ditu(
                        "地图野外东",
                        self.get_resource_path(
                            "serveAssets/images/zhengdian/zhuojun.bmp"),
                        "涿郡野外",
                        "涿郡野外",
                        "",
                        True,
                    )
                time.sleep(1)
                self.zhanhun49Script()
        elif "镇" == result_item["name"]:
            if not self.waitFor("洛阳", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.zhenhun_lianyu_script()
        elif "噬" == result_item["name"]:
            if not self.waitFor("洛阳", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.shihun_lianyu_script()
        # 飞溶洞
        if self.overed:
            return
        elif "溶" == result_item["name"]:
            if not self.waitFor("绿林路", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图绿林路",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "绿林路",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
            time.sleep(1)
            for i in range(int(self.rongdong_count)):
                if self.overed:
                    return
                hasRongdong = self.rongdongScript()
                if not hasRongdong:
                    break
            time.sleep(1)
        # 飞炼丹
        if self.overed:
            return
        elif "丹" == result_item["name"]:
            if not self.waitFor("五指峡谷", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图五指峡谷",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/zhuojun.bmp"),
                    "五指峡谷",
                    "驿站五指峡谷",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '', True)
            # else:
            # 	self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '')
            self.liandanScript()
            time.sleep(1)
        # 飞五行
        if self.overed:
            return
        elif "五" == result_item["name"]:
            if not self.waitFor("野外西", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图野外西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "野外西",
                    "驿站城西",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	# self.feiFb('副本老板', True)
            # 	self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '驿站城西', '', True)
            # else:
            # 	self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '驿站城西', '')
            time.sleep(1)
            self.wuxingScript()
        # 飞云游精英
        if self.overed:
            return
        elif "云" == result_item["name"]:
            if not self.waitFor("嵩山", self.dituLocation, 2):
                # self.feiFb('副本仙人', True)
                self.go_in_ditu(
                    "地图嵩山",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "嵩山",
                    "",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.feiFb('副本仙人', True)
            # else:
            # 	self.go_in_ditu('地图嵩山', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '嵩山', '', '')
            time.sleep(1)
            self.yunyouJyScript()
            time.sleep(1)
        # 飞名将挑战赛
        elif "名" == result_item["name"]:
            if not self.waitFor("洛阳", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图洛阳大道",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "洛阳",
                    "",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '', True)
            # else:
            # 	self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '')
            time.sleep(1)
            self.mingjiangtiaozhan()
            time.sleep(1)

        elif "八" == result_item["name"]:
            if not self.waitFor("许昌", self.dituLocation, 2):
                # self.feiFb('副本分身', True)
                self.go_in_ditu(
                    "地图许昌城",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "许昌",
                    "驿站许昌",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.feiFb('副本分身', True)
            # else:
            # 	self.go_in_ditu('地图许昌城', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '许昌', '驿站许昌', '')
            time.sleep(1)
            self.bamenScript()
            time.sleep(1)
        # 飞100精英
        elif "鼠" == result_item["name"]:
            if not self.waitFor("碧水地穴", self.dituLocation, 2):
                # self.feiFb('副本猎鼠人', True)
                self.go_in_ditu(
                    "地图碧水地穴",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    "碧水地穴",
                    "驿站襄阳",
                    "",
                    True,
                )
            # if '飞' in self.richangSelection:
            # 	self.feiFb('副本猎鼠人', True)
            # else:
            # 	self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', "驿站城西", '')
            # 	time.sleep(1)
            # 	self.go_in_ditu('地图碧水地穴', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '碧水地穴', '驿站襄阳', '')
            time.sleep(1)
            self.laoshuJyScript()
            time.sleep(1)
        # 飞100精英
        elif "英" == result_item["name"]:
            if not self.waitFor(
                    self.get_resource_path(
                        "serveAssets/images/hong/luanshipo.bmp"),
                    self.dituLocation,
                    2,
            ):
                # self.feiFb('副本老仙', True)
                self.go_in_ditu(
                    "地图乱石坡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path(
                        "serveAssets/images/hong/luanshipo.bmp"),
                    "驿站襄阳",
                    "",
                    True,
                )
            time.sleep(1)
            self.yinhunScript()
        elif "庐" == result_item["name"]:
            if not self.waitFor(
                    self.get_resource_path(
                        "serveAssets/images/sangumaolu/xinye.bmp"),
                    self.dituLocation,
                    2,
            ):
                # self.feiFb('副本老仙', True)
                self.go_in_ditu(
                    "地图新野",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path(
                        "serveAssets/images/sangumaolu/xinye.bmp"),
                    "驿站襄阳",
                    "",
                    True,
                )
            time.sleep(1)
            self.sangumaoluScript()
        # 红
        if self.overed:
            return
        elif "红" == result_item["name"]:
            if not self.waitFor("虎牢关外", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.hongScript()
        elif "渊" == result_item["name"]:
            if not self.waitFor("虎牢关外", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图虎牢关外",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "虎牢关外",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.qingyuanScript()
        # 飞官渡精英
        if self.overed:
            return
        elif "帮" == result_item["name"]:
            if not self.waitFor("城西", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图城西",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/luoyang.bmp"),
                    "城西",
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            # 进入帮派大本营
            self.findAndClickPic(
                "城西",
                f"{self.get_resource_path('serveAssets/images/longdao/bangpai.bmp')}|{self.get_resource_path('serveAssets/images/longdao/bangpai1.bmp')}",
                "帮派大本营",
                self.gameBottomLocation,
                self.get_resource_path(
                    "serveAssets/images/longdao/dabenying.bmp"),
                self.dituLocation,
                "0.107,0.156",
            )
            for i in range(22):
                if self.check_stop_or_over():
                    return
                # 根据循环次数传入不同的任务名称
                if i == 0:
                    rw_name = "抓捕异兽"
                elif i == 1:
                    rw_name = "挑战者黄"
                else:
                    rw_name = "帮派声誉"
                self.bangpaiRW(rw_name)
        # 飞官渡精英
        if self.overed:
            return
        elif "四" == result_item["name"]:
            if not self.find_pic(self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"), self.dituLocation, 0):
                self.go_in_ditu(
                    "地图封魔遗迹",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xiangyang.bmp"),
                    self.get_resource_path("serveAssets/images/sixiang/fengmoyiji.bmp"),
                    "",
                    "",
                    True,
                )
            time.sleep(1)
            self.sixiangScript()
        # 飞官渡精英
        if self.overed:
            return
        elif "官" == result_item["name"]:
            if not self.waitFor("官渡", self.dituLocation, 2):
                self.go_in_ditu(
                    "地图官渡",
                    self.get_resource_path(
                        "serveAssets/images/zhengdian/xuchang.bmp"),
                    "官渡",
                    "驿站城西",
                    "驿站许昌",
                    True,
                )
            time.sleep(1)
            self.guanduJyScript()
        time.sleep(1)
        use_minute = datetime.now().minute - start_minute
        print(f"耗时{use_minute}分钟")
        for item in self.riChangList:
            if item == result_item:
                item["count"] -= 1
                item["time"] = use_minute

    def process_data(self, source_list, filter_names):
        filter_set = set(filter_names)
        result = []
        for item in source_list:
            if item["name"] in filter_set:
                new_item = item.copy()
                if new_item["name"] == "镇":
                    new_item["count"] = self.lianyu_count
                elif new_item["name"] == "渊":
                    new_item["count"] = self.qingyuan_count
                elif new_item["name"] == "溶":
                    new_item["count"] = 1  # 调度用count=1，循环次数在执行时取
                elif new_item["name"] == "丹":
                    new_item["count"] = self.liandan_count
                elif new_item["name"] == "五":
                    new_item["count"] = self.wuxing_count
                elif new_item["name"] == "英":
                    new_item["count"] = self.yinhun_count
                elif new_item["name"] == "庐":
                    new_item["count"] = self.sangumaolu_count
                elif new_item["name"] == "红":
                    new_item["count"] = self.hong_count
                elif new_item["name"] == "帮":
                    new_item["count"] = 22 if self.bangpai_enabled else 0
                elif new_item["name"] == "名":
                    new_item["count"] = self.mingjiang_count
                if new_item["name"] == "战":
                    new_item["count"] = self.zhanhun_count
                if new_item["name"] == "噬":
                    new_item["count"] = self.shihun_count
                if new_item["name"] == "四":
                    new_item["count"] = self.sixiang_count
                result.append(new_item)
        return result

    def find_optimal_item(self, time_threshold):
        res = None
        for item in self.riChangList:
            if item["time"] <= time_threshold and item["count"] > 0:
                res = item
                break
        return res

    def get_remaining_minutes(self):
        """计算当前分钟到当前小时59分的剩余分钟数"""
        current_time = datetime.now()
        current_minute = current_time.minute
        return 58 - current_minute

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="脚本", size=(370, 420),
                          style=wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(
            wx.Icon(
                self.get_resource_path("serveAssets/images/script1.ico"),
                wx.BITMAP_TYPE_ICO,
            )
        )
        self.SetPosition(wx.Point(10, 30))
        self.SetBackgroundColour(wx.Colour(243, 244, 248))

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(243, 244, 248))

        # 初始化变量
        self.scriptName = ""
        self.heifengCount = ""
        self.lianyu_count = ""
        self.qingyuan_count = ""
        self.zhanhun_count = ""
        self.zhanhunFloor = ""
        self.zhanhunFloorNew = ""
        self.heifengFloor = ""
        self.choice_line = ""
        self.teammate1_pos = ""
        self.teammate2_pos = ""
        self.team_leader_pos = ""
        self.shihun_count = ""
        self.shihun_floor = ""
        self.zhanhun_start_floor = "1层"
        self.sixiang_count = "21"
        self.sixiang_difficulty = ""
        self.rongdong_count = ""
        self.liandan_count = ""
        self.wuxing_count = ""
        self.yinhun_count = ""
        self.sangumaolu_count = ""
        self.hong_count = ""
        self.yunyou_count = ""
        self.bamen_count = ""
        self.laoshu_count = ""
        self.guandujy_count = ""
        self.bangpai_enabled = False
        self.mingjiang_count = ""
        self.richang_zhengdian = False
        self.richang_mojing = False
        self.addBloudFlag = False
        self.combat_auto_scenes = []
        self.liubeiCounts = {0: 1, 1: 0, 2: 0}
        self.use_heal_item = False
        self.independent_win1 = False
        self.independent_win2 = False

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(8)

        # ── 脚本选择行 ──
        row_top = wx.BoxSizer(wx.HORIZONTAL)
        self.dropdown = None
        lbl = wx.StaticText(self.panel, label="脚本")
        lbl.SetForegroundColour(wx.Colour(50, 80, 140))
        lbl.SetMinSize((36, -1))
        lbl.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        row_top.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.btn_settings = wx.Button(self.panel, size=(30, 30), style=wx.BORDER_NONE)
        self.btn_settings.SetBitmap(self._load_icon("btn_settings.png", 16))
        self.btn_settings.SetBackgroundColour(wx.Colour(215, 218, 226))
        self.btn_settings.SetForegroundColour(wx.Colour(50, 80, 140))
        self.btn_settings.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.btn_settings.Bind(wx.EVT_BUTTON, self.on_button_click)
        row_top.Add(self.btn_settings, 0, wx.ALIGN_CENTER_VERTICAL)

        # self.btn_factory = wx.Button(self.panel, size=(30, 30), style=wx.BORDER_NONE)
        # factory_bmp = wx.Bitmap(wx.Image(self.get_resource_path("serveAssets/images/menu_factory.png")).Scale(20, 20, wx.IMAGE_QUALITY_HIGH))
        # self.btn_factory.SetBitmap(factory_bmp)
        # self.btn_factory.SetBackgroundColour(wx.Colour(215, 218, 226))
        # self.btn_factory.SetToolTip("脚本工厂")
        # self.btn_factory.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        # self.btn_factory.Bind(wx.EVT_BUTTON, self.on_factory_click)
        # row_top.Add(self.btn_factory, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        main_sizer.Add(row_top, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        # ── 控制按钮（开始 F1 · 暂停 F2 · 继续 F3 · 重置 F4） ──
        def _ctrl_btn(name, bg, hotkey):
            vs = wx.BoxSizer(wx.VERTICAL)
            path = self.get_resource_path("serveAssets/images/" + name)
            bmp = wx.Bitmap(wx.Image(path).Scale(28, 28, wx.IMAGE_QUALITY_HIGH))
            btn = wx.Button(self.panel, size=(46, 46), style=wx.BORDER_NONE)
            btn.SetBitmap(bmp)
            btn.SetBackgroundColour(bg)
            btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            vs.Add(btn, 0, wx.ALIGN_CENTER)
            lb = wx.StaticText(self.panel, label=hotkey, style=wx.ALIGN_CENTER)
            lb.SetForegroundColour(wx.Colour(100, 105, 115))
            lb.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            vs.Add(lb, 0, wx.ALIGN_CENTER | wx.TOP, 2)
            return vs, btn

        button_col = wx.BoxSizer(wx.VERTICAL)
        vs1, self.button_start = _ctrl_btn("btn_start.png", wx.Colour(39, 174, 96), "F1")
        self.Bind(wx.EVT_BUTTON, self.button_start_click, self.button_start)
        button_col.Add(vs1, 0, wx.ALIGN_CENTER)
        self.button_start.SetToolTip("开始")
        button_col.AddSpacer(8)
        vs2, self.button_pause = _ctrl_btn("btn_pause.png", wx.Colour(192, 57, 43), "F2")
        self.Bind(wx.EVT_BUTTON, self.button_pause_click, self.button_pause)
        button_col.Add(vs2, 0, wx.ALIGN_CENTER)
        button_col.AddSpacer(8)
        self.button_pause.SetToolTip("暂停")
        vs3, self.button_resume = _ctrl_btn("btn_resume.png", wx.Colour(41, 128, 185), "F3")
        self.Bind(wx.EVT_BUTTON, self.button_resume_click, self.button_resume)
        button_col.Add(vs3, 0, wx.ALIGN_CENTER)
        button_col.AddSpacer(8)
        self.button_resume.SetToolTip("继续")
        vs4, self.button_stop = _ctrl_btn("btn_reset.png", wx.Colour(215, 218, 226), "F4")
        self.Bind(wx.EVT_BUTTON, self.button_stop_click, self.button_stop)
        button_col.Add(vs4, 0, wx.ALIGN_CENTER)
        self.button_stop.SetToolTip("重置")

        content_row = wx.BoxSizer(wx.HORIZONTAL)

        # ── 日志 ──
        log_card = wx.Panel(self.panel)
        log_card.SetBackgroundColour(wx.Colour(240, 242, 246))
        lcs = wx.BoxSizer(wx.VERTICAL)

        # ── 副本统计面板（四象/噬魂） ──
        _C_WIN      = wx.Colour(34, 184, 100)
        _C_FAIL     = wx.Colour(235, 64, 52)
        _C_DONE     = wx.Colour(130, 135, 145)
        _C_CARD_BG  = wx.Colour(248, 250, 252)
        _C_SEP      = wx.Colour(226, 230, 236)

        self.stats_panel = wx.Panel(log_card)
        self.stats_panel.SetBackgroundColour(wx.Colour(236, 240, 245))
        stats_sizer = wx.BoxSizer(wx.HORIZONTAL)

        def _make_card(label):
            card = wx.Panel(self.stats_panel)
            card.SetBackgroundColour(_C_CARD_BG)
            vs = wx.BoxSizer(wx.VERTICAL)

            # 标题行 — 左标题 + 右进度
            title_row = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(card, label=label)
            title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            title.SetForegroundColour(wx.Colour(40, 45, 55))
            title_row.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
            title_row.AddStretchSpacer()
            done_num = wx.StaticText(card, label="0/0")
            done_num.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            done_num.SetForegroundColour(_C_DONE)
            title_row.Add(done_num, 0, wx.ALIGN_CENTER_VERTICAL)
            vs.Add(title_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
            vs.AddSpacer(1)

            # 分隔线
            sep = wx.Panel(card, size=(-1, 1))
            sep.SetBackgroundColour(_C_SEP)
            vs.Add(sep, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
            vs.AddSpacer(1)

            # 数据行 — 胜 | 败 (1:1)
            row = wx.BoxSizer(wx.HORIZONTAL)

            left_box = wx.BoxSizer(wx.HORIZONTAL)
            left_box.AddStretchSpacer()
            wl = wx.StaticText(card, label="胜")
            wl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            wl.SetForegroundColour(_C_WIN)
            left_box.Add(wl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
            w_num = wx.StaticText(card, label="0")
            w_num.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            w_num.SetForegroundColour(_C_WIN)
            left_box.Add(w_num, 0, wx.ALIGN_CENTER_VERTICAL)
            left_box.AddStretchSpacer()
            row.Add(left_box, 1, wx.ALIGN_CENTER_VERTICAL)

            vsep = wx.Panel(card, size=(1, 16))
            vsep.SetBackgroundColour(_C_SEP)
            row.Add(vsep, 0, wx.ALIGN_CENTER_VERTICAL)

            right_box = wx.BoxSizer(wx.HORIZONTAL)
            right_box.AddStretchSpacer()
            fl = wx.StaticText(card, label="败")
            fl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            fl.SetForegroundColour(_C_FAIL)
            right_box.Add(fl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
            f_num = wx.StaticText(card, label="0")
            f_num.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            f_num.SetForegroundColour(_C_FAIL)
            right_box.Add(f_num, 0, wx.ALIGN_CENTER_VERTICAL)
            right_box.AddStretchSpacer()
            row.Add(right_box, 1, wx.ALIGN_CENTER_VERTICAL)

            vs.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)
            card.SetSizer(vs)
            return card, w_num, f_num, done_num

        sx_card, self.stats_sx_win, self.stats_sx_fail, self.stats_sx_done = _make_card("四象")
        self._sx_card = sx_card
        stats_sizer.Add(sx_card, 1, wx.EXPAND | wx.RIGHT, 6)
        sh_card, self.stats_sh_win, self.stats_sh_fail, self.stats_sh_done = _make_card("噬魂")
        self._sh_card = sh_card
        stats_sizer.Add(sh_card, 1, wx.EXPAND)

        self.stats_panel.SetSizer(stats_sizer)
        self.stats_panel.Hide()
        lcs.Add(self.stats_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        log_header = wx.BoxSizer(wx.HORIZONTAL)
        log_lbl = wx.StaticText(log_card, label="● 运行日志")
        log_lbl.SetForegroundColour(wx.Colour(50, 80, 140))
        log_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        log_header.Add(log_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        log_header.AddStretchSpacer()
        log_ts = wx.StaticText(log_card, label=datetime.now().strftime("%H:%M:%S"))
        log_ts.SetForegroundColour(wx.Colour(140, 145, 155))
        log_ts.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        log_header.Add(log_ts, 0, wx.ALIGN_CENTER_VERTICAL)
        self.log_ts = log_ts

        lcs.Add(log_header, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 4)

        self.text_ctrl = wx.TextCtrl(log_card, size=(-1, 200), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)
        self.text_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl.SetForegroundColour(wx.Colour(40, 42, 50))
        self.text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        lcs.Add(self.text_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        log_card.SetSizer(lcs)

        content_row.Add(log_card, 1, wx.EXPAND)
        content_row.Add(button_col, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        main_sizer.Add(content_row, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        main_sizer.AddSpacer(8)

        # ── 底部 ──
        btm = wx.BoxSizer(wx.HORIZONTAL)
        link_color = wx.Colour(50, 80, 140)

        self.contact = wx.StaticText(self.panel, label="群 955753707")
        self.contact.SetForegroundColour(wx.Colour(100, 105, 115))
        self.contact.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))

        self.update_notify_panel = wx.Panel(self.panel, size=(14, 14))
        self.update_notify_panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.update_notify_panel.Hide()
        self.update_notify_panel.Bind(wx.EVT_PAINT, self.on_update_notify_paint)
        self.update_notify_panel.SetToolTip("有新版本可用")

        self.updateVersion = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        update_bmp = wx.Bitmap(wx.Image(self.get_resource_path("serveAssets/images/check_update.png")).Scale(18, 18, wx.IMAGE_QUALITY_HIGH))
        self.updateVersion.SetBitmap(update_bmp)
        self.updateVersion.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.updateVersion.SetToolTip("检查更新")
        self.updateVersion.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.updateVersion.Bind(wx.EVT_BUTTON, self.on_update_link_click)

        btm.Add(self.contact, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        btm.AddStretchSpacer()

        self.help_link = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        self.help_link.SetBitmap(self._load_icon("btn_help.png", 18))
        self.help_link.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.help_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.help_link.SetToolTip("帮助说明")
        self.help_link.Bind(wx.EVT_BUTTON, self.on_help_link_click)
        btm.Add(self.help_link, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        btm.Add(self.update_notify_panel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        btm.Add(self.updateVersion, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        main_sizer.Add(btm, 0, wx.EXPAND | wx.BOTTOM, 10)
        self.panel.SetSizer(main_sizer)

        self.thread = None
        sys.stdout = self
        self.bind_hotkeys()
        # self.contact = wx.StaticText(self.panel, label="v25.6.0", pos=(190, 236), style=wx.ST_NO_AUTORESIZE)
        # font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        # self.contact.SetFont(font)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._closing_soft = False
        self.game_name = ""
        self.teammate1_name = ""
        self.teammate2_name = ""
        self.selections = ""
        self.mojingFloor = ""
        self.zhengdianFloor = ""
        self.afterZreo = ""
        self.richangSelection = []
        self.mac_address = self.get_mac_address()
        self.mac_address1 = ":".join(
            ["{:02x}".format((uuid.getnode() >> elements) & 0xFF) for elements in range(0, 8 * 6, 8)][::-1]
        )
        self.has_script = "free"
        self.user_name = "免费用户"
        self.end_time = "2199-12-30 23:59:59"
        self.remote_info = self.check_gitee_update()
        self.current_version = self.get_current_version()
        self.update_notify_timer = None
        self.update_notify_visible = True
        if self.remote_info:
            self.userData = self.remote_info.get("userData", {})
        else:
            self.userData = {}
        self.check_and_update_notify_status()
        is_pass = self.is_user_valid()
        if not is_pass:
            self.user_name = "免费用户"
            self.end_time = "2199-12-30 23:59:59"
            self.has_script = "free"
        print(f"用户名：{self.user_name}\n有效期：{self.end_time}\n脚本权限：{self.has_script}")
        if self.is_virtual_machine() and self.user_name not in [
            "关服就离开",
            "RInoicc",
            "钞能力",
        ]:
            print("虚拟机")
            return
        self._init_done = True

        self.has_choices = (
            [
                "官渡",
                "魔镜",
                "日常",
                "黑风",
                "矿产",
                "龙岛",
                "龙珠",
                "四象",
                "青渊",
                "清妖",
                "龙王令",
                "引魔符",
                # "藏宝图",
                "49日常",
                "49战魂",
                "49整点",
                "帮派任务",
                "名将闯关",
                "怪物攻城",
                "挂机+整点",
                "西瓜保卫战",
                "战魂楼(精英)",
                "战魂楼(镇魂)",
                "战魂楼(噬魂)",
                "天外天传送符",
                "嗜血战场(精英)",
                "英魂秘境(精英)",
                # "整点",
                # "测试",
            ],
        )
        self.free_choices = (
            [
                "官渡",
                "魔镜",
                "日常",
                "黑风",
                "矿产",
                "龙岛",
                "龙珠",
                "四象",
                "青渊",
                "龙王令",
                "引魔符",
                # "藏宝图",
                "49日常",
                "49战魂",
                "49整点",
                "帮派任务",
                "名将闯关",
                "怪物攻城",
                "挂机+整点",
                "西瓜保卫战",
                "战魂楼(精英)",
                "战魂楼(镇魂)",
                "战魂楼(噬魂)",
                "天外天传送符",
                "嗜血战场(精英)",
                "英魂秘境(精英)",
                # "测试",
            ],
        )
        has_choices = self.free_choices[0] if self.has_script == "free" else self.has_choices[0]
        # try:
        #     from ScriptFactory import get_user_script_choices
        #     user_scripts = get_user_script_choices()
        #     has_choices = list(has_choices) + user_scripts
        # except:
        #     pass
        self.dropdown = wx.ComboBox(self.panel, size=(-1, 34),
                                    choices=has_choices)
        self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
        self.dropdown.SetHint("选择执行脚本")
        row_top.Insert(1, self.dropdown, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.dropdown.SetBackgroundColour(wx.Colour(240, 242, 246))
        self.dropdown.SetForegroundColour(wx.Colour(40, 42, 50))
        self.dropdown.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.panel.Layout()
        self.Layout()

        # 时钟实时更新
        self._clock_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._update_clock, self._clock_timer)
        self._clock_timer.Start(1000)

    def _load_icon(self, name, size):
        path = self.get_resource_path("serveAssets/images/" + name)
        img = wx.Image(path).Scale(size, size, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

    def check_gitee_update(self):
        try:
            url = "https://gitee.com/syf0910/mhsg-script-update/raw/master/version.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[错误] 检查更新失败: {e}")
            return None

    def get_mac_address(self):
        # 使用 psutil 获取所有网络接口信息
        interfaces = psutil.net_if_addrs()

        # 遍历接口信息，找到MAC地址
        for interface_name, interface_addresses in interfaces.items():
            for address in interface_addresses:
                if str(address.family) == "AddressFamily.AF_LINK":
                    return address.address

        return "MAC address not found"

    def is_virtual_machine(self):
        """
        检测当前系统是否为虚拟机
        兼容 Windows 10 和 Windows 11
        """
        try:
            # 方法1：使用 PowerShell Get-CimInstance（Windows 10/11 兼容）
            try:
                # 创建启动信息，隐藏窗口（Windows 专用）
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creation_flags = subprocess.CREATE_NO_WINDOW
                else:
                    startupinfo = None
                    creation_flags = 0

                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                ]
                output = subprocess.check_output(
                    cmd,
                    shell=False,
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    startupinfo=startupinfo,
                    creationflags=creation_flags,
                )
            except (
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    subprocess.SubprocessError,
            ):
                # 方法2：回退到 Get-WmiObject（更兼容，但较慢）
                try:
                    # 创建启动信息，隐藏窗口（Windows 专用）
                    if sys.platform == "win32":
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        creation_flags = subprocess.CREATE_NO_WINDOW
                    else:
                        startupinfo = None
                        creation_flags = 0

                    cmd = [
                        "powershell",
                        "-NoProfile",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        "Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                    ]
                    output = subprocess.check_output(
                        cmd,
                        shell=False,
                        text=True,
                        stderr=subprocess.DEVNULL,
                        timeout=5,
                        startupinfo=startupinfo,
                        creationflags=creation_flags,
                    )
                except (
                        subprocess.TimeoutExpired,
                        FileNotFoundError,
                        subprocess.SubprocessError,
                ):
                    # 方法3：使用 platform 模块（最简单，但信息较少）
                    import platform

                    output = f"{platform.system()} {platform.machine()}"

            vm_keywords = [
                "VMware",
                "VirtualBox",
                "KVM",
                "QEMU",
                "Xen",
                "Bochs",
                "Hyper-V",
                "Microsoft Corporation",
            ]  # Hyper-V 的制造商
            output_upper = output.upper()
            return any(
                keyword.upper() in output_upper for keyword in vm_keywords)
        except Exception as e:
            # 如果所有方法都失败，返回 False（非虚拟机）
            return False

    def is_user_valid(self):
        current_time = datetime.now()
        for user in self.userData:
            if self.mac_address in user["user_mac"] or self.mac_address1 in \
                    user["user_mac"]:
                # if user['has_script'] != 'all' and not self.scriptName in user['has_script']:
                # 	return False
                # if user['has_script'] != 'all' and self.frame.zhengdianFloor and not '整点' in user['has_script']:
                # 	return False
                expiration_time = datetime.strptime(user["end_time"],
                                                    "%Y-%m-%d %H:%M:%S")
                if current_time > expiration_time:
                    return False
                else:
                    self.user_name = user["user_name"]
                    self.end_time = user["end_time"]
                    self.has_script = user["has_script"]
                    return True
        return False

    def on_help_link_click(self, event):
        # 定义弹窗的内容和图片路径
        content = [
            "使用说明：(每一条都很必要)",
            "1.第一次脚本需要使用管理员模式开启；",
            "2.脚本启动之前填入游戏名称(360大厅主页左侧边栏设置的游戏名称)；",
            "3.脚本关闭之前先点重置，如果卡住了一直点右上角x号即可关闭；",
            "4.请将游戏画面缩放到900*580（使用键盘Ctrl+鼠标滚轮调整）,",
            "5.脚本如果出现被杀毒软件清掉，可以新建一个文件夹，将脚本放到文件夹中，给文件夹添加信任即可。",
            "脚本说明：",
            "1.日常根据填入的次数来打，对应的副本，也是根据日常中填入的次数打；",
            "2.0点后执行的脚本选了之后，晚上0点整点打完之后会去执行对应脚本，选择名将闯关下午3点，晚上9点整点之后会去打名将闯关；",
            "3.队友名称在多开并且多开的号已经拆分了的情况下再填，填的是360游戏大厅设置的小号名称，绑定成功的小号会在队友对话框发送1；",
            "4.黑风/矿产次数填多少次打多少次，打完自动去官渡；",
            "6.挂机+整点，使用之前打开查看副本，点一下需要打的副本，然后启动脚本即可；",
            "7.保存数据之后会在脚本同级文件夹生成一个setting.json，下次使用脚本会自动读入数据；",
            "8.整点全打为飞过去打页面上能找到的怪物，走路打九黎族祭坛，魔魂山，魔谷西三个地图的怪物；",
            "9.自动战斗选择了对应的副本/整点，到打的时候会自动开启，刘备数量为账号内拥有的刘备数量总和，包括出战的，自动战斗多开，脚本队友1要在游戏队伍中第二位，脚本队友2在游戏队伍中第三位，吃药功能为吃恢复药；",
            "10.窗口绑定的独立方法如：原平台两个号，新平台一个号，那么新平台的小号勾选独立并且填入360游戏大厅对应的游戏名称。",
            "常见问题：",
            "1.点开始脚本没任何反应：使用管理员打开脚本；",
            "2.点开始之后提示无效窗口：务必保证输入的没问题，360最新版的只能绑定第一个打开的窗口；",
            "3.脚本关了一直提示未找到句柄窗口：点击重置即可；",
            "4.卡在副本进门位置不动：务必多开变身卡；",
            "5.脚本关了卡死直接按F9/F10。",
        ]
        images = [
            self.get_resource_path("serveAssets/images/shuoming1.bmp"),
            self.get_resource_path("serveAssets/images/shuoming2.bmp"),
            self.get_resource_path("serveAssets/images/shuoming4.bmp"),
        ]

        # 打开弹窗
        dialog = HelpDialog(self, "说明", content, images)
        dialog.ShowModal()
        dialog.Destroy()

    def get_current_version(self):
        """从UpdateDialog类获取当前版本号"""
        return UpdateDialog.get_current_version()

    def check_and_update_notify_status(self):
        """检查版本状态并更新提示图标"""
        # 停止闪烁（如果正在运行）
        self.stop_update_notify_blink()

        def _safe_hide(panel):
            try:
                if panel is not None:
                    panel.Hide()
            except Exception:
                pass

        def _safe_show(panel):
            try:
                if panel is not None:
                    panel.Show()
            except Exception:
                pass

        if not self.remote_info or "version" not in self.remote_info:
            # 无法获取版本信息，隐藏提示图标
            if hasattr(self, "update_notify_panel"):
                _safe_hide(self.update_notify_panel)
            return

        latest_version = self.remote_info["version"]

        # 比较版本号：只有远端 > 本地才提示更新
        def _parse(v):
            try:
                parts = v.split(".")
                return tuple(int(p) for p in parts)
            except Exception:
                return (0,)

        if _parse(latest_version) > _parse(self.current_version):
            # 有新版本，显示提示图标（静态显示，不闪烁）
            if hasattr(self, "update_notify_panel"):
                _safe_show(self.update_notify_panel)
        else:
            # 已是最新版本，隐藏提示图标
            if hasattr(self, "update_notify_panel"):
                _safe_hide(self.update_notify_panel)

    # def on_factory_click(self, event):
    #     from ScriptFactory import ScriptFactoryDialog
    #     dlg = ScriptFactoryDialog(self)
    #     dlg.Show()

    def on_update_link_click(self, event):
        # 停止闪烁
        self.stop_update_notify_blink()
        dialog = UpdateDialog(self, self.remote_info)
        dialog.ShowModal()
        dialog.Destroy()
        # 重新检查版本状态
        self.check_and_update_notify_status()

    def start_update_notify_blink(self):
        """启动更新提示图标闪烁"""
        if self.update_notify_timer is None:
            self.update_notify_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_update_notify_blink,
                      self.update_notify_timer)
        self.update_notify_timer.Start(500)  # 每500毫秒闪烁一次

    def stop_update_notify_blink(self):
        """停止更新提示图标闪烁"""
        if self.update_notify_timer and self.update_notify_timer.IsRunning():
            self.update_notify_timer.Stop()

    def on_update_notify_paint(self, event):
        """绘制更新提示图标（绿色小圆点）"""
        dc = wx.PaintDC(self.update_notify_panel)
        size = self.update_notify_panel.GetSize()

        # 使用GraphicsContext绘制更平滑的圆形
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            # 绘制绿色圆形（直径为12）
            radius = 6.0
            center_x = size.width / 2.0
            center_y = size.height / 2.0

            # 设置绿色画刷
            brush = gc.CreateBrush(wx.Brush(wx.Colour(103, 194, 58)))
            gc.SetBrush(brush)

            # 绘制圆形
            gc.DrawEllipse(center_x - radius, center_y - radius, radius * 2,
                           radius * 2)
        else:
            # 如果GraphicsContext不可用，使用传统方法
            radius = 6
            center_x = size.width // 2
            center_y = size.height // 2
            dc.SetBrush(wx.Brush(wx.Colour(103, 194, 58)))
            dc.SetPen(wx.Pen(wx.Colour(103, 194, 58), 1))
            dc.DrawCircle(center_x, center_y, radius)

    def get_resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

    def on_button_click(self, event):
        dialog = MyDialog(self, self.has_script)
        if self.game_name:
            dialog.team_leader_text.SetValue(self.game_name)
            dialog.heifeng_count.SetValue(self.heifengCount)
            dialog.choiceCeng.SetValue(self.zhanhunFloor)
            dialog.choiceZhanHunCeng.SetValue(self.zhanhunFloorNew)
            dialog.choiceMojing.SetValue(self.mojingFloor)
            dialog.choiceZhengdian.SetValue(self.zhengdianFloor)
            dialog.choiceHeifeng.SetValue(self.heifengFloor)
            dialog.choiceAfterZreo.SetValue(self.afterZreo)
            dialog.teammate1_text.SetValue(self.teammate1_name)
            dialog.teammate2_text.SetValue(self.teammate2_name)
            dialog.choice_line.SetValue(self.choice_line)
            dialog.teammate1_pos.SetValue(self.teammate1_pos)
            dialog.teammate2_pos.SetValue(self.teammate2_pos)
            dialog.team_leader_pos.SetValue(self.team_leader_pos)
            dialog.lianyu_count.SetValue(self.lianyu_count)
            dialog.qingyuan_count.SetValue(self.qingyuan_count)
            dialog.zhanhun_count.SetValue(self.zhanhun_count)
            dialog.shihun_count.SetValue(self.shihun_count)
            dialog.choiceShiHunCeng.SetValue(self.shihun_floor)
            if hasattr(self, 'zhanhun_start_floor') and self.zhanhun_start_floor:
                dialog.zhanhun_start_floor.SetValue(self.zhanhun_start_floor)
            dialog.sixiang_count.SetValue(self.sixiang_count)
            dialog.sixiang_difficulty.SetValue(self.sixiang_difficulty)
            dialog.rongdong_count.SetValue(self.rongdong_count)
            dialog.liandan_count.SetValue(self.liandan_count)
            dialog.wuxing_count.SetValue(self.wuxing_count)
            dialog.yinhun_count.SetValue(self.yinhun_count)
            dialog.sangumaolu_count.SetValue(self.sangumaolu_count)
            dialog.hong_count.SetValue(self.hong_count)
            dialog.yunyou_count.SetValue(self.yunyou_count)
            dialog.bamen_count.SetValue(self.bamen_count)
            dialog.laoshu_count.SetValue(self.laoshu_count)
            dialog.guandujy_count.SetValue(self.guandujy_count)
            dialog.cb_bangpai.SetValue(self.bangpai_enabled)
            dialog.mingjiang_count.SetValue(self.mingjiang_count)
            if hasattr(self, 'richang_zhengdian'):
                dialog.cb_zhengdian.SetValue(self.richang_zhengdian)
            if hasattr(self, 'richang_mojing'):
                dialog.cb_mojing.SetValue(self.richang_mojing)
            if hasattr(self, "liubeiCounts") and hasattr(dialog, "liubeiCountInputs"):
                for idx, val in self.liubeiCounts.items():
                    if idx in dialog.liubeiCountInputs:
                        dialog.liubeiCountInputs[idx].SetValue(str(val))
            if hasattr(self, "independent_win1") and hasattr(dialog, "independent_win1_on"):
                if self.independent_win1:
                    dialog.independent_win1_off.Hide()
                    dialog.independent_win1_on.Show()
                else:
                    dialog.independent_win1_on.Hide()
                    dialog.independent_win1_off.Show()
            if hasattr(self, "independent_win2") and hasattr(dialog, "independent_win2_on"):
                if self.independent_win2:
                    dialog.independent_win2_off.Hide()
                    dialog.independent_win2_on.Show()
                else:
                    dialog.independent_win2_on.Hide()
                    dialog.independent_win2_off.Show()
            if hasattr(self, 'combat_auto_scenes') and hasattr(dialog, 'combat_auto_checkboxes'):
                for scene, cb in dialog.combat_auto_checkboxes.items():
                    cb.SetValue(scene in self.combat_auto_scenes)
            if hasattr(self, 'use_heal_item') and hasattr(dialog, 'use_heal_cb'):
                dialog.use_heal_cb.SetValue(self.use_heal_item)
        if dialog.ShowModal() == wx.ID_OK:
            print("当前游戏名称：" + self.game_name)
        dialog.Destroy()

    def _update_clock(self, event):
        if hasattr(self, 'log_ts') and self.log_ts:
            self.log_ts.SetLabel(datetime.now().strftime("%H:%M:%S"))

    def _refresh_dungeon_stats(self):
        """从当前脚本线程同步副本统计数据到UI（主线程中调用）"""
        try:
            if not hasattr(self, 'stats_panel') or not self.stats_panel:
                return
            show_sx = show_sh = False
            t = self.thread

            if t is not None:
                sx = getattr(t, 'sixiang_stats', None)
                if sx and sx.get('total', 0) > 0:
                    self.stats_sx_win.SetLabel(str(sx['win']))
                    self.stats_sx_fail.SetLabel(str(sx['fail']))
                    self.stats_sx_done.SetLabel("{}/{}".format(sx['done'], sx.get('total', 0)))
                    show_sx = True
            if hasattr(self, '_sx_card') and self._sx_card:
                self._sx_card.Show(show_sx)

            if t is not None:
                sh = getattr(t, 'shihun_stats', None)
                if sh and sh.get('total', 0) > 0:
                    self.stats_sh_win.SetLabel(str(sh['win']))
                    self.stats_sh_fail.SetLabel(str(sh['fail']))
                    self.stats_sh_done.SetLabel("{}/{}".format(sh['done'], sh.get('total', 0)))
                    show_sh = True
            if hasattr(self, '_sh_card') and self._sh_card:
                self._sh_card.Show(show_sh)

            if show_sx or show_sh:
                self.stats_panel.Show()
            else:
                self.stats_panel.Hide()
            self.stats_panel.GetParent().Layout()
        except Exception:
            pass

    def write(self, text):
        # 使用 wx.CallAfter 确保 GUI 操作在主线程中执行（线程安全）
        if wx.GetApp() and wx.GetApp().IsMainLoopRunning():
            wx.CallAfter(self._write_text, text)
        else:
            # 如果 wx 应用未初始化或不在主线程，尝试直接调用（可能失败，但不会崩溃）
            try:
                self._write_text(text)
            except Exception:
                pass  # 忽略错误，避免崩溃

    def _write_text(self, text):
        """实际的文本写入方法（在主线程中调用）"""
        try:
            if hasattr(self, "text_ctrl") and self.text_ctrl:
                self.text_ctrl.WriteText(text)
        except Exception:
            pass  # 忽略错误，避免崩溃

    # self.print_and_speak(text)

    def bind_hotkeys(self):
        """绑定全局快捷键"""
        keyboard.add_hotkey("F1", lambda: wx.CallAfter(self.start_script))
        keyboard.add_hotkey("F2", lambda: wx.CallAfter(self.pause_script))
        keyboard.add_hotkey("F3", lambda: wx.CallAfter(self.resume_script))
        keyboard.add_hotkey("F4", lambda: wx.CallAfter(self.stop_script))
        keyboard.add_hotkey("f10", lambda: self.force_quit())  # 强制关闭脚本（用于抢鼠标时）
        keyboard.add_hotkey("F9", lambda: self.force_quit())  # 强制关闭脚本（用于抢鼠标时）

    def start_script(self):
        # 如果线程已存在且正在运行，先停止它
        if self.thread is not None and self.thread.is_alive():
            print("检测到已有线程在运行，先停止...")
            self.stop_script()
            # 等待一下确保线程完全停止
            time.sleep(0.5)

        # 检查脚本名称
        if not self.scriptName:
            self.show_error_message("请先选择脚本！")
            return

        if not self.game_name:
            self.show_error_message("请输入游戏名称！")
            return

        # 创建新线程（每次都是全新的）
        scriptName = self.scriptName
        self.thread = MyThread(scriptName, self.userData)
        self.thread.daemon = True
        self.thread.frame = self
        self.thread.overed = False
        self.thread.stoped = False

        print("开始脚本！")
        self.button_start.Disable()
        self.thread.start()

    def pause_script(self):
        if not self.scriptName:
            print("请先选择脚本！")
            return
        print("暂停脚本！")
        if self.thread is not None:
            # paused.set()
            self.thread.stoped = True

    def resume_script(self):
        if not self.scriptName:
            print("请先选择脚本！")
            return
        print("继续执行脚本！")
        if self.thread is not None:
            # paused.clear()
            self.thread.stoped = False
            with condition:
                condition.notify_all()

    def stop_script(self):
        """重置脚本，停止所有线程并初始化所有状态"""
        global condition  # 在使用之前声明 global

        # 防止重复点击重置按钮
        if not hasattr(self, "_resetting"):
            self._resetting = False

        if self._resetting:
            print("重置操作正在进行中，请勿重复点击...")
            return

        self._resetting = True
        print("开始重置脚本...")

        try:
            # 停止战斗自动操作
            if self.thread is not None and hasattr(self.thread,
                                                   "_stop_combat_auto"):
                try:
                    self.thread._stop_combat_auto()
                except:
                    pass

            # 等待所有线程结束（即使 scriptName 为空也要执行）
            if self.thread is not None:
                # 先设置停止标志，让线程进入等待状态
                self.thread.stoped = True
                # 然后设置结束标志，让线程知道要结束
                self.thread.overed = True
                if hasattr(self.thread, "scriptName"):
                    self.thread.scriptName = ""  # 重置线程的脚本名称

                # 通知所有等待的线程，让它们从 condition.wait() 中醒来
                with condition:
                    condition.notify_all()

                # 停止所有子线程（使用更短的超时，避免长时间阻塞）
                if hasattr(self.thread,
                           "child_thread") and self.thread.child_thread is not None:
                    if self.thread.child_thread.is_alive():
                        self.thread.child_thread.join(timeout=0.5)

                if hasattr(self.thread,
                           "win1_thread") and self.thread.win1_thread is not None:
                    if self.thread.win1_thread.is_alive():
                        self.thread.win1_thread.join(timeout=0.5)

                if hasattr(self.thread,
                           "win2_thread") and self.thread.win2_thread is not None:
                    if self.thread.win2_thread.is_alive():
                        self.thread.win2_thread.join(timeout=0.5)

                if hasattr(self.thread,
                           "combat_auto_thread") and self.thread.combat_auto_thread is not None:
                    if self.thread.combat_auto_thread.is_alive():
                        self.thread.combat_auto_thread.join(timeout=0.5)

                # 使用超时等待主线程，避免无限阻塞界面
                if self.thread.is_alive():
                    print("等待主线程结束...")
                    self.thread.join(timeout=1.5)
                    if self.thread.is_alive():
                        print("警告：主线程未在1.5秒内结束，强制继续")

                # 安全地解绑窗口，避免访问已销毁的对象
                if hasattr(self.thread, "dm") and self.thread.dm:
                    try:
                        self.thread.dm.UnBindWindow()
                    except:
                        pass
                if hasattr(self.thread, "win1_dm") and self.thread.win1_dm:
                    try:
                        self.thread.win1_dm.UnBindWindow()
                    except:
                        pass
                if hasattr(self.thread, "win2_dm") and self.thread.win2_dm:
                    try:
                        self.thread.win2_dm.UnBindWindow()
                    except:
                        pass

            # 重新创建 condition，确保下次启动时是全新的
            condition = threading.Condition()

            # 初始化所有状态变量
            self.thread = None
            self.scriptName = ""  # 重置脚本名称
            self.text_ctrl.SetValue("")
            if self.dropdown:
                self.dropdown.SetSelection(-1)

            # 隐藏副本统计面板
            if hasattr(self, 'stats_panel') and self.stats_panel:
                self.stats_panel.Hide()
                self.stats_panel.GetParent().Layout()

            # 重置所有相关变量

            print("任务已全部结束！")
            self.button_start.Enable()
        except Exception as e:
            print(f"重置脚本时发生错误: {e}")
        finally:
            # 重置标志，允许下次点击
            self._resetting = False

    def force_quit(self):
        """强制关闭脚本（用于抢鼠标时）"""
        print("强制关闭脚本（F9快捷键）...")
        try:
            # 强制停止所有线程
            if self.thread is not None:
                self.thread.stoped = True
                self.thread.overed = True
                # 尝试解绑窗口
                try:
                    if hasattr(self.thread, "dm") and self.thread.dm:
                        self.thread.dm.UnBindWindow()
                except:
                    pass
                try:
                    if hasattr(self.thread, "win1_dm") and self.thread.win1_dm:
                        self.thread.win1_dm.UnBindWindow()
                except:
                    pass
                try:
                    if hasattr(self.thread, "win2_dm") and self.thread.win2_dm:
                        self.thread.win2_dm.UnBindWindow()
                except:
                    pass

            # 清理键盘快捷键
            try:
                keyboard.unhook_all()
            except:
                pass

            # 强制退出
            os._exit(0)
        except Exception as e:
            print(f"强制关闭时发生错误: {e}")
            os._exit(0)

    def on_close(self, event):
        """处理窗口关闭事件"""
        print("正在关闭窗口...")
        try:
            if self.thread is not None:
                self.thread.stoped = True
                self.thread.overed = True

                with condition:
                    condition.notify_all()

                try:
                    if hasattr(self.thread, "dm") and self.thread.dm:
                        self.thread.dm.UnBindWindow()
                except:
                    pass
                try:
                    if hasattr(self.thread, "win1_dm") and self.thread.win1_dm:
                        self.thread.win1_dm.UnBindWindow()
                except:
                    pass
                try:
                    if hasattr(self.thread, "win2_dm") and self.thread.win2_dm:
                        self.thread.win2_dm.UnBindWindow()
                except:
                    pass

            try:
                keyboard.unhook_all()
            except:
                pass
        except Exception as e:
            print(f"关闭窗口时发生错误: {e}")
        finally:
            try:
                self.Destroy()
            except:
                pass
            if not self._closing_soft:
                try:
                    wx.GetApp().ExitMainLoop()
                except:
                    pass
                os._exit(0)

    def on_select_script(self, event):
        self.scriptName = self.dropdown.GetValue()
        self.Layout()

    def button_start_click(self, event):
        self.start_script()

    def button_pause_click(self, event):
        self.pause_script()

    def button_resume_click(self, event):
        self.resume_script()

    def button_stop_click(self, event):
        # 禁用按钮，防止重复点击
        self.button_stop.Disable()
        if self.thread is not None:
            # paused.set()
            self.thread.stoped = True
        try:
            self.stop_script()
        finally:
            # 重新启用按钮
            wx.CallAfter(self.button_stop.Enable)

    def show_error_message(self, message):
        app = wx.App()
        dlg = wx.MessageDialog(None, message, "Error",
                               style=wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        app.MainLoop()


class App(wx.App):
    BASE_URL = "https://yian.syf88.top"

    def __init__(self):
        super().__init__()
        self.user_info = {"username": "", "has_script": "free", "end_time": "2199-12-30 23:59:59", "token": ""}

class MyDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(70, 75, 85)
    C_INPUT_BG = wx.Colour(255, 255, 255)

    def __init__(self, parent, has_script):
        super().__init__(parent, title="游戏设置", size=(570, 610), pos=(200, 20))
        self.SetBackgroundColour(self.C_BG)
        self.frame = parent
        self.config_file = "settings_config.json"
        self.schemes = OrderedDict()
        self.current_scheme = ""
        self.load_config()
        self.max_schemes = 10

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(8)

        def label(text, sz=36):
            l = wx.StaticText(panel, label=text)
            l.SetForegroundColour(self.C_MUTED)
            l.SetMinSize((sz, -1))
            return l

        def combo(choices, hint, sz=(-1, 28)):
            c = wx.ComboBox(panel, size=sz, choices=choices)
            c.SetBackgroundColour(self.C_INPUT_BG)
            c.SetForegroundColour(self.C_TEXT)
            c.SetHint(hint)
            return c

        def text_input(hint, sz=(-1, 28), v=None):
            if v:
                t = wx.TextCtrl(panel, size=sz, validator=v)
            else:
                t = wx.TextCtrl(panel, size=sz)
            t.SetBackgroundColour(self.C_INPUT_BG)
            t.SetForegroundColour(self.C_TEXT)
            t.SetHint(hint)
            return t

        # ── 标题 + 方案 ──
        top_row = wx.BoxSizer(wx.HORIZONTAL)
        l = label("方案", 36)
        l.SetForegroundColour(self.C_GOLD)
        top_row.Add(l, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.scheme_choice = wx.ComboBox(panel, size=(140, 30), choices=list(self.schemes.keys()))
        self.scheme_choice.SetHint("方案名称")
        self.scheme_choice.SetBackgroundColour(self.C_INPUT_BG)
        self.scheme_choice.SetForegroundColour(self.C_TEXT)
        if self.current_scheme and self.current_scheme in self.schemes:
            self.scheme_choice.SetValue(self.current_scheme)
        self.scheme_choice.Bind(wx.EVT_COMBOBOX, self.on_scheme_select)
        top_row.Add(self.scheme_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        for name, fn, tip in [("btn_save.png", self.on_save_scheme, "保存方案"), ("btn_add.png", self.on_add, "添加方案"), ("btn_delete.png", self.on_delete, "删除方案")]:
            b = wx.Button(panel, size=(28, 28), style=wx.BORDER_NONE)
            b.SetBitmap(self._dialog_icon(name, 14))
            b.SetBackgroundColour(self.C_SURFACE)
            b.SetToolTip(tip)
            b.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            b.Bind(wx.EVT_BUTTON, fn)
            top_row.Add(b, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        main_sizer.Add(top_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        # ── 队伍 ──
        sec = lambda t: self._section_header(main_sizer, panel, t)
        sec("队伍")
        tm = wx.FlexGridSizer(cols=4, vgap=5, hgap=6)
        tm.AddGrowableCol(1, 1)

        def _make_toggle_btn(parent, label_off, label_on, bind_fn):
            container = wx.Panel(parent, size=(74, 30))
            container.SetBackgroundColour(self.C_BG)
            btn_off = wx.Button(container, label=label_off, size=(72, 28), style=wx.BORDER_NONE, pos=(1, 1))
            btn_off.SetBackgroundColour(wx.Colour(190, 195, 205))
            btn_off.SetForegroundColour(wx.Colour(60, 60, 60))
            btn_off.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            btn_off.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            btn_on = wx.Button(container, label=label_on, size=(72, 28), style=wx.BORDER_NONE, pos=(1, 1))
            btn_on.SetBackgroundColour(wx.Colour(34, 153, 84))
            btn_on.SetForegroundColour(wx.Colour(255, 255, 255))
            btn_on.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            btn_on.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            btn_on.Hide()
            btn_off.Bind(wx.EVT_BUTTON, lambda e, c=container, o=btn_off, n=btn_on: bind_fn(e, True, c, o, n))
            btn_on.Bind(wx.EVT_BUTTON, lambda e, c=container, o=btn_off, n=btn_on: bind_fn(e, False, c, o, n))
            return container, btn_off, btn_on

        for txt, attr_hint, is_leader in [("队长", "游戏名称", True), ("队友1", "队友1", False), ("队友2", "队友2", False)]:
            tm.Add(label(txt, 40), 0, wx.ALIGN_CENTER_VERTICAL)
            tc = text_input(attr_hint)
            if is_leader:
                self.team_leader_text = tc
                self.team_leader_text.Bind(wx.EVT_TEXT, self.on_text_change)
            elif "1" in txt:
                self.teammate1_text = tc
            else:
                self.teammate2_text = tc
            tm.Add(tc, 1, wx.EXPAND)
            b = wx.Button(panel, label="📍", size=(28, 28), style=wx.BORDER_NONE)
            b.SetBackgroundColour(self.C_SURFACE)
            b.SetForegroundColour(self.C_MUTED)
            b.Hide()
            tm.Add(b, 0, wx.ALIGN_CENTER_VERTICAL)
            if is_leader:
                tm.Add(wx.Panel(panel, size=(58, 1)), 0, wx.ALIGN_CENTER_VERTICAL)
            elif "1" in txt:
                def _toggle1(event, flag, container, off_btn, on_btn):
                    if flag:
                        off_btn.Hide(); on_btn.Show(); container.Layout()
                    else:
                        on_btn.Hide(); off_btn.Show(); container.Layout()
                container, off_btn, on_btn = _make_toggle_btn(panel, "独立✅", "独立✅", _toggle1)
                self.independent_win1_off = off_btn
                self.independent_win1_on = on_btn
                tm.Add(container, 0, wx.ALIGN_CENTER_VERTICAL)
                self.independent_win1_off.SetToolTip("勾选之后独立绑定360大厅单开窗口")
            else:
                def _toggle2(event, flag, container, off_btn, on_btn):
                    if flag:
                        off_btn.Hide(); on_btn.Show(); container.Layout()
                    else:
                        on_btn.Hide(); off_btn.Show(); container.Layout()
                container, off_btn, on_btn = _make_toggle_btn(panel, "独立✅", "独立✅", _toggle2)
                self.independent_win2_off = off_btn
                self.independent_win2_on = on_btn
                tm.Add(container, 0, wx.ALIGN_CENTER_VERTICAL)
                self.independent_win2_off.SetToolTip("勾选之后独立绑定360大厅单开窗口")
        main_sizer.Add(tm, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        # 暂时修改
        _show_auto_combat = has_script != "free" or datetime.now() < datetime(2026, 9, 30)
        if _show_auto_combat:
            main_sizer.AddSpacer(8)
            sec("自动战斗")
            auto_combat_panel = wx.Panel(panel)
            auto_combat_panel.SetBackgroundColour(self.C_BG)
            auto_row = wx.BoxSizer(wx.HORIZONTAL)

            self.combat_auto_checkboxes = {}
            scene_label = wx.StaticText(auto_combat_panel, label="副本开关")
            scene_label.SetForegroundColour(self.C_MUTED)
            scene_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            auto_row.Add(scene_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            for scene in ["战魂", "蛇", "四象"]:
                cb = wx.CheckBox(auto_combat_panel, label=scene)
                cb.SetForegroundColour(self.C_MUTED)
                cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
                self.combat_auto_checkboxes[scene] = cb
                auto_row.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

            auto_row.AddStretchSpacer()

            liubei_label = wx.StaticText(auto_combat_panel, label="刘备数量")
            liubei_label.SetForegroundColour(self.C_MUTED)
            liubei_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            auto_row.Add(liubei_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            self.liubeiCountInputs = {}
            for idx, lbl in [(0, "队长"), (1, "队友1"), (2, "队友2")]:
                lb = wx.StaticText(auto_combat_panel, label=f"{lbl}:")
                lb.SetForegroundColour(self.C_MUTED)
                auto_row.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
                tc = wx.TextCtrl(auto_combat_panel, size=(32, 24), validator=NumberValidator())
                tc.SetValue("1" if idx == 0 else "0")
                tc.SetBackgroundColour(self.C_INPUT_BG)
                tc.SetForegroundColour(self.C_TEXT)
                self.liubeiCountInputs[idx] = tc
                auto_row.Add(tc, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2)

            auto_row.AddSpacer(12)
            self.use_heal_cb = wx.CheckBox(auto_combat_panel, label="吃药")
            self.use_heal_cb.SetForegroundColour(self.C_MUTED)
            self.use_heal_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            auto_row.Add(self.use_heal_cb, 0, wx.ALIGN_CENTER_VERTICAL)

            auto_combat_panel.SetSizer(auto_row)
            main_sizer.Add(auto_combat_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        else:
            self.liubeiCountInputs = {0: 1, 1: 0, 2: 0}
            self.combat_auto_checkboxes = {}

        # ── 三栏：日常次数 | 层数/难度 | 整点 ──
        cols = wx.BoxSizer(wx.HORIZONTAL)

        # 日常次数列
        f_daily = wx.Panel(panel)
        f_daily.SetBackgroundColour(self.C_SURFACE)
        fds = wx.BoxSizer(wx.VERTICAL)
        t0 = wx.StaticText(f_daily, label="日常次数")
        t0.SetForegroundColour(self.C_GOLD)
        t0.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        fds.Add(t0, 0, wx.ALL, 6)

        daily_grid = wx.FlexGridSizer(cols=2, vgap=2, hgap=4)

        self.zhanhun_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.zhanhun_count.SetHint("21")
        self.zhanhun_count.SetBackgroundColour(self.C_INPUT_BG)
        self.zhanhun_count.SetForegroundColour(self.C_TEXT)
        self.qingyuan_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.qingyuan_count.SetHint("21")
        self.qingyuan_count.SetBackgroundColour(self.C_INPUT_BG)
        self.qingyuan_count.SetForegroundColour(self.C_TEXT)
        self.lianyu_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.lianyu_count.SetHint("21")
        self.lianyu_count.SetBackgroundColour(self.C_INPUT_BG)
        self.lianyu_count.SetForegroundColour(self.C_TEXT)
        self.shihun_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.shihun_count.SetHint("21")
        self.shihun_count.SetBackgroundColour(self.C_INPUT_BG)
        self.shihun_count.SetForegroundColour(self.C_TEXT)
        self.sixiang_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.sixiang_count.SetHint("21")
        self.sixiang_count.SetBackgroundColour(self.C_INPUT_BG)
        self.sixiang_count.SetForegroundColour(self.C_TEXT)
        self.rongdong_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.rongdong_count.SetHint("2")
        self.rongdong_count.SetBackgroundColour(self.C_INPUT_BG)
        self.rongdong_count.SetForegroundColour(self.C_TEXT)
        self.mingjiang_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.mingjiang_count.SetHint("8")
        self.mingjiang_count.SetBackgroundColour(self.C_INPUT_BG)
        self.mingjiang_count.SetForegroundColour(self.C_TEXT)
        self.liandan_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.liandan_count.SetHint("3")
        self.liandan_count.SetBackgroundColour(self.C_INPUT_BG)
        self.liandan_count.SetForegroundColour(self.C_TEXT)
        self.yinhun_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.yinhun_count.SetHint("4")
        self.yinhun_count.SetBackgroundColour(self.C_INPUT_BG)
        self.yinhun_count.SetForegroundColour(self.C_TEXT)
        self.wuxing_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.wuxing_count.SetHint("2")
        self.wuxing_count.SetBackgroundColour(self.C_INPUT_BG)
        self.wuxing_count.SetForegroundColour(self.C_TEXT)
        self.sangumaolu_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.sangumaolu_count.SetHint("3")
        self.sangumaolu_count.SetBackgroundColour(self.C_INPUT_BG)
        self.sangumaolu_count.SetForegroundColour(self.C_TEXT)
        self.hong_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.hong_count.SetHint("4")
        self.hong_count.SetBackgroundColour(self.C_INPUT_BG)
        self.hong_count.SetForegroundColour(self.C_TEXT)

        self.yunyou_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.yunyou_count.SetHint("1")
        self.yunyou_count.SetBackgroundColour(self.C_INPUT_BG)
        self.yunyou_count.SetForegroundColour(self.C_TEXT)
        self.bamen_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.bamen_count.SetHint("1")
        self.bamen_count.SetBackgroundColour(self.C_INPUT_BG)
        self.bamen_count.SetForegroundColour(self.C_TEXT)
        self.laoshu_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.laoshu_count.SetHint("1")
        self.laoshu_count.SetBackgroundColour(self.C_INPUT_BG)
        self.laoshu_count.SetForegroundColour(self.C_TEXT)
        self.guandujy_count = wx.TextCtrl(f_daily, size=(50, 26), validator=NumberValidator())
        self.guandujy_count.SetHint("1")
        self.guandujy_count.SetBackgroundColour(self.C_INPUT_BG)
        self.guandujy_count.SetForegroundColour(self.C_TEXT)

        daily_items = [
            ("战魂", self.zhanhun_count), ("青渊", self.qingyuan_count),
            ("镇魂", self.lianyu_count), ("噬魂", self.shihun_count),
            ("四象", self.sixiang_count), ("溶洞", self.rongdong_count),
            ("名将", self.mingjiang_count), ("炼丹", self.liandan_count),
            ("英魂", self.yinhun_count), ("五行", self.wuxing_count),
            ("茅庐", self.sangumaolu_count), ("红", self.hong_count),
            ("云游", self.yunyou_count), ("八门", self.bamen_count),
            ("老鼠", self.laoshu_count), ("官渡", self.guandujy_count),
        ]
        bold_labels = {"战魂", "镇魂", "噬魂", "青渊", "四象"}
        for label_text, ctrl in daily_items:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f_daily, label=label_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            if label_text in bold_labels:
                lb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
            rs.Add(ctrl, 0, wx.ALIGN_CENTER_VERTICAL)
            daily_grid.Add(rs, 0, wx.ALIGN_CENTER_VERTICAL)
        fds.Add(daily_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        sep = wx.StaticLine(f_daily, size=(-1, 1))
        fds.Add(sep, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
        fds.AddSpacer(4)
        # 第一行: 帮派任务 + 打完魔镜
        row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_bangpai = wx.CheckBox(f_daily, label="帮派任务")
        self.cb_bangpai.SetForegroundColour(self.C_MUTED)
        self.cb_bangpai.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        row1.Add(self.cb_bangpai, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)
        self.cb_mojing = wx.CheckBox(f_daily, label="打完魔镜")
        self.cb_mojing.SetForegroundColour(self.C_MUTED)
        self.cb_mojing.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        row1.Add(self.cb_mojing, 0, wx.ALIGN_CENTER_VERTICAL)
        fds.Add(row1, 0, wx.LEFT | wx.RIGHT, 6)

        # 第二行: 穿插整点 + 清空/重置按钮
        row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_zhengdian = wx.CheckBox(f_daily, label="穿插整点")
        self.cb_zhengdian.SetForegroundColour(self.C_MUTED)
        self.cb_zhengdian.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        if has_script != "all":
            self.cb_zhengdian.Hide()
        row2.Add(self.cb_zhengdian, 0, wx.ALIGN_CENTER_VERTICAL)
        row2.AddStretchSpacer()

        _btn_bg = wx.Colour(215, 218, 226)
        self.btn_clear = wx.Button(f_daily, label="清空", size=(44, 24), style=wx.BORDER_NONE)
        self.btn_clear.SetBackgroundColour(_btn_bg)
        self.btn_clear.SetForegroundColour(self.C_MUTED)
        self.btn_clear.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.btn_clear.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.btn_clear.Bind(wx.EVT_BUTTON, self.on_clear_click)
        row2.Add(self.btn_clear, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.btn_reset = wx.Button(f_daily, label="重置", size=(44, 24), style=wx.BORDER_NONE)
        self.btn_reset.SetBackgroundColour(_btn_bg)
        self.btn_reset.SetForegroundColour(self.C_MUTED)
        self.btn_reset.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.btn_reset.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.btn_reset.Bind(wx.EVT_BUTTON, self.on_reset_click)
        row2.Add(self.btn_reset, 0, wx.ALIGN_CENTER_VERTICAL)
        fds.Add(row2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)

        f_daily.SetSizer(fds)
        cols.Add(f_daily, 1, wx.EXPAND | wx.RIGHT, 4)

        # 层数/难度列
        f_floor = wx.Panel(panel)
        f_floor.SetBackgroundColour(self.C_SURFACE)
        ffs = wx.BoxSizer(wx.VERTICAL)
        t2 = wx.StaticText(f_floor, label="层数/难度")
        t2.SetForegroundColour(self.C_GOLD)
        t2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        ffs.Add(t2, 0, wx.ALL, 6)

        self.choiceMojing = wx.ComboBox(f_floor, size=(-1, 28), choices=["迷幻境（虚实）", "狱境（黑白无常）", "刷张辽", "炎冰境"])
        self.choiceMojing.SetHint("魔镜层数")
        self.choiceMojing.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceMojing.SetForegroundColour(self.C_TEXT)
        self.choiceHeifeng = wx.ComboBox(f_floor, size=(-1, 28), choices=["大/80", "二/50", "刷龙珠", "大全程", "二全程"])
        self.choiceHeifeng.SetHint("黑风/龙岛")
        self.choiceHeifeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceHeifeng.SetForegroundColour(self.C_TEXT)
        self.heifeng_count = wx.TextCtrl(f_floor, size=(50, 26), validator=NumberValidator())
        self.heifeng_count.SetHint("0")
        self.heifeng_count.SetBackgroundColour(self.C_INPUT_BG)
        self.heifeng_count.SetForegroundColour(self.C_TEXT)
        self.choiceCeng = wx.ComboBox(f_floor, size=(-1, 28), choices=["20层", "21层", "22层", "23层", "24层", "25层"])
        self.choiceCeng.SetHint("战魂层数")
        self.choiceCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceCeng.SetForegroundColour(self.C_TEXT)
        self.zhanhun_start_floor = wx.ComboBox(f_floor, size=(-1, 28), choices=[f"{i}层" for i in range(1, 21)])
        self.zhanhun_start_floor.SetValue("1层")
        self.zhanhun_start_floor.SetBackgroundColour(self.C_INPUT_BG)
        self.zhanhun_start_floor.SetForegroundColour(self.C_TEXT)
        self.choiceZhanHunCeng = wx.ComboBox(f_floor, size=(-1, 28), choices=["26层", "27层", "27层自动战斗"])
        self.choiceZhanHunCeng.SetHint("镇魂层数")
        self.choiceZhanHunCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceZhanHunCeng.SetForegroundColour(self.C_TEXT)
        self.choiceShiHunCeng = wx.ComboBox(f_floor, size=(-1, 28), choices=["28层", "29层"])
        self.choiceShiHunCeng.SetHint("噬魂层数")
        self.choiceShiHunCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceShiHunCeng.SetForegroundColour(self.C_TEXT)
        self.sixiang_difficulty = wx.ComboBox(f_floor, size=(-1, 28), choices=["普通", "精英", "炼狱"])
        self.sixiang_difficulty.SetHint("四象难度")
        self.sixiang_difficulty.SetBackgroundColour(self.C_INPUT_BG)
        self.sixiang_difficulty.SetForegroundColour(self.C_TEXT)

        for lbl_text, ctrl in [
            ("魔镜", self.choiceMojing), ("黑风", self.choiceHeifeng),
            ("次数", self.heifeng_count),
            ("战魂", self.choiceCeng), ("开始", self.zhanhun_start_floor),
            ("镇魂", self.choiceZhanHunCeng), ("噬魂", self.choiceShiHunCeng),
            ("四象", self.sixiang_difficulty),
        ]:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f_floor, label=lbl_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            rs.Add(ctrl, 1, wx.EXPAND)
            ffs.Add(rs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        f_floor.SetSizer(ffs)
        cols.Add(f_floor, 1, wx.EXPAND | wx.RIGHT, 4)

        # 整点列
        f3 = wx.Panel(panel)
        f3.SetBackgroundColour(self.C_SURFACE)
        fs3 = wx.BoxSizer(wx.VERTICAL)
        t3 = wx.StaticText(f3, label="整点")
        t3.SetForegroundColour(self.C_GOLD)
        t3.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        fs3.Add(t3, 0, wx.ALL, 6)

        zdc = ["蛇+全打", "龙+全打", "全打", "走路", "49整点", "49蛇+全打", "49龙+全打"]
        self.choiceZhengdian = wx.ComboBox(f3, size=(-1, 28), choices=zdc)
        self.choiceZhengdian.SetHint("整点")
        self.choiceZhengdian.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceZhengdian.SetForegroundColour(self.C_TEXT)
        self.choiceAfterZreo = wx.ComboBox(f3, size=(-1, 28), choices=["官渡", "魔镜", "日常", "49日常", "名将闯关"])
        self.choiceAfterZreo.SetHint("0点执行的脚本")
        self.choiceAfterZreo.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceAfterZreo.SetForegroundColour(self.C_TEXT)

        for lbl_text, ctrl in [("整点", self.choiceZhengdian), ("0点", self.choiceAfterZreo)]:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f3, label=lbl_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            rs.Add(ctrl, 1, wx.EXPAND)
            fs3.Add(rs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        f3.SetSizer(fs3)
        cols.Add(f3, 1, wx.EXPAND)

        main_sizer.Add(cols, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        # ── 确定按钮 ──
        self.button = wx.Button(panel, label="✓ 确定", size=(-1, 36), style=wx.BORDER_NONE)
        self.button.SetBackgroundColour(self.C_GOLD)
        self.button.SetForegroundColour(wx.Colour(255, 255, 255))
        self.button.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.button.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.button.Disable()
        main_sizer.Add(self.button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        # 方案底部按钮（保留引用但移到方案行用图标了）
        self.saveButton = self.updateButton = self.getButton = None

        # 隐藏的控件
        self.choice_line = wx.ComboBox(panel, size=(60, 28), choices=["一线", "二线", "三线"])
        self.choice_line.Hide()
        self.team_leader_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.team_leader_pos.Hide()
        self.teammate1_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.teammate1_pos.Hide()
        self.teammate2_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.teammate2_pos.Hide()

        panel.SetSizer(main_sizer)
        self.load_current_scheme()
        self.team_leader_text.SetFocus()

        # 日常次数控件列表 + 默认值（用于清空/重置）
        self._daily_defaults = {
            self.zhanhun_count: "21", self.qingyuan_count: "21", self.lianyu_count: "21",
            self.shihun_count: "21", self.sixiang_count: "21", self.rongdong_count: "2",
            self.mingjiang_count: "8", self.liandan_count: "3", self.yinhun_count: "4",
            self.wuxing_count: "2", self.sangumaolu_count: "3", self.hong_count: "4",
            self.yunyou_count: "1", self.bamen_count: "1", self.laoshu_count: "1",
            self.guandujy_count: "1",
        }

    def on_clear_click(self, event):
        for ctrl in self._daily_defaults:
            ctrl.SetValue("0")
        self.cb_mojing.SetValue(False)
        self.cb_bangpai.SetValue(False)
        if hasattr(self, 'cb_zhengdian') and self.cb_zhengdian.IsShown():
            self.cb_zhengdian.SetValue(False)

    def on_reset_click(self, event):
        for ctrl, default in self._daily_defaults.items():
            ctrl.SetValue(default)
        self.cb_mojing.SetValue(False)
        self.cb_bangpai.SetValue(False)
        if hasattr(self, 'cb_zhengdian') and self.cb_zhengdian.IsShown():
            self.cb_zhengdian.SetValue(False)

    def _section_header(self, sizer, panel, text):
        l = wx.StaticText(panel, label=f"▸ {text}")
        l.SetForegroundColour(wx.Colour(50, 80, 140))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        sizer.Add(l, 0, wx.LEFT | wx.RIGHT, 12)
        sizer.AddSpacer(4)

    def _make_card(self, panel):
        c = wx.Panel(panel)
        c.SetBackgroundColour(wx.Colour(240, 242, 246))
        return c

    def _dialog_icon(self, name, size):
        path = self.frame.get_resource_path("serveAssets/images/" + name)
        img = wx.Image(path).Scale(size, size, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

    # self.choiceCeng.Hide()
    # self.Bind(wx.EVT_COMBOBOX, self.choiceCengScript, self.choiceCeng)
    # self.teammate1_text.Bind(wx.EVT_TEXT, self.on_text_change)
    # self.teammate2_text.Bind(wx.EVT_TEXT, self.on_text_change)
    # choices = ["加血", "卖装备", "拆分强化石", "换大丹"]
    # self.checklist = wx.CheckListBox(panel, choices=choices, pos=(130, 10))

    # self.checklist.Bind(wx.EVT_CHECKLISTBOX, self.on_checklistbox)

    # def on_checklistbox(self, event):
    # 	selections = [self.checklist.GetString(i) for i in range(self.checklist.GetCount()) if self.checklist.IsChecked(i)]
    # 	print("选中的值为:", selections)
    # def choiceCengScript(self, event):
    # 	self.zhanhunFloor = self.choiceCeng.GetValue()

    def on_any_checkbox_change(self, event):
        pass

    def on_save_data(self, event):
        game_name = self.team_leader_text.GetValue()
        heifeng_count = self.heifeng_count.GetValue()
        zhanhun_floor = self.choiceCeng.GetValue()
        mojing_floor = self.choiceMojing.GetValue()
        zhengdian_floor = self.choiceZhengdian.GetValue()
        heifeng_floor = self.choiceHeifeng.GetValue()
        after_zreo = self.choiceAfterZreo.GetValue()
        teammate1_text = self.teammate1_text.GetValue()
        teammate2_text = self.teammate2_text.GetValue()
        choiceZhanHunCeng = self.choiceZhanHunCeng.GetValue()
        choice_line = self.choice_line.GetValue()
        teammate1_pos = self.teammate1_pos.GetValue()
        teammate2_pos = self.teammate2_pos.GetValue()
        team_leader_pos = self.team_leader_pos.GetValue()
        lianyu_count = self.lianyu_count.GetValue()
        qingyuan_count = self.qingyuan_count.GetValue()
        zhanhun_count = self.zhanhun_count.GetValue()
        shihun_count = self.shihun_count.GetValue()
        shihun_floor = self.choiceShiHunCeng.GetValue()
        sixiang_count = self.sixiang_count.GetValue()
        sixiang_difficulty = self.sixiang_difficulty.GetValue()
        zhanhun_start_floor = self.zhanhun_start_floor.GetValue()
        rongdong_count = self.rongdong_count.GetValue()
        liandan_count = self.liandan_count.GetValue()
        wuxing_count = self.wuxing_count.GetValue()
        yinhun_count = self.yinhun_count.GetValue()
        sangumaolu_count = self.sangumaolu_count.GetValue()
        hong_count = self.hong_count.GetValue()
        mingjiang_count = self.mingjiang_count.GetValue()
        yunyou_count = self.yunyou_count.GetValue()
        bamen_count = self.bamen_count.GetValue()
        laoshu_count = self.laoshu_count.GetValue()
        guandujy_count = self.guandujy_count.GetValue()
        richang_zhengdian = self.cb_zhengdian.GetValue()
        richang_mojing = self.cb_mojing.GetValue()
        bangpai_enabled = self.cb_bangpai.GetValue()

        # 保存数据到文件
        self.save_to_file(
            teammate1_pos,
            teammate2_pos,
            team_leader_pos,
            game_name,
            heifeng_count,
            zhanhun_floor,
            mojing_floor,
            zhengdian_floor,
            teammate1_text,
            teammate2_text,
            heifeng_floor,
            after_zreo,
            choiceZhanHunCeng,
            choice_line,
            lianyu_count,
            zhanhun_count,
            qingyuan_count,
            shihun_count,
            shihun_floor,
            sixiang_count,
            sixiang_difficulty,
            zhanhun_start_floor,
            rongdong_count,
            liandan_count,
            wuxing_count,
            yinhun_count,
            sangumaolu_count,
            hong_count,
            mingjiang_count,
            yunyou_count,
            bamen_count,
            laoshu_count,
            guandujy_count,
            richang_zhengdian,
            richang_mojing,
            bangpai_enabled,
        )

    def save_to_file(
            self,
            teammate1_pos,
            teammate2_pos,
            team_leader_pos,
            game_name,
            heifeng_count,
            zhanhun_floor,
            mojing_floor,
            zhengdian_floor,
            teammate1_text,
            teammate2_text,
            heifeng_floor,
            after_zreo,
            choiceZhanHunCeng,
            choice_line,
            lianyu_count,
            zhanhun_count,
            qingyuan_count,
            shihun_count,
            shihun_floor,
            sixiang_count,
            sixiang_difficulty,
            zhanhun_start_floor,
            rongdong_count,
            liandan_count,
            wuxing_count,
            yinhun_count,
            sangumaolu_count,
            hong_count,
            mingjiang_count,
            yunyou_count,
            bamen_count,
            laoshu_count,
            guandujy_count,
            richang_zhengdian,
            richang_mojing,
            bangpai_enabled,
    ):
        # 获取脚本文件的同级目录
        exe_path = sys.executable
        script_dir = os.path.dirname(exe_path)
        file_path = os.path.join(script_dir, "data.txt")

        # 写入数据到文件
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"game_name: {game_name}\n")
            file.write(f"heifeng_count: {heifeng_count}\n")
            file.write(f"zhanhun_floor: {zhanhun_floor}\n")
            file.write(f"mojing_floor: {mojing_floor}\n")
            file.write(f"zhengdian_floor: {zhengdian_floor}\n")
            file.write(f"teammate1_text: {teammate1_text}\n")
            file.write(f"teammate2_text: {teammate2_text}\n")
            file.write(f"heifeng_floor: {heifeng_floor}\n")
            file.write(f"after_zreo: {after_zreo}\n")
            file.write(f"choiceZhanHunCeng: {choiceZhanHunCeng}\n")
            file.write(f"choice_line: {choice_line}\n")
            file.write(f"teammate1_pos: {teammate1_pos}\n")
            file.write(f"teammate2_pos: {teammate2_pos}\n")
            file.write(f"team_leader_pos: {team_leader_pos}\n")
            file.write(f"lianyu_count: {lianyu_count}\n")
            file.write(f"qingyuan_count: {qingyuan_count}\n")
            file.write(f"zhanhun_count: {zhanhun_count}\n")
            file.write(f"shihun_count: {shihun_count}\n")
            file.write(f"shihun_floor: {shihun_floor}\n")
            file.write(f"sixiang_count: {sixiang_count}\n")
            file.write(f"sixiang_difficulty: {sixiang_difficulty}\n")
            file.write(f"zhanhun_start_floor: {zhanhun_start_floor}\n")
            file.write(f"rongdong_count: {rongdong_count}\n")
            file.write(f"liandan_count: {liandan_count}\n")
            file.write(f"wuxing_count: {wuxing_count}\n")
            file.write(f"yinhun_count: {yinhun_count}\n")
            file.write(f"sangumaolu_count: {sangumaolu_count}\n")
            file.write(f"hong_count: {hong_count}\n")
            file.write(f"mingjiang_count: {mingjiang_count}\n")
            file.write(f"yunyou_count: {yunyou_count}\n")
            file.write(f"bamen_count: {bamen_count}\n")
            file.write(f"laoshu_count: {laoshu_count}\n")
            file.write(f"guandujy_count: {guandujy_count}\n")
            file.write(f"richang_zhengdian: {richang_zhengdian}\n")
            file.write(f"richang_mojing: {richang_mojing}\n")
            file.write(f"bangpai_enabled: {bangpai_enabled}\n")
        wx.MessageBox("数据已保存", "成功", wx.OK | wx.ICON_INFORMATION)

    def get_file_info(self, event):
        # 获取脚本文件的同级目录
        exe_path = sys.executable
        script_dir = os.path.dirname(exe_path)
        file_path = os.path.join(script_dir, "data.txt")

        # 读取数据从文件
        if not os.path.exists(file_path):
            wx.MessageBox("文件不存在", "错误", wx.OK | wx.ICON_ERROR)
            return None
        data = {}
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if len(line.strip().split(": ", 1)) != 2:
                    continue
                key, value = line.strip().split(": ", 1)
                data[key] = value
        game_name = data.get("game_name", "")
        heifeng_count = data.get("heifeng_count", "")
        zhanhun_floor = data.get("zhanhun_floor", "")
        mojing_floor = data.get("mojing_floor", "")
        zhengdian_floor = data.get("zhengdian_floor", "")
        heifeng_floor = data.get("heifeng_floor", "")
        after_zreo = data.get("after_zreo", "")
        teammate1_text = data.get("teammate1_text", "")
        teammate2_text = data.get("teammate2_text", "")
        choiceZhanHunCeng = data.get("choiceZhanHunCeng", "")
        choice_line = data.get("choice_line", "")
        teammate1_pos = data.get("teammate1_pos", "")
        teammate2_pos = data.get("teammate2_pos", "")
        team_leader_pos = data.get("team_leader_pos", "")
        lianyu_count = data.get("lianyu_count", "")
        qingyuan_count = data.get("qingyuan_count", "")
        zhanhun_count = data.get("zhanhun_count", "")
        shihun_count = data.get("shihun_count", "")
        shihun_floor = data.get("shihun_floor", "")
        sixiang_count = data.get("sixiang_count", "21")
        sixiang_difficulty = data.get("sixiang_difficulty", "")
        zhanhun_start_floor = data.get("zhanhun_start_floor", "1层")
        rongdong_count = data.get("rongdong_count", "")
        liandan_count = data.get("liandan_count", "")
        wuxing_count = data.get("wuxing_count", "")
        yinhun_count = data.get("yinhun_count", "")
        sangumaolu_count = data.get("sangumaolu_count", "")
        hong_count = data.get("hong_count", "")
        mingjiang_count = data.get("mingjiang_count", "")
        yunyou_count = data.get("yunyou_count", "")
        bamen_count = data.get("bamen_count", "")
        laoshu_count = data.get("laoshu_count", "")
        guandujy_count = data.get("guandujy_count", "")
        self.team_leader_text.SetValue(game_name)
        self.heifeng_count.SetValue(heifeng_count)
        self.choiceCeng.SetValue(zhanhun_floor)
        self.choiceMojing.SetValue(mojing_floor)
        self.choiceZhengdian.SetValue(zhengdian_floor)
        self.choiceHeifeng.SetValue(heifeng_floor)
        self.choiceAfterZreo.SetValue(after_zreo)
        self.teammate1_text.SetValue(teammate1_text)
        self.teammate2_text.SetValue(teammate2_text)
        self.choiceZhanHunCeng.SetValue(choiceZhanHunCeng)
        self.choice_line.SetValue(choice_line)
        self.teammate1_pos.SetValue(teammate1_pos)
        self.teammate2_pos.SetValue(teammate2_pos)
        self.team_leader_pos.SetValue(team_leader_pos)
        self.lianyu_count.SetValue(lianyu_count)
        self.qingyuan_count.SetValue(qingyuan_count)
        self.zhanhun_count.SetValue(zhanhun_count)
        self.shihun_count.SetValue(shihun_count)
        self.choiceShiHunCeng.SetValue(shihun_floor)
        self.sixiang_count.SetValue(sixiang_count)
        self.sixiang_difficulty.SetValue(sixiang_difficulty)
        self.zhanhun_start_floor.SetValue(zhanhun_start_floor)
        self.rongdong_count.SetValue(rongdong_count)
        self.liandan_count.SetValue(liandan_count)
        self.wuxing_count.SetValue(wuxing_count)
        self.yinhun_count.SetValue(yinhun_count)
        self.sangumaolu_count.SetValue(sangumaolu_count)
        self.hong_count.SetValue(hong_count)
        self.mingjiang_count.SetValue(mingjiang_count)
        self.yunyou_count.SetValue(yunyou_count)
        self.bamen_count.SetValue(bamen_count)
        self.laoshu_count.SetValue(laoshu_count)
        self.guandujy_count.SetValue(guandujy_count)
        self.cb_zhengdian.SetValue(data.get("richang_zhengdian", "False") == "True")
        self.cb_mojing.SetValue(data.get("richang_mojing", "False") == "True")
        self.cb_bangpai.SetValue(data.get("bangpai_enabled", "False") == "True")

    def on_text_change(self, event):
        if self.team_leader_text.GetValue():
            self.button.Enable()
        else:
            self.button.Disable()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.schemes = OrderedDict(data.get("schemes", {}))
                    self.current_scheme = data.get("current", "")
            except:
                self.schemes = OrderedDict()
                self.current_scheme = ""

    def save_config(self):
        data = {"schemes": dict(self.schemes), "current": self.current_scheme}
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    def collect_settings(self):
        combat_auto_scenes = []
        if hasattr(self, 'combat_auto_checkboxes'):
            for scene, cb in self.combat_auto_checkboxes.items():
                if cb.GetValue():
                    combat_auto_scenes.append(scene)
        return {
            "game_name": self.team_leader_text.GetValue(),
            "heifeng_count": self.heifeng_count.GetValue(),
            "zhanhun_floor": self.choiceCeng.GetValue(),
            "mojing_floor": self.choiceMojing.GetValue(),
            "zhengdian_floor": self.choiceZhengdian.GetValue(),
            "heifeng_floor": self.choiceHeifeng.GetValue(),
            "after_zreo": self.choiceAfterZreo.GetValue(),
            "teammate1_text": self.teammate1_text.GetValue(),
            "teammate2_text": self.teammate2_text.GetValue(),
            "choiceZhanHunCeng": self.choiceZhanHunCeng.GetValue(),
            "choice_line": self.choice_line.GetValue(),
            "teammate1_pos": self.teammate1_pos.GetValue(),
            "teammate2_pos": self.teammate2_pos.GetValue(),
            "team_leader_pos": self.team_leader_pos.GetValue(),
            "lianyu_count": self.lianyu_count.GetValue(),
            "qingyuan_count": self.qingyuan_count.GetValue(),
            "zhanhun_count": self.zhanhun_count.GetValue(),
            "shihun_count": self.shihun_count.GetValue(),
            "shihun_floor": self.choiceShiHunCeng.GetValue(),
            "sixiang_count": self.sixiang_count.GetValue(),
            "sixiang_difficulty": self.sixiang_difficulty.GetValue(),
            "zhanhun_start_floor": self.zhanhun_start_floor.GetValue(),
            "rongdong_count": self.rongdong_count.GetValue(),
            "liandan_count": self.liandan_count.GetValue(),
            "wuxing_count": self.wuxing_count.GetValue(),
            "yinhun_count": self.yinhun_count.GetValue(),
            "sangumaolu_count": self.sangumaolu_count.GetValue(),
            "hong_count": self.hong_count.GetValue(),
            "yunyou_count": self.yunyou_count.GetValue(),
            "bamen_count": self.bamen_count.GetValue(),
            "laoshu_count": self.laoshu_count.GetValue(),
            "guandujy_count": self.guandujy_count.GetValue(),
            "mingjiang_count": self.mingjiang_count.GetValue(),
            "richang_zhengdian": self.cb_zhengdian.GetValue(),
            "richang_mojing": self.cb_mojing.GetValue(),
            "bangpai_enabled": self.cb_bangpai.GetValue(),
            "liubei_counts": {idx: (str(self.liubeiCountInputs[idx]) if isinstance(self.liubeiCountInputs[idx], int) else self.liubeiCountInputs[idx].GetValue()) for idx in self.liubeiCountInputs},
            "combat_auto_scenes": combat_auto_scenes,
            "use_heal_item": self.use_heal_cb.GetValue() if hasattr(self, 'use_heal_cb') else False,
        }

    def apply_settings(self, settings):
        self.team_leader_text.SetValue(str(settings.get("game_name", "")))
        self.heifeng_count.SetValue(str(settings.get("heifeng_count", "")))
        self.choiceCeng.SetValue(settings.get("zhanhun_floor", ""))
        self.choiceMojing.SetValue(settings.get("mojing_floor", ""))
        self.choiceZhengdian.SetValue(settings.get("zhengdian_floor", ""))
        self.choiceHeifeng.SetValue(settings.get("heifeng_floor", ""))
        self.choiceAfterZreo.SetValue(settings.get("after_zreo", ""))
        self.teammate1_text.SetValue(settings.get("teammate1_text", ""))
        self.teammate2_text.SetValue(settings.get("teammate2_text", ""))
        self.choiceZhanHunCeng.SetValue(settings.get("choiceZhanHunCeng", ""))
        self.choice_line.SetValue(settings.get("choice_line", ""))
        self.teammate1_pos.SetValue(settings.get("teammate1_pos", ""))
        self.teammate2_pos.SetValue(settings.get("teammate2_pos", ""))
        self.team_leader_pos.SetValue(settings.get("team_leader_pos", ""))
        self.lianyu_count.SetValue(settings.get("lianyu_count", ""))
        self.qingyuan_count.SetValue(settings.get("qingyuan_count", ""))
        self.zhanhun_count.SetValue(settings.get("zhanhun_count", ""))
        self.shihun_count.SetValue(settings.get("shihun_count", ""))
        self.choiceShiHunCeng.SetValue(settings.get("shihun_floor", ""))
        self.sixiang_count.SetValue(settings.get("sixiang_count", "21"))
        self.sixiang_difficulty.SetValue(settings.get("sixiang_difficulty", ""))
        self.zhanhun_start_floor.SetValue(settings.get("zhanhun_start_floor", "1层"))
        self.rongdong_count.SetValue(settings.get("rongdong_count", ""))
        self.liandan_count.SetValue(settings.get("liandan_count", ""))
        self.wuxing_count.SetValue(settings.get("wuxing_count", ""))
        self.yinhun_count.SetValue(settings.get("yinhun_count", ""))
        self.sangumaolu_count.SetValue(settings.get("sangumaolu_count", ""))
        self.hong_count.SetValue(settings.get("hong_count", ""))
        self.yunyou_count.SetValue(settings.get("yunyou_count", ""))
        self.bamen_count.SetValue(settings.get("bamen_count", ""))
        self.laoshu_count.SetValue(settings.get("laoshu_count", ""))
        self.guandujy_count.SetValue(settings.get("guandujy_count", ""))
        self.mingjiang_count.SetValue(settings.get("mingjiang_count", ""))
        self.cb_zhengdian.SetValue(settings.get("richang_zhengdian", False))
        self.cb_mojing.SetValue(settings.get("richang_mojing", False))
        self.cb_bangpai.SetValue(settings.get("bangpai_enabled", False))
        liubei_counts = settings.get("liubei_counts", {"0": "1", "1": "0", "2": "0"})
        for idx in self.liubeiCountInputs:
            key = str(idx)
            default_val = "1" if idx == 0 else "0"
            if not isinstance(self.liubeiCountInputs[idx], int):
                self.liubeiCountInputs[idx].SetValue(str(liubei_counts.get(key, default_val)))
        if hasattr(self, 'combat_auto_checkboxes'):
            saved_scenes = settings.get("combat_auto_scenes", [])
            for scene, cb in self.combat_auto_checkboxes.items():
                cb.SetValue(scene in saved_scenes)
        if hasattr(self, 'use_heal_cb'):
            self.use_heal_cb.SetValue(settings.get("use_heal_item", False))

    def on_scheme_select(self, event):
        scheme_name = self.scheme_choice.GetValue()
        if scheme_name in self.schemes:
            self.apply_settings(self.schemes[scheme_name])
            self.current_scheme = scheme_name

    def load_current_scheme(self):
        if self.current_scheme and self.current_scheme in self.schemes:
            self.apply_settings(self.schemes[self.current_scheme])
            self.scheme_choice.SetValue(self.current_scheme)

    def on_add(self, event):
        if len(self.schemes) >= self.max_schemes:
            wx.MessageBox(
                f"最多只能保存{self.max_schemes}个方案",
                "提示",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        dlg = wx.TextEntryDialog(self, "请输入方案名称:", "新增方案")
        if dlg.ShowModal() == wx.ID_OK:
            scheme_name = dlg.GetValue().strip()
            if not scheme_name:
                wx.MessageBox("方案名称不能为空", "错误", wx.OK | wx.ICON_ERROR)
                return

            if scheme_name in self.schemes:
                confirm = wx.MessageBox(
                    f"方案「{scheme_name}」已存在，是否覆盖？",
                    "确认覆盖", wx.YES_NO | wx.ICON_QUESTION)
                if confirm != wx.YES:
                    return

            settings = self.collect_settings()
            self.schemes[scheme_name] = settings
            self.current_scheme = scheme_name

            # 更新下拉框
            choices = list(self.schemes.keys())
            self.scheme_choice.SetItems(choices)
            self.scheme_choice.SetValue(scheme_name)

            self.save_config()
            wx.MessageBox("方案新增成功", "成功", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_save_scheme(self, event):
        scheme_name = self.scheme_choice.GetValue().strip()
        # 有选中方案且方案存在，直接保存
        if scheme_name and scheme_name in self.schemes:
            settings = self.collect_settings()
            self.schemes[scheme_name] = settings
            self.current_scheme = scheme_name
            self.save_config()
            wx.MessageBox("方案保存成功", "成功", wx.OK | wx.ICON_INFORMATION)
        else:
            # 没有选中方案或方案不存在，走新增逻辑
            self.on_add(event)

    def on_delete(self, event):
        scheme_name = self.scheme_choice.GetValue()
        if not scheme_name or scheme_name not in self.schemes:
            return

        confirm = wx.MessageBox(
            f"确定要删除方案 '{scheme_name}' 吗?",
            "确认删除",
            wx.YES_NO | wx.ICON_QUESTION,
        )
        if confirm == wx.YES:
            del self.schemes[scheme_name]

            choices = list(self.schemes.keys())
            self.scheme_choice.SetItems(choices)
            self.scheme_choice.SetValue(choices[0] if choices else "")

            if self.current_scheme == scheme_name:
                self.current_scheme = choices[0] if choices else ""

            if self.current_scheme and self.current_scheme in self.schemes:
                self.apply_settings(self.schemes[self.current_scheme])

            self.save_config()
            wx.MessageBox("方案已删除", "成功", wx.OK | wx.ICON_INFORMATION)

    def on_button_click(self, event):
        if not self.team_leader_text.GetValue().strip():
            wx.MessageBox("请先输入游戏名称", "提示", wx.OK | wx.ICON_WARNING)
            return
        parent = self.GetParent()
        parent.game_name = self.team_leader_text.GetValue()
        parent.heifengCount = self.heifeng_count.GetValue() or "0"
        parent.zhanhunFloor = self.choiceCeng.GetValue()
        parent.zhanhunFloorNew = self.choiceZhanHunCeng.GetValue()
        parent.heifengFloor = self.choiceHeifeng.GetValue()
        parent.afterZreo = self.choiceAfterZreo.GetValue()
        parent.mojingFloor = self.choiceMojing.GetValue()
        parent.zhengdianFloor = self.choiceZhengdian.GetValue()
        parent.teammate1_name = self.teammate1_text.GetValue()
        parent.teammate2_name = self.teammate2_text.GetValue()
        parent.choice_line = self.choice_line.GetValue()
        parent.teammate1_pos = self.teammate1_pos.GetValue()
        parent.teammate2_pos = self.teammate2_pos.GetValue()
        parent.team_leader_pos = self.team_leader_pos.GetValue()
        parent.lianyu_count = self.lianyu_count.GetValue() or "21"
        parent.qingyuan_count = self.qingyuan_count.GetValue() or "21"
        parent.zhanhun_count = self.zhanhun_count.GetValue() or "21"
        parent.shihun_count = self.shihun_count.GetValue() or "21"
        parent.shihun_floor = self.choiceShiHunCeng.GetValue()
        parent.sixiang_count = self.sixiang_count.GetValue() or "21"
        parent.sixiang_difficulty = self.sixiang_difficulty.GetValue()
        parent.zhanhun_start_floor = self.zhanhun_start_floor.GetValue()
        parent.rongdong_count = self.rongdong_count.GetValue() or "2"
        parent.liandan_count = self.liandan_count.GetValue() or "3"
        parent.wuxing_count = self.wuxing_count.GetValue() or "2"
        parent.yinhun_count = self.yinhun_count.GetValue() or "4"
        parent.sangumaolu_count = self.sangumaolu_count.GetValue() or "3"
        parent.hong_count = self.hong_count.GetValue() or "4"
        parent.yunyou_count = self.yunyou_count.GetValue() or "1"
        parent.bamen_count = self.bamen_count.GetValue() or "1"
        parent.laoshu_count = self.laoshu_count.GetValue() or "1"
        parent.guandujy_count = self.guandujy_count.GetValue() or "1"
        parent.bangpai_enabled = self.cb_bangpai.GetValue()
        parent.mingjiang_count = self.mingjiang_count.GetValue() or "8"
        parent.richang_zhengdian = self.cb_zhengdian.GetValue()
        parent.richang_mojing = self.cb_mojing.GetValue()
        parent.combat_auto_scenes = []
        if hasattr(self, 'combat_auto_checkboxes'):
            for scene, cb in self.combat_auto_checkboxes.items():
                if cb.GetValue():
                    parent.combat_auto_scenes.append(scene)
        parent.liubeiCounts = {}
        for idx in self.liubeiCountInputs:
            item = self.liubeiCountInputs[idx]
            if isinstance(item, int):
                parent.liubeiCounts[idx] = item
            else:
                val = item.GetValue()
                parent.liubeiCounts[idx] = int(val) if val.isdigit() else (1 if idx == 0 else 0)
        parent.independent_win1 = self.independent_win1_on.IsShown() if hasattr(self, "independent_win1_on") else False
        parent.independent_win2 = self.independent_win2_on.IsShown() if hasattr(self, "independent_win2_on") else False
        parent.use_heal_item = self.use_heal_cb.GetValue() if hasattr(self, 'use_heal_cb') else False
        if self.IsModal():
            self.EndModal(wx.ID_OK)


class NumberValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumberValidator()

    def OnChar(self, event):
        key = event.GetKeyCode()
        # 允许控制键（退格、删除、方向键、Tab等）
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE:
            event.Skip()
            return
        # 只允许数字
        if wx.WXK_NUMPAD0 <= key <= wx.WXK_NUMPAD9:
            event.Skip()
            return
        if chr(key).isdigit():
            event.Skip()
            return
        # 其他字符（英文等）直接拦截，不调用 Skip

    def Validate(self, win):
        text_ctrl = self.GetWindow()
        value = text_ctrl.GetValue()
        if not value.isdigit():
            wx.MessageBox("请输入数字", "错误", wx.OK | wx.ICON_ERROR)
            text_ctrl.SetBackgroundColour(wx.Colour(255, 230, 230))
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False
        else:
            text_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
            text_ctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class HelpDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(70, 75, 85)

    def __init__(self, parent, title, content, images):
        super(HelpDialog, self).__init__(
            parent, title=title, size=(800, 600), pos=(200, 20),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.SetBackgroundColour(self.C_BG)

        scroll = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL)
        scroll.SetBackgroundColour(self.C_BG)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        title_panel = wx.Panel(scroll)
        title_panel.SetBackgroundColour(self.C_BG)
        title_sizer_b = wx.BoxSizer(wx.HORIZONTAL)
        title_text = wx.StaticText(title_panel, label=title)
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(self.C_GOLD)
        title_sizer_b.Add(title_text, 1, wx.ALIGN_CENTER | wx.ALL, 12)
        title_panel.SetSizer(title_sizer_b)
        main_sizer.Add(title_panel, 0, wx.EXPAND)

        all_text = "\n\n".join(content)
        text_ctrl = wx.TextCtrl(scroll, value=all_text,
                                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.TE_NO_VSCROLL)
        text_ctrl.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        text_ctrl.SetForegroundColour(self.C_TEXT)
        text_ctrl.SetBackgroundColour(self.C_BG)
        dc = wx.ClientDC(text_ctrl)
        dc.SetFont(text_ctrl.GetFont())
        line_h = dc.GetCharHeight()
        available_w = 800 - 40
        wrapped_lines = 0
        for line in all_text.split('\n'):
            if not line:
                wrapped_lines += 1
                continue
            tw, _ = dc.GetTextExtent(line)
            wrapped_lines += max(1, int(tw / available_w) + 1)
        text_h = line_h * (wrapped_lines + 1) + 20
        main_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        text_ctrl.SetMinSize((-1, text_h))

        def _forward_wheel(evt):
            pos = scroll.GetScrollPos(wx.VERTICAL)
            delta = evt.GetWheelRotation()
            step = 3
            if delta > 0:
                scroll.Scroll(0, max(0, pos - step))
            else:
                scroll.Scroll(0, pos + step)
        text_ctrl.Bind(wx.EVT_MOUSEWHEEL, _forward_wheel)

        for idx, image_path in enumerate(images):
            try:
                image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                if image.IsOk():
                    img_panel = wx.Panel(scroll)
                    img_panel.SetBackgroundColour(self.C_SURFACE)
                    row = wx.BoxSizer(wx.HORIZONTAL)
                    dialog_width = self.GetSize().width
                    max_width = int(dialog_width * 0.85)
                    ow, oh = image.GetWidth(), image.GetHeight()
                    if ow > max_width:
                        nw, nh = max_width, int(oh * max_width / ow)
                    else:
                        nw, nh = ow, oh
                    image = image.Scale(nw, nh, wx.IMAGE_QUALITY_HIGH)
                    bitmap = wx.StaticBitmap(img_panel, -1, image.ConvertToBitmap())
                    row.Add(bitmap, 0, wx.ALL | wx.LEFT, 10)
                    img_panel.SetSizer(row)
                    main_sizer.Add(img_panel, 0, wx.EXPAND | wx.LEFT, 5)
                    if idx < len(images) - 1:
                        line = wx.StaticLine(scroll, style=wx.LI_HORIZONTAL)
                        main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
            except Exception as e:
                print(f"加载图片失败: {e}")

        button_panel = wx.Panel(scroll)
        button_panel.SetBackgroundColour(self.C_BG)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_button = wx.Button(button_panel, label="关闭", size=(100, 35), style=wx.BORDER_NONE)
        close_button.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        close_button.SetBackgroundColour(self.C_SURFACE)
        close_button.SetForegroundColour(self.C_TEXT)
        close_button.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        button_sizer.AddStretchSpacer()
        button_sizer.Add(close_button, 0, wx.ALL, 10)
        button_panel.SetSizer(button_sizer)
        main_sizer.Add(button_panel, 0, wx.EXPAND | wx.TOP, 8)

        scroll.SetSizer(main_sizer)
        scroll.SetupScrolling(scroll_x=False, scroll_y=True, rate_y=20)
        scroll.FitInside()

        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(scroll, 1, wx.EXPAND)
        self.SetSizer(dialog_sizer)


class UpdateDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_TEXT = wx.Colour(50, 80, 140)
    C_BTN = wx.Colour(50, 80, 140)

    def __init__(self, parent, remote_info):
        super().__init__(parent, title="检查更新", size=(550, 560), pos=(260, 30),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetBackgroundColour(self.C_BG)

        self.current_version = UpdateDialog.get_current_version()
        self.remote_info = remote_info
        self.latest_version = self.remote_info["version"]
        self.download_url = self.remote_info["download_url"]
        self.release_date = self.remote_info.get("release_date", "")

        self.InitUI()

        changelog = self.remote_info.get("changelog", "")
        if isinstance(changelog, list):
            changelog = "\n".join(changelog)
        self.changelog_text.SetValue(changelog)

        def _parse(v):
            try:
                parts = v.split(".")
                return tuple(int(p) for p in parts)
            except Exception:
                return (0,)

        if _parse(self.latest_version) > _parse(self.current_version):
            self.update_btn.Show()
            self.status_text.SetLabel("发现新版本！")
            self.status_text.SetForegroundColour(wx.Colour(220, 60, 50))
        else:
            self.status_text.SetLabel("已是最新版本")
            self.status_text.SetForegroundColour(wx.Colour(40, 160, 80))

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        vs = wx.BoxSizer(wx.VERTICAL)

        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(self.C_BG)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_text = wx.StaticText(title_panel, label="检查更新")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(self.C_TEXT)
        title_sizer.Add(title_text, 0, wx.ALIGN_CENTER_VERTICAL)
        title_panel.SetSizer(title_sizer)
        vs.Add(title_panel, 0, wx.ALL | wx.EXPAND, 12)

        info_panel = wx.Panel(panel)
        info_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        info_sizer = wx.FlexGridSizer(3, 2, 10, 10)
        info_sizer.AddGrowableCol(1, 1)

        labels = ["当前版本:", "最新版本:", "发布日期:"]
        values = [self.current_version, self.latest_version, self.release_date]
        self.info_texts = []
        for label, value in zip(labels, values):
            lb = wx.StaticText(info_panel, label=label)
            lb.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            lb.SetForegroundColour(wx.Colour(80, 80, 90))
            val = wx.StaticText(info_panel, label=value)
            val.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            val.SetForegroundColour(wx.Colour(40, 42, 50))
            info_sizer.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL)
            info_sizer.Add(val, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
            self.info_texts.append(val)

        info_panel.SetSizer(info_sizer)
        vs.Add(info_panel, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 12)

        self.status_text = wx.StaticText(panel, label="检查中...")
        self.status_text.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vs.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.TOP, 12)

        vs.AddSpacer(8)

        changelog_label = wx.StaticText(panel, label="更新日志:")
        changelog_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        changelog_label.SetForegroundColour(self.C_TEXT)
        vs.Add(changelog_label, 0, wx.LEFT | wx.RIGHT, 12)

        self.changelog_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        self.changelog_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.changelog_text.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.changelog_text.SetMinSize((-1, 200))
        vs.Add(self.changelog_text, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.update_btn = wx.Button(panel, label="立即更新", size=(120, 36), style=wx.BORDER_NONE)
        self.update_btn.SetBackgroundColour(wx.Colour(50, 80, 140))
        self.update_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.update_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.update_btn.Bind(wx.EVT_BUTTON, self.on_update)
        self.update_btn.Hide()
        btn_sizer.Add(self.update_btn, 0, wx.ALIGN_CENTER)

        close_btn = wx.Button(panel, label="关闭", size=(120, 36), style=wx.BORDER_NONE)
        close_btn.SetBackgroundColour(wx.Colour(160, 165, 170))
        close_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        close_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        btn_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.LEFT, 12)

        vs.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 12)

        panel.SetSizer(vs)

    def on_update(self, event):
        self.download_update()

    @staticmethod
    def check_gitee_update():
        try:
            url = "https://gitee.com/syf0910/mhsg-script-update/raw/master/version.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[错误] 检查更新失败: {e}")
            return None

    @staticmethod
    def get_current_version():
        try:
            if getattr(sys, 'frozen', False):
                base = sys._MEIPASS
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            version_file = os.path.join(base, "version.json")
            if os.path.exists(version_file):
                with open(version_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("version", "0.0.0")
        except Exception:
            pass
        return "0.0.0"

    def download_update(self):
        import urllib.request, urllib.parse, http.cookiejar, time, os, webbrowser, threading, sys

        try:
            import browser_cookie3
        except Exception:
            browser_cookie3 = None

        download_url = getattr(self, "download_url", None)
        if not download_url:
            return False

        referer = "https://gitee.com/syf0910/mhsg-script-update/releases"
        cj = http.cookiejar.CookieJar()
        if browser_cookie3:
            try:
                bcj = browser_cookie3.load(domain_name="gitee.com")
                cj = bcj
            except Exception:
                pass

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [
            ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"),
            ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
            ("Accept-Language", "zh-CN,zh;q=0.9"),
            ("Connection", "keep-alive"),
            ("Referer", referer),
            ("Upgrade-Insecure-Requests", "1"),
        ]

        state = {"downloaded": 0, "total": None, "done": False, "ok": False, "error": None, "dst": None, "speed_bps": 0.0}
        speed_window = []
        SPEED_WINDOW_SECONDS = 8.0
        SPEED_THRESHOLD_BPS = 10 * 1024

        def _worker():
            try:
                try:
                    opener.open(referer, timeout=15)
                except Exception:
                    pass
                resp = opener.open(download_url, timeout=40)
                code = getattr(resp, "status", resp.getcode())
                ctype = resp.getheader("Content-Type", "") or ""
                if code != 200 or "text/html" in ctype.lower():
                    state["error"] = "non-file"
                    state["done"] = True
                    return
                length = resp.getheader("Content-Length")
                try:
                    total = int(length) if length else None
                except Exception:
                    total = None
                state["total"] = total
                fname = os.path.basename(urllib.parse.unquote(urllib.parse.urlparse(download_url).path)) or f"脚本v{getattr(self,'latest_version','unknown')}.exe"
                dst = os.path.join(os.getcwd(), fname)
                state["dst"] = dst
                chunk_size = 256 * 1024
                last_time = time.time()
                last_downloaded = 0
                with open(dst + ".part", "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        state["downloaded"] += len(chunk)
                        now = time.time()
                        dt = now - last_time
                        if dt >= 0.5:
                            delta = state["downloaded"] - last_downloaded
                            inst_bps = delta / dt if dt > 0 else 0.0
                            speed_window.append((now, state["downloaded"]))
                            cutoff = now - SPEED_WINDOW_SECONDS
                            while len(speed_window) > 1 and speed_window[0][0] < cutoff:
                                speed_window.pop(0)
                            if len(speed_window) >= 2:
                                t0, d0 = speed_window[0]
                                tn, dn = speed_window[-1]
                                avg_bps = (dn - d0) / (tn - t0) if (tn - t0) > 0 else inst_bps
                            else:
                                avg_bps = inst_bps
                            state["speed_bps"] = avg_bps
                            last_time = now
                            last_downloaded = state["downloaded"]
                try:
                    os.replace(dst + ".part", dst)
                except Exception:
                    try:
                        os.remove(dst)
                    except Exception:
                        pass
                    os.rename(dst + ".part", dst)
                state["ok"] = True
            except Exception as e:
                state["error"] = str(e)
            finally:
                state["done"] = True

        th = threading.Thread(target=_worker, daemon=True)
        th.start()

        use_wx = False
        try:
            import wx
            use_wx = True
        except Exception:
            use_wx = False

        progress_dialog = None
        try:
            if use_wx and hasattr(self, "__class__"):
                try:
                    progress_dialog = wx.ProgressDialog("下载更新", "正在下载...", maximum=100, parent=getattr(self, "GetParent", lambda: None)(), style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT)
                except Exception:
                    progress_dialog = None

            while not state["done"]:
                dl = state["downloaded"]
                total = state["total"]
                dl_mb = dl / (1024.0 * 1024.0)
                total_mb = (total / (1024.0 * 1024.0)) if total else None
                pct = int((dl * 100 / total) if total and total > 0 else 0)
                if total_mb:
                    display = f"{pct}%({dl_mb:.2f}MB/{total_mb:.2f}MB)"
                else:
                    display = "资源加载中..."
                if progress_dialog:
                    cont, _ = progress_dialog.Update(pct, display)
                    if not cont:
                        try:
                            progress_dialog.Destroy()
                        except Exception:
                            pass
                        try:
                            webbrowser.open(download_url)
                        except Exception:
                            pass
                        return False
                time.sleep(0.12)

            final_dl_mb = state["downloaded"] / (1024.0 * 1024.0)
            final_total_mb = (state["total"] / (1024.0 * 1024.0)) if state["total"] else final_dl_mb
            final_pct = int((state["downloaded"] * 100 / state["total"]) if state["total"] and state["total"] > 0 else 100)
            if progress_dialog:
                try:
                    progress_dialog.Update(final_pct)
                except Exception:
                    pass
                try:
                    progress_dialog.Destroy()
                except Exception:
                    pass

            if not state["ok"]:
                try:
                    webbrowser.open(download_url)
                except Exception:
                    pass
                return False

            limited = False
            if state.get("speed_bps", 0.0) < SPEED_THRESHOLD_BPS:
                try:
                    total_bytes = state["total"] or state["downloaded"]
                    if total_bytes > 200 * 1024:
                        limited = True
                except Exception:
                    limited = False

            if use_wx:
                try:
                    dst = state.get("dst") or os.path.basename(urllib.parse.unquote(urllib.parse.urlparse(download_url).path))
                    msg = f"下载完成：{dst}"
                    if limited:
                        msg += "\n注意：下载速率较低，可能被限速。"
                    wx.CallAfter(lambda: wx.MessageBox(msg, "下载完成", wx.OK | wx.ICON_INFORMATION))
                except Exception:
                    pass
            return True
        finally:
            try:
                th.join(timeout=0.1)
            except Exception:
                pass


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()