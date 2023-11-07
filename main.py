import os
import tkinter as tk

from CSV_plik import CSVDisplay
from Sledzenie import Sledzenie
from Video import VideoPlayer
from BBox import BBox
from podzial import podzial

class Main:
    def __init__(self, root, title):
        self.root = root
        self.root.title(title)

        self.btn_clicked = False
        self.editing_mode = False

        self.canvas = tk.Canvas(root)
        self.canvas.pack(pady=20)

        self.video_manager = VideoPlayer(self.root, self.canvas, self.update_buttons_state)
        self.podzial_instance = podzial(self)
        self.sledzenie = Sledzenie()
        self.csv_display = CSVDisplay(self)
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=20)

        self.btn_select = tk.Button(self.buttons_frame, text="Wybierz wideo", width=15, command=self.on_select_video)
        self.btn_select.grid(row=0, column=1, padx=5, pady=10)

        self.btn_play_output = tk.Button(self.buttons_frame, text="Odtwórz", width=15, command=self.on_play_output, state=tk.NORMAL)
        self.btn_play_output.grid(row=0, column=2, padx=5, pady=10)

        self.btn_play = tk.Button(self.buttons_frame, text="Wzów odtwarzanie", width=15, command=self.video_manager.play_video, state=tk.DISABLED)
        self.btn_play.grid(row=0, column=3, padx=5, pady=10)

        self.btn_stop = tk.Button(self.buttons_frame, text="Zatrzymaj", width=10, command=self.video_manager.stop_video, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=4, padx=5, pady=10)

        self.btn_bbox = tk.Button(self.buttons_frame, text="Ustaw BBox", width=15, command=self.on_set_bbox, state=tk.NORMAL)
        self.btn_bbox.grid(row=1, column=2, padx=5, pady=10)

        self.btn_divide = tk.Button(self.buttons_frame, text="Dziel wideo na klatki", width=20, command=self.podzial_instance.divide_video_into_frames)
        self.btn_divide.grid(row=1, column=4, padx=5, pady=10)

        self.btn_show_current = tk.Button(self.buttons_frame, text="Pokaż aktualny obraz", width=20, command=self.podzial_instance.show_current_image, state=tk.NORMAL)
        self.btn_show_current.grid(row=2, column=1, padx=5, pady=10)

        self.btn_next_image = tk.Button(self.buttons_frame, text="Następny obraz", width=15, command=self.podzial_instance.display_next_image, state=tk.NORMAL)
        self.btn_next_image.grid(row=2, column=2, padx=5, pady=10)

        self.btn_prev_image = tk.Button(self.buttons_frame, text="Poprzedni obraz", width=15, command=self.podzial_instance.display_prev_image, state=tk.NORMAL)
        self.btn_prev_image.grid(row=2, column=3, padx=5, pady=10)


    def on_play_output(self):
        self.video_manager.set_video("output.avi")
        self.video_manager.load_video()
        self.video_manager.play_video()

    def on_select_video(self):
        selected_video_path = self.sledzenie.load_video()
        if selected_video_path:
            self.sledzenie.run()
        self.update_buttons_state()

    def reset_btn_flag(self):
        self.btn_clicked = False

    def update_buttons_state(self):
        if self.video_manager.is_video_opened():
            self.btn_play.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)

        else:
            self.btn_play.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
        if os.path.exists("output.avi"):
            self.btn_play_output.config(state=tk.NORMAL)
        else:
            self.btn_play_output.config(state=tk.DISABLED)
        if self.podzial_instance.current_image_index < len(self.podzial_instance.image_paths) - 1:
            self.podzial_instance.main_instance.btn_next_image.config(state=tk.NORMAL)
        else:
            self.podzial_instance.main_instance.btn_next_image.config(state=tk.DISABLED)

        if self.podzial_instance.current_image_index > 0:
            self.podzial_instance.main_instance.btn_prev_image.config(state=tk.NORMAL)
        else:
            self.podzial_instance.main_instance.btn_prev_image.config(state=tk.DISABLED)

    def on_set_bbox(self):
        bbox_handler = BBox(self.podzial_instance)
        bbox_handler.set_bbox()

def toggle_fullscreen(event=None):
    state = not root.attributes('-fullscreen')
    root.attributes('-fullscreen', state)
    return "break"

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("250x250")  # Ustaw rozmiar głównego okna jeśli potrzebujesz
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", toggle_fullscreen)
    app = Main(root, "Odtwarzacz wideo")
    root.mainloop()