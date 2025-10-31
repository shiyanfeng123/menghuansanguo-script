import time
import wx
import psutil
import uuid


# 打包：pyinstaller -F -w .\getInfo.py


class DeviceInfoFrame(wx.Frame):
	def __init__(self):
		super().__init__(None, title="设备MAC 地址获取", size=(400, 200))
		panel = wx.Panel(self)

		vbox = wx.BoxSizer(wx.VERTICAL)

		self.info_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
		vbox.Add(self.info_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

		btn = wx.Button(panel, label="获取MAC 地址并复制")
		btn.Bind(wx.EVT_BUTTON, self.on_get_info)
		vbox.Add(btn, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

		panel.SetSizer(vbox)

	def on_get_info(self, event):
		hardware_serial = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 8 * 6, 8)][::-1])
		mac_address = self.get_mac_address()

		info_str = f"{hardware_serial}\n{mac_address}"
		self.info_text.SetValue(info_str)
		
		# 复制到剪切板
		self.copy_to_clipboard(info_str)
		time.sleep(0.5)
		# 提示用户
		wx.MessageBox("MAC地址已复制到剪切板！", "提示", wx.OK | wx.ICON_INFORMATION)
	
	def copy_to_clipboard(self, text):
		"""将文本复制到剪切板"""
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(wx.TextDataObject(text))
			wx.TheClipboard.Close()

	def get_mac_address(self):
		# 使用 psutil 获取所有网络接口信息
		interfaces = psutil.net_if_addrs()

		# 遍历接口信息，找到MAC地址
		for interface_name, interface_addresses in interfaces.items():
			for address in interface_addresses:
				if str(address.family) == "AddressFamily.AF_LINK":
					return address.address

		return "MAC address not found"


if __name__ == "__main__":
	app = wx.App(False)
	frame = DeviceInfoFrame()
	frame.Show(True)
	app.MainLoop()
