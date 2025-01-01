import wx
import cv2
import numpy as np

def get_first_frame(video_path):
    video = cv2.VideoCapture(video_path)
    ret, frame = video.read()
    video.release()
    if ret:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return None

def resize_image(image, max_width, max_height):
    h, w = image.shape[:2]
    aspect = w / h
    if h * aspect > max_width:
        new_w = max_width
        new_h = int(new_w / aspect)
    else:
        new_h = max_height
        new_w = int(aspect * new_h)
    return cv2.resize(image, (new_w, new_h))

class ImagePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.bitmap = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetImage(self, image):
        self.original_image = image
        self.ResizeImage()

    def ResizeImage(self):
        if hasattr(self, 'original_image'):
            size = self.GetSize()
            image = resize_image(self.original_image, size.width, size.height)
            height, width = image.shape[:2]
            self.bitmap = wx.Bitmap.FromBuffer(width, height, image)
            self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        if self.bitmap:
            dc.DrawBitmap(self.bitmap, 0, 0, True)

    def OnSize(self, event):
        self.ResizeImage()
        event.Skip()

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Video Frame Viewer', size=(1200, 800))
        panel = wx.Panel(self)
        
        self.file_ctrl = wx.TextCtrl(panel)
        browse_button = wx.Button(panel, label="Browse")
        browse_button.Bind(wx.EVT_BUTTON, self.OnBrowse)
        
        self.image_panel = ImagePanel(panel)
        self.log_ctrl = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        file_sizer.Add(self.file_ctrl, 1, wx.EXPAND)
        file_sizer.Add(browse_button, 0, wx.LEFT, 5)
        
        content_sizer.Add(self.image_panel, 1, wx.EXPAND | wx.RIGHT, 5)
        content_sizer.Add(self.log_ctrl, 1, wx.EXPAND | wx.LEFT, 5)
        
        main_sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(content_sizer, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer)
        
        self.Show()

    def OnBrowse(self, event):
        wildcard = "MP4 files (*.mp4)|*.mp4"
        dialog = wx.FileDialog(self, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.file_ctrl.SetValue(file_path)
            self.LoadVideo(file_path)
        
        dialog.Destroy()

    def LoadVideo(self, file_path):
        frame = get_first_frame(file_path)
        if frame is not None:
            self.image_panel.SetImage(frame)
            self.LogMessage(f"Loaded first frame from: {file_path}")
        else:
            wx.MessageBox("Failed to load video frame", "Error", wx.OK | wx.ICON_ERROR)
            self.LogMessage(f"Failed to load frame from: {file_path}")

    def LogMessage(self, message):
        self.log_ctrl.AppendText(message + "\n")

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()