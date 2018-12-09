import wx
from wx.richtext import RichTextCtrl
from ConfigHolder import ConfigHolder
from ast import literal_eval
from colors import strip_color

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

        #TO-DO not safe
        rgbColour = literal_eval(ConfigHolder().config.get('color', 'default_text_color'))

        self.outputCtrl.SetDefaultStyle(wx.TextAttr(wx.Colour(rgbColour)))
        self.outputCtrl.SetBackgroundColour(ConfigHolder().config.get('color', 'terminal_background_color'))
        #self.writeText("begin")

        sizer.Add(self.outputCtrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def writeText(self, text):

        #TO-DO deal with text colour
        text = strip_color(text)
        self.outputCtrl.WriteText(text)

    def OnChar(self, event):
        self.sendToBackend(chr(event.GetKeyCode()))
        #event.Skip()
