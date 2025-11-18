"""
网页资源下载器
功能：从网页中提取所有图片和视频资源，并提供下载功能
"""

import wx
import wx.lib.scrolledpanel as scrolled
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re
import threading
import time
from pathlib import Path
import io
import tempfile

# 尝试导入PIL（用于图片处理）
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 尝试导入Selenium（可选）
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 尝试导入Chrome DevTools Protocol相关模块
try:
    import json
    DEVTOOLS_AVAILABLE = True
except ImportError:
    DEVTOOLS_AVAILABLE = False


class ResourceDownloader(wx.Frame):
    """网页资源下载器主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="网页资源下载器",
            size=(1000, 700),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        self.SetBackgroundColour(wx.Colour(240, 245, 255))
        
        # 创建主面板
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域
        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(wx.Colour(64, 158, 255))
        title_panel.SetMinSize((-1, 80))
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title = wx.StaticText(title_panel, label="🌐 网页资源下载器")
        title_font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        subtitle = wx.StaticText(title_panel, label="提取网页中的图片和视频资源")
        subtitle_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(wx.Colour(240, 248, 255))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        title_sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        title_panel.SetSizer(title_sizer)
        main_sizer.Add(title_panel, 0, wx.EXPAND)
        
        # 输入区域
        input_panel = wx.Panel(panel)
        input_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 第一行：URL输入
        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        url_label = wx.StaticText(input_panel, label="网址：")
        url_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                 wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        url_label.SetMinSize((60, -1))
        
        self.url_input = wx.TextCtrl(input_panel, value="", style=wx.TE_PROCESS_ENTER)
        self.url_input.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                      wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.url_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.url_input.Bind(wx.EVT_TEXT, self.on_url_changed)
        self.url_input.Bind(wx.EVT_TEXT_ENTER, self.on_confirm)
        
        self.confirm_btn = wx.Button(input_panel, label="确认", size=(100, 35))
        self.confirm_btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.confirm_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        self.confirm_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.confirm_btn.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.confirm_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: self.confirm_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        self.confirm_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self.confirm_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        self.confirm_btn.Enable(False)
        
        url_sizer.Add(url_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        url_sizer.Add(self.url_input, 1, wx.EXPAND | wx.ALL, 10)
        url_sizer.Add(self.confirm_btn, 0, wx.ALL, 10)
        
        # 第二行：选项
        option_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.use_selenium_check = wx.CheckBox(input_panel, label="使用浏览器渲染（处理JavaScript动态内容）")
        self.use_selenium_check.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                                wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        if not SELENIUM_AVAILABLE:
            self.use_selenium_check.Enable(False)
            self.use_selenium_check.SetLabel("使用浏览器渲染（需要安装selenium: pip install selenium）")
            self.use_selenium_check.SetForegroundColour(wx.Colour(150, 150, 150))
        option_sizer.Add(self.use_selenium_check, 0, wx.ALL, 5)
        
        # 保存登录状态选项
        self.save_login_check = wx.CheckBox(input_panel, label="保存登录状态（避免每次登录）")
        self.save_login_check.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                              wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.save_login_check.SetValue(True)  # 默认启用
        if not SELENIUM_AVAILABLE:
            self.save_login_check.Enable(False)
        option_sizer.Add(self.save_login_check, 0, wx.ALL, 5)
        
        option_sizer.AddStretchSpacer()
        
        input_sizer.Add(url_sizer, 0, wx.EXPAND)
        input_sizer.Add(option_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        input_panel.SetSizer(input_sizer)
        main_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # 状态栏
        self.status_text = wx.StaticText(panel, label="请输入网址并点击确认")
        self.status_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.status_text.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(self.status_text, 0, wx.ALL, 5)
        
        # 资源列表区域
        list_panel = wx.Panel(panel)
        list_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        list_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 列表标题和批量下载按钮
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        list_title = wx.StaticText(list_panel, label="资源列表")
        list_title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        list_title.SetForegroundColour(wx.Colour(48, 49, 51))
        title_sizer.Add(list_title, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        # 批量下载按钮
        self.batch_download_btn = wx.Button(list_panel, label="批量下载", size=(100, 35))
        self.batch_download_btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                               wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.batch_download_btn.SetBackgroundColour(wx.Colour(103, 194, 58))
        self.batch_download_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.batch_download_btn.Bind(wx.EVT_BUTTON, self.on_batch_download)
        self.batch_download_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: self.batch_download_btn.SetBackgroundColour(wx.Colour(124, 214, 78)))
        self.batch_download_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self.batch_download_btn.SetBackgroundColour(wx.Colour(103, 194, 58)))
        self.batch_download_btn.Enable(False)  # 初始状态禁用
        title_sizer.AddStretchSpacer()
        title_sizer.Add(self.batch_download_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        list_sizer.Add(title_sizer, 0, wx.EXPAND)
        
        # 创建滚动面板（设置最小尺寸，确保可以滚动）
        scroll_panel = scrolled.ScrolledPanel(list_panel)
        scroll_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        scroll_panel.SetMinSize((-1, 400))  # 设置最小高度，确保有滚动空间
        scroll_panel.SetAutoLayout(True)
        
        self.resource_sizer = wx.BoxSizer(wx.VERTICAL)
        scroll_panel.SetSizer(self.resource_sizer)
        
        # 设置滚动参数（启用双向滚动，设置滚动速度）
        scroll_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20)
        
        list_sizer.Add(scroll_panel, 1, wx.EXPAND | wx.ALL, 5)
        list_panel.SetSizer(list_sizer)
        main_sizer.Add(list_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 资源列表
        self.resources = []
        self.scroll_panel = scroll_panel
        
        # 缩略图缓存
        self.thumbnail_cache = {}  # {url: wx.Bitmap}
        self.temp_files = []  # 临时文件列表，用于清理
        
        # 复选框字典，用于跟踪每个资源的选中状态
        self.checkboxes = {}  # {resource_index: checkbox}
        
        # 用户数据目录和Cookie保存路径
        self.user_data_dir = os.path.join(os.path.expanduser('~'), '.web_resource_downloader', 'chrome_user_data')
        self.cookie_file = os.path.join(os.path.expanduser('~'), '.web_resource_downloader', 'cookies.json')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.user_data_dir), exist_ok=True)
        os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
        
    def on_url_changed(self, event):
        """URL输入框内容改变事件"""
        url = self.url_input.GetValue().strip()
        is_valid = self.is_valid_url(url)
        self.confirm_btn.Enable(is_valid)
        
    def _clean_url(self, url):
        """
        清理URL，移除错误的转义字符和特殊字符
        【关键改进】统一解码所有URL编码，确保URL比较时使用相同的格式
        """
        if not url:
            return None
        
        # 移除错误的转义字符（如 %5C%5C%5C）
        import urllib.parse
        try:
            # 【关键】先完全解码URL（包括多次编码的情况）
            decoded = urllib.parse.unquote(url)
            # 如果还有编码，继续解码（处理多次编码的情况）
            while '%' in decoded and decoded != urllib.parse.unquote(decoded):
                decoded = urllib.parse.unquote(decoded)
            
            # 移除Windows路径分隔符（反斜杠）和其他非法字符
            decoded = decoded.replace('\\', '/')
            decoded = decoded.replace('\n', '').replace('\r', '').replace('\t', '')
            
            # 【关键改进】对于imgextra路径的图片，保留原始URL格式（不重新编码）
            # 因为淘宝的图片URL中可能包含特殊字符（如!!），需要保持原样
            if 'imgextra' in decoded.lower():
                # 只清理明显的错误字符，保留URL的原始格式
                return decoded.strip()
            
            # 对于其他URL，重新编码URL路径部分
            parsed = urllib.parse.urlparse(decoded)
            # 只编码路径部分，保留查询参数和片段
            clean_path = urllib.parse.quote(parsed.path, safe='/')
            clean_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                clean_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return clean_url
        except:
            # 如果解析失败，至少移除明显的错误字符
            url = url.replace('%5C', '').replace('\\', '/')
            # 尝试解码
            try:
                import urllib.parse
                url = urllib.parse.unquote(url)
            except:
                pass
            return url.strip()
    
    def is_valid_url(self, url):
        """验证URL是否有效"""
        if not url:
            return False
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def is_accessible_resource(self, url):
        """验证资源是否可以访问（快速检查，避免添加无法加载的资源）"""
        if not url or not url.startswith('http'):
            return False
        
        # 排除明显无效的URL模式
        url_lower = url.lower()
        invalid_patterns = [
            # 排除统计/日志URL（通常返回1x1像素的gif）
            '/v.gif', '/m.gif', '/1.gif', '/log.gif', '/track.gif',
            # 排除明显的非资源URL
            '/api/', '/ajax/', '/service/', '/script/',
            # 排除item.taobao.com根路径下的简单文件名（通常是无效的）
            'item.taobao.com/v.', 'item.taobao.com/m.', 'item.taobao.com/1.',
            # 排除mmstat.com的统计URL
            'mmstat.com', 'arms.', 'statistics'
        ]
        
        # 检查是否匹配无效模式
        for pattern in invalid_patterns:
            if pattern in url_lower:
                return False
        
        # 检查URL路径是否太短（可能是无效URL）
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        # 如果路径只有1-2个字符，可能是无效URL（如 /v, /m, /1）
        if len(path) <= 2 and not path.startswith('i') and not path.startswith('O'):
            return False
        
        return True
    
    def on_confirm(self, event):
        """确认按钮点击事件"""
        url = self.url_input.GetValue().strip()
        if not self.is_valid_url(url):
            wx.MessageBox("请输入有效的网址！", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        # 禁用按钮，显示加载状态
        self.confirm_btn.Enable(False)
        self.status_text.SetLabel("正在解析网页，请稍候...")
        self.status_text.SetForegroundColour(wx.Colour(64, 158, 255))
        
        # 在新线程中执行网页解析
        thread = threading.Thread(target=self.fetch_resources, args=(url,))
        thread.daemon = True
        thread.start()
    
    def fetch_resources(self, url):
        """获取网页资源（在线程中执行）"""
        use_selenium = self.use_selenium_check.GetValue() if SELENIUM_AVAILABLE else False
        html_content = None
        
        try:
            if use_selenium:
                # 使用Selenium获取渲染后的HTML（同时监听网络请求）
                wx.CallAfter(self.status_text.SetLabel, "正在使用浏览器渲染页面并监听网络请求，请稍候...")
                html_content = self.fetch_with_selenium(url)
                if not html_content:
                    wx.CallAfter(self.show_error, "浏览器渲染失败，请检查Chrome浏览器和ChromeDriver是否正确安装")
                    return
            else:
                # 使用requests获取HTML
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                response.raise_for_status()
                
                # 尝试多种编码方式
                if response.encoding:
                    response.encoding = response.apparent_encoding or response.encoding
                
                html_content = response.text
            
            if not html_content:
                wx.CallAfter(self.show_error, "无法获取网页内容")
                return
            
            # 调试信息：显示HTML内容长度和前500字符
            html_preview = html_content[:500].replace('\n', ' ').replace('\r', ' ')
            print(f"获取到的HTML长度: {len(html_content)} 字符")
            print(f"HTML预览: {html_preview}...")
            
            # 检测是否是JavaScript动态加载的页面
            is_js_page = False
            script_count = html_content.lower().count('<script')
            if script_count > 5 or 'document.write' in html_content.lower() or 'innerHTML' in html_content.lower():
                # 检查是否有大量script标签但很少的img标签
                temp_soup = BeautifulSoup(html_content, 'html.parser')
                temp_imgs = temp_soup.find_all('img')
                if script_count > len(temp_imgs) * 2 and len(temp_imgs) < 3:
                    is_js_page = True
                    print(f"检测到JavaScript动态加载页面（{script_count}个script标签，{len(temp_imgs)}个img标签）")
            
            # 解析HTML - 尝试使用lxml，如果失败则使用html.parser
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # 清空现有资源（如果使用Selenium，网络资源已经添加，不清空）
            if not use_selenium:
                self.resources = []
            found_urls = set()  # 用于去重
            # 如果使用Selenium，网络资源已经添加，将现有URL添加到found_urls中
            if use_selenium:
                found_urls.update({r['url'] for r in self.resources})
            
            # 特殊处理：淘宝商品页面（仅在不使用Selenium时，因为Selenium已经处理了）
            if not use_selenium and ('taobao.com' in url or 'tmall.com' in url):
                self.extract_taobao_resources(soup, url, found_urls)
            
            # 查找所有图片（改进：查找所有img标签，不管有没有src）
            images = soup.find_all('img')
            img_count = 0
            
            # 如果检测到JS页面但没找到图片，且没有使用Selenium，提示用户
            if is_js_page and len(images) == 0 and not use_selenium:
                wx.CallAfter(self.show_js_warning, url)
                return
            
            for img in images:
                # 尝试多种可能的属性
                img_url = None
                for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-srcset', 
                            'data-url', 'data-img', 'data-image', 'srcset', 'data-webp', 'webp']:
                    img_url = img.get(attr)
                    if img_url:
                        # 处理srcset格式：可能包含多个URL（包括webp）
                        if attr == 'srcset' or attr == 'data-srcset':
                            # srcset格式：url1 1x, url2 2x 或 url1 100w, url2 200w
                            # 提取所有URL（包括webp格式）
                            urls = re.findall(r'([^\s,]+)', img_url)
                            if urls:
                                # 处理srcset中的所有URL（包括webp）
                                for url_item in urls:
                                    url_item = url_item.strip()
                                    if url_item and not url_item.startswith('data:'):
                                        full_url_item = urljoin(url, url_item)
                                        # 排除明显的非媒体文件
                                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                                        path_item = urlparse(full_url_item).path.lower()
                                        if any(path_item.endswith(ext) for ext in excluded_exts):
                                            continue
                                        if full_url_item not in found_urls:
                                            # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                            if not self.is_accessible_resource(full_url_item):
                                                continue  # 跳过无法访问的资源
                                            
                                            found_urls.add(full_url_item)
                                            name = img.get('alt') or img.get('title') or os.path.basename(urlparse(full_url_item).path) or f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                            self.resources.append({
                                                'name': name,
                                                'url': full_url_item,
                                                'type': 'image'
                                            })
                                            img_count += 1
                                # srcset处理完后，继续处理其他属性
                                img_url = urls[0] if urls else None
                            else:
                                img_url = None
                        
                        if img_url and img_url.strip():
                            break
                
                if img_url:
                    # 清理URL（移除查询参数中的尺寸等）
                    img_url = img_url.split('?')[0].split('#')[0].strip()
                    
                    # 处理base64图片
                    if img_url.startswith('data:image/'):
                        self._process_base64_image(img_url, found_urls)
                        continue
                    # 跳过javascript和其他非图片的data URL
                    if img_url.startswith('data:') or img_url.startswith('javascript:'):
                        continue
                    
                    # 转换为绝对URL
                    full_url = urljoin(url, img_url)
                    
                    # 排除明显的非媒体文件（只排除.js, .css, .html等）
                    excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                    path = urlparse(full_url).path.lower()
                    # 只在路径中检查，不在查询参数中
                    if any(path.endswith(ext) for ext in excluded_exts):
                        continue
                    
                    # 如果是img标签，直接添加（不做过多的验证，让图片加载时自然处理）
                    # img标签中的src属性通常就是图片资源
                    
                    # 去重
                    if full_url in found_urls:
                        continue
                    found_urls.add(full_url)
                    
                    # 获取名称
                    name = img.get('alt') or img.get('title') or ''
                    if not name:
                        name = os.path.basename(urlparse(full_url).path)
                    if not name or name == '':
                        name = f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                    
                    # 清理名称
                    name = re.sub(r'[<>:"/\\|?*]', '_', name)
                    
                    # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                    if not self.is_accessible_resource(full_url):
                        continue  # 跳过无法访问的资源
                    
                    self.resources.append({
                        'name': name,
                        'url': full_url,
                        'type': 'image'
                    })
                    img_count += 1
            
            # 查找所有视频
            videos = soup.find_all('video')
            for video in videos:
                video_url = video.get('src')
                if not video_url:
                    # 查找source子标签
                    source = video.find('source')
                    if source:
                        video_url = source.get('src')
                
                if video_url:
                    full_url = urljoin(url, video_url)
                    if full_url in found_urls:
                        continue
                    found_urls.add(full_url)
                    
                    name = video.get('title') or video.get('alt') or ''
                    if not name:
                        name = os.path.basename(urlparse(full_url).path)
                    if not name:
                        name = f"视频_{len([r for r in self.resources if r['type'] == 'video']) + 1}"
                    
                    name = re.sub(r'[<>:"/\\|?*]', '_', name)
                    
                    self.resources.append({
                        'name': name,
                        'url': full_url,
                        'type': 'video'
                    })
            
            # 查找source标签中的视频
            sources = soup.find_all('source')
            for source in sources:
                video_url = source.get('src')
                if video_url:
                    # 检查是否是视频类型
                    src_type = source.get('type', '').lower()
                    if 'video' in src_type or any(video_url.lower().endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv']):
                        full_url = urljoin(url, video_url)
                        if full_url in found_urls:
                            continue
                        found_urls.add(full_url)
                        
                        name = source.get('title') or ''
                        if not name:
                            name = os.path.basename(urlparse(full_url).path)
                        if not name:
                            name = f"视频_{len([r for r in self.resources if r['type'] == 'video']) + 1}"
                        
                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                        
                        self.resources.append({
                            'name': name,
                            'url': full_url,
                            'type': 'video'
                        })
            
            # 查找iframe中的视频（YouTube等）
            iframes = soup.find_all('iframe', src=True)
            for iframe in iframes:
                iframe_src = iframe.get('src')
                if iframe_src and ('youtube' in iframe_src.lower() or 'vimeo' in iframe_src.lower() or 'bilibili' in iframe_src.lower()):
                    if iframe_src in found_urls:
                        continue
                    found_urls.add(iframe_src)
                    
                    name = iframe.get('title') or '嵌入视频'
                    self.resources.append({
                        'name': name,
                        'url': iframe_src,
                        'type': 'video'
                    })
            
            # 查找CSS背景图片（通过style属性）
            elements_with_bg = soup.find_all(style=True)
            for elem in elements_with_bg:
                style = elem.get('style', '')
                # 查找background-image: url(...)
                bg_images = re.findall(r'background-image\s*:\s*url\(["\']?([^"\'()]+)["\']?\)', style, re.IGNORECASE)
                for bg_url in bg_images:
                    bg_url = bg_url.strip()
                    if bg_url and not bg_url.startswith('data:'):
                        full_url = urljoin(url, bg_url)
                        # 排除明显的非媒体文件
                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                        path = urlparse(full_url).path.lower()
                        if any(path.endswith(ext) for ext in excluded_exts):
                            continue
                        if full_url in found_urls:
                            continue
                        found_urls.add(full_url)
                        
                        name = elem.get('alt') or elem.get('title') or os.path.basename(urlparse(full_url).path) or f"背景图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                        
                        self.resources.append({
                            'name': name,
                            'url': full_url,
                            'type': 'image'
                        })
            
            # 从HTML文本中直接提取所有图片URL（更全面的方法）
            html_text = str(soup)
            # 匹配所有可能的图片URL格式（包括webp）
            # 匹配模式：http://xxx.jpg, https://xxx.png, //xxx.webp等
            img_url_patterns = [
                r'https?://[^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg)(\?[^\s<>"\'\)]*)?',
                r'//[^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg)(\?[^\s<>"\'\)]*)?',
                r'["\']([^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg))(\?[^\s<>"\'\)]*)?["\']',
            ]
            
            for pattern in img_url_patterns:
                matches = re.finditer(pattern, html_text, re.IGNORECASE)
                for match in matches:
                    img_url = match.group(0)
                    # 清理引号
                    img_url = img_url.strip('"\'')
                    # 如果是相对URL，转换为绝对URL
                    if img_url.startswith('//'):
                        img_url = urlparse(url).scheme + ':' + img_url
                    elif not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    
                    # 清理URL（移除查询参数中的尺寸等，但保留基本URL）
                    clean_url = img_url.split('?')[0].split('#')[0].strip()
                    
                    # 排除明显的非媒体文件
                    excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                    path = urlparse(clean_url).path.lower()
                    if any(path.endswith(ext) for ext in excluded_exts):
                        continue
                    
                    # 处理base64图片
                    if clean_url.startswith('data:image/'):
                        self._process_base64_image(clean_url, found_urls)
                        continue
                    # 跳过其他非图片的data URL和javascript
                    if clean_url.startswith('data:') or clean_url.startswith('javascript:'):
                        continue
                    
                    # 验证是否是图片URL（检查扩展名）
                    if not self._is_image_url(clean_url):
                        continue
                    
                    # 去重
                    if clean_url in found_urls:
                        continue
                    found_urls.add(clean_url)
                    
                    # 获取名称
                    name = os.path.basename(urlparse(clean_url).path) or f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                    if not name or name == '':
                        name = f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                    name = re.sub(r'[<>:"/\\|?*]', '_', name)
                    
                    self.resources.append({
                        'name': name,
                        'url': clean_url,
                        'type': 'image'
                    })
                    img_count += 1
            
            # 在主线程中更新UI
            wx.CallAfter(self.update_resource_list, img_count, len(images), len(html_content))
            
        except requests.exceptions.RequestException as e:
            wx.CallAfter(self.show_error, f"网络错误：{str(e)}")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"错误详情: {error_detail}")
            wx.CallAfter(self.show_error, f"解析错误：{str(e)}")
    
    def extract_taobao_resources(self, soup, url, found_urls):
        """提取淘宝商品页面的图片资源"""
        try:
            html_text = str(soup)
            seen_urls = set()
            
            # 方法1: 直接从HTML文本中提取所有淘宝图片和视频URL（更全面的正则表达式）
            # 匹配模式：https://xxx.alicdn.com/xxx.jpg 或 https://xxx.taobaocdn.com/xxx.webp等
            # 支持更多格式和URL模式
            patterns = [
                # 淘宝CDN域名
                r'https?://[^"\s<>]*\.(alicdn|taobaocdn|tbcdn)\.(com|cn)[^"\s<>]*\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|mp4|webm|avi|mov|flv|mkv|JPG|JPEG|PNG|GIF|WEBP|BMP|ICO|SVG|MP4|WEBM|AVI|MOV|FLV|MKV)(\?[^"\s<>]*)?',
                # 通用图片URL（包含常见图片扩展名）
                r'https?://[^"\s<>]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg)(\?[^"\s<>]*)?',
                # 带引号的图片URL
                r'["\']([^"\']+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg))(\?[^"\']*)?["\']',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, html_text, re.IGNORECASE)
                for match in matches:
                    img_url = match.group(0)
                    # 清理引号
                    img_url = img_url.strip('"\'')
                    
                    # 如果是相对URL，转换为绝对URL
                    if img_url.startswith('//'):
                        img_url = urlparse(url).scheme + ':' + img_url
                    elif not img_url.startswith('http'):
                        img_url = urljoin(url, img_url)
                    
                    # 清理URL（移除查询参数中的尺寸等，但保留基本URL）
                    clean_url = img_url.split('?')[0].split('#')[0].strip()
                    # 清理URL中的错误转义字符
                    clean_url = self._clean_url(clean_url) if clean_url else None
                    if not clean_url:
                        continue
                    
                    # 排除明显的非媒体文件（只排除.js, .css, .html等）
                    excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                    path = urlparse(clean_url).path.lower()
                    if any(path.endswith(ext) for ext in excluded_exts):
                        continue
                    
                    # 处理base64图片
                    if clean_url.startswith('data:image/'):
                        self._process_base64_image(clean_url, found_urls)
                        continue
                    # 跳过其他非图片的data URL和javascript
                    if clean_url.startswith('data:') or clean_url.startswith('javascript:'):
                        continue
                    
                    if clean_url not in found_urls and clean_url not in seen_urls:
                        seen_urls.add(clean_url)
                        found_urls.add(clean_url)
                        
                        # 判断是图片还是视频（主要依赖后缀名，放宽条件，特别注意webp）
                        path = urlparse(clean_url).path.lower()
                        is_video = any(ext in path for ext in ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv'])
                        # 特别注意webp格式
                        is_image = any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif'])
                        
                        # 如果没有明确的扩展名，但URL中包含image或img或webp或avif，也认为是图片
                        if not is_image and not is_video:
                            if 'image' in clean_url.lower() or 'img' in clean_url.lower() or 'webp' in clean_url.lower() or 'avif' in clean_url.lower():
                                is_image = True
                            elif 'video' in clean_url.lower() or 'mp4' in clean_url.lower():
                                is_video = True
                            else:
                                # 如果都不匹配，跳过（避免添加太多非媒体资源）
                                continue
                        
                        resource_type = 'video' if is_video else 'image'
                        type_label = '淘宝视频' if is_video else '淘宝图片'
                        
                        name = os.path.basename(urlparse(clean_url).path) or f"{type_label}_{len([r for r in self.resources if r['type'] == resource_type]) + 1}"
                        if not name or name == '':
                            name = f"{type_label}_{len([r for r in self.resources if r['type'] == resource_type]) + 1}"
                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                        self.resources.append({
                            'name': name,
                            'url': clean_url,
                            'type': resource_type
                        })
            
            # 方法2: 查找script标签中的JSON数据
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.string
                if not script_text:
                    continue
                
                # 查找JSON格式的图片URL
                json_patterns = [
                    r'"picUrl"\s*:\s*"([^"]+)"',
                    r'"image"\s*:\s*"([^"]+)"',
                    r'"img"\s*:\s*"([^"]+)"',
                    r'"url"\s*:\s*"([^"]+)"',
                    r'"src"\s*:\s*"([^"]+)"',
                ]
                
                for pattern in json_patterns:
                    matches = re.finditer(pattern, script_text, re.IGNORECASE)
                    for match in matches:
                        img_url = match.group(1)
                        if img_url and ('alicdn.com' in img_url or 'taobaocdn.com' in img_url or 'tbcdn.cn' in img_url or '360buyimg.com' in img_url):
                            img_url = img_url.split('?')[0].split('#')[0].strip()
                            
                            # 排除明显的非媒体文件（只排除.js, .css, .html等）
                            excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                            path = urlparse(img_url).path.lower()
                            if any(path.endswith(ext) for ext in excluded_exts):
                                continue
                            
                            if img_url not in found_urls and img_url not in seen_urls and img_url.startswith('http'):
                                seen_urls.add(img_url)
                                found_urls.add(img_url)
                                
                                # 判断是图片还是视频（放宽条件，只要包含扩展名即可）
                                path = urlparse(img_url).path.lower()
                                is_video = any(ext in path for ext in ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv'])
                                is_image = any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg'])
                                
                                # 如果没有明确的扩展名，但URL中包含image或img或webp，也认为是图片
                                if not is_image and not is_video:
                                    if 'image' in img_url.lower() or 'img' in img_url.lower() or 'webp' in img_url.lower():
                                        is_image = True
                                    elif 'video' in img_url.lower() or 'mp4' in img_url.lower():
                                        is_video = True
                                    else:
                                        # 如果都不匹配，跳过（避免添加太多非媒体资源）
                                        continue
                                
                                resource_type = 'video' if is_video else 'image'
                                type_label = '淘宝视频' if is_video else '淘宝图片'
                                
                                name = os.path.basename(urlparse(img_url).path) or f"{type_label}_{len([r for r in self.resources if r['type'] == resource_type]) + 1}"
                                name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                self.resources.append({
                                    'name': name,
                                    'url': img_url,
                                    'type': resource_type
                                })
            
            # 方法3: 查找data属性中的图片和视频
            for attr in ['data-src', 'data-original', 'data-lazy-src', 'data-url', 'data-video', 'data-mp4']:
                elements = soup.find_all(attrs={attr: True})
                for elem in elements:
                    img_url = elem.get(attr)
                    if img_url and ('alicdn.com' in img_url or 'taobaocdn.com' in img_url or 'tbcdn.cn' in img_url or '360buyimg.com' in img_url):
                        full_url = urljoin(url, img_url)
                        full_url = full_url.split('?')[0].split('#')[0].strip()
                        
                        # 排除明显的非媒体文件（只排除.js, .css, .html等）
                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                        path = urlparse(full_url).path.lower()
                        if any(path.endswith(ext) for ext in excluded_exts):
                            continue
                        
                        if full_url not in found_urls and full_url not in seen_urls:
                            seen_urls.add(full_url)
                            found_urls.add(full_url)
                            
                            # 判断是图片还是视频（放宽条件，只要包含扩展名即可）
                            path = urlparse(full_url).path.lower()
                            is_video = any(ext in path for ext in ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv']) or 'video' in attr.lower() or 'mp4' in attr.lower()
                            is_image = any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif'])
                            
                            # 如果没有明确的扩展名，但URL中包含image或img或webp或avif，也认为是图片
                            if not is_image and not is_video:
                                if 'image' in full_url.lower() or 'img' in full_url.lower() or 'webp' in full_url.lower() or 'avif' in full_url.lower():
                                    is_image = True
                                elif 'video' in full_url.lower() or 'mp4' in full_url.lower():
                                    is_video = True
                                else:
                                    # 如果都不匹配，跳过（避免添加太多非媒体资源）
                                    continue
                            
                            resource_type = 'video' if is_video else 'image'
                            type_label = '淘宝视频' if is_video else '淘宝图片'
                            
                            name = elem.get('alt') or elem.get('title') or os.path.basename(urlparse(full_url).path) or f"{type_label}_{len([r for r in self.resources if r['type'] == resource_type]) + 1}"
                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                            self.resources.append({
                                'name': name,
                                'url': full_url,
                                'type': resource_type
                            })
            
            print(f"淘宝页面提取到 {len([r for r in self.resources if r['type'] == 'image'])} 个图片资源和 {len([r for r in self.resources if r['type'] == 'video'])} 个视频资源")
            
        except Exception as e:
            import traceback
            print(f"提取淘宝资源时出错: {e}")
            print(traceback.format_exc())
    
    def fetch_with_selenium(self, url):
        """使用Selenium获取渲染后的HTML，并监听网络请求捕获图片资源"""
        # 确保导入必要的模块
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError as e:
            print(f"导入Selenium模块失败: {e}")
            return None
        
        driver = None
        network_resources = {}  # 存储从网络请求中捕获的资源：{url: {'mime_type': '...', 'initiator_type': '...'}}
        request_id_to_initiator = {}  # 在函数开头创建，确保在整个过程中可用
        request_id_to_mime = {}  # 存储requestId到MIME类型的映射
        captured_request_ids = set()  # 记录已处理过的requestId，避免重复处理
        
        try:
            # 配置Chrome选项（增强反反爬虫措施）
            chrome_options = Options()
            # 【关键】禁用无头模式，因为headless模式容易被检测
            # chrome_options.add_argument('--headless')  # 注释掉无头模式
            
            # 【关键】使用用户数据目录保存登录状态（如果启用）
            save_login = hasattr(self, 'save_login_check') and self.save_login_check.GetValue()
            if save_login:
                # 使用用户数据目录，Chrome会保持登录状态
                chrome_options.add_argument(f'--user-data-dir={self.user_data_dir}')
                print(f"使用用户数据目录保存登录状态: {self.user_data_dir}")
                print("提示：首次使用需要登录一次，之后会自动保持登录状态")
            
            # 基本选项
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')  # 最大化窗口，更像真实用户
            
            # 反检测选项
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 更真实的User-Agent
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 添加更多反检测选项
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_argument('--lang=zh-CN,zh,en-US,en')
            
            # 预加载参数（让浏览器更像真实用户）
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,  # 禁用通知
                },
                "profile.managed_default_content_settings": {
                    "images": 1  # 允许加载图片
                },
                "intl.accept_languages": "zh-CN,zh,en-US,en"
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # 启用性能日志来捕获网络请求
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            # 创建WebDriver
            try:
                driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                print(f"无法启动Chrome: {e}")
                print("提示：请确保已安装Chrome浏览器，并且ChromeDriver版本与Chrome浏览器匹配")
                return None
            
            driver.set_page_load_timeout(30)
            
            # 【关键】如果启用了保存登录状态，尝试加载Cookie（作为备用方案）
            if save_login:
                try:
                    self.load_cookies(driver)
                    print("✓ 已加载保存的Cookie（如果存在）")
                except Exception as e:
                    print(f"加载Cookie时出错（不影响使用）: {e}")
            
            # 【关键】执行反检测脚本，隐藏webdriver特征
            print("执行反检测脚本...")
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    // 覆盖plugins属性
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    // 覆盖languages属性
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en-US', 'en']
                    });
                    // 覆盖platform属性
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32'
                    });
                    // Chrome对象
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
            
            # 【重要】在访问网页之前启用网络域监听
            print("启用Network监听...")
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Runtime.enable', {})
            
            # 【关键】设置额外的HTTP头，模拟真实浏览器
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "acceptLanguage": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "platform": "Win32"
            })
            
            # 【关键】设置额外的请求头
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0"
                }
            })
            
            # 【关键改进】设置实时监听器，捕获所有网络请求（包括未显示在页面上的）
            print("设置实时网络请求监听器...")
            
            # 使用JavaScript注入CDP监听器（通过Runtime.addBinding）
            driver.execute_cdp_cmd('Runtime.addBinding', {'name': 'networkListener'})
            
            # 注入JavaScript代码来实时监听所有网络请求
            driver.execute_script("""
                // 拦截所有网络请求，通过Performance API实时获取
                (function() {
                    // 保存原始fetch和XMLHttpRequest
                    var originalFetch = window.fetch;
                    var originalXHROpen = XMLHttpRequest.prototype.open;
                    var originalXHRSend = XMLHttpRequest.prototype.send;
                    
                    // 拦截fetch请求
                    window.fetch = function(...args) {
                        var url = args[0];
                        if (typeof url === 'string' && url.startsWith('http')) {
                            console.log('[Network Intercept] fetch:', url);
                        }
                        return originalFetch.apply(this, args);
                    };
                    
                    // 拦截XMLHttpRequest
                    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                        this._url = url;
                        if (typeof url === 'string' && url.startsWith('http')) {
                            console.log('[Network Intercept] XHR:', url);
                        }
                        return originalXHROpen.apply(this, [method, url, ...rest]);
                    };
                    
                    XMLHttpRequest.prototype.send = function(...args) {
                        if (this._url && this._url.startsWith('http')) {
                            console.log('[Network Intercept] XHR send:', this._url);
                        }
                        return originalXHRSend.apply(this, args);
                    };
                })();
            """)
            
            print(f"Network监听已启用，requestId映射已初始化（当前大小: {len(request_id_to_initiator)}）")
            
            # 访问网页（在访问过程中，所有网络请求都会被实时捕获）
            print(f"开始访问网页: {url}")
            
            # 【关键】先访问主页，建立会话，然后再访问目标页面
            if 'taobao.com' in url.lower() or 'tmall.com' in url.lower():
                try:
                    print("先访问淘宝主页建立会话...")
                    driver.get('https://www.taobao.com')
                    time.sleep(3)  # 等待主页加载
                    
                    # 检查是否需要登录
                    current_url = driver.current_url
                    if 'login' in current_url.lower() or 'havana' in current_url.lower():
                        if save_login:
                            print("检测到需要登录（首次使用或登录已过期）")
                            print("提示：请在浏览器窗口中手动登录一次，之后会自动保存登录状态")
                            print("提示：下次使用时将自动保持登录状态，无需再次登录")
                        else:
                            print("检测到需要登录，等待用户手动登录...")
                            print("提示：请在浏览器窗口中手动登录，登录完成后程序会自动继续")
                        
                        # 等待用户登录（最多等待60秒）
                        for i in range(60):
                            time.sleep(1)
                            current_url = driver.current_url
                            if 'login' not in current_url.lower() and 'havana' not in current_url.lower():
                                print("✓ 登录成功，继续访问商品页面")
                                
                                # 如果启用了保存登录状态，保存Cookie（作为备用方案）
                                if save_login:
                                    try:
                                        self.save_cookies(driver)
                                        print("✓ Cookie已保存，下次启动将自动加载")
                                    except Exception as e:
                                        print(f"保存Cookie时出错（不影响使用）: {e}")
                                break
                            if i % 10 == 0 and i > 0:
                                print(f"等待登录中... ({i}/60秒)")
                except Exception as e:
                    print(f"访问主页时出错: {e}")
            
            # 访问目标页面
            print(f"访问目标页面: {url}")
            driver.get(url)
            
            # 等待页面加载
            import time
            try:
                # 等待body标签出现
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 【关键】页面加载后立即获取一次日志（捕获初始请求）
                print("页面body加载完成，立即获取日志...")
                try:
                    immediate_logs = driver.get_log('performance')
                    print(f"立即获取到 {len(immediate_logs)} 条性能日志")
                except Exception as e:
                    print(f"立即获取日志失败: {e}")
                
                # 等待图片加载（最多等待10秒）
                max_wait = 10
                waited = 0
                while waited < max_wait:
                    imgs = driver.find_elements(By.TAG_NAME, "img")
                    if len(imgs) > 0:
                        loaded_count = 0
                        for img in imgs:
                            try:
                                if img.get_attribute('complete') == 'true' or img.get_attribute('src'):
                                    loaded_count += 1
                            except:
                                pass
                        if loaded_count > 0:
                            break
                    time.sleep(0.5)
                    waited += 0.5
                
                # 额外等待JavaScript执行和API调用
                print("等待页面完全加载...")
                time.sleep(2)  # 减少等待时间到2秒
                
                # 使用IntersectionObserver强制触发所有懒加载图片（更高效的方式）
                print("使用IntersectionObserver强制触发所有懒加载图片...")
                try:
                    driver.execute_script("""
                        // 创建IntersectionObserver来强制触发所有懒加载图片
                        var observer = new IntersectionObserver(function(entries) {
                            entries.forEach(function(entry) {
                                if (entry.isIntersecting) {
                                    var target = entry.target;
                                    // 如果目标是img元素，尝试从data-src加载
                                    if (target.tagName === 'IMG') {
                                        var dataSrc = target.getAttribute('data-src') || 
                                                     target.getAttribute('data-original') || 
                                                     target.getAttribute('data-lazy-src') ||
                                                     target.getAttribute('data-url');
                                        if (dataSrc && !target.src) {
                                            target.src = dataSrc;
                                        }
                                    }
                                }
                            });
                        }, { rootMargin: '100px', threshold: 0.01 });
                        
                        // 观察所有img元素
                        var allImgs = document.querySelectorAll('img');
                        allImgs.forEach(function(img) {
                            observer.observe(img);
                        });
                        
                        // 也观察所有可能的图片容器
                        var containers = document.querySelectorAll('[data-src], [data-img], [data-image], [data-url], [data-original]');
                        containers.forEach(function(container) {
                            observer.observe(container);
                        });
                    """)
                    time.sleep(1)  # 减少等待时间到1秒
                except:
                    pass
                
                # 滚动页面以触发懒加载和更多API调用（优化滚动，减少等待时间）
                print("滚动页面以触发懒加载图片...")
                
                # 减少滚动轮数，优化滚动速度
                for scroll_round in range(2):  # 减少到2轮滚动
                    print(f"第 {scroll_round + 1} 轮滚动...")
                    # 获取页面总高度（每次滚动后可能变化）
                    total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                    print(f"页面总高度: {total_height}px")
                    
                    # 减少滚动步数，加快滚动速度
                    scroll_steps = 10  # 减少滚动步数到10
                    step_height = max(200, total_height // scroll_steps)
                    for i in range(scroll_steps + 1):
                        scroll_pos = i * step_height
                        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
                        time.sleep(0.2)  # 减少等待时间到0.2秒
                    
                    # 滚动到底部（快速尝试，减少等待时间）
                    print("滚动到最底部...")
                    for bottom_attempt in range(2):  # 减少到2次尝试
                        last_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                        driver.execute_script("window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));")
                        time.sleep(0.5)  # 减少等待时间到0.5秒
                        new_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                        print(f"  尝试 {bottom_attempt + 1}: 上次高度 {last_height}px, 当前高度 {new_height}px")
                        if new_height == last_height:
                            print("  已到达页面底部")
                            break
                        time.sleep(0.3)  # 减少额外等待时间
                    
                    # 在底部短暂等待
                    print("在底部等待，确保内容加载...")
                    time.sleep(1)  # 减少等待时间到1秒
                    
                    # 检查是否有新图片加载（通过检查img元素数量）
                    img_count = driver.execute_script("return document.querySelectorAll('img').length")
                    print(f"当前页面共有 {img_count} 个img元素")
                
                # 尝试点击所有可能的图片查看按钮（淘宝商品详情页可能有"查看大图"按钮）
                print("尝试点击可能的图片查看按钮...")
                try:
                    driver.execute_script("""
                        // 查找所有可能的图片查看按钮
                        var buttons = document.querySelectorAll('button, a, div[class*="expand"], div[class*="more"], div[class*="view"], [class*="zoom"], [class*="detail"]');
                        buttons.forEach(function(btn) {
                            var text = (btn.textContent || btn.innerText || '').trim();
                            if (text.match(/查看大图|展开|更多|查看全部|显示更多|加载更多|查看详情|查看原图/i)) {
                                try {
                                    btn.click();
                                } catch(e) {}
                            }
                        });
                    """)
                    time.sleep(1)  # 减少等待时间到1秒
                except:
                    pass
                
                print("页面滚动完成，准备获取所有资源...")
                
                # 最后滚动到最底部，确保获取所有资源
                print("最后滚动到最底部，确保获取所有资源...")
                for final_attempt in range(2):  # 减少到2次尝试
                    last_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                    driver.execute_script("window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));")
                    time.sleep(1)  # 减少等待时间到1秒
                    new_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                    print(f"  最终尝试 {final_attempt + 1}: 上次高度 {last_height}px, 当前高度 {new_height}px")
                    if new_height == last_height:
                        print("  确认已到达页面最底部")
                        break
                    else:
                        print(f"  页面高度增加 {new_height - last_height}px，继续等待...")
                        time.sleep(0.5)  # 减少额外等待时间
                
                # 在底部短暂等待
                print("在底部等待，确保所有资源完全加载...")
                time.sleep(2)  # 减少等待时间到2秒
                
            except Exception as e:
                print(f"等待页面加载时出错: {e}")
                pass  # 如果超时也继续
            
            # 【完美资源获取方法】使用全面的方法获取所有资源
            print("\n" + "=" * 80)
            print("【完美资源获取方法】开始全面提取所有资源...")
            print("=" * 80)
            
            # 执行完美的资源获取JavaScript
            try:
                print("执行完美的资源获取JavaScript...")
                perfect_resources_result = driver.execute_script("""
                    (function() {
                        var allResources = [];
                        var seen = new Set();
                        var debugInfo = [];
                        
                        // 辅助函数：处理图片URL，去除尺寸参数获取原图
                        function getOriginalImageUrl(url) {
                            if (!url) return url;
                            // 淘宝图片URL格式：https://xxx.alicdn.com/xxx.jpg_50x50.jpg
                            // 去除尺寸参数，获取原图
                            url = url.replace(/_[0-9]+x[0-9]+\\.jpg/g, '.jpg');
                            url = url.replace(/_[0-9]+x[0-9]+\\.png/g, '.png');
                            url = url.replace(/_[0-9]+x[0-9]+\\.webp/g, '.webp');
                            url = url.replace(/_[0-9]+x[0-9]+\\.avif/g, '.avif');
                            // 去除其他尺寸参数（如-tps-48-48）
                            url = url.replace(/-tps-[0-9]+-[0-9]+/g, '');
                            // 去除查询参数中的尺寸参数
                            url = url.replace(/[?&]x-oss-process[^&]*/g, '');
                            url = url.replace(/[?&]imageView[^&]*/g, '');
                            // 去除查询参数（可选，保留基本URL）
                            // url = url.replace(/\\?.*$/, '');
                            return url;
                        }
                        
                        // 辅助函数：判断是否是资源URL
                        function isResourceUrl(url) {
                            if (!url || typeof url !== 'string') return false;
                            if (url.startsWith('data:')) return false;
                            if (url.startsWith('javascript:')) return false;
                            if (!url.startsWith('http') && !url.startsWith('//')) return false;
                            
                            // 检查是否是图片、视频、音频等资源
                            var imageExts = /\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif|heic|heif)(\\?|$)/i;
                            var videoExts = /\.(mp4|webm|avi|mov|flv|mkv|m4v|3gp|wmv)(\\?|$)/i;
                            var audioExts = /\.(mp3|wav|ogg|aac|m4a|flac|wma)(\\?|$)/i;
                            var fontExts = /\.(woff|woff2|ttf|otf|eot)(\\?|$)/i;
                            
                            if (imageExts.test(url) || videoExts.test(url) || audioExts.test(url) || fontExts.test(url)) {
                                return true;
                            }
                            
                            // 检查URL中是否包含资源关键字
                            var resourceKeywords = ['image', 'img', 'pic', 'photo', 'video', 'audio', 'media', 
                                                   'cdn', 'static', 'upload', 'assets', 'resource', 'alicdn', 
                                                   'taobaocdn', 'tbcdn', 'imgextra', 'oss', 'tps'];
                            var urlLower = url.toLowerCase();
                            for (var i = 0; i < resourceKeywords.length; i++) {
                                if (urlLower.includes(resourceKeywords[i])) {
                                    // 排除明显的非资源URL
                                    if (!urlLower.includes('/api/') && !urlLower.includes('/ajax/') && 
                                        !urlLower.includes('/service/') && !urlLower.includes('/script/')) {
                                        return true;
                                    }
                                }
                            }
                            
                            return false;
                        }
                        
                        // 方法1: 从所有window对象中深度提取资源URL
                        debugInfo.push('方法1: 从window对象中深度提取资源...');
                        try {
                            function extractFromObject(obj, depth, path, visited) {
                                if (depth > 20 || !obj) return;
                                if (visited && visited.has && visited.has(obj)) return;
                                if (visited && visited.add) visited.add(obj);
                                
                                if (typeof obj === 'string') {
                                    if (isResourceUrl(obj)) {
                                        var originalUrl = getOriginalImageUrl(obj);
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            allResources.push({url: originalUrl, source: path || 'windowObject', type: 'unknown'});
                                        }
                                    }
                                } else if (Array.isArray(obj)) {
                                    obj.forEach(function(item, index) {
                                        extractFromObject(item, depth + 1, path + '[' + index + ']', visited);
                                    });
                                } else if (obj && typeof obj === 'object') {
                                    for (var key in obj) {
                                        if (obj.hasOwnProperty(key)) {
                                            try {
                                                var newPath = path ? (path + '.' + key) : key;
                                                extractFromObject(obj[key], depth + 1, newPath, visited);
                                            } catch(e) {}
                                        }
                                    }
                                }
                            }
                            
                            // 从所有可能的全局对象中提取
                            var globalObjects = ['TB', 'g_config', 'runParams', 'itemData', 'skuData', 'detailData', 
                                                 'itemDetail', 'pageData', 'props', 'state', 'store', 'model', 
                                                 'viewModel', 'goodsData', 'productData', 'itemInfo', 'skuMap', 
                                                 'descInfo', 'images', 'pics', 'photos', 'gallery', 'album'];
                            
                            var visited = new WeakSet();
                            globalObjects.forEach(function(objName) {
                                try {
                                    if (window[objName] && typeof window[objName] === 'object') {
                                        extractFromObject(window[objName], 0, objName, visited);
                                    }
                                } catch(e) {}
                            });
                            
                            // 遍历window对象的所有属性（限制数量避免性能问题）
                            var windowKeys = Object.keys(window);
                            var maxKeys = Math.min(500, windowKeys.length);
                            for (var i = 0; i < maxKeys; i++) {
                                try {
                                    var key = windowKeys[i];
                                    // 跳过一些明显不相关的属性
                                    if (key.startsWith('webkit') || key.startsWith('moz') || key.startsWith('ms') || 
                                        key === 'document' || key === 'navigator' || key === 'location' || 
                                        key === 'history' || key === 'screen' || key === 'console' || 
                                        key === 'performance' || key === 'localStorage' || key === 'sessionStorage' ||
                                        key === 'XMLHttpRequest' || key === 'fetch' || key === 'Promise') {
                                        continue;
                                    }
                                    var obj = window[key];
                                    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                                        try {
                                            extractFromObject(obj, 0, key, visited);
                                        } catch(e) {}
                                    }
                                } catch(e) {}
                            }
                            
                            debugInfo.push('方法1完成，找到 ' + allResources.length + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法1出错: ' + e.toString());
                        }
                        
                        // 方法2: 从DOM中提取所有资源（包括所有可能的属性）
                        debugInfo.push('方法2: 从DOM中提取所有资源...');
                        try {
                            var domCount = 0;
                            
                            // 提取所有img元素
                            var imgs = document.querySelectorAll('img');
                            imgs.forEach(function(img) {
                                var sources = [
                                    img.src, img.currentSrc,
                                    img.getAttribute('src'), img.getAttribute('data-src'),
                                    img.getAttribute('data-original'), img.getAttribute('data-lazy-src'),
                                    img.getAttribute('data-url'), img.getAttribute('data-img'),
                                    img.getAttribute('data-image'), img.getAttribute('data-srcset'),
                                    img.getAttribute('srcset'), img.getAttribute('data-zoom'),
                                    img.getAttribute('data-zoom-src'), img.getAttribute('data-lazy'),
                                    img.getAttribute('lazy-src'), img.getAttribute('original-src'),
                                    img.getAttribute('data-original-src'), img.getAttribute('data-full'),
                                    img.getAttribute('data-large'), img.getAttribute('data-webp'),
                                    img.getAttribute('webp'), img.getAttribute('data-avif'),
                                    img.getAttribute('avif')
                                ];
                                
                                sources.forEach(function(src) {
                                    if (src && (src.startsWith('http') || src.startsWith('//'))) {
                                        if (src.startsWith('//')) {
                                            src = window.location.protocol + src;
                                        }
                                        // 处理srcset格式
                                        if (src.includes(',')) {
                                            var urls = src.split(',');
                                            urls.forEach(function(url) {
                                                url = url.trim().split(' ')[0];
                                                if (url && isResourceUrl(url)) {
                                                    var originalUrl = getOriginalImageUrl(url);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        allResources.push({url: originalUrl, source: 'DOM.img', type: 'image'});
                                                        domCount++;
                                                    }
                                                }
                                            });
                                        } else if (isResourceUrl(src)) {
                                            var originalUrl = getOriginalImageUrl(src);
                                            if (!seen.has(originalUrl)) {
                                                seen.add(originalUrl);
                                                allResources.push({url: originalUrl, source: 'DOM.img', type: 'image'});
                                                domCount++;
                                            }
                                        }
                                    }
                                });
                            });
                            
                            // 提取所有video元素
                            var videos = document.querySelectorAll('video');
                            videos.forEach(function(video) {
                                var sources = [
                                    video.src,
                                    video.getAttribute('src'), video.getAttribute('data-src'),
                                    video.getAttribute('poster') // 视频封面图
                                ];
                                
                                sources.forEach(function(src) {
                                    if (src && isResourceUrl(src)) {
                                        if (src.startsWith('//')) {
                                            src = window.location.protocol + src;
                                        }
                                        var originalUrl = getOriginalImageUrl(src);
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            allResources.push({url: originalUrl, source: 'DOM.video', type: src.includes('poster') ? 'image' : 'video'});
                                            domCount++;
                                        }
                                    }
                                });
                                
                                // 提取source子元素
                                var sources = video.querySelectorAll('source');
                                sources.forEach(function(source) {
                                    var src = source.getAttribute('src');
                                    if (src && isResourceUrl(src)) {
                                        if (src.startsWith('//')) {
                                            src = window.location.protocol + src;
                                        }
                                        var originalUrl = getOriginalImageUrl(src);
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            allResources.push({url: originalUrl, source: 'DOM.video.source', type: 'video'});
                                            domCount++;
                                        }
                                    }
                                });
                            });
                            
                            // 提取所有audio元素
                            var audios = document.querySelectorAll('audio');
                            audios.forEach(function(audio) {
                                var src = audio.src || audio.getAttribute('src');
                                if (src && isResourceUrl(src)) {
                                    if (src.startsWith('//')) {
                                        src = window.location.protocol + src;
                                    }
                                    var originalUrl = getOriginalImageUrl(src);
                                    if (!seen.has(originalUrl)) {
                                        seen.add(originalUrl);
                                        allResources.push({url: originalUrl, source: 'DOM.audio', type: 'audio'});
                                        domCount++;
                                    }
                                }
                            });
                            
                            // 提取所有元素的CSS背景图片
                            var allElements = document.querySelectorAll('*');
                            var maxElements = Math.min(10000, allElements.length);
                            for (var i = 0; i < maxElements; i++) {
                                try {
                                    var elem = allElements[i];
                                    var style = window.getComputedStyle(elem);
                                    var bgImage = style.backgroundImage;
                                    if (bgImage && bgImage !== 'none') {
                                        var matches = bgImage.match(/url\\(["']?([^"')]+)["']?\\)/g);
                                        if (matches) {
                                            matches.forEach(function(match) {
                                                var url = match.replace(/url\\(["']?([^"')]+)["']?\\)/, '$1');
                                                if (url && isResourceUrl(url)) {
                                                    if (url.startsWith('//')) {
                                                        url = window.location.protocol + url;
                                                    }
                                                    var originalUrl = getOriginalImageUrl(url);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        allResources.push({url: originalUrl, source: 'DOM.background', type: 'image'});
                                                        domCount++;
                                                    }
                                                }
                                            });
                                        }
                                    }
                                    
                                    // 检查内联样式
                                    var inlineStyle = elem.getAttribute('style');
                                    if (inlineStyle) {
                                        var inlineMatches = inlineStyle.match(/background[-_]?image\\s*:\\s*url\\(["']?([^"')]+)["']?\\)/gi);
                                        if (inlineMatches) {
                                            inlineMatches.forEach(function(match) {
                                                var url = match.replace(/.*url\\(["']?([^"')]+)["']?\\).*/i, '$1');
                                                if (url && isResourceUrl(url)) {
                                                    if (url.startsWith('//')) {
                                                        url = window.location.protocol + url;
                                                    }
                                                    var originalUrl = getOriginalImageUrl(url);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        allResources.push({url: originalUrl, source: 'DOM.inlineStyle', type: 'image'});
                                                        domCount++;
                                                    }
                                                }
                                            });
                                        }
                                    }
                                    
                                    // 检查data属性
                                    ['data-src', 'data-original', 'data-url', 'data-img', 'data-image', 'data-pic', 'data-photo'].forEach(function(attr) {
                                        var attrValue = elem.getAttribute(attr);
                                        if (attrValue && isResourceUrl(attrValue)) {
                                            if (attrValue.startsWith('//')) {
                                                attrValue = window.location.protocol + attrValue;
                                            }
                                            var originalUrl = getOriginalImageUrl(attrValue);
                                            if (!seen.has(originalUrl)) {
                                                seen.add(originalUrl);
                                                allResources.push({url: originalUrl, source: 'DOM.data.' + attr, type: 'image'});
                                                domCount++;
                                            }
                                        }
                                    });
                                } catch(e) {}
                            }
                            
                            debugInfo.push('方法2完成，从DOM找到 ' + domCount + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法2出错: ' + e.toString());
                        }
                        
                        // 方法3: 从所有script标签中提取资源URL
                        debugInfo.push('方法3: 从script标签中提取资源...');
                        try {
                            var scriptCount = 0;
                            var scripts = document.querySelectorAll('script');
                            scripts.forEach(function(script) {
                                var scriptText = script.textContent || script.innerHTML;
                                if (!scriptText || scriptText.length < 50) return;
                                
                                // 使用正则表达式提取所有资源URL
                                var patterns = [
                                    /https?:\\/\\/[^"'\s<>)]+\\.[a-z]{2,4}(?:[?&#][^"'\s<>)]*)?/gi,
                                    /\/\/[^"'\s<>)]+\\.[a-z]{2,4}(?:[?&#][^"'\s<>)]*)?/gi,
                                    /["']([^"']+\\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif|mp4|webm|avi|mov|flv|mkv|mp3|wav|ogg))["']/gi
                                ];
                                
                                patterns.forEach(function(pattern) {
                                    var matches = scriptText.match(pattern);
                                    if (matches) {
                                        matches.forEach(function(match) {
                                            var url = match.replace(/^["']|["']$/g, '');
                                            if (url && isResourceUrl(url)) {
                                                if (url.startsWith('//')) {
                                                    url = window.location.protocol + url;
                                                }
                                                var originalUrl = getOriginalImageUrl(url);
                                                if (!seen.has(originalUrl)) {
                                                    seen.add(originalUrl);
                                                    allResources.push({url: originalUrl, source: 'scriptTag', type: 'unknown'});
                                                    scriptCount++;
                                                }
                                            }
                                        });
                                    }
                                });
                            });
                            
                            debugInfo.push('方法3完成，从script标签找到 ' + scriptCount + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法3出错: ' + e.toString());
                        }
                        
                        // 方法4: 从整个HTML内容中提取资源URL
                        debugInfo.push('方法4: 从HTML内容中提取资源...');
                        try {
                            var htmlCount = 0;
                            var htmlContent = document.documentElement.innerHTML;
                            
                            // 使用正则表达式提取所有资源URL
                            var htmlPatterns = [
                                /https?:\\/\\/[^"'\s<>)]+\\.[a-z]{2,4}(?:[?&#][^"'\s<>)]*)?/gi,
                                /\/\/[^"'\s<>)]+\\.[a-z]{2,4}(?:[?&#][^"'\s<>)]*)?/gi
                            ];
                            
                            htmlPatterns.forEach(function(pattern) {
                                var matches = htmlContent.match(pattern);
                                if (matches) {
                                    matches.forEach(function(match) {
                                        if (isResourceUrl(match)) {
                                            if (match.startsWith('//')) {
                                                match = window.location.protocol + match;
                                            }
                                            var originalUrl = getOriginalImageUrl(match);
                                            if (!seen.has(originalUrl)) {
                                                seen.add(originalUrl);
                                                allResources.push({url: originalUrl, source: 'htmlContent', type: 'unknown'});
                                                htmlCount++;
                                            }
                                        }
                                    });
                                }
                            });
                            
                            debugInfo.push('方法4完成，从HTML内容找到 ' + htmlCount + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法4出错: ' + e.toString());
                        }
                        
                        // 方法5: 从Performance API中提取资源
                        debugInfo.push('方法5: 从Performance API中提取资源...');
                        try {
                            var perfCount = 0;
                            if (window.performance && window.performance.getEntriesByType) {
                                var entries = window.performance.getEntriesByType('resource');
                                entries.forEach(function(entry) {
                                    var url = entry.name;
                                    if (url && isResourceUrl(url)) {
                                        var originalUrl = getOriginalImageUrl(url);
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            allResources.push({url: originalUrl, source: 'performanceAPI', type: 'unknown'});
                                            perfCount++;
                                        }
                                    }
                                });
                            }
                            
                            debugInfo.push('方法5完成，从Performance API找到 ' + perfCount + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法5出错: ' + e.toString());
                        }
                        
                        // 方法6: 从iframe中提取资源
                        debugInfo.push('方法6: 从iframe中提取资源...');
                        try {
                            var iframeCount = 0;
                            var iframes = document.querySelectorAll('iframe');
                            iframes.forEach(function(iframe) {
                                try {
                                    var iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                                    if (iframeDoc) {
                                        var iframeImgs = iframeDoc.querySelectorAll('img');
                                        iframeImgs.forEach(function(img) {
                                            var src = img.src || img.getAttribute('src') || img.getAttribute('data-src');
                                            if (src && isResourceUrl(src)) {
                                                var originalUrl = getOriginalImageUrl(src);
                                                if (!seen.has(originalUrl)) {
                                                    seen.add(originalUrl);
                                                    allResources.push({url: originalUrl, source: 'iframe', type: 'image'});
                                                    iframeCount++;
                                                }
                                            }
                                        });
                                    }
                                } catch(e) {
                                    // 跨域iframe无法访问，跳过
                                }
                            });
                            
                            debugInfo.push('方法6完成，从iframe找到 ' + iframeCount + ' 个资源');
                        } catch(e) {
                            debugInfo.push('方法6出错: ' + e.toString());
                        }
                        
                        debugInfo.push('总共找到 ' + allResources.length + ' 个资源');
                        
                        return {resources: allResources, debug: debugInfo};
                    })();
                """)
                
                # 处理提取到的资源
                if perfect_resources_result:
                    if isinstance(perfect_resources_result, dict) and 'debug' in perfect_resources_result:
                        debug_info = perfect_resources_result.get('debug', [])
                        print("完美资源获取调试信息:")
                        for info in debug_info:
                            print(f"  {info}")
                        resources_list = perfect_resources_result.get('resources', [])
                    else:
                        resources_list = perfect_resources_result if isinstance(perfect_resources_result, list) else []
                    
                    print(f"\n完美资源获取方法找到 {len(resources_list)} 个资源")
                    
                    # 获取已存在的URL集合
                    existing_urls = {r['url'] for r in self.resources}
                    added_count = 0
                    
                    for resource_info in resources_list:
                        if isinstance(resource_info, dict):
                            resource_url = resource_info.get('url', '')
                            source = resource_info.get('source', 'unknown')
                            resource_type = resource_info.get('type', 'unknown')
                        else:
                            resource_url = str(resource_info)
                            source = 'unknown'
                            resource_type = 'unknown'
                        
                        if resource_url and resource_url.startswith('http'):
                            # 清理URL
                            clean_url = resource_url.split('#')[0].strip()
                            clean_url = self._clean_url(clean_url) if clean_url else None
                            if clean_url and clean_url not in existing_urls:
                                existing_urls.add(clean_url)
                                
                                # 判断资源类型
                                if resource_type == 'unknown':
                                    if self._is_image_url(clean_url):
                                        resource_type = 'image'
                                    elif self._is_video_url(clean_url):
                                        resource_type = 'video'
                                    else:
                                        resource_type = 'image'  # 默认为图片
                                
                                # 生成文件名
                                name = f"资源_{added_count + 1}"
                                url_path = urlparse(clean_url).path
                                url_filename = os.path.basename(url_path)
                                if url_filename and url_filename not in ['', '/']:
                                    name = f"资源_{added_count + 1}_{url_filename}"
                                name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                
                                self.resources.append({
                                    'name': name,
                                    'url': clean_url,
                                    'type': resource_type,
                                    'source': source
                                })
                                added_count += 1
                    
                    print(f"成功添加 {added_count} 个资源到资源列表（来源：完美资源获取方法）")
                else:
                    print("警告：完美资源获取方法返回空结果")
            except Exception as e:
                import traceback
                print(f"完美资源获取方法出错: {e}")
                print(traceback.format_exc())
            
            # 【关键改进】如果是淘宝/天猫页面，立即提取主图（在提取网络请求之前）
            if 'taobao.com' in url.lower() or 'tmall.com' in url.lower():
                print("\n" + "=" * 80)
                print("检测到淘宝/天猫页面，立即开始提取主图...")
                print("=" * 80)
                
                # 检查是否跳转到登录页，如果是登录页，多次尝试重新加载详情页
                is_login_page = False
                max_retry = 3  # 最多重试3次
                retry_count = 0
                
                while retry_count < max_retry:
                    try:
                        current_url = driver.current_url
                        if 'login' in current_url.lower() or 'havana' in current_url.lower():
                            is_login_page = True
                            retry_count += 1
                            print(f"警告：页面跳转到登录页 (第{retry_count}次检测): {current_url[:100]}")
                            
                            # 尝试返回商品页面
                            if 'detail.tmall.com' in url.lower() or 'detail.taobao.com' in url.lower() or 'item.taobao.com' in url.lower():
                                print(f"尝试重新加载商品详情页 (第{retry_count}次尝试): {url[:100]}")
                                try:
                                    driver.get(url)
                                    time.sleep(5)  # 减少等待时间到5秒（登录相关，保持合理）
                                    
                                    # 再次检查是否还是登录页
                                    current_url_after = driver.current_url
                                    if 'login' in current_url_after.lower() or 'havana' in current_url_after.lower():
                                        if retry_count < max_retry:
                                            print(f"重新加载后仍然是登录页，等待5秒后再次尝试...")
                                            time.sleep(5)
                                            continue  # 继续重试
                                        else:
                                            print("错误：多次尝试后仍然是登录页，无法访问商品详情页")
                                            print("提示：可能需要手动登录后再次尝试，或者检查URL是否正确")
                                            is_login_page = True
                                            break
                                    else:
                                        print("✓ 已成功加载商品详情页")
                                        is_login_page = False
                                        break
                                except Exception as e:
                                    print(f"重新加载页面时出错: {e}")
                                    if retry_count < max_retry:
                                        time.sleep(5)
                                        continue
                                    else:
                                        is_login_page = True
                                        break
                            else:
                                # 不是商品详情页URL，无法重试
                                print("警告：当前URL不是商品详情页，无法重新加载")
                                is_login_page = True
                                break
                        else:
                            # 不是登录页，成功
                            is_login_page = False
                            print("✓ 当前页面是商品详情页")
                            break
                    except Exception as e:
                        print(f"检查登录页时出错: {e}")
                        if retry_count < max_retry:
                            retry_count += 1
                            time.sleep(3)
                            continue
                        else:
                            is_login_page = True
                            break
                
                # 如果最终还是登录页，跳过主图提取
                if is_login_page:
                    print("\n" + "=" * 80)
                    print("警告：无法访问商品详情页，已跳转到登录页")
                    print("提示：将跳过主图提取，只从网络请求中提取资源")
                    print("提示：如果需要提取详情页图片，请先手动登录后再运行")
                    print("=" * 80)
                    time.sleep(2)
                else:
                    # 等待页面完全加载
                    print("等待商品详情页完全加载...")
                    time.sleep(3)  # 减少等待时间到3秒
                
                # 尝试滚动到主图区域
                try:
                    driver.execute_script("""
                        // 滚动到主图区域
                        var mainPicArea = document.querySelector('#J_ImgBooth, .tb-booth, .main-pic, [class*="mainPic"], [id*="mainPic"]');
                        if (mainPicArea) {
                            mainPicArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    """)
                    time.sleep(2)
                except:
                    pass
                
                # 只有在非登录页时才提取主图
                if not is_login_page:
                    try:
                        # 【关键改进】专门提取淘宝商品主图 - 更全面的方法
                        print("开始执行主图提取JavaScript...")
                        main_images_result = driver.execute_script("""
                        (function() {
                            var mainImages = [];
                            var seen = new Set();
                            var debugInfo = [];
                            
                            // 辅助函数：处理图片URL，去除尺寸参数获取原图
                            function getOriginalImageUrl(url) {
                                if (!url) return url;
                                // 淘宝图片URL格式：https://xxx.alicdn.com/xxx.jpg_50x50.jpg
                                // 去除尺寸参数，获取原图
                                url = url.replace(/_[0-9]+x[0-9]+\\.jpg/g, '.jpg');
                                url = url.replace(/_[0-9]+x[0-9]+\\.png/g, '.png');
                                url = url.replace(/_[0-9]+x[0-9]+\\.webp/g, '.webp');
                                // 去除其他尺寸参数（如-tps-48-48）
                                url = url.replace(/-tps-[0-9]+-[0-9]+/g, '');
                                // 去除查询参数
                                url = url.replace(/\\?.*$/, '');
                                return url;
                            }
                            
                            // 调试：检查window对象结构
                            debugInfo.push('检查window对象...');
                            if (window.TB) {
                                debugInfo.push('找到window.TB');
                                if (window.TB.detail) {
                                    debugInfo.push('找到window.TB.detail');
                                } else {
                                    debugInfo.push('未找到window.TB.detail');
                                }
                            } else {
                                debugInfo.push('未找到window.TB');
                            }
                            
                            // 调试：列出所有可能的全局对象
                            var possibleObjects = [];
                            for (var key in window) {
                                if (key && (key.includes('TB') || key.includes('item') || key.includes('detail') || 
                                           key.includes('goods') || key.includes('product') || key.includes('data'))) {
                                    try {
                                        if (window[key] && typeof window[key] === 'object') {
                                            possibleObjects.push(key);
                                        }
                                    } catch(e) {}
                                }
                            }
                            debugInfo.push('可能的对象: ' + possibleObjects.join(', '));
                            
                            // 辅助函数：递归提取对象中的所有图片URL
                            function extractAllImageUrls(obj, depth, path) {
                                if (depth > 10 || !obj) return;
                                path = path || '';
                                
                                if (typeof obj === 'string') {
                                    if (obj.startsWith('http') && 
                                        (obj.includes('alicdn') || obj.includes('taobaocdn') || obj.includes('tbcdn') || 
                                         obj.match(/\\.(jpg|jpeg|png|gif|webp|avif)/i))) {
                                        var originalUrl = getOriginalImageUrl(obj);
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            mainImages.push({url: originalUrl, source: path || 'recursive'});
                                        }
                                    }
                                } else if (Array.isArray(obj)) {
                                    obj.forEach(function(item, index) {
                                        extractAllImageUrls(item, depth + 1, path + '[' + index + ']');
                                    });
                                } else if (obj && typeof obj === 'object') {
                                    for (var key in obj) {
                                        if (obj.hasOwnProperty(key)) {
                                            var newPath = path ? (path + '.' + key) : key;
                                            // 特别关注包含image、img、pic、photo等关键字的属性
                                            if (key.toLowerCase().includes('image') || 
                                                key.toLowerCase().includes('img') || 
                                                key.toLowerCase().includes('pic') || 
                                                key.toLowerCase().includes('photo') ||
                                                key.toLowerCase().includes('url')) {
                                                extractAllImageUrls(obj[key], depth + 1, newPath);
                                            } else {
                                                extractAllImageUrls(obj[key], depth + 1, newPath);
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // 方法1: 从window.TB.detail中提取主图（最可靠的方法）
                            try {
                                if (window.TB && window.TB.detail) {
                                    debugInfo.push('开始提取window.TB.detail...');
                                    
                                    // 递归提取整个TB.detail对象中的所有图片
                                    extractAllImageUrls(window.TB.detail, 0, 'TB.detail');
                                    
                                    // 特别提取itemInfo中的主图
                                    if (window.TB.detail.itemInfo) {
                                        if (window.TB.detail.itemInfo.images) {
                                            var images = window.TB.detail.itemInfo.images;
                                            if (Array.isArray(images)) {
                                                debugInfo.push('找到itemInfo.images数组，长度: ' + images.length);
                                                images.forEach(function(img) {
                                                    var imgUrl = typeof img === 'string' ? img : (img && img.url ? img.url : null);
                                                    if (imgUrl && imgUrl.startsWith('http')) {
                                                        var originalUrl = getOriginalImageUrl(imgUrl);
                                                        if (!seen.has(originalUrl)) {
                                                            seen.add(originalUrl);
                                                            mainImages.push({url: originalUrl, source: 'itemInfo.images'});
                                                        }
                                                    }
                                                });
                                            }
                                        }
                                        // 提取其他可能的图片字段
                                        ['picUrl', 'pic', 'image', 'img', 'mainPic', 'mainPicUrl'].forEach(function(key) {
                                            if (window.TB.detail.itemInfo[key]) {
                                                var imgUrl = window.TB.detail.itemInfo[key];
                                                if (typeof imgUrl === 'string' && imgUrl.startsWith('http')) {
                                                    var originalUrl = getOriginalImageUrl(imgUrl);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        mainImages.push({url: originalUrl, source: 'itemInfo.' + key});
                                                    }
                                                }
                                            }
                                        });
                                    }
                                    
                                    // 提取images数组（主图列表）
                                    if (window.TB.detail.images && Array.isArray(window.TB.detail.images)) {
                                        debugInfo.push('找到detail.images数组，长度: ' + window.TB.detail.images.length);
                                        window.TB.detail.images.forEach(function(img) {
                                            var imgUrl = typeof img === 'string' ? img : (img && img.url ? img.url : null);
                                            if (imgUrl && imgUrl.startsWith('http')) {
                                                var originalUrl = getOriginalImageUrl(imgUrl);
                                                if (!seen.has(originalUrl)) {
                                                    seen.add(originalUrl);
                                                    mainImages.push({url: originalUrl, source: 'detail.images'});
                                                }
                                            }
                                        });
                                    }
                                    
                                    // 提取skuMap中的所有图片
                                    if (window.TB.detail.skuMap) {
                                        var skuCount = Object.keys(window.TB.detail.skuMap).length;
                                        debugInfo.push('找到skuMap，SKU数量: ' + skuCount);
                                        for (var skuId in window.TB.detail.skuMap) {
                                            if (window.TB.detail.skuMap.hasOwnProperty(skuId)) {
                                                var sku = window.TB.detail.skuMap[skuId];
                                                extractAllImageUrls(sku, 0, 'skuMap.' + skuId);
                                            }
                                        }
                                    }
                                    
                                    // 提取descInfo中的图片
                                    if (window.TB.detail.descInfo) {
                                        extractAllImageUrls(window.TB.detail.descInfo, 0, 'descInfo');
                                    }
                                    
                                    // 提取所有可能的图片字段
                                    ['images', 'imageList', 'picList', 'picUrls', 'imageUrls', 'mainImages', 'thumbImages'].forEach(function(key) {
                                        if (window.TB.detail[key]) {
                                            extractAllImageUrls(window.TB.detail[key], 0, 'detail.' + key);
                                        }
                                    });
                                }
                            } catch(e) {
                                debugInfo.push('提取window.TB.detail失败: ' + e.toString());
                            }
                            
                            // 方法1.5: 从所有可能的全局对象中提取
                            try {
                                var globalObjects = ['TB', 'g_config', 'runParams', 'itemData', 'skuData', 'detailData', 
                                                     'itemDetail', 'pageData', 'props', 'state', 'store', 'model', 
                                                     'viewModel', 'goodsData', 'productData'];
                                globalObjects.forEach(function(objName) {
                                    try {
                                        var obj = window[objName];
                                        if (obj && typeof obj === 'object') {
                                            extractAllImageUrls(obj, 0, objName);
                                        }
                                    } catch(e) {}
                                });
                            } catch(e) {
                                debugInfo.push('提取全局对象失败: ' + e.toString());
                            }
                            
                            // 方法2: 从主图轮播区域提取（通过DOM选择器）
                            try {
                                debugInfo.push('开始从DOM提取主图...');
                                var mainImageSelectors = [
                                    '#J_ImgBooth', '.tb-booth', '.main-pic', '[class*="mainPic"]',
                                    '[class*="main-pic"]', '[id*="mainPic"]', '[id*="main-pic"]',
                                    '.tb-pic', '[class*="pic-list"]', '[class*="picList"]', '.J_ImgBooth'
                                ];
                                
                                var domImgCount = 0;
                                mainImageSelectors.forEach(function(selector) {
                                    try {
                                        var containers = document.querySelectorAll(selector);
                                        if (containers.length > 0) {
                                            debugInfo.push('找到容器: ' + selector + ', 数量: ' + containers.length);
                                        }
                                        containers.forEach(function(container) {
                                            var imgs = container.querySelectorAll('img');
                                            imgs.forEach(function(img) {
                                                var src = img.src || img.getAttribute('src') || 
                                                         img.getAttribute('data-src') || 
                                                         img.getAttribute('data-original') || 
                                                         img.getAttribute('data-lazy-src') ||
                                                         img.getAttribute('data-url') ||
                                                         img.getAttribute('data-zoom-src') ||
                                                         img.currentSrc;
                                                if (src && src.startsWith('http')) {
                                                    var originalUrl = getOriginalImageUrl(src);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        mainImages.push({url: originalUrl, source: 'mainPicContainer'});
                                                        domImgCount++;
                                                    }
                                                }
                                                
                                                var srcset = img.getAttribute('srcset') || img.getAttribute('data-srcset');
                                                if (srcset) {
                                                    var urls = srcset.split(',');
                                                    urls.forEach(function(item) {
                                                        var url = item.trim().split(' ')[0];
                                                        if (url && url.startsWith('http')) {
                                                            var originalUrl = getOriginalImageUrl(url);
                                                            if (!seen.has(originalUrl)) {
                                                                seen.add(originalUrl);
                                                                mainImages.push({url: originalUrl, source: 'mainPicContainer.srcset'});
                                                                domImgCount++;
                                                            }
                                                        }
                                                    });
                                                }
                                            });
                                        });
                                    } catch(e) {}
                                });
                                debugInfo.push('从DOM提取到 ' + domImgCount + ' 个图片');
                            } catch(e) {
                                debugInfo.push('从DOM提取失败: ' + e.toString());
                            }
                            
                            // 方法4: 从页面脚本标签中提取主图URL
                            try {
                                debugInfo.push('开始从script标签提取...');
                                var scripts = document.querySelectorAll('script');
                                debugInfo.push('找到 ' + scripts.length + ' 个script标签');
                                var scriptImgCount = 0;
                                
                                scripts.forEach(function(script) {
                                    var scriptText = script.textContent || script.innerHTML;
                                    if (!scriptText || scriptText.length < 100) return;
                                    
                                    // 提取所有alicdn的URL
                                    var alicdnPattern = /https?:\/\/[^"'\s<>)]+alicdn[^"'\s<>)]+\.(jpg|jpeg|png|gif|webp|avif|JPG|JPEG|PNG|GIF|WEBP|AVIF)([^"'\s<>)]*)?/gi;
                                    var alicdnMatches = scriptText.match(alicdnPattern);
                                    if (alicdnMatches) {
                                        alicdnMatches.forEach(function(url) {
                                            var originalUrl = getOriginalImageUrl(url);
                                            if (!originalUrl.includes('logo') && !originalUrl.includes('icon') && 
                                                !originalUrl.includes('avatar') && !seen.has(originalUrl)) {
                                                seen.add(originalUrl);
                                                mainImages.push({url: originalUrl, source: 'scriptTag.alicdn'});
                                                scriptImgCount++;
                                            }
                                        });
                                    }
                                });
                                
                                debugInfo.push('从script标签提取到 ' + scriptImgCount + ' 个图片');
                            } catch(e) {
                                debugInfo.push('从script标签提取失败: ' + e.toString());
                            }
                            
                            // 方法6: 从整个页面HTML中提取所有imgextra路径的图片（无论主图数量多少）
                            try {
                                debugInfo.push('开始从整个页面HTML提取所有imgextra图片...');
                                var htmlContent = document.documentElement.innerHTML;
                                
                                // 【关键】特别提取imgextra路径的图片
                                var imgextraPattern = /https?:\/\/[^"'\s<>)]+imgextra[^"'\s<>)]+\.(jpg|jpeg|png|gif|webp|avif|JPG|JPEG|PNG|GIF|WEBP|AVIF)([^"'\s<>)]*)?/gi;
                                var imgextraMatches = htmlContent.match(imgextraPattern);
                                if (imgextraMatches) {
                                    var imgextraImgCount = 0;
                                    imgextraMatches.forEach(function(url) {
                                        var originalUrl = getOriginalImageUrl(url);
                                        // 不过滤小图标，因为用户可能想要所有图片
                                        if (!seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            mainImages.push({url: originalUrl, source: 'htmlContent.imgextra'});
                                            imgextraImgCount++;
                                        }
                                    });
                                    debugInfo.push('从HTML内容提取到 ' + imgextraImgCount + ' 个imgextra图片');
                                }
                                
                                // 也提取所有alicdn的图片
                                var allAlicdnPattern = /https?:\/\/[^"'\s<>)]+alicdn[^"'\s<>)]+\.(jpg|jpeg|png|gif|webp|avif|JPG|JPEG|PNG|GIF|WEBP|AVIF)([^"'\s<>)]*)?/gi;
                                var allMatches = htmlContent.match(allAlicdnPattern);
                                if (allMatches) {
                                    var htmlImgCount = 0;
                                    allMatches.forEach(function(url) {
                                        var originalUrl = getOriginalImageUrl(url);
                                        if (!originalUrl.includes('logo') && 
                                            !originalUrl.includes('icon') && 
                                            !originalUrl.includes('avatar') &&
                                            !seen.has(originalUrl)) {
                                            seen.add(originalUrl);
                                            mainImages.push({url: originalUrl, source: 'htmlContent.alicdn'});
                                            htmlImgCount++;
                                        }
                                    });
                                    debugInfo.push('从HTML内容提取到 ' + htmlImgCount + ' 个alicdn图片');
                                }
                            } catch(e) {
                                debugInfo.push('从HTML内容提取失败: ' + e.toString());
                            }
                            
                            // 方法7: 从所有可能的window对象中深度搜索图片URL
                            try {
                                debugInfo.push('开始深度搜索所有window对象中的图片URL...');
                                var deepSearchCount = 0;
                                
                                // 搜索所有window对象的属性
                                for (var key in window) {
                                    try {
                                        if (key && (key.includes('item') || key.includes('detail') || 
                                                   key.includes('goods') || key.includes('product') || 
                                                   key.includes('data') || key.includes('config') ||
                                                   key.includes('props') || key.includes('state'))) {
                                            var obj = window[key];
                                            if (obj && typeof obj === 'object') {
                                                // 深度搜索这个对象
                                                function deepSearch(obj, depth, path) {
                                                    if (depth > 15 || !obj) return;
                                                    
                                                    if (typeof obj === 'string') {
                                                        if (obj.startsWith('http') && 
                                                            (obj.includes('imgextra') || obj.includes('alicdn'))) {
                                                            var originalUrl = getOriginalImageUrl(obj);
                                                            if (!seen.has(originalUrl)) {
                                                                seen.add(originalUrl);
                                                                mainImages.push({url: originalUrl, source: 'deepSearch.' + path});
                                                                deepSearchCount++;
                                                            }
                                                        }
                                                    } else if (Array.isArray(obj)) {
                                                        obj.forEach(function(item, index) {
                                                            deepSearch(item, depth + 1, path + '[' + index + ']');
                                                        });
                                                    } else if (obj && typeof obj === 'object') {
                                                        for (var k in obj) {
                                                            if (obj.hasOwnProperty(k)) {
                                                                deepSearch(obj[k], depth + 1, path + '.' + k);
                                                            }
                                                        }
                                                    }
                                                }
                                                deepSearch(obj, 0, key);
                                            }
                                        }
                                    } catch(e) {}
                                }
                                debugInfo.push('深度搜索找到 ' + deepSearchCount + ' 个图片');
                            } catch(e) {
                                debugInfo.push('深度搜索失败: ' + e.toString());
                            }
                            
                            debugInfo.push('总共找到 ' + mainImages.length + ' 个主图');
                            
                            return {images: mainImages, debug: debugInfo};
                        })();
                    """)
                    
                        # 处理提取到的主图
                        if main_images_result:
                            # 提取调试信息
                            if isinstance(main_images_result, dict) and 'debug' in main_images_result:
                                debug_info = main_images_result.get('debug', [])
                                print("主图提取调试信息:")
                                for info in debug_info:
                                    print(f"  {info}")
                                main_images_list = main_images_result.get('images', [])
                            else:
                                main_images_list = main_images_result if isinstance(main_images_result, list) else []
                            
                            print(f"从淘宝页面提取到 {len(main_images_list)} 个主图")
                            main_img_added = 0
                            # 获取已存在的URL集合
                            existing_urls = {r['url'] for r in self.resources}
                            
                            for img_info in main_images_list:
                                if isinstance(img_info, dict):
                                    img_url = img_info.get('url', '')
                                    source = img_info.get('source', 'unknown')
                                else:
                                    img_url = str(img_info)
                                    source = 'unknown'
                                
                                if img_url and img_url.startswith('http'):
                                    # 清理URL
                                    clean_url = img_url.split('#')[0].strip()
                                    clean_url = self._clean_url(clean_url) if clean_url else None
                                    if clean_url and clean_url not in existing_urls:
                                        # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                        if not self.is_accessible_resource(clean_url):
                                            continue  # 跳过无法访问的资源
                                        
                                        existing_urls.add(clean_url)
                                        # 生成文件名
                                        name = f"主图_{main_img_added + 1}"
                                        url_path = urlparse(clean_url).path
                                        url_filename = os.path.basename(url_path)
                                        if url_filename and url_filename not in ['', '/']:
                                            name = f"主图_{main_img_added + 1}_{url_filename}"
                                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                        self.resources.append({
                                            'name': name,
                                            'url': clean_url,
                                            'type': 'image',
                                            'source': source
                                        })
                                        main_img_added += 1
                                        if main_img_added <= 10:
                                            print(f"  主图 {main_img_added}: {clean_url[:80]}... (来源: {source})")
                            
                            print(f"成功添加 {main_img_added} 个主图到资源列表")
                        else:
                            print("警告：主图提取返回空结果")
                    except Exception as e:
                        import traceback
                        print(f"主图提取出错: {e}")
                        print(traceback.format_exc())
                else:
                    print("跳过主图提取：当前页面是登录页，无法提取详情页主图")
                    print("提示：将从网络请求中提取资源，但可能包含登录页的图片")
            
            # 【关键改进】从性能日志中提取网络请求（在滚动完成后，多次获取以确保捕获所有请求）
            
            # 从性能日志中提取网络请求（在滚动过程中持续获取，确保捕获所有请求）
            print("\n" + "=" * 80)
            print("开始从Network请求中提取资源...")
            print("=" * 80)
            
            # 【关键改进】多次获取日志，确保捕获所有网络请求（包括未显示在页面上的）
            print("开始获取所有性能日志（多次获取以确保不遗漏）...")
            all_logs = []
            
            # 第1次：立即获取（捕获初始请求）
            try:
                logs1 = driver.get_log('performance')
                print(f"第1次获取到 {len(logs1)} 条性能日志")
                all_logs.extend(logs1)
            except Exception as e:
                print(f"第1次获取日志失败: {e}")
            
            # 等待一下，让更多请求完成
            time.sleep(1)
            
            # 第2次：再次获取（捕获延迟请求）
            try:
                logs2 = driver.get_log('performance')
                print(f"第2次获取到 {len(logs2)} 条性能日志（新增: {len(logs2) - len(logs1) if 'logs1' in locals() else len(logs2)}）")
                all_logs.extend(logs2)
            except Exception as e:
                print(f"第2次获取日志失败: {e}")
            
            # 等待一下，让懒加载图片请求完成
            time.sleep(1)
            
            # 第3次：最后获取（捕获所有懒加载请求）
            try:
                logs3 = driver.get_log('performance')
                print(f"第3次获取到 {len(logs3)} 条性能日志（新增: {len(logs3) - len(logs2) if 'logs2' in locals() else len(logs3)}）")
                all_logs.extend(logs3)
            except Exception as e:
                print(f"第3次获取日志失败: {e}")
            
            # 去重日志（基于message内容）
            seen_messages = set()
            initial_logs = []
            for log in all_logs:
                msg_key = str(log.get('message', ''))
                if msg_key not in seen_messages:
                    seen_messages.add(msg_key)
                    initial_logs.append(log)
            
            print(f"去重后共有 {len(initial_logs)} 条唯一的性能日志")
            
            # 【关键】立即处理首次获取的日志（这些日志可能包含所有avif/webp请求）
            if initial_logs:
                print("开始处理首次获取的日志（可能包含所有图片请求）...")
                initial_processed = 0
                for log in initial_logs:
                    try:
                        message = json.loads(log['message'])
                        method = message.get('message', {}).get('method', '')
                        
                        # 处理Network.requestWillBeSent事件
                        if method == 'Network.requestWillBeSent':
                            params = message.get('message', {}).get('params', {})
                            request = params.get('request', {})
                            request_url = request.get('url', '')
                            request_id = params.get('requestId', '')
                            
                            if request_id and request_id not in captured_request_ids:
                                captured_request_ids.add(request_id)
                                initiator = params.get('initiator', {})
                                initiator_type = initiator.get('type', '').lower() if initiator else ''
                                
                                if request_id and initiator_type:
                                    request_id_to_initiator[request_id] = initiator_type
                                
                                if request_url:
                                    # 【关键改进】如果initiatorType是'img'，直接添加（不排除任何文件，因为img标签发起的请求都是图片）
                                    if initiator_type in ['img', 'image', 'imageset']:
                                        # 只排除明显的非资源文件（如.js, .css等），但保留所有可能的图片格式
                                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                                        path = urlparse(request_url).path.lower()
                                        # 如果路径以排除的扩展名结尾，跳过
                                        if path and any(path.endswith(ext) for ext in excluded_exts):
                                            continue
                                        
                                        if request_url not in network_resources:
                                            mime_type = request_id_to_mime.get(request_id, '')
                                            network_resources[request_url] = {
                                                'mime_type': mime_type or 'image/*',  # 如果MIME类型为空，默认为image/*
                                                'initiator_type': initiator_type,
                                                'priority': 'high'  # 标记为高优先级
                                            }
                                            initial_processed += 1
                                            if initial_processed <= 50:  # 增加输出数量
                                                print(f"  [initial] [IMG标签] 捕获到img类型资源: {request_url[:100]} (MIME: {mime_type or 'N/A'})")
                        
                        # 处理Network.responseReceived事件
                        elif method == 'Network.responseReceived':
                            params = message.get('message', {}).get('params', {})
                            response = params.get('response', {})
                            response_url = response.get('url', '')
                            request_id = params.get('requestId', '')
                            
                            # 获取MIME类型
                            content_type = response.get('mimeType', '').lower()
                            
                            # 如果mimeType为空，尝试从响应头中获取
                            if not content_type:
                                headers = response.get('headers', {})
                                if isinstance(headers, dict):
                                    content_type = headers.get('content-type', '').lower()
                                elif isinstance(headers, list):
                                    for header in headers:
                                        if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                            content_type = header.get('value', '').lower()
                                            break
                            
                            # 【关键】如果还是没有，尝试从响应对象的其他字段获取
                            if not content_type:
                                # 检查response对象中是否有其他字段包含MIME类型信息
                                if 'type' in response:
                                    response_type_value = response.get('type', '').lower()
                                    if response_type_value in ['avif', 'webp']:
                                        content_type = f'image/{response_type_value}'
                            
                            # 移除MIME类型中的参数（但保留完整的MIME类型，如image/avif）
                            if content_type:
                                # 只移除参数部分（如charset=utf-8），保留完整的MIME类型
                                if ';' in content_type:
                                    content_type = content_type.split(';')[0].strip()
                                content_type = content_type.strip()
                            
                            # 保存requestId到MIME类型的映射
                            if request_id and content_type:
                                request_id_to_mime[request_id] = content_type
                            
                            initiator_type = request_id_to_initiator.get(request_id, '').lower()
                            
                            if not response_url:
                                continue
                            
                            # 排除明显的非媒体文件
                            excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                            path = urlparse(response_url).path.lower()
                            if path and any(path.endswith(ext) for ext in excluded_exts):
                                continue
                            
                            # 排除明显的非媒体MIME类型
                            excluded_mimes = ['application/javascript', 'text/javascript', 'text/css', 'text/html', 'font/', 'application/x-font']
                            if content_type and any(mime in content_type for mime in excluded_mimes):
                                continue
                            
                            # 【关键改进】优先检查MIME类型，如果是image类型就直接添加（不管initiatorType）
                            # 这样可以确保捕获所有图片资源，而不仅仅是initiatorType='img'的
                            # 【特别处理】明确检查avif和webp MIME类型
                            # 【关键】检查MIME类型，包括完整格式（image/gif）和简化格式（gif）
                            image_extensions = ['gif', 'png', 'jpg', 'jpeg', 'avif', 'webp', 'bmp', 'svg', 'ico', 'heic', 'heif']
                            is_avif_mime = content_type and ('image/avif' in content_type or content_type == 'avif' or 'avif' in content_type)
                            is_webp_mime = content_type and ('image/webp' in content_type or content_type == 'webp' or 'webp' in content_type)
                            # 检查完整格式：image/gif, image/png等
                            is_image_full_format = content_type and ('image' in content_type or content_type.startswith('image/'))
                            # 检查简化格式：gif, png, jpg等（不带image/前缀）
                            is_image_simple_format = content_type and content_type.lower() in image_extensions
                            is_image_by_mime = is_image_full_format or is_image_simple_format or is_avif_mime or is_webp_mime
                            is_video_by_mime = content_type and 'video' in content_type
                            
                            # 检查URL模式（即使MIME类型为空也要检查）
                            url_lower = response_url.lower()
                            is_image_by_url = self._is_image_url(response_url) or self._is_video_url(response_url)
                            
                            # 扩展关键字列表，包括更多CDN和图片路径模式
                            image_keywords = [
                                # CDN域名
                                'alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'jd.com/img', 'jd.com/image',
                                'img.alicdn', 'gw.alicdn', 'cbu01.alicdn', 'sc01.alicdn', 'sc02.alicdn',
                                'img01.360buyimg', 'img10.360buyimg', 'img11.360buyimg', 'img12.360buyimg',
                                'img13.360buyimg', 'img14.360buyimg', 'img15.360buyimg',
                                # 路径关键字
                                '/img/', '/image/', '/pic/', '/photo/', '/picture/', '/upload/', '/media/',
                                '/jfs/', '/imagetools/', '/uba/', '/devfe/', '/babel/', '/static/', '/assets/',
                                # 文件扩展名
                                '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico', '.avif',
                                # 通用关键字
                                'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload', 'media', 'avif',
                                # 淘宝特定模式（包括带数字路径的imgextra，如 imgextra/i3/2218673265158/）
                                'imgextra', 'tps', 'oss', 'oss-cn', 'aliyuncs',
                                # 匹配imgextra后的数字路径模式（如 i1/, i2/, i3/ 等，以及完整路径）
                                '/imgextra/i', 'imgextra/i1/', 'imgextra/i2/', 'imgextra/i3/', 'imgextra/i4/',
                                'imgextra/i5/', 'imgextra/i6/', 'imgextra/i7/', 'imgextra/i8/', 'imgextra/i9/',
                                # 京东特定模式
                                'jfs', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9', 'n10',
                                # 其他常见模式
                                'thumbnail', 'thumb', 'preview', 'original', 'large', 'small', 'medium'
                            ]
                            
                            is_image_by_keyword = any(keyword in url_lower for keyword in image_keywords)
                            
                            # 排除明显的非图片URL（更严格的排除）
                            excluded_patterns = [
                                '/api/', '/ajax/', '/service/', '/script/', '/js/', '/css/',
                                'login', 'logout', 'auth', 'token', 'session', 'cookie',
                                'analytics', 'tracking', 'monitor', 'statistics', 'log',
                                '.min.js', '.min.css', 'fontawesome', 'iconfont'
                            ]
                            
                            # 如果URL包含排除模式，跳过（除非明确是图片MIME类型或URL明确是图片）
                            is_excluded = any(pattern in url_lower for pattern in excluded_patterns)
                            
                            # 【关键】如果满足以下任一条件，就添加资源：
                            # 1. MIME类型是image（最高优先级，即使被排除规则过滤也要添加）
                            # 2. MIME类型是video（最高优先级）
                            # 3. initiatorType是'img'（高优先级）
                            # 4. URL扩展名匹配图片/视频（高优先级）
                            # 5. URL包含图片关键字（且未被排除）
                            should_add = False
                            add_reason = ""
                            
                            # 【最高优先级】如果MIME类型是image，直接添加（不管排除规则）
                            if is_image_by_mime:
                                should_add = True
                                add_reason = f"MIME类型为image ({content_type})"
                            # 【最高优先级】如果MIME类型是video，直接添加
                            elif is_video_by_mime:
                                should_add = True
                                add_reason = f"MIME类型为video ({content_type})"
                            # 【最高优先级】如果initiatorType是'img'，直接添加（img标签发起的请求都是图片，优先级最高）
                            elif initiator_type in ['img', 'image', 'imageset']:
                                should_add = True
                                add_reason = f"[IMG标签] initiatorType为{initiator_type}"
                                # 如果MIME类型为空，设置为image/*
                                if not content_type:
                                    content_type = 'image/*'
                            # 【高优先级】如果URL扩展名匹配图片/视频，直接添加
                            elif is_image_by_url:
                                should_add = True
                                add_reason = "URL扩展名匹配图片/视频"
                            # 【普通优先级】如果URL包含图片关键字（且未被排除）
                            elif is_image_by_keyword and not is_excluded:
                                should_add = True
                                add_reason = "URL包含图片关键字"
                            
                            if should_add and response_url not in network_resources:
                                network_resources[response_url] = {
                                    'mime_type': content_type,
                                    'initiator_type': initiator_type,
                                    'response_type': ''
                                }
                                initial_processed += 1
                                # 【关键调试】特别标记avif和webp资源
                                debug_prefix = ""
                                if is_avif_mime or (content_type and 'avif' in content_type):
                                    debug_prefix = "[AVIF] "
                                elif is_webp_mime or (content_type and 'webp' in content_type):
                                    debug_prefix = "[WEBP] "
                                elif '.webp' in url_lower or '.avif' in url_lower:
                                    debug_prefix = "[WEBP/AVIF URL] "
                                
                                if initial_processed <= 100:  # 增加输出数量，便于调试
                                    print(f"  [initial] {debug_prefix}捕获资源 ({add_reason}): {response_url[:80]} (MIME: {content_type or 'N/A'}, initiator: {initiator_type or 'N/A'})")
                    except (KeyError, json.JSONDecodeError, TypeError) as e:
                        continue
                
                print(f"首次日志处理完成，新增 {initial_processed} 个资源，当前总数: {len(network_resources)}")
                
                # 【关键统计】统计所有从img标签发起的请求
                img_initiator_count = 0
                img_initiator_urls = []
                for url, info in network_resources.items():
                    initiator_type = info.get('initiator_type', '').lower()
                    if initiator_type in ['img', 'image', 'imageset']:
                        img_initiator_count += 1
                        if len(img_initiator_urls) < 50:  # 只保存前50个用于显示
                            img_initiator_urls.append(url)
                
                print(f"\n【IMG标签统计】从img标签发起的请求: {img_initiator_count} 个")
                if img_initiator_urls:
                    print(f"前{min(50, len(img_initiator_urls))}个img标签请求的URL:")
                    for i, url in enumerate(img_initiator_urls, 1):
                        mime = network_resources[url].get('mime_type', 'N/A')
                        print(f"  {i}. {url[:100]}... (MIME: {mime})")
                else:
                    print("  警告：未找到任何从img标签发起的请求！")
                    print("  这可能意味着：")
                    print("    1. 页面中的图片是通过其他方式加载的（如CSS背景图、JavaScript动态加载等）")
                    print("    2. initiatorType字段可能为空或使用了其他值")
                    print("    3. 需要检查Network.requestWillBeSent事件中的initiator字段")
                
                # 【调试】打印首次日志中所有包含avif或webp的MIME类型（检查所有日志）
                avif_webp_found = []
                image_resources_found = []
                for log in initial_logs:  # 检查所有日志
                    try:
                        message = json.loads(log['message'])
                        method = message.get('message', {}).get('method', '')
                        if method == 'Network.responseReceived':
                            params = message.get('message', {}).get('params', {})
                            response = params.get('response', {})
                            response_url = response.get('url', '')
                            content_type = response.get('mimeType', '').lower()
                            
                            # 【关键】如果mimeType为空，尝试从响应头中获取（与处理逻辑一致）
                            if not content_type:
                                headers = response.get('headers', {})
                                if isinstance(headers, dict):
                                    content_type = headers.get('content-type', '').lower()
                                elif isinstance(headers, list):
                                    for header in headers:
                                        if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                            content_type = header.get('value', '').lower()
                                            break
                            
                            # 移除MIME类型中的参数
                            if content_type:
                                content_type = content_type.split(';')[0].strip()
                            
                            # 检查avif/webp（包括URL中包含.webp或.avif的情况）
                            url_lower = response_url.lower()
                            is_avif_webp_mime = content_type and ('avif' in content_type or 'webp' in content_type)
                            is_avif_webp_url = '.webp' in url_lower or '.avif' in url_lower
                            
                            if is_avif_webp_mime or is_avif_webp_url:
                                avif_webp_found.append((response_url[:80], content_type or 'N/A', 'MIME' if is_avif_webp_mime else 'URL'))
                            
                            # 统计所有图片资源
                            if content_type and 'image' in content_type:
                                image_resources_found.append((response_url[:80], content_type))
                    except:
                        pass
                
                print(f"\n【调试统计】首次日志分析结果:")
                print(f"  - 总日志数: {len(initial_logs)}")
                print(f"  - 包含'avif'或'webp'的MIME类型: {len(avif_webp_found)} 个")
                print(f"  - 所有图片MIME类型: {len(image_resources_found)} 个")
                
                # 【关键调试】检查所有图片MIME类型的资源，看看哪些没有被捕获
                print(f"\n【调试】检查所有图片MIME类型的资源（共{len(image_resources_found)}个）:")
                not_captured_count = 0
                not_captured_urls = []
                for url, mime in image_resources_found:
                    if url not in network_resources:
                        not_captured_count += 1
                        if not_captured_count <= 30:
                            not_captured_urls.append((url, mime))
                
                if not_captured_count > 0:
                    print(f"  警告：有 {not_captured_count} 个图片MIME类型的资源未被捕获！")
                    print(f"  前30个未被捕获的资源:")
                    for url, mime in not_captured_urls:
                        # 检查为什么没有被捕获
                        url_lower = url.lower()
                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                        path = urlparse(url).path.lower()
                        is_excluded = path and any(path.endswith(ext) for ext in excluded_exts)
                        is_image_by_url = self._is_image_url(url)
                        is_image_by_keyword = any(keyword in url_lower for keyword in ['alicdn', 'imgextra', 'tps', 'img', 'image', 'pic', 'photo'])
                        print(f"    - URL: {url[:80]}..., MIME: {mime}, 被排除: {is_excluded}, URL匹配: {is_image_by_url}, 关键字匹配: {is_image_by_keyword}")
                else:
                    print(f"  ✓ 所有图片MIME类型的资源都已捕获")
                
                if avif_webp_found:
                    print(f"\n【重要发现】找到 {len(avif_webp_found)} 个包含'avif'或'webp'的资源:")
                    for item in avif_webp_found[:30]:
                        if len(item) == 3:
                            url, mime, source = item
                            print(f"  - URL: {url}..., MIME: {mime}, 来源: {source}")
                        else:
                            url, mime = item
                            print(f"  - URL: {url}..., MIME: {mime}")
                else:
                    print(f"\n【警告】未找到包含'avif'或'webp'的MIME类型")
                    print("  检查所有图片MIME类型（前30个）:")
                    unique_image_mimes = list(set([mime for _, mime in image_resources_found]))[:30]
                    for mime in unique_image_mimes:
                        print(f"    - {mime}")
            
            # 等待网络请求完成
            print("等待网络请求完成...")
            time.sleep(2)  # 减少等待时间到2秒
            
            # 等待所有图片加载完成（通过JavaScript检查）
            print("等待所有图片加载完成...")
            driver.execute_script("""
                return new Promise((resolve) => {
                    let checkCount = 0;
                    let maxChecks = 15;
                    let lastImgCount = 0;
                    let stableCount = 0;
                    
                    function checkImages() {
                        checkCount++;
                        let images = document.querySelectorAll('img');
                        let currentImgCount = images.length;
                        let loaded = 0;
                        let total = images.length;
                        
                        if (currentImgCount > lastImgCount) {
                            checkCount = 0;
                            stableCount = 0;
                            lastImgCount = currentImgCount;
                            console.log('检测到新图片，当前总数: ' + currentImgCount);
                        } else if (currentImgCount === lastImgCount && currentImgCount > 0) {
                            stableCount++;
                        }
                        
                        if (total === 0) {
                            resolve();
                            return;
                        }
                        
                        images.forEach(img => {
                            if (img.complete || img.naturalWidth > 0) {
                                loaded++;
                            } else {
                                img.onload = img.onerror = () => { loaded++; };
                            }
                        });
                        
                        if (loaded >= total * 0.9 && stableCount >= 2) {
                            console.log('图片加载完成，总数: ' + total + ', 已加载: ' + loaded);
                            resolve();
                        } else if (checkCount >= maxChecks) {
                            console.log('达到最大检查次数，总数: ' + total + ', 已加载: ' + loaded);
                            resolve();
                        } else {
                            setTimeout(checkImages, 500);
                        }
                    }
                    
                    checkImages();
                    setTimeout(resolve, 20000);
                });
            """)
            time.sleep(2)
            
            # 【关键改进】使用JavaScript Performance API直接从浏览器获取所有资源（最直接的方法）
            print("\n" + "=" * 80)
            print("【方法0】使用JavaScript Performance API直接从浏览器获取所有资源...")
            print("=" * 80)
            
            js_performance_count_before = len(network_resources)
            try:
                # 使用JavaScript Performance API获取所有资源
                js_resources = driver.execute_script("""
                    var resources = [];
                    var seen = new Set();
                    
                    // 方法1: 从Performance API获取所有资源
                    try {
                        var entries = performance.getEntriesByType('resource');
                        entries.forEach(function(entry) {
                            var url = entry.name;
                            if (url && !seen.has(url)) {
                                seen.add(url);
                                // 检查是否是图片或视频资源（更宽松的条件）
                                var urlLower = url.toLowerCase();
                                // 【关键】优先检查URL中是否包含.webp或.avif（包括特殊格式如.jpg_.webp）
                                var hasWebpAvif = urlLower.includes('.webp') || urlLower.includes('.avif');
                                // 【关键】检查imgextra路径（所有imgextra路径都认为是图片）
                                var hasImgextra = urlLower.includes('imgextra');
                                // 检查图片扩展名
                                var hasImageExt = urlLower.match(/\\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)(\\?|$|_)/i);
                                // 检查CDN域名
                                var hasCdn = urlLower.includes('alicdn') || urlLower.includes('taobaocdn') || 
                                            urlLower.includes('tbcdn') || urlLower.includes('360buyimg');
                                // 检查图片路径关键字
                                var hasImagePath = urlLower.includes('/img/') || urlLower.includes('/image/') ||
                                                  urlLower.includes('/pic/') || urlLower.includes('/photo/') ||
                                                  urlLower.includes('/picture/') || urlLower.includes('/upload/');
                                // 检查initiatorType
                                var isImgInitiator = entry.initiatorType === 'img' || 
                                                    entry.initiatorType === 'image' || 
                                                    entry.initiatorType === 'imageset';
                                
                                var isImage = hasWebpAvif || hasImgextra || hasImageExt || 
                                             (hasCdn && !urlLower.includes('.js') && !urlLower.includes('.css')) ||
                                             hasImagePath || isImgInitiator;
                                
                                var isVideo = urlLower.match(/\\.(mp4|webm|avi|mov|flv|mkv|m3u8|ts|f4v|mpg|mpeg|m4v)(\\?|$)/i) ||
                                             entry.initiatorType === 'video' ||
                                             entry.initiatorType === 'media';
                                
                                if (isImage || isVideo) {
                                    resources.push({
                                        url: url,
                                        type: entry.initiatorType || '',
                                        size: entry.transferSize || 0
                                    });
                                }
                            }
                        });
                    } catch(e) {
                        console.error('Performance API错误:', e);
                    }
                    
                    // 方法2: 从所有img元素中提取URL（包括所有属性）
                    try {
                        var images = document.querySelectorAll('img');
                        images.forEach(function(img) {
                            var attrs = ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-url', 
                                        'data-img', 'data-image', 'data-zoom', 'data-zoom-src', 'srcset',
                                        'data-webp', 'data-srcset', 'currentSrc'];
                            attrs.forEach(function(attr) {
                                var url = img.getAttribute(attr) || (attr === 'currentSrc' ? img.currentSrc : null);
                                if (url && url.startsWith('http') && !seen.has(url)) {
                                    seen.add(url);
                                    // 处理srcset（可能包含多个URL）
                                    if (attr === 'srcset' || attr === 'data-srcset') {
                                        var urls = url.split(/[,\\s]+/);
                                        urls.forEach(function(u) {
                                            u = u.trim().split(' ')[0]; // 移除尺寸描述
                                            if (u && u.startsWith('http') && !seen.has(u)) {
                                                seen.add(u);
                                                resources.push({
                                                    url: u,
                                                    type: 'img',
                                                    size: 0
                                                });
                                            }
                                        });
                                    } else {
                                        resources.push({
                                            url: url,
                                            type: 'img',
                                            size: 0
                                        });
                                    }
                                }
                            });
                        });
                    } catch(e) {
                        console.error('img元素提取错误:', e);
                    }
                    
                    // 方法3: 从CSS背景图片中提取
                    try {
                        var allElements = document.querySelectorAll('*');
                        allElements.forEach(function(el) {
                            try {
                                var style = window.getComputedStyle(el);
                                var bgImage = style.backgroundImage;
                                if (bgImage && bgImage !== 'none') {
                                    var matches = bgImage.match(/url\\(["']?([^"']+)["']?\\)/g);
                                    if (matches) {
                                        matches.forEach(function(match) {
                                            var url = match.replace(/url\\(["']?([^"']+)["']?\\)/, '$1');
                                            if (url && url.startsWith('http') && !seen.has(url)) {
                                                seen.add(url);
                                                resources.push({
                                                    url: url,
                                                    type: 'css',
                                                    size: 0
                                                });
                                            }
                                        });
                                    }
                                }
                            } catch(e) {}
                        });
                    } catch(e) {
                        console.error('CSS背景图片提取错误:', e);
                    }
                    
                    // 方法4: 从页面文本中提取所有图片URL（正则表达式，更全面）
                    try {
                        var htmlText = document.documentElement.innerHTML;
                        // 匹配所有可能的图片URL（包括特殊格式如.jpg_.webp）
                        var patterns = [
                            // 【关键】匹配imgextra路径（最高优先级）
                            /https?:\\/\\/[^\\s"'<>)]*imgextra\\/[^\\s"'<>)]*/gi,
                            // 匹配包含.webp或.avif的URL（包括特殊格式）
                            /https?:\\/\\/[^\\s"'<>)]*[\\._](webp|avif)[^\\s"'<>)]*/gi,
                            // 匹配明确以图片扩展名结尾的URL（包括多个扩展名如.jpg_.webp）
                            /https?:\\/\\/[^\\s"'<>)]*\\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)[^\\s"'<>)]*[\\._]?(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)?[^\\s"'<>)]*(\\?[^\\s"'<>)]*)?/gi,
                            // 匹配CDN域名的URL
                            /https?:\\/\\/[^\\s"'<>)]*(alicdn|taobaocdn|tbcdn|360buyimg)[^\\s"'<>)]*/gi,
                            // 匹配引号中的图片URL
                            /["'](https?:\\/\\/[^\\s"'<>)]*(imgextra|alicdn|taobaocdn|tbcdn|360buyimg|\\/[^\\s"'<>)]*\\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif))[^\\s"'<>)]*)["']/gi
                        ];
                        patterns.forEach(function(pattern) {
                            var matches = htmlText.match(pattern);
                            if (matches) {
                                matches.forEach(function(match) {
                                    // 清理匹配结果（移除引号）
                                    var url = match.trim().replace(/^["']|["']$/g, '');
                                    if (url && url.startsWith('http') && !seen.has(url)) {
                                        seen.add(url);
                                        resources.push({
                                            url: url,
                                            type: 'regex',
                                            size: 0
                                        });
                                    }
                                });
                            }
                        });
                    } catch(e) {
                        console.error('正则表达式提取错误:', e);
                    }
                    
                    // 方法5: 从JavaScript变量中提取图片URL（淘宝页面常用）
                    try {
                        // 尝试从window对象中提取图片URL
                        if (window.TB && window.TB.detail) {
                            // 递归遍历对象，查找所有图片URL
                            function findImageUrls(obj, depth) {
                                if (depth > 5) return; // 限制深度
                                if (!obj) return;
                                
                                if (typeof obj === 'string') {
                                    if (obj.startsWith('http') && 
                                        (obj.includes('imgextra') || obj.includes('.webp') || obj.includes('.avif') ||
                                         obj.match(/\\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)/i))) {
                                        if (!seen.has(obj)) {
                                            seen.add(obj);
                                            resources.push({
                                                url: obj,
                                                type: 'js-object',
                                                size: 0
                                            });
                                        }
                                    }
                                } else if (Array.isArray(obj)) {
                                    obj.forEach(function(item) {
                                        findImageUrls(item, depth + 1);
                                    });
                                } else if (typeof obj === 'object') {
                                    for (var key in obj) {
                                        if (obj.hasOwnProperty(key)) {
                                            findImageUrls(obj[key], depth + 1);
                                        }
                                    }
                                }
                            }
                            
                            // 检查常见的淘宝数据对象
                            var tbObjects = ['images', 'image', 'picUrl', 'pic', 'photo', 'picture', 'img', 'itemInfo', 'skuMap', 'descInfo'];
                            tbObjects.forEach(function(key) {
                                try {
                                    var obj = window.TB.detail[key];
                                    if (obj) {
                                        findImageUrls(obj, 0);
                                    }
                                } catch(e) {}
                            });
                        }
                    } catch(e) {
                        console.error('JavaScript对象提取错误:', e);
                    }
                    
                    return resources;
                """)
                
                print(f"JavaScript Performance API提取到 {len(js_resources)} 个资源")
                js_added = 0
                for js_resource in js_resources:
                    js_url = js_resource.get('url', '')
                    if js_url and js_url not in network_resources:
                        # 清理URL
                        clean_url = js_url.split('#')[0].strip()
                        clean_url = self._clean_url(clean_url) if clean_url else None
                        if clean_url:
                            network_resources[clean_url] = {
                                'mime_type': '',
                                'initiator_type': js_resource.get('type', ''),
                                'response_type': ''
                            }
                            js_added += 1
                            if js_added <= 50:
                                print(f"  [JS Performance] 捕获资源: {clean_url[:80]} (type: {js_resource.get('type', 'N/A')})")
                
                print(f"从JavaScript Performance API中添加了 {js_added} 个资源到network_resources（当前总数: {len(network_resources)}）")
            except Exception as e:
                print(f"JavaScript Performance API提取失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 【关键改进】多次获取日志，每次获取后立即处理，确保不遗漏
            print("\n开始提取Network请求资源（多次获取以确保捕获所有请求）...")
            print(f"当前network_resources大小: {len(network_resources)}")
            
            # 获取并处理日志（多次，每次间隔获取）
            for attempt in range(5):  # 增加到5次，确保捕获所有请求
                print(f"\n第{attempt+1}次获取性能日志...")
                try:
                    logs = driver.get_log('performance')
                    print(f"第{attempt+1}次获取到 {len(logs)} 条性能日志")
                    
                    # 立即处理这批日志（不等待）
                    processed_count = 0
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            
                            # 处理Network.requestWillBeSent事件
                            if method == 'Network.requestWillBeSent':
                                params = message.get('message', {}).get('params', {})
                                request = params.get('request', {})
                                request_url = request.get('url', '')
                                request_id = params.get('requestId', '')
                                
                                if request_id and request_id not in captured_request_ids:
                                    captured_request_ids.add(request_id)
                                    initiator = params.get('initiator', {})
                                    initiator_type = initiator.get('type', '').lower() if initiator else ''
                                    
                                    # 【调试】打印initiatorType信息（前20个）
                                    if len(request_id_to_initiator) < 20:
                                        print(f"  [DEBUG] requestWillBeSent: RequestId={request_id[:20]}..., initiatorType={initiator_type}, URL={request_url[:60]}...")
                                    
                                    if request_id and initiator_type:
                                        request_id_to_initiator[request_id] = initiator_type
                                    
                                    if request_url:
                                        # 排除明显的非媒体文件
                                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                                        path = urlparse(request_url).path.lower()
                                        if path and any(path.endswith(ext) for ext in excluded_exts):
                                            continue
                                        
                                        # 【关键】如果initiatorType是'img'，直接添加
                                        # 注意：这对应浏览器Network面板中"Img"标签筛选的功能
                                        # initiatorType='img' 表示资源是由 <img> 标签发起的请求
                                        if initiator_type in ['img', 'image', 'imageset']:
                                            if request_url not in network_resources:
                                                # 尝试从requestId获取MIME类型，如果还没有则稍后在responseReceived中更新
                                                mime_type = request_id_to_mime.get(request_id, '')
                                                network_resources[request_url] = {
                                                    'mime_type': mime_type,
                                                    'initiator_type': initiator_type
                                                }
                                                processed_count += 1
                                                if processed_count <= 10:  # 只打印前10个
                                                    print(f"  [requestWillBeSent] 捕获到img类型资源: {request_url[:80]} (MIME: {mime_type})")
                            
                            # 处理Network.responseReceived事件
                            elif method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                response_url = response.get('url', '')
                                request_id = params.get('requestId', '')
                                
                                # 获取MIME类型（从mimeType字段，也可能需要检查headers）
                                content_type = response.get('mimeType', '').lower()
                                
                                # 【关键】检查response.type字段（Chrome DevTools Protocol可能在这里存储类型信息）
                                response_type = response.get('type', '').lower()
                                
                                # 如果mimeType为空，尝试从响应头中获取
                                if not content_type:
                                    headers = response.get('headers', {})
                                    if isinstance(headers, dict):
                                        # headers可能是字典格式
                                        content_type = headers.get('content-type', '').lower()
                                    elif isinstance(headers, list):
                                        # headers也可能是列表格式 [{'name': 'Content-Type', 'value': '...'}]
                                        for header in headers:
                                            if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                content_type = header.get('value', '').lower()
                                                break
                                
                                # 移除MIME类型中的参数（如charset=utf-8）
                                if content_type:
                                    content_type = content_type.split(';')[0].strip()
                                
                                # 【关键】如果response.type包含avif或webp，也认为是这些格式
                                if response_type in ['avif', 'webp']:
                                    if response_type == 'avif':
                                        content_type = 'image/avif'
                                    elif response_type == 'webp':
                                        content_type = 'image/webp'
                                
                                # 保存requestId到MIME类型的映射
                                if request_id and content_type:
                                    request_id_to_mime[request_id] = content_type
                                
                                # 【重要】移除request_id检查限制，处理所有响应（避免遗漏）
                                # if request_id and request_id not in captured_request_ids:
                                #     captured_request_ids.add(request_id)
                                initiator_type = request_id_to_initiator.get(request_id, '').lower()
                                
                                # 【调试】打印所有response信息（前20个，用于诊断）
                                if processed_count < 20:
                                    # 打印完整的response对象结构（用于调试）
                                    print(f"  [DEBUG] responseReceived: URL={response_url[:60]}...")
                                    print(f"    - mimeType: {response.get('mimeType', 'N/A')}")
                                    print(f"    - type: {response_type}")
                                    print(f"    - initiatorType: {initiator_type}")
                                    print(f"    - status: {response.get('status', 'N/A')}")
                                    print(f"    - headers: {str(response.get('headers', {}))[:100]}...")
                                    # 打印response对象的所有键（用于调试）
                                    print(f"    - response对象的所有键: {list(response.keys())[:10]}")
                                    
                                    # 【关键】检查响应头中的Content-Type
                                    headers = response.get('headers', {})
                                    if isinstance(headers, dict):
                                        content_type_header = headers.get('content-type', '')
                                        if content_type_header:
                                            print(f"    - Content-Type头: {content_type_header}")
                                    elif isinstance(headers, list):
                                        for header in headers:
                                            if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                print(f"    - Content-Type头: {header.get('value', '')}")
                                                break
                                
                                if not response_url:
                                    continue
                                
                                # 排除明显的非媒体文件
                                excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                                path = urlparse(response_url).path.lower()
                                if path and any(path.endswith(ext) for ext in excluded_exts):
                                    continue
                                
                                # 排除明显的非媒体MIME类型
                                excluded_mimes = ['application/javascript', 'text/javascript', 'text/css', 'text/html', 'font/', 'application/x-font']
                                if content_type and any(mime in content_type for mime in excluded_mimes):
                                    continue
                                
                                # 【关键改进】使用与首次日志处理相同的逻辑，确保捕获所有图片资源
                                # 【特别处理】明确检查avif和webp MIME类型
                                # 【关键】检查MIME类型，包括完整格式（image/gif）和简化格式（gif）
                                image_extensions = ['gif', 'png', 'jpg', 'jpeg', 'avif', 'webp', 'bmp', 'svg', 'ico', 'heic', 'heif']
                                is_avif_mime = content_type and ('image/avif' in content_type or content_type == 'avif' or 'avif' in content_type)
                                is_webp_mime = content_type and ('image/webp' in content_type or content_type == 'webp' or 'webp' in content_type)
                                # 检查完整格式：image/gif, image/png等
                                is_image_full_format = content_type and ('image' in content_type or content_type.startswith('image/'))
                                # 检查简化格式：gif, png, jpg等（不带image/前缀）
                                is_image_simple_format = content_type and content_type.lower() in image_extensions
                                is_image_by_mime = is_image_full_format or is_image_simple_format or is_avif_mime or is_webp_mime
                                is_video_by_mime = content_type and 'video' in content_type
                                
                                # 检查URL模式（即使MIME类型为空也要检查）
                                url_lower = response_url.lower()
                                is_image_by_url = self._is_image_url(response_url) or self._is_video_url(response_url)
                                
                                # 扩展关键字列表（与首次日志处理一致）
                                image_keywords = [
                                    'alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'jd.com/img', 'jd.com/image',
                                    'img.alicdn', 'gw.alicdn', 'cbu01.alicdn', 'sc01.alicdn', 'sc02.alicdn',
                                    '/img/', '/image/', '/pic/', '/photo/', '/picture/', '/upload/', '/media/',
                                    '/jfs/', '/imagetools/', '/uba/', '/devfe/', '/babel/', '/static/', '/assets/',
                                    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico', '.avif',
                                    'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload', 'media', 'avif',
                                    'imgextra', 'tps', 'oss', 'oss-cn', 'aliyuncs',
                                    '/imgextra/i', 'imgextra/i1/', 'imgextra/i2/', 'imgextra/i3/', 'imgextra/i4/',
                                    'imgextra/i5/', 'imgextra/i6/', 'imgextra/i7/', 'imgextra/i8/', 'imgextra/i9/',
                                    'jfs', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9', 'n10',
                                    'thumbnail', 'thumb', 'preview', 'original', 'large', 'small', 'medium'
                                ]
                                
                                is_image_by_keyword = any(keyword in url_lower for keyword in image_keywords)
                                
                                # 排除明显的非图片URL（除非明确是图片MIME类型）
                                excluded_patterns = [
                                    '/api/', '/ajax/', '/service/', '/script/', '/js/', '/css/',
                                    'login', 'logout', 'auth', 'token', 'session', 'cookie',
                                    'analytics', 'tracking', 'monitor', 'statistics', 'log',
                                    '.min.js', '.min.css', 'fontawesome', 'iconfont'
                                ]
                                
                                is_excluded = any(pattern in url_lower for pattern in excluded_patterns)
                                
                                # 【关键】如果满足以下任一条件，就添加资源：
                                # 1. MIME类型是image（最高优先级，即使被排除规则过滤也要添加）
                                # 2. MIME类型是video（最高优先级）
                                # 3. response.type是'avif'或'webp'（高优先级）
                                # 4. initiatorType是'img'（高优先级）
                                # 5. URL扩展名匹配图片/视频（高优先级）
                                # 6. URL包含图片关键字（且未被排除）
                                should_add = False
                                add_reason = ""
                                
                                # 【最高优先级】如果MIME类型是image，直接添加（不管排除规则）
                                if is_image_by_mime:
                                    should_add = True
                                    add_reason = f"MIME类型为image ({content_type})"
                                # 【最高优先级】如果MIME类型是video，直接添加
                                elif is_video_by_mime:
                                    should_add = True
                                    add_reason = f"MIME类型为video ({content_type})"
                                # 【高优先级】如果response.type是'avif'或'webp'，直接添加
                                elif response_type in ['avif', 'webp']:
                                    should_add = True
                                    add_reason = f"response.type为{response_type}"
                                # 【高优先级】如果initiatorType是'img'，直接添加
                                # 注意：这对应浏览器Network面板中"Img"标签筛选的功能
                                # initiatorType='img' 表示资源是由 <img> 标签发起的请求
                                elif initiator_type in ['img', 'image', 'imageset']:
                                    should_add = True
                                    add_reason = f"initiatorType为{initiator_type}（对应浏览器Img筛选）"
                                # 【高优先级】如果URL扩展名匹配图片/视频，直接添加
                                elif is_image_by_url:
                                    should_add = True
                                    add_reason = "URL扩展名匹配图片/视频"
                                # 【普通优先级】如果URL包含图片关键字（且未被排除）
                                elif is_image_by_keyword and not is_excluded:
                                    should_add = True
                                    add_reason = "URL包含图片关键字"
                                
                                if should_add and response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': content_type,
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    processed_count += 1
                                    if processed_count <= 50:
                                        print(f"  [responseReceived] 捕获资源 ({add_reason}): {response_url[:80]} (MIME: {content_type or 'N/A'}, initiator: {initiator_type or 'N/A'})")
                        
                        except (KeyError, json.JSONDecodeError, TypeError) as e:
                            continue
                    
                    print(f"第{attempt+1}次处理完成，新增 {processed_count} 个资源，当前总数: {len(network_resources)}")
                    
                    # 如果不是最后一次，等待一下再获取（让更多请求完成）
                    if attempt < 4:
                        time.sleep(5)  # 增加等待时间到5秒，确保所有资源加载完成
                
                except Exception as e:
                    print(f"第{attempt+1}次获取日志时出错: {e}")
                    continue
            
            # 最后一次获取所有日志并处理（确保没有遗漏）
            print("\n等待5秒后，最后一次获取所有日志并处理...")
            time.sleep(5)  # 额外等待5秒，确保所有资源加载完成
            try:
                final_logs = driver.get_log('performance')
                print(f"最后一次获取到 {len(final_logs)} 条性能日志")
                
                # 处理所有日志（包括之前可能遗漏的）
                final_processed = 0
                for log in final_logs:
                    try:
                        message = json.loads(log['message'])
                        method = message.get('message', {}).get('method', '')
                        
                        if method == 'Network.responseReceived':
                            params = message.get('message', {}).get('params', {})
                            response = params.get('response', {})
                            response_url = response.get('url', '')
                            request_id = params.get('requestId', '')
                            
                            # 获取MIME类型（从mimeType字段，也可能需要检查headers）
                            content_type = response.get('mimeType', '').lower()
                            
                            # 【关键】检查response.type字段（Chrome DevTools Protocol可能在这里存储类型信息）
                            response_type = response.get('type', '').lower()
                            
                            # 如果mimeType为空，尝试从响应头中获取
                            if not content_type:
                                headers = response.get('headers', {})
                                if isinstance(headers, dict):
                                    # headers可能是字典格式
                                    content_type = headers.get('content-type', '').lower()
                                elif isinstance(headers, list):
                                    # headers也可能是列表格式 [{'name': 'Content-Type', 'value': '...'}]
                                    for header in headers:
                                        if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                            content_type = header.get('value', '').lower()
                                            break
                            
                            # 移除MIME类型中的参数（如charset=utf-8）
                            if content_type:
                                content_type = content_type.split(';')[0].strip()
                            
                            # 【关键】如果response.type包含avif或webp，也认为是这些格式
                            if response_type in ['avif', 'webp']:
                                if response_type == 'avif':
                                    content_type = 'image/avif'
                                elif response_type == 'webp':
                                    content_type = 'image/webp'
                            
                            # 保存requestId到MIME类型的映射
                            if request_id and content_type:
                                request_id_to_mime[request_id] = content_type
                            
                            if not response_url:
                                continue
                            
                            # 排除明显的非媒体文件
                            excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                            path = urlparse(response_url).path.lower()
                            if path and any(path.endswith(ext) for ext in excluded_exts):
                                continue
                            
                            # 排除明显的非媒体MIME类型
                            excluded_mimes = ['application/javascript', 'text/javascript', 'text/css', 'text/html', 'font/', 'application/x-font']
                            if content_type and any(mime in content_type for mime in excluded_mimes):
                                continue
                            
                            # 获取initiatorType
                            initiator_type = request_id_to_initiator.get(request_id, '').lower()
                            
                            # 【关键】如果initiatorType是'img'，直接添加（无论MIME类型是什么）
                            if initiator_type in ['img', 'image', 'imageset']:
                                if response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': content_type,
                                        'initiator_type': initiator_type,
                                        'response_type': response_type  # 保存response.type
                                    }
                                    final_processed += 1
                                    if final_processed <= 10:
                                        print(f"  [final] 捕获到img类型资源: {response_url[:80]} (MIME: {content_type}, type: {response_type})")
                            
                            # 【关键】如果response.type是'avif'或'webp'，直接添加
                            elif response_type in ['avif', 'webp']:
                                if response_url not in network_resources:
                                    mime_to_set = 'image/avif' if response_type == 'avif' else 'image/webp'
                                    network_resources[response_url] = {
                                        'mime_type': mime_to_set,
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    final_processed += 1
                                    if final_processed <= 10:
                                        print(f"  [final] 捕获到{response_type}类型资源（通过response.type）: {response_url[:80]} (MIME: {content_type})")
                            
                            # 【关键】如果MIME类型是image/avif或image/webp，直接添加（即使initiatorType不是img）
                            # 使用更宽松的匹配（包含检查）
                            elif content_type and ('image/avif' in content_type or content_type == 'avif' or 'avif' in content_type):
                                if response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': 'image/avif',
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    final_processed += 1
                                    if final_processed <= 10:
                                        print(f"  [final] 捕获到avif类型资源: {response_url[:80]} (MIME: {content_type})")
                            elif content_type and ('image/webp' in content_type or content_type == 'webp' or 'webp' in content_type):
                                if response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': 'image/webp',
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    final_processed += 1
                                    if final_processed <= 10:
                                        print(f"  [final] 捕获到webp类型资源: {response_url[:80]} (MIME: {content_type})")
                            
                            # 如果MIME类型是image/video，直接添加
                            elif content_type and ('image' in content_type or 'video' in content_type):
                                if response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': content_type,
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    final_processed += 1
                            
                            # 检查URL扩展名
                            elif self._is_image_url(response_url) or self._is_video_url(response_url):
                                if response_url not in network_resources:
                                    network_resources[response_url] = {
                                        'mime_type': content_type,
                                        'initiator_type': initiator_type,
                                        'response_type': response_type
                                    }
                                    final_processed += 1
                            
                            # 【关键改进】更宽松的条件：只要URL包含任何图片相关关键字，就添加
                            else:
                                url_lower = response_url.lower()
                                # 非常宽松的条件：只要URL中包含图片相关关键字，就认为是图片
                                if any(keyword in url_lower for keyword in [
                                    'alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'jd.com/img', 'jd.com/image',
                                    '/img/', '/image/', '/pic/', '/photo/', '/picture/', '/upload/', '/media/',
                                    '/jfs/', '/imagetools/', '/uba/', '/devfe/', '/babel/',
                                    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico', '.avif',
                                    'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload', 'media', 'avif'
                                ]):
                                    if response_url not in network_resources:
                                        network_resources[response_url] = {
                                            'mime_type': content_type,
                                            'initiator_type': initiator_type,
                                            'response_type': response_type
                                        }
                                        final_processed += 1
                        
                        elif method == 'Network.requestWillBeSent':
                            params = message.get('message', {}).get('params', {})
                            request = params.get('request', {})
                            request_url = request.get('url', '')
                            request_id = params.get('requestId', '')
                            
                            if request_id and request_id not in captured_request_ids:
                                captured_request_ids.add(request_id)
                                initiator = params.get('initiator', {})
                                initiator_type = initiator.get('type', '').lower() if initiator else ''
                                
                                if request_id and initiator_type:
                                    request_id_to_initiator[request_id] = initiator_type
                                
                                if request_url:
                                    # 排除明显的非媒体文件
                                    excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2', '.ttf']
                                    path = urlparse(request_url).path.lower()
                                    if path and any(path.endswith(ext) for ext in excluded_exts):
                                        continue
                                    
                                    # 【关键】如果initiatorType是'img'，直接添加（无论MIME类型是什么）
                                    if initiator_type in ['img', 'image', 'imageset']:
                                        if request_url not in network_resources:
                                            # 尝试从requestId获取MIME类型，如果还没有则稍后在responseReceived中更新
                                            mime_type = request_id_to_mime.get(request_id, '')
                                            network_resources[request_url] = {
                                                'mime_type': mime_type,
                                                'initiator_type': initiator_type
                                            }
                                            final_processed += 1
                                            if final_processed <= 10:
                                                print(f"  [requestWillBeSent] 捕获到img类型资源: {request_url[:80]}")
                            
                            # 【关键】处理Network.loadingFinished事件（从响应体中提取图片URL）
                            elif method == 'Network.loadingFinished':
                                params = message.get('message', {}).get('params', {})
                                request_id = params.get('requestId', '')
                                
                                if not request_id:
                                    continue
                                
                                # 尝试获取响应体（从API响应中提取图片URL）
                                try:
                                    response_body_result = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                    if response_body_result and 'body' in response_body_result:
                                        response_body = response_body_result['body']
                                        
                                        # 检查响应体是否包含图片相关关键字
                                        response_body_lower = response_body.lower()
                                        if (len(response_body) > 100 and
                                            (any(keyword in response_body_lower for keyword in ['alicdn', 'taobaocdn', 'tbcdn', 'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload', 'http']) or
                                             any(ext in response_body_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.mp4', '.webm', '.avi', '.mov']))):
                                            
                                            # 正则表达式提取图片URL
                                            import re as re_module
                                            json_img_urls = re_module.findall(
                                                r'https?://[^\s"\'<>\)]+(?:alicdn|taobaocdn|tbcdn|img|image|pic|photo|cdn|static)[^\s"\'<>\)]*(?:\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif|mp4|webm|avi|mov|flv|mkv))?(?:\?[^\s"\'<>\)]*)?',
                                                response_body, re_module.IGNORECASE
                                            )
                                            if json_img_urls:
                                                for img_url in json_img_urls:
                                                    if img_url not in network_resources:
                                                        network_resources[img_url] = {
                                                            'mime_type': '',
                                                            'initiator_type': ''
                                                        }
                                                        final_processed += 1
                                            
                                            # JSON解析提取（递归）
                                            import json as json_module
                                            try:
                                                json_data = json_module.loads(response_body)
                                                def extract_urls_from_json(obj, urls_set, depth=0):
                                                    if depth > 15:
                                                        return
                                                    if isinstance(obj, dict):
                                                        for key, value in obj.items():
                                                            key_lower = str(key).lower()
                                                            if isinstance(value, str):
                                                                if value.startswith('http'):
                                                                    value_lower = value.lower()
                                                                    if (any(ext in value_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif', '.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv', '.m3u8']) or 
                                                                        any(keyword in value_lower for keyword in ['alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload', 'media', 'picture', 'gallery']) or
                                                                        any(keyword in key_lower for keyword in ['img', 'image', 'pic', 'photo', 'url', 'src', 'thumb', 'thumbnail', 'cover', 'poster', 'picurl', 'picurls', 'imageurl', 'imageurls'])):
                                                                        urls_set.add(value)
                                                                elif 'http' in value or '//' in value:
                                                                    import re
                                                                    url_pattern = r'https?://[^\s<>"\'\)]+|//[^\s<>"\'\)]+'
                                                                    matches = re.findall(url_pattern, value)
                                                                    for match in matches:
                                                                        match_lower = match.lower()
                                                                        if (any(ext in match_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif', '.mp4', '.webm', '.avi', '.mov']) or 
                                                                            any(keyword in match_lower for keyword in ['alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'img', 'image', 'pic', 'photo', 'cdn', 'static', 'upload'])):
                                                                            if match.startswith('//'):
                                                                                match = 'https:' + match
                                                                            urls_set.add(match)
                                                            elif isinstance(value, (dict, list)):
                                                                extract_urls_from_json(value, urls_set, depth + 1)
                                                    elif isinstance(obj, list):
                                                        for item in obj:
                                                            extract_urls_from_json(item, urls_set, depth + 1)
                                                
                                                json_urls = set()
                                                extract_urls_from_json(json_data, json_urls)
                                                if json_urls:
                                                    for json_url in json_urls:
                                                        if json_url not in network_resources:
                                                            network_resources[json_url] = {
                                                                'mime_type': '',
                                                                'initiator_type': ''
                                                            }
                                                            final_processed += 1
                                            except:
                                                pass
                                except:
                                    pass
                    
                    except (KeyError, json.JSONDecodeError, TypeError):
                        continue
                
                print(f"最后一次处理完成，新增 {final_processed} 个资源")
            
            except Exception as e:
                print(f"最后一次获取日志时出错: {e}")
            
            print(f"\n从Network请求中提取到 {len(network_resources)} 个资源URL")
            print(f"requestId到initiatorType映射: {len(request_id_to_initiator)} 条记录")
            print(f"requestId到MIME类型映射: {len(request_id_to_mime)} 条记录")
            
            # 统计initiatorType为img的资源数量
            img_type_count = 0
            for req_id, init_type in request_id_to_initiator.items():
                if init_type in ['img', 'image', 'imageset']:
                    img_type_count += 1
            
            # 统计MIME类型为avif和webp的资源数量（从request_id_to_mime）
            avif_mime_count = 0
            webp_mime_count = 0
            for req_id, mime in request_id_to_mime.items():
                if mime:
                    mime_lower = mime.lower()
                    if 'avif' in mime_lower or mime_lower == 'avif':
                        avif_mime_count += 1
                    elif 'webp' in mime_lower or mime_lower == 'webp':
                        webp_mime_count += 1
            
            # 统计network_resources中MIME类型为avif和webp的资源数量
            avif_in_resources = 0
            webp_in_resources = 0
            avif_by_type = 0  # 通过response.type识别的avif
            webp_by_type = 0  # 通过response.type识别的webp
            for url, info in network_resources.items():
                mime = info.get('mime_type', '').lower()
                resp_type = info.get('response_type', '').lower()
                if 'avif' in mime or mime == 'avif' or resp_type == 'avif':
                    avif_in_resources += 1
                    if resp_type == 'avif':
                        avif_by_type += 1
                elif 'webp' in mime or mime == 'webp' or resp_type == 'webp':
                    webp_in_resources += 1
                    if resp_type == 'webp':
                        webp_by_type += 1
            
            print(f"统计信息：")
            print(f"  - initiatorType为'img'的资源: {img_type_count} 个")
            print(f"  - MIME类型包含'avif'的资源（从requestId映射）: {avif_mime_count} 个")
            print(f"  - MIME类型包含'webp'的资源（从requestId映射）: {webp_mime_count} 个")
            print(f"  - network_resources中MIME类型包含'avif'的资源: {avif_in_resources} 个（其中通过response.type识别: {avif_by_type} 个）")
            print(f"  - network_resources中MIME类型包含'webp'的资源: {webp_in_resources} 个（其中通过response.type识别: {webp_by_type} 个）")
            
            # 打印一些示例MIME类型（用于调试）
            if request_id_to_mime:
                print(f"\n示例MIME类型（前20个，用于调试）:")
                count = 0
                for req_id, mime in list(request_id_to_mime.items())[:20]:
                    print(f"  {count+1}. RequestId: {req_id[:20]}... MIME: {mime}")
                    count += 1
                
                # 特别打印所有包含avif或webp的MIME类型
                avif_webp_mimes = []
                for req_id, mime in request_id_to_mime.items():
                    if mime and ('avif' in mime.lower() or 'webp' in mime.lower()):
                        avif_webp_mimes.append((req_id, mime))
                
                if avif_webp_mimes:
                    print(f"\n找到 {len(avif_webp_mimes)} 个包含'avif'或'webp'的MIME类型:")
                    for req_id, mime in avif_webp_mimes[:20]:
                        print(f"  - RequestId: {req_id[:30]}... MIME: {mime}")
                else:
                    print(f"\n警告：未找到任何包含'avif'或'webp'的MIME类型！")
                    print("这可能意味着：")
                    print("  1. Chrome DevTools Protocol返回的MIME类型格式不同")
                    print("  2. 需要检查响应头中的Content-Type")
                    print("  3. 或者MIME类型为空，需要从其他来源获取")
                    print("  4. 【重要】可能需要检查response.type字段而不是mimeType字段")
            
            # 【新增】打印所有response.type为avif或webp的资源
            avif_webp_by_type = []
            for url, info in network_resources.items():
                resp_type = info.get('response_type', '').lower()
                if resp_type in ['avif', 'webp']:
                    avif_webp_by_type.append((url, resp_type, info.get('mime_type', '')))
            
            if avif_webp_by_type:
                print(f"\n找到 {len(avif_webp_by_type)} 个response.type为'avif'或'webp'的资源:")
                for url, resp_type, mime in avif_webp_by_type[:20]:
                    print(f"  - Type: {resp_type}, MIME: {mime}, URL: {url[:80]}...")
            else:
                print(f"\n警告：未找到任何response.type为'avif'或'webp'的资源！")
                print("请检查Chrome DevTools Protocol返回的response对象结构")
            
            print(f"通过initiatorType='img'识别到 {img_type_count} 个图片资源")
            
            # 输出前50个资源URL用于调试
            if len(network_resources) > 0:
                print("前50个资源URL示例:")
                for i, res_url in enumerate(list(network_resources)[:50]):
                    print(f"  {i+1}. {res_url}")
            
            # 通过执行JavaScript获取所有加载的资源（Performance API）
            try:
                resource_script = """
                var resources = [];
                // 方法1: 使用Performance API获取所有资源
                if (window.performance && window.performance.getEntriesByType) {
                    var entries = window.performance.getEntriesByType('resource');
                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        var url = entry.name;
                        
                        // 排除明显的非媒体文件（只排除.js, .css, .html等）
                        var excludedExts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt'];
                        var path = url.toLowerCase();
                        var isExcluded = false;
                        // 只在路径中检查，不在查询参数中
                        for (var k = 0; k < excludedExts.length; k++) {
                            if (path.endsWith(excludedExts[k])) {
                                isExcluded = true;
                                break;
                            }
                        }
                        if (isExcluded) {
                            continue;
                        }
                        
                        // 检查是否是图片或视频资源（放宽条件，只要包含扩展名即可）
                        var imageExts = /\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)/i;
                        var videoExts = /\.(mp4|webm|avi|mov|flv|mkv|m3u8|ts|f4v|mpg|mpeg|m4v)/i;
                        
                        // 如果是img或video类型的资源，直接添加
                        if (entry.initiatorType === 'img') {
                            resources.push(url);
                        } else if (entry.initiatorType === 'video') {
                            resources.push(url);
                        } else if (imageExts.test(url)) {
                            resources.push(url);
                        } else if (videoExts.test(url)) {
                            resources.push(url);
                        } else if (url.includes('alicdn.com') || url.includes('taobaocdn.com') || url.includes('tbcdn.cn') || 
                                   url.includes('360buyimg.com') || url.includes('jd.com/img') || url.includes('jd.com/image') ||
                                   url.includes('cdn') || url.includes('img') || url.includes('image') || url.includes('static') ||
                                   url.includes('pic') || url.includes('photo') || url.includes('upload') || url.includes('media') ||
                                   url.includes('picture') || url.includes('gallery')) {
                            // 如果是CDN域名或其他常见图片域名，检查是否包含图片或视频扩展名（特别注意webp）
                            // 或者URL路径包含图片相关关键字（如/jfs/, /imagetools/等）
                            if (imageExts.test(url) || videoExts.test(url) || 
                                url.includes('image') || url.includes('img') || url.includes('webp') || url.includes('avif') || 
                                url.includes('pic') || url.includes('photo') || url.includes('picture') ||
                                url.includes('video') || url.includes('mp4') || url.includes('bmp') ||
                                url.includes('/jfs/') || url.includes('/imagetools/') || url.includes('/img/') ||
                                url.includes('/image/') || url.includes('/pic/') || url.includes('/photo/')) {
                                resources.push(url);
                            }
                        }
                        // 检查URL路径中是否包含图片或视频相关关键字（更宽松的条件，包括京东路径）
                        else if (url.includes('/image/') || url.includes('/img/') || url.includes('/pic/') || 
                                url.includes('/photo/') || url.includes('/media/') || url.includes('/picture/') ||
                                url.includes('/upload/') || url.includes('/jfs/') || url.includes('/imagetools/') ||
                                url.includes('/uba/') || url.includes('/devfe/') || url.includes('/babel/') ||
                                url.includes('.jpg') || url.includes('.jpeg') || url.includes('.png') ||
                                url.includes('.gif') || url.includes('.webp') || url.includes('.bmp') ||
                                url.includes('.svg') || url.includes('.ico') || url.includes('.avif') || url.includes('/video/') ||
                                url.includes('.mp4') || url.includes('.webm') || url.includes('.avi') ||
                                url.includes('.mov') || url.includes('.flv') || url.includes('.mkv') ||
                                url.includes('.m3u8') || url.includes('.ts') || url.includes('.f4v') ||
                                url.includes('.mpg') || url.includes('.mpeg') || url.includes('.m4v')) {
                            // 只要URL中包含这些路径关键字，就认为是图片或视频
                            resources.push(url);
                        }
                    }
                }
                
                // 方法2: 查找所有img标签的src属性（包括懒加载的，支持更多属性，包括webp）
                var imgs = document.querySelectorAll('img');
                for (var i = 0; i < imgs.length; i++) {
                    var img = imgs[i];
                    // 尝试更多可能的属性（包括webp相关的属性）
                    var src = img.src || img.getAttribute('data-src') || img.getAttribute('data-original') || 
                             img.getAttribute('data-lazy-src') || img.getAttribute('data-url') ||
                             img.getAttribute('data-img') || img.getAttribute('data-image') ||
                             img.getAttribute('lazy-src') || img.getAttribute('original-src');
                    if (src && (src.startsWith('http') || src.startsWith('//')) && !src.startsWith('data:')) {
                        // 如果是相对URL，转换为绝对URL
                        if (src.startsWith('//')) {
                            src = window.location.protocol + src;
                        }
                        resources.push(src);
                    }
                    // 处理srcset属性（可能包含多个URL，包括webp）
                    var srcset = img.getAttribute('srcset');
                    if (srcset) {
                        var srcsetUrls = srcset.split(',');
                        for (var j = 0; j < srcsetUrls.length; j++) {
                            var url = srcsetUrls[j].trim().split(' ')[0];
                            if (url && (url.startsWith('http') || url.startsWith('//')) && !url.startsWith('data:')) {
                                if (url.startsWith('//')) {
                                    url = window.location.protocol + url;
                                }
                                resources.push(url);
                            }
                        }
                    }
                }
                
                // 方法3: 查找所有video标签的src属性和source子标签
                var videos = document.querySelectorAll('video');
                for (var i = 0; i < videos.length; i++) {
                    var video = videos[i];
                    // 获取video的src
                    var src = video.src || video.getAttribute('data-src') || video.getAttribute('data-url');
                    if (src && src.startsWith('http') && !src.startsWith('data:')) {
                        resources.push(src);
                    }
                    // 获取source子标签的src
                    var sources = video.querySelectorAll('source');
                    for (var j = 0; j < sources.length; j++) {
                        var sourceSrc = sources[j].src || sources[j].getAttribute('data-src');
                        if (sourceSrc && sourceSrc.startsWith('http') && !sourceSrc.startsWith('data:')) {
                            resources.push(sourceSrc);
                        }
                    }
                }
                
                // 方法4: 查找所有audio标签（某些网站可能用audio播放视频）
                var audios = document.querySelectorAll('audio');
                for (var i = 0; i < audios.length; i++) {
                    var audio = audios[i];
                    var src = audio.src || audio.getAttribute('data-src');
                    if (src && src.startsWith('http') && !src.startsWith('data:')) {
                        // 检查是否是视频格式
                        if (src.match(/\.(mp4|webm|avi|mov|flv|mkv|m3u8|ts|f4v|mpg|mpeg|m4v)(\?|$)/i)) {
                            resources.push(src);
                        }
                    }
                }
                
                // 方法5: 查找所有可能的视频API响应（通过window对象）
                try {
                    // 尝试从全局变量中查找视频URL（某些网站会在window对象中存储）
                    if (window.TB && window.TB.detail && window.TB.detail.videos) {
                        var videos = window.TB.detail.videos;
                        if (Array.isArray(videos)) {
                            videos.forEach(function(v) {
                                if (v && v.url && v.url.startsWith('http')) {
                                    resources.push(v.url);
                                }
                            });
                        }
                    }
                    // 尝试从window.TB.detail.images中提取图片URL（淘宝页面）
                    if (window.TB && window.TB.detail && window.TB.detail.images) {
                        var images = window.TB.detail.images;
                        if (Array.isArray(images)) {
                            images.forEach(function(img) {
                                if (img && img.url && img.url.startsWith('http')) {
                                    resources.push(img.url);
                                } else if (img && typeof img === 'string' && img.startsWith('http')) {
                                    resources.push(img);
                                }
                            });
                        }
                    }
                    // 尝试从window.TB.detail.skuMap中提取图片（淘宝商品详情页）
                    if (window.TB && window.TB.detail && window.TB.detail.skuMap) {
                        var skuMap = window.TB.detail.skuMap;
                        for (var key in skuMap) {
                            if (skuMap.hasOwnProperty(key)) {
                                var sku = skuMap[key];
                                if (sku && sku.image && sku.image.startsWith('http')) {
                                    resources.push(sku.image);
                                }
                                if (sku && sku.picUrl && sku.picUrl.startsWith('http')) {
                                    resources.push(sku.picUrl);
                                }
                            }
                        }
                    }
                    // 尝试从window.TB.detail.descInfo中提取图片（商品描述图片）
                    if (window.TB && window.TB.detail && window.TB.detail.descInfo) {
                        var descInfo = window.TB.detail.descInfo;
                        if (descInfo.images && Array.isArray(descInfo.images)) {
                            descInfo.images.forEach(function(img) {
                                if (img && img.startsWith('http')) {
                                    resources.push(img);
                                } else if (img && img.url && img.url.startsWith('http')) {
                                    resources.push(img.url);
                                }
                            });
                        }
                    }
                    // 尝试从window.TB.detail.itemInfo中提取图片
                    if (window.TB && window.TB.detail && window.TB.detail.itemInfo) {
                        var itemInfo = window.TB.detail.itemInfo;
                        if (itemInfo.images && Array.isArray(itemInfo.images)) {
                            itemInfo.images.forEach(function(img) {
                                if (img && img.startsWith('http')) {
                                    resources.push(img);
                                } else if (img && img.url && img.url.startsWith('http')) {
                                    resources.push(img.url);
                                }
                            });
                        }
                        if (itemInfo.picUrl && itemInfo.picUrl.startsWith('http')) {
                            resources.push(itemInfo.picUrl);
                        }
                    }
                    // 尝试从window.g_config中提取图片（淘宝页面可能使用）
                    if (window.g_config && window.g_config.data) {
                        var data = window.g_config.data;
                        if (data.images && Array.isArray(data.images)) {
                            data.images.forEach(function(img) {
                                if (img && img.startsWith('http')) {
                                    resources.push(img);
                                } else if (img && img.url && img.url.startsWith('http')) {
                                    resources.push(img.url);
                                }
                            });
                        }
                    }
                    // 尝试从window.runParams中提取图片（淘宝页面可能使用）
                    if (window.runParams && window.runParams.data) {
                        var data = window.runParams.data;
                        if (data.images && Array.isArray(data.images)) {
                            data.images.forEach(function(img) {
                                if (img && img.startsWith('http')) {
                                    resources.push(img);
                                } else if (img && img.url && img.url.startsWith('http')) {
                                    resources.push(img.url);
                                }
                            });
                        }
                    }
                } catch(e) {
                    console.log('提取window对象中的资源时出错:', e);
                }
                
                // 方法6: 从所有可能的JavaScript变量中提取图片URL（更全面的方法）
                try {
                    // 遍历所有全局变量，查找可能包含图片URL的对象
                    var globalVars = ['TB', 'g_config', 'runParams', 'itemData', 'skuData', 'detailData'];
                    globalVars.forEach(function(varName) {
                        try {
                            var obj = window[varName];
                            if (obj && typeof obj === 'object') {
                                // 递归查找所有包含图片URL的属性
                                function findImageUrls(obj, depth) {
                                    if (depth > 5) return; // 防止无限递归
                                    if (!obj || typeof obj !== 'object') return;
                                    
                                    for (var key in obj) {
                                        if (!obj.hasOwnProperty(key)) continue;
                                        var value = obj[key];
                                        
                                        // 如果值是字符串且看起来像图片URL
                                        if (typeof value === 'string' && value.startsWith('http') && 
                                            (value.match(/\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|avif|mp4|webm|avi|mov|flv|mkv)(\?|$)/i) ||
                                             value.match(/(alicdn|taobaocdn|tbcdn|img|image|pic|photo|cdn)/i))) {
                                            resources.push(value);
                                        }
                                        
                                        // 如果值是数组，递归查找
                                        if (Array.isArray(value)) {
                                            value.forEach(function(item) {
                                                findImageUrls(item, depth + 1);
                                            });
                                        }
                                        
                                        // 如果值是对象，递归查找
                                        if (value && typeof value === 'object') {
                                            findImageUrls(value, depth + 1);
                                        }
                                    }
                                }
                                findImageUrls(obj, 0);
                            }
                        } catch(e) {}
                    });
                } catch(e) {
                    console.log('从全局变量提取资源时出错:', e);
                }
                
                // 去重
                return Array.from(new Set(resources));
                """
                js_resources = driver.execute_script(resource_script)
                js_resource_count = 0
                if js_resources:
                    print(f"从JavaScript Performance API获取到 {len(js_resources)} 个资源")
                    for js_url in js_resources:
                        if js_url and js_url.startswith('http'):
                            if js_url not in network_resources:
                                # 从Performance API获取的资源没有MIME类型信息，稍后会在responseReceived中更新
                                network_resources[js_url] = {
                                    'mime_type': '',
                                    'initiator_type': ''
                                }
                                js_resource_count += 1
                    print(f"从JavaScript Performance API中添加了 {js_resource_count} 个新资源")
                
            except Exception as e:
                import traceback
                print(f"通过JavaScript获取资源时出错: {e}")
                print(traceback.format_exc())
            
            # 将network_resources添加到资源列表（只保留 initiatorType='img' 的资源，不做任何URL处理）
            if network_resources:
                print(f"\n开始将 {len(network_resources)} 个网络请求资源添加到列表...")
                network_count_before = len(self.resources)
                existing_urls = {r['url'] for r in self.resources}  # 获取已存在的URL集合
                added_count = 0
                skipped_count = 0
                skipped_urls = []
                
                # 统计initiatorType为'img'的资源数量
                img_initiator_count = 0
                
                for resource_url, resource_info in network_resources.items():
                    initiator_type = resource_info.get('initiator_type', '').lower()
                    mime_type = resource_info.get('mime_type', '').lower()
                    
                    # 【放宽筛选条件】保留以下资源：
                    # 1. initiatorType='img' 的资源
                    # 2. MIME类型为 image/* 的资源（包括所有图片格式）
                    is_img_initiator = initiator_type in ['img', 'image', 'imageset']
                    # 【关键】通过MIME类型筛选（对应浏览器Network面板的"Type"列）
                    # 包括完整格式：image/gif, image/png, image/jpeg, image/webp, image/avif等
                    # 也包括简化格式：gif, png, jpg, jpeg, avif, webp等（不带image/前缀）
                    image_extensions = ['gif', 'png', 'jpg', 'jpeg', 'avif', 'webp', 'bmp', 'svg', 'ico', 'heic', 'heif']
                    is_image_mime = False
                    if mime_type:
                        mime_lower = mime_type.lower()
                        # 检查完整格式：image/gif, image/png等
                        if 'image' in mime_lower or mime_lower.startswith('image/'):
                            is_image_mime = True
                        # 检查简化格式：gif, png, jpg等（不带image/前缀）
                        elif mime_lower in image_extensions:
                            is_image_mime = True
                    
                    if not is_img_initiator and not is_image_mime:
                        skipped_count += 1
                        skipped_urls.append((resource_url, f"initiatorType={initiator_type}, MIME={mime_type}"))
                        continue
                    
                    # 【图片链接不做任何处理，直接使用原始URL】
                    original_url = resource_url  # 保持原始URL，不做任何处理
                    
                    # 检查是否已存在（去重）
                    if original_url in existing_urls:
                        skipped_count += 1
                        skipped_urls.append((original_url, "已存在"))
                        continue
                    
                    # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                    if not self.is_accessible_resource(original_url):
                        skipped_count += 1
                        skipped_urls.append((original_url, "无法访问（无效URL模式）"))
                        continue
                    
                    # 生成文件名（仅用于显示，不影响URL）
                    name = os.path.basename(urlparse(original_url).path) or f"图片_{len(self.resources) + 1}"
                    if not name or name == '':
                        name = f"图片_{len(self.resources) + 1}"
                    name = re.sub(r'[<>:"/\\|?*]', '_', name)
                    
                    # 添加到资源列表（使用原始URL，不做任何处理）
                    self.resources.append({
                        'name': name,
                        'url': original_url,  # 使用原始URL，不做任何处理
                        'type': 'image',
                        'mime_type': mime_type
                    })
                    existing_urls.add(original_url)
                    added_count += 1
                    if is_img_initiator:
                        img_initiator_count += 1
                
                print(f"\n从网络请求中添加了 {added_count} 个资源到列表（跳过 {skipped_count} 个）")
                print(f"统计信息：")
                print(f"  - initiatorType为'img'的资源: {img_initiator_count} 个")
                print(f"  - 总共添加的图片资源: {added_count} 个（包括initiatorType='img'和MIME类型为image/*的资源）")
                print(f"  - network_resources总数: {len(network_resources)} 个")
                
                # 统计MIME类型分布（用于调试，对应浏览器Network面板的"Type"列）
                mime_types = {}
                for url, info in network_resources.items():
                    mime = info.get('mime_type', '').lower()
                    if mime:
                        mime_types[mime] = mime_types.get(mime, 0) + 1
                if mime_types:
                    print(f"  - MIME类型分布（前10个，对应浏览器Type列）:")
                    for mime, count in sorted(mime_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                        print(f"    {mime}: {count} 个")
                
                # 显示被跳过的资源URL和原因
                if skipped_count > 0:
                    print(f"被跳过的 {min(skipped_count, 20)} 个资源URL和原因:")
                    for i, (skipped_url, reason) in enumerate(skipped_urls[:20]):
                        print(f"  {i+1}. {skipped_url[:100]}... 原因: {reason}")
                if added_count == 0 and len(network_resources) > 0:
                    print(f"警告：网络请求中捕获到 {len(network_resources)} 个资源，但都没有添加到列表！")
                    print("所有被跳过的资源URL:")
                    for i, (skipped_url, reason) in enumerate(skipped_urls):
                        print(f"  {i+1}. {skipped_url} 原因: {reason}")
            
            # 【新增】专门提取所有MIME类型为image/*的资源（包括image/jpeg, image/png, image/avif等所有图片类型）
            print("\n" + "=" * 80)
            print("【专门提取】提取所有MIME类型为image/*的资源（包括所有图片类型：jpeg, png, avif, gif, webp等）...")
            print("=" * 80)
            
            # 【关键】从API响应体中提取所有图片URL（包括imgextra路径和京东图片路径）
            print("方法-1: 从API响应体中提取所有图片URL（包括imgextra路径和京东图片路径）...")
            imgextra_from_api_responses = []
            jd_images_from_api = []  # 京东图片
            try:
                # 获取所有CDP日志（在保存之前先获取一次）
                print("  获取CDP日志（用于提取API响应）...")
                logs = driver.get_log('performance')
                print(f"  检查 {len(logs)} 条CDP日志，查找API响应...")
                
                if len(logs) == 0:
                    print("  警告：CDP日志为空，尝试等待后重新获取...")
                    time.sleep(2)
                    logs = driver.get_log('performance')
                    print(f"  重新获取后得到 {len(logs)} 条CDP日志")
                
                api_response_count = 0
                processed_count = 0
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        method = message.get('message', {}).get('method', '')
                        
                        if method == 'Network.responseReceived':
                            params = message.get('message', {}).get('params', {})
                            response = params.get('response', {})
                            response_url = response.get('url', '')
                            request_id = params.get('requestId', '')
                            
                            # 检查是否是API请求（JSON响应）
                            content_type = response.get('mimeType', '').lower()
                            processed_count += 1
                            
                            if 'application/json' in content_type or 'text/json' in content_type:
                                api_response_count += 1
                                if api_response_count <= 5:  # 只打印前5个API响应
                                    print(f"  找到API响应 #{api_response_count}: {response_url[:80]}... (MIME: {content_type})")
                                
                                # 尝试获取响应体
                                try:
                                    response_body_result = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                    if response_body_result and 'body' in response_body_result:
                                        response_body = response_body_result['body']
                                        
                                        # 解析JSON
                                        try:
                                            if response_body_result.get('base64Encoded', False):
                                                import base64
                                                response_body = base64.b64decode(response_body).decode('utf-8')
                                            
                                            json_data = json.loads(response_body)
                                            
                                            # 递归搜索JSON中的所有imgextra路径的图片URL
                                            def extract_imgextra_from_json(obj, depth=0):
                                                if depth > 10:
                                                    return
                                                
                                                if isinstance(obj, str):
                                                    # 【关键】先解码URL，确保能正确匹配
                                                    import urllib.parse
                                                    try:
                                                        decoded_obj = urllib.parse.unquote(obj)
                                                        # 处理多次编码的情况
                                                        while '%' in decoded_obj and decoded_obj != urllib.parse.unquote(decoded_obj):
                                                            decoded_obj = urllib.parse.unquote(decoded_obj)
                                                    except:
                                                        decoded_obj = obj
                                                    
                                                    # 提取imgextra路径的图片
                                                    if 'imgextra' in decoded_obj.lower() and decoded_obj.startswith('http'):
                                                        clean_url = self._clean_url(decoded_obj.strip())
                                                        if clean_url and clean_url not in imgextra_from_api_responses:
                                                            imgextra_from_api_responses.append(clean_url)
                                                            print(f"  从API响应中找到imgextra图片: {clean_url[:100]}...")
                                                    
                                                    # 提取京东图片路径（360buyimg.com）
                                                    if '360buyimg.com' in decoded_obj.lower() and decoded_obj.startswith('http'):
                                                        clean_url = self._clean_url(decoded_obj.strip())
                                                        if clean_url and clean_url not in jd_images_from_api:
                                                            jd_images_from_api.append(clean_url)
                                                            print(f"  从API响应中找到京东图片: {clean_url[:100]}...")
                                                    
                                                    # 提取所有图片URL（只要是http开头且包含图片扩展名）
                                                    if decoded_obj.startswith('http') and any(ext in decoded_obj.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp']):
                                                        # 检查是否是CDN图片路径
                                                        if any(cdn in decoded_obj.lower() for cdn in ['alicdn', 'taobaocdn', 'tbcdn', '360buyimg', 'jdimg']):
                                                            clean_url = self._clean_url(decoded_obj.strip())
                                                            if clean_url and clean_url not in imgextra_from_api_responses and clean_url not in jd_images_from_api:
                                                                # 根据域名分类
                                                                if '360buyimg' in clean_url.lower():
                                                                    jd_images_from_api.append(clean_url)
                                                                    print(f"  从API响应中找到京东图片: {clean_url[:100]}...")
                                                                else:
                                                                    imgextra_from_api_responses.append(clean_url)
                                                                    print(f"  从API响应中找到CDN图片: {clean_url[:100]}...")
                                                elif isinstance(obj, dict):
                                                    for key, value in obj.items():
                                                        extract_imgextra_from_json(value, depth + 1)
                                                elif isinstance(obj, list):
                                                    for item in obj:
                                                        extract_imgextra_from_json(item, depth + 1)
                                            
                                            extract_imgextra_from_json(json_data)
                                        except json.JSONDecodeError:
                                            # 如果不是JSON，尝试用正则表达式搜索imgextra URL
                                            # 【关键改进】使用更全面的正则表达式，确保提取完整的URL（包括查询参数等）
                                            # 注意：re模块已在文件顶部导入，不需要再次导入
                                            # 匹配完整的imgextra URL，包括所有后缀和查询参数
                                            imgextra_pattern = r'https?://[^"\'\\s<>)]+imgextra[^"\'\\s<>)]+\.(jpg|jpeg|png|gif|webp|avif|JPG|JPEG|PNG|GIF|WEBP|AVIF)([^"\'\\s<>)]*)?'
                                            # 使用finditer来获取所有匹配，避免重复
                                            seen_matches = set()
                                            for url_match in re.finditer(imgextra_pattern, response_body):
                                                url = url_match.group(0)
                                                if url not in seen_matches:
                                                    seen_matches.add(url)
                                                    # 【关键】先解码URL，确保完整
                                                    import urllib.parse
                                                    try:
                                                        decoded_url = urllib.parse.unquote(url)
                                                        # 处理多次编码的情况
                                                        while '%' in decoded_url and decoded_url != urllib.parse.unquote(decoded_url):
                                                            decoded_url = urllib.parse.unquote(decoded_url)
                                                    except:
                                                        decoded_url = url
                                                    
                                                    clean_url = self._clean_url(decoded_url.strip())
                                                    if clean_url and clean_url.startswith('http') and clean_url not in imgextra_from_api_responses:
                                                        imgextra_from_api_responses.append(clean_url)
                                                        print(f"  从API响应文本中找到imgextra图片: {clean_url[:150]}...")
                                        except Exception as e:
                                            pass
                                except Exception as e:
                                    # 无法获取响应体（可能已过期或被清空）
                                    pass
                    except:
                        continue
                
                print(f"方法-1处理了 {processed_count} 个响应，检查了 {api_response_count} 个API响应")
                print(f"  - 找到 {len(imgextra_from_api_responses)} 个imgextra/CDN图片")
                print(f"  - 找到 {len(jd_images_from_api)} 个京东图片")
                
                if api_response_count == 0:
                    print("  警告：未找到任何API响应（JSON类型），可能的原因：")
                    print("    1. API响应可能不是JSON格式")
                    print("    2. CDP日志可能已被清空")
                    print("    3. 需要更早地捕获API响应")
                
                if len(imgextra_from_api_responses) > 0:
                    print(f"  前{min(10, len(imgextra_from_api_responses))}个从API响应中找到的imgextra/CDN图片:")
                    for i, url in enumerate(imgextra_from_api_responses[:10], 1):
                        print(f"    {i}. {url[:100]}...")
                
                if len(jd_images_from_api) > 0:
                    print(f"  前{min(10, len(jd_images_from_api))}个从API响应中找到的京东图片:")
                    for i, url in enumerate(jd_images_from_api[:10], 1):
                        print(f"    {i}. {url[:100]}...")
                
                # 将找到的图片添加到network_resources中
                for img_url in imgextra_from_api_responses:
                    if img_url not in network_resources:
                        network_resources[img_url] = {
                            'mime_type': 'image/png',  # 默认假设是png
                            'initiator_type': 'api_response'
                        }
                for img_url in jd_images_from_api:
                    if img_url not in network_resources:
                        network_resources[img_url] = {
                            'mime_type': 'image/jpeg',  # 默认假设是jpeg
                            'initiator_type': 'api_response'
                        }
            except Exception as e:
                import traceback
                print(f"  从API响应提取imgextra图片时出错: {e}")
                print(traceback.format_exc())
            
            # 【关键】直接从network_resources中提取所有图片（包括imgextra路径和京东图片路径）
            print("方法0: 直接从已捕获的network_resources中提取所有图片（包括imgextra路径和京东图片路径）...")
            imgextra_from_network = []
            jd_images_from_network = []
            all_images_from_network = []  # 所有图片
            try:
                print(f"  检查 {len(network_resources)} 个已捕获的网络资源...")
                for resource_url, resource_info in network_resources.items():
                    if not resource_url or not resource_url.startswith('http'):
                        continue
                    
                    # 【关键】先解码URL，确保能正确匹配
                    import urllib.parse
                    try:
                        decoded_url = urllib.parse.unquote(resource_url)
                        # 处理多次编码的情况
                        while '%' in decoded_url and decoded_url != urllib.parse.unquote(decoded_url):
                            decoded_url = urllib.parse.unquote(decoded_url)
                    except:
                        decoded_url = resource_url
                    
                    url_lower = decoded_url.lower()
                    mime_type = resource_info.get('mime_type', '').lower()
                    
                    # 【关键】检查是否是图片（MIME类型为image/*或URL是图片格式）
                    is_image_mime = mime_type and mime_type.startswith('image/')
                    is_image_url = any(ext in url_lower for ext in ['.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.bmp'])
                    
                    if is_image_mime or is_image_url:
                        # 【关键】使用解码后的URL进行清理
                        clean_url = self._clean_url(decoded_url.strip())
                        if clean_url and clean_url.startswith('http'):
                            # 分类提取
                            if 'imgextra' in url_lower or 'alicdn' in url_lower or 'taobaocdn' in url_lower:
                                if clean_url not in imgextra_from_network:
                                    imgextra_from_network.append(clean_url)
                                    print(f"  找到imgextra/CDN图片: {clean_url[:100]}... (MIME: {mime_type or 'N/A'})")
                            elif '360buyimg' in url_lower or 'jdimg' in url_lower:
                                if clean_url not in jd_images_from_network:
                                    jd_images_from_network.append(clean_url)
                                    print(f"  找到京东图片: {clean_url[:100]}... (MIME: {mime_type or 'N/A'})")
                            
                            # 添加到所有图片列表
                            if clean_url not in all_images_from_network:
                                all_images_from_network.append(clean_url)
                
                print(f"方法0从network_resources中找到:")
                print(f"  - {len(imgextra_from_network)} 个imgextra/CDN图片")
                print(f"  - {len(jd_images_from_network)} 个京东图片")
                print(f"  - 总共 {len(all_images_from_network)} 个图片")
                
                # 输出前10个找到的图片URL示例
                if len(imgextra_from_network) > 0:
                    print(f"  前{min(10, len(imgextra_from_network))}个imgextra/CDN图片URL示例:")
                    for i, url in enumerate(imgextra_from_network[:10], 1):
                        mime = network_resources.get(url, {}).get('mime_type', 'unknown')
                        print(f"    {i}. {url[:100]}... (MIME: {mime})")
                
                if len(jd_images_from_network) > 0:
                    print(f"  前{min(10, len(jd_images_from_network))}个京东图片URL示例:")
                    for i, url in enumerate(jd_images_from_network[:10], 1):
                        mime = network_resources.get(url, {}).get('mime_type', 'unknown')
                        print(f"    {i}. {url[:100]}... (MIME: {mime})")
            except Exception as e:
                import traceback
                print(f"  从network_resources提取imgextra图片时出错: {e}")
                print(traceback.format_exc())
            
            # 【关键】在提取avif之前，先保存所有CDP日志（避免被清空）
            print("保存所有CDP日志（避免被清空）...")
            saved_cdp_logs = []
            try:
                saved_cdp_logs = driver.get_log('performance')
                print(f"  已保存 {len(saved_cdp_logs)} 条CDP日志")
            except Exception as e:
                print(f"  保存CDP日志时出错: {e}")
            
            # 【关键】在提取avif之前，添加等待时间，确保页面完全加载
            print("等待页面完全加载，确保所有avif图片加载完成...")
            time.sleep(5)  # 先等待5秒
            
            # 滚动页面，触发懒加载
            print("滚动页面，触发懒加载...")
            try:
                driver.execute_script("""
                    // 缓慢滚动页面，触发懒加载
                    var scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
                    var viewportHeight = window.innerHeight;
                    var scrollStep = viewportHeight / 2;
                    var currentScroll = 0;
                    
                    function scrollDown() {
                        currentScroll += scrollStep;
                        if (currentScroll < scrollHeight) {
                            window.scrollTo(0, currentScroll);
                            setTimeout(scrollDown, 300);
                        } else {
                            window.scrollTo(0, scrollHeight);
                        }
                    }
                    scrollDown();
                """)
                time.sleep(3)  # 等待滚动完成
            except:
                pass
            
            # 等待所有图片加载完成（特别是avif格式）
            print("等待所有图片（包括avif格式）加载完成...")
            driver.execute_script("""
                return new Promise((resolve) => {
                    let checkCount = 0;
                    let maxChecks = 30;  // 增加检查次数
                    let loadedCount = 0;
                    let totalCount = 0;
                    
                    function checkAvifImages() {
                        checkCount++;
                        let images = document.querySelectorAll('img');
                        totalCount = images.length;
                        loadedCount = 0;
                        
                        images.forEach(img => {
                            if (img.complete && img.naturalWidth > 0) {
                                loadedCount++;
                            } else {
                                // 监听加载事件
                                img.onload = img.onerror = () => { loadedCount++; };
                            }
                        });
                        
                        console.log('检查avif图片加载: 总数=' + totalCount + ', 已加载=' + loadedCount);
                        
                        if (totalCount === 0 || (loadedCount >= totalCount * 0.95 && checkCount >= 5)) {
                            console.log('图片加载完成');
                            resolve();
                        } else if (checkCount >= maxChecks) {
                            console.log('达到最大检查次数');
                            resolve();
                        } else {
                            setTimeout(checkAvifImages, 500);
                        }
                    }
                    
                    checkAvifImages();
                    setTimeout(resolve, 15000);  // 最多等待15秒
                });
            """)
            time.sleep(2)  # 额外等待2秒
            
            # 再次滚动到顶部，确保所有图片都加载过
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            except:
                pass
            
            avif_extraction_count_before = len(self.resources)
            existing_urls_avif = {r['url'] for r in self.resources}
            
            try:
                # 方法1: 从Network请求中提取所有MIME类型为image/*的资源（包括所有图片类型）
                avif_from_network = []
                print("方法1: 从network_resources中检查所有image/*类型的资源...")
                for resource_url, resource_info in network_resources.items():
                    mime_type = resource_info.get('mime_type', '').lower()
                    response_type = resource_info.get('response_type', '').lower()
                    
                    # 【关键】检查MIME类型是否为image/*（所有图片类型）
                    is_image = False
                    if mime_type:
                        is_image = mime_type.startswith('image/')
                    if not is_image and response_type:
                        is_image = response_type.startswith('image/')
                    if not is_image:
                        # 检查URL中是否包含图片扩展名
                        url_lower = resource_url.lower()
                        is_image = any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp'])
                    
                    if is_image:
                        clean_url = self._clean_url(resource_url.strip())
                        if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                            avif_from_network.append(clean_url)
                            print(f"  找到图片资源: {clean_url[:80]}... (MIME: {mime_type or 'N/A'}, type: {response_type or 'N/A'})")
                
                # 方法1.5: 从CDP日志中重新检查所有资源，特别关注MIME类型为image/*的（所有图片类型）
                print("方法1.5: 从CDP日志中重新检查所有image/*类型的资源...")
                avif_from_cdp = []
                try:
                    # 获取所有CDP日志
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            
                            if method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                response_url = response.get('url', '')
                                request_id = params.get('requestId', '')
                                
                                # 获取MIME类型
                                content_type = response.get('mimeType', '').lower()
                                
                                # 如果mimeType为空，尝试从响应头中获取
                                if not content_type:
                                    headers = response.get('headers', {})
                                    if isinstance(headers, dict):
                                        content_type = headers.get('content-type', '').lower()
                                    elif isinstance(headers, list):
                                        for header in headers:
                                            if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                content_type = header.get('value', '').lower()
                                                break
                                
                                # 移除MIME类型中的参数
                                if content_type:
                                    content_type = content_type.split(';')[0].strip()
                                
                                # 【关键】检查是否是image/*（所有图片类型）
                                is_image_mime = content_type and content_type.startswith('image/')
                                url_lower = response_url.lower()
                                is_image_url = any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp'])
                                
                                if is_image_mime or is_image_url:
                                    clean_url = self._clean_url(response_url.strip())
                                    if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                        if clean_url not in avif_from_cdp:
                                            avif_from_cdp.append(clean_url)
                                            print(f"  从CDP日志找到图片资源: {clean_url[:80]}... (MIME: {content_type or 'N/A'})")
                        except:
                            continue
                except Exception as e:
                    print(f"  从CDP日志提取图片时出错: {e}")
                
                # 合并方法1和方法1.5的结果
                avif_from_network = list(set(avif_from_network + avif_from_cdp))
                print(f"方法1和方法1.5共找到 {len(avif_from_network)} 个图片资源（所有image/*类型）")
                
                # 方法2: 使用JavaScript从页面中提取所有avif格式的图片URL
                print("方法2: 使用JavaScript从页面中提取所有avif格式的图片URL...")
                avif_from_js = driver.execute_script("""
                    var avifUrls = [];
                    var seen = new Set();
                    var debugInfo = [];
                    
                    // 【关键】方法2.1: 检查所有主图的实际加载URL（currentSrc），看看哪些是avif格式
                    try {
                        debugInfo.push('开始检查主图区域的currentSrc...');
                        var mainPicSelectors = [
                            '#J_ImgBooth img', '.tb-booth img', '.main-pic img', 
                            '[class*="mainPic"] img', '[id*="mainPic"] img',
                            '.tb-pic img', '[class*="pic-list"] img', '.J_ImgBooth img'
                        ];
                        
                        mainPicSelectors.forEach(function(selector) {
                            try {
                                var imgs = document.querySelectorAll(selector);
                                imgs.forEach(function(img) {
                                    // 检查currentSrc（浏览器实际加载的URL）
                                    var currentSrc = img.currentSrc || img.src;
                                    if (currentSrc && currentSrc.startsWith('http')) {
                                        var currentSrcLower = currentSrc.toLowerCase();
                                        // 检查是否是avif格式
                                        if ((currentSrcLower.includes('.avif') || currentSrcLower.includes('/avif') || 
                                             currentSrcLower.match(/[_\\.]avif/i)) && !seen.has(currentSrc)) {
                                            seen.add(currentSrc);
                                            avifUrls.push(currentSrc);
                                            debugInfo.push('从主图currentSrc找到avif: ' + currentSrc);
                                        }
                                        
                                        // 对于CDN图片，尝试构造avif版本的URL
                                        if (currentSrcLower.includes('alicdn') || currentSrcLower.includes('taobaocdn')) {
                                            // 尝试在URL中添加.avif扩展名或修改为avif格式
                                            var avifUrl = currentSrc;
                                            // 如果URL包含.jpg或.png，尝试替换为.avif
                                            if (avifUrl.match(/\\.(jpg|jpeg|png|webp)(\\?|$)/i)) {
                                                avifUrl = avifUrl.replace(/\\.(jpg|jpeg|png|webp)(\\?|$)/i, '.avif$1');
                                                if (!seen.has(avifUrl)) {
                                                    seen.add(avifUrl);
                                                    avifUrls.push(avifUrl);
                                                    debugInfo.push('构造avif URL: ' + avifUrl);
                                                }
                                            }
                                        }
                                    }
                                    
                                    // 检查srcset中的所有URL
                                    var srcset = img.getAttribute('srcset') || img.getAttribute('data-srcset');
                                    if (srcset) {
                                        var urls = srcset.split(/[,\\s]+/);
                                        urls.forEach(function(item) {
                                            var url = item.trim().split(' ')[0];
                                            if (url && url.startsWith('http') && !seen.has(url)) {
                                                var urlLower = url.toLowerCase();
                                                if (urlLower.includes('.avif') || urlLower.includes('/avif') || 
                                                    urlLower.match(/[_\\.]avif/i)) {
                                                    seen.add(url);
                                                    avifUrls.push(url);
                                                    debugInfo.push('从srcset找到avif: ' + url);
                                                }
                                            }
                                        });
                                    }
                                });
                            } catch(e) {
                                debugInfo.push('选择器 ' + selector + ' 检查失败: ' + e.toString());
                            }
                        });
                    } catch(e) {
                        debugInfo.push('检查主图currentSrc失败: ' + e.toString());
                    }
                    
                    // 方法2.2: 从Performance API中提取所有avif资源
                    try {
                        var entries = performance.getEntriesByType('resource');
                        debugInfo.push('Performance API中找到 ' + entries.length + ' 个资源');
                        entries.forEach(function(entry) {
                            var url = entry.name;
                            if (url && !seen.has(url)) {
                                var urlLower = url.toLowerCase();
                                // 检查URL中是否包含avif
                                var isAvifUrl = urlLower.includes('.avif') || urlLower.includes('/avif') || 
                                               urlLower.match(/[_\\.]avif/i);
                                // 检查是否是图片资源（initiatorType为img）
                                var isImgResource = entry.initiatorType === 'img' || entry.initiatorType === 'image';
                                // 检查是否是CDN图片资源（可能支持avif）
                                var isCdnImage = urlLower.includes('alicdn') || urlLower.includes('taobaocdn') || 
                                                urlLower.includes('tbcdn') || urlLower.includes('360buyimg');
                                
                                if (isAvifUrl) {
                                    seen.add(url);
                                    avifUrls.push(url);
                                    debugInfo.push('从Performance API找到avif: ' + url);
                                }
                            }
                        });
                    } catch(e) {
                        debugInfo.push('Performance API提取avif错误: ' + e.toString());
                    }
                    
                    // 方法2.3: 从所有img元素中提取avif格式的URL
                    try {
                        var images = document.querySelectorAll('img');
                        debugInfo.push('找到 ' + images.length + ' 个img元素');
                        images.forEach(function(img) {
                            // 优先检查currentSrc（浏览器实际加载的URL，可能是avif）
                            var currentSrc = img.currentSrc || img.src;
                            if (currentSrc && currentSrc.startsWith('http')) {
                                var currentSrcLower = currentSrc.toLowerCase();
                                if ((currentSrcLower.includes('.avif') || currentSrcLower.includes('/avif') || 
                                     currentSrcLower.match(/[_\\.]avif/i)) && !seen.has(currentSrc)) {
                                    seen.add(currentSrc);
                                    avifUrls.push(currentSrc);
                                    debugInfo.push('从currentSrc找到avif: ' + currentSrc);
                                }
                            }
                            
                            // 检查所有可能的属性
                            var attrs = ['src', 'data-src', 'data-original', 'data-lazy-src', 
                                        'data-url', 'data-img', 'data-image', 'data-zoom-src', 
                                        'data-zoom', 'srcset', 'data-srcset'];
                            attrs.forEach(function(attr) {
                                var url = img.getAttribute(attr);
                                if (url && url.startsWith('http') && !seen.has(url)) {
                                    var urlLower = url.toLowerCase();
                                    if (urlLower.includes('.avif') || urlLower.includes('/avif') || 
                                        urlLower.match(/[_\\.]avif/i)) {
                                        seen.add(url);
                                        avifUrls.push(url);
                                        debugInfo.push('从属性 ' + attr + ' 找到avif: ' + url);
                                    }
                                    // 处理srcset（可能包含多个URL）
                                    if (attr === 'srcset' || attr === 'data-srcset') {
                                        var urls = url.split(/[,\\s]+/);
                                        urls.forEach(function(u) {
                                            u = u.trim().split(' ')[0];
                                            if (u && u.startsWith('http') && !seen.has(u)) {
                                                var uLower = u.toLowerCase();
                                                if (uLower.includes('.avif') || uLower.includes('/avif') || 
                                                    uLower.match(/[_\\.]avif/i)) {
                                                    seen.add(u);
                                                    avifUrls.push(u);
                                                    debugInfo.push('从srcset找到avif: ' + u);
                                                }
                                            }
                                        });
                                    }
                                }
                            });
                        });
                    } catch(e) {
                        debugInfo.push('从img元素提取avif错误: ' + e.toString());
                    }
                    
                    // 输出调试信息
                    console.log('avif提取调试信息:');
                    debugInfo.forEach(function(info) {
                        console.log('  ' + info);
                    });
                    
                    return {urls: avifUrls, debug: debugInfo};
                """)
                
                # 处理JavaScript返回的结果
                if isinstance(avif_from_js, dict):
                    if 'debug' in avif_from_js:
                        print("JavaScript提取avif调试信息:")
                        for info in avif_from_js.get('debug', []):
                            print(f"  {info}")
                    avif_from_js = avif_from_js.get('urls', [])
                elif not isinstance(avif_from_js, list):
                    avif_from_js = []
                
                print(f"方法2从JavaScript中找到 {len(avif_from_js) if avif_from_js else 0} 个avif资源")
                
                # 方法3: 从所有API请求中提取所有image/*类型的图片（全面检查）
                print("方法3: 从所有API请求中提取所有image/*类型的图片（包括jpeg, png, avif, gif, webp等）...")
                avif_from_cdn_check = []
                png_from_api = []
                all_images_from_cdp = []  # 所有图片类型
                try:
                    # 【关键】使用之前保存的CDP日志，如果为空则重新获取
                    print("  使用保存的CDP日志...")
                    logs = saved_cdp_logs if saved_cdp_logs else []
                    print(f"  从保存的日志中获取到 {len(logs)} 条CDP日志")
                    
                    # 如果保存的日志为空，尝试重新获取
                    if len(logs) == 0:
                        print("  保存的CDP日志为空，重新获取...")
                        logs = driver.get_log('performance')
                        print(f"  重新获取后得到 {len(logs)} 条CDP日志")
                        
                        # 如果还是为空，等待并再次获取
                        if len(logs) == 0:
                            print("  CDP日志仍为空，等待2秒后再次获取...")
                            time.sleep(2)
                            logs = driver.get_log('performance')
                            print(f"  再次获取后得到 {len(logs)} 条CDP日志")
                    
                    checked_count = 0
                    image_count = 0
                    avif_count = 0
                    png_count = 0
                    
                    # 用于存储所有找到的图片URL和MIME类型
                    all_image_urls = {}
                    
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            
                            if method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                response_url = response.get('url', '')
                                
                                if not response_url or not response_url.startswith('http'):
                                    continue
                                
                                # 获取MIME类型
                                content_type = response.get('mimeType', '').lower()
                                
                                # 如果mimeType为空，尝试从响应头中获取
                                if not content_type:
                                    headers = response.get('headers', {})
                                    if isinstance(headers, dict):
                                        content_type = headers.get('content-type', '').lower()
                                    elif isinstance(headers, list):
                                        for header in headers:
                                            if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                content_type = header.get('value', '').lower()
                                                break
                                
                                # 移除MIME类型中的参数
                                if content_type:
                                    content_type = content_type.split(';')[0].strip()
                                
                                # 检查是否是图片资源（特别是imgextra路径的）
                                url_lower = response_url.lower()
                                is_image = False
                                
                                # 【关键】优先检查MIME类型
                                if content_type:
                                    is_image = content_type.startswith('image/')
                                
                                # 检查URL是否是图片（特别是imgextra路径）
                                if not is_image:
                                    is_image = (
                                        'imgextra' in url_lower or  # 特别关注imgextra路径
                                        any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico', '.avif']) or
                                        'alicdn' in url_lower or 'taobaocdn' in url_lower or 'tbcdn' in url_lower or
                                        '/img/' in url_lower or '/image/' in url_lower or '/pic/' in url_lower
                                    )
                                
                                if is_image:
                                    image_count += 1
                                    clean_url = self._clean_url(response_url.strip())
                                    
                                    # 保存所有图片URL和MIME类型
                                    if clean_url and clean_url.startswith('http'):
                                        all_image_urls[clean_url] = content_type or 'unknown'
                                    
                                    # 【关键】提取所有image/*类型的图片
                                    if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                        if clean_url not in all_images_from_cdp:
                                            all_images_from_cdp.append(clean_url)
                                            print(f"  找到图片资源: {clean_url[:100]}... (MIME: {content_type or 'N/A'})")
                                    
                                    # 检查是否是image/avif（保留原有逻辑）
                                    is_avif = False
                                    if content_type:
                                        is_avif = (content_type == 'image/avif' or content_type == 'avif' or 'avif' in content_type)
                                    if not is_avif:
                                        is_avif = ('.avif' in url_lower or '/avif' in url_lower)
                                    
                                    # 检查是否是image/png（保留原有逻辑）
                                    is_png = False
                                    if content_type:
                                        is_png = (content_type == 'image/png' or content_type == 'png')
                                    if not is_png:
                                        is_png = ('.png' in url_lower and 'imgextra' in url_lower)
                                    
                                    if is_avif:
                                        avif_count += 1
                                        if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                            if clean_url not in avif_from_cdn_check:
                                                avif_from_cdn_check.append(clean_url)
                                    
                                    # 也提取所有image/png的imgextra图片
                                    if is_png and 'imgextra' in url_lower:
                                        png_count += 1
                                        if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                            if clean_url not in png_from_api:
                                                png_from_api.append(clean_url)
                                
                                # 统计检查的日志数量
                                checked_count += 1
                                
                                # 每检查1000条日志输出一次进度
                                if checked_count % 1000 == 0 and checked_count > 0:
                                    print(f"  已检查 {checked_count} 条日志，找到 {image_count} 个图片资源，其中 {avif_count} 个是avif，{png_count} 个是png")
                        except Exception as e:
                            continue
                    
                    print(f"  检查完成：共检查 {checked_count} 条日志，找到 {image_count} 个图片资源")
                    print(f"    - image/avif: {avif_count} 个")
                    print(f"    - image/png (imgextra): {png_count} 个")
                    print(f"    - 所有image/*类型图片: {len(all_images_from_cdp)} 个")
                    print(f"    - 所有图片URL总数: {len(all_image_urls)} 个")
                    
                    # 【新增】输出所有imgextra路径的图片URL（无论MIME类型）
                    imgextra_urls = [url for url in all_image_urls.keys() if 'imgextra' in url.lower()]
                    print(f"    - imgextra路径的图片: {len(imgextra_urls)} 个")
                    if len(imgextra_urls) > 0:
                        print(f"  前10个imgextra图片URL示例:")
                        for i, url in enumerate(imgextra_urls[:10], 1):
                            mime = all_image_urls.get(url, 'unknown')
                            print(f"    {i}. {url[:100]}... (MIME: {mime})")
                            
                except Exception as e:
                    import traceback
                    print(f"  检查CDP日志时出错: {e}")
                    print(traceback.format_exc())
                
                print(f"方法3找到 {len(avif_from_cdn_check)} 个avif资源，{len(png_from_api)} 个png资源，{len(all_images_from_cdp)} 个所有图片类型资源")
                
                # 方法3.5: 提取所有imgextra路径的图片（无论MIME类型，因为用户特别要求）
                print("方法3.5: 提取所有imgextra路径的图片（包括所有image/*类型）...")
                imgextra_all_images = []
                try:
                    # 使用保存的CDP日志提取所有imgextra路径的图片
                    logs = saved_cdp_logs if saved_cdp_logs else driver.get_log('performance')
                    print(f"  从 {len(logs)} 条CDP日志中提取imgextra图片...")
                    
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            
                            if method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                response_url = response.get('url', '')
                                
                                if not response_url or not response_url.startswith('http'):
                                    continue
                                
                                url_lower = response_url.lower()
                                
                                # 检查是否是imgextra路径的图片
                                if 'imgextra' in url_lower:
                                    # 获取MIME类型
                                    content_type = response.get('mimeType', '').lower()
                                    if not content_type:
                                        headers = response.get('headers', {})
                                        if isinstance(headers, dict):
                                            content_type = headers.get('content-type', '').lower()
                                        elif isinstance(headers, list):
                                            for header in headers:
                                                if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                    content_type = header.get('value', '').lower()
                                                    break
                                    
                                    if content_type:
                                        content_type = content_type.split(';')[0].strip()
                                    
                                    # 【关键】提取所有imgextra路径的图片，只要MIME类型是image/*（所有图片类型）
                                    is_image_mime = content_type and content_type.startswith('image/')
                                    is_image_url = any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.bmp'])
                                    
                                    if is_image_mime or is_image_url:
                                        clean_url = self._clean_url(response_url.strip())
                                        if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                            if clean_url not in imgextra_all_images:
                                                imgextra_all_images.append(clean_url)
                                                print(f"  找到imgextra图片: {clean_url[:100]}... (MIME: {content_type or 'N/A'})")
                        except:
                            continue
                except Exception as e:
                    import traceback
                    print(f"  提取imgextra图片时出错: {e}")
                    print(traceback.format_exc())
                
                print(f"方法3.5找到 {len(imgextra_all_images)} 个imgextra图片（avif/png）")
                
                # 方法4: 对于所有主图，检查它们实际加载的MIME类型（即使URL不包含.avif）
                print("方法4: 检查所有主图的实际MIME类型...")
                avif_from_main_images = []
                try:
                    # 获取所有主图URL（从之前提取的主图中）
                    main_image_urls = []
                    for resource in self.resources:
                        if '主图' in resource.get('name', '') or resource.get('type') == 'image':
                            main_image_urls.append(resource.get('url', ''))
                    
                    print(f"  找到 {len(main_image_urls)} 个主图URL，检查它们的实际MIME类型...")
                    
                    # 使用保存的CDP日志检查这些主图URL的实际MIME类型
                    logs = saved_cdp_logs if saved_cdp_logs else driver.get_log('performance')
                    main_image_urls_set = set(main_image_urls)
                    
                    for log in logs:
                        try:
                            message = json.loads(log['message'])
                            method = message.get('message', {}).get('method', '')
                            
                            if method == 'Network.responseReceived':
                                params = message.get('message', {}).get('params', {})
                                response = params.get('response', {})
                                response_url = response.get('url', '')
                                
                                # 检查是否是主图URL（去掉查询参数和锚点后比较）
                                response_url_clean = self._clean_url(response_url.strip())
                                is_main_image = False
                                for main_url in main_image_urls_set:
                                    main_url_clean = self._clean_url(main_url.strip())
                                    if response_url_clean == main_url_clean or response_url_clean in main_url_clean or main_url_clean in response_url_clean:
                                        is_main_image = True
                                        break
                                
                                if is_main_image:
                                    # 获取MIME类型
                                    content_type = response.get('mimeType', '').lower()
                                    
                                    # 如果mimeType为空，尝试从响应头中获取
                                    if not content_type:
                                        headers = response.get('headers', {})
                                        if isinstance(headers, dict):
                                            content_type = headers.get('content-type', '').lower()
                                        elif isinstance(headers, list):
                                            for header in headers:
                                                if isinstance(header, dict) and header.get('name', '').lower() == 'content-type':
                                                    content_type = header.get('value', '').lower()
                                                    break
                                    
                                    # 移除MIME类型中的参数
                                    if content_type:
                                        content_type = content_type.split(';')[0].strip()
                                    
                                    # 检查是否是image/avif
                                    if content_type == 'image/avif' or content_type == 'avif':
                                        clean_url = self._clean_url(response_url.strip())
                                        if clean_url and clean_url.startswith('http') and clean_url not in existing_urls_avif:
                                            if clean_url not in avif_from_main_images:
                                                avif_from_main_images.append(clean_url)
                                                print(f"  主图实际加载为avif: {clean_url[:80]}... (MIME: {content_type})")
                        except:
                            continue
                except Exception as e:
                    import traceback
                    print(f"  检查主图MIME类型时出错: {e}")
                    print(traceback.format_exc())
                
                print(f"方法4找到 {len(avif_from_main_images)} 个主图的avif版本")
                
                # 方法5: 已禁用URL构造
                # 【重要】不再随意构造URL，只使用从接口返回的实际数据
                print("方法5: 已禁用URL构造（只使用从接口返回的实际URL）...")
                avif_from_constructed = []
                print(f"方法5: 已禁用，不再构造URL（只使用接口返回的实际数据）")
                
                # 合并所有图片资源（包括所有image/*类型）
                all_image_urls = set(avif_from_network)
                # 【关键】首先添加从API响应中提取的所有图片
                for url in imgextra_from_api_responses:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in jd_images_from_api:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                # 【关键】然后添加从network_resources中提取的所有图片
                for url in imgextra_from_network:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in jd_images_from_network:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in all_images_from_network:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in avif_from_js:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in avif_from_cdn_check:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in all_images_from_cdp:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in png_from_api:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in imgextra_all_images:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in avif_from_main_images:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                for url in avif_from_constructed:
                    if url and url.startswith('http'):
                        clean_url = self._clean_url(url.strip())
                        if clean_url:
                            all_image_urls.add(clean_url)
                
                # 添加所有图片资源到列表（包括所有image/*类型）
                image_added_count = 0
                for image_url in all_image_urls:
                    if image_url not in existing_urls_avif:
                        # 从network_resources中获取实际的MIME类型
                        actual_mime_type = 'image/jpeg'  # 默认
                        if image_url in network_resources:
                            actual_mime_type = network_resources[image_url].get('mime_type', 'image/jpeg')
                        elif any(url == image_url for url in imgextra_from_api_responses + jd_images_from_api):
                            # 从API响应中找到的，尝试从URL推断
                            url_lower = image_url.lower()
                            if '.png' in url_lower:
                                actual_mime_type = 'image/png'
                            elif '.jpg' in url_lower or '.jpeg' in url_lower:
                                actual_mime_type = 'image/jpeg'
                            elif '.gif' in url_lower:
                                actual_mime_type = 'image/gif'
                            elif '.webp' in url_lower:
                                actual_mime_type = 'image/webp'
                            elif '.avif' in url_lower:
                                actual_mime_type = 'image/avif'
                        
                        # 生成文件名（根据实际MIME类型）
                        url_path = urlparse(image_url).path
                        name = os.path.basename(url_path) or f"image_{len(self.resources) + 1}"
                        if not name or name == '':
                            name = f"image_{len(self.resources) + 1}"
                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                        
                        # 根据MIME类型确定扩展名
                        if actual_mime_type == 'image/png' and not name.lower().endswith('.png'):
                            name_without_ext = os.path.splitext(name)[0]
                            name = name_without_ext + '.png'
                        elif actual_mime_type == 'image/jpeg' and not name.lower().endswith(('.jpg', '.jpeg')):
                            name_without_ext = os.path.splitext(name)[0]
                            name = name_without_ext + '.jpg'
                        elif actual_mime_type == 'image/gif' and not name.lower().endswith('.gif'):
                            name_without_ext = os.path.splitext(name)[0]
                            name = name_without_ext + '.gif'
                        elif actual_mime_type == 'image/webp' and not name.lower().endswith('.webp'):
                            name_without_ext = os.path.splitext(name)[0]
                            name = name_without_ext + '.webp'
                        elif actual_mime_type == 'image/avif' and not name.lower().endswith('.avif'):
                            name_without_ext = os.path.splitext(name)[0]
                            name = name_without_ext + '.avif'
                        
                        self.resources.append({
                            'name': name,
                            'url': image_url,
                            'type': 'image',
                            'mime_type': actual_mime_type
                        })
                        existing_urls_avif.add(image_url)
                        image_added_count += 1
                
                image_extraction_count_after = len(self.resources)
                print(f"\n【所有图片类型提取结果统计】")
                print(f"  - 方法-1（API响应体 imgextra）: {len(imgextra_from_api_responses)} 个")
                print(f"  - 方法-1（API响应体 京东图片）: {len(jd_images_from_api)} 个")
                print(f"  - 方法0（network_resources imgextra）: {len(imgextra_from_network)} 个")
                print(f"  - 方法0（network_resources 京东图片）: {len(jd_images_from_network)} 个")
                print(f"  - 方法0（network_resources 所有图片）: {len(all_images_from_network)} 个")
                print(f"  - 方法1（Network请求）: {len(avif_from_network)} 个")
                print(f"  - 方法2（JavaScript）: {len(avif_from_js) if avif_from_js else 0} 个")
                print(f"  - 方法3（CDP日志avif）: {len(avif_from_cdn_check)} 个")
                print(f"  - 方法3（CDP日志png）: {len(png_from_api)} 个")
                print(f"  - 方法3.5（imgextra图片）: {len(imgextra_all_images)} 个")
                print(f"  - 方法4（主图MIME检查）: {len(avif_from_main_images)} 个")
                print(f"  - 方法5（构造avif URL）: {len(avif_from_constructed)} 个（已禁用）")
                print(f"  - 去重后总共: {len(all_image_urls)} 个图片资源（所有image/*类型）")
                print(f"  - 新增添加到列表: {image_added_count} 个图片资源")
                print(f"  - 提取前资源总数: {avif_extraction_count_before}")
                print(f"  - 提取后资源总数: {image_extraction_count_after}")
                
                if image_added_count > 0:
                    print(f"\n  ✓ 成功提取并添加了 {image_added_count} 个图片资源（包括所有image/*类型：jpeg, png, avif, gif, webp等）！")
                    print(f"  这些是您要的图片（包括imgextra路径和京东图片路径），请检查资源列表。")
                else:
                    print(f"\n  ⚠ 警告：未找到任何图片资源")
                    print(f"  可能的原因：")
                    print(f"    1. 页面可能不包含图片")
                    print(f"    2. CDP日志可能已被清空，需要更早获取")
                    print(f"    3. 需要更长的等待时间让图片加载完成")
                    print(f"  提示：请检查浏览器开发者工具的Network标签，查看图片的实际MIME类型")
                    
            except Exception as e:
                import traceback
                print(f"提取avif资源时出错: {e}")
                print(traceback.format_exc())
            
            # 获取渲染后的HTML
            html_content = driver.page_source
            
            # Network请求的资源已经在上面添加到列表了，这里记录最终数量
            network_count_after = len(self.resources)
            
            # 从渲染后的HTML中提取更多资源（作为补充，但主要应该从Network请求中获取）
            print("\n" + "=" * 80)
            print("开始从渲染后的HTML中提取资源（补充方法）...")
            network_added = network_count_after - network_count_before if 'network_count_before' in locals() else 0
            print(f"当前已有资源数量: {len(self.resources)}（包括Network请求提取的 {network_added} 个资源）")
            print("=" * 80)
            if html_content:
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    found_urls_html = set()  # 用于去重
                    
                    # 确保found_urls_html包含已存在的URL
                    for r in self.resources:
                        found_urls_html.add(r['url'])
                    
                    # 保存原始URL用于urljoin
                    base_url = url
                    
                    # 方法1: 直接从HTML文本中扫描所有可能的图片URL（最彻底的方法）
                    print("\n【方法1】从HTML文本中直接扫描所有图片URL...")
                    html_text_count_before = len(self.resources)
                    # 使用正则表达式从HTML文本中提取所有可能的图片URL
                    # 匹配所有包含图片相关关键字的URL（更全面的模式）
                    image_url_patterns = [
                        # 【关键】匹配imgextra路径的URL（包括带数字路径的，如 imgextra/i3/2218673265158/）
                        r'https?://[^\s"\'<>\)]*imgextra/[^\s"\'<>\)]*(?:\?[^\s"\'<>\)]*)?',
                        # 匹配包含CDN域名的URL（即使没有扩展名）
                        r'https?://[^\s"\'<>\)]+(?:alicdn|taobaocdn|tbcdn|360buyimg|jd\.com/img|jd\.com/image)[^\s"\'<>\)]*(?:\?[^\s"\'<>\)]*)?',
                        # 匹配包含图片路径关键字的URL
                        r'https?://[^\s"\'<>\)]+/[^\s"\'<>\)]*(?:/jfs/|/imagetools/|/img/|/image/|/pic/|/photo/|/picture/|/upload/)[^\s"\'<>\)]*(?:\?[^\s"\'<>\)]*)?',
                        # 匹配明确以图片扩展名结尾的URL（包括avif和webp，支持多个扩展名如.jpg_.webp）
                        r'https?://[^\s"\'<>\)]+\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)[^\s"\'<>\)]*(?:\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif))*(?:\?[^\s"\'<>\)]*)?',
                        # 匹配二级域名包含图片扩展名的URL（包括avif）
                        r'https?://[^\s"\'<>\)]+\.[^\s"\'<>\)]*\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)(?:\?[^\s"\'<>\)]*)?',
                        # 匹配引号中的imgextra URL
                        r'["\'](https?://[^\s"\'<>\)]*imgextra/[^\s"\'<>\)]*)["\']',
                        # 匹配引号中的图片URL（更宽松）
                        r'["\'](https?://[^\s"\'<>\)]+(?:alicdn|taobaocdn|tbcdn|360buyimg|jd\.com/img|jd\.com/image|/img/|/image/|/pic/|/photo/|/picture/)[^\s"\'<>\)]*)["\']',
                        # 匹配引号中的任何包含图片扩展名的URL（包括avif和webp，支持多个扩展名）
                        r'["\']([^\s"\'<>\)]+\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)[^\s"\'<>\)]*(?:\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif))*(?:\?[^\s"\'<>\)]*)?)["\']',
                        # 匹配JavaScript变量赋值中的图片URL（包括avif和imgextra）
                        r'(?:var|let|const|url|src|image|img|pic|photo)\s*[=:]\s*["\']?((?:https?://)?[^\s"\'<>\)]+(?:alicdn|taobaocdn|tbcdn|360buyimg|imgextra|/img/|/image/|/pic/|\.(?:jpg|jpeg|png|gif|webp|avif))[^\s"\'<>\)]*)["\']?',
                        # 匹配JSON中的图片URL（更宽松，包括avif和webp，支持多个扩展名）
                        r'["\']?([^"\']*\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif)[^"\']*(?:\.(?:jpg|jpeg|png|gif|webp|bmp|ico|svg|avif))*(?:\?[^"\']*)?)["\']?',
                    ]
                    
                    html_text_urls = set()
                    for pattern_idx, pattern in enumerate(image_url_patterns):
                        try:
                            matches = re.findall(pattern, html_content, re.IGNORECASE)
                            pattern_matches = 0
                            for match in matches:
                                # 处理匹配结果（可能是字符串或元组）
                                if isinstance(match, tuple):
                                    # 如果匹配返回元组，取第一个非空元素
                                    url = None
                                    for m in match:
                                        if m and isinstance(m, str):
                                            url = m
                                            break
                                    if not url:
                                        continue
                                else:
                                    url = match
                                
                                # 清理匹配结果（移除引号）
                                url = str(url).strip().strip('"').strip("'").strip()
                                
                                # 如果是相对URL，转换为绝对URL（使用base_url）
                                if url and not url.startswith('http'):
                                    if url.startswith('//'):
                                        url = 'https:' + url
                                    elif url.startswith('/'):
                                        # urljoin(base_url, relative_url)
                                        url = urljoin(base_url, url)
                                    else:
                                        # 相对路径，使用urljoin
                                        url = urljoin(base_url, url)
                                
                                if url and (url.startswith('http') or url.startswith('//')):
                                    # 处理协议相对URL
                                    if url.startswith('//'):
                                        url = 'https:' + url
                                    
                                    # 清理URL
                                    clean_url = url.split('#')[0].strip()
                                    clean_url = self._clean_url(clean_url) if clean_url else None
                                    if clean_url and clean_url not in found_urls_html:
                                        # 验证不是非媒体文件
                                        excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt', '.woff', '.woff2']
                                        path = urlparse(clean_url).path.lower()
                                        # 更宽松的验证：只要不是明确排除的文件类型，就认为是图片
                                        if not any(path.endswith(ext) for ext in excluded_exts):
                                            # 进一步验证：包含图片相关关键字或扩展名
                                            url_lower = clean_url.lower()
                                            # 【关键】imgextra路径的URL都认为是图片
                                            if (any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif']) or
                                                any(keyword in url_lower for keyword in ['img', 'image', 'pic', 'photo', 'picture', 'alicdn', 'taobaocdn', 'tbcdn', '360buyimg', '/jfs/', '/imagetools/', 'imgextra', 'tps', 'oss'])):
                                                html_text_urls.add(clean_url)
                                                pattern_matches += 1
                            if pattern_matches > 0:
                                print(f"  模式{pattern_idx + 1}匹配到 {pattern_matches} 个URL")
                        except Exception as pattern_error:
                            print(f"  模式{pattern_idx + 1}执行出错: {pattern_error}")
                            continue
                    
                    print(f"从HTML文本中扫描到 {len(html_text_urls)} 个可能的图片URL")
                    html_text_added = 0
                    for html_url in html_text_urls:
                        if html_url not in found_urls_html:
                            # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                            if not self.is_accessible_resource(html_url):
                                continue  # 跳过无法访问的资源
                            
                            found_urls_html.add(html_url)
                            name = os.path.basename(urlparse(html_url).path) or f"图片_{len(self.resources) + 1}"
                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                            self.resources.append({
                                'name': name,
                                'url': html_url,
                                'type': 'image'
                            })
                            html_text_added += 1
                    print(f"从HTML文本中添加了 {html_text_added} 个资源（当前总数: {len(self.resources)}）")
                    
                    # 提取淘宝资源（如果域名匹配）
                    if 'taobao.com' in url.lower() or 'tmall.com' in url.lower():
                        print("\n【方法2】检测到淘宝页面，使用淘宝资源提取方法...")
                        taobao_count_before = len(self.resources)
                        self.extract_taobao_resources(soup, url, found_urls_html)
                        taobao_count_after = len(self.resources)
                        print(f"淘宝资源提取方法添加了 {taobao_count_after - taobao_count_before} 个资源（当前总数: {len(self.resources)}）")
                    
                    # 从页面元素中直接提取所有图片（使用Selenium直接查找，更可靠）
                    print("\n【方法3】从页面元素中直接提取所有图片...")
                    try:
                        from selenium.webdriver.common.by import By
                        # 等待一下，确保所有图片元素都加载完成
                        time.sleep(2)
                        
                        selenium_count_before = len(self.resources)
                        selenium_images = driver.find_elements(By.TAG_NAME, "img")
                        selenium_img_count = 0
                        print(f"Selenium找到 {len(selenium_images)} 个img元素")
                        
                        # 也查找所有可能的图片容器（可能使用div或其他元素包裹图片）
                        try:
                            img_containers = driver.find_elements(By.CSS_SELECTOR, 
                                "[class*='img'], [class*='image'], [class*='pic'], [class*='photo'], [id*='img'], [id*='image'], [data-src], [data-original], [data-lazy-src]")
                            print(f"找到 {len(img_containers)} 个可能的图片容器")
                            for container in img_containers:
                                try:
                                    # 尝试从容器的data属性中提取图片URL
                                    for attr in ['data-src', 'data-original', 'data-lazy-src', 'data-url', 'data-img', 'data-image', 'data-zoom', 'data-zoom-src']:
                                        img_url = container.get_attribute(attr)
                                        if img_url and img_url.startswith('http') and not img_url.startswith('data:'):
                                            clean_url = img_url.split('?')[0].split('#')[0].strip()
                                            if clean_url not in found_urls_html:
                                                # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                                if not self.is_accessible_resource(clean_url):
                                                    continue  # 跳过无法访问的资源
                                                
                                                found_urls_html.add(clean_url)
                                                name = os.path.basename(urlparse(clean_url).path) or f"图片_{len(self.resources) + 1}"
                                                name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                                self.resources.append({
                                                    'name': name,
                                                    'url': clean_url,
                                                    'type': 'image'
                                                })
                                                selenium_img_count += 1
                                    
                                    # 尝试从CSS背景图片中提取
                                    try:
                                        bg_image = container.value_of_css_property('background-image')
                                        if bg_image and bg_image != 'none':
                                            matches = re.findall(r'url\(["\']?([^"\'\)]+)["\']?\)', bg_image)
                                            for match in matches:
                                                img_url = match.strip()
                                                if img_url.startswith('http') or img_url.startswith('//'):
                                                    if img_url.startswith('//'):
                                                        img_url = urlparse(url).scheme + ':' + img_url
                                                    clean_url = img_url.split('?')[0].split('#')[0].strip()
                                                    # 清理URL中的错误转义字符
                                                    clean_url = self._clean_url(clean_url) if clean_url else None
                                                    if clean_url and clean_url not in found_urls_html:
                                                        # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                                        if not self.is_accessible_resource(clean_url):
                                                            continue  # 跳过无法访问的资源
                                                        
                                                        found_urls_html.add(clean_url)
                                                        name = os.path.basename(urlparse(clean_url).path) or f"图片_{len(self.resources) + 1}"
                                                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                                        self.resources.append({
                                                            'name': name,
                                                            'url': clean_url,
                                                            'type': 'image'
                                                        })
                                                        selenium_img_count += 1
                                    except:
                                        pass
                                except:
                                    continue
                        except Exception as e:
                            print(f"从图片容器提取资源时出错: {e}")
                        
                        for img_elem in selenium_images:
                            try:
                                # 尝试多种可能的属性
                                img_url = None
                                for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-srcset', 
                                            'data-url', 'data-img', 'data-image', 'srcset', 'data-webp', 
                                            'data-zoom', 'data-zoom-src', 'data-lazy', 'lazy-src', 'original-src',
                                            'currentSrc']:  # 添加currentSrc，获取当前实际使用的src
                                    img_url = img_elem.get_attribute(attr)
                                    if img_url and img_url.strip() and not img_url.strip().startswith('data:'):
                                        # 处理srcset格式
                                        if attr == 'srcset' or attr == 'data-srcset':
                                            urls = re.findall(r'([^\s,]+)', img_url)
                                            if urls:
                                                for url_item in urls:
                                                    url_item = url_item.strip()
                                                    if url_item and not url_item.startswith('data:'):
                                                        if url_item.startswith('//'):
                                                            url_item = urlparse(url).scheme + ':' + url_item
                                                        elif not url_item.startswith('http'):
                                                            url_item = urljoin(url, url_item)
                                                        clean_url_item = url_item.split('?')[0].split('#')[0].strip()
                                                        # 清理URL中的错误转义字符
                                                        clean_url_item = self._clean_url(clean_url_item) if clean_url_item else None
                                                        if clean_url_item and clean_url_item not in found_urls_html:
                                                            # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                                            if not self.is_accessible_resource(clean_url_item):
                                                                continue  # 跳过无法访问的资源
                                                            
                                                            found_urls_html.add(clean_url_item)
                                                            name = os.path.basename(urlparse(clean_url_item).path) or f"图片_{len(self.resources) + 1}"
                                                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                                            self.resources.append({
                                                                'name': name,
                                                                'url': clean_url_item,
                                                                'type': 'image'
                                                            })
                                                            selenium_img_count += 1
                                                img_url = urls[0] if urls else None
                                            else:
                                                img_url = None
                                        
                                        if img_url and img_url.strip() and not img_url.strip().startswith('data:'):
                                            break
                                
                                if img_url and img_url.strip() and not img_url.strip().startswith('data:'):
                                    # 清理URL（但保留查询参数，因为可能包含重要信息）
                                    original_img_url = img_url  # 保存原始URL用于调试
                                    if img_url.startswith('//'):
                                        img_url = urlparse(url).scheme + ':' + img_url
                                    elif not img_url.startswith('http'):
                                        img_url = urljoin(url, img_url)
                                    
                                    # 只移除片段（#），保留查询参数（?）
                                    img_url = img_url.split('#')[0].strip()
                                    # 清理URL中的错误转义字符
                                    cleaned_url = self._clean_url(img_url) if img_url else None
                                    if not cleaned_url:
                                        # 调试：如果清理后URL为空，输出信息
                                        if selenium_img_count == 0 and len(selenium_images) > 0:
                                            print(f"  调试：清理后URL为空，原始URL: {original_img_url[:100]}")
                                        continue
                                    img_url = cleaned_url
                                    
                                    # 处理base64图片
                                    if img_url.startswith('data:image/'):
                                        self._process_base64_image(img_url, found_urls)
                                        continue
                                    # 跳过其他非图片的data URL和javascript
                                    if img_url.startswith('data:') or img_url.startswith('javascript:'):
                                        continue
                                    
                                    # 验证URL格式（更宽松的验证）
                                    try:
                                        parsed = urlparse(img_url)
                                        if not parsed.scheme or not parsed.netloc:
                                            # 调试：如果URL格式验证失败，输出信息
                                            if selenium_img_count == 0 and len(selenium_images) > 0:
                                                print(f"  调试：URL格式验证失败，URL: {img_url[:100]}")
                                            continue
                                    except Exception as e:
                                        # 调试：如果URL解析出错，输出信息
                                        if selenium_img_count == 0 and len(selenium_images) > 0:
                                            print(f"  调试：URL解析出错: {e}, URL: {img_url[:100]}")
                                        continue
                                    
                                    # 去重
                                    if img_url not in found_urls_html:
                                        # 【关键】验证资源是否可以访问，过滤掉无法加载的资源
                                        if not self.is_accessible_resource(img_url):
                                            continue  # 跳过无法访问的资源
                                        
                                        found_urls_html.add(img_url)
                                        name = img_elem.get_attribute('alt') or img_elem.get_attribute('title') or ''
                                        if not name:
                                            # 尝试从URL路径中提取文件名
                                            path = urlparse(img_url).path
                                            name = os.path.basename(path)
                                            # 如果路径中没有文件名，尝试从查询参数中提取
                                            if not name or name == '':
                                                query = urlparse(img_url).query
                                                if query:
                                                    # 尝试从查询参数中提取文件名
                                                    for param in query.split('&'):
                                                        if '=' in param:
                                                            key, value = param.split('=', 1)
                                                            if key.lower() in ['name', 'file', 'filename', 'img']:
                                                                name = value
                                                                break
                                        if not name or name == '':
                                            name = f"图片_{len(self.resources) + 1}"
                                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                        self.resources.append({
                                            'name': name,
                                            'url': img_url,
                                            'type': 'image'
                                        })
                                        selenium_img_count += 1
                                    else:
                                        # 调试：如果URL已存在，输出信息
                                        if selenium_img_count == 0 and len(selenium_images) > 0:
                                            print(f"  调试：URL已存在（重复），URL: {img_url[:100]}")
                            except Exception as e:
                                # 添加调试信息，看看为什么提取失败
                                try:
                                    debug_src = img_elem.get_attribute('src')
                                    debug_data_src = img_elem.get_attribute('data-src')
                                    debug_data_original = img_elem.get_attribute('data-original')
                                    # 只在有属性值但提取失败时输出调试信息
                                    if debug_src or debug_data_src or debug_data_original:
                                        print(f"提取img元素时出错: {e}, src={debug_src[:80] if debug_src else None}, data-src={debug_data_src[:80] if debug_data_src else None}, data-original={debug_data_original[:80] if debug_data_original else None}")
                                except:
                                    pass
                                continue
                        
                        # 如果提取不到资源，输出调试信息
                        if selenium_img_count == 0 and len(selenium_images) > 0:
                            print(f"警告：找到 {len(selenium_images)} 个img元素，但未提取到任何URL。检查前3个元素的属性：")
                            for i, img_elem in enumerate(selenium_images[:3]):
                                try:
                                    debug_src = img_elem.get_attribute('src')
                                    debug_data_src = img_elem.get_attribute('data-src')
                                    debug_data_original = img_elem.get_attribute('data-original')
                                    debug_current_src = img_elem.get_attribute('currentSrc')
                                    print(f"  img元素{i+1}: src={debug_src[:80] if debug_src else None}, data-src={debug_data_src[:80] if debug_data_src else None}, data-original={debug_data_original[:80] if debug_data_original else None}, currentSrc={debug_current_src[:80] if debug_current_src else None}")
                                except:
                                    print(f"  img元素{i+1}: 无法获取属性")
                        
                        selenium_count_after = len(self.resources)
                        print(f"从Selenium元素中提取了 {selenium_img_count} 个图片资源（当前总数: {len(self.resources)}，新增: {selenium_count_after - selenium_count_before}）")
                    except Exception as e:
                        import traceback
                        print(f"从Selenium元素提取资源时出错: {e}")
                        print(traceback.format_exc())
                    
                    # 强制触发所有懒加载图片（淘宝专用，主图已在前面提取）
                    if 'taobao.com' in url.lower() or 'tmall.com' in url.lower():
                        print("检测到淘宝页面，触发懒加载图片...")
                        try:
                            # 执行JavaScript来强制触发所有懒加载图片
                            lazy_img_result = driver.execute_script("""
                                // 强制触发所有懒加载图片
                                try {
                                    var triggered = 0;
                                    
                                    // 1. 查找所有包含data-src属性的img元素，将data-src赋值给src
                                    var lazyImages = document.querySelectorAll('img[data-src], img[data-original], img[data-lazy-src], img[data-url], img[data-img]');
                                    console.log('找到 ' + lazyImages.length + ' 个懒加载图片');
                                    lazyImages.forEach(function(img) {
                                        var src = img.getAttribute('data-src') || img.getAttribute('data-original') || 
                                                 img.getAttribute('data-lazy-src') || img.getAttribute('data-url') || 
                                                 img.getAttribute('data-img');
                                        if (src && (!img.src || img.src.startsWith('data:') || img.src === '')) {
                                            img.src = src;
                                            triggered++;
                                        }
                                    });
                                    
                                    // 2. 查找所有包含data-src属性的非img元素，也尝试触发
                                    var lazyContainers = document.querySelectorAll('[data-src]:not(img), [data-original]:not(img), [data-lazy-src]:not(img)');
                                    lazyContainers.forEach(function(container) {
                                        var src = container.getAttribute('data-src') || container.getAttribute('data-original') || 
                                                 container.getAttribute('data-lazy-src');
                                        if (src && src.startsWith('http')) {
                                            // 尝试创建img元素来加载图片
                                            var img = document.createElement('img');
                                            img.src = src;
                                            document.body.appendChild(img);
                                            triggered++;
                                        }
                                    });
                                    
                                    // 3. 触发所有图片的load事件
                                    var allImages = document.querySelectorAll('img');
                                    allImages.forEach(function(img) {
                                        if (!img.complete && img.src && !img.src.startsWith('data:')) {
                                            // 触发load事件
                                            var event = new Event('load');
                                            img.dispatchEvent(event);
                                        }
                                    });
                                    
                                    // 4. 尝试滚动所有图片容器到视口
                                    var imgContainers = document.querySelectorAll('[data-src], [data-original], [data-lazy-src]');
                                    imgContainers.forEach(function(container) {
                                        try {
                                            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                        } catch(e) {}
                                    });
                                    
                                    return JSON.stringify({ total: allImages.length, triggered: triggered });
                                } catch(e) {
                                    return JSON.stringify({ total: 0, triggered: 0, error: e.toString() });
                                }
                            """)
                            
                            # 处理提取到的主图
                            if main_images_result:
                                # 提取调试信息
                                if isinstance(main_images_result, dict) and 'debug' in main_images_result:
                                    debug_info = main_images_result.get('debug', [])
                                    print("主图提取调试信息:")
                                    for info in debug_info:
                                        print(f"  {info}")
                                    main_images_list = main_images_result.get('images', [])
                                else:
                                    main_images_list = main_images_result if isinstance(main_images_result, list) else []
                                
                                print(f"从淘宝页面提取到 {len(main_images_list)} 个主图")
                                main_img_added = 0
                                for img_info in main_images_list:
                                    if isinstance(img_info, dict):
                                        img_url = img_info.get('url', '')
                                        source = img_info.get('source', 'unknown')
                                    else:
                                        img_url = str(img_info)
                                        source = 'unknown'
                                    
                                    if img_url and img_url.startswith('http'):
                                        # 清理URL（保留查询参数，因为可能包含尺寸信息）
                                        clean_url = img_url.split('#')[0].strip()
                                        clean_url = self._clean_url(clean_url) if clean_url else None
                                        if clean_url and clean_url not in found_urls_html:
                                            found_urls_html.add(clean_url)
                                            # 生成文件名（优先使用主图标识）
                                            name = f"主图_{main_img_added + 1}"
                                            # 尝试从URL中提取文件名
                                            url_path = urlparse(clean_url).path
                                            url_filename = os.path.basename(url_path)
                                            if url_filename and url_filename not in ['', '/']:
                                                # 保留原始文件名但添加主图标识
                                                name = f"主图_{main_img_added + 1}_{url_filename}"
                                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                            self.resources.append({
                                                'name': name,
                                                'url': clean_url,
                                                'type': 'image',
                                                'source': source  # 保存来源信息
                                            })
                                            main_img_added += 1
                                            if main_img_added <= 10:
                                                print(f"  主图 {main_img_added}: {clean_url[:80]}... (来源: {source})")
                                
                                print(f"成功添加 {main_img_added} 个主图到资源列表")
                            else:
                                print("警告：主图提取返回空结果，可能页面结构不同或需要更长时间加载")
                                # 尝试直接执行一个简单的提取
                                try:
                                    simple_result = driver.execute_script("""
                                        var imgs = [];
                                        var seen = new Set();
                                        // 从所有img标签提取
                                        document.querySelectorAll('img').forEach(function(img) {
                                            var src = img.src || img.currentSrc || img.getAttribute('src') || 
                                                     img.getAttribute('data-src') || img.getAttribute('data-original');
                                            if (src && src.includes('alicdn') && !seen.has(src)) {
                                                seen.add(src);
                                                imgs.push(src);
                                            }
                                        });
                                        return imgs;
                                    """)
                                    if simple_result and len(simple_result) > 0:
                                        print(f"简单提取方法找到 {len(simple_result)} 个图片")
                                except Exception as e:
                                    print(f"简单提取也失败: {e}")
                            
                            # 等待轮播切换完成，然后再次提取主图
                            print("等待主图轮播切换完成...")
                            time.sleep(5)  # 增加等待时间，让所有轮播切换完成
                            
                            # 再次提取主图（轮播切换后可能有新图片）
                            print("轮播切换后，再次提取主图...")
                            main_images_result2 = driver.execute_script("""
                                (function() {
                                    var mainImages = [];
                                    var seen = new Set();
                                    
                                    // 辅助函数：处理图片URL，去除尺寸参数获取原图
                                    function getOriginalImageUrl(url) {
                                        if (!url || !url.includes('alicdn') && !url.includes('taobaocdn')) {
                                            return url;
                                        }
                                        url = url.replace(/_[0-9]+x[0-9]+\\.jpg/g, '.jpg');
                                        url = url.replace(/_[0-9]+x[0-9]+\\.png/g, '.png');
                                        url = url.replace(/_[0-9]+x[0-9]+\\.webp/g, '.webp');
                                        url = url.replace(/\\?.*$/, '');
                                        return url;
                                    }
                                    
                                    // 从当前显示的主图区域提取
                                    var mainPicSelectors = ['#J_ImgBooth img', '.tb-booth img', '.main-pic img', '[class*="mainPic"] img'];
                                    mainPicSelectors.forEach(function(sel) {
                                        try {
                                            var imgs = document.querySelectorAll(sel);
                                            imgs.forEach(function(img) {
                                                var src = img.src || img.currentSrc || img.getAttribute('src') ||
                                                         img.getAttribute('data-src') || img.getAttribute('data-zoom-src');
                                                if (src && src.startsWith('http')) {
                                                    var originalUrl = getOriginalImageUrl(src);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        mainImages.push({url: originalUrl, source: 'mainPicAfterSwitch'});
                                                    }
                                                }
                                            });
                                        } catch(e) {}
                                    });
                                    
                                    // 从缩略图列表提取
                                    var thumbSelectors = ['.tb-thumb li img', '.pic-list li img', '#J_UlThumb li img'];
                                    thumbSelectors.forEach(function(sel) {
                                        try {
                                            var imgs = document.querySelectorAll(sel);
                                            imgs.forEach(function(img) {
                                                var src = img.src || img.getAttribute('src') || 
                                                         img.getAttribute('data-src') || img.getAttribute('data-original');
                                                if (src && src.startsWith('http')) {
                                                    var originalUrl = getOriginalImageUrl(src);
                                                    if (!seen.has(originalUrl)) {
                                                        seen.add(originalUrl);
                                                        mainImages.push({url: originalUrl, source: 'thumbAfterSwitch'});
                                                    }
                                                }
                                            });
                                        } catch(e) {}
                                    });
                                    
                                    return mainImages;
                                })();
                            """)
                            
                            # 处理第二次提取的主图
                            if main_images_result2:
                                main_img_added2 = 0
                                for img_info in main_images_result2:
                                    if isinstance(img_info, dict):
                                        img_url = img_info.get('url', '')
                                        source = img_info.get('source', 'unknown')
                                    else:
                                        img_url = str(img_info)
                                        source = 'unknown'
                                    
                                    if img_url and img_url.startswith('http'):
                                        clean_url = img_url.split('#')[0].strip()
                                        clean_url = self._clean_url(clean_url) if clean_url else None
                                        if clean_url and clean_url not in found_urls_html:
                                            found_urls_html.add(clean_url)
                                            name = f"主图_{len([r for r in self.resources if '主图' in r.get('name', '')]) + 1}"
                                            url_path = urlparse(clean_url).path
                                            url_filename = os.path.basename(url_path)
                                            if url_filename and url_filename not in ['', '/']:
                                                name = f"主图_{len([r for r in self.resources if '主图' in r.get('name', '')]) + 1}_{url_filename}"
                                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                            self.resources.append({
                                                'name': name,
                                                'url': clean_url,
                                                'type': 'image',
                                                'source': source
                                            })
                                            main_img_added2 += 1
                                
                                if main_img_added2 > 0:
                                    print(f"轮播切换后，新增 {main_img_added2} 个主图")
                            
                            # 等待一下，让点击事件生效
                            time.sleep(2)
                            
                            # 执行JavaScript来强制触发所有懒加载图片
                            lazy_img_result = driver.execute_script("""
                                // 强制触发所有懒加载图片
                                try {
                                    var triggered = 0;
                                    
                                    // 1. 查找所有包含data-src属性的img元素，将data-src赋值给src
                                    var lazyImages = document.querySelectorAll('img[data-src], img[data-original], img[data-lazy-src], img[data-url], img[data-img]');
                                    console.log('找到 ' + lazyImages.length + ' 个懒加载图片');
                                    lazyImages.forEach(function(img) {
                                        var src = img.getAttribute('data-src') || img.getAttribute('data-original') || 
                                                 img.getAttribute('data-lazy-src') || img.getAttribute('data-url') || 
                                                 img.getAttribute('data-img');
                                        if (src && (!img.src || img.src.startsWith('data:') || img.src === '')) {
                                            img.src = src;
                                            triggered++;
                                        }
                                    });
                                    
                                    // 2. 查找所有包含data-src属性的非img元素，也尝试触发
                                    var lazyContainers = document.querySelectorAll('[data-src]:not(img), [data-original]:not(img), [data-lazy-src]:not(img)');
                                    lazyContainers.forEach(function(container) {
                                        var src = container.getAttribute('data-src') || container.getAttribute('data-original') || 
                                                 container.getAttribute('data-lazy-src');
                                        if (src && src.startsWith('http')) {
                                            // 尝试创建img元素来加载图片
                                            var img = document.createElement('img');
                                            img.src = src;
                                            document.body.appendChild(img);
                                            triggered++;
                                        }
                                    });
                                    
                                    // 3. 触发所有图片的load事件
                                    var allImages = document.querySelectorAll('img');
                                    allImages.forEach(function(img) {
                                        if (!img.complete && img.src && !img.src.startsWith('data:')) {
                                            // 触发load事件
                                            var event = new Event('load');
                                            img.dispatchEvent(event);
                                        }
                                    });
                                    
                                    // 4. 尝试滚动所有图片容器到视口
                                    var imgContainers = document.querySelectorAll('[data-src], [data-original], [data-lazy-src]');
                                    imgContainers.forEach(function(container) {
                                        try {
                                            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                        } catch(e) {}
                                    });
                                    
                                    return JSON.stringify({ total: allImages.length, triggered: triggered });
                                } catch(e) {
                                    return JSON.stringify({ total: 0, triggered: 0, error: e.toString() });
                                }
                            """)
                            # 解析JSON字符串
                            try:
                                if lazy_img_result:
                                    import json as json_module
                                    lazy_img_result = json_module.loads(lazy_img_result)
                                    if isinstance(lazy_img_result, dict):
                                        print(f"强制触发了 {lazy_img_result.get('triggered', 0)} 个懒加载图片，当前共有 {lazy_img_result.get('total', 0)} 个img元素")
                                        if 'error' in lazy_img_result:
                                            print(f"JavaScript执行出错: {lazy_img_result.get('error')}")
                                    else:
                                        print(f"强制触发懒加载图片，返回值: {lazy_img_result}")
                                else:
                                    print("强制触发懒加载图片，未返回结果")
                            except Exception as e:
                                print(f"解析JavaScript返回值时出错: {e}, 原始返回值: {lazy_img_result}")
                            time.sleep(5)  # 增加等待时间，让懒加载图片有时间加载
                            
                            # 再次滚动，确保所有图片都加载
                            driver.execute_script("window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));")
                            time.sleep(4)
                            driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(2)
                            driver.execute_script("window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));")
                            time.sleep(4)
                            
                            # 再次从Selenium元素中提取图片（懒加载图片可能已经加载）
                            try:
                                from selenium.webdriver.common.by import By
                                selenium_images_after = driver.find_elements(By.TAG_NAME, "img")
                                print(f"懒加载触发后，Selenium找到 {len(selenium_images_after)} 个img元素")
                                new_img_count = 0
                                for img_elem in selenium_images_after:
                                    try:
                                        # 尝试多个属性（包括更多可能的属性）
                                        img_url = None
                                        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-url', 
                                                    'data-img', 'data-image', 'currentSrc', 'data-zoom', 'data-zoom-src']:
                                            img_url = img_elem.get_attribute(attr)
                                            if img_url and img_url.strip() and not img_url.strip().startswith('data:'):
                                                # 处理相对URL
                                                if img_url.startswith('//'):
                                                    img_url = urlparse(url).scheme + ':' + img_url
                                                elif not img_url.startswith('http'):
                                                    img_url = urljoin(url, img_url)
                                                if img_url.startswith('http'):
                                                    break
                                        
                                        if img_url and img_url.strip() and img_url.startswith('http') and not img_url.strip().startswith('data:'):
                                            clean_url = img_url.split('?')[0].split('#')[0].strip()
                                            # 清理URL中的错误转义字符
                                            clean_url = self._clean_url(clean_url) if clean_url else None
                                            if clean_url and clean_url not in found_urls_html:
                                                found_urls_html.add(clean_url)
                                                name = img_elem.get_attribute('alt') or img_elem.get_attribute('title') or ''
                                                if not name:
                                                    name = os.path.basename(urlparse(clean_url).path)
                                                if not name or name == '':
                                                    name = f"图片_{len(self.resources) + 1}"
                                                name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                                self.resources.append({
                                                    'name': name,
                                                    'url': clean_url,
                                                    'type': 'image'
                                                })
                                                new_img_count += 1
                                    except Exception as e:
                                        # 添加调试信息
                                        try:
                                            debug_src = img_elem.get_attribute('src')
                                            if debug_src:
                                                print(f"懒加载后提取img元素时出错: {e}, src={debug_src[:80]}")
                                        except:
                                            pass
                                        continue
                                if new_img_count > 0:
                                    print(f"懒加载触发后，新增了 {new_img_count} 个图片资源")
                            except Exception as e:
                                print(f"懒加载触发后提取图片时出错: {e}")
                        except Exception as e:
                            import traceback
                            print(f"强制触发懒加载图片时出错: {e}")
                            print(traceback.format_exc())
                    
                    # 从JavaScript对象中提取资源（通过执行JavaScript）
                    print("\n【方法4】从JavaScript对象中提取资源...")
                    js_obj_count_before = len(self.resources)
                    try:
                        # 改进的JavaScript提取脚本，尝试更多可能的数据结构
                        js_extract_script = """
                        (function() {
                            var js_resources = [];
                            
                            // 方法1: 从window对象中递归查找所有图片URL
                            function findImageUrls(obj, depth, visited) {
                                if (depth > 8 || visited.has(obj)) return; // 防止无限递归
                                if (!obj || typeof obj !== 'object') return;
                                visited.add(obj);
                                
                                try {
                                    if (Array.isArray(obj)) {
                                        obj.forEach(function(item) {
                                            if (typeof item === 'string' && item.startsWith('http')) {
                                                if (item.match(/\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|mp4|webm|avi|mov|flv|mkv)(\?|$)/i) ||
                                                    item.match(/(alicdn|taobaocdn|tbcdn|img|image|pic|photo|cdn)/i)) {
                                                    js_resources.push(item);
                                                }
                                            } else if (item && typeof item === 'object') {
                                                findImageUrls(item, depth + 1, visited);
                                            }
                                        });
                                    } else {
                                        for (var key in obj) {
                                            if (!obj.hasOwnProperty(key)) continue;
                                            var value = obj[key];
                                            
                                            if (typeof value === 'string' && value.startsWith('http')) {
                                                if (value.match(/\.(jpg|jpeg|png|gif|webp|bmp|ico|svg|mp4|webm|avi|mov|flv|mkv)(\?|$)/i) ||
                                                    value.match(/(alicdn|taobaocdn|tbcdn|img|image|pic|photo|cdn)/i)) {
                                                    js_resources.push(value);
                                                }
                                            } else if (value && typeof value === 'object') {
                                                findImageUrls(value, depth + 1, visited);
                                            }
                                        }
                                    }
                                } catch(e) {}
                            }
                            
                            // 从所有可能的全局对象中查找（扩展列表）
                            var searchObjects = ['TB', 'g_config', 'runParams', 'itemData', 'skuData', 'detailData', 'itemDetail', 'skuMap', 
                                                 'item', 'product', 'goods', 'detail', 'images', 'pics', 'photos', 'gallery', 'album',
                                                 'data', 'config', 'pageData', 'pageData', 'props', 'state', 'store', 'model', 'viewModel'];
                            var visited = new WeakSet();
                            searchObjects.forEach(function(objName) {
                                try {
                                    var obj = window[objName];
                                    if (obj && typeof obj === 'object') {
                                        findImageUrls(obj, 0, visited);
                                    }
                                } catch(e) {}
                            });
                            
                            // 更全面：遍历window对象的所有属性（深度限制）
                            try {
                                var windowKeys = Object.keys(window);
                                for (var i = 0; i < windowKeys.length && i < 200; i++) { // 限制最多检查200个属性
                                    var key = windowKeys[i];
                                    try {
                                        // 跳过一些明显不相关的属性
                                        if (key.startsWith('webkit') || key.startsWith('moz') || key.startsWith('ms') || 
                                            key === 'document' || key === 'navigator' || key === 'location' || 
                                            key === 'history' || key === 'screen' || key === 'console' || 
                                            key === 'performance' || key === 'localStorage' || key === 'sessionStorage') {
                                            continue;
                                        }
                                        var obj = window[key];
                                        if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
                                            try {
                                                // 尝试访问对象属性（可能有访问限制）
                                                if (Object.keys(obj).length > 0 || obj.length > 0) {
                                                    findImageUrls(obj, 0, visited);
                                                }
                                            } catch(e) {}
                                        }
                                    } catch(e) {}
                                }
                            } catch(e) {
                                console.error('遍历window对象时出错:', e);
                            }
                            
                            // 方法2: 从DOM元素中提取所有图片URL（包括懒加载的）
                            try {
                                var allImages = document.querySelectorAll('img');
                                console.log('找到 ' + allImages.length + ' 个img元素');
                                allImages.forEach(function(img, index) {
                                    // 尝试更多可能的属性
                                    var sources = [
                                        img.src,
                                        img.currentSrc, // 当前实际使用的src（包括srcset）
                                        img.getAttribute('src'),
                                        img.getAttribute('data-src'),
                                        img.getAttribute('data-original'),
                                        img.getAttribute('data-lazy-src'),
                                        img.getAttribute('data-url'),
                                        img.getAttribute('data-img'),
                                        img.getAttribute('data-image'),
                                        img.getAttribute('data-srcset'),
                                        img.getAttribute('srcset'),
                                        img.getAttribute('data-zoom'),
                                        img.getAttribute('data-zoom-src'),
                                        img.getAttribute('data-lazy'),
                                        img.getAttribute('lazy-src'),
                                        img.getAttribute('original-src'),
                                        img.getAttribute('data-original-src'),
                                        img.getAttribute('data-full'),
                                        img.getAttribute('data-large'),
                                        img.getAttribute('data-webp'),
                                        img.getAttribute('webp')
                                    ];
                                    sources.forEach(function(src) {
                                        if (src && (src.startsWith('http') || src.startsWith('//')) && !src.startsWith('data:')) {
                                            // 处理相对URL
                                            if (src.startsWith('//')) {
                                                src = window.location.protocol + src;
                                            }
                                            // 处理srcset格式
                                            if (src.includes(',')) {
                                                var urls = src.split(',');
                                                urls.forEach(function(url) {
                                                    url = url.trim().split(' ')[0];
                                                    if (url && (url.startsWith('http') || url.startsWith('//'))) {
                                                        if (url.startsWith('//')) {
                                                            url = window.location.protocol + url;
                                                        }
                                                        js_resources.push(url);
                                                    }
                                                });
                                            } else {
                                                js_resources.push(src);
                                            }
                                        }
                                    });
                                });
                                
                                // 也查找所有可能的图片容器（淘宝商品详情页可能使用div包裹图片）
                                var imgContainers = document.querySelectorAll('[class*="img"], [class*="image"], [class*="pic"], [class*="photo"], [id*="img"], [id*="image"]');
                                imgContainers.forEach(function(container) {
                                    var style = window.getComputedStyle(container);
                                    var bgImage = style.backgroundImage;
                                    if (bgImage && bgImage !== 'none') {
                                        var matches = bgImage.match(/url\(["']?([^"')]+)["']?\)/);
                                        if (matches && matches[1]) {
                                            var url = matches[1];
                                            if ((url.startsWith('http') || url.startsWith('//')) && !url.startsWith('data:')) {
                                                if (url.startsWith('//')) {
                                                    url = window.location.protocol + url;
                                                }
                                                js_resources.push(url);
                                            }
                                        }
                                    }
                                    // 检查data属性
                                    ['data-src', 'data-original', 'data-url', 'data-img', 'data-image'].forEach(function(attr) {
                                        var attrValue = container.getAttribute(attr);
                                        if (attrValue && (attrValue.startsWith('http') || attrValue.startsWith('//')) && !attrValue.startsWith('data:')) {
                                            if (attrValue.startsWith('//')) {
                                                attrValue = window.location.protocol + attrValue;
                                            }
                                            js_resources.push(attrValue);
                                        }
                                    });
                                });
                            } catch(e) {
                                console.error('从DOM提取图片时出错:', e);
                            }
                            
                            // 方法3: 从所有可能的CSS背景图片中提取（包括多重背景）
                            try {
                                var allElements = document.querySelectorAll('*');
                                allElements.forEach(function(elem) {
                                    try {
                                        var style = window.getComputedStyle(elem);
                                        var bgImage = style.backgroundImage;
                                        if (bgImage && bgImage !== 'none') {
                                            // 支持多重背景图片（多个url()）
                                            var matches = bgImage.match(/url\(["']?([^"')]+)["']?\)/g);
                                            if (matches) {
                                                matches.forEach(function(match) {
                                                    var urlMatch = match.match(/url\(["']?([^"')]+)["']?\)/);
                                                    if (urlMatch && urlMatch[1]) {
                                                        var url = urlMatch[1];
                                                        if (url.startsWith('http') || url.startsWith('//')) {
                                                            if (url.startsWith('//')) {
                                                                url = window.location.protocol + url;
                                                            }
                                                            js_resources.push(url);
                                                        }
                                                    }
                                                });
                                            }
                                        }
                                    } catch(e) {}
                                });
                            } catch(e) {}
                            
                            // 方法4: 检查所有data-*属性（可能包含图片URL）
                            try {
                                var allElementsWithData = document.querySelectorAll('[data-src], [data-img], [data-image], [data-url], [data-original], [data-lazy], [data-lazy-src], [data-zoom], [data-zoom-src]');
                                allElementsWithData.forEach(function(elem) {
                                    var attrs = ['data-src', 'data-img', 'data-image', 'data-url', 'data-original', 'data-lazy', 'data-lazy-src', 'data-zoom', 'data-zoom-src', 'data-full', 'data-large', 'data-thumb', 'data-thumbnail'];
                                    attrs.forEach(function(attr) {
                                        var value = elem.getAttribute(attr);
                                        if (value && (value.startsWith('http') || value.startsWith('//')) && !value.startsWith('data:')) {
                                            if (value.startsWith('//')) {
                                                value = window.location.protocol + value;
                                            }
                                            js_resources.push(value);
                                        }
                                    });
                                });
                            } catch(e) {}
                            
                            // 方法5: 检查picture标签的source子元素
                            try {
                                var pictures = document.querySelectorAll('picture');
                                pictures.forEach(function(picture) {
                                    var sources = picture.querySelectorAll('source');
                                    sources.forEach(function(source) {
                                        var srcset = source.getAttribute('srcset');
                                        if (srcset) {
                                            var urls = srcset.split(',');
                                            urls.forEach(function(urlItem) {
                                                var url = urlItem.trim().split(' ')[0];
                                                if (url && (url.startsWith('http') || url.startsWith('//')) && !url.startsWith('data:')) {
                                                    if (url.startsWith('//')) {
                                                        url = window.location.protocol + url;
                                                    }
                                                    js_resources.push(url);
                                                }
                                            });
                                        }
                                        var src = source.getAttribute('src');
                                        if (src && (src.startsWith('http') || src.startsWith('//')) && !src.startsWith('data:')) {
                                            if (src.startsWith('//')) {
                                                src = window.location.protocol + src;
                                            }
                                            js_resources.push(src);
                                        }
                                    });
                                });
                            } catch(e) {}
                            
                            // 方法6: 检查link标签的preload/prefetch资源
                            try {
                                var links = document.querySelectorAll('link[rel="preload"], link[rel="prefetch"], link[rel="dns-prefetch"]');
                                links.forEach(function(link) {
                                    var href = link.getAttribute('href');
                                    if (href && (href.startsWith('http') || href.startsWith('//')) && !href.startsWith('data:')) {
                                        var as = link.getAttribute('as');
                                        if (as === 'image' || as === 'video' || !as) {
                                            if (href.startsWith('//')) {
                                                href = window.location.protocol + href;
                                            }
                                            js_resources.push(href);
                                        }
                                    }
                                });
                            } catch(e) {}
                            
                            // 方法7: 检查video标签的source子元素和poster属性
                            try {
                                var videos = document.querySelectorAll('video');
                                videos.forEach(function(video) {
                                    // 检查poster属性（视频封面图）
                                    var poster = video.getAttribute('poster');
                                    if (poster && (poster.startsWith('http') || poster.startsWith('//')) && !poster.startsWith('data:')) {
                                        if (poster.startsWith('//')) {
                                            poster = window.location.protocol + poster;
                                        }
                                        js_resources.push(poster);
                                    }
                                    // 检查source子元素
                                    var sources = video.querySelectorAll('source');
                                    sources.forEach(function(source) {
                                        var src = source.getAttribute('src');
                                        if (src && (src.startsWith('http') || src.startsWith('//')) && !src.startsWith('data:')) {
                                            if (src.startsWith('//')) {
                                                src = window.location.protocol + src;
                                            }
                                            js_resources.push(src);
                                        }
                                    });
                                });
                            } catch(e) {}
                            
                            // 方法8: 检查iframe中的资源（递归）
                            try {
                                var iframes = document.querySelectorAll('iframe');
                                iframes.forEach(function(iframe) {
                                    try {
                                        var iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                                        if (iframeDoc) {
                                            var iframeImgs = iframeDoc.querySelectorAll('img');
                                            iframeImgs.forEach(function(img) {
                                                var src = img.src || img.getAttribute('src') || img.getAttribute('data-src');
                                                if (src && (src.startsWith('http') || src.startsWith('//')) && !src.startsWith('data:')) {
                                                    if (src.startsWith('//')) {
                                                        src = window.location.protocol + src;
                                                    }
                                                    js_resources.push(src);
                                                }
                                            });
                                        }
                                    } catch(e) {
                                        // 跨域iframe无法访问，跳过
                                    }
                                });
                            } catch(e) {}
                            
                            return Array.from(new Set(js_resources));
                        })();
                        """
                        try:
                            js_obj_resources = driver.execute_script(js_extract_script)
                        except Exception as js_error:
                            print(f"执行JavaScript时出错: {js_error}")
                            js_obj_resources = []
                        
                        js_obj_count = 0
                        # 确保js_obj_resources是列表
                        if js_obj_resources is None:
                            print("警告：JavaScript返回None，尝试使用备用方法...")
                            # 备用方法：直接从DOM中提取所有图片URL
                            try:
                                js_obj_resources = driver.execute_script("""
                                    var resources = [];
                                    var imgs = document.querySelectorAll('img');
                                    imgs.forEach(function(img) {
                                        var src = img.src || img.currentSrc || img.getAttribute('data-src') || img.getAttribute('data-original') || img.getAttribute('data-lazy-src');
                                        if (src && src.startsWith('http') && !src.startsWith('data:')) {
                                            resources.push(src);
                                        }
                                        var srcset = img.getAttribute('srcset') || img.getAttribute('data-srcset');
                                        if (srcset) {
                                            srcset.split(',').forEach(function(item) {
                                                var url = item.trim().split(' ')[0];
                                                if (url && url.startsWith('http') && !url.startsWith('data:')) {
                                                    resources.push(url);
                                                }
                                            });
                                        }
                                    });
                                    return Array.from(new Set(resources));
                                """)
                                print(f"备用方法找到 {len(js_obj_resources) if js_obj_resources else 0} 个资源")
                            except Exception as backup_error:
                                print(f"备用方法也失败: {backup_error}")
                                js_obj_resources = []
                        
                        if js_obj_resources and isinstance(js_obj_resources, list) and len(js_obj_resources) > 0:
                            print(f"从JavaScript对象中提取到 {len(js_obj_resources)} 个资源")
                            for js_url in js_obj_resources:
                                if js_url and js_url.startswith('http'):
                                    clean_url = js_url.split('?')[0].split('#')[0].strip()
                                    # 清理URL中的错误转义字符
                                    clean_url = self._clean_url(clean_url) if clean_url else None
                                    if clean_url and clean_url not in found_urls_html:
                                        found_urls_html.add(clean_url)
                                        # 判断是图片还是视频
                                        path = urlparse(clean_url).path.lower()
                                        is_video = any(ext in path for ext in ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv'])
                                        is_image = any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg']) or not is_video
                                        resource_type = 'video' if is_video else 'image'
                                        name = os.path.basename(urlparse(clean_url).path) or f"资源_{len(self.resources) + 1}"
                                        name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                        self.resources.append({
                                            'name': name,
                                            'url': clean_url,
                                            'type': resource_type
                                        })
                                        js_obj_count += 1
                            js_obj_count_after = len(self.resources)
                            print(f"从JavaScript对象中添加了 {js_obj_count} 个资源（当前总数: {len(self.resources)}，新增: {js_obj_count_after - js_obj_count_before}）")
                        else:
                            if js_obj_resources is None:
                                print("从JavaScript对象中未提取到资源（返回值为None）")
                            elif isinstance(js_obj_resources, list):
                                print(f"从JavaScript对象中未提取到资源（返回空数组，长度为{len(js_obj_resources)}）")
                            else:
                                print(f"从JavaScript对象中未提取到资源（返回值类型: {type(js_obj_resources)}，值: {js_obj_resources}")
                    except Exception as e:
                        import traceback
                        print(f"从JavaScript对象提取资源时出错: {e}")
                        print(traceback.format_exc())
                    
                    # 从HTML中提取所有图片标签
                    print("\n【方法5】从HTML中提取所有img标签...")
                    html_bs4_count_before = len(self.resources)
                    images = soup.find_all('img')
                    print(f"从HTML中找到 {len(images)} 个img标签")
                    html_img_count = 0
                    for img in images:
                        # 尝试多种可能的属性
                        img_url = None
                        for attr in ['src', 'data-src', 'data-original', 'data-lazy-src', 'data-srcset', 
                                    'data-url', 'data-img', 'data-image', 'srcset', 'data-webp', 'webp']:
                            img_url = img.get(attr)
                            if img_url:
                                # 处理srcset格式：可能包含多个URL（包括webp）
                                if attr == 'srcset' or attr == 'data-srcset':
                                    # srcset格式：url1 1x, url2 2x 或 url1 100w, url2 200w
                                    # 提取所有URL（包括webp格式）
                                    urls = re.findall(r'([^\s,]+)', img_url)
                                    if urls:
                                        # 处理srcset中的所有URL（包括webp）
                                        for url_item in urls:
                                            url_item = url_item.strip()
                                            if url_item and not url_item.startswith('data:'):
                                                full_url_item = urljoin(url, url_item)
                                                # 排除明显的非媒体文件
                                                excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                                                path_item = urlparse(full_url_item).path.lower()
                                                if any(path_item.endswith(ext) for ext in excluded_exts):
                                                    continue
                                                clean_url_item = full_url_item.split('?')[0].split('#')[0].strip()
                                                if clean_url_item not in found_urls_html:
                                                    found_urls_html.add(clean_url_item)
                                                    name = img.get('alt') or img.get('title') or os.path.basename(urlparse(clean_url_item).path) or f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                                                    name = re.sub(r'[<>:"/\\|?*]', '_', name)
                                                    self.resources.append({
                                                        'name': name,
                                                        'url': clean_url_item,
                                                        'type': 'image'
                                                    })
                                                    html_img_count += 1
                                        # srcset处理完后，继续处理其他属性
                                        img_url = urls[0] if urls else None
                                    else:
                                        img_url = None
                                
                                if img_url and img_url.strip():
                                    break
                        
                        if img_url:
                            # 清理URL（只移除片段，保留查询参数）
                            img_url = img_url.split('#')[0].strip()
                            
                            # 处理base64图片
                            if img_url.startswith('data:image/'):
                                self._process_base64_image(img_url, found_urls)
                                continue
                            # 跳过其他非图片的data URL和javascript
                            if img_url.startswith('data:') or img_url.startswith('javascript:'):
                                continue
                            
                            # 转换为绝对URL
                            full_url = urljoin(url, img_url)
                            
                            # 验证URL格式（更宽松的验证）
                            try:
                                parsed = urlparse(full_url)
                                if not parsed.scheme or not parsed.netloc:
                                    continue
                            except:
                                continue
                            
                            # 排除明显的非媒体文件（只排除.js, .css, .html等）
                            excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                            path = parsed.path.lower()
                            # 只在路径中检查，不在查询参数中
                            if any(path.endswith(ext) for ext in excluded_exts):
                                continue
                            
                            # 去重（使用完整URL，包括查询参数）
                            clean_url = full_url.split('#')[0].strip()  # 只移除片段，保留查询参数
                            if clean_url in found_urls_html:
                                continue
                            found_urls_html.add(clean_url)
                            
                            # 获取名称
                            name = img.get('alt') or img.get('title') or ''
                            if not name:
                                # 尝试从URL路径中提取文件名
                                path = parsed.path
                                name = os.path.basename(path)
                                # 如果路径中没有文件名，尝试从查询参数中提取
                                if not name or name == '':
                                    query = parsed.query
                                    if query:
                                        # 尝试从查询参数中提取文件名
                                        for param in query.split('&'):
                                            if '=' in param:
                                                key, value = param.split('=', 1)
                                                if key.lower() in ['name', 'file', 'filename', 'img']:
                                                    name = value
                                                    break
                            if not name or name == '':
                                name = f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                            
                            # 清理名称
                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                            
                            self.resources.append({
                                'name': name,
                                'url': clean_url,
                                'type': 'image'
                            })
                            html_img_count += 1
                    
                    html_bs4_count_after = len(self.resources)
                    print(f"从HTML的img标签中提取了 {html_img_count} 个图片资源（当前总数: {len(self.resources)}，新增: {html_bs4_count_after - html_bs4_count_before}）")
                    
                    # 从HTML文本中直接提取所有图片URL（更全面的方法）
                    print("\n【方法6】从HTML文本中直接提取所有图片URL（第二次扫描）...")
                    html_text2_count_before = len(self.resources)
                    html_text = str(soup)
                    # 匹配所有可能的图片URL格式（包括webp），更全面的正则表达式
                    img_url_patterns = [
                        r'https?://[^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg)(\?[^\s<>"\'\)]*)?',
                        r'//[^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg)(\?[^\s<>"\'\)]*)?',
                        r'["\']([^\s<>"\'\)]+\.(jpg|jpeg|png|gif|webp|bmp|ico|svg))(\?[^\s<>"\'\)]*)?["\']',
                    ]
                    
                    html_text_count = 0
                    for pattern in img_url_patterns:
                        matches = re.finditer(pattern, html_text, re.IGNORECASE)
                        for match in matches:
                            img_url = match.group(0)
                            # 清理引号
                            img_url = img_url.strip('"\'')
                            # 如果是相对URL，转换为绝对URL
                            if img_url.startswith('//'):
                                img_url = urlparse(url).scheme + ':' + img_url
                            elif not img_url.startswith('http'):
                                img_url = urljoin(url, img_url)
                            
                            # 清理URL（移除查询参数中的尺寸等，但保留基本URL）
                            clean_url = img_url.split('?')[0].split('#')[0].strip()
                            
                            # 排除明显的非媒体文件
                            excluded_exts = ['.js', '.css', '.html', '.htm', '.json', '.xml', '.txt']
                            path = urlparse(clean_url).path.lower()
                            if any(path.endswith(ext) for ext in excluded_exts):
                                continue
                            
                            # 处理base64图片
                            if clean_url.startswith('data:image/'):
                                self._process_base64_image(clean_url, found_urls)
                                continue
                            # 跳过其他非图片的data URL和javascript
                            if clean_url.startswith('data:') or clean_url.startswith('javascript:'):
                                continue
                            
                            # 验证是否是图片URL（检查扩展名）
                            if not self._is_image_url(clean_url):
                                continue
                            
                            # 去重
                            if clean_url in found_urls_html:
                                continue
                            found_urls_html.add(clean_url)
                            
                            # 获取名称
                            name = os.path.basename(urlparse(clean_url).path) or f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                            if not name or name == '':
                                name = f"图片_{len([r for r in self.resources if r['type'] == 'image']) + 1}"
                            name = re.sub(r'[<>:"/\\|?*]', '_', name)
                            
                            self.resources.append({
                                'name': name,
                                'url': clean_url,
                                'type': 'image'
                            })
                            html_text_count += 1
                    
                    html_text2_count_after = len(self.resources)
                    print(f"从HTML文本中提取了 {html_text_count} 个图片资源（当前总数: {len(self.resources)}，新增: {html_text2_count_after - html_text2_count_before}）")
                    
                    # 最终统计
                    print("\n" + "=" * 80)
                    print("资源提取统计汇总：")
                    # 计算Network请求的资源数量（如果存在）
                    # network_count_before在1802行定义，network_count_after在1926行定义
                    try:
                        if 'network_count_before' in locals() and 'network_count_after' in locals():
                            network_count_added = network_count_after - network_count_before
                            if network_count_added > 0:
                                print(f"  方法0（Network请求）: 新增 {network_count_added} 个资源")
                        elif 'network_count_after' in locals():
                            # 如果network_count_before不在，说明可能没有执行到那里，使用network_count_after作为参考
                            print(f"  方法0（Network请求）: 新增约 {network_count_after} 个资源（统计可能不准确）")
                    except:
                        pass  # 如果变量不存在，跳过Network请求的统计
                    print(f"  方法1（HTML文本扫描）: 新增 {html_text_added} 个资源")
                    if 'taobao_count_before' in locals() and 'taobao_count_after' in locals():
                        if 'taobao.com' in url.lower() or 'tmall.com' in url.lower():
                            print(f"  方法2（淘宝资源提取）: 新增 {taobao_count_after - taobao_count_before} 个资源")
                    if 'selenium_count_before' in locals() and 'selenium_count_after' in locals():
                        print(f"  方法3（Selenium元素）: 新增 {selenium_count_after - selenium_count_before} 个资源")
                    if 'js_obj_count_before' in locals() and 'js_obj_count_after' in locals():
                        print(f"  方法4（JavaScript对象）: 新增 {js_obj_count_after - js_obj_count_before} 个资源")
                    if 'html_bs4_count_before' in locals() and 'html_bs4_count_after' in locals():
                        print(f"  方法5（HTML img标签）: 新增 {html_bs4_count_after - html_bs4_count_before} 个资源")
                    if 'html_text2_count_before' in locals() and 'html_text2_count_after' in locals():
                        print(f"  方法6（HTML文本扫描2）: 新增 {html_text2_count_after - html_text2_count_before} 个资源")
                    print(f"  总计找到资源: {len(self.resources)} 个")
                    print("=" * 80 + "\n")
                    
                except Exception as e:
                    import traceback
                    print(f"从HTML提取资源时出错: {e}")
                    print(traceback.format_exc())
            
            driver.quit()
            return html_content
            
        except Exception as e:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            import traceback
            error_detail = traceback.format_exc()
            print(f"Selenium错误: {e}")
            print(f"错误详情: {error_detail}")
            return None
    
    def show_error(self, message):
        """显示错误信息"""
        self.status_text.SetLabel(message)
        self.status_text.SetForegroundColour(wx.Colour(245, 108, 108))
        self.confirm_btn.Enable(True)
        wx.MessageBox(message, "错误", wx.OK | wx.ICON_ERROR)
    
    def show_js_warning(self, url):
        """显示JavaScript页面警告"""
        if SELENIUM_AVAILABLE:
            msg = "检测到网页使用JavaScript动态加载内容，未找到图片资源。\n\n是否使用浏览器渲染重新尝试？\n\n（这将使用Chrome浏览器加载页面，需要安装Chrome浏览器）"
            dlg = wx.MessageDialog(self, msg, "提示", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                # 自动勾选Selenium选项并重新获取
                self.use_selenium_check.SetValue(True)
                self.on_confirm(None)
            else:
                dlg.Destroy()
                self.status_text.SetLabel("未找到任何资源（网页使用JavaScript动态加载，请勾选'使用浏览器渲染'选项）")
                self.status_text.SetForegroundColour(wx.Colour(226, 192, 0))
                self.confirm_btn.Enable(True)
        else:
            msg = "检测到网页使用JavaScript动态加载内容，未找到图片资源。\n\n请安装Selenium以支持浏览器渲染：\n\npip install selenium\n\n并确保已安装Chrome浏览器和ChromeDriver。"
            wx.MessageBox(msg, "提示", wx.OK | wx.ICON_INFORMATION)
            self.status_text.SetLabel("未找到任何资源（网页使用JavaScript动态加载，需要安装Selenium）")
            self.status_text.SetForegroundColour(wx.Colour(226, 192, 0))
            self.confirm_btn.Enable(True)
    
    def update_resource_list(self, img_count=0, total_img_tags=0, html_length=0):
        """更新资源列表UI"""
        # 清空现有列表
        self.resource_sizer.Clear(True)
        
        if not self.resources:
            debug_msg = f"未找到任何资源（网页中共有 {total_img_tags} 个img标签，HTML长度: {html_length} 字符）"
            if total_img_tags == 0 and html_length > 0:
                debug_msg += "\n提示：如果网页使用JavaScript动态加载内容，请勾选'使用浏览器渲染'选项"
            self.status_text.SetLabel(debug_msg)
            self.status_text.SetForegroundColour(wx.Colour(226, 192, 0))
            self.confirm_btn.Enable(True)
            # 清空复选框字典并禁用批量下载按钮
            self.checkboxes = {}
            if hasattr(self, 'batch_download_btn'):
                self.batch_download_btn.Enable(False)
            return
        
        # 初始化复选框字典
        self.checkboxes = {}
        
        # 批量下载按钮初始状态为禁用（需要选中资源才能下载）
        if hasattr(self, 'batch_download_btn'):
            self.batch_download_btn.Enable(False)
        
        # 添加资源项
        for idx, resource in enumerate(self.resources):
            self.add_resource_item(resource, idx)
        
        # 刷新布局并更新滚动区域（重要：确保滚动功能正常工作）
        self.resource_sizer.Layout()
        self.scroll_panel.Layout()
        
        # 重新设置滚动（确保内容更新后滚动条正确显示）
        self.scroll_panel.SetupScrolling(scroll_x=True, scroll_y=True, rate_x=20, rate_y=20)
        
        # 强制刷新并滚动到顶部
        self.scroll_panel.Refresh()
        self.scroll_panel.Update()
        
        # 滚动到顶部
        self.scroll_panel.Scroll(0, 0)
        
        image_count = len([r for r in self.resources if r['type'] == 'image'])
        video_count = len([r for r in self.resources if r['type'] == 'video'])
        self.status_text.SetLabel(f"找到 {len(self.resources)} 个资源（图片：{image_count} 个，视频：{video_count} 个）")
        self.status_text.SetForegroundColour(wx.Colour(103, 194, 58))
        self.confirm_btn.Enable(True)
    
    def add_resource_item(self, resource, index):
        """添加资源项到列表"""
        # 创建资源项面板
        item_panel = wx.Panel(self.scroll_panel)
        item_panel.SetBackgroundColour(wx.Colour(250, 252, 255) if index % 2 == 0 else wx.Colour(255, 255, 255))
        item_panel.SetMinSize((-1, 100))  # 增加高度以容纳缩略图
        
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 复选框（用于批量下载选择）
        checkbox = wx.CheckBox(item_panel)
        checkbox.SetValue(False)  # 默认不选中
        checkbox.Bind(wx.EVT_CHECKBOX, lambda e: self.on_checkbox_changed())
        self.checkboxes[index] = checkbox
        item_sizer.Add(checkbox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # 缩略图区域
        thumbnail_panel = wx.Panel(item_panel)
        thumbnail_panel.SetBackgroundColour(wx.Colour(240, 242, 245))
        thumbnail_panel.SetMinSize((100, 90))
        thumbnail_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 缩略图（异步加载）
        thumbnail_bitmap = wx.StaticBitmap(thumbnail_panel, size=(90, 70))
        thumbnail_bitmap.SetBackgroundColour(wx.Colour(240, 242, 245))
        
        # 加载占位符
        placeholder_text = "加载中..." if resource['type'] == 'image' else "视频"
        placeholder_label = wx.StaticText(thumbnail_panel, label=placeholder_text)
        placeholder_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                         wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        placeholder_label.SetForegroundColour(wx.Colour(150, 150, 150))
        thumbnail_sizer.Add(placeholder_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        thumbnail_sizer.Add(thumbnail_bitmap, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        thumbnail_panel.SetSizer(thumbnail_sizer)
        
        # 绑定点击事件（预览）
        thumbnail_panel.Bind(wx.EVT_LEFT_DOWN, lambda e, r=resource: self.preview_resource(r))
        thumbnail_bitmap.Bind(wx.EVT_LEFT_DOWN, lambda e, r=resource: self.preview_resource(r))
        placeholder_label.Bind(wx.EVT_LEFT_DOWN, lambda e, r=resource: self.preview_resource(r))
        thumbnail_panel.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        thumbnail_bitmap.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        placeholder_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        
        item_sizer.Add(thumbnail_panel, 0, wx.ALL, 5)
        
        # 右侧信息区域
        info_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 资源名称
        name_label = wx.StaticText(item_panel, label=resource['name'][:80])
        name_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                  wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        name_label.SetForegroundColour(wx.Colour(48, 49, 51))
        name_label.Wrap(400)
        info_sizer.Add(name_label, 0, wx.ALL, 3)
        
        # 下载地址（可选中）
        url_text = wx.TextCtrl(item_panel, value=resource['url'], style=wx.TE_READONLY)
        url_text.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, faceName="Consolas"))
        url_text.SetBackgroundColour(wx.Colour(245, 247, 250))
        info_sizer.Add(url_text, 1, wx.EXPAND | wx.ALL, 3)
        
        # 按钮区域
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 预览按钮
        preview_btn = wx.Button(item_panel, label="预览", size=(70, 30))
        preview_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        preview_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        preview_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        preview_btn.Bind(wx.EVT_BUTTON, lambda e, r=resource: self.preview_resource(r))
        preview_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=preview_btn: b.SetBackgroundColour(wx.Colour(85, 170, 255)))
        preview_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=preview_btn: b.SetBackgroundColour(wx.Colour(64, 158, 255)))
        btn_sizer.Add(preview_btn, 0, wx.ALL, 2)
        
        # 下载按钮
        download_btn = wx.Button(item_panel, label="下载", size=(70, 30))
        download_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        download_btn.SetBackgroundColour(wx.Colour(103, 194, 58))
        download_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        download_btn.Bind(wx.EVT_BUTTON, lambda e, r=resource: self.download_resource(r))
        download_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=download_btn: b.SetBackgroundColour(wx.Colour(133, 224, 88)))
        download_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=download_btn: b.SetBackgroundColour(wx.Colour(103, 194, 58)))
        btn_sizer.Add(download_btn, 0, wx.ALL, 2)
        
        info_sizer.Add(btn_sizer, 0, wx.ALL, 3)
        item_sizer.Add(info_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        item_panel.SetSizer(item_sizer)
        self.resource_sizer.Add(item_panel, 0, wx.EXPAND | wx.ALL, 2)
        
        # 异步加载缩略图
        thread = threading.Thread(target=self.load_thumbnail, args=(resource, thumbnail_bitmap, placeholder_label))
        thread.daemon = True
        thread.start()
    
    def _is_image_url(self, url):
        """检查URL是否是图片URL（通过后缀名判断）"""
        if not url:
            return False
        # 检查是否是base64图片
        if url.startswith('data:image/'):
            return True
        
        url_lower = url.lower()
        
        # 【关键】检查URL中是否包含.webp或.avif（最高优先级，包括特殊格式如.jpg_.webp）
        if '.webp' in url_lower or '.avif' in url_lower:
            return True
        
        # 只检查URL路径部分，不检查查询参数
        path = urlparse(url).path.lower()
        # 检查路径中是否包含图片扩展名（不要求严格以扩展名结尾，因为可能有查询参数）
        # 添加avif格式支持，包括.webp和.avif
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif']
        # 检查路径中是否包含这些扩展名
        if any(ext in path for ext in image_exts):
            return True
        
        # 【关键】检查imgextra路径（淘宝图片URL特征）
        if 'imgextra' in url_lower:
            # 如果URL包含imgextra，很可能是图片（不需要检查数字路径）
            return True
        
        # 【关键】检查URL路径中包含图片相关关键字
        if any(keyword in url_lower for keyword in ['/img/', '/image/', '/pic/', '/photo/', '/picture/', 'alicdn', 'taobaocdn']):
            return True
        
        return False
    
    def _process_base64_image(self, data_url, found_urls):
        """处理base64图片，将其添加到资源列表"""
        try:
            # base64格式：data:image/png;base64,xxxxx 或 data:image/jpeg;base64,xxxxx
            if not data_url.startswith('data:image/'):
                return False
            
            # 解析base64数据
            header, data = data_url.split(',', 1)
            # 从header中提取MIME类型
            mime_type = header.split(';')[0].replace('data:', '')
            
            # 解码base64数据
            import base64
            try:
                image_data = base64.b64decode(data)
            except Exception as e:
                print(f"Base64解码失败: {e}")
                return False
            
            # 生成文件名（基于MIME类型和索引）
            ext_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp',
                'image/bmp': '.bmp',
                'image/svg+xml': '.svg',
                'image/avif': '.avif'
            }
            ext = ext_map.get(mime_type, '.png')
            name = f"base64图片_{len([r for r in self.resources if r['type'] == 'image' and r['url'].startswith('data:')]) + 1}{ext}"
            
            # 添加到资源列表（使用data_url作为唯一标识）
            if data_url not in found_urls:
                found_urls.add(data_url)
                self.resources.append({
                    'name': name,
                    'url': data_url,  # 保存完整的data URL
                    'type': 'image',
                    'base64_data': image_data,  # 保存解码后的数据，用于下载
                    'mime_type': mime_type
                })
                return True
        except Exception as e:
            print(f"处理base64图片时出错: {e}")
        return False
    
    def _is_video_url(self, url):
        """检查URL是否是视频URL（通过后缀名判断）"""
        if not url:
            return False
        # 只检查URL路径部分，不检查查询参数
        path = urlparse(url).path.lower()
        # 检查路径中是否包含视频扩展名
        video_exts = ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv', '.m3u8', '.ts', '.f4v', '.mpg', '.mpeg', '.m4v']
        return any(ext in path for ext in video_exts)
    
    def load_thumbnail(self, resource, thumbnail_bitmap, placeholder_label):
        """异步加载缩略图（支持avif和webp格式，以及base64图片）"""
        try:
            url = resource['url']
            
            if resource['type'] == 'image':
                # 【关键】处理base64图片
                if url.startswith('data:image/'):
                    if 'base64_data' in resource:
                        image_data = resource['base64_data']
                        # 使用PIL或wx.Image加载base64图片
                        try:
                            from io import BytesIO
                            if PIL_AVAILABLE:
                                img = Image.open(BytesIO(image_data))
                                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                                wx_img = wx.Image(img.size[0], img.size[1])
                                wx_img.SetData(img.convert('RGB').tobytes())
                            else:
                                wx_img = wx.ImageFromStream(BytesIO(image_data))
                            
                            if wx_img.IsOk():
                                wx_img = wx_img.Scale(150, 150, wx.IMAGE_QUALITY_HIGH)
                                bitmap = wx.Bitmap(wx_img)
                                wx.CallAfter(thumbnail_bitmap.SetBitmap, bitmap)
                                return
                        except Exception as e:
                            print(f"加载base64缩略图失败: {e}")
                    # 如果加载失败，显示占位符
                    wx.CallAfter(placeholder_label.Show)
                    return
                
                # 加载网络图片缩略图（优先使用PIL处理avif/webp格式）
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': urlparse(url).scheme + '://' + urlparse(url).netloc
                }
                
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                response.raise_for_status()
                img_data = response.content
                
                # 如果数据太小，显示错误
                if len(img_data) < 50:
                    wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
                    return
                
                # 检查是否是avif或webp格式（wx.Image可能不支持，优先使用PIL）
                url_lower = url.lower()
                is_avif = '.avif' in url_lower or url.endswith('.avif')
                is_webp = '.webp' in url_lower or url.endswith('.webp')
                
                # 如果是avif或webp格式，优先使用PIL处理
                if (is_avif or is_webp) and PIL_AVAILABLE:
                    try:
                        img = Image.open(io.BytesIO(img_data))
                        img.thumbnail((90, 70), Image.Resampling.LANCZOS)
                        # 转换为RGB模式（wx.Image需要RGB）
                        if img.mode != 'RGB':
                            rgb_img = img.convert('RGB')
                        else:
                            rgb_img = img
                        width, height = rgb_img.size
                        wx_img = wx.Image(width, height)
                        wx_img.SetData(rgb_img.tobytes())
                        bitmap = wx_img.ConvertToBitmap()
                        wx.CallAfter(self.update_thumbnail, thumbnail_bitmap, placeholder_label, bitmap)
                        return
                    except Exception as pil_error:
                        print(f"PIL处理{('avif' if is_avif else 'webp')}格式失败: {pil_error}，尝试使用wx.Image")
                
                # 尝试使用wx.Image加载（对于其他格式或PIL失败的情况）
                try:
                    wx_img = wx.Image(io.BytesIO(img_data))
                    if wx_img.IsOk():
                        wx_img = wx_img.Scale(90, 70, wx.IMAGE_QUALITY_HIGH)
                        bitmap = wx_img.ConvertToBitmap()
                        wx.CallAfter(self.update_thumbnail, thumbnail_bitmap, placeholder_label, bitmap)
                    else:
                        # 如果wx.Image也无法加载，尝试使用PIL（如果可用）
                        if PIL_AVAILABLE:
                            try:
                                img = Image.open(io.BytesIO(img_data))
                                img.thumbnail((90, 70), Image.Resampling.LANCZOS)
                                if img.mode != 'RGB':
                                    rgb_img = img.convert('RGB')
                                else:
                                    rgb_img = img
                                width, height = rgb_img.size
                                wx_img = wx.Image(width, height)
                                wx_img.SetData(rgb_img.tobytes())
                                bitmap = wx_img.ConvertToBitmap()
                                wx.CallAfter(self.update_thumbnail, thumbnail_bitmap, placeholder_label, bitmap)
                            except:
                                wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
                        else:
                            wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
                except Exception as wx_error:
                    # wx.Image加载失败，尝试使用PIL（如果可用）
                    if PIL_AVAILABLE:
                        try:
                            img = Image.open(io.BytesIO(img_data))
                            img.thumbnail((90, 70), Image.Resampling.LANCZOS)
                            if img.mode != 'RGB':
                                rgb_img = img.convert('RGB')
                            else:
                                rgb_img = img
                            width, height = rgb_img.size
                            wx_img = wx.Image(width, height)
                            wx_img.SetData(rgb_img.tobytes())
                            bitmap = wx_img.ConvertToBitmap()
                            wx.CallAfter(self.update_thumbnail, thumbnail_bitmap, placeholder_label, bitmap)
                        except Exception as pil_error2:
                            print(f"PIL处理图片失败: {pil_error2}")
                            wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
                    else:
                        print(f"wx.Image加载失败: {wx_error}")
                        wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
                
            else:
                # 视频：显示视频图标
                wx.CallAfter(self.update_video_thumbnail, thumbnail_bitmap, placeholder_label)
                
        except requests.exceptions.RequestException as e:
            print(f"加载缩略图网络错误: {e}")
            wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
        except Exception as e:
            print(f"加载缩略图失败: {e}")
            wx.CallAfter(self.update_error_thumbnail, thumbnail_bitmap, placeholder_label)
    
    def update_thumbnail(self, thumbnail_bitmap, placeholder_label, bitmap):
        """更新缩略图显示"""
        placeholder_label.Hide()
        thumbnail_bitmap.SetBitmap(bitmap)
        thumbnail_bitmap.Refresh()
    
    def update_video_thumbnail(self, thumbnail_bitmap, placeholder_label):
        """更新视频缩略图"""
        placeholder_label.SetLabel("🎬 视频")
        placeholder_label.Show()
        # 可以尝试加载视频第一帧，这里先显示图标
    
    def update_error_thumbnail(self, thumbnail_bitmap, placeholder_label):
        """更新错误缩略图"""
        placeholder_label.SetLabel("加载失败")
        placeholder_label.Show()
    
    def preview_resource(self, resource):
        """预览资源（显示大图或视频播放器）"""
        if resource['type'] == 'image':
            self.preview_image(resource)
        else:
            self.preview_video(resource)
    
    def preview_image(self, resource):
        """预览图片"""
        try:
            # 创建预览窗口
            preview_frame = wx.Frame(self, title=f"预览 - {resource['name']}", size=(800, 600))
            preview_frame.SetBackgroundColour(wx.Colour(240, 240, 240))
            
            panel = wx.Panel(preview_frame)
            panel.SetBackgroundColour(wx.Colour(240, 240, 240))
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            # 标题
            title_label = wx.StaticText(panel, label=resource['name'])
            title_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            sizer.Add(title_label, 0, wx.ALL, 10)
            
            # 图片显示区域（滚动）
            scroll_panel = scrolled.ScrolledPanel(panel)
            scroll_panel.SetupScrolling()
            scroll_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
            
            scroll_sizer = wx.BoxSizer(wx.VERTICAL)
            
            # 加载图片
            image_bitmap = wx.StaticBitmap(scroll_panel)
            loading_label = wx.StaticText(scroll_panel, label="正在加载图片...")
            loading_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                         wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            scroll_sizer.Add(loading_label, 0, wx.ALL | wx.ALIGN_CENTER, 20)
            scroll_sizer.Add(image_bitmap, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            scroll_panel.SetSizer(scroll_sizer)
            
            sizer.Add(scroll_panel, 1, wx.EXPAND | wx.ALL, 5)
            
            # 按钮
            btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            close_btn = wx.Button(panel, label="关闭", size=(100, 35))
            close_btn.Bind(wx.EVT_BUTTON, lambda e: preview_frame.Close())
            btn_sizer.Add(close_btn, 0, wx.ALL, 10)
            sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
            
            panel.SetSizer(sizer)
            preview_frame.Show()
            
            # 异步加载图片
            thread = threading.Thread(target=self.load_preview_image, args=(resource['url'], image_bitmap, loading_label))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            wx.MessageBox(f"预览失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def load_preview_image(self, url, image_bitmap, loading_label):
        """加载预览图片（支持avif和webp格式）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': urlparse(url).scheme + '://' + urlparse(url).netloc
            }
            
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            img_data = response.content
            
            # 检查是否是avif或webp格式
            url_lower = url.lower()
            is_avif = '.avif' in url_lower or url.endswith('.avif')
            is_webp = '.webp' in url_lower or url.endswith('.webp')
            
            # 优先使用PIL处理（特别是avif和webp格式）
            if PIL_AVAILABLE:
                try:
                    img = Image.open(io.BytesIO(img_data))
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    # 转换为RGB模式（wx.Image需要RGB）
                    if img.mode != 'RGB':
                        rgb_img = img.convert('RGB')
                    else:
                        rgb_img = img
                    width, height = rgb_img.size
                    wx_img = wx.Image(width, height)
                    wx_img.SetData(rgb_img.tobytes())
                    bitmap = wx_img.ConvertToBitmap()
                    wx.CallAfter(loading_label.Hide)
                    wx.CallAfter(image_bitmap.SetBitmap, bitmap)
                    wx.CallAfter(image_bitmap.GetParent().Layout)
                    return
                except Exception as pil_error:
                    print(f"PIL处理图片失败: {pil_error}，尝试使用wx.Image")
                    # 如果PIL失败，继续尝试wx.Image
            
            # 尝试使用wx.Image加载（对于其他格式或PIL不可用的情况）
            try:
                wx_img = wx.Image(io.BytesIO(img_data))
                if wx_img.IsOk():
                    # 调整大小以适应窗口
                    width, height = wx_img.GetWidth(), wx_img.GetHeight()
                    if width > 800 or height > 600:
                        scale = min(800 / width, 600 / height)
                        wx_img = wx_img.Scale(int(width * scale), int(height * scale), wx.IMAGE_QUALITY_HIGH)
                    bitmap = wx_img.ConvertToBitmap()
                    wx.CallAfter(loading_label.Hide)
                    wx.CallAfter(image_bitmap.SetBitmap, bitmap)
                    wx.CallAfter(image_bitmap.GetParent().Layout)
                else:
                    raise Exception("wx.Image无法加载图片")
            except Exception as wx_error:
                # 如果wx.Image也失败，且是avif/webp格式，提示用户
                if is_avif or is_webp:
                    error_msg = f"无法预览{'avif' if is_avif else 'webp'}格式图片。请安装Pillow库以支持此格式：pip install Pillow"
                    wx.CallAfter(loading_label.SetLabel, error_msg)
                else:
                    wx.CallAfter(loading_label.SetLabel, f"加载失败：{str(wx_error)}")
            
        except Exception as e:
            wx.CallAfter(loading_label.SetLabel, f"加载失败：{str(e)}")
    
    def preview_video(self, resource):
        """预览视频"""
        try:
            # 创建预览窗口
            preview_frame = wx.Frame(self, title=f"视频预览 - {resource['name']}", size=(800, 500))
            preview_frame.SetBackgroundColour(wx.Colour(240, 240, 240))
            
            panel = wx.Panel(preview_frame)
            panel.SetBackgroundColour(wx.Colour(240, 240, 240))
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            # 标题
            title_label = wx.StaticText(panel, label=resource['name'])
            title_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            title_label.Wrap(750)
            sizer.Add(title_label, 0, wx.ALL, 10)
            
            # 视频图标
            icon_label = wx.StaticText(panel, label="🎬")
            icon_label.SetFont(wx.Font(80, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                     wx.FONTWEIGHT_NORMAL, faceName="Segoe UI Emoji"))
            sizer.Add(icon_label, 0, wx.ALIGN_CENTER | wx.ALL, 20)
            
            # 提示信息
            info_label = wx.StaticText(panel, label="视频预览功能需要外部播放器\n\n您可以：\n1. 点击下方按钮在浏览器中打开\n2. 使用下载功能下载后播放")
            info_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                     wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            info_label.SetForegroundColour(wx.Colour(100, 100, 100))
            info_label.Wrap(700)
            sizer.Add(info_label, 0, wx.ALIGN_CENTER | wx.ALL, 20)
            
            # 视频URL显示
            url_text = wx.TextCtrl(panel, value=resource['url'], style=wx.TE_READONLY | wx.TE_MULTILINE)
            url_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="Consolas"))
            url_text.SetBackgroundColour(wx.Colour(250, 250, 250))
            url_text.SetMinSize((-1, 80))
            sizer.Add(url_text, 0, wx.EXPAND | wx.ALL, 10)
            
            # 按钮区域
            btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
            
            # 在浏览器中打开按钮
            open_btn = wx.Button(panel, label="在浏览器中打开", size=(150, 40))
            open_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            open_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
            open_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            open_btn.Bind(wx.EVT_BUTTON, lambda e, u=resource['url']: self.open_url_in_browser(u))
            open_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=open_btn: b.SetBackgroundColour(wx.Colour(85, 170, 255)))
            open_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=open_btn: b.SetBackgroundColour(wx.Colour(64, 158, 255)))
            btn_sizer.Add(open_btn, 0, wx.ALL, 5)
            
            # 下载按钮
            download_btn = wx.Button(panel, label="下载视频", size=(150, 40))
            download_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                        wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            download_btn.SetBackgroundColour(wx.Colour(103, 194, 58))
            download_btn.SetForegroundColour(wx.Colour(255, 255, 255))
            download_btn.Bind(wx.EVT_BUTTON, lambda e, r=resource: self.download_resource(r))
            download_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=download_btn: b.SetBackgroundColour(wx.Colour(133, 224, 88)))
            download_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=download_btn: b.SetBackgroundColour(wx.Colour(103, 194, 58)))
            btn_sizer.Add(download_btn, 0, wx.ALL, 5)
            
            # 关闭按钮
            close_btn = wx.Button(panel, label="关闭", size=(100, 40))
            close_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                     wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            close_btn.Bind(wx.EVT_BUTTON, lambda e: preview_frame.Close())
            btn_sizer.Add(close_btn, 0, wx.ALL, 5)
            
            sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
            
            panel.SetSizer(sizer)
            preview_frame.Show()
            
        except Exception as e:
            wx.MessageBox(f"预览失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def open_url_in_browser(self, url):
        """在系统默认浏览器中打开URL"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            wx.MessageBox(f"无法打开浏览器：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def download_resource(self, resource):
        """下载资源"""
        try:
            # 【关键】处理base64图片
            if resource['url'].startswith('data:image/'):
                if 'base64_data' in resource:
                    # 使用保存的base64数据
                    image_data = resource['base64_data']
                    mime_type = resource.get('mime_type', 'image/png')
                    
                    # 从MIME类型提取扩展名
                    mime_to_ext = {
                        'image/png': '.png',
                        'image/jpeg': '.jpg',
                        'image/jpg': '.jpg',
                        'image/gif': '.gif',
                        'image/webp': '.webp',
                        'image/bmp': '.bmp',
                        'image/svg+xml': '.svg',
                        'image/avif': '.avif'
                    }
                    ext = mime_to_ext.get(mime_type, '.png')
                    
                    # 选择保存位置
                    with wx.FileDialog(self, "保存base64图片", wildcard=f"图片文件 (*{ext})|*{ext}",
                                     style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                        if fileDialog.ShowModal() == wx.ID_CANCEL:
                            return
                        filepath = fileDialog.GetPath()
                        
                        # 确保文件扩展名正确
                        if not filepath.endswith(ext):
                            filepath += ext
                        
                        # 保存文件
                        with open(filepath, 'wb') as f:
                            f.write(image_data)
                        
                        wx.MessageBox(f"base64图片已保存到：{filepath}", "下载完成", wx.OK | wx.ICON_INFORMATION)
                        return
                else:
                    wx.MessageBox("base64图片数据丢失", "错误", wx.OK | wx.ICON_ERROR)
                    return
            
            # 【关键】优先使用资源中保存的MIME类型来设置扩展名
            mime_type = resource.get('mime_type', '').lower()
            ext = ''
            
            if mime_type:
                if mime_type == 'image/avif':
                    ext = '.avif'
                elif mime_type == 'image/webp':
                    ext = '.webp'
                elif mime_type.startswith('image/'):
                    # 从MIME类型提取扩展名
                    mime_to_ext = {
                        'image/jpeg': '.jpg',
                        'image/jpg': '.jpg',
                        'image/png': '.png',
                        'image/gif': '.gif',
                        'image/bmp': '.bmp',
                        'image/svg+xml': '.svg',
                        'image/x-icon': '.ico',
                        'image/ico': '.ico'
                    }
                    ext = mime_to_ext.get(mime_type, '')
            
            # 如果MIME类型无法提供扩展名，从URL提取
            if not ext:
                url_path = urlparse(resource['url']).path
                ext = os.path.splitext(url_path)[1].lower()
            
            # 如果仍然没有扩展名，根据资源类型设置默认扩展名
            if not ext:
                if resource['type'] == 'image':
                    ext = '.jpg'
                else:
                    ext = '.mp4'
            
            # 确保扩展名包含在文件名中（检查URL中是否包含格式标识）
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.ico', '.svg', '.avif'] and resource['type'] == 'image':
                # 如果扩展名不在常见图片格式中，检查URL中是否包含格式标识
                url_lower = resource['url'].lower()
                if '.avif' in url_lower:
                    ext = '.avif'
                elif '.webp' in url_lower:
                    ext = '.webp'
                elif '.png' in url_lower:
                    ext = '.png'
                elif '.gif' in url_lower:
                    ext = '.gif'
                else:
                    ext = '.jpg'  # 默认使用jpg
            
            # 生成默认文件名
            filename = resource['name']
            # 清理文件名中的非法字符
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            # 确保文件名包含正确的扩展名
            if ext and not filename.lower().endswith(ext.lower()):
                # 移除旧的扩展名（如果有）
                name_without_ext = os.path.splitext(filename)[0]
                filename = name_without_ext + ext
            
            # 选择保存位置（包含avif格式）
            wildcard = "图片文件 (*.jpg;*.png;*.gif;*.webp;*.avif)|*.jpg;*.png;*.gif;*.webp;*.avif|视频文件 (*.mp4;*.webm;*.avi)|*.mp4;*.webm;*.avi|所有文件 (*.*)|*.*"
            if resource['type'] == 'image':
                wildcard = "图片文件 (*.jpg;*.png;*.gif;*.webp;*.avif)|*.jpg;*.png;*.gif;*.webp;*.avif|所有文件 (*.*)|*.*"
            else:
                wildcard = "视频文件 (*.mp4;*.webm;*.avi)|*.mp4;*.webm;*.avi|所有文件 (*.*)|*.*"
            
            with wx.FileDialog(self, "保存文件", defaultFile=filename, wildcard=wildcard,
                             style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                
                save_path = fileDialog.GetPath()
                
                # 在新线程中下载
                self.status_text.SetLabel(f"正在下载：{resource['name']}...")
                self.status_text.SetForegroundColour(wx.Colour(64, 158, 255))
                
                thread = threading.Thread(target=self.download_file, args=(resource['url'], save_path, resource['name']))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            wx.MessageBox(f"下载失败：{str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    def download_file(self, url, save_path, name):
        """下载文件（在线程中执行）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # 更新进度（可选）
                            if total_size > 0:
                                progress = downloaded / total_size * 100
                                wx.CallAfter(self.status_text.SetLabel, 
                                            f"正在下载：{name}... {progress:.1f}%")
            
            wx.CallAfter(self.status_text.SetLabel, f"下载完成：{name}")
            wx.CallAfter(self.status_text.SetForegroundColour, wx.Colour(103, 194, 58))
            wx.MessageBox(f"文件已保存到：\n{save_path}", "下载完成", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.CallAfter(self.show_error, f"下载失败：{str(e)}")
    
    def on_checkbox_changed(self):
        """复选框状态改变时调用，更新批量下载按钮状态"""
        if hasattr(self, 'batch_download_btn'):
            # 检查是否有选中的资源
            has_selected = any(checkbox.GetValue() for checkbox in self.checkboxes.values())
            self.batch_download_btn.Enable(has_selected)
    
    def on_batch_download(self, event):
        """批量下载选中的资源"""
        # 获取选中的资源
        selected_resources = []
        for idx, checkbox in self.checkboxes.items():
            if checkbox.GetValue() and idx < len(self.resources):
                selected_resources.append((idx, self.resources[idx]))
        
        if not selected_resources:
            wx.MessageBox("请先选择要下载的资源！", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        
        # 选择保存文件夹
        with wx.DirDialog(self, "选择保存文件夹", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            save_dir = dirDialog.GetPath()
            
            # 确认下载
            resource_count = len(selected_resources)
            msg = f"将下载 {resource_count} 个选中的资源到：\n{save_dir}\n\n是否继续？"
            dlg = wx.MessageDialog(self, msg, "确认批量下载", wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() != wx.ID_YES:
                dlg.Destroy()
                return
            dlg.Destroy()
            
            # 在新线程中批量下载
            self.status_text.SetLabel(f"准备批量下载 {resource_count} 个资源...")
            self.status_text.SetForegroundColour(wx.Colour(64, 158, 255))
            self.batch_download_btn.Enable(False)  # 禁用按钮，防止重复点击
            
            thread = threading.Thread(target=self.batch_download_files, args=(save_dir, selected_resources))
            thread.daemon = True
            thread.start()
    
    def batch_download_files(self, save_dir, selected_resources):
        """批量下载文件（在线程中执行）"""
        try:
            total_count = len(selected_resources)
            success_count = 0
            fail_count = 0
            failed_resources = []
            
            wx.CallAfter(self.status_text.SetLabel, f"开始批量下载，共 {total_count} 个资源...")
            
            for download_idx, (resource_idx, resource) in enumerate(selected_resources, 1):
                try:
                    # 更新状态
                    wx.CallAfter(self.status_text.SetLabel, 
                                f"正在下载 ({download_idx}/{total_count}): {resource['name']}...")
                    
                    # 生成文件名
                    filename = resource['name']
                    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                    
                    # 处理base64图片
                    if resource['url'].startswith('data:image/'):
                        if 'base64_data' in resource:
                            image_data = resource['base64_data']
                            mime_type = resource.get('mime_type', 'image/png')
                            
                            # 从MIME类型提取扩展名
                            mime_to_ext = {
                                'image/png': '.png',
                                'image/jpeg': '.jpg',
                                'image/jpg': '.jpg',
                                'image/gif': '.gif',
                                'image/webp': '.webp',
                                'image/bmp': '.bmp',
                                'image/svg+xml': '.svg',
                                'image/avif': '.avif'
                            }
                            ext = mime_to_ext.get(mime_type, '.png')
                            
                            # 确保文件名有扩展名
                            if not filename.lower().endswith(ext):
                                name_without_ext = os.path.splitext(filename)[0]
                                filename = name_without_ext + ext
                            
                            filepath = os.path.join(save_dir, filename)
                            
                            # 如果文件已存在，添加序号
                            if os.path.exists(filepath):
                                base_name, ext = os.path.splitext(filename)
                                counter = 1
                                while os.path.exists(filepath):
                                    filename = f"{base_name}_{counter}{ext}"
                                    filepath = os.path.join(save_dir, filename)
                                    counter += 1
                            
                            # 保存文件
                            with open(filepath, 'wb') as f:
                                f.write(image_data)
                            
                            success_count += 1
                        else:
                            fail_count += 1
                            failed_resources.append((resource['name'], "base64数据丢失"))
                    else:
                        # 下载网络资源
                        # 确定文件扩展名
                        mime_type = resource.get('mime_type', '').lower()
                        ext = ''
                        
                        if mime_type:
                            if mime_type == 'image/avif':
                                ext = '.avif'
                            elif mime_type == 'image/webp':
                                ext = '.webp'
                            elif mime_type.startswith('image/'):
                                mime_to_ext = {
                                    'image/jpeg': '.jpg',
                                    'image/jpg': '.jpg',
                                    'image/png': '.png',
                                    'image/gif': '.gif',
                                    'image/bmp': '.bmp',
                                    'image/svg+xml': '.svg',
                                    'image/x-icon': '.ico',
                                    'image/ico': '.ico'
                                }
                                ext = mime_to_ext.get(mime_type, '')
                        
                        # 如果MIME类型无法提供扩展名，从URL提取
                        if not ext:
                            url_path = urlparse(resource['url']).path
                            ext = os.path.splitext(url_path)[1].lower()
                        
                        # 如果仍然没有扩展名，根据资源类型设置默认扩展名
                        if not ext:
                            if resource['type'] == 'image':
                                ext = '.jpg'
                            else:
                                ext = '.mp4'
                        
                        # 确保文件名有扩展名
                        if not filename.lower().endswith(ext.lower()):
                            name_without_ext = os.path.splitext(filename)[0]
                            filename = name_without_ext + ext
                        
                        filepath = os.path.join(save_dir, filename)
                        
                        # 如果文件已存在，添加序号
                        if os.path.exists(filepath):
                            base_name, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(filepath):
                                filename = f"{base_name}_{counter}{ext}"
                                filepath = os.path.join(save_dir, filename)
                                counter += 1
                        
                        # 下载文件
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        
                        response = requests.get(resource['url'], headers=headers, stream=True, timeout=30)
                        response.raise_for_status()
                        
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        success_count += 1
                
                except Exception as e:
                    # 下载失败不影响其他资源的下载
                    fail_count += 1
                    failed_resources.append((resource['name'], str(e)))
                    print(f"下载失败: {resource['name']}, 错误: {e}")
                    # 继续下载下一个资源，不中断
                    continue
            
            # 显示下载结果
            result_msg = f"批量下载完成！\n\n"
            result_msg += f"成功: {success_count} 个\n"
            result_msg += f"失败: {fail_count} 个\n"
            result_msg += f"保存位置: {save_dir}"
            
            if failed_resources:
                result_msg += f"\n\n失败的资源:\n"
                for name, error in failed_resources[:10]:  # 只显示前10个
                    result_msg += f"  - {name}: {error[:50]}\n"
                if len(failed_resources) > 10:
                    result_msg += f"  ... 还有 {len(failed_resources) - 10} 个失败\n"
            
            wx.CallAfter(self.status_text.SetLabel, f"批量下载完成：成功 {success_count} 个，失败 {fail_count} 个")
            if success_count > 0:
                wx.CallAfter(self.status_text.SetForegroundColour, wx.Colour(103, 194, 58))
            else:
                wx.CallAfter(self.status_text.SetForegroundColour, wx.Colour(245, 108, 108))
            
            wx.CallAfter(self.batch_download_btn.Enable, True)  # 重新启用按钮
            wx.MessageBox(result_msg, "批量下载完成", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.CallAfter(self.status_text.SetLabel, f"批量下载出错：{str(e)}")
            wx.CallAfter(self.status_text.SetForegroundColour, wx.Colour(245, 108, 108))
            wx.CallAfter(self.batch_download_btn.Enable, True)  # 重新启用按钮
            wx.CallAfter(self.show_error, f"批量下载失败：{str(e)}")
    
    def save_cookies(self, driver):
        """保存Cookie到文件"""
        try:
            cookies = driver.get_cookies()
            import json
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"Cookie已保存到: {self.cookie_file}")
        except Exception as e:
            print(f"保存Cookie失败: {e}")
            raise
    
    def load_cookies(self, driver):
        """从文件加载Cookie"""
        try:
            import json
            if not os.path.exists(self.cookie_file):
                return  # 文件不存在，跳过
            
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 先访问目标网站的主页，确保域名正确
            if cookies:
                # 从Cookie中获取域名
                first_cookie = cookies[0]
                domain = first_cookie.get('domain', '')
                
                # 访问主页以设置Cookie
                if 'taobao.com' in domain or 'tmall.com' in domain:
                    driver.get('https://www.taobao.com')
                    time.sleep(1)
                
                # 添加所有Cookie
                for cookie in cookies:
                    try:
                        # 移除可能导致问题的字段
                        cookie_dict = {
                            'name': cookie.get('name'),
                            'value': cookie.get('value'),
                            'domain': cookie.get('domain'),
                            'path': cookie.get('path', '/'),
                        }
                        # 只添加有效的字段
                        if cookie.get('expiry'):
                            cookie_dict['expiry'] = cookie.get('expiry')
                        if cookie.get('secure'):
                            cookie_dict['secure'] = cookie.get('secure')
                        if cookie.get('httpOnly'):
                            cookie_dict['httpOnly'] = cookie.get('httpOnly')
                        
                        driver.add_cookie(cookie_dict)
                    except Exception as e:
                        print(f"添加Cookie失败: {cookie.get('name', 'unknown')}, 错误: {e}")
                        continue
                
                print(f"已加载 {len(cookies)} 个Cookie")
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            raise


def main():
    """主函数"""
    app = wx.App()
    frame = ResourceDownloader()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()

