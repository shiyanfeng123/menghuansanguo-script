# -*- coding: utf-8 -*-
import json
import os
import requests
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from datetime import datetime

import wx
import keyboard

from ya_engine import GameEngine
from ya_scripts import SCRIPT_REGISTRY, get_script_names


class App(wx.App):
    BASE_URL = "https://p01--script-serve--5yyh9pxyhqq4.code.run"

    def __init__(self):
        super().__init__()
        self.user_info = {"username": "", "has_script": "free", "end_time": "2199-12-30 23:59:59", "token": ""}

    def _load_cached(self):
        try:
            data = self._dpapi_load("mhsg_login")
            if data:
                return json.loads(data)
        except:
            pass
        return {}

    def _save_cached(self, username, password, auto_login):
        try:
            self._dpapi_save("mhsg_login", json.dumps({"username": username, "password": password, "auto_login": auto_login}))
        except:
            pass

    @staticmethod
    def _dpapi_save(name, plain):
        import winreg
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\MHSG")
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, plain)
            winreg.CloseKey(key)
        except:
            pass

    @staticmethod
    def _dpapi_load(name):
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\MHSG")
            value, _ = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)
            return value
        except:
            return None

    def _get_mac(self):
        try:
            import uuid
            return ":".join(["{:02x}".format((uuid.getnode() >> e) & 0xFF) for e in range(0, 8 * 6, 8)][::-1])
        except:
            return ""
    mac_address = property(_get_mac)

    def _api(self, path, body=None):
        headers = {}
        if self.user_info.get("token"):
            headers["Authorization"] = f"Bearer {self.user_info['token']}"
        try:
            url = f"{self.BASE_URL}{path}"
            if body is None:
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=body, timeout=10)
            if response.status_code == 200:
                return response.json()
            try:
                return response.json()
            except:
                return None
        except:
            return None
    def do_login(self, username, password, remember):
        resp = self._api("/api/login", {"username": username, "password": password, "device_mac": self.mac_address})
        if resp and resp.get("token"):
            self.user_info = {
                "username": resp.get("user_name", username),
                "has_script": resp.get("has_script", "free"),
                "end_time": resp.get("end_time", "2199-12-30 23:59:59"),
                "token": resp["token"],
                "schemes": resp.get("schemes", {}),
            }
            if remember:
                self._save_cached(username, password, True)
            return {"success": True}
        return {"success": False, "error": resp.get("error", "登录失败") if resp else "网络错误"}

    def do_register(self, username, password, remember):
        resp = self._api("/api/register-free", {"username": username, "password": password, "device_mac": self.mac_address})
        if resp and resp.get("token"):
            self.user_info = {
                "username": resp.get("user_name", username),
                "has_script": "free",
                "end_time": resp.get("end_time", "2199-12-30 23:59:59"),
                "token": resp["token"],
                "schemes": {},
            }
            if remember:
                self._save_cached(username, password, True)
            return {"success": True}
        return {"success": False, "error": resp.get("error", "注册失败") if resp else "网络错误"}

    def do_activate(self, username, password, invite_code, remember):
        resp = self._api("/api/activate", {"username": username, "password": password, "invite_code": invite_code, "device_mac": self.mac_address})
        if resp and resp.get("token"):
            self.user_info = {
                "username": resp.get("user_name", username),
                "has_script": resp.get("has_script", "vip"),
                "end_time": resp.get("end_time", "2199-12-30 23:59:59"),
                "token": resp["token"],
                "schemes": resp.get("schemes", {}),
            }
            if remember:
                self._save_cached(username, password, True)
            return {"success": True}
        return {"success": False, "error": resp.get("error", "激活失败") if resp else "网络错误"}

    def logout(self):
        self.user_info = {"username": "", "has_script": "free", "end_time": "2199-12-30 23:59:59", "token": ""}


