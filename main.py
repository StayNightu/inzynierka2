import os
import tkinter as tk
from Sledzenie import Sledzenie
from Video import VideoPlayer
from CSV_plik import CSVDisplay
from BBox import BBox

class Main:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.btn_clicked = False
        self.editing_mode = False

        self.canvas = tk.Canvas(window)
        self.canvas.pack(pady=20)

        self.video_manager = VideoPlayer(self.window, self.canvas, self.update_buttons_state)
        self.sledzenie = Sledzenie()
        self.buttons_frame = tk.Frame(window)
        self.buttons_frame.pack(pady=20)

        self.btn_select = tk.Button(self.buttons_frame, text="Wybierz wideo", width=15, command=self.on_select_video)
        self.btn_select.grid(row=0, column=1, padx=5, pady=10)

        self.btn_play_output = tk.Button(self.buttons_frame, text="Odtwórz", width=15, command=self.on_play_output, state=tk.NORMAL)
        self.btn_play_output.grid(row=0, column=2, padx=5, pady=10)

        self.btn_play = tk.Button(self.buttons_frame, text="Wzów odtwarzanie", width=15, command=self.video_manager.play_video, state=tk.DISABLED)
        self.btn_play.grid(row=0, column=3, padx=5, pady=10)

        self.btn_stop = tk.Button(self.buttons_frame, text="Zatrzymaj", width=10, command=self.video_manager.stop_video, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=4, padx=5, pady=10)

        self.btn_next_frame = tk.Button(self.buttons_frame, text="Następna klatka", width=15, command=self.video_manager.next_frame, state=tk.DISABLED)
        self.btn_next_frame.grid(row=0, column=5, padx=5, pady=10)

        self.btn_prev_frame = tk.Button(self.buttons_frame, text="Poprzednia klatka", width=17, command=self.video_manager.prev_frame, state=tk.DISABLED)
        self.btn_prev_frame.grid(row=0, column=6, padx=5, pady=10)

        self.btn_replay = tk.Button(self.buttons_frame, text="Odtwórz od nowa", width=15, command=self.video_manager.replay_video, state=tk.DISABLED)
        self.btn_replay.grid(row=1, column=1, padx=5, pady=10)

        self.btn_bbox = tk.Button(self.buttons_frame, text="Ustaw BBox", width=15, command=self.on_set_bbox, state=tk.DISABLED)
        self.btn_bbox.grid(row=1, column=2, padx=5, pady=10)

        self.btn_export_bbox = tk.Button(self.buttons_frame, text="Zapisz zmienione", width=15,
                                         command=self.video_manager.export_with_bboxes)
        self.btn_export_bbox.grid(row=1, column=3, padx=5, pady=10)

        self.show_csv()

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

    def show_csv(self):
        csv_display = CSVDisplay(self.window, "1.csv")
        csv_display.run()

    def update_buttons_state(self):
        if self.video_manager.is_video_opened():
            self.btn_play.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_replay.config(state=tk.NORMAL)

            if not self.video_manager.is_playing:
                self.btn_next_frame.config(state=tk.NORMAL)
                self.btn_prev_frame.config(state=tk.NORMAL)
            else:
                self.btn_next_frame.config(state=tk.DISABLED)
                self.btn_prev_frame.config(state=tk.DISABLED)
        else:
            self.btn_play.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_next_frame.config(state=tk.DISABLED)
            self.btn_prev_frame.config(state=tk.DISABLED)
            self.btn_replay.config(state=tk.DISABLED)
        if os.path.exists("output.avi"):
            self.btn_play_output.config(state=tk.NORMAL)
        else:
            self.btn_play_output.config(state=tk.DISABLED)
        if self.video_manager.is_video_opened():
            self.btn_bbox.config(state=tk.NORMAL)
        else:
            self.btn_bbox.config(state=tk.DISABLED)

    def on_set_bbox(self):
        bbox_handler = BBox(self.video_manager)
        bbox_handler.set_bbox()

def toggle_fullscreen(event=None):
    state = not root.attributes('-fullscreen')
    root.attributes('-fullscreen', state)
    return "break"

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", toggle_fullscreen)
    App = Main(root, "Odtwarzacz wideo")
    root.mainloop()