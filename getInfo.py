import wx
import uuid
import wmi
import psutil


class DeviceInfoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="设备信息及 MAC 地址获取", size=(400, 200))
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.info_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.info_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        btn = wx.Button(panel, label="获取设备信息及 MAC 地址")
        btn.Bind(wx.EVT_BUTTON, self.on_get_info)
        vbox.Add(btn, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

    def on_get_info(self, event):
        c = wmi.WMI()
        for item in c.Win32_BaseBoard():
            hardware_serial = item.SerialNumber
        mac_address = self.get_mac_address()

        info_str = f"硬件序列号：{hardware_serial}\nMAC 地址：{mac_address}"
        self.info_text.SetValue(info_str)

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
