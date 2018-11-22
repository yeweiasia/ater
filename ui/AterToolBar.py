import wx
from TermianalTabPanel import TerminalTabPanel


class AterToolBar():
    def __init__(self, parent):
        TBFLAGS = (wx.TB_HORIZONTAL |
                   wx.NO_BORDER |
                   wx.TB_FLAT)
        self.parent = parent
        self.toolbar = parent.CreateToolBar(TBFLAGS)

        btnNewSessionPng = wx.Bitmap("resource/new-session.png", wx.BITMAP_TYPE_PNG)
        btnNewSession = wx.BitmapButton(self.toolbar, id=wx.ID_ANY, bitmap=btnNewSessionPng, style=wx.NO_BORDER|wx.BU_EXACTFIT,
                                 size=(btnNewSessionPng.GetWidth() + 10, btnNewSessionPng.GetHeight() + 10))
        btnNewSession.Bind(wx.EVT_BUTTON, self.OnBtnNewSessionClicked)


        btnOpenSessionPng = wx.Bitmap("resource/open-session.png", wx.BITMAP_TYPE_PNG)
        btnOpenSession = wx.BitmapButton(self.toolbar, id=wx.ID_ANY, bitmap=btnOpenSessionPng,style=wx.NO_BORDER|wx.BU_EXACTFIT,
                                        size=(btnOpenSessionPng.GetWidth() + 10, btnOpenSessionPng.GetHeight() + 10))
        btnOpenSession.Bind(wx.EVT_BUTTON, self.OnBtnOpenSessionClicked)


        self.toolbar.AddControl(btnNewSession)
        self.toolbar.AddSeparator()
        self.toolbar.AddControl(btnOpenSession)
        self.toolbar.Realize()

    def OnBtnNewSessionClicked(self, event):
        self.parent.notebook.addPanel("tab-default", TerminalTabPanel, True)

    def OnBtnOpenSessionClicked(self,event):
        self.parent.notebook.addPanel("tab-default", TerminalTabPanel, True)