import wx

class SessionManager():

    def __init__(self, parent):
        self.parent = parent
        dlg = wx.TextEntryDialog(parent, 'Host', 'Connect to')
        dlg.SetValue("Default")
        if dlg.ShowModal() == wx.ID_OK:
            self.host = dlg.GetValue()
        dlg.Destroy()
