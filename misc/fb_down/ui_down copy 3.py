import wx
import threading
import os
import uuid
import sys
from os.path import isfile, isdir, join
from down import download_facebook_video
import yt_dlp
from io import StringIO

class StreamToLogger:
    def __init__(self, log_callback):
        self.log_callback = log_callback

    def write(self, message):
        if message.strip():  # Only log non-empty messages
            self.log_callback(message)

    def flush(self):
        pass  # No need to implement flush for this use case

class DownloaderFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Facebook Video Downloader')
        panel = wx.Panel(self)

        # URL input
        self.url_label = wx.StaticText(panel, label="URL:")
        self.url_ctrl = wx.TextCtrl(panel, size=(300, -1))

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

        # Log display
        self.log_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 200))

        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        url_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cookie_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        url_sizer.Add(self.url_label, 0, wx.ALL | wx.CENTER, 5)
        url_sizer.Add(self.url_ctrl, 0, wx.ALL, 5)
        url_sizer.Add(self.download_btn, 0, wx.ALL | wx.CENTER, 5)
        cookie_sizer.Add(self.cookie_label, 0, wx.ALL | wx.CENTER, 5)
        cookie_sizer.Add(self.cookie_ctrl, 0, wx.ALL, 5)
        cookie_sizer.Add(self.cookie_btn, 0, wx.ALL, 5)

        main_sizer.Add(url_sizer, 0, wx.ALL, 5)
        main_sizer.Add(cookie_sizer, 0, wx.ALL, 5)
        
        main_sizer.Add(self.log_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(main_sizer)
        self.SetSize(500, 400)
        self.Centre()

    def on_browse_cookie(self, event):
        with wx.FileDialog(self, "Select Cookie File", wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.cookie_ctrl.SetValue(fileDialog.GetPath())

    def on_download(self, event):
        url = self.url_ctrl.GetValue()
        cookie_file = self.cookie_ctrl.GetValue()
        if not url or not cookie_file:
            self.log("Please enter a URL and select a cookie file.")
            return

        self.download_btn.Disable()
        threading.Thread(target=self.download_video, args=(url, cookie_file), daemon=True).start()

    def download_video(self, url, cookie_file):
        output_path = 'downloads'
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = StreamToLogger(self.log)
        sys.stderr = StreamToLogger(self.log)

        try:
            self.log(f"Downloading video from: {url}")
            self.log(f"Using cookie file: {cookie_file}")

            downloaded_file = download_facebook_video(url, output_path, cookie_file)

            if downloaded_file:
                self.log(f"Downloaded video: {downloaded_file}")
                self.process_downloaded_file(downloaded_file)
            else:
                self.log("Failed to download the video.")
        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        wx.CallAfter(self.download_btn.Enable)

    def process_downloaded_file(self, downloaded_file):
        output_path = 'downloads'
        random_prefix = str(uuid.uuid4())
        new_downloaded_file = join(output_path, f"{random_prefix}_{os.path.basename(downloaded_file)}")
        self.log(f"Renaming {downloaded_file} to {new_downloaded_file}")
        os.rename(downloaded_file, new_downloaded_file)

        latest_output_path = join('downloads', 'latest')
        if not isdir(latest_output_path):
            os.makedirs(latest_output_path)
        else:
            backup_path = join('downloads', 'backup')
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

    def log(self, message):
        wx.CallAfter(self.log_ctrl.AppendText, message + "\n")

if __name__ == '__main__':
    app = wx.App()
    frame = DownloaderFrame()
    frame.Show()
    app.MainLoop()
