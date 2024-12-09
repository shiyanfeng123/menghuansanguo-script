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
		# self.userInfoMac = ["50-9A-4C-C9-FE-BA", "B0-25-AA-26-64-03"]
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
		self.talkLocation = None
		self.oneWeek = 604800
		self.threeDays = 259200
		self.monthDays = 2592000
		self.oneDay = 86400
		self.heifengCount = 0
		self.heifengWhileCount = 0
		self.click_hwnd = 0
		self.color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000'

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
		# app = pywinauto.Application(backend="uia").connect(title="11")
		# self.game = app.window(title="11")
		self.child_thread.start()
		if self.scriptName == "官渡":
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
			self.guanduWhile()
		elif self.scriptName == "云游精英":
			self.beginFun()
			self.yunyouJyScript()
			self.guanduWhile()
		elif self.scriptName == "80精英":
			self.beginFun()
			self.bamenScript()
			self.guanduWhile()
		elif self.scriptName == "100精英":
			self.beginFun()
			self.laoshuJyScript()
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
			print(f'子窗口句柄: {hwnd}, 标题: {window_text}, 类名: {class_name}')
			return True  # 返回 True 继续枚举

		# 将回调函数转换为 ctypes 函数指针
		enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)
		# 查找目标窗口句柄
		target_window_title = self.frame.game_name
		target_window_class = 'DUIWindow'  # 如果不知道类名，可以设为 None
		hwnd = self.dm.FindWindowEx(0, target_window_class, target_window_title)
		print(hwnd)
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
		self.locationRightTopHeight = y * 0.2
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
			int(self.locationWidth * 0.7),
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
			int(self.locationRightTopWidth * 0.5),
			self.locationRightTopHeight,
		)
		self.dituRightLocation = (
			int(self.locationRightTopX + (self.locationRightTopWidth * 0.5)),
			self.locationRightTopY,
			int(self.locationRightTopWidth * 0.5),
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
			# 关闭右边
			self.click_image(
				self.get_resource_path("serveAssets/images/closeright.bmp"),
				self.confidenceNum,
				self.gameRightLocation,
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
			time.sleep(0.8)

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
			self.talkLocation,
			1
		)
		with condition:
			if self.stoped:
				condition.wait()
		if closeTalkXY:
			self.dm.MoveTo(closeTalkXY.x, closeTalkXY.y)
			for i in range(4):
				time.sleep(0.001)
				self.dm.LeftClick()
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
				(87, 6, 210, 50),
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
			self.get_resource_path("serveAssets/images/zdjs.bmp"),
			self.gameBottomLocation,
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
			self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
			self.guanduWhile()

		elif self.scriptName == "祭坛魔镜":
			findMojingshizhe = self.feiFb(
				self.get_resource_path("images/mojing/fubenmojingshizhe.png"), False
			)
			if findMojingshizhe:
				self.mojingWhile()
			else:
				self.scriptName = "官渡"
				self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
				self.guanduWhile()
		elif self.scriptName == "战魂+红+整点":
			self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
			time.sleep(1)
			self.click_image(self.get_resource_path("images/close.png"), self.confidenceNum, self.gameLocation)
			time.sleep(1)
			self.feiFb(self.get_resource_path("images/dituzhanhun.png"), True)
			self.guanduAndHongAndZd()
		elif self.scriptName == "黑风山寨":
			self.feiFb(
				self.get_resource_path("images/ditubashanhu.png"), False
			)
			self.heifengWhile()

	# 飞副本
	def feiFb(self, image_path, isJy):
		# 打开副本
		time.sleep(0.3)
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
				print(fei_pos, 'fei_pos')
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
		yjian = 90 if not types else 20
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
	def waitForTwo(self, image1_path, image2_path, image_region, timeout=None, find_dir=1):
		start_time = time.time()
		res = ""
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			xy = self.find_pic_or_str(
				image1_path, image_region, find_dir
			)
			if xy:
				res = "first"
				return res
			xy2 = self.find_pic_or_str(
				image2_path, image_region, find_dir
			)
			if xy2:
				res = "second"
				return res
			if timeout is not None:
				if time.time() - start_time > timeout:
					return False
			time.sleep(0.2)

	# 	if self.confidenceNum > 0.8:
	# 		self.confidenceNum -= 0.1
	# self.confidenceNum = 0.9

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

	# if clickB:
	# 	break

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
			image_regionB = (
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			)
		while not pyautogui.locateOnScreen(
				image_pathA, confidence=self.confidenceNum, region=image_regionA
		) or not pyautogui.locateOnScreen(
			image_pathA2, confidence=self.confidenceNum, region=image_regionA
		):
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
	def clickDitu(self, x, y, find_image, find_region, break_image):
		while not self.find_pic(break_image, self.gameBottomLocation, 0):
			self.dm.LeftClick(int(x + self.get_random_number()), y)
			time.sleep(0.1)
			isFind = self.click_image_with_min_x1(find_image, find_region, break_image, 0)
			if isFind:
				time.sleep(0.7)
			else:
				time.sleep(0.3)

	# 找图并且点击6
	def findAndClickPic(self, A, B, B1, B2, C1, C2, D, E, E2=None, E2DownTime=0.6):
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
				if D and self.clickBTime == 0:
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
				while E != "" and not EIsDown:
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
			self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
			self.get_resource_path("serveAssets/images/guandu/caocao.bmp"),
			self.gameBottomLocation,
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
				self.gameLeftLocation,
				self.get_resource_path("serveAssets/images/zdzd.bmp"),
				self.gameLeftLocation,
				hbjLocations[i],
				"",
			)
		# 颜良
		# 0.091,0.118
		self.findAndClickPic(
			'曹袁战场',
			self.get_resource_path('serveAssets/images/guandu/yanliang1.bmp'),
			self.get_resource_path('serveAssets/images/guandu/yanliang2.bmp'),
			self.gameLeftLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"0.097,0.118",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 文丑
		self.findAndClickPic(
			'曹袁战场',
			'文丑',
			f"{self.get_resource_path('serveAssets/images/guandu/wenchou1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/wenchou2.bmp')}",
			self.gameBottomLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"",
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
			'袁绍',
			f"{self.get_resource_path('serveAssets/images/guandu/yuanshao1.bmp')}|{self.get_resource_path('serveAssets/images/guandu/yuanshao2.bmp')}",
			self.gameLeftLocation,
			self.get_resource_path("serveAssets/images/zdzd.bmp"),
			self.gameLeftLocation,
			"",
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
			self.get_resource_path("images/hong/hulaoguanwai.png"),
			self.get_resource_path("images/hong/hongdianwei.png"),
			self.get_resource_path("images/hong/hongdianwei.png"),
			self.get_resource_path("images/hong/inhong.png"),
			self.get_resource_path("images/hong/inhong.png"),
			"",
			"down",
		)
		# self.waitForAAndClickB1(
		# 	self.get_resource_path("images/hong/inhong.png"),
		# 	self.get_resource_path("images/hong/hongdianwei.png"),
		# 	(
		# 		self.locationX,
		# 		self.locationY,
		# 		self.locationWidth,
		# 		self.locationHeight,
		# 	), None,
		# )
		self.waitForAAndClickB1(
			self.get_resource_path("images/hong/junyin.png"),
			self.get_resource_path("images/hong/inhong.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), None,
		)
		isInHong = self.waitFor(self.get_resource_path("images/hong/junyin.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInHong:
			print('红没次数了')
			return False
		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/hulaoguanwai.png"),
		# 	self.get_resource_path("images/hong/inhong.png"),
		# 	self.get_resource_path("images/hong/inhong.png"),
		# 	self.get_resource_path("images/hong/junyin.png"),
		# 	self.get_resource_path("images/hong/junyin.png"),
		# 	"",
		# 	"",
		# )
		# 第一个弓兵
		# 0.121，0.125  0.064，0.125 0.036，0.12
		self.findAndClickPic(
			self.get_resource_path("images/hong/junyin.png"),
			self.get_resource_path("images/hong/gongbin.png"),
			self.get_resource_path("images/hong/gongbin1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		self.findAndClickPic(
			self.get_resource_path("images/hong/junyin.png"),
			self.get_resource_path("images/hong/gongbin.png"),
			self.get_resource_path("images/hong/gongbin1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 弓兵头领
		self.findAndClickPic(
			self.get_resource_path("images/hong/junyin.png"),
			self.get_resource_path("images/hong/gongbintoulin.png"),
			self.get_resource_path("images/hong/gongbintoulin1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入军粮营
		self.waitForAAndClickB1(
			self.get_resource_path("images/hong/junliangyin.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				int(self.locationRightTopWidth * 0.5),
				self.locationRightTopHeight,
			),
		)
		self.waitFor(self.get_resource_path("images/hong/junliangyin.png"), self.dituLocation)
		# 第一个护卫兵
		self.press_keys_until_image_found(
			self.get_resource_path("images/hong/huweibin2.png"),
			self.get_resource_path("images/hong/huweibin1.png"),
			self.get_resource_path("images/zdzd.png"),
			"right",
			"",
		)
		self.waitFor(self.get_resource_path("images/hong/junliangyin.png"), self.dituLocation)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/junliangyin.png"),
		# 	self.get_resource_path("images/hong/huweibin.png"),
		# 	self.get_resource_path("images/hong/huweibin1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"right",
		# )
		# 第二个护卫兵
		self.press_keys_until_image_found(
			self.get_resource_path("images/hong/huweibin2.png"),
			self.get_resource_path("images/hong/huweibin1.png"),
			self.get_resource_path("images/zdzd.png"),
			"right",
			"",
		)
		self.waitFor(self.get_resource_path("images/hong/junliangyin.png"), self.dituLocation)

		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/junliangyin.png"),
		# 	self.get_resource_path("images/hong/huweibin.png"),
		# 	self.get_resource_path("images/hong/huweibin1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"right",
		# )
		# 护粮将领
		# 第二个护卫兵
		self.press_keys_until_image_found(
			self.get_resource_path("images/hong/huliangjianglin1.png"),
			self.get_resource_path("images/hong/huliangjianglin2.png"),
			self.get_resource_path("images/zdzd.png"),
			"right",
			"",
		)
		self.waitFor(self.get_resource_path("images/hong/junliangyin.png"), self.dituLocation)

		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/junliangyin.png"),
		# 	self.get_resource_path("images/hong/huliangjianglin.png"),
		# 	self.get_resource_path("images/hong/huliangjianglin1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"right",
		# )
		# 进入训兵营
		self.waitForAAndClickB1(
			self.get_resource_path("images/hong/xunbinyin.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				int(self.locationRightTopX + (self.locationRightTopWidth * 0.5)),
				self.locationRightTopY,
				int(self.locationRightTopWidth * 0.5),
				self.locationRightTopHeight,
			),
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/junliangyin.png"),
		# 	self.get_resource_path("images/hong/xunbinyin.png"),
		# 	self.get_resource_path("images/hong/goxunbinyin1.png"),
		# 	self.get_resource_path("images/hong/xunbinyin.png"),
		# 	self.get_resource_path("images/hong/xunbinyin.png"),
		# 	"",
		# 	"right",
		# )
		# 第一个骑兵
		self.findAndClickPic(
			self.get_resource_path("images/hong/xunbinyin.png"),
			self.get_resource_path("images/hong/qibin.png"),
			self.get_resource_path("images/hong/qibin1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		self.waitFor(self.get_resource_path("images/hong/xunbinyin.png"), self.dituLocation)
		# 第2个骑兵
		# 109  81
		self.clickDitu(int(self.righttop1.left + 101), int(self.righttop1.top + 83), self.get_resource_path("images/hong/qibin.png"), (self.locationX, self.locationY, int(self.locationWidth * 0.7), self.locationHeight), self.get_resource_path("images/zdzd.png"))
		# keyboard.press('down')
		# time.sleep(1)
		# keyboard.release('down')
		# self.press_keys_until_image_found(
		# 	self.get_resource_path("images/hong/qibin1.png"),
		# 	self.get_resource_path("images/hong/qibin2.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	"right",
		# 	"",
		# 	# 1.3
		# )
		# self.waitFor(self.get_resource_path("images/hong/xunbinyin.png"), self.dituLocation)

		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/xunbinyin.png"),
		# 	self.get_resource_path("images/hong/qibin.png"),
		# 	self.get_resource_path("images/hong/qibin1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"right",
		# 	"down",
		# )
		# 第3个骑兵
		self.findAndClickPic(
			self.get_resource_path("images/hong/xunbinyin.png"),
			self.get_resource_path("images/hong/qibin.png"),
			self.get_resource_path("images/hong/qibin1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 训兵将领
		self.findAndClickPic(
			self.get_resource_path("images/hong/xunbinyin.png"),
			self.get_resource_path("images/hong/xunbinjiangling.png"),
			self.get_resource_path("images/hong/xunbinjiangling1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进入军营
		self.findAndClickPic(
			self.get_resource_path("images/hong/xunbinyin.png"),
			self.get_resource_path("images/hong/gojunyin2.png"),
			self.get_resource_path("images/hong/gojunyin.png"),
			self.get_resource_path("images/hong/junyin.png"),
			self.get_resource_path("images/hong/junyin.png"),
			"",
			"up",
			"left"
		)
		# 进入帐篷
		self.waitForAAndClickB1(
			self.get_resource_path("images/hong/zhangpeng.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				int(self.locationRightTopX + (self.locationRightTopWidth * 0.5)),
				self.locationRightTopY,
				int(self.locationRightTopWidth * 0.5),
				self.locationRightTopHeight,
			),
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/hong/junyin.png"),
		# 	self.get_resource_path("images/hong/gozhangpeng.png"),
		# 	self.get_resource_path("images/hong/gozhangpeng1.png"),
		# 	self.get_resource_path("images/hong/zhangpeng.png"),
		# 	self.get_resource_path("images/hong/zhangpeng.png"),
		# 	"",
		# 	"left",
		# )
		# boss
		self.findAndClickPic(
			self.get_resource_path("images/hong/zhangpeng.png"),
			self.get_resource_path("images/hong/konghunwushi.png"),
			self.get_resource_path("images/hong/konghunwushi1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"up",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/hong/zhangpeng.png"))
		return True

	#  战魂脚本
	# 0.098,0.113
	def zhanhunScript(self):
		print("开始战魂")
		with condition:
			if self.stoped:
				condition.wait()
		# 进入战魂
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			self.get_resource_path("images/zhanhun/zhanhun.png"),
			self.get_resource_path("images/zhanhun/zhanhun1.png"),
			self.get_resource_path("images/zhanhun/inzhanhun.png"),
			self.get_resource_path("images/zhanhun/inzhanhun.png"),
			self.get_resource_path("images/zhanhun/inzhanhunD.png"),
			"",
		)
		# 点击进入战魂
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
			self.get_resource_path("images/zhanhun/inzhanhun.png"),
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

	# 魔镜脚本

	def mojingScript(self):
		self.mojingCount += 1
		print(f"第{self.mojingCount}次魔镜.")
		isInGuanDu = self.waitFor(self.get_resource_path("images/mojing/luyangchengxi.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/mojing/fubenmojingshizhe.png"), False)
		# print("开始魔镜祭坛")
		# 进入魔镜
		self.findAndClickPic(
			self.get_resource_path("images/mojing/luyangchengxi.png"),
			self.get_resource_path("images/mojing/mojingshizhe.png"),
			self.get_resource_path("images/mojing/mojingshizhe.png"),
			self.get_resource_path("images/mojing/injitan.png"),
			self.get_resource_path("images/mojing/injitan.png"),
			self.get_resource_path("images/mojing/mojingD.png"),
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/mojing/jingxiangdiceng.png"),
			self.get_resource_path("images/mojing/injitan.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
			None
		)
		isInMojing = self.waitFor(self.get_resource_path("images/mojing/jingxiangdiceng.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInMojing:
			print('魔镜没了')
			return False
		# self.findAndClickPic(
		# 	self.get_resource_path("images/mojing/luyangchengxi.png"),
		# 	self.get_resource_path("images/mojing/injitan.png"),
		# 	self.get_resource_path("images/mojing/injitan.png"),
		# 	self.get_resource_path("images/mojing/jingxiangdiceng.png"),
		# 	self.get_resource_path("images/mojing/jingxiangdiceng.png"),
		# 	"",
		# 	"",
		# )
		# 打一个第一层的怪
		self.findAndClickPic(
			self.get_resource_path("images/mojing/jingxiangdiceng.png"),
			self.get_resource_path("images/mojing/chirenyao.png"),
			self.get_resource_path("images/mojing/chirenyao.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入第二层
		self.waitForAAndClickB(
			self.get_resource_path("images/mojing/go2.png"),
			self.get_resource_path("images/xiaolvren.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
			self.get_resource_path("images/mojing/go3.png"),
			self.get_resource_path("images/mojing/go3.png"),
		)
		self.waitForAAndClickB(
			self.get_resource_path("images/mojing/yijijingxiang.png"),
			self.get_resource_path("images/mojing/go2.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
			None,
			self.get_resource_path("images/mojing/go3.png"),
			self.get_resource_path("images/mojing/go3.png"),
		)
		# 打狮王
		self.findAndClickPic(
			self.get_resource_path("images/mojing/yijijingxiang.png"),
			self.get_resource_path("images/mojing/shiwanghun.png"),
			self.get_resource_path("images/mojing/shiwanghun.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入第三层
		self.waitForAAndClickB(
			self.get_resource_path("images/mojing/go2.png"),
			self.get_resource_path("images/xiaolvren.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
			self.get_resource_path("images/mojing/go3.png"),
			self.get_resource_path("images/mojing/go3.png"),
		)
		self.waitForAAndClickB(
			self.get_resource_path("images/mojing/mihuanjing.png"),
			self.get_resource_path("images/mojing/go2.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
			None,
			self.get_resource_path("images/mojing/go3.png"),
			self.get_resource_path("images/mojing/go3.png"),
		)
		# 打虚实
		self.findAndClickPic(
			self.get_resource_path("images/mojing/mihuanjing.png"),
			self.get_resource_path("images/mojing/xu.png"),
			self.get_resource_path("images/mojing/xu.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		self.findAndClickPic(
			self.get_resource_path("images/mojing/mihuanjing.png"),
			self.get_resource_path("images/mojing/shi.png"),
			self.get_resource_path("images/mojing/shi.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)

		# # 进入第四层
		# self.waitForAAndClickB(
		# 	self.get_resource_path("images/mojing/go2.png"),
		# 	self.get_resource_path("images/xiaolvren.png"),
		# 	(
		# 		self.locationX,
		# 		self.locationY,
		# 		self.locationWidth,
		# 		self.locationHeight,
		# 	),
		# 	(
		# 		self.locationRightTopX,
		# 		self.locationRightTopY,
		# 		self.locationRightTopWidth,
		# 		self.locationRightTopHeight,
		# 	),
		# 	self.get_resource_path("images/mojing/go3.png"),
		# 	self.get_resource_path("images/mojing/go3.png"),
		# )
		# self.waitForAAndClickB(
		# 	self.get_resource_path("images/mojing/yujing.png"),
		# 	self.get_resource_path("images/mojing/go2.png"),
		# 	(
		# 		self.locationRightTopX,
		# 		self.locationRightTopY,
		# 		self.locationRightTopWidth,
		# 		self.locationRightTopHeight,
		# 	),
		# 	None,
		# 	self.get_resource_path("images/mojing/go3.png"),
		# 	self.get_resource_path("images/mojing/go3.png"),
		# )
		# # 打黑白无常
		# self.findAndClickPic(
		# 	self.get_resource_path("images/mojing/yujing.png"),
		# 	self.get_resource_path("images/mojing/heiwuchang.png"),
		# 	self.get_resource_path("images/mojing/heiwuchang.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"right",
		# )
		# self.findAndClickPic(
		# 	self.get_resource_path("images/mojing/yujing.png"),
		# 	self.get_resource_path("images/mojing/baiwuchang.png"),
		# 	self.get_resource_path("images/mojing/baiwuchang.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"left",
		# )
		# 退出副本
		self.outScript(self.get_resource_path("images/mojing/mihuanjing.png"))
		return True

	# 炼丹脚本
	def liandanScript(self):
		print('开始炼丹房')
		isInGuanDu = self.waitFor(self.get_resource_path("images/liandan/wuzhixiagu.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditunanhualaoren.png"), False)
		# 进入炼丹
		self.findAndClickPic(
			self.get_resource_path("images/liandan/wuzhixiagu.png"),
			self.get_resource_path("images/liandan/nanhualaoren.png"),
			self.get_resource_path("images/liandan/nanhualaoren.png"),
			self.get_resource_path("images/liandan/goliandao.png"),
			self.get_resource_path("images/liandan/goliandao.png"),
			"",
			"down",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/nantianmen.png"),
			self.get_resource_path("images/liandan/goliandao.png"),
			self.dituLocation,
			None
		)
		isInMojing = self.waitFor(self.get_resource_path("images/liandan/nantianmen.png"), self.dituLocation, 5)
		if not isInMojing:
			print('炼丹没次数了')
			return False
		# 打门神
		self.findAndClickPic(
			self.get_resource_path("images/liandan/nantianmen.png"),
			self.get_resource_path("images/liandan/zuomenshen.png"),
			self.get_resource_path("images/liandan/zuomenshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			self.get_resource_path("images/liandan/nantianmenD.png"),
			"",
		)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/nantianmen.png"),
			self.get_resource_path("images/liandan/youmenshen.png"),
			self.get_resource_path("images/liandan/youmenshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		# 进入第二层
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/tiangongxiaodao.png"),
			self.get_resource_path("images/liandan/gotiangongD.png"),
			self.dituLocation,
			self.gameLocation,
		)
		self.waitFor(self.get_resource_path("images/liandan/tiangongxiaodao.png"), self.dituLocation, )
		# 进入
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/liandanfang.png"),
			self.get_resource_path("images/chuansongmenRight.png"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 开始打炼丹童子童女
		for i in range(5):
			self.findAndClickPic(
				self.get_resource_path("images/liandan/liandanfang.png"),
				self.get_resource_path("images/liandan/liandantong.png"),
				self.get_resource_path("images/liandan/liandantong.png"),
				self.get_resource_path("images/zdzd.png"),
				self.get_resource_path("images/zdzd1.png"),
				"",
				"down",
			)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/liandanfang.png"),
			self.get_resource_path("images/liandan/liandantong.png"),
			self.get_resource_path("images/liandan/liandantong.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		for i in range(4):
			self.findAndClickPic(
				self.get_resource_path("images/liandan/liandanfang.png"),
				self.get_resource_path("images/liandan/liandantong.png"),
				self.get_resource_path("images/liandan/liandantong.png"),
				self.get_resource_path("images/zdzd.png"),
				self.get_resource_path("images/zdzd1.png"),
				"",
				"right",
			)
		# 退出副本
		self.outScript(self.get_resource_path("images/liandan/liandanfang.png"))
		return True

	# 五行脚本
	def wuxingScript(self):
		print('开始五行')
		isInGuanDu = self.waitFor(self.get_resource_path("images/liandan/luoyangchengyewaixi.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditubanbuduolaoban.png"), True)
		# 进入五行
		self.findAndClickPic(
			self.get_resource_path("images/liandan/luoyangchengyewaixi.png"),
			self.get_resource_path("images/liandan/banbuduolaoban.png"),
			self.get_resource_path("images/liandan/banbuduolaoban.png"),
			self.get_resource_path("images/liandan/gowuxing.png"),
			self.get_resource_path("images/liandan/gowuxing.png"),
			self.get_resource_path("images/liandan/wuxingD.png"),
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/wuxingshengdian.png"),
			self.get_resource_path("images/liandan/gowuxing.png"),
			self.dituLocation,
			None
		)
		isInMojing = self.waitFor(self.get_resource_path("images/liandan/wuxingshengdian.png"), self.dituLocation, 5)
		if not isInMojing:
			print('五行没次数了')
			return False
		# 打大乔
		self.press_keys_until_image_found(
			self.get_resource_path("images/liandan/wuxingdaqiao.png"),
			self.get_resource_path("images/liandan/wuxingdaqiao1.png"),
			self.get_resource_path("images/zdzd.png"),
			"left",
			"",
		)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/wuxingshengdian.png"),
			self.get_resource_path("images/liandan/shenhuoxi.png"),
			self.get_resource_path("images/liandan/shenhuoxi.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/wuxingshengdian.png"),
			self.get_resource_path("images/liandan/shenjinxi.png"),
			self.get_resource_path("images/liandan/shenjinxi.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		self.waitFor(self.get_resource_path("images/liandan/wuxingshengdian.png"), self.dituLocation)
		self.press_keys_until_image_found(
			self.get_resource_path("images/liandan/wuxingzhangliao.png"),
			self.get_resource_path("images/liandan/wuxingzhangliao1.png"),
			self.get_resource_path("images/zdzd.png"),
			"left",
			"",
		)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/wuxingshengdian.png"),
			self.get_resource_path("images/liandan/shenmuxi.png"),
			self.get_resource_path("images/liandan/shenmuxi.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		self.outScript(self.get_resource_path("images/liandan/wuxingshengdian.png"))
		return True

	# 溶洞
	def rongdongScript(self):
		print('开始溶洞')
		isInGuanDu = self.waitFor(self.get_resource_path("images/liandan/lvlinlu.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditulongxiaotian.png"), False)
		# 进入溶洞
		self.findAndClickPic(
			self.get_resource_path("images/liandan/lvlinlu.png"),
			self.get_resource_path("images/liandan/longtianxiao.png"),
			self.get_resource_path("images/liandan/longtianxiao.png"),
			self.get_resource_path("images/liandan/gorongdong.png"),
			self.get_resource_path("images/liandan/gorongdong.png"),
			self.get_resource_path("images/liandan/rongdongD.png"),
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/yiwangzhilin.png"),
			self.get_resource_path("images/liandan/gorongdong.png"),
			self.dituLocation,
			None
		)
		isInMojing = self.waitFor(self.get_resource_path("images/liandan/yiwangzhilin.png"), self.dituLocation, 5)
		if not isInMojing:
			print('溶洞没次数了')
			return False
		# 开始打第一层
		for i in range(3):
			self.findAndClickPic(
				self.get_resource_path("images/liandan/yiwangzhilin.png"),
				self.get_resource_path("images/liandan/yuanguganshi.png"),
				self.get_resource_path("images/liandan/yuanguganshi.png"),
				self.get_resource_path("images/zdzd.png"),
				self.get_resource_path("images/zdzd1.png"),
				"",
				"left",
			)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/yiwangzhilin.png"),
			self.get_resource_path("images/liandan/baolixiong.png"),
			self.get_resource_path("images/liandan/baolixiong.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进入第二层
		self.waitForAAndClickB1(
			self.get_resource_path("images/liandan/yuangurongdong.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation,
			self.dituLeftLocation,
		)
		self.findAndClickPic(
			self.get_resource_path("images/liandan/yuangurongdong.png"),
			self.get_resource_path("images/liandan/yonghengzhihuo.png"),
			self.get_resource_path("images/liandan/yonghengzhihuo.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/liandan/yuangurongdong.png"))
		return True

	# 80精英
	def bamenScript(self):
		print('开始80精英')
		isInGuanDu = self.waitFor(self.get_resource_path("images/80jy/xuchangcheng.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/dituzuocifenshen.png"), True)
		# 进入80精英
		self.findAndClickPic(
			self.get_resource_path("images/80jy/xuchangcheng.png"),
			self.get_resource_path("images/80jy/zuocifenshen.png"),
			self.get_resource_path("images/80jy/zuocifenshen.png"),
			self.get_resource_path("images/80jy/in80jy.png"),
			self.get_resource_path("images/80jy/in80jy.png"),
			self.get_resource_path("images/80jy/80jyD.png"),
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/80jy/modaorukou.png"),
			self.get_resource_path("images/80jy/in80jy.png"),
			self.dituLocation,
			None
		)
		isInMojing = self.waitFor(self.get_resource_path("images/80jy/modaorukou.png"), self.dituLocation, 5)
		if not isInMojing:
			print('80精英没次数了')
			return False
		# 进入幻境凶
		self.waitForAAndClickB1(
			self.get_resource_path("images/80jy/huanjinxiong.png"),
			self.get_resource_path("images/80jy/goxiong.png"),
			self.dituLocation,
			self.gameLocation
		)
		# 打妖族之王
		self.findAndClickPic(
			self.get_resource_path("images/80jy/huanjinxiong.png"),
			self.get_resource_path("images/80jy/yaozuzhiwang.png"),
			self.get_resource_path("images/80jy/yaozuzhiwang.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入地牢
		self.waitForAAndClickB1(
			self.get_resource_path("images/80jy/modaodilao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打穷奇
		self.findAndClickPic(
			self.get_resource_path("images/80jy/modaodilao.png"),
			self.get_resource_path("images/80jy/qiongqi.png"),
			self.get_resource_path("images/80jy/qiongqi.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入二层
		self.waitForAAndClickB1(
			self.get_resource_path("images/80jy/modaodilao2.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打吕布
		self.findAndClickPic(
			self.get_resource_path("images/80jy/modaodilao2.png"),
			self.get_resource_path("images/80jy/yaohualvbu.png"),
			self.get_resource_path("images/80jy/yaohualvbu.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进入boss
		self.waitForAAndClickB1(
			self.get_resource_path("images/80jy/modaoshuniu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打boss
		self.findAndClickPic(
			self.get_resource_path("images/80jy/modaoshuniu.png"),
			self.get_resource_path("images/80jy/yaohuaguojia.png"),
			self.get_resource_path("images/80jy/yaohuaguojia.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/80jy/modaoshuniu.png"))
		return True

	# 官渡精英
	def guanduJyScript(self):
		print("开始官渡精英")
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor(self.get_resource_path("images/guanDu1.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
		guaiwugongjiLocation = pyautogui.locateOnScreen(self.get_resource_path("images/guaiwugongji.png"), confidence=self.confidenceNum, region=self.gameLocation)
		if guaiwugongjiLocation:
			self.click_image(self.get_resource_path("images/check.png"), self.confidenceNum, (guaiwugongjiLocation.left, guaiwugongjiLocation.top, guaiwugongjiLocation.width, guaiwugongjiLocation.height))
		# 进入官渡
		self.findAndClickPic(
			self.get_resource_path("images/guanDu1.png"),
			self.get_resource_path("images/caoCao.png"),
			self.get_resource_path("images/caoCao2.png"),
			self.get_resource_path("images/inguandujy.png"),
			self.get_resource_path("images/inguandujy.png"),
			self.get_resource_path("images/guanduD.png"),
			"",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/caoyindazhangjy.png"),
			self.get_resource_path("images/inguandujy.png"),
			self.dituLocation, None,
		)
		isInMojing = self.waitFor(self.get_resource_path("images/caoyindazhangjy.png"), self.dituLocation, 5)
		if not isInMojing:
			print('官渡精英没次数了')
			return False
		self.waitFor(self.get_resource_path("images/caoyindazhangjy.png"), self.dituLocation, 5)
		self.waitForAAndClickB1(
			self.get_resource_path("images/caoyuanzhangchangjy.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		# 第一个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhangchangjy.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		self.waitFor(self.get_resource_path("images/caoyuanzhangchangjy.png"), self.dituLocation)

		# 第二个河北军
		self.clickDitu(int(self.righttop1.left + 85), int(self.righttop1.top + 71), self.get_resource_path("images/hbj4.png"), (self.locationX, self.locationY, int(self.locationWidth * 0.7), self.locationHeight), self.get_resource_path("images/zdzd.png"))

		# 84  71
		# self.press_keys_until_image_found(
		# 	self.get_resource_path("images/hbj4.png"),
		# 	self.get_resource_path("images/hbj1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	"",
		# 	"right",
		# 	1.9
		# )
		# self.findAndClickPic(
		# 	self.get_resource_path("images/caoyuanzhangchangjy.png"),
		# 	self.get_resource_path("images/hbj4.png"),
		# 	self.get_resource_path("images/hbj1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	self.get_resource_path("images/hbj2D.png"),
		# 	"",
		# )
		# 颜良
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhangchangjy.png"),
			self.get_resource_path("images/yanliang.png"),
			self.get_resource_path("images/yanliang1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 文丑
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhangchangjy.png"),
			self.get_resource_path("images/wenchou.png"),
			self.get_resource_path("images/wenchou1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 去大帐
		self.waitForAAndClickB1(
			self.get_resource_path("images/caoyindazhangjy.png"),
			self.get_resource_path("images/chuansongmenguandu.png"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor(self.get_resource_path("images/caoyindazhangjy.png"), self.dituLocation)
		# 找到曹操进入乌巢
		self.waitForAAndClickB1(
			self.get_resource_path("images/gowuchao.png"),
			self.get_resource_path("images/xiaolvren.png"),
			self.gameLocation, self.dituLocation,
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/wuchaojy.png"),
			self.get_resource_path("images/gowuchao.png"),
			self.dituLocation, None,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/wuchaojy.png"),
		# 	self.get_resource_path("images/wenchouzhihun.png"),
		# 	self.get_resource_path("images/wenchouzhihun1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"left",
		# )
		self.waitForAAndClickB1(
			self.get_resource_path("images/hundianjy.png"),
			self.get_resource_path("images/wuchaochuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor(self.get_resource_path("images/hundianjy.png"), self.dituLocation)
		self.findAndClickPic(
			self.get_resource_path("images/hundianjy.png"),
			self.get_resource_path("images/wenchouzhihun.png"),
			self.get_resource_path("images/wenchouzhihun1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 打董卓
		self.findAndClickPic(
			self.get_resource_path("images/hundianjy.png"),
			self.get_resource_path("images/dongzhuozhihun.png"),
			self.get_resource_path("images/dongzhuozhihun.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 魂殿进乌巢
		self.waitForAAndClickB1(
			self.get_resource_path("images/wuchaojy.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		# 打淳
		self.findAndClickPic(
			self.get_resource_path("images/wuchaojy.png"),
			self.get_resource_path("images/cyq.png"),
			self.get_resource_path("images/cyq1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 打袁绍
		self.waitFor(self.get_resource_path("images/wuchaojy.png"), self.dituLocation)
		self.press_keys_until_image_found(
			self.get_resource_path("images/yuanshao1.png"),
			self.get_resource_path("images/yuanshao2.png"),
			self.get_resource_path("images/zdzd.png"),
			"",
			"",
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/wuchaojy.png"),
		# 	self.get_resource_path("images/yuanshao.png"),
		# 	self.get_resource_path("images/yuanshao1.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	self.get_resource_path("images/zdzd1.png"),
		# 	"",
		# 	"",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# 退出副本
		self.outScript(self.get_resource_path("images/wuchao.png"))

	# 云游精英
	def yunyouJyScript(self):
		print('开始云游精英')
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor(self.get_resource_path("images/yunyoujy/songshan.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/dituyunyouxianren.png"), True)
		# 进入云游
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/songshan.png"),
			self.get_resource_path("images/yunyoujy/yunyouxianren.png"),
			self.get_resource_path("images/yunyoujy/yunyouxianren.png"),
			self.get_resource_path("images/yunyoujy/inyunyoujy.png"),
			self.get_resource_path("images/yunyoujy/inyunyoujy.png"),
			"",
			"up",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/donghaizhiji.png"),
			self.get_resource_path("images/yunyoujy/inyunyoujy.png"),
			self.dituLocation, None,
		)
		isInMojing = self.waitFor(self.get_resource_path("images/yunyoujy/donghaizhiji.png"), self.dituLocation, 5)
		if not isInMojing:
			print('云游精英没次数了')
			return False
		# 进鬼气林
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/guiqilin.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		# 打黑无常
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/guiqilin.png"),
			self.get_resource_path("images/yunyoujy/heiwuchang.png"),
			self.get_resource_path("images/yunyoujy/heiwuchang.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		self.waitFor(self.get_resource_path("images/yunyoujy/guiqilin.png"), self.dituLocation)
		# 进东海之极
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/donghaizhiji.png"),
			self.get_resource_path("images/yunyoujy/guiqilinchuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor(self.get_resource_path("images/yunyoujy/donghaizhiji.png"), self.dituLocation)
		# 找云霞仙子
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/gtianti.png"),
			self.get_resource_path("images/yunyoujy/zixiaxianzi1.png"),
			self.gameLocation, self.dituLocation,
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/tianti.png"),
			self.get_resource_path("images/yunyoujy/gtianti.png"),
			self.dituLocation, self.gameLocation,
		)
		# 打张辽
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/tianti.png"),
			self.get_resource_path("images/yunyoujy/tianjieshouhuzhe.png"),
			self.get_resource_path("images/yunyoujy/tianjieshouhuzhe.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进云端
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor(self.get_resource_path("images/yunyoujy/yunduan.png"), self.dituLocation)
		# 进入第一个传送门
		self.click_image_with_min_x(self.get_resource_path("images/chuansongmen.png"), self.dituLocation, self.get_resource_path("images/yunyoujy/renjie.png"))
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/tianjie.png"),
			self.get_resource_path("images/yunyoujy/tianjiefenshen.png"),
			self.get_resource_path("images/yunyoujy/tianjiefenshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进云端
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		# 进地狱打巨灵神
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/yunyoujy/diyufenshen.png"),
			self.get_resource_path("images/yunyoujy/diyufenshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		# 进云端
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/yunyoujy/diyuchuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		self.waitFor(self.get_resource_path("images/yunyoujy/yunduan.png"), self.dituLocation)
		# 进人界
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/renjie.png"),
			self.get_resource_path("images/yunyoujy/gorenjie.png"),
			self.dituLocation, self.gameLocation,
		)
		# 打人界巨灵神
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/renjie.png"),
			self.get_resource_path("images/yunyoujy/renjiefenshen.png"),
			self.get_resource_path("images/yunyoujy/renjiefenshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进云端
		self.waitForAAndClickB1(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLocation,
		)
		# 打boss
		self.findAndClickPic(
			self.get_resource_path("images/yunyoujy/yunduan.png"),
			self.get_resource_path("images/yunyoujy/julingshen.png"),
			self.get_resource_path("images/yunyoujy/julingshen.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			self.get_resource_path("images/yunyoujy/bossD.png"),
			"",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/yunyoujy/yunduan.png"))
		return True

	# 100精英
	def laoshuJyScript(self):
		print('开始老鼠精英')
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor(self.get_resource_path("images/laoshujy/bishuidixue.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditulieshuren.png"), True)
		# 进入老鼠
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/bishuidixue.png"),
			self.get_resource_path("images/laoshujy/lieshuren1.png"),
			self.get_resource_path("images/laoshujy/lieshuren1.png"),
			self.get_resource_path("images/laoshujy/inlaoshujy.png"),
			self.get_resource_path("images/laoshujy/inlaoshujy.png"),
			"",
			"",
		)
		# 进入第一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shuxuerukoujy.png"),
			self.get_resource_path("images/laoshujy/inlaoshujy.png"),
			self.dituLocation, None,
		)
		isInMojing = self.waitFor(self.get_resource_path("images/laoshujy/shuxuerukoujy.png"), self.dituLocation)
		if not isInMojing:
			print('老鼠精英没次数了')
			return False
		# 打妖鼠头领
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/shuxuerukoujy.png"),
			self.get_resource_path("images/laoshujy/yaoshutoulin.png"),
			self.get_resource_path("images/laoshujy/yaoshutoulin.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shuxuejy.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLeftLocation,
		)
		# 打猎杀鼠
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/shuxuejy.png"),
			self.get_resource_path("images/laoshujy/anshashu.png"),
			self.get_resource_path("images/laoshujy/anshashu.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shuchaoneijy.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLeftLocation,
		)
		# 打鼠长老
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/shuchaoneijy.png"),
			self.get_resource_path("images/laoshujy/shuzhanglao.png"),
			self.get_resource_path("images/laoshujy/shuzhanglao.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shudatinjy.png"),
			self.get_resource_path("images/laoshujy/goshudatin2.png"),
			self.dituLocation, self.dituLocation,
		)
		# 打boss1
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/shudatinjy.png"),
			self.get_resource_path("images/laoshujy/bishuishuwang1.png"),
			self.get_resource_path("images/laoshujy/bishuishuwang1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"up",
		)
		# 进入下一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shuchaoneijy.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation, self.dituLeftLocation,
		)
		self.waitFor(self.get_resource_path("images/laoshujy/shuchaoneijy.png"), self.dituLocation, 5)
		# 进入boss
		self.waitForAAndClickB1(
			self.get_resource_path("images/laoshujy/shudianjy.png"),
			self.get_resource_path("images/laoshujy/goboss.png"),
			self.dituLocation, self.gameLocation,
		)
		# 打boss1
		self.findAndClickPic(
			self.get_resource_path("images/laoshujy/shudianjy.png"),
			self.get_resource_path("images/laoshujy/bishuishuwang2.png"),
			self.get_resource_path("images/laoshujy/bishuishuwang2.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"down",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/laoshujy/shudianjy.png"))
		return True

	# 名将挑战赛
	def mingjiangtiaozhan(self):
		print('名将挑战赛')
		with condition:
			if self.stoped:
				condition.wait()
		# 进入
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/luoyangdadao.png"),
			self.get_resource_path("images/zhanhun/zhanhun.png"),
			self.get_resource_path("images/zhanhun/zhanhun1.png"),
			self.get_resource_path("images/zhanhun/inmingjiang.png"),
			self.get_resource_path("images/zhanhun/inmingjiang.png"),
			self.get_resource_path("images/zhanhun/inzhanhunD.png"),
			"",
		)
		# 点击进入名将
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/inmingjiang.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), None,
		)
		isInZhanhun = self.waitFor(self.get_resource_path("images/zhanhun/wushendian.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInZhanhun:
			print('名将挑战没次数了')
			return False
		# 打刘备
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/mingjiangliubei.png"),
			self.get_resource_path("images/zhanhun/mingjiangliubei.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			"",
			"left",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.gameLocation, self.gameLocation,
		)
		self.waitFor(self.get_resource_path("images/zdjs.png"), self.gameLocation)
		# 打张飞
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/mingjiangzhangfei.png"),
			self.get_resource_path("images/zhanhun/mingjiangzhangfei.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			"",
			"down",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.gameLocation, self.gameLocation,
		)
		self.waitFor(self.get_resource_path("images/zdjs.png"), self.gameLocation)
		# 打关羽
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/mingjiangguanyu.png"),
			self.get_resource_path("images/zhanhun/mingjiangguanyu.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			"",
			"right",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.gameLocation, self.gameLocation,
		)
		self.waitFor(self.get_resource_path("images/zdjs.png"), self.gameLocation)
		# 打吕布
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/mingjianglvbu.png"),
			self.get_resource_path("images/zhanhun/mingjianglvbu.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			"",
			"down",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zhanhun/tiaozhan.png"),
			self.gameLocation, self.gameLocation,
		)
		self.waitFor(self.get_resource_path("images/zhanhun/wushendian.png"), self.dituLocation)
		# 找守卫
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/wushendian.png"),
			self.get_resource_path("images/zhanhun/tianwaitianshouwei.png"),
			self.get_resource_path("images/zhanhun/tianwaitianshouwei.png"),
			self.get_resource_path("images/zhanhun/intianwai.png"),
			self.get_resource_path("images/zhanhun/intianwai.png"),
			self.get_resource_path("images/zhanhun/intianwaiD.png"),
			"",
		)
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/tianwaitian.png"),
			self.get_resource_path("images/zhanhun/intianwai.png"),
			self.dituLocation, self.gameLocation,
		)

		for i in range(7):
			self.waitFor(self.get_resource_path("images/zhanhun/tianwaitian.png"), self.dituLocation)
			self.press_keys_until_image_found(
				self.get_resource_path("images/zhanhun/dixuechanchu.png"),
				self.get_resource_path("images/zhanhun/dixuechanchu.png"),
				self.get_resource_path("images/zdzd.png"),
				"right",
				"",
			)
		waitForTwoRes = self.waitForTwo(
			self.get_resource_path("images/zhanhun/shoucainuchuxian.png"),
			self.get_resource_path("images/zhanhun/yunqitailanle.png"),
			self.gameLocation,
		)
		if waitForTwoRes == "second":
			print("没有守财奴")
			return True
		self.findAndClickPic(
			self.get_resource_path("images/zhanhun/tianwaitian.png"),
			self.get_resource_path("images/zhanhun/shoucainu.png"),
			self.get_resource_path("images/zhanhun/shoucainu.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd.png"),
			"",
			"left",
		)
		self.waitFor(self.get_resource_path("images/zhanhun/luoyangdadao.png"), self.dituLocation)
		return True

	# 一直执行天外天
	def mingjiangtiaozhanWhile(self):
		self.beginFun()
		for i in range(8):
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break
		self.guanduWhile()

	# 黑风
	def heifengScript(self):
		self.heifengCount += 1
		print(f"第{self.heifengCount}次黑风.")
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor(self.get_resource_path("images/heifeng/qiankundong5.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditubashanhu.png"), False)
		# 进入黑风
		self.findAndClickPic(
			self.get_resource_path("images/heifeng/qiankundong5.png"),
			self.get_resource_path("images/heifeng/bashanhu.png"),
			self.get_resource_path("images/heifeng/bashanhu.png"),
			self.get_resource_path("images/heifeng/inheifeng.png"),
			self.get_resource_path("images/heifeng/inheifeng.png"),
			"",
			"up",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入第一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/heifeng/heifengshanzhai.png"),
			self.get_resource_path("images/heifeng/inheifeng.png"),
			self.dituLocation, None,
		)
		# 打刀贼
		for i in range(2):
			self.findAndClickPic(
				self.get_resource_path("images/heifeng/heifengshanzhai.png"),
				self.get_resource_path("images/heifeng/daozei.png"),
				self.get_resource_path("images/heifeng/daozei.png"),
				self.get_resource_path("images/zdzd.png"),
				self.get_resource_path("images/zdzd1.png"),
				"",
				"left",
			)
		self.waitFor(self.get_resource_path("images/heifeng/heifengshanzhai.png"), self.dituLocation)
		self.clickDitu(int(self.righttop1.left + 103), int(self.righttop1.top + 72), self.get_resource_path("images/heifeng/daozei.png"), (int(self.locationX + self.locationWidth * 0.3), self.locationY, int(self.locationWidth * 0.7), self.locationHeight), self.get_resource_path("images/zdzd.png"))
		# self.press_keys_until_image_found(
		# 	self.get_resource_path("images/heifeng/daozei2.png"),
		# 	self.get_resource_path("images/heifeng/daozei3.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	"", "left"
		# )
		self.waitFor(self.get_resource_path("images/heifeng/heifengshanzhai.png"), self.dituLocation)
		self.clickDitu(int(self.righttop1.left + 84), int(self.righttop1.top + 75), self.get_resource_path("images/heifeng/daozei.png"), (int(self.locationX + self.locationWidth * 0.3), self.locationY, int(self.locationWidth * 0.7), self.locationHeight), self.get_resource_path("images/zdzd.png"))
		# self.press_keys_until_image_found(
		# 	self.get_resource_path("images/heifeng/daozei.png"),
		# 	self.get_resource_path("images/heifeng/daozei.png"),
		# 	self.get_resource_path("images/zdzd.png"),
		# 	"", "left", 0.9
		# )
		# 81  72
		self.findAndClickPic(
			self.get_resource_path("images/heifeng/heifengshanzhai.png"),
			self.get_resource_path("images/heifeng/daozeitoumu.png"),
			self.get_resource_path("images/heifeng/daozeitoumu.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		self.waitFor(self.get_resource_path("images/heifeng/heifengshanzhai.png"), self.dituLocation)
		# 进入第二层
		self.waitForAAndClickB1(
			self.get_resource_path("images/heifeng/shanzhaibenyin.png"),
			self.get_resource_path("images/heifeng/1chuansongmen.png"),
			self.dituLocation,
			self.dituLeftLocation
		)
		self.waitFor(self.get_resource_path("images/heifeng/shanzhaibenyin.png"), self.dituLocation)
		# 进入二当家
		self.waitForAAndClickB1(
			self.get_resource_path("images/heifeng/shaizhaineitang.png"),
			self.get_resource_path("images/chuansongmen.png"),
			self.dituLocation,
			self.dituRightLocation
		)
		# 打二当家
		self.findAndClickPic(
			self.get_resource_path("images/heifeng/shaizhaineitang.png"),
			self.get_resource_path("images/heifeng/erdangjia.png"),
			self.get_resource_path("images/heifeng/erdangjia.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"up",
		)
		# 退出副本
		self.outScript(self.get_resource_path("images/heifeng/shaizhaineitang.png"))
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
		dict_id = self.dm.SetDict(0, self.get_resource_path("serveAssets/fonts/guandu.txt"))  # 字库文件路径
		# self.beginFun()
		# while True:
		self.guanduScript()

	# 一直执行红
	def hongWhile(self):
		self.beginFun()
		for i in range(7):
			hongRes = self.hongScript()
			if not hongRes:
				print('红没次数')
				break
		self.guanduWhile()

	# 一直执行战魂
	def zhanhunWhile(self):
		self.beginFun()
		for i in range(6):
			zhanhunRes = self.zhanhunScript()
			if not zhanhunRes:
				print('战魂没次数')
				break
		self.guanduWhile()

	# 一直执行魔镜
	def mojingWhile(self):
		self.beginFun()
		while True:
			overMojing = self.mojingScript()
			if not overMojing:
				print('魔镜没次数')
				break
		self.guanduWhile()

	# 一次战魂一次红+整点
	def guanduAndHongAndZd(self):
		self.beginFun()
		self.zhanhunScript()
		time.sleep(1)
		self.feiFb(self.get_resource_path("images/ditudianwei.png"), True)
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
		isInGuanDu = self.waitFor(self.get_resource_path("images/liandan/wuzhixiagu.png"), self.dituLocation, 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditunanhualaoren.png"), False)
		for i in range(5):
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		time.sleep(2)
		# 飞五行
		self.feiFb(self.get_resource_path("images/ditubanbuduolaoban.png"), True)
		time.sleep(1)
		for i in range(3):
			hasWuxing = self.wuxingScript()
			if not hasWuxing:
				break
		time.sleep(2)
		# 飞溶洞
		self.feiFb(self.get_resource_path("images/ditulongxiaotian.png"), False)
		time.sleep(1)
		for i in range(3):
			hasRongdong = self.rongdongScript()
			if not hasRongdong:
				break
		time.sleep(2)
		# 飞80精英
		self.feiFb(self.get_resource_path("images/dituzuocifenshen.png"), True)
		time.sleep(1)
		self.bamenScript()
		time.sleep(2)
		# 飞云游精英
		self.feiFb(self.get_resource_path("images/dituyunyouxianren.png"), True)
		time.sleep(1)
		self.yunyouJyScript()
		# 飞名将挑战赛
		time.sleep(2)
		self.feiFb(self.get_resource_path("images/dituzhanhun.png"), True)
		time.sleep(1)
		for i in range(8):
			zhanhunRes = self.mingjiangtiaozhan()
			if not zhanhunRes:
				print('名将没次数')
				break
		time.sleep(1)
		# 飞100精英
		self.feiFb(self.get_resource_path("images/ditulieshuren.png"), True)
		time.sleep(1)
		self.laoshuJyScript()
		time.sleep(2)
		# 飞官渡精英
		self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
		time.sleep(1)
		self.guanduJyScript()
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
		self.guanduWhile()

	# 战魂红官渡
	def zhanhunHongGdWhile(self):
		self.beginFun()
		for i in range(7):
			hasHong = self.hongScript()
			if not hasHong:
				break
		self.feiFb(self.get_resource_path("images/dituzhanhun.png"), True)
		for i in range(6):
			hasZhanhun = self.zhanhunScript()
			if not hasZhanhun:
				break
		self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
		while True:
			self.guanduScript()

	# 49黑风
	def heifeng49While(self):
		self.beginFun()
		guaiwugongjiLocation = pyautogui.locateOnScreen(self.get_resource_path("images/heifeng/guaiwugongji.png"), confidence=self.confidenceNum, region=self.gameLocation)
		if guaiwugongjiLocation:
			self.click_image(self.get_resource_path("images/heifeng/check.png"), self.confidenceNum, (guaiwugongjiLocation.left, guaiwugongjiLocation.top, guaiwugongjiLocation.width, guaiwugongjiLocation.height))
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
			self.feiFb(self.get_resource_path("images/ditunanhualaoren.png"), False)
		for i in range(5):
			liandanHas = self.liandanScript()
			if not liandanHas:
				break
		# 飞五行
		self.feiFb(self.get_resource_path("images/ditubanbuduolaoban.png"), True)
		time.sleep(1)
		for i in range(3):
			hasWuxing = self.wuxingScript()
			if not hasWuxing:
				break
		# 飞溶洞
		self.feiFb(self.get_resource_path("images/ditulongxiaotian.png"), False)
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
