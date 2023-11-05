import tkinter as tk

#from BBox import BBox
from Video import VideoPlayer
from CSV_plik import CSVDisplay

class Main:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.btn_clicked = False
        self.bbox_drawer = None  # Dodane
        self.editing_mode = False  # Dodane

        self.canvas = tk.Canvas(window)
        self.canvas.pack(pady=20)

        self.video_manager = VideoPlayer(self.window, self.canvas, self.update_buttons_state)

        self.buttons_frame = tk.Frame(window)
        self.buttons_frame.pack(pady=20)

        self.btn_show_csv = tk.Button(self.buttons_frame, text="Pokaż wartości CSV", width=20, command=self.show_csv)
        self.btn_show_csv.grid(row=0, column=0, padx=5, pady=10)

        self.btn_select = tk.Button(self.buttons_frame, text="Wybierz wideo", width=15, command=self.video_manager.load_video)
        self.btn_select.grid(row=0, column=1, padx=5, pady=10)

        self.btn_play = tk.Button(self.buttons_frame, text="Odtwórz", width=10, command=self.video_manager.play_video, state=tk.DISABLED)
        self.btn_play.grid(row=0, column=2, padx=5, pady=10)

        self.btn_stop = tk.Button(self.buttons_frame, text="Zatrzymaj", width=10, command=self.video_manager.stop_video, state=tk.DISABLED)
        self.btn_stop.grid(row=0, column=3, padx=5, pady=10)

        self.btn_next_frame = tk.Button(self.buttons_frame, text="Następna klatka", width=15, command=self.video_manager.next_frame, state=tk.DISABLED)
        self.btn_next_frame.grid(row=0, column=4, padx=5, pady=10)

        self.btn_prev_frame = tk.Button(self.buttons_frame, text="Poprzednia klatka", width=17, command=self.video_manager.prev_frame, state=tk.DISABLED)
        self.btn_prev_frame.grid(row=0, column=5, padx=5, pady=10)

        self.btn_replay = tk.Button(self.buttons_frame, text="Odtwórz od nowa", width=15, command=self.video_manager.replay_video, state=tk.DISABLED)
        self.btn_replay.grid(row=0, column=6, padx=5, pady=10)

        self.btn_add_bbox = tk.Button(self.buttons_frame, text="Dodaj BBox", width=15, command=self.add_bbox,
                                      state=tk.DISABLED)
        self.btn_add_bbox.grid(row=1, column=0, padx=5, pady=10)

        self.btn_edit_bbox = tk.Button(self.buttons_frame, text="Edytuj BBox", width=15, command=self.edit_bbox,
                                       state=tk.DISABLED)
        self.btn_edit_bbox.grid(row=1, column=1, padx=5, pady=10)

        self.btn_delete_bbox = tk.Button(self.buttons_frame, text="Usuń BBox", width=15, command=self.delete_bbox,
                                         state=tk.DISABLED)
        self.btn_delete_bbox.grid(row=1, column=2, padx=5, pady=10)

    def on_select_video(self):
        if not self.btn_clicked:
            self.btn_clicked = True
            self.video_manager.load_video()
            self.window.after(1000, self.reset_btn_flag)  # Reset the flag after 1 second

    def reset_btn_flag(self):
        self.btn_clicked = False

    def show_csv(self):
        csv_display = CSVDisplay()
        csv_display.run()

    def add_bbox(self):
        if self.video_manager.is_video_opened():
            if self.bbox_drawer:
                self.bbox_drawer.clear()
                self.bbox_drawer.unbind()
            self.bbox_drawer = BBox(self.canvas)
            self.bbox_drawer.edit_mode = False

    def edit_bbox(self):
        if self.video_manager.is_video_opened():
            if self.bbox_drawer:
                self.bbox_drawer.edit_mode = True

    def delete_bbox(self):
        if self.video_manager.is_video_opened():
            # Usuń aktualnie narysowany bounding box
            if hasattr(self, 'bbox_drawer') and self.bbox_drawer:
                self.bbox_drawer.clear()
                self.bbox_drawer = None
                self.editing_mode = False

    def update_buttons_state(self):
        # Jeśli wideo jest załadowane
        if self.video_manager.is_video_opened():
            self.btn_play.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_replay.config(state=tk.NORMAL)

            # Enable next and previous frame buttons only when the video is not playing
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
        if self.video_manager.is_video_opened():
            self.btn_add_bbox.config(state=tk.NORMAL)
            self.btn_edit_bbox.config(
                state=tk.NORMAL)  # Możesz też ustawić to na DISABLED, jeśli nie chcesz na razie edytować bounding boxów
            self.btn_delete_bbox.config(state=tk.NORMAL)
        else:
            self.btn_add_bbox.config(state=tk.DISABLED)
            self.btn_edit_bbox.config(state=tk.DISABLED)
            self.btn_delete_bbox.config(state=tk.DISABLED)



def toggle_fullscreen(event = None):
    state = not root.attributes('-fullscreen')  # Pobieranie aktualnego stanu i zmiana go na przeciwny
    root.attributes('-fullscreen', state)
    return "break"

if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", toggle_fullscreen)  # Bindowanie klawisza Escape do funkcji toggle_fullscreen
    App = Main(root, "Odtwarzacz wideo")
    root.mainloop()