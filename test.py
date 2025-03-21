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
# target_window_title = "Path of Exile"
# target_window_class = 'POEWindowClass'  # 如果不知道类名，可以设为 None
hwnd = dm.FindWindowEx(0, target_window_class, target_window_title)
# bind_result = dm.BindWindowEx(hwnd, "gdi", "windows3", "windows", '', 0)
# if bind_result == 1:
# 	print("窗口绑定成功")
# else:
# 	print("窗口绑定失败")
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
			if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
				print(left, top, right, bottom)
				click_hwnd = hwnd
				return False
		# if class_name == 'Chrome_RenderWidgetHostHWND':
		# 	click_hwnd = hwnd
		# 	return False
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
location = dm.GetClientSize(hwnd)
print(location)
x, y, res = location
print(x, y)
# dm.Capture(0, 0, x, y, 'srcc.bmp')
# image_list = "images/addBloud.png"  # 图像文件路径，多个图像用 | 分隔
# delta_color = "000000-605f60"  # 颜色容差
# # ab7b5c|ffffff右上角找图色偏差值

import subprocess

# def is_virtual_machine():
# 	try:
# 		# 执行 systeminfo 命令
# 		result = subprocess.check_output("systeminfo", shell=True, stderr=subprocess.DEVNULL)
# 		result = result.decode().lower()
#
# 		# 检查是否存在虚拟机相关的关键词
# 		virtual_machines = ['vmware', 'virtualbox', 'qemu', 'hyper-v']
# 		return any(vm in result for vm in virtual_machines)
# 	except Exception as e:
# 		return False
#
#
# if is_virtual_machine():
# 	print("当前设备是虚拟机")
# else:
# 	print("当前设备不是虚拟机")
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# import uuid
#
#
# def get_mac_address():
# 	return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])
#
#
# res121 = get_mac_address()
# print(res121)
longLocation = (0, 490, 320, 530)
similarity = 0.6  # 相似度阈值
dm_ret = dm.FindPicEx(0, 490, 320, 530, r"E:\project\python\serveAssets\images\fei3.bmp", "", similarity, 0)
# dm_ret1 = dm.FindPicEx(0, 0, x, y, r"E:\project\python\serveAssets\images\fei3.bmp", "", similarity, 0)
# # #
print(dm_ret, 'dm_ret')
# print(dm_ret1, 'dm_ret1')
# if not dm_ret:
# 	print('未找到'
# dm_ret = dm_ret.split(',')
# print(dm_ret)
# x, y = dm_ret[1], dm_ret[2]
# print(f'找到图像，坐标: ({x}, {y})')
# resmove = dm.MoveTo(int(int(x) + 100), int(int(y) + 20))
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
dict_id = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\common.txt")  # 字库文件路径
# dict_id1 = dm.SetDict(1, r"E:\project\python\serveAssets\fonts\team1.txt")  # 字库文件路径
# dict_id2 = dm.SetDict(2, r"E:\project\python\serveAssets\fonts\team2.txt")  # 字库文件路径
# dict_id2 = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\zhengdian.txt")  # 字库文件路径
# print(f'字库加载成功，{dict_id},{dict_id1},{dict_id2}')
# print(dm.GetDictCount(0), dm.GetDictCount(1), dm.GetDictCount(2))
# 文字识别参数
color_format = 'ffffff-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000'
# color_format = "ffffff-000000"  # 右上角偏移色
# color_format = 'ffffff-00000|00ff00-000000a'  # 绿色字体
# color_format = 'ffff00-000000'
sim = 0.9  # 相似度阈值，可以根据实际情况调整
# find_str_result = dm.FindStrFastEx(0, 0, x, y, '打就打', color_format, sim)
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

#
#
