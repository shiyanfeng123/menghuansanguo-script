from datetime import time
import uuid
import pyautogui
import time
import wmi
import webbrowser
import os
import sys

# import pywebview
# webview = pywebview.WebView()
import keyboard
import threading
import wx
import pygame

import psutil

pyautogui.PAUSE = 0.005
pyautogui.FAILSAFE = True  # 鼠标光标在屏幕左上角，会导致程序异常，用于终止程序运行。
# 打包命令：pyinstaller -F -w --add-data "images;images" --icon=images\script.ico .\main.py
# pyinstaller main.spec

# 创建一个线程
# thread = threading.Thread(target=thread_function)

# 启动线程
# thread.start()
# testFun()
# thread.join()

# def open_html_page(html_path):
#     url = "file:///" + os.path.abspath(html_path)
#     webbrowser.open(url)
#
# if getattr(sys, 'frozen', False):  # 检查是否是打包后的程序
#     base_path = sys._MEIPASS
# else:
#     base_path = os.path.abspath(".")
#
# # 显示项目目录信息
# print("项目目录：", base_path)
#
# html_path = os.path.join(base_path, "index.html")
#
# open_html_page(html_path)
# c = wmi.WMI()
# for item in c.Win32_BaseBoard():
#     print("硬件序列号:", item.SerialNumber)

# def get_mac_address():
#     # 使用 psutil 获取所有网络接口信息
#     interfaces = psutil.net_if_addrs()
#
#     # 遍历接口信息，找到MAC地址
#     for interface_name, interface_addresses in interfaces.items():
#         for address in interface_addresses:
#             if str(address.family) == 'AddressFamily.AF_LINK':
#                 return address.address
#
#     return "MAC address not found"
#
# mac_address = get_mac_address()
# print("MAC Address:", mac_address)
# print(":".join([uuid.uuid1().hex[-12:][i : i + 2] for i in range(0, 11, 2)]))
paused = threading.Event()
terminate = threading.Event()
condition = threading.Condition()


