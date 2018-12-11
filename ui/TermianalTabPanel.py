import wx
from wx.richtext import RichTextCtrl
from ConfigHolder import ConfigHolder
from ast import literal_eval
from colors import strip_color

class TerminalTabPanel(wx.Panel):

    def __init__(self, parent, sendToBackend):
        wx.Panel.__init__(self, parent=parent)

        self.lastPosition = 0
        self.lastFreezePosition = 0
        self.commandSequence = ""
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

        if len(text) == 1 and ord(text) == 7:
            return

        #TO-DO deal with text colour
        text = strip_color(text)

        # if special key pressed, dealing with it, otherwise write to output
        if not self.dealingWithSpecialKey(text):
            self.outputCtrl.WriteText(text)

        self.lastPosition = self.outputCtrl.GetLastPosition()
        self.lastFreezePosition = self.lastPosition
        # scroll to the end of output
        #self.outputCtrl.SetScrollPos( wx.VERTICAL,self.outputCtrl.GetScrollRange(wx.VERTICAL))
        self.outputCtrl.ShowPosition(self.outputCtrl.GetLastPosition())


    def OnChar(self, event):

        keyCode = event.GetKeyCode()
        keyChar = chr(keyCode)
        # press enter to send command and clear the command sequence buffer
        if keyCode == 13:
            self.commandSequence = ""
        # ansi code 127 id DEL
        if keyCode > 32 and keyCode != 127:
            self.commandSequence += keyChar

        self.sendToBackend(keyChar)
        #event.Skip()

    def dealingWithSpecialKey(self, keyValue):
        # backspace
        if keyValue == '\b':
            lastPosition = self.outputCtrl.GetLastPosition()
            self.outputCtrl.Delete((lastPosition-2, lastPosition-1))
            return True

        return False