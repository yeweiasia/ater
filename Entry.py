import wx
from ui.MainWindowUI import MainWindowUI

if __name__ == "__main__":
    app = wx.App()
    frame = MainWindowUI("Ater").Show()
    app.MainLoop()