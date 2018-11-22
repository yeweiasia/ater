import wx
from wx.richtext import RichTextCtrl
from ConfigHolder import ConfigHolder

class TerminalTabPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.session = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        #TO-DO Termainl here

        self.outputCtrl = RichTextCtrl(self, -1, style=wx.TE_MULTILINE | wx.EXPAND | wx.BORDER_SUNKEN | wx.TE_DONTWRAP,
                             size=(800, 500))
        self.outputCtrl.Bind(wx.EVT_CHAR, self.OnChar)

        #TO-DO:load color schema from config
        self.outputCtrl.SetBackgroundColour(ConfigHolder().config.get('color', 'terminal_background'))

        sizer.Add(self.outputCtrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def appendText(self, text):
        self.outputCtrl.AppendText(text)

    def OnChar(self, event):

        event.Skip()
