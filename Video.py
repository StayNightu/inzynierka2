import cv2
from PIL import Image, ImageTk
import tkinter as tk
class VideoPlayer:
    def __init__(self, window, canvas, callback=None):
        self.window = window
        self.canvas = canvas
        self.video_source = ""
        self.vid = None
        self.is_playing = False
        self.callback = callback
        self.image_on_canvas = None
        self.bbox_coords = {}

    def set_video(self, video_path):
        self.video_source = video_path

    def load_video(self):
        if self.vid:
            self.vid.release()

        self.vid = cv2.VideoCapture(self.video_source)
        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.config(width=self.width, height=self.height)

        self.callback()

    def play_video(self):
        if self.is_playing:
            return
        self.is_playing = True
        self.callback()
        self.update()

    def stop_video(self):
        self.is_playing = False
        self.callback()

    def update(self):
        if self.is_playing:
            ret, frame = self.vid.read()
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                if self.image_on_canvas:
                    self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
                else:
                    self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

                self.window.after(10, self.update)
            else:
                self.stop_video()

    def is_video_opened(self):
        return self.vid is not None and self.vid.isOpened()

    def export_with_bboxes(self, output_folder="output_frames"):
        import os

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        frame_count = 0
        while True:
            ret, frame = self.vid.read()
            if not ret:
                break

            # Draw each bbox on the frame
            for _, coords in self.bbox_coords.items():
                x1, y1, x2, y2 = map(int, coords)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Save the frame as an image
            frame_path = os.path.join(output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

        print(f"Frames saved in {output_folder}")