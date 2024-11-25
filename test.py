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
xy = pyautogui.locateCenterOnScreen("images/fei.png", confidence=0.9)
print(xy)
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
