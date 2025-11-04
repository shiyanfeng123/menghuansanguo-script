"""
电商利润计算器 - wxPython GUI版本
"""

import wx
import wx.lib.scrolledpanel as scrolled
import re


class EcommerceProfitCalculator(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="电商利润计算器 - 智能版",
            size=(1200, 900),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # 设置主窗口背景色（渐变效果模拟）
        self.SetBackgroundColour(wx.Colour(240, 245, 255))
        
        # 创建主面板（带边框效果）
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # 创建主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域（精美设计）
        title_panel = wx.Panel(panel)
        # 使用渐变蓝色背景
        title_panel.SetBackgroundColour(wx.Colour(64, 158, 255))
        title_panel.SetMinSize((-1, 90))
        
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 主标题
        title = wx.StaticText(title_panel, label="💰 电商利润计算器")
        title_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        # 副标题
        subtitle = wx.StaticText(title_panel, label="✨ 智能识别 · 实时计算 · 盈利分析")
        subtitle_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(wx.Colour(240, 248, 255))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        title_sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        title_panel.SetSizer(title_sizer)
        main_sizer.Add(title_panel, 0, wx.EXPAND | wx.ALL, 0)
        
        # 智能识别输入区域（新增）
        smart_input_panel = self.create_smart_input_panel(panel)
        main_sizer.Add(smart_input_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # 创建左右分栏
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域（美化）
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((380, -1))
        input_panel = self.create_input_panel(left_panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(input_panel, 1, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域（美化）
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        result_panel = self.create_result_panel(right_panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(result_panel, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        # 添加左右面板到主布局
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 初始化计算
        self.calculate()
        
    def create_smart_input_panel(self, parent):
        """创建智能识别输入面板（精美设计）"""
        # 外层容器（带阴影效果模拟）
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        container.SetMinSize((-1, 140))
        
        # 内层面板（卡片效果）
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域（带图标）
        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        title = wx.StaticText(title_panel, label="🤖 智能识别输入")
        title_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(64, 158, 255))
        
        subtitle = wx.StaticText(title_panel, label="支持自然语言描述")
        subtitle_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(wx.Colour(144, 147, 153))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        title_sizer.AddStretchSpacer()
        title_sizer.Add(subtitle, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        title_panel.SetSizer(title_sizer)
        title_panel.SetMinSize((-1, 30))
        
        sizer.Add(title_panel, 0, wx.EXPAND | wx.TOP, 8)
        
        # 提示文本（更精美）
        hint_panel = wx.Panel(panel)
        hint_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        hint = wx.StaticText(hint_panel, label="💡 示例：售价69/六十九 成本40  ROI 4.65/四点六五  退货率30%/百分之三十  平台扣点千六/千分之六/6‰  运费险1.04  退货运费5  其他成本20  100单")
        hint_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        hint.SetFont(hint_font)
        hint.SetForegroundColour(wx.Colour(102, 126, 234))
        hint_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hint_sizer.Add(hint, 0, wx.LEFT, 10)
        hint_panel.SetSizer(hint_sizer)
        hint_panel.SetMinSize((-1, 25))
        
        sizer.Add(hint_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.AddSpacer(5)
        
        # 输入框区域
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 输入框（美化）
        self.smart_input = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            size=(-1, 70)
        )
        input_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.smart_input.SetFont(input_font)
        self.smart_input.SetBackgroundColour(wx.Colour(250, 252, 255))
        self.smart_input.SetHint("💬 在此输入自然语言描述，系统将自动识别并填充数据...")
        
        # 识别按钮（精美设计）
        parse_btn = wx.Button(panel, label="✨ 智能识别", size=(110, 70))
        parse_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        parse_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        parse_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        parse_btn.SetFont(parse_font)
        # 设置按钮悬停效果
        parse_btn.Bind(wx.EVT_BUTTON, self.on_parse_clicked)
        parse_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: parse_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        parse_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: parse_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        
        input_sizer.Add(self.smart_input, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        input_sizer.Add(parse_btn, 0, wx.RIGHT | wx.BOTTOM | wx.ALIGN_BOTTOM, 10)
        
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        panel.SetSizer(sizer)
        container_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 8)
        container.SetSizer(container_sizer)
        
        return container
    
    def chinese_to_number(self, chinese_str):
        """将中文数字转换为阿拉伯数字"""
        if not chinese_str:
            return None
        
        # 如果已经是数字，直接返回
        try:
            return float(chinese_str)
        except:
            pass
        
        # 中文数字映射
        chinese_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5,
            '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10
        }
        
        # 处理小数（有"点"的情况，如"四点六五" -> 4.65）
        if '点' in chinese_str or '.' in chinese_str:
            parts = re.split(r'[点.]', chinese_str)
            if len(parts) == 2:
                integer_part = self._chinese_to_integer(parts[0], chinese_map)
                # 小数部分需要逐位转换（如"六五" -> 65，表示0.65）
                decimal_str = parts[1]
                decimal_value = 0
                decimal_multiplier = 0.1
                for char in decimal_str:
                    if char in chinese_map:
                        digit_value = chinese_map[char]
                        decimal_value += digit_value * decimal_multiplier
                        decimal_multiplier *= 0.1
                    elif char.isdigit():
                        # 如果遇到阿拉伯数字，也处理
                        decimal_value += int(char) * decimal_multiplier
                        decimal_multiplier *= 0.1
                
                if integer_part is not None:
                    return float(integer_part) + decimal_value
        
        # 处理"X点XX"格式的小数（没有"点"但表示小数，如"四点六五"）
        # 匹配模式：一个或多个数字 + "点" + 一个或多个数字
        # 如果没有"点"，尝试识别"X点XX"格式（如"四点六五"）
        if '点' not in chinese_str and '.' not in chinese_str:
            # 尝试匹配"X点XX"格式（如"四点六五"）
            # 查找"点"字的前后是否都是中文数字
            point_match = re.search(r'([零一二三四五六七八九十百]+)点([零一二三四五六七八九十]+)', chinese_str)
            if point_match:
                integer_part = self._chinese_to_integer(point_match.group(1), chinese_map)
                decimal_part = self._chinese_to_integer(point_match.group(2), chinese_map)
                if integer_part is not None and decimal_part is not None:
                    return float(f"{integer_part}.{decimal_part}")
            
            # 如果没有显式的"点"，尝试识别连续的中文数字序列（可能是"X点XX"格式）
            # 例如："四点六五" -> 4.65
            # 匹配模式：一个数字 + "点" + 两个数字（但"点"被省略了）
            # 尝试识别：第一个数字是整数部分，后面的数字是小数部分
            chinese_digits = [ch for ch in chinese_str if ch in chinese_map]
            if len(chinese_digits) >= 3:
                # 尝试多种分割方式
                # 方式1：第一个是整数，后面是小数（如"四点六五" -> 4.65）
                first_digit = chinese_map.get(chinese_digits[0], None)
                if first_digit is not None and first_digit < 10:
                    # 提取后面的数字
                    rest_str = ''.join(ch for ch in chinese_str if ch in chinese_map)
                    if len(rest_str) > 1:
                        # 第一个数字是整数部分
                        integer_part = chinese_map.get(rest_str[0], None)
                        # 后面的数字组成小数部分
                        decimal_str = rest_str[1:]
                        decimal_part = 0
                        decimal_multiplier = 0.1
                        for digit_char in decimal_str:
                            if digit_char in chinese_map:
                                digit_value = chinese_map[digit_char]
                                decimal_part += digit_value * decimal_multiplier
                                decimal_multiplier *= 0.1
                        if integer_part is not None:
                            return float(integer_part) + decimal_part
        
        # 处理整数
        result = self._chinese_to_integer(chinese_str, chinese_map)
        return float(result) if result is not None else None
    
    def _chinese_to_integer(self, chinese_str, chinese_map):
        """将中文整数转换为阿拉伯数字"""
        if not chinese_str:
            return None
        
        # 如果是纯数字，直接返回
        if chinese_str.isdigit():
            return int(chinese_str)
        
        # 处理"十"的特殊情况（十、十一、十二等）
        if chinese_str == '十':
            return 10
        if chinese_str.startswith('十') and len(chinese_str) > 1:
            # 十一、十二...十九
            rest = chinese_str[1:]
            if rest in chinese_map:
                return 10 + chinese_map[rest]
        
        # 处理十位数（二十、三十...九十九）
        if len(chinese_str) >= 2 and chinese_str[-1] == '十':
            # 二十、三十...九十
            if chinese_str[0] in chinese_map:
                return chinese_map[chinese_str[0]] * 10
        elif len(chinese_str) >= 3 and '十' in chinese_str:
            # 二十一、二十二...九十九
            parts = chinese_str.split('十')
            if len(parts) == 2:
                tens = self._chinese_to_integer(parts[0], chinese_map) if parts[0] else 1
                ones = self._chinese_to_integer(parts[1], chinese_map) if parts[1] else 0
                if tens is not None and ones is not None:
                    return tens * 10 + ones
        
        # 处理百位数（一百、二百...九百九十九）
        if '百' in chinese_str:
            parts = chinese_str.split('百')
            if len(parts) == 2:
                hundreds = self._chinese_to_integer(parts[0], chinese_map) if parts[0] else 1
                rest = self._chinese_to_integer(parts[1], chinese_map) if parts[1] else 0
                if hundreds is not None and rest is not None:
                    return hundreds * 100 + rest
        
        # 处理单个数字
        if chinese_str in chinese_map:
            return chinese_map[chinese_str]
        
        return None
    
    def parse_number_from_text(self, text, patterns):
        """从文本中提取数字（支持中文和阿拉伯数字）"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # 先尝试直接转换
                    value_str = match.group(1)
                    value = self.chinese_to_number(value_str)
                    if value is not None:
                        return value
                except:
                    pass
        return None
    
    def parse_smart_input(self, text):
        """解析智能输入文本"""
        if not text:
            return
        
        text = text.strip()
        
        # 售价（支持中文数字）
        price_patterns = [
            r'售价\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'价格\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'单价\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, price_patterns)
        if value is not None:
            try:
                self.price_ctrl.SetValue(value)
            except:
                pass
        
        # 成本（支持中文数字）
        cost_patterns = [
            r'成本\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, cost_patterns)
        if value is not None:
            try:
                self.cost_ctrl.SetValue(value)
            except:
                pass
        
        # ROI（支持中文数字）
        roi_patterns = [
            r'ROI\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'roi\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'投入产出比\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, roi_patterns)
        if value is not None:
            try:
                self.roi_ctrl.SetValue(value)
            except:
                pass
        
        # 退货率（支持中文数字和"百分之"格式）
        return_rate_parsed = False
        
        # 1. 先匹配"百分之X"格式（如：百分之三十、百分之30）
        percent_patterns = [
            r'退货率\s*[:：算]?\s*百分之([零一二三四五六七八九十百\d\.点]+)',
            r'退货\s*率\s*[:：算]?\s*百分之([零一二三四五六七八九十百\d\.点]+)',
            r'退货率\s*[:：算]?\s*百分之\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        for pattern in percent_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1)
                    value = self.chinese_to_number(value_str)
                    if value is not None:
                        self.return_rate_ctrl.SetValue(value)
                        return_rate_parsed = True
                        break
                except:
                    pass
        
        # 2. 如果没有匹配到"百分之X"，尝试匹配普通格式
        if not return_rate_parsed:
            return_rate_patterns = [
                r'退货率\s*[:：算]?\s*([零一二三四五六七八九十百\d\.点]+)\s*%?',
                r'退货\s*率\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)\s*%?',
            ]
            value = self.parse_number_from_text(text, return_rate_patterns)
            if value is not None:
                try:
                    self.return_rate_ctrl.SetValue(value)
                    return_rate_parsed = True
                except:
                    pass
        
        # 平台扣点（支持多种格式：千六、千5、千分之六、千分之6、6‰、0.6‰等）
        platform_fee_parsed = False
        
        # 1. 先匹配"千分之X"格式（如：千分之六、千分之6）
        qianfen_pattern = re.search(r'平台扣点\s*[:：]?\s*千分之[零一二三四五六七八九十\d]+', text, re.IGNORECASE)
        if qianfen_pattern:
            qianfen_match = re.search(r'千分之([零一二三四五六七八九十\d]+)', qianfen_pattern.group(0), re.IGNORECASE)
            if qianfen_match:
                qianfen_str = qianfen_match.group(1)
                qian_map = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                           '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                if qianfen_str.isdigit():
                    value = float(qianfen_str) / 10.0
                elif qianfen_str in qian_map:
                    value = float(qian_map[qianfen_str]) / 10.0
                else:
                    value = 0.0
                try:
                    self.platform_fee_ctrl.SetValue(value)
                    platform_fee_parsed = True
                except:
                    pass
        
        # 2. 如果没有匹配到"千分之X"，尝试匹配"千X"格式（如：千六、千5）
        if not platform_fee_parsed:
            qian_pattern = re.search(r'平台扣点\s*[:：]?\s*千[零一二三四五六七八九十\d]+', text, re.IGNORECASE)
            if qian_pattern:
                qian_match = re.search(r'千([零一二三四五六七八九十\d]+)', qian_pattern.group(0), re.IGNORECASE)
                if qian_match:
                    qian_str = qian_match.group(1)
                    qian_map = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
                               '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                    if qian_str.isdigit():
                        value = float(qian_str) / 10.0
                    elif qian_str in qian_map:
                        value = float(qian_map[qian_str]) / 10.0
                    else:
                        value = 0.0
                    try:
                        self.platform_fee_ctrl.SetValue(value)
                        platform_fee_parsed = True
                    except:
                        pass
        
        # 3. 如果还没有匹配到，尝试匹配千分号格式（如：6‰、0.6‰）
        if not platform_fee_parsed:
            # 匹配全角千分号 ‰ 或半角千分号 ‰
            permille_pattern = re.search(r'平台扣点\s*[:：]?\s*(\d+\.?\d*)\s*[‰‰]', text, re.IGNORECASE)
            if permille_pattern:
                try:
                    value = float(permille_pattern.group(1)) / 10.0  # 千分号转百分比（6‰ = 0.6%）
                    self.platform_fee_ctrl.SetValue(value)
                    platform_fee_parsed = True
                except:
                    pass
            # 如果没有匹配到，尝试匹配单独的千分号（不包含"平台扣点"关键字）
            if not platform_fee_parsed:
                permille_pattern = re.search(r'(\d+\.?\d*)\s*[‰‰]', text, re.IGNORECASE)
                if permille_pattern:
                    # 检查是否在"扣点"附近
                    pos = permille_pattern.start()
                    context = text[max(0, pos-20):pos+20]
                    if '扣点' in context or '平台' in context:
                        try:
                            value = float(permille_pattern.group(1)) / 10.0
                            self.platform_fee_ctrl.SetValue(value)
                            platform_fee_parsed = True
                        except:
                            pass
        
        # 4. 如果还没有匹配到，尝试匹配百分比格式（如：0.6%、6%）
        if not platform_fee_parsed:
            platform_fee_patterns = [
                r'平台扣点\s*[:：]?\s*(\d+\.?\d*)\s*%',
                r'扣点\s*[:：]?\s*(\d+\.?\d*)\s*%',
                r'平台扣点\s*[:：]?\s*(\d+\.?\d*)',
                r'扣点\s*[:：]?\s*(\d+\.?\d*)',
            ]
            for pattern in platform_fee_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        self.platform_fee_ctrl.SetValue(value)
                        platform_fee_parsed = True
                    except:
                        pass
                    break
        
        # 运费险（支持中文数字）
        shipping_insurance_patterns = [
            r'运费险\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'运费险\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, shipping_insurance_patterns)
        if value is not None:
            try:
                self.shipping_insurance_ctrl.SetValue(value)
            except:
                pass
        
        # 退货运费（支持中文数字）
        return_shipping_patterns = [
            r'退货运费\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'退货.*运费\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'退货.*扣\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)\s*元',
            r'退货.*运费\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, return_shipping_patterns)
        if value is not None:
            try:
                self.return_shipping_ctrl.SetValue(value)
            except:
                pass
        
        # 其他成本（支持中文数字）
        other_cost_patterns = [
            r'其他成本\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.parse_number_from_text(text, other_cost_patterns)
        if value is not None:
            try:
                self.other_cost_ctrl.SetValue(value)
            except:
                pass
        
        # 订单数（支持中文数字）
        orders_patterns = [
            r'([零一二三四五六七八九十百\d]+)\s*单',
            r'订单数\s*[:：]?\s*([零一二三四五六七八九十百\d]+)',
            r'订单\s*[:：]?\s*([零一二三四五六七八九十百\d]+)',
        ]
        value = self.parse_number_from_text(text, orders_patterns)
        if value is not None:
            try:
                self.orders_ctrl.SetValue(int(value))
            except:
                pass
    
    def on_parse_clicked(self, event):
        """智能识别按钮点击事件"""
        text = self.smart_input.GetValue()
        if text:
            self.parse_smart_input(text)
            self.calculate()
        # 直接执行，不显示提示
    
    def create_input_panel(self, parent):
        """创建输入参数面板（精美设计）"""
        # 外层容器
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        # 内层面板（卡片效果）
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域（精美设计）
        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(wx.Colour(64, 158, 255))
        title_panel.SetMinSize((-1, 40))
        
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(title_panel, label="📊 基础参数设置")
        title_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        title_sizer.AddStretchSpacer()
        title_panel.SetSizer(title_sizer)
        
        sizer.Add(title_panel, 0, wx.EXPAND)
        sizer.AddSpacer(10)
        
        # 创建网格布局（美化）
        grid_sizer = wx.FlexGridSizer(rows=9, cols=2, vgap=12, hgap=20)
        grid_sizer.AddGrowableCol(1, 1)
        
        # 售价（美化）
        self.price_label = wx.StaticText(panel, label="💰 售价（元）:")
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.price_label.SetFont(label_font)
        self.price_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.price_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10000, 
                                           inc=1, size=(200, 28))
        self.price_ctrl.SetDigits(2)
        self.price_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.price_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.price_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.price_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.price_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 成本（美化）
        self.cost_label = wx.StaticText(panel, label="💵 成本（元）:")
        self.cost_label.SetFont(label_font)
        self.cost_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.cost_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10000,
                                          inc=1, size=(200, 28))
        self.cost_ctrl.SetDigits(2)
        self.cost_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.cost_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.cost_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.cost_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.cost_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # ROI（美化）
        self.roi_label = wx.StaticText(panel, label="📊 ROI（投入产出比）:")
        self.roi_label.SetFont(label_font)
        self.roi_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.roi_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0.1, max=100,
                                         inc=0.1, size=(200, 28))
        self.roi_ctrl.SetDigits(2)
        self.roi_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.roi_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.roi_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.roi_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.roi_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 退货率（美化）
        self.return_rate_label = wx.StaticText(panel, label="🔄 退货率（%）:")
        self.return_rate_label.SetFont(label_font)
        self.return_rate_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.return_rate_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                  inc=0.1, size=(200, 28))
        self.return_rate_ctrl.SetDigits(1)
        self.return_rate_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.return_rate_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.return_rate_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.return_rate_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.return_rate_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 平台扣点（美化）
        self.platform_fee_label = wx.StaticText(panel, label="💳 平台扣点（%）:")
        self.platform_fee_label.SetFont(label_font)
        self.platform_fee_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.platform_fee_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10,
                                                   inc=0.01, size=(200, 28))
        self.platform_fee_ctrl.SetDigits(2)
        self.platform_fee_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.platform_fee_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.platform_fee_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.platform_fee_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.platform_fee_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 运费险（美化）
        self.shipping_insurance_label = wx.StaticText(panel, label="📦 运费险（元/单）:")
        self.shipping_insurance_label.SetFont(label_font)
        self.shipping_insurance_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.shipping_insurance_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                         inc=0.01, size=(200, 28))
        self.shipping_insurance_ctrl.SetDigits(2)
        self.shipping_insurance_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.shipping_insurance_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.shipping_insurance_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.shipping_insurance_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.shipping_insurance_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 退货运费（美化）
        self.return_shipping_label = wx.StaticText(panel, label="↩️ 退货运费（元/单）:")
        self.return_shipping_label.SetFont(label_font)
        self.return_shipping_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.return_shipping_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                      inc=0.1, size=(200, 28))
        self.return_shipping_ctrl.SetDigits(2)
        self.return_shipping_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.return_shipping_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.return_shipping_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.return_shipping_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.return_shipping_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 其他成本（美化）
        self.other_cost_label = wx.StaticText(panel, label="📋 其他成本（元）:")
        self.other_cost_label.SetFont(label_font)
        self.other_cost_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.other_cost_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100000,
                                                 inc=1, size=(200, 28))
        self.other_cost_ctrl.SetDigits(2)
        self.other_cost_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.other_cost_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.other_cost_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.other_cost_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_value_changed)
        self.other_cost_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        # 订单数（美化）
        self.orders_label = wx.StaticText(panel, label="📦 订单数（单）:")
        self.orders_label.SetFont(label_font)
        self.orders_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.orders_ctrl = wx.SpinCtrl(panel, value="0", min=0, max=100000,
                                       size=(200, 28))
        self.orders_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.orders_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.orders_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.orders_ctrl.Bind(wx.EVT_SPINCTRL, self.on_value_changed)
        self.orders_ctrl.Bind(wx.EVT_TEXT, self.on_value_changed)
        
        sizer.Add(grid_sizer, 0, wx.ALL, 15)
        sizer.AddSpacer(10)
        
        # 清空按钮（精美设计）
        button_panel = wx.Panel(panel)
        button_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        button_panel.SetMinSize((-1, 55))
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        clear_btn = wx.Button(button_panel, label="🗑️ 清空所有", size=(150, 40))
        clear_btn.SetBackgroundColour(wx.Colour(245, 108, 108))
        clear_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        clear_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        clear_btn.SetFont(clear_font)
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_all)
        # 按钮悬停效果
        clear_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: clear_btn.SetBackgroundColour(wx.Colour(255, 128, 128)))
        clear_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: clear_btn.SetBackgroundColour(wx.Colour(245, 108, 108)))
        
        button_sizer.AddStretchSpacer()
        button_sizer.Add(clear_btn, 0, wx.ALL, 15)
        button_sizer.AddStretchSpacer()
        button_panel.SetSizer(button_sizer)
        
        sizer.Add(button_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(sizer)
        container_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 8)
        container.SetSizer(container_sizer)
        return container
    
    def create_result_panel(self, parent):
        """创建结果显示面板（精美设计）"""
        # 外层容器
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        # 内层面板（卡片效果）
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域（精美设计）
        title_panel = wx.Panel(panel)
        title_panel.SetBackgroundColour(wx.Colour(64, 158, 255))
        title_panel.SetMinSize((-1, 40))
        
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(title_panel, label="📈 利润分析结果")
        title_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        title_sizer.AddStretchSpacer()
        title_panel.SetSizer(title_sizer)
        
        sizer.Add(title_panel, 0, wx.EXPAND)
        sizer.AddSpacer(10)
        
        # 创建结果显示区域（使用TextCtrl，支持富文本）
        self.result_text = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            size=(-1, 400)
        )
        result_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.result_text.SetFont(result_font)
        self.result_text.SetBackgroundColour(wx.Colour(250, 252, 255))
        
        sizer.Add(self.result_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        sizer.AddSpacer(10)
        
        panel.SetSizer(sizer)
        container_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 8)
        container.SetSizer(container_sizer)
        
        return container
    
    def on_clear_all(self, event):
        """清空所有输入框"""
        # 直接清空，不显示确认对话框
        self.price_ctrl.SetValue(0)
        self.cost_ctrl.SetValue(0)
        self.roi_ctrl.SetValue(0)
        self.return_rate_ctrl.SetValue(0)
        self.platform_fee_ctrl.SetValue(0)
        self.shipping_insurance_ctrl.SetValue(0)
        self.return_shipping_ctrl.SetValue(0)
        self.other_cost_ctrl.SetValue(0)
        self.orders_ctrl.SetValue(0)
        
        # 清空智能识别输入框
        self.smart_input.Clear()
        
        # 重新计算（显示空结果）
        self.calculate()
    
    def on_value_changed(self, event):
        """当输入值变化时触发计算"""
        self.calculate()
    
    def calculate(self):
        """执行利润计算"""
        try:
            # 获取输入值
            price = self.price_ctrl.GetValue()
            cost = self.cost_ctrl.GetValue()
            roi = self.roi_ctrl.GetValue()
            return_rate = self.return_rate_ctrl.GetValue() / 100.0  # 转换为小数
            platform_fee_rate = self.platform_fee_ctrl.GetValue() / 100.0  # 转换为小数
            shipping_insurance = self.shipping_insurance_ctrl.GetValue()
            return_shipping_cost = self.return_shipping_ctrl.GetValue()
            other_cost = self.other_cost_ctrl.GetValue()  # 其他成本
            total_orders = self.orders_ctrl.GetValue()
            
            # 计算订单数
            successful_orders = int(total_orders * (1 - return_rate))
            returned_orders = total_orders - successful_orders
            
            # 计算收入
            revenue = successful_orders * price
            
            # 计算成本
            ad_cost = revenue / roi if roi > 0 else 0
            product_cost = total_orders * cost
            platform_fee = successful_orders * price * platform_fee_rate
            shipping_insurance_cost = total_orders * shipping_insurance
            return_shipping_cost_total = returned_orders * return_shipping_cost
            
            # 总成本（包含其他成本）
            total_cost = ad_cost + product_cost + platform_fee + shipping_insurance_cost + return_shipping_cost_total + other_cost
            
            # 利润
            profit = revenue - total_cost
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            # 盈亏平衡售价（包含其他成本）
            if successful_orders > 0 and roi > 0:
                variable_cost_rate = (1 / roi) + platform_fee_rate
                fixed_costs = product_cost + shipping_insurance_cost + return_shipping_cost_total + other_cost
                break_even_price = fixed_costs / (successful_orders * (1 - variable_cost_rate))
            else:
                break_even_price = 0
            
            # 显示结果
            self.display_results(
                price, cost, roi, return_rate, platform_fee_rate,
                shipping_insurance, return_shipping_cost, other_cost, total_orders,
                successful_orders, returned_orders,
                revenue, ad_cost, product_cost, platform_fee,
                shipping_insurance_cost, return_shipping_cost_total,
                total_cost, profit, profit_margin, break_even_price
            )
            
        except Exception as e:
            self.result_text.Clear()
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(255, 0, 0))
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText(f"计算出错: {str(e)}\n")
    
    def display_results(self, price, cost, roi, return_rate, platform_fee_rate,
                       shipping_insurance, return_shipping_cost, other_cost, total_orders,
                       successful_orders, returned_orders,
                       revenue, ad_cost, product_cost, platform_fee,
                       shipping_insurance_cost, return_shipping_cost_total,
                       total_cost, profit, profit_margin, break_even_price):
        """显示计算结果"""
        self.result_text.Clear()
        
        # 创建字体样式
        bold_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        normal_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        
        # 标题（紧凑版）
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(20, 180, 168))
        attr.SetFont(bold_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText("利润分析结果\n")
        self.result_text.AppendText("─" * 50 + "\n")
        
        # 订单分析（紧凑版）
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(0, 0, 0))
        attr.SetFont(normal_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText("【订单分析】 ")
        self.result_text.AppendText(f"总订单数: {total_orders}单 | ")
        self.result_text.AppendText(f"成功: {successful_orders}单({100*(1-return_rate):.1f}%) | ")
        self.result_text.AppendText(f"退货: {returned_orders}单({return_rate*100:.1f}%)\n")
        
        # 收入（紧凑版）
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(0, 102, 204))
        attr.SetFont(normal_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText("【收入】 ")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText(f"{successful_orders}单 × {price:.2f}元 = {revenue:.2f}元\n")
        
        # 成本明细（紧凑版）
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(226, 96, 95))
        attr.SetFont(normal_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText("【成本明细】\n")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText(f"  广告: {ad_cost:.2f}元 | ")
        self.result_text.AppendText(f"产品成本: {product_cost:.2f}元 | ")
        self.result_text.AppendText(f"平台扣点: {platform_fee:.2f}元 | ")
        self.result_text.AppendText(f"运费险: {shipping_insurance_cost:.2f}元 | ")
        self.result_text.AppendText(f"退货运费: {return_shipping_cost_total:.2f}元")
        if other_cost > 0:
            self.result_text.AppendText(f" | 其他成本: {other_cost:.2f}元")
        self.result_text.AppendText(f"\n  总成本: {total_cost:.2f}元\n")
        
        # 利润分析（紧凑版）
        profit_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        attr = wx.TextAttr()
        if profit > 0:
            attr.SetTextColour(wx.Colour(103, 194, 58))
        elif profit < 0:
            attr.SetTextColour(wx.Colour(255, 0, 0))
        else:
            attr.SetTextColour(wx.Colour(144, 144, 153))
        attr.SetFont(profit_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText("【利润分析】 ")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        attr.SetFont(normal_font)
        self.result_text.SetDefaultStyle(attr)
        self.result_text.AppendText(f"收入: {revenue:.2f}元 | 成本: {total_cost:.2f}元 | ")
        
        if profit > 0:
            attr.SetTextColour(wx.Colour(103, 194, 58))
            attr.SetFont(profit_font)
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText(f"利润: +{profit:.2f}元 | 利润率: +{profit_margin:.2f}%\n")
            self.result_text.AppendText(f"  ✓ 盈利: {profit:.2f}元\n")
        elif profit < 0:
            attr.SetTextColour(wx.Colour(255, 0, 0))
            attr.SetFont(profit_font)
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText(f"利润: {profit:.2f}元 | 利润率: {profit_margin:.2f}%\n")
            self.result_text.AppendText(f"  ✗ 亏损: {abs(profit):.2f}元\n")
        else:
            attr.SetTextColour(wx.Colour(144, 144, 153))
            attr.SetFont(profit_font)
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText(f"利润: 0.00元 | 利润率: 0.00%\n")
            self.result_text.AppendText(f"  ○ 盈亏平衡\n")
        
        # 盈亏平衡点（紧凑版）
        if break_even_price > 0:
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(0, 102, 204))
            attr.SetFont(normal_font)
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText("【盈亏平衡点】 ")
            attr.SetTextColour(wx.Colour(0, 0, 0))
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText(f"当前售价: {price:.2f}元 | 平衡售价: {break_even_price:.2f}元")
            if break_even_price > price:
                self.result_text.AppendText(f" | 需提价: {break_even_price - price:.2f}元({((break_even_price - price) / price * 100):.2f}%)\n")
            elif break_even_price < price:
                self.result_text.AppendText(f" | 高于平衡点: {price - break_even_price:.2f}元\n")
            else:
                self.result_text.AppendText("\n")
        
        # 盈利建议（亏损时显示详细建议，紧凑版）
        if profit < 0:
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(226, 96, 95))
            attr.SetFont(profit_font)
            self.result_text.SetDefaultStyle(attr)
            self.result_text.AppendText("【盈利建议】\n")
            attr.SetTextColour(wx.Colour(0, 0, 0))
            attr.SetFont(normal_font)
            self.result_text.SetDefaultStyle(attr)
            
            suggestions = []
            
            # 方案1：提高售价（计算达到盈亏平衡和10%利润率的售价）
            if break_even_price > price:
                # 盈亏平衡售价
                suggestions.append({
                    'type': '售价',
                    'current': price,
                    'target': break_even_price,
                    'change': break_even_price - price,
                    'change_pct': ((break_even_price - price) / price * 100),
                    'target_profit': 0,
                    'description': f'提价至 {break_even_price:.2f}元（盈亏平衡）'
                })
                
                # 10%利润率售价
                target_price_10 = break_even_price * 1.1
                if target_price_10 > price:
                    test_successful = int(total_orders * (1 - return_rate))
                    test_revenue = test_successful * target_price_10
                    test_ad_cost = test_revenue / roi
                    test_platform_fee = test_successful * target_price_10 * platform_fee_rate
                    test_total_cost = test_ad_cost + product_cost + test_platform_fee + shipping_insurance_cost + return_shipping_cost_total
                    test_profit = test_revenue - test_total_cost
                    test_margin = (test_profit / test_revenue * 100) if test_revenue > 0 else 0
                    
                    suggestions.append({
                        'type': '售价',
                        'current': price,
                        'target': target_price_10,
                        'change': target_price_10 - price,
                        'change_pct': ((target_price_10 - price) / price * 100),
                        'target_profit': test_profit,
                        'target_margin': test_margin,
                        'description': f'提价至 {target_price_10:.2f}元（10%利润率）'
                    })
            
            # 方案2：降低退货率（逐步降低到盈利）
            test_return_rates = [0.25, 0.20, 0.15, 0.10]
            for test_rate in test_return_rates:
                if test_rate < return_rate:
                    test_successful = int(total_orders * (1 - test_rate))
                    test_returned = total_orders - test_successful
                    test_revenue = test_successful * price
                    test_ad_cost = test_revenue / roi
                    test_platform_fee = test_successful * price * platform_fee_rate
                    test_fixed = total_orders * cost + total_orders * shipping_insurance + test_returned * return_shipping_cost
                    test_total_cost = test_ad_cost + test_platform_fee + test_fixed
                    test_profit = test_revenue - test_total_cost
                    
                    if test_profit > 0:
                        test_margin = (test_profit / test_revenue * 100) if test_revenue > 0 else 0
                        suggestions.append({
                            'type': '退货率',
                            'current': return_rate * 100,
                            'target': test_rate * 100,
                            'change': (return_rate - test_rate) * 100,
                            'change_pct': ((return_rate - test_rate) / return_rate * 100),
                            'target_profit': test_profit,
                            'target_margin': test_margin,
                            'description': f'退货率降至 {test_rate*100:.0f}%'
                        })
                        break  # 找到第一个盈利的退货率就停止
            
            # 方案3：提高ROI（逐步提升到盈利）
            test_rois = [5.5, 6.0, 7.0, 8.0]
            for test_roi in test_rois:
                if test_roi > roi:
                    test_ad_cost = revenue / test_roi
                    test_total_cost = test_ad_cost + product_cost + platform_fee + shipping_insurance_cost + return_shipping_cost_total
                    test_profit = revenue - test_total_cost
                    
                    if test_profit > 0:
                        test_margin = (test_profit / revenue * 100) if revenue > 0 else 0
                        suggestions.append({
                            'type': 'ROI',
                            'current': roi,
                            'target': test_roi,
                            'change': test_roi - roi,
                            'change_pct': ((test_roi - roi) / roi * 100),
                            'target_profit': test_profit,
                            'target_margin': test_margin,
                            'description': f'ROI提升至 {test_roi:.2f}'
                        })
                        break  # 找到第一个盈利的ROI就停止
            
            # 方案4：降低产品成本
            if successful_orders > 0:
                variable_cost_rate = (1 / roi) + platform_fee_rate
                fixed_costs = shipping_insurance_cost + return_shipping_cost_total
                # 盈亏平衡成本 = (收入 * (1 - 可变成本率) - 固定成本 - 其他成本) / 订单数
                break_even_cost = (revenue * (1 - variable_cost_rate) - fixed_costs - other_cost) / total_orders
                if break_even_cost < cost and break_even_cost > 0:
                    test_product_cost = break_even_cost * total_orders
                    test_total_cost = ad_cost + test_product_cost + platform_fee + shipping_insurance_cost + return_shipping_cost_total
                    test_profit = revenue - test_total_cost
                    
                    suggestions.append({
                        'type': '成本',
                        'current': cost,
                        'target': break_even_cost,
                        'change': cost - break_even_cost,
                        'change_pct': ((cost - break_even_cost) / cost * 100),
                        'target_profit': test_profit,
                        'target_margin': 0,
                        'description': f'成本降至 {break_even_cost:.2f}元（盈亏平衡）'
                    })
            
            # 显示建议（紧凑版）
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    self.result_text.AppendText(f"  方案{i}: {suggestion['description']}")
                    if suggestion['type'] == '售价':
                        self.result_text.AppendText(f" | 当前: {suggestion['current']:.2f}元 → 目标: {suggestion['target']:.2f}元 | 提价: {suggestion['change']:.2f}元({suggestion['change_pct']:.2f}%)")
                    elif suggestion['type'] == '退货率':
                        self.result_text.AppendText(f" | 当前: {suggestion['current']:.1f}% → 目标: {suggestion['target']:.1f}% | 降低: {suggestion['change']:.1f}%({suggestion['change_pct']:.1f}%)")
                    elif suggestion['type'] == 'ROI':
                        self.result_text.AppendText(f" | 当前: {suggestion['current']:.2f} → 目标: {suggestion['target']:.2f} | 提升: {suggestion['change']:.2f}({suggestion['change_pct']:.1f}%)")
                    elif suggestion['type'] == '成本':
                        self.result_text.AppendText(f" | 当前: {suggestion['current']:.2f}元 → 目标: {suggestion['target']:.2f}元 | 降低: {suggestion['change']:.2f}元({suggestion['change_pct']:.1f}%)")
                    
                    if suggestion['target_profit'] > 0:
                        self.result_text.AppendText(f" | 预期利润: {suggestion['target_profit']:.2f}元")
                        if 'target_margin' in suggestion and suggestion['target_margin'] > 0:
                            self.result_text.AppendText(f" | 利润率: {suggestion['target_margin']:.2f}%")
                    self.result_text.AppendText("\n")
            else:
                self.result_text.AppendText("  暂无可行的盈利方案\n")
        
        # 滚动到顶部（从顶部开始显示）
        self.result_text.ShowPosition(0)


def main():
    app = wx.App()
    frame = EcommerceProfitCalculator()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()

