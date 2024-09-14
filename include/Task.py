import wx
import wx.lib.mixins.listctrl as listmix
import locale
from pprint import pprint as pp
from include.reel_utils import check_status, check_reel_status, check_facebook_reel_api_limit
from pubsub import pub
import include.config.init_config as init_config 
apc = init_config.apc
from include.common import PropertyDefaultDict
from datetime import datetime, timedelta
# Set the locale for string comparison
locale.setlocale(locale.LC_ALL, '')
class TaskListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
    def __init__(self, parent, *args, **kwargs):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES, *args, **kwargs)
        self.itemDataMap = {}
        self.itemIndexMap = []
        self.col = -1
        self.ascending = True
        self.next_rowid = 0  # To keep track of unique row IDs
        self.pydata = {}
        self.InsertColumn(0, "Task", width=150)
        self.InsertColumn(1, "Started", width=120)
        self.InsertColumn(2, "Status", width=100)
        self.InsertColumn(3, "Type", width=100)

        # Dynamically initialize the column sorter with the number of columns
        listmix.ColumnSorterMixin.__init__(self, self.GetColumnCount())



        #self.refresh_data()
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRowSelected)  # Bind row selection event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        pub.subscribe(self.on_show_tasks, 'on_show_tasks')

        pub.subscribe(self.on_update_task_status, 'update_task_status')
        pub.subscribe(self.on_set_task_reel_id,     'set_task_reel_id')

    def on_item_activated(self, event):
        # Get the index of the clicked item
        index = event.GetIndex()
        
        # Get the values from the selected row
        item_id = self.GetItemText(index, 0)
        item_name = self.GetItemText(index, 1)
        print(f'Row {index} activated!\nID: {item_id}\nName: {item_name}', 'Info')
        #task_id=index
        task_id = self.GetItemData(index)
        data=self.pydata[task_id]   
        pp(data)
        user_id=data['user_id'] 
        page_id=data['page_id']
        #
        if 1:
            reel_id=data.get('reel_id')
            if reel_id:
                status=check_status(user_id, page_id, reel_id)
                print(123344, status)
        if 0:
            reel_id=data['reel_id']
            status=check_reel_status(user_id, page_id, reel_id)
            print(5345, status)
        reel_url=f"https://www.facebook.com/reel/{reel_id}"
        print( reel_url)

        if 1:
            # Example usage
            
           
            

            can_upload = check_facebook_reel_api_limit(user_id, page_id)

            if can_upload is True:
                print("You can still upload reels.")
            elif can_upload is False:
                print("You have reached your reel upload limit for today.")
            else:
                print("Unable to determine reel upload limit status.")



    def on_set_task_reel_id(self, scope_id,task_id, reel_id):
          
        self.set_task_reel_id(scope_id,task_id, reel_id)
    def set_task_reel_id(self, scope_id, task_id,reel_id):
        print('*****************************set_task_reel_id', scope_id, task_id, reel_id)
        
        sitem=apc.scope_log[scope_id]
        if type(sitem) is dict:
            apc.scope_log[scope_id]=sitem=PropertyDefaultDict(sitem)
        print('task_id',task_id)    
        sitem.tasks[task_id]['reel_id']=reel_id
        apc.scope_log.update_item(scope_id,sitem)


    def on_update_task_status(self, scope_id,task_id, status):
          
        self.update_task_status(scope_id,task_id, status) 

    def update_task_status(self, scope_id, task_id,status):
        print('*****************************update_task_status', scope_id, task_id, status)
        self.update_row_status(task_id,status) 
        sitem=apc.scope_log[scope_id]
        pp(sitem)
        if type(sitem) is dict:
            apc.scope_log[scope_id]=sitem=PropertyDefaultDict(sitem)
        print('task_id',task_id)    
        sitem.tasks[task_id].update({'status':status})
        apc.scope_log.update_item(scope_id,sitem)

    def update_row_status(self, rowid, new_status):
        self.Freeze()
        # Update the status in the itemDataMap
        if rowid in self.itemDataMap:
            task, date_obj, _,  type = self.itemDataMap[rowid]
            self.itemDataMap[rowid] = (task, date_obj, new_status, type)
            # Find the item's position in the list and update the display
            index = self.itemIndexMap.index(rowid)
            self.SetItem(index, 2, new_status)
            self.RefreshItem(index)
            #self.Refresh()
            #self.Update()
        self.Thaw() 
    def on_show_tasks(self, user_id, scope_id, tasks):
        print(999, scope_id)
        self.user_id=user_id
        self.scope_id=scope_id
        #pp(tasks)   
        self.next_rowid = 0
        self.refresh_data(scope_id)
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


    def add_row(self, row):

        task, date, status, type= [v for k, v in row.items() if k.lower() in ['task', 'date', 'status', 'type']]
        current_datetime = date
        

        rowid = self.next_rowid
        self.next_rowid += 1

   
        date_obj = datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
        
        # Store in itemDataMap with rowid as key
        self.itemDataMap[rowid] = (task, date_obj, status, type)
        self.itemIndexMap.append(rowid)

        # Add the item to the ListCtrl (before sorting)
        index = self.GetItemCount()
        self.InsertItem(index, task)
        self.SetItem(index, 1, current_datetime)
        self.SetItem(index, 2, status)
        self.SetItem(index, 3, type)
        self.SetItemData(index, rowid)

        #print(f"Added row: {task}, {current_datetime}, {status}, rowid={rowid}")

        #if self.col != -1:
        #    self.SortItems()
        
        self.EnsureVisible(index)
        #self.Select(index)
        self.pydata[rowid]= row
        return rowid   # Return the unique rowid

    def refresh_data(self, scope_id):
        self.Freeze()
        new_data = apc.scope_log[scope_id][  'tasks']
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        for item in new_data:
            selected= [v for k, v in item.items() if k.lower() in ['task', 'date', 'status', 'type']]
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
        self.DeleteAllItems()
        self.itemDataMap.clear()
        self.itemIndexMap = []
        new_data = apc.task_log
        # Populate the itemDataMap with rowid as key
        for item in new_data:
            selected= [v for k, v in item.items() if k.lower() in ['task', 'date', 'status', 'type']]
           
            self.add_row(*[v for k, v in item.items() if k.lower() in ['task', 'date', 'status', 'type']])

        # Sort itemDataMap by date in descending order
        sorted_items = sorted(self.itemDataMap.items(), key=lambda x: x[1][1], reverse=True)

        # Clear itemIndexMap and repopulate in sorted order
        self.itemIndexMap = [item[0] for item in sorted_items]

        # Clear all items and reinsert them in sorted order
        self.DeleteAllItems()
        for index, (rowid, data) in enumerate(sorted_items):
            task, date_obj, status = data
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            self.InsertItem(index, task)
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
            task, date_obj, status, type = self.itemDataMap[rowid]
            date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Include hours, minutes, and seconds
            self.InsertItem(new_position, task)
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
        index = event.GetIndex()
        
        # Fetch the rowid from itemDataMap using the selected index
        rowid = self.GetItemData(index)
        
        
                
        
        # Get the values from the selected row
        item_id = self.GetItemText(index, 0)
        item_name = self.GetItemText(index, 1)
        print(f'Row {index} selected!\nID: {item_id}\nName: {item_name}', 'Info')
        
        data=self.pydata[rowid]
        pp(data)
        reel_id=data['reel_id'] 
        reel_url=f"https://www.facebook.com/reel/{reel_id}"
        print( reel_url)
        event.Skip()  # Allow the event to propagate
