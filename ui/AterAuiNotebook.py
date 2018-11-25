import time
import wx.aui as aui
from SessionManager import SessionManager

class AterAuiNotebook(aui.AuiNotebook):

    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.parent = parent
        self.default_style = aui.AUI_NB_TOP | aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS
        self.SetWindowStyleFlag(self.default_style)

    def addPanel(self, label, panel, backend, selected):
        import threading
        page = panel(self, backend.sendChar)

        # backendThread = threading.Thread(target=self.initBackendThread, args=(backend, page))
        # backendThread.start()

        self.AddPage(page, label, selected)
        self.initBackend(backend, page)

    #pass ui output method to backend thread
    def initBackend(self, backend, page):

        #init session if session is None
        if not page.session:
            #TO-DO: open session dialog to get connnection info
            page.session = SessionManager(self.parent)

        if len(page.session.sessionManagerDialog.host.GetValue()) == 0:
            return

        term = backend(page.writeText)
        page.term = term


