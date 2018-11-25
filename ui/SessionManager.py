import wx

class SessionManager():

    def __init__(self, parent):
        self.parent = parent
        self.sessionManagerDialog = SessionManagerDialog(parent, "New Session")
        self.sessionManagerDialog.CenterOnParent()
        self.sessionManagerDialog.ShowModal()

class SessionManagerDialog(wx.Dialog):

    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY, title=title, size=(450, 600))
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.parent = parent
        panel = wx.Panel(self)
        hostLbl = wx.StaticText(panel, -1, "Host:")
        self.host = wx.TextCtrl(panel, -1, "")
        portLbl = wx.StaticText(panel, -1, "Port:")
        self.port = wx.TextCtrl(panel, -1, "22")
        usernameLbl = wx.StaticText(panel, -1, "Username:")
        self.username = wx.TextCtrl(panel, -1, "")
        passwordLbl = wx.StaticText(panel, -1, "Password:")
        self.password = wx.TextCtrl(panel, -1, "", style=wx.TE_PASSWORD)
        self.btn = wx.Button(panel, wx.ID_OK, label="ok", size=(50, 20), pos=(200, 550))
        goBtn = wx.Button(panel, -1, "Go")
        clearBtn = wx.Button(panel, -1, "Clear")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        addrSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        addrSizer.AddGrowableCol(1)
        addrSizer.Add(hostLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.host, 0, wx.EXPAND)
        addrSizer.Add(portLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.port, 0, wx.EXPAND)
        addrSizer.Add(usernameLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.username, 0, wx.EXPAND)
        addrSizer.Add(passwordLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(self.password, 0, wx.EXPAND)
        mainSizer.Add(addrSizer, 0, wx.EXPAND | wx.ALL, 10)
        addrSizer.Add((10, 10))  # some empty space
        addrSizer.Add((10, 10))  # some empty space
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add((20, 20), 1)
        btnSizer.Add(goBtn)
        btnSizer.Add((20, 20), 1)
        btnSizer.Add(clearBtn)
        btnSizer.Add((20, 20), 1)
        mainSizer.Add(btnSizer, 0, wx.EXPAND | wx.BOTTOM, 10)
        panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)
        goBtn.Bind(wx.EVT_BUTTON, self.getSessionInfo)
        clearBtn.Bind(wx.EVT_BUTTON, self.clear)


    def getSessionInfo(self, event):
        hostname = self.host.GetValue()
        portNumber = self.port.GetValue()
        username = self.username.GetValue()
        password = self.password.GetValue()
        self.Destroy()
        return (hostname, portNumber, username, password)

    def clear(self, event):
        self.host.SetValue("")
        self.port.SetValue("")
        self.username.SetValue("")
        self.password.SetValue("")

    def onClose(self, event):
        self.Destroy()