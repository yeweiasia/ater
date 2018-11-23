
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
        page = panel(self)

        backendThread = threading.Thread(target=self.initBackendThread, args=(backend, page))
        backendThread.start()

        self.AddPage(page, label, selected)

    #pass ui output method to backend thread
    def initBackendThread(self, backend, page):

        #init session if session is None
        if not page.session:
            #TO-DO: open session dialog to get connnection info
            page.session = SessionManager(self.parent)

        term = backend(page.appendText)
        page.term = term


