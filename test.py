import os
import ctypes
from comtypes.client import CreateObject
import comtypes.client
import subprocess
import time
import inspect
import asyncio

# from playwright.sync_api import sync_playwright
# from pyppeteer import launch
# def get_current_function_name():
# 	return inspect.stack()[1].function


# def example_function():
# 	count = 0
# 	while True:
# 		count += 1
# 		print_11(count)
# 		time.sleep(2)
# 		print("Current function name:", get_current_function_name())
#
#
# def print_11(count):
# 	print("Hello World!", count)


# def register_dll(dll_path):
# 	# 构建 regsvr32 命令，添加 /s 参数以静默运行
# 	command = ['regsvr32', '/s', dll_path]
# 	# 执行命令
# 	subprocess.run(command, check=True, capture_output=True, text=True)
#
#
# # 调用注册函数
# from pyppeteer import launch
#
#
# async def main():
# 	browser = await launch(headless=True)
# 	page = await browser.newPage()
# 	await page.goto("http://game.mhsg.online")  # 替换为您的游戏网址
#
# 	# 在这里添加您需要的逻辑
# 	# 例如等待游戏加载完成，或执行其他操作
#
# 	# 关闭浏览器
# 	await browser.close()
#
#
# asyncio.get_event_loop().run_until_complete(main())
# return
# dm_obj = ctypes.windll.LoadLibrary(r'E:\project\python\serveAssets\plugins\RegDll.dll')
# location_dmreg = r'E:\project\python\serveAssets\plugins\dm.dll'
# register_dll(location_dmreg)
# dm_obj.DllRegisterServer(location_dmreg, 0)
dm = CreateObject('dm.dmsoft')
print(dm.Ver())
# 定义回调函数类型
ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
click_hwnd = 0


# 定义回调函数
def enum_child_windows_callback(hwnd, lParam):
	window_text = dm.GetWindowText(hwnd)
	class_name = dm.GetClassName(hwnd)
	print(f'子窗口句柄: {hwnd}, 标题: {window_text}, 类名: {class_name}')
	return True  # 返回 True 继续枚举


# 将回调函数转换为 ctypes 函数指针
enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)

# 查找目标窗口句柄
target_window_title = "11"
target_window_class = 'DUIWindow'  # 如果不知道类名，可以设为 None
hwnd = dm.FindWindowEx(0, target_window_class, target_window_title)

if hwnd == 0:
	print("目标窗口未找到")
else:
	print('找到目标窗口')
	#
	# 使用 Windows API 的 EnumChildWindows
	user32 = ctypes.WinDLL('user32', use_last_error=True)
	# 获取屏幕分辨率
	screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
	screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度


	def enum_child_proc(hwnd, lParam):
		global click_hwnd
		class_name = dm.GetWindowClass(hwnd)
		child_rect = dm.GetWindowRect(hwnd)
		if child_rect != 0:
			left, top, right, bottom, isFind = child_rect
			# if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
			# 	print(left, top, right, bottom)
			# 	click_hwnd = hwnd
			# 	return False
			if class_name == 'Chrome_RenderWidgetHostHWND':
				click_hwnd = hwnd
				return False
		return True


	enum_child_proc_type = ENUMWINDOWSPROC(enum_child_proc)
	user32.EnumChildWindows(hwnd, enum_child_proc_type, 0)
print(click_hwnd)
# 绑定窗口到后台模式
bind_result = dm.BindWindowEx(click_hwnd, "gdi", "windows3", "windows", '', 0)
if bind_result == 1:
	print("窗口绑定成功")
else:
	print("窗口绑定失败")

# 进行后台找图
# 定义查找区域
location = dm.GetClientSize(click_hwnd)
print(location)
x, y, res = location
print(x, y)
# dm.Capture(0, 0, x, y, 'srcc.bmp')
# image_list = "images/addBloud.png"  # 图像文件路径，多个图像用 | 分隔
# delta_color = "000000-605f60"  # 颜色容差
# # ab7b5c|ffffff右上角找图色偏差值
# similarity = 0.7  # 相似度阈值
dm_ret = dm.FindPicEx(0, 0, x, y, r"E:\project\python\serveAssets\images\guandu\caocao1.bmp", "", 0.9, 0)

# print(dm.CmpColor(820, 50, '091311', 1) == 0)
print(dm_ret, 'dm_ret')
# if not dm_ret:
# 	print('未找到')
# dm_ret = dm_ret.split('|')
# print(dm_ret)
# x, y = dm_ret[1], dm_ret[2]
# print(f'找到图像，坐标: ({x}, {y})')
# resmove = dm.MoveTo(int(x), int(y))
# time.sleep(0.01)
# print(resmove)
# resclick = dm.LeftClick()
# print(resclick)

