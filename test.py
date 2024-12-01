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
import pywinauto
import pyautogui
import time
from pywinauto import Desktop
# 获取所有窗口的标题
all_windows = Desktop(backend="uia").windows()

# 打印所有窗口的标题
for window in all_windows:
    print(window.window_text())
# 获取目标窗口的句柄
# app = pywinauto.Application(backend="uia").connect(title="11")
# dlg = app.window(title="11")

# # 获取窗口的位置和大小
# rect = dlg.rectangle()
# print(rect)
# # x = rect.left + 50  # 相对于窗口左上角的 x 坐标
# # y = rect.top + 50   # 相对于窗口左上角的 y 坐标

# # 模拟鼠标点击
# pyautogui.moveTo(475, 632)
# pyautogui.click()

# 或者直接使用相对位置点击
# pyautogui.click(x, y)

# print(f"Clicked at ({x}, {y})")
