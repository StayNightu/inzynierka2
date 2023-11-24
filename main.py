import tkinter as tk
from Sledzenie import Sledzenie
from BBoxoverlay import BBoxOverlay
from CSV_Edytor import CSVEditor
class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Edytor BBoxow")
        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.pack(side=tk.TOP)
        video_path = 'output.avi'
        csv_path = 'bbox_data.csv'
        self.BBox = BBoxOverlay(video_path, csv_path, self)
        self.sledzenie = Sledzenie()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.initialize_ui()
        self.csv_editor = None

    def initialize_ui(self):
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.select_video_button = tk.Button(button_frame, text="Wybierz plik wideo", command=self.on_select_video)
        self.select_video_button.pack(side=tk.LEFT)

        self.bbox_video_button = tk.Button(button_frame, text="Wideo z BBoxami", command=self.on_bbox_video)
        self.bbox_video_button.pack(side=tk.LEFT)

        self.next_frame_button = tk.Button(button_frame, text="Następna klatka", command=self.on_next_frame)
        self.next_frame_button.pack(side=tk.LEFT)

        self.prev_frame_button = tk.Button(button_frame, text="Poprzednia klatka", command=self.on_prev_frame)
        self.prev_frame_button.pack(side=tk.LEFT)

        self.select_bbox_button = tk.Button(button_frame, text="Zaznacz BBox", command=self.on_select_bbox_mode)
        self.select_bbox_button.pack(side=tk.LEFT)

        self.create_bbox_button = tk.Button(button_frame, text="Utwórz BBox", command=self.on_create_bbox)
        self.create_bbox_button.pack(side=tk.LEFT)

        self.edit_bbox_size_button = tk.Button(button_frame, text="Edytuj rozmiar BBox",
                                               command=self.on_edit_bbox_size_mode)
        self.edit_bbox_size_button.pack(side=tk.LEFT)

        self.delete_bbox_button = tk.Button(button_frame, text="Usuń BBox", command=self.on_delete_bbox)
        self.delete_bbox_button.pack(side=tk.LEFT)

        self.open_csv_editor_button = tk.Button(button_frame, text="Otwórz edytor CSV", command=self.open_csv_editor)
        self.open_csv_editor_button.pack(side=tk.LEFT)


        self.save_video_button = tk.Button(button_frame, text="Zapisz wideo z BBoxami", command=self.on_save_video)
        self.save_video_button.pack(side=tk.LEFT)

    def generate_new_id(self):
        return max([bbox['id'] for bboxes in self.BBox.bbox_data.values() for bbox in bboxes], default=0) + 1

    def generate_new_detection_id(self):
        all_detection_ids = [bbox['detection_id'] for frame_bboxes in self.BBox.bbox_data.values() for bbox in frame_bboxes]
        return max(all_detection_ids, default=0) + 1

    def on_prev_frame(self):
        print("ebe")
        frame = self.BBox.prev_frame()
        if frame is not None:
            self.update_canvas(frame)

    def on_next_frame(self):
        print("Następna klatka - metoda wywołana")  # Dodaj taki wydruk
        frame = self.BBox.next_frame()
        if frame is not None:
            self.update_canvas(frame)

    def on_canvas_click(self, event):
        if self.BBox and self.BBox.select_bbox(event.x, event.y):
            self.update_canvas(self.BBox.get_frame())

    def update_canvas(self, frame):
        tk_frame = self.BBox.convert_frame_to_tkinter_format(frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_frame)
        self.canvas.image = tk_frame

    def open_csv_editor(self):
        csv_editor_window = tk.Toplevel(self)
        csv_editor_window.title("Edytor CSV")
        self.csv_editor = CSVEditor(csv_editor_window, './bbox_data.csv', self.refresh_frame)
        csv_editor_window.protocol("WM_DELETE_WINDOW", self.on_csv_editor_close)
    def on_select_video(self):
        try:
            selected_video_path = self.sledzenie.load_video()
            if selected_video_path:
                self.sledzenie.run()
        except ValueError as e:
            print(e)

    def on_bbox_video(self):
        video_path = './output.avi'
        csv_path = './bbox_data.csv'
        self.BBox = BBoxOverlay(video_path, csv_path, self)
        self.BBox.paused = True
        current_frame = self.BBox.get_frame()
        if current_frame is not None:
            self.update_canvas(current_frame)

    def on_select_bbox_mode(self):
        self.is_selecting_bbox = True
        self.canvas.bind("<Button-1>", self.on_canvas_click_select_bbox)
    def on_create_bbox(self):
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.start_x = None
        self.start_y = None
        self.rect = None

    def on_delete_bbox(self):
        if self.BBox and self.BBox.selected_bbox:
            self.BBox.delete_selected_bbox()
            self.refresh_frame()
            if self.csv_editor is not None:
                self.csv_editor.refresh_data()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red')

    def on_mouse_drag(self, event):
        curX, curY = (event.x, event.y)
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.save_bbox(self.start_x, self.start_y, end_x, end_y)
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        if self.BBox:
            current_frame = self.BBox.get_frame()
            if current_frame is not None:
                self.update_canvas(current_frame)

    def on_edit_bbox_size_mode(self):
        self.is_editing_bbox_size = True
        self.canvas.bind("<ButtonPress-1>", self.on_bbox_resize_press)
        self.canvas.bind("<B1-Motion>", self.on_bbox_resize_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_bbox_resize_release)

    def on_bbox_resize_press(self, event):
        if self.BBox and self.is_editing_bbox_size:
            self.BBox.start_resizing_bbox(event.x, event.y)

    def on_bbox_resize_drag(self, event):
        if self.BBox and self.is_editing_bbox_size:
            self.BBox.resize_bbox(event.x, event.y)
            self.update_canvas(self.BBox.get_frame())

    def on_bbox_resize_release(self, event):
        if self.BBox and self.is_editing_bbox_size:
            self.BBox.finish_resizing_bbox()
            self.BBox.save_bbox_data()
            if self.csv_editor is not None:
                self.csv_editor.refresh_data()
            self.update_canvas(self.BBox.get_frame())


    def save_bbox(self, x1, y1, x2, y2):
        bbox_width = abs(x2 - x1)
        bbox_height = abs(y2 - y1)
        new_bbox = {
            'detection_id': self.generate_new_detection_id(),
            'x1': min(x1, x2),
            'y1': min(y1, y2),
            'width': bbox_width,
            'height': bbox_height,
            'id': self.generate_new_id(),
        }
        self.BBox.save_new_bbox(new_bbox)
        self.refresh_frame()
        self.BBox.save_bbox_data()
        if self.csv_editor is not None:
            self.csv_editor.refresh_data()

    def refresh_frame(self):
        if self.BBox:
            self.BBox.update_bbox_data()
            current_frame = self.BBox.get_frame()
            if current_frame is not None:
                self.update_canvas(current_frame)

    def on_csv_editor_close(self):
        if self.csv_editor is not None:
            self.csv_editor.master.destroy()
            self.csv_editor = None

    def on_canvas_click_select_bbox(self, event):
        if self.is_selecting_bbox and self.BBox:
            if self.BBox.select_bbox(event.x, event.y):
                self.update_canvas(self.BBox.get_frame())
            else:
                self.BBox.selected_bbox = None
                self.update_canvas(self.BBox.get_frame())

    def on_save_video(self):
        output_path = 'output_z_bboxami.avi'
        self.BBox.save_video_with_bbox(output_path)

if __name__ == "__main__":
    app = Main()
    app.mainloop()