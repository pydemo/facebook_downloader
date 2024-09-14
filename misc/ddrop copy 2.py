import wx
import cv2
import numpy as np
import os
import math

class ImagePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.images = []
        self.showing_default = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Enable drag and drop
        self.SetDropTarget(FileDropTarget(self))

    def SetImages(self, images):
        self.images = images
        self.showing_default = False
        self.Refresh()

    def ClearImages(self):
        self.images.clear()
        self.showing_default = False
        self.Refresh()

    def ShowDefaultMessage(self):
        default_image = np.zeros((300, 400, 3), dtype=np.uint8)
        msg = [
            "Drag and drop reel",
            "videos here"
        ]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_color = (255, 255, 255)
        thickness = 2
        line_type = cv2.LINE_AA

        # Calculate total text height
        text_size = cv2.getTextSize(msg[0], font, font_scale, thickness)[0]
        line_height = text_size[1] + 10

        # Calculate starting Y position to center the text vertically
        y = (default_image.shape[0] - len(msg) * line_height) // 2

        for i, line in enumerate(msg):
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            x = (default_image.shape[1] - text_size[0]) // 2  # Center horizontally
            y += line_height
            cv2.putText(default_image, line, (x, y), font, font_scale, font_color, thickness, line_type)

        self.images = [default_image]
        self.showing_default = True
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DrawImages(dc)

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def DrawImages(self, dc):
        if not self.images:
            return

        width, height = self.GetSize()
        num_images = len(self.images)
        cols = math.ceil(math.sqrt(num_images))
        rows = math.ceil(num_images / cols)

        img_width = width // cols
        img_height = height // rows

        for i, image in enumerate(self.images):
            row = i // cols
            col = i % cols

            # Calculate aspect ratio
            img_aspect = image.shape[1] / image.shape[0]
            panel_aspect = img_width / img_height

            if img_aspect > panel_aspect:
                # Image is wider than panel, fit to width
                new_width = img_width
                new_height = int(img_width / img_aspect)
            else:
                # Image is taller than panel, fit to height
                new_height = img_height
                new_width = int(img_height * img_aspect)

            # Center the image
            x_offset = (img_width - new_width) // 2
            y_offset = (img_height - new_height) // 2

            resized_image = cv2.resize(image, (new_width, new_height))
            height, width = resized_image.shape[:2]
            bitmap = wx.Bitmap.FromBuffer(width, height, resized_image)

            dc.DrawBitmap(bitmap, col * img_width + x_offset, row * img_height + y_offset)


    def get_first_frame(self, video_path):
        video = cv2.VideoCapture(video_path)
        ret, frame = video.read()
        video.release()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def LoadFiles(self, filepaths):
        new_images = []
        for filepath in filepaths:
            _, file_extension = os.path.splitext(filepath)
            if file_extension.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                image = cv2.imread(filepath)
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    new_images.append(image)
            elif file_extension.lower() in ['.mp4', '.avi', '.mov']:
                image = self.get_first_frame(filepath)
                if image is not None:
                    new_images.append(image)
            else:
                wx.MessageBox(f"Unsupported file format: {filepath}", "Error", wx.OK | wx.ICON_ERROR)
        
        self.SetImages(new_images)  # Use SetImages instead of AddImages

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.LoadFiles(filenames)
        return True

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Multi-file Image Viewer with Grid Layout')
        panel = wx.Panel(self)
        self.image_panel = ImagePanel(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.image_panel, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        # Add a clear button
        self.clear_button = wx.Button(panel, label="Clear Images")
        self.clear_button.Bind(wx.EVT_BUTTON, self.OnClear)
        sizer.Add(self.clear_button, 0, wx.ALL | wx.CENTER, 5)

        self.SetSize(800, 1200)
        self.Show()

        # Show the default message
        self.image_panel.ShowDefaultMessage()

    def OnClear(self, event):
        self.image_panel.ClearImages()
        self.image_panel.ShowDefaultMessage()

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()