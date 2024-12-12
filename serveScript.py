import pyautogui
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
from comtypes.client import CreateObject
import subprocess

pyautogui.PAUSE = 0.005
pyautogui.FAILSAFE = True  # 鼠标光标在屏幕左上角，会导致程序异常，用于终止程序运行。
# 打包命令：pyinstaller -F -w --add-data "images;images" --icon=images\script.ico .\main.py
# pyinstaller main.spec
condition = threading.Condition()


class ResXy:
	def __init__(resInit, x, y):
		resInit.x = x
		resInit.y = y


class MyThread(threading.Thread):
	def __init__(self, scriptName):
		super().__init__()
		self.userInfoMac = ["50-9A-4C-C9-FE-BA"]
		# 烈烈残阳mac：00-E2-69-6A-22-81
		# self.userInfoMac = ["00-E2-69-6A-22-81"]
		# 黑北：E4-60-17-15-B4-73,BC-EC-A0-28-FA-5C
		# self.userInfoMac = ["BC-EC-A0-28-FA-5C"]
		# 山竹:7C-21-4A-48-36-7D
		# self.userInfoMac = ["7C-21-4A-48-36-7D"]
		# 三千梨树：08-8F-C3-75-B5-7A
		# self.userInfoMac = ["08-8F-C3-75-B5-7A"]
		# self.userInfoMac = ["08-8F-C3-75-B5-7A", "14-75-5B-98-DE-89"]
		# self.userInfoMac = ["50-9A-4C-C9-FE-BA"]
		regPath = self.get_resource_path('serveAssets/plugins/RegDll.dll')
		dms = ctypes.windll.LoadLibrary(str(regPath))
		dmPath = self.get_resource_path('serveAssets/plugins/dm.dll')
		# 构建 regsvr32 命令，添加 /s 参数以静默运行
		command = ['regsvr32', '/s', dmPath]
		# 执行命令
		subprocess.run(command, check=True, capture_output=True, text=True)
		dms.DllRegisterServer(dmPath, 0)
		self.dm = CreateObject('dm.dmsoft')
		self.frame = None
		self.zhanhunFloor = ''
		# 创建子线程
		self.child_thread = threading.Thread(target=self.child_task)
		self.guanDuCount = 0
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
		self.stoped = False
		self.zdzdPath = self.get_resource_path("serveAssets/images/zdzd.bmp")
		self.Dx = 0
		self.Dy = 0
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
		self.click_hwnd = 0
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000'

	def run(self):
		# c = wmi.WMI()
		# for item in c.Win32_BaseBoard():
		#     hardware_serial = item.SerialNumber
		self.zhanhunFloor = self.frame.zhanhunFloor
		self.heifengWhileCount = int(self.frame.heifengCount)
		startTime = 1732958685
		# 一个月脚本
		# if time.time() - startTime > self.monthDays:
		# 	print('脚本已过期!')
		# 	return
		# 三天脚本
		# if time.time() - startTime > self.threeDays:
		# 	print('脚本已过期!')
		# 	return
		# 七天脚本
		# if time.time() - startTime > self.oneWeek:
		# 	print('脚本已过期!')
		# 	return
		# 一天脚本
		# if time.time() - startTime > self.oneDay:
		# 	print('脚本已过期!')
		# 	return
		mac_address = self.get_mac_address()
		if mac_address in self.userInfoMac:
			print("已注册用户!")
		else:
			self.show_error_message("未注册用户，请联系管理员")
			return
		print("鼠标放屏幕左上角退出当前脚本")
		isFindGame = self.findGame()
		if not isFindGame:
			return
		self.child_thread.start()
		if self.scriptName == "官渡":
			self.beginFun()
			self.guanduWhile()
		elif self.scriptName == "嗜血战场(精英)":
			self.hongWhile()
		elif self.scriptName == "战魂楼(精英)":
			if not self.zhanhunFloor:
				self.zhanhunFloor = '26层'
				print('未选择层数，自动打26层')
			self.zhanhunWhile()
		elif self.scriptName == "整点":
			self.zhengDian()
		elif self.scriptName == "祭坛魔镜":
			self.mojingWhile()
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
		elif self.scriptName == "黑风山寨":
			self.heifengWhile()
		elif self.scriptName == "名将挑战赛":
			self.mingjiangtiaozhanWhile()
		elif self.scriptName == "战魂+红+官渡+整点":
			self.zhanhunHongGdWhile()
		elif self.scriptName == "官渡精英":
			self.beginFun()
			self.guanduJyScript()
			self.scriptName = "官渡"
			self.guanduWhile()
		elif self.scriptName == "云游精英":
			self.beginFun()
			self.yunyouJyScript()
			self.scriptName = "官渡"
			self.guanduWhile()
		elif self.scriptName == "80精英":
			self.beginFun()
			self.bamenScript()
			self.scriptName = "官渡"
			self.guanduWhile()
		elif self.scriptName == "100精英":
			self.beginFun()
			self.laoshuJyScript()
			self.scriptName = "官渡"
			self.guanduWhile()
		elif self.scriptName == "49黑风山寨":
			self.heifeng49While()
		elif self.scriptName == "49日常":
			self.richang49Script()
		elif self.scriptName == "49战魂":
			self.zhanhun49Script()
		elif self.scriptName == "49祭坛魔镜":
			self.mojing49While()
		elif self.scriptName == "49嗜血战场(精英)":
			self.hong49While()
		elif self.scriptName == "49名将挑战赛":
			self.hong49While()

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
		hwnd = self.dm.FindWindowEx(0, target_window_class, target_window_title)
		if hwnd:
			#
			# 使用 Windows API 的 EnumChildWindows
			user32 = ctypes.WinDLL('user32', use_last_error=True)
			# 获取屏幕分辨率
			screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
			screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度

			def enum_child_proc(hwnd, lParam):
				class_name = self.dm.GetWindowClass(hwnd)
				child_rect = self.dm.GetWindowRect(hwnd)
				if child_rect != 0:
					left, top, right, bottom, isFind = child_rect
					if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
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
		location = self.dm.GetClientSize(self.click_hwnd)
		x, y, res = location
		print(x, y)
		if res == 1:
			print('已找到游戏画面')
		else:
			self.show_error_message("未检测到游戏页面")
			return False
		self.dm.SetDict(0, self.get_resource_path("serveAssets/fonts/guandu.txt"))  # 字库文件路径
		self.locationX = 0
		self.locationY = 0
		self.locationWidth = x
		self.locationHeight = y
		self.locationRightTopX = x * 0.8
		self.locationRightTopY = 0
		self.locationRightTopWidth = x
		self.locationRightTopHeight = int(y * 0.2)
		self.gameLocation = (
			self.locationX,
			self.locationY,
			self.locationWidth,
			self.locationHeight,
		)
		self.gameLeftLocation = (
			self.locationX,
			int(self.locationY + (self.locationHeight * 0.3)),
			int(self.locationWidth * 0.7),
			self.locationHeight
		)
		self.gameRightLocation = (
			int(self.locationX + int(self.locationWidth * 0.3)),
			int(self.locationY + (self.locationHeight * 0.3)),
			self.locationWidth,
			self.locationHeight
		)
		self.gameBottomLocation = (
			self.locationX,
			int(self.locationY + (self.locationHeight * 0.3)),
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
			int(self.locationRightTopX + (self.locationWidth * 0.2 * 0.3)),
			self.locationRightTopY,
			int(self.locationRightTopX + (self.locationWidth * 0.1) + (self.locationWidth * 0.2 * 0.3)),
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
			int(self.locationWidth * 0.5),
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
		types = 'serveAssets' in find
		if not types:
			res = self.find_str(find, region, find_dir)
		else:
			res = self.find_pic(find, region, find_dir)
		return res

	# 找图方法
	def find_pic(self, image_path, image_region, find_dir):
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

	# 图中找图
	def fing_fei_in_image_or_str(self, base, base_region, h, fei_image):
		base_pos = self.find_pic_or_str(base, base_region, 0)
		if not base_pos:
			return False
		find_fei_h = base_pos.y + h
		x1, y1, w1, h1 = base_region
		fei_pox = self.dm.FindPicEx(int(x1), int(y1), int(w1), int(h1), fei_image, "", self.confidenceNum, 0)
		if not fei_pox:
			return False
		fei_pox = fei_pox.split('|')
		res_pos = None
		min_difference = float('inf')  # 初始化为无穷大
		for item in fei_pox:
			parts = item.split(',')
			if len(parts) >= 3:
				try:
					second_value = int(parts[2])
					if second_value <= find_fei_h:
						difference = find_fei_h - second_value
						if difference < min_difference:
							min_difference = difference
							res_pos = item
				except ValueError:
					print(f"无法将 {parts[1]} 转换为整数，跳过该项")
		res_pos = res_pos.split(',')
		posX = int(res_pos[1])
		posY = int(res_pos[2])
		res = ResXy(int(posX), int(posY))
		return res

	def child_task(self):
		while True:
			self.click_image(self.get_resource_path("serveAssets/images/guandu/dialog.bmp"), self.confidenceNum, self.gameBottomLocation)
			self.click_image(self.get_resource_path("serveAssets/images/guandu/dialog1.bmp"), self.confidenceNum, self.gameBottomLocation)
			self.click_image(self.get_resource_path("serveAssets/images/dialog3.bmp"), self.confidenceNum, self.gameBottomLocation)
			self.click_image(self.get_resource_path("serveAssets/images/fubenzudui.bmp"), self.confidenceNum, self.gameBottomLocation)
			# 关闭右边
			self.click_image(
				self.get_resource_path("serveAssets/images/closeRight.bmp"),
				self.confidenceNum,
				self.gameLocation,
			)
			# 点击拒绝
			self.click_image(
				self.get_resource_path("serveAssets/images/jujue.bmp"),
				self.confidenceNum,
				self.gameBottomLocation,
			)
			# 点自动
			if self.scriptName == "官渡" or self.scriptName == "祭坛魔镜":
				self.click_image(
					self.get_resource_path("serveAssets/images/zidong.bmp"),
					self.confidenceNum,
					self.gameBottomLocation,
				)
			time.sleep(0.4)

	def addBloud(self):
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)))
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)))
		self.click_image(self.get_resource_path("serveAssets/images/addBloud.bmp"), self.confidenceNum, (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)))
		self.click_image(self.get_resource_path("serveAssets/images/addBloud1.bmp"), self.confidenceNum, (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)))

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
			self.gameBottomLocation,
			0
		)
		with condition:
			if self.stoped:
				condition.wait()
		if closeTalkXY:
			self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
			for i in range(4):
				time.sleep(0.5)
				self.dm.LeftClick()
		# 关闭右边
		self.click_image(
			self.get_resource_path("serveAssets/images/closeright.bmp"),
			self.confidenceNum,
			self.gameBottomLocation,
		)
		self.click_image(
			self.get_resource_path("serveAssets/images/yincang.bmp"),
			self.confidenceNum,
			self.gameLocation,
		)
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
	def outScript(self, current):
		self.waitFor(current, self.dituLocation)
		with condition:
			if self.stoped:
				condition.wait()
		time.sleep(0.3)
		outX = self.locationWidth * 0.61
		outY = self.locationHeight * 0.077
		self.dm.MoveTo(int(outX), int(outY))
		time.sleep(0.001)
		self.dm.LeftClick()
		locationQueding = self.waitFor(
			self.get_resource_path("serveAssets/images/outFb.bmp"),
			self.gameLocation,
			3,
		)
		if locationQueding:
			self.dm.MoveTo(locationQueding.x, locationQueding.y)
			time.sleep(0.001)
			self.dm.LeftClick()
			huodetongbiLocation = self.waitFor('获得铜币', self.gameLeftLocation, 1)
			if huodetongbiLocation:
				self.dm.MoveTo(huodetongbiLocation.x, huodetongbiLocation.y)
				time.sleep(0.001)
				self.dm.LeftClick()
		else:
			return

	# 飞整点等到打完
	def feiZhengDian(self, fei_image, base_image, scroll_deg):
		findSmallFeiTime = time.time()
		jindutiaoLocation = self.waitFor(
			self.get_resource_path("serveAssets/images/downTalk.bmp"),
			self.talkLocation,
		)
		while not self.find_str(
				fei_image,
				self.talkLocation,
				1
		):
			if time.time() - findSmallFeiTime > 15:
				return
			# 去除获得铜币黑框
			self.click_image(
				'获得铜币',
				self.confidenceNum,
				self.gameBottomLocation,
			)
			with condition:
				if self.stoped:
					condition.wait()
			if jindutiaoLocation:
				self.dm.MoveTo(jindutiaoLocation.x, jindutiaoLocation.y)
				self.dm.WheelUp()
		findShengXiaoTime = time.time()
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			if time.time() - findShengXiaoTime > 5:
				return
			self.shengxiaoLocation = self.fing_fei_in_image_or_str(
				fei_image,
				self.talkLocation,
				50,
				self.get_resource_path("serveAssets/images/fei.bmp")
			)
			if self.shengxiaoLocation:
				break
		feiTime = time.time()
		while not self.find_str(
				base_image,
				self.dituLocation,
				2
		):
			if time.time() - feiTime > 6:
				return
			with condition:
				if self.stoped:
					condition.wait()
			if self.shengxiaoLocation:
				self.dm.MoveTo(self.shengxiaoLocation.x, self.shengxiaoLocation.y)
				time.sleep(0.001)
				self.dm.LeftClick()
				time.sleep(1.3)
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
			return
		zhengdianHas = False
		queryTime = time.time()
		while hasZhengDian:
			with condition:
				if self.stoped:
					condition.wait()
			if time.time() - queryTime > 5:
				zhengdianHas = False
				break
			if self.find_pic(
					self.get_resource_path("serveAssets/images/zdzd.bmp"),
					self.gameBottomLocation, 0
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
		if not zhengdianHas:
			return
		self.waitFor(
			base_image,
			self.dituLocation,
		)

	# 清包
	def clearBag(self):
		self.dm.KeyPressChar('e')
		# bagPos = self.waitFor(self.get_resource_path("serveAssets/images/beibao.bmp"), self.gameBottomLocation)
		# if bagPos:
		# 	self.dm.MoveTo(bagPos.x, bagPos.y)
		# 	time.sleep(0.001)
		# 	self.dm.LeftClick()
		# self.get_resource_path("serveAssets/images/yijianchushou.bmp")
		chushou = self.waitFor('一键出售', self.gameBottomLocation)
		if chushou:
			self.dm.MoveTo(chushou.x, chushou.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(0.5)
		zise = self.waitFor('紫色', self.gameBottomLocation)
		if zise:
			self.dm.MoveTo(zise.x, zise.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(0.5)
		quedingchushou = self.waitFor(self.get_resource_path("serveAssets/images/quedingchushou.bmp"), self.gameBottomLocation)
		if quedingchushou:
			self.dm.MoveTo(quedingchushou.x, quedingchushou.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(0.5)
		self.waitFor(self.get_resource_path("serveAssets/images/closeBag.bmp"), self.gameLocation)
		while self.find_pic(self.get_resource_path("serveAssets/images/closeBag.bmp"), self.gameLocation, 1):
			self.click_image(self.get_resource_path("serveAssets/images/closeBag.bmp"), self.confidenceNum, self.gameLocation)
			time.sleep(0.8)

	# 整点
	def zhengDian(
			self,
	):
		print("打整点")
		with condition:
			if self.stoped:
				condition.wait()
		time.sleep(1.5)
		openTalkXY = self.waitFor(
			self.get_resource_path("serveAssets/images/openTalk.bmp"),
			self.talkLocation
		)
		if openTalkXY:
			self.dm.MoveTo(openTalkXY.x, openTalkXY.y)
			for i in range(4):
				time.sleep(0.2)
				self.dm.LeftClick()
		bangpaiTalkXY = self.waitFor(
			'帮派',
			self.talkLocation,
		)
		if bangpaiTalkXY:
			self.dm.MoveTo(bangpaiTalkXY.x, bangpaiTalkXY.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		huodongTalkXY = self.waitFor(
			'活动',
			self.talkLocation,
		)
		if huodongTalkXY:
			self.dm.MoveTo(huodongTalkXY.x, huodongTalkXY.y)
			time.sleep(0.001)
			self.dm.LeftClick()
		time.sleep(2)
		self.clearBag()
		time.sleep(2)
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			current_time = time.localtime()
			if (current_time.tm_min == 0 and current_time.tm_sec == 0) or (
					current_time.tm_min == 0 and current_time.tm_sec == 1
			):
				break
			time.sleep(1)  # 每秒钟检查一次
		# 飞牛
		self.feiZhengDian(
			'牛',
			'魔魂山',
			350,
		)
		# 飞老虎
		self.feiZhengDian(
			'虎',
			'九黎族祭坛',
			350,
		)
		# 飞兔子
		self.feiZhengDian(
			'兔',
			'徐州',
			200,
		)
		# 飞牛
		self.feiZhengDian(
			'牛',
			'魔魂山',
			300,
		)
		# 飞老虎
		self.feiZhengDian(
			'虎',
			'九黎族祭坛',
			350,
		)
		# 飞兔子
		self.feiZhengDian(
			'兔',
			'徐州',
			200,
		)
		# 飞猴子
		self.feiZhengDian(
			'猴',
			'幽暗密林',
			100,
		)
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
			self.dm.MoveTo(dragBox.x, int(dragBox.y + 150))
			time.sleep(0.001)
			self.dm.LeftUp()
			# 飞羊
			self.feiZhengDian(
				'羊',
				'魔谷西',
				300,
			)
			# 飞猴子
			self.feiZhengDian(
				'猴',
				'幽暗密林',
				350,
			)
			# 飞羊
			self.feiZhengDian(
				'羊',
				'魔谷西',
				350,
			)
		closeTalkXY = self.waitFor(
			self.get_resource_path("serveAssets/images/closetalk.bmp"),
			self.talkLocation,
		)
		if closeTalkXY:
			self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
			for i in range(4):
				time.sleep(0.2)
				self.dm.LeftClick()
		if self.scriptName == "官渡":
			self.feiFb('副本曹操', True)
			self.guanduWhile()

		elif self.scriptName == "祭坛魔镜":
			findMojingshizhe = self.feiFb('副本魔镜使者', False
			                              )
			if findMojingshizhe:
				self.mojingWhile()
			else:
				self.scriptName = "官渡"
				self.feiFb('副本曹操', True)
				self.guanduWhile()
		elif self.scriptName == "战魂+红+整点":
			self.feiFb('副本曹操', True)
			time.sleep(1)
			self.click_image(self.get_resource_path("serveAssets/images/closeBag.bmp"), self.confidenceNum, self.gameLocation)
			time.sleep(1)
			self.feiFb('副本挑战赛', True)
			self.guanduAndHongAndZd()
		elif self.scriptName == "黑风山寨":
			self.feiFb('副本霸山虎', False)
			self.heifengWhile()

	# 飞副本
	def feiFb(self, image_path, isJy):
		# 打开副本
		time.sleep(1.5)
		outX = self.locationWidth * 0.673
		outY = self.locationHeight * 0.077
		self.dm.MoveTo(int(outX), int(outY))
		time.sleep(0.001)
		self.dm.LeftClick()
		self.waitForTwo('精英', '精英1', self.gameLocation)
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
				fei_pos = self.fing_fei_in_image_or_str(image_path, self.gameLocation, 5, self.get_resource_path("serveAssets/images/fubenfei.bmp"))
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
			while not self.find_str(image_path, self.gameLocation, 0):
				downTalk = self.waitFor(
					self.get_resource_path("serveAssets/images/downFb.bmp"),
					(
						self.locationX,
						self.locationY,
						int(self.locationWidth * 0.75),
						self.locationHeight,
					),
				)
				if downTalk:
					self.dm.MoveTo(downTalk.x, downTalk.y)
					for i in range(10):
						time.sleep(0.001)
						self.dm.LeftClick()
					time.sleep(1)
			findPerTime = time.time()
			while True:
				fei_pos = self.fing_fei_in_image_or_str(image_path, self.gameLocation, 5, self.get_resource_path("serveAssets/images/fubenfei.bmp"))
				if fei_pos:
					break
			if fei_pos:
				self.dm.MoveTo(fei_pos.x, fei_pos.y)
				time.sleep(0.001)
				self.dm.LeftClick()
		return True

	# 找图并且点击
	def click_image(self, image_path, image_confidence, image_region, find_dir=0):
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

	# 找一样的字，点击最左边的图
	def click_image_with_min_x(self, image_path, image_region, image_path2, find_dir=0):
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
		if image_path2 == self.zdzdPath:
			self.dm.MoveTo(target.x, int(target.y - yjian))
			time.sleep(0.001)
			self.dm.LeftDoubleClick()
			self.dm.MoveTo(target.x + 200, target.y + 200)
			time.sleep(1)
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
		types = 'serveAssets' in image_path
		target = None
		if not types:
			target = self.find_str(image_path, image_region, find_dir)
			if target:
				target.x = target.x + 25
				target.y = target.y + 5
		else:
			target = self.find_pic(image_path, image_region, find_dir)
			if target:
				self.dm.MoveTo(target.x, target.y)
		if not target:
			return False
		target_x = target.x
		target_y = target.y
		if image_path2 == self.zdzdPath:
			self.dm.MoveTo(target.x, target.y)
			time.sleep(0.001)
			self.dm.LeftDoubleClick()
			self.dm.MoveTo(target.x + 200, target.y + 200)
			time.sleep(1)
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

	# 等待图片出现
	def waitFor(self, image_path, image_region, timeout=None):
		start_time = time.time()
		while True:
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

	# 等待两张图片出现
	def waitForTwo(self, image1_path, image2_path, image_region1, image_region2=None, timeout=None, find_dir=1):
		start_time = time.time()
		res = ""
		if image_region2 is None:
			image_region2 = image_region1
		while True:
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
		if not image_regionB:
			image_regionB = self.gameLocation
		while not self.find_str(find_text, find_region, 0):
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
		if not image_regionB:
			image_regionB = self.gameLocation
		while not self.find_str(image_pathA, image_regionA, 0) or not self.find_str(image_pathA2, image_regionA, 0):
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
			clickB = self.click_image(
				image_pathB2,
				self.confidenceNum,
				image_regionB,
			)
			if clickB:
				break
			time.sleep(0.2)

	# 使用键盘命令找图
	def press_keys_until_image_found(self, image_path, image_path1, image_path2, key1, key2, key2DownTime=0.6):
		key1IsUp = False
		# 去除获得铜币黑框
		# self.click_image(
		# 	self.get_resource_path("images/huodetongbi.png"),
		# 	self.confidenceNum,
		# 	(
		# 		self.locationX,
		# 		self.locationY,
		# 		self.locationWidth,
		# 		self.locationHeight,
		# 	),
		# )
		if key2:
			self.dm.KeyDownChar(key2)
			time.sleep(key2DownTime)
			self.dm.KeyUpChar(key2)
		find_dir = 1 if key1 == 'right' else 2
		while not self.find_pic(image_path2, self.gameBottomLocation, find_dir):
			with condition:
				if self.stoped:
					condition.wait()
			if key1 and not key1IsUp:
				self.dm.KeyDownChar(key1)
				key1IsUp = True
			# 去除获得铜币黑框
			# self.click_image(
			# 	self.get_resource_path("images/huodetongbi.png"),
			# 	self.confidenceNum,
			# 	self.gameBottomLocation,
			# )
			image_pathisOk = self.find_pic(image_path, self.gameBottomLocation, find_dir)
			if image_pathisOk:
				if key1:
					self.dm.KeyUpChar(key1)
					key1IsUp = True
				self.click_image_with_min_x1(
					image_path,
					self.gameBottomLocation,
					image_path2,
					0
				)
			image_path1isOk = self.find_pic(image_path1, self.gameBottomLocation, find_dir)
			if image_path1isOk:
				if key1:
					self.dm.KeyUpChar(key1)
					key1IsUp = True
				self.click_image_with_min_x1(
					image_path1,
					self.gameBottomLocation,
					image_path2,
					0
				)
		# 点过b之后如果过了4秒还没有找到C，重新点一次b的坐标
		if self.clickBTime > 0 and time.time() - self.clickBTime > 4:
			self.dm.MoveTo(self.clickBX, self.clickBy)
			time.sleep(0.001)
			self.dm.LeftClick()
			self.clickBTime = time.time()
		if key1:
			self.dm.KeyUpChar(key1)

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
	def findAndClickPic(self, A, B, B1, B2, C1, C2, D, E=None, E2=None, E2DownTime=0.6):
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
			if time.localtime().tm_min == 58:
				if self.scriptName == "官渡" or self.scriptName == "祭坛魔镜" or self.scriptName == "黑风山寨":
					# 打整点
					self.outScript(A)
					self.zhengDian()
					return
			# # 去除获得铜币黑框
			self.click_image(
				'获得铜币',
				self.confidenceNum,
				self.gameLeftLocation,
			)
			# 按下E2
			if E2 and not E2IsDown:
				self.dm.KeyDownChar(E2)
				E2IsDown = True
				time.sleep(E2DownTime)
				self.dm.KeyUpChar(E2)
			# 开始找C的时间
			startTime = time.time()
			find_dir = 2 if E == 'left' else 1
			while not self.find_pic_or_str(C1, C2, find_dir):
				with condition:
					if self.stoped:
						condition.wait()
				if time.time() - startTime > 20:
					if self.scriptName == "官渡":
						print("超过20s没找到目标,重新进入官渡")
						self.outScript(A)
						self.guanduWhile()
						return
					elif self.scriptName == "祭坛魔镜":
						print("超过20s没找到目标,重新进入魔镜")
						self.outScript(A)
						self.mojingWhile()
						return
					elif self.scriptName == "黑风山寨":
						print("超过20s没找到目标,重新进入黑风")
						self.outScript(A)
						self.heifengWhile()
						return
				#   D找图片D点击
				if D and self.clickBTime == 0 and not self.find_pic_or_str(B, B2, find_dir) and not self.find_pic_or_str(B1, B2, find_dir):
					with condition:
						if self.stoped:
							condition.wait()
					d_pos = D.split(',')
					d_pos[0] = (1000 - int(float(d_pos[0]) * 1000)) / 1000 * self.locationWidth
					d_pos[1] = (int(float(d_pos[1]) * 1000)) / 1000 * self.locationHeight
					self.dm.MoveToEx(int(d_pos[0]), int(d_pos[1]), 3, 2)
					time.sleep(0.001)
					self.dm.LeftClick()
					time.sleep(0.3)
				if self.find_pic_or_str(C1, C2, find_dir):
					break
				while E != "" and not EIsDown and not self.find_pic_or_str(B, B2, find_dir) and not self.find_pic_or_str(B1, B2, find_dir):
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
					print('click')
					self.dm.MoveTo(self.clickBX, self.clickBy)
					time.sleep(0.001)
					self.dm.LeftClick()
					self.clickBTime = time.time()
		except Exception as e:
			self.show_error_message(f"发生错误: {e}")

	# 官渡脚本
	def guanduScript(self):
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
			'0.038,0.134',
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入第一层
		self.waitForAAndClickB1(
			'曹操大帐',
			'进入',
			self.dituLocation, self.gameLeftLocation,
		)
		self.waitFor('曹操大帐', self.dituLocation, 5)
		with condition:
			if self.stoped:
				condition.wait()
		self.waitForAAndClickB1(
			'曹袁战场',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)

		with condition:
			if self.stoped:
				condition.wait()
		# 第一个河北军
		hbjLocations = ['0.163,0.122', '0.141,0.122', '0.116,0.127', '0.085,0.118', '0.066,0.117', '0.044,0.12']
		for i in range(6):
			self.findAndClickPic(
				'曹袁战场',
				'河北军',
				f"{self.get_resource_path('serveAssets/images/guandu/hbj2.bmp')}|{self.get_resource_path('serveAssets/images/guandu/hbj1.bmp')}",
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				hbjLocations[i],
				"",
			)
		# 颜良
		# 0.091,0.118
		self.findAndClickPic(
			'曹袁战场',
			self.get_resource_path('serveAssets/images/guandu/yanliang.bmp'),
			f"{self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.097,0.124",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 文丑
		self.findAndClickPic(
			'曹袁战场',
			self.get_resource_path('serveAssets/images/guandu/wenchou.bmp'),
			f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.081,0.122",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 去大帐
		self.waitForAAndClickB1(
			'曹操大帐',
			self.get_resource_path("serveAssets/images/guandu/guandu1chuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor('曹操大帐', self.dituLocation)
		with condition:
			if self.stoped:
				condition.wait()
		# 找到曹操进入乌巢
		self.waitForAAndClickB1(
			'知道了',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.gameLeftLocation, self.dituLocation,
		)
		with condition:
			if self.stoped:
				condition.wait()
		self.waitForAAndClickB1(
			'鸟巢粮仓',
			'知道了',
			self.dituLocation, self.gameLeftLocation,
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入魂殿打魂
		# 0.161,0.106
		self.findAndClickPic(
			'鸟巢粮仓',
			'文丑之魂',
			'文丑之魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"",
			"left",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 魂殿进乌巢
		self.waitForAAndClickB1(
			'鸟巢粮仓',
			self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 打淳
		self.findAndClickPic(
			'鸟巢粮仓',
			'淳于琼',
			f"{self.get_resource_path('serveAssets/images/guandu/cyq1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/cyq2.bmp')}",
			self.gameLeftLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 打袁绍
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
		# 进入红
		self.findAndClickPic(
			'虎牢关外',
			self.get_resource_path("serveAssets/images/hong/hongdianweiditu.bmp"),
			self.get_resource_path("serveAssets/images/hong/hongdianwei.bmp"),
			self.gameLocation,
			'嗜血战场',
			self.gameBottomLocation,
			"0.123,0.12"
		)
		self.waitForAAndClickB1(
			'军营',
			'嗜血战场',
			self.dituLocation, self.gameBottomLocation,
		)
		isInHong = self.waitFor('军营', self.dituLocation, 5)
		if not isInHong:
			print('红没次数了')
			return False
		# 第一层
		gonbin_poss = ['0.121,0.125', '0.064,0.125', '0.036,0.12']
		for i in range(3):
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
		self.waitForAAndClickB1(
			'军粮营',
			self.get_resource_path("serveAssets/images/hong/chuansongmen1.bmp"),
			self.dituLocation, self.dituLeftLocation,
		)
		self.waitFor('军粮营', self.dituLocation)
		# 第二层
		huweibin_poss = ['0.144,0.124', '0.1,0.118', '0.035,0.124']
		for i in range(2):
			self.findAndClickPic(
				'军粮营',
				'护卫兵',
				f"{self.get_resource_path('serveAssets/images/hong/huweibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huweibin2.bmp')}",
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				huweibin_poss[i],
			)
		self.findAndClickPic(
			'军粮营',
			'护粮将领',
			f"{self.get_resource_path('serveAssets/images/hong/huliangjianglin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/huliangjianglin2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			huweibin_poss[2],
		)
		# 进入训兵营
		self.waitForAAndClickB1(
			'训兵营',
			self.get_resource_path("serveAssets/images/chuansongmen.bmp"),
			self.dituLocation, self.dituRightLocation,
		)
		# 第二层
		qibin_poss = ['0.136,0.112', '0.104,0.148', '0.06,0.124', '0.121,0.131']
		for i in range(3):
			self.findAndClickPic(
				'训兵营',
				'骑兵',
				f"{self.get_resource_path('serveAssets/images/hong/qibin1.bmp')}|{self.get_resource_path('serveAssets/images/hong/qibin2.bmp')}",
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				qibin_poss[i],
			)
		self.findAndClickPic(
			'训兵营',
			self.get_resource_path('serveAssets/images/hong/xunbinjiangling.bmp'),
			f"{self.get_resource_path('serveAssets/images/hong/shenjinxi1.bmp')}|{self.get_resource_path('serveAssets/images/hong/shenjinxi2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			qibin_poss[3],
		)
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
			'战魂',
			'战魂楼',
			self.dituLocation, self.gameBottomLocation,
		)
		isInZhanhun = self.waitFor('战魂', self.dituLocation, 5)
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
			'张梁',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'张角',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'文丑',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'颜良',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'华雄',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'孙策',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'典韦',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'郭嘉',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'刘备',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'曹操',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'袁绍',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'张飞',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'大乔',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'关羽',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'吕布',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'张飞',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'关羽',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'吕布',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'吕布',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
		)
		# 20
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/20.bmp"),
			'吕布',
			'吕布',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.098,0.113"
		)
		self.waitForAAndClickB1(
			'刘备',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'袁绍',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'曹操',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'吕布',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
			'吕布',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
		)
		# 25
		self.findAndClickPic(
			self.get_resource_path("serveAssets/images/zhanhun/25.bmp"),
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
			print("25层没打过")
			return True
		if self.zhanhunFloor == '25层':
			# 退出副本
			self.outScript('战魂')
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			'人参娃',
			self.get_resource_path("serveAssets/images/zhanhun/chuansongmen.bmp"),
			self.gameBottomLocation, self.dituLocation,
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
		self.mojingCount += 1
		print(f"第{self.mojingCount}次魔镜.")
		isInGuanDu = self.waitFor('城西', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本魔镜使者', False)
		# 进入魔镜
		self.findAndClickPic(
			'城西',
			self.get_resource_path("serveAssets/images/mojing/mojingshizhe.bmp"),
			self.get_resource_path("serveAssets/images/mojing/mojingshizhe1.bmp"),
			self.gameBottomLocation,
			'进入',
			self.gameBottomLocation,
			"",
		)
		self.waitForAAndClickB1(
			'镜像地层',
			'进入',
			self.dituLocation,
			self.gameBottomLocation,
		)
		isInMojing = self.waitFor('镜像地层', self.dituLocation, 5)
		if not isInMojing:
			print('魔镜没了')
			return False
		# 打一个第一层的怪
		self.findAndClickPic(
			'镜像地层',
			'吃人妖',
			'吃人妖',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 进入第二层
		self.waitForAAndClickB1(
			'进入',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.gameBottomLocation, self.dituLocation,
		)
		self.findAndClickPic(
			'镜像地层',
			'进入',
			'知道了',
			self.gameBottomLocation,
			'遗迹镜像',
			self.dituLocation,
			"",
		)
		# 打狮王
		self.findAndClickPic(
			'遗迹镜像',
			'狮王魂',
			'狮王魂',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 进入第三层
		self.waitForAAndClickB1(
			'进入',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.gameBottomLocation, self.dituLocation,
		)
		self.findAndClickPic(
			'遗迹镜像',
			'进入',
			'知道了',
			self.gameBottomLocation,
			'迷幻境',
			self.dituLocation,
			"",
		)
		# 打虚实
		self.findAndClickPic(
			'迷幻境',
			'虚',
			'虚',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		self.findAndClickPic(
			'迷幻境',
			'实',
			'实',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 进入第四层
		self.waitForAAndClickB1(
			'进入',
			self.get_resource_path("serveAssets/images/xiaolvren.bmp"),
			self.gameBottomLocation, self.dituLocation,
		)
		self.findAndClickPic(
			'迷幻境',
			'进入',
			'知道了',
			self.gameBottomLocation,
			'狱境',
			self.dituLocation,
			"",
		)
		# 打黑白无常
		self.findAndClickPic(
			'狱境',
			'白无常',
			'白无常',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		self.findAndClickPic(
			'狱境',
			'黑无常魔镜',
			'黑无常魔镜',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"",
		)
		# 退出副本
		self.outScript('狱境')
		return True

	# 炼丹脚本
	def liandanScript(self):
		print('开始炼丹房')
		isInGuanDu = self.waitFor('五指峡谷', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本南华老人', False)
		# 进入炼丹
		# 0.164,0.131
		self.findAndClickPic(
			'五指峡谷',
			self.get_resource_path("serveAssets/images/richang/nanhualaoren.bmp"),
			self.get_resource_path("serveAssets/images/richang/nanhualaoren.bmp"),
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
		isInHong = self.waitFor('南天门', self.dituLocation, 5)
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
		liandan1_poss = ['0.155,0.151', '0.135,0.12', '0.155,0.151', '0.135,0.12', '0.155,0.151']
		for i in range(5):
			self.findAndClickPic(
				'炼丹房',
				'炼丹童',
				'炼丹童',
				self.gameBottomLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
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
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				liandan2_poss[i],
			)
		# 退出副本
		self.outScript('炼丹房')
		return True

	# 五行脚本
	def wuxingScript(self):
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
		isInMojing = self.waitFor('五行圣殿', self.dituLocation, 5)
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
		print('开始溶洞')
		isInGuanDu = self.waitFor('绿林路', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本龙天啸', False)
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
		isInMojing = self.waitFor('遗忘之林', self.dituLocation, 5)
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
			self.dituLeftLocation,
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
		isInMojing = self.waitFor('魔岛入口', self.dituLocation, 5)
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
		self.waitForAAndClickB1(
			'地牢二层',
			self.get_resource_path("serveAssets/images/richang/dilaochuansongmen.bmp"),
			self.dituLocation,
			self.dituRightLocation
		)
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
			'0.117,0.124'
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
			'官渡文丑',
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
			self.get_resource_path("serveAssets/images/guandu/guandu1chuansongmen.bmp"),
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
			"",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 打袁绍
		self.findAndClickPic(
			'粮仓',
			'官渡袁绍',
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
			self.get_resource_path("serveAssets/images/guandu/hundianchuansongmen.bmp"),
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
		self.waitForAAndClickB1(
			'云端',
			self.get_resource_path("serveAssets/images/richang/tianjiechuansongmen.bmp"),
			self.dituLocation, self.dituLocation,
		)
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
			'巨灵神1',
			'巨灵神1',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.1,0.115",
		)
		# 退出副本
		self.outScript('云端')
		return True

	# 100精英
	def laoshuJyScript(self):
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
		isInMojing = self.waitFor('鼠穴入口', self.dituLocation)
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
			self.dituLocation, self.dituLeftLocation,
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
			self.dituLeftLocation,
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
		isInZhanhun = self.waitFor('武神殿', self.dituLocation, 5)
		if not isInZhanhun:
			print('名将没次数了')
			return False
		# 打刘备
		self.findAndClickPic(
			'武神殿',
			self.get_resource_path("serveAssets/images/richang/mingjiangliubei2.bmp"),
			self.get_resource_path("serveAssets/images/richang/mingjiangliubei2.bmp"),
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
			self.get_resource_path("serveAssets/images/richang/mingjiangzhangfei1.bmp"),
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
			self.get_resource_path("serveAssets/images/richang/mingjiangguanyu1.bmp"),
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
			self.get_resource_path("serveAssets/images/richang/mingjianglvbu1.bmp"),
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
		chanchu_pos = ['0.14,0.119', '0.121,0.112', '0.104,0.103', '0.078,0.108', '0.067,0.118', '0.046,0.106', '0.038,0.113']
		for i in range(7):
			self.findAndClickPic(
				'天外天',
				'地穴蟾蜍',
				'地穴蟾蜍',
				self.gameLocation,
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
		self.beginFun()
		for i in range(8):
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break
		self.scriptName = '官渡'
		self.guanduWhile()

	# 黑风
	def heifengScript(self):
		self.heifengCount += 1
		print(f"第{self.heifengCount}次黑风.")
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor('五层', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本霸山虎', False)
		# 进入黑风
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
		daozei_poss = ['0.041,0.118', '0.08,0.124', '0.1,0.117', '0.116,0.127']
		for i in range(4):
			self.findAndClickPic(
				'黑风山寨',
				'刀贼',
				f"{self.get_resource_path('serveAssets/images/heifeng/daozei1.bmp')}|{self.get_resource_path('serveAssets/images/heifeng/daozei2.bmp')}",
				self.gameRightLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameBottomLocation,
				daozei_poss[i]
			)
		# 81  72
		self.findAndClickPic(
			'黑风山寨',
			'刀贼头目',
			'刀贼头目',
			self.gameRightLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			'0.153,0.12'
		)
		# 进入第二层
		self.waitForAAndClickB1(
			'山寨本营',
			self.get_resource_path("serveAssets/images/heifeng/heifeng1chuansongmen.bmp"),
			self.dituLocation,
			self.dituLeftLocation
		)
		self.waitFor('山寨本营', self.dituLocation)
		#
		print(self.dituCenterLocation)
		self.waitForAAndClickB1(
			'山寨内堂',
			self.get_resource_path("serveAssets/images/heifeng/chuansongmen2.bmp"),
			self.dituLocation,
			self.dituCenterLocation
		)
		# 打二当家
		self.findAndClickPic(
			'山寨内堂',
			'二当家',
			'二当家',
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameBottomLocation,
			"0.127,0.141",
		)
		# 退出副本
		self.outScript('山寨内堂')
		return True

	def heifengWhile(self):
		self.beginFun()
		guaiwugongjiLocation = pyautogui.locateOnScreen(self.get_resource_path("images/heifeng/guaiwugongji.png"), confidence=self.confidenceNum, region=self.gameLocation)
		if guaiwugongjiLocation:
			self.click_image(self.get_resource_path("images/heifeng/check.png"), self.confidenceNum, (guaiwugongjiLocation.left, guaiwugongjiLocation.top, guaiwugongjiLocation.width, guaiwugongjiLocation.height))
		for i in range(self.heifengWhileCount):
			self.heifengScript()
			if self.heifengCount == self.heifengWhileCount:
				break
		print(f"{self.heifengWhileCount}次黑风已完成,去官渡")
		self.guanduWhile()

	# 一直执行官渡
	def guanduWhile(self):
		while True:
			self.guanduScript()

	# 一直执行红
	def hongWhile(self):
		self.beginFun()
		for i in range(7):
			hongRes = self.hongScript()
			if not hongRes:
				print('红没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一直执行战魂
	def zhanhunWhile(self):
		self.beginFun()
		for i in range(6):
			zhanhunRes = self.zhanhunScript()
			if not zhanhunRes:
				print('战魂没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一直执行魔镜
	def mojingWhile(self):
		self.beginFun()
		while True:
			overMojing = self.mojingScript()
			if not overMojing:
				print('魔镜没次数')
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 一次战魂一次红+整点
	def guanduAndHongAndZd(self):
		self.beginFun()
		self.zhanhunScript()
		time.sleep(1)
		self.feiFb('副本典韦', True)
		toZhengdianTime = 59 - time.localtime().tm_min
		if 10 <= toZhengdianTime < 20:
			hongOver = self.hongScript()
			if not hongOver:
				self.guanduWhile()
		elif toZhengdianTime >= 20:
			for i in range(2):
				hongOver = self.hongScript()
				if not hongOver:
					self.guanduWhile()
		elif toZhengdianTime < 10:
			self.guanduWhile()
		time.sleep(1)
		self.guanduWhile()
		self.zhengDian()

	# 日常一条龙
	def richangeScript(self):
		print('日常')
		self.beginFun()
		# 飞炼丹
		isInGuanDu = self.waitFor('五指峡谷', self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本南华老人', False)
		for i in range(5):
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		time.sleep(2)
		# 飞溶洞
		self.feiFb('副本龙天啸', False)
		time.sleep(1)
		for i in range(3):
			hasRongdong = self.rongdongScript()
			if not hasRongdong:
				break
		# 飞五行
		self.feiFb('副本老板', True)
		time.sleep(1)
		for i in range(3):
			hasWuxing = self.wuxingScript()
			if not hasWuxing:
				break
		# 飞名将挑战赛
		time.sleep(2)
		self.feiFb('副本挑战赛', True)
		time.sleep(1)
		for i in range(8):
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break
		time.sleep(2)
		# 飞80精英
		self.feiFb('副本分身', True)
		time.sleep(1)
		self.bamenScript()
		time.sleep(2)
		# 飞云游精英
		self.feiFb('副本仙人', True)
		time.sleep(1)
		self.yunyouJyScript()
		time.sleep(1)
		# 飞100精英
		self.feiFb('副本猎鼠人', True)
		time.sleep(1)
		self.laoshuJyScript()
		time.sleep(2)
		# 飞官渡精英
		self.feiFb('副本曹操', True)
		time.sleep(1)
		self.guanduJyScript()
		self.scriptName = "官渡"
		self.guanduWhile()

	# 五行
	def wuxingWhile(self):
		self.beginFun()
		for i in range(3):
			hasWuxing = self.wuxingScript()
			if not hasWuxing:
				break
		self.guanduWhile()

	# 溶洞
	def rongdongWhile(self):
		self.beginFun()
		for i in range(3):
			hasRongdong = self.rongdongScript()
			if not hasRongdong:
				break
		self.guanduWhile()

	# 炼丹
	def liandanWhile(self):
		self.beginFun()
		for i in range(5):
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		self.scriptName = "官渡"
		self.guanduWhile()

	# 战魂红官渡
	def zhanhunHongGdWhile(self):
		self.beginFun()
		for i in range(7):
			hasHong = self.hongScript()
			if not hasHong:
				break
		self.feiFb('副本典韦', True)
		for i in range(6):
			hasZhanhun = self.zhanhunScript()
			if not hasZhanhun:
				break
		self.feiFb('副本曹操', True)
		self.scriptName = "官渡"
		while True:
			self.guanduScript()

	# 49黑风
	def heifeng49While(self):
		self.beginFun()
		for i in range(self.heifengWhileCount):
			self.heifengScript()
			if self.heifengCount == self.heifengWhileCount:
				break
		print(f"{self.heifengWhileCount}次黑风已完成")

	# 49日常
	def richang49Script(self):
		print('日常')
		self.beginFun()
		# 飞炼丹
		isInGuanDu = self.waitFor(self.get_resource_path("images/liandan/wuzhixiagu.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb('副本南华老人', False)
		for i in range(5):
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		# 飞五行
		self.feiFb('副本老板', True)
		time.sleep(1)
		for i in range(3):
			hasWuxing = self.wuxingScript()
			if not hasWuxing:
				break
		# 飞溶洞
		self.feiFb('副本龙天啸', False)
		time.sleep(1)
		for i in range(3):
			hasRongdong = self.rongdongScript()
			if not hasRongdong:
				break

	# 49战魂
	def zhanhun49Script(self):
		print("开始49战魂")
		with condition:
			if self.stoped:
				condition.wait()
		# 进入战魂
		self.findAndClickPic(
			self.get_resource_path("images/40/zhuojunyewaidong.png"),
			self.get_resource_path("images/40/qinshoujiang.png"),
			self.get_resource_path("images/40/qinshoujiang.png"),
			self.get_resource_path("images/40/inzhanhun.png"),
			self.get_resource_path("images/40/inzhanhun.png"),
			"",
			"down",
		)
		# 点击进入战魂
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
			self.get_resource_path("images/40/inzhanhun.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), None,
		)
		isInZhanhun = self.waitFor(self.get_resource_path("images/zhanhun/zhanhunlou1.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInZhanhun:
			print('战魂没次数了')
			return False
		# 1
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
			self.get_resource_path("images/zhanhun/zhangbao.png"),
			self.get_resource_path("images/zhanhun/zhangbao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/zhangliang.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
		# 	self.get_resource_path("images/zhanhun/go2.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/zhangliang.png"),
		# 	self.get_resource_path("images/zhanhun/zhangliang.png"),
		# 	"",
		# 	"right",
		# )
		# 2
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
			self.get_resource_path("images/zhanhun/zhangliang.png"),
			self.get_resource_path("images/zhanhun/zhangliang.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/zhangjiao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
		# 	self.get_resource_path("images/zhanhun/go3.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/zhangjiao.png"),
		# 	self.get_resource_path("images/zhanhun/zhangjiao.png"),
		# 	"",
		# 	"right",
		# )
		# 3
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou3.png"),
			self.get_resource_path("images/zhanhun/zhangjiao.png"),
			self.get_resource_path("images/zhanhun/zhangjiao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/wenchou.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou3.png"),
		# 	self.get_resource_path("images/zhanhun/go4.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/wenchou.png"),
		# 	self.get_resource_path("images/zhanhun/wenchou.png"),
		# 	"",
		# 	"right",
		# )
		# 4
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou4.png"),
			self.get_resource_path("images/zhanhun/wenchou.png"),
			self.get_resource_path("images/zhanhun/wenchou1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/yanliang.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou4.png"),
		# 	self.get_resource_path("images/zhanhun/go5.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/yanliang.png"),
		# 	self.get_resource_path("images/zhanhun/yanliang.png"),
		# 	"",
		# 	"right",
		# )
		# 5
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou5.png"),
			self.get_resource_path("images/zhanhun/yanliang.png"),
			self.get_resource_path("images/zhanhun/yanliang2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/huaxiong.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou5.png"),
		# 	self.get_resource_path("images/zhanhun/go6.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/huaxiong.png"),
		# 	self.get_resource_path("images/zhanhun/huaxiong.png"),
		# 	"",
		# 	"right",
		# )
		# 6
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou6.png"),
			self.get_resource_path("images/zhanhun/huaxiong.png"),
			self.get_resource_path("images/zhanhun/huaxiong2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/sunce.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou6.png"),
		# 	self.get_resource_path("images/zhanhun/go7.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/sunce.png"),
		# 	self.get_resource_path("images/zhanhun/sunce.png"),
		# 	"",
		# 	"right",
		# )
		# 7
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou7.png"),
			self.get_resource_path("images/zhanhun/sunce.png"),
			self.get_resource_path("images/zhanhun/sunce2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/dianwei.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou7.png"),
		# 	self.get_resource_path("images/zhanhun/go8.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/dianwei.png"),
		# 	self.get_resource_path("images/zhanhun/dianwei.png"),
		# 	"",
		# 	"right",
		# )
		# 8
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou8.png"),
			self.get_resource_path("images/zhanhun/dianwei.png"),
			self.get_resource_path("images/zhanhun/dianwei2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/guojia.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou8.png"),
		# 	self.get_resource_path("images/zhanhun/go9.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/guojia.png"),
		# 	self.get_resource_path("images/zhanhun/guojia.png"),
		# 	"",
		# 	"right",
		# )
		# 9
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou9.png"),
			self.get_resource_path("images/zhanhun/guojia.png"),
			self.get_resource_path("images/zhanhun/guojia2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/liubei.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou9.png"),
		# 	self.get_resource_path("images/zhanhun/go10.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/liubei.png"),
		# 	self.get_resource_path("images/zhanhun/liubei.png"),
		# 	"",
		# 	"right",
		# )
		# 10
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou10.png"),
			self.get_resource_path("images/zhanhun/liubei.png"),
			self.get_resource_path("images/zhanhun/liubei2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/caocao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou10.png"),
		# 	self.get_resource_path("images/zhanhun/go11.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/caocao.png"),
		# 	self.get_resource_path("images/zhanhun/caocao.png"),
		# 	"",
		# 	"right",
		# )
		# 11
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou11.png"),
			self.get_resource_path("images/zhanhun/caocao.png"),
			self.get_resource_path("images/zhanhun/caocao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/yuanshao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou11.png"),
		# 	self.get_resource_path("images/zhanhun/go12.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/yuanshao.png"),
		# 	self.get_resource_path("images/zhanhun/yuanshao.png"),
		# 	"",
		# 	"right",
		# )
		# 12
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou12.png"),
			self.get_resource_path("images/zhanhun/yuanshao.png"),
			self.get_resource_path("images/zhanhun/yuanshao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/zhangfei.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou12.png"),
		# 	self.get_resource_path("images/zhanhun/go13.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/zhangfei.png"),
		# 	self.get_resource_path("images/zhanhun/zhangfei.png"),
		# 	"",
		# 	"right",
		# )
		# 13
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou13.png"),
			self.get_resource_path("images/zhanhun/zhangfei.png"),
			self.get_resource_path("images/zhanhun/zhangfei2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/daqiao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou13.png"),
		# 	self.get_resource_path("images/zhanhun/go14.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/daqiao.png"),
		# 	self.get_resource_path("images/zhanhun/daqiao.png"),
		# 	"",
		# 	"right",
		# )
		# 14
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou14.png"),
			self.get_resource_path("images/zhanhun/daqiao.png"),
			self.get_resource_path("images/zhanhun/daqiao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/guanyu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou14.png"),
		# 	self.get_resource_path("images/zhanhun/go15.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/guanyu.png"),
		# 	self.get_resource_path("images/zhanhun/guanyu.png"),
		# 	"",
		# 	"right",
		# )
		# 15
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou15.png"),
			self.get_resource_path("images/zhanhun/guanyu.png"),
			self.get_resource_path("images/zhanhun/guanyu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/lvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou15.png"),
		# 	self.get_resource_path("images/zhanhun/go16.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/lvbu.png"),
		# 	self.get_resource_path("images/zhanhun/lvbu.png"),
		# 	"",
		# 	"right",
		# )
		# 16
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou16.png"),
			self.get_resource_path("images/zhanhun/lvbu.png"),
			self.get_resource_path("images/zhanhun/lvbu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou16.png"),
		# 	self.get_resource_path("images/zhanhun/go17.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
		# 	self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
		# 	"",
		# 	"right",
		# )
		# 17
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou17.png"),
			self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
			self.get_resource_path("images/zhanhun/mohuazhangfei2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou17.png"),
		# 	self.get_resource_path("images/zhanhun/go18.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
		# 	self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
		# 	"",
		# 	"right",
		# )
		# 18
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou18.png"),
			self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
			self.get_resource_path("images/zhanhun/mohuaguanyu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou18.png"),
		# 	self.get_resource_path("images/zhanhun/go19.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	"",
		# 	"right",
		# )
		# 19
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou19.png"),
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/zhanhun/mohualvbu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou19.png"),
		# 	self.get_resource_path("images/zhanhun/go20.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	"",
		# 	"right",
		# )
		# 20
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou20.png"),
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/zhanhun/mohualvbu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/liubei.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou20.png"),
		# 	self.get_resource_path("images/zhanhun/go21.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/liubei.png"),
		# 	self.get_resource_path("images/zhanhun/liubei.png"),
		# 	"",
		# 	"right",
		# )
		# 21
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
			self.get_resource_path("images/zhanhun/liubei.png"),
			self.get_resource_path("images/zhanhun/liubei2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("21层没打过")
			return True
		if self.zhanhunFloor == '21层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou21.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/yuanshao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
		# 	self.get_resource_path("images/zhanhun/go22.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/yuanshao.png"),
		# 	self.get_resource_path("images/zhanhun/yuanshao.png"),
		# 	"",
		# 	"right",
		# )
		# 22
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
			self.get_resource_path("images/zhanhun/yuanshao.png"),
			self.get_resource_path("images/zhanhun/yuanshao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("22层没打过")
			return True
		if self.zhanhunFloor == '22层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou22.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/caocao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
		# 	self.get_resource_path("images/zhanhun/go23.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/caocao.png"),
		# 	self.get_resource_path("images/zhanhun/caocao.png"),
		# 	"",
		# 	"right",
		# )
		# 23
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
			self.get_resource_path("images/zhanhun/caocao.png"),
			self.get_resource_path("images/zhanhun/caocao2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("23层没打过")
			return True
		if self.zhanhunFloor == '23层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou23.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/lvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
		# 	self.get_resource_path("images/zhanhun/go24.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/lvbu.png"),
		# 	self.get_resource_path("images/zhanhun/lvbu.png"),
		# 	"",
		# 	"right",
		# )
		# 24
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
			self.get_resource_path("images/zhanhun/lvbu.png"),
			self.get_resource_path("images/zhanhun/lvbu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("24层没打过")
			return True
		if self.zhanhunFloor == '24层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou24.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
		# 	self.get_resource_path("images/zhanhun/go25.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	self.get_resource_path("images/zhanhun/mohualvbu.png"),
		# 	"",
		# 	"right",
		# )
		# 25
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/zhanhun/mohualvbu2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("25层没打过")
			return True
		if self.zhanhunFloor == '25层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou25.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/renshengwa.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.gameBottomLocation, self.dituLocation,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
		# 	self.get_resource_path("images/zhanhun/go26.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
		# 	self.get_resource_path("images/zhanhun/renshengwa.png"),
		# 	self.get_resource_path("images/zhanhun/renshengwa.png"),
		# 	"",
		# 	"right",
		# )
		# 26
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/zhanhunlou26.png"),
			self.get_resource_path("images/zhanhun/renshengwa.png"),
			self.get_resource_path("images/zhanhun/renshengwa2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/zhanhunlou26.png"),
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		if waitForTwoRes == "second":
			print("26层没打过")
			return True
		if self.zhanhunFloor == '26层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou26.png"))
			return True
		# 退出副本
		self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou26.png"))
		return True

	# 49天外天
	def mingjiangtiaozhan49While(self):
		self.beginFun()
		for i in range(8):
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break

	# 49红
	def hong49While(self):
		self.beginFun()
		for i in range(7):
			hongRes = self.hongScript()
			if not hongRes:
				print('红没次数')
				break

	# 49魔镜
	def mojing49While(self):
		self.beginFun()
		while True:
			overMojing = self.mojingScript()
			if not overMojing:
				print('魔镜没次数')
				break


class MyFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="梦幻三国脚本", size=(260, 300))
		self.SetIcon(
			wx.Icon(self.get_resource_path("images/script.ico"), wx.BITMAP_TYPE_ICO)
		)
		self.SetPosition(wx.Point(10, 30))
		self.panel = wx.Panel(self)
		# self.SetWindowStyle(wx.STAY_ON_TOP)  # 按钮所在控件一直存在在桌面上
		self.scriptName = ""
		self.heifengCount = 0
		self.zhanhunFloor = ""
		self.button_start = wx.Button(
			self.panel,
			label="开始脚本(F5)",
			pos=(10, 35),
			size=(226, 26),
			style=wx.BORDER_NONE,
		)
		self.Bind(wx.EVT_BUTTON, self.button_start_click, self.button_start)
		# 设置按钮背景颜色
		self.button_start.SetBackgroundColour(wx.Colour(20, 180, 168))  # 设置为红色背景
		self.button_start.SetForegroundColour(
			wx.Colour(255, 255, 255)
		)  # 设置为白色文字
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

		# Stop button
		# self.button_stop = wx.Button(self.panel, label="退出脚本(F8)", pos=(146, 110),style=wx.BORDER_NONE)
		# self.Bind(wx.EVT_BUTTON, self.button_stop_click, self.button_stop)
		# 设置按钮背景颜色
		# self.button_stop.SetBackgroundColour(wx.Colour(144, 144, 153))
		# self.button_stop.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字

		self.dropdown = wx.ComboBox(
			self.panel,
			pos=(10, 5),
			size=(135, 30),
			choices=[
				"官渡",
				"祭坛魔镜",
				"日常",
				"战魂+红+整点",
				"战魂+红+官渡+整点",
				"战魂楼(精英)",
				"嗜血战场(精英)",
				"黑风山寨",
				"49黑风山寨",
				"49日常",
				"49战魂",
				"49祭坛魔镜",
				"49嗜血战场(精英)",
				"49名将挑战赛",
				"五行",
				"溶洞",
				"炼丹",
				"名将挑战赛",
				"官渡精英",
				"云游精英",
				"80精英",
				"100精英",
				"整点",
			],
		)
		self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
		self.dropdown.SetHint("选择执行脚本")
		self.text_ctrl = wx.TextCtrl(
			self.panel, pos=(10, 100), size=(225, 130), style=wx.TE_MULTILINE
		)
		self.button = wx.Button(self.panel, label="设置队友信息", pos=(155, 5), size=(80, 25))
		self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
		# 创建第二个下拉框，初始状态下隐藏
		self.choiceCeng = wx.ComboBox(self.panel, pos=(155, 5), size=(80, 30), choices=['21层', '22层', '23层', '24层', '25层', '26层'])
		self.choiceCeng.SetHint("战魂层数")
		self.choiceCeng.Hide()
		self.Bind(wx.EVT_COMBOBOX, self.choiceCengScript, self.choiceCeng)
		self.thread = None
		sys.stdout = self
		# 创建一个只能输入数字的文本输入框
		self.number_input = wx.TextCtrl(self.panel, pos=(155, 5), size=(80, 24), validator=NumberValidator())
		self.number_input.Hide()
		self.number_input.SetHint("黑风次数")
		self.number_input.Bind(wx.EVT_TEXT, self.on_text_change)
		self.bind_hotkeys()
		self.help_link = wx.StaticText(self.panel, label="说明", pos=(10, 235), style=wx.ST_NO_AUTORESIZE)
		self.help_link.SetForegroundColour(wx.BLUE)
		self.help_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
		self.help_link.Bind(wx.EVT_LEFT_DOWN, self.on_help_link_click)
		self.contact = wx.StaticText(self.panel, label="联系作者QQ：1728349744", pos=(100, 236), style=wx.ST_NO_AUTORESIZE)
		font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
		self.contact.SetFont(font)
		self.Bind(wx.EVT_CLOSE, self.on_close)
		self.game_name = ""
		self.teammate1_name = ""
		self.teammate2_name = ""
		self.selections = ""

	def on_help_link_click(self, event):
		# 定义弹窗的内容和图片路径
		content = [
			"脚本说明：",
			"1.官渡、魔镜、黑风自带打整点，打整点是58分之后退出副本等待整点，魔镜只做了刷包的版本，打完虚实就退；",
			"2.战魂、嗜血战场结束后自动去官渡,战魂21以上会自动加血,战魂不选择层数默认打26；",
			"3.战魂+红+整点内容是一次战魂，红的次数是根据到整点时间算的，10分钟以下不打，10分钟-20分钟打一次，20分钟以上打两次，一次整点，建议每个小时刚开始启动，战魂跟红都没次数之后会自动去官渡；",
			"4.战魂+红+官渡+整点是先打红，把红的次数打完，打战魂的次数，打完了去官渡+整点；",
			"5.黑风只打二当家，选择黑风之后填入黑风剩余次数，打完次数会自动去官渡；",
			"6.日常跟每一个单独的日常打完都会去打官渡",
			"7.日常脚本:炼丹=>五行=>溶洞=>80精英=>云游精英=>名将挑战=>100精英=>官渡精英=>官渡；",
			"8.自动去打的官渡都带整点；整点在竞技的时候(活动被刷屏的时候)大概率会漏打，但是每个也会飞一次。",
			"使用说明：",
			"1.请将电脑的屏幕分辨率调到1920*1080；",
			"2.请将电脑的缩放比放到100%；",
			"3.请将游戏所在浏览器缩放比放到100%(缩小到左右没有白边即可)；",
			"4.脚本没有停止脚本按钮，停止脚本先将鼠标放到右上角(多放几次)，等脚本不动之后按F8键重置脚本。",
		]
		images = [
			self.get_resource_path("images/shiyongshuoming.png")
		]

		# 打开弹窗
		dialog = HelpDialog(self, "使用说明", content, images)
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
			print(self.game_name)

		dialog.Destroy()

	def write(self, text):
		self.text_ctrl.WriteText(text)

	def bind_hotkeys(self):
		keyboard.add_hotkey('F5', self.start_script)
		keyboard.add_hotkey('F6', self.pause_script)
		keyboard.add_hotkey('F7', self.resume_script)
		keyboard.add_hotkey('F8', self.stop_script)

	# def on_key_pressed(self, event):
	# 	key_code = event.GetKeyCode()

	# 	if key_code == wx.WXK_F5:
	# 		self.start_script()
	# 	elif key_code == wx.WXK_F6:
	# 		self.pause_script()
	# 	elif key_code == wx.WXK_F7:
	# 		self.resume_script()
	# 	elif key_code == wx.WXK_F8:
	# 		self.stop_script()

	# 	event.Skip()

	def start_script(self):
		if self.thread is None or not self.thread.is_alive():
			scriptName = self.scriptName
			self.thread = MyThread(scriptName)
			self.thread.frame = self
		if self.scriptName == '黑风山寨' and not self.number_input.GetValidator().Validate(self.number_input):
			self.heifengCount = 0
			self.number_input.SetValue('')
			return
		if not self.scriptName:
			self.thread.show_error_message("请先选择脚本！")
			return
		print("现在开始脚本！")
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
		global condition
		if not self.scriptName:
			self.thread.show_error_message("请先选择脚本！")
			return
		if self.thread is not None:
			self.text_ctrl.SetValue("")
			self.dropdown.SetSelection(-1)
			condition = threading.Condition()
			self.thread = None
			self.choiceCeng.Hide()
			self.number_input.Hide()

	def on_close(self, event):
		if self.thread is not None:
			self.thread.stoped = True
			self.thread.join()
		self.Destroy()

	def on_text_change(self, event):
		self.heifengCount = self.number_input.GetValue()

	def on_select_script(self, event):
		self.scriptName = self.dropdown.GetValue()
		if self.scriptName == '战魂楼(精英)' or self.scriptName == '战魂+红+整点' or self.scriptName == '49战魂' or self.scriptName == '战魂+红+官渡+整点':
			self.choiceCeng.Show()
		else:
			self.choiceCeng.Hide()
		if self.scriptName == '黑风山寨' or self.scriptName == '49黑风山寨':
			self.number_input.Show()
		else:
			self.number_input.Hide()
		self.Layout()

	def choiceCengScript(self, event):
		self.zhanhunFloor = self.choiceCeng.GetValue()

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
		super().__init__(parent, title="输入信息", size=(300, 200))

		panel = wx.Panel(self)

		self.team_leader_text = wx.TextCtrl(panel, pos=(10, 10))
		self.team_leader_text.SetHint("游戏名称")
		self.teammate1_text = wx.TextCtrl(panel, pos=(10, 40))
		self.teammate1_text.SetHint("队友1名称")
		self.teammate2_text = wx.TextCtrl(panel, pos=(10, 70))
		self.teammate2_text.SetHint("队友2名称")
		self.button = wx.Button(panel, label="确定", pos=(100, 120))
		self.button.Disable()  # 初始化时禁用确定按钮
		# self.button.SetBackgroundColour(wx.Colour(20, 180, 168))  # 设置为红色背景
		# self.button.SetForegroundColour(
		# 	wx.Colour(255, 255, 255)
		# )  # 设置为白色文字
		self.button.Bind(wx.EVT_BUTTON, self.on_button_click)

		self.team_leader_text.Bind(wx.EVT_TEXT, self.on_text_change)
		self.teammate1_text.Bind(wx.EVT_TEXT, self.on_text_change)
		self.teammate2_text.Bind(wx.EVT_TEXT, self.on_text_change)
		choices = ["加血", "卖装备", "拆分强化石", "换大丹"]
		self.checklist = wx.CheckListBox(panel, choices=choices, pos=(130, 10))

	# self.checklist.Bind(wx.EVT_CHECKLISTBOX, self.on_checklistbox)

	# def on_checklistbox(self, event):
	# 	selections = [self.checklist.GetString(i) for i in range(self.checklist.GetCount()) if self.checklist.IsChecked(i)]
	# 	print("选中的值为:", selections)

	def on_text_change(self, event):
		if self.team_leader_text.GetValue():
			self.button.Enable()
		else:
			self.button.Disable()

	def on_button_click(self, event):
		# 获取文本框中的值并保存在父窗口(MyFrame)中
		parent = self.GetParent()
		selections = [self.checklist.GetString(i) for i in range(self.checklist.GetCount()) if self.checklist.IsChecked(i)]
		parent.game_name = self.team_leader_text.GetValue()
		parent.teammate1_name = self.teammate1_text.GetValue()
		parent.teammate2_name = self.teammate2_text.GetValue()
		parent.selections = selections

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
		super(HelpDialog, self).__init__(parent, title=title, size=(600, 400))

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
