import wx
from ui.MainWindowUI import MainWindowUI
from ConfigHolder import ConfigHolder

if __name__ == "__main__":
    ConfigHolder("etc/ater.ini")
    app = wx.App()
    frame = MainWindowUI("Ater").Show()
    app.MainLoop()