import wmi
from datetime import time
import uuid
import pyautogui
import time
import webbrowser
import os
import sys

# import pywebview
# webview = pywebview.WebView()
import keyboard
import threading
import wx
import pygame

# pyautogui.PAUSE = 0.005
# shengxiaoLaction = 0
# locationD = pyautogui.locateCenterOnScreen("images/opentalk.png", confidence=0.8)
# if locationD:
#   pyautogui.click(locationD.x, locationD.y,clicks=2,interval=0.1)
# location1 = pyautogui.locateCenterOnScreen("images/bangpaitalk.png", confidence=0.8)
# if location1:
#   pyautogui.click(location1.x, location1.y)
# location2 = pyautogui.locateCenterOnScreen("images/huodongtalk.png", confidence=0.8)
# if location2:
#   pyautogui.click(location2.x, location2.y)
# while True:
#   if pyautogui.locateOnScreen("images/tushengxiao.png", confidence=0.8):
#     break
#   location3 = pyautogui.locateCenterOnScreen("images/jindutiao.png", confidence=0.9)
#   if location3:
#     pyautogui.moveTo(location3.x, location3.y)
#     pyautogui.scroll(400)  # 移动到(100, 100)位置，然后滚轮向上滚动10格
# shengxiaoLaction = pyautogui.locateOnScreen("images/hushengxiao.png", confidence=0.8)
# location4 = pyautogui.locateCenterOnScreen("images/fei.png", confidence=0.8,region=(shengxiaoLaction.left-100,shengxiaoLaction.top,shengxiaoLaction.left+180,shengxiaoLaction.top+45))
# if location4:
#   pyautogui.click(location4.x, location4.y)
from pywinauto import Application

# import lackey
# lackey.wait("images/guge.png",10)
# lackey.click("images/guge.png")

# app = Application().connect(title='微信')
# win = app.window(title_re="微信")
#
#
# Datetime:2022/11/27 0:36
# Feature:# 打开指定的应用程序
# from pywinauto.application import Application
# # 打开windows上安装的猎豹浏览器
# app_test = Application(backend="uia").start(r"E:\360Game5\bin\360Game.exe --ico1")
# notepad = app_test['360游戏大厅']
# edit = notepad['360游戏大厅']
# text_content = edit.window_text()
# print(text_content)

# m = win.child_window(title="帮助(H)", control_type="MenuItem")
#
# # 获取文本属性
# print(win.texts())
# print(m.texts())
#
# # 窗口、控件名称
# print(m.window_text())
# # 子控件个数
# print(m.control_count())
#
#
# # 获取class 属性
# print(win.get_properties())
# print(m.get_properties())
# res = pyautogui.locateOnScreen("images/3.png",confidence=0.5,region=(0,0,1920,1080))
# print(res)
import pyautogui

# 在屏幕上查找所有与指定的图像匹配的位置

# def click_image_with_min_x(image_path):
# 	image_locations = list(pyautogui.locateAllOnScreen(image_path, confidence=0.9, region=(0, 0, 1920, 1080)))
#
# 	if image_locations:
# 		# min_x_location = min(image_locations, key=lambda loc: loc.left)
# 		# target_x, target_y = min_x_location.left, min_x_location.top
# 		# pyautogui.click(target_x, target_y)
# 		print(image_locations)
# 	else:
# 		print("未找到目标图像")


#
#
# # 调用方法并传入要查找的图像路径
# image_path = "images/hbj2.png"
# click_image_with_min_x("images/addBloud1.png")