class LoginWindow(wx.Dialog):
    def __init__(self, app, skip_auto=False):
        super().__init__(None, title="梦幻三国脚本", size=(360, 340), pos=(200, 60),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.app = app
        self._cancelled = False
        self._skip_auto = skip_auto

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.panel = panel
        vs = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="梦幻三国脚本")
        title.SetForegroundColour(wx.Colour(50, 80, 140))
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vs.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 16)

        self.loading_panel = wx.Panel(panel, size=(300, 60))
        self.loading_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        lds = wx.BoxSizer(wx.HORIZONTAL)
        self.loading_text = wx.StaticText(self.loading_panel, label="正在自动登录...")
        self.loading_text.SetForegroundColour(wx.Colour(100, 105, 115))
        self.loading_text.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        lds.Add(self.loading_text, 1, wx.ALIGN_CENTER | wx.ALL, 12)

        self.cancel_btn = wx.Button(self.loading_panel, size=(80, 28), style=wx.BORDER_NONE, label="取消")
        self.cancel_btn.SetBackgroundColour(wx.Colour(192, 57, 43))
        self.cancel_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.cancel_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel_auto)
        lds.Add(self.cancel_btn, 0, wx.ALIGN_CENTER | wx.ALL, 12)
        self.loading_panel.SetSizer(lds)
        vs.Add(self.loading_panel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.loading_panel.Hide()

        self.main_section = wx.Panel(panel)
        self.main_section.SetBackgroundColour(wx.Colour(243, 244, 248))
        mvs = wx.BoxSizer(wx.VERTICAL)

        input_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")
        self.user_input = wx.TextCtrl(self.main_section, size=(290, 34))
        self.user_input.SetHint("账号")
        self.user_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.user_input.SetFont(input_font)
        mvs.Add(self.user_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.pass_input = wx.TextCtrl(self.main_section, size=(290, 34), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("密码")
        self.pass_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.pass_input.SetFont(input_font)
        mvs.Add(self.pass_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        btn_bar = wx.BoxSizer(wx.HORIZONTAL)
        self.login_btn = wx.Button(self.main_section, size=(141, 38), style=wx.BORDER_NONE, label="登录")
        self.login_btn.SetBackgroundColour(wx.Colour(39, 174, 96))
        self.login_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.login_btn.SetFont(btn_font)
        self.login_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        btn_bar.Add(self.login_btn, 0, wx.RIGHT, 8)

        self.skip_btn = wx.Button(self.main_section, size=(141, 38), style=wx.BORDER_NONE, label="直接使用")
        self.skip_btn.SetBackgroundColour(wx.Colour(240, 242, 246))
        self.skip_btn.SetForegroundColour(wx.Colour(100, 105, 115))
        self.skip_btn.SetFont(btn_font)
        self.skip_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.skip_btn.Bind(wx.EVT_BUTTON, self.on_skip)
        btn_bar.Add(self.skip_btn, 0)
        mvs.Add(btn_bar, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        bottom_bar = wx.BoxSizer(wx.HORIZONTAL)
        self.remember_cb = wx.CheckBox(self.main_section, label="记住密码，自动登录")
        self.remember_cb.SetValue(False)
        self.remember_cb.SetForegroundColour(wx.Colour(100, 105, 115))
        self.remember_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        bottom_bar.Add(self.remember_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        bottom_bar.AddStretchSpacer()

        self.activate_link = wx.StaticText(self.main_section, label="激活账号 →")
        self.activate_link.SetForegroundColour(wx.Colour(50, 80, 140))
        self.activate_link.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.activate_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.activate_link.Bind(wx.EVT_LEFT_DOWN, self.on_open_activate)
        bottom_bar.Add(self.activate_link, 0, wx.ALIGN_CENTER_VERTICAL)
        mvs.Add(bottom_bar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.error_label = wx.StaticText(self.main_section, label="")
        self.error_label.SetForegroundColour(wx.Colour(192, 57, 43))
        self.error_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        mvs.Add(self.error_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)

        self.main_section.SetSizer(mvs)
        vs.Add(self.main_section, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 26)

        panel.SetSizer(vs)
        ds = wx.BoxSizer(wx.VERTICAL)
        ds.Add(panel, 1, wx.EXPAND)
        self.SetSizer(ds)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        self._show_loading()
        wx.CallAfter(self._start_auto_login)

    def _show_loading(self):
        self.main_section.Hide()
        self.loading_panel.Show()
        self.Layout()
        self.Fit()

    def _show_login(self):
        self.loading_panel.Hide()
        self.main_section.Show()
        cached = self.app._load_cached()
        if cached.get("username"):
            self.user_input.SetValue(cached.get("username", ""))
            self.pass_input.SetValue(cached.get("password", ""))
        self.remember_cb.SetValue(cached.get("auto_login", False))
        self.Layout()
        self.Fit()

    def on_cancel_auto(self, event):
        self._cancelled = True

    def _end_modal(self, result):
        try:
            self.EndModal(result)
        except:
            wx.CallAfter(self._end_modal, result)

    def _start_auto_login(self):
        self._cancelled = False
        if self._skip_auto:
            wx.CallAfter(self._show_login)
            return

        cached = self.app._load_cached()

        if not cached or not cached.get("auto_login"):
            wx.CallAfter(self._show_login)
            return

        if not cached.get("username") or not cached.get("password"):
            self.app.user_info = {"username": "", "has_script": "free", "end_time": "2199-12-30 23:59:59", "token": ""}
            self._end_modal(wx.ID_OK)
            return

        def do_login():
            return self.app.do_login(cached["username"], cached["password"], True)

        def on_result(result):
            if self._cancelled:
                self._show_login()
                return
            if result["success"]:
                self.EndModal(wx.ID_OK)
            else:
                self._show_login()

        t = threading.Thread(target=lambda: wx.CallAfter(on_result, do_login()), daemon=True)
        t.start()

    def on_login(self, event):
        username = self.user_input.GetValue().strip()
        password = self.pass_input.GetValue().strip()
        if not username or not password:
            self.error_label.SetLabel("请输入账号和密码")
            return
        result = self.app.do_login(username, password, self.remember_cb.GetValue())
        if result["success"]:
            self.EndModal(wx.ID_OK)
        else:
            self.error_label.SetLabel(result["error"])

    def on_skip(self, event):
        self.app._save_cached("", "", self.remember_cb.GetValue())
        self.EndModal(wx.ID_OK)

    def on_open_activate(self, event):
        dlg = ActivateDialog(self.app, self.user_input.GetValue(), self.pass_input.GetValue(), self.remember_cb.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.EndModal(wx.ID_OK)
        else:
            self.user_input.SetValue(dlg.user_input.GetValue())
            self.pass_input.SetValue(dlg.pass_input.GetValue())
            self.remember_cb.SetValue(dlg.remember_cb.GetValue())
        dlg.Destroy()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.on_login(None)
        else:
            event.Skip()


class ActivateDialog(wx.Dialog):
    def __init__(self, app, seed_user="", seed_pass="", seed_remember=False):
        super().__init__(None, title="激活账号", size=(360, 340), pos=(200, 60),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.app = app

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        vs = wx.BoxSizer(wx.VERTICAL)

        header = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(panel, size=(60, 26), style=wx.BORDER_NONE, label="← 返回")
        back_btn.SetBackgroundColour(wx.Colour(240, 242, 246))
        back_btn.SetForegroundColour(wx.Colour(100, 105, 115))
        back_btn.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        back_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        header.Add(back_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        header.AddStretchSpacer()

        title = wx.StaticText(panel, label="激活/注册账号")
        title.SetForegroundColour(wx.Colour(50, 80, 140))
        title.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        header.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        vs.Add(header, 0, wx.EXPAND | wx.ALL, 12)

        input_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")

        self.invite_input = wx.TextCtrl(panel, size=(290, 34))
        self.invite_input.SetHint("激活码 (选填，不填则注册免费账号)")
        self.invite_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.invite_input.SetFont(input_font)
        vs.Add(self.invite_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.user_input = wx.TextCtrl(panel, size=(290, 34))
        self.user_input.SetHint("账号")
        self.user_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.user_input.SetFont(input_font)
        vs.Add(self.user_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.pass_input = wx.TextCtrl(panel, size=(290, 34), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("密码")
        self.pass_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.pass_input.SetFont(input_font)
        vs.Add(self.pass_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.user_input.SetValue(seed_user)
        self.pass_input.SetValue(seed_pass)

        self.remember_cb = wx.CheckBox(panel, label="记住密码，自动登录")
        self.remember_cb.SetValue(seed_remember)
        self.remember_cb.SetForegroundColour(wx.Colour(100, 105, 115))
        self.remember_cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        vs.Add(self.remember_cb, 0, wx.ALIGN_CENTER | wx.BOTTOM, 6)

        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        self.action_btn = wx.Button(panel, size=(290, 38), style=wx.BORDER_NONE, label="激活/注册")
        self.action_btn.SetBackgroundColour(wx.Colour(50, 80, 140))
        self.action_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.action_btn.SetFont(btn_font)
        self.action_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.action_btn.Bind(wx.EVT_BUTTON, self.on_action)
        vs.Add(self.action_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.error_label = wx.StaticText(panel, label="")
        self.error_label.SetForegroundColour(wx.Colour(192, 57, 43))
        self.error_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        vs.Add(self.error_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)

        panel.SetSizer(vs)
        ds = wx.BoxSizer(wx.VERTICAL)
        ds.Add(panel, 1, wx.EXPAND)
        self.SetSizer(ds)

    def on_back(self, event):
        self.EndModal(wx.ID_CANCEL)

    def on_action(self, event):
        username = self.user_input.GetValue().strip()
        password = self.pass_input.GetValue().strip()
        invite = self.invite_input.GetValue().strip()

        if not username or not password:
            self.error_label.SetLabel("请输入账号和密码")
            return
        if len(username) < 3 or len(password) < 6:
            self.error_label.SetLabel("账号至少3位，密码至少6位")
            return

        remember = self.remember_cb.GetValue()

        if invite:
            result = self.app.do_activate(username, password, invite, remember)
        else:
            result = self.app.do_register(username, password, remember)

        if result["success"]:
            self.EndModal(wx.ID_OK)
        else:
            self.error_label.SetLabel(result["error"])


class ChangePasswordDialog(wx.Dialog):
    def __init__(self, app):
        super().__init__(None, title="修改密码", size=(340, 310), pos=(250, 80),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.app = app

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        vs = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="修改密码")
        title.SetForegroundColour(wx.Colour(50, 80, 140))
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vs.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 16)

        input_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑")

        self.user_input = wx.TextCtrl(panel, size=(260, 34))
        self.user_input.SetHint("账号")
        self.user_input.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.user_input.SetFont(input_font)
        vs.Add(self.user_input, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.old_pass = wx.TextCtrl(panel, size=(260, 34), style=wx.TE_PASSWORD)
        self.old_pass.SetHint("旧密码")
        self.old_pass.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.old_pass.SetFont(input_font)
        vs.Add(self.old_pass, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.new_pass = wx.TextCtrl(panel, size=(260, 34), style=wx.TE_PASSWORD)
        self.new_pass.SetHint("新密码")
        self.new_pass.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.new_pass.SetFont(input_font)
        vs.Add(self.new_pass, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        btn_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        action_btn = wx.Button(panel, size=(260, 36), style=wx.BORDER_NONE, label="修改密码")
        action_btn.SetBackgroundColour(wx.Colour(50, 80, 140))
        action_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        action_btn.SetFont(btn_font)
        action_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        action_btn.Bind(wx.EVT_BUTTON, self.on_change)
        vs.Add(action_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)

        self.error_label = wx.StaticText(panel, label="")
        self.error_label.SetForegroundColour(wx.Colour(192, 57, 43))
        self.error_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        vs.Add(self.error_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 4)

        panel.SetSizer(vs)
        ds = wx.BoxSizer(wx.VERTICAL)
        ds.Add(panel, 1, wx.EXPAND)
        self.SetSizer(ds)

    def on_change(self, event):
        username = self.user_input.GetValue().strip()
        old = self.old_pass.GetValue().strip()
        new = self.new_pass.GetValue().strip()
        if not username or not old or not new:
            self.error_label.SetLabel("请填写所有字段")
            return
        if len(new) < 6:
            self.error_label.SetLabel("新密码至少6位")
            return
        result = self._api("/api/change-password", {"username": username, "old_password": old, "new_password": new})
        if result.get("message"):
            self.app._save_cached(username, "", True)
            self.EndModal(wx.ID_OK)
        else:
            self.error_label.SetLabel(result.get("error", "修改失败"))

    def _api(self, path, body):
        headers = {}
        token = self.app.user_info.get("token", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            url = f"{self.app.BASE_URL}{path}"
            r = requests.post(url, json=body, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.json()
            try:
                return r.json()
            except:
                return {"error": "服务器错误"}
        except:
            return {"error": "网络错误"}


class NumberValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)

    def Clone(self):
        return NumberValidator()

    def Validate(self, win):
        text_ctrl = self.GetWindow()
        value = text_ctrl.GetValue()
        if value and not value.isdigit():
            wx.MessageBox("请输入数字", "错误", wx.OK | wx.ICON_ERROR)
            text_ctrl.SetBackgroundColour(wx.Colour(255, 230, 230))
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False
        else:
            text_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
            text_ctrl.Refresh()
            return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="梦幻三国脚本(OpenCV版)", size=(370, 420),
                          style=wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(
            wx.Icon(
                self.get_resource_path("serveAssets/images/script.ico"),
                wx.BITMAP_TYPE_ICO,
            )
        )
        self.SetPosition(wx.Point(10, 30))
        self.SetBackgroundColour(wx.Colour(243, 244, 248))

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(243, 244, 248))

        self.scriptName = ""
        self.heifengCount = ""
        self.lianyu_count = ""
        self.qingyuan_count = ""
        self.zhanhun_count = ""
        self.zhanhunFloor = ""
        self.zhanhunFloorNew = ""
        self.heifengFloor = ""
        self.choice_line = ""
        self.teammate1_pos = ""
        self.teammate2_pos = ""
        self.team_leader_pos = ""
        self.shihun_count = ""
        self.shihun_floor = ""
        self.addBloudFlag = False

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(8)

        row_top = wx.BoxSizer(wx.HORIZONTAL)
        self.dropdown = None
        lbl = wx.StaticText(self.panel, label="脚本")
        lbl.SetForegroundColour(wx.Colour(50, 80, 140))
        lbl.SetMinSize((36, -1))
        lbl.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        row_top.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.btn_settings = wx.Button(self.panel, size=(30, 30), style=wx.BORDER_NONE)
        self.btn_settings.SetBitmap(self._load_icon("btn_settings.png", 16))
        self.btn_settings.SetBackgroundColour(wx.Colour(215, 218, 226))
        self.btn_settings.SetForegroundColour(wx.Colour(50, 80, 140))
        self.btn_settings.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.btn_settings.Bind(wx.EVT_BUTTON, self.on_button_click)
        row_top.Add(self.btn_settings, 0, wx.ALIGN_CENTER_VERTICAL)

        self.btn_factory = wx.Button(self.panel, size=(30, 30), style=wx.BORDER_NONE)
        factory_bmp = wx.Bitmap(wx.Image(self.get_resource_path("serveAssets/images/menu_factory.png")).Scale(20, 20, wx.IMAGE_QUALITY_HIGH))
        self.btn_factory.SetBitmap(factory_bmp)
        self.btn_factory.SetBackgroundColour(wx.Colour(215, 218, 226))
        self.btn_factory.SetToolTip("ScriptFactory")
        self.btn_factory.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.btn_factory.Bind(wx.EVT_BUTTON, self.on_factory_click)
        row_top.Add(self.btn_factory, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        main_sizer.Add(row_top, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        def _ctrl_btn(name, bg, hotkey):
            vs = wx.BoxSizer(wx.VERTICAL)
            path = self.get_resource_path("serveAssets/images/" + name)
            bmp = wx.Bitmap(wx.Image(path).Scale(28, 28, wx.IMAGE_QUALITY_HIGH))
            btn = wx.Button(self.panel, size=(46, 46), style=wx.BORDER_NONE)
            btn.SetBitmap(bmp)
            btn.SetBackgroundColour(bg)
            btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            vs.Add(btn, 0, wx.ALIGN_CENTER)
            lb = wx.StaticText(self.panel, label=hotkey, style=wx.ALIGN_CENTER)
            lb.SetForegroundColour(wx.Colour(100, 105, 115))
            lb.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            vs.Add(lb, 0, wx.ALIGN_CENTER | wx.TOP, 2)
            return vs, btn

        bar = wx.BoxSizer(wx.HORIZONTAL)
        vs1, self.button_start = _ctrl_btn("btn_start.png", wx.Colour(39, 174, 96), "F1")
        self.Bind(wx.EVT_BUTTON, self.button_start_click, self.button_start)
        bar.Add(vs1, 0, wx.ALIGN_CENTER_VERTICAL)
        bar.AddStretchSpacer()
        vs2, self.button_pause = _ctrl_btn("btn_pause.png", wx.Colour(192, 57, 43), "F2")
        self.Bind(wx.EVT_BUTTON, self.button_pause_click, self.button_pause)
        bar.Add(vs2, 0, wx.ALIGN_CENTER_VERTICAL)
        bar.AddStretchSpacer()
        vs3, self.button_resume = _ctrl_btn("btn_resume.png", wx.Colour(41, 128, 185), "F3")
        self.Bind(wx.EVT_BUTTON, self.button_resume_click, self.button_resume)
        bar.Add(vs3, 0, wx.ALIGN_CENTER_VERTICAL)
        bar.AddStretchSpacer()
        vs4, self.button_stop = _ctrl_btn("btn_reset.png", wx.Colour(215, 218, 226), "F4")
        self.Bind(wx.EVT_BUTTON, self.button_stop_click, self.button_stop)
        bar.Add(vs4, 0, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(bar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(10)

        log_card = wx.Panel(self.panel)
        log_card.SetBackgroundColour(wx.Colour(240, 242, 246))
        lcs = wx.BoxSizer(wx.VERTICAL)

        log_header = wx.BoxSizer(wx.HORIZONTAL)
        log_lbl = wx.StaticText(log_card, label="● 运行日志")
        log_lbl.SetForegroundColour(wx.Colour(50, 80, 140))
        log_lbl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        log_header.Add(log_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        log_header.AddStretchSpacer()
        log_ts = wx.StaticText(log_card, label=datetime.now().strftime("%H:%M"))
        log_ts.SetForegroundColour(wx.Colour(140, 145, 155))
        log_ts.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        log_header.Add(log_ts, 0, wx.ALIGN_CENTER_VERTICAL)

        lcs.Add(log_header, 0, wx.EXPAND | wx.ALL, 8)
        lcs.AddSpacer(2)

        self.text_ctrl = wx.TextCtrl(log_card, size=(-1, 140), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)
        self.text_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.text_ctrl.SetForegroundColour(wx.Colour(40, 42, 50))
        self.text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        lcs.Add(self.text_ctrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        log_card.SetSizer(lcs)

        main_sizer.Add(log_card, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        btm = wx.BoxSizer(wx.HORIZONTAL)

        self.contact = wx.StaticText(self.panel, label="群 955753707")
        self.contact.SetForegroundColour(wx.Colour(100, 105, 115))
        self.contact.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))

        self.update_notify_panel = wx.Panel(self.panel, size=(8, 8))
        self.update_notify_panel.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.update_notify_panel.Hide()
        self.update_notify_panel.Bind(wx.EVT_PAINT, self.on_update_notify_paint)
        self.update_notify_panel.SetToolTip("有新版本可用")

        self.updateVersion = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        update_bmp = wx.Bitmap(wx.Image(self.get_resource_path("serveAssets/images/check_update.png")).Scale(18, 18, wx.IMAGE_QUALITY_HIGH))
        self.updateVersion.SetBitmap(update_bmp)
        self.updateVersion.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.updateVersion.SetToolTip("CheckUpdate")
        self.updateVersion.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.updateVersion.Bind(wx.EVT_BUTTON, self.on_update_link_click)

        btm.Add(self.contact, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
        btm.AddStretchSpacer()

        self.help_link = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        self.help_link.SetBitmap(self._load_icon("btn_help.png", 18))
        self.help_link.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.help_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.help_link.Bind(wx.EVT_BUTTON, self.on_help_link_click)
        btm.Add(self.help_link, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)

        self.changepw_btn = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        self.changepw_btn.SetBitmap(self._load_icon("btn_changepw.png", 18))
        self.changepw_btn.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.changepw_btn.SetToolTip("修改密码")
        self.changepw_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.changepw_btn.Bind(wx.EVT_BUTTON, self.on_change_password)
        btm.Add(self.changepw_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)

        self.logout_btn = wx.Button(self.panel, size=(26, 26), style=wx.BORDER_NONE)
        self.logout_btn.SetBitmap(self._load_icon("btn_logout.png", 18))
        self.logout_btn.SetBackgroundColour(wx.Colour(243, 244, 248))
        self.logout_btn.SetToolTip("退出登录")
        self.logout_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.logout_btn.Bind(wx.EVT_BUTTON, self.on_logout)
        btm.Add(self.logout_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)

        btm.Add(self.update_notify_panel, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        btm.Add(self.updateVersion, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 12)

        main_sizer.Add(btm, 0, wx.EXPAND | wx.BOTTOM, 10)
        self.panel.SetSizer(main_sizer)

        self.engine = None
        self.script_thread = None
        self.condition = threading.Condition()
        sys.stdout = self
        self.bind_hotkeys()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self._closing_soft = False
        self.game_name = ""
        self.teammate1_name = ""
        self.teammate2_name = ""
        self.mojingFloor = ""
        self.zhengdianFloor = ""
        self.afterZreo = ""
        self.richangSelection = []
        self.mac_address = ""
        self.has_script = "free"
        self.user_name = "免费用户"
        self.end_time = "2199-12-30 23:59:59"
        self.remote_info = None
        self.BASE_URL = "https://p01--script-serve--5yyh9pxyhqq4.code.run"
        self.current_version = self.get_current_version()
        self.update_notify_timer = None
        self.update_notify_visible = True
        self.userData = {}
        self._init_done = False

        has_choices = [
            "官渡", "魔镜", "日常", "黑风", "矿产", "龙岛",
            "龙王令", "引魔符", "49日常", "49战魂", "49整点",
            "帮派任务", "名将闯关", "怪物攻城", "挂机+整点",
            "西瓜保卫战", "战魂楼(精英)", "天外天传送符",
            "嗜血战场(精英)", "英魂秘境(精英)",
            "炼狱战魂楼", "战魂+红+整点", "战魂+红+魔镜+整点",
        ]
        try:
            from ScriptFactory import get_user_script_choices
            user_scripts = get_user_script_choices()
            has_choices = list(has_choices) + user_scripts
        except:
            pass
        self.dropdown = wx.ComboBox(self.panel, size=(-1, 34),
                                    choices=has_choices)
        self.Bind(wx.EVT_COMBOBOX, self.on_select_script, self.dropdown)
        self.dropdown.SetHint("选择执行脚本")
        row_top.Insert(1, self.dropdown, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.dropdown.SetBackgroundColour(wx.Colour(240, 242, 246))
        self.dropdown.SetForegroundColour(wx.Colour(40, 42, 50))
        self.dropdown.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))

    def _init_async(self):
        self.remote_info = self.check_server_update()
        self.mac_address = self.get_mac_address()
        app = wx.GetApp()
        self.user_name = app.user_info.get("username", "免费用户")
        self.has_script = app.user_info.get("has_script", "free")
        self.end_time = app.user_info.get("end_time", "2199-12-30 23:59:59")
        self._update_user_display()
        print(
            f"用户名：{self.user_name}\n有效期：{self.end_time}\n脚本权限：{self.has_script}")
        if self.is_virtual_machine():
            print("检测到虚拟机环境")
        wx.CallAfter(self._check_and_show_update)
        self._init_done = True

    def _update_user_display(self):
        pass

    def on_change_password(self, event):
        app = wx.GetApp()
        dlg = ChangePasswordDialog(app)
        if dlg.ShowModal() == wx.ID_OK:
            dlg.Destroy()
            self._restart_to_login()
        else:
            dlg.Destroy()

    def on_logout(self, event):
        app = wx.GetApp()
        dlg = wx.MessageDialog(self, "退出登录将重置正在运行的脚本，是否继续？", "退出登录",
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() != wx.ID_YES:
            dlg.Destroy()
            return
        dlg.Destroy()
        app.logout()
        self._restart_to_login()

    def _restart_to_login(self):
        try:
            keyboard.remove_all_hotkeys()
        except:
            pass
        if self.script_thread is not None and self.script_thread.is_alive():
            if self.engine is not None:
                self.engine.stopped = True
                self.engine.overed = True
            time.sleep(0.3)
        self._closing_soft = True
        self.Close()
        app = wx.GetApp()
        login = LoginWindow(app, skip_auto=True)
        result = login.ShowModal()
        login.Destroy()
        if result != wx.ID_OK:
            app.Exit()
            sys.exit(0)
        frame = MyFrame()
        frame.Show()
        threading.Thread(target=frame._init_async, daemon=True).start()

    def _load_icon(self, name, size):
        path = self.get_resource_path("serveAssets/images/" + name)
        img = wx.Image(path).Scale(size, size, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

    def check_server_update(self):
        try:
            url = f"{wx.GetApp().BASE_URL}/api/version"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"[错误] 检查更新失败: {e}")
            return None

    def get_mac_address(self):
        try:
            import psutil
            interfaces = psutil.net_if_addrs()
            for interface_name, interface_addresses in interfaces.items():
                for address in interface_addresses:
                    if str(address.family) == "AddressFamily.AF_LINK":
                        return address.address
            return "MAC address not found"
        except Exception:
            try:
                import uuid
                return ":".join(["{:02x}".format((uuid.getnode() >> e) & 0xFF) for e in range(0, 8 * 6, 8)][::-1])
            except:
                return ""

    def is_virtual_machine(self):
        try:
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creation_flags = subprocess.CREATE_NO_WINDOW
            else:
                startupinfo = None
                creation_flags = 0

            try:
                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle",
                    "Hidden",
                    "-Command",
                    "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                ]
                output = subprocess.check_output(
                    cmd,
                    shell=False,
                    text=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                    startupinfo=startupinfo,
                    creationflags=creation_flags,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                try:
                    cmd = [
                        "powershell",
                        "-NoProfile",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        "Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty Manufacturer, Model | Out-String",
                    ]
                    output = subprocess.check_output(
                        cmd,
                        shell=False,
                        text=True,
                        stderr=subprocess.DEVNULL,
                        timeout=5,
                        startupinfo=startupinfo,
                        creationflags=creation_flags,
                    )
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    import platform
                    output = f"{platform.system()} {platform.machine()}"

            vm_keywords = [
                "VMware",
                "VirtualBox",
                "KVM",
                "QEMU",
                "Xen",
                "Bochs",
                "Hyper-V",
                "Microsoft Corporation",
            ]
            output_upper = output.upper()
            return any(keyword.upper() in output_upper for keyword in vm_keywords)
        except Exception:
            return False

    def is_user_valid(self):
        current_time = datetime.now()
        for user in self.userData:
            if self.mac_address in user.get("user_mac", ""):
                expiration_time = datetime.strptime(user["end_time"],
                                                    "%Y-%m-%d %H:%M:%S")
                if current_time > expiration_time:
                    return False
                else:
                    self.user_name = user["user_name"]
                    self.end_time = user["end_time"]
                    self.has_script = user["has_script"]
                    return True
        return False

    def on_help_link_click(self, event):
        content = [
            "使用说明：(每一条都很必要)",
            "1.第一次脚本需要使用管理员模式开启；",
            "2.脚本启动之前填入游戏名称(360大厅主页左侧边栏设置的游戏名称)；",
            "3.脚本关闭之前先点重置，如果卡住了一直点右上角x号即可关闭；",
            "4.请将游戏画面缩放到900*580（使用键盘Ctrl+鼠标滚轮调整）；",
            "5.脚本如果出现被杀毒软件清掉，可以新建一个文件夹，将脚本放到文件夹中，给文件夹添加信任即可。",
            "脚本说明：",
            "1.日常勾选了的就会去打，镜勾选之后日常结束会去打魔镜，卖是卖藏宝图操作，V勾选红跟英魂打7次，不勾选打5次，",
            "整勾选是新模式日常，要选择整点才能启动，会自动去打整点，不会退出副本，49日常结束默认打49整点，日常结束默认打官渡；",
            "2.0点后执行的脚本选了之后，晚上0点整点打完之后会去执行对应脚本，选择名将闯关下午3点，晚上9点整点之后会去打名将闯关；",
            "3.队友名称在多开并且多开的号已经拆分了的情况下再填，填的是360游戏大厅设置的小号名称，绑定成功的小号会在队友对话框发送1；",
            "4.黑风/矿产次数填多少次打多少次，打完自动去官渡；",
            "6.挂机+整点，使用之前打开查看副本，点一下需要打的副本，然后启动脚本即可；",
            "7.保存数据之后会在脚本同级文件夹生成一个data.txt，下次使用脚本直接点击读取即可自动填入；",
            "8.日常顺序是：战魂楼精英=>炼狱战魂楼=>溶洞=>炼丹=>五行=>云游精英=>名将挑战赛=>八门精英=>老鼠精英=>英魂=>三顾茅庐=>红=>青渊=>帮派任务=>官渡精英;",
            "9.自动战斗点击之后，战魂楼28，29层会自己战斗；",
            "10.整点全打为飞过去打页面上能找到的怪物，走路打九黎族祭坛，魔魂山，魔谷西三个地图的怪物。",
            "常见问题：",
            "1.点开始脚本没任何反应：使用管理员打开脚本；",
            "2.点开始之后提示无效窗口：务必保证输入的没问题，360最新版的只能绑定第一个打开的窗口；",
            "3.脚本关了一直提示未找到句柄窗口：点击重置即可；",
            "4.卡在副本进门位置不动：务必多开变身卡。",
        ]
        images = [
            self.get_resource_path("serveAssets/images/shuoming1.bmp"),
            self.get_resource_path("serveAssets/images/shuoming2.bmp"),
            self.get_resource_path("serveAssets/images/shuoming3.bmp"),
            self.get_resource_path("serveAssets/images/shuoming4.bmp"),
        ]
        dialog = HelpDialog(self, "说明", content, images)
        dialog.ShowModal()
        dialog.Destroy()

    def get_current_version(self):
        return "26.1.2"

    def check_and_update_notify_status(self):
        self.stop_update_notify_blink()
        if not self.remote_info or "version" not in self.remote_info:
            if hasattr(self, "update_notify_panel"):
                self.update_notify_panel.Hide()
            return
        latest_version = self.remote_info["version"]
        if self.current_version != latest_version:
            if hasattr(self, "update_notify_panel"):
                self.update_notify_panel.Show()
        else:
            if hasattr(self, "update_notify_panel"):
                self.update_notify_panel.Hide()

    def _check_and_show_update(self):
        self.check_and_update_notify_status()
        if self.remote_info and "version" in self.remote_info:
            latest_version = self.remote_info["version"]
            if self.current_version != latest_version:
                dlg = UpdateDialog(self, self.current_version, self.remote_info)
                dlg.ShowModal()
                dlg.Destroy()

    def on_factory_click(self, event):
        try:
            from ScriptFactory import ScriptFactoryDialog
            dlg = ScriptFactoryDialog(parent_frame=self)
            dlg.Show()
        except Exception as e:
            import traceback
            traceback.print_exc()
            wx.MessageBox("ScriptFactory启动失败: " + str(e), "错误", wx.OK | wx.ICON_ERROR)

    def on_update_link_click(self, event):
        self.stop_update_notify_blink()
        if self.remote_info:
            version = self.remote_info.get("version", "未知")
            changelog = self.remote_info.get("changelog", "无更新说明")
            msg = f"最新版本: {version}\n\n更新内容:\n{changelog}\n\n当前版本: {self.current_version}"
            wx.MessageBox(msg, "版本更新", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("无法获取更新信息", "版本更新", wx.OK | wx.ICON_WARNING)
        self.check_and_update_notify_status()

    def start_update_notify_blink(self):
        if self.update_notify_timer is None:
            self.update_notify_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._on_update_notify_blink,
                      self.update_notify_timer)
        self.update_notify_timer.Start(500)

    def _on_update_notify_blink(self, event):
        self.update_notify_visible = not self.update_notify_visible
        if self.update_notify_visible:
            self.update_notify_panel.Show()
        else:
            self.update_notify_panel.Hide()

    def stop_update_notify_blink(self):
        if self.update_notify_timer and self.update_notify_timer.IsRunning():
            self.update_notify_timer.Stop()

    def on_update_notify_paint(self, event):
        dc = wx.PaintDC(self.update_notify_panel)
        size = self.update_notify_panel.GetSize()
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            radius = 6.0
            center_x = size.width / 2.0
            center_y = size.height / 2.0
            brush = gc.CreateBrush(wx.Brush(wx.Colour(103, 194, 58)))
            gc.SetBrush(brush)
            gc.DrawEllipse(center_x - radius, center_y - radius, radius * 2,
                           radius * 2)
        else:
            radius = 6
            center_x = size.width // 2
            center_y = size.height // 2
            dc.SetBrush(wx.Brush(wx.Colour(103, 194, 58)))
            dc.SetPen(wx.Pen(wx.Colour(103, 194, 58), 1))
            dc.DrawCircle(center_x, center_y, radius)

    def get_resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def on_button_click(self, event):
        dialog = MyDialog(self, self.has_script)
        if self.game_name:
            dialog.team_leader_text.SetValue(self.game_name)
            dialog.number_input.SetValue(self.heifengCount)
            dialog.choiceCeng.SetValue(self.zhanhunFloor)
            dialog.choiceZhanHunCeng.SetValue(self.zhanhunFloorNew)
            dialog.choiceMojing.SetValue(self.mojingFloor)
            dialog.choiceZhengdian.SetValue(self.zhengdianFloor)
            dialog.choiceHeifeng.SetValue(self.heifengFloor)
            dialog.choiceAfterZreo.SetValue(self.afterZreo)
            dialog.teammate1_text.SetValue(self.teammate1_name)
            dialog.teammate2_text.SetValue(self.teammate2_name)
            dialog.choice_line.SetValue(self.choice_line)
            dialog.teammate1_pos.SetValue(self.teammate1_pos)
            dialog.teammate2_pos.SetValue(self.teammate2_pos)
            dialog.team_leader_pos.SetValue(self.team_leader_pos)
            dialog.lianyu_count.SetValue(self.lianyu_count)
            dialog.qingyuan_count.SetValue(self.qingyuan_count)
            dialog.zhanhun_count.SetValue(self.zhanhun_count)
            dialog.shihun_count.SetValue(self.shihun_count)
            dialog.choiceShiHunCeng.SetValue(self.shihun_floor)
            if self.richangSelection:
                for cb in dialog.check_boxes:
                    if cb.GetLabel() in self.richangSelection:
                        cb.SetValue(True)
                    else:
                        cb.SetValue(False)
            if self.addBloudFlag:
                dialog.addBloudBtn.Hide()
                dialog.closeBloudBtn.Show()
            else:
                dialog.addBloudBtn.Show()
                dialog.closeBloudBtn.Hide()
        if dialog.ShowModal() == wx.ID_OK:
            print("当前游戏名称：" + self.game_name)
        dialog.Destroy()

    def write(self, text):
        if wx.GetApp() and wx.GetApp().IsMainLoopRunning():
            wx.CallAfter(self._write_text, text)
        else:
            try:
                self._write_text(text)
            except Exception:
                pass

    def _write_text(self, text):
        try:
            if hasattr(self, "text_ctrl") and self.text_ctrl:
                self.text_ctrl.WriteText(text)
        except Exception:
            pass

    def print_and_speak(self, text):
        print(text)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    def bind_hotkeys(self):
        keyboard.add_hotkey("F1", lambda: wx.CallAfter(self.start_script))
        keyboard.add_hotkey("F2", lambda: wx.CallAfter(self.pause_script))
        keyboard.add_hotkey("F3", lambda: wx.CallAfter(self.resume_script))
        keyboard.add_hotkey("F4", lambda: wx.CallAfter(self.stop_script))
        keyboard.add_hotkey("F9", lambda: self.force_quit())

    def start_script(self):
        if self.script_thread is not None and self.script_thread.is_alive():
            print("检测到已有线程在运行，先停止...")
            self.stop_script()
            time.sleep(0.5)

        if not self.scriptName:
            wx.MessageBox("请先选择脚本！", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not self.game_name:
            wx.MessageBox("请输入游戏名称！", "Error", wx.OK | wx.ICON_ERROR)
            return

        script_name = self.scriptName
        entry = SCRIPT_REGISTRY.get(script_name)
        if not entry:
            if script_name.startswith("📝 "):
                user_script_name = script_name[2:].strip()
                from ScriptEngine import ScriptEngine
                config = ScriptEngine.load_config(user_script_name)
                if config:
                    print("开始脚本！")
                    wx.CallAfter(self.print_and_speak, "脚本已启动")
                    self.button_start.Disable()

                    def run_user():
                        try:
                            engine = GameEngine()
                            engine.condition = self.condition
                            self.engine = engine
                            engine.scriptName = script_name
                            engine.zhengdianFloor = self.zhengdianFloor
                            engine.mojingFloor = self.mojingFloor
                            engine.heifengFloor = self.heifengFloor
                            engine.afterZreo = self.afterZreo
                            engine.heifengCount = int(self.heifengCount) if self.heifengCount and self.heifengCount.isdigit() else 0
                            engine.qingyuanCount = int(self.qingyuan_count) if self.qingyuan_count and self.qingyuan_count.isdigit() else 0
                            engine.zhanhunCount = int(self.zhanhun_count) if self.zhanhun_count and self.zhanhun_count.isdigit() else 0
                            engine.lianyuCount = int(self.lianyu_count) if self.lianyu_count and self.lianyu_count.isdigit() else 0
                            engine.shihunCount = int(self.shihun_count) if self.shihun_count and self.shihun_count.isdigit() else 0
                            engine.zhanhunFloor = self.zhanhunFloor
                            engine.zhanhunFloorNew = self.zhanhunFloorNew
                            engine.shihunFloor = self.shihun_floor
                            engine.richangSelection = self.richangSelection
                            engine.addBloudFlag = self.addBloudFlag
                            engine.line = self.choice_line
                            engine.teammate1_pos = self.teammate1_pos
                            engine.teammate2_pos = self.teammate2_pos
                            engine.team_leader_pos = self.team_leader_pos
                            engine._speak_zhengdian = lambda: wx.CallAfter(self.print_and_speak, "整点时间到")
                            hwnd = engine.find_window(self.game_name)
                            if not hwnd:
                                wx.CallAfter(wx.MessageBox, "未找到游戏窗口：" + self.game_name, "错误",
                                             wx.OK | wx.ICON_ERROR)
                                return
                            from ya_engine import GameWindow
                            engine.main_win = GameWindow(hwnd)
                            engine.windows["main"] = engine.main_win
                            if self.teammate1_name:
                                hwnd1 = engine.find_window(self.teammate1_name)
                                if hwnd1:
                                    engine.team1_win = GameWindow(hwnd1)
                                    engine.windows["team1"] = engine.team1_win
                            if self.teammate2_name:
                                hwnd2 = engine.find_window(self.teammate2_name)
                                if hwnd2:
                                    engine.team2_win = GameWindow(hwnd2)
                                    engine.windows["team2"] = engine.team2_win

                            class EngineAdapter:
                                def __init__(self, engine):
                                    self.engine = engine
                                def MoveTo(self, x, y):
                                    win = self.engine._get_window("main")
                                    if win:
                                        win.input.move_to(x, y)
                                def LeftClick(self):
                                    win = self.engine._get_window("main")
                                    if win:
                                        win.input.left_click(0, 0)

                            engine.dm = EngineAdapter(engine)
                            se = ScriptEngine(engine, config)
                            se.run()
                        except RuntimeError:
                            print("脚本已停止\n")
                        except Exception as e:
                            import traceback
                            tb = traceback.format_exc()
                            print(tb)
                            wx.CallAfter(wx.MessageBox, "脚本异常：" + str(e) + "\n\n" + tb, "错误", wx.OK | wx.ICON_ERROR)
                        finally:
                            print("脚本执行结束\n")
                            wx.CallAfter(self.button_start.Enable)

                    self.script_thread = threading.Thread(target=run_user, daemon=True)
                    self.script_thread.start()
                    return
                else:
                    wx.MessageBox("未找到脚本配置：" + script_name, "错误", wx.OK | wx.ICON_ERROR)
                    return
            else:
                wx.MessageBox("未找到脚本：" + script_name, "错误", wx.OK | wx.ICON_ERROR)
                return
        script_fn = entry[0]

        print("开始脚本！")
        wx.CallAfter(self.print_and_speak, "脚本已启动")
        self.button_start.Disable()

        def run():
            try:
                engine = GameEngine()
                engine.condition = self.condition
                self.engine = engine
                engine.scriptName = script_name
                engine.zhengdianFloor = self.zhengdianFloor
                engine.mojingFloor = self.mojingFloor
                engine.heifengFloor = self.heifengFloor
                engine.afterZreo = self.afterZreo
                engine.heifengCount = int(self.heifengCount) if self.heifengCount and self.heifengCount.isdigit() else 0
                engine.qingyuanCount = int(self.qingyuan_count) if self.qingyuan_count and self.qingyuan_count.isdigit() else 0
                engine.zhanhunCount = int(self.zhanhun_count) if self.zhanhun_count and self.zhanhun_count.isdigit() else 0
                engine.lianyuCount = int(self.lianyu_count) if self.lianyu_count and self.lianyu_count.isdigit() else 0
                engine.shihunCount = int(self.shihun_count) if self.shihun_count and self.shihun_count.isdigit() else 0
                engine.zhanhunFloor = self.zhanhunFloor
                engine.zhanhunFloorNew = self.zhanhunFloorNew
                engine.shihunFloor = self.shihun_floor
                engine.richangSelection = self.richangSelection
                engine.addBloudFlag = self.addBloudFlag
                engine.line = self.choice_line
                engine.teammate1_pos = self.teammate1_pos
                engine.teammate2_pos = self.teammate2_pos
                engine.team_leader_pos = self.team_leader_pos
                engine._speak_zhengdian = lambda: wx.CallAfter(self.print_and_speak, "整点时间到")
                hwnd = engine.find_window(self.game_name)
                if not hwnd:
                    wx.CallAfter(wx.MessageBox, "未找到游戏窗口：" + self.game_name, "错误",
                                 wx.OK | wx.ICON_ERROR)
                    return
                from ya_engine import GameWindow
                engine.main_win = GameWindow(hwnd)
                engine.windows["main"] = engine.main_win
                if self.teammate1_name:
                    hwnd1 = engine.find_window(self.teammate1_name)
                    if hwnd1:
                        engine.team1_win = GameWindow(hwnd1)
                        engine.windows["team1"] = engine.team1_win
                if self.teammate2_name:
                    hwnd2 = engine.find_window(self.teammate2_name)
                    if hwnd2:
                        engine.team2_win = GameWindow(hwnd2)
                        engine.windows["team2"] = engine.team2_win
                script_fn(engine)
            except RuntimeError:
                print("脚本已停止\n")
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                print(tb)
                wx.CallAfter(wx.MessageBox, "脚本异常：" + str(e) + "\n\n" + tb, "错误", wx.OK | wx.ICON_ERROR)
            finally:
                print("脚本执行结束\n")
                wx.CallAfter(self.button_start.Enable)

        self.script_thread = threading.Thread(target=run, daemon=True)
        self.script_thread.start()

    def pause_script(self):
        if not self.scriptName:
            return
        print("暂停脚本！")
        if self.engine is not None:
            self.engine.stopped = True

    def resume_script(self):
        if not self.scriptName:
            return
        print("继续执行脚本！")
        if self.engine is not None:
            self.engine.stopped = False
            with self.condition:
                self.condition.notify_all()

    def stop_script(self):
        if not hasattr(self, "_resetting"):
            self._resetting = False
        if self._resetting:
            print("重置操作正在进行中，请勿重复点击...")
            return
        self._resetting = True
        print("开始重置脚本...")
        try:
            if self.engine is not None:
                self.engine.stopped = True
                self.engine.overed = True
                with self.condition:
                    self.condition.notify_all()
            self.condition = threading.Condition()
            self.engine = None
            self.script_thread = None
            self.scriptName = ""
            self.text_ctrl.SetValue("")
            if self.dropdown:
                self.dropdown.SetSelection(-1)
            print("任务已全部结束！")
            self.button_start.Enable()
        except Exception as e:
            print(f"重置脚本时发生错误: {e}")
        finally:
            self._resetting = False

    def force_quit(self):
        print("强制关闭脚本（F9快捷键）...")
        try:
            if self.engine is not None:
                self.engine.stopped = True
                self.engine.overed = True
            keyboard.unhook_all()
            os._exit(0)
        except Exception:
            os._exit(0)

    def on_close(self, event):
        print("正在关闭窗口...")
        try:
            if self.engine is not None:
                self.engine.stopped = True
                self.engine.overed = True
                with self.condition:
                    self.condition.notify_all()
            keyboard.unhook_all()
        except Exception:
            pass
        finally:
            try:
                self.Destroy()
            except Exception:
                pass
            if not self._closing_soft:
                try:
                    wx.GetApp().ExitMainLoop()
                except Exception:
                    pass
                os._exit(0)

    def on_select_script(self, event):
        self.scriptName = self.dropdown.GetValue()
        self.Layout()

    def button_start_click(self, event):
        self.start_script()

    def button_pause_click(self, event):
        self.pause_script()

    def button_resume_click(self, event):
        self.resume_script()

    def button_stop_click(self, event):
        self.button_stop.Disable()
        if self.engine is not None:
            self.engine.stopped = True
        try:
            self.stop_script()
        finally:
            wx.CallAfter(self.button_stop.Enable)

    def show_error_message(self, message):
        wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)


class MyDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(70, 75, 85)
    C_INPUT_BG = wx.Colour(255, 255, 255)

    def __init__(self, parent, has_script="free"):
        super().__init__(parent, title="游戏设置", size=(570, 610), pos=(200, 20))
        self.SetBackgroundColour(self.C_BG)
        self.frame = parent
        self.has_script = has_script
        self.config_file = "settings_config.json"
        self.schemes = OrderedDict()
        self.current_scheme = ""
        self.load_config()
        self.max_schemes = 10

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(8)

        def label(text, sz=36):
            l = wx.StaticText(panel, label=text)
            l.SetForegroundColour(self.C_MUTED)
            l.SetMinSize((sz, -1))
            return l

        top_row = wx.BoxSizer(wx.HORIZONTAL)
        l = label("方案", 36)
        l.SetForegroundColour(self.C_GOLD)
        top_row.Add(l, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.scheme_choice = wx.ComboBox(panel, size=(140, 30), choices=list(self.schemes.keys()))
        self.scheme_choice.SetHint("方案名称")
        self.scheme_choice.SetBackgroundColour(self.C_INPUT_BG)
        self.scheme_choice.SetForegroundColour(self.C_TEXT)
        if self.current_scheme and self.current_scheme in self.schemes:
            self.scheme_choice.SetValue(self.current_scheme)
        self.scheme_choice.Bind(wx.EVT_COMBOBOX, self.on_scheme_select)
        top_row.Add(self.scheme_choice, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        for name, fn in [("btn_save.png", self.on_save), ("btn_edit.png", self.on_update), ("btn_delete.png", self.on_delete)]:
            b = wx.Button(panel, size=(28, 28), style=wx.BORDER_NONE)
            b.SetBitmap(self._dialog_icon(name, 14))
            b.SetBackgroundColour(self.C_SURFACE)
            b.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            b.Bind(wx.EVT_BUTTON, fn)
            top_row.Add(b, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        main_sizer.Add(top_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        sec = lambda t: self._section_header(main_sizer, panel, t)
        sec("队伍")
        tm = wx.FlexGridSizer(cols=3, vgap=5, hgap=6)
        tm.AddGrowableCol(1, 1)

        for txt, attr_hint, is_leader in [("队长", "游戏名称", True), ("队友1", "队友1", False),
                                           ("队友2", "队友2", False)]:
            tm.Add(label(txt, 40), 0, wx.ALIGN_CENTER_VERTICAL)
            tc = wx.TextCtrl(panel, size=(-1, 28))
            tc.SetBackgroundColour(self.C_INPUT_BG)
            tc.SetForegroundColour(self.C_TEXT)
            tc.SetHint(attr_hint)
            if is_leader:
                self.team_leader_text = tc
                self.team_leader_text.Bind(wx.EVT_TEXT, self.on_text_change)
            elif "1" in txt:
                self.teammate1_text = tc
            else:
                self.teammate2_text = tc
            tm.Add(tc, 1, wx.EXPAND)
            b = wx.Button(panel, label="📍", size=(28, 28), style=wx.BORDER_NONE)
            b.SetBackgroundColour(self.C_SURFACE)
            b.SetForegroundColour(self.C_MUTED)
            b.Hide()
            tm.Add(b, 0, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(tm, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        sw_row = wx.BoxSizer(wx.HORIZONTAL)
        self.addBloudBtn = wx.Button(panel, label="🔴 自动战斗 关", size=(130, 30), style=wx.BORDER_NONE)
        self.addBloudBtn.SetBackgroundColour(self.C_SURFACE)
        self.addBloudBtn.SetForegroundColour(self.C_MUTED)
        self.addBloudBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.addBloudBtn.Bind(wx.EVT_BUTTON, self.addBloudFun)
        self.closeBloudBtn = wx.Button(panel, label="🟢 自动战斗 开", size=(130, 30), style=wx.BORDER_NONE)
        self.closeBloudBtn.SetBackgroundColour(wx.Colour(34, 153, 84))
        self.closeBloudBtn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.closeBloudBtn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.closeBloudBtn.Bind(wx.EVT_BUTTON, self.closeBloudFun)
        self.closeBloudBtn.Hide()
        sw_row.AddStretchSpacer()
        sw_row.Add(self.addBloudBtn, 0, wx.ALIGN_CENTER_VERTICAL)
        sw_row.Add(self.closeBloudBtn, 0, wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(sw_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.liubeiCountInputs = {}
        if self.has_script != "free":
            liubei_row = wx.FlexGridSizer(cols=6, vgap=4, hgap=4)
            for idx, lbl in [(0, "队长"), (1, "队友1"), (2, "队友2")]:
                lb = wx.StaticText(panel, label=lbl + "刘备")
                lb.SetForegroundColour(self.C_MUTED)
                lb.SetMinSize((50, -1))
                liubei_row.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL)
                tc = wx.TextCtrl(panel, size=(40, 26), validator=NumberValidator())
                tc.SetHint("0")
                tc.SetBackgroundColour(self.C_INPUT_BG)
                tc.SetForegroundColour(self.C_TEXT)
                self.liubeiCountInputs[idx] = tc
                liubei_row.Add(tc, 0, wx.ALIGN_CENTER_VERTICAL)
            main_sizer.Add(liubei_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

            self.persistentLiubeiCB = wx.CheckBox(panel, label="持久刘备")
            self.persistentLiubeiCB.SetForegroundColour(self.C_MUTED)
            self.persistentLiubeiCB.SetValue(True)
            main_sizer.Add(self.persistentLiubeiCB, 0, wx.LEFT | wx.RIGHT, 12)
        else:
            self.addBloudBtn.Hide()
            self.closeBloudBtn.Hide()

        main_sizer.AddSpacer(8)

        cols = wx.BoxSizer(wx.HORIZONTAL)

        f1 = wx.Panel(panel)
        f1.SetBackgroundColour(self.C_SURFACE)
        fs = wx.BoxSizer(wx.VERTICAL)
        t0 = wx.StaticText(f1, label="副本")
        t0.SetForegroundColour(self.C_GOLD)
        t0.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        fs.Add(t0, 0, wx.ALL, 6)

        self.choiceHeifeng = wx.ComboBox(f1, size=(-1, 28),
                                         choices=["大/80", "二/50", "刷龙珠", "大全程", "二全程"])
        self.choiceHeifeng.SetHint("黑风/龙岛")
        self.choiceHeifeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceHeifeng.SetForegroundColour(self.C_TEXT)
        self.choiceMojing = wx.ComboBox(f1, size=(-1, 28),
                                        choices=["迷幻境（虚实）", "狱境（黑白无常）", "刷张辽", "炎冰境"])
        self.choiceMojing.SetHint("魔镜层数")
        self.choiceMojing.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceMojing.SetForegroundColour(self.C_TEXT)
        self.number_input = wx.TextCtrl(f1, size=(-1, 28), validator=NumberValidator())
        self.number_input.SetHint("次数")
        self.number_input.SetBackgroundColour(self.C_INPUT_BG)
        self.number_input.SetForegroundColour(self.C_TEXT)
        self.qingyuan_count = wx.TextCtrl(f1, size=(-1, 28), validator=NumberValidator())
        self.qingyuan_count.SetHint("青渊次数")
        self.qingyuan_count.SetBackgroundColour(self.C_INPUT_BG)
        self.qingyuan_count.SetForegroundColour(self.C_TEXT)

        for lbl_text, ctrl in [("魔镜", self.choiceMojing), ("类型", self.choiceHeifeng),
                                ("次数", self.number_input), ("青渊", self.qingyuan_count)]:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f1, label=lbl_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            rs.Add(ctrl, 1, wx.EXPAND)
            fs.Add(rs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        f1.SetSizer(fs)
        cols.Add(f1, 1, wx.EXPAND | wx.RIGHT, 4)

        f2 = wx.Panel(panel)
        f2.SetBackgroundColour(self.C_SURFACE)
        fs2 = wx.BoxSizer(wx.VERTICAL)
        t2 = wx.StaticText(f2, label="战魂")
        t2.SetForegroundColour(self.C_GOLD)
        t2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        fs2.Add(t2, 0, wx.ALL, 6)

        self.choiceCeng = wx.ComboBox(f2, size=(-1, 28),
                                      choices=["20层", "21层", "22层", "23层", "24层", "25层"])
        self.choiceCeng.SetHint("战魂层数")
        self.choiceCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceCeng.SetForegroundColour(self.C_TEXT)
        self.zhanhun_count = wx.TextCtrl(f2, size=(55, 26), validator=NumberValidator())
        self.zhanhun_count.SetHint("次数")
        self.zhanhun_count.SetBackgroundColour(self.C_INPUT_BG)
        self.zhanhun_count.SetForegroundColour(self.C_TEXT)
        self.choiceZhanHunCeng = wx.ComboBox(f2, size=(-1, 28), choices=["26层", "27层"])
        self.choiceZhanHunCeng.SetHint("镇魂层数")
        self.choiceZhanHunCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceZhanHunCeng.SetForegroundColour(self.C_TEXT)
        self.lianyu_count = wx.TextCtrl(f2, size=(55, 26), validator=NumberValidator())
        self.lianyu_count.SetHint("次数")
        self.lianyu_count.SetBackgroundColour(self.C_INPUT_BG)
        self.lianyu_count.SetForegroundColour(self.C_TEXT)
        self.choiceShiHunCeng = wx.ComboBox(f2, size=(-1, 28), choices=["28层", "29层"])
        self.choiceShiHunCeng.SetHint("噬魂层数")
        self.choiceShiHunCeng.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceShiHunCeng.SetForegroundColour(self.C_TEXT)
        self.shihun_count = wx.TextCtrl(f2, size=(55, 26), validator=NumberValidator())
        self.shihun_count.SetHint("次数")
        self.shihun_count.SetBackgroundColour(self.C_INPUT_BG)
        self.shihun_count.SetForegroundColour(self.C_TEXT)

        for lbl_text, ctrl, narrow in [
            ("战魂", self.choiceCeng, False), ("次数", self.zhanhun_count, True),
            ("镇魂", self.choiceZhanHunCeng, False), ("次数", self.lianyu_count, True),
            ("噬魂", self.choiceShiHunCeng, False), ("次数", self.shihun_count, True),
        ]:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f2, label=lbl_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            rs.Add(ctrl, 1 if not narrow else 0, wx.EXPAND)
            fs2.Add(rs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        f2.SetSizer(fs2)
        cols.Add(f2, 1, wx.EXPAND | wx.RIGHT, 4)

        f3 = wx.Panel(panel)
        f3.SetBackgroundColour(self.C_SURFACE)
        fs3 = wx.BoxSizer(wx.VERTICAL)
        t3 = wx.StaticText(f3, label="整点")
        t3.SetForegroundColour(self.C_GOLD)
        t3.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        fs3.Add(t3, 0, wx.ALL, 6)

        zdc = ["蛇+全打", "龙+全打", "全打", "走路", "49整点", "49蛇+全打", "49龙+全打"]
        self.choiceZhengdian = wx.ComboBox(f3, size=(-1, 28), choices=zdc)
        self.choiceZhengdian.SetHint("整点")
        self.choiceZhengdian.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceZhengdian.SetForegroundColour(self.C_TEXT)
        self.choiceAfterZreo = wx.ComboBox(f3, size=(-1, 28),
                                           choices=["官渡", "魔镜", "日常", "49日常", "名将闯关"])
        self.choiceAfterZreo.SetHint("0点执行的脚本")
        self.choiceAfterZreo.SetBackgroundColour(self.C_INPUT_BG)
        self.choiceAfterZreo.SetForegroundColour(self.C_TEXT)

        for lbl_text, ctrl in [("整点", self.choiceZhengdian), ("0点", self.choiceAfterZreo)]:
            rs = wx.BoxSizer(wx.HORIZONTAL)
            lb = wx.StaticText(f3, label=lbl_text)
            lb.SetForegroundColour(self.C_MUTED)
            lb.SetMinSize((28, -1))
            rs.Add(lb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
            rs.Add(ctrl, 1, wx.EXPAND)
            fs3.Add(rs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)
        f3.SetSizer(fs3)
        cols.Add(f3, 1, wx.EXPAND)

        main_sizer.Add(cols, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        sec("日常")
        day_panel = wx.Panel(panel)
        day_panel.SetBackgroundColour(self.C_BG)
        grid = wx.FlexGridSizer(cols=11, vgap=4, hgap=3)
        grid.SetFlexibleDirection(wx.BOTH)
        grid.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.check_boxes = []
        opts = ["战", "镇", "噬", "溶", "丹", "五", "云", "名", "八", "鼠", "英", "庐", "红", "渊", "帮", "官",
                "镜", "卖", "V", "整", "全"]
        for opt in opts:
            cb = wx.CheckBox(day_panel, label=opt)
            cb.SetForegroundColour(self.C_MUTED)
            cb.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            if opt not in ["镜", "名", "卖", "噬", "整", "渊", "庐"]:
                cb.SetValue(True)
            if opt == "整" and self.has_script == "free":
                cb.Hide()
            self.check_boxes.append(cb)
            grid.Add(cb, 0, wx.ALIGN_CENTER_VERTICAL)
            if opt == "全":
                cb.Bind(wx.EVT_CHECKBOX, self.on_any_checkbox_change)
        day_panel.SetSizer(grid)
        main_sizer.Add(day_panel, 0, wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(6)

        self.button = wx.Button(panel, label="确定", size=(-1, 36), style=wx.BORDER_NONE)
        self.button.SetBackgroundColour(self.C_GOLD)
        self.button.SetForegroundColour(wx.Colour(255, 255, 255))
        self.button.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        self.button.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
        self.button.Disable()
        main_sizer.Add(self.button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)
        main_sizer.AddSpacer(8)

        self.choice_line = wx.ComboBox(panel, size=(60, 28), choices=["一线", "二线", "三线"])
        self.choice_line.Hide()
        self.team_leader_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.team_leader_pos.Hide()
        self.teammate1_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.teammate1_pos.Hide()
        self.teammate2_pos = wx.ComboBox(panel, size=(60, 28), choices=["1", "2", "3", "4"])
        self.teammate2_pos.Hide()

        panel.SetSizer(main_sizer)
        self.load_current_scheme()

    def _section_header(self, sizer, panel, text):
        l = wx.StaticText(panel, label=f"▸ {text}")
        l.SetForegroundColour(wx.Colour(50, 80, 140))
        l.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        sizer.Add(l, 0, wx.LEFT | wx.RIGHT, 12)
        sizer.AddSpacer(4)

    def _dialog_icon(self, name, size):
        path = self.frame.get_resource_path("serveAssets/images/" + name)
        img = wx.Image(path).Scale(size, size, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(img)

    def on_any_checkbox_change(self, event):
        cb = event.GetEventObject()
        if cb.GetValue():
            for cbItem in self.check_boxes:
                cbItem.SetValue(True)
        else:
            for cbItem in self.check_boxes:
                cbItem.SetValue(False)

    def addBloudFun(self, event):
        self.addBloudBtn.Hide()
        self.closeBloudBtn.Show()
        self.frame.addBloudFlag = True
        print("自动战斗标志已设置为 True")

    def closeBloudFun(self, event):
        self.addBloudBtn.Show()
        self.closeBloudBtn.Hide()
        self.frame.addBloudFlag = False
        print("自动战斗标志已设置为 False")

    def on_text_change(self, event):
        if self.team_leader_text.GetValue():
            self.button.Enable()
        else:
            self.button.Disable()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.schemes = OrderedDict(data.get("schemes", {}))
                    self.current_scheme = data.get("current", "")
            except Exception:
                self.schemes = OrderedDict()
                self.current_scheme = ""

    def save_config(self):
        data = {"schemes": dict(self.schemes), "current": self.current_scheme}
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=2)

    def collect_settings(self):
        selected_options = []
        for cb in self.check_boxes:
            if cb.GetValue():
                selected_options.append(cb.GetLabel())
        return {
            "selected_options": selected_options,
            "game_name": self.team_leader_text.GetValue(),
            "heifeng_count": self.number_input.GetValue(),
            "zhanhun_floor": self.choiceCeng.GetValue(),
            "mojing_floor": self.choiceMojing.GetValue(),
            "zhengdian_floor": self.choiceZhengdian.GetValue(),
            "heifeng_floor": self.choiceHeifeng.GetValue(),
            "after_zreo": self.choiceAfterZreo.GetValue(),
            "teammate1_text": self.teammate1_text.GetValue(),
            "teammate2_text": self.teammate2_text.GetValue(),
            "choiceZhanHunCeng": self.choiceZhanHunCeng.GetValue(),
            "choice_line": self.choice_line.GetValue(),
            "teammate1_pos": self.teammate1_pos.GetValue(),
            "teammate2_pos": self.teammate2_pos.GetValue(),
            "team_leader_pos": self.team_leader_pos.GetValue(),
            "lianyu_count": self.lianyu_count.GetValue(),
            "qingyuan_count": self.qingyuan_count.GetValue(),
            "zhanhun_count": self.zhanhun_count.GetValue(),
            "shihun_count": self.shihun_count.GetValue(),
            "shihun_floor": self.choiceShiHunCeng.GetValue(),
        }

    def apply_settings(self, settings):
        for cb in self.check_boxes:
            if cb.GetLabel() in settings.get("selected_options", ""):
                cb.SetValue(True)
            else:
                cb.SetValue(False)
        self.team_leader_text.SetValue(str(settings.get("game_name", "")))
        self.number_input.SetValue(str(settings.get("heifeng_count", "")))
        self.choiceCeng.SetValue(settings.get("zhanhun_floor", ""))
        self.choiceMojing.SetValue(settings.get("mojing_floor", ""))
        self.choiceZhengdian.SetValue(settings.get("zhengdian_floor", ""))
        self.choiceHeifeng.SetValue(settings.get("heifeng_floor", ""))
        self.choiceAfterZreo.SetValue(settings.get("after_zreo", ""))
        self.teammate1_text.SetValue(settings.get("teammate1_text", ""))
        self.teammate2_text.SetValue(settings.get("teammate2_text", ""))
        self.choiceZhanHunCeng.SetValue(settings.get("choiceZhanHunCeng", ""))
        self.choice_line.SetValue(settings.get("choice_line", ""))
        self.teammate1_pos.SetValue(settings.get("teammate1_pos", ""))
        self.teammate2_pos.SetValue(settings.get("teammate2_pos", ""))
        self.team_leader_pos.SetValue(settings.get("team_leader_pos", ""))
        self.lianyu_count.SetValue(settings.get("lianyu_count", ""))
        self.qingyuan_count.SetValue(settings.get("qingyuan_count", ""))
        self.zhanhun_count.SetValue(settings.get("zhanhun_count", ""))
        self.shihun_count.SetValue(settings.get("shihun_count", ""))
        self.choiceShiHunCeng.SetValue(settings.get("shihun_floor", ""))

    def on_scheme_select(self, event):
        scheme_name = self.scheme_choice.GetValue()
        if scheme_name in self.schemes:
            self.apply_settings(self.schemes[scheme_name])
            self.current_scheme = scheme_name

    def load_current_scheme(self):
        if self.current_scheme and self.current_scheme in self.schemes:
            self.apply_settings(self.schemes[self.current_scheme])
            self.scheme_choice.SetValue(self.current_scheme)

    def on_save(self, event):
        if len(self.schemes) >= self.max_schemes:
            wx.MessageBox(f"最多只能保存{self.max_schemes}个方案", "提示", wx.OK | wx.ICON_INFORMATION)
            return
        dlg = wx.TextEntryDialog(self, "请输入方案名称:", "保存方案")
        if dlg.ShowModal() == wx.ID_OK:
            scheme_name = dlg.GetValue().strip()
            if not scheme_name:
                wx.MessageBox("方案名称不能为空", "错误", wx.OK | wx.ICON_ERROR)
                return
            if scheme_name in self.schemes:
                confirm = wx.MessageBox(f"方案「{scheme_name}」已存在，是否覆盖？", "确认覆盖",
                                        wx.YES_NO | wx.ICON_QUESTION)
                if confirm != wx.YES:
                    return
            settings = self.collect_settings()
            self.schemes[scheme_name] = settings
            self.current_scheme = scheme_name
            choices = list(self.schemes.keys())
            self.scheme_choice.SetItems(choices)
            self.scheme_choice.SetValue(scheme_name)
            self.save_config()
            wx.MessageBox("方案保存成功", "成功", wx.OK | wx.ICON_INFORMATION)
        dlg.Destroy()

    def on_update(self, event):
        scheme_name = self.scheme_choice.GetValue().strip()
        if not scheme_name:
            wx.MessageBox("请先选择一个方案", "提示", wx.OK | wx.ICON_WARNING)
            return
        if scheme_name not in self.schemes:
            wx.MessageBox(f"方案「{scheme_name}」不存在，请先保存为新方案", "提示", wx.OK | wx.ICON_WARNING)
            return
        settings = self.collect_settings()
        self.schemes[scheme_name] = settings
        self.current_scheme = scheme_name
        self.save_config()
        wx.MessageBox("方案修改成功", "成功", wx.OK | wx.ICON_INFORMATION)

    def on_delete(self, event):
        scheme_name = self.scheme_choice.GetValue()
        if not scheme_name or scheme_name not in self.schemes:
            return
        confirm = wx.MessageBox(f"确定要删除方案 '{scheme_name}' 吗?", "确认删除",
                                wx.YES_NO | wx.ICON_QUESTION)
        if confirm == wx.YES:
            del self.schemes[scheme_name]
            choices = list(self.schemes.keys())
            self.scheme_choice.SetItems(choices)
            self.scheme_choice.SetValue(choices[0] if choices else "")
            if self.current_scheme == scheme_name:
                self.current_scheme = choices[0] if choices else ""
            if self.current_scheme and self.current_scheme in self.schemes:
                self.apply_settings(self.schemes[self.current_scheme])
            self.save_config()
            wx.MessageBox("方案已删除", "成功", wx.OK | wx.ICON_INFORMATION)

    def on_button_click(self, event):
        if not self.team_leader_text.GetValue().strip():
            wx.MessageBox("请先输入游戏名称", "提示", wx.OK | wx.ICON_WARNING)
            return
        parent = self.frame
        selected_options = []
        for cb in self.check_boxes:
            if cb.GetValue():
                selected_options.append(cb.GetLabel())
        parent.game_name = self.team_leader_text.GetValue()
        parent.heifengCount = self.number_input.GetValue() if self.number_input.GetValue() else ""
        parent.zhanhunFloor = self.choiceCeng.GetValue()
        parent.zhanhunFloorNew = self.choiceZhanHunCeng.GetValue()
        parent.heifengFloor = self.choiceHeifeng.GetValue()
        parent.afterZreo = self.choiceAfterZreo.GetValue()
        parent.mojingFloor = self.choiceMojing.GetValue()
        parent.zhengdianFloor = self.choiceZhengdian.GetValue()
        parent.richangSelection = selected_options
        parent.teammate1_name = self.teammate1_text.GetValue()
        parent.teammate2_name = self.teammate2_text.GetValue()
        parent.choice_line = self.choice_line.GetValue()
        parent.teammate1_pos = self.teammate1_pos.GetValue()
        parent.teammate2_pos = self.teammate2_pos.GetValue()
        parent.team_leader_pos = self.team_leader_pos.GetValue()
        parent.lianyu_count = self.lianyu_count.GetValue()
        parent.qingyuan_count = self.qingyuan_count.GetValue()
        parent.zhanhun_count = self.zhanhun_count.GetValue()
        parent.shihun_count = self.shihun_count.GetValue()
        parent.shihun_floor = self.choiceShiHunCeng.GetValue()
        if self.addBloudBtn.IsShown():
            parent.addBloudFlag = False
        else:
            parent.addBloudFlag = True
        parent.enablePersistentLiubei = self.persistentLiubeiCB.GetValue() if hasattr(self, "persistentLiubeiCB") else True
        parent.liubeiCounts = {}
        for idx in self.liubeiCountInputs:
            item = self.liubeiCountInputs[idx]
            if isinstance(item, int):
                parent.liubeiCounts[idx] = item
            else:
                val = item.GetValue()
                parent.liubeiCounts[idx] = int(val) if val.isdigit() else (1 if idx == 0 else 0)
        self.EndModal(wx.ID_OK)


class HelpDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(70, 75, 85)

    def __init__(self, parent, title, content, images):
        super(HelpDialog, self).__init__(
            parent, title=title, size=(800, 600), pos=(200, 20),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.SetBackgroundColour(self.C_BG)

        scroll = scrolled.ScrolledPanel(self, -1, style=wx.TAB_TRAVERSAL)
        scroll.SetBackgroundColour(self.C_BG)
        scroll.SetupScrolling(scroll_y=True, rate_y=20)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        title_panel = wx.Panel(scroll)
        title_panel.SetBackgroundColour(self.C_BG)
        title_sizer_b = wx.BoxSizer(wx.HORIZONTAL)
        title_text = wx.StaticText(title_panel, label=title)
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑")
        title_text.SetFont(title_font)
        title_text.SetForegroundColour(self.C_GOLD)
        title_sizer_b.Add(title_text, 1, wx.ALIGN_CENTER | wx.ALL, 12)
        title_panel.SetSizer(title_sizer_b)
        main_sizer.Add(title_panel, 0, wx.EXPAND)

        all_text = "\n\n".join(content)
        text_ctrl = wx.TextCtrl(scroll, value=all_text,
                                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.TE_NO_VSCROLL)
        text_ctrl.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        text_ctrl.SetForegroundColour(self.C_TEXT)
        text_ctrl.SetBackgroundColour(self.C_BG)
        dc = wx.ClientDC(text_ctrl)
        dc.SetFont(text_ctrl.GetFont())
        line_h = dc.GetCharHeight()
        lines = all_text.count('\n') + 1
        text_h = line_h * lines + 60
        main_sizer.Add(text_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        text_ctrl.SetMinSize((-1, min(text_h, 3000)))

        for idx, image_path in enumerate(images):
            try:
                image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                if image.IsOk():
                    img_panel = wx.Panel(scroll)
                    img_panel.SetBackgroundColour(self.C_SURFACE)
                    row = wx.BoxSizer(wx.HORIZONTAL)
                    dialog_width = self.GetSize().width
                    max_width = int(dialog_width * 0.85)
                    ow, oh = image.GetWidth(), image.GetHeight()
                    if ow > max_width:
                        nw, nh = max_width, int(oh * max_width / ow)
                    else:
                        nw, nh = ow, oh
                    image = image.Scale(nw, nh, wx.IMAGE_QUALITY_HIGH)
                    bitmap = wx.StaticBitmap(img_panel, -1, image.ConvertToBitmap())
                    row.Add(bitmap, 0, wx.ALL | wx.LEFT, 10)
                    img_panel.SetSizer(row)
                    main_sizer.Add(img_panel, 0, wx.EXPAND | wx.LEFT, 5)
                    if idx < len(images) - 1:
                        line = wx.StaticLine(scroll, style=wx.LI_HORIZONTAL)
                        main_sizer.Add(line, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
            except Exception as e:
                print(f"加载图片失败: {e}")

        button_panel = wx.Panel(scroll)
        button_panel.SetBackgroundColour(self.C_BG)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_button = wx.Button(button_panel, label="关闭", size=(100, 35), style=wx.BORDER_NONE)
        close_button.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        close_button.SetBackgroundColour(self.C_SURFACE)
        close_button.SetForegroundColour(self.C_TEXT)
        close_button.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        button_sizer.AddStretchSpacer()
        button_sizer.Add(close_button, 0, wx.ALL, 10)
        button_panel.SetSizer(button_sizer)
        main_sizer.Add(button_panel, 0, wx.EXPAND | wx.TOP, 8)

        scroll.SetSizer(main_sizer)

        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(scroll, 1, wx.EXPAND)
        self.SetSizer(dialog_sizer)


class UpdateDialog(wx.Dialog):
    C_BG = wx.Colour(243, 244, 248)
    C_SURFACE = wx.Colour(240, 242, 246)
    C_GOLD = wx.Colour(50, 80, 140)
    C_TEXT = wx.Colour(40, 42, 50)
    C_MUTED = wx.Colour(70, 75, 85)

    def __init__(self, parent, current_version, remote_info):
        super().__init__(parent, title="版本更新", size=(420, 380),
                         style=wx.DEFAULT_DIALOG_STYLE)
        self.SetBackgroundColour(self.C_BG)
        self.remote_info = remote_info
        self.current_version = current_version

        panel = wx.Panel(self)
        panel.SetBackgroundColour(self.C_BG)
        vs = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(panel, label="发现新版本!")
        title.SetForegroundColour(self.C_GOLD)
        title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vs.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 16)

        version_info = wx.Panel(panel)
        version_info.SetBackgroundColour(self.C_SURFACE)
        vis = wx.BoxSizer(wx.VERTICAL)

        cur_label = wx.StaticText(version_info, label=f"当前版本: {current_version}")
        cur_label.SetForegroundColour(self.C_MUTED)
        cur_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        vis.Add(cur_label, 0, wx.ALL, 6)

        new_version = remote_info.get("version", "未知")
        new_label = wx.StaticText(version_info, label=f"最新版本: {new_version}")
        new_label.SetForegroundColour(wx.Colour(39, 174, 96))
        new_label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        vis.Add(new_label, 0, wx.ALL, 6)

        version_info.SetSizer(vis)
        vs.Add(version_info, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        changelog = remote_info.get("changelog", "")
        if changelog:
            log_label = wx.StaticText(panel, label="更新内容:")
            log_label.SetForegroundColour(self.C_GOLD)
            log_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
            vs.Add(log_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 16)

            log_text = wx.TextCtrl(panel, size=(-1, 120), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE)
            log_text.SetValue(changelog)
            log_text.SetBackgroundColour(self.C_SURFACE)
            log_text.SetForegroundColour(self.C_TEXT)
            log_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
            vs.Add(log_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        btn_bar = wx.BoxSizer(wx.HORIZONTAL)
        download_btn = wx.Button(panel, size=(130, 36), style=wx.BORDER_NONE, label="下载更新")
        download_btn.SetBackgroundColour(wx.Colour(39, 174, 96))
        download_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        download_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="微软雅黑"))
        download_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        download_btn.Bind(wx.EVT_BUTTON, self.on_download)
        btn_bar.Add(download_btn, 0, wx.RIGHT, 10)

        later_btn = wx.Button(panel, size=(130, 36), style=wx.BORDER_NONE, label="稍后更新")
        later_btn.SetBackgroundColour(self.C_SURFACE)
        later_btn.SetForegroundColour(self.C_MUTED)
        later_btn.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="微软雅黑"))
        later_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        later_btn.Bind(wx.EVT_BUTTON, self.on_later)
        btn_bar.Add(later_btn, 0)

        vs.Add(btn_bar, 0, wx.ALIGN_CENTER | wx.ALL, 16)

        panel.SetSizer(vs)
        ds = wx.BoxSizer(wx.VERTICAL)
        ds.Add(panel, 1, wx.EXPAND)
        self.SetSizer(ds)

    def on_download(self, event):
        try:
            import webbrowser
            url = self.remote_info.get("download_url", "")
            if url:
                webbrowser.open(url)
            else:
                webbrowser.open("https://p01--script-serve--5yyh9pxyhqq4.code.run")
        except Exception:
            pass
        self.EndModal(wx.ID_OK)

    def on_later(self, event):
        self.EndModal(wx.ID_CANCEL)


if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
