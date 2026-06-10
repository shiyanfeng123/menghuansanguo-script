import wx
import wx.grid
import requests
import json
import os
import sys
import threading
from datetime import datetime

BASE_URL = "https://p01--script-serve--5yyh9pxyhqq4.code.run"
PERMANENT_DATE = "2199-12-30 23:59:59"

class AdminApp(wx.App):
    def __init__(self):
        super().__init__()
        self.token = ""
        self.username = ""

    def _api_sync(self, path, body=None, method="POST"):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            url = f"{BASE_URL}{path}"
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=10)
            else:
                r = requests.post(url, json=body or {}, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.json()
            try:
                err = r.json()
                return {"error": err.get("error", "操作失败")}
            except:
                return {"error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _async_call(self, fn, callback):
        def worker():
            result = fn()
            wx.CallAfter(callback, result)
        threading.Thread(target=worker, daemon=True).start()


class LoginDialog(wx.Dialog):
    def __init__(self, app):
        super().__init__(None, title="管理员登录", size=(340, 260), pos=(300, 150),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.app = app
        self._busy = False

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        vs = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="梦幻三国 - 后台管理")
        title.SetForegroundColour(wx.Colour(50, 80, 140))
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vs.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 16)

        input_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")

        self.user_input = wx.TextCtrl(panel, size=(260, 34))
        self.user_input.SetHint("管理员账号")
        self.user_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.user_input.SetFont(input_font)
        vs.Add(self.user_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.pass_input = wx.TextCtrl(panel, size=(260, 34), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("密码")
        self.pass_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.pass_input.SetFont(input_font)
        vs.Add(self.pass_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        self.login_btn = wx.Button(panel, size=(260, 36), style=wx.BORDER_NONE, label="登录")
        self.login_btn.SetBackgroundColour(wx.Colour(50, 80, 140))
        self.login_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.login_btn.SetFont(btn_font)
        self.login_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        vs.Add(self.login_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.error_label = wx.StaticText(panel, label="")
        self.error_label.SetForegroundColour(wx.Colour(192, 57, 43))
        self.error_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        vs.Add(self.error_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)

        panel.SetSizer(vs)
        ds = wx.BoxSizer(wx.VERTICAL)
        ds.Add(panel, 1, wx.EXPAND)
        self.SetSizer(ds)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

    def on_login(self, event):
        if self._busy:
            return
        username = self.user_input.GetValue().strip()
        password = self.pass_input.GetValue().strip()
        if not username or not password:
            self.error_label.SetLabel("请输入账号和密码")
            return

        self._busy = True
        self.login_btn.SetLabel("登录中...")
        self.login_btn.Disable()

        def do_login():
            resp = self.app._api_sync("/api/login", {"username": username, "password": password})
            if resp and resp.get("token"):
                token = resp["token"]
                self.app.token = token
                verify = self.app._api_sync("/api/verify", {"token": token})
                if verify and verify.get("valid") and verify.get("role") == "admin":
                    self.app.username = username
                    return True
                else:
                    self.app.token = ""
                    return {"error": "此账号无管理员权限"}
            return resp

        def on_result(result):
            self._busy = False
            self.login_btn.SetLabel("登录")
            self.login_btn.Enable()
            if result is True:
                self.EndModal(wx.ID_OK)
            else:
                self.error_label.SetLabel(result.get("error", "登录失败") if result else "网络错误")

        threading.Thread(target=lambda: on_result(do_login()), daemon=True).start()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN and not self._busy:
            self.on_login(None)
        else:
            event.Skip()


class AdminFrame(wx.Frame):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(100, 105, 115)

    def __init__(self, app):
        super().__init__(None, title="梦幻三国 - 后台管理", size=(800, 580), pos=(100, 40))
        self.SetBackgroundColour(self.C_BG)
        self.app = app
        self._busy = False

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(panel, label="后台管理")
        title.SetForegroundColour(self.C_GOLD)
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        header.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        header.AddStretchSpacer()

        user_info = wx.StaticText(panel, label=f"管理员: {app.username}")
        user_info.SetForegroundColour(self.C_MUTED)
        user_info.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        header.Add(user_info, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.refresh_btn = wx.Button(panel, size=(60, 26), style=wx.BORDER_NONE, label="刷新")
        self.refresh_btn.SetBackgroundColour(self.C_SURFACE)
        self.refresh_btn.SetForegroundColour(self.C_TEXT)
        self.refresh_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        header.Add(self.refresh_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        main_sizer.Add(header, 0, wx.EXPAND | wx.ALL, 12)
        main_sizer.AddSpacer(6)

        cols = wx.BoxSizer(wx.HORIZONTAL)

        # 左栏：用户列表
        left_panel = wx.Panel(panel)
        left_panel.SetBackgroundColour(self.C_SURFACE)
        lvs = wx.BoxSizer(wx.VERTICAL)

        lt = wx.StaticText(left_panel, label="用户列表")
        lt.SetForegroundColour(self.C_GOLD)
        lt.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        lvs.Add(lt, 0, wx.ALL, 8)

        self.user_grid = wx.grid.Grid(left_panel, size=(380, 420))
        self.user_grid.CreateGrid(0, 6)
        self.user_grid.SetColLabelValue(0, "用户名")
        self.user_grid.SetColLabelValue(1, "权限")
        self.user_grid.SetColLabelValue(2, "到期")
        self.user_grid.SetColLabelValue(3, "设备数")
        self.user_grid.SetColLabelValue(4, "角色")
        self.user_grid.SetColLabelValue(5, "创建")
        self.user_grid.SetColSize(0, 70)
        self.user_grid.SetColSize(1, 45)
        self.user_grid.SetColSize(2, 130)
        self.user_grid.SetColSize(3, 50)
        self.user_grid.SetColSize(4, 45)
        self.user_grid.SetColSize(5, 70)
        self.user_grid.SetRowLabelSize(25)
        self.user_grid.SetDefaultCellFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.user_grid.SetLabelFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.user_grid.EnableEditing(False)
        self.user_grid.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.user_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_user_select)
        lvs.Add(self.user_grid, 1, wx.EXPAND | wx.ALL, 6)

        left_panel.SetSizer(lvs)
        cols.Add(left_panel, 2, wx.EXPAND | wx.RIGHT, 6)

        # 右栏：操作区
        right_panel = wx.Panel(panel)
        right_panel.SetBackgroundColour(self.C_SURFACE)
        rvs = wx.BoxSizer(wx.VERTICAL)

        rt = wx.StaticText(right_panel, label="操作")
        rt.SetForegroundColour(self.C_GOLD)
        rt.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        rvs.Add(rt, 0, wx.ALL, 8)

        box_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        input_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")

        def _section(label):
            lb = wx.StaticText(right_panel, label=label)
            lb.SetForegroundColour(self.C_GOLD)
            lb.SetFont(box_font)
            rvs.Add(lb, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)

        _section("添加用户")
        self.add_user_input = wx.TextCtrl(right_panel, size=(-1, 28))
        self.add_user_input.SetHint("用户名")
        self.add_user_input.SetFont(input_font)
        rvs.Add(self.add_user_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        self.add_pass_input = wx.TextCtrl(right_panel, size=(-1, 28), style=wx.TE_PASSWORD)
        self.add_pass_input.SetHint("密码")
        self.add_pass_input.SetFont(input_font)
        rvs.Add(self.add_pass_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        add_row = wx.BoxSizer(wx.HORIZONTAL)
        self.add_days_input = wx.TextCtrl(right_panel, size=(60, 28))
        self.add_days_input.SetHint("天数")
        self.add_days_input.SetValue("30")
        self.add_days_input.SetFont(input_font)
        add_row.Add(self.add_days_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.add_permanent_cb = wx.CheckBox(right_panel, label="永久")
        self.add_permanent_cb.SetForegroundColour(self.C_MUTED)
        self.add_permanent_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.add_permanent_cb.Bind(wx.EVT_CHECKBOX, lambda e: self.add_days_input.Disable() if self.add_permanent_cb.GetValue() else self.add_days_input.Enable())
        add_row.Add(self.add_permanent_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.add_script_choice = wx.ComboBox(right_panel, size=(60, 28), choices=["vip", "free"], value="vip")
        self.add_script_choice.SetFont(input_font)
        add_row.Add(self.add_script_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.add_role_choice = wx.ComboBox(right_panel, size=(60, 28), choices=["user", "admin"], value="user")
        self.add_role_choice.SetFont(input_font)
        add_row.Add(self.add_role_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.add_btn = wx.Button(right_panel, size=(60, 28), style=wx.BORDER_NONE, label="添加")
        self.add_btn.SetBackgroundColour(wx.Colour(39, 174, 96))
        self.add_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.add_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.add_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_user)
        add_row.Add(self.add_btn, 0)
        rvs.Add(add_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        rvs.AddSpacer(8)

        _section("续期")
        self.extend_user_label = wx.StaticText(right_panel, label="选择左侧用户...")
        self.extend_user_label.SetForegroundColour(self.C_MUTED)
        self.extend_user_label.SetFont(input_font)
        rvs.Add(self.extend_user_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)

        ext_row = wx.BoxSizer(wx.HORIZONTAL)
        self.extend_days_input = wx.TextCtrl(right_panel, size=(60, 28))
        self.extend_days_input.SetHint("续期天数")
        self.extend_days_input.SetValue("30")
        self.extend_days_input.SetFont(input_font)
        ext_row.Add(self.extend_days_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.extend_permanent_cb = wx.CheckBox(right_panel, label="永久")
        self.extend_permanent_cb.SetForegroundColour(self.C_MUTED)
        self.extend_permanent_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.extend_permanent_cb.Bind(wx.EVT_CHECKBOX, lambda e: self.extend_days_input.Disable() if self.extend_permanent_cb.GetValue() else self.extend_days_input.Enable())
        ext_row.Add(self.extend_permanent_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.extend_script_choice = wx.ComboBox(right_panel, size=(60, 28), choices=["vip", "free"])
        self.extend_script_choice.SetFont(input_font)
        ext_row.Add(self.extend_script_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.extend_btn = wx.Button(right_panel, size=(60, 28), style=wx.BORDER_NONE, label="续期")
        self.extend_btn.SetBackgroundColour(wx.Colour(41, 128, 185))
        self.extend_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.extend_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.extend_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.extend_btn.Bind(wx.EVT_BUTTON, self.on_extend)
        ext_row.Add(self.extend_btn, 0)
        rvs.Add(ext_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        rvs.AddSpacer(8)

        self.delete_btn = wx.Button(right_panel, size=(-1, 28), style=wx.BORDER_NONE, label="删除选中用户")
        self.delete_btn.SetBackgroundColour(wx.Colour(192, 57, 43))
        self.delete_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.delete_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.delete_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        rvs.Add(self.delete_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)

        rvs.AddSpacer(12)

        _section("生成邀请码")
        invite_row = wx.BoxSizer(wx.HORIZONTAL)
        self.invite_count_input = wx.TextCtrl(right_panel, size=(50, 28))
        self.invite_count_input.SetHint("数量")
        self.invite_count_input.SetValue("1")
        self.invite_count_input.SetFont(input_font)
        invite_row.Add(self.invite_count_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.invite_script_choice = wx.ComboBox(right_panel, size=(60, 28), choices=["vip", "free"], value="vip")
        self.invite_script_choice.SetFont(input_font)
        invite_row.Add(self.invite_script_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.invite_days_input = wx.TextCtrl(right_panel, size=(50, 28))
        self.invite_days_input.SetHint("天数")
        self.invite_days_input.SetValue("30")
        self.invite_days_input.SetFont(input_font)
        invite_row.Add(self.invite_days_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self.invite_permanent_cb = wx.CheckBox(right_panel, label="永久")
        self.invite_permanent_cb.SetForegroundColour(self.C_MUTED)
        self.invite_permanent_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        self.invite_permanent_cb.Bind(wx.EVT_CHECKBOX, lambda e: self.invite_days_input.Disable() if self.invite_permanent_cb.GetValue() else self.invite_days_input.Enable())
        invite_row.Add(self.invite_permanent_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.invite_btn = wx.Button(right_panel, size=(60, 28), style=wx.BORDER_NONE, label="生成")
        self.invite_btn.SetBackgroundColour(wx.Colour(50, 80, 140))
        self.invite_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.invite_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.invite_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.invite_btn.Bind(wx.EVT_BUTTON, self.on_gen_invite)
        invite_row.Add(self.invite_btn, 0)
        rvs.Add(invite_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 6)

        rvs.AddSpacer(6)

        self.invite_result = wx.TextCtrl(right_panel, size=(-1, 100), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.invite_result.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.invite_result.SetBackgroundColour(wx.Colour(255, 255, 255))
        rvs.Add(self.invite_result, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        self.status_label = wx.StaticText(right_panel, label="")
        self.status_label.SetForegroundColour(wx.Colour(39, 174, 96))
        self.status_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        rvs.Add(self.status_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)

        right_panel.SetSizer(rvs)
        cols.Add(right_panel, 1, wx.EXPAND)

        main_sizer.Add(cols, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        panel.SetSizer(main_sizer)

        self.selected_user = ""
        self.selected_row = -1

    def _run_async(self, fn, callback):
        def worker():
            try:
                result = fn()
            except Exception as e:
                result = {"error": str(e)}
            wx.CallAfter(callback, result)
        threading.Thread(target=worker, daemon=True).start()

    def refresh_users(self):
        def do_refresh():
            return self.app._api_sync("/api/users", method="GET")

        def on_result(resp):
            if isinstance(resp, list):
                self.user_grid.ClearGrid()
                rows = self.user_grid.GetNumberRows()
                if rows > 0:
                    self.user_grid.DeleteRows(0, rows)
                self.user_grid.AppendRows(len(resp))
                for i, u in enumerate(resp):
                    self.user_grid.SetCellValue(i, 0, u.get("username", ""))
                    self.user_grid.SetCellValue(i, 1, u.get("has_script", ""))
                    self.user_grid.SetCellValue(i, 2, u.get("end_time", ""))
                    self.user_grid.SetCellValue(i, 3, str(u.get("device_count", 0)))
                    self.user_grid.SetCellValue(i, 4, u.get("role", ""))
                    self.user_grid.SetCellValue(i, 5, u.get("created_at", ""))
                    if u.get("role") == "admin":
                        self.user_grid.SetCellBackgroundColour(i, 0, wx.Colour(255, 245, 200))
                self.user_grid.ForceRefresh()
            else:
                wx.MessageBox(f"获取用户列表失败: {resp.get('error', '未知错误')}", "错误")

        self._run_async(do_refresh, on_result)

    def on_refresh(self, event=None):
        self.refresh_users()
        self.status_label.SetLabel("刷新中...")

    def on_user_select(self, event):
        row = event.GetRow()
        if row >= 0:
            self.selected_user = self.user_grid.GetCellValue(row, 0)
            self.selected_row = row
            script = self.user_grid.GetCellValue(row, 1)
            expiry = self.user_grid.GetCellValue(row, 2)
            self.extend_user_label.SetLabel(f"选中: {self.selected_user} ({script}) 到期: {expiry}")
            self.extend_script_choice.SetValue(script)
        event.Skip()

    def _show_status(self, msg, is_error=False):
        self.status_label.SetLabel(msg)
        self.status_label.SetForegroundColour(wx.Colour(192, 57, 43) if is_error else wx.Colour(39, 174, 96))

    def on_add_user(self, event):
        username = self.add_user_input.GetValue().strip()
        password = self.add_pass_input.GetValue().strip()
        hs = self.add_script_choice.GetValue()

        if not username or not password:
            self._show_status("请输入用户名和密码", True)
            return

        if self.add_permanent_cb.GetValue():
            days = 99999
        else:
            days_s = self.add_days_input.GetValue().strip()
            try:
                days = int(days_s)
            except:
                self._show_status("天数必须为数字", True)
                return

        self._show_status("添加中...")

        def do_add():
            role = self.add_role_choice.GetValue()
            return self.app._api_sync("/api/users/add", {
                "username": username, "password": password, "has_script": hs, "days": days, "role": role,
            })

        def on_result(resp):
            if resp.get("message"):
                self._show_status(f"添加成功: {username}")
                self.add_user_input.SetValue("")
                self.add_pass_input.SetValue("")
                self.refresh_users()
            else:
                self._show_status(resp.get("error", "添加失败"), True)

        self._run_async(do_add, on_result)

    def on_extend(self, event):
        if not self.selected_user:
            self._show_status("请先在左侧选择要操作的用户", True)
            return

        hs = self.extend_script_choice.GetValue()

        if self.extend_permanent_cb.GetValue():
            days = 99999
        else:
            days_s = self.extend_days_input.GetValue().strip()
            try:
                days = int(days_s)
            except:
                self._show_status("天数必须为数字", True)
                return

        self._show_status("续期中...")

        def do_extend():
            return self.app._api_sync("/api/users/extend", {
                "username": self.selected_user, "days": days, "has_script": hs,
            })

        def on_result(resp):
            if resp.get("message"):
                self._show_status(f"续期成功: {self.selected_user}")
                self.refresh_users()
            else:
                self._show_status(resp.get("error", "续期失败"), True)

        self._run_async(do_extend, on_result)

    def on_delete(self, event):
        if not self.selected_user:
            self._show_status("请先在左侧选择要删除的用户", True)
            return

        dlg = wx.MessageDialog(self,
                               f"确认删除用户 \"{self.selected_user}\"？\n此操作不可撤销！",
                               "确认删除",
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dlg.ShowModal() == wx.ID_YES:
            self._show_status("删除中...")

            def do_delete():
                return self.app._api_sync("/api/users/delete", {"username": self.selected_user})

            def on_result(resp):
                if resp.get("message"):
                    self._show_status(f"已删除: {self.selected_user}")
                    self.selected_user = ""
                    self.extend_user_label.SetLabel("选择左侧用户...")
                    self.refresh_users()
                else:
                    self._show_status(resp.get("error", "删除失败"), True)

            self._run_async(do_delete, on_result)
        dlg.Destroy()

    def on_gen_invite(self, event):
        count_s = self.invite_count_input.GetValue().strip()
        hs = self.invite_script_choice.GetValue()
        days_s = self.invite_days_input.GetValue().strip()

        try:
            count = int(count_s)
        except:
            self._show_status("数量必须为数字", True)
            return

        if self.invite_permanent_cb.GetValue():
            days = 99999
            days_label = "永久"
        else:
            days_s = self.invite_days_input.GetValue().strip()
            try:
                days = int(days_s)
                days_label = f"{days}天"
            except:
                self._show_status("天数必须为数字", True)
                return

        self._show_status("生成中...")

        def do_gen():
            return self.app._api_sync("/api/invite-codes", {
                "count": count, "has_script": hs, "days": days,
            })

        def on_result(resp):
            if isinstance(resp, list):
                codes = [f"{c['code']}  ({hs} {days_label})" for c in resp]
                code_text = "\n".join(codes)
                self.invite_result.SetValue(code_text)
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(code_text))
                    wx.TheClipboard.Close()
                self._show_status(f"生成 {len(resp)} 个邀请码 (已复制到剪切板)")
            else:
                self._show_status(resp.get("error", "生成失败"), True)

        self._run_async(do_gen, on_result)


if __name__ == "__main__":
    app = AdminApp()

    login = LoginDialog(app)
    result = login.ShowModal()
    login.Destroy()

    if result != wx.ID_OK:
        app.Exit()
        sys.exit(0)

    frame = AdminFrame(app)
    frame.Show()
    frame.refresh_users()
    app.MainLoop()