# 开发思路： 参数1：找图方式：byKey，bymouse,
# 参数2：要点击的图片或者键盘移动方向，
# 参数3：要点击的图片或者键盘移动方向，
# 参数4：找到目标之后要点的目标图1，
# 参数5：找到目标之后要点的目标图2，
# 参数6：结束图1，
# 参数7：结束图2，
# def click_all_images(image_path):
# 	# 找到屏幕上所有匹配图像的位置
# 	matches = list(pyautogui.locateAllOnScreen(image_path, confidence=0.9, region=(0, 0, 1920, 1080)))
# 	print(matches)
# 	if not matches:
# 		print("没有找到匹配的图像。")
# 		return
#
# 	for match in matches:
# 		# 获取图像位置的中心点坐标
# 		x, y = pyautogui.center(match)
# 		# 点击图像位置
# 		pyautogui.click(x, y)
# 	time.sleep(0.5)  # 等待 0.5 秒，可以根据需要调整点击间隔
#
#
# # 调用函数，传入图像文件路径
# click_all_images("images/addBloud.png")  # 替换为你自己的图像文件路径
# xy = pyautogui.locateCenterOnScreen("images/fei.png", confidence=0.9)
# print(xy)
# pyautogui.click(xy.x, xy.y, clicks=100)
# 设定起始位置和拖动距离
# xy = pyautogui.locateCenterOnScreen("images/dragBox.png", confidence=0.9)
# drag_distance = 200
#
# # 移动鼠标到起始位置
# pyautogui.moveTo(xy.x, xy.y)
#
# # 模拟鼠标按下
# pyautogui.mouseDown()
#
# # 拖动鼠标
# pyautogui.dragRel(0, 150, duration=1)
#
# # 等待一段时间
# time.sleep(1)
#
# # 释放鼠标
# pyautogui.mouseUp()
# import wx
# import wx.lib.scrolledpanel as scrolled
#
# class HelpDialog(wx.Dialog):
#     def __init__(self, parent, title, content, images):
#         super(HelpDialog, self).__init__(parent, title=title, size=(600, 400))
#
#         panel = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
#         panel.SetupScrolling()
#
#         sizer = wx.BoxSizer(wx.VERTICAL)
#
#         # 添加文字内容
#         for text in content:
#             text_ctrl = wx.StaticText(panel, label=text)
#             sizer.Add(text_ctrl, 0, wx.ALL | wx.EXPAND, 5)
#
#         # 添加图片
#         for image_path in images:
#             image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
#             # 获取弹窗的宽度
#             dialog_width = self.GetSize().width
#             # 计算新的高度以保持宽高比
#             original_width = image.GetWidth()
#             original_height = image.GetHeight()
#             new_height = int((dialog_width / original_width) * original_height)
#             # 调整图片宽度为弹窗宽度的100%，高度自适应
#             image = image.Scale(dialog_width, new_height, wx.IMAGE_QUALITY_HIGH)
#             bitmap = wx.StaticBitmap(panel, -1, image.ConvertToBitmap())
#             sizer.Add(bitmap, 0, wx.ALL | wx.CENTER, 5)
#
#         panel.SetSizer(sizer)
#
# class MainFrame(wx.Frame):
#     def __init__(self, *args, **kwargs):
#         super(MainFrame, self).__init__(*args, **kwargs)
#
#         self.panel = wx.Panel(self)
#         self.sizer = wx.BoxSizer(wx.VERTICAL)
#
#         # 创建一个带有蓝色文字和下划线的链接控件
#         self.help_link = wx.StaticText(self.panel, label="使用说明", style=wx.ST_NO_AUTORESIZE)
#         self.help_link.SetForegroundColour(wx.BLUE)
#         self.help_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
#         self.help_link.Bind(wx.EVT_LEFT_DOWN, self.on_help_link_click)
#         self.sizer.Add(self.help_link, 0, wx.ALL | wx.CENTER, 5)
#
#         self.panel.SetSizer(self.sizer)
#
#     def on_help_link_click(self, event):
#         # 定义弹窗的内容和图片路径
#         content = [
#             "这是使用说明的第一段文字。",
#             "这是使用说明的第二段文字。",
#             "这是使用说明的第三段文字。"
#         ]
#         images = [
#             "images/shiyongshuoming.png",
#             "images/game.png"
#         ]
#
#         # 打开弹窗
#         dialog = HelpDialog(self, "使用说明", content, images)
#         dialog.ShowModal()
#         dialog.Destroy()
#
# if __name__ == "__main__":
#     app = wx.App(False)
#     frame = MainFrame(None, title="主窗口")
#     frame.Show()
#     app.MainLoop()
# keyboard.press('up')
# time.sleep(2)
# keyboard.release('up')
# pyautogui.keyDown('right')
# time.sleep(2)
# pyautogui.keyUp('right')
# class MyFrame(wx.Frame):
# 	def __init__(self, *args, **kw):
# 		super(MyFrame, self).__init__(*args, **kw)
# 		self.InitUI()

