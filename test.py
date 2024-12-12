import os
import ctypes
from comtypes.client import CreateObject
import comtypes.client
import subprocess
import time
import inspect

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
#
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
			if class_name == 'NativeWindowClass' and left > 0 and right < screen_width and bottom < screen_height:
				print(left, top, right, bottom)
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
dm_ret = dm.FindPicEx(0, 0, x, y, r"E:\project\python\serveAssets\images\richang\mingjiangliubei2.bmp", "", 0.9, 0)

if not dm_ret:
	print('未找到')
dm_ret = dm_ret.split('|')
print(dm_ret)
# x, y = dm_ret[1], dm_ret[2]
# print(f'找到图像，坐标: ({x}, {y})')
# resmove = dm.MoveTo(int(x), int(y))
# time.sleep(0.01)
# print(resmove)
# resclick = dm.LeftClick()
# print(resclick)

# print(x, y)
# # 加载字库
dict_id = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\guandu.txt")  # 字库文件路径
print(f'字库加载成功，{dict_id}')
#
# # 文字识别参数
color_format = 'ffffff-00000|00ff00-000000|ffff00-000000'
# # color_format = "ffffff-000000"  # 右上角偏移色
# # color_format = '00ff00'  #绿色字体
# # color_format = 'ffff00-000000'
sim = 0.9  # 相似度阈值，可以根据实际情况调整
# dm.KeyDownChar('left')
# time.sleep(5)
# dm.KeyUpChar('left')
#
# # 进行文字识别


# example_function()
# find_str_result = dm.FindStrFastE(0, 0, x, y, '张宝', color_format, sim)
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