class MyThread(threading.Thread):
    def __init__(self, scriptName):
        super().__init__()
        self.userInfoMac = ["50-9A-4C-C9-FE-BA"]
        # 创建子线程
        self.child_thread = threading.Thread(target=self.child_task)
        self.guanDuCount = 0
        self.scriptName = scriptName
        self.confidenceNum = 0.9
        while True:
            if pyautogui.locateOnScreen(
                self.get_resource_path("images/2.png"),
                confidence=0.5,
                region=(0, 0, 1920, 1080),
            ) and pyautogui.locateOnScreen(
                self.get_resource_path("images/3.png"),
                confidence=0.5,
                region=(0, 0, 1920, 1080),
            ):
                time.sleep(1)
                break
        self.righttop1 = pyautogui.locateOnScreen(
            self.get_resource_path("images/2.png"), confidence=0.5
        )
        self.leftbottom = pyautogui.locateOnScreen(
            self.get_resource_path("images/3.png"), confidence=0.5
        )
        if not self.righttop1 or not self.leftbottom:
            self.show_error_message("未检测到游戏页面")
            return
        self.locationX = self.leftbottom.left
        self.locationY = self.righttop1.top
        self.locationWidth = self.righttop1.left + self.righttop1.width - self.locationX
        self.locationHeight = (
            self.leftbottom.top + self.leftbottom.height - self.locationY
        )
        self.locationRightTopX = self.righttop1.left
        self.locationRightTopY = self.righttop1.top
        self.locationRightTopWidth = self.righttop1.width
        self.locationRightTopHeight = self.righttop1.height
        self.stoped = False
        self.zdzdPath = self.get_resource_path("images/zdzd.png")
        self.Dx = 0
        self.Dy = 0
        self.BisClick = False
        self.clickBTime = 0
        self.clickBX = 0
        self.clickBy = 0
        self.shengxiaoLocation = None

    def run(self):
        # c = wmi.WMI()
        # for item in c.Win32_BaseBoard():
        #     hardware_serial = item.SerialNumber
        mac_address = self.get_mac_address()

        if mac_address in self.userInfoMac:
            print("已注册用户")
        else:
            self.show_error_message("未注册用户，请联系管理员")
            return
        print("鼠标放屏幕左上角退出当前脚本")
        self.child_thread.start()
        if self.scriptName == "官渡":
            self.guanduWhile()
        elif self.scriptName == "嗜血战场(精英)":
            self.hongWhile()
        elif self.scriptName == "战魂楼(精英)":
            self.zhanhunWhile()
        elif self.scriptName == "整点":
            self.zhengDian()
        elif self.scriptName == "祭坛魔镜":
            self.mojingWhile()
        elif self.scriptName == "战魂+红+整点":
            self.guanduAndHongAndZd()

    def child_task(self):
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
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
            # self.click_image(
            #     self.get_resource_path("images/closeJJ.png"),
            #     self.confidenceNum,
            #     (
            #         self.locationX,
            #         self.locationY,
            #         self.locationWidth,
            #         self.locationHeight,
            #     ),
            # )
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
            # 点击x
            # self.click_image(
            #     self.get_resource_path("images/close.png"),
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
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            # 点击拒绝
            self.click_image(
                self.get_resource_path("images/jujue.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            # 点自动
            if self.scriptName == "官渡" or self.scriptName == "祭坛魔镜":
                self.click_image(
                    self.get_resource_path("images/zidong.png"),
                    self.confidenceNum,
                    (
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
                )
            # self.click_nth_image(self.get_resource_path("images/addBloud.png"), (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)), 1)
            # self.click_nth_image(self.get_resource_path("images/addBloud1.png"), (self.locationX, self.locationY, int(self.locationWidth * 0.5), int(self.locationHeight * 0.5)), 1)

    def get_mac_address(self):
        # 使用 psutil 获取所有网络接口信息
        interfaces = psutil.net_if_addrs()

        # 遍历接口信息，找到MAC地址
        for interface_name, interface_addresses in interfaces.items():
            for address in interface_addresses:
                if str(address.family) == "AddressFamily.AF_LINK":
                    return address.address

        return "MAC address not found"

    def beginFun(self):
        closeTalkXY = pyautogui.locateCenterOnScreen(
            self.get_resource_path("images/closetalk.png"),
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                int(self.locationY + (self.locationHeight * 0.5)),
                int(self.locationWidth * 0.5),
                self.locationHeight,
            ),
        )
        if closeTalkXY:
            pyautogui.click(closeTalkXY.x, closeTalkXY.y, clicks=4, interval=0.3)
        self.click_image(
            self.get_resource_path("images/hide.png"),
            self.confidenceNum,
            (self.locationX, self.locationY, self.locationWidth, self.locationHeight),
        )
        yseXY = pyautogui.locateCenterOnScreen(
            self.get_resource_path("images/yes.png"),
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        )
        if yseXY:
            pyautogui.click(yseXY.x, yseXY.y)
        time.sleep(0.5)
        yseXY = pyautogui.locateCenterOnScreen(
            self.get_resource_path("images/yes.png"),
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        )
        if yseXY:
            pyautogui.click(yseXY.x, yseXY.y)

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

    # 战斗结束去除黑色弹框
    def clearBox(self, current):
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            if pyautogui.locateOnScreen(
                current,
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            ):
                break

    # 退出当前副本
    def outScript(self, current):
        print("退出当前副本")
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            if pyautogui.locateOnScreen(
                current,
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            ):
                break
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            if pyautogui.locateOnScreen(
                self.get_resource_path("images/xiulian.png"),
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            ):
                break
        locationOut = pyautogui.locateCenterOnScreen(
            self.get_resource_path("images/xiulian.png"),
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        )
        pyautogui.click(int(locationOut.x - 20), int(locationOut.y - 40))
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
            pyautogui.click(locationQueding.x, locationQueding.y)
        else:
            return

    # 飞整点等到打完
    def feiZhengDian(self, fei_image, base_image, scroll_deg):
        while not pyautogui.locateOnScreen(
            fei_image,
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                int(self.locationY + (self.locationHeight * 0.5)),
                int(self.locationWidth * 0.5),
                self.locationHeight,
            ),
        ):
            # 去除获得铜币黑框
            self.click_image(
                self.get_resource_path("images/huodetongbi.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            jindutiaoLocation = pyautogui.locateCenterOnScreen(
                self.get_resource_path("images/upTalk.png"),
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    int(self.locationY + (self.locationHeight * 0.5)),
                    int(self.locationWidth * 0.5),
                    self.locationHeight,
                ),
            )
            if jindutiaoLocation:
                pyautogui.moveTo(jindutiaoLocation.x, jindutiaoLocation.y)
                pyautogui.scroll(scroll_deg)
        while True:
            with condition:
                if self.stoped:
                    condition.wait()
            self.shengxiaoLocation = pyautogui.locateOnScreen(
                fei_image,
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    int(self.locationY + (self.locationHeight * 0.5)),
                    int(self.locationWidth * 0.5),
                    self.locationHeight,
                ),
            )
            if self.shengxiaoLocation is not None:
                break
        feiTime = time.time()
        while not pyautogui.locateOnScreen(
            base_image,
            confidence=self.confidenceNum,
            region=(
                self.locationRightTopX,
                self.locationRightTopY,
                self.locationRightTopWidth,
                self.locationRightTopHeight,
            ),
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
                pyautogui.click(feiLocation.x, feiLocation.y)
                pyautogui.moveTo(feiLocation.x - 200, feiLocation.y - 200)
                time.sleep(1.3)
            else:
                return
        # 去除获得铜币黑框
        self.click_image(
            self.get_resource_path("images/huodetongbi.png"),
            self.confidenceNum,
            (
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        )
        time.sleep(0.2)
        # 有人在打
        hasZhengDian = self.click_image(
            self.get_resource_path("images/dajiuda.png"),
            self.confidenceNum,
            (
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        )
        if not hasZhengDian:
            return
        zhengdianHas = False
        queryTime = time.time()
        while hasZhengDian:

            if time.time() - queryTime > 5:
                zhengdianHas = False
                break
            if pyautogui.locateOnScreen(
                self.get_resource_path("images/zdzd.png"),
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            ):
                zhengdianHas = True
                break
            yourendaLocation = pyautogui.locateCenterOnScreen(
                self.get_resource_path("images/yourenda1.png"),
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            if yourendaLocation:
                pyautogui.click(yourendaLocation.x, yourendaLocation.y)
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
            pyautogui.click(openTalkXY.x, openTalkXY.y, clicks=4, interval=0.2)
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
            pyautogui.click(bangpaiTalkXY.x, bangpaiTalkXY.y)
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
            pyautogui.click(huodongTalkXY.x, huodongTalkXY.y)
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
            300,
        )
        # 飞老虎
        self.feiZhengDian(
            self.get_resource_path("images/hushengxiao1.png"),
            self.get_resource_path("images/jiulizujitan.png"),
            300,
        )
        # 飞兔子
        self.feiZhengDian(
            self.get_resource_path("images/tushengxiao1.png"),
            self.get_resource_path("images/xuzhou.png"),
            300,
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
            300,
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
            300,
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
            pyautogui.moveTo(dragBox.x, dragBox.y)
            pyautogui.mouseDown()
            pyautogui.dragRel(0, 150, duration=0.5)
            time.sleep(0.5)
            pyautogui.mouseUp()
            # 飞羊
            self.feiZhengDian(
                self.get_resource_path("images/yangshengxiao1.png"),
                self.get_resource_path("images/moguxi.png"),
                200,
            )
            # 飞猴子
            self.feiZhengDian(
                self.get_resource_path("images/houshengxiao1.png"),
                self.get_resource_path("images/youanmilin.png"),
                300,
            )
            # 飞羊
            self.feiZhengDian(
                self.get_resource_path("images/yangshengxiao1.png"),
                self.get_resource_path("images/moguxi.png"),
                300,
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
            pyautogui.click(closeTalkXY.x, closeTalkXY.y, clicks=4, interval=0.2)
        if self.scriptName == "官渡":
            self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
            self.guanduWhile()

        elif self.scriptName == "祭坛魔镜":
            self.feiFb(
                self.get_resource_path("images/mojing/fubenmojingshizhe.png"), False
            )
            self.mojingWhile()
        elif self.scriptName == "战魂+红+整点":
            self.feiFb(self.get_resource_path("images/ditucaocao.png"), True)
            time.sleep(0.5)
            self.feiFb(self.get_resource_path("images/dituzhanhun.png"), True)
            self.guanduAndHongAndZd()

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
            pyautogui.click(int(tuLocation.x + 24), int(tuLocation.y - 34))
        time.sleep(0.8)
        if isJy:
            self.click_image(
                self.get_resource_path("images/activejy.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            self.click_image(
                self.get_resource_path("images/unActivejy.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            while True:
                with condition:
                    if self.stoped:
                        condition.wait()
                imagePathLocation = pyautogui.locateOnScreen(
                    image_path,
                    confidence=self.confidenceNum,
                    region=(
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
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
                pyautogui.click(feiLocation.x, feiLocation.y)
        else:
            self.click_image(
                self.get_resource_path("images/activeFb.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            self.click_image(
                self.get_resource_path("images/unActiveFb.png"),
                self.confidenceNum,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            while not pyautogui.locateOnScreen(
                image_path,
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
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
                    pyautogui.click(downTalk.x, downTalk.y, clicks=10)
                    time.sleep(1)
            while True:
                with condition:
                    if self.stoped:
                        condition.wait()
                imagePathLocation = pyautogui.locateOnScreen(
                    image_path,
                    confidence=self.confidenceNum,
                    region=(
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
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
                pyautogui.click(feiLocation.x, feiLocation.y)

    # 找图并且点击
    def click_image(self, image_path, image_confidence, image_region):
        image_locations = pyautogui.locateCenterOnScreen(
            image_path, confidence=image_confidence, region=image_region
        )
        if image_locations:
            with condition:
                if self.stoped:
                    condition.wait()
            pyautogui.click(image_locations.x, image_locations.y)
            pyautogui.moveTo(image_locations.x + 200, image_locations.y + 200)
            return True
        else:
            return False

    # 找出一样的图，点击第N个图
    def click_nth_image(self, image_path, image_region, n):
        images = list(
            pyautogui.locateAllOnScreen(
                image_path, confidence=self.confidenceNum, region=image_region
            )
        )
        if len(images) >= n:
            with condition:
                if self.stoped:
                    condition.wait()
            target_location = images[n - 1]
            target_x = target_location.left + target_location.width // 2
            target_y = target_location.top + target_location.height // 2
            pyautogui.click(target_x, target_y, clicks=1, interval=0.01)
            return True
        else:
            return False

    # 找一样的图，点击最左边的图
    def click_image_with_min_x(self, image_path, image_region, image_path2):
        image_locations = list(
            pyautogui.locateAllOnScreen(
                image_path, confidence=self.confidenceNum, region=image_region
            )
        )
        if image_locations:
            with condition:
                if self.stoped:
                    condition.wait()
            min_x_location = min(image_locations, key=lambda loc: loc.left)
            target_x = min_x_location.left + min_x_location.width // 2
            target_y = min_x_location.top + min_x_location.height // 2
            if image_path2 == self.zdzdPath:
                pyautogui.click(target_x, int(target_y - 90), clicks=3, interval=0.008)
            else:
                pyautogui.click(target_x, target_y, clicks=1, interval=0.01)
            self.clickBTime = time.time()
            self.clickBX = target_x
            self.clickBy = target_y
            pyautogui.moveTo(target_x + 200, target_y + 200)
            return True
        else:
            return False

    # 等待图片出现
    def waitFor(self, image_path, image_region, timeout=None):
        start_time = time.time()
        xy = None
        while True:
            xy = pyautogui.locateCenterOnScreen(
                image_path, confidence=self.confidenceNum, region=image_region
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
            xy = pyautogui.locateCenterOnScreen(
                image1_path, confidence=self.confidenceNum, region=image_region
            )
            if xy:
                res = "first"
                break
            xy2 = pyautogui.locateCenterOnScreen(
                image2_path, confidence=self.confidenceNum, region=image_region
            )
            if xy2:
                res = "second"
                break
            if timeout is not None:
                if time.time() - start_time > timeout:
                    return False
            time.sleep(0.1)
            if self.confidenceNum > 0.8:
                self.confidenceNum -= 0.1
        self.confidenceNum = 0.9
        return res

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
    def press_keys_until_image_found(self, image_path1, image_path2, key1, key2):
        if key2:
            pyautogui.keyDown(key2)
            time.sleep(1)
            pyautogui.keyUp(key2)
        while not pyautogui.locateOnScreen(
            image_path2,
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        ):
            with condition:
                if self.stoped:
                    condition.wait()
            pyautogui.keyDown(key1)
            image_path1Location = self.waitFor(
                image_path1,
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
            )
            if image_path1Location:
                pyautogui.keyUp(key1)
                click1 = self.click_image_with_min_x(
                    image_path1,
                    (
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
                    image_path2,
                )
                if click1:
                    time.sleep(1)

    # 找图并且点击
    def findAndClickPic(self, A, B1, B2, C1, C2, D, E, E2=None, E2DownTime=1):
        EIsDown = False
        E2IsDown = False
        self.BisClick = False
        self.clickBTime = 0
        self.clickBX = 0
        self.clickBy = 0

        with condition:
            if self.stoped:
                condition.wait()
        aIsOk = self.waitFor(
            A, (self.locationX, self.locationY, self.locationWidth, self.locationHeight)
        )
        if not aIsOk:
            self.show_error_message("未找到开始地点")
            return
        if time.localtime().tm_min == 58:
            if self.scriptName == "官渡" or self.scriptName == "祭坛魔镜":
                # 打整点
                self.outScript(A)
                self.zhengDian()
                return
        # 开始找C的时间
        startTime = time.time()
        while not pyautogui.locateOnScreen(
            C1,
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
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
            #   D找图片D点击
            if D and not self.BisClick:
                with condition:
                    if self.stoped:
                        condition.wait()
                Dxy = pyautogui.locateCenterOnScreen(
                    D,
                    confidence=self.confidenceNum,
                    region=(
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
                )
                if Dxy:
                    pyautogui.click(Dxy.x, Dxy.y, clicks=2, interval=0.01)
            #     点击按钮E
            while E != "" and not EIsDown:
                with condition:
                    if self.stoped:
                        condition.wait()
                if E2 is not None and not E2IsDown:
                    pyautogui.keyDown(E2)
                    E2IsDown = True
                    time.sleep(E2DownTime)
                    pyautogui.keyUp(E2)
                pyautogui.keyDown(E)
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
                    pyautogui.keyUp(E)
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
                    if isClick:
                        # time.sleep(1)
                        if E2 is not None and E2IsDown:
                            pyautogui.keyUp(E2)
                    break
                if pyautogui.locateOnScreen(
                    C1,
                    confidence=self.confidenceNum,
                    region=(
                        self.locationX,
                        self.locationY,
                        self.locationWidth,
                        self.locationHeight,
                    ),
                ):
                    EIsDown = True
                    time.sleep(0.1)
                    pyautogui.keyUp(E)
                    if E2 is not None and E2IsDown:
                        pyautogui.keyUp(E2)
                    break
                if self.confidenceNum > 0.8:
                    self.confidenceNum -= 0.1
            self.confidenceNum = 0.9
            if E != "" and EIsDown:
                pyautogui.keyUp(E)
                if E2 is not None and E2IsDown:
                    pyautogui.keyUp(E2)
            with condition:
                if self.stoped:
                    condition.wait()
            if pyautogui.locateOnScreen(
                C1,
                confidence=self.confidenceNum,
                region=(
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
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
                pyautogui.click(self.clickBX, self.clickBy)
        if self.confidenceNum > 0.8:
            self.confidenceNum -= 0.1
        self.confidenceNum = 0.9
        if E != "":
            with condition:
                if self.stoped:
                    condition.wait()
            pyautogui.keyUp(E)

    # 官渡脚本
    def guanduScript(self):
        with condition:
            if self.stoped:
                condition.wait()
        self.guanDuCount += 1
        print(f"第{self.guanDuCount}次官渡.")
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
        self.findAndClickPic(
            self.get_resource_path("images/guanDu1.png"),
            self.get_resource_path("images/inguanDu.png"),
            self.get_resource_path("images/inguanDu.png"),
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/caoyindazhang.png"),
            "",
            "",
        )
        with condition:
            if self.stoped:
                condition.wait()
        self.findAndClickPic(
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/dycrk2.png"),
            self.get_resource_path("images/dycrk2.png"),
            self.get_resource_path("images/caoyuanzhanchang.png"),
            self.get_resource_path("images/caoyuanzhanchang.png"),
            "",
            "",
        )

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
        self.findAndClickPic(
            self.get_resource_path("images/caoyuanzhanchang.png"),
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/godazhang.png"),
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/caoyindazhang.png"),
            "",
            "left",
        )
        with condition:
            if self.stoped:
                condition.wait()
        # 找到曹操进入乌巢
        self.findAndClickPic(
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/caochengxiang.png"),
            self.get_resource_path("images/caochengxiang1.png"),
            self.get_resource_path("images/gowuchao.png"),
            self.get_resource_path("images/gowuchao.png"),
            "",
            "down",
        )
        with condition:
            if self.stoped:
                condition.wait()
        self.findAndClickPic(
            self.get_resource_path("images/caoyindazhang.png"),
            self.get_resource_path("images/gowuchao.png"),
            self.get_resource_path("images/gowuchao.png"),
            self.get_resource_path("images/wuchao.png"),
            self.get_resource_path("images/wuchao.png"),
            "",
            "",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/hundian.png"),
            self.get_resource_path("images/gowuchao2.png"),
            self.get_resource_path("images/gowuchao2.png"),
            self.get_resource_path("images/wuchao.png"),
            self.get_resource_path("images/wuchao.png"),
            "",
            "",
        )
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
            self.get_resource_path("images/hong/inhongD.png"),
            "",
        )
        self.findAndClickPic(
            self.get_resource_path("images/hong/hulaoguanwai.png"),
            self.get_resource_path("images/hong/inhong.png"),
            self.get_resource_path("images/hong/inhong.png"),
            self.get_resource_path("images/hong/junyin.png"),
            self.get_resource_path("images/hong/junyin.png"),
            "",
            "",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/hong/junyin.png"),
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/gojunliangyin1.png"),
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/junliangyin.png"),
            "",
            "left",
            "down",
        )
        # 第一个护卫兵
        self.findAndClickPic(
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/huweibin.png"),
            self.get_resource_path("images/hong/huweibin1.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "right",
            "down",
        )
        # 第二个护卫兵
        self.findAndClickPic(
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/huweibin.png"),
            self.get_resource_path("images/hong/huweibin1.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "right",
        )
        # 护粮将领
        self.findAndClickPic(
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/huliangjianglin.png"),
            self.get_resource_path("images/hong/huliangjianglin1.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "right",
        )
        # 进入训兵营
        self.findAndClickPic(
            self.get_resource_path("images/hong/junliangyin.png"),
            self.get_resource_path("images/hong/xunbinyin.png"),
            self.get_resource_path("images/hong/goxunbinyin1.png"),
            self.get_resource_path("images/hong/xunbinyin.png"),
            self.get_resource_path("images/hong/xunbinyin.png"),
            "",
            "right",
        )
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
        # 第2个骑兵
        self.findAndClickPic(
            self.get_resource_path("images/hong/xunbinyin.png"),
            self.get_resource_path("images/hong/qibin.png"),
            self.get_resource_path("images/hong/qibin1.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "right",
            "down",
        )
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
            self.get_resource_path("images/hong/gojunyin1.png"),
            self.get_resource_path("images/hong/gojunyin.png"),
            self.get_resource_path("images/hong/junyin.png"),
            self.get_resource_path("images/hong/junyin.png"),
            "",
            "up",
            "left",
            int(0.6),
        )
        # 进入帐篷
        self.findAndClickPic(
            self.get_resource_path("images/hong/junyin.png"),
            self.get_resource_path("images/hong/gozhangpeng.png"),
            self.get_resource_path("images/hong/gozhangpeng1.png"),
            self.get_resource_path("images/hong/zhangpeng.png"),
            self.get_resource_path("images/hong/zhangpeng.png"),
            "",
            "left",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/luoyangdadao.png"),
            self.get_resource_path("images/zhanhun/inzhanhun.png"),
            self.get_resource_path("images/zhanhun/inzhanhun.png"),
            self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
            self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
            "",
            "",
        )
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

        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
            self.get_resource_path("images/zhanhun/go2.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/zhangliang.png"),
            self.get_resource_path("images/zhanhun/zhangliang.png"),
            "",
            "right",
        )
        # 2
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
            self.get_resource_path("images/zhanhun/zhangliang.png"),
            self.get_resource_path("images/zhanhun/zhangliang2.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "",
        )
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
            self.get_resource_path("images/zhanhun/go3.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/zhangjiao.png"),
            self.get_resource_path("images/zhanhun/zhangjiao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou3.png"),
            self.get_resource_path("images/zhanhun/go4.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/wenchou.png"),
            self.get_resource_path("images/zhanhun/wenchou.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou4.png"),
            self.get_resource_path("images/zhanhun/go5.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/yanliang.png"),
            self.get_resource_path("images/zhanhun/yanliang.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou5.png"),
            self.get_resource_path("images/zhanhun/go6.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/huaxiong.png"),
            self.get_resource_path("images/zhanhun/huaxiong.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou6.png"),
            self.get_resource_path("images/zhanhun/go7.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/sunce.png"),
            self.get_resource_path("images/zhanhun/sunce.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou7.png"),
            self.get_resource_path("images/zhanhun/go8.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/dianwei.png"),
            self.get_resource_path("images/zhanhun/dianwei.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou8.png"),
            self.get_resource_path("images/zhanhun/go9.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/guojia.png"),
            self.get_resource_path("images/zhanhun/guojia.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou9.png"),
            self.get_resource_path("images/zhanhun/go10.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/liubei.png"),
            self.get_resource_path("images/zhanhun/liubei.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou10.png"),
            self.get_resource_path("images/zhanhun/go11.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/caocao.png"),
            self.get_resource_path("images/zhanhun/caocao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou11.png"),
            self.get_resource_path("images/zhanhun/go12.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/yuanshao.png"),
            self.get_resource_path("images/zhanhun/yuanshao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou12.png"),
            self.get_resource_path("images/zhanhun/go13.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/zhangfei.png"),
            self.get_resource_path("images/zhanhun/zhangfei.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou13.png"),
            self.get_resource_path("images/zhanhun/go14.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/daqiao.png"),
            self.get_resource_path("images/zhanhun/daqiao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou14.png"),
            self.get_resource_path("images/zhanhun/go15.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/guanyu.png"),
            self.get_resource_path("images/zhanhun/guanyu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou15.png"),
            self.get_resource_path("images/zhanhun/go16.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/lvbu.png"),
            self.get_resource_path("images/zhanhun/lvbu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou16.png"),
            self.get_resource_path("images/zhanhun/go17.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
            self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou17.png"),
            self.get_resource_path("images/zhanhun/go18.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
            self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou18.png"),
            self.get_resource_path("images/zhanhun/go19.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou19.png"),
            self.get_resource_path("images/zhanhun/go20.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou20.png"),
            self.get_resource_path("images/zhanhun/go21.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/liubei.png"),
            self.get_resource_path("images/zhanhun/liubei.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
            self.get_resource_path("images/zhanhun/go22.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/yuanshao.png"),
            self.get_resource_path("images/zhanhun/yuanshao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
            self.get_resource_path("images/zhanhun/go23.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/caocao.png"),
            self.get_resource_path("images/zhanhun/caocao.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
            self.get_resource_path("images/zhanhun/go24.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/lvbu.png"),
            self.get_resource_path("images/zhanhun/lvbu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
            self.get_resource_path("images/zhanhun/go25.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            self.get_resource_path("images/zhanhun/mohualvbu.png"),
            "",
            "right",
        )
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
        self.findAndClickPic(
            self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
            self.get_resource_path("images/zhanhun/go26.png"),
            self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
            self.get_resource_path("images/zhanhun/renshengwa.png"),
            self.get_resource_path("images/zhanhun/renshengwa.png"),
            "",
            "right",
        )
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
        # 退出副本
        self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou26.png"))

    # 魔镜脚本
    def mojingScript(self):
        print("开始祭坛魔镜")
        # 进入魔镜
        inLuoYangChengXi = self.waitFor(
            self.get_resource_path(
                "images/mojing/luyangchengxi.png",
            ),
            (
                self.locationRightTopX,
                self.locationRightTopY,
                self.locationRightTopWidth,
                self.locationRightTopHeight,
            ),
            5,
        )
        if not inLuoYangChengXi:
            self.feiFb(
                self.get_resource_path("images/mojing/fubenmojingshizhe.png"), False
            )
        if not pyautogui.locateOnScreen(
            self.get_resource_path("images/mojing/injitan.png"),
            confidence=self.confidenceNum,
            region=(
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
        ):
            self.waitForAAndClickB(
                self.get_resource_path("images/mojing/mojingshizhe.png"),
                self.get_resource_path("images/mojing/mojingD.png"),
                (
                    self.locationX,
                    self.locationY,
                    self.locationWidth,
                    self.locationHeight,
                ),
                None,
                self.get_resource_path("images/mojing/mojingshizhe.png"),
                self.get_resource_path("images/mojing/mojingD.png"),
            )
        self.waitForAAndClickB(
            self.get_resource_path("images/mojing/injitan.png"),
            self.get_resource_path("images/mojing/mojingshizhe.png"),
            (
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
            None,
            self.get_resource_path("images/mojing/injitan.png"),
            self.get_resource_path("images/mojing/mojingshizhe.png"),
        )
        self.waitForAAndClickB(
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/injitan.png"),
            (
                self.locationX,
                self.locationY,
                self.locationWidth,
                self.locationHeight,
            ),
            None,
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/injitan.png"),
        )
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/jingxiangdiceng.png"))
            self.zhengDian()
            return
        # 打一个第一层的怪
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/chirenyao.png"),
            self.get_resource_path("images/zdzd.png"),
            "right",
            "",
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
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/yijijingxiang.png"))
            self.zhengDian()
            return
        # 打狮王
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/shiwanghun.png"),
            self.get_resource_path("images/zdzd.png"),
            "right",
            "",
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
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/mihuanjing.png"))
            self.zhengDian()
            return
        # 打虚实
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/xu.png"),
            self.get_resource_path("images/zdzd.png"),
            "right",
            "",
        )
        self.waitFor(
            self.get_resource_path("images/mojing/mihuanjing.png"),
            (
                self.locationRightTopX,
                self.locationRightTopY,
                self.locationRightTopWidth,
                self.locationRightTopHeight,
            ),
        )
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/mihuanjing.png"))
            self.zhengDian()
            return
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/shi.png"),
            self.get_resource_path("images/zdzd.png"),
            "left",
            "",
        )
        # 进入第四层
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
            self.get_resource_path("images/mojing/yujing.png"),
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
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/yujing.png"))
            self.zhengDian()
            return
        # 打黑白无常
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/heiwuchang.png"),
            self.get_resource_path("images/zdzd.png"),
            "right",
            "",
        )
        self.waitFor(
            self.get_resource_path("images/mojing/yujing.png"),
            (
                self.locationRightTopX,
                self.locationRightTopY,
                self.locationRightTopWidth,
                self.locationRightTopHeight,
            ),
        )
        if time.localtime().tm_min == 58:
            # 打整点
            self.outScript(self.get_resource_path("images/mojing/yujing.png"))
            self.zhengDian()
            return
        self.press_keys_until_image_found(
            self.get_resource_path("images/mojing/baiwuchang.png"),
            self.get_resource_path("images/zdzd.png"),
            "left",
            "",
        )
        # 退出副本
        self.outScript(self.get_resource_path("images/mojing/yujing.png"))
        # 魔镜脚本

    def mojingScriptOld(self):
        print("开始魔镜祭坛")
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
        self.findAndClickPic(
            self.get_resource_path("images/mojing/luyangchengxi.png"),
            self.get_resource_path("images/mojing/injitan.png"),
            self.get_resource_path("images/mojing/injitan.png"),
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            "",
            "",
        )
        # 打一个第一层的怪
        self.findAndClickPic(
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/chirenyao.png"),
            self.get_resource_path("images/mojing/chirenyao.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "",
        )
        # 进入第二层
        self.findAndClickPic(
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            "",
            "right",
        )
        self.findAndClickPic(
            self.get_resource_path("images/mojing/jingxiangdiceng.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/yijijingxiang.png"),
            self.get_resource_path("images/mojing/yijijingxiang.png"),
            "",
            "",
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
        self.findAndClickPic(
            self.get_resource_path("images/mojing/yijijingxiang.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            "",
            "right",
        )
        self.findAndClickPic(
            self.get_resource_path("images/mojing/yijijingxiang.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/mihuanjing.png"),
            self.get_resource_path("images/mojing/mihuanjing.png"),
            "",
            "",
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

        # 进入第四层
        self.findAndClickPic(
            self.get_resource_path("images/mojing/mihuanjing.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/tiaoyuetu.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            "",
            "right",
        )
        self.findAndClickPic(
            self.get_resource_path("images/mojing/mihuanjing.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/go2.png"),
            self.get_resource_path("images/mojing/yujing.png"),
            self.get_resource_path("images/mojing/yujing.png"),
            "",
            "",
        )
        # 打黑白无常
        self.findAndClickPic(
            self.get_resource_path("images/mojing/yujing.png"),
            self.get_resource_path("images/mojing/baiwuchang.png"),
            self.get_resource_path("images/mojing/baiwuchang.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "left",
        )
        self.findAndClickPic(
            self.get_resource_path("images/mojing/yujing.png"),
            self.get_resource_path("images/mojing/heiwuchang.png"),
            self.get_resource_path("images/mojing/heiwuchang.png"),
            self.get_resource_path("images/zdzd.png"),
            self.get_resource_path("images/zdzd1.png"),
            "",
            "right",
        )
        # 退出副本
        self.outScript(self.get_resource_path("images/mojing/yujing.png"))

    # 一直执行官渡
    def guanduWhile(self):
        self.beginFun()
        while True:
            self.guanduScript()

    # 一直执行红
    def hongWhile(self):
        self.beginFun()
        while True:
            self.hongScript()

    # 一直执行战魂
    def zhanhunWhile(self):
        self.beginFun()
        while True:
            self.zhanhunScript()

    # 一直执行魔镜
    def mojingWhile(self):
        self.beginFun()
        while True:
            self.mojingScript()

    # 一次战魂一次红+整点
    def guanduAndHongAndZd(self):
        self.beginFun()
        self.zhanhunScript()
        time.sleep(1)
        self.feiFb(self.get_resource_path("images/mojing/ditudianwei.png"), True)
        self.hongScript()
        time.sleep(1)
        self.zhengDian()


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

        # bmp = wx.Bitmap(self.get_resource_path("images/script.ico"),wx.BITMAP_TYPE_ICO)
        # bitmap = wx.StaticBitmap(self.panel, -1, bmp, pos=(10, 10),size=(26, 26))
        # text = wx.StaticText(self.panel, -1, label="梦幻三国脚本", pos=(40, 17))
        # # 获取按钮的字体设置字体为加粗
        # font = text.GetFont()
        # font.SetWeight(wx.FONTWEIGHT_BOLD)
        # font.SetPointSize(10)
        # text.SetFont(font)
        # Start button
        self.button_start = wx.Button(
            self.panel,
            label="开始脚本(F5)",
            pos=(10, 45),
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
            self.panel, label="暂停脚本(F6)", pos=(10, 75), style=wx.BORDER_NONE
        )
        self.Bind(wx.EVT_BUTTON, self.button_pause_click, self.button_pause)
        # 设置按钮背景颜色
        self.button_pause.SetBackgroundColour(wx.Colour(226, 96, 95))
        self.button_pause.SetForegroundColour(
            wx.Colour(255, 255, 255)
        )  # 设置为白色文字

        # Resume button
        self.button_resume = wx.Button(
            self.panel, label="继续脚本(F7)", pos=(146, 75), style=wx.BORDER_NONE
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
            pos=(10, 10),
            size=(225, 30),
            choices=[
                "官渡",
                "嗜血战场(精英)",
                "战魂楼(精英)",
                "祭坛魔镜",
                "战魂+红+整点",
                "整点",
            ],
        )
        self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
        self.dropdown.SetHint("选择一个要执行的脚本")
        self.text_ctrl = wx.TextCtrl(
            self.panel, pos=(10, 110), size=(225, 130), style=wx.TE_MULTILINE
        )
        self.thread = None
        sys.stdout = self

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_pressed)

    def get_resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def write(self, text):
        self.text_ctrl.WriteText(text)

    def on_key_pressed(self, event):
        key_code = event.GetKeyCode()

        if key_code == wx.WXK_F5:
            self.start_script()
        elif key_code == wx.WXK_F6:
            self.pause_script()
        elif key_code == wx.WXK_F7:
            self.resume_script()
        elif key_code == wx.WXK_F8:
            self.stop_script()

        event.Skip()

    def start_script(self):
        if self.thread is None or not self.thread.is_alive():
            scriptName = self.scriptName
            self.thread = MyThread(scriptName)
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
        if not self.scriptName:
            self.thread.show_error_message("请先选择脚本！")
            return
        # terminate.set()
        print("退出脚本！")
        # self.thread.stoped = True
        sys.exit()

    def on_select_script(self, event):
        self.scriptName = self.dropdown.GetValue()

    def button_start_click(self, event):
        self.start_script()

    def button_pause_click(self, event):
        self.pause_script()

    def button_resume_click(self, event):
        self.resume_script()

    def button_stop_click(self, event):
        self.stop_script()


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
