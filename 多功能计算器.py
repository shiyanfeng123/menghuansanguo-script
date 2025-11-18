"""
多功能计算器 - 主程序
支持多种计算器：基础计算器、房贷计算器、车贷计算器、贷款计算器、
社保计算器、公积金计算器、个税计算器、投资计算器、电商利润计算器等
"""

import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
import math
import re
import datetime


class MultiCalculatorApp(wx.Frame):
    """多功能计算器主窗口"""
    
    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="多功能计算器 - 智能版",
            size=(1200, 900),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # 设置主窗口背景色
        self.SetBackgroundColour(wx.Colour(240, 245, 255))
        
        # 创建主面板
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # 创建主布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域
        title_panel = self.create_title_panel(panel)
        main_sizer.Add(title_panel, 0, wx.EXPAND | wx.ALL, 0)
        
        # 创建标签页容器（支持多行标签）
        self.notebook = wx.Notebook(panel, style=wx.NB_TOP | wx.NB_MULTILINE)
        self.notebook.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # 初始化计算器字典
        self.calculators = {}
        
        # 添加电商利润计算器
        ecommerce_calc = self.create_ecommerce_calculator_panel()
        self.notebook.AddPage(ecommerce_calc, "💰 电商利润")
        self.calculators['电商利润'] = ecommerce_calc
        
        # 添加基础计算器（占位）
        basic_calc = self.create_basic_calculator_panel()
        self.notebook.AddPage(basic_calc, "🔢 基础计算")
        self.calculators['基础计算'] = basic_calc
        
        # 添加房贷计算器（占位）
        mortgage_calc = self.create_mortgage_calculator_panel()
        self.notebook.AddPage(mortgage_calc, "🏠 房贷计算")
        self.calculators['房贷计算'] = mortgage_calc
        
        # 添加车贷计算器（占位）
        car_loan_calc = self.create_car_loan_calculator_panel()
        self.notebook.AddPage(car_loan_calc, "🚗 车贷计算")
        self.calculators['车贷计算'] = car_loan_calc
        
        # 添加贷款计算器（占位）
        loan_calc = self.create_loan_calculator_panel()
        self.notebook.AddPage(loan_calc, "💳 贷款计算")
        self.calculators['贷款计算'] = loan_calc
        
        # 添加个税计算器（占位）
        tax_calc = self.create_tax_calculator_panel()
        self.notebook.AddPage(tax_calc, "📊 个税计算")
        self.calculators['个税计算'] = tax_calc
        
        # 添加社保计算器
        social_security_calc = self.create_social_security_calculator_panel()
        self.notebook.AddPage(social_security_calc, "🛡️ 社保计算")
        self.calculators['社保计算'] = social_security_calc
        
        # 添加公积金计算器
        housing_fund_calc = self.create_housing_fund_calculator_panel()
        self.notebook.AddPage(housing_fund_calc, "🏦 公积金")
        self.calculators['公积金'] = housing_fund_calc
        
        # 添加投资计算器
        investment_calc = self.create_investment_calculator_panel()
        self.notebook.AddPage(investment_calc, "📈 投资计算")
        self.calculators['投资计算'] = investment_calc
        
        # 添加BMI计算器
        bmi_calc = self.create_bmi_calculator_panel()
        self.notebook.AddPage(bmi_calc, "⚖️ BMI计算")
        self.calculators['BMI计算'] = bmi_calc
        
        # 添加单位换算器
        unit_convert_calc = self.create_unit_converter_panel()
        self.notebook.AddPage(unit_convert_calc, "🔄 单位换算")
        self.calculators['单位换算'] = unit_convert_calc
        
        # 添加日期计算器
        date_calc = self.create_date_calculator_panel()
        self.notebook.AddPage(date_calc, "📅 日期计算")
        self.calculators['日期计算'] = date_calc
        
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 绑定标签页切换事件
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
    
    def create_title_panel(self, parent):
        """创建标题面板"""
        title_panel = wx.Panel(parent)
        title_panel.SetBackgroundColour(wx.Colour(64, 158, 255))
        title_panel.SetMinSize((-1, 90))
        
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 主标题
        title = wx.StaticText(title_panel, label="🧮 多功能计算器")
        title_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        
        # 副标题
        subtitle = wx.StaticText(title_panel, label="✨ 生活 · 金融 · 投资 · 理财 · 一站式计算工具")
        subtitle_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(wx.Colour(240, 248, 255))
        
        title_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        title_sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        title_panel.SetSizer(title_sizer)
        
        return title_panel
    
    def create_ecommerce_calculator_panel(self):
        """创建电商利润计算器面板（完整嵌入版）"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(240, 245, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 智能识别输入区域
        smart_input_panel = self.create_ecommerce_smart_input_panel(panel)
        main_sizer.Add(smart_input_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # 创建左右分栏
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        input_panel = self.create_ecommerce_input_panel(left_panel)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(input_panel, 1, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        result_panel = self.create_ecommerce_result_panel(right_panel)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(result_panel, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 初始化计算
        self.ecommerce_calculate()
        
        return panel
    
    def create_basic_calculator_panel(self):
        """创建基础计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建左右分栏
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：计算器界面
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((500, -1))
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 结果显示区域（卡片式设计）
        result_panel = wx.Panel(left_panel)
        result_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        result_panel.SetMinSize((-1, 140))
        
        result_container = wx.Panel(result_panel)
        result_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        result_container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 表达式显示
        self.basic_expression_text = wx.StaticText(result_container, label="", style=wx.ALIGN_RIGHT)
        expr_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.basic_expression_text.SetFont(expr_font)
        self.basic_expression_text.SetForegroundColour(wx.Colour(144, 147, 153))
        
        # 结果显示
        self.basic_result_text = wx.StaticText(result_container, label="0", style=wx.ALIGN_RIGHT)
        result_font = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        self.basic_result_text.SetFont(result_font)
        self.basic_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        
        result_sizer.Add(self.basic_expression_text, 1, wx.EXPAND | wx.ALL, 15)
        result_sizer.Add(self.basic_result_text, 2, wx.EXPAND | wx.ALL, 15)
        result_container.SetSizer(result_sizer)
        result_container_sizer.Add(result_container, 1, wx.EXPAND | wx.ALL, 8)
        result_panel.SetSizer(result_container_sizer)
        
        left_sizer.Add(result_panel, 0, wx.EXPAND | wx.ALL, 8)
        
        # 按钮网格（卡片式设计）
        button_panel = wx.Panel(left_panel)
        button_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        button_container = wx.Panel(button_panel)
        button_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        button_grid = wx.GridSizer(5, 5, 8, 8)
        
        # 按钮文本和颜色（RGB元组）
        buttons = [
            ('C', (245, 108, 108)), ('CE', (245, 108, 108)), ('(', (144, 147, 153)), (')', (144, 147, 153)), ('/', (64, 158, 255)),
            ('7', (48, 49, 51)), ('8', (48, 49, 51)), ('9', (48, 49, 51)), ('*', (64, 158, 255)), ('√', (103, 194, 58)),
            ('4', (48, 49, 51)), ('5', (48, 49, 51)), ('6', (48, 49, 51)), ('-', (64, 158, 255)), ('x²', (103, 194, 58)),
            ('1', (48, 49, 51)), ('2', (48, 49, 51)), ('3', (48, 49, 51)), ('+', (64, 158, 255)), ('1/x', (103, 194, 58)),
            ('±', (144, 147, 153)), ('0', (48, 49, 51)), ('.', (48, 49, 51)), ('=', (64, 158, 255)), ('%', (144, 147, 153)),
        ]
        
        self.basic_buttons = {}
        for text, color_rgb in buttons:
            btn = wx.Button(button_container, label=text, size=(85, 65))
            btn.SetBackgroundColour(wx.Colour(color_rgb[0], color_rgb[1], color_rgb[2]))
            btn.SetForegroundColour(wx.Colour(255, 255, 255))
            btn_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
            btn.SetFont(btn_font)
            btn.Bind(wx.EVT_BUTTON, self.on_basic_button_click)
            # 添加悬停效果
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn, c=color_rgb: b.SetBackgroundColour(wx.Colour(min(255, c[0]+20), min(255, c[1]+20), min(255, c[2]+20))))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn, c=color_rgb: b.SetBackgroundColour(wx.Colour(c[0], c[1], c[2])))
            button_grid.Add(btn, 0, wx.EXPAND)
            self.basic_buttons[text] = btn
        
        button_container.SetSizer(button_grid)
        button_container_sizer = wx.BoxSizer(wx.VERTICAL)
        button_container_sizer.Add(button_container, 1, wx.EXPAND | wx.ALL, 8)
        button_panel.SetSizer(button_container_sizer)
        left_sizer.Add(button_panel, 1, wx.EXPAND | wx.ALL, 8)
        
        # 科学计算按钮区域（卡片式设计）
        sci_panel = wx.Panel(left_panel)
        sci_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        sci_container = wx.Panel(sci_panel)
        sci_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        sci_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sci_title = wx.StaticText(sci_container, label="🔬 科学函数：")
        sci_title.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        sci_title.SetForegroundColour(wx.Colour(48, 49, 51))
        sci_sizer.Add(sci_title, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        
        sci_buttons = [
            ('sin', 'sin'), ('cos', 'cos'), ('tan', 'tan'),
            ('log', 'log'), ('ln', 'ln'), ('π', 'pi'),
            ('e', 'e'), ('^', '**')
        ]
        
        for label, func in sci_buttons:
            btn = wx.Button(sci_container, label=label, size=(65, 38))
            btn.SetBackgroundColour(wx.Colour(67, 194, 58))
            btn.SetForegroundColour(wx.Colour(255, 255, 255))
            btn_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
            btn.SetFont(btn_font)
            btn.Bind(wx.EVT_BUTTON, lambda e, f=func: self.on_basic_sci_button(f))
            btn.Bind(wx.EVT_ENTER_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(87, 214, 78)))
            btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e, b=btn: b.SetBackgroundColour(wx.Colour(67, 194, 58)))
            sci_sizer.Add(btn, 0, wx.ALL, 3)
        
        sci_container.SetSizer(sci_sizer)
        sci_container_sizer = wx.BoxSizer(wx.VERTICAL)
        sci_container_sizer.Add(sci_container, 1, wx.EXPAND | wx.ALL, 8)
        sci_panel.SetSizer(sci_container_sizer)
        left_sizer.Add(sci_panel, 0, wx.EXPAND | wx.ALL, 8)
        
        left_panel.SetSizer(left_sizer)
        
        # 右侧：表达式输入和历史记录（卡片式设计）
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 表达式输入区域（卡片式设计）
        expr_input_panel = wx.Panel(right_panel)
        expr_input_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        expr_input_container = wx.Panel(expr_input_panel)
        expr_input_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        expr_input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        expr_label = wx.StaticText(expr_input_container, label="📝 表达式输入")
        expr_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                   wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        expr_label.SetForegroundColour(wx.Colour(64, 158, 255))
        
        self.basic_expr_input = wx.TextCtrl(expr_input_container, style=wx.TE_MULTILINE, size=(-1, 90))
        self.basic_expr_input.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                         wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.basic_expr_input.SetBackgroundColour(wx.Colour(250, 252, 255))
        self.basic_expr_input.Bind(wx.EVT_TEXT, self.on_basic_expr_input)
        
        calc_btn = wx.Button(expr_input_container, label="计算表达式", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_expr)
        calc_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        calc_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        
        expr_input_sizer.Add(expr_label, 0, wx.ALL, 10)
        expr_input_sizer.Add(self.basic_expr_input, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        expr_input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        expr_input_container.SetSizer(expr_input_sizer)
        
        expr_input_container_sizer = wx.BoxSizer(wx.VERTICAL)
        expr_input_container_sizer.Add(expr_input_container, 1, wx.EXPAND | wx.ALL, 8)
        expr_input_panel.SetSizer(expr_input_container_sizer)
        
        right_sizer.Add(expr_input_panel, 0, wx.EXPAND | wx.ALL, 8)
        
        # 历史记录区域（卡片式设计）
        history_panel = wx.Panel(right_panel)
        history_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        history_container = wx.Panel(history_panel)
        history_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        history_sizer = wx.BoxSizer(wx.VERTICAL)
        
        history_label = wx.StaticText(history_container, label="📋 计算历史")
        history_label.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                     wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        history_label.SetForegroundColour(wx.Colour(64, 158, 255))
        
        self.basic_history_list = wx.ListBox(history_container, style=wx.LB_SINGLE)
        self.basic_history_list.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.basic_history_list.SetBackgroundColour(wx.Colour(250, 252, 255))
        self.basic_history_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_history_select)
        
        clear_history_btn = wx.Button(history_container, label="🗑️ 清空历史", size=(-1, 35))
        clear_history_btn.SetBackgroundColour(wx.Colour(144, 147, 153))
        clear_history_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        clear_history_btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                         wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        clear_history_btn.Bind(wx.EVT_BUTTON, self.on_clear_history)
        clear_history_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: clear_history_btn.SetBackgroundColour(wx.Colour(164, 167, 173)))
        clear_history_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: clear_history_btn.SetBackgroundColour(wx.Colour(144, 147, 153)))
        
        history_sizer.Add(history_label, 0, wx.ALL, 10)
        history_sizer.Add(self.basic_history_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        history_sizer.Add(clear_history_btn, 0, wx.EXPAND | wx.ALL, 10)
        history_container.SetSizer(history_sizer)
        
        history_container_sizer = wx.BoxSizer(wx.VERTICAL)
        history_container_sizer.Add(history_container, 1, wx.EXPAND | wx.ALL, 8)
        history_panel.SetSizer(history_container_sizer)
        
        right_sizer.Add(history_panel, 1, wx.EXPAND | wx.ALL, 8)
        
        right_panel.SetSizer(right_sizer)
        
        # 添加左右面板
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        # 初始化状态
        self.basic_current_value = "0"
        self.basic_expression = ""
        self.basic_history = []
        
        return panel
    
    def create_mortgage_calculator_panel(self):
        """创建房贷计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建左右分栏
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 输入参数区域
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="🏠 房贷计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 贷款总额
        loan_amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_amount_label = wx.StaticText(input_panel, label="贷款总额（万元）：")
        loan_amount_label.SetMinSize((150, -1))
        self.mortgage_loan_amount = wx.TextCtrl(input_panel, value="100")
        loan_amount_sizer.Add(loan_amount_label, 0, wx.ALL, 5)
        loan_amount_sizer.Add(self.mortgage_loan_amount, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_amount_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款期限
        loan_term_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_term_label = wx.StaticText(input_panel, label="贷款期限（年）：")
        loan_term_label.SetMinSize((150, -1))
        self.mortgage_loan_term = wx.TextCtrl(input_panel, value="30")
        loan_term_sizer.Add(loan_term_label, 0, wx.ALL, 5)
        loan_term_sizer.Add(self.mortgage_loan_term, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_term_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 年利率
        interest_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        interest_rate_label = wx.StaticText(input_panel, label="年利率（%）：")
        interest_rate_label.SetMinSize((150, -1))
        self.mortgage_interest_rate = wx.TextCtrl(input_panel, value="4.5")
        interest_rate_sizer.Add(interest_rate_label, 0, wx.ALL, 5)
        interest_rate_sizer.Add(self.mortgage_interest_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(interest_rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 还款方式选择
        repayment_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        repayment_type_label = wx.StaticText(input_panel, label="还款方式：")
        repayment_type_label.SetMinSize((150, -1))
        self.mortgage_repayment_type = wx.RadioBox(
            input_panel,
            choices=["等额本息", "等额本金"],
            majorDimension=2,
            style=wx.RA_HORIZONTAL
        )
        repayment_type_sizer.Add(repayment_type_label, 0, wx.ALL, 5)
        repayment_type_sizer.Add(self.mortgage_repayment_type, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(repayment_type_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_mortgage)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 结果显示面板（使用滚动面板）
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.mortgage_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.mortgage_result_text.SetFont(result_font)
        self.mortgage_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.mortgage_result_text.Wrap(600)
        
        result_sizer.Add(self.mortgage_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        # 添加左右面板
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_mortgage(self, event):
        """计算房贷"""
        try:
            loan_amount = float(self.mortgage_loan_amount.GetValue()) * 10000  # 转换为元
            loan_term_years = int(self.mortgage_loan_term.GetValue())
            annual_rate = float(self.mortgage_interest_rate.GetValue()) / 100
            
            if loan_amount <= 0 or loan_term_years <= 0 or annual_rate <= 0:
                raise ValueError("参数必须大于0")
            
            repayment_type = self.mortgage_repayment_type.GetSelection()  # 0=等额本息, 1=等额本金
            
            if repayment_type == 0:
                # 等额本息
                result = self.calculate_equal_principal_interest(loan_amount, loan_term_years, annual_rate)
            else:
                # 等额本金
                result = self.calculate_equal_principal(loan_amount, loan_term_years, annual_rate)
            
            self.mortgage_result_text.SetLabel(result)
            self.mortgage_result_text.Wrap(600)
            result_scroll = self.mortgage_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def calculate_equal_principal_interest(self, loan_amount, loan_term_years, annual_rate):
        """等额本息计算"""
        monthly_rate = annual_rate / 12
        total_months = loan_term_years * 12
        
        # 月供计算公式
        if monthly_rate == 0:
            monthly_payment = loan_amount / total_months
        else:
            monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** total_months / \
                            ((1 + monthly_rate) ** total_months - 1)
        
        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        
        result = f"""等额本息还款计算结果：

贷款总额：{loan_amount/10000:.2f} 万元
贷款期限：{loan_term_years} 年（{total_months} 个月）
年利率：{annual_rate*100:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

月供金额：{monthly_payment:.2f} 元

总还款额：{total_payment:.2f} 元
总利息：{total_interest:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

还款明细（前12个月）：
"""
        
        remaining_principal = loan_amount
        for month in range(1, min(13, total_months + 1)):
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment
            
            result += f"\n第{month}期："
            result += f"月供 {monthly_payment:.2f} 元 "
            result += f"（本金 {principal_payment:.2f} 元 + 利息 {interest_payment:.2f} 元）"
            result += f" 剩余本金 {remaining_principal:.2f} 元"
        
        if total_months > 12:
            result += f"\n\n...（共{total_months}期）"
        
        return result
    
    def calculate_equal_principal(self, loan_amount, loan_term_years, annual_rate):
        """等额本金计算"""
        monthly_rate = annual_rate / 12
        total_months = loan_term_years * 12
        
        # 每月本金
        monthly_principal = loan_amount / total_months
        
        # 首月月供
        first_month_payment = monthly_principal + loan_amount * monthly_rate
        
        # 末月月供
        last_month_payment = monthly_principal + monthly_principal * monthly_rate
        
        # 总利息
        total_interest = loan_amount * monthly_rate * (total_months + 1) / 2
        
        total_payment = loan_amount + total_interest
        
        result = f"""等额本金还款计算结果：

贷款总额：{loan_amount/10000:.2f} 万元
贷款期限：{loan_term_years} 年（{total_months} 个月）
年利率：{annual_rate*100:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

首月月供：{first_month_payment:.2f} 元
末月月供：{last_month_payment:.2f} 元
每月递减：{monthly_principal * monthly_rate:.2f} 元

总还款额：{total_payment:.2f} 元
总利息：{total_interest:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

还款明细（前12个月）：
"""
        
        remaining_principal = loan_amount
        for month in range(1, min(13, total_months + 1)):
            interest_payment = remaining_principal * monthly_rate
            monthly_payment = monthly_principal + interest_payment
            remaining_principal -= monthly_principal
            
            result += f"\n第{month}期："
            result += f"月供 {monthly_payment:.2f} 元 "
            result += f"（本金 {monthly_principal:.2f} 元 + 利息 {interest_payment:.2f} 元）"
            result += f" 剩余本金 {remaining_principal:.2f} 元"
        
        if total_months > 12:
            result += f"\n\n...（共{total_months}期）"
        
        return result
    
    def create_car_loan_calculator_panel(self):
        """创建车贷计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="🚗 车贷计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 车价
        car_price_sizer = wx.BoxSizer(wx.HORIZONTAL)
        car_price_label = wx.StaticText(input_panel, label="车价（万元）：")
        car_price_label.SetMinSize((150, -1))
        self.car_price = wx.TextCtrl(input_panel, value="20")
        car_price_sizer.Add(car_price_label, 0, wx.ALL, 5)
        car_price_sizer.Add(self.car_price, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(car_price_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 首付比例
        down_payment_sizer = wx.BoxSizer(wx.HORIZONTAL)
        down_payment_label = wx.StaticText(input_panel, label="首付比例（%）：")
        down_payment_label.SetMinSize((150, -1))
        self.car_down_payment_rate = wx.TextCtrl(input_panel, value="30")
        down_payment_sizer.Add(down_payment_label, 0, wx.ALL, 5)
        down_payment_sizer.Add(self.car_down_payment_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(down_payment_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款期限
        loan_term_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_term_label = wx.StaticText(input_panel, label="贷款期限（年）：")
        loan_term_label.SetMinSize((150, -1))
        self.car_loan_term = wx.TextCtrl(input_panel, value="3")
        loan_term_sizer.Add(loan_term_label, 0, wx.ALL, 5)
        loan_term_sizer.Add(self.car_loan_term, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_term_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 年利率
        interest_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        interest_rate_label = wx.StaticText(input_panel, label="年利率（%）：")
        interest_rate_label.SetMinSize((150, -1))
        self.car_interest_rate = wx.TextCtrl(input_panel, value="6.0")
        interest_rate_sizer.Add(interest_rate_label, 0, wx.ALL, 5)
        interest_rate_sizer.Add(self.car_interest_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(interest_rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_car_loan)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.car_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.car_result_text.SetFont(result_font)
        self.car_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.car_result_text.Wrap(600)
        
        result_sizer.Add(self.car_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_car_loan(self, event):
        """计算车贷"""
        try:
            car_price = float(self.car_price.GetValue()) * 10000  # 转换为元
            down_payment_rate = float(self.car_down_payment_rate.GetValue()) / 100
            loan_term_years = int(self.car_loan_term.GetValue())
            annual_rate = float(self.car_interest_rate.GetValue()) / 100
            
            if car_price <= 0 or down_payment_rate < 0 or down_payment_rate >= 1 or loan_term_years <= 0 or annual_rate <= 0:
                raise ValueError("参数无效")
            
            down_payment = car_price * down_payment_rate
            loan_amount = car_price - down_payment
            monthly_rate = annual_rate / 12
            total_months = loan_term_years * 12
            
            # 等额本息计算
            if monthly_rate == 0:
                monthly_payment = loan_amount / total_months
            else:
                monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** total_months / \
                                ((1 + monthly_rate) ** total_months - 1)
            
            total_payment = monthly_payment * total_months
            total_interest = total_payment - loan_amount
            total_cost = car_price + total_interest
            
            result = f"""车贷计算结果：

车辆价格：{car_price/10000:.2f} 万元
首付金额：{down_payment/10000:.2f} 万元（{down_payment_rate*100:.1f}%）
贷款金额：{loan_amount/10000:.2f} 万元
贷款期限：{loan_term_years} 年（{total_months} 个月）
年利率：{annual_rate*100:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

月供金额：{monthly_payment:.2f} 元

总还款额：{total_payment:.2f} 元
总利息：{total_interest:.2f} 元
购车总成本：{total_cost/10000:.2f} 万元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

还款明细（前12个月）：
"""
            
            remaining_principal = loan_amount
            for month in range(1, min(13, total_months + 1)):
                interest_payment = remaining_principal * monthly_rate
                principal_payment = monthly_payment - interest_payment
                remaining_principal -= principal_payment
                
                result += f"\n第{month}期："
                result += f"月供 {monthly_payment:.2f} 元 "
                result += f"（本金 {principal_payment:.2f} 元 + 利息 {interest_payment:.2f} 元）"
                result += f" 剩余本金 {remaining_principal:.2f} 元"
            
            if total_months > 12:
                result += f"\n\n...（共{total_months}期）"
            
            self.car_result_text.SetLabel(result)
            self.car_result_text.Wrap(600)
            result_scroll = self.car_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_loan_calculator_panel(self):
        """创建贷款计算器面板（占位）"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        placeholder = wx.Panel(panel)
        placeholder.SetBackgroundColour(wx.Colour(250, 252, 255))
        
        info_text = wx.StaticText(
            placeholder,
            label="💳 贷款计算器\n\n"
                  "功能：\n"
                  "• 个人贷款计算\n"
                  "• 商业贷款计算\n"
                  "• 多种还款方式\n"
                  "• 利率计算器\n\n"
                  "🚧 开发中，敬请期待..."
        )
        info_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        info_text.SetFont(info_font)
        info_text.SetForegroundColour(wx.Colour(144, 147, 153))
        
        sizer.Add(info_text, 1, wx.ALIGN_CENTER | wx.ALL, 50)
        placeholder.SetSizer(sizer)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(placeholder, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def create_loan_calculator_panel(self):
        """创建贷款计算器面板（与房贷计算器类似，但更通用）"""
        # 复用房贷计算器的实现，但标签改为"贷款计算器"
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="💳 贷款计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 贷款总额
        loan_amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_amount_label = wx.StaticText(input_panel, label="贷款总额（万元）：")
        loan_amount_label.SetMinSize((150, -1))
        self.loan_amount = wx.TextCtrl(input_panel, value="50")
        loan_amount_sizer.Add(loan_amount_label, 0, wx.ALL, 5)
        loan_amount_sizer.Add(self.loan_amount, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_amount_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款期限
        loan_term_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_term_label = wx.StaticText(input_panel, label="贷款期限（年）：")
        loan_term_label.SetMinSize((150, -1))
        self.loan_term = wx.TextCtrl(input_panel, value="5")
        loan_term_sizer.Add(loan_term_label, 0, wx.ALL, 5)
        loan_term_sizer.Add(self.loan_term, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_term_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 年利率
        interest_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        interest_rate_label = wx.StaticText(input_panel, label="年利率（%）：")
        interest_rate_label.SetMinSize((150, -1))
        self.loan_interest_rate = wx.TextCtrl(input_panel, value="5.5")
        interest_rate_sizer.Add(interest_rate_label, 0, wx.ALL, 5)
        interest_rate_sizer.Add(self.loan_interest_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(interest_rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 还款方式选择
        repayment_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        repayment_type_label = wx.StaticText(input_panel, label="还款方式：")
        repayment_type_label.SetMinSize((150, -1))
        self.loan_repayment_type = wx.RadioBox(
            input_panel,
            choices=["等额本息", "等额本金"],
            majorDimension=2,
            style=wx.RA_HORIZONTAL
        )
        repayment_type_sizer.Add(repayment_type_label, 0, wx.ALL, 5)
        repayment_type_sizer.Add(self.loan_repayment_type, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(repayment_type_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_loan)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.loan_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.loan_result_text.SetFont(result_font)
        self.loan_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.loan_result_text.Wrap(600)
        
        result_sizer.Add(self.loan_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_loan(self, event):
        """计算贷款（复用房贷计算方法）"""
        try:
            loan_amount = float(self.loan_amount.GetValue()) * 10000
            loan_term_years = int(self.loan_term.GetValue())
            annual_rate = float(self.loan_interest_rate.GetValue()) / 100
            
            if loan_amount <= 0 or loan_term_years <= 0 or annual_rate <= 0:
                raise ValueError("参数必须大于0")
            
            repayment_type = self.loan_repayment_type.GetSelection()
            
            if repayment_type == 0:
                result = self.calculate_equal_principal_interest(loan_amount, loan_term_years, annual_rate)
            else:
                result = self.calculate_equal_principal(loan_amount, loan_term_years, annual_rate)
            
            self.loan_result_text.SetLabel(result)
            self.loan_result_text.Wrap(600)
            result_scroll = self.loan_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_tax_calculator_panel(self):
        """创建个税计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="📊 个税计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 月薪
        salary_sizer = wx.BoxSizer(wx.HORIZONTAL)
        salary_label = wx.StaticText(input_panel, label="月薪（元）：")
        salary_label.SetMinSize((150, -1))
        self.tax_salary = wx.TextCtrl(input_panel, value="10000")
        salary_sizer.Add(salary_label, 0, wx.ALL, 5)
        salary_sizer.Add(self.tax_salary, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(salary_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 五险一金
        social_security_sizer = wx.BoxSizer(wx.HORIZONTAL)
        social_security_label = wx.StaticText(input_panel, label="五险一金（元）：")
        social_security_label.SetMinSize((150, -1))
        self.tax_social_security = wx.TextCtrl(input_panel, value="1500")
        social_security_sizer.Add(social_security_label, 0, wx.ALL, 5)
        social_security_sizer.Add(self.tax_social_security, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(social_security_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 专项扣除
        deduction_sizer = wx.BoxSizer(wx.HORIZONTAL)
        deduction_label = wx.StaticText(input_panel, label="专项扣除（元）：")
        deduction_label.SetMinSize((150, -1))
        self.tax_deduction = wx.TextCtrl(input_panel, value="2000")
        deduction_sizer.Add(deduction_label, 0, wx.ALL, 5)
        deduction_sizer.Add(self.tax_deduction, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(deduction_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_tax)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.tax_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.tax_result_text.SetFont(result_font)
        self.tax_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.tax_result_text.Wrap(600)
        
        result_sizer.Add(self.tax_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_tax(self, event):
        """计算个税（2023年个税计算规则）"""
        try:
            monthly_salary = float(self.tax_salary.GetValue())
            social_security = float(self.tax_social_security.GetValue())
            deduction = float(self.tax_deduction.GetValue())
            
            if monthly_salary < 0:
                raise ValueError("月薪不能为负")
            
            # 基本减除费用（起征点）
            basic_deduction = 5000
            
            # 应纳税所得额
            taxable_income = monthly_salary - social_security - deduction - basic_deduction
            
            if taxable_income <= 0:
                result = f"""个税计算结果：

月薪：{monthly_salary:.2f} 元
五险一金：{social_security:.2f} 元
专项扣除：{deduction:.2f} 元
基本减除费用：{basic_deduction:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

应纳税所得额：{taxable_income:.2f} 元

个人所得税：0.00 元
税后收入：{monthly_salary - social_security:.2f} 元
"""
            else:
                # 个税税率表（2023年，年度累计）
                # 格式：(年度收入下限, 年度收入上限, 税率, 速算扣除数)
                tax_brackets = [
                    (0, 36000, 0.03, 0),
                    (36000, 144000, 0.10, 2520),
                    (144000, 300000, 0.20, 16920),
                    (300000, 420000, 0.25, 31920),
                    (420000, 660000, 0.30, 52920),
                    (660000, 960000, 0.35, 85920),
                    (960000, float('inf'), 0.45, 181920),
                ]
                
                annual_taxable_income = taxable_income * 12
                annual_tax = 0
                
                # 使用累进税率计算年度税额
                for min_income, max_income, rate, quick_deduction in tax_brackets:
                    if annual_taxable_income > min_income:
                        if annual_taxable_income <= max_income:
                            # 在这个区间内，使用公式：应纳税额 = 应纳税所得额 × 税率 - 速算扣除数
                            annual_tax = annual_taxable_income * rate - quick_deduction
                            break
                    else:
                        break
                
                # 计算月度税额（平均分配）
                monthly_tax = annual_tax / 12
                after_tax_income = monthly_salary - social_security - monthly_tax
                
                result = f"""个税计算结果：

月薪：{monthly_salary:.2f} 元
五险一金：{social_security:.2f} 元
专项扣除：{deduction:.2f} 元
基本减除费用：{basic_deduction:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

应纳税所得额：{taxable_income:.2f} 元
年度应纳税所得额：{annual_taxable_income:.2f} 元

个人所得税：{monthly_tax:.2f} 元/月
年度个人所得税：{annual_tax:.2f} 元

税后收入：{after_tax_income:.2f} 元/月
年度税后收入：{after_tax_income * 12:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

税率说明：
• 不超过36,000元：3%
• 超过36,000至144,000元：10%
• 超过144,000至300,000元：20%
• 超过300,000至420,000元：25%
• 超过420,000至660,000元：30%
• 超过660,000至960,000元：35%
• 超过960,000元：45%
"""
            
            self.tax_result_text.SetLabel(result)
            self.tax_result_text.Wrap(600)
            result_scroll = self.tax_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_social_security_calculator_panel(self):
        """创建社保计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="🛡️ 社保计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 缴费基数
        base_sizer = wx.BoxSizer(wx.HORIZONTAL)
        base_label = wx.StaticText(input_panel, label="缴费基数（元）：")
        base_label.SetMinSize((150, -1))
        self.ss_base = wx.TextCtrl(input_panel, value="10000")
        base_sizer.Add(base_label, 0, wx.ALL, 5)
        base_sizer.Add(self.ss_base, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(base_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算类型选择
        calc_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calc_type_label = wx.StaticText(input_panel, label="计算类型：")
        calc_type_label.SetMinSize((150, -1))
        self.ss_calc_type = wx.RadioBox(
            input_panel,
            choices=["五险一金缴费", "退休金预估"],
            majorDimension=2,
            style=wx.RA_HORIZONTAL
        )
        calc_type_sizer.Add(calc_type_label, 0, wx.ALL, 5)
        calc_type_sizer.Add(self.ss_calc_type, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(calc_type_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 缴费年限（用于退休金计算）
        years_sizer = wx.BoxSizer(wx.HORIZONTAL)
        years_label = wx.StaticText(input_panel, label="缴费年限（年）：")
        years_label.SetMinSize((150, -1))
        self.ss_years = wx.TextCtrl(input_panel, value="30")
        years_sizer.Add(years_label, 0, wx.ALL, 5)
        years_sizer.Add(self.ss_years, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(years_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 城市选择（影响缴费比例）
        city_sizer = wx.BoxSizer(wx.HORIZONTAL)
        city_label = wx.StaticText(input_panel, label="所在城市：")
        city_label.SetMinSize((150, -1))
        self.ss_city = wx.Choice(input_panel, choices=["北京", "上海", "广州", "深圳", "其他城市"])
        self.ss_city.SetSelection(0)
        city_sizer.Add(city_label, 0, wx.ALL, 5)
        city_sizer.Add(self.ss_city, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(city_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_social_security)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.ss_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.ss_result_text.SetFont(result_font)
        self.ss_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ss_result_text.Wrap(600)
        
        result_sizer.Add(self.ss_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_social_security(self, event):
        """计算社保"""
        try:
            base = float(self.ss_base.GetValue())
            calc_type = self.ss_calc_type.GetSelection()  # 0=缴费, 1=退休金
            years = int(self.ss_years.GetValue())
            city_idx = self.ss_city.GetSelection()
            
            if base <= 0:
                raise ValueError("缴费基数必须大于0")
            
            # 五险一金缴费比例（示例：北京标准，实际比例可能因城市而异）
            # 养老保险：单位16%，个人8%
            # 医疗保险：单位10%，个人2%
            # 失业保险：单位0.8%，个人0.2%
            # 工伤保险：单位0.5%，个人0%
            # 生育保险：单位0.8%，个人0%
            # 住房公积金：单位12%，个人12%
            
            if calc_type == 0:
                # 五险一金缴费计算
                pension_unit = base * 0.16
                pension_personal = base * 0.08
                medical_unit = base * 0.10
                medical_personal = base * 0.02
                unemployment_unit = base * 0.008
                unemployment_personal = base * 0.002
                work_injury_unit = base * 0.005
                maternity_unit = base * 0.008
                housing_unit = base * 0.12
                housing_personal = base * 0.12
                
                total_unit = pension_unit + medical_unit + unemployment_unit + work_injury_unit + maternity_unit + housing_unit
                total_personal = pension_personal + medical_personal + unemployment_personal + housing_personal
                total_payment = total_unit + total_personal
                
                result = f"""五险一金缴费计算结果：

缴费基数：{base:.2f} 元/月

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【单位缴费】：
养老保险：{pension_unit:.2f} 元（16%）
医疗保险：{medical_unit:.2f} 元（10%）
失业保险：{unemployment_unit:.2f} 元（0.8%）
工伤保险：{work_injury_unit:.2f} 元（0.5%）
生育保险：{maternity_unit:.2f} 元（0.8%）
住房公积金：{housing_unit:.2f} 元（12%）

单位合计：{total_unit:.2f} 元/月

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【个人缴费】：
养老保险：{pension_personal:.2f} 元（8%）
医疗保险：{medical_personal:.2f} 元（2%）
失业保险：{unemployment_personal:.2f} 元（0.2%）
住房公积金：{housing_personal:.2f} 元（12%）

个人合计：{total_personal:.2f} 元/月

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总计缴费：{total_payment:.2f} 元/月
年度缴费：{total_payment * 12:.2f} 元

个人到手工资：{base - total_personal:.2f} 元/月

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 以上比例仅供参考，实际比例因城市而异
• 缴费基数有上下限（通常为当地平均工资的60%-300%）
• 建议咨询当地社保部门获取准确比例
"""
            else:
                # 退休金预估（简化计算）
                # 基础养老金 = (全省上年度在岗职工月平均工资 + 本人指数化月平均缴费工资) / 2 × 缴费年限 × 1%
                # 个人账户养老金 = 个人账户储存额 / 计发月数
                
                avg_salary = base * 1.2  # 假设平均工资为基数的1.2倍
                indexed_salary = base
                
                basic_pension = (avg_salary + indexed_salary) / 2 * years * 0.01
                
                # 个人账户储存额（简化：假设按8%缴费，年化收益率3%）
                personal_account = base * 0.08 * 12 * years * (1 + 0.03) ** years
                # 计发月数（60岁退休按139个月）
                months = 139
                personal_pension = personal_account / months
                
                total_pension = basic_pension + personal_pension
                
                result = f"""退休金预估结果：

缴费基数：{base:.2f} 元/月
缴费年限：{years} 年
退休年龄：60岁

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【基础养老金】：
基础养老金 = (平均工资 + 指数化工资) / 2 × 缴费年限 × 1%
           = ({avg_salary:.2f} + {indexed_salary:.2f}) / 2 × {years} × 1%
           = {basic_pension:.2f} 元/月

【个人账户养老金】：
个人账户储存额：{personal_account:.2f} 元
计发月数：{months} 个月
个人账户养老金 = {personal_account:.2f} / {months}
               = {personal_pension:.2f} 元/月

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

预估月退休金：{total_pension:.2f} 元/月
预估年退休金：{total_pension * 12:.2f} 元/年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 此计算为简化估算，实际退休金受多种因素影响
• 实际退休金计算需考虑：
  - 当地平均工资水平
  - 个人缴费指数
  - 实际退休年龄
  - 政策调整等因素
• 建议咨询当地社保部门获取准确信息
"""
            
            self.ss_result_text.SetLabel(result)
            self.ss_result_text.Wrap(600)
            result_scroll = self.ss_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_housing_fund_calculator_panel(self):
        """创建公积金计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="🏦 公积金计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 计算类型选择
        calc_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calc_type_label = wx.StaticText(input_panel, label="计算类型：")
        calc_type_label.SetMinSize((150, -1))
        self.hf_calc_type = wx.RadioBox(
            input_panel,
            choices=["缴费计算", "贷款计算"],
            majorDimension=2,
            style=wx.RA_HORIZONTAL
        )
        calc_type_sizer.Add(calc_type_label, 0, wx.ALL, 5)
        calc_type_sizer.Add(self.hf_calc_type, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(calc_type_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 缴费基数
        base_sizer = wx.BoxSizer(wx.HORIZONTAL)
        base_label = wx.StaticText(input_panel, label="缴费基数（元）：")
        base_label.SetMinSize((150, -1))
        self.hf_base = wx.TextCtrl(input_panel, value="10000")
        base_sizer.Add(base_label, 0, wx.ALL, 5)
        base_sizer.Add(self.hf_base, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(base_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 缴费比例
        rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rate_label = wx.StaticText(input_panel, label="缴费比例（%）：")
        rate_label.SetMinSize((150, -1))
        self.hf_rate = wx.TextCtrl(input_panel, value="12")
        rate_sizer.Add(rate_label, 0, wx.ALL, 5)
        rate_sizer.Add(self.hf_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款金额（用于贷款计算）
        loan_amount_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_amount_label = wx.StaticText(input_panel, label="贷款金额（万元）：")
        loan_amount_label.SetMinSize((150, -1))
        self.hf_loan_amount = wx.TextCtrl(input_panel, value="100")
        loan_amount_sizer.Add(loan_amount_label, 0, wx.ALL, 5)
        loan_amount_sizer.Add(self.hf_loan_amount, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_amount_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款期限
        loan_term_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_term_label = wx.StaticText(input_panel, label="贷款期限（年）：")
        loan_term_label.SetMinSize((150, -1))
        self.hf_loan_term = wx.TextCtrl(input_panel, value="30")
        loan_term_sizer.Add(loan_term_label, 0, wx.ALL, 5)
        loan_term_sizer.Add(self.hf_loan_term, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_term_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 贷款利率
        loan_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loan_rate_label = wx.StaticText(input_panel, label="贷款利率（%）：")
        loan_rate_label.SetMinSize((150, -1))
        self.hf_loan_rate = wx.TextCtrl(input_panel, value="3.25")
        loan_rate_sizer.Add(loan_rate_label, 0, wx.ALL, 5)
        loan_rate_sizer.Add(self.hf_loan_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(loan_rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_housing_fund)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.hf_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.hf_result_text.SetFont(result_font)
        self.hf_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.hf_result_text.Wrap(600)
        
        result_sizer.Add(self.hf_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_housing_fund(self, event):
        """计算公积金"""
        try:
            calc_type = self.hf_calc_type.GetSelection()  # 0=缴费, 1=贷款
            base = float(self.hf_base.GetValue())
            rate = float(self.hf_rate.GetValue()) / 100
            
            if calc_type == 0:
                # 缴费计算
                if base <= 0 or rate <= 0:
                    raise ValueError("参数必须大于0")
                
                unit_payment = base * rate
                personal_payment = base * rate
                total_payment = unit_payment + personal_payment
                
                result = f"""公积金缴费计算结果：

缴费基数：{base:.2f} 元/月
缴费比例：{rate*100:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

单位缴费：{unit_payment:.2f} 元/月
个人缴费：{personal_payment:.2f} 元/月

合计缴费：{total_payment:.2f} 元/月
年度缴费：{total_payment * 12:.2f} 元/年

个人账户余额：{total_payment:.2f} 元/月
年度账户余额：{total_payment * 12:.2f} 元/年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 公积金缴费比例通常为5%-12%，由单位和个人各承担50%
• 缴费基数有上下限，需咨询当地公积金管理中心
• 公积金可用于购房、租房、装修等用途
"""
            else:
                # 贷款计算
                loan_amount = float(self.hf_loan_amount.GetValue()) * 10000
                loan_term_years = int(self.hf_loan_term.GetValue())
                annual_rate = float(self.hf_loan_rate.GetValue()) / 100
                
                if loan_amount <= 0 or loan_term_years <= 0 or annual_rate <= 0:
                    raise ValueError("参数必须大于0")
                
                monthly_rate = annual_rate / 12
                total_months = loan_term_years * 12
                
                # 等额本息计算
                if monthly_rate == 0:
                    monthly_payment = loan_amount / total_months
                else:
                    monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** total_months / \
                                    ((1 + monthly_rate) ** total_months - 1)
                
                total_payment = monthly_payment * total_months
                total_interest = total_payment - loan_amount
                
                # 计算贷款额度（简化：通常为账户余额的10-15倍）
                account_balance = total_payment * 12 * loan_term_years  # 假设按当前缴费计算
                max_loan = account_balance * 12  # 简化计算
                
                result = f"""公积金贷款计算结果：

贷款金额：{loan_amount/10000:.2f} 万元
贷款期限：{loan_term_years} 年（{total_months} 个月）
贷款利率：{annual_rate*100:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

月供金额：{monthly_payment:.2f} 元

总还款额：{total_payment:.2f} 元
总利息：{total_interest:.2f} 元

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

贷款额度参考：
根据当前缴费情况，预估可贷额度约：{max_loan/10000:.2f} 万元

（实际贷款额度受以下因素影响：
• 账户余额
• 还款能力
• 房屋价值
• 当地政策规定）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

还款明细（前12个月）：
"""
                
                remaining_principal = loan_amount
                for month in range(1, min(13, total_months + 1)):
                    interest_payment = remaining_principal * monthly_rate
                    principal_payment = monthly_payment - interest_payment
                    remaining_principal -= principal_payment
                    
                    result += f"\n第{month}期："
                    result += f"月供 {monthly_payment:.2f} 元 "
                    result += f"（本金 {principal_payment:.2f} 元 + 利息 {interest_payment:.2f} 元）"
                    result += f" 剩余本金 {remaining_principal:.2f} 元"
                
                if total_months > 12:
                    result += f"\n\n...（共{total_months}期）"
            
            self.hf_result_text.SetLabel(result)
            self.hf_result_text.Wrap(600)
            result_scroll = self.hf_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_investment_calculator_panel(self):
        """创建投资计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_panel, label="📈 投资计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 10)
        
        # 计算类型选择
        calc_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calc_type_label = wx.StaticText(input_panel, label="计算类型：")
        calc_type_label.SetMinSize((150, -1))
        self.inv_calc_type = wx.RadioBox(
            input_panel,
            choices=["复利计算", "定投计算", "年化收益"],
            majorDimension=3,
            style=wx.RA_HORIZONTAL
        )
        calc_type_sizer.Add(calc_type_label, 0, wx.ALL, 5)
        calc_type_sizer.Add(self.inv_calc_type, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(calc_type_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 本金/初始投资
        principal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        principal_label = wx.StaticText(input_panel, label="本金（元）：")
        principal_label.SetMinSize((150, -1))
        self.inv_principal = wx.TextCtrl(input_panel, value="100000")
        principal_sizer.Add(principal_label, 0, wx.ALL, 5)
        principal_sizer.Add(self.inv_principal, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(principal_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 年化收益率
        rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rate_label = wx.StaticText(input_panel, label="年化收益率（%）：")
        rate_label.SetMinSize((150, -1))
        self.inv_rate = wx.TextCtrl(input_panel, value="8")
        rate_sizer.Add(rate_label, 0, wx.ALL, 5)
        rate_sizer.Add(self.inv_rate, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(rate_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 投资期限
        years_sizer = wx.BoxSizer(wx.HORIZONTAL)
        years_label = wx.StaticText(input_panel, label="投资期限（年）：")
        years_label.SetMinSize((150, -1))
        self.inv_years = wx.TextCtrl(input_panel, value="10")
        years_sizer.Add(years_label, 0, wx.ALL, 5)
        years_sizer.Add(self.inv_years, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(years_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 每月定投金额（用于定投计算）
        monthly_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monthly_label = wx.StaticText(input_panel, label="每月定投（元）：")
        monthly_label.SetMinSize((150, -1))
        self.inv_monthly = wx.TextCtrl(input_panel, value="5000")
        monthly_sizer.Add(monthly_label, 0, wx.ALL, 5)
        monthly_sizer.Add(self.inv_monthly, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(monthly_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 最终金额（用于年化收益计算）
        final_sizer = wx.BoxSizer(wx.HORIZONTAL)
        final_label = wx.StaticText(input_panel, label="最终金额（元）：")
        final_label.SetMinSize((150, -1))
        self.inv_final = wx.TextCtrl(input_panel, value="200000")
        final_sizer.Add(final_label, 0, wx.ALL, 5)
        final_sizer.Add(self.inv_final, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(final_sizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # 计算按钮
        calc_btn = wx.Button(input_panel, label="计算", size=(-1, 40))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_investment)
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 10)
        
        input_panel.SetSizer(input_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(250, 252, 255))
        result_scroll.SetupScrolling()
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.inv_result_text = wx.StaticText(result_scroll, label="请输入参数并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.inv_result_text.SetFont(result_font)
        self.inv_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.inv_result_text.Wrap(600)
        
        result_sizer.Add(self.inv_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_scroll.SetSizer(result_sizer)
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 5)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 5)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_calculate_investment(self, event):
        """计算投资"""
        try:
            calc_type = self.inv_calc_type.GetSelection()  # 0=复利, 1=定投, 2=年化收益
            
            if calc_type == 0:
                # 复利计算
                principal = float(self.inv_principal.GetValue())
                annual_rate = float(self.inv_rate.GetValue()) / 100
                years = float(self.inv_years.GetValue())
                
                if principal <= 0 or annual_rate <= 0 or years <= 0:
                    raise ValueError("参数必须大于0")
                
                # 复利公式：FV = PV × (1 + r)^n
                final_value = principal * (1 + annual_rate) ** years
                total_interest = final_value - principal
                total_return_rate = (final_value / principal - 1) * 100
                
                result = f"""复利计算结果：

初始本金：{principal:.2f} 元
年化收益率：{annual_rate*100:.2f}%
投资期限：{years:.0f} 年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

最终金额：{final_value:.2f} 元
总收益：{total_interest:.2f} 元
总收益率：{total_return_rate:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

年度收益明细（前5年）：
"""
                
                for year in range(1, min(6, int(years) + 1)):
                    year_value = principal * (1 + annual_rate) ** year
                    year_interest = year_value - principal
                    result += f"\n第{year}年：本金 {principal:.2f} 元 → 本息 {year_value:.2f} 元，收益 {year_interest:.2f} 元"
                
                if years > 5:
                    result += f"\n\n...（共{years:.0f}年）"
                
            elif calc_type == 1:
                # 定投计算
                monthly = float(self.inv_monthly.GetValue())
                annual_rate = float(self.inv_rate.GetValue()) / 100
                years = float(self.inv_years.GetValue())
                
                if monthly <= 0 or annual_rate <= 0 or years <= 0:
                    raise ValueError("参数必须大于0")
                
                # 定投公式：FV = PMT × [((1 + r)^n - 1) / r] × (1 + r)
                # 其中 r 是月利率，n 是总月数
                monthly_rate = annual_rate / 12
                total_months = years * 12
                
                if monthly_rate == 0:
                    final_value = monthly * total_months
                else:
                    final_value = monthly * ((1 + monthly_rate) ** total_months - 1) / monthly_rate * (1 + monthly_rate)
                
                total_invested = monthly * total_months
                total_interest = final_value - total_invested
                total_return_rate = (final_value / total_invested - 1) * 100
                
                result = f"""定投计算结果：

每月定投：{monthly:.2f} 元
年化收益率：{annual_rate*100:.2f}%
投资期限：{years:.0f} 年（{total_months:.0f} 个月）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总投入：{total_invested:.2f} 元
最终金额：{final_value:.2f} 元
总收益：{total_interest:.2f} 元
总收益率：{total_return_rate:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

年度收益明细（前5年）：
"""
                
                cumulative_invested = 0
                for year in range(1, min(6, int(years) + 1)):
                    cumulative_invested += monthly * 12
                    year_value = monthly * ((1 + monthly_rate) ** (year * 12) - 1) / monthly_rate * (1 + monthly_rate)
                    year_interest = year_value - cumulative_invested
                    result += f"\n第{year}年：投入 {monthly * 12:.2f} 元，累计投入 {cumulative_invested:.2f} 元，"
                    result += f"本息 {year_value:.2f} 元，收益 {year_interest:.2f} 元"
                
                if years > 5:
                    result += f"\n\n...（共{years:.0f}年）"
                    
            else:
                # 年化收益率计算
                principal = float(self.inv_principal.GetValue())
                final_value = float(self.inv_final.GetValue())
                years = float(self.inv_years.GetValue())
                
                if principal <= 0 or final_value <= 0 or years <= 0:
                    raise ValueError("参数必须大于0")
                
                # 年化收益率 = (最终金额 / 初始金额)^(1/年数) - 1
                if final_value >= principal:
                    annual_return_rate = (final_value / principal) ** (1 / years) - 1
                    total_return_rate = (final_value / principal - 1) * 100
                    total_interest = final_value - principal
                else:
                    annual_return_rate = -((principal / final_value) ** (1 / years) - 1)
                    total_return_rate = (final_value / principal - 1) * 100
                    total_interest = final_value - principal
                
                result = f"""年化收益率计算结果：

初始本金：{principal:.2f} 元
最终金额：{final_value:.2f} 元
投资期限：{years:.0f} 年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总收益：{total_interest:.2f} 元
总收益率：{total_return_rate:.2f}%
年化收益率：{annual_return_rate*100:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 年化收益率 = (最终金额/初始金额)^(1/年数) - 1
• 此计算为简化版本，未考虑复利频率等因素
• 实际投资收益可能因市场波动而有所不同
"""
            
            self.inv_result_text.SetLabel(result)
            self.inv_result_text.Wrap(600)
            result_scroll = self.inv_result_text.GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def create_ecommerce_smart_input_panel(self, parent):
        """创建电商智能识别输入面板"""
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        container.SetMinSize((-1, 140))
        
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域
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
        
        # 提示文本
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
        
        self.ecommerce_smart_input = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
            size=(-1, 70)
        )
        input_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.ecommerce_smart_input.SetFont(input_font)
        self.ecommerce_smart_input.SetBackgroundColour(wx.Colour(250, 252, 255))
        self.ecommerce_smart_input.SetHint("💬 在此输入自然语言描述，系统将自动识别并填充数据...")
        
        parse_btn = wx.Button(panel, label="✨ 智能识别", size=(110, 70))
        parse_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        parse_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        parse_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        parse_btn.SetFont(parse_font)
        parse_btn.Bind(wx.EVT_BUTTON, self.on_ecommerce_parse_clicked)
        parse_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: parse_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        parse_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: parse_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        
        input_sizer.Add(self.ecommerce_smart_input, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        input_sizer.Add(parse_btn, 0, wx.RIGHT | wx.BOTTOM | wx.ALIGN_BOTTOM, 10)
        
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        
        panel.SetSizer(sizer)
        container_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 8)
        container.SetSizer(container_sizer)
        
        return container
    
    def create_ecommerce_input_panel(self, parent):
        """创建电商输入参数面板"""
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域
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
        
        # 创建网格布局
        grid_sizer = wx.FlexGridSizer(rows=9, cols=2, vgap=12, hgap=20)
        grid_sizer.AddGrowableCol(1, 1)
        
        label_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        
        # 售价
        self.ecommerce_price_label = wx.StaticText(panel, label="💰 售价（元）:")
        self.ecommerce_price_label.SetFont(label_font)
        self.ecommerce_price_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_price_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10000, 
                                           inc=1, size=(200, 28))
        self.ecommerce_price_ctrl.SetDigits(2)
        self.ecommerce_price_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_price_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_price_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_price_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_price_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 成本
        self.ecommerce_cost_label = wx.StaticText(panel, label="💵 成本（元）:")
        self.ecommerce_cost_label.SetFont(label_font)
        self.ecommerce_cost_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_cost_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10000,
                                          inc=1, size=(200, 28))
        self.ecommerce_cost_ctrl.SetDigits(2)
        self.ecommerce_cost_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_cost_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_cost_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_cost_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_cost_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # ROI
        self.ecommerce_roi_label = wx.StaticText(panel, label="📊 ROI（投入产出比）:")
        self.ecommerce_roi_label.SetFont(label_font)
        self.ecommerce_roi_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_roi_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0.1, max=100,
                                         inc=0.1, size=(200, 28))
        self.ecommerce_roi_ctrl.SetDigits(2)
        self.ecommerce_roi_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_roi_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_roi_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_roi_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_roi_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 退货率
        self.ecommerce_return_rate_label = wx.StaticText(panel, label="🔄 退货率（%）:")
        self.ecommerce_return_rate_label.SetFont(label_font)
        self.ecommerce_return_rate_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_return_rate_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                  inc=0.1, size=(200, 28))
        self.ecommerce_return_rate_ctrl.SetDigits(1)
        self.ecommerce_return_rate_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_return_rate_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_return_rate_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_return_rate_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_return_rate_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 平台扣点
        self.ecommerce_platform_fee_label = wx.StaticText(panel, label="💳 平台扣点（%）:")
        self.ecommerce_platform_fee_label.SetFont(label_font)
        self.ecommerce_platform_fee_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_platform_fee_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=10,
                                                   inc=0.01, size=(200, 28))
        self.ecommerce_platform_fee_ctrl.SetDigits(2)
        self.ecommerce_platform_fee_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_platform_fee_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_platform_fee_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_platform_fee_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_platform_fee_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 运费险
        self.ecommerce_shipping_insurance_label = wx.StaticText(panel, label="📦 运费险（元/单）:")
        self.ecommerce_shipping_insurance_label.SetFont(label_font)
        self.ecommerce_shipping_insurance_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_shipping_insurance_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                         inc=0.01, size=(200, 28))
        self.ecommerce_shipping_insurance_ctrl.SetDigits(2)
        self.ecommerce_shipping_insurance_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_shipping_insurance_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_shipping_insurance_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_shipping_insurance_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_shipping_insurance_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 退货运费
        self.ecommerce_return_shipping_label = wx.StaticText(panel, label="↩️ 退货运费（元/单）:")
        self.ecommerce_return_shipping_label.SetFont(label_font)
        self.ecommerce_return_shipping_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_return_shipping_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100,
                                                      inc=0.1, size=(200, 28))
        self.ecommerce_return_shipping_ctrl.SetDigits(2)
        self.ecommerce_return_shipping_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_return_shipping_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_return_shipping_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_return_shipping_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_return_shipping_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 其他成本
        self.ecommerce_other_cost_label = wx.StaticText(panel, label="📋 其他成本（元）:")
        self.ecommerce_other_cost_label.SetFont(label_font)
        self.ecommerce_other_cost_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_other_cost_ctrl = wx.SpinCtrlDouble(panel, value="0", min=0, max=100000,
                                                 inc=1, size=(200, 28))
        self.ecommerce_other_cost_ctrl.SetDigits(2)
        self.ecommerce_other_cost_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_other_cost_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_other_cost_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_other_cost_ctrl.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_ecommerce_value_changed)
        self.ecommerce_other_cost_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        # 订单数
        self.ecommerce_orders_label = wx.StaticText(panel, label="📦 订单数（单）:")
        self.ecommerce_orders_label.SetFont(label_font)
        self.ecommerce_orders_label.SetForegroundColour(wx.Colour(48, 49, 51))
        self.ecommerce_orders_ctrl = wx.SpinCtrl(panel, value="0", min=0, max=100000,
                                       size=(200, 28))
        self.ecommerce_orders_ctrl.SetBackgroundColour(wx.Colour(250, 252, 255))
        grid_sizer.Add(self.ecommerce_orders_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)
        grid_sizer.Add(self.ecommerce_orders_ctrl, 0, wx.EXPAND | wx.RIGHT, 15)
        self.ecommerce_orders_ctrl.Bind(wx.EVT_SPINCTRL, self.on_ecommerce_value_changed)
        self.ecommerce_orders_ctrl.Bind(wx.EVT_TEXT, self.on_ecommerce_value_changed)
        
        sizer.Add(grid_sizer, 0, wx.ALL, 15)
        sizer.AddSpacer(10)
        
        # 清空按钮
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
        clear_btn.Bind(wx.EVT_BUTTON, self.on_ecommerce_clear_all)
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
    
    def create_ecommerce_result_panel(self, parent):
        """创建电商结果显示面板"""
        container = wx.Panel(parent)
        container.SetBackgroundColour(wx.Colour(245, 247, 250))
        
        panel = wx.Panel(container)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        container_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 标题区域
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
        
        # 结果显示区域
        self.ecommerce_result_text = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
            size=(-1, 400)
        )
        result_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.ecommerce_result_text.SetFont(result_font)
        self.ecommerce_result_text.SetBackgroundColour(wx.Colour(250, 252, 255))
        
        sizer.Add(self.ecommerce_result_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 15)
        sizer.AddSpacer(10)
        
        panel.SetSizer(sizer)
        container_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 8)
        container.SetSizer(container_sizer)
        
        return container
    
    def ecommerce_chinese_to_number(self, chinese_str):
        """将中文数字转换为阿拉伯数字（电商计算器专用）"""
        if not chinese_str:
            return None
        
        try:
            return float(chinese_str)
        except:
            pass
        
        chinese_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5,
            '陆': 6, '柒': 7, '捌': 8, '玖': 9, '拾': 10
        }
        
        if '点' in chinese_str or '.' in chinese_str:
            parts = re.split(r'[点.]', chinese_str)
            if len(parts) == 2:
                integer_part = self._ecommerce_chinese_to_integer(parts[0], chinese_map)
                decimal_str = parts[1]
                decimal_value = 0
                decimal_multiplier = 0.1
                for char in decimal_str:
                    if char in chinese_map:
                        decimal_value += chinese_map[char] * decimal_multiplier
                        decimal_multiplier *= 0.1
                    elif char.isdigit():
                        decimal_value += int(char) * decimal_multiplier
                        decimal_multiplier *= 0.1
                
                if integer_part is not None:
                    return float(integer_part) + decimal_value
        
        result = self._ecommerce_chinese_to_integer(chinese_str, chinese_map)
        return float(result) if result is not None else None
    
    def _ecommerce_chinese_to_integer(self, chinese_str, chinese_map):
        """将中文整数转换为阿拉伯数字"""
        if not chinese_str:
            return None
        
        if chinese_str.isdigit():
            return int(chinese_str)
        
        if chinese_str == '十':
            return 10
        if chinese_str.startswith('十') and len(chinese_str) > 1:
            rest = chinese_str[1:]
            if rest in chinese_map:
                return 10 + chinese_map[rest]
        
        if len(chinese_str) >= 2 and chinese_str[-1] == '十':
            if chinese_str[0] in chinese_map:
                return chinese_map[chinese_str[0]] * 10
        elif len(chinese_str) >= 3 and '十' in chinese_str:
            parts = chinese_str.split('十')
            if len(parts) == 2:
                tens = self._ecommerce_chinese_to_integer(parts[0], chinese_map) if parts[0] else 1
                ones = self._ecommerce_chinese_to_integer(parts[1], chinese_map) if parts[1] else 0
                if tens is not None and ones is not None:
                    return tens * 10 + ones
        
        if '百' in chinese_str:
            parts = chinese_str.split('百')
            if len(parts) == 2:
                hundreds = self._ecommerce_chinese_to_integer(parts[0], chinese_map) if parts[0] else 1
                rest = self._ecommerce_chinese_to_integer(parts[1], chinese_map) if parts[1] else 0
                if hundreds is not None and rest is not None:
                    return hundreds * 100 + rest
        
        if chinese_str in chinese_map:
            return chinese_map[chinese_str]
        
        return None
    
    def ecommerce_parse_number_from_text(self, text, patterns):
        """从文本中提取数字（支持中文和阿拉伯数字）"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1)
                    value = self.ecommerce_chinese_to_number(value_str)
                    if value is not None:
                        return value
                except:
                    pass
        return None
    
    def on_ecommerce_parse_clicked(self, event):
        """电商智能识别按钮点击事件"""
        text = self.ecommerce_smart_input.GetValue()
        if text:
            self.ecommerce_parse_smart_input(text)
            self.ecommerce_calculate()
    
    def ecommerce_parse_smart_input(self, text):
        """解析智能输入文本"""
        if not text:
            return
        
        text = text.strip()
        
        # 售价
        price_patterns = [
            r'售价\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'价格\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'单价\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, price_patterns)
        if value is not None:
            try:
                self.ecommerce_price_ctrl.SetValue(value)
            except:
                pass
        
        # 成本
        cost_patterns = [
            r'成本\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, cost_patterns)
        if value is not None:
            try:
                self.ecommerce_cost_ctrl.SetValue(value)
            except:
                pass
        
        # ROI
        roi_patterns = [
            r'ROI\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'roi\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'投入产出比\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, roi_patterns)
        if value is not None:
            try:
                self.ecommerce_roi_ctrl.SetValue(value)
            except:
                pass
        
        # 退货率
        return_rate_parsed = False
        
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
                    value = self.ecommerce_chinese_to_number(value_str)
                    if value is not None:
                        self.ecommerce_return_rate_ctrl.SetValue(value)
                        return_rate_parsed = True
                        break
                except:
                    pass
        
        if not return_rate_parsed:
            return_rate_patterns = [
                r'退货率\s*[:：算]?\s*([零一二三四五六七八九十百\d\.点]+)\s*%?',
                r'退货\s*率\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)\s*%?',
            ]
            value = self.ecommerce_parse_number_from_text(text, return_rate_patterns)
            if value is not None:
                try:
                    self.ecommerce_return_rate_ctrl.SetValue(value)
                    return_rate_parsed = True
                except:
                    pass
        
        # 平台扣点
        platform_fee_parsed = False
        
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
                    self.ecommerce_platform_fee_ctrl.SetValue(value)
                    platform_fee_parsed = True
                except:
                    pass
        
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
                        self.ecommerce_platform_fee_ctrl.SetValue(value)
                        platform_fee_parsed = True
                    except:
                        pass
        
        if not platform_fee_parsed:
            permille_pattern = re.search(r'平台扣点\s*[:：]?\s*(\d+\.?\d*)\s*[‰‰]', text, re.IGNORECASE)
            if permille_pattern:
                try:
                    value = float(permille_pattern.group(1)) / 10.0
                    self.ecommerce_platform_fee_ctrl.SetValue(value)
                    platform_fee_parsed = True
                except:
                    pass
        
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
                        self.ecommerce_platform_fee_ctrl.SetValue(value)
                        platform_fee_parsed = True
                    except:
                        pass
                    break
        
        # 运费险
        shipping_insurance_patterns = [
            r'运费险\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'运费险\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, shipping_insurance_patterns)
        if value is not None:
            try:
                self.ecommerce_shipping_insurance_ctrl.SetValue(value)
            except:
                pass
        
        # 退货运费
        return_shipping_patterns = [
            r'退货运费\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'退货.*运费\s*[:：]?\s*每单\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
            r'退货.*扣\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)\s*元',
            r'退货.*运费\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, return_shipping_patterns)
        if value is not None:
            try:
                self.ecommerce_return_shipping_ctrl.SetValue(value)
            except:
                pass
        
        # 其他成本
        other_cost_patterns = [
            r'其他成本\s*[:：]?\s*([零一二三四五六七八九十百\d\.点]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, other_cost_patterns)
        if value is not None:
            try:
                self.ecommerce_other_cost_ctrl.SetValue(value)
            except:
                pass
        
        # 订单数
        orders_patterns = [
            r'([零一二三四五六七八九十百\d]+)\s*单',
            r'订单数\s*[:：]?\s*([零一二三四五六七八九十百\d]+)',
            r'订单\s*[:：]?\s*([零一二三四五六七八九十百\d]+)',
        ]
        value = self.ecommerce_parse_number_from_text(text, orders_patterns)
        if value is not None:
            try:
                self.ecommerce_orders_ctrl.SetValue(int(value))
            except:
                pass
    
    def on_ecommerce_value_changed(self, event):
        """电商计算器值变化事件"""
        self.ecommerce_calculate()
    
    def on_ecommerce_clear_all(self, event):
        """清空所有电商输入框"""
        self.ecommerce_price_ctrl.SetValue(0)
        self.ecommerce_cost_ctrl.SetValue(0)
        self.ecommerce_roi_ctrl.SetValue(0)
        self.ecommerce_return_rate_ctrl.SetValue(0)
        self.ecommerce_platform_fee_ctrl.SetValue(0)
        self.ecommerce_shipping_insurance_ctrl.SetValue(0)
        self.ecommerce_return_shipping_ctrl.SetValue(0)
        self.ecommerce_other_cost_ctrl.SetValue(0)
        self.ecommerce_orders_ctrl.SetValue(0)
        self.ecommerce_smart_input.Clear()
        self.ecommerce_calculate()
    
    def ecommerce_calculate(self):
        """执行电商利润计算"""
        try:
            price = self.ecommerce_price_ctrl.GetValue()
            cost = self.ecommerce_cost_ctrl.GetValue()
            roi = self.ecommerce_roi_ctrl.GetValue()
            return_rate = self.ecommerce_return_rate_ctrl.GetValue() / 100.0
            platform_fee_rate = self.ecommerce_platform_fee_ctrl.GetValue() / 100.0
            shipping_insurance = self.ecommerce_shipping_insurance_ctrl.GetValue()
            return_shipping_cost = self.ecommerce_return_shipping_ctrl.GetValue()
            other_cost = self.ecommerce_other_cost_ctrl.GetValue()
            total_orders = self.ecommerce_orders_ctrl.GetValue()
            
            successful_orders = int(total_orders * (1 - return_rate))
            returned_orders = total_orders - successful_orders
            
            revenue = successful_orders * price
            
            ad_cost = revenue / roi if roi > 0 else 0
            product_cost = total_orders * cost
            platform_fee = successful_orders * price * platform_fee_rate
            shipping_insurance_cost = total_orders * shipping_insurance
            return_shipping_cost_total = returned_orders * return_shipping_cost
            
            total_cost = ad_cost + product_cost + platform_fee + shipping_insurance_cost + return_shipping_cost_total + other_cost
            
            profit = revenue - total_cost
            profit_margin = (profit / revenue * 100) if revenue > 0 else 0
            
            if successful_orders > 0 and roi > 0:
                variable_cost_rate = (1 / roi) + platform_fee_rate
                fixed_costs = product_cost + shipping_insurance_cost + return_shipping_cost_total + other_cost
                break_even_price = fixed_costs / (successful_orders * (1 - variable_cost_rate))
            else:
                break_even_price = 0
            
            self.ecommerce_display_results(
                price, cost, roi, return_rate, platform_fee_rate,
                shipping_insurance, return_shipping_cost, other_cost, total_orders,
                successful_orders, returned_orders,
                revenue, ad_cost, product_cost, platform_fee,
                shipping_insurance_cost, return_shipping_cost_total,
                total_cost, profit, profit_margin, break_even_price
            )
            
        except Exception as e:
            self.ecommerce_result_text.Clear()
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(255, 0, 0))
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText(f"计算出错: {str(e)}\n")
    
    def ecommerce_display_results(self, price, cost, roi, return_rate, platform_fee_rate,
                       shipping_insurance, return_shipping_cost, other_cost, total_orders,
                       successful_orders, returned_orders,
                       revenue, ad_cost, product_cost, platform_fee,
                       shipping_insurance_cost, return_shipping_cost_total,
                       total_cost, profit, profit_margin, break_even_price):
        """显示电商计算结果"""
        self.ecommerce_result_text.Clear()
        
        bold_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        normal_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        
        # 标题
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(20, 180, 168))
        attr.SetFont(bold_font)
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText("利润分析结果\n")
        self.ecommerce_result_text.AppendText("─" * 50 + "\n")
        
        # 订单分析
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(0, 0, 0))
        attr.SetFont(normal_font)
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText("【订单分析】 ")
        self.ecommerce_result_text.AppendText(f"总订单数: {total_orders}单 | ")
        self.ecommerce_result_text.AppendText(f"成功: {successful_orders}单({100*(1-return_rate):.1f}%) | ")
        self.ecommerce_result_text.AppendText(f"退货: {returned_orders}单({return_rate*100:.1f}%)\n")
        
        # 收入
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(0, 102, 204))
        attr.SetFont(normal_font)
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText("【收入】 ")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText(f"{successful_orders}单 × {price:.2f}元 = {revenue:.2f}元\n")
        
        # 成本明细
        attr = wx.TextAttr()
        attr.SetTextColour(wx.Colour(226, 96, 95))
        attr.SetFont(normal_font)
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText("【成本明细】\n")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText(f"  广告: {ad_cost:.2f}元 | ")
        self.ecommerce_result_text.AppendText(f"产品成本: {product_cost:.2f}元 | ")
        self.ecommerce_result_text.AppendText(f"平台扣点: {platform_fee:.2f}元 | ")
        self.ecommerce_result_text.AppendText(f"运费险: {shipping_insurance_cost:.2f}元 | ")
        self.ecommerce_result_text.AppendText(f"退货运费: {return_shipping_cost_total:.2f}元")
        if other_cost > 0:
            self.ecommerce_result_text.AppendText(f" | 其他成本: {other_cost:.2f}元")
        self.ecommerce_result_text.AppendText(f"\n  总成本: {total_cost:.2f}元\n")
        
        # 利润分析
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
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText("【利润分析】 ")
        attr.SetTextColour(wx.Colour(0, 0, 0))
        attr.SetFont(normal_font)
        self.ecommerce_result_text.SetDefaultStyle(attr)
        self.ecommerce_result_text.AppendText(f"收入: {revenue:.2f}元 | 成本: {total_cost:.2f}元 | ")
        
        if profit > 0:
            attr.SetTextColour(wx.Colour(103, 194, 58))
            attr.SetFont(profit_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText(f"利润: +{profit:.2f}元 | 利润率: +{profit_margin:.2f}%\n")
            self.ecommerce_result_text.AppendText(f"  ✓ 盈利: {profit:.2f}元\n")
        elif profit < 0:
            attr.SetTextColour(wx.Colour(255, 0, 0))
            attr.SetFont(profit_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText(f"利润: {profit:.2f}元 | 利润率: {profit_margin:.2f}%\n")
            self.ecommerce_result_text.AppendText(f"  ✗ 亏损: {abs(profit):.2f}元\n")
        else:
            attr.SetTextColour(wx.Colour(144, 144, 153))
            attr.SetFont(profit_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText(f"利润: 0.00元 | 利润率: 0.00%\n")
            self.ecommerce_result_text.AppendText(f"  ○ 盈亏平衡\n")
        
        # 盈亏平衡点
        if break_even_price > 0:
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(0, 102, 204))
            attr.SetFont(normal_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText("【盈亏平衡点】 ")
            attr.SetTextColour(wx.Colour(0, 0, 0))
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText(f"当前售价: {price:.2f}元 | 平衡售价: {break_even_price:.2f}元")
            if break_even_price > price:
                self.ecommerce_result_text.AppendText(f" | 需提价: {break_even_price - price:.2f}元({((break_even_price - price) / price * 100):.2f}%)\n")
            elif break_even_price < price:
                self.ecommerce_result_text.AppendText(f" | 高于平衡点: {price - break_even_price:.2f}元\n")
            else:
                self.ecommerce_result_text.AppendText("\n")
        
        # 盈利建议
        if profit < 0:
            attr = wx.TextAttr()
            attr.SetTextColour(wx.Colour(226, 96, 95))
            attr.SetFont(profit_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            self.ecommerce_result_text.AppendText("【盈利建议】\n")
            attr.SetTextColour(wx.Colour(0, 0, 0))
            attr.SetFont(normal_font)
            self.ecommerce_result_text.SetDefaultStyle(attr)
            
            suggestions = []
            
            if break_even_price > price:
                suggestions.append({
                    'type': '售价',
                    'current': price,
                    'target': break_even_price,
                    'change': break_even_price - price,
                    'change_pct': ((break_even_price - price) / price * 100),
                    'description': f'提价至 {break_even_price:.2f}元（盈亏平衡）'
                })
            
            test_return_rates = [0.25, 0.20, 0.15, 0.10]
            for test_rate in test_return_rates:
                if test_rate < return_rate:
                    test_successful = int(total_orders * (1 - test_rate))
                    test_returned = total_orders - test_successful
                    test_revenue = test_successful * price
                    test_ad_cost = test_revenue / roi
                    test_platform_fee = test_successful * price * platform_fee_rate
                    test_fixed = total_orders * cost + total_orders * shipping_insurance + test_returned * return_shipping_cost
                    test_total_cost = test_ad_cost + test_platform_fee + test_fixed + other_cost
                    test_profit = test_revenue - test_total_cost
                    
                    if test_profit > 0:
                        test_margin = (test_profit / test_revenue * 100) if test_revenue > 0 else 0
                        suggestions.append({
                            'type': '退货率',
                            'current': return_rate * 100,
                            'target': test_rate * 100,
                            'change': (return_rate - test_rate) * 100,
                            'target_profit': test_profit,
                            'target_margin': test_margin,
                            'description': f'退货率降至 {test_rate*100:.0f}%'
                        })
                        break
            
            test_rois = [5.5, 6.0, 7.0, 8.0]
            for test_roi in test_rois:
                if test_roi > roi:
                    test_ad_cost = revenue / test_roi
                    test_total_cost = test_ad_cost + product_cost + platform_fee + shipping_insurance_cost + return_shipping_cost_total + other_cost
                    test_profit = revenue - test_total_cost
                    
                    if test_profit > 0:
                        test_margin = (test_profit / revenue * 100) if revenue > 0 else 0
                        suggestions.append({
                            'type': 'ROI',
                            'current': roi,
                            'target': test_roi,
                            'change': test_roi - roi,
                            'target_profit': test_profit,
                            'target_margin': test_margin,
                            'description': f'ROI提升至 {test_roi:.2f}'
                        })
                        break
            
            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    self.ecommerce_result_text.AppendText(f"  方案{i}: {suggestion['description']}")
                    if suggestion['type'] == '售价':
                        self.ecommerce_result_text.AppendText(f" | 当前: {suggestion['current']:.2f}元 → 目标: {suggestion['target']:.2f}元 | 提价: {suggestion['change']:.2f}元({suggestion['change_pct']:.2f}%)")
                    elif suggestion['type'] == '退货率':
                        self.ecommerce_result_text.AppendText(f" | 当前: {suggestion['current']:.1f}% → 目标: {suggestion['target']:.1f}% | 降低: {suggestion['change']:.1f}%")
                    elif suggestion['type'] == 'ROI':
                        self.ecommerce_result_text.AppendText(f" | 当前: {suggestion['current']:.2f} → 目标: {suggestion['target']:.2f} | 提升: {suggestion['change']:.2f}")
                    
                    if suggestion['target_profit'] > 0:
                        self.ecommerce_result_text.AppendText(f" | 预期利润: {suggestion['target_profit']:.2f}元")
                        if 'target_margin' in suggestion and suggestion['target_margin'] > 0:
                            self.ecommerce_result_text.AppendText(f" | 利润率: {suggestion['target_margin']:.2f}%")
                    self.ecommerce_result_text.AppendText("\n")
            else:
                self.ecommerce_result_text.AppendText("  暂无可行的盈利方案\n")
        
        self.ecommerce_result_text.ShowPosition(0)
    
    def create_bmi_calculator_panel(self):
        """创建BMI计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        input_container = wx.Panel(input_panel)
        input_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_container, label="⚖️ BMI计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 15)
        
        # 身高
        height_sizer = wx.BoxSizer(wx.HORIZONTAL)
        height_label = wx.StaticText(input_container, label="身高（cm）：")
        height_label.SetMinSize((150, -1))
        height_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.bmi_height = wx.TextCtrl(input_container, value="170")
        self.bmi_height.SetBackgroundColour(wx.Colour(250, 252, 255))
        height_sizer.Add(height_label, 0, wx.ALL, 8)
        height_sizer.Add(self.bmi_height, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(height_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 体重
        weight_sizer = wx.BoxSizer(wx.HORIZONTAL)
        weight_label = wx.StaticText(input_container, label="体重（kg）：")
        weight_label.SetMinSize((150, -1))
        weight_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.bmi_weight = wx.TextCtrl(input_container, value="70")
        self.bmi_weight.SetBackgroundColour(wx.Colour(250, 252, 255))
        weight_sizer.Add(weight_label, 0, wx.ALL, 8)
        weight_sizer.Add(self.bmi_weight, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(weight_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 计算按钮
        calc_btn = wx.Button(input_container, label="计算BMI", size=(-1, 45))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_bmi)
        calc_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        calc_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 15)
        
        input_container.SetSizer(input_sizer)
        input_container_sizer = wx.BoxSizer(wx.VERTICAL)
        input_container_sizer.Add(input_container, 1, wx.EXPAND | wx.ALL, 8)
        input_panel.SetSizer(input_container_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 8)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(245, 247, 250))
        result_scroll.SetupScrolling()
        
        result_container = wx.Panel(result_scroll)
        result_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.bmi_result_text = wx.StaticText(result_container, label="请输入身高和体重并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.bmi_result_text.SetFont(result_font)
        self.bmi_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.bmi_result_text.Wrap(600)
        
        result_sizer.Add(self.bmi_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_container.SetSizer(result_sizer)
        
        result_scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        result_scroll_sizer.Add(result_container, 1, wx.EXPAND | wx.ALL, 8)
        result_scroll.SetSizer(result_scroll_sizer)
        
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 8)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 8)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 8)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 8)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def create_unit_converter_panel(self):
        """创建单位换算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        input_container = wx.Panel(input_panel)
        input_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_container, label="🔄 单位换算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 15)
        
        # 换算类型
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_label = wx.StaticText(input_container, label="换算类型：")
        type_label.SetMinSize((150, -1))
        type_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.unit_type = wx.Choice(input_container, choices=["长度", "重量", "温度", "面积", "体积"])
        self.unit_type.SetSelection(0)
        self.unit_type.Bind(wx.EVT_CHOICE, self.on_unit_type_changed)
        type_sizer.Add(type_label, 0, wx.ALL, 8)
        type_sizer.Add(self.unit_type, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(type_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 输入值
        value_sizer = wx.BoxSizer(wx.HORIZONTAL)
        value_label = wx.StaticText(input_container, label="输入值：")
        value_label.SetMinSize((150, -1))
        value_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.unit_input_value = wx.TextCtrl(input_container, value="100")
        self.unit_input_value.SetBackgroundColour(wx.Colour(250, 252, 255))
        value_sizer.Add(value_label, 0, wx.ALL, 8)
        value_sizer.Add(self.unit_input_value, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(value_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 原单位
        from_unit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        from_unit_label = wx.StaticText(input_container, label="原单位：")
        from_unit_label.SetMinSize((150, -1))
        from_unit_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.unit_from = wx.Choice(input_container, choices=["米", "千米", "厘米", "毫米"])
        self.unit_from.SetSelection(0)
        from_unit_sizer.Add(from_unit_label, 0, wx.ALL, 8)
        from_unit_sizer.Add(self.unit_from, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(from_unit_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 目标单位
        to_unit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        to_unit_label = wx.StaticText(input_container, label="目标单位：")
        to_unit_label.SetMinSize((150, -1))
        to_unit_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.unit_to = wx.Choice(input_container, choices=["米", "千米", "厘米", "毫米"])
        self.unit_to.SetSelection(1)
        to_unit_sizer.Add(to_unit_label, 0, wx.ALL, 8)
        to_unit_sizer.Add(self.unit_to, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(to_unit_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 计算按钮
        calc_btn = wx.Button(input_container, label="换算", size=(-1, 45))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_unit)
        calc_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        calc_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 15)
        
        input_container.SetSizer(input_sizer)
        input_container_sizer = wx.BoxSizer(wx.VERTICAL)
        input_container_sizer.Add(input_container, 1, wx.EXPAND | wx.ALL, 8)
        input_panel.SetSizer(input_container_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 8)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(245, 247, 250))
        result_scroll.SetupScrolling()
        
        result_container = wx.Panel(result_scroll)
        result_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.unit_result_text = wx.StaticText(result_container, label="请输入数值并选择单位进行换算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.unit_result_text.SetFont(result_font)
        self.unit_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.unit_result_text.Wrap(600)
        
        result_sizer.Add(self.unit_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_container.SetSizer(result_sizer)
        
        result_scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        result_scroll_sizer.Add(result_container, 1, wx.EXPAND | wx.ALL, 8)
        result_scroll.SetSizer(result_scroll_sizer)
        
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 8)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 8)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 8)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 8)
        panel.SetSizer(main_sizer)
        
        # 初始化单位列表
        self.on_unit_type_changed(None)
        
        return panel
    
    def create_date_calculator_panel(self):
        """创建日期计算器面板"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        # 左侧：输入参数区域
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(wx.Colour(250, 252, 255))
        left_panel.SetMinSize((400, -1))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        input_panel = wx.Panel(left_panel)
        input_panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        input_container = wx.Panel(input_panel)
        input_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(input_container, label="📅 日期计算器")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(wx.Colour(48, 49, 51))
        input_sizer.Add(title_label, 0, wx.ALL, 15)
        
        # 计算类型
        calc_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calc_type_label = wx.StaticText(input_container, label="计算类型：")
        calc_type_label.SetMinSize((150, -1))
        calc_type_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.date_calc_type = wx.RadioBox(
            input_container,
            choices=["日期差", "日期加减"],
            majorDimension=2,
            style=wx.RA_HORIZONTAL
        )
        self.date_calc_type.Bind(wx.EVT_RADIOBOX, self.on_date_calc_type_changed)
        calc_type_sizer.Add(calc_type_label, 0, wx.ALL, 8)
        calc_type_sizer.Add(self.date_calc_type, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(calc_type_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 日期1
        date1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        date1_label = wx.StaticText(input_container, label="日期1：")
        date1_label.SetMinSize((150, -1))
        date1_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.date_date1 = wx.adv.DatePickerCtrl(input_container, style=wx.adv.DP_DROPDOWN)
        date1_sizer.Add(date1_label, 0, wx.ALL, 8)
        date1_sizer.Add(self.date_date1, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(date1_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 日期2（用于日期差）
        date2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        date2_label = wx.StaticText(input_container, label="日期2：")
        date2_label.SetMinSize((150, -1))
        date2_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.date_date2 = wx.adv.DatePickerCtrl(input_container, style=wx.adv.DP_DROPDOWN)
        date2_sizer.Add(date2_label, 0, wx.ALL, 8)
        date2_sizer.Add(self.date_date2, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(date2_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 天数（用于日期加减）
        days_sizer = wx.BoxSizer(wx.HORIZONTAL)
        days_label = wx.StaticText(input_container, label="天数：")
        days_label.SetMinSize((150, -1))
        days_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.date_days = wx.TextCtrl(input_container, value="0")
        self.date_days.SetBackgroundColour(wx.Colour(250, 252, 255))
        days_sizer.Add(days_label, 0, wx.ALL, 8)
        days_sizer.Add(self.date_days, 1, wx.EXPAND | wx.ALL, 8)
        input_sizer.Add(days_sizer, 0, wx.EXPAND | wx.ALL, 8)
        
        # 计算按钮
        calc_btn = wx.Button(input_container, label="计算", size=(-1, 45))
        calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255))
        calc_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        calc_btn.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate_date)
        calc_btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(85, 170, 255)))
        calc_btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: calc_btn.SetBackgroundColour(wx.Colour(64, 158, 255)))
        input_sizer.Add(calc_btn, 0, wx.EXPAND | wx.ALL, 15)
        
        input_container.SetSizer(input_sizer)
        input_container_sizer = wx.BoxSizer(wx.VERTICAL)
        input_container_sizer.Add(input_container, 1, wx.EXPAND | wx.ALL, 8)
        input_panel.SetSizer(input_container_sizer)
        left_sizer.Add(input_panel, 0, wx.EXPAND | wx.ALL, 8)
        left_panel.SetSizer(left_sizer)
        
        # 右侧：结果显示区域
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        result_scroll = scrolled.ScrolledPanel(right_panel)
        result_scroll.SetBackgroundColour(wx.Colour(245, 247, 250))
        result_scroll.SetupScrolling()
        
        result_container = wx.Panel(result_scroll)
        result_container.SetBackgroundColour(wx.Colour(255, 255, 255))
        result_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.date_result_text = wx.StaticText(result_container, label="请选择日期并点击计算", style=wx.ALIGN_LEFT)
        result_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                             wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.date_result_text.SetFont(result_font)
        self.date_result_text.SetForegroundColour(wx.Colour(48, 49, 51))
        self.date_result_text.Wrap(600)
        
        result_sizer.Add(self.date_result_text, 0, wx.EXPAND | wx.ALL, 15)
        result_container.SetSizer(result_sizer)
        
        result_scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        result_scroll_sizer.Add(result_container, 1, wx.EXPAND | wx.ALL, 8)
        result_scroll.SetSizer(result_scroll_sizer)
        
        right_sizer.Add(result_scroll, 1, wx.EXPAND | wx.ALL, 8)
        right_panel.SetSizer(right_sizer)
        
        hbox.Add(left_panel, 0, wx.EXPAND | wx.ALL, 8)
        hbox.Add(right_panel, 1, wx.EXPAND | wx.ALL, 8)
        main_sizer.Add(hbox, 1, wx.EXPAND | wx.ALL, 8)
        panel.SetSizer(main_sizer)
        
        # 初始化显示
        self.on_date_calc_type_changed(None)
        
        return panel
    
    def create_placeholder_panel(self, title, icon, features):
        """创建占位面板（通用方法）"""
        panel = wx.Panel(self.notebook)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        placeholder = wx.Panel(panel)
        placeholder.SetBackgroundColour(wx.Colour(250, 252, 255))
        
        info_text = wx.StaticText(
            placeholder,
            label=f"{icon} {title}\n\n"
                  f"{features}\n\n"
                  "🚧 开发中，敬请期待..."
        )
        info_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        info_text.SetFont(info_font)
        info_text.SetForegroundColour(wx.Colour(144, 147, 153))
        
        sizer.Add(info_text, 1, wx.ALIGN_CENTER | wx.ALL, 50)
        placeholder.SetSizer(sizer)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(placeholder, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(main_sizer)
        
        return panel
    
    def on_basic_button_click(self, event):
        """基础计算器按钮点击事件"""
        btn = event.GetEventObject()
        text = btn.GetLabel()
        
        if text == 'C':
            self.basic_current_value = "0"
            self.basic_expression = ""
            self.update_basic_display()
        elif text == 'CE':
            self.basic_current_value = "0"
            self.update_basic_display()
        elif text == '=':
            self.calculate_basic_expression()
        elif text == '±':
            if self.basic_current_value != "0":
                if self.basic_current_value.startswith('-'):
                    self.basic_current_value = self.basic_current_value[1:]
                else:
                    self.basic_current_value = '-' + self.basic_current_value
                self.update_basic_display()
        elif text == '%':
            try:
                val = float(self.basic_current_value) / 100
                self.basic_current_value = str(val)
                self.update_basic_display()
            except:
                pass
        elif text in ['+', '-', '*', '/']:
            if self.basic_expression and not self.basic_expression[-1] in ['+', '-', '*', '/']:
                self.basic_expression += self.basic_current_value + text
            else:
                self.basic_expression = self.basic_current_value + text
            self.basic_current_value = "0"
            self.update_basic_display()
        elif text == '√':
            try:
                val = math.sqrt(float(self.basic_current_value))
                self.basic_current_value = str(val)
                self.add_to_history(f"√{self.basic_expression_text.GetLabel() or self.basic_current_value} = {val}")
                self.basic_expression = ""
                self.update_basic_display()
            except:
                pass
        elif text == 'x²':
            try:
                val = float(self.basic_current_value) ** 2
                self.basic_current_value = str(val)
                self.add_to_history(f"({self.basic_current_value})² = {val}")
                self.basic_expression = ""
                self.update_basic_display()
            except:
                pass
        elif text == '1/x':
            try:
                val = 1 / float(self.basic_current_value)
                self.basic_current_value = str(val)
                self.add_to_history(f"1/({self.basic_expression_text.GetLabel() or self.basic_current_value}) = {val}")
                self.basic_expression = ""
                self.update_basic_display()
            except:
                pass
        elif text in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
            if self.basic_current_value == "0" and text != '.':
                self.basic_current_value = text
            else:
                if text == '.' and '.' in self.basic_current_value:
                    return
                self.basic_current_value += text
            self.update_basic_display()
        elif text in ['(', ')']:
            self.basic_expression += text
            self.update_basic_display()
    
    def on_basic_sci_button(self, func):
        """科学计算按钮点击"""
        try:
            val = float(self.basic_current_value)
            if func == 'sin':
                result = math.sin(math.radians(val))
                expr = f"sin({val}°)"
            elif func == 'cos':
                result = math.cos(math.radians(val))
                expr = f"cos({val}°)"
            elif func == 'tan':
                result = math.tan(math.radians(val))
                expr = f"tan({val}°)"
            elif func == 'log':
                result = math.log10(val)
                expr = f"log({val})"
            elif func == 'ln':
                result = math.log(val)
                expr = f"ln({val})"
            elif func == 'pi':
                result = math.pi
                expr = "π"
            elif func == 'e':
                result = math.e
                expr = "e"
            elif func == '**':
                # 幂运算，需要输入第二个数
                self.basic_expression = self.basic_current_value + "**"
                self.basic_current_value = "0"
                self.update_basic_display()
                return
            else:
                return
            
            self.basic_current_value = str(result)
            self.add_to_history(f"{expr} = {result}")
            self.basic_expression = ""
            self.update_basic_display()
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def calculate_basic_expression(self):
        """计算基础表达式"""
        try:
            if self.basic_expression:
                expr = self.basic_expression + self.basic_current_value
            else:
                expr = self.basic_current_value
            
            # 替换数学函数和常量
            expr = expr.replace('π', str(math.pi))
            expr = expr.replace('e', str(math.e))
            
            # 安全计算（只允许数字、运算符、括号和基本函数）
            result = eval(expr, {"__builtins__": {}}, {"math": math, "sin": math.sin, "cos": math.cos, 
                                                      "tan": math.tan, "log": math.log10, "ln": math.log,
                                                      "sqrt": math.sqrt, "pow": pow})
            
            self.add_to_history(f"{expr} = {result}")
            self.basic_current_value = str(result)
            self.basic_expression = ""
            self.update_basic_display()
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def update_basic_display(self):
        """更新基础计算器显示"""
        self.basic_result_text.SetLabel(self.basic_current_value)
        self.basic_expression_text.SetLabel(self.basic_expression)
        self.basic_result_text.Wrap(-1)
        self.basic_expression_text.Wrap(-1)
    
    def on_basic_expr_input(self, event):
        """表达式输入框事件"""
        pass
    
    def on_calculate_expr(self, event):
        """计算表达式按钮事件"""
        expr = self.basic_expr_input.GetValue().strip()
        if not expr:
            return
        
        try:
            # 替换数学函数和常量
            expr_processed = expr.replace('π', str(math.pi))
            expr_processed = expr_processed.replace('e', str(math.e))
            expr_processed = expr_processed.replace('^', '**')
            
            result = eval(expr_processed, {"__builtins__": {}}, {"math": math, "sin": math.sin, "cos": math.cos,
                                                                 "tan": math.tan, "log": math.log10, "ln": math.log,
                                                                 "sqrt": math.sqrt, "pow": pow})
            
            self.add_to_history(f"{expr} = {result}")
            self.basic_current_value = str(result)
            self.basic_expression = ""
            self.update_basic_display()
            self.basic_expr_input.SetValue("")
        except Exception as e:
            wx.MessageBox(f"表达式错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def add_to_history(self, item):
        """添加到历史记录"""
        self.basic_history.insert(0, item)
        if len(self.basic_history) > 50:
            self.basic_history = self.basic_history[:50]
        self.basic_history_list.Set(self.basic_history)
    
    def on_history_select(self, event):
        """历史记录选择事件"""
        selection = self.basic_history_list.GetSelection()
        if selection >= 0:
            item = self.basic_history[selection]
            # 提取表达式部分
            if ' = ' in item:
                expr = item.split(' = ')[0]
                self.basic_expr_input.SetValue(expr)
    
    def on_clear_history(self, event):
        """清空历史记录"""
        self.basic_history = []
        self.basic_history_list.Set([])
    
    def on_calculate_bmi(self, event):
        """计算BMI"""
        try:
            height = float(self.bmi_height.GetValue()) / 100  # 转换为米
            weight = float(self.bmi_weight.GetValue())
            
            if height <= 0 or weight <= 0:
                raise ValueError("身高和体重必须大于0")
            
            bmi = weight / (height ** 2)
            
            # BMI分类
            if bmi < 18.5:
                category = "偏瘦"
                color = wx.Colour(64, 158, 255)
                advice = "建议适当增加营养摄入，保持健康体重"
            elif bmi < 24:
                category = "正常"
                color = wx.Colour(103, 194, 58)
                advice = "恭喜！您的体重在正常范围内，请继续保持"
            elif bmi < 28:
                category = "偏胖"
                color = wx.Colour(226, 192, 0)
                advice = "建议适当控制饮食，增加运动量"
            else:
                category = "肥胖"
                color = wx.Colour(245, 108, 108)
                advice = "建议咨询专业医生，制定科学的减重计划"
            
            result = f"""BMI计算结果：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

身高：{height*100:.1f} cm
体重：{weight:.1f} kg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BMI值：{bmi:.2f}

分类：{category}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

健康建议：
{advice}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BMI标准参考：
• 偏瘦：BMI < 18.5
• 正常：18.5 ≤ BMI < 24
• 偏胖：24 ≤ BMI < 28
• 肥胖：BMI ≥ 28

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• BMI = 体重(kg) / 身高(m)²
• 此计算仅供参考，具体健康评估请咨询专业医生
• 不同年龄、性别、肌肉量等因素可能影响BMI的准确性
"""
            
            self.bmi_result_text.SetLabel(result)
            self.bmi_result_text.Wrap(600)
            result_scroll = self.bmi_result_text.GetParent().GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_unit_type_changed(self, event):
        """单位类型改变事件"""
        unit_type = self.unit_type.GetSelection()
        
        if unit_type == 0:  # 长度
            units = ["米", "千米", "厘米", "毫米", "英尺", "英寸", "英里", "码"]
        elif unit_type == 1:  # 重量
            units = ["千克", "克", "吨", "毫克", "磅", "盎司", "斤", "两"]
        elif unit_type == 2:  # 温度
            units = ["摄氏度", "华氏度", "开尔文"]
        elif unit_type == 3:  # 面积
            units = ["平方米", "平方千米", "公顷", "平方厘米", "平方英尺", "平方英寸", "亩", "英亩"]
        else:  # 体积
            units = ["升", "毫升", "立方米", "立方厘米", "加仑", "品脱", "夸脱"]
        
        self.unit_from.SetItems(units)
        self.unit_to.SetItems(units)
        self.unit_from.SetSelection(0)
        self.unit_to.SetSelection(1 if len(units) > 1 else 0)
    
    def on_calculate_unit(self, event):
        """计算单位换算"""
        try:
            value = float(self.unit_input_value.GetValue())
            unit_type = self.unit_type.GetSelection()
            from_unit = self.unit_from.GetStringSelection()
            to_unit = self.unit_to.GetStringSelection()
            
            if value < 0:
                raise ValueError("数值必须大于等于0")
            
            # 长度换算（以米为基准）
            if unit_type == 0:
                length_units = {
                    "米": 1, "千米": 1000, "厘米": 0.01, "毫米": 0.001,
                    "英尺": 0.3048, "英寸": 0.0254, "英里": 1609.344, "码": 0.9144
                }
                from_value = value * length_units.get(from_unit, 1)
                to_value = from_value / length_units.get(to_unit, 1)
                
            # 重量换算（以千克为基准）
            elif unit_type == 1:
                weight_units = {
                    "千克": 1, "克": 0.001, "吨": 1000, "毫克": 0.000001,
                    "磅": 0.453592, "盎司": 0.0283495, "斤": 0.5, "两": 0.05
                }
                from_value = value * weight_units.get(from_unit, 1)
                to_value = from_value / weight_units.get(to_unit, 1)
                
            # 温度换算
            elif unit_type == 2:
                if from_unit == "摄氏度":
                    if to_unit == "华氏度":
                        to_value = value * 9 / 5 + 32
                    elif to_unit == "开尔文":
                        to_value = value + 273.15
                    else:
                        to_value = value
                elif from_unit == "华氏度":
                    if to_unit == "摄氏度":
                        to_value = (value - 32) * 5 / 9
                    elif to_unit == "开尔文":
                        to_value = (value - 32) * 5 / 9 + 273.15
                    else:
                        to_value = value
                else:  # 开尔文
                    if to_unit == "摄氏度":
                        to_value = value - 273.15
                    elif to_unit == "华氏度":
                        to_value = (value - 273.15) * 9 / 5 + 32
                    else:
                        to_value = value
                        
            # 面积换算（以平方米为基准）
            elif unit_type == 3:
                area_units = {
                    "平方米": 1, "平方千米": 1000000, "公顷": 10000, "平方厘米": 0.0001,
                    "平方英尺": 0.092903, "平方英寸": 0.00064516, "亩": 666.667, "英亩": 4046.86
                }
                from_value = value * area_units.get(from_unit, 1)
                to_value = from_value / area_units.get(to_unit, 1)
                
            # 体积换算（以升为基准）
            else:
                volume_units = {
                    "升": 1, "毫升": 0.001, "立方米": 1000, "立方厘米": 0.001,
                    "加仑": 3.78541, "品脱": 0.473176, "夸脱": 0.946353
                }
                from_value = value * volume_units.get(from_unit, 1)
                to_value = from_value / volume_units.get(to_unit, 1)
            
            result = f"""单位换算结果：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输入值：{value:.6f} {from_unit}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

换算结果：{to_value:.6f} {to_unit}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

换算公式：
{value:.6f} {from_unit} = {to_value:.6f} {to_unit}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 支持长度、重量、温度、面积、体积等多种单位换算
• 温度换算：摄氏度 ↔ 华氏度 ↔ 开尔文
• 其他单位换算均以国际标准单位（米、千克、升等）为基准
"""
            
            self.unit_result_text.SetLabel(result)
            self.unit_result_text.Wrap(600)
            result_scroll = self.unit_result_text.GetParent().GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_date_calc_type_changed(self, event):
        """日期计算类型改变事件"""
        calc_type = self.date_calc_type.GetSelection()
        
        if calc_type == 0:  # 日期差
            self.date_date2.Show()
            self.date_days.Hide()
        else:  # 日期加减
            self.date_date2.Hide()
            self.date_days.Show()
        
        if hasattr(self, 'date_date2'):
            self.date_date2.GetParent().Layout()
            self.date_days.GetParent().Layout()
    
    def on_calculate_date(self, event):
        """计算日期"""
        try:
            calc_type = self.date_calc_type.GetSelection()
            date1 = self.date_date1.GetValue()
            # wx.DateTime的month是0-11，需要加1
            date1_py = datetime.date(date1.year, date1.month + 1, date1.day)
            
            if calc_type == 0:
                # 日期差
                date2 = self.date_date2.GetValue()
                # wx.DateTime的month是0-11，需要加1
                date2_py = datetime.date(date2.year, date2.month + 1, date2.day)
                
                delta = date2_py - date1_py
                days = abs(delta.days)
                
                years = days // 365
                months = days // 30
                weeks = days // 7
                
                result = f"""日期差计算结果：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

日期1：{date1_py.strftime('%Y年%m月%d日')}
日期2：{date2_py.strftime('%Y年%m月%d日')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

相差天数：{days} 天

相差周数：{weeks} 周

相差月数：约 {months} 个月

相差年数：约 {years} 年

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 日期差计算以天数为基准
• 周数、月数、年数为约数，仅供参考
"""
            else:
                # 日期加减
                days = int(self.date_days.GetValue())
                
                result_date = date1_py + datetime.timedelta(days=days)
                
                result = f"""日期加减计算结果：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基准日期：{date1_py.strftime('%Y年%m月%d日')}
加减天数：{days:+d} 天

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

计算结果：{result_date.strftime('%Y年%m月%d日')}

星期：{['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][result_date.weekday()]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

说明：
• 正数表示向后加，负数表示向前减
• 自动处理月份和年份的进位
"""
            
            self.date_result_text.SetLabel(result)
            self.date_result_text.Wrap(600)
            result_scroll = self.date_result_text.GetParent().GetParent()
            result_scroll.Layout()
            
        except ValueError as e:
            wx.MessageBox(f"输入错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"计算错误: {e}", "错误", wx.OK | wx.ICON_ERROR)
    
    def on_page_changed(self, event):
        """标签页切换事件"""
        current_page = self.notebook.GetSelection()
        page_text = self.notebook.GetPageText(current_page)
        print(f"切换到标签页: {page_text}")
        event.Skip()


def main():
    """主函数"""
    app = wx.App()
    frame = MultiCalculatorApp()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()

