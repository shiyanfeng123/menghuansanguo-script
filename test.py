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
# dm_obj = ctypes.windll.LoadLibrary(r'D:\myproject\menghuansanguo-script-master\menghuansanguo-script\serveAssets\plugins\RegDll.dll')
# location_dmreg = r'D:\myproject\menghuansanguo-script-master\menghuansanguo-script\serveAssets\plugins\dm.dll'
# register_dll(location_dmreg)
# dm_obj.DllRegisterServer(location_dmreg, 0)
dm = CreateObject("dm.dmsoft")
print(dm.Ver())
time.sleep(10)
# 定义回调函数类型
ENUMWINDOWSPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
click_hwnd = 0


# 定义回调函数
def enum_child_windows_callback(hwnd, lParam):
    window_text = dm.GetWindowText(hwnd)
    class_name = dm.GetClassName(hwnd)
    print(f"子窗口句柄: {hwnd}, 标题: {window_text}, 类名: {class_name}")
    return True  # 返回 True 继续枚举


# 将回调函数转换为 ctypes 函数指针
enum_child_windows_callback_func = ENUMWINDOWSPROC(enum_child_windows_callback)

# 查找目标窗口句柄
target_window_title = "小号3"
target_window_class = "DUIWindow"  # 如果不知道类名，可以设为 None
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
    print("找到目标窗口")
    #
    # 使用 Windows API 的 EnumChildWindows
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    # 获取屏幕分辨率
    screen_width = user32.GetSystemMetrics(0)  # 0 表示屏幕宽度
    screen_height = user32.GetSystemMetrics(1)  # 1 表示屏幕高度

    def enum_child_proc(hwnd, lParam):
        global click_hwnd
        class_name = dm.GetWindowClass(hwnd)
        child_rect = dm.GetWindowRect(hwnd)
        if child_rect != 0:
            left, top, right, bottom, isFind = child_rect
            if class_name == "NativeWindowClass" and left > 0 and right < screen_width and bottom < screen_height:
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
bind_result = dm.BindWindowEx(click_hwnd, "gdi", "windows3", "windows", "", 0)
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
import requests
import json
import os
import hashlib
import zipfile
import sys
import shutil
from pathlib import Path


# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager


class UpdateVer:
    def get_current_version(self):
        """从本地文件读取当前版本"""
        try:
            with open("version.json") as f:
                return json.load(f)["version"]
        except:
            return "1.0.0"  # 默认版本

    def check_gitee_update(self):
        """检查Gitee上的版本信息"""
        try:
            url = "https://gitee.com/syf0910/mhsg-script-update/raw/master/version.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[错误] 检查更新失败: {e}")
            return None

    # def selenium_login(self, username, password):
    # 	# 1. 自动下载并初始化 WebDriver
    # 	# driver = webdriver.Chrome(ChromeDriverManager().install())
    # 	# # 2. 访问页面
    # 	# driver.get("https://gitee.com")
    #
    # 	chrome_options = Options()
    # 	chrome_options.add_argument("--start-maximized")  # 最大化窗口
    # 	chrome_options.add_argument("--headless")  # 无头模式
    # 	chrome_options.add_argument("--disable-gpu")
    # 	chrome_options.add_argument("--no-sandbox")
    # 	service = Service(ChromeDriverManager().install())
    # 	driver = webdriver.Chrome(service=service, options=chrome_options)
    # 	# driver = webdriver.Chrome(ChromeDriverManager().install())
    # 	driver.get("https://gitee.com/login")
    # 	csrf_token = driver.find_element(By.NAME, "authenticity_token").get_attribute("value")
    # 	driver.find_element(By.NAME, "login").send_keys(username)
    # 	driver.find_element(By.NAME, "password").send_keys(password)
    # 	driver.find_element(By.NAME, "commit").click()
    # 	# 获取浏览器 Cookie
    # 	cookies = driver.get_cookies()
    # 	driver.quit()
    # 	return {c["name"]: c["value"] for c in cookies}

    def download_update(self, url, save_path):
        """下载更新包"""
        session = requests.Session()
        # # 1. 模拟登录获取 Cookie
        # cookie = self.selenium_login('18175312372', 's1728349744')
        # print(cookie, 'cookie')
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        # ?access_token=91670e5d97cb3ae58aa652296bcf5c8b
        session.headers.update(headers)
        # session.cookies.update(cookie)
        try:
            response = session.get(f"{url}", stream=True)
            print(response.status_code, "response.status_code")
            print(response.raise_for_status(), "response.raise_for_status")
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"[错误] 下载失败: {e}")
            return False

    def verify_file(self, file_path, expected_hash):
        """校验文件完整性"""
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def apply_update(self, update_zip):
        """应用更新"""
        # 创建备份目录
        backup_dir = Path("backup")
        backup_dir.mkdir(exist_ok=True)

        # 备份当前文件（排除更新包和备份目录）
        for item in Path(".").iterdir():
            if item.name not in [update_zip, "backup"]:
                dest = backup_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        # 解压更新包
        with zipfile.ZipFile(update_zip, "r") as zip_ref:
            zip_ref.extractall(".")

        # 删除临时文件
        os.remove(update_zip)
        print("[成功] 更新已应用")

    def restart_application(self):
        """重启应用（需根据打包工具调整）"""
        if getattr(sys, "frozen", False):  # 如果是PyInstaller打包的EXE
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            print("请手动重启应用")

    def main(self):
        print("正在检查更新...")
        current_version = self.get_current_version()
        remote_info = self.check_gitee_update()

        if not remote_info:
            print("无法获取更新信息")
            return

        if remote_info["version"] == current_version:
            print(f"当前已是最新版本 ({current_version})")
            return

        print(f"发现新版本: {remote_info['version']}")
        print(f"更新内容: {remote_info['changelog']}")

        # 下载更新包
        update_file = f"脚本v25.6.0.exe"
        if not self.download_update(remote_info["download_url"], update_file):
            return
        # 校验文件
        file_hash = self.verify_file(update_file, remote_info["hash"])
        print(file_hash, "file_hash")
        print(remote_info["hash"], 'remote_info["hash"]')
        # if file_hash != remote_info["hash"]:
        # 	print("[错误] 文件校验失败！可能被篡改")
        # 	# os.remove(update_file)
        # 	return

        # 应用更新
        try:
            self.apply_update(update_file)
            print("更新成功，正在重启...")
            self.restart_application()
        except Exception as e:
            # print(f"[严重错误] 更新失败: {e}")
            # 自动回滚（可选）
            print("正在恢复备份...")
            shutil.copytree("backup", ".", dirs_exist_ok=True)


