import wx
import webbrowser
import os, sys, time, traceback, json
from os.path import isfile
from pprint import pprint as pp 
from pprint import pformat
import  wx.adv
from pubsub import pub
from os.path import join
from include.Scope import ScopeListCtrl
from include.Task import TaskListCtrl
from include.ReelUploader import ReelUploader   
import include.config.init_config as init_config 

init_config.init(**{})
apc = init_config.apc




from include.page_utils import set_page_access_tokens, check_page_token_validity
from include.reel_utils import check_status, get_page_metrics,   wait_for_reel_publishing

from include.common import PropertyDefaultDict, ErrorValidatingAccessToken
from io import StringIO

from datetime import datetime, timedelta
from include.image_utils import ImagePanel
e=sys.exit


import requests
try:
    set_page_access_tokens()
except ErrorValidatingAccessToken as e:
    print(f"Error: {e}")
    print("User token expired. Resetting after update.")
    #apc.init_pages()
    







#pages= {page_id: page.page_name for page_id, page in apc.pages[apc.user].items()}
import textwrap

class CustomWrappingDialog(wx.Dialog):
    def __init__(self, parent, title, message, caption):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(CustomWrappingDialog, self).__init__(parent, -1, title, style=style)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a wx.StaticText for the caption
        caption_text = wx.StaticText(self, label=caption)
        caption_text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(caption_text, 0, wx.ALL | wx.EXPAND, 10)

        # Create a wx.TextCtrl for the message with word wrap
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.TE_AUTO_URL)
        self.text_ctrl.SetValue(message)
        
        # Set a larger minimum size for the text control
        self.text_ctrl.SetMinSize((480, 200))  # Increased width and height
        
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        # Add buttons
        button_sizer = wx.StdDialogButtonSizer()
        self.yes_button = wx.Button(self, wx.ID_YES)
        self.no_button = wx.Button(self, wx.ID_NO)
        button_sizer.AddButton(self.yes_button)
        button_sizer.AddButton(self.no_button)
        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Fit()
        self.SetMinSize((500, 300))  # Set a larger minimum size for the entire dialog

        self.yes_button.Bind(wx.EVT_BUTTON, self.on_yes)
        self.no_button.Bind(wx.EVT_BUTTON, self.on_no)

    def on_yes(self, event):
        self.EndModal(wx.ID_YES)

    def on_no(self, event):
        self.EndModal(wx.ID_NO)

class WrappingMessageDialog(wx.Dialog):
    def __init__(self, parent, message, caption, style):
        super().__init__(parent, title=caption, style=style | wx.RESIZE_BORDER)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create a caption
        caption_text = wx.StaticText(self, label="Do you want to upload?")
        caption_text.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(caption_text, 0, wx.ALL, 10)
        
        # Create a read-only TextCtrl with word wrapping
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_NONE)
        self.text_ctrl.SetValue(message + '\n\n')  # Add extra newlines for padding
        
        # Set size for the text control
        width = 500  # Increased width to 500 pixels
        height = min(self.text_ctrl.GetBestHeight(width) + 40, 400)  # Increased max height to 400 pixels, added extra padding
        self.text_ctrl.SetMinSize((width, height))
        
        main_sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        # Add buttons
        button_sizer = wx.StdDialogButtonSizer()
        yes_button = wx.Button(self, wx.ID_YES)
        no_button = wx.Button(self, wx.ID_NO)
        button_sizer.AddButton(yes_button)
        button_sizer.AddButton(no_button)
        button_sizer.Realize()
        
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.SetSizer(main_sizer)
        self.Fit()
        self.Center()
        
        # Set a minimum size for the dialog
        self.SetMinSize((550, 300))  # Increased minimum size
        
        # Bind events to buttons
        yes_button.Bind(wx.EVT_BUTTON, self.on_yes)
        no_button.Bind(wx.EVT_BUTTON, self.on_no)
    
    def ShowModal(self):
        # Ensure the dialog is large enough to show all content
        self.Fit()
        size = self.GetSize()
        self.SetSize((max(size.width, 550), max(size.height, 300)))
        return super().ShowModal()
    
    def on_yes(self, event):
        self.EndModal(wx.ID_YES)
    
    def on_no(self, event):
        self.EndModal(wx.ID_NO)


