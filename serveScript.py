import random
import time
import os
import sys
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

# 打包命令：pyinstaller -F -w --add-data "serveAssets;serveAssets" --icon=serveAssets\images\script.ico .\serveScript.py
# pyinstaller serveScript.spec
condition = threading.Condition()


class ResXy:
	def __init__(resInit, x, y):
		resInit.x = x
		resInit.y = y


def sort_array_by_second_value(arr, order):
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
		return int(item.split(',')[1])

	# 使用字典去除第二个值重复的项
	seen = {}
	unique_arr = []
	for item in arr:
		second_value = key_func(item)
		if second_value not in seen:
			seen[second_value] = True
			unique_arr.append(item)
	# 根据order参数决定排序顺序
	reverse_order = (order == 1)

	# 使用sorted函数进行排序
	sorted_arr = sorted(arr, key=key_func, reverse=reverse_order)
	return sorted_arr


class MyThread(threading.Thread):
	def __init__(self, scriptName):
		super().__init__()
		self.userData = [
			{'user_name': 'author', 'user_mac': ["50-9A-4C-C9-FE-BA", "00-E0-4C-68-11-80"], 'end_time': '2029-12-30 23:59:00'},
			{'user_name': '无情', 'user_mac': ['EE-2E-98-CC-6B-CB', '80-B6-55-70-F7-2F', '00-E2-69-6A-22-81'], 'end_time': '2025-3-10 23:59:00'},
			{'user_name': '不知秋雨寒', 'user_mac': ["E4-60-17-15-B4-73", "BC-EC-A0-28-FA-5C"], 'end_time': '2199-12-30 23:59:00'},
			{'user_name': '三千梨树', 'user_mac': ["08-8F-C3-75-B5-7A", "14-75-5B-98-DE-89"], 'end_time': '2199-12-30 23:59:00'},
			{'user_name': '欧阳慕青', 'user_mac': ["98-5F-41-8E-78-DB", '24-6A-0E-D2-83-BF'], 'end_time': '2025-2-5 23:59:00'},
			{'user_name': '天蓬元帅', 'user_mac': ["D0-65-78-10-5A-46"], 'end_time': '2024-12-29 23:59:00'},
			{'user_name': '折纸寄相思', 'user_mac': ["00-E0-4C-57-BD-CF"], 'end_time': '2025-2-5 23:59:00'},
			{'user_name': '敢为天下先', 'user_mac': ["B0-25-AA-26-64-03"], 'end_time': '2025-1-20 23:59:00'},
			{'user_name': '山竹', 'user_mac': ["7C-21-4A-48-36-7D"], 'end_time': '2025-1-10 23:59:00'},
			{'user_name': 'ice', 'user_mac': ["90-6F-18-07-B5-30"], 'end_time': '2025-1-4 23:59:00'},
			{'user_name': '尔康', 'user_mac': ["E8-9C-25-77-AC-2D"], 'end_time': '2025-1-12 23:59:00'},
			{'user_name': '翩翩少年', 'user_mac': ["3C-97-0E-FE-4B-B6", "2C-D0-5A-E0-A9-B0"], 'end_time': '2025-1-4 23:59:00'},
			{'user_name': '玄灯', 'user_mac': ["54-EE-75-C5-2C-25"], 'end_time': '2025-1-4 23:59:00'},
			{'user_name': '赵公子', 'user_mac': ["DC-85-DE-F7-ED-30"], 'end_time': '2025-1-5 23:59:00'},
		]
		try:
			self.dm = CreateObject('dm.dmsoft')
		except:
			regPath = self.get_resource_path('serveAssets/plugins/RegDll.dll')
			dms = ctypes.windll.LoadLibrary(str(regPath))
			dmPath = self.get_resource_path('serveAssets/plugins/dm.dll')
			# 构建 regsvr32 命令，添加 /s 参数以静默运行
			command = ['regsvr32', '/s', dmPath]
			# 执行命令
			subprocess.run(command, check=True, capture_output=True, text=True)
			dms.DllRegisterServer(dmPath, 0)
			self.dm = CreateObject('dm.dmsoft')
		self.win1_dm = None
		self.win2_dm = None
		self.frame = None
		self.zhanhunFloor = ''
		self.heifengFloor = ''
		# 创建子线程
		self.child_thread = threading.Thread(target=self.child_task)
		self.win1_thread = threading.Thread(target=self.find_and_bing_windows1)
		self.win2_thread = threading.Thread(target=self.find_and_bing_windows2)
		self.guanDuCount = 0
		self.mojingFloor = ''
		self.zhengdianFloor = ''
		self.teammate1_name = ''
		self.teammate2_name = ''
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
		self.clickFlag = False
		self.addBloudFlag = False
		self.stoped = False
		self.zdzdPath = self.get_resource_path("serveAssets/images/zdzd.bmp")
		self.Dx = 0
		self.Dy = 0
		self.downTalkLocation = None
		self.BisClick = False
		self.clickBTime = 0
		self.clickBX = 0
		self.clickBy = 0
		self.shengxiaoLocation = None
		self.mojingCount = 0
		self.gameLocation = None
		self.gameLeftLocation = None
		self.gameRightLocation = None
		self.gameBottomLocation = None
		self.dituLocation = None
		self.dituLeftLocation = None
		self.dituRightLocation = None
		self.dituCenterLocation = None
		self.talkLocation = None
		self.oneWeek = 604800
		self.threeDays = 259200
		self.monthDays = 2592000
		self.oneDay = 86400
		self.heifengCount = 0
		self.heifengWhileCount = 0
		self.richangSelection = []
		self.click_hwnd = 0
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		self.zhengdianFb = ["官渡", "魔镜", "黑风", "战魂+红+整点", "战魂+红+魔镜+整点"]
		self.hundianFlag = False
		self.win1_hwnd = 0
		self.win2_hwnd = 0
		self.zhengdian_flag = False
		self.clearMapFlag = False
		self.mac_address = ''
		self.user_name = ''
		self.end_time = ''
		self.overed = False

	def run(self):
		self.mac_address = self.get_mac_address()
		is_pass = self.is_user_valid()
		if not is_pass:
			self.show_error_message('未注册用户，请联系管理员注册!')
			return
		print(f'{self.user_name}，你好，你的脚本有效期为{self.end_time}!')
		self.zhanhunFloor = self.frame.zhanhunFloor
		self.mojingFloor = self.frame.mojingFloor
		self.teammate1_name = self.frame.teammate1_name
		self.teammate2_name = self.frame.teammate2_name
		self.zhengdianFloor = self.frame.zhengdianFloor
		self.heifengFloor = self.frame.heifengFloor
		self.richangSelection = self.frame.richangSelection
		self.heifengWhileCount = int(self.frame.heifengCount)
		# display = Display(visible=False, size=(1920, 1080))
		# display.start()
		isFindGame = self.findGame()
		if not isFindGame:
			return
		self.child_thread.start()
		self.win1_thread.start()
		self.win2_thread.start()
		self.beginFun()
		if self.scriptName == "官渡":
			self.guanduWhile()
		elif self.scriptName == "测试":
			self.clear_hide_map()
			# self.clearBag()
			self.go_in_ditu('地图许昌城', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '许昌', '驿站许昌', '驿站城西')
		# self.feiFb('副本曹操', True)
		# self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '驿站五指峡谷')
		elif self.scriptName == "嗜血战场(精英)":
			self.hongWhile()
		elif self.scriptName == "战魂楼(精英)":
			if not self.zhanhunFloor:
				self.zhanhunFloor = '26层'
				print('未选择层数，自动打26层')
			self.zhanhunWhile()
		elif self.scriptName == "整点":
			time.sleep(1)
			if self.zhengdianFloor == '牛+虎+兔+猴+羊':
				self.zhengDian()
			elif self.zhengdianFloor == '虎+牛+兔+猴+羊':
				self.new_zhengdian()
			elif self.zhengdianFloor == '虎+猴+羊':
				self.go_zhengdian()
			elif self.zhengdianFloor == '火焰+寒冰':
				self.go_zhengdian49()
		elif self.scriptName == "魔镜":
			self.mojingWhile()
		elif self.scriptName == "名将闯关":
			print('开始名将闯关')
			while True:
				has_mingjiang = self.mingjiangchuangguan()
				if not has_mingjiang:
					break
			time.sleep(1)
			self.scriptName = "官渡"
			self.feiFb('副本曹操', True)
			time.sleep(1)
			self.guanduWhile()
		elif self.scriptName == "战魂+红+整点":
			if not self.zhanhunFloor:
				self.zhanhunFloor = '26层'
				print('未选择层数，自动打26层')
			self.guanduAndHongAndZd()
		elif self.scriptName == "日常":
			self.richangeScript()
		elif self.scriptName == "五行":
			self.wuxingWhile()
		elif self.scriptName == "溶洞":
			self.rongdongWhile()
		elif self.scriptName == "炼丹":
			self.liandanWhile()
		elif self.scriptName == "龙岛":
			while True:
				if self.overed:
					return
				self.longdaoScript()
		elif self.scriptName == "黑风":
			self.heifengWhile()
		elif self.scriptName == "名将挑战赛":
			self.mingjiangtiaozhanWhile()
		elif self.scriptName == "战魂+红+魔镜+整点":
			if not self.zhanhunFloor:
				self.zhanhunFloor = '26层'
				print('未选择层数，自动打26层')
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
				if self.overed:
					return
				self.go_zhengdian49()
		elif self.scriptName == "49战魂":
			for i in range(6):
				self.zhanhun49Script()
		elif self.scriptName == "矿产":
			for i in range(self.heifengWhileCount):
				if self.overed:
					return
				self.kuangchanScript()
				if self.heifengCount == self.heifengWhileCount:
					break
			print(f"{self.heifengWhileCount}次矿产已完成,去官渡")
			self.guanduWhile()
		elif self.scriptName == "龙王令":
			print('将龙王令放到背包当前页')
			while True:
				if self.overed:
					return
				self.longwanglingScript()
		elif self.scriptName == "引魔符":
			print('将引魔符放到背包当前页')
			while True:
				if self.overed:
					return
				self.yinmofuScript()

	def is_user_valid(self):
		if self.overed:
			return
		current_time = datetime.now()
		for user in self.userData:
			if self.mac_address in user['user_mac']:
				expiration_time = datetime.strptime(user['end_time'], '%Y-%m-%d %H:%M:%S')
				if current_time > expiration_time:
					return False
				else:
					self.user_name = user['user_name']
					self.end_time = user['end_time']
					return True
		return False

	def findGame(self):
		ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
		self.click_hwnd = 0

		# 定义回调函数
		def enum_child_windows_callback(hwnd, lParam):
			window_text = self.dm.GetWindowText(hwnd)
			class_name = self.dm.GetClassName(hwnd)
			return True  # 返回 True 继续枚举

		# 将回调函数转换为 ctypes 函数指针
		enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)
		# 查找目标窗口句柄
		target_window_title = self.frame.game_name
		target_window_class = 'DUIWindow'  # 如果不知道类名，可以设为 None
		hwnds = self.dm.EnumWindow(0, target_window_title, target_window_class, 1 + 2)
		hwnds = hwnds.split(",")
		hwnd = 0
		for item in hwnds:
			if self.overed:
				return
			if item and self.dm.GetWindowTitle(int(item)) == target_window_title:
				hwnd = int(item)
				break
		if hwnd:
			# 使用 Windows API 的 EnumChildWindows
			user32 = ctypes.WinDLL('user32', use_last_error=True)

			# 获取屏幕分辨率
			# screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度

			# screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度
			if self.overed:
				return

			def enum_child_proc(hwnd, lParam):
				if self.overed:
					return
				class_name = self.dm.GetWindowClass(hwnd)
				child_rect = self.dm.GetWindowRect(hwnd)
				if child_rect != 0:
					left, top, right, bottom, isFind = child_rect
					# if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
					# 	self.click_hwnd = hwnd
					# 	return False
					if class_name == 'Chrome_RenderWidgetHostHWND':
						if left > 50:
							print('请5s内关闭小号列表！')
							time.sleep(5)

						self.click_hwnd = hwnd
						return False
				return True

			enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
			user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
		else:
			print('未找到游戏窗口，请检查输入的游戏名称是否正确！')
		# 绑定窗口到后台模式
		bind_result = self.dm.BindWindowEx(self.click_hwnd, "gdi", "windows3", "windows", '', 0)
		if bind_result == 1:
			print("窗口绑定成功")
		else:
			print("窗口绑定失败")
			return False
		location = self.dm.GetClientSize(self.click_hwnd)
		x, y, res = location
		if res == 1:
			print('已找到游戏画面')
		else:
			self.show_error_message("未检测到游戏页面")
			return False
		if self.overed:
			return
		self.dm.SetDict(0, self.get_resource_path("serveAssets/fonts/common.txt"))  # 字库文件路径
		current_rect = self.dm.GetWindowRect(self.click_hwnd)
		left, top, right, bottom, isFind = current_rect
		self.locationX = int((right - 900) / 2)
		xian_pos = self.dm.FindPicEx(left, top, right, bottom, self.get_resource_path("serveAssets/images/xian.bmp"), "", 0.8, 2)
		if not xian_pos:
			self.show_error_message('未找到游戏画面顶部，请重新启动脚本')
			return
		xian_pos = xian_pos.split(',')
		self.locationY = int(int(xian_pos[2]) - 2)
		self.locationWidth = 900 + self.locationX
		self.locationHeight = 580 + self.locationY
		self.locationRightTopX = self.locationX + int((900 * 0.8))
		self.locationRightTopY = self.locationY
		self.locationRightTopWidth = 900 + self.locationX
		self.locationRightTopHeight = self.locationY + int(580 * 0.2)
		self.gameLocation = (
			self.locationX,
			self.locationY,
			self.locationWidth,
			self.locationHeight,
		)
		self.gameLeftLocation = (
			self.locationX,
			int(self.locationY + (580 * 0.3)),
			int(self.locationX + (900 * 0.7)),
			self.locationHeight
		)
		self.gameRightLocation = (
			int(self.locationX + int(900 * 0.3)),
			int(self.locationY + (580 * 0.3)),
			self.locationWidth,
			self.locationHeight
		)
		self.gameBottomLocation = (
			self.locationX,
			int(self.locationY + (580 * 0.3)),
			self.locationWidth,
			self.locationHeight
		)
		self.dituLeftLocation = (
			self.locationRightTopX,
			self.locationRightTopY,
			int(self.locationRightTopX + (self.locationWidth * 0.1)),
			self.locationRightTopHeight,
		)
		self.dituCenterLocation = (
			int(self.locationRightTopX + (900 * 0.2 * 0.3)),
			self.locationRightTopY,
			int(self.locationRightTopX + (900 * 0.1) + (900 * 0.2 * 0.3)),
			self.locationRightTopHeight,
		)
		self.dituRightLocation = (
			int(self.locationRightTopX + (900 * 0.1)),
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		)
		self.talkLocation = (
			self.locationX,
			int(self.locationY + (580 * 0.5)),
			int(450 + self.locationX),
			self.locationHeight
		)
		self.dituLocation = (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		)
		return True

	def find_pic_or_str(self, find, region, find_dir):
		if self.overed:
			return
		types = 'serveAssets' in find
		if not types:
			res = self.find_str(find, region, find_dir)
		else:
			res = self.find_pic(find, region, find_dir)
		return res

	def find_pic_or_str_team1(self, find, region, find_dir):
		if self.overed:
			return
		types = 'serveAssets' in find
		if not types:
			res = self.find_str_team1(find, region, find_dir)
		else:
			res = self.find_pic_team1(find, region, find_dir)
		return res

	def find_pic_or_str_team2(self, find, region, find_dir):
		if self.overed:
			return
		types = 'serveAssets' in find
		if not types:
			res = self.find_str_team2(find, region, find_dir)
		else:
			res = self.find_pic_team2(find, region, find_dir)
		return res

	# 找图方法z
	def find_pic(self, image_path, image_region, find_dir):
		if self.overed:
			return
		find_path = image_path
		# picSize = self.dm.GetPicSize(image_path)
		# picSize = picSize.split(',')
		# picW, picH = picSize[0], picSize[1]
		x, y, w, h = image_region
		pos = self.dm.FindPicEx(int(x), int(y), int(w), int(h), find_path, "", self.confidenceNum, find_dir)
		if not pos:
			return False
		pos = pos.split('|')
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
		pos_res = pos[0].split(',')
		pics = image_path.split('|')
		picSize = self.dm.GetPicSize(pics[int(pos_res[0])])
		picSize = picSize.split(',')
		picW, picH = picSize[0], picSize[1]
		posX = int(pos_res[1]) + (int(picW) * 0.5)
		posY = int(pos_res[2]) + (int(picH) * 0.5)
		res = ResXy(int(posX), int(posY))
		return res

	# 找字方法
	def find_str(self, text, region, find_dir):
		if self.overed:
			return
		x, y, w, h = region
		find_str_result = self.dm.FindStrFastE(int(x), int(y), int(w), int(h), text, self.color_format, self.confidenceNum)
		find_str_result = find_str_result.split('|')
		if int(find_str_result[0]) < 0:
			return False
		else:
			pos_res = None
			if len(find_str_result) == 3:
				pos_res = find_str_result
			elif len(find_str_result) > 3:
				if int(find_str_result[1]) < int(find_str_result[4]) and find_dir in [0, 1]:
					pos_res = find_str_result[:3]
				else:
					pos_res = find_str_result[3:6]
			posX = pos_res[1]
			posY = pos_res[2]
			res = ResXy(int(posX), int(posY))
			return res

	# 找图方法z
	def find_pic_team1(self, image_path, image_region, find_dir):
		if self.overed:
			return
		find_path = image_path
		# picSize = self.dm.GetPicSize(image_path)
		# picSize = picSize.split(',')
		# picW, picH = picSize[0], picSize[1]
		x, y, w, h = image_region
		pos = self.win1_dm.FindPicEx(int(x), int(y), int(w), int(h), find_path, "", self.confidenceNum, find_dir)
		if not pos:
			return False
		pos = pos.split('|')
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
		pos_res = pos[0].split(',')
		pics = image_path.split('|')
		picSize = self.win1_dm.GetPicSize(pics[int(pos_res[0])])
		picSize = picSize.split(',')
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
		find_str_result = self.win1_dm.FindStrFastE(int(x), int(y), int(w), int(h), text, self.color_format, self.confidenceNum)
		find_str_result = find_str_result.split('|')
		if int(find_str_result[0]) < 0:
			return False
		else:
			pos_res = None
			if len(find_str_result) == 3:
				pos_res = find_str_result
			elif len(find_str_result) > 3:
				if int(find_str_result[1]) < int(find_str_result[4]) and find_dir in [0, 1]:
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
		pos = self.win2_dm.FindPicEx(int(x), int(y), int(w), int(h), find_path, "", self.confidenceNum, find_dir)
		if not pos:
			return False
		pos = pos.split('|')
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
		pos_res = pos[0].split(',')
		pics = image_path.split('|')
		picSize = self.win2_dm.GetPicSize(pics[int(pos_res[0])])
		picSize = picSize.split(',')
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
		find_str_result = self.win2_dm.FindStrFastE(int(x), int(y), int(w), int(h), text, self.color_format, self.confidenceNum)
		find_str_result = find_str_result.split('|')
		if int(find_str_result[0]) < 0:
			return False
		else:
			pos_res = None
			if len(find_str_result) == 3:
				pos_res = find_str_result
			elif len(find_str_result) > 3:
				if int(find_str_result[1]) < int(find_str_result[4]) and find_dir in [0, 1]:
					pos_res = find_str_result[:3]
				else:
					pos_res = find_str_result[3:6]
			posX = pos_res[1]
			posY = pos_res[2]
			res = ResXy(int(posX), int(posY))
			return res

	# 图中找图
	def fing_fei_in_image_or_str(self, base, base_region, fei_region, fei_image):
		if self.overed:
			return
		base_pos = self.find_pic_or_str(base, base_region, 0)
		if not base_pos:
			return False
		x, y, w, h = fei_region
		fei_pox = self.dm.FindPicEx(int(base_pos.x - x), int(base_pos.y - y), int(base_pos.x + w), int(base_pos.y + h), fei_image, "", 0.8, 0)
		if not fei_pox or fei_pox is None:
			return False
		res_pos = fei_pox.split('|')
		res_pos = res_pos[0].split(',')
		pics = fei_image.split('|')
		picSize = self.dm.GetPicSize(pics[int(res_pos[0])])
		picSize = picSize.split(',')
		picW, picH = picSize[0], picSize[1]
		posX = int(res_pos[1]) + (int(picW) * 0.5)
		posY = int(res_pos[2]) + (int(picH) * 0.5)
		res = ResXy(int(posX), int(posY))
		return res

	def child_task(self):
		while True:
			if self.overed:
				return
			# self.click_image(self.get_resource_path("serveAssets/images/guandu/dialog.bmp"), self.confidenceNum, self.gameBottomLocation)
			# self.click_image(self.get_resource_path("serveAssets/images/guandu/dialog1.bmp"), self.confidenceNum, self.gameBottomLocation)
			# self.click_image(self.get_resource_path("serveAssets/images/dialog3.bmp"), self.confidenceNum, self.gameBottomLocation)
			# self.click_image(self.get_resource_path("serveAssets/images/fubenzudui.bmp"), self.confidenceNum, self.gameBottomLocation)
			# 关闭右边
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
			# 点击取消
			if self.find_pic_or_str(f"{self.get_resource_path('serveAssets/images/jingji1.bmp')}|{self.get_resource_path('serveAssets/images/nohasfei.bmp')}", self.gameBottomLocation, 0):
				self.click_image(
					self.get_resource_path("serveAssets/images/closeJJ.bmp"),
					self.confidenceNum,
					self.gameBottomLocation,
				)
			# 点自动
			if self.scriptName == "官渡" or self.scriptName == "魔镜" or self.scriptName == "黑风" or self.scriptName == "矿产":
				self.click_image(
					self.get_resource_path("serveAssets/images/zidong.bmp"),
					self.confidenceNum,
					self.gameBottomLocation, )
			time.sleep(0.5)

	# 绑定第一个窗口
	def find_and_bing_windows1(self):
		if not self.teammate1_name:
			return
		CoInitialize()
		self.win1_hwnd = 0
		self.win1_dm = CreateObject('dm.dmsoft')
		ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

		# 定义回调函数
		def enum_child_windows_callback(hwnd, lParam):
			window_text = self.win1_dm.GetWindowText(hwnd)
			class_name = self.win1_dm.GetClassName(hwnd)
			return True  # 返回 True 继续枚举

		# 将回调函数转换为 ctypes 函数指针
		enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)
		# 查找目标窗口句柄
		target_window_title = self.teammate1_name + ' | ' + self.frame.game_name
		target_window_class = 'DUIWindow'  # 如果不知道类名，可以设为 None
		hwnds = self.win1_dm.EnumWindow(0, target_window_title, target_window_class, 1 + 2)
		hwnds = hwnds.split(",")
		hwnd = 0
		for item in hwnds:
			if item and self.win1_dm.GetWindowTitle(int(item)) == target_window_title:
				hwnd = int(item)
				break
		if hwnd:
			# 使用 Windows API 的 EnumChildWindows
			user32 = ctypes.WinDLL('user32', use_last_error=True)
			# 获取屏幕分辨率
			screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
			screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度

			def enum_child_proc(hwnd, lParam):
				class_name = self.win1_dm.GetWindowClass(hwnd)
				child_rect = self.win1_dm.GetWindowRect(hwnd)
				if child_rect != 0:
					left, top, right, bottom, isFind = child_rect
					# if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
					# 	self.win1_hwnd = hwnd
					# 	return False
					if class_name == 'Chrome_RenderWidgetHostHWND':
						self.win1_hwnd = hwnd
						return False
				return True

			enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
			user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
		else:
			self.show_error_message('未找到游戏窗口，请检查输入的队友1名称是否正确！')
		# 绑定窗口到后台模式
		bind_result = self.win1_dm.BindWindowEx(self.win1_hwnd, "gdi", "windows3", "windows", '', 0)
		if bind_result != 1:
			self.show_error_message('队友1绑定失败')
			return False
		self.win1_dm.SetDict(0, self.get_resource_path("serveAssets/fonts/team1.txt"))
		time.sleep(0.5)
		duiwu_pos = self.waitFor_team1('队伍', self.talkLocation, 3)
		if duiwu_pos:
			self.win1_dm.MoveTo(duiwu_pos.x, duiwu_pos.y)
			time.sleep(0.01)
			self.win1_dm.LeftClick()
			time.sleep(0.5)
			self.win1_dm.MoveTo(duiwu_pos.x, int(duiwu_pos.y + 28))
			time.sleep(0.01)
			self.win1_dm.LeftClick()
			time.sleep(0.3)
			self.win1_dm.KeyPressChar('1')
			time.sleep(1)
			self.win1_dm.KeyPressChar('enter')
		time.sleep(0.5)
		self.win1_dm.KeyPressChar('d')
		while True:
			if self.overed:
				return
			if self.clickFlag:
				self.clearBag_team1()
			if self.addBloudFlag:
				self.addBloud_team1()
			if self.clearMapFlag:
				self.clear_hide_map_team1()
			time.sleep(1)

	# 绑定第二个窗口
	def find_and_bing_windows2(self):
		if not self.teammate2_name:
			return
		CoInitialize()
		self.win2_hwnd = 0
		self.win2_dm = CreateObject('dm.dmsoft')
		ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

		# 定义回调函数
		def enum_child_windows_callback(hwnd, lParam):
			window_text = self.win2_dm.GetWindowText(hwnd)
			class_name = self.win2_dm.GetClassName(hwnd)
			return True  # 返回 True 继续枚举

		# 将回调函数转换为 ctypes 函数指针
		enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)
		# 查找目标窗口句柄
		target_window_title = self.teammate2_name + ' | ' + self.frame.game_name
		target_window_class = 'DUIWindow'  # 如果不知道类名，可以设为 None
		hwnds = self.win2_dm.EnumWindow(0, target_window_title, target_window_class, 1 + 2)
		hwnds = hwnds.split(",")
		hwnd = 0
		for item in hwnds:
			if item and self.win2_dm.GetWindowTitle(int(item)) == target_window_title:
				hwnd = int(item)
				break
		if hwnd:
			# 使用 Windows API 的 EnumChildWindows
			user32 = ctypes.WinDLL('user32', use_last_error=True)

			# 获取屏幕分辨率
			# screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
			# screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度
			def enum_child_proc(hwnd, lParam):
				class_name = self.win2_dm.GetWindowClass(hwnd)
				child_rect = self.win2_dm.GetWindowRect(hwnd)
				if child_rect != 0:
					left, top, right, bottom, isFind = child_rect
					# if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
					# 	self.win2_hwnd = hwnd
					# 	return False
					if class_name == 'Chrome_RenderWidgetHostHWND':
						self.win2_hwnd = hwnd
						return False
				return True

			enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
			user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
		else:
			self.show_error_message('未找到游戏窗口，请检查输入的队友2名称是否正确！')
		# 绑定窗口到后台模式
		bind_result = self.win2_dm.BindWindowEx(self.win2_hwnd, "gdi", "windows3", "windows", '', 0)
		if bind_result != 1:
			self.show_error_message('队友2绑定失败')
			return False
		self.win2_dm.SetDict(0, self.get_resource_path("serveAssets/fonts/team2.txt"))
		time.sleep(0.5)
		duiwu_pos = self.waitFor_team2('队伍', self.talkLocation, 3)
		if duiwu_pos:
			self.win2_dm.MoveTo(duiwu_pos.x, duiwu_pos.y)
			time.sleep(0.01)
			self.win2_dm.LeftClick()
			time.sleep(0.5)
			self.win2_dm.MoveTo(duiwu_pos.x, int(duiwu_pos.y + 28))
			time.sleep(0.01)
			self.win2_dm.LeftClick()
			time.sleep(0.3)
			self.win2_dm.KeyPressChar('1')
			time.sleep(1)
			self.win2_dm.KeyPressChar('enter')
		time.sleep(0.5)
		self.win2_dm.KeyPressChar('d')
		while True:
			if self.overed:
				return
			time.sleep(1)
			if self.clickFlag:
				self.clearBag_team2()
			if self.addBloudFlag:
				self.addBloud_team2()
			if self.clearMapFlag:
				self.clear_hide_map_team2()

	def addBloud(self):
		if self.overed:
			return
		self.confidenceNum = 0.8
		self.addBloudFlag = True
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		self.addBloudFlag = False
		self.confidenceNum = 0.9

	def addBloud_team1(self):
		if self.overed:
			return
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team1(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)

	def addBloud_team2(self):
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, self.gameLocation)
		time.sleep(0.3)
		self.click_image_team2(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, self.gameLocation)

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
			0
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
		time.sleep(0.2)
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
		dlg = wx.MessageDialog(None, message, "Error", style=wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		app.MainLoop()

	# 找当前的路径
	def get_resource_path(self, relative_path):
		if hasattr(sys, "_MEIPASS"):
			return os.path.join(sys._MEIPASS, relative_path)
		return os.path.join(os.path.abspath("."), relative_path)

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
		locationQueding = None
		while True:
			if locationQueding:
				break
			outX = 900 * 0.615 + self.locationX
			outY = 580 * 0.077 + self.locationY
			self.dm.MoveTo(int(outX), int(outY))
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(0.2)
			locationQueding = self.waitFor(
				self.get_resource_path("serveAssets/images/outFb.bmp"),
				self.gameLocation,
				3,
			)
		time.sleep(0.5)
		if locationQueding:
			self.dm.MoveTo(locationQueding.x, locationQueding.y)
			time.sleep(0.1)
			self.dm.LeftClick()
			huodetongbiLocation = self.waitFor('获得铜币', self.gameLeftLocation, 1)
			if huodetongbiLocation:
				self.dm.MoveTo(huodetongbiLocation.x, huodetongbiLocation.y)
				time.sleep(0.001)
				self.dm.LeftClick()
		else:
			return

	# 飞整点等到打完
	def feiZhengDian(self, fei_image, base_image, scroll_flag):
		# print(100)
		if self.overed:
			return
		time.sleep(0.001)
		self.dm.MoveTo(100, 100)
		time.sleep(0.001)
		findSmallFeiTime = time.time()
		# self.downTalkLocation = self.waitFor(
		# 	f"{self.get_resource_path('serveAssets/images/downTalk.bmp')}|{self.get_resource_path('serveAssets/images/downTalk1.bmp')}",
		# 	self.talkLocation,
		# 	5
		# )
		# if not self.downTalkLocation:
		# 	return f'没找到箭头'
		self.downTalkLocation = self.waitFor(
			f"{self.get_resource_path('serveAssets/images/upTalk.bmp')}|{self.get_resource_path('serveAssets/images/upTalk1.bmp')}",
			self.talkLocation,
			10
		)
		if not self.downTalkLocation:
			return f'没找到箭头'
		if not scroll_flag:
			time.sleep(0.8)
		while True:
			if self.overed:
				return
			if self.find_str(fei_image, self.talkLocation, 0):
				break
			if time.time() - findSmallFeiTime > 5:
				return f'没找到{fei_image}'
			# 去除获得铜币黑框
			self.click_image(
				'获得铜币',
				self.confidenceNum,
				self.gameLocation,
			)
			with condition:
				if self.stoped:
					condition.wait()
			if self.downTalkLocation:
				self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
				# self.dm.WheelUp()
				for i in range(8):
					time.sleep(0.001)
					self.dm.LeftClick()
				time.sleep(0.08)
		findShengXiaoTime = time.time()
		while True:
			if self.overed:
				return
			with condition:
				if self.stoped:
					condition.wait()
			if time.time() - findShengXiaoTime > 5:
				return '没找到飞鞋'
			shengxiaoLocation = self.fing_fei_in_image_or_str(
				fei_image,
				self.talkLocation,
				(70, 0, 230, 45),
				f"{self.get_resource_path('serveAssets/images/fei.bmp')}|{self.get_resource_path('serveAssets/images/fei3.bmp')}|{self.get_resource_path('serveAssets/images/fei2.bmp')}|{self.get_resource_path('serveAssets/images/fei1.bmp')}",
			)
			if shengxiaoLocation:
				break
		feiTime = time.time()
		while not self.find_str(
				base_image,
				self.dituLocation,
				2
		):
			if self.overed:
				return
			if time.time() - feiTime > 6:
				return f'没找到{base_image}'
			with condition:
				if self.stoped:
					condition.wait()
			if shengxiaoLocation:
				self.dm.MoveTo(shengxiaoLocation.x, shengxiaoLocation.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(1.7)
			else:
				return
		# 去除获得铜币黑框
		self.click_image(
			'获得铜币',
			self.confidenceNum,
			self.gameBottomLocation,
		)
		time.sleep(0.2)
		# 有人在打
		hasZhengDian = self.click_image(
			'打就打',
			self.confidenceNum,
			self.gameBottomLocation,
		)
		if not hasZhengDian:
			return f"飞过去没有{fei_image}"
		zhengdianHas = False
		queryTime = time.time()
		while hasZhengDian:
			if self.overed:
				return
			with condition:
				if self.stoped:
					condition.wait()
			if time.time() - queryTime > 5:
				zhengdianHas = False
				return f"点了没找到{fei_image}"
			if self.find_pic(
					self.get_resource_path("serveAssets/images/zdzd.bmp"),
					self.gameLocation, 0
			):
				zhengdianHas = True
				break
			yourendaLocation = self.find_str(
				'点击',
				self.gameBottomLocation, 0
			)
			if yourendaLocation:
				self.dm.MoveTo(yourendaLocation.x, yourendaLocation.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				zhengdianHas = False
				return f"有人打{fei_image}"
		self.waitFor(
			base_image,
			self.dituLocation,
		)
		return f"打完了{fei_image}"

	# 清包
	def clearBag_team1(self):
		if self.overed:
			return
		time.sleep(15)
		bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.win1_dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.5)
			self.win1_dm.LeftClick()
		chushou = self.waitFor_team1('一键出售', self.gameBottomLocation, 5)
		if chushou:
			self.win1_dm.MoveTo(chushou.x, chushou.y)
			time.sleep(0.5)
			self.win1_dm.LeftClick()
		else:
			bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win1_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win1_dm.LeftClick()
		time.sleep(0.5)
		zise = self.waitFor_team1('紫色', self.gameBottomLocation, 5)
		if zise:
			self.win1_dm.MoveTo(zise.x, zise.y)
			time.sleep(0.5)
			self.win1_dm.LeftClick()
		else:
			bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win1_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win1_dm.LeftClick()
		time.sleep(0.5)
		quedingchushou = self.waitFor_team1(self.get_resource_path("serveAssets/images/quedingchushou.bmp"), self.gameBottomLocation, 5)
		if quedingchushou:
			self.win1_dm.MoveTo(quedingchushou.x, quedingchushou.y)
			time.sleep(0.5)
			self.win1_dm.LeftClick()
		else:
			bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win1_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win1_dm.LeftClick()
		time.sleep(4)
		bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
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
		bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.win2_dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.5)
			self.win2_dm.LeftClick()
		chushou = self.waitFor_team2('一键出售', self.gameBottomLocation, 5)
		if chushou:
			self.win2_dm.MoveTo(chushou.x, chushou.y)
			time.sleep(0.5)
			self.win2_dm.LeftClick()
		else:
			bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win2_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win2_dm.LeftClick()
		time.sleep(0.5)
		zise = self.waitFor_team2('紫色', self.gameBottomLocation, 5)
		if zise:
			self.win2_dm.MoveTo(zise.x, zise.y)
			time.sleep(0.5)
			self.win2_dm.LeftClick()
		else:
			bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win2_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win2_dm.LeftClick()
		time.sleep(1)
		quedingchushou = self.waitFor_team2(self.get_resource_path("serveAssets/images/quedingchushou.bmp"), self.gameBottomLocation, 5)
		if quedingchushou:
			self.win2_dm.MoveTo(quedingchushou.x, quedingchushou.y)
			time.sleep(0.5)
			self.win2_dm.LeftClick()
		else:
			bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.win2_dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.win2_dm.LeftClick()
		time.sleep(2)
		self.clickFlag = False
		time.sleep(4)
		bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.win2_dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.5)
			self.win2_dm.LeftClick()

	# 清包
	def clearBag(self):
		if self.overed:
			return
		self.clickFlag = True
		bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.5)
			self.dm.LeftClick()
		chushou = self.waitFor('一键出售', self.gameBottomLocation, 5)
		if chushou:
			self.dm.MoveTo(chushou.x, chushou.y)
			time.sleep(0.5)
			self.dm.LeftClick()
		else:
			bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.dm.LeftClick()
			return
		time.sleep(1)
		zise = self.waitFor('紫色', self.gameBottomLocation, 5)
		if zise:
			self.dm.MoveTo(zise.x, zise.y)
			time.sleep(0.5)
			self.dm.LeftClick()
		else:
			bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.dm.LeftClick()
			return
		time.sleep(1)
		quedingchushou = self.waitFor(self.get_resource_path("serveAssets/images/quedingchushou.bmp"), self.gameBottomLocation, 5)
		if quedingchushou:
			self.dm.MoveTo(quedingchushou.x, quedingchushou.y)
			time.sleep(0.5)
			self.dm.LeftClick()
		else:
			bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
			if bagPos:
				self.dm.MoveTo(bagPos.x, bagPos.y)
				time.sleep(0.5)
				self.dm.LeftClick()
			return
		time.sleep(4)
		self.clickFlag = False
		bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.5)
			self.dm.LeftClick()

	# 清藏宝图
	def clear_hide_map(self):
		if self.overed:
			return
		self.clearMapFlag = True
		time.sleep(0.5)
		bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(0.5)
		x, y, w, h = self.gameBottomLocation
		yi_pos = self.dm.FindStrFastEx(x, y, w, h, '一', self.color_format, self.confidenceNum)
		bag_poss = yi_pos.split('|')
		self.confidenceNum = 0.8
		wu_pos = self.dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/wu.bmp'), "", self.confidenceNum, 0)
		shi_pos = self.dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/shi.bmp'), "", self.confidenceNum, 0)
		self.confidenceNum = 0.9
		if wu_pos:
			bag_poss.append(wu_pos)
		if shi_pos:
			bag_poss.append(shi_pos)
		bag_poss = self.sort_array_by_second_value(bag_poss, 2)
		for bag_pos in bag_poss:
			if self.overed:
				return
			if not bag_pos:
				continue
			new_bag_pos = bag_pos.split(',')
			self.dm.MoveTo(int(int(new_bag_pos[1]) + 3), int(int(new_bag_pos[2]) + 4))
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(1)
			while True:
				cangbaotu_pos = self.waitFor(f"{self.get_resource_path('serveAssets/images/cangbaotu.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu1.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu2.bmp')}", self.gameLocation, 2)
				if not cangbaotu_pos:
					break
				self.dm.MoveTo(cangbaotu_pos.x, cangbaotu_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				chushou_pos = self.waitFor('出售', self.gameLocation, 3)
				if not chushou_pos:
					break
				self.dm.MoveTo(chushou_pos.x, chushou_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.dm.LeftClick()
				time.sleep(3.5)

	# 清藏宝图1
	def clear_hide_map_team1(self):
		if self.overed:
			return
		time.sleep(0.5)
		bagPos = self.waitFor_team1(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.win1_dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.001)
			self.win1_dm.LeftClick()
		time.sleep(0.5)
		x, y, w, h = self.gameBottomLocation
		yi_pos = self.win1_dm.FindStrFastEx(x, y, w, h, '一', self.color_format, self.confidenceNum)
		bag_poss = yi_pos.split('|')
		self.confidenceNum = 0.8
		wu_pos = self.win1_dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/wu.bmp'), "", self.confidenceNum, 0)
		shi_pos = self.win1_dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/shi.bmp'), "", self.confidenceNum, 0)
		self.confidenceNum = 0.9
		if wu_pos:
			bag_poss.append(wu_pos)
		if shi_pos:
			bag_poss.append(shi_pos)
		bag_poss = self.sort_array_by_second_value(bag_poss, 2)
		for bag_pos in bag_poss:
			if not bag_pos:
				continue
			new_bag_pos = bag_pos.split(',')
			self.win1_dm.MoveTo(int(int(new_bag_pos[1]) + 3), int(int(new_bag_pos[2]) + 4))
			time.sleep(0.001)
			self.win1_dm.LeftClick()
			time.sleep(1)
			while True:
				cangbaotu_pos = self.waitFor_team1(f"{self.get_resource_path('serveAssets/images/cangbaotu.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu1.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu2.bmp')}", self.gameLocation, 2)
				if not cangbaotu_pos:
					break
				self.win1_dm.MoveTo(cangbaotu_pos.x, cangbaotu_pos.y)
				time.sleep(0.001)
				self.win1_dm.LeftClick()
				time.sleep(0.5)
				chushou_pos = self.waitFor_team1('出售', self.gameLocation, 3)
				if not chushou_pos:
					break
				self.win1_dm.MoveTo(chushou_pos.x, chushou_pos.y)
				time.sleep(0.001)
				self.win1_dm.LeftClick()
				time.sleep(0.5)
				self.win1_dm.LeftClick()
				time.sleep(3.5)

	# 清藏宝图2
	def clear_hide_map_team2(self):
		if self.overed:
			return
		self.clearMapFlag = True
		time.sleep(0.5)
		bagPos = self.waitFor_team2(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation, 5)
		if bagPos:
			self.win2_dm.MoveTo(bagPos.x, bagPos.y)
			time.sleep(0.001)
			self.win2_dm.LeftClick()
		time.sleep(0.5)
		x, y, w, h = self.gameBottomLocation
		yi_pos = self.win2_dm.FindStrFastEx(x, y, w, h, '一', self.color_format, self.confidenceNum)
		bag_poss = yi_pos.split('|')
		self.confidenceNum = 0.8
		wu_pos = self.win2_dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/wu.bmp'), "", self.confidenceNum, 0)
		shi_pos = self.win2_dm.FindPicEx(x, y, w, h, self.get_resource_path('serveAssets/images/shi.bmp'), "", self.confidenceNum, 0)
		self.confidenceNum = 0.9
		if wu_pos:
			bag_poss.append(wu_pos)
		if shi_pos:
			bag_poss.append(shi_pos)
		bag_poss = self.sort_array_by_second_value(bag_poss, 2)
		for bag_pos in bag_poss:
			if not bag_pos:
				continue
			new_bag_pos = bag_pos.split(',')
			self.win2_dm.MoveTo(int(int(new_bag_pos[1]) + 3), int(int(new_bag_pos[2]) + 4))
			time.sleep(0.001)
			self.win2_dm.LeftClick()
			time.sleep(1)
			while True:
				cangbaotu_pos = self.waitFor_team2(f"{self.get_resource_path('serveAssets/images/cangbaotu.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu1.bmp')}|{self.get_resource_path('serveAssets/images/cangbaotu2.bmp')}", self.gameLocation, 2)
				if not cangbaotu_pos:
					break
				self.win2_dm.MoveTo(cangbaotu_pos.x, cangbaotu_pos.y)
				time.sleep(0.001)
				self.win2_dm.LeftClick()
				time.sleep(0.5)
				chushou_pos = self.waitFor_team2('出售', self.gameLocation, 3)
				if not chushou_pos:
					break
				self.win2_dm.MoveTo(chushou_pos.x, chushou_pos.y)
				time.sleep(0.001)
				self.win2_dm.LeftClick()
				time.sleep(0.5)
				self.win2_dm.LeftClick()
				time.sleep(3.5)

	# V3整点
	def zhengDian(self):
		if self.overed:
			return
		print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
		with condition:
			if self.stoped:
				condition.wait()
		time.sleep(1.5)
		time.sleep(0.1)
		openTalkXY = self.waitFor(
			self.get_resource_path("serveAssets/images/openTalk.bmp"),
			self.talkLocation
		)
		if openTalkXY:
			self.dm.MoveTo(openTalkXY.x, openTalkXY.y)
			for i in range(4):
				time.sleep(0.2)
				self.dm.LeftClick()
		time.sleep(0.5)
		bangpaiTalkXY = self.waitFor(
			'帮派',
			self.talkLocation,
			5
		)
		if bangpaiTalkXY:
			self.dm.MoveTo(bangpaiTalkXY.x, bangpaiTalkXY.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(1.5)
		huodongTalkXY = self.waitFor(
			'活动',
			self.talkLocation,
			5
		)
		if huodongTalkXY:
			self.dm.MoveTo(huodongTalkXY.x, huodongTalkXY.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		self.set_dict()
		time.sleep(0.5)
		gc.collect()
		while True:
			if self.overed:
				return
			with condition:
				if self.stoped:
					condition.wait()
			current_time = time.localtime()
			if (current_time.tm_min == 0 and current_time.tm_sec == 1) or (
					current_time.tm_min == 0 and current_time.tm_sec == 2
			):
				break
			time.sleep(1)  # 每秒钟检查一次
		# 飞牛
		zhengdian_res = self.feiZhengDian(
			'牛生肖',
			'魔魂山',
			False,
		)
		print(zhengdian_res)
		# 飞老虎
		zhengdian_res = self.feiZhengDian(
			'虎生肖',
			'九黎族祭坛',
			True,
		)
		print(zhengdian_res)
		# if zhengdian_res in ['打完了虎生肖', '飞过去没有虎生肖', '点了没找到虎生肖', '有人打虎生肖']:
		# 	self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
		# 飞兔子
		zhengdian_res = self.feiZhengDian(
			'兔生肖',
			'徐州',
			True,
		)
		print(zhengdian_res)
		# 飞牛
		zhengdian_res = self.feiZhengDian(
			'牛生肖',
			'魔魂山',
			True,
		)
		print(zhengdian_res)
		if self.downTalkLocation:
			self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
			# self.dm.WheelUp()
			for i in range(10):
				time.sleep(0.001)
				self.dm.LeftClick()
			time.sleep(0.07)
			for i in range(10):
				time.sleep(0.001)
				self.dm.LeftClick()
			time.sleep(0.07)
			# self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
			# self.dm.WheelUp()
			# time.sleep(0.04)
			# self.dm.WheelUp()
			# time.sleep(0.04)
			# self.dm.WheelUp()
			# time.sleep(0.04)
			self.dm.MoveTo(int(self.downTalkLocation.x + 100), self.downTalkLocation.y)
			time.sleep(0.01)
		# 飞老虎
		zhengdian_res = self.feiZhengDian(
			'虎生肖',
			'九黎族祭坛',
			True,
		)
		print(zhengdian_res)
		# 飞兔子
		zhengdian_res = self.feiZhengDian(
			'兔生肖',
			'徐州',
			True,
		)
		print(zhengdian_res)
		# 飞猴子
		zhengdian_res = self.feiZhengDian(
			'猴生肖',
			'幽暗密林',
			False,
		)
		print(zhengdian_res)
		# if zhengdian_res in ['打完了猴生肖', '飞过去没有猴生肖', '点了没找到猴生肖', '有人打猴生肖']:
		# 	self.zhengdian_by_xiaolvren('幽暗密林', 0, int(845 + self.locationX), [int(43 + self.locationY)], 2)
		# 将进度条拖动到最底下
		dragBox = self.waitFor(
			self.get_resource_path("serveAssets/images/dragBox.bmp"),
			self.talkLocation,
		)
		if dragBox:
			self.dm.MoveTo(dragBox.x, dragBox.y)
			time.sleep(0.001)
			self.dm.LeftDown()
			time.sleep(0.001)
			self.dm.MoveTo(dragBox.x, int(dragBox.y + 230))
			time.sleep(0.001)
			self.dm.LeftUp()
			time.sleep(0.001)
			# if self.downTalkLocation is not None:
			# 	self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
			# 	for i in range(10):
			# 		time.sleep(0.001)
			# 		self.dm.LeftClick()
			# 	time.sleep(0.1)
			# 	self.dm.MoveTo(int(self.downTalkLocation.x + 100), self.downTalkLocation.y)
			# 	time.sleep(0.1)
			# 飞羊
			zhengdian_res = self.feiZhengDian(
				'羊生肖',
				'魔谷西',
				True,
			)
			print(zhengdian_res)
			# if zhengdian_res in ['打完了羊生肖', '飞过去没有羊生肖', '点了没找到羊生肖', '有人打羊生肖']:
			# 	self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
			# 飞猴子
			zhengdian_res = self.feiZhengDian(
				'猴生肖',
				'幽暗密林',
				False,
			)
			print(zhengdian_res)
			if self.downTalkLocation:
				self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
				# self.dm.WheelUp()
				for i in range(10):
					time.sleep(0.001)
					self.dm.LeftClick()
				time.sleep(0.07)
				for i in range(10):
					time.sleep(0.001)
					self.dm.LeftClick()
				time.sleep(0.07)
			# if self.downTalkLocation is not None:
			# 	self.dm.MoveTo(self.downTalkLocation.x, self.downTalkLocation.y)
			# 	self.dm.WheelUp()
			# 	time.sleep(0.04)
			# 	self.dm.WheelUp()
			# 	time.sleep(0.04)
			# 	self.dm.WheelUp()
			# 	time.sleep(0.04)
			# 	self.dm.MoveTo(int(self.downTalkLocation.x + 100), self.downTalkLocation.y)
			# 	time.sleep(0.01)
			# 飞羊
			zhengdian_res = self.feiZhengDian(
				'羊生肖',
				'魔谷西',
				True,
			)
			print(zhengdian_res)
			if zhengdian_res in ['打完了羊', '飞过去没有羊', '点了没找到羊', '有人打羊']:
				self.zhengdian_by_xiaolvren('魔谷西', 2, 857, [50, 46], 1)
		closeTalkXY = self.waitFor(
			self.get_resource_path("serveAssets/images/closetalk.bmp"),
			self.talkLocation,
		)
		if closeTalkXY:
			self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
			for i in range(4):
				time.sleep(0.2)
				self.dm.LeftClick()
		time.sleep(0.5)
		self.zhengdian_flag = False
		gc.collect()
		if self.scriptName == "官渡":
			is_in_guandu = self.find_pic_or_str('官渡', self.dituLocation, 0)
			if not is_in_guandu:
				self.feiFb('副本曹操', True)
			is_in_guandu = self.waitFor('官渡', self.dituLocation, 5)
			if not is_in_guandu:
				self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站城西', '驿站许昌')
			time.sleep(1)
			self.guanduWhile()
		elif self.scriptName == "魔镜" or self.scriptName == "整点":
			findMojingshizhe = self.feiFb('副本魔镜使者', False)
			if findMojingshizhe:
				is_in_guandu = self.waitFor('城西', self.dituLocation, 5)
				if not is_in_guandu:
					self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
				time.sleep(1)
				self.mojingWhile()
			else:
				self.scriptName = "官渡"
				self.feiFb('副本曹操', True)
				is_in_guandu = self.waitFor('官渡', self.dituLocation, 5)
				if not is_in_guandu:
					self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站城西', '驿站许昌')
				self.guanduWhile()
		elif self.scriptName == "战魂+红+整点":
			time.sleep(1)
			self.feiFb('副本曹操', True)
			time.sleep(1)
			self.feiFb('副本挑战赛', True)
			self.guanduAndHongAndZd()
		elif self.scriptName == "战魂+红+魔镜+整点":
			time.sleep(1)
			self.feiFb('副本曹操', True)
			time.sleep(1)
			self.feiFb('副本挑战赛', True)
			time.sleep(10)
			self.mojingAndHongAndZd()
		elif self.scriptName == "黑风":
			time.sleep(1)
			self.feiFb('副本霸山虎', False)
			self.heifengWhile()

	# 牛虎兔
	def new_zhengdian1(self):
		if self.overed:
			return
		print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
		with condition:
			if self.stoped:
				condition.wait()
		self.set_dict()
		time.sleep(1.5)
		gc.collect()
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
		is_fei = self.go_in_ditu('地图牛', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '魔魂山', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('魔魂山', 0, 0, [], 2)
			is_in_bibotan = self.waitFor('魔魂山', self.dituLocation, 5)
			if is_in_bibotan:
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('魔魂山', 0, 0, [], 2)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图老虎', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '九黎族祭坛', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
			is_in_bibotan = self.waitFor('九黎族祭坛', self.dituLocation, 5)
			if is_in_bibotan:
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图徐州', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '徐州', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('徐州', 0, int(845 + self.locationX), [int(43 + self.locationY)], 2)
			is_in_bibotan = self.waitFor('徐州', self.dituLocation, 5)
			if is_in_bibotan:
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('徐州', 0, int(845 + self.locationX), [int(43 + self.locationY)], 2)
			time.sleep(0.5)
		# is_fei = self.go_in_ditu('地图幽暗密林', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '幽暗密林', '', '', True)
		# if is_fei:
		# 	self.zhengdian_by_xiaolvren('幽暗密林', 0, int(763 + self.locationX), [int(49 + self.locationY), int(53 + self.locationY)], 2)
		# 	is_in_bibotan = self.waitFor('幽暗密林', self.dituLocation, 5)
		# 	if is_in_bibotan:
		# 		time.sleep(0.5)
		# 		self.zhengdian_by_xiaolvren('幽暗密林', 0, int(763 + self.locationX), [int(49 + self.locationY), int(53 + self.locationY)], 2)
		# 	time.sleep(0.5)
		# is_fei = self.go_in_ditu('地图羊', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '魔谷西', '', '', True)
		# if is_fei:
		# 	self.zhengdian_by_xiaolvren('魔谷西', 2, int(857 + self.locationX), [int(45 + self.locationY), int(49 + self.locationY)], 1)
		# 	time.sleep(0.5)
		# 	is_in_bibotan = self.waitFor('魔谷西', self.dituLocation, 5)
		# 	if is_in_bibotan:
		# 		self.zhengdian_by_xiaolvren('魔谷西', 2, int(857 + self.locationX), [int(45 + self.locationY), int(49 + self.locationY)], 1)
		# 	time.sleep(0.5)
		time.sleep(0.5)
		self.zhengdian_flag = False
		gc.collect()
		if self.scriptName == "官渡":
			is_in_guandu = self.find_pic_or_str('官渡', self.dituLocation, 0)
			if not is_in_guandu:
				self.feiFb('副本曹操', True)
			is_in_guandu = self.waitFor('官渡', self.dituLocation, 5)
			if not is_in_guandu:
				self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站城西', '驿站许昌', True)
			time.sleep(1)
			self.guanduWhile()
		elif self.scriptName == "魔镜" or self.scriptName == "整点":
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '', True)
			time.sleep(1)
			self.mojingWhile()
		elif self.scriptName == "战魂+红+整点":
			time.sleep(1)
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西', True)
			time.sleep(2)
			self.guanduAndHongAndZd()
		elif self.scriptName == "战魂+红+魔镜+整点":
			time.sleep(1)
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西', True)
			time.sleep(2)
			self.mojingAndHongAndZd()
		elif self.scriptName == "黑风":
			time.sleep(1)
			self.feiFb('副本霸山虎', False)
			self.heifengWhile()

	# 虎牛兔猴羊
	def new_zhengdian(self):
		if self.overed:
			return
		print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
		with condition:
			if self.stoped:
				condition.wait()
		self.set_dict()
		time.sleep(0.5)
		gc.collect()
		time.sleep(0.5)
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
		is_fei = self.go_in_ditu('地图老虎', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '九黎族祭坛', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
			is_in_bibotan = self.waitFor('九黎族祭坛', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
				is_in_bibotan1 = self.waitFor('九黎族祭坛', self.dituLocation, 5)
				if is_in_bibotan1:
					self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
					self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图牛', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '魔魂山', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('魔魂山', 0, 0, [], 2)
			is_in_bibotan = self.waitFor('魔魂山', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('魔魂山', 0, 0, [], 2)
				is_in_bibotan1 = self.waitFor('魔魂山', self.dituLocation, 5)
				if is_in_bibotan1:
					self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
					self.zhengdian_by_xiaolvren('魔魂山', 0, 0, [], 2)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图徐州', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '徐州', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('徐州', 0, int(845 + self.locationX), [int(43 + self.locationY)], 2)
			is_in_bibotan = self.waitFor('徐州', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('徐州', 0, int(845 + self.locationX), [int(43 + self.locationY)], 1)
				is_in_bibotan = self.waitFor('徐州', self.dituLocation, 5)
				if is_in_bibotan:
					self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
					self.zhengdian_by_xiaolvren('徐州', 0, int(845 + self.locationX), [int(43 + self.locationY)], 1)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图幽暗密林', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '幽暗密林', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 1)
			is_in_bibotan = self.waitFor('幽暗密林', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 2)
				is_in_bibotan1 = self.waitFor('幽暗密林', self.dituLocation, 5)
				if is_in_bibotan1:
					self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
					self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 2)
			time.sleep(0.5)
		is_fei = self.go_in_ditu('地图羊', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '魔谷西', '', '', True)
		if is_fei:
			self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
			time.sleep(0.5)
			is_in_bibotan = self.waitFor('魔谷西', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
				is_in_bibotan = self.waitFor('魔谷西', self.dituLocation, 5)
				if is_in_bibotan:
					self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
					self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
			time.sleep(0.5)
		time.sleep(0.5)
		self.zhengdian_flag = False
		if self.scriptName == "官渡":
			is_in_guandu = self.find_pic_or_str('官渡', self.dituLocation, 0)
			if not is_in_guandu:
				is_fei = self.feiFb('副本曹操', True)
			is_in_guandu = self.waitFor('官渡', self.dituLocation, 5)
			if not is_in_guandu:
				self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站城西', '驿站许昌', True)
			time.sleep(1)
			self.guanduWhile()
		elif self.scriptName == "魔镜" or self.scriptName == "整点":
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '', True)
			time.sleep(1)
			self.mojingWhile()
		elif self.scriptName == "战魂+红+整点":
			time.sleep(1)
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西', True)
			time.sleep(2)
			self.guanduAndHongAndZd()
		elif self.scriptName == "战魂+红+魔镜+整点":
			time.sleep(1)
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西', True)
			time.sleep(2)
			self.mojingAndHongAndZd()
		elif self.scriptName == "黑风":
			time.sleep(1)
			self.feiFb('副本霸山虎', False)
			self.heifengWhile()

	# 跑整点120
	def go_zhengdian(self):
		if self.overed:
			return
		print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
		if self.scriptName == '官渡' or self.scriptName == "战魂+红+整点":
			self.go_in_ditu('地图老虎遗迹', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '九黎族遗迹', '驿站城西', '驿站襄阳')
		elif self.scriptName == '魔镜' or self.scriptName == "战魂+红+魔镜+整点" or self.scriptName == "整点":
			self.go_in_ditu('地图老虎遗迹', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '九黎族遗迹', '驿站襄阳', '驿站城西')
		self.set_dict()
		time.sleep(0.5)
		gc.collect()
		time.sleep(0.5)
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			current_time = time.localtime()
			if (current_time.tm_min == 59 and current_time.tm_sec == 55) or (
					current_time.tm_min == 59 and current_time.tm_sec == 56
			):
				break
			time.sleep(1)  # 每秒钟检查一次
		# 进祭坛
		self.findAndClickPic(
			'九黎族遗迹',
			'九黎族祭坛',
			'九黎族祭坛',
			self.dituLocation,
			'九黎族祭坛',
			self.dituLocation,
			'0.187,0.139'
		)
		# 打老虎
		time.sleep(1)
		self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
		is_in_bibotan = self.waitFor('九黎族祭坛', self.dituLocation, 5)
		if is_in_bibotan:
			self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(0.5)
			self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
			is_in_bibotan = self.waitFor('九黎族祭坛', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('九黎族祭坛', 0, 0, [], 1)
		time.sleep(0.5)
		# 回城
		self.dm.KeyPressChar('e')
		self.confidenceNum = 0.7
		huichengjuan_pos = self.waitFor(f"{self.get_resource_path('serveAssets/images/zhengdian/huichengjuan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huichengjuan1.bmp')}", self.gameLocation, 5)
		self.confidenceNum = 0.9
		if huichengjuan_pos:
			find_huicheng = self.press_keys_until_image_found(
				f"{self.get_resource_path('serveAssets/images/zhengdian/huichengjuan.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huichengjuan1.bmp')}",
				'襄阳城',
				self.gameLocation,
				self.dituLocation,
				'使用'
			)
			if find_huicheng:
				time.sleep(0.001)
				self.dm.KeyPressChar('e')
				time.sleep(0.5)
				# 0.08,0.108
				self.findAndClickPic(
					'襄阳城',
					'幽暗密林',
					'幽暗密林',
					self.dituLocation,
					'幽暗密林',
					self.dituLocation,
					'0.08,0.108'
				)
			else:
				self.go_in_ditu('地图幽暗密林', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '幽暗密林', '', '')
		else:
			self.go_in_ditu('地图幽暗密林', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '幽暗密林', '', '')
		self.waitFor('幽暗密林', self.dituLocation)
		# 打猴子
		time.sleep(1)
		# 763  50/54
		self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 2)
		time.sleep(0.5)
		is_in_bibotan = self.waitFor('幽暗密林', self.dituLocation, 5)
		if is_in_bibotan:
			self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(0.5)
			self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 2)
			is_in_bibotan = self.waitFor('幽暗密林', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('幽暗密林', 0, int(764 + self.locationX), [int(44 + self.locationY)], 2)
		time.sleep(0.5)
		# 去魔谷西
		self.go_in_ditu('地图羊', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '魔谷西', '', '')
		# 打羊
		time.sleep(1)
		# 856 46/50
		self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
		time.sleep(0.5)
		is_in_bibotan = self.waitFor('魔谷西', self.dituLocation, 5)
		if is_in_bibotan:
			self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(0.5)
			self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
			is_in_bibotan = self.waitFor('魔谷西', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('魔谷西', 2, int(858 + self.locationX), [int(40 + self.locationY)], 1)
		time.sleep(0.5)
		self.zhengdian_flag = False
		gc.collect()
		if self.scriptName == '官渡':
			# 回官渡
			self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站城西', '驿站许昌')
			time.sleep(1)
			self.guanduWhile()
		elif self.scriptName == '魔镜' or self.scriptName == '整点':
			# 回洛阳城西
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
			time.sleep(1)
			self.mojingWhile()
		elif self.scriptName == "战魂+红+整点":
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '驿站城西', '')
			time.sleep(1)
			self.guanduAndHongAndZd()
		elif self.scriptName == "战魂+红+魔镜+整点":
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '驿站城西', '')
			time.sleep(1)
			self.mojingAndHongAndZd()

	# 跑整点49
	def go_zhengdian49(self):
		if self.overed:
			return
		print(f"打{int(time.localtime().tm_hour) + 1}点的整点")
		time.sleep(1)
		# openTalkXY = self.waitFor(
		# 	self.get_resource_path("serveAssets/images/openTalk.bmp"),
		# 	self.talkLocation
		# )
		# if openTalkXY:
		# 	self.dm.MoveTo(openTalkXY.x, openTalkXY.y)
		# 	for i in range(4):
		# 		time.sleep(0.2)
		# 		self.dm.LeftClick()
		# bangpaiTalkXY = self.waitFor(
		# 	'帮派',
		# 	self.talkLocation,
		# )
		# if bangpaiTalkXY:
		# 	self.dm.MoveTo(bangpaiTalkXY.x, bangpaiTalkXY.y)
		# 	time.sleep(0.001)
		# 	self.dm.LeftClick()
		# huodongTalkXY = self.waitFor(
		# 	'活动',
		# 	self.talkLocation,
		# )
		# if huodongTalkXY:
		# 	self.dm.MoveTo(huodongTalkXY.x, huodongTalkXY.y)
		# 	time.sleep(0.001)
		# 	self.dm.LeftClick()
		# time.sleep(0.5)
		self.findAndClickPic(
			'城西',
			self.get_resource_path("serveAssets/images/zhengdian/luoyangyizhan.bmp"),
			self.get_resource_path("serveAssets/images/zhengdian/luoyangyizhan1.bmp"),
			self.gameLeftLocation,
			'驿站五指峡谷',
			self.gameBottomLocation,
			'0.158,0.139'
		)
		self.waitForAAndClickB1(
			'五指峡谷',
			'驿站五指峡谷',
			self.dituLocation, self.gameLeftLocation,
		)
		self.set_dict()
		time.sleep(0.5)
		gc.collect()
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
		self.findAndClickPic(
			'五指峡谷',
			'碧波潭',
			'碧波潭',
			self.dituLocation,
			'碧波潭',
			self.dituLocation,
			'0.011,0.108'
		)
		# 打火焰
		time.sleep(0.8)
		# 735 58/62
		self.zhengdian_by_xiaolvren('碧波潭', 2, int(737 + self.locationX), [int(52 + self.locationY)], 2)
		time.sleep(0.5)
		is_in_bibotan = self.waitFor('碧波潭', self.dituLocation, 5)
		if is_in_bibotan:
			self.dm.MoveTo(self.locationX + 790, self.locationY + 75)
			time.sleep(0.001)
			self.dm.LeftClick()
			time.sleep(0.5)
			self.zhengdian_by_xiaolvren('碧波潭', 2, int(737 + self.locationX), [int(52 + self.locationY)], 2)
			is_in_bibotan = self.waitFor('碧波潭', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.MoveTo(self.locationX + 830, self.locationY + 75)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.5)
				self.zhengdian_by_xiaolvren('碧波潭', 2, int(737 + self.locationX), [int(52 + self.locationY)], 2)
		time.sleep(0.5)
		# 飞寒冰
		is_fei = self.go_in_ditu('地图皇宫东院', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '皇宫东院', '', '', True)
		# self.feiZhengDian(
		# 	'寒冰',
		# 	'皇宫东院',
		# 	350,
		# )
		if is_fei:
			time.sleep(0.5)
			# 848  49/53
			self.zhengdian_by_xiaolvren('皇宫东院', 0, int(849 + self.locationX), [int(43 + self.locationY)], 2)
			is_in_bibotan = self.waitFor('皇宫东院', self.dituLocation, 5)
			if is_in_bibotan:
				self.dm.KeyDownChar('left')
				time.sleep(1.5)
				self.dm.KeyUpChar('left')
				time.sleep(0.3)
				self.zhengdian_by_xiaolvren('皇宫东院', 0, int(849 + self.locationX), [int(43 + self.locationY)], 2)
		# if closeTalkXY:
		# 	self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
		# 	for i in range(4):
		# 		time.sleep(0.2)
		# 		self.dm.LeftClick()
		time.sleep(0.5)
		self.zhengdian_flag = False
		gc.collect()
		self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
		time.sleep(1)
		if self.scriptName == '魔镜':
			self.mojingWhile()

	# 在地图通过小绿人打整点
	def zhengdian_by_xiaolvren(self, base_image, find_dir, npc_posx=0, npc_possy=[], order=1):
		if npc_possy is None:
			npc_possy = []
		if self.overed:
			return
		base_image_res = self.waitFor(base_image, self.dituLocation, 5)
		if not base_image_res:
			return f'不在{base_image}'
		x, y, w, h = self.dituLocation
		xiaolvren = self.get_resource_path("serveAssets/images/zhengdian/xiaolvren2.bmp")
		picSize = self.dm.GetPicSize(xiaolvren)
		picSize = picSize.split(',')
		picW, picH = picSize[0], picSize[1]
		xiaolvren_pos = self.dm.FindPicEx(int(x), int(y), int(w), int(h), self.get_resource_path("serveAssets/images/zhengdian/xiaolvren2.bmp"), '', 0.7, find_dir)
		if xiaolvren_pos:
			xiaolvren_pos = xiaolvren_pos.split('|')
			# print(xiaolvren_pos, 'xiaolvren_pos')
			xiaolvren_pos = self.sort_array_by_second_value(xiaolvren_pos, order)
			# print(xiaolvren_pos, 'xiaolvren_pos111')
			xiaolvren_pos_color = self.dm.GetColor(int(int(xiaolvren_pos[0].split(',')[1]) + int(int(picW) * 0.5)), int(int(xiaolvren_pos[0].split(',')[2]) + int(int(picH) * 0.5)))
			for item in xiaolvren_pos:
				if self.overed:
					return
				new_item = item.split(',')
				if npc_posx != 0 and int(new_item[1]) == npc_posx and int(new_item[2]) in npc_possy:
					continue
				item_x = int(new_item[1]) + int(int(picW) * 0.5)
				item_y = int(new_item[2]) + int(int(picH) * 0.5)
				hasZhengDian = False
				change_color_time = 0
				find_zhengdian_time = time.time()
				self.dm.MoveTo(item_x, item_y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.001)
				self.dm.MoveTo(int(item_x - 200), item_y)
				time.sleep(0.1)
				while True:
					if time.time() - find_zhengdian_time > 10:
						print('超时10s')
						break
					# if not self.find_str(base_image, self.dituLocation, 0):
					# 	break
					if change_color_time == 0 and self.dm.CmpColor(item_x, item_y, xiaolvren_pos_color, 0.7) == 1:
						change_color_time = time.time()
					time.sleep(0.01)
					self.confidenceNum = 0.8
					time.sleep(0.001)
					if self.find_pic(
							f"{self.get_resource_path('serveAssets/images/zhengdian/dianwei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/dianwei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/jixu2.bmp')}",
							self.gameBottomLocation, 0):
						print('npc')
						self.confidenceNum = 0.9
						break
					self.confidenceNum = 0.9
					time.sleep(0.01)
					if change_color_time > 0 and time.time() - change_color_time > 5:
						print('超时')
						break
					self.confidenceNum = 0.8
					time.sleep(0.6)
					if self.find_pic(
							f"{self.get_resource_path('serveAssets/images/zhengdian/da.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da4.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da5.bmp')}",
							self.gameBottomLocation, 0):
						time.sleep(0.001)
						if self.find_pic(
								f"{self.get_resource_path('serveAssets/images/zhengdian/long.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long4.bmp')}",
								self.gameBottomLocation, 0):
							print('龙')
							self.confidenceNum = 0.9
							break
						else:
							self.confidenceNum = 0.9
							hasZhengDian = True
							break
					self.confidenceNum = 0.9
					is_zhengdian = self.waitFor('打就打', self.gameBottomLocation, 0.6)
					if is_zhengdian:
						self.confidenceNum = 0.8
						time.sleep(0.001)
						if self.find_pic(
								f"{self.get_resource_path('serveAssets/images/zhengdian/long.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/long4.bmp')}",
								self.gameBottomLocation, 0):
							print('龙')
							self.confidenceNum = 0.9
							break
						else:
							self.confidenceNum = 0.9
							hasZhengDian = True
							break
					del is_zhengdian
				if hasZhengDian:
					print(f'{base_image}有整点')
					find_time = time.time()
					dajiuda_pos = None
					while True:
						dajiuda_pos = self.find_pic(
							f"{self.get_resource_path('serveAssets/images/zhengdian/da.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da3.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/da5.bmp')}",
							self.gameBottomLocation, 0)
						if dajiuda_pos:
							break
						dajiuda_pos = self.find_str('打就打', self.gameBottomLocation, 0)
						if dajiuda_pos:
							break
						time.sleep(0.3)
						if self.confidenceNum > 0.7:
							self.confidenceNum = self.confidenceNum - 0.1
						if time.time() - find_time > 4:
							print('没找到打就打')
							break
					self.confidenceNum = 0.9
					if dajiuda_pos:
						self.dm.MoveTo(int(dajiuda_pos.x + 10), int(dajiuda_pos.y + 3))
						time.sleep(0.001)
						self.dm.LeftClick()
						queryTime = time.time()
						while True:
							with condition:
								if self.stoped:
									condition.wait()
							if time.time() - queryTime > 5:
								zhengdianHas = False
								break
							if self.find_pic(
									self.get_resource_path("serveAssets/images/zdzd.bmp"),
									self.gameLocation, 0
							):
								zhengdianHas = True
								break
							yourendaLocation = self.find_str(
								'点击',
								self.gameBottomLocation, 0
							)
							if yourendaLocation:
								self.dm.MoveTo(yourendaLocation.x, yourendaLocation.y)
								time.sleep(0.001)
								self.dm.LeftClick()
								zhengdianHas = False
								break
						del dajiuda_pos
						if zhengdianHas:
							self.waitFor(base_image, self.dituLocation)
							time.sleep(0.1)
							if base_image == '九黎族祭坛':
								print('打完了一个虎')
							elif base_image == '幽暗密林':
								print('打完了一个猴')
							elif base_image == '魔谷西':
								print('打完了一个羊')
							elif base_image == '碧波潭':
								print('打完了一个火焰帝')
							elif base_image == '皇宫东院':
								print('打完了一个寒冰帝')
							elif base_image == '魔魂山':
								print('打完了一个牛')
							elif base_image == '徐州':
								print('打完了一个兔')
				else:
					print('没找到整点')
			del xiaolvren_pos

		else:
			return

	# 重新设置大漠跟字库
	def set_dict(self):
		time.sleep(0.5)
		self.dm.SetDict(0, self.get_resource_path("serveAssets/fonts/common.txt"))  # 字库文件路径
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
			return int(item.split(',')[1])

		# 根据order参数决定排序顺序
		reverse_order = (order == 1)

		# 使用sorted函数进行排序
		sorted_arr = sorted(arr, key=key_func, reverse=reverse_order)
		return sorted_arr

	# 跑图
	def go_in_ditu(self, find_address, address_pos_city, break_address, yizhan_name1, yizhan_name2, is_fei=False):
		if self.overed:
			return
		time.sleep(0.5)
		# self.dm.KeyPressChar('m')
		self.dm.MoveTo(int(self.locationX + 737), int(self.locationY + 115))
		time.sleep(0.05)
		self.dm.LeftClick()
		address_pos_city_pos = self.waitFor(address_pos_city, self.gameLocation, 3)
		if not address_pos_city_pos:
			time.sleep(0.1)
			self.dm.KeyPressChar('m')
			address_pos_city_pos = self.waitFor(address_pos_city, self.gameLocation, 3)
			if not address_pos_city_pos:
				return
		self.dm.MoveTo(address_pos_city_pos.x, address_pos_city_pos.y)
		time.sleep(0.001)
		self.dm.LeftClick()
		self.waitFor(find_address, self.gameLocation)
		if not is_fei:
			go_pos = self.fing_fei_in_image_or_str(
				find_address,
				self.gameLocation,
				(0, 5, 150, 20),
				f"{self.get_resource_path('serveAssets/images/zhengdian/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang3.bmp')}", )
			if go_pos:
				self.dm.MoveTo(go_pos.x, go_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(0.05)
				self.dm.LeftClick()
				time.sleep(0.5)
			query_time = time.time()
			yizhan_name1_flag = True
			yizhan_name2_flag = True
			while not self.find_pic_or_str(break_address, self.dituLocation, 0):
				if self.overed:
					return
				if time.time() - query_time > 80:
					time.sleep(0.3)
					self.dm.KeyPressChar('down')
					time.sleep(0.3)
					self.dm.KeyPressChar('down')
					time.sleep(0.3)
					self.dm.MoveTo(int(self.locationX + 737), int(self.locationY + 115))
					time.sleep(0.05)
					self.dm.LeftClick()
					address_pos_city_pos = self.waitFor(address_pos_city, self.gameLocation)
					self.dm.MoveTo(address_pos_city_pos.x, address_pos_city_pos.y)
					time.sleep(0.001)
					self.dm.LeftClick()
					self.waitFor(find_address, self.gameLocation)
					go_pos = self.fing_fei_in_image_or_str(find_address, self.gameLocation, (0, 5, 130, 20), f"{self.get_resource_path('serveAssets/images/zhengdian/qianwang.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/qianwang1.bmp')}", )
					if go_pos:
						self.dm.MoveTo(go_pos.x, go_pos.y)
						time.sleep(0.001)
						self.dm.LeftClick()
						time.sleep(0.05)
						self.dm.LeftClick()
						time.sleep(0.5)
					query_time = time.time()
				if yizhan_name1 and yizhan_name1_flag:
					self.confidenceNum = 0.8
					yizhan_name1_click = self.click_image(yizhan_name1, self.confidenceNum, self.gameBottomLocation)
					self.confidenceNum = 0.9
					if yizhan_name1_click:
						yizhan_name1_flag = False
						time.sleep(1)
				if yizhan_name2 and yizhan_name2_flag:
					self.confidenceNum = 0.8
					yizhan_name2_click = self.click_image(yizhan_name2, self.confidenceNum, self.gameBottomLocation)
					self.confidenceNum = 0.9
					if yizhan_name2_click:
						yizhan_name2_flag = False
						time.sleep(1)
		else:
			find_fei_time = time.time()
			while True:
				if time.time() - find_fei_time > 10:
					return False
				fei_pos = self.fing_fei_in_image_or_str(find_address, self.gameLocation, (0, 5, 180, 20),
				                                        f"{self.get_resource_path('serveAssets/images/zhengdian/fei.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei2.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/fei3.bmp')}", )
				if fei_pos:
					self.dm.MoveTo(fei_pos.x, fei_pos.y)
					time.sleep(0.05)
					self.dm.LeftClick()
					time.sleep(0.5)
					return True

	# 飞副本
	def feiFb(self, image_path, isJy):
		if self.overed:
			return
		# 打开副本
		time.sleep(1.5)
		# self.dm.KeyPressChar('z')
		self.dm.MoveTo(int(self.locationX + 612), int(self.locationY + 48))
		time.sleep(0.05)
		self.dm.LeftClick()
		is_find_jy = self.waitForTwo('精英', '精英1', self.gameLocation, self.gameLocation, 15)
		if not is_find_jy:
			print('没找到副本')
			return
		time.sleep(1)
		if isJy:
			self.click_image(
				'精英',
				self.confidenceNum,
				self.gameLocation,
			)
			self.click_image(
				'精英1',
				self.confidenceNum,
				self.gameLocation,
			)
			findPerTime = time.time()
			while True:
				if time.time() - findPerTime > 10:
					self.dm.KeyPressChar('z')
					return False
				if self.overed:
					return
				fei_pos = self.fing_fei_in_image_or_str(image_path, self.gameLocation, (0, 5, 120, 20), f"{self.get_resource_path('serveAssets/images/fubenfei.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei1.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei2.bmp')}")
				if fei_pos:
					break
			if fei_pos:
				self.dm.MoveTo(fei_pos.x, fei_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
		else:
			self.click_image(
				'普通',
				self.confidenceNum,
				self.gameLocation,
			)
			self.click_image(
				'普通1',
				self.confidenceNum,
				self.gameLocation,
			)
			time.sleep(0.5)
			self.dm.MoveTo(100, 100)
			downTalk = self.waitFor(
				f"{self.get_resource_path('serveAssets/images/downFb.bmp')}|{self.get_resource_path('serveAssets/images/downFb1.bmp')}",
				(
					self.locationX,
					self.locationY,
					int(self.locationX + 900 * 0.75),
					self.locationHeight,
				),
				10
			)
			if not downTalk:
				return
			while not self.find_str(image_path, self.gameLocation, 0):
				if self.overed:
					return
				if downTalk:
					self.dm.MoveTo(downTalk.x, downTalk.y)
					for i in range(4):
						time.sleep(0.001)
						self.dm.LeftClick()
					time.sleep(0.4)
			time.sleep(1)
			findPerTime = time.time()
			while True:
				if self.overed:
					return
				if time.time() - findPerTime > 10:
					return
				fei_pos = self.fing_fei_in_image_or_str(image_path, self.gameLocation, (0, 5, 120, 20), f"{self.get_resource_path('serveAssets/images/fubenfei.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei1.bmp')}|{self.get_resource_path('serveAssets/images/fubenfei2.bmp')}", )
				if fei_pos:
					break
			if fei_pos:
				self.dm.MoveTo(fei_pos.x, fei_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
		return True

	# 找图并且点击
	def click_image(self, image_path, image_confidence, image_region, find_dir=0):
		if self.overed:
			return
		image_locations = self.find_pic_or_str(image_path, image_region, find_dir)
		if image_locations:
			with condition:
				if self.stoped:
					condition.wait()
			self.dm.MoveTo(image_locations.x, image_locations.y)
			time.sleep(0.001)
			self.dm.LeftClick()
			return True
		else:
			return False

	def click_image_team1(self, image_path, image_confidence, image_region, find_dir=0):
		if self.overed:
			return
		image_locations = self.find_pic_or_str_team1(image_path, image_region, find_dir)
		if image_locations:
			with condition:
				if self.stoped:
					condition.wait()
			self.win1_dm.MoveTo(image_locations.x, image_locations.y)
			time.sleep(0.001)
			self.win1_dm.LeftClick()
			return True
		else:
			return False

	def click_image_team2(self, image_path, image_confidence, image_region, find_dir=0):
		if self.overed:
			return
		image_locations = self.find_pic_or_str_team2(image_path, image_region, find_dir)
		if image_locations:
			with condition:
				if self.stoped:
					condition.wait()
			self.win2_dm.MoveTo(image_locations.x, image_locations.y)
			time.sleep(0.001)
			self.win2_dm.LeftClick()
			return True
		else:
			return False

	# 找一样的字，点击最左边的图
	def click_image_with_min_x(self, image_path, image_region, image_path2, find_dir=0):
		if self.overed:
			return
		types = 'serveAssets' in image_path
		target = None
		if not types:
			target = self.find_str(image_path, image_region, find_dir)
			if target:
				target.x = target.x + 25
				target.y = target.y + 5
		else:
			target = self.find_pic(image_path, image_region, find_dir)
		if not target:
			return False
		yjian = 40 if not types else 20
		if self.zdzdPath == image_path2 or image_path2 == self.get_resource_path("serveAssets/images/zdzd111.bmp"):
			self.dm.MoveTo(target.x, int(target.y - yjian))
			time.sleep(0.001)
			self.dm.LeftClick()
			self.dm.MoveTo(target.x + 200, target.y + 200)
			time.sleep(0.5)
		else:
			self.dm.MoveTo(target.x, target.y)
			time.sleep(0.001)
			self.dm.LeftClick()
			self.dm.MoveTo(target.x + 200, target.y + 200)
			time.sleep(0.3)
		self.clickBTime = time.time()
		self.clickBX = target.x
		self.clickBy = target.y
		return True

	def click_image_with_min_x1(self, image_path, image_region, image_path2, find_dir=0):
		if self.overed:
			return
		types = 'serveAssets' in image_path
		target = None
		if not types:
			target = self.find_str(image_path, image_region, find_dir)
		else:
			target = self.find_pic(image_path, image_region, find_dir)
		if not target:
			return False
		target_x = target.x
		target_y = target.y
		if 'zdzd' in image_path2:
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
			if self.overed:
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
			time.sleep(0.1)
		return target

	# 等待图片出现
	def waitFor_team1(self, image_path, image_region, timeout=None):
		if self.overed:
			return
		start_time = time.time()
		while True:
			if self.overed:
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
			if self.overed:
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
	def waitForTwo(self, image1_path, image2_path, image_region1, image_region2=None, timeout=None, find_dir=1):
		if self.overed:
			return
		start_time = time.time()
		res = ""
		if image_region2 is None:
			image_region2 = image_region1
		while True:
			if self.overed:
				return
			with condition:
				if self.stoped:
					condition.wait()
			xy = self.find_pic_or_str(
				image1_path, image_region1, find_dir
			)
			if xy:
				res = "first"
				return res
			xy2 = self.find_pic_or_str(
				image2_path, image_region2, find_dir
			)
			if xy2:
				res = "second"
				return res
			if timeout is not None:
				if time.time() - start_time > timeout:
					return False
			time.sleep(0.2)

	# 等待图片1出现，一直点击图2
	def waitForAAndClickB1(
			self,
			find_text,
			image_pathB,
			find_region,
			image_regionB=None
	):
		if self.overed:
			return
		if image_regionB is None:
			image_regionB = self.gameLocation
		while not self.find_pic_or_str(find_text, find_region, 0):
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
			image_pathB2=None,
	):
		if self.overed:
			return
		if not image_regionB:
			image_regionB = self.gameLocation
		while not self.find_str(image_pathA, image_regionA, 0) or not self.find_str(image_pathA2, image_regionA, 0):
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
			clickB = self.click_image(
				image_pathB2,
				self.confidenceNum,
				image_regionB,
			)
			if clickB:
				time.sleep(0.5)
			time.sleep(0.1)

	# 使用道具
	def press_keys_until_image_found(self, image_path, image_path2, region1, region2, find_text):
		if self.overed:
			return
		self.confidenceNum = 0.8
		image_path_pos = self.waitFor(image_path, region1, 5)
		self.confidenceNum = 0.9
		if not image_path_pos:
			return False
		while True:
			if self.overed:
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
		d_pos = xy.split(',')
		d_pos[0] = (1000 - int(float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
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
	def findAndClickPic(self, A, B, B1, B2, C1, C2, D, E='', E2=None, E2DownTime=0.6):
		if self.overed:
			return
		self.mac_address = self.get_mac_address()
		is_pass = self.is_user_valid()
		if not is_pass:
			self.show_error_message('未注册用户，请联系管理员注册!')
			time.sleep(1000000)
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
			aIsOk = self.waitFor(
				A, self.dituLocation
			)
			if not aIsOk:
				self.show_error_message("未找到开始地点")
				return
			if time.localtime().tm_min == 58 and self.scriptName != '49整点' and not self.zhengdian_flag:
				if self.scriptName in ['官渡', '矿产']:
					time.sleep(1)
					self.clearBag()
					time.sleep(1)
				if self.zhengdianFloor == '牛+虎+兔+猴+羊' and self.scriptName in self.zhengdianFb:
					# 打整点
					self.zhengdian_flag = True
					self.outScript(A)
					time.sleep(2)
					self.zhengDian()
					return
				if self.zhengdianFloor in ['虎+牛+兔+猴+羊', '牛+虎+兔'] and self.scriptName in self.zhengdianFb:
					# 打整点
					self.zhengdian_flag = True
					self.outScript(A)
					time.sleep(2)
					if self.zhengdianFloor == '虎+牛+兔+猴+羊':
						self.new_zhengdian()
					else:
						self.new_zhengdian1()
					return
				elif self.zhengdianFloor == '虎+猴+羊' and self.scriptName in ['官渡', '魔镜', "战魂+红+整点", "战魂+红+魔镜+整点"]:
					# 打整点
					self.zhengdian_flag = True
					self.outScript(A)
					time.sleep(2)
					self.go_zhengdian()
					return
				elif self.zhengdianFloor == '火焰+寒冰' and self.scriptName == '魔镜':
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
			find_dir = 2 if E == 'left' else 0
			while not self.find_pic_or_str(C1, C2, find_dir):
				if self.overed:
					return
				with condition:
					if self.stoped:
						condition.wait()
				if time.time() - startTime > 10 and self.hundianFlag:
					self.click_image(self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"), self.confidenceNum, self.dituLocation)
				if time.time() - startTime > 22:
					if self.scriptName == "官渡":
						print("超过15s没找到目标,重新进入官渡")
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
				# 点击B
				# self.BisClick = self.click_image_with_min_x(
				# 	B,
				# 	B2,
				# 	C1,
				# )
				# self.BisClick = self.click_image_with_min_x(
				# 	B1,
				# 	B2,
				# 	C1,
				# )
				#   D找图片D点击‘
				if D and self.clickBTime == 0 and not self.find_pic_or_str(B, B2, 0) and not self.find_pic_or_str(B1, B2, 0):
					if self.overed:
						return
					with condition:
						if self.stoped:
							condition.wait()
					d_pos = D.split(',')
					d_pos[0] = (1000 - int(float(d_pos[0]) * 1000)) / 1000 * 900
					d_pos[1] = (int(float(d_pos[1]) * 1000)) / 1000 * 580
					self.dm.MoveToEx(int(int(d_pos[0]) + self.locationX), int(int(d_pos[1]) + self.locationY), 3, 2)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.5)
				if self.find_pic_or_str(C1, C2, find_dir):
					break
				while E != "" and not EIsDown and not self.find_pic_or_str(B, B2, find_dir) and not self.find_pic_or_str(B1, B2, find_dir):
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
				with condition:
					if self.stoped:
						condition.wait()
				if self.find_pic_or_str(C1, C2, find_dir):
					break
				# 点击B
				self.BisClick = self.click_image_with_min_x(
					B,
					B2,
					C1,
				)
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
		isInGuanDu = self.waitFor('官渡', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本曹操', True)
		# 进入官渡
		self.findAndClickPic(
			'官渡',
			self.get_resource_path("serveAssets/images/guandu/caocao1.bmp"),
			self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
			self.gameLocation,
			'进入',
			self.gameBottomLocation,
			'0.038,0.134'
		)
		with condition:
			if self.overed:
				return
			if self.stoped:
				condition.wait()
		if self.overed:
			return
		# 进入第一层
		self.waitForAAndClickB1(
			'曹操大帐',
			'进入',
			self.dituLocation, self.gameBottomLocation,
		)
		is_in_guandu = self.waitFor('曹操大帐', self.dituLocation, 5)
		if not is_in_guandu:
			self.outScript()
			time.sleep(1)
			return True
		with condition:
			if self.stoped:
				condition.wait()
		# 0.078,0.127
		self.findAndClickPic(
			'曹操大帐',
			'曹袁战场',
			'曹袁战场',
			self.dituLocation,
			'曹袁战场',
			self.dituLocation,
			'0.078,0.127'
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
		hbjLocations = ['0.141,0.124', '0.112,0.125', '0.086,0.125', '0.065,0.121']
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'曹袁战场',
			'河北军',
			f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.165,0.122'
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		for i in range(4):
			self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
			# f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
			self.findAndClickPic(
				'曹袁战场',
				'河北军',
				'河北军',
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				hbjLocations[i],
				"",
			)
			self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'曹袁战场',
			'河北军',
			f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.052,0.125'
		)
		if self.overed:
			return
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		# 颜良
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		# 0.091,0.118  f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}"
		self.findAndClickPic(
			'曹袁战场',
			self.get_resource_path('serveAssets/images/guandu/yanliang.bmp'),
			'官渡颜良',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd111.bmp"),
			self.gameBottomLocation,
			"0.097,0.124",
			"",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		with condition:
			if self.overed:
				return
			if self.stoped:
				condition.wait()
		# 文丑
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		# f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}"
		self.findAndClickPic(
			'曹袁战场',
			'官渡文丑',
			f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd111.bmp"),
			self.gameBottomLocation,
			"0.081,0.122",
			"",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		with condition:
			if self.overed:
				return
			if self.stoped:
				condition.wait()
		# 去大帐
		self.findAndClickPic(
			'曹袁战场',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.dituLocation,
			'知道了',
			self.gameLeftLocation,
			"0.192,0.129",
			"",
		)
		self.findAndClickPic(
			'曹操大帐',
			'知道了',
			'知道了',
			self.gameLeftLocation,
			'鸟巢粮仓',
			self.dituLocation,
			'',
			"",
		)
		# self.waitForAAndClickB1(
		# 	'曹操大帐',
		# 	self.get_resource_path("serveAssets/images/guandu/guandu1chuansongmen.bmp"),
		# 	self.dituLocation, self.dituLocation,
		# )
		# self.waitFor('曹操大帐', self.dituLocation)
		if self.overed:
			return
		with condition:
			if self.stoped:
				condition.wait()
		# 找到曹操进入乌巢
		# self.waitForAAndClickB1(
		# 	'知道了',
		# 	self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
		# 	self.gameLeftLocation, self.dituLocation,
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# self.waitForAAndClickB1(
		# 	'鸟巢粮仓',
		# 	'知道了',
		# 	self.dituLocation, self.gameLeftLocation,
		# )
		if self.overed:
			return
		with condition:
			if self.stoped:
				condition.wait()
		# 进入魂殿打魂
		# 0.161,0.106
		self.waitForAAndClickB1(
			'枯寂',
			self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# self.waitFor('枯寂', self.dituLocation)
		self.findAndClickPic(
			'枯寂',
			'文丑之魂',
			'文丑之魂',
			self.gameLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.167,0.103",
		)
		self.hundianFlag = True
		self.findAndClickPic(
			'枯寂',
			'鸟巢粮仓',
			'鸟巢粮仓',
			self.dituLocation,
			'鸟巢粮仓',
			self.dituLocation,
			"0.138,0.12"
		)
		if self.overed:
			return
		with condition:
			if self.stoped:
				condition.wait()
		# 打淳
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		# f"{self.get_resource_path('serveAssets/images/guandu/cyq1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq2.bmp')}",
		self.findAndClickPic(
			'鸟巢粮仓',
			f"{self.get_resource_path('serveAssets/images/guandu/cyq.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq3.bmp')}",
			'淳于琼',
			self.gameLeftLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"0.161,0.129",
			"",
		)
		self.hundianFlag = False
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		with condition:
			if self.stoped:
				condition.wait()
		if self.overed:
			return
		# 打袁绍
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'鸟巢粮仓',
			'官渡袁绍',
			f"{self.get_resource_path('serveAssets/images/guandu/yuanshao1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yuanshao2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"0.152,0.124",
			"",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		if self.overed:
			return
		with condition:
			if self.stoped:
				condition.wait()
		# 退出副本
		self.outScript('鸟巢粮仓')

	# 红脚本
	def hongScript(self):
		print("开始打红")
		with condition:
			if self.stoped:
				condition.wait()
		if self.overed:
			return
		# 进入红
		self.findAndClickPic(
			'虎牢关外',
			self.get_resource_path("serveAssets/images/hong/hongdianweiditu.bmp"),
			self.get_resource_path("serveAssets/images/hong/hongdianwei.bmp"),
			self.gameLocation,
			'嗜血战场',
			self.gameBottomLocation,
			"0.117,0.129"
		)
		self.waitForAAndClickB1(
			'军营',
			'嗜血战场',
			self.dituLocation, self.gameBottomLocation,
		)
		if self.overed:
			return
		isInHong = self.waitFor('军营', self.dituLocation, 8)
		if not isInHong:
			print('红没次数了')
			return False
		# 第一层
		if self.overed:
			return
		gonbin_poss = ['0.121,0.125', '0.064,0.125', '0.036,0.12']
		for i in range(3):
			if self.overed:
				return
			self.findAndClickPic(
				'军营',
				'弓兵',
				'弓兵',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				gonbin_poss[i],
			)

		# 进入军粮营
		self.findAndClickPic(
			'军营',
			'军粮营',
			'军粮营',
			self.dituLocation,
			'军粮营',
			self.dituLocation,
			'0.158,0.146',
			'',
			'down'
		)
		# 第二层
		huweibin_poss = ['0.144,0.124', '0.1,0.118', '0.035,0.124']
		for i in range(2):
			if self.overed:
				return
			self.findAndClickPic(
				'军粮营',
				'护卫兵',
				f"{self.get_resource_path('serveAssets/images/hong/huweibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huweibin2.bmp')}",
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				huweibin_poss[i],
			)
		self.findAndClickPic(
			'军粮营',
			'护粮将领',
			f"{self.get_resource_path('serveAssets/images/hong/huliangjianglin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huliangjianglin2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd111.bmp"),
			self.gameBottomLocation,
			huweibin_poss[2],
		)
		# 进入训兵营
		self.findAndClickPic(
			'军粮营',
			'训兵营',
			'训兵营',
			self.dituLocation,
			'训兵营',
			self.dituLocation,
			'0.015,0.127',
		)
		# self.waitForAAndClickB1(
		# 	'训兵营',
		# 	self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
		# 	self.dituLocation, self.dituRightLocation,
		# )
		# 第3层
		qibin_poss = ['0.136,0.112', '0.104,0.148', '0.06,0.124', '0.121,0.131']
		for i in range(3):
			self.findAndClickPic(
				'训兵营',
				'骑兵',
				f"{self.get_resource_path('serveAssets/images/hong/qibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/qibin2.bmp')}",
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				qibin_poss[i],
			)
		if self.overed:
			return
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'训兵营',
			'训兵将领',
			f"{self.get_resource_path('serveAssets/images/hong/shenjinxi1.bmp')}|{self.get_resource_path('serveAssets/images/hong/shenjinxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			qibin_poss[3],
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		# 进入军营
		self.findAndClickPic(
			'训兵营',
			'军营',
			'军营',
			self.dituLocation,
			'军营',
			self.dituLocation,
			"0.106,0.091",
		)
		if self.overed:
			return
		self.addBloud()
		time.sleep(0.5)
		# 进入帐篷
		self.waitForAAndClickB1(
			'帐篷',
			self.get_resource_path("serveAssets/images/hong/chuansongmen3.bmp"),
			self.dituLocation, self.dituCenterLocation,
		)
		# boss
		self.findAndClickPic(
			'帐篷',
			'控魂巫师',
			'控魂巫师',
			self.gameRightLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameRightLocation,
			"0.117,0.119",
		)
		# 退出副本
		self.outScript('帐篷', )
		return True

	#  战魂脚本
	def zhanhunScript(self):
		if self.overed:
			return
		print("开始战魂")
		isInGuanDu = self.waitFor('洛阳', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本挑战赛', True)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入战魂
		self.findAndClickPic(
			'洛阳',
			self.get_resource_path("serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/zhanhuntiaozhanditu.bmp"),
			self.gameBottomLocation,
			'战魂楼',
			self.gameBottomLocation,
			"0.067,0.132"
		)
		# 点击进入战魂
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/1.bmp"),
			'战魂楼',
			self.dituLocation, self.gameBottomLocation,
		)
		isInZhanhun = self.waitFor('战魂', self.dituLocation, 8)
		if not isInZhanhun:
			print('战魂没次数了')
			return False
		# 1
		self.findAndClickPic(
			'战魂',
			'张宝',
			'张宝',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 2
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
			'张梁',
			f"{self.get_resource_path('serveAssets/images/zhanhun/zhangliang1.bmp')}|{self.get_resource_path('serveAssets/images/zhanhun/zhangliang2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 3
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
			'张角',
			'张角',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 4
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
			'文丑',
			'文丑',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 5
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
			'颜良',
			'颜良',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 6
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
			'华雄',
			'华雄',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 7
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
			'孙策',
			'孙策',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 8
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
			'典韦',
			'典韦',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 9
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
			'郭嘉',
			'郭嘉',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 10
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
			'刘备',
			'刘备',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 11
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
			'曹操',
			'曹操',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 12
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
			'袁绍',
			'袁绍',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 13
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
			'张飞',
			'张飞',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 14
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
			'大乔',
			'大乔',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 15
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
			'关羽',
			'关羽',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 16
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 17
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
			'张飞',
			'张飞',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 18
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
			'关羽',
			'关羽',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 19
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 20
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
			'魔化吕布',
			'魔化吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		if self.zhanhunFloor == '20层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 21
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
			'刘备',
			'刘备',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("21层没打过")
			return True
		if self.zhanhunFloor == '21层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 22
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
			'袁绍',
			'袁绍',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("22层没打过")
			return True
		if self.zhanhunFloor == '22层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 23
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
			'曹操',
			'曹操',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("23层没打过")
			return True
		if self.zhanhunFloor == '23层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 24
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("24层没打过")
			return True
		if self.zhanhunFloor == '24层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 25
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
			'魔化吕布',
			'魔化吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("25层没打过")
			return True
		if self.zhanhunFloor == '25层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/26.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 26
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/26.bmp"),
			'人参娃',
			'人参娃',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'洛阳',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("26层没打过")
			return True
		if self.zhanhunFloor == '26层':
			# 退出副本
			self.outScript('战魂')
			return True
		# 退出副本
		self.outScript('战魂')
		return True

	# 魔镜脚本
	def mojingScript(self):
		if self.overed:
			return
		self.mojingCount += 1
		print(f"第{self.mojingCount}次魔镜.")
		isInGuanDu = self.waitFor('城西', self.dituLocation, 5)
		if not isInGuanDu:
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
		# 进入魔镜
		self.findAndClickPic(
			'城西',
			self.get_resource_path("serveAssets/images/mojing/mojingshizhe.bmp"),
			self.get_resource_path("serveAssets/images/mojing/mojingshizhe1.bmp"),
			self.gameBottomLocation,
			'进入',
			self.gameBottomLocation,
			"0.14,0.124",
		)
		self.waitForAAndClickB1(
			'镜像地层',
			'进入',
			self.dituLocation,
			self.gameBottomLocation,
		)
		# isInMojing = self.waitFor('镜像地层', self.dituLocation, 8)
		# if not isInMojing:
		# 	print('魔镜没了')
		# 	return False
		# 打一个第一层的怪
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'镜像地层',
			'吃人妖',
			'吃人妖',
			self.gameLeftLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.155,0.121",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		# 进入第二层
		self.findAndClickPic(
			'镜像地层',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'进入|知道了',
			self.gameBottomLocation,
			"",
		)
		# self.waitForAAndClickB1(
		# 	'进入',
		# 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
		# 	self.gameBottomLocation, self.dituLocation,
		# )
		self.findAndClickPic(
			'镜像地层',
			'进入|知道了',
			f"{self.get_resource_path('serveAssets/images/mojing/jin.bmp')}|{self.get_resource_path('serveAssets/images/mojing/zhidao.bmp')}",
			self.gameBottomLocation,
			'遗迹镜像',
			self.dituLocation,
			"",
		)
		# self.waitForAAndClickB(
		# 	'遗迹镜像',
		# 	'进入',
		# 	self.dituLocation,
		# 	self.gameBottomLocation,
		# 	'遗迹镜像',
		# 	'知道了',
		# )
		# 打狮王
		self.findAndClickPic(
			'遗迹镜像',
			'狮王魂',
			'狮王魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.118,0.125",
		)
		# 进入第三层
		self.findAndClickPic(
			'遗迹镜像',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'进入|知道了',
			self.gameBottomLocation,
			"",
		)
		# self.waitForAAndClickB1(
		# 	'进入',
		# 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
		# 	self.gameBottomLocation, self.dituLocation,
		# )
		self.findAndClickPic(
			'遗迹镜像',
			'进入|知道了',
			f"{self.get_resource_path('serveAssets/images/mojing/jin.bmp')}|{self.get_resource_path('serveAssets/images/mojing/zhidao.bmp')}",
			self.gameBottomLocation,
			'迷幻境',
			self.dituLocation,
			"",
		)
		# 打虚实
		self.color_format = 'ffffff-00000|00ff00-000000|ff0000-000000'
		self.findAndClickPic(
			'迷幻境',
			'虚',
			'虚',
			self.gameRightLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.056,0.143",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		self.findAndClickPic(
			'迷幻境',
			'实',
			'实',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.152,0.132",
		)
		if self.mojingFloor == '迷幻境（虚实）':
			# 退出副本
			self.outScript('迷幻境')
			return True
		# 进入第四层
		self.findAndClickPic(
			'迷幻境',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'进入|知道了',
			self.gameBottomLocation,
			"",
		)
		# self.waitForAAndClickB1(
		# 	'进入',
		# 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
		# 	self.gameBottomLocation, self.dituLocation,
		# )
		self.findAndClickPic(
			'迷幻境',
			'进入|知道了',
			f"{self.get_resource_path('serveAssets/images/mojing/jin.bmp')}|{self.get_resource_path('serveAssets/images/mojing/zhidao.bmp')}",
			self.gameBottomLocation,
			'狱境',
			self.dituLocation,
			"",
		)
		# self.waitForAAndClickB(
		# 	'狱境',
		# 	'进入',
		# 	self.dituLocation,
		# 	self.gameBottomLocation,
		# 	'狱境',
		# 	'知道了',
		# )
		# 打黑白无常
		self.findAndClickPic(
			'狱境',
			'黑无常之魂',
			'黑无常之魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.11,0.12",
		)
		self.findAndClickPic(
			'狱境',
			'白无常之魂',
			'白无常之魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.163,0.118",
		)
		if self.mojingFloor == '狱境（黑白无常）':
			# 退出副本
			self.outScript('狱境')
			return True
		# 进入第五层
		self.findAndClickPic(
			'狱境',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'进入|知道了',
			self.gameBottomLocation,
			"",
		)
		# self.waitForAAndClickB1(
		# 	'进入',
		# 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
		# 	self.gameBottomLocation, self.dituLocation,
		# )
		self.findAndClickPic(
			'狱境',
			'进入|知道了',
			f"{self.get_resource_path('serveAssets/images/mojing/jin.bmp')}|{self.get_resource_path('serveAssets/images/mojing/zhidao.bmp')}",
			self.gameBottomLocation,
			'炎冰境',
			self.dituLocation,
			"",
		)
		# self.waitForAAndClickB(
		# 	'炎冰境',
		# 	'进入',
		# 	self.dituLocation,
		# 	self.gameBottomLocation,
		# 	'炎冰境',
		# 	'知道了',
		# )
		# 打黑白无常
		self.findAndClickPic(
			'炎冰境',
			'冰魔',
			'冰魔',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.05,0.125",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ff0000-000000'
		self.findAndClickPic(
			'炎冰境',
			'炎魔',
			f"{self.get_resource_path('serveAssets/images/zhengdian/huoyan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huoyan2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.172,0.127",
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		self.findAndClickPic(
			'炎冰境',
			'炎兄',
			f"{self.get_resource_path('serveAssets/images/zhengdian/huoyan1.bmp')}|{self.get_resource_path('serveAssets/images/zhengdian/huoyan2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.156,0.127",
		)
		if self.mojingFloor == '炎冰境':
			# 退出副本
			self.outScript('炎冰境')
			return True
		# 进入第六层
		self.findAndClickPic(
			'炎冰境',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'进入|知道了',
			self.gameBottomLocation,
			"",
		)
		# self.waitForAAndClickB1(
		# 	'进入',
		# 	self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
		# 	self.gameBottomLocation, self.dituLocation,
		# )
		self.findAndClickPic(
			'炎冰境',
			'进入|知道了',
			f"{self.get_resource_path('serveAssets/images/mojing/jin.bmp')}|{self.get_resource_path('serveAssets/images/mojing/zhidao.bmp')}",
			self.gameBottomLocation,
			'印魔殿',
			self.dituLocation,
			"",
		)
		# self.waitForAAndClickB(
		# 	'印魔殿',
		# 	'进入',
		# 	self.dituLocation,
		# 	self.gameBottomLocation,
		# 	'印魔殿',
		# 	'知道了',
		# )
		# 北境
		self.findAndClickPic(
			'印魔殿',
			'北境',
			'北境',
			self.dituLocation,
			'北境',
			self.dituLocation,
			"0.122,0.075",
		)
		self.findAndClickPic(
			'北境',
			'四神',
			'四神',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.125",
		)
		self.findAndClickPic(
			'北境',
			'印魔殿',
			'印魔殿',
			self.dituLocation,
			'印魔殿',
			self.dituLocation,
			"0.101,0.172",
		)
		# 西境
		self.findAndClickPic(
			'印魔殿',
			'西境',
			'西境',
			self.dituLocation,
			'西境',
			self.dituLocation,
			"0.182,0.115",
		)
		self.findAndClickPic(
			'西境',
			'四神',
			'四神',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.104,0.137",
		)
		self.waitForAAndClickB1(
			'印魔殿',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 南境
		self.findAndClickPic(
			'印魔殿',
			'南境',
			'南境',
			self.dituLocation,
			'南境',
			self.dituLocation,
			"0.123,0.153",
		)
		self.findAndClickPic(
			'南境',
			'四神',
			'四神',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.1,0.139",
		)
		self.findAndClickPic(
			'南境',
			'印魔殿',
			'印魔殿',
			self.dituLocation,
			'印魔殿',
			self.dituLocation,
			"0.102,0.113",
		)
		# 东境
		self.findAndClickPic(
			'印魔殿',
			'东境',
			'东境',
			self.dituLocation,
			'东境',
			self.dituLocation,
			"0.053,0.117",
		)
		self.findAndClickPic(
			'东境',
			'四神',
			'四神',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.107,0.137",
		)
		self.waitForAAndClickB1(
			'印魔殿',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# boss
		self.findAndClickPic(
			'印魔殿',
			'魔将',
			'魔将',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.135,0.101",
		)
		# 退出副本
		self.outScript('印魔殿')
		return True

	# 炼丹脚本
	def liandanScript(self):
		if self.overed:
			return
		print('开始炼丹房')
		isInGuanDu = self.waitFor('五指峡谷', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本南华老人', False)
		# 进入炼丹
		# 0.164,0.131
		self.findAndClickPic(
			'五指峡谷',
			self.get_resource_path("serveAssets/images/richang/nanhualaoren.bmp"),
			self.get_resource_path("serveAssets/images/richang/nanhualaoren1.bmp"),
			self.gameLocation,
			'进入',
			self.gameBottomLocation,
			"0.164,0.131"
		)
		self.waitForAAndClickB1(
			'南天门',
			'进入',
			self.dituLocation, self.gameBottomLocation,
		)
		isInHong = self.waitFor('南天门', self.dituLocation, 8)
		if not isInHong:
			print('炼丹没次数了')
			return False
		# 打门神 0.1111,0.131
		self.findAndClickPic(
			'南天门',
			'左门',
			'左门',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.111,0.131",
		)
		# 0.083,0.127
		self.findAndClickPic(
			'南天门',
			'右门',
			'右门',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.083,0.127",
		)
		# 进入第二层  0.103,0.115
		self.findAndClickPic(
			'南天门',
			'天宫小道',
			'天宫小道',
			self.dituLocation,
			'天宫小道',
			self.dituLocation,
			"0.103,0.115",
		)
		# 进入
		self.waitForAAndClickB1(
			'炼丹房',
			self.get_resource_path("serveAssets/images/richang/liandanchuansongmen.bmp"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 开始打炼丹童子童女  0.155,0.151  0.135,0.12
		liandan1_poss = ['0.135,0.12', '0.155,0.151', '0.135,0.12', '0.155,0.151', '0.135,0.12']
		for i in range(5):
			self.findAndClickPic(
				'炼丹房',
				'炼丹童',
				'炼丹童',
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd111.bmp"),
				self.gameBottomLocation,
				liandan1_poss[i],
			)
		# 0.052,0.143   0.071,0.118
		liandan2_poss = ['0.071,0.118', '0.052,0.143', '0.071,0.118', '0.052,0.143', '0.071,0.118']
		for i in range(5):
			self.findAndClickPic(
				'炼丹房',
				'炼丹童',
				'炼丹童',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd111.bmp"),
				self.gameBottomLocation,
				liandan2_poss[i],
			)
		# 退出副本
		self.outScript('炼丹房')
		return True

	# 五行脚本
	def wuxingScript(self):
		if self.overed:
			return
		print('开始五行')
		isInGuanDu = self.waitFor('野外西', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本老板', True)
		# 进入五行
		self.findAndClickPic(
			'野外西',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.dituLocation,
			'进五行',
			self.gameBottomLocation,
			"0.03,0.12"
		)
		self.waitForAAndClickB1(
			'五行圣殿',
			'进五行',
			self.dituLocation,
			self.gameBottomLocation,
		)
		isInMojing = self.waitFor('五行圣殿', self.dituLocation, 8)
		if not isInMojing:
			print('五行没次数了')
			return False
		# 0.082,0.117
		self.findAndClickPic(
			'五行圣殿',
			'神火系',
			f"{self.get_resource_path('serveAssets/images/richang/shenhuoxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenhuoxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.082,0.117",
		)
		time.sleep(0.5)
		self.click_image(self.get_resource_path("serveAssets/images/guaji.bmp"), self.confidenceNum, self.gameBottomLocation)
		self.waitFor('野外西', self.dituLocation)
		return True
		# 打大乔  0.077,0.146
		self.findAndClickPic(
			'五行圣殿',
			self.get_resource_path('serveAssets/images/richang/shenshuixi1.bmp'),
			self.get_resource_path('serveAssets/images/richang/shenshuixi2.bmp'),
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.077,0.146",
		)

		# 0.104,0.125
		self.findAndClickPic(
			'五行圣殿',
			'神金系',
			f"{self.get_resource_path('serveAssets/images/richang/shenjinxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenjinxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.104,0.125",
		)
		# 0.148,0.151
		self.findAndClickPic(
			'五行圣殿',
			self.get_resource_path('serveAssets/images/richang/shentuxi.bmp'),
			f"{self.get_resource_path('serveAssets/images/richang/shentuxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shentuxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.148,0.151",
		)
		# 0.121,0.117
		self.findAndClickPic(
			'五行圣殿',
			self.get_resource_path('serveAssets/images/richang/shenmuxi.bmp'),
			f"{self.get_resource_path('serveAssets/images/richang/shenmuxi1.bmp')}|{self.get_resource_path('serveAssets/images/richang/shenmuxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.121,0.117",
		)
		self.outScript('五行圣殿', )
		return True

	# 溶洞
	def rongdongScript(self):
		if self.overed:
			return
		print('开始溶洞')
		isInGuanDu = self.waitFor('绿林路', self.dituLocation, 5)
		if not isInGuanDu:
			print('请前往副本门口！')
		# self.feiFb('副本龙天啸', False)
		# 进入溶洞  0.065,0.124
		self.findAndClickPic(
			'绿林路',
			self.get_resource_path("serveAssets/images/richang/longtianxiao2.bmp"),
			self.get_resource_path("serveAssets/images/richang/longtianxiao.bmp"),
			self.gameLocation,
			'进入',
			self.gameBottomLocation,
			"0.065,0.124",
		)
		self.waitForAAndClickB1(
			'遗忘之林',
			'进入',
			self.dituLocation,
			self.gameBottomLocation,
		)
		isInMojing = self.waitFor('遗忘之林', self.dituLocation, 8)
		if not isInMojing:
			print('溶洞没次数了')
			return False
		# 开始打第一层  0.054,0.113  0.086,0.129   0.121,0.113
		ganshi_pos = ['0.054,0.113', '0.086,0.129', '0.121,0.113']
		for i in range(3):
			self.findAndClickPic(
				'遗忘之林',
				'远古干尸',
				'远古干尸',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				ganshi_pos[i],
			)
		# 0.162,0.132
		self.findAndClickPic(
			'遗忘之林',
			'暴力熊',
			'暴力熊',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.162,0.132',
		)
		# 进入第二层
		self.waitForAAndClickB1(
			'远古溶洞',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation,
			self.dituLocation,
		)
		# 0.176,0.124
		self.findAndClickPic(
			'远古溶洞',
			'永恒之火',
			'永恒之火',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.176,0.124",
		)
		# 退出副本
		self.outScript('远古溶洞')
		return True

	# 80精英
	def bamenScript(self):
		if self.overed:
			return
		print('开始80精英')
		isInGuanDu = self.waitFor('许昌', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本分身', True)
		# 进入80精英  0.108,0.134
		self.findAndClickPic(
			'许昌',
			self.get_resource_path("serveAssets/images/richang/zuocifenshen.bmp"),
			self.get_resource_path("serveAssets/images/richang/zuocifenshen1.bmp"),
			self.gameLocation,
			'进精英',
			self.gameBottomLocation,
			"0.108,0.134",
		)
		self.waitForAAndClickB1(
			'魔岛入口',
			'进精英',
			self.dituLocation,
			self.gameBottomLocation
		)
		isInMojing = self.waitFor('魔岛入口', self.dituLocation, 8)
		if not isInMojing:
			print('80精英没次数了')
			return False
		# 进入幻境凶  0.134,0.141
		self.findAndClickPic(
			'魔岛入口',
			'凶',
			'凶',
			self.dituLocation,
			'凶',
			self.dituLocation,
			"0.134,0.141",
		)
		# 打妖族之王 0.083.0.129
		self.findAndClickPic(
			'凶',
			'妖族',
			'妖族',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.083,0.129",
		)
		# 进入地牢  0.067,0.108
		self.waitForAAndClickB1(
			'地牢',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打穷奇   0.067,0.108
		self.findAndClickPic(
			'地牢',
			'穷奇',
			'穷奇',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.067,0.108",
		)
		# 进入二层
		self.findAndClickPic(
			'地牢',
			'地牢二层',
			'地牢二层',
			self.dituLocation,
			'地牢二层',
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
			'地牢二层',
			'妖化',
			'妖化',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.127,0.113",
		)
		# 进入boss
		self.waitForAAndClickB1(
			'阵枢',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打boss
		self.findAndClickPic(
			'阵枢',
			'妖化',
			'妖化',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 退出副本
		self.outScript('阵枢', )
		return True

	# 官渡精英
	def guanduJyScript(self):
		print("开始官渡精英")
		if self.overed:
			return
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor('官渡', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本曹操', True)
		# 进入官渡
		self.findAndClickPic(
			'官渡',
			self.get_resource_path("serveAssets/images/guandu/caocao1.bmp"),
			self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
			self.gameLocation,
			'进精英',
			self.gameBottomLocation,
			'0.038,0.134',
			"",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			'大帐',
			'进精英',
			self.dituLocation, self.gameLeftLocation,
		)
		isInMojing = self.waitFor('大帐', self.dituLocation, 5)
		if not isInMojing:
			print('官渡精英没次数了')
			return False
		self.waitForAAndClickB1(
			'战场',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 第一个河北军  0.153,0.122
		self.findAndClickPic(
			'战场',
			'河北军',
			f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.153,0.122'
		)
		# 第二个河北军  0.117,0.124
		self.findAndClickPic(
			'战场',
			'河北军',
			f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.117,0.129'
		)
		# 颜良  0.097,0.124
		self.findAndClickPic(
			'战场',
			self.get_resource_path('serveAssets/images/guandu/yanliang.bmp'),
			f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.097,0.124'
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 文丑  0.077,0.122
		self.findAndClickPic(
			'战场',
			self.get_resource_path('serveAssets/images/guandu/wenchou.bmp'),
			f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.077,0.122",
			"",
		)
		# 去大帐
		self.waitForAAndClickB1(
			'大帐',
			self.get_resource_path("serveAssets/images/guandu/jy1chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor('大帐', self.dituLocation)
		# 找到曹操进入乌巢
		self.waitForAAndClickB1(
			'知道了',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.gameLeftLocation, self.dituLocation,
		)
		self.waitForAAndClickB1(
			'粮仓',
			'知道了',
			self.dituLocation, self.gameLeftLocation,
		)
		self.waitForAAndClickB1(
			'枯寂',
			self.get_resource_path("serveAssets/images/guandu/jygohundianchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor('枯寂', self.dituLocation)
		# 0.167,0.103
		self.findAndClickPic(
			'枯寂',
			'文丑之魂',
			'文丑之魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.167,0.103",
		)
		# 打董卓 0.142,0.115
		self.findAndClickPic(
			'枯寂',
			'董卓',
			'董卓',
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
			'粮仓',
			self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 打淳
		self.findAndClickPic(
			'粮仓',
			'淳于琼',
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
			'粮仓',
			self.get_resource_path('serveAssets/images/guandu/yuanshao.bmp'),
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
		self.outScript('粮仓')

	# 云游精英
	def yunyouJyScript(self):
		if self.overed:
			return
		print('开始云游精英')
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor('嵩山', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本仙人', True)
		# 进入云游  0.186,0.105
		self.findAndClickPic(
			'嵩山',
			self.get_resource_path("serveAssets/images/richang/yunyouxianren1.bmp"),
			self.get_resource_path("serveAssets/images/richang/yunyouxianren.bmp"),
			self.gameLocation,
			'进精英',
			self.gameBottomLocation,
			"0.186,0.105",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			'东海之极',
			'进精英',
			self.dituLocation,
			self.gameBottomLocation
		)
		isInMojing = self.waitFor('东海之极', self.dituLocation, 5)
		if not isInMojing:
			print('云游精英没次数了')
			return False
		# 进鬼气林
		self.waitForAAndClickB1(
			'鬼气林',
			self.get_resource_path("serveAssets/images/richang/yunyou1chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 打黑无常 0.141,0.112
		self.findAndClickPic(
			'鬼气林',
			'黑无常',
			'黑无常',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.141,0.112",
		)
		# 进东海之极
		self.waitForAAndClickB1(
			'东海之极',
			self.get_resource_path("serveAssets/images/richang/guiqilinchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor('东海之极', self.dituLocation)
		# 找云霞仙子
		self.waitForAAndClickB1(
			'进天梯',
			self.get_resource_path("serveAssets/images/richang/zixiaxianzi.bmp"),
			self.gameBottomLocation, self.gameBottomLocation,
		)
		self.waitForAAndClickB1(
			'天梯',
			'进天梯',
			self.dituLocation, self.gameBottomLocation,
		)
		# 打张辽 0.146,0.118
		self.findAndClickPic(
			'天梯',
			'天界',
			'天界',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.146,0.118",
		)
		# 进云端
		self.waitForAAndClickB1(
			'云端',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 进入第一个传送门 0.034,0.124
		self.findAndClickPic(
			'云端',
			'天界精英',
			'天界精英',
			self.dituLocation,
			'天界精英',
			self.dituLocation,
			"0.034,0.124",
		)
		# 0.054,0.122
		self.findAndClickPic(
			'天界精英',
			'天界分身',
			'天界分身',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.054,0.122",
		)
		# 进云端
		self.findAndClickPic(
			'天界精英',
			'云端',
			'云端',
			self.dituLocation,
			'云端',
			self.dituLocation,
			"0.014,0.131",
		)
		# self.waitForAAndClickB1(
		# 	'云端',
		# 	self.get_resource_path("serveAssets/images/richang/tianjiechuansongmen.bmp"),
		# 	self.dituLocation, self.dituLocation,
		# )
		# 进地狱打巨灵神  0.012,0.127
		self.findAndClickPic(
			'云端',
			'地狱',
			'地狱',
			self.dituLocation,
			'地狱',
			self.dituLocation,
			"0.012,0.127",
		)
		# 0.146,0.118
		self.findAndClickPic(
			'地狱',
			'地狱分',
			'地狱分',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.146,0.118",
		)
		# 进云端
		self.waitForAAndClickB1(
			'云端',
			self.get_resource_path("serveAssets/images/richang/diyuchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 进人界
		self.findAndClickPic(
			'云端',
			'人界',
			'人界',
			self.dituLocation,
			'人界',
			self.dituLocation,
			"0.012,0.127",
		)
		# 打人界巨灵神0.095,0.134
		self.findAndClickPic(
			'人界',
			'人界分身',
			'人界分身',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.095,0.134",
		)
		# 进云端
		self.waitForAAndClickB1(
			'云端',
			self.get_resource_path("serveAssets/images/richang/renjiechuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 打boss  0.1,0.115
		self.findAndClickPic(
			'云端',
			'巨灵神',
			'巨灵神',
			self.gameLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.1,0.115",
			'',
			'down'
		)
		# 退出副本
		self.outScript('云端')
		return True

	# 100精英
	def laoshuJyScript(self):
		if self.overed:
			return
		print('开始老鼠精英')
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor('碧水地穴', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本猎鼠人', True)
		# 进入老鼠  0.086,0.103
		self.findAndClickPic(
			'碧水地穴',
			self.get_resource_path("serveAssets/images/richang/lieshuren.bmp"),
			self.get_resource_path("serveAssets/images/richang/lieshuren1.bmp"),
			self.gameLocation,
			'进精英',
			self.gameBottomLocation,
			"0.086,0.103",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			'鼠穴入口',
			'进精英',
			self.dituLocation,
			self.gameBottomLocation,
		)
		isInMojing = self.waitFor('鼠穴入口', self.dituLocation, 5)
		if not isInMojing:
			print('老鼠精英没次数了')
			return False
		# 打妖鼠头领  0.152,0.122
		self.findAndClickPic(
			'鼠穴入口',
			'妖鼠头领',
			'妖鼠头领',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.152,0.122",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			'鼠穴',
			self.get_resource_path("serveAssets/images/richang/laoshu1chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 打猎杀鼠  0.097,0.124
		self.findAndClickPic(
			'鼠穴',
			'暗杀鼠',
			'暗杀鼠',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.097,0.124",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			'鼠巢内',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation,
			self.dituLocation,
		)
		# 打鼠长老  0.143,0.112
		self.findAndClickPic(
			'鼠巢内',
			'鼠长老',
			'鼠长老',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.143,0.112",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			'鼠大厅',
			self.get_resource_path("serveAssets/images/richang/shuchaoneichuansongmen1.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 打boss1  0.108,0.11
		self.findAndClickPic(
			'鼠大厅',
			'碧水鼠王',
			'碧水鼠王',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.108,0.11",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			'鼠巢内',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor('鼠巢内', self.dituLocation)
		# 进入boss
		self.waitForAAndClickB1(
			'鼠殿',
			self.get_resource_path("serveAssets/images/richang/shuchaoneichuansongmen2.bmp"),
			self.dituLocation, self.gameLocation,
		)
		# 打boss1
		self.findAndClickPic(
			'鼠殿',
			'碧水鼠王',
			'碧水鼠王',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 退出副本
		self.outScript('鼠殿')
		return True

	# 名将挑战赛
	def mingjiangtiaozhan(self):
		if self.overed:
			return
		print('名将挑战赛')
		with condition:
			if self.stoped:
				condition.wait()
		# 进入
		isInGuanDu = self.waitFor('洛阳', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本挑战赛', True)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入战魂
		self.findAndClickPic(
			'洛阳',
			self.get_resource_path("serveAssets/images/zhanhun/zhanhuntiaozhan.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/zhanhuntiaozhanditu.bmp"),
			self.gameBottomLocation,
			'进名将挑战',
			self.gameBottomLocation,
			"0.067,0.132"
		)
		# 点击进入战魂
		self.waitForAAndClickB1(
			'武神殿',
			'进名将挑战',
			self.dituLocation, self.gameBottomLocation,
		)
		isInZhanhun = self.waitFor('武神殿', self.dituLocation, 8)
		if not isInZhanhun:
			print('名将没次数了')
			return False
		# 打刘备
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/mingjiangliubei2.bmp"),
			self.get_resource_path("serveAssets/images/richang/mingjiangliubei.bmp"),
			self.gameBottomLocation,
			'挑战',
			self.gameBottomLocation,
			"0.156,0.144",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			'挑战',
			self.gameBottomLocation, self.gameBottomLocation,
		)
		self.waitFor(self.get_resource_path("serveAssets/images/zdzd.bmp"), self.gameBottomLocation)
		# 打张飞
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/mingjiangzhangfei1.bmp"),
			self.get_resource_path("serveAssets/images/richang/mingjiangzhangfei.bmp"),
			self.gameBottomLocation,
			'挑战',
			self.gameBottomLocation,
			"0.142,0.115",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			'挑战',
			self.gameBottomLocation, self.gameBottomLocation,
		)
		self.waitFor(self.get_resource_path("serveAssets/images/zdzd.bmp"), self.gameBottomLocation)
		# 打关羽
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/mingjiangguanyu1.bmp"),
			self.get_resource_path("serveAssets/images/richang/mingjiangguanyu.bmp"),
			self.gameBottomLocation,
			'挑战',
			self.gameBottomLocation,
			"0.043,0.144",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			'挑战',
			self.gameBottomLocation, self.gameBottomLocation,
		)
		self.waitFor(self.get_resource_path("serveAssets/images/zdzd.bmp"), self.gameBottomLocation)
		# 打吕布
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/mingjianglvbu1.bmp"),
			self.get_resource_path("serveAssets/images/richang/mingjianglvbu.bmp"),
			self.gameBottomLocation,
			'挑战',
			self.gameBottomLocation,
			"0.063,0.113",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			'挑战',
			self.gameBottomLocation, self.gameBottomLocation,
		)
		self.waitFor(self.get_resource_path("serveAssets/images/zdzd.bmp"), self.gameBottomLocation)
		# 找守卫
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/tianwaitianshouwei.bmp"),
			self.get_resource_path("serveAssets/images/richang/tianwaitianshouwei1.bmp"),
			self.gameLocation,
			'进天外',
			self.gameBottomLocation,
			"0.063,0.113",
		)
		self.waitForAAndClickB1(
			'天外天',
			'进天外',
			self.dituLocation, self.gameBottomLocation,
		)
		chanchu_pos = ['0.121,0.112', '0.104,0.103', '0.078,0.108', '0.067,0.118', '0.046,0.106', '0.038,0.113']
		self.findAndClickPic(
			'天外天',
			'地穴蟾蜍',
			'地穴蟾蜍',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.14,0.119',
		)
		for i in range(6):
			self.findAndClickPic(
				'天外天',
				'地穴蟾蜍',
				'地穴蟾蜍',
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				chanchu_pos[i],
			)
		waitForTwoRes = self.waitForTwo(
			'出现',
			'运气太烂',
			self.gameBottomLocation,
		)
		if waitForTwoRes == "second":
			print("没有守财奴")
			return True
		time.sleep(0.5)
		self.dm.KeyPressChar('g')
		self.waitFor('洛阳', self.dituLocation)
		return True

	# 一直执行天外天
	def mingjiangtiaozhanWhile(self):
		for i in range(8):
			if self.overed:
				return
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break
		self.scriptName = '官渡'
		self.guanduWhile()

	# 名将闯关
	def mingjiangchuangguan(self):
		isInGuanDu = self.waitFor('城西', self.dituLocation, 5)
		if not isInGuanDu:
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
		# 进入魔镜
		self.findAndClickPic(
			'城西',
			'名将使者',
			f"{self.get_resource_path('serveAssets/images/mingjiangshizhe1.bmp')}|{self.get_resource_path('serveAssets/images/mingjiangshizhe2.bmp')}",
			self.gameBottomLocation,
			'进入',
			self.gameBottomLocation,
			"0.074,0.138",
		)
		self.waitForAAndClickB1(
			'名战殿',
			'进入',
			self.dituLocation,
			self.gameBottomLocation,
		)
		isInHong = self.waitFor('名战殿', self.dituLocation, 8)
		if not isInHong:
			print('名将时间到了')
			return False
		time.sleep(0.5)
		self.dm.KeyPressChar('g')
		self.waitFor('城西', self.dituLocation)
		return True

	# 黑风
	def heifengScript(self):
		if self.overed:
			return
		self.heifengCount += 1
		print(f"第{self.heifengCount}次黑风.")
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor('五层', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本霸山虎', False)
		# 进入黑风
		time.sleep(1)
		self.findAndClickPic(
			'五层',
			self.get_resource_path("serveAssets/images/heifeng/11.bmp"),
			self.get_resource_path("serveAssets/images/heifeng/bashanhu.bmp"),
			self.gameLeftLocation,
			'黑风山寨',
			self.gameLeftLocation,
			"0.166,0.12",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入第一层
		self.waitForAAndClickB1(
			'黑风山寨',
			'黑风山寨',
			self.dituLocation, self.gameLeftLocation,
		)
		# 打刀贼
		daozei_poss = ['0.044,0.12', '0.076,0.131', '0.096,0.121', '0.117,0.129']
		for i in range(3):
			self.findAndClickPic(
				'黑风山寨',
				'刀贼',
				f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				daozei_poss[i]
			)
		self.findAndClickPic(
			'黑风山寨',
			'刀贼',
			f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			daozei_poss[3]
		)
		# 81  72
		self.findAndClickPic(
			'黑风山寨',
			'头目',
			'头目',
			self.gameRightLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.153,0.123'
		)
		# 进入第二层
		self.waitForAAndClickB1(
			'山寨本营',
			self.get_resource_path("serveAssets/images/heifeng/heifeng1chuansongmen.bmp"),
			self.dituLocation,
			self.dituLocation
		)
		self.waitFor('山寨本营', self.dituLocation)
		#
		if self.heifengFloor == '大/80':
			self.findAndClickPic(
				'山寨本营',
				'头目',
				'头目',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				"0.177,0.141",
			)
			self.findAndClickPic(
				'山寨本营',
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
				'当家',
				'当家',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				"0.142,0.11",
			)
			# 退出副本
			self.outScript(self.get_resource_path("serveAssets/images/heifeng/midong.bmp"), )
			return True
		else:
			self.waitForAAndClickB1(
				'山寨内堂',
				self.get_resource_path("serveAssets/images/heifeng/chuansongmen2.bmp"),
				self.dituLocation,
				self.dituCenterLocation
			)
			# 打二当家
			self.findAndClickPic(
				'山寨内堂',
				'当家',
				'当家',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				"0.127,0.141",
			)
			# 退出副本
			self.outScript('山寨内堂')
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
		isInGuanDu = self.waitFor('五层', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本霸山虎', False)
		# 进入矿产
		self.findAndClickPic(
			'五层',
			self.get_resource_path("serveAssets/images/heifeng/11.bmp"),
			self.get_resource_path("serveAssets/images/heifeng/bashanhu.bmp"),
			self.gameLeftLocation,
			'矿产',
			self.gameLeftLocation,
			"0.166,0.12",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			'矿场洞窟',
			'矿产',
			self.dituLocation, self.gameLeftLocation,
		)
		# 打矿工凶灵
		chikuang_poss = ['0.044,0.134', '0.072,0.136', '0.102,0.131', '0.127,0.139', '0.154,0.134']
		for i1 in range(5):
			self.findAndClickPic(
				'矿场洞窟',
				'矿工凶灵',
				f"{self.get_resource_path('serveAssets/images/heifeng/xiongling1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/xiongling2.bmp')}",
				self.gameRightLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				chikuang_poss[i1]
			)
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'矿场洞窟',
			'吃矿小鬼',
			'吃矿小鬼',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.184,0.132'
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		# 进入第二层
		self.waitForAAndClickB1(
			'矿场内',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation,
			self.dituLocation
		)
		# 打矿工凶灵
		chikuang_poss1 = ['0.125,0.127', '0.163,0.141', '0.188,0.12', '0.063,0.137', '0.017,0.118']
		self.findAndClickPic(
			'矿场内',
			'矿工凶灵',
			self.get_resource_path('serveAssets/images/heifeng/xiongling2.bmp'),
			self.gameRightLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.097,0.138'
		)
		for i in range(4):
			self.findAndClickPic(
				'矿场内',
				'矿工凶灵',
				f"{self.get_resource_path('serveAssets/images/heifeng/xiongling1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/xiongling2.bmp')}",
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				chikuang_poss1[i]
			)
		self.color_format = 'ffffff-00000|00ff00-000000|00fe0d-000000'
		self.findAndClickPic(
			'矿场内',
			'吃矿小鬼',
			'吃矿小鬼',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			chikuang_poss1[4]
		)
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00fe0d-000000|fdff1b-000000|ff1c13-000000|fdff1b-000000|00ef0b-000000'
		# 进入第三层  0.043,0.12
		self.findAndClickPic(
			'矿场内',
			'岩石洞',
			'岩石洞',
			self.dituLocation,
			'岩石洞',
			self.dituLocation,
			'0.043,0.12'
		)
		# 打炼矿小鬼
		liankuang_poss = ['0.144,0.132', '0.11,0.144', '0.087,0.131', '0.066,0.139']
		for i in range(4):
			self.findAndClickPic(
				'岩石洞',
				'炼矿小鬼',
				f"{self.get_resource_path('serveAssets/images/heifeng/liankuang1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/liankuang2.bmp')}",
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				liankuang_poss[i]
			)
		self.findAndClickPic(
			'岩石洞',
			'炎魔神',
			'炎魔神',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.031,0.136'
		)
		# 退出副本
		self.outScript('岩石洞')
		return True

	# 龙岛
	def longdaoScript(self):
		if self.overed:
			return
		print(f"开始龙岛")
		isInGuanDu = self.waitFor('城西', self.dituLocation, 5)
		if not isInGuanDu:
			self.go_in_ditu('地图城西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '城西', '驿站城西', '')
		# 进入龙岛
		self.findAndClickPic(
			'城西',
			self.get_resource_path("serveAssets/images/longdao/bangpai.bmp"),
			self.get_resource_path("serveAssets/images/longdao/bangpai1.bmp"),
			self.gameBottomLocation,
			'进龙岛',
			self.gameBottomLocation,
			"0.123,0.139",
		)
		self.waitForAAndClickB1(
			'龙岛',
			'进龙岛',
			self.dituLocation,
			self.gameBottomLocation,
		)
		# 打守门人
		self.findAndClickPic(
			'龙岛',
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.get_resource_path("serveAssets/images/mojing/xiaolvren.bmp"),
			self.dituLocation,
			'挑战龙族',
			self.gameBottomLocation,
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			'挑战龙族',
			self.gameBottomLocation,
			self.gameBottomLocation,
		)
		self.waitFor(self.get_resource_path("serveAssets/images/zdzd.bmp"), self.gameBottomLocation)
		self.findAndClickPic(
			'龙岛',
			'进入',
			'进入',
			self.gameBottomLocation,
			'密洞',
			self.dituLocation,
			"",
		)
		self.findAndClickPic(
			'密洞',
			'金龙王',
			'金龙王',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.036,0.131",
		)
		if self.heifengFloor == '大/80':
			self.findAndClickPic(
				'密洞',
				'龙巢',
				'龙巢',
				self.dituLocation,
				'龙巢',
				self.dituLocation,
				"0.182,0.127",
			)
		else:
			self.findAndClickPic(
				'密洞',
				'龙巢',
				'龙巢',
				self.dituLocation,
				'龙巢',
				self.dituLocation,
				"0.18,0.158",
			)
		longchao_poss = ["0.02,0.113", '0.036,0.131', '0.048,0.117', '0.075,0.131', '0.091,0.122', '0.121,0.144', '0.142,0.143', '0.147,0.119']
		for index, item in enumerate(longchao_poss):
			self.findAndClickPic(
				'龙巢',
				'龙孙|龙孙一|龙子|龙子一',
				f"{self.get_resource_path('serveAssets/images/longdao/longsun.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longsun1.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longzi.bmp')}|{self.get_resource_path('serveAssets/images/longdao/longzi1.bmp')}",
				self.gameRightLocation if index < 5 else self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd111.bmp"),
				self.gameBottomLocation,
				item,
			)
		self.findAndClickPic(
			'龙巢',
			'地狱炎龙',
			'五爪金龙',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.183,0.134',
		)
		self.outScript('龙巢')

	# 黑风循环
	def heifengWhile(self):
		for i in range(self.heifengWhileCount):
			if self.overed:
				return
			self.heifengScript()
			if self.heifengCount == self.heifengWhileCount:
				break
		print(f"{self.heifengWhileCount}次黑风已完成,去官渡")
		if self.overed:
			return
		self.guanduWhile()

	# 一直执行官渡
	def guanduWhile(self):
		while True:
			if self.overed:
				return
			self.guanduScript()

	# 一直执行红
	def hongWhile(self):
		for i in range(7):
			if self.overed:
				return
			hongRes = self.hongScript()
			if not hongRes:
				print('红没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一直执行战魂
	def zhanhunWhile(self):
		for i in range(6):
			if self.overed:
				return
			zhanhunRes = self.zhanhunScript()
			if not zhanhunRes:
				print('战魂没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一直执行魔镜
	def mojingWhile(self):
		while True:
			if self.overed:
				return
			overMojing = self.mojingScript()
			if not overMojing:
				print('魔镜没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一次战魂一次红+整点
	def guanduAndHongAndZd(self):
		if self.overed:
			return
		self.zhanhunScript()
		time.sleep(1)
		if self.overed:
			return
		self.feiFb('副本典韦', True)
		toZhengdianTime = 59 - time.localtime().tm_min
		if 10 <= toZhengdianTime < 20:
			hongOver = self.hongScript()
			if not hongOver:
				self.guanduWhile()
		if self.overed:
			return
		elif toZhengdianTime >= 20:
			for i in range(2):
				hongOver = self.hongScript()
				if not hongOver:
					self.guanduWhile()
		elif toZhengdianTime < 10:
			self.guanduWhile()
		time.sleep(1)
		if self.overed:
			return
		self.guanduWhile()
		if self.overed:
			return
		self.zhengDian()

	# 日常一条龙
	def richangeScript(self):
		print('日常')
		# 飞溶洞
		if self.overed:
			return
		if '溶' in self.richangSelection:
			time.sleep(1)
			for i in range(3):
				hasRongdong = self.rongdongScript()
				if not hasRongdong:
					break
			time.sleep(1)
		# 飞炼丹
		if self.overed:
			return
		if '炼丹' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '驿站五指峡谷', True)
			else:
				self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '驿站五指峡谷', '驿站五指峡谷')
			for i in range(5):
				liandanHas = self.liandanScript()
				if not liandanHas:
					break
			time.sleep(1)
		# 飞五行
		if self.overed:
			return
		if '五行' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本老板', True)
			else:
				self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '', '驿站城西')
			time.sleep(1)
			for i in range(3):
				hasWuxing = self.wuxingScript()
				if not hasWuxing:
					break
			time.sleep(1)
		# 飞云游精英
		if self.overed:
			return
		if '云游' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本仙人', True)
			else:
				self.go_in_ditu('地图嵩山', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '嵩山', '', '驿站城西')
			time.sleep(1)
			self.yunyouJyScript()
			time.sleep(1)
		# 飞名将挑战赛
		if '名将' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本挑战赛', True)
			else:
				self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西')
			time.sleep(1)
			for i in range(8):
				zhanhunRes = self.mingjiangtiaozhan()
				if not zhanhunRes:
					print('名将没次数')
					break
			time.sleep(1)
		# 卖藏宝图
		# if '卖图' in self.richangSelection:
		# 	time.sleep(1)
		# 	self.clear_hide_map()
		# 	time.sleep(1)
		# 飞80精英
		if self.overed:
			return
		if '80' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本分身', True)
			else:
				self.go_in_ditu('地图许昌城', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '许昌', '驿站许昌', '驿站城西')
			time.sleep(1)
			self.bamenScript()
			time.sleep(1)
		# 飞100精英
		if '老鼠' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本猎鼠人', True)
			else:
				self.go_in_ditu('地图碧水地穴', self.get_resource_path("serveAssets/images/zhengdian/xiangyang.bmp"), '碧水地穴', '驿站襄阳', '驿站城西')
			time.sleep(1)
			self.laoshuJyScript()
			time.sleep(1)
		# 红
		if self.overed:
			return
		if '红' in self.richangSelection:
			self.feiFb('副本典韦', True)
			time.sleep(1)
			for i in range(7):
				hongRes = self.hongScript()
				if not hongRes:
					break
		# 战魂
		if self.overed:
			return
		if '战魂' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本挑战赛', True)
			else:
				self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '驿站城西', '')
			time.sleep(1)
			for i in range(6):
				hongRes = self.zhanhunScript()
				if not hongRes:
					break
		# 飞官渡精英
		if self.overed:
			return
		if '官渡' in self.richangSelection:
			if '飞' in self.richangSelection:
				self.feiFb('副本曹操', True)
			else:
				self.go_in_ditu('地图官渡', self.get_resource_path("serveAssets/images/zhengdian/xuchang.bmp"), '官渡', '驿站许昌', '驿站城西')
			time.sleep(1)
			self.guanduJyScript()
		time.sleep(1)
		if self.overed:
			return
		self.scriptName = "官渡"
		if self.overed:
			return
		self.guanduWhile()

	# 五行
	def wuxingWhile(self):
		for i in range(3):
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
		for i in range(3):
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
		for i in range(5):
			if self.overed:
				return
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		self.scriptName = "官渡"
		if self.overed:
			return
		self.guanduWhile()

	# 战魂+红+魔镜+整点
	def mojingAndHongAndZd(self):
		if self.overed:
			return
		self.zhanhunScript()
		if self.overed:
			return
		time.sleep(1)
		self.feiFb('副本典韦', True)
		if self.overed:
			return
		toZhengdianTime = 59 - time.localtime().tm_min
		if 10 <= toZhengdianTime < 20:
			hongOver = self.hongScript()
			if self.overed:
				return
			if not hongOver:
				self.mojingWhile()
		elif toZhengdianTime >= 20:
			for i in range(2):
				hongOver = self.hongScript()
				if self.overed:
					return
				if not hongOver:
					self.mojingWhile()
		elif toZhengdianTime < 10:
			self.mojingWhile()
			if self.overed:
				return
		time.sleep(1)
		if self.overed:
			return
		self.mojingWhile()
		if self.overed:
			return
		self.zhengDian()

	# 49日常
	def richang49Script(self):
		print('日常')
		if self.overed:
			return
		# 飞溶洞
		if '溶' in self.richangSelection:
			time.sleep(1)
			for i in range(3):
				hasRongdong = self.rongdongScript()
				if not hasRongdong:
					break
			time.sleep(1)
		# 飞炼丹
		if self.overed:
			return
		if '炼丹' in self.richangSelection:
			self.go_in_ditu('地图五指峡谷', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '五指峡谷', '涿郡野外', '驿站五指峡谷')
			for i in range(5):
				liandanHas = self.liandanScript()
				if not liandanHas:
					break
			time.sleep(1)
		# 飞五行
		if self.overed:
			return
		if '五行' in self.richangSelection:
			self.go_in_ditu('地图野外西', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '野外西', '', '驿站城西')
			time.sleep(1)
			for i in range(3):
				hasWuxing = self.wuxingScript()
				if not hasWuxing:
					break
		time.sleep(1)
		# 飞名将挑战赛
		if self.overed:
			return
		if '名将' in self.richangSelection:
			self.go_in_ditu('地图洛阳大道', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '洛阳', '', '驿站城西')
			time.sleep(1)
			for i in range(8):
				zhanhunRes = self.mingjiangtiaozhan()
				if not zhanhunRes:
					print('名将没次数')
					break
			time.sleep(1)
		# 卖藏宝图
		if self.overed:
			return
		# if '卖图' in self.richangSelection:
		# 	time.sleep(1)
		# 	self.clear_hide_map()
		# 	time.sleep(1)
		# 红
		if self.overed:
			return
		if '红' in self.richangSelection:
			self.go_in_ditu('地图虎牢关外', self.get_resource_path("serveAssets/images/zhengdian/luoyang.bmp"), '虎牢关外', '驿站城西', '')
			time.sleep(1)
			for i in range(7):
				hongRes = self.hongScript()
				if not hongRes:
					break
		# 战魂
		if self.overed:
			return
		if '战魂' in self.richangSelection:
			self.go_in_ditu('地图野外东', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '涿郡野外', '涿郡野外', '驿站城西')
			time.sleep(1)
			for i in range(6):
				hongRes = self.zhanhun49Script()
				if not hongRes:
					break

	# 49战魂
	def zhanhun49Script(self):
		if self.overed:
			return
		print("开始49战魂")
		isInGuanDu = self.waitFor('涿郡野外', self.dituLocation, 5)
		if not isInGuanDu:
			self.go_in_ditu('地图野外东', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '涿郡野外', '涿郡野外', '驿站城西')
		with condition:
			if self.stoped:
				condition.wait()
		# 进入战魂
		self.findAndClickPic(
			'涿郡野外',
			self.get_resource_path("serveAssets/images/zhanhun/qinshoujiang1.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/qinshoujiang2.bmp"),
			self.gameBottomLocation,
			'战魂楼',
			self.gameBottomLocation,
			"0.181,0.124"
		)
		# 点击进入战魂
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/1.bmp"),
			'战魂楼',
			self.dituLocation, self.gameBottomLocation,
		)
		isInZhanhun = self.waitFor('战魂', self.dituLocation, 8)
		if not isInZhanhun:
			print('战魂没次数了')
			return False
		# 1
		self.findAndClickPic(
			'战魂',
			'张宝',
			'张宝',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 2
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/2.bmp"),
			'张梁',
			'张梁',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 3
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/3.bmp"),
			'张角',
			'张角',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 4
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/4.bmp"),
			'文丑',
			'文丑',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 5
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/5.bmp"),
			'颜良',
			'颜良',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 6
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/6.bmp"),
			'华雄',
			'华雄',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 7
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/7.bmp"),
			'孙策',
			'孙策',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 8
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/8.bmp"),
			'典韦',
			'典韦',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 9
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/9.bmp"),
			'郭嘉',
			'郭嘉',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 10
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/10.bmp"),
			'刘备',
			'刘备',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 11
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/11.bmp"),
			'曹操',
			'曹操',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 12
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/12.bmp"),
			'袁绍',
			'袁绍',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 13
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/13.bmp"),
			'张飞',
			'张飞',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 14
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/14.bmp"),
			'大乔',
			'大乔',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 15
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/15.bmp"),
			'关羽',
			'关羽',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 16
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/16.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 17
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/17.bmp"),
			'张飞',
			'张飞',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 18
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/18.bmp"),
			'关羽',
			'关羽',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 19
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/19.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 20
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
			'魔化吕布',
			'魔化吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		if self.zhanhunFloor == '20层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 21
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/21.bmp"),
			'刘备',
			'刘备',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("21层没打过")
			return True
		if self.zhanhunFloor == '21层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 22
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/22.bmp"),
			'袁绍',
			'袁绍',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("22层没打过")
			return True
		if self.zhanhunFloor == '22层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 23
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/23.bmp"),
			'曹操',
			'曹操',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("23层没打过")
			return True
		if self.zhanhunFloor == '23层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 24
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/24.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("24层没打过")
			return True
		if self.zhanhunFloor == '24层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 25
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
			'魔化吕布',
			'魔化吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("25层没打过")
			return True
		if self.zhanhunFloor == '25层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("serveAssets/images/zhanhun/26.bmp"),
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		# 26
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/26.bmp"),
			'人参娃',
			'人参娃',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		waitForTwoRes = self.waitForTwo(
			'获得铜币',
			'涿郡野外',
			self.gameLocation,
			self.dituLocation,
		)
		if waitForTwoRes == "second":
			print("26层没打过")
			return True
		if self.zhanhunFloor == '26层':
			# 退出副本
			self.outScript('战魂')
			return True
		# 退出副本
		self.outScript('战魂')
		return True

	# 龙王令
	def longwanglingScript(self):
		if self.overed:
			return
		print('开始打龙王令')
		time.sleep(0.3)
		self.dm.KeyPressChar('e')
		self.confidenceNum = 0.7
		self.press_keys_until_image_found(
			f"{self.get_resource_path('serveAssets/images/longwang.bmp')}|{self.get_resource_path('serveAssets/images/longwang1.bmp')}",
			'摘星楼',
			self.gameLocation, self.dituLocation, '使用')
		self.confidenceNum = 0.9
		self.findAndClickPic('摘星楼', self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.dituLocation, '挑战龙', self.gameBottomLocation, '0.167,0.144')
		self.waitForAAndClickB1('修罗级', '挑战龙', self.gameBottomLocation, self.gameBottomLocation)
		self.waitFor('修罗级', self.gameBottomLocation)
		self.waitForAAndClickB1('挑战龙', '修罗级', self.gameBottomLocation, self.gameBottomLocation)
		time.sleep(3)
		self.findAndClickPic('摘星楼', self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.get_resource_path("serveAssets/images/zhengdian/xiaolvren.bmp"), self.dituLocation, '离开', self.gameBottomLocation, '0.167,0.144')
		self.waitForAAndClickB1('修罗级', '离开', self.gameBottomLocation, self.gameBottomLocation)

	# 49一键
	def all49Script(self):
		if self.overed:
			return
		self.richang49Script()
		time.sleep(1)
		self.go_in_ditu('地图野外东', self.get_resource_path("serveAssets/images/zhengdian/zhuojun.bmp"), '涿郡野外', '涿郡野外', '驿站城西')
		time.sleep(1)
		for i in range(6):
			if self.overed:
				return
			self.zhanhun49Script()

	# 引魔符
	def yinmofuScript(self):
		if self.overed:
			return
		print('开始打引魔符')
		time.sleep(0.3)
		self.dm.KeyPressChar('e')
		time.sleep(0.1)
		self.confidenceNum = 0.7
		self.press_keys_until_image_found(
			f"{self.get_resource_path('serveAssets/images/ymf.bmp')}|{self.get_resource_path('serveAssets/images/ymf1.bmp')}",
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLocation,
			self.gameBottomLocation, '使用')
		self.confidenceNum = 0.9
		huodetongbi_pos = self.waitFor('获得铜币', self.gameBottomLocation)
		self.dm.MoveTo(huodetongbi_pos.x, huodetongbi_pos.y)
		time.sleep(0.001)
		self.dm.LeftClick()


class MyFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="梦幻三国脚本", size=(260, 300))
		self.SetIcon(
			wx.Icon(self.get_resource_path("serveAssets/images/script.ico"), wx.BITMAP_TYPE_ICO)
		)
		self.SetPosition(wx.Point(10, 30))
		self.panel = wx.Panel(self)
		# self.SetWindowStyle(wx.STAY_ON_TOP)  # 按钮所在控件一直存在在桌面上
		self.scriptName = ""
		self.heifengCount = 0
		self.zhanhunFloor = ""
		self.heifengFloor = ""
		# size=(226, 26),
		self.button_start = wx.Button(
			self.panel,
			label="开始脚本(F5)",
			pos=(10, 35),
			style=wx.BORDER_NONE,
		)
		self.Bind(wx.EVT_BUTTON, self.button_start_click, self.button_start)
		# 设置按钮背景颜色
		self.button_start.SetBackgroundColour(wx.Colour(20, 180, 168))  # 设置为红色背景
		self.button_start.SetForegroundColour(
			wx.Colour(255, 255, 255)
		)  # 设置为白色文字
		# Stop button
		self.button_stop = wx.Button(self.panel, label="重置脚本(F8)", pos=(146, 35), style=wx.BORDER_NONE)
		self.Bind(wx.EVT_BUTTON, self.button_stop_click, self.button_stop)
		# 设置按钮背景颜色
		self.button_stop.SetBackgroundColour(wx.Colour(144, 144, 153))
		self.button_stop.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字

		# Pause button
		self.button_pause = wx.Button(
			self.panel, label="暂停脚本(F6)", pos=(10, 65), style=wx.BORDER_NONE
		)
		self.Bind(wx.EVT_BUTTON, self.button_pause_click, self.button_pause)
		# 设置按钮背景颜色
		self.button_pause.SetBackgroundColour(wx.Colour(226, 96, 95))
		self.button_pause.SetForegroundColour(
			wx.Colour(255, 255, 255)
		)  # 设置为白色文字

		# Resume button
		self.button_resume = wx.Button(
			self.panel, label="继续脚本(F7)", pos=(146, 65), style=wx.BORDER_NONE
		)
		self.Bind(wx.EVT_BUTTON, self.button_resume_click, self.button_resume)
		# 设置按钮背景颜色
		self.button_resume.SetBackgroundColour(wx.Colour(103, 194, 58))
		self.button_resume.SetForegroundColour(
			wx.Colour(255, 255, 255)
		)  # 设置为白色文字
		self.dropdown = wx.ComboBox(
			self.panel,
			pos=(10, 5),
			size=(135, 30),
			choices=[
				"官渡",
				"魔镜",
				"日常",
				"黑风",
				"矿产",
				"龙岛",
				"龙王令",
				"引魔符",
				"49日常",
				"49战魂",
				"49整点",
				"名将闯关",
				"战魂楼(精英)",
				"嗜血战场(精英)",
				"战魂+红+整点",
				"战魂+红+魔镜+整点",
				# "整点",
				# "测试",
			],
		)
		self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
		self.dropdown.SetHint("选择执行脚本")
		self.text_ctrl = wx.TextCtrl(
			self.panel, pos=(10, 100), size=(225, 130), style=wx.TE_MULTILINE
		)
		self.button = wx.Button(self.panel, label="设置游戏信息", pos=(155, 5), size=(80, 25))
		self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
		self.thread = None
		sys.stdout = self
		self.bind_hotkeys()
		self.help_link = wx.StaticText(self.panel, label="说明", pos=(10, 235), style=wx.ST_NO_AUTORESIZE)
		self.help_link.SetForegroundColour(wx.BLUE)
		self.help_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
		self.help_link.Bind(wx.EVT_LEFT_DOWN, self.on_help_link_click)
		self.contact = wx.StaticText(self.panel, label="交流群（QQ）：955753707", pos=(100, 236), style=wx.ST_NO_AUTORESIZE)
		font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
		self.contact.SetFont(font)
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.game_name = ""
		self.teammate1_name = ""
		self.teammate2_name = ""
		self.selections = ""
		self.mojingFloor = ''
		self.zhengdianFloor = ''
		self.richangSelection = []

	def on_help_link_click(self, event):
		# 定义弹窗的内容和图片路径
		content = [
			"脚本说明：",
			"1.整点'虎+牛+兔+猴+羊'、'牛+虎+兔'在官渡、黑风、魔镜、战魂+红+整点、战魂+红+魔镜+整点的时候可以选择，建议V3玩家使用；",
			"2.整点'虎+猴+羊'在官渡、魔镜、战魂+红+整点、战魂+红+魔镜+整点的时候可以选择，需要在背包当前页左上角放上回城卷，不需要传送鞋；",
			"3.整点'火焰+寒冰'在魔镜的时候可以选择，每次使用一个飞鞋，如果选择'49整点'脚本，在洛阳城西启动；",
			"4.战魂+红+整点内容是一次战魂，((58-完成战魂分钟)/2)次红，一次整点，战魂跟红都没次数之后会自动去官渡(一定每个小时开始启动，到整点会退出副本)，战魂+红+魔镜+整点内容为战魂+红+整点的魔镜平替；",
			"5.黑风/矿产次数填多少次打多少次，打完自动去官渡；",
			"6.日常脚本:溶洞=>炼丹=>五行=>云游精英=>名将挑战=>80精英=>100精英=>红=>战魂=>官渡精英=>官渡；49日常脚本:溶洞=>炼丹=>五行=>名将挑战=>红=>战魂，选择飞就是飞副本，去掉就是跑过去；",
			"7.引魔符、龙王令脚本把引魔符、龙王令放在背包当前页，关闭背包；",
			"8.保存数据不保存日常选择的数据，其他数据都会保存，下次使用脚本直接点击读取即可自动填入；",
			"9.如需要给多开的号卖装备、加血在队友名中填入队友名称，名称为小号列表的名字，并且将多开号拆分出单独窗口并且不被最小化，绑定成功的小号会在队友对话框发送1。",
			"使用说明：",
			"1.第一次脚本需要使用管理员模式开启；",
			"2.脚本启动之前填入游戏名称；",
			"3.请将电脑的屏幕分辨率调到1920*1080；",
			"4.请将电脑的缩放比放到100%；",
			"5.请将游戏画面缩放到900*580，并且关闭小号列表。",
		]
		images = [
		]

		# 打开弹窗
		dialog = HelpDialog(self, "说明", content, images)
		dialog.ShowModal()
		dialog.Destroy()

	def get_resource_path(self, relative_path):
		if hasattr(sys, "_MEIPASS"):
			return os.path.join(sys._MEIPASS, relative_path)
		return os.path.join(os.path.abspath("."), relative_path)

	def on_button_click(self, event):
		dialog = MyDialog(self)
		if dialog.ShowModal() == wx.ID_OK:
			# 在对话框结束后，获取对话框中输入的数据
			print('当前游戏名称：' + self.game_name)
		dialog.Destroy()

	def write(self, text):
		self.text_ctrl.WriteText(text)

	def bind_hotkeys(self):
		keyboard.add_hotkey('F5', self.start_script)
		keyboard.add_hotkey('F6', self.pause_script)
		keyboard.add_hotkey('F7', self.resume_script)
		keyboard.add_hotkey('F8', self.stop_script)

	def start_script(self):
		if self.thread is None or not self.thread.is_alive():
			scriptName = self.scriptName
			self.thread = MyThread(scriptName)
			self.thread.frame = self
			self.thread.overed = False
		if not self.game_name:
			self.thread.show_error_message("请输入游戏名称！")
			return
		if not self.scriptName:
			self.thread.show_error_message("请先选择脚本！")
			return
		print("开始脚本！")
		self.thread.start()

	def pause_script(self):
		if not self.scriptName:
			self.thread.show_error_message("请先选择脚本！")
			return
		print("暂停脚本！")
		if self.thread is not None:
			# paused.set()
			self.thread.stoped = True

	def resume_script(self):
		if not self.scriptName:
			self.thread.show_error_message("请先选择脚本！")
			return
		print("继续执行脚本！")
		if self.thread is not None:
			# paused.clear()
			self.thread.stoped = False
			with condition:
				condition.notify_all()

	def stop_script(self):
		if not self.scriptName:
			return
		# 等待所有线程结束
		if self.thread is not None and self.thread.is_alive():
			print('等待任务结束,请勿重复点击')
			self.thread.overed = True
			self.thread.join()
			if self.thread.child_thread is not None and self.thread.child_thread.is_alive():
				self.thread.child_thread.join()
			if self.thread.win1_thread is not None and self.thread.win1_thread.is_alive():
				self.thread.win1_thread.join()
			if self.thread.win2_thread is not None and self.thread.win2_thread.is_alive():
				self.thread.win2_thread.join()
		print('任务已全部结束')
		self.text_ctrl.SetValue("")
		self.dropdown.SetSelection(-1)
		self.thread.dm.UnBindWindow()
		self.thread = None

	def on_close(self, event):
		self.stop_script()
		self.Destroy()
		wx.Exit()

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
		self.stop_script()


class MyDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="设置游戏信息", size=(300, 230), pos=(260, 30))

		panel = wx.Panel(self)

		self.team_leader_text = wx.TextCtrl(panel, pos=(10, 130), size=(120, 24))
		self.team_leader_text.SetHint("游戏名称")
		self.choiceHeifeng = wx.ComboBox(panel, pos=(10, 40), size=(120, 30), choices=['大/80', '二/50'])
		self.choiceHeifeng.SetHint("黑风/龙岛层数")
		self.team_leader_text.Bind(wx.EVT_TEXT, self.on_text_change)
		self.teammate1_text = wx.TextCtrl(panel, pos=(10, 100), size=(120, 24), )
		self.teammate1_text.SetHint("队友1名称")
		self.teammate2_text = wx.TextCtrl(panel, pos=(150, 100), size=(120, 24), )
		self.teammate2_text.SetHint("队友2名称")
		self.button = wx.Button(panel, label="确定", pos=(10, 160))
		self.button.Disable()  # 初始化时禁用确定按钮
		self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
		self.saveButton = wx.Button(panel, label="保存信息", pos=(100, 160))
		self.saveButton.Bind(wx.EVT_BUTTON, self.on_save_data)
		self.getButton = wx.Button(panel, label="读取信息", pos=(190, 160))
		self.getButton.Bind(wx.EVT_BUTTON, self.get_file_info)
		# 创建一个只能输入数字的文本输入框
		self.number_input = wx.TextCtrl(panel, pos=(150, 40), size=(120, 24), validator=NumberValidator())
		self.number_input.SetHint("黑风/矿产次数")
		self.number_input.Bind(wx.EVT_TEXT, self.on_text_change)
		self.choiceCeng = wx.ComboBox(panel, pos=(150, 70), size=(120, 30), choices=['20层', '21层', '22层', '23层', '24层', '25层', '26层'])
		self.choiceCeng.SetHint("战魂层数")
		self.choiceMojing = wx.ComboBox(panel, pos=(10, 70), size=(120, 30), choices=['迷幻境（虚实）', '狱境（黑白无常）', '炎冰境'])
		self.choiceMojing.SetHint("魔镜层数")
		# '牛+虎+兔+猴+羊',
		self.choiceZhengdian = wx.ComboBox(panel, pos=(150, 130), size=(120, 30), choices=['虎+牛+兔+猴+羊', '牛+虎+兔', '虎+猴+羊', '火焰+寒冰'])
		self.choiceZhengdian.SetHint("整点")
		# 创建多个CheckBox控件，并设置默认勾选状态
		vbox = wx.WrapSizer(wx.HORIZONTAL, wx.VERTICAL)
		self.check_boxes = []
		options = ["溶", "炼丹", "五行", "云游", "名将", "80", "老鼠", '红', '战魂', "官渡", '飞']
		for option in options:
			self.cb = wx.CheckBox(panel, label=option)
			# 设置默认勾选状态
			self.cb.SetValue(True)
			self.check_boxes.append(self.cb)
			vbox.Add(self.cb, 0, flag=wx.LEFT | wx.RIGHT, border=1)
		panel.SetSizer(vbox)

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
	def on_save_data(self, event):
		# 获取用户输入的数据
		selected_options = []
		for cb in self.check_boxes:
			if cb.GetValue():
				selected_options.append(cb.GetLabel())
		game_name = self.team_leader_text.GetValue()
		heifeng_count = self.number_input.GetValue()
		zhanhun_floor = self.choiceCeng.GetValue()
		mojing_floor = self.choiceMojing.GetValue()
		zhengdian_floor = self.choiceZhengdian.GetValue()
		teammate1_text = self.teammate1_text.GetValue()
		teammate2_text = self.teammate2_text.GetValue()

		# 保存数据到文件
		self.save_to_file(game_name, heifeng_count, zhanhun_floor, mojing_floor, zhengdian_floor, teammate1_text, teammate2_text)

	def save_to_file(self, game_name, heifeng_count, zhanhun_floor, mojing_floor, zhengdian_floor, teammate1_text, teammate2_text):
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
		game_name = data.get('game_name', '')
		heifeng_count = data.get('heifeng_count', '')
		zhanhun_floor = data.get('zhanhun_floor', '')
		mojing_floor = data.get('mojing_floor', '')
		zhengdian_floor = data.get('zhengdian_floor', '')
		teammate1_text = data.get('teammate1_text', '')
		teammate2_text = data.get('teammate2_text', '')
		self.team_leader_text.SetValue(game_name)
		self.number_input.SetValue(heifeng_count)
		self.choiceCeng.SetValue(zhanhun_floor)
		self.choiceMojing.SetValue(mojing_floor)
		self.choiceZhengdian.SetValue(zhengdian_floor)
		self.teammate1_text.SetValue(teammate1_text)
		self.teammate2_text.SetValue(teammate2_text)

	def on_text_change(self, event):
		if self.team_leader_text.GetValue():
			self.button.Enable()
		else:
			self.button.Disable()

	def on_button_click(self, event):
		# 获取文本框中的值并保存在父窗口(MyFrame)中
		parent = self.GetParent()
		selected_options = []
		for cb in self.check_boxes:
			if cb.GetValue():
				selected_options.append(cb.GetLabel())
		# selections = [self.checklist.GetString(i) for i in range(self.checklist.GetCount()) if self.checklist.IsChecked(i)]
		parent.game_name = self.team_leader_text.GetValue()
		parent.heifengCount = self.number_input.GetValue() if self.number_input.GetValue() else 0
		parent.zhanhunFloor = self.choiceCeng.GetValue()
		parent.heifengFloor = self.choiceHeifeng.GetValue()
		parent.mojingFloor = self.choiceMojing.GetValue()
		parent.zhengdianFloor = self.choiceZhengdian.GetValue()
		parent.richangSelection = selected_options
		parent.teammate1_name = self.teammate1_text.GetValue()
		parent.teammate2_name = self.teammate2_text.GetValue()
		# parent.selections = selections

		# 关闭对话框
		self.EndModal(wx.ID_OK)


class NumberValidator(wx.Validator):
	def __init__(self):
		wx.Validator.__init__(self)

	def Clone(self):
		return NumberValidator()

	def Validate(self, win):
		text_ctrl = self.GetWindow()
		value = text_ctrl.GetValue()
		if not value.isdigit():
			wx.MessageBox("请输入数字", "错误", wx.OK | wx.ICON_ERROR)
			text_ctrl.SetBackgroundColour("pink")
			text_ctrl.SetFocus()
			text_ctrl.Refresh()
			return False
		else:
			text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
			text_ctrl.Refresh()
			return True

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True


class HelpDialog(wx.Dialog):
	def __init__(self, parent, title, content, images):
		super(HelpDialog, self).__init__(parent, title=title, size=(600, 400), pos=(260, 30))

		panel = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
		panel.SetupScrolling()

		sizer = wx.BoxSizer(wx.VERTICAL)

		# 添加文字内容
		for text in content:
			text_ctrl = wx.StaticText(panel, label=text)
			sizer.Add(text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

		# 添加图片
		for image_path in images:
			image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
			# 获取弹窗的宽度
			dialog_width = self.GetSize().width
			# 计算新的高度以保持宽高比
			original_width = image.GetWidth()
			original_height = image.GetHeight()
			new_height = int((dialog_width / original_width) * original_height)
			# 调整图片宽度为弹窗宽度的100%，高度自适应
			image = image.Scale(dialog_width, new_height, wx.IMAGE_QUALITY_HIGH)
			bitmap = wx.StaticBitmap(panel, -1, image.ConvertToBitmap())
			sizer.Add(bitmap, 0, wx.ALL | wx.CENTER, 5)

		panel.SetSizer(sizer)


if __name__ == "__main__":
	app = wx.App()
	frame = MyFrame()
	frame.Show()
	app.MainLoop()