# print(x, y)
# # 加载字库
# 定义字库文件路径
# import ctypes
# from comtypes.client import CreateObject
#
# # 定义字库文件路径
# font_file_path = r"E:\project\python\serveAssets\fonts\common.txt"
#
# # 读取字库文件内容
# font_data = dm.ReadFile(font_file_path)
#
# # 将字库内容转换为字节数据
# font_buffer = dm.StringToData(font_data, 1)
# # 动态分配内存
# memory_address = ctypes.windll.kernel32.VirtualAlloc(
# 	ctypes.c_void_p(0),
# 	ctypes.c_size_t(len(font_data)),
# 	0x3000,  # MEM_COMMIT | MEM_RESERVE
# 	0x40  # PAGE_READWRITE
# )
# dm.WriteData(hwnd, str(memory_address), font_data)
# print(memory_address, str(hex(memory_address)), 'memory_address')
# # 设置字典内存
# dict_id = dm.SetDictMem(0, int(memory_address), len(font_data))
#
# if dict_id != 0:
# 	print(f"字典加载成功，字典ID: {dict_id}")
# else:
# 	print("字典加载失败")

# 释放内存
# dm.FreeMem(memory_address)
# dict_id = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\common.txt")  # 字库文件路径
# dict_id1 = dm.SetDict(1, r"E:\project\python\serveAssets\fonts\team1.txt")  # 字库文件路径
# dict_id2 = dm.SetDict(2, r"E:\project\python\serveAssets\fonts\team2.txt")  # 字库文件路径
# dict_id2 = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\zhengdian.txt")  # 字库文件路径
# print(f'字库加载成功，{dict_id},{dict_id1},{dict_id2}')
# print(dm.GetDictCount(0), dm.GetDictCount(1), dm.GetDictCount(2))
# 文字识别参数
color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000'
# color_format = "ffffff-000000"  # 右上角偏移色
# color_format = 'ffffff-00000|00ff00-000000'  # 绿色字体
# color_format = 'ffff00-000000'
sim = 0.7  # 相似度阈值，可以根据实际情况调整
# dm.KeyDownChar('left')
# time.sleep(5)
# dm.KeyUpChar('left')
#
# # 进行文字识别
# example_function
print(dm.GetNowDict())
# dm.UseDict(1)
import requests
from bs4 import BeautifulSoup

# 关闭浏览器
# url = 'http://game.mhsg.online'
# import asyncio
# from pyppeteer import launch
#
#
# # 获取网页源代码
# import requests
# from bs4 import BeautifulSoup
#
# # 目标网页的 URL
# url = 'http://game.mhsg.online/'
#
# # 发送 HTTP 请求获取网页内容
# response = requests.get(url)
# # print(response)
# soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)
# # 找到所有的 iframe 元素
# iframes = soup.find_all('iframe')
#
# # 打印每个 iframe 元素的属性信息
# for i, iframe in enumerate(iframes):
# 	print(f"iframe {i + 1} 属性:")
# 	for attr, value in iframe.attrs.items():
# 		print(f"  {attr}: {value}")
# async def main():
# 	browser = await launch()
# 	page = await browser.newPage()
# 	await page.goto("https://www.4399.com/flash/71450.htm")
#
# 	iframe = await page.waitForSelector("iframe")
# 	iframe_box = await iframe.boundingBox()  # 获取iframe元素的边界框信息
# 	print("iframe 元素的坐标信息：", iframe_box)
#
# 	await browser.close()
#
#
# asyncio.get_event_loop().run_until_complete(main())
# find_str_result = dm.FindStrFastEx(0, 0, x, y, '龙生', '73766d-000000|6b726a-000000|dcdeb8-4599b9|6b7269-000000|6f736b-000000', sim)
# print(f'FindStrFast 返回结果: {find_str_result}')
# find_str_result = find_str_result.split(',')
# print(find_str_result)
# print(find_str_result[0])
# print(find_str_result[1])
# print(find_str_result[2])
# x, y = find_str_result[1], find_str_result[2]
# print(res, x, y)
# found_text = find_str_result[3]
# print(f'找到文字: {found_text}, 坐标: ({x}, {y})')

# 移动鼠标到文字中心并点击
# move_result = dm.MoveToEx(int(x), int(y), 10, 0)
# if move_result == 1:
# 	print(f'鼠标移动到 ({x}, {y}) 成功')
# 	time.sleep(0.001)
# 	click_result = dm.LeftClick()
# 	if click_result == 1:
# 		print('点击成功')
# 	else:
# 		print('点击失败')
# else:
# 	print(f'鼠标移动到 ({x}, {y}) 失败')