class LogRedirector(StringIO):
    def __init__(self, log_ctrl):
        super().__init__()
        self.log_ctrl = log_ctrl

    def write(self, string):
        wx.CallAfter(self.log_ctrl.AppendText, string)




class FileUploaderFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='File Uploader', size=(1000, 800))
        panel = wx.Panel(self)
        
        # Create a main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create a sizer for the top controls
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.user_name = wx.ComboBox(panel, choices=apc.users, style=wx.CB_DROPDOWN)
        self.user_name.Bind(wx.EVT_COMBOBOX, self.on_select_user)
        if apc.user:
            if apc.user in apc.users:
                self.user_name.SetValue(apc.user)
        else:
            self.user_name.SetValue(apc.users[0])     
            apc.user=apc.users[0]    
        apc.pages=apc.page_tokens[apc.user]
        #print(999,apc.pages)
        #for page_id, page in apc.pages.items():
        #    print(333,page_id, type(page), page['page_name'])
        pages= {page_id: page.page_name for page_id, page in apc.pages.items()}
        self.keys = list(pages.keys())
        choices = list(pages.values())
        self.page_name = wx.ComboBox(panel, choices=choices, style=wx.CB_DROPDOWN)
        self.page_name.Bind(wx.EVT_COMBOBOX, self.on_select_page)
        if apc.page_id:
            if apc.page_id in pages:
                self.page_name.SetValue(pages[apc.page_id])
         
        else:
            self.page_name.SetValue(choices[0])


        top_sizer.Add(self.user_name, 0, wx.RIGHT, 10)
        top_sizer.Add(self.page_name, 0, wx.RIGHT, 10)
        
        self.file_ctrl = wx.TextCtrl(panel)
        if apc.input_files:
            self.file_ctrl.SetValue(';'.join(apc.input_files.values()) + ' ')
        #self.file_ctrl.SetValue(r'C:\Users\alex_\myg\facebook_downloader\downloads\ArtForUkraine\backup\done\bbb6ef9a-9ed3-4b7b-8b5b-27281f1cc53b_Технологічна революція в Сеньківці 😎 – Серіал Будиночок на щастя_processed_for_reels.mp4 ')
        #self.file_ctrl.SetValue(r'C:\Users\alex_\myg\facebook_downloader\downloads\ArtForUkraine\backup\done\bbb6ef9a-9ed3-4b7b-8b5b-27281f1cc53b_Технологічна революція в Сеньківці 😎 – Серіал Будиночок на щастя.mp4 ')
        top_sizer.Add(self.file_ctrl, 1, wx.EXPAND | wx.RIGHT, 10)
        
        browse_btn = wx.Button(panel, label='Browse')
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        top_sizer.Add(browse_btn, 0, wx.RIGHT, 10)

        self.validate_btn = wx.Button(panel, label='Validate')
        #self.validate_btn.Bind(wx.EVT_BUTTON, self.on_validate)
        top_sizer.Add(self.validate_btn, 0)

        self.upload_btn = wx.Button(panel, label='Upload')
        #self.upload_btn.Bind(wx.EVT_BUTTON, self.on_upload)
        top_sizer.Add(self.upload_btn, 0)
        self.publish_btn = wx.Button(panel, label='Publish')
        #self.publish_btn.Bind(wx.EVT_BUTTON, self.on_publish)
        top_sizer.Add(self.publish_btn, 0)

        self.status_btn = wx.Button(panel, label='Status')
        self.status_btn.Bind(wx.EVT_BUTTON, self.on_status)
        top_sizer.Add(self.status_btn, 0)

        self.all_btn = wx.Button(panel, label='All')
        self.all_btn.Bind(wx.EVT_BUTTON, self.on_all)
        top_sizer.Add(self.all_btn, 0)

        url = "https://www.facebook.com"
        if apc.reel_id:
            url=f'https://www.facebook.com/reel/{apc.reel_id}'
        self.reel_hl = wx.adv.HyperlinkCtrl(panel, -1, "Reel", url)
        
        # Bind the event to open URL in default browser
        self.Bind(wx.adv.EVT_HYPERLINK, self.on_reel_hl, self.reel_hl)


        top_sizer.Add(self.reel_hl, 0)
        lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        if 1:
            self.user_token = wx.TextCtrl(panel)
            #apc.user_token= 'EAAHbeMlmZCbYBO2lLjTv9mtYE0yf3VDS6URecjaEwalTZCvDxU0lP0hseSr5slLIzg6ZBkmcvaBsY5AyEtPTF98s3ZAh49QwHbYAy2Kgw0rigzJcpzwZASZCTZCg7I19Kp55PHx6XBAu5kU5vHFcdrfDDjTXBPZAvw6ZBCDPyhNDWyVbo07mUhB1H4O1DN6utBlB53M1Fn7gX0V3Hy63y7BGQMIVPslgGnmgZD'
            self.user_token.SetValue(apc.user_token)
            self.user_token.Bind(wx.EVT_TEXT, self.on_text_change)
            self.user_token.Bind(wx.EVT_LEFT_DOWN, self.on_ut_click)
            self.user_token.Bind(wx.EVT_KEY_DOWN, self.on_ut_key_press)
            
            lower_sizer.Add(self.user_token, 1 , wx.EXPAND | wx.ALL)
        if 1:
            self.reel_descr = wx.TextCtrl(panel, size=(300, -1))
            
            self.reel_descr.SetValue(apc.get_reel_descr())
            #self.reel_descr.Bind(wx.EVT_TEXT, self.on_reel_descr_change)
            self.reel_descr.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
            
            lower_sizer.Add(self.reel_descr, 0 )

        if 1:
            #get scopes from config/scopes.json
            pp(apc.scopes)
            scope_choicess =  ['default'] + [scope for scope in apc.scopes]
            self.upload_scope = wx.ComboBox(panel, choices=scope_choicess, style=wx.CB_DROPDOWN)
            print(24142,apc.scope_name)
            self.upload_scope.SetValue(apc.scope_name)
            self.page_name.Bind(wx.EVT_COMBOBOX, self.on_upload_scope)
            #self.reel_descr.Bind(wx.EVT_TEXT, self.on_reel_descr_change)
            #self.upload_scope.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
            
            lower_sizer.Add(self.upload_scope, 0 )

            


        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 3)
        main_sizer.Add(lower_sizer, 0, wx.EXPAND | wx.ALL, 3)
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.image_panel = ImagePanel(panel)
        if 1:
            log_sizer = wx.BoxSizer(wx.VERTICAL)
            self.scope_log=ScopeListCtrl (panel)
            self.task_log = TaskListCtrl (panel)
            self.log_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
            log_sizer.Add(self.scope_log, 0, wx.EXPAND | wx.ALL, 5)
            log_sizer.Add(self.task_log, 0, wx.EXPAND | wx.ALL, 5)
            log_sizer.Add(self.log_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        
        image_sizer = wx.BoxSizer(wx.VERTICAL)
        image_sizer.Add(self.image_panel, 1, wx.EXPAND | wx.ALL, 5)
        # Create a horizontal box sizer for both the label and button
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add a label to show the number of images loaded
        self.image_count_label = wx.StaticText(panel, label="0 images loaded")
        bottom_sizer.Add(self.image_count_label, 0, wx.ALL | wx.ALIGN_LEFT, 5)

        # Add a stretchable space between the label and the button
        bottom_sizer.AddStretchSpacer(1)

        # Add the Clear Images button and center it
        self.clear_button = wx.Button(panel, label="Clear Images")
        self.clear_button.Bind(wx.EVT_BUTTON, self.OnClear)
        bottom_sizer.Add(self.clear_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Add the bottom_sizer to the main vertical sizer
        image_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.ALL, 5)

        panel_sizer.Add(image_sizer, 1, wx.EXPAND | wx.ALL, 5)
        panel_sizer.Add(log_sizer, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(panel_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        close_btn = wx.Button(panel, label='Close')
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        main_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        panel.SetSizer(main_sizer)
        
        self.Centre()
        #self.stdout_redirector = LogRedirector(self.log_ctrl)
        #self.video_id= None
        #self.update_page_token()
        pub.subscribe(self.OnUserChanged, "user_changed")
        pub.subscribe(self.OnPageChanged, "page_id_changed")
        pub.subscribe(self.OnInputFilesChanged, "input_files_changed")
        pub.subscribe(self.OnScopeSelected, "on_scope_selected")
        pub.subscribe(self.OnAllocatedReelId, "allocated_reel_id")
        pub.subscribe(self.OnReelFileNameChanged, "reel_file_name_changed")
        pub.subscribe(self.OnSetReelStatus, "set_reel_status")
        pub.subscribe(self.OnLog, "on_log")
        pub.subscribe(self.OnRedoScope, "on_redo_scope")
        
        #pub.subscribe(self.OnTaskSelected, "task_selected")
        self.Layout()
        self.Show()
        if apc.input_files:
            
           loaded_cnt = self.image_panel.LoadFiles(apc.input_files.values())
           if not loaded_cnt:
                self.image_panel.ShowDefaultMessage()
        else:   
            self.image_panel.ShowDefaultMessage()
    def on_upload_scope(self, event):
        print('Upload Scope:', self.upload_scope.GetValue())
        apc.scope_name = self.upload_scope.GetValue()
       
    def OnLog(self, msg, scope_id, task_id, file_id):      
        self.log_ctrl.AppendText(f's{scope_id}.t{task_id}.f{file_id}: {msg}\n')   
    def OnSetReelStatus(self, value, scope_id, task_id, file_id):   
        print('OnSetReelStatus:', value)
        print('task_id:', task_id)
        print('file_id:', file_id)
        self.scope_log.update_scope_status( scope_id, f't{task_id}.f{file_id}.{value}')   
        self.task_log.update_task_status( scope_id, task_id, f'f{file_id}.{value}')

    def OnReelFileNameChanged(self, value, scope_id, task_id, file_id):
        print('OnReelFileNameChanged: Reel File Name Changed:', value)
        assert file_id in apc.input_files
        assert isfile(value), ('OnReelFileNameChanged',value )
        apc.input_files[file_id] = value

    def OnAllocatedReelId(self, value, scope_id, task_id, file_id):
        print('Allocated Reel Id:', value)
        pub.sendMessage("set_task_reel_id", scope_id=scope_id, task_id=task_id, reel_id=value)

        if 0:
            self.reel_hl.SetURL(f'https://www.facebook.com/reel/{value}')
            self.reel_hl.SetLabel(f'Reel: {value}')
            self.reel_hl.SetToolTip(f'Reel: {value}')
            self.reel_hl.Refresh()
    def OnInputFilesChanged   (self, value):
        print('Input files changed:', value)
        self.file_ctrl.SetValue(';'.join(value.values()) + ' ')         

    def OnClear(self, event):
        self.image_panel.ClearImages()
        self.image_panel.ShowDefaultMessage()
        self.UpdateImageCount(0)

    def UpdateImageCount(self, count):
        self.image_count_label.SetLabel(f"{count} files loaded")

    def OnScopeSelected(self, scope_id):
        print('Scope selected:',scope_id)
        
    def on_key_down(self, event):
        key_code = event.GetKeyCode()
        ctrl_down = event.ControlDown()
        
        if ctrl_down and key_code == 86:  # Ctrl+V (paste)
            self.handle_paste()
            print(self.reel_descr.GetValue())
        elif ctrl_down and key_code == 67:  # Ctrl+C (copy)
            print("Copy operation detected")
        elif ctrl_down and key_code == 88:  # Ctrl+X (cut)
            print("Cut operation detected")
        else:
            char = chr(key_code) if 32 <= key_code <= 126 else f"Code: {key_code}"
            print(f"Key pressed: {char}")
            apc.set_reel_descr(self.reel_descr.GetValue())
        
        event.Skip()
    def handle_paste(self):
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                data = wx.TextDataObject()
                success = wx.TheClipboard.GetData(data)
                wx.TheClipboard.Close()
                if success:
                    paste_text = data.GetText()
                    print(f"Pasted text: {paste_text}")
                    apc.set_reel_descr(paste_text)
                else:
                    print("Failed to get data from clipboard")
            else:
                print("Text data not available in clipboard")
            wx.TheClipboard.Close()
        else:
            print("Cannot open the clipboard")

    def on_reel_descr_change(self):
        # This method will be called every time the text changes
        print('Reel Descr changed', self.reel_descr.GetValue())
        apc.set_reel_descr(self.reel_descr.GetValue())

    def OnPageChanged(self, value):
        print('Page changed:', value)
        print(111, apc.page_id)
        print('Reel Descr:', apc.get_reel_descr())    
        self.reel_descr.SetValue(apc.get_reel_descr())

    def OnUserChanged(self, value):
        print('User changed:', value)
        apc.user_token= apc.get_user_token()
        self.user_token.SetValue(apc.user_token) 
        if apc.user_token:      
            self.update_page_tokens()
            self.reset_pages_combobox()

    def LoadVideo(self, file_path):
        frame = self.image_panel.get_first_frame(file_path)
        if frame is not None:
            self.image_panel.SetImage(frame)
        else:
            wx.MessageBox("Failed to load video frame", "Error", wx.OK | wx.ICON_ERROR)

    def reset_pages_combobox(self):
        assert apc.pages
        self.keys = list(apc.pages.keys())
        new_choices =[page.page_name for page in list(apc.pages.values())]        
        current_selection = self.page_name.GetValue()
        self.page_name.Clear()
        pp(new_choices)
        self.page_name.AppendItems(new_choices)
        
        if current_selection in new_choices:
            self.page_name.SetStringSelection(current_selection)
        else:
            self.page_name.SetSelection(wx.NOT_FOUND)

    def on_select_user(self, event):
        # Get the selected index from the ComboBox
        selected_user_id = self.user_name.GetSelection()
        
        # Get the corresponding key using the index
        if selected_user_id != wx.NOT_FOUND:
            #print(222, users)
            apc.user = apc.users[selected_user_id]
            print(f"111 Selected User: {apc.user}")
        else:
            print("No valid selection.")
        
        event.Skip()

    def on_ut_click(self, event):
        self.previous_value = self.user_token.GetValue()
        self.user_token.Clear()
        event.Skip()

    def on_ut_key_press(self, event):
        if event.GetModifiers() == wx.MOD_CONTROL and event.GetKeyCode() == ord('Z'):
            self.user_token.SetValue(self.previous_value)
        else:
            event.Skip()       
    def update_page_tokens(self):
        is_valid =False
        if apc.pages:
            is_valid = check_page_token_validity()  
        print('First Valid:', is_valid)

        if not is_valid:
            set_page_access_tokens()
            print(777)
            #apc.dump_page_tokens()

            if 1:
                is_valid = check_page_token_validity()  
                print('Second Valid:', is_valid)



    def on_text_change(self, event):
        # This method will be called every time the text changes
        new_value=self.user_token.GetValue()
        apc.set_user_token(new_value)
        print(f"Key changed. New value: {apc.user_token}")
        if not apc.pages:
            try:
                set_page_access_tokens()
            except ErrorValidatingAccessToken as e:
                print(f"Error: {e}")
                print("User token expired. Resetting after update.")
                #apc.init_pages()

        if  new_value:
            #assert apc.pages
            self.update_page_tokens()
            self.reset_pages_combobox()

    def on_reel_hl(self, event):
        url = event.GetURL()
        webbrowser.open(url)        
    def on_select_page(self, event):
        # Get the selected index from the ComboBox
        selected_index = self.page_name.GetSelection()
        
        # Get the corresponding key using the index
        if selected_index != wx.NOT_FOUND:
            apc.page_id = self.keys[selected_index]
            print(f"Selected Key: {apc.page_id}")
        else:
            print("No valid selection.")
        print(222, apc.page_id)

    def _on_browse(self, event):
        downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', self.page_name.GetValue())

        with wx.FileDialog(self, "Choose a file", defaultDir=downloads_path, wildcard="*.*",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.file_ctrl.SetValue(pathname + ' ')
            self.LoadVideo(pathname)



    def on_browse(self, event):
        downloads_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads', self.page_name.GetValue())

        with wx.FileDialog(self, "Choose files", defaultDir=downloads_path, wildcard="*.mp4",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Get paths of all selected files
            pathnames = fileDialog.GetPaths()
            pp(pathnames)
            apc.set_input_files(pathnames)
            self.file_ctrl.SetValue(';'.join(pathnames) + ' ')



    def show_custom_dialog(parent, message):
        msg = textwrap.fill(message, width=60)  # Wrap text to 60 characters per line
        dialog = CustomWrappingDialog(parent, "Confirmation", msg, "Do you want to upload?")
        result = dialog.ShowModal()
        dialog.Destroy()
        return result 
    def show_upload_confirmation(self):
        msg = f"User: {apc.user}\nPage: {self.page_name.GetValue()}\nDescr: {apc.get_reel_descr()}"
        dialog = WrappingMessageDialog(self, msg, 'Do you want to upload?', wx.YES_NO | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        dialog.Destroy()
        return result
                
    def on_all(self, event=None):  
        # oppen dialog box to comnfirm yes/no
        # if yes, do all steps
        # if no, do nothing
        #message = f"User: {apc.user}\nPage: {self.page_name.GetValue()}\nDescr: {apc.get_reel_descr()}     "
        #ret=self.show_custom_dialog(message)   
        ret=self.show_upload_confirmation()
        if ret == wx.ID_NO:
            return  
        rfn=self.file_ctrl.GetValue().rstrip()  
        assert rfn,rfn
        self.add_scope_log()  
        

        wx.Yield()
        self.process_tasks()
    def show_redo_confirmation(self, scope_id):
        msg = f"User: {apc.user}\nPage: {self.page_name.GetValue()}\nDescr: {apc.get_reel_descr()}\nScope: {scope_id}"
        dialog = WrappingMessageDialog(self, msg, 'Do you want to REDO upload?', wx.YES_NO | wx.ICON_QUESTION)
        result = dialog.ShowModal()
        dialog.Destroy()
        return result
    def OnRedoScope(self, scope_id):  
        # oppen dialog box to comnfirm yes/no
        # if yes, do all steps
        # if no, do nothing
        #message = f"User: {apc.user}\nPage: {self.page_name.GetValue()}\nDescr: {apc.get_reel_descr()}     "
        #ret=self.show_custom_dialog(message)   
        ret=self.show_redo_confirmation(scope_id)
        if ret == wx.ID_NO:
            return  
        rfn=self.file_ctrl.GetValue().rstrip()  
        assert rfn,rfn
        #self.add_scope_log()  
        

        wx.Yield()
        self.redo_process_tasks(scope_id)

    def redo_process_tasks(self, scope_id):
        print('redo_process_tasks:',scope_id)
        assert apc.tasks
        
        #pp(apc.tasks)
        
        for task in apc.tasks:
            if not task['status'].endswith('.PUBLISHED'):
                print(111,task['status'], type(task))
                
                task=PropertyDefaultDict(task)
                self.redo_process_reel(task)
                
            else:
                print('Ignoring task', task['status'])
    def redo_process_reel(self, task):
        print('Processing task/reel:',task)
        if 1: #for file_id in apc.input_files:
            file_id=task['file_id']
            print(111,file_id)
            apc.input_files[file_id]=task['file_path']
            assert isfile(apc.input_files[file_id]), f'File "{file_id}" not found:'+apc.input_files[file_id]
            if 1:
                #pp(task)
                #e()
                
                #task.file_id=file_id
                #task.file_path=apc.input_files[file_id]

                pipeline=ReelUploader(apc.scope_rowid, task) 
                if 1:  
                    pipeline.on_validate()
                    pipeline.on_upload()
                    pipeline.wait_on_reel()

                    pipeline.on_publish()
    def process_tasks(self):
        assert apc.tasks
        
        pp(apc.tasks)
        for task in apc.tasks:
            if task.status in ['CREATED']:
                print(111,task)
                self.process_reel(task)
                
            else:
                print('Ignoring task',task, task.status)
                
    def process_reel(self, task):
        print('Processing task/reel:',task)
        if 1: #for file_id in apc.input_files:
            file_id=task['file_id']
            print(111,file_id)
            assert isfile(apc.input_files[file_id]), f'File "{file_id}" not found:'+apc.input_files[file_id]
            if 1:
                #pp(task)
                #e()
                
                #task.file_id=file_id
                #task.file_path=apc.input_files[file_id]

                pipeline=ReelUploader(apc.scope_rowid, task) 
                if 1:  
                    pipeline.on_validate()
                    pipeline.on_upload()
                    pipeline.wait_on_reel()

                    pipeline.on_publish()


    def add_scope_log(self):

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upload_scope=self.upload_scope.GetValue()

        scope=upload_scope
        if scope != 'default':
            
            assert scope in apc.scopes, scope   
            pp(apc.scopes[scope]) 
            user_id, _=scope.split(':')
        else:  
            user_id =apc.user
        row=PropertyDefaultDict({"scope":scope, "Date":current_datetime, "status":'CREATED',"type":'reel', 
            "file":self.file_ctrl.GetValue(),"user_id":user_id})
        self.task_log.next_rowid  =0
        apc.tasks=self.create_tasks(scope)
        #pp(apc.tasks)
        #e()
        #e()
        row['tasks']=apc.tasks
        
        apc.scope_log.add_item(row)
        #self.scope_log.add_row(self, scope, date, status, type)
        #self.scope_log.refresh_data ()
        rowid=self.scope_log.add_row(row)    
        scope_log_id= self.scope_log.get_scope_id(rowid)
        apc.scope_rowid=rowid
        #print(333,rowid, scope_log_id)
        apc.upload_log[scope_log_id]=[]
        #apc.scope_log_id=scope_log_id

        #create task list
        
        #apc.scope_log[rowid]['tasks']=tasks
        pub.sendMessage("update_scope_status", scope_id=rowid, status='TASKED_3')
        return rowid

    def create_tasks(self, scope): 
        out=[]
        if scope == 'default':
            task=f'{apc.user}:{self.page_name.GetValue()}' 
           # print(77,scope)
            #create single task 


            for file_id in apc.input_files: 
                row={"task":f'f{file_id}:{task}', "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status":'CREATED',"type":'reel',
                    "user_id":apc.user,
                    "page_id":apc.page_id,'scope':scope,
                    "reel_descr":apc.get_reel_descr(),
                    "page_name":task.split(':')[1],
                    "file_id":file_id,'file_path':apc.input_files[file_id]}


                task_id=self.task_log.add_row(row)   
                row['task_id']=task_id                 
                out.append  (PropertyDefaultDict(row))
        else:
            #scope=scope
            assert scope in apc.scopes, scope   
            #pp(apc.scopes[scope])

            for user in apc.scopes[scope]:
                user_pages=apc.scopes[scope][user]
                for page_id in user_pages:  
                    #print(88,page_id)  
                    page_name=apc.pages[page_id].page_name
                    task=f'{user}:{page_name}'  
                    for file_id in apc.input_files: 
                        row={"task":f'f{file_id}:{task}', "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status":'CREATED',"type":'reel',
                            "user_id":user,
                            "page_id":page_id,'scope':scope,
                            "reel_descr":apc.get_reel_descr(),
                            "page_name":page_name, 
                            "file_id":file_id,'file_path':apc.input_files[file_id]
                        }
                        #print(99,row)

                        task_id=self.task_log.add_row(row)   
                        row['task_id']=task_id   
                        out.append  (PropertyDefaultDict(row))



        return out
    def on_status(self, event=None):
        self.status_btn.Disable()
        get_page_metrics()
        try:
            status=check_status()
            self.log_ctrl.AppendText(self.pp(status))
            
        except Exception as e:

            self.log_ctrl.AppendText(f"Error during status check: {str(e)}\n")
            raise e
        finally:
            self.status_btn.Enable()
        print(f'https://www.facebook.com/reel/{apc.reel_id}')   
        print('on_status Done')


    def pp(slef, dd):
        return pformat(dd, indent=2, width=80) +os.linesep

    def on_close(self, event):
        self.Close()

if __name__ == '__main__':
    app = wx.App()
    frame = FileUploaderFrame()
    frame.Show()
    app.MainLoop()