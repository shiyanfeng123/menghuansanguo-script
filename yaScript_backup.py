#win32 gdi方案
import win32con
import win32gui
import win32ui
import win32api
import time

import numpy as np
import os
from PIL import Image
import aircv as ac
from ctypes import windll, byref
from ctypes.wintypes import HWND, POINT
import string
import sys
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
import cv2

pyautogui.PAUSE = 0.005
pyautogui.FAILSAFE = True  # 鼠标光标在屏幕左上角，会导致程序异常，用于终止程序运行。
sys.coinit_flags = 0

scale = 1  # 电脑的缩放比例
radius = 2  # 随机半径
x_coor = 0  # 窗口位置
y_coor = 0  # 窗口位置
# 打包命令：pyinstaller -F -w --add-data "images;images" --icon=images\script.ico .\main.py
# pyinstaller main.spec

condition = threading.Condition()


class MyThread(threading.Thread):
	def __init__(self, scriptName):
		super().__init__()
		self.userInfoMac = ["50-9A-4C-C9-FE-BA"]
		self.frame = None
		self.zhanhunFloor = ''
		self.autoClick = AutoClick()
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
		self.zdzdPath = self.get_resource_path("images/zdzd.png")
		self.Dx = 0
		self.Dy = 0
		self.BisClick = False
		self.clickBTime = 0
		self.clickBX = 0
		self.clickBy = 0
		self.shengxiaoLocation = None
		self.mojingCount = 0
		self.gameLocation = None
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

	def run(self):
		# c = wmi.WMI()
		# for item in c.Win32_BaseBoard():
		#     hardware_serial = item.SerialNumber
		self.zhanhunFloor = self.frame.zhanhunFloor
		self.heifengWhileCount = int(self.frame.heifengCount)
		startTime = 1732958685
		# 一个月脚本
		if time.time() - startTime > self.monthDays:
			print('脚本已过期!')
			return
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
		isFind = self.autoClick.get_winds(self.frame.game_name)
		if not isFind:
			print('未找到游戏')
			return
		self.autoClick.get_src()
		# isFindGame = self.findGame()
		# if not isFindGame:
		# 	return
		# self.child_thread.start()
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
		elif self.scriptName == "test":
			print('111')
			self.click_image(self.get_resource_path("images/closetalk.png"), self.confidenceNum)

	# self.autoClick.mouse_click(785, 388)

	# self.autoClick.mouse_click_image("images/xiulian.png")

	def find_template_location(self, template, threshold, type):
		if type != 'all':
			template_pos = self.autoClick.recognize(template, threshold)
			if template_pos is not None:
				if type == 'location':
					class Res:
						def __init__(resInit, left, top, width, height):
							resInit.left = left
							resInit.top = top
							resInit.width = width
							resInit.height = height

					left, top, right, bottom = template_pos['rectangle']
					res = Res(left[0], left[1], bottom[0], bottom[1])
					return res
				elif type == 'center':
					x, y = template_pos['result']

					class ResXy:
						def __init__(resInit, x, y):
							resInit.x = x
							resInit.y = y

					res = ResXy(x, y)
					return res
			else:
				return None
		else:
			template_pos = self.autoClick.recognize_all(template, threshold)
			if template_pos is not None:
				return template_pos
			else:
				return None

	def child_task(self):
		# res = self.find_template_location(self.get_resource_path("images/closeright.png"), self.confidenceNum, 'all')
		# print(res, 'resresres')
		while True:
			# 去除获得铜币黑框
			# self.click_image(
			#     self.get_resource_path("images/huodetongbi.png"),
			#     self.confidenceNum,
			#     (
			#         self.locationX,
			#         self.locationY,
			#         self.locationWidth,
			#         self.locationHeight,
			#     ),
			# )
			# 点击取消
			if self.find_template_location(self.get_resource_path("images/jingji.png"), self.confidenceNum, 'location'):
				self.click_image(
					self.get_resource_path("images/closeJJ.png"),
					self.confidenceNum
				)
			# 去掉副本奖励精英弹窗
			# self.click_image(
			#     self.get_resource_path("images/fubenjiangli.png"),
			#     self.confidenceNum,
			#     (
			#         self.locationX,
			#         self.locationY,
			#         self.locationWidth,
			#         self.locationHeight,
			#     ),
			# )
			# 关闭右边
			self.click_image(
				self.get_resource_path("images/closeright.png"),
				self.confidenceNum,
			)
			# 点击拒绝
			self.click_image(
				self.get_resource_path("images/jujue.png"),
				self.confidenceNum,
			)
			# 点自动
			if self.scriptName == "官渡" or self.scriptName == "祭坛魔镜":
				self.click_image(
					self.get_resource_path("images/zidong.png"),
					self.confidenceNum,
				)
			time.sleep(0.5)

	def addBloud(self):
		self.click_image(self.get_resource_path("images/addBloud.png"), self.confidenceNum, )
		self.click_image(self.get_resource_path("images/addBloud1.png"), self.confidenceNum, )
		self.click_image(self.get_resource_path("images/addBloud.png"), self.confidenceNum, )
		self.click_image(self.get_resource_path("images/addBloud1.png"), self.confidenceNum, )

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
		# 点击x
		self.click_image(
			self.get_resource_path("images/close.png"),
			self.confidenceNum,
		)
		self.click_image(self.get_resource_path("images/closetalk.png"), self.confidenceNum)
		self.click_image(
			self.get_resource_path("images/hide.png"),
			self.confidenceNum)
		with condition:
			if self.stoped:
				condition.wait()
		self.click_image(
			self.get_resource_path("images/yes.png"),
			self.confidenceNum)
		time.sleep(0.5)
		with condition:
			if self.stoped:
				condition.wait()
		self.click_image(
			self.get_resource_path("images/yes.png"),
			self.confidenceNum)

	# if not check:
	# 	yseXY = pyautogui.locateCenterOnScreen(
	# 		self.get_resource_path("images/yes.png"),
	# 		confidence=self.confidenceNum,
	# 		region=(
	# 			self.locationX,
	# 			self.locationY,
	# 			self.locationWidth,
	# 			self.locationHeight,
	# 		),
	# 	)
	# 	if yseXY:
	# 		pyautogui.click(yseXY.x, yseXY.y)
	# 	time.sleep(0.5)
	# 	with condition:
	# 		if self.stoped:
	# 			condition.wait()
	# 	yseXY = pyautogui.locateCenterOnScreen(
	# 		self.get_resource_path("images/yes.png"),
	# 		confidence=self.confidenceNum,
	# 		region=(
	# 			self.locationX,
	# 			self.locationY,
	# 			self.locationWidth,
	# 			self.locationHeight,
	# 		),
	# 	)
	# 	if yseXY:
	# 		pyautogui.click(yseXY.x, yseXY.y)
	# else:
	# 	showBloudLocation = pyautogui.locateCenterOnScreen(
	# 		self.get_resource_path("images/xianshixueliang.png"),
	# 		confidence=self.confidenceNum,
	# 		region=(
	# 			self.locationX,
	# 			self.locationY,
	# 			self.locationWidth,
	# 			self.locationHeight,
	# 		),
	# 	)
	# 	if showBloudLocation:
	# 		noXY = pyautogui.locateCenterOnScreen(
	# 			self.get_resource_path("images/noCheck.png"),
	# 			confidence=self.confidenceNum,
	# 			region=(
	# 				showBloudLocation.left,
	# 				showBloudLocation.top - 20,
	# 				120,
	# 				40,
	# 			),
	# 		)
	# 		if noXY:
	# 			pyautogui.click(noXY.x, noXY.y)
	# 	else:
	# 		noXY = pyautogui.locateCenterOnScreen(
	# 			self.get_resource_path("images/noCheck.png"),
	# 			confidence=self.confidenceNum,
	# 			region=(
	# 				showBloudLocation.left,
	# 				showBloudLocation.top - 20,
	# 				120,
	# 				40,
	# 			),
	# 		)
	# 		if noXY:
	# 			pyautogui.click(noXY.x, noXY.y)
	# 		time.sleep(0.5)
	# 		noXY = pyautogui.locateCenterOnScreen(
	# 			self.get_resource_path("images/noCheck.png"),
	# 			confidence=self.confidenceNum,
	# 			region=(
	# 				showBloudLocation.left,
	# 				showBloudLocation.top - 20,
	# 				120,
	# 				40,
	# 			),
	# 		)
	# 		if noXY:
	# 			pyautogui.click(noXY.x, noXY.y)

	# self.click_image(
	# 	self.get_resource_path("images/yes.png"),
	# 	self.confidenceNum,
	# 	(self.locationX, self.locationY, self.locationWidth, self.locationHeight),
	# )

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
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			if self.find_template_location(
					current,
					self.confidenceNum,
					'location',
			):
				break
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			if self.find_template_location(
					self.get_resource_path("images/xiulian.png"),
					self.confidenceNum,
					'location',
			):
				break
		locationOut = self.find_template_location(
			self.get_resource_path("images/xiulian.png"),
			self.confidenceNum,
			'center',
		)
		with condition:
			if self.stoped:
				condition.wait()
		self.autoClick.mouse_click(int(locationOut.x - 20), int(locationOut.y - 40))
		locationQueding = self.waitFor(
			self.get_resource_path("images/queding.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			),
			3,
		)
		if locationQueding:
			self.autoClick.mouse_click(locationQueding.x, locationQueding.y)
			huodetongbiLocation = self.waitFor(self.get_resource_path("images/huodetongbi.png"), (
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), 1)
			if huodetongbiLocation:
				self.autoClick.mouse_click(huodetongbiLocation.x, huodetongbiLocation.y)
		else:
			return

	# 飞整点等到打完
	def feiZhengDian(self, fei_image, base_image, scroll_deg):
		findSmallFeiTime = time.time()
		while not self.find_template_location(
				fei_image,
				self.confidenceNum,
				'location',
		):
			if time.time() - findSmallFeiTime > 15:
				return
			# 去除获得铜币黑框
			self.click_image(
				self.get_resource_path("images/huodetongbi.png"),
				self.confidenceNum)
			with condition:
				if self.stoped:
					condition.wait()
			jindutiaoLocation = self.find_template_location(
				self.get_resource_path("images/downTalk.png"),
				self.confidenceNum,
				'center',
			)
			if jindutiaoLocation:
				self.autoClick.move_to(jindutiaoLocation.x, jindutiaoLocation.y)
				self.autoClick.scroll_up(jindutiaoLocation.x, jindutiaoLocation.y)
		findShengXiaoTime = time.time()
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			if time.time() - findShengXiaoTime > 5:
				return
			self.shengxiaoLocation = self.find_template_location(
				fei_image, self.confidenceNum, 'location',
			)
			if self.shengxiaoLocation is not None:
				break
		feiTime = time.time()
		while not self.find_template_location(
				base_image, self.confidenceNum, 'location',
		):
			if time.time() - feiTime > 6:
				return
			with condition:
				if self.stoped:
					condition.wait()
			feiLocation = self.waitFor(
				self.get_resource_path("images/fei.png"),
				(
					self.shengxiaoLocation.left - 50,
					self.shengxiaoLocation.top,
					self.shengxiaoLocation.left + 150,
					self.shengxiaoLocation.top + 45,
				),
				2,
			)
			if feiLocation:
				self.autoClick.mouse_click(feiLocation.x, feiLocation.y)
				self.autoClick.move_to(feiLocation.x - 200, feiLocation.y - 200)
				time.sleep(1.3)
			else:
				return
		# 去除获得铜币黑框
		self.click_image(
			self.get_resource_path("images/huodetongbi.png"),
			self.confidenceNum,
		)
		time.sleep(0.2)
		# 有人在打
		hasZhengDian = self.click_image(
			self.get_resource_path("images/dajiuda.png"),
			self.confidenceNum,
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
			if self.find_template_location(
					self.get_resource_path("images/zdzd.png"),
					self.confidenceNum, 'location',
			):
				zhengdianHas = True
				break
			yourendaLocation = self.find_template_location(
				self.get_resource_path("images/yourenda1.png"),
				self.confidenceNum, 'center',
			)
			if yourendaLocation:
				self.autoClick.mouse_click(yourendaLocation.x, yourendaLocation.y)
				zhengdianHas = False
				break
		if not zhengdianHas:
			return
		self.waitFor(
			self.get_resource_path("images/zdjs.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			),
		)

	# # 在屏幕找整点
	# def findZd_and_click(self, image_path_1, image_path_2, image_path_3):
	# 	# 找到屏幕上所有匹配第一张图片的位置
	# 	matches_1 = list(pyautogui.locateAllOnScreen(image_path_1, confidence=self.confidenceNum, region=(self.locationRightTopX, self.locationRightTopY, self.locationRightTopWidth, self.locationRightTopHeight)))
	# 	if not matches_1:
	# 		print("没有找到第一张图片。")
	# 		return
	# 	for match_1 in matches_1:
	# 		# 获取第一张图片位置的中心点坐标
	# 		x_1, y_1 = pyautogui.center(match_1)
	# 		# 移动鼠标到第一张图片位置
	# 		pyautogui.moveTo(x_1, y_1)
	# 		# 等待鼠标移动到该位置
	# 		time.sleep(0.5)
	# 		# 在该位置查找第二张图片
	# 		match_2 = pyautogui.locateOnScreen(image_path_2)
	#
	# 		if match_2:
	# 			x_2, y_2 = pyautogui.center(match_2)
	# 			pyautogui.click(x_2, y_2)
	# 			time.sleep(0.5)
	#
	# 		# 查找第三张图片
	# 		match_3 = pyautogui.locateOnScreen(image_path_3)
	#
	# 		if match_3:
	# 			x_3, y_3 = pyautogui.center(match_3)
	# 			return x_3, y_3
	#
	# 	return None

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
			self.get_resource_path("images/opentalk.png"),
			(
				self.locationX,
				int(self.locationY + (self.locationHeight * 0.5)),
				int(self.locationWidth * 0.5),
				self.locationHeight,
			),
		)
		if openTalkXY:
			self.autoClick.mouse_click(openTalkXY.x, openTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(openTalkXY.x, openTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(openTalkXY.x, openTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(openTalkXY.x, openTalkXY.y)
		bangpaiTalkXY = self.waitFor(
			self.get_resource_path("images/bangpaitalk.png"),
			(
				self.locationX,
				int(self.locationY + (self.locationHeight * 0.5)),
				int(self.locationWidth * 0.5),
				self.locationHeight,
			),
		)
		if bangpaiTalkXY:
			self.autoClick.mouse_click(bangpaiTalkXY.x, bangpaiTalkXY.y)
		huodongTalkXY = self.waitFor(
			self.get_resource_path("images/huodongtalk.png"),
			(
				self.locationX,
				int(self.locationY + (self.locationHeight * 0.5)),
				int(self.locationWidth * 0.5),
				self.locationHeight,
			),
		)
		if huodongTalkXY:
			self.autoClick.mouse_click(huodongTalkXY.x, huodongTalkXY.y)
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
			self.get_resource_path("images/niushengxiao1.png"),
			self.get_resource_path("images/mohunshan.png"),
			350,
		)
		# 飞老虎
		self.feiZhengDian(
			self.get_resource_path("images/hushengxiao1.png"),
			self.get_resource_path("images/jiulizujitan.png"),
			350,
		)
		# 飞兔子
		self.feiZhengDian(
			self.get_resource_path("images/tushengxiao1.png"),
			self.get_resource_path("images/xuzhou.png"),
			200,
		)
		# 飞牛
		self.feiZhengDian(
			self.get_resource_path("images/niushengxiao1.png"),
			self.get_resource_path("images/mohunshan.png"),
			300,
		)
		# 飞老虎
		self.feiZhengDian(
			self.get_resource_path("images/hushengxiao1.png"),
			self.get_resource_path("images/jiulizujitan.png"),
			350,
		)
		# 飞兔子
		self.feiZhengDian(
			self.get_resource_path("images/tushengxiao1.png"),
			self.get_resource_path("images/xuzhou.png"),
			200,
		)
		# 飞猴子
		self.feiZhengDian(
			self.get_resource_path("images/houshengxiao1.png"),
			self.get_resource_path("images/youanmilin.png"),
			100,
		)
		# 将进度条拖动到最底下
		dragBox = self.waitFor(
			self.get_resource_path("images/dragBox.png"),
			(
				self.locationX,
				int(self.locationY + (self.locationHeight * 0.5)),
				int(self.locationWidth * 0.5),
				self.locationHeight,
			),
		)
		if dragBox:
			self.autoClick.move_to(dragBox.x, dragBox.y)
			self.autoClick.left_down(dragBox.x, dragBox.y)
			self.autoClick.move_to(dragBox.x, dragBox.y + 150)
			# pyautogui.dragRel(0, 150, duration=0.5)
			time.sleep(0.5)
			self.autoClick.left_up(dragBox.x, dragBox.y)
			# 飞羊
			self.feiZhengDian(
				self.get_resource_path("images/yangshengxiao1.png"),
				self.get_resource_path("images/moguxi.png"),
				300,
			)
			# 飞猴子
			self.feiZhengDian(
				self.get_resource_path("images/houshengxiao1.png"),
				self.get_resource_path("images/youanmilin.png"),
				350,
			)
			# 飞羊
			self.feiZhengDian(
				self.get_resource_path("images/yangshengxiao1.png"),
				self.get_resource_path("images/moguxi.png"),
				350,
			)
		closeTalkXY = self.waitFor(
			self.get_resource_path("images/closetalk.png"),
			(
				self.locationX,
				int(self.locationY + (self.locationHeight * 0.5)),
				int(self.locationWidth * 0.5),
				self.locationHeight,
			),
		)
		if closeTalkXY:
			self.autoClick.mouse_click(closeTalkXY.x, closeTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(closeTalkXY.x, closeTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(closeTalkXY.x, closeTalkXY.y)
			time.sleep(0.2)
			self.autoClick.mouse_click(closeTalkXY.x, closeTalkXY.y)
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
			self.mojingWhile()

	# 飞副本
	def feiFb(self, image_path, isJy):
		# 打开副本
		tuLocation = self.waitFor(
			self.get_resource_path("images/xiulian.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			),
		)
		if tuLocation:
			self.autoClick.mouse_click(int(tuLocation.x + 24), int(tuLocation.y - 34))
		time.sleep(0.8)
		if isJy:
			self.click_image(
				self.get_resource_path("images/activejy.png"),
				self.confidenceNum
			)
			self.click_image(
				self.get_resource_path("images/unActivejy.png"),
				self.confidenceNum
			)
			findPerTime = time.time()
			while True:
				with condition:
					if self.stoped:
						condition.wait()
				if time.time() - findPerTime > 10:
					return False
				imagePathLocation = self.find_template_location(
					image_path,
					self.confidenceNum, 'location',
				)
				if imagePathLocation:
					break
			feiLocation = self.waitFor(
				self.get_resource_path("images/fubenfei.png"),
				(
					imagePathLocation.left,
					imagePathLocation.top,
					imagePathLocation.width,
					imagePathLocation.height,
				),
			)
			if feiLocation:
				self.autoClick.mouse_click(feiLocation.x, feiLocation.y)
		else:
			self.click_image(
				self.get_resource_path("images/activeFb.png"),
				self.confidenceNum
			)
			self.click_image(
				self.get_resource_path("images/unActiveFb.png"),
				self.confidenceNum
			)
			while not self.find_template_location(
					image_path, self.confidenceNum, 'location'
			):

				downTalk = self.waitFor(
					self.get_resource_path("images/downFuben.png"),
					(
						self.locationX,
						self.locationY,
						int(self.locationWidth * 0.75),
						self.locationHeight,
					),
				)
				if downTalk:
					for i in range(10):
						self.autoClick.mouse_click(downTalk.x, downTalk.y)
					time.sleep(1)
			findPerTime = time.time()
			while True:
				with condition:
					if self.stoped:
						condition.wait()
				if time.time() - findPerTime > 15:
					return False
				imagePathLocation = self.find_template_location(
					image_path, self.confidenceNum, 'location',
				)
				if imagePathLocation:
					break
			feiLocation = self.waitFor(
				self.get_resource_path("images/fubenfei.png"),
				(
					imagePathLocation.left,
					imagePathLocation.top,
					imagePathLocation.width,
					imagePathLocation.height,
				),
			)
			if feiLocation:
				self.autoClick.mouse_click(feiLocation.x, feiLocation.y)
		return True

	# 找图并且点击
	def click_image(self, image_path, image_confidence):
		res = self.autoClick.mouse_click_image(image_path, image_confidence)
		return res

	# 找出一样的图，点击第N个图
	# def click_nth_image(self, image_path, image_region, n):
	# 	images = list(
	# 		pyautogui.locateAllOnScreen(
	# 			image_path, confidence=self.confidenceNum, region=image_region
	# 		)
	# 	)
	# 	if len(images) >= n:
	# 		with condition:
	# 			if self.stoped:
	# 				condition.wait()
	# 		target_location = images[n - 1]
	# 		target_x = target_location.left + target_location.width // 2
	# 		target_y = target_location.top + target_location.height // 2
	# 		pyautogui.click(target_x, target_y, clicks=1, interval=0.01)
	# 		return True
	# 	else:
	# 		return False

	# 找一样的图，点击最左边的图
	def click_image_with_min_x(self, image_path, image_region, image_path2):
		image_locations = list(self.find_template_location(
			image_path, self.confidenceNum, 'all'
		))
		if image_locations:
			with condition:
				if self.stoped:
					condition.wait()
			min_x_match = min(image_locations, key=lambda match: match['result'][0])
			# 获取匹配项的中心坐标
			center_x = min_x_match['result'][0] + min_x_match['rectangle'][2] // 2
			center_y = min_x_match['result'][1] + min_x_match['rectangle'][3] // 2
			if image_path2 == self.zdzdPath:
				for i in range(3):
					self.autoClick.mouse_click(center_x, int(center_y - 90))
					time.sleep(0.008)
				self.autoClick.move_to(center_x + 200, center_y + 200)
				time.sleep(1)
			else:
				self.autoClick.mouse_click(center_x, center_y)
				self.autoClick.move_to(center_x + 200, center_y + 200)
			self.clickBTime = time.time()
			self.clickBX = center_x
			self.clickBy = center_y
			self.autoClick.move_to(center_x + 200, center_y + 200)
			return True
		else:
			return False

	def click_image_with_min_x1(self, image_path, image_region, image_path2):
		image_locations = list(self.find_template_location(
			image_path, self.confidenceNum, 'all'
		))
		if image_locations:
			with condition:
				if self.stoped:
					condition.wait()
			min_x_match = min(image_locations, key=lambda loc: loc['result'][0])
			# 获取匹配项的中心坐标
			center_x = min_x_match['result'][0] + min_x_match['rectangle'][2] // 2
			center_y = min_x_match['result'][1] + min_x_match['rectangle'][3] // 2
			if image_path2 == self.zdzdPath:
				for i in range(3):
					self.autoClick.mouse_click(center_x, int(center_y))
					time.sleep(0.008)
				self.autoClick.move_to(center_x + 200, center_y + 200)
				time.sleep(1)
			else:
				self.autoClick.mouse_click(center_x, center_y)
				self.autoClick.move_to(center_x + 200, center_y + 200)
			self.clickBTime = time.time()
			self.clickBX = center_x
			self.clickBy = center_y
			self.autoClick.move_to(center_x + 200, center_y + 200)
			return True
		else:
			return False

	# 等待图片出现
	def waitFor(self, image_path, image_region, timeout=None):
		start_time = time.time()
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			xy = self.find_template_location(
				image_path, self.confidenceNum, 'center'
			)
			if xy:
				break
			if timeout is not None:
				if time.time() - start_time > timeout:
					return False
			time.sleep(0.1)
			if self.confidenceNum > 0.8:
				self.confidenceNum -= 0.1
		self.confidenceNum = 0.9
		return xy

	# 等待两张图片出现
	def waitForTwo(self, image1_path, image2_path, image_region, timeout=None):
		start_time = time.time()
		res = ""
		while True:
			with condition:
				if self.stoped:
					condition.wait()
			xy = self.find_template_location(
				image1_path, self.confidenceNum, 'center'
			)
			if xy:
				res = "first"
				break
			xy2 = self.find_template_location(
				image2_path, self.confidenceNum, 'center'
			)
			if xy2:
				res = "second"
				break
			if timeout is not None:
				if time.time() - start_time > timeout:
					return False
			time.sleep(0.1)
		# 	if self.confidenceNum > 0.8:
		# 		self.confidenceNum -= 0.1
		# self.confidenceNum = 0.9
		return res

	# 等待图片1出现，一直点击图2
	def waitForAAndClickB1(
			self,
			image_pathA,
			image_pathB,
			image_regionA,
			image_regionB=None
	):
		if not image_regionB:
			image_regionB = (
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			)
		while not self.find_template_location(
				image_pathA, self.confidenceNum, 'location'
		):
			with condition:
				if self.stoped:
					condition.wait()
			clickB = self.click_image(
				image_pathB,
				self.confidenceNum
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
		while not self.find_template_location(
				image_pathA, self.confidenceNum, 'location'
		) or not self.find_template_location(
			image_pathA2, self.confidenceNum, 'location'
		):
			with condition:
				if self.stoped:
					condition.wait()
			clickB = self.click_image(
				image_pathB,
				self.confidenceNum
			)
			if clickB:
				break
			clickB = self.click_image(
				image_pathB2,
				self.confidenceNum
			)
			if clickB:
				break

	# 使用键盘命令找图
	def press_keys_until_image_found(self, image_path, image_path1, image_path2, key1, key2, key2DownTime=0.6):
		key1IsUp = False
		# 去除获得铜币黑框
		self.click_image(
			self.get_resource_path("images/huodetongbi.png"),
			self.confidenceNum
		)
		if key2:
			self.autoClick.push_key(key2, key2DownTime)
		while not self.find_template_location(
				image_path2, self.confidenceNum, 'location'
		):
			with condition:
				if self.stoped:
					condition.wait()
			if key1 and not key1IsUp:
				self.autoClick.key_down(key1)
				key1IsUp = True
			# 去除获得铜币黑框
			self.click_image(
				self.get_resource_path("images/huodetongbi.png"),
				self.confidenceNum
			)
			image_pathisOk = self.find_template_location(image_path, self.confidenceNum, 'location')
			if image_pathisOk:
				if key1:
					self.autoClick.key_up(key1)
					key1IsUp = True
				self.click_image_with_min_x1(
					image_path,
					(
						self.locationX,
						self.locationY,
						self.locationWidth,
						self.locationHeight,
					),
					image_path2,
				)
			image_path1isOk = self.find_template_location(image_path1, self.confidenceNum, 'location')
			if image_path1isOk:
				if key1:
					self.autoClick.key_up(key1)
					key1IsUp = True
				self.click_image_with_min_x1(
					image_path1,
					(
						self.locationX,
						self.locationY,
						self.locationWidth,
						self.locationHeight,
					),
					image_path2,
				)
		# 点过b之后如果过了4秒还没有找到C，重新点一次b的坐标
		if self.clickBTime > 0 and time.time() - self.clickBTime > 4:
			self.autoClick.mouse_click(self.clickBX, self.clickBy)
			self.clickBTime = time.time()
		if key1:
			self.autoClick.key_up(key1)

	def get_random_number(self):
		numbers = [-2, -1, 0, 1, 2]
		return random.choice(numbers)

	# 点小地图
	def clickDitu(self, x, y, find_image, find_region, break_image):
		while not self.find_template_location(break_image, self.confidenceNum, 'location'):
			self.autoClick.mouse_click(int(x + self.get_random_number()), int(y + self.get_random_number()))
			time.sleep(0.1)
			isFind = self.click_image_with_min_x1(find_image, find_region, break_image)
			if isFind:
				time.sleep(0.7)
			else:
				time.sleep(0.3)

	# 找图并且点击6
	def findAndClickPic(self, A, B1, B2, C1, C2, D, E, E2=None, E2DownTime=0.6):
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
				A, (
					self.locationRightTopX,
					self.locationRightTopY,
					self.locationRightTopWidth,
					self.locationRightTopHeight,
				)
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
			# 去除获得铜币黑框
			self.click_image(
				self.get_resource_path("images/huodetongbi.png"),
				self.confidenceNum
			)
			# 按下E2
			if E2 and not E2IsDown:
				self.autoClick.push_key(E2, E2DownTime)
				E2IsDown = True
			# 开始找C的时间
			startTime = time.time()
			while not self.find_template_location(
					C1, self.confidenceNum, 'location'
			):
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
				if D and not self.BisClick:
					with condition:
						if self.stoped:
							condition.wait()
					self.click_image(D, self.confidenceNum)
				# Dxy = pyautogui.locateCenterOnScreen(
				# 	D,
				# 	confidence=self.confidenceNum,
				# 	region=(
				# 		self.locationX,
				# 		self.locationY,
				# 		self.locationWidth,
				# 		self.locationHeight,
				# 	),
				# )
				# if Dxy:
				# 	pyautogui.click(Dxy.x, Dxy.y, clicks=2, interval=0.01)
				#     点击按钮E
				# if E:
				# 	self.press_keys_until_image_found(B1, C1, E, E2, E2DownTime)

				while E != "" and not EIsDown:
					with condition:
						if self.stoped:
							condition.wait()
					self.autoClick.key_down(E)
					B1Location = self.waitFor(
						B1,
						(
							self.locationX,
							self.locationY,
							self.locationWidth,
							self.locationHeight,
						),
					)
					if B1Location:
						EIsDown = True
						self.autoClick.key_up(E)
					# if E2 is not None and E2IsDown:
					# 	keyboard.release(E2)
					# break
					isClick = self.click_image_with_min_x(
						B1,
						(
							self.locationX,
							self.locationY,
							self.locationWidth,
							self.locationHeight,
						),
						C1,
					)
					# if isClick:
					# 	if E2 is not None and E2IsDown:
					# 		keyboard.release(E2)
					# 	break
					if self.find_template_location(
							C1, self.confidenceNum, 'location'
					):
						EIsDown = True
						time.sleep(0.1)
						self.autoClick.key_up(E)
						# if E2 is not None and E2IsDown:
						# 	pyautogui.keyUp(E2)
						break
				# 	if self.confidenceNum > 0.8:
				# 		self.confidenceNum -= 0.1
				# self.confidenceNum = 0.9
				# if E != "" and EIsDown:
				# 	keyboard.release(E)
				# 	if E2 is not None and E2IsDown:
				# 		keyboard.release(E2)
				with condition:
					if self.stoped:
						condition.wait()
				if self.find_template_location(
						C1, self.confidenceNum, 'location'
				):
					break
				# 点击B
				self.BisClick = self.click_image_with_min_x(
					B1,
					(
						self.locationX,
						self.locationY,
						self.locationWidth,
						self.locationHeight,
					),
					C1,
				)
				# 点过b之后如果过了4秒还没有找到C，重新点一次b的坐标
				if self.clickBTime > 0 and time.time() - self.clickBTime > 4:
					self.autoClick.mouse_click(self.clickBX, self.clickBy)
					self.clickBTime = time.time()
		# 	if self.confidenceNum > 0.8:
		# 		self.confidenceNum -= 0.1
		# self.confidenceNum = 0.9
		except Exception as e:
			self.show_error_message(f"发生错误: {e}")

	# if E != "":
	# 	with condition:
	# 		if self.stoped:
	# 			condition.wait()
	# 	pyautogui.keyUp(E)

	# 官渡脚本
	def guanduScript(self):
		self.guanDuCount += 1
		print(f"第{self.guanDuCount}次官渡.")
		with condition:
			if self.stoped:
				condition.wait()
		isInGuanDu = self.waitFor(self.get_resource_path("images/guanDu1.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		if not isInGuanDu:
			self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
		# 进入官渡
		self.findAndClickPic(
			self.get_resource_path("images/guanDu1.png"),
			self.get_resource_path("images/caoCao.png"),
			self.get_resource_path("images/caoCao2.png"),
			self.get_resource_path("images/inguanDu.png"),
			self.get_resource_path("images/inguanDu.png"),
			self.get_resource_path("images/guanduD.png"),
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 进入第一层
		self.waitForAAndClickB1(
			self.get_resource_path("images/dazhang.png"),
			self.get_resource_path("images/inguanDu.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), None,
		)
		self.waitFor(self.get_resource_path("images/caoyindazhang.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		), 5)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/guanDu1.png"),
		# 	self.get_resource_path("images/inguanDu.png"),
		# 	self.get_resource_path("images/inguanDu.png"),
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	"",
		# 	"",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		self.waitForAAndClickB1(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/dycrk2.png"),
		# 	self.get_resource_path("images/dycrk2.png"),
		# 	self.get_resource_path("images/caoyuanzhanchang.png"),
		# 	self.get_resource_path("images/caoyuanzhanchang.png"),
		# 	"",
		# 	"",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# 第一个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 第二个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 第三个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 第四个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 第五个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 第6个河北军
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/hbj4.png"),
			self.get_resource_path("images/hbj1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 颜良
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/yanliang.png"),
			self.get_resource_path("images/yanliang1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 文丑
		self.findAndClickPic(
			self.get_resource_path("images/caoyuanzhanchang.png"),
			self.get_resource_path("images/wenchou.png"),
			self.get_resource_path("images/wenchou1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"right",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 去大帐
		self.waitForAAndClickB1(
			self.get_resource_path("images/dazhang.png"),
			self.get_resource_path("images/chuansongmenLeft.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		self.waitFor(self.get_resource_path("images/dazhang.png"), (
			self.locationRightTopX,
			self.locationRightTopY,
			self.locationRightTopWidth,
			self.locationRightTopHeight,
		))
		# self.findAndClickPic(
		# 	self.get_resource_path("images/caoyuanzhanchang.png"),
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/godazhang.png"),
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	"",
		# 	"left",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# 找到曹操进入乌巢
		self.waitForAAndClickB1(
			self.get_resource_path("images/gowuchao.png"),
			self.get_resource_path("images/xiaolvren.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/caochengxiang.png"),
		# 	self.get_resource_path("images/caochengxiang1.png"),
		# 	self.get_resource_path("images/gowuchao.png"),
		# 	self.get_resource_path("images/gowuchao.png"),
		# 	"",
		# 	"down",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		self.waitForAAndClickB1(
			self.get_resource_path("images/wuchao.png"),
			self.get_resource_path("images/gowuchao.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), None,
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/caoyindazhang.png"),
		# 	self.get_resource_path("images/gowuchao.png"),
		# 	self.get_resource_path("images/gowuchao.png"),
		# 	self.get_resource_path("images/wuchao.png"),
		# 	self.get_resource_path("images/wuchao.png"),
		# 	"",
		# 	"",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# 进入魂殿打魂
		# self.findAndClickPic(self.get_resource_path("images/wuchao.png"), self.get_resource_path("images/inhundian1.png"), self.get_resource_path("images/inhundian1.png"),self.get_resource_path("images/hundian.png"),self.get_resource_path("images/hundian.png"),'', 'left')
		# with condition:
		#   if self.stoped:
		#     condition.wait()
		self.findAndClickPic(
			self.get_resource_path("images/wuchao.png"),
			self.get_resource_path("images/wenchouzhihun.png"),
			self.get_resource_path("images/wenchouzhihun1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"left",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 魂殿进乌巢
		self.waitForAAndClickB1(
			self.get_resource_path("images/wuchao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
		)
		# self.findAndClickPic(
		# 	self.get_resource_path("images/hundian.png"),
		# 	self.get_resource_path("images/gowuchao2.png"),
		# 	self.get_resource_path("images/gowuchao2.png"),
		# 	self.get_resource_path("images/wuchao.png"),
		# 	self.get_resource_path("images/wuchao.png"),
		# 	"",
		# 	"",
		# )
		with condition:
			if self.stoped:
				condition.wait()
		# 打淳
		self.findAndClickPic(
			self.get_resource_path("images/wuchao.png"),
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
		self.findAndClickPic(
			self.get_resource_path("images/wuchao.png"),
			self.get_resource_path("images/yuanshao.png"),
			self.get_resource_path("images/yuanshao1.png"),
			self.get_resource_path("images/zdzd.png"),
			self.get_resource_path("images/zdzd1.png"),
			"",
			"",
		)
		with condition:
			if self.stoped:
				condition.wait()
		# 退出副本
		self.outScript(self.get_resource_path("images/wuchao.png"))

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
		# self.waitForAAndClickB1(
		# 	self.get_resource_path("images/zhanhun/inzhanhun.png"),
		# 	self.get_resource_path("images/zhanhun/zhanhun.png"),
		# 	(
		# 		self.locationX,
		# 		self.locationY,
		# 		self.locationWidth,
		# 		self.locationHeight,
		# 	), None,
		# )
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
		if self.zhanhunFloor == '21层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou21.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/yuanshao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
		if self.zhanhunFloor == '22层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou22.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/caocao.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
		if self.zhanhunFloor == '23层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou23.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/lvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
		if self.zhanhunFloor == '24层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou24.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/mohualvbu.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
		if self.zhanhunFloor == '25层':
			# 退出副本
			self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou25.png"))
			return True
		self.addBloud()
		self.waitForAAndClickB1(
			self.get_resource_path("images/zhanhun/renshengwa.png"),
			self.get_resource_path("images/chuansongmen.png"),
			(
				self.locationX,
				self.locationY,
				self.locationWidth,
				self.locationHeight,
			), (
				self.locationRightTopX,
				self.locationRightTopY,
				self.locationRightTopWidth,
				self.locationRightTopHeight,
			),
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
			return
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
			self.get_resource_path("images/liandan/liandanD.png"),
			"",
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
		guaiwugongjiLocation = self.find_template_location(self.get_resource_path("images/guaiwugongji.png"), self.confidenceNum, 'location')
		if guaiwugongjiLocation:
			self.click_image(self.get_resource_path("images/check.png"), self.confidenceNum)
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
		guaiwugongjiLocation = self.find_template_location(self.get_resource_path("images/heifeng/guaiwugongji.png"), self.confidenceNum, 'location')
		if guaiwugongjiLocation:
			self.click_image(self.get_resource_path("images/heifeng/check.png"), self.confidenceNum)
		for i in range(self.heifengWhileCount):
			self.heifengScript()
			if self.heifengCount == self.heifengWhileCount:
				break
		print(f"{self.heifengWhileCount}次黑风已完成,去官渡")
		self.guanduWhile()

	# 一直执行官渡
	def guanduWhile(self):
		self.beginFun()
		while True:
			self.guanduScript()

	# 一直执行红
	def hongWhile(self):
		self.beginFun()
		while True:
			hongRes = self.hongScript()
			if not hongRes:
				print('红没次数')
				break
		self.guanduWhile()

	# 一直执行战魂
	def zhanhunWhile(self):
		self.beginFun()
		while True:
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
		# 飞80精英
		self.feiFb(self.get_resource_path("images/dituzuocifenshen.png"), True)
		time.sleep(1)
		self.bamenScript()
		# 飞云游精英
		self.feiFb(self.get_resource_path("images/dituyunyouxianren.png"), True)
		time.sleep(1)
		self.yunyouJyScript()
		# 飞100精英
		self.feiFb(self.get_resource_path("images/ditulieshuren.png"), True)
		time.sleep(1)
		self.laoshuJyScript()
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
				"五行",
				"溶洞",
				"炼丹",
				"官渡精英",
				"云游精英",
				"80精英",
				"100精英",
				"整点",
				"test",
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

	def on_button_click(self, event):
		dialog = MyDialog(self)
		if dialog.ShowModal() == wx.ID_OK:
			# 在对话框结束后，获取对话框中输入的数据
			print(self.game_name)

		dialog.Destroy()

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
			"7.日常脚本:炼丹=>五行=>溶洞=>80精英=>云游精英=>100精英=>官渡精英=>官渡；",
			"8.自动去打的官渡都带整点。",
			"使用说明：",
			"1.请将电脑的屏幕分辨率调到1920*1080；",
			"2.请将电脑的缩放比放到100%;",
			"3.请将游戏所在浏览器缩放比放到100%(缩小到左右没有白边即可)。"
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
		if self.scriptName == '战魂楼(精英)' or self.scriptName == '战魂+红+整点':
			self.choiceCeng.Show()
		else:
			self.choiceCeng.Hide()
		if self.scriptName == '黑风山寨':
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
		if self.team_leader_text.GetValue() and self.teammate1_text.GetValue() and self.teammate2_text.GetValue():
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


class AutoClick():
	"""
	@description  :自动点击类，包含后台截图、图像匹配
	---------
	@param  :
	-------
	@Returns  :
	-------
	"""

	__PostMessageW = windll.user32.PostMessageW
	__SendMessageW = windll.user32.SendMessageW
	__MapVirtualKeyW = windll.user32.MapVirtualKeyW
	__VkKeyScanA = windll.user32.VkKeyScanA
	__ClientToScreen = windll.user32.ClientToScreen
	# __PostMessageW = win32gui.PostMessage
	# __SendMessageW = win32gui.SendMessage
	# __MapVirtualKeyW = win32api.MapVirtualKey
	# __VkKeyScanA = win32api.VkKeyScan
	# __ClientToScreen = win32gui.ClientToScreen

	__WM_KEYDOWN = 0x100
	__WM_KEYUP = 0x101
	__WM_MOUSEMOVE = 0x0200
	__WM_LBUTTONDOWN = 0x0201
	__WM_LBUTTONUP = 0x202
	__WM_MOUSEWHEEL = 0x020A
	__WHEEL_DELTA = 120
	__WM_SETCURSOR = 0x20
	__WM_MOUSEACTIVATE = 0x21

	__HTCLIENT = 1
	__MA_ACTIVATE = 1

	__VkCode = {
		"back": 0x08,
		"tab": 0x09,
		"return": 0x0D,
		"shift": 0x10,
		"control": 0x11,
		"menu": 0x12,
		"pause": 0x13,
		"capital": 0x14,
		"escape": 0x1B,
		"space": 0x20,
		"end": 0x23,
		"home": 0x24,
		"left": 0x25,
		"up": 0x26,
		"right": 0x27,
		"down": 0x28,
		"print": 0x2A,
		"snapshot": 0x2C,
		"insert": 0x2D,
		"delete": 0x2E,
		"lwin": 0x5B,
		"rwin": 0x5C,
		"numpad0": 0x60,
		"numpad1": 0x61,
		"numpad2": 0x62,
		"numpad3": 0x63,
		"numpad4": 0x64,
		"numpad5": 0x65,
		"numpad6": 0x66,
		"numpad7": 0x67,
		"numpad8": 0x68,
		"numpad9": 0x69,
		"multiply": 0x6A,
		"add": 0x6B,
		"separator": 0x6C,
		"subtract": 0x6D,
		"decimal": 0x6E,
		"divide": 0x6F,
		"f1": 0x70,
		"f2": 0x71,
		"f3": 0x72,
		"f4": 0x73,
		"f5": 0x74,
		"f6": 0x75,
		"f7": 0x76,
		"f8": 0x77,
		"f9": 0x78,
		"f10": 0x79,
		"f11": 0x7A,
		"f12": 0x7B,
		"numlock": 0x90,
		"scroll": 0x91,
		"lshift": 0xA0,
		"rshift": 0xA1,
		"lcontrol": 0xA2,
		"rcontrol": 0xA3,
		"lmenu": 0xA4,
		"rmenu": 0XA5
	}

	def __get_virtual_keycode(self, key: str):
		"""根据按键名获取虚拟按键码

		Args:
			key (str): 按键名

		Returns:
			int: 虚拟按键码
		"""
		if len(key) == 1 and key in string.printable:
			# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscana
			return self.__VkKeyScanA(ord(key)) & 0xff
		else:
			return self.__VkCode[key]

	def key_down(self, key: str):
		"""按下指定按键

		Args:
			handle (HWND): 窗口句柄
			key (str): 按键名
		"""
		vk_code = self.__get_virtual_keycode(key)
		scan_code = self.__MapVirtualKeyW(vk_code, 0)
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keydown
		wparam = vk_code
		lparam = (scan_code << 16) | 1
		self.__PostMessageW(self.__clickhandle, self.__WM_KEYDOWN, wparam, lparam)

	def key_up(self, key: str):
		"""放开指定按键

		Args:
			handle (HWND): 窗口句柄
			key (str): 按键名
		"""
		vk_code = self.__get_virtual_keycode(key)
		scan_code = self.__MapVirtualKeyW(vk_code, 0)
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-keyup
		wparam = vk_code
		lparam = (scan_code << 16) | 0XC0000001
		self.__PostMessageW(self.__clickhandle, self.__WM_KEYUP, wparam, lparam)

	def drag_mouse(self, start_x, start_y, end_x, end_y):
		"""
		在指定窗口句柄中模拟鼠标从 (start_x, start_y) 拖拽到 (end_x, end_y) 的操作。

		:param start_x: 起始横坐标
		:param start_y: 起始纵坐标
		:param end_x: 结束横坐标
		:param end_y: 结束纵坐标
		"""
		self.left_down(int(start_x / scale), int(start_y / scale))
		self.move_to(int(end_x / scale), int(end_y / scale))
		self.left_up(int(end_x / scale), int(end_y / scale))

	def __activate_mouse(self, handle: HWND):
		"""
		@Description : 激活窗口接受鼠标消息
		---------
		@Args : handle (HWND): 窗口句柄
		-------
		@Returns :
		-------
		"""
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mouseactivate
		lparam = (self.__WM_LBUTTONDOWN << 16) | self.__HTCLIENT
		self.__PostMessageW(handle, self.__WM_MOUSEACTIVATE, self.__handle, lparam)

	def __set_cursor(self, handle: HWND, msg):
		"""
		@Description : Sent to a window if the mouse causes the cursor to move within a window and mouse input is not captured
		---------
		@Args : handle (HWND): 窗口句柄, msg : setcursor消息
		-------
		@Returns :
		-------
		"""
		lparam = (msg << 16) | self.__HTCLIENT
		self.__SendMessageW(handle, self.__WM_SETCURSOR, handle, lparam)

	def move_to(self, x: int, y: int):
		"""移动鼠标到坐标（x, y)

		Args:
			x (int): 横坐标
			y (int): 纵坐标
		"""
		print(x, y)
		wparam = 0
		lparam = y << 16 | x
		self.__PostMessageW(self.__clickhandle, self.__WM_MOUSEMOVE, wparam, lparam)

	def left_down(self, x: int, y: int):
		"""在坐标(x, y)按下鼠标左键

		Args:
			x (int): 横坐标
			y (int): 纵坐标
		"""
		wparam = 0x001
		lparam = y << 16 | x
		self.__PostMessageW(self.__clickhandle, self.__WM_LBUTTONDOWN, wparam, lparam)

	def left_up(self, x: int, y: int):
		"""在坐标(x, y)放开鼠标左键

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""

		wparam = 0
		lparam = y << 16 | x
		self.__PostMessageW(self.__clickhandle, self.__WM_LBUTTONUP, wparam, lparam)

	def scroll(self, handle: HWND, delta: int, x: int, y: int):
		"""在坐标(x, y)滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			delta (int): 为正向上滚动，为负向下滚动
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.move_to(handle, x, y)
		wparam = delta << 16
		p = POINT(x, y)
		self.__ClientToScreen(handle, byref(p))
		lparam = p.y << 16 | p.x
		self.__SendMessageW(handle, self.__WM_MOUSEWHEEL, wparam, lparam)

	def scroll_up(self, x: int, y: int):
		"""在坐标(x, y)向上滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.scroll(self.__clickhandle, self.__WHEEL_DELTA, x, y)

	def scroll_down(self, x: int, y: int):
		"""在坐标(x, y)向下滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.scroll(self.__clickhandle, -self.__WHEEL_DELTA, x, y)

	def get_winds(self, title: str):
		"""
		@description : 获取游戏句柄 ,并把游戏窗口置顶并激活窗口
		---------
		@param : 窗口名
		-------
		@Returns : 窗口句柄
		-------
		"""
		# self.__handle = win32gui.FindWindowEx(0, 0, "Qt5QWindowIcon", "MuMu模拟器")
		parent_hwnd = win32gui.FindWindow(None, title)
		self.get_child_windows(parent_hwnd)

		# self.__classname = win32gui.GetClassName(self.__handle)
		# print(self.__classname, self.__handle)
		self.__clickhandle = self.__handle
		if self.__handle:
			return True
		else:
			return False

	def get_child_windows(self, parent_hwnd):
		"""
		打印指定句柄下的所有子孙控件及其位置
		:param parent_hwnd: 父窗口句柄
		"""

		def callback(hwnd, _):
			screen_width, screen_height = pyautogui.size()
			# 获取窗口类名和标题
			class_name = win32gui.GetClassName(hwnd)
			window_title = win32gui.GetWindowText(hwnd)
			# 获取窗口位置
			left, top, right, bottom = win32gui.GetWindowRect(hwnd)
			if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
				print(hwnd)
				self.__handle = hwnd
				print(left, top, right, bottom)
				return
			# 递归调用，查找子控件
			self.get_child_windows(hwnd)
			return True

		# 枚举所有子窗口
		return win32gui.EnumChildWindows(parent_hwnd, callback, None)

	def get_src(self):
		"""
		@description : 获得后台窗口截图
		---------
		@param : None
		-------
		@Returns : None
		-------
		"""

		left, top, right, bot = win32gui.GetWindowRect(self.__handle)
		# Remove border around window (8 pixels on each side)
		bl = 0
		# Remove border on top
		bt = 0

		width = int((right - left + 1) * scale) - 2 * bl
		height = int((bot - top + 1) * scale) - bt - bl
		# 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
		hWndDC = win32gui.GetDC(self.__handle)
		# 创建设备描述表
		mfcDC = win32ui.CreateDCFromHandle(hWndDC)
		# 创建内存设备描述表
		saveDC = mfcDC.CreateCompatibleDC()
		# 创建位图对象准备保存图片
		saveBitMap = win32ui.CreateBitmap()
		# 为bitmap开辟存储空间
		saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
		# 将截图保存到saveBitMap中
		saveDC.SelectObject(saveBitMap)
		# 保存bitmap到内存设备描述表
		saveDC.BitBlt((0, 0), (width, height), mfcDC, (bl, bt), win32con.SRCCOPY)
		###获取位图信息
		bmpinfo = saveBitMap.GetInfo()
		bmpstr = saveBitMap.GetBitmapBits(True)
		###生成图像
		im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
		# 内存释放
		win32gui.DeleteObject(saveBitMap.GetHandle())
		saveDC.DeleteDC()
		mfcDC.DeleteDC()
		win32gui.ReleaseDC(self.__handle, hWndDC)
		###PrintWindow成功,保存到文件,显示到屏幕
		im_PIL.save("src.jpg")  # 保存

	# im_PIL.show()  # 显示

	def recognize(self, template, threshold=0.9):
		"""
		@description : 图像识别之模板匹配
		---------
		@param : 需要匹配的模板名
		-------
		@Returns : 将传进来的图片和全屏截图匹配如果找到就返回图像在屏幕的坐标 否则返回None
		-------
		"""

		imobj = ac.imread(template)
		imsrc = ac.imread('%s\\src.jpg' % os.getcwd())
		pos = ac.find_template(imsrc, imobj, 0.7)
		return pos

	def recognize_all(self, template, threshold=0.9):
		"""
		@description : 图像识别之模板匹配
		---------
		@param : 需要匹配的模板名
		-------
		@Returns : 将传进来的图片和全屏截图匹配如果找到就返回图像在屏幕的坐标 否则返回None
		-------
		"""

		imobj = ac.imread(template)
		imsrc = ac.imread('%s\\src.jpg' % os.getcwd())
		pos = ac.find_all_template(imsrc, imobj, threshold)
		return pos

	def find_image_in_screenshot(self, screenshot, template):
		"""在截图中查找模板图像的位置"""
		result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
		min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
		h, w = template.shape[:2]
		center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
		return center, max_val

	def match_images(self, parent_image_path, template_image_path):
		"""匹配父图像中的模板图像，并返回模板图像在窗口中的中心点"""
		# 读取父图像和模板图像
		parent_image = cv2.imread(parent_image_path)
		template_image = cv2.imread(template_image_path)

		if parent_image is None or template_image is None:
			raise ValueError("图像文件路径无效或图像无法读取")

		# 查找 parent_image 在窗口中的位置
		self.get_src()
		screenshot = ac.imread('%s\\src.jpg' % os.getcwd())

		if screenshot is None:
			raise ValueError("截图无法读取")

		parent_center, parent_confidence = self.find_image_in_screenshot(screenshot, parent_image)
		if parent_confidence < 0.8:  # 可以根据需要调整阈值
			raise ValueError("未找到父图像")

		# 查找 template_image 在 parent_image 中的位置
		template_center, template_confidence = self.find_image_in_screenshot(parent_image, template_image)
		if template_confidence < 0.8:  # 可以根据需要调整阈值
			raise ValueError("未找到模板图像")

		# 计算 template_image 在窗口中的中心点
		final_center = (parent_center[0] + template_center[0], parent_center[1] + template_center[1])
		return final_center

	def grab_screen(self, region=None):
		"""
		截取指定窗口句柄的屏幕区域
		:param hwnd: 窗口句柄
		:param region: 区域元组 (left, top, width, height)
		:return: 截图的numpy数组
		"""
		left, top, right, bottom = win32gui.GetWindowRect(self.__handle)
		if region:
			left += region[0]
			top += region[1]
			right = left + region[2]
			bottom = top + region[3]

		width = right - left
		height = bottom - top

		hwindc = win32gui.GetWindowDC(self.__handle)
		srcdc = win32ui.CreateDCFromHandle(hwindc)
		memdc = srcdc.CreateCompatibleDC()
		bmp = win32ui.CreateBitmap()
		bmp.CreateCompatibleBitmap(srcdc, width, height)
		memdc.SelectObject(bmp)
		memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)

		signedIntsArray = bmp.GetBitmapBits(True)
		img = np.frombuffer(signedIntsArray, dtype='uint8')
		img.shape = (height, width, 4)

		srcdc.DeleteDC()
		memdc.DeleteDC()
		win32gui.ReleaseDC(self.__handle, hwindc)
		img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
		return img

	def find_template_in_region(self, template_img, search_region):
		"""
		在指定窗口句柄的屏幕区域内查找模板图像
		:param hwnd: 窗口句柄
		:param template_img: 模板图像路径或numpy数组
		:param search_region: 查找区域元组 (left, top, width, height)
		:return: 查找结果字典
		"""
		# 截取指定区域的屏幕图像
		screen_img = self.grab_screen(search_region)

		# 读取图像
		template_img = ac.imread(template_img)
		# 查找模板图像
		res = ac.find_template(screen_img, template_img)

		if res['result']:
			# 调整找到的坐标到原始屏幕坐标系
			res['rectangle'] = [
				(res['rectangle'][0][0] + search_region[0], res['rectangle'][0][1] + search_region[1]),
				(res['rectangle'][1][0] + search_region[0], res['rectangle'][1][1] + search_region[1]),
				(res['rectangle'][2][0] + search_region[0], res['rectangle'][2][1] + search_region[1]),
				(res['rectangle'][3][0] + search_region[0], res['rectangle'][3][1] + search_region[1])
			]
			res['result'] = (
				res['result'][0] + search_region[0],
				res['result'][1] + search_region[1]
			)

		return res

	def mouse_click(self, x, y, times=0.5):
		"""
		@description : 单击左键
		---------
		@param : 位置坐标x,y 单击后延时times(s)
		-------
		@Returns :
		-------
		"""
		# self.__set_cursor(self.__clickhandle, self.__WM_MOUSEACTIVATE)
		# self.move_to(self.__clickhandle, int(x / scale), int(y / scale))
		# self.__activate_mouse(self.__clickhandle)
		# self.__set_cursor(self.__clickhandle, self.__WM_LBUTTONDOWN)
		self.left_down(int(x / scale), int(y / scale))
		self.move_to(int(x / scale), int(y / scale))
		self.left_up(int(x / scale), int(y / scale))

	# time.sleep(times)

	def mouse_click_image(self, name: any, confidence=0.9, times=0.5):
		"""
		@Description : 鼠标左键点击识别到的图片位置
		---------
		@Args : name:输入图片名; times:单击后延时
		-------
		@Returns : None
		-------
		"""
		try:
			result = self.recognize(name)
			print(result, 'result')
			if result is None or result['confidence'] < 0.7:
				return False
			else:
				self.mouse_click(result['result'][0] + x_coor * scale + 8, result['result'][1] + y_coor * scale + 39)
				return True
		except:
			return False

	def mouse_click_radius(self, x, y, times=0.2):
		"""
		@description : 在范围内随机位置单击（防检测）
		---------
		@param : 位置坐标x,y 单击后延时times(s)
		-------
		@Returns :
		-------
		"""

		random_x = np.random.randint(-radius, radius)
		random_y = np.random.randint(-radius, radius)
		self.mouse_click(x + random_x, y + random_y)
		# self.__left_down(self.__clickhandle, int((x + random_x) / scale), int((y + random_y) / scale))
		# time.sleep(0.1)
		# self.__left_up(self.__clickhandle, int((x + random_x) / scale), int((y + random_y) / scale))
		time.sleep(times)

	def push_key(self, key: str, times=0.9):
		"""
		@Description : 按键
		---------
		@Args : key:按键 times:按下改键后距松开的延时
		-------
		@Returns : None
		-------
		"""
		self.key_down(self.__clickhandle, key)
		time.sleep(times)
		self.key_up(self.__clickhandle, key)

	# time.sleep(0.5)

	def type_str(self, msg: str):
		"""
		@Description : 打字
		---------
		@Args : msg:目标字符
		-------
		@Returns : None
		-------
		"""
		for i in msg:
			self.__SendMessageW(self.__clickhandle, win32con.WM_CHAR, ord(i), 0)


if __name__ == "__main__":
	app = wx.App()
	frame = MyFrame()
	frame.Show()
	app.MainLoop()
