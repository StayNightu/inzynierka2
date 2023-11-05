import cv2
from PIL import Image, ImageTk
from tkinter import filedialog
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

    def load_video(self):
        self.video_source = filedialog.askopenfilename(filetypes=[("Pliki MP4", "*.mp4"), ("Wszystkie pliki", "*.*")])
        if not self.video_source:
            return

        if self.vid:
            self.vid.release()

        self.vid = cv2.VideoCapture(self.video_source)
        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.config(width=self.width, height=self.height)

        self.callback()

    def play_video(self):
        if self.is_playing:  # Prevents playing if the video is already playing
            return
        self.is_playing = True
        self.callback()  # Update buttons' state when the video starts playing
        self.update()

    def stop_video(self):
        self.is_playing = False
        self.callback()

    def next_frame(self):
        if self.vid:
            ret, frame = self.vid.read()
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def prev_frame(self):
        if self.vid:
            # Pobierz aktualny indeks klatki
            frame_pos = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
            # Przesuń wideo o dwie klatki do tyłu
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_pos - 2)
            # Wyświetl poprzednią klatkę
            self.next_frame()

    def replay_video(self):
        if self.vid:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.play_video()

    def update(self):
        if self.is_playing:
            ret, frame = self.vid.read()
            if ret:
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                if self.image_on_canvas:
                    self.canvas.itemconfig(self.image_on_canvas, image=self.photo)  # aktualizowanie obrazu
                else:
                    self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

                self.window.after(10, self.update)
            else:
                self.stop_video()

    def is_video_opened(self):
        return self.vid is not None and self.vid.isOpened()
