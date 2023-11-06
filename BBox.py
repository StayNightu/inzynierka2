import tkinter as tk
from tkinter import simpledialog

class BBox:
    def __init__(self, video_manager):
        self.video_manager = video_manager
        self.canvas = video_manager.canvas
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bboxes = {}  # Dictionary to store bbox IDs and their rectangle objects
        self.current_id = 0  # Start IDs from 0

    def set_bbox(self):
        self.canvas.bind("<ButtonPress-1>", self.on_start)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_start(self, event):
        # Store the initial point
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # Create a rectangle
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def on_release(self, event):
        self.current_id += 1
        bbox_id = "ID: " + str(self.current_id)
        self.bboxes[self.current_id] = self.rect

        x, y, _, _ = self.canvas.coords(self.rect)
        self.canvas.create_text(x + 10, y, text=bbox_id, fill="red", anchor=tk.NW)

        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.video_manager.bbox_coords[self.current_id] = (x1, y1, x2, y2)

        # Reset the rectangle
        self.rect = None