# 释放字库
# dm.FreeDict(dict_id)
# print(f'字库ID: {dict_id} 已释放')
# class MyDialog(wx.Dialog):
# 	def __init__(self, parent):
# 		super().__init__(parent, title="输入信息", size=(300, 230))
#
# 		panel = wx.Panel(self)
#
# 		# 创建一个垂直的BoxSizer来管理所有控件
# 		vbox = wx.BoxSizer(wx.VERTICAL)
#
# 		# 游戏名称输入框
# 		self.team_leader_text = wx.TextCtrl(panel, size=(260, 24))
# 		self.team_leader_text.SetHint("游戏名称")
# 		self.team_leader_text.Bind(wx.EVT_TEXT, self.on_text_change)
# 		vbox.Add(self.team_leader_text, flag=wx.ALL, border=5)
#
# 		# 战魂层数 ComboBox
# 		self.choiceCeng = wx.ComboBox(panel, size=(120, 30), choices=['20层', '21层', '22层', '23层', '24层', '25层', '26层'])
# 		self.choiceCeng.SetHint("战魂层数")
# 		vbox.Add(self.choiceCeng, flag=wx.ALL, border=5)
#
# 		# 黑风/矿产次数输入框
# 		self.number_input = wx.TextCtrl(panel, size=(120, 24), validator=NumberValidator())
# 		self.number_input.SetHint("黑风/矿产次数")
# 		self.number_input.Bind(wx.EVT_TEXT, self.on_text_change)
# 		vbox.Add(self.number_input, flag=wx.ALL, border=5)
#
# 		# 魔镜层数 ComboBox
# 		self.choiceMojing = wx.ComboBox(panel, size=(120, 30), choices=['迷幻境（虚实）', '狱境（黑白无常）', '炎冰境'])
# 		self.choiceMojing.SetHint("魔镜层数")
# 		vbox.Add(self.choiceMojing, flag=wx.ALL, border=5)
#
# 		# 整点 ComboBox
# 		self.choiceZhengdian = wx.ComboBox(panel, size=(120, 30), choices=['牛+虎+兔+猴+羊', '虎+猴+羊', '火焰+寒冰'])
# 		self.choiceZhengdian.SetHint("整点")
# 		vbox.Add(self.choiceZhengdian, flag=wx.ALL, border=5)
#
# 		# 多选框部分
# 		checkbox_sizer = wx.WrapSizer(wx.HORIZONTAL, wx.VERTICAL)
# 		self.check_boxes = []
# 		options = ["炼丹", "溶洞", "五行", "名将", "80精英", "云游精英", "100精英", "官渡精英"]
# 		for option in options:
# 			cb = wx.CheckBox(panel, label=option)
# 			cb.SetValue(True)  # 设置默认勾选状态
# 			checkbox_sizer.Add(cb, 0, flag=wx.LEFT | wx.RIGHT, border=2)
# 			self.check_boxes.append(cb)
#
# 		# 创建一个水平的BoxSizer来放置多选框
# 		hbox = wx.BoxSizer(wx.HORIZONTAL)
# 		hbox.Add(checkbox_sizer, flag=wx.ALL, border=5)
# 		vbox.Add(hbox, flag=wx.EXPAND | wx.ALL, border=5)
#
# 		# 确定按钮
# 		self.button = wx.Button(panel, label="确定")
# 		self.button.Disable()  # 初始化时禁用确定按钮
# 		self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
# 		vbox.Add(self.button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
#
# 		panel.SetSizer(vbox)
#
# 	def on_text_change(self, event):
# 		if self.team_leader_text.GetValue():
# 			self.button.Enable()
# 		else:
# 			self.button.Disable()
#
# 	def on_button_click(self, event):
# 		# 获取文本框中的值并保存在父窗口(MyFrame)中
# 		parent = self.GetParent()
# 		selected_options = []
# 		for cb in self.check_boxes:
# 			if cb.GetValue():
# 				selected_options.append(cb.GetLabel())
#
# 		parent.game_name = self.team_leader_text.GetValue()
# 		parent.heifengCount = self.number_input.GetValue() if self.number_input.GetValue() else 0
# 		parent.zhanhunFloor = self.choiceCeng.GetValue()
# 		parent.mojingFloor = self.choiceMojing.GetValue()
# 		parent.zhengdianFloor = self.choiceZhengdian.GetValue()
# 		parent.richangSelection = selected_options
#
# 		# 关闭对话框
# 		self.EndModal(wx.ID_OK)
#
#
# # 示例主窗口类
# class MyFrame(wx.Frame):
# 	def __init__(self, parent, title):
# 		super(MyFrame, self).__init__(parent, title=title, size=(300, 200))
#
# 		panel = wx.Panel(self)
#
# 		button = wx.Button(panel, label="打开对话框")
# 		button.Bind(wx.EVT_BUTTON, self.on_button_click)
#
# 		vbox = wx.BoxSizer(wx.VERTICAL)
# 		vbox.Add(button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
# 		panel.SetSizer(vbox)
#
# 		self.Show()
#
# 	def on_button_click(self, event):
# 		dialog = MyDialog(self)
# 		result = dialog.ShowModal()
# 		if result == wx.ID_OK:
# 			print(f"游戏名称: {self.game_name}")
# 			print(f"黑风/矿产次数: {self.heifengCount}")
# 			print(f"战魂层数: {self.zhanhunFloor}")
# 			print(f"魔镜层数: {self.mojingFloor}")
# 			print(f"整点: {self.zhengdianFloor}")
# 			print(f"日常选择: {self.richangSelection}")
# 		dialog.Destroy()
#
#
# if __name__ == '__main__':
# 	app = wx.App(False)
# 	frame = MyFrame(None, '示例窗口')
# 	app.MainLoop()
