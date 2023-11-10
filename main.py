import tkinter as tk
from Klatki import WyswietlanieKlatek
from BBox import BoundingBox
from Sledzenie import Sledzenie
from dzielenie import dzielenie
from TworzenieFilmu import Tworzenie
from Wyswietl import Wyswietl
class Main(tk.Tk):
    def __init__(self, BBox_instance=None, Tworzenie_instance=None, Klatki_instance=None ):
        super().__init__()
        self.title("Edytor BBoxow")
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack(side=tk.TOP)
        self.viewer = WyswietlanieKlatek(self.canvas)
        if BBox_instance is None:
            self.BBox = BoundingBox(main_instance=self, canvas=self.canvas)
        else:
            self.BBox = BBox_instance
        if Tworzenie_instance is None:
            self.TworzenieFilmu = Tworzenie()
        else:
            self.TworzenieFilmu = Tworzenie_instance
        if Klatki_instance is None:
            self.Klatki = WyswietlanieKlatek(self.canvas, self)
        else:
            self.Klatki = Klatki_instance
        self.viewer = self.Klatki
        self.sledzenie = Sledzenie()
        self.dzielenie = dzielenie(self)
        self.initialize_ui()

    def initialize_ui(self):
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.select_video_button = tk.Button(button_frame, text="Wybierz plik wideo", command=self.on_select_video)
        self.select_video_button.pack(side=tk.LEFT)

        divide_video_button = tk.Button(button_frame, text="Podziel wideo na klatki", command=self.dzielenie.divide_video_into_frames)
        divide_video_button.pack(side=tk.LEFT)


        display_button = tk.Button(button_frame, text="Wyświetl obraz", command=self.viewer.show_first_frame)
        display_button.pack(side=tk.LEFT)

        next_button = tk.Button(button_frame, text="Następna klatka", command=self.viewer.next_frame)
        next_button.pack(side=tk.LEFT)

        prev_button = tk.Button(button_frame, text="Poprzednia klatka", command=self.viewer.previous_frame)
        prev_button.pack(side=tk.LEFT)

        self.draw_button = tk.Button(button_frame, text="Rysuj Bounding Box", command=self.BBox.toggle_drawing_mode)
        self.draw_button.pack(side=tk.LEFT)

        del_button = tk.Button(button_frame, text="Usuń BBox", command=self.BBox.delete_selected_bbox)
        del_button.pack(side=tk.LEFT)

        save_button = tk.Button(button_frame, text="Zapisz Bounding Boxy", command=self.viewer.save_boxes)
        save_button.pack(side=tk.LEFT)

        create_video_button = tk.Button(button_frame, text="Stwórz wideo", command=self.TworzenieFilmu.create_video)
        create_video_button.pack(side=tk.LEFT)

        wyswietl_button = tk.Button(button_frame, text="Wyświetl wideo", command=self.wyswietl_wideo)
        wyswietl_button.pack(side=tk.LEFT)

    def on_select_video(self):
        try:
            selected_video_path = self.sledzenie.load_video()
            if selected_video_path:
                self.sledzenie.run()
        except ValueError as e:
            print(e)

    def wyswietl_wideo(self):
        video_path = 'output2.mp4'
        player = Wyswietl(self, video_path)
        player.play_video()

if __name__ == "__main__":
    app = Main()
    app.mainloop()