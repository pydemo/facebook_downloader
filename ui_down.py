from __future__ import unicode_literals
import wx
import threading
import webbrowser
import os, sys
import uuid
from os.path import isfile, isdir, join
import yt_dlp
from pprint import pprint as pp 
import include.config.init_config as init_config 

init_config.init(**{})
apc = init_config.apc

e= sys.exit

class ClickableURL(wx.TextCtrl):
    def __init__(self, parent, id=-1, value="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator,
                 name=wx.TextCtrlNameStr):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style|wx.TE_READONLY, validator, name)
        self.SetForegroundColour(wx.BLUE)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        font = self.GetFont()
        font.SetUnderlined(True)
        self.SetFont(font)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClick)
        self.url = ""

    def OnClick(self, event):
        if self.url:
            webbrowser.open(self.url)

    def SetUrlAndTitle(self, url, title):
        self.url = url
        self.SetValue(title)

class CustomLogger:
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def debug(self, msg):
        self.log_callback(f"DEBUG: {msg}")

    def info(self, msg):
        self.log_callback(f"INFO: {msg}")

    def warning(self, msg):
        self.log_callback(f"WARNING: {msg}")

    def error(self, msg):
        self.log_callback(f"ERROR: {msg}")

def download_facebook_video(video_url, output_path, cookie_file, log_callback):
    bn=uuid.uuid4()
    out_fn = f'{output_path}/{bn}.%(ext)s'
    ydl_opts = {
        'outtmpl': out_fn,
        'verbose': True,
        'cookiefile': cookie_file,
        'format': 'best',
        'no_warnings': False,
        'ignoreerrors': False,
        'logger': CustomLogger(log_callback),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            
            if info:
                log_callback(f"Video title: {info.get('title', 'Unknown')}")
                log_callback(f"Available formats: {len(info.get('formats', []))}")
                
                if info.get('formats'):
                    filename = ydl.prepare_filename(info)
                    download_result = ydl.download([video_url])
                    
                    if download_result == 0:  # 0 indicates success
                        log_callback(f"Download successful. Result code: {download_result}")
                        return filename
                    else:
                        log_callback(f"Download failed. Result code: {download_result}")
                else:
                    log_callback("No formats found. The video might be private or restricted.")
            else:
                log_callback("Failed to extract video information.")
                
        except Exception as e:
            log_callback(f"An error occurred: {str(e)}")
            log_callback("Please check the video URL, your cookie file, and your internet connection.")
            log_callback("If the problem persists, consider reporting this issue to the yt-dlp GitHub repository.")
    
    return None 

class DownloaderFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Facebook Video Downloader')
        panel = wx.Panel(self)
        self.page_name = wx.ComboBox(panel, choices=["Any", "ArtForUkraine", "Sexy"], style=wx.CB_DROPDOWN)
        self.page_name.SetValue("ArtForUkraine")
        # URL input
        #self.url_label = wx.StaticText(panel, label="URL:")
        self.url_ctrl = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PROCESS_ENTER)
        self.url_ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_download)
        self.url_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_url_ctrl_focus) 

        # Download button
        self.download_btn = wx.Button(panel, label="Download")
        self.download_btn.Bind(wx.EVT_BUTTON, self.on_download)
        
        # Cookie file input
        self.cookie_label = wx.StaticText(panel, label="Cookie File:")
        self.cookie_ctrl = wx.TextCtrl(panel, size=(200, -1))

        default_cookie_file = os.path.join(os.getcwd(), 'cookies.txt')
        self.cookie_ctrl.SetValue(default_cookie_file)
        self.cookie_btn = wx.Button(panel, label="Browse")
        self.cookie_btn.Bind(wx.EVT_BUTTON, self.on_browse_cookie)

        # Open latest directory button
        self.latest_dir_btn = wx.Button(panel, label="Latest")
        self.latest_dir_btn.Bind(wx.EVT_BUTTON, self.on_open_latest_dir)
        self.backup_dir_btn = wx.Button(panel, label="Backup")
        self.backup_dir_btn.Bind(wx.EVT_BUTTON, self.on_open_backup_dir)
        # Log display
        self.log_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 200))
        self.create_url = ClickableURL(panel, size=(-1, -1))
        self.create_url.SetUrlAndTitle('https://www.facebook.com/reels/create', 'Create')

        self.reels_url = ClickableURL(panel, size=(-1, -1))
        self.reels_url.SetUrlAndTitle('https://www.facebook.com/profile.php?id=100083627761445&sk=reels_tab', 'Reels')

        


        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cookie_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        url_sizer.Add(self.page_name, 0, wx.ALL | wx.CENTER, 5)
        url_sizer.Add(self.url_ctrl, 0, wx.ALL, 5)
        url_sizer.Add(self.download_btn, 0, wx.ALL | wx.CENTER, 5)
        
        cookie_sizer.Add(self.cookie_label, 0, wx.ALL | wx.CENTER, 5)
        cookie_sizer.Add(self.cookie_ctrl, 0, wx.ALL, 5)
        cookie_sizer.Add(self.cookie_btn, 0, wx.ALL, 5)

        main_sizer.Add(url_sizer, 0, wx.ALL, 5)
        main_sizer.Add(cookie_sizer, 0, wx.ALL, 5)
        
        main_sizer.Add(self.log_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        reels_url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        reels_url_sizer.Add(self.create_url, 0, wx.LEFT , 5)
        reels_url_sizer.Add(self.reels_url, 0, wx.LEFT , 5)
        reels_url_sizer.Add(self.backup_dir_btn, 1,  wx.RIGHT, 5)
        reels_url_sizer.Add(self.latest_dir_btn, 1,  wx.RIGHT, 5)
        main_sizer.Add(reels_url_sizer, 0, wx.ALL | wx.EXPAND, 0)
        panel.SetSizer(main_sizer)
        self.SetSize(500, 500)
        self.Centre()

    def download_completed(self):
        self.download_btn.Enable()
        self.shift_focus_to_log()

    def on_url_ctrl_focus(self, event):
        wx.CallAfter(self.highlight_url_ctrl)
        self.url_ctrl.SetValue("")
        event.Skip()

    def highlight_url_ctrl(self):
        self.url_ctrl.SetSelection(-1, -1)  # Select all text
        #self.log("URL control text highlighted")
    def on_browse_cookie(self, event):
        with wx.FileDialog(self, "Select Cookie File", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.cookie_ctrl.SetValue(fileDialog.GetPath())
    def shift_focus_to_log(self):
        self.log_ctrl.SetFocus()
        self.log_ctrl.SetInsertionPointEnd()
        self.log("Download completed. Focus shifted to log.")
    def on_download(self, event):
        url = self.url_ctrl.GetValue()
        cookie_file = self.cookie_ctrl.GetValue()
        if not url or not cookie_file:
            self.log("Please enter a URL and select a cookie file.")
            return
        

        self.download_btn.Disable()
        if url.startswith('https://youtu.be'):
            threading.Thread(target=self.download_youtube_video, args=(url, cookie_file, self.log), daemon=True).start()
        else:
            threading.Thread(target=self.download_video, args=(url, cookie_file), daemon=True).start()
    def download_youtube_video(self, url, output_path, log_callback):
        page_name=self.page_name.GetValue()
        output_path = join('downloads', page_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.log(f"Downloading video from: {url}")

        ydl_opts = {
            'format': 'mp4',
            'outtmpl': output_path.rstrip('/')+'/%(title)s.%(ext)s',
            'verbose': True,  # Enable verbose output
        }

        pp(ydl_opts) 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)

            # Extract the file name from the result
            if 'requested_downloads' in result:
                downloaded_file = result['requested_downloads'][0]['_filename']
                print(f"Downloaded file path: {downloaded_file}")
                if downloaded_file:
                    self.log(f"Downloaded video: {downloaded_file}")
                    self.process_downloaded_file(downloaded_file)
                else:
                    self.log("Failed to download the video.")

            else:
                print("No file downloaded.")
        wx.CallAfter(self.download_btn.Enable)
        wx.CallAfter(self.download_completed)            


    def download_video(self, url, cookie_file):
        page_name=self.page_name.GetValue()
        output_path = join('downloads', page_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.log(f"Downloading video from: {url}")
        self.log(f"Using cookie file: {cookie_file}")

        downloaded_file = download_facebook_video(url, output_path, cookie_file, self.log)
        
        if downloaded_file:
            self.log(f"Downloaded video: {downloaded_file}")
            self.process_downloaded_file(downloaded_file)
        else:
            self.log("Failed to download the video.")

        wx.CallAfter(self.download_btn.Enable)
        wx.CallAfter(self.download_completed)

    def process_downloaded_file(self, downloaded_file):
        page_name=self.page_name.GetValue()
        output_path = join('downloads', page_name)
        random_prefix = str(uuid.uuid4())
        new_downloaded_file = join(output_path, f"{random_prefix}_{os.path.basename(downloaded_file)}")
        self.log(f"Renaming {downloaded_file} to {new_downloaded_file}")
        os.rename(downloaded_file, new_downloaded_file)

        latest_output_path = join('downloads',page_name, 'latest')
        if not isdir(latest_output_path):
            os.makedirs(latest_output_path)
        else:
            backup_path = join('downloads',page_name, 'backup')
            if not isdir(backup_path):
                os.makedirs(backup_path)
            files = [f for f in os.listdir(latest_output_path) if isfile(join(latest_output_path, f))]
            if files:
                latest_file = join(latest_output_path, files[0])
                os.rename(latest_file, join(backup_path, os.path.basename(latest_file)))
                self.log(f"Moved previous latest file to backup: {latest_file}")

        final_path = join(latest_output_path, os.path.basename(new_downloaded_file))
        os.rename(new_downloaded_file, final_path)
        self.log(f"Moved downloaded file to latest: {final_path}")

    def on_open_backup_dir(self, event):
        page_name=self.page_name.GetValue()
        backup_output_path = join('downloads', page_name, 'backup')
        if isdir(backup_output_path):
            try:
                os.startfile(backup_output_path)
            except AttributeError:
                # startfile is not available on non-Windows platforms
                self.log("Opening file explorer is only supported on Windows.")
        else:
            self.log("Latest download directory does not exist yet.")
    def on_open_latest_dir(self, event):
        page_name=self.page_name.GetValue()
        latest_output_path = join('downloads',page_name, 'latest')
        if isdir(latest_output_path):
            try:
                os.startfile(latest_output_path)
            except AttributeError:
                # startfile is not available on non-Windows platforms
                self.log("Opening file explorer is only supported on Windows.")
        else:
            self.log("Latest download directory does not exist yet.")

    def log(self, message):
        wx.CallAfter(self.log_ctrl.AppendText, message + "\n")

if __name__ == '__main__':
    app = wx.App()
    frame = DownloaderFrame()
    frame.Show()
    app.MainLoop()