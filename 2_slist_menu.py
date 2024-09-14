import wx
import wx.lib.mixins.listctrl as listmix
from datetime import datetime
import locale
import json
from pubsub import pub  # Import pypubsub

class SortableListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES, *args, **kwargs)
        self.itemDataMap = {}
        self.itemIndexMap = []
        self.col = -1
        self.ascending = True
        self.next_rowid = 0

        self.InsertColumn(0, "Scope", width=150)
        self.InsertColumn(1, "Date", width=200)
        self.InsertColumn(2, "Status", width=150)

        listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())

        self.data = json.loads('''{
          "scope_log": [
            {"Scope": "test", "Date": "2023-05-15 12:00:00", "Status": "OK"},
            {"Scope": "default", "Date": "2023-05-15 13:00:00", "Status": "STARTED"},
            {"Scope": "default", "Date": "2023-05-15 14:00:00", "Status": "TEST"}
          ]
        }''')

        self.refresh_data(self.data['scope_log'])
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRowSelected)
        
        # Bind the context menu event
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def on_refresh(self, event):
        # Simulate getting new data (you can replace this with actual data fetching)
        new_data = [
            {"Scope": "production", "Date": "2023-05-16 12:30:00", "Status": "RUNNING"},
            {"Scope": "staging", "Date": "2023-05-16 13:00:00", "Status": "STOPPED"},
            {"Scope": "development", "Date": "2023-05-16 14:15:00", "Status": "TESTING"}
        ]
        self.refresh_data(new_data)
        self.Refresh()
        self.Update()

    def GetListCtrl(self):
        return self

    def GetColumnText(self, col):
        item = self.GetColumn(col)
        return item.GetText()

    def OnColClick(self, event):
        col = event.GetColumn()
        if col == self.col:
            self.ascending = not self.ascending
        else:
            self.col = col
            self.ascending = True
        self.UpdateColumnHeaders()
        self.SortItems()

    def UpdateColumnHeaders(self):
        for i in range(self.GetColumnCount()):
            item = wx.ListItem()
            item.SetMask(wx.LIST_MASK_TEXT)
            header = self.GetColumnText(i)
            header = header.replace(" ▲", "").replace(" ▼", "")
            item.SetText(header)
            self.SetColumn(i, item)
        if self.col != -1:
            item = wx.ListItem()
            item.SetMask(wx.LIST_MASK_TEXT)
            header = self.GetColumnText(self.col)
            if self.ascending:
                header += " ▲"
            else:
                header += " ▼"
            item.SetText(header)
            self.SetColumn(self.col, item)

    def add_row(self, scope, status):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rowid = self.next_rowid
        self.next_rowid += 1
        date_obj = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
        self.itemDataMap[rowid] = (scope, date_obj, status)
        self.itemIndexMap.append(rowid)
        index = self.GetItemCount()
        self.InsertItem(index, scope)
        self.SetItem(index, 1, current_datetime)
        self.SetItem(index, 2, status)
        self.SetItemData(index, rowid)
        if self.col != -1:
            self.SortItems()
        self.EnsureVisible(index)
        return rowid

    def refresh_data(self, new_data):
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        for item in new_data:
            self.add_row(item['Scope'], item['Status'])
        self.col = -1
        self.ascending = True

    def SortItems(self):
        if self.col == -1:
            return
        def sort_function(rowid):
            item = self.itemDataMap[rowid][self.col]
            if isinstance(item, str):
                return locale.strxfrm(item.lower())
            return item
        self.itemIndexMap.sort(key=sort_function, reverse=not self.ascending)
        self.DeleteAllItems()
        for new_position, rowid in enumerate(self.itemIndexMap):
            scope, date_obj, status = self.itemDataMap[rowid]
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.InsertItem(new_position, scope)
            self.SetItem(new_position, 1, date_str)
            self.SetItem(new_position, 2, status)
            self.SetItemData(new_position, rowid)
        self.Refresh()
        self.Update()

    def OnRowSelected(self, event):
        selected_index = event.GetIndex()
        rowid = self.GetItemData(selected_index)
        scope, date_obj, status = self.itemDataMap[rowid]
        date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        # Send a message via pypubsub when a row is selected
        pub.sendMessage('row.selected', rowid=rowid, scope=scope, date=date_str, status=status)
        
        print(f"Row selected: rowid={rowid}, index={selected_index}")
        event.Skip()
        
    # Context menu event handler
    def OnContextMenu(self, event):
        # Get the position of the mouse event
        position = event.GetPosition()
        position = self.ScreenToClient(position)
        # Determine the item that was clicked
        item, flags = self.HitTest(position)
        self.right_click_item = item

        # Create the context menu
        menu = wx.Menu()
        if item != wx.NOT_FOUND and flags & wx.LIST_HITTEST_ONITEM:
            menu.Append(wx.ID_EDIT, "Edit")
            menu.Append(wx.ID_DELETE, "Delete")
            self.Bind(wx.EVT_MENU, self.OnEditItem, id=wx.ID_EDIT)
            self.Bind(wx.EVT_MENU, self.OnDeleteItem, id=wx.ID_DELETE)
        else:
            menu.Append(wx.ID_ANY, "No item selected")

        # Display the context menu
        self.PopupMenu(menu, position)
        menu.Destroy()

    # Handler for the "Edit" menu item
    def OnEditItem(self, event):
        if self.right_click_item != -1:
            rowid = self.GetItemData(self.right_click_item)
            scope, date_obj, status = self.itemDataMap[rowid]
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            # Here you can add code to edit the item
            wx.MessageBox(f"Edit item:\nScope: {scope}\nDate: {date_str}\nStatus: {status}", "Edit Item", wx.OK | wx.ICON_INFORMATION)
            print(f"Edit item {self.right_click_item}")
        else:
            wx.MessageBox("No item selected", "Info", wx.OK | wx.ICON_INFORMATION)

    # Handler for the "Delete" menu item
    def OnDeleteItem(self, event):
        if self.right_click_item != -1:
            # Remove the item from the list control
            self.DeleteItem(self.right_click_item)
            # Remove the item from the data maps
            rowid = self.GetItemData(self.right_click_item)
            if rowid in self.itemDataMap:
                del self.itemDataMap[rowid]
            if rowid in self.itemIndexMap:
                self.itemIndexMap.remove(rowid)
            print(f"Deleted item {self.right_click_item}")
            # Reset the selection
            self.right_click_item = -1
        else:
            wx.MessageBox("No item selected", "Info", wx.OK | wx.ICON_INFORMATION)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Scope Log ListCtrl Example")
        
        # Subscribe to the 'row.selected' message
        pub.subscribe(self.on_row_selected, 'row.selected')
        
        panel = wx.Panel(self)
        self.list_ctrl = SortableListCtrl(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(sizer)
        refresh_button = wx.Button(panel, label="Refresh Data")
        refresh_button.Bind(wx.EVT_BUTTON, self.list_ctrl.on_refresh)
        sizer.Add(refresh_button, 0, wx.ALL, 10)
        append_button = wx.Button(panel, label="Append Row")
        append_button.Bind(wx.EVT_BUTTON, self.on_append)
        sizer.Add(append_button, 0, wx.ALL, 10)
        self.Show()

    def on_row_selected(self, rowid, scope, date, status):
        # Handle the row selected message here
        print(f"Received message: Row ID={rowid}, Scope={scope}, Date={date}, Status={status}")

    def on_append(self, event):
        scope = "test"
        status = "OK"
        rowid = self.list_ctrl.add_row(scope, status)
        print(f"Appended row with rowid={rowid}")

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
