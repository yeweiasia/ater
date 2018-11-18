
import wx.aui as aui

class AterAuiNotebook(aui.AuiNotebook):

    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.parent = parent
        self.default_style = aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS
        self.SetWindowStyleFlag(self.default_style)

    def addPanel(self, label, panel, selected):
        self.AddPage(panel(self), label, selected)