# 	def InitUI(self):
# 		panel = wx.Panel(self)
# 		vbox = wx.BoxSizer(wx.VERTICAL)

# 		self.start_button = wx.Button(panel, label='Start')
# 		self.pause_button = wx.Button(panel, label='Pause')
# 		self.resume_button = wx.Button(panel, label='Resume')
# 		self.stop_button = wx.Button(panel, label='Stop')

# 		vbox.Add(self.start_button, flag=wx.ALL | wx.EXPAND, border=5)
# 		vbox.Add(self.pause_button, flag=wx.ALL | wx.EXPAND, border=5)
# 		vbox.Add(self.resume_button, flag=wx.ALL | wx.EXPAND, border=5)
# 		vbox.Add(self.stop_button, flag=wx.ALL | wx.EXPAND, border=5)

# 		panel.SetSizer(vbox)

# 		self.Bind(wx.EVT_BUTTON, self.on_start, self.start_button)
# 		self.Bind(wx.EVT_BUTTON, self.on_pause, self.pause_button)
# 		self.Bind(wx.EVT_BUTTON, self.on_resume, self.resume_button)
# 		self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)

# 		self.thread = None

# 		self.Bind(wx.EVT_CLOSE, self.on_close)

# 	def on_start(self, event):
# 		if self.thread is None or not self.thread.is_alive():
# 			self.thread = FindPicThread()
# 			self.thread.start()

# 	def on_pause(self, event):
# 		if self.thread and self.thread.is_alive():
# 			self.thread.pause()

# 	def on_resume(self, event):
# 		if self.thread and self.thread.is_alive():
# 			self.thread.resume()

# 	def on_stop(self, event):
# 		if self.thread and self.thread.is_alive():
# 			self.thread.stop()
# 			self.thread.join()
# 			self.thread = None

# 	def on_close(self, event):
# 		if self.thread and self.thread.is_alive():
# 			self.thread.stop()
# 			self.thread.join()
# 		self.Destroy()


# def main():
# 	app = wx.App()
# 	frame = MyFrame(None, title='FindPic Control', size=(300, 200))
# 	frame.Show()
# 	app.MainLoop()


# if __name__ == '__main__':
# 	main()
# import wx
#
# class NumberValidator(wx.Validator):
#     def __init__(self):
#         wx.Validator.__init__(self)
#
#     def Clone(self):
#         return NumberValidator()
#
#     def Validate(self, win):
#         text_ctrl = self.GetWindow()
#         value = text_ctrl.GetValue()
#         if not value.isdigit():
#             wx.MessageBox("请输入数字", "错误", wx.OK | wx.ICON_ERROR)
#             text_ctrl.SetBackgroundColour("pink")
#             text_ctrl.SetFocus()
#             text_ctrl.Refresh()
#             return False
#         else:
#             text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
#             text_ctrl.Refresh()
#             return True
#
#     def TransferToWindow(self):
#         return True
#
#     def TransferFromWindow(self):
#         return True
#
# class MyFrame(wx.Frame):
#     def __init__(self, *args, **kw):
#         super(MyFrame, self).__init__(*args, **kw)
#         panel = wx.Panel(self)
#         vbox = wx.BoxSizer(wx.VERTICAL)
#
#         # 创建一个只能输入数字的文本输入框
#         self.number_input = wx.TextCtrl(panel, validator=NumberValidator())
#         vbox.Add(self.number_input, flag=wx.ALL, border=10)
#
#         # 添加一个按钮来测试输入是否有效
#         self.test_button = wx.Button(panel, label="测试")
#         self.test_button.Bind(wx.EVT_BUTTON, self.on_test)
#         vbox.Add(self.test_button, flag=wx.ALL, border=10)
#
#         panel.SetSizer(vbox)
#
#     def on_test(self, event):
#         if self.number_input.GetValidator().Validate(self.number_input):
#             wx.MessageBox(f"输入的数字是: {self.number_input.GetValue()}", "成功", wx.OK | wx.ICON_INFORMATION)
#         else:
#             wx.MessageBox("输入无效", "错误", wx.OK | wx.ICON_ERROR)
#
# class MyApp(wx.App):
#     def OnInit(self):
#         frame = MyFrame(None, title="数字输入框示例", size=(300, 200))
#         frame.Show()
#         return True
#
# if __name__ == "__main__":
#     app = MyApp()
#     app.MainLoop()
# import pywinauto
# import pyautogui
# import time
#
# from pywinauto import Desktop
#
# # 获取所有窗口的标题
# all_windows = Desktop(backend="uia").windows()
#
# # 打印所有窗口的标题
# for window in all_windows:
# 	print(window.window_text())
# # 获取目标窗口的句柄
# app = pywinauto.Application(backend="uia").connect(title="QQ")
# dlg = app.window(title="QQ")
#
# # # # 获取窗口的位置和大小
# rect = dlg.rectangle()
# print(rect)
# x = rect.left + 50  # 相对于窗口左上角的 x 坐标
# y = rect.top + 50   # 相对于窗口左上角的 y 坐标

