# -*- coding: utf-8 -*-
import sys

sys.coinit_flags = 0

from ya_gui import App, LoginWindow, MyFrame
import wx


def main():
    application = App()

    login = LoginWindow(application)
    result = login.ShowModal()
    login.Destroy()
    if result != wx.ID_OK:
        application.Exit()
        sys.exit(0)

    frame = MyFrame()
    frame.Show()
    application.MainLoop()


if __name__ == "__main__":
    main()
