import wx
import wx.lib.mixins.listctrl as listmix
from include.reel_utils import  check_facebook_reel_api_limit
import locale
from pprint import pprint as pp
#pubsub
from pubsub import pub
from include.common import PropertyDefaultDict
import include.config.init_config as init_config 
apc = init_config.apc

from datetime import datetime, timedelta
# Set the locale for string comparison
locale.setlocale(locale.LC_ALL, '')
class ScopeListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent, *args, **kwargs):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES, *args, **kwargs)
        self.parent=parent
        self.itemDataMap = {}
        self.itemIndexMap = []
        self.pydata={}
        self.col = -1
        self.ascending = True
        self.next_rowid = 0  # To keep track of unique row IDs

        self.InsertColumn(0, "Scope", width=150)
        self.InsertColumn(1, "Date", width=120)
        self.InsertColumn(2, "Status", width=100)
        self.InsertColumn(3, "Type", width=100)

        # Dynamically initialize the column sorter with the number of columns
        listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        self.refresh_data()
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRowSelected)  # Bind row selection event
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnRowActivated)  # Bind row selection event
        pub.subscribe(self.on_update_scope_status, 'update_scope_status')
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
            menu.Append(wx.ID_EDIT, "Redo")
            
            self.Bind(wx.EVT_MENU, self.OnRedoScope, id=wx.ID_EDIT)
            
        else:
            menu.Append(wx.ID_ANY, "No item selected")

        # Display the context menu
        self.PopupMenu(menu, position)
        menu.Destroy()

    # Handler for the "Edit" menu item
    def OnRedoScope(self, event):
        if self.right_click_item != -1:
            rowid = self.GetItemData(self.right_click_item)
            pp(self.itemDataMap[rowid])
            scope, date_obj, status, type = self.itemDataMap[rowid]
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Redo item {rowid}")
            # Here you can add code to edit the item
            print(f"Edit item:\nScope: {scope}\nDate: {date_str}\nStatus: {status}")
            print(f"Edit item {self.right_click_item}")
            pp(self.pydata[rowid]['tasks'])

            apc.tasks= self.pydata[rowid]['tasks']
   
            pub.sendMessage('on_redo_scope', scope_id=rowid)
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

    def OnRowActivated(self, event):
        # Get the selected row index
        selected_index = event.GetIndex()
        
        # Fetch the rowid from itemDataMap using the selected index
        rowid = self.GetItemData(selected_index)
        
        print(f"Row activated: rowid={rowid}, index={selected_index}")


        

        if 1:
            # Example usage
            
            user_id=self.pydata[rowid]['user_id']
            page_id=self.pydata[rowid]['page_id']
            

            can_upload = check_facebook_reel_api_limit(user_id, page_id)

            if can_upload is True:
                print("You can still upload reels.")
            elif can_upload is False:
                print("You have reached your reel upload limit for today.")
            else:
                print("Unable to determine reel upload limit status.")
        event.Skip()

    def on_update_scope_status(self, scope_id, status):
          
        self.update_scope_status(scope_id, status) 
    def update_scope_status(self, scope_id, status):
        self.update_row_status(scope_id,status) 
        sitem=apc.scope_log[scope_id]
        print(sitem)
        sitem.update({  'status':status})
        apc.scope_log.update_item(scope_id,sitem)

    def get_scope_id(self, rowid):
        scope, date_obj, status, type =self.itemDataMap[rowid]
        scope_id= f'{rowid}_{scope}_{type}'
        return scope_id

        return apc.scope_log_id
    def GetListCtrl(self):
        return self

    def GetColumnText(self, col):
        item = self.GetColumn(col)
        return item.GetText()

    def OnColClick(self, event):
        col = event.GetColumn()
        print(f"Column clicked: {col}")  # Debug print

        if col == self.col:
            # Toggle sorting order on the same column
            self.ascending = not self.ascending
        else:
            # New column clicked, set it as the sorting column and start with ascending order
            self.col = col
            self.ascending = True  # Ensures the first click always sorts in ascending order

        # Update the column header text to indicate sort order
        self.UpdateColumnHeaders()

        print(f"Sorting column {col} in {'ascending' if self.ascending else 'descending'} order")  # Debug print
        self.SortItems()

    def UpdateColumnHeaders(self):
        # Clear previous sort indicators
        for i in range(self.GetColumnCount()):
            item = wx.ListItem()
            item.SetMask(wx.LIST_MASK_TEXT)
            # Remove any existing sort indicators
            header = self.GetColumnText(i)
            header = header.replace(" ▲", "").replace(" ▼", "")
            item.SetText(header)
            self.SetColumn(i, item)

        # Add sort indicator to the currently sorted column
        if self.col != -1:
            item = wx.ListItem()
            item.SetMask(wx.LIST_MASK_TEXT)
            header = self.GetColumnText(self.col)
            if self.ascending:
                header += " ▲"  # Up arrow for ascending
            else:
                header += " ▼"  # Down arrow for descending
            item.SetText(header)
            self.SetColumn(self.col, item)

    def deselect_all(self):
        for i in range(self.GetItemCount()):
            self.SetItemState(i, 0, wx.LIST_STATE_SELECTED)

    def add_row(self, row):
        selected= [v for k, v in row.items() if k.lower() in ['scope', 'date', 'status', 'type']]
        pp(selected )
        scope, date, status, type = selected
        current_datetime = date
        

        rowid = self.next_rowid
        self.next_rowid += 1

   
        date_obj = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
        
        # Store in itemDataMap with rowid as key
        self.itemDataMap[rowid] = (scope, date_obj, status, type)
        self.itemIndexMap.append(rowid)

        # Add the item to the ListCtrl (before sorting)
        index = self.GetItemCount()
        self.InsertItem(index, scope)
        self.SetItem(index, 1, current_datetime)
        self.SetItem(index, 2, status)
        self.SetItem(index, 3, type)
        self.SetItemData(index, rowid)
        self.pydata[rowid]= row

        #print(f"Added row: {scope}, {current_datetime}, {status}, rowid={rowid}")

        #if self.col != -1:
        #    self.SortItems()
        
        self.EnsureVisible(index)
        self.deselect_all()
        self.Select(index)
        return rowid   # Return the         

    def _add_row(self, scope, date, status, type):
        current_datetime = date
        

        rowid = self.next_rowid
        self.next_rowid += 1

   
        date_obj = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
        
        # Store in itemDataMap with rowid as key
        self.itemDataMap[rowid] = (scope, date_obj, status, type)
        self.itemIndexMap.append(rowid)

        # Add the item to the ListCtrl (before sorting)
        index = self.GetItemCount()
        self.InsertItem(index, scope)
        self.SetItem(index, 1, current_datetime)
        self.SetItem(index, 2, status)
        self.SetItem(index, 3, type)
        self.SetItemData(index, rowid)

        #print(f"Added row: {scope}, {current_datetime}, {status}, rowid={rowid}")

        #if self.col != -1:
        #    self.SortItems()
        
        self.EnsureVisible(index)
        self.deselect_all()
        self.Select(index)
        return rowid   # Return the unique rowid

    def refresh_data(self):
        self.Freeze()
        new_data = apc.scope_log
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        for item in new_data:
            
            #print(999,selected)
            self.add_row(item)
        
        # Reset the column sorter
        self.col = -1
        self.ascending = True
        last_row_index = len(self.itemDataMap) - 1
        if last_row_index >= 0:
            self.EnsureVisible(last_row_index)
            self.Select(last_row_index)
        print("Data refreshed")  # Debug print
        self.Thaw() 


    def _refresh_data(self):
        self.Freeze()
        new_data = apc.scope_log
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        for item in new_data:
            selected= [v for k, v in item.items() if k.lower() in ['scope', 'date', 'status', 'type']]
            #print(999,selected)
            self.add_row(*[v for k, v in item.items() if k.lower() in ['scope', 'date', 'status', 'type']])
        
        # Reset the column sorter
        self.col = -1
        self.ascending = True
        last_row_index = len(self.itemDataMap) - 1
        if last_row_index >= 0:
            self.EnsureVisible(last_row_index)
            self.Select(last_row_index)
        print("Data refreshed")  # Debug print
        self.Thaw() 

    def _refresh_data(self):
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        new_data = apc.scope_log
        # Populate the itemDataMap with rowid as key
        for item in new_data:
            selected= [v for k, v in item.items() if k.lower() in ['scope', 'date', 'status', 'type']]
            #print(999,selected)
            self.add_row(*[v for k, v in item.items() if k.lower() in ['scope', 'date', 'status', 'type']])

        # Sort itemDataMap by date in descending order
        sorted_items = sorted(self.itemDataMap.items(), key=lambda x: x[1][1], reverse=True)

        # Clear itemIndexMap and repopulate in sorted order
        self.itemIndexMap = [item[0] for item in sorted_items]

        # Clear all items and reinsert them in sorted order
        self.DeleteAllItems()
        for index, (rowid, data) in enumerate(sorted_items):
            scope, date_obj, status = data
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.InsertItem(index, scope)
            self.SetItem(index, 1, date_str)
            self.SetItem(index, 2, status)
            self.SetItemData(index, rowid)

        # Highlight the last row in the sorted list
        last_row_index = len(sorted_items) - 1
        if last_row_index >= 0:
            self.EnsureVisible(last_row_index)
            self.Select(last_row_index)

        print("Data refreshed and sorted by date in descending order.")  # Debug print



    def SortItems(self):
        if self.col == -1:
            # If no column has been clicked yet, skip sorting
            return

        def sort_function(rowid):
            # Sort by the selected column, not by rowid
            item = self.itemDataMap[rowid][self.col]
            if isinstance(item, str):
                return locale.strxfrm(item.lower())
            return item

        # Sort the itemIndexMap based on the selected column and sort order
        self.itemIndexMap.sort(key=sort_function, reverse=not self.ascending)

        # Clear all items from the ListCtrl and reinsert them in the new sorted order
        self.DeleteAllItems()
        for new_position, rowid in enumerate(self.itemIndexMap):
            scope, date_obj, status, type = self.itemDataMap[rowid]
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Include hours, minutes, and seconds
            self.InsertItem(new_position, scope)
            self.SetItem(new_position, 1, date_str)
            self.SetItem(new_position, 2, status)
            self.SetItem(new_position, 3, type)
            # Maintain the rowid reference
            self.SetItemData(new_position, rowid)

        self.Refresh()  # Refresh the ListCtrl to show the new order
        self.Update()   # Force an immediate update to the UI

        print("Sorted order:")  # Debug print
        for rowid in self.itemIndexMap:
            print(f"{rowid}: {self.itemDataMap[rowid][self.col]}")  # Debug print

    def OnRowSelected(self, event):
        # Get the selected row index
        selected_index = event.GetIndex()
        
        # Fetch the rowid from itemDataMap using the selected index
        rowid = self.GetItemData(selected_index)
        
        print(f"222 Row selected: rowid={rowid}, index={selected_index}")
        #self.user_name.SetValue(apc.users[1])
        

             
        pub.sendMessage('on_scope_selected', scope_id=rowid)
        pub.sendMessage('on_show_tasks', user_id=self.pydata[rowid]['user_id'], scope_id=rowid, tasks=self.pydata[rowid]['tasks'])
        #pp(self.pydata[rowid])
        #print(self.Parent.Parent)
        event.Skip()  # Allow the event to propagate

    def update_row_status(self, rowid, new_status):
        # Update the status in the itemDataMap
        if rowid in self.itemDataMap:
            scope, date_obj, _,  type = self.itemDataMap[rowid]
            self.itemDataMap[rowid] = (scope, date_obj, new_status, type)
            # Find the item's position in the list and update the display
            index = self.itemIndexMap.index(rowid)
            self.SetItem(index, 2, new_status)
            self.RefreshItem(index)
            #self.Refresh()
            #self.Update()