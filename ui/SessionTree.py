import wx

class SessionTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id, style):
        wx.TreeCtrl.__init__(self, parent, id, style=style)

    def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1


class SessionTreeCtrlPanel(wx.Panel):
    def __init__(self, parent, size):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, size=size, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = SessionTreeCtrl(self, -1, wx.TR_HAS_BUTTONS)

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, isz))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        self.root = self.tree.AddRoot("default")
        self.tree.SetItemData(self.root, None)
        self.tree.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)

        for x in range(7):
            child = self.tree.AppendItem(self.root, "Item %d" % x)
            self.tree.SetItemData(child, None)
            self.tree.SetItemImage(child, self.fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, self.fldropenidx, wx.TreeItemIcon_Expanded)

            for y in range(5):
                last = self.tree.AppendItem(child, "item %d-%s" % (x, chr(ord("a") + y)))
                self.tree.SetItemData(last, None)
                self.tree.SetItemImage(last, self.fileidx, wx.TreeItemIcon_Normal)

        self.tree.Expand(self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragBegin)
        self.Bind(wx.EVT_TREE_END_DRAG, self.OnDragEnd)

        self.Bind(wx.EVT_TIMER, self.OnTime)

    def OnDragBegin(self, evt):
        item = evt.GetItem()

        if self.tree.GetItemParent(item) == self.root:
            evt.Veto()
            return

        self.dragitem = item
        evt.Allow()
        self.tree.Bind(wx.EVT_MOTION, self.OnMotion)
        self.tree.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)

    def OnDragEnd(self, evt):
        target = evt.GetItem()

        if not target.IsOk() or target == self.root:
            return

        text = self.tree.GetItemText(self.dragitem)
        if self.tree.GetItemParent(target) == self.root:
            added = self.tree.AppendItem(target, text)
        else:
            parent = self.tree.GetItemParent(target)
            added = self.tree.InsertItem(parent, self.findItem(target), text)

        self.tree.Delete(self.dragitem)
        self.tree.SetItemImage(added, self.fileidx, wx.TreeItemIcon_Normal)

        self.tree.SelectItem(added)
        self.tree.EnsureVisible(added)

    def OnMouseLeftUp(self, evt):
        self.tree.Unbind(wx.EVT_MOTION)
        self.tree.Unbind(wx.EVT_LEFT_UP)
        evt.Skip()

    def OnMotion(self, evt):
        size = self.tree.GetSize()
        x, y = evt.GetPosition()

        if y < 0 or y > size[1] and not hasattr(self, 'timer'):
            self.timer = wx.Timer(self)
            self.timer.Start(70)
        evt.Skip()

    def OnTime(self, evt):
        x, y = self.tree.ScreenToClient(wx.GetMousePosition())
        size = self.tree.GetSize()

        if y < 0:
            self.ScrollUp()
        elif y > size[1]:
            self.ScrollDown()
        else:
            del self.timer
            return
        self.timer.Start(70)

    def ScrollUp(self):
        if "wxMSW" in wx.PlatformInfo:
            self.tree.ScrollLines(-1)
        else:
            first = self.tree.GetFirstVisibleItem()
            prev = self.tree.GetPrevSibling(first)
            if prev:
                # drill down to find last expanded child
                while self.tree.IsExpanded(prev):
                    prev = self.tree.GetLastChild(prev)
            else:
                # if no previous sub then try the parent
                prev = self.tree.GetItemParent(first)

            if prev:
                self.tree.ScrollTo(prev)
            else:
                self.tree.EnsureVisible(first)

    def ScrollDown(self):
        if "wxMSW" in wx.PlatformInfo:
            self.tree.ScrollLines(1)
        else:
            # first find last visible item by starting with the first
            next = None
            last = None
            item = self.tree.GetFirstVisibleItem()
            while item:
                if not self.tree.IsVisible(item): break
                last = item
                item = self.tree.GetNextVisible(item)

            # figure out what the next visible item should be,
            # either the first child, the next sibling, or the
            # parent's sibling
            if last:
                if self.tree.IsExpanded(last):
                    next = self.tree.GetFirstChild(last)[0]
                else:
                    next = self.tree.GetNextSibling(last)
                    if not next:
                        prnt = self.tree.GetItemParent(last)
                        if prnt:
                            next = self.tree.GetNextSibling(prnt)

            if next:
                self.tree.ScrollTo(next)
            elif last:
                self.tree.EnsureVisible(last)

    def traverse(self, parent=None):
        if parent is None:
            parent = self.root
        nc = self.tree.GetChildrenCount(parent, False)

        def GetFirstChild(parent, cookie):
            return self.tree.GetFirstChild(parent)

        GetChild = GetFirstChild
        cookie = 1
        for i in range(nc):
            child, cookie = GetChild(parent, cookie)
            GetChild = self.tree.GetNextChild
            yield child

    def findItem(self, item):
        parent = self.tree.GetItemParent(item)
        for n, i in enumerate(self.traverse(parent)):
            if item == i:
                return n

    def OnSize(self, event):
        w, h = self.GetClientSize()
        self.tree.SetSize(0, 0, w, h)

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        event.Skip()