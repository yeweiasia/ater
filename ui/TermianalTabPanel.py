import wx
from wx.richtext import RichTextCtrl
from wx.richtext import RichTextAttr
from ConfigHolder import ConfigHolder

class TerminalTabPanel(wx.Panel):

    def __init__(self, parent, sendToBackend):
        wx.Panel.__init__(self, parent=parent)
        self.sendToBackend = sendToBackend
        self.session = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        #TO-DO Termainl here

        self.outputCtrl = RichTextCtrl(self, -1, style=wx.TE_RICH2 | wx.TE_MULTILINE | wx.EXPAND | wx.BORDER_SUNKEN | wx.TE_DONTWRAP,
                             size=(800, 450))
        self.outputCtrl.Bind(wx.EVT_CHAR, self.OnChar)

        #TO-DO:load color schema from config
        self.outputCtrl.SetDefaultStyle(wx.TextAttr(ConfigHolder().config.get('color', 'default_text_color')))
        self.outputCtrl.SetBackgroundColour(ConfigHolder().config.get('color', 'terminal_background_color'))
        self.writeText("begin")

        sizer.Add(self.outputCtrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def writeText(self, text):
        self.outputCtrl.WriteText(text)

    def OnChar(self, event):
        self.sendToBackend(event.GetKeyCode())
        event.Skip()
