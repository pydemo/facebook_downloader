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
        panel_width, panel_height = self.GetSize()
        print(panel_width, panel_height)
        # Create a larger blank image to use as the background, matching the panel size
        background_image = np.zeros((panel_height, panel_width, 3), dtype=np.uint8)

        msg = [
            "Drag and drop reel",
            "videos here"
        ]

        # Dynamically adjust the font scale based on panel size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(panel_width, panel_height) / 500  # Adjust this divisor for scaling
        font_color = (255, 255, 255)
        thickness = 2
        line_type = cv2.LINE_AA

        # Calculate total text height
        text_size = cv2.getTextSize(msg[0], font, font_scale, thickness)[0]
        line_height = text_size[1] + 10

        # Calculate starting Y position to center the text vertically
        y = (background_image.shape[0] - len(msg) * line_height) // 2

        for line in msg:
            text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
            x = (background_image.shape[1] - text_size[0]) // 2  # Center horizontally
            y += line_height
            cv2.putText(background_image, line, (x, y), font, font_scale, font_color, thickness, line_type)

        # Assign the background image as the current image to display
        self.images = [background_image]
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
        
        if num_images == 1:
            # If there is only one image, resize it to fit the entire panel
            resized_image = cv2.resize(self.images[0], (width, height))
            bitmap = wx.Bitmap.FromBuffer(resized_image.shape[1], resized_image.shape[0], resized_image)
            dc.DrawBitmap(bitmap, 0, 0)
        else:
            # If there are multiple images, arrange them in a grid
            cols = math.ceil(math.sqrt(num_images))
            rows = math.ceil(num_images / cols)

            img_width = width // cols
            img_height = height // rows

            for i, image in enumerate(self.images):
                row = i // cols
                col = i % cols

                # Resize each image to fit within its grid cell
                resized_image = cv2.resize(image, (img_width, img_height))
                height, width = resized_image.shape[:2]
                bitmap = wx.Bitmap.FromBuffer(width, height, resized_image)

                # Draw each image in the corresponding grid position
                dc.DrawBitmap(bitmap, col * img_width, row * img_height)

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
        # Update the label text
        self.GetTopLevelParent().UpdateImageCount(len(self.images))  # Use GetTopLevelParent() to access MainFrame

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
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)

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
        sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSize(800, 1000)
        self.Show()

        # Show the default message
        self.image_panel.ShowDefaultMessage()

    def OnClear(self, event):
        self.image_panel.ClearImages()
        self.image_panel.ShowDefaultMessage()
        self.UpdateImageCount(0)

    def UpdateImageCount(self, count):
        self.image_count_label.SetLabel(f"{count} images loaded")

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
