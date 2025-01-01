import wx
import cv2
import numpy as np
import os
from pprint import pprint as pp


class ImagePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.bitmap = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Enable drag and drop
        self.SetDropTarget(FileDropTarget(self))

    def SetImage(self, image):
        self.original_image = image
        self.ResizeImage()

    def ResizeImage(self):
        if hasattr(self, 'original_image'):
            size = self.GetSize()
            image = self.resize_image(self.original_image, size.width, size.height)
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

    def get_first_frame(self, video_path):
        video = cv2.VideoCapture(video_path)
        ret, frame = video.read()
        video.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def resize_image(self, image, max_width, max_height):
        h, w = image.shape[:2]
        aspect = w / h
        if h * aspect > max_width:
            new_w = max_width
            new_h = int(new_w / aspect)
        else:
            new_h = max_height
            new_w = int(aspect * new_h)
        return cv2.resize(image, (new_w, new_h))

    def LoadFile(self, filepath):
        _, file_extension = os.path.splitext(filepath)
        if file_extension.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
            image = cv2.imread(filepath)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.SetImage(image)
        elif file_extension.lower() in ['.mp4', '.avi', '.mov']:
            image = self.get_first_frame(filepath)
            if image is not None:
                self.SetImage(image)
        else:
            wx.MessageBox("Unsupported file format", "Error", wx.OK | wx.ICON_ERROR)

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        pp(filenames)
        if filenames:
            
            self.window.LoadFile(filenames[0])
        return True

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Image Viewer with Drag and Drop')
        panel = wx.Panel(self)
        self.image_panel = ImagePanel(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.image_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.SetSize(800, 600)
        self.Show()

        # Load a default image or display a message
        default_image = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.putText(default_image, "Drag and drop an image here", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        self.image_panel.SetImage(default_image)

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()