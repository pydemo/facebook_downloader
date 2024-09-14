import wx
import cv2
import numpy as np
from os.path import isfile  
import os
import math
from pprint import pprint as pp
import include.config.init_config as init_config 
apc = init_config.apc
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
        print('in setimages', images)
        assert images, "No images to display"
        self.images = images
        self.showing_default = False
        self.Refresh()

    def ClearImages(self):
        self.images.clear()
        self.showing_default = False
        self.Refresh()

    def ShowDefaultMessage(self):
        panel_width, panel_height = self.GetSize()
        #print(444444,panel_width, panel_height)
        #print(444444,self.Parent.Parent.GetSize())

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
        input_files=[]
        print(2222, filepaths   )
        for filepath in filepaths:
            print(9999, filepath)
            _, file_extension = os.path.splitext(filepath)
            assert file_extension.lower() in ['.mp4', '.avi', '.mov'], f"Unsupported file format: {filepath}"
            if file_extension.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                image = cv2.imread(filepath)
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    new_images.append(image)
            elif file_extension.lower() in ['.mp4', '.avi', '.mov']:
                if isfile(filepath):
                    input_files.append(filepath)
                    image = self.get_first_frame(filepath)
                    if image is not None:
                        new_images.append(image)
                    else:
                        raise Exception(f"Could not load video: {filepath}")
            else:
                wx.MessageBox(f"Unsupported file format: {filepath}", "Error", wx.OK | wx.ICON_ERROR)
        if input_files:
            
            self.SetImages(new_images)  # Use SetImages instead of AddImages
            # Update the label text
            self.GetTopLevelParent().UpdateImageCount(len(self.images))  # Use GetTopLevelParent() to access MainFrame
        return len(input_files)
        #apc.input_files=input_files
class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.LoadFiles(filenames)
        apc.set_input_files(filenames)
        return True