# # # 模拟鼠标点击
# # pyautogui.moveTo(475, 632)
# # pyautogui.click()

# # 或者直接使用相对位置点击
# # pyautogui.click(x, y)

# # print(f"Clicked at ({x}, {y})")
# # !/usr/bin/env python
# # -*- encoding: utf-8 -*-
# '''
# @File    :   AutoClick.py
# @Time    :   2021/10/09 15:10:01
# @Author  :   Yaadon 
# '''

# !/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   AutoClick.py
@Time    :   2021/10/09 15:10:01
@Author  :   Yaadon 
'''

# here put the import lib
import win32con
import win32gui
import win32ui
import time
# import threading
import numpy as np
import os
from PIL import Image
from PIL import ImageOps
import aircv as ac
import pytesseract
from ctypes import windll, byref
from ctypes.wintypes import HWND, POINT
import string
import sys

sys.coinit_flags = 0
import pythoncom

# import sys
# import cv2
# from memory_pic import *
# import win32api
# import autopy
# from PIL import ImageGrab

scale = 1  # 电脑的缩放比例
radius = 5  # 随机半径
x_coor = 10  # 窗口位置
y_coor = 10  # 窗口位置


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

	def __key_down(self, handle: HWND, key: str):
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
		self.__PostMessageW(handle, self.__WM_KEYDOWN, wparam, lparam)

	def __key_up(self, handle: HWND, key: str):
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
		self.__PostMessageW(handle, self.__WM_KEYUP, wparam, lparam)

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
		self.__SendMessageW(handle, self.__WM_MOUSEACTIVATE, self.__handle, lparam)

	def __set_cursor(self, handle: HWND, msg):
		"""
		@Description : Sent to a window if the mouse causes the cursor to move within a window and mouse input is not captured
		---------
		@Args : handle (HWND): 窗口句柄, msg : setcursor消息
		-------
		@Returns :
		-------
		"""
		# https://docs.microsoft.com/en-us/windows/win32/menurc/wm-setcursor
		lparam = (msg << 16) | self.__HTCLIENT
		self.__SendMessageW(handle, self.__WM_SETCURSOR, handle, lparam)

	def __move_to(self, handle: HWND, x: int, y: int):
		"""移动鼠标到坐标（x, y)

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
		wparam = 0
		lparam = y << 16 | x
		self.__PostMessageW(handle, self.__WM_MOUSEMOVE, wparam, lparam)

	def __left_down(self, handle: HWND, x: int, y: int):
		"""在坐标(x, y)按下鼠标左键

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
		wparam = 0x001
		lparam = y << 16 | x
		self.__PostMessageW(handle, self.__WM_LBUTTONDOWN, wparam, lparam)

	def __left_up(self, handle: HWND, x: int, y: int):
		"""在坐标(x, y)放开鼠标左键

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
		wparam = 0
		lparam = y << 16 | x
		self.__PostMessageW(handle, self.__WM_LBUTTONUP, wparam, lparam)

	def __scroll(self, handle: HWND, delta: int, x: int, y: int):
		"""在坐标(x, y)滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			delta (int): 为正向上滚动，为负向下滚动
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.__move_to(handle, x, y)
		# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel
		wparam = delta << 16
		p = POINT(x, y)
		self.__ClientToScreen(handle, byref(p))
		lparam = p.y << 16 | p.x
		self.__PostMessageW(handle, self.__WM_MOUSEWHEEL, wparam, lparam)

	def __scroll_up(self, handle: HWND, x: int, y: int):
		"""在坐标(x, y)向上滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.__scroll(handle, self.__WHEEL_DELTA, x, y)

	def __scroll_down(self, handle: HWND, x: int, y: int):
		"""在坐标(x, y)向下滚动鼠标滚轮

		Args:
			handle (HWND): 窗口句柄
			x (int): 横坐标
			y (int): 纵坐标
		"""
		self.__scroll(handle, -self.__WHEEL_DELTA, x, y)

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
		self.__handle = windll.user32.FindWindowW(None, title)
		self.__classname = win32gui.GetClassName(self.__handle)
		# print(self.__classname)
		if self.__classname == 'Qt5QWindowIcon':
			self.__mainhandle = win32gui.FindWindowEx(self.__handle, 0, "Qt5QWindowIcon", "MainWindowWindow")
			# print(self.__mainhandle)
			self.__centerhandle = win32gui.FindWindowEx(self.__mainhandle, 0, "Qt5QWindowIcon", "CenterWidgetWindow")
			# print(self.__centerhandle)
			self.__renderhandle = win32gui.FindWindowEx(self.__centerhandle, 0, "Qt5QWindowIcon", "RenderWindowWindow")
			# print(self.__renderhandle)
			self.__clickhandle = self.__renderhandle
		else:
			self.__clickhandle = self.__handle
		# self.__subhandle = win32gui.FindWindowEx(self.__renderhandle, 0, "subWin", "sub")
		# print(self.__subhandle)
		# self.__subsubhandle = win32gui.FindWindowEx(self.__subhandle, 0, "subWin", "sub")
		# print(self.__subsubhandle)
		# win32gui.ShowWindow(hwnd1, win32con.SW_RESTORE)
		# print(win32gui.GetWindowRect(hwnd1))
		win32gui.SetWindowPos(self.__handle, win32con.HWND_TOP, x_coor, y_coor, 0, 0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOSIZE)
		print(self.__clickhandle)
		return self.__handle

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
		bl = 8
		# Remove border on top
		bt = 39

		width = int((right - left + 1) * scale) - 2 * bl
		height = int((bot - top + 1) * scale) - bt - bl
		# 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
		hWndDC = win32gui.GetWindowDC(self.__handle)
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

	def recognize(self, objs):
		"""
		@description : 图像识别之模板匹配
		---------
		@param : 需要匹配的模板名
		-------
		@Returns : 将传进来的图片和全屏截图匹配如果找到就返回图像在屏幕的坐标 否则返回None
		-------
		"""

		imobj = ac.imread(objs)
		imsrc = ac.imread('%s\\src.jpg' % os.getcwd())
		pos = ac.find_template(imsrc, imobj, 0.5)
		return pos

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
		# self.__move_to(self.__clickhandle, int(x / scale), int(y / scale))
		# self.__activate_mouse(self.__clickhandle)
		# self.__set_cursor(self.__clickhandle, self.__WM_LBUTTONDOWN)
		self.__left_down(self.__clickhandle, int(x / scale), int(y / scale))
		self.__move_to(self.__clickhandle, int(x / scale), int(y / scale))
		self.__left_up(self.__clickhandle, int(x / scale), int(y / scale))
		time.sleep(times)

	def mouse_click_image(self, name: str, times=0.5):
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
			if result is None or result['confidence'] < 0.9:
				print("No results!")
			else:
				print(result['result'][0] + x_coor * scale + 8, " ", result['result'][1] + y_coor * scale + 39)
				self.mouse_click(result['result'][0] + x_coor * scale + 8, result['result'][1] + y_coor * scale + 39)
		except:
			raise Exception("error")

	def mouse_click_radius(self, x, y, times=0.5):
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

	def push_key(self, key: str, times=1):
		"""
		@Description : 按键
		---------
		@Args : key:按键 times:按下改键后距松开的延时
		-------
		@Returns : None
		-------
		"""
		self.__key_down(self.__clickhandle, key)
		time.sleep(times)
		self.__key_up(self.__clickhandle, key)
		time.sleep(0.5)

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
			self.__PostMessageW(self.__clickhandle, win32con.WM_CHAR, ord(i), 0)


if __name__ == '__main__':
	click = AutoClick()
	click.get_winds("微信")
	# click.get_src()
	# click.mouse_click(172, 497)
	click.mouse_click_image('testImages/111.png')

# click.mouse_click(1086, 269) # 输入框
# click.mouse_click(237, 211) # 输入框
# click.mouse_click(1228, 201) # 输入框
# click.type_str("123木头人abc")
from ctypes import windll, byref
from ctypes.wintypes import HWND, POINT
import time

PostMessageW = windll.user32.PostMessageW
ClientToScreen = windll.user32.ClientToScreen

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x202
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120


def move_to(handle: HWND, x: int, y: int):
	"""移动鼠标到坐标（x, y)

	Args:
		handle (HWND): 窗口句柄
		x (int): 横坐标
		y (int): 纵坐标
	"""
	# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousemove
	wparam = 0
	lparam = y << 16 | x
	PostMessageW(handle, WM_MOUSEMOVE, wparam, lparam)


def left_down(handle: HWND, x: int, y: int):
	"""在坐标(x, y)按下鼠标左键

	Args:
		handle (HWND): 窗口句柄
		x (int): 横坐标
		y (int): 纵坐标
	"""
	# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttondown
	wparam = 0
	lparam = y << 16 | x
	PostMessageW(handle, WM_LBUTTONDOWN, wparam, lparam)


def left_up(handle: HWND, x: int, y: int):
	"""在坐标(x, y)放开鼠标左键

	Args:
		handle (HWND): 窗口句柄
		x (int): 横坐标
		y (int): 纵坐标
	"""
	# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-lbuttonup
	wparam = 0
	lparam = y << 16 | x
	PostMessageW(handle, WM_LBUTTONUP, wparam, lparam)


def scroll(handle: HWND, delta: int, x: int, y: int):
	"""在坐标(x, y)滚动鼠标滚轮

	Args:
		handle (HWND): 窗口句柄
		delta (int): 为正向上滚动，为负向下滚动
		x (int): 横坐标
		y (int): 纵坐标
	"""
	move_to(handle, x, y)
	# https://docs.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel
	wparam = delta << 16
	p = POINT(x, y)
	ClientToScreen(handle, byref(p))
	lparam = p.y << 16 | p.x
	PostMessageW(handle, WM_MOUSEWHEEL, wparam, lparam)


def scroll_up(handle: HWND, x: int, y: int):
	"""在坐标(x, y)向上滚动鼠标滚轮

	Args:
		handle (HWND): 窗口句柄
		x (int): 横坐标
		y (int): 纵坐标
	"""
	scroll(handle, WHEEL_DELTA, x, y)


def scroll_down(handle: HWND, x: int, y: int):
	"""在坐标(x, y)向下滚动鼠标滚轮

	Args:
		handle (HWND): 窗口句柄
		x (int): 横坐标
		y (int): 纵坐标
	"""
	scroll(handle, -WHEEL_DELTA, x, y)

# if __name__ == "__main__":
# 	# 需要和目标窗口同一权限，游戏窗口通常是管理员权限
# 	import sys
#
# 	if not windll.shell32.IsUserAnAdmin():
# 		# 不是管理员就提权
# 		windll.shell32.ShellExecuteW(
# 			None, "runas", sys.executable, __file__, None, 1)
#
# 	handle = windll.user32.FindWindowW(None, "微信")
# 	# 点击线路
# 	left_down(handle, 152, 292)
# 	time.sleep(0.1)
# 	left_up(handle, 152, 292)
# 	time.sleep(1)
# 滚动线路列表
# scroll_down(handle, 1000, 200)
