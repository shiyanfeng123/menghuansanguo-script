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

pyautogui.PAUSE = 0.005
pyautogui.FAILSAFE = True  # 鼠标光标在屏幕左上角，会导致程序异常，用于终止程序运行。
# 打包命令：pyinstaller -F -w --add-data "images;images" --icon=images\script.ico .\yaScript.py
# pyinstaller yaScript.spec

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
# import psutil
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
  def __init__(self,scriptName):
    super().__init__()
    self.guanDuCount = 0
    self.scriptName = scriptName
    self.confidenceNum = 0.9
    while True:
      if pyautogui.locateOnScreen(self.get_resource_path("images/lefttop.png"),
                                  confidence=self.confidenceNum) and pyautogui.locateOnScreen(
              self.get_resource_path("images/righttop.png"), confidence=self.confidenceNum) and pyautogui.locateOnScreen(
              self.get_resource_path("images/leftbottom.png"), confidence=self.confidenceNum):
        break
    self.lefttop = pyautogui.locateOnScreen(self.get_resource_path("images/lefttop.png"),confidence=self.confidenceNum)
    self.righttop1 = pyautogui.locateOnScreen(self.get_resource_path("images/righttop.png"),confidence=self.confidenceNum)
    self.leftbottom = pyautogui.locateOnScreen(self.get_resource_path("images/leftbottom.png"),confidence=self.confidenceNum)
    if not self.lefttop or not self.righttop1 or not self.leftbottom:
      self.show_error_message('未检测到游戏页面')
      return
    self.locationX = self.lefttop.left-50
    self.locationY = self.lefttop.top-50
    self.locationWidth = self.righttop1.left+self.righttop1.width-self.locationX+50
    self.locationHeight = self.leftbottom.top+self.leftbottom.height-self.locationY+50
    self.stoped = False
    self.clickBTime=0
    self.prevA = ''


  def run(self):
    print('鼠标放屏幕左上角退出当前脚本')
    if self.scriptName == '官渡':
      while True:
        self.guanduScript()
    elif self.scriptName == '嗜血战场(精英)':
      while True:
        self.hongScript()
    elif self.scriptName=='战魂楼(精英)':
      while True:
        self.zhanhunScript()

  def show_error_message(self,message):
    app = wx.App()
    dlg = wx.MessageDialog(None, message, "Error", style=wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()

  # 找当前的路径
  def get_resource_path(self,relative_path):
    if hasattr(sys, '_MEIPASS'):
      return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
  # 战斗结束去除黑色弹框
  def clearBox(self,current):
    while True:
      with condition:
        if self.stoped == True:
          condition.wait()
      if pyautogui.locateOnScreen(current,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
        break
  # 退出当前副本
  def outScript(self,current):
    print('退出当前副本')
    while True:
      with condition:
        if self.stoped == True:
          condition.wait()
      if pyautogui.locateOnScreen(current,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
        break
    while True:
      with condition:
        if self.stoped == True:
          condition.wait()
      if pyautogui.locateOnScreen(self.get_resource_path("images/xiulian.png"),confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
        break
    locationOut = pyautogui.locateCenterOnScreen(self.get_resource_path("images/xiulian.png"), confidence=self.confidenceNum,region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
    pyautogui.click(int(locationOut.x-20),int( locationOut.y-40))
    while True:
      with condition:
        if self.stoped == True:
          condition.wait()
      if pyautogui.locateOnScreen(self.get_resource_path("images/queding.png"),confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
        break
    locationQueding = pyautogui.locateCenterOnScreen(self.get_resource_path("images/queding.png"), confidence=self.confidenceNum,region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
    pyautogui.click(locationQueding.x, locationQueding.y)
    time.sleep(1)
    fubenjiangli = pyautogui.locateCenterOnScreen(self.get_resource_path("images/fubenjiangli.png"),confidence=self.confidenceNum, region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
    pyautogui.click(fubenjiangli.x, fubenjiangli.y)
  # 整点
  def zhengDian(self):
     with condition:
      if self.stoped==True:
        condition.wait()
      print('打整点')
     while True:
       with condition:
         if self.stoped == True:
           condition.wait()
       if pyautogui.locateOnScreen(self.get_resource_path("images/opentalk.png"), confidence=self.confidenceNum,region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight)):
         break
     location1 = pyautogui.locateCenterOnScreen(self.get_resource_path("images/opentalk.png"), confidence=self.confidenceNum,region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
     if location1:
       pyautogui.click(location1.x, location1.y)
  # 找图并且点击
  def click_image(self, image_path, image_confidence, image_region):
    image_locations = pyautogui.locateCenterOnScreen(image_path, confidence=image_confidence, region=image_region)
    if image_locations:
      with condition:
        if self.stoped == True:
          condition.wait()
      pyautogui.click(image_locations.x, image_locations.y,clicks=1)
      return True
    else:
      return False
  #找一样的图，点击最左边的图
  def click_image_with_min_x(self,image_path,image_confidence,image_region):
    image_locations = list(pyautogui.locateAllOnScreen(image_path, confidence=image_confidence, region=image_region))
    if image_locations:
      with condition:
          if self.stoped == True:
            condition.wait()
      min_x_location = min(image_locations, key=lambda loc: loc.left)
      target_x = min_x_location.left + min_x_location.width // 2
      target_y = min_x_location.top + min_x_location.height // 2
      pyautogui.click(target_x, target_y,clicks=2,interval=0.02)
      return True
    else:
      return False
  # 找图并且点击
  def findAndClickPic(self,A, B1,B2, C1,C2,D,E):
       EIsDown=False
       self.clickBTime = 0
       # if time.localtime().tm_min == 58:
       #   zhengDian()
       #   return
       # print(B1)
       startTime = time.time()
       with condition:
        if self.stoped == True:
          condition.wait()
       while not pyautogui.locateOnScreen(A,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
        with condition:
          if self.stoped == True:
            condition.wait()
           # print("未找到图片")
          time.sleep(0.1)
          if self.confidenceNum>0.7:
            self.confidenceNum-=0.1
       self.confidenceNum=0.9
       while not pyautogui.locateOnScreen(C1,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)) and not pyautogui.locateOnScreen(C2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
          with condition:
            if self.stoped == True:
              condition.wait()
          # 去除获得铜币黑框
          self.click_image(self.get_resource_path("images/huodetongbi.png"),self.confidenceNum,(self.locationX,self.locationY,self.locationWidth,self.locationHeight))
          # 点击取消
          self.click_image(self.get_resource_path("images/closeJJ.png"),self.confidenceNum,(self.locationX,self.locationY,self.locationWidth,self.locationHeight))
          # 点击x
          self.click_image(self.get_resource_path("images/close.png"), self.confidenceNum,(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
          if time.time()-startTime > 120:
            print('超过两分钟没找到目标，退出副本重新进入')
            self.outScript(A)
            self.guanduScript()
            return '重新进入'
            #   D找图片D点击
          if D != '' and self.clickBTime==0:
              with condition:
                if self.stoped == True:
                  condition.wait()
              self.click_image(D,self.confidenceNum,(self.locationX,self.locationY,self.locationWidth,self.locationHeight))
          #     点击按钮E
          while E != '' and not EIsDown:
            with condition:
              if self.stoped == True:
                condition.wait()
            pyautogui.keyDown(E)
            isClick = self.click_image_with_min_x(B1,self.confidenceNum,(self.locationX,self.locationY,self.locationWidth,self.locationHeight))
            if isClick:
              EIsDown = True
              pyautogui.keyUp(E)
              break
            isClick2 = self.click_image_with_min_x(B2, self.confidenceNum, (
            self.locationX, self.locationY, self.locationWidth, self.locationHeight))
            if isClick2:
              EIsDown = True
              pyautogui.keyUp(E)
              break
            # if pyautogui.locateCenterOnScreen(B1,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight))or pyautogui.locateCenterOnScreen(B2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
            #   EIsDown = True
            #   pyautogui.keyUp(E)
            #   break
          if E != '' and EIsDown:
            pyautogui.keyUp(E)
          with condition:
            if self.stoped == True:
              condition.wait()
          isClickB1 = False
          if pyautogui.locateOnScreen(C1,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)) or pyautogui.locateOnScreen(C2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
            break
          isClickB1 = self.click_image_with_min_x(B1,self.confidenceNum,(self.locationX,self.locationY,int(self.locationWidth*0.75),self.locationHeight))
          if isClickB1:
            self.clickBTime = time.time()
          if pyautogui.locateOnScreen(C1,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)) or pyautogui.locateOnScreen(C2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
            break
          isClickB2 = self.click_image_with_min_x(B2, self.confidenceNum, (self.locationX, self.locationY, int(self.locationWidth * 0.75), self.locationHeight))
          if isClickB2:
            self.clickBTime = time.time()
          if pyautogui.locateOnScreen(C1,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)) or pyautogui.locateOnScreen(C2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
            break
          if not isClickB1:
            isClickB1 = self.click_image_with_min_x(B1, self.confidenceNum, (
            self.locationX, self.locationY, self.locationWidth, self.locationHeight))
            if isClickB1:
              self.clickBTime = time.time()
            if pyautogui.locateOnScreen(C1, confidence=self.confidenceNum, region=(self.locationX, self.locationY, self.locationWidth, self.locationHeight)) or pyautogui.locateOnScreen(C2,confidence=self.confidenceNum,region=(self.locationX,self.locationY,self.locationWidth,self.locationHeight)):
              break
          if not isClickB2:
           isClickB2 = self.click_image_with_min_x(B2, self.confidenceNum, (self.locationX, self.locationY, self.locationWidth, self.locationHeight))
           if isClickB2:
            self.clickBTime = time.time()
           if self.confidenceNum>0.7:
            self.confidenceNum-=0.1
          # elif self.clickBTime>0and time.time()-self.clickBTime > 5 and EIsDown == True:
          #       self.clickBTime = time.time()
          #       pyautogui.press('up', interval=0.2)
       self.confidenceNum = 0.9
       if E != '':
         with condition:
          if self.stoped == True:
            condition.wait()
         pyautogui.keyUp(E)
       self.prevA = A
  #官渡脚本
  def guanduScript(self):
      with condition:
        if self.stoped == True:
          condition.wait()
      self.guanDuCount += 1
      print(f"开始第{self.guanDuCount}次官渡.")
      # 进入官渡
      self.findAndClickPic(self.get_resource_path("images/guandu.png"), self.get_resource_path("images/caoCao.png"), self.get_resource_path("images/caoCao2.png"), self.get_resource_path("images/inguanDu.png"),self.get_resource_path("images/inguanDu.png"),
                      self.get_resource_path('images/guanduD.png'),'')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 进入第一层
      self.findAndClickPic(self.get_resource_path("images/guandu.png"), self.get_resource_path("images/inguanDu.png"), self.get_resource_path("images/inguanDu.png"), self.get_resource_path("images/caoyindazhang.png"),self.get_resource_path("images/caoyindazhang.png"), '','')
      with condition:
        if self.stoped == True:
          condition.wait()
      self.findAndClickPic(self.get_resource_path("images/caoyindazhang.png"), self.get_resource_path("images/dycrk.png"), self.get_resource_path("images/dycrk2.png"), self.get_resource_path("images/caoyuanzhanchang.png"),self.get_resource_path("images/caoyuanzhanchang.png"),
                      '','')
      # 关闭右边框
      self.click_image(self.get_resource_path("images/closeright.png"), self.confidenceNum,(self.locationX, self.locationY, self.locationWidth, self.locationHeight))
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第一个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj3.png"), self.get_resource_path("images/hbj4.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '','')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第二个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj2.png"), self.get_resource_path("images/hbj1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),'','right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第三个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj2.png"), self.get_resource_path("images/hbj1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '','right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第四个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj2.png"), self.get_resource_path("images/hbj1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '','right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第五个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj2.png"), self.get_resource_path("images/hbj1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '', 'right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 第五个河北军
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/hbj2.png"), self.get_resource_path("images/hbj1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '', 'right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 颜良
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/yanliang.png"), self.get_resource_path("images/yanliang1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '', 'left')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 文丑
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/wenchou.png"), self.get_resource_path("images/wenchou1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),
                      '', 'right')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 去大帐
      self.findAndClickPic(self.get_resource_path("images/caoyuanzhanchang.png"), self.get_resource_path("images/godazhang.png"), self.get_resource_path("images/godazhang.png"), self.get_resource_path("images/caoyindazhang.png"),self.get_resource_path("images/caoyindazhang.png"),
                      '', 'left')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 找到曹操进入乌巢
      self.findAndClickPic(self.get_resource_path("images/caoyindazhang.png"), self.get_resource_path("images/caochengxiang.png"), self.get_resource_path("images/caochengxiang1.png"),
                      self.get_resource_path("images/gowuchao.png"),self.get_resource_path("images/gowuchao.png"),
                      '', '')
      with condition:
        if self.stoped == True:
          condition.wait()
      self.findAndClickPic(self.get_resource_path("images/caoyindazhang.png"), self.get_resource_path("images/gowuchao.png"), self.get_resource_path("images/gowuchao.png"),
                      self.get_resource_path("images/wuchao.png"),self.get_resource_path("images/wuchao.png"),
                      '', '')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 进入魂殿打魂
      # self.findAndClickPic(self.get_resource_path("images/wuchao.png"), self.get_resource_path("images/inhundian1.png"), self.get_resource_path("images/inhundian1.png"),self.get_resource_path("images/hundian.png"),self.get_resource_path("images/hundian.png"),'', 'left')
      # with condition:
      #   if self.stoped == True:
      #     condition.wait()
      self.findAndClickPic(self.get_resource_path("images/wuchao.png"), self.get_resource_path("images/wenchouzhihun.png"), self.get_resource_path("images/wenchouzhihun1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"), '', 'left')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 魂殿进乌巢
      self.findAndClickPic(self.get_resource_path("images/hundian.png"), self.get_resource_path("images/gowuchao2.png"), self.get_resource_path("images/gowuchao2.png"),self.get_resource_path("images/wuchao.png"),self.get_resource_path("images/wuchao.png"),'', '')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 打淳
      self.findAndClickPic(self.get_resource_path("images/wuchao.png"), self.get_resource_path("images/cyq.png"), self.get_resource_path("images/cyq1.png"),self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),'', '')
      with condition:
        if self.stoped == True:
          condition.wait()
      # 打袁绍
      self.findAndClickPic(self.get_resource_path("images/wuchao.png"), self.get_resource_path("images/yuanshao.png"), self.get_resource_path("images/yuanshao1.png"), self.get_resource_path("images/zdzd.png"),self.get_resource_path("images/zdzd1.png"),'', '')
      with condition:
        if self.stoped == True:
          condition.wait()
      #退出副本
      self.outScript(self.get_resource_path("images/wuchao.png"))
  # 红脚本
  def hongScript(self):
    print('开始打红')
    with condition:
      if self.stoped == True:
        condition.wait()
    # 进入红
    self.findAndClickPic(self.get_resource_path("images/hong/hulaoguanwai.png"), self.get_resource_path("images/hong/hongdianwei.png"),
                         self.get_resource_path("images/hong/hongdianwei.png"), self.get_resource_path("images/hong/inhong.png"),
                         self.get_resource_path("images/hong/inhong.png"),
                         self.get_resource_path("images/hong/inhongD.png"), '')
    self.findAndClickPic(self.get_resource_path("images/hong/hulaoguanwai.png"),
                         self.get_resource_path("images/hong/inhong.png"),
                         self.get_resource_path("images/hong/inhong.png"),
                         self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/junyin.png"),
                         '', '')
    # 第一个弓兵
    self.findAndClickPic(self.get_resource_path("images/hong/junyin.png"),
                       self.get_resource_path("images/hong/gongbin.png"),
                       self.get_resource_path("images/hong/gongbin1.png"),
                       self.get_resource_path("images/zdzd.png"),
                       self.get_resource_path("images/zdzd1.png"),
                       '', 'right')
    self.findAndClickPic(self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/gongbin.png"),
                         self.get_resource_path("images/hong/gongbin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 弓兵头领
    self.findAndClickPic(self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/gongbintoulin.png"),
                         self.get_resource_path("images/hong/gongbintoulin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 进入军粮营
    self.findAndClickPic(self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/gojunliangyin.png"),
                         self.get_resource_path("images/hong/gojunliangyin1.png"),
                         self.get_resource_path("images/hong/junliangyin.png"),
                         self.get_resource_path("images/hong/junliangyin.png"),
                         '', 'left')
    # 第一个护卫兵
    self.findAndClickPic(self.get_resource_path("images/hong/junliangyin.png"),
                         self.get_resource_path("images/hong/huweibin.png"),
                         self.get_resource_path("images/hong/huweibin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 第二个护卫兵
    self.findAndClickPic(self.get_resource_path("images/hong/junliangyin.png"),
                         self.get_resource_path("images/hong/huweibin.png"),
                         self.get_resource_path("images/hong/huweibin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 护粮将领
    self.findAndClickPic(self.get_resource_path("images/hong/junliangyin.png"),
                         self.get_resource_path("images/hong/huliangjianglin.png"),
                         self.get_resource_path("images/hong/huliangjianglin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 进入训兵营
    self.findAndClickPic(self.get_resource_path("images/hong/junliangyin.png"),
                         self.get_resource_path("images/hong/goxunbinyin.png"),
                         self.get_resource_path("images/hong/goxunbinyin1.png"),
                         self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/xunbinyin.png"),
                         '', 'right')
    # 第一个骑兵
    self.findAndClickPic(self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/qibin.png"),
                         self.get_resource_path("images/hong/qibin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 第2个骑兵
    self.findAndClickPic(self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/qibin.png"),
                         self.get_resource_path("images/hong/qibin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 第3个骑兵
    self.findAndClickPic(self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/qibin.png"),
                         self.get_resource_path("images/hong/qibin1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'right')
    # 训兵将领
    self.findAndClickPic(self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/xunbinjiangling.png"),
                         self.get_resource_path("images/hong/xunbinjiangling1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'left')
    # 进入军营
    self.findAndClickPic(self.get_resource_path("images/hong/xunbinyin.png"),
                         self.get_resource_path("images/hong/gojunyin1.png"),
                         self.get_resource_path("images/hong/gojunyin.png"),
                         self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/junyin.png"),
                         '', 'up')
    # 进入帐篷
    self.findAndClickPic(self.get_resource_path("images/hong/junyin.png"),
                         self.get_resource_path("images/hong/gozhangpeng.png"),
                         self.get_resource_path("images/hong/gozhangpeng1.png"),
                         self.get_resource_path("images/hong/zhangpeng.png"),
                         self.get_resource_path("images/hong/zhangpeng.png"),
                         '', 'left')
    # boss
    self.findAndClickPic(self.get_resource_path("images/hong/zhangpeng.png"),
                         self.get_resource_path("images/hong/konghunwushi.png"),
                         self.get_resource_path("images/hong/konghunwushi1.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', 'up')
    # 退出副本
    self.outScript(self.get_resource_path("images/hong/zhangpeng.png"))
  #  战魂脚本
  def zhanhunScript(self):
    print('开始战魂')
    with condition:
      if self.stoped == True:
        condition.wait()
    # 进入战魂
    self.findAndClickPic(self.get_resource_path("images/zhanhun/luoyangdadao.png"), self.get_resource_path("images/zhanhun/zhanhun.png"),
                         self.get_resource_path("images/zhanhun/zhanhun1.png"), self.get_resource_path("images/zhanhun/inzhanhun.png"),
                         self.get_resource_path("images/zhanhun/inzhanhun.png"),
                         self.get_resource_path("images/zhanhun/inzhanhunD.png"), '')

    self.findAndClickPic(self.get_resource_path("images/zhanhun/luoyangdadao.png"),
                         self.get_resource_path("images/zhanhun/inzhanhun.png"),
                         self.get_resource_path("images/zhanhun/inzhanhun.png"),
                         self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
                         self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
                         '', '')
    # 1
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
                         self.get_resource_path("images/zhanhun/zhangbao1.png"),
                         self.get_resource_path("images/zhanhun/zhangbao2.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', '')

    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou1.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/zhangliang.png"),
                         self.get_resource_path("images/zhanhun/zhangliang.png"),
                         '', 'right')
    # 2
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
                         self.get_resource_path("images/zhanhun/zhangliang1.png"),
                         self.get_resource_path("images/zhanhun/zhangliang2.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou2.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/zhangjiao.png"),
                         self.get_resource_path("images/zhanhun/zhangjiao.png"),
                         '', 'right')
    # 3
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou3.png"),
                         self.get_resource_path("images/zhanhun/zhangjiao1.png"),
                         self.get_resource_path("images/zhanhun/zhangjiao2.png"),
                         self.get_resource_path("images/zdzd.png"),
                         self.get_resource_path("images/zdzd1.png"),
                         '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou3.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/wenchou.png"),
                         self.get_resource_path("images/zhanhun/wenchou.png"),
                         '', 'right')
    # 4
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou4.png"),
                        self.get_resource_path("images/zhanhun/wenchou1.png"),
                        self.get_resource_path("images/zhanhun/wenchou1.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou4.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/yanliang.png"),
                         self.get_resource_path("images/zhanhun/yanliang.png"),
                         '', 'right')
    # 5
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou5.png"),
                        self.get_resource_path("images/zhanhun/yanliang1.png"),
                        self.get_resource_path("images/zhanhun/yanliang2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou5.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/huaxiong.png"),
                         self.get_resource_path("images/zhanhun/huaxiong.png"),
                         '', 'right')
    # 6
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou6.png"),
                        self.get_resource_path("images/zhanhun/huaxiong1.png"),
                        self.get_resource_path("images/zhanhun/huaxiong2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou6.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/sunce.png"),
                         self.get_resource_path("images/zhanhun/sunce.png"),
                         '', 'right')
    # 7
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou7.png"),
                        self.get_resource_path("images/zhanhun/sunce1.png"),
                        self.get_resource_path("images/zhanhun/sunce2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou7.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/dianwei.png"),
                         self.get_resource_path("images/zhanhun/dianwei.png"),
                         '', 'right')
    # 8
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou8.png"),
                        self.get_resource_path("images/zhanhun/dianwei1.png"),
                        self.get_resource_path("images/zhanhun/dianwei2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou8.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/guojia.png"),
                         self.get_resource_path("images/zhanhun/guojia.png"),
                         '', 'right')
    # 9
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou9.png"),
                        self.get_resource_path("images/zhanhun/guojia1.png"),
                        self.get_resource_path("images/zhanhun/guojia2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou9.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/liubei.png"),
                         self.get_resource_path("images/zhanhun/liubei.png"),
                         '', 'right')
    # 10
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou10.png"),
                        self.get_resource_path("images/zhanhun/liubei1.png"),
                        self.get_resource_path("images/zhanhun/liubei2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou10.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/caocao.png"),
                         self.get_resource_path("images/zhanhun/caocao.png"),
                         '', 'right')
    # 11
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou11.png"),
                        self.get_resource_path("images/zhanhun/caocao1.png"),
                        self.get_resource_path("images/zhanhun/caocao2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou11.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/yuanshao.png"),
                         self.get_resource_path("images/zhanhun/yuanshao.png"),
                         '', 'right')
    # 12
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou12.png"),
                        self.get_resource_path("images/zhanhun/yuanshao1.png"),
                        self.get_resource_path("images/zhanhun/yuanshao2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou12.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/zhangfei.png"),
                         self.get_resource_path("images/zhanhun/zhangfei.png"),
                         '', 'right')
    # 13
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou13.png"),
                        self.get_resource_path("images/zhanhun/zhangfei1.png"),
                        self.get_resource_path("images/zhanhun/zhangfei2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou13.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/daqiao.png"),
                         self.get_resource_path("images/zhanhun/daqiao.png"),
                         '', 'right')
    # 14
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou14.png"),
                        self.get_resource_path("images/zhanhun/daqiao1.png"),
                        self.get_resource_path("images/zhanhun/daqiao2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou14.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/guanyu.png"),
                         self.get_resource_path("images/zhanhun/guanyu.png"),
                         '', 'right')
    # 15
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou15.png"),
                        self.get_resource_path("images/zhanhun/guanyu1.png"),
                        self.get_resource_path("images/zhanhun/guanyu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou15.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/lvbu.png"),
                         self.get_resource_path("images/zhanhun/lvbu.png"),
                         '', 'right')
    # 16
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou16.png"),
                        self.get_resource_path("images/zhanhun/lvbu1.png"),
                        self.get_resource_path("images/zhanhun/lvbu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou16.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
                         self.get_resource_path("images/zhanhun/mohuazhangfei.png"),
                         '', 'right')
    # 17
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou17.png"),
                        self.get_resource_path("images/zhanhun/mohuazhangfei1.png"),
                        self.get_resource_path("images/zhanhun/mohuazhangfei2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou17.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
                         self.get_resource_path("images/zhanhun/mohuaguanyu.png"),
                         '', 'right')
    # 18
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou18.png"),
                        self.get_resource_path("images/zhanhun/mohuaguanyu1.png"),
                        self.get_resource_path("images/zhanhun/mohuaguanyu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou18.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         '', 'right')
    # 19
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou19.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu1.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou19.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         '', 'right')
    # 20
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou20.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu1.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou20.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/liubei.png"),
                         self.get_resource_path("images/zhanhun/liubei.png"),
                         '', 'right')
    # 21
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
                        self.get_resource_path("images/zhanhun/liubei1.png"),
                        self.get_resource_path("images/zhanhun/liubei2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou21.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/yuanshao.png"),
                         self.get_resource_path("images/zhanhun/yuanshao.png"),
                         '', 'right')
    # 22
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
                        self.get_resource_path("images/zhanhun/yuanshao1.png"),
                        self.get_resource_path("images/zhanhun/yuanshao2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou22.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/caocao.png"),
                         self.get_resource_path("images/zhanhun/caocao.png"),
                         '', 'right')
    # 23
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
                        self.get_resource_path("images/zhanhun/caocao1.png"),
                        self.get_resource_path("images/zhanhun/caocao2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou23.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/lvbu.png"),
                         self.get_resource_path("images/zhanhun/lvbu.png"),
                         '', 'right')
    # 24
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
                        self.get_resource_path("images/zhanhun/lvbu1.png"),
                        self.get_resource_path("images/zhanhun/lvbu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou24.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         self.get_resource_path("images/zhanhun/mohualvbu.png"),
                         '', 'right')
    # 25
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu1.png"),
                        self.get_resource_path("images/zhanhun/mohualvbu2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou25.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext.png"),
                         self.get_resource_path("images/zhanhun/zhanhungonext1.png"),
                         self.get_resource_path("images/zhanhun/renshengwa.png"),
                         self.get_resource_path("images/zhanhun/renshengwa.png"),
                         '', 'right')
    # 26
    self.findAndClickPic(self.get_resource_path("images/zhanhun/zhanhunlou26.png"),
                        self.get_resource_path("images/zhanhun/renshengwa1.png"),
                        self.get_resource_path("images/zhanhun/renshengwa2.png"),
                        self.get_resource_path("images/zdzd.png"),
                        self.get_resource_path("images/zdzd1.png"),
                        '', '')
    # 退出副本
    self.outScript(self.get_resource_path("images/zhanhun/zhanhunlou26.png"))
class MyFrame(wx.Frame):
  def __init__(self):
    wx.Frame.__init__(self, None, title="梦幻三国脚本",  size=(260, 300))

    self.SetIcon(wx.Icon(self.get_resource_path("images/script.ico"),wx.BITMAP_TYPE_ICO))
    self.SetPosition(wx.Point(10, 30))
    self.panel = wx.Panel(self)
    self.SetWindowStyle(wx.STAY_ON_TOP)  # 按钮所在控件一直存在在桌面上
    self.scriptName = ""

    bmp = wx.Bitmap(self.get_resource_path("images/script.ico"), wx.BITMAP_TYPE_ICO)
    bitmap = wx.StaticBitmap( self.panel, -1, bmp, pos=(10, 10),size=(26,26))
    text = wx.StaticText(self.panel, -1, label="梦幻三国脚本", pos=(40, 17))
    # 获取按钮的字体设置字体为加粗
    font = text.GetFont()
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    font.SetPointSize(10)
    text.SetFont(font)
    # Start button
    self.button_start = wx.Button(self.panel, label="开始脚本(F5)", pos=(10, 80),size=(226,26),style=wx.BORDER_NONE)
    self.Bind(wx.EVT_BUTTON, self.button_start_click, self.button_start)
    # 设置按钮背景颜色
    self.button_start.SetBackgroundColour(wx.Colour(20, 180, 168))  # 设置为红色背景
    self.button_start.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字
    # Pause button
    self.button_pause = wx.Button(self.panel, label="暂停脚本(F6)", pos=(10, 110),style=wx.BORDER_NONE)
    self.Bind(wx.EVT_BUTTON, self.button_pause_click, self.button_pause)
    # 设置按钮背景颜色
    self.button_pause.SetBackgroundColour(wx.Colour(226, 96, 95))
    self.button_pause.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字

    # Resume button
    self.button_resume = wx.Button(self.panel, label="继续脚本(F7)", pos=(146, 110),style=wx.BORDER_NONE)
    self.Bind(wx.EVT_BUTTON, self.button_resume_click, self.button_resume)
    # 设置按钮背景颜色
    self.button_resume.SetBackgroundColour(wx.Colour(103, 194, 58))
    self.button_resume.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字

    # Stop button
    # self.button_stop = wx.Button(self.panel, label="退出脚本(F8)", pos=(146, 110),style=wx.BORDER_NONE)
    # self.Bind(wx.EVT_BUTTON, self.button_stop_click, self.button_stop)
    # 设置按钮背景颜色
    # self.button_stop.SetBackgroundColour(wx.Colour(144, 144, 153))
    # self.button_stop.SetForegroundColour(wx.Colour(255, 255, 255))  # 设置为白色文字

    self.dropdown = wx.ComboBox(self.panel, pos=(10, 45),size=(225,30), choices=["官渡", "嗜血战场(精英)", "战魂楼(精英)"])
    self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
    self.dropdown.SetHint('选择一个要执行的脚本')
    self.text_ctrl = wx.TextCtrl(self.panel, pos=(10, 145), size=(225, 130), style=wx.TE_MULTILINE)
    self.thread = None
    sys.stdout = self

    self.Bind(wx.EVT_CHAR_HOOK, self.on_key_pressed)

  def get_resource_path(self , relative_path):
    if hasattr(sys, '_MEIPASS'):

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
        self.thread.show_error_message('请先选择脚本！')
        return
      print('现在开始脚本！')
      self.thread.start()

  def pause_script(self):
    if not self.scriptName:
      self.thread.show_error_message('请先选择脚本！')
      return
    print('暂停脚本！')
    if self.thread is not None:
      # paused.set()
      self.thread.stoped = True

  def resume_script(self):
    if not self.scriptName:
      self.thread.show_error_message('请先选择脚本！')
      return
    print('继续执行脚本！')
    if self.thread is not None:
      # paused.clear()
      self.thread.stoped = False
      with condition:
        condition.notify_all()

  def stop_script(self):
    if not self.scriptName:
      self.thread.show_error_message('请先选择脚本！')
      return
    # terminate.set()
    print('退出脚本！')
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


if __name__ == '__main__':
  app = wx.App()
  frame = MyFrame()
  frame.Show()
  app.MainLoop()