# if __name__ == "__main__":
# 	UpdateVer = UpdateVer()
# 	UpdateVer.main()
# import hashlib
#
# shutil.make_archive("v6.0.0", "zip", "dist_new")
#
# with open("v6.0.0.zip", "rb") as f:
# 	print(hashlib.sha256(f.read()).hexdigest())
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
import win32gui
import win32con
import win32api
import time

# send_f5(hwnd)
# dm.SetWindowState(hwnd, 1)
# time.sleep(0.5)
# # dm.KeyPressChar('F5')
# time.sleep(0.5)
#
# dm.KeyDown(17)  # Ctrl
# dm.KeyPress(82)  # R
# dm.KeyUp(17)
# dm.KeyPress(116)
# import uuid
#
#
# def get_mac_address():
# 	return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])
#
#
# res121 = get_mac_address()
# print(res121)
# longLocation = (0, 0, 900, 580)
similarity = 0.7  # 相似度阈值


# # dm.EnableDisplayDebug(1)
# dm_ret = dm.Capture(426, 305, 461, 337, 'name.bmp')
# dm_ret2 = dm.Capture(538, 305, 587, 335, 'name1.bmp')
# print(111)
# time.sleep(20)
def get_resource_path(self, relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# (85, 490, 141, 530)
# dm.Capture(85, 490, 141, 530, 'name111.bmp')
# print(time.time())
# dm.KeyDownChar('left')
# time.sleep(5)
# dm.KeyUpChar('left')
# dm.KeyDownChar('right')
# time.sleep(5)
dm_ret = dm.FindPicEx(0, 0, x, y,
                      r"E:\project\python\serveAssets\images/cangbaotu.bmp",
                      "", similarity, 0)
# dm_ret1 = dm.FindPicEx(420, 0, 465, 580, r"E:\project\python\name.bmp", "", similarity, 0)
# print(dm_ret1)
# dm_ret3 = dm.FindPicEx(530, 0, 589, 580, r"E:\project\python\name1.bmp", "", similarity, 0)
# # # #
# res111 = dm.GetNetTime()
# print('res111', res111)
# 249  342 391  352
# dm_ret = dm.FindColor(249, 340, 291, 352, "ffff00-000000", 0.9, 0)
def search_all_images(dm, region, similarity=0.6):
    base = r"E:\project\python\serveAssets\images\zhengdian"
    monsters = [
        ("虎", "hu"),
        ("牛", "niu"),
        ("兔", "tu"),
        ("猴", "hou"),
        ("羊", "yang"),
        ("火焰帝红", "huoyan"),
        ("寒冰帝", "hanbin"),
        ("蛇", "she"),
        ("龙", "long"),
    ]
    parts = ["head", "body", "foot"]
    left, top, right, bottom = region
    for name, code in monsters:
        found = []
        for part in parts:
            img1 = f"{base}/{code}-{part}-1.bmp"
            img2 = f"{base}/{code}-{part}-2.bmp"
            if not os.path.exists(img1) or not os.path.exists(img2):
                continue
            img_path = f"{img1}|{img2}"
            ret = dm.FindPicEx(left, top, right, bottom, img_path, "", similarity, 0)
            if ret:
                hits = {}
                for item in ret.split("|"):
                    idx = int(item.split(",")[0])
                    label = f"{part}-1" if idx == 0 else f"{part}-2"
                    hits[label] = hits.get(label, 0) + 1
                found.extend(hits.keys())
        if found:
            print(f"[{name}] 找到: {', '.join(found)}")
        else:
            print(f"[{name}] 未找到")


print(dm_ret, 'dm_ret')
# search_all_images(dm, (0, 0, x, y), similarity)
# x, y, r = dm_ret
# print(x, y, r)
# if r == 1:
# 	print('找到了')
# print(dm_ret1, dm_ret3, 'dm_ret1')
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
import wx
import webbrowser
from urllib.request import urlopen
from datetime import datetime
import re


def get_network_hour():
    try:
        # 访问国家授时中心（返回文本时间）
        with urlopen("http://www.ntsc.ac.cn") as response:
            html = response.read().decode("utf-8")

        # 使用正则提取时间（格式：2023-05-15 12:34:56）
        time_str = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", html).group()

        # 转换为小时数
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").hour
    except Exception as e:
        print(f"获取网络时间失败: {e}")
        return None


# 使用示例
# hour = get_network_hour()
# if hour is not None:
# 	print(f"当前网络时间的小时数: {hour}")
import requests
from datetime import datetime


def get_network_hour():
    try:
        # 使用公共时间API（返回JSON格式数据）
        response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Shanghai")
        data = response.json()

        # 解析时间字符串（格式：2023-05-15T12:34:56.789+08:00）
        datetime_str = data["datetime"]
        current_time = datetime.fromisoformat(datetime_str)

        return current_time.hour
    except Exception as e:
        print(f"获取网络时间失败: {e}")
        return None


# 使用示例
# hour = get_network_hour()
# if hour is not None:
# 	print(f"当前网络时间的小时数: {hour}")


class VersionInfo:
    def __init__(self, version, description, download_url):
        self.version = version
        self.description = description
        self.download_url = download_url


class VersionDisplayFrame(wx.Frame):
    def __init__(self, parent, title):
        super(VersionDisplayFrame, self).__init__(parent, title=title, size=(600, 400))

        # 创建示例数据
        self.version_list = [
            VersionInfo(
                "v2.3.0",
                "1. 新增暗黑模式支持\n2. 优化性能提升30%\n3. 修复文件保存问题",
                "https://example.com/download/v2.3.0",
            ),
            VersionInfo(
                "v2.2.1",
                "1. 修复登录验证漏洞\n2. 改进用户界面体验\n3. 增加多语言支持",
                "https://example.com/download/v2.2.1",
            ),
            VersionInfo(
                "v2.1.5",
                "1. 首次公开版本发布\n2. 包含基本功能模块\n3. 已知问题修复列表",
                "https://example.com/download/v2.1.5",
            ),
            VersionInfo(
                "v2.0.0", "1. 完全重构代码库\n2. 新增插件系统\n3. 支持云同步功能", "https://example.com/download/v2.0.0"
            ),
            VersionInfo(
                "v1.5.2",
                "1. 修复内存泄漏问题\n2. 增加快捷键设置\n3. 优化启动速度",
                "https://example.com/download/v1.5.2",
            ),
            VersionInfo(
                "v1.4.0",
                "1. 添加自动更新功能\n2. 改进文档编辑器\n3. 新增主题切换",
                "https://example.com/download/v1.4.0",
            ),
            VersionInfo(
                "v1.3.1", "1. 修复数据导出问题\n2. 增强安全防护\n3. 优化资源占用", "https://example.com/download/v1.3.1"
            ),
        ]

        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        # 创建可滚动窗口
        scrolled_win = wx.ScrolledWindow(self)
        scrolled_win.SetScrollRate(10, 10)  # 设置滚动步长

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 添加标题
        title = wx.StaticText(scrolled_win, label="软件版本历史")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        main_sizer.Add(wx.StaticLine(scrolled_win), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # 遍历版本列表并创建显示项
        for idx, version_info in enumerate(self.version_list):
            version_sizer = self.create_version_item(scrolled_win, version_info)
            main_sizer.Add(version_sizer, 0, wx.EXPAND | wx.ALL, 15)

            # 在版本之间添加分隔线（最后一个版本不添加）
            if idx < len(self.version_list) - 1:
                main_sizer.Add(wx.StaticLine(scrolled_win), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)

        scrolled_win.SetSizer(main_sizer)

        # 计算内容所需高度并设置虚拟大小
        scrolled_win.FitInside()

        # 添加底部提示
        # bottom_text = wx.StaticText(self, label="↑ 滚动查看历史版本 ↑")
        # bottom_text.SetForegroundColour(wx.Colour(100, 100, 100))
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # bottom_sizer.Add(bottom_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        # 主框架布局
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(scrolled_win, 1, wx.EXPAND)
        frame_sizer.Add(bottom_sizer, 0, wx.ALIGN_CENTER)

        self.SetSizer(frame_sizer)

    def create_version_item(self, parent, version_info):
        # 主容器
        container = wx.BoxSizer(wx.VERTICAL)

        # 第一行：版本号 + 下载链接
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 版本号（大字体加粗）
        version_text = wx.StaticText(parent, label=version_info.version)
        version_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        version_text.SetFont(version_font)
        header_sizer.Add(version_text, 1, wx.ALIGN_CENTER_VERTICAL)

        # 添加伸缩空间使下载按钮靠右
        header_sizer.AddStretchSpacer(1)

        # 下载链接按钮
        download_btn = wx.Button(parent, label="下载", size=(80, 30))
        download_btn.Bind(wx.EVT_BUTTON, lambda e, url=version_info.download_url: webbrowser.open(url))
        header_sizer.Add(download_btn, 0, wx.LEFT, 10)

        container.Add(header_sizer, 0, wx.EXPAND | wx.BOTTOM, 5)

        # 版本说明（禁用文本框）
        desc_text = wx.TextCtrl(
            parent, value=version_info.description, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN
        )
        desc_text.SetBackgroundColour(wx.Colour(240, 240, 240))  # 设置禁用状态背景色
        desc_text.SetMinSize((-1, 80))  # 设置最小高度

        container.Add(desc_text, 1, wx.EXPAND | wx.TOP, 5)

        return container


# if __name__ == "__main__":
# 	app = wx.App()
# 	VersionDisplayFrame(None, "软件版本历史")
# 	app.MainLoop()
# 释放内存
# dm.FreeMem(memory_address)
dict_id = dm.SetDict(0, r"E:\project\python\serveAssets\fonts\common.txt")  # 字库文件路径
dict_id1 = dm.SetDict(1, r"E:\project\python\serveAssets\fonts\team1.txt")  # 字库文件路径
dict_id2 = dm.SetDict(2, r"E:\project\python\serveAssets\fonts\team2.txt")  # 字库文件路径
# dict_id2 = dm.SetDict(0, r"D:\myproject\menghuansanguo-script-master\menghuansanguo-script\serveAssets\fonts\zhengdian.txt")  # 字库文件路径
print(f"字库加载成功，{dict_id},{dict_id1},{dict_id2}")
# print(dm.GetDictCount(0), dm.GetDictCount(1), dm.GetDictCount(2))
# 文字识别参数
color_format = '0ff000-000000|ffffff-00000|ffcc00-00000|00ff00-000000|ffff00-000000|0ff000-000000|ff0000-000000|fff200-000000|00ffff-000000'
# color_format = "b@ffff00-000000|fff200-000000" # 右上角偏移色
# color_format = 'ffffff-00000|00ff00-000000a'  # 绿色字体
print(dm.GetColor(854,334))
# color_format = "ffff00-000000|fff200-000000|f4f400-000000"
# 切换到目标窗口
# dm.SetWindowState(hwnd, 1)  # 激活窗口
# dm.MoveTo(1000, 500)
# time.sleep(1000)
# 发送F5
# dm.KeyPressChar('F5')
sim = 0.9  # 相似度阈值，可以根据实际情况调整
# long = dm.FindMultiColor(0, 300, 340, 580, "0ff000-0ff000",
#                          "6|8|0ff000-0ff000,3|9|0ff000-0ff000,-2|6|0ff000-0ff000,2|2|0ff000-0ff000,2|8|0ff000-0ff000,6|7|0ff000-0ff000,5|1|0ff000-0ff000,-1|4|0ff000-0ff000,-3|8|0ff000-0ff000,-3|1|0ff000-0ff000,1|1|0ff000-0ff000,6|9|0ff000-0ff000,2|3|0ff000-0ff000,2|6|0ff000-0ff000,3|6|0ff000-0ff000",
#                          0.9, 0)
# print(long, 'long')
# yang = dm.FindMultiColor(0, 300, 340, 580, "000000-0ff000",
#                          '4|5|0ff000-0ff000,10|1|83a451-0ff000,10|5|000000-0ff000,9|6|000000-0ff000,8|2|000000-0ff000,5|5|000000-0ff000,2|0|0ff000-0ff000,9|7|0ff000-0ff000,10|2|83a451-0ff000,2|4|0ff000-0ff000,1|8|000000-0ff000,5|7|0ff000-0ff000,9|8|000000-0ff000,10|8|000000-0ff000,5|1|0ff000-0ff000,7|4|0ff000-0ff000,0|5|000000-0ff000,6|4|0ff000-0ff000,0|8|000000-0ff000',
#                          0.9, 0)
# print(yang, 'yang')
# niu = dm.FindMultiColor(0, 300, 340, 580, "000000-0ff000",
#                         '9|7|0ff000-0ff000,8|2|000000-0ff000,4|3|0ff000-0ff000,9|4|000000-0ff000,10|8|000000-0ff000,6|0|617557-0ff000,6|5|656d53-0ff000,9|6|000000-0ff000,1|4|000000-0ff000,9|8|000000-0ff000,2|8|000000-0ff000,2|6|000000-0ff000,3|2|000000-0ff000,8|7|0ff000-0ff000,2|3|0ff000-0ff000,8|8|000000-0ff000,7|2|000000-0ff000,3|4|000000-0ff000,9|0|637356-0ff000',
#                         0.9, 0)
# print(niu, 'niu')
# dm_ret = dm.FindColor(249, 340, 291, 352, "ffff00-000000", 0.7, 0)
# x, y, r = dm_ret
# print(dm_ret)

# dm.CapturePng(0, 0, x, y, f"wait_for_more_than_22_seconds.png") 534 368
# find_str_result = dm.FindStrFastE(0, 0, x, y, "神龙守护者", color_format, sim)
# print(f"FindStrFast 返回结果: {find_str_result}")
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
# import requests
# from bs4 import BeautifulSoup
# import json
#
#
# def get_gitee_cookies_api(username, password):
# 	# 创建会话
# 	session = requests.Session()
#
# 	# 获取登录页面获取 authenticity_token
# 	login_url = "https://gitee.com/login"
# 	headers = {
# 		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# 	}
#
# 	try:
# 		# 第一次请求获取 authenticity_token
# 		response = session.get(login_url, headers=headers)
# 		response.raise_for_status()
#
# 		# 解析 authenticity_token
# 		soup = BeautifulSoup(response.text, 'html.parser')
# 		auth_token = soup.find('input', {'name': 'authenticity_token'}).get('value')
#
# 		# 准备登录数据
# 		login_data = {
# 			'utf8': '✓',
# 			'authenticity_token': auth_token,
# 			'user[login]': username,
# 			'user[password]': password,
# 			'user[remember_me]': '0'
# 		}
#
# 		# 提交登录请求
# 		post_url = "https://gitee.com/login"
# 		response = session.post(post_url, data=login_data, headers=headers)
# 		response.raise_for_status()
#
# 		# 检查登录是否成功
# 		if "我的工作台" in response.text:
# 			# 获取 Cookie
# 			cookies = session.cookies.get_dict()
#
# 			# 保存 Cookie
# 			with open("gitee_cookies.json", "w") as f:
# 				json.dump(cookies, f)
#
# 			print("登录成功！Cookie 已保存")
# 			return cookies
# 		else:
# 			print("登录失败，请检查用户名和密码")
# 			return None
#
# 	except Exception as e:
# 		print(f"请求失败: {str(e)}")
# 		return None
#
#
# # 使用示例
# if __name__ == "__main__":
# 	# 替换为你的 Gitee 账号
# 	username = "18175312372"
# 	password = "s1728349744"
#
# 	cookies = get_gitee_cookies_api(username, password)
#
# 	if cookies:
# 		print("获取到的 Cookie:")
# 		for name, value in cookies.items():
# 			print(f"{name}: {value}")
