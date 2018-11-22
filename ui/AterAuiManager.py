import wx.aui as aui


class AterAuiManager(aui.AuiManager):

    def __init__(self, managed_window):
        aui.AuiManager.__init__(self)
        self.SetManagedWindow(managed_window)