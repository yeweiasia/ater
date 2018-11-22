import wx

class AterMenuBar(wx.MenuBar):

    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent = parent
        self.menuBar = self.createMenuBar()
        parent.SetMenuBar(self.menuBar)


    def bindEvent(self, target, item, handler):
        target.Bind(wx.EVT_MENU, handler, item)

    def createMenuBar(self):
        aterMenuBar = wx.MenuBar()
        aterMenuBar.Append(self.createFileMenu(), "File")
        aterMenuBar.Append(self.createOptionMenu(), "Options")
        return aterMenuBar

    def createFileMenu(self):
        fileMenu = wx.Menu()
        self.bindEvent(self.parent, fileMenu.Append(wx.ID_ANY, "&Exit\t(Alt+F4)",
                        "Exit Program"), self.parent.OnExit)
        return fileMenu

    def createOptionMenu(self):
        optionMenu = wx.Menu()
        self.bindEvent(self.parent, optionMenu.Append(wx.ID_ANY,
                                  "Exit"),
               self.parent.OnExit)
        return optionMenu


