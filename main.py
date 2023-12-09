import tkinter as tk
from Sledzenie import Sledzenie
from BBoxoverlay import BBoxOverlay
from CSV_Edytor import CSVEditor
from dymki import Tooltip
import tkinter.simpledialog as sd
import tkinter.messagebox as messagebox
class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Edytor BBoxow")
        video_path = 'output.avi'
        csv_path = 'bbox_data.csv'
        self.BBox = BBoxOverlay(video_path, csv_path, self)
        self.sledzenie = Sledzenie()
        self.initialize_ui()
        self.csv_editor = None
        self.bind_all("<d>", self.on_delete_bbox_key)
        self.bind_all("<e>", self.on_manage_bbox_mode_key)
        self.bind_all("<w>", self.on_create_bbox_key)
        self.bbox_data_display.bind('<Double-1>', self.on_bbox_data_click)
        self.resizable(True, False)

    def initialize_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        left_button_frame = tk.Frame(self, height=720)
        left_button_frame.grid(row=0, column=2, sticky="ns")
        self.next_frame_button = tk.Button(left_button_frame, text="Następna klatka", command=self.on_next_frame)
        self.next_frame_button.pack(fill="both", expand=True)  

        self.canvas = tk.Canvas(self, width=1280, height=720)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        right_button_frame = tk.Frame(self, height=720)  
        right_button_frame.grid(row=0, column=0, sticky="ns")
        self.prev_frame_button = tk.Button(right_button_frame, text="Poprzednia klatka", command=self.on_prev_frame)
        self.prev_frame_button.pack(fill="both", expand=True)

        center_button_frame = tk.Frame(self)
        center_button_frame.grid(row=1, column=1, sticky="ew")

        left_spacer = tk.Frame(center_button_frame, width=50)
        left_spacer.pack(side=tk.LEFT, fill="x", expand=True)

        self.create_bbox_button = tk.Button(center_button_frame, text="Utwórz BBox", command=self.on_create_bbox)
        self.create_bbox_button.pack(side=tk.LEFT)
        Tooltip(self.create_bbox_button, "Skrót W.")

        self.manage_bbox_button = tk.Button(center_button_frame, text="Zarządzaj BBox",
                                            command=self.on_manage_bbox_mode)
        self.manage_bbox_button.pack(side=tk.LEFT)
        Tooltip(self.manage_bbox_button, "Skrót E.")

        self.delete_bbox_button = tk.Button(center_button_frame, text="Usuń BBox", command=self.on_delete_bbox)
        self.delete_bbox_button.pack(side=tk.LEFT)
        Tooltip(self.delete_bbox_button, "Skrót D.")

        right_spacer = tk.Frame(center_button_frame, width=50)
        right_spacer.pack(side=tk.LEFT, fill="x", expand=True)

        right_side_frame = tk.Frame(self)
        right_side_frame.grid(row=0, column=3, rowspan=2, sticky="ns")
        self.select_video_button = tk.Button(right_side_frame, text="Wybierz plik wideo", command=self.on_select_video)
        self.select_video_button.pack()
        self.bbox_video_button = tk.Button(right_side_frame, text="Wideo z BBoxami", command=self.on_bbox_video)
        self.bbox_video_button.pack()
        self.open_csv_editor_button = tk.Button(right_side_frame, text="Otwórz edytor CSV",
                                                command=self.open_csv_editor)
        self.open_csv_editor_button.pack()
        self.save_video_button = tk.Button(right_side_frame, text="Zapisz wideo z BBoxami", command=self.on_save_video)
        self.save_video_button.pack()

        listbox_frame = tk.Canvas(self)
        listbox_frame.grid(row=0, column=4, sticky="nsew")
        listbox_frame.grid_propagate(False)
        self.bbox_data_display = tk.Listbox(listbox_frame, width=30, height=40)
        self.bbox_data_display.grid(row=0, column=0, sticky="nsew")
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)

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
        self.update_bbox_data_display()

    def on_next_frame(self):
        print("Następna klatka - metoda wywołana")
        frame = self.BBox.next_frame()
        if frame is not None:
            self.update_canvas(frame)
        self.update_bbox_data_display()


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
        self.update_bbox_data_display()

    def update_bbox_data_display(self):
        self.bbox_data_display.delete(0, tk.END)
        current_bboxes = self.BBox.get_bbox_data_for_current_frame()
        for bbox in current_bboxes:
            display_text = f"ID: {bbox['id']}, Width: {bbox['width']}, Height: {bbox['height']}"
            self.bbox_data_display.insert(tk.END, display_text)

    def on_bbox_data_click(self, event):
        selected_index = self.bbox_data_display.curselection()
        if selected_index:
            selected_bbox = self.BBox.get_bbox_data_for_current_frame()[selected_index[0]]
            self.open_bbox_edit_window(selected_bbox)

    def open_bbox_edit_window(self, bbox):
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit BBox")
        tk.Label(edit_window, text="ID:").grid(row=0, column=0)
        id_entry = tk.Entry(edit_window)
        id_entry.grid(row=0, column=1)
        id_entry.insert(0, str(bbox['id']))
        tk.Label(edit_window, text="Szerokosc:").grid(row=1, column=0)
        width_entry = tk.Entry(edit_window)
        width_entry.grid(row=1, column=1)
        width_entry.insert(0, str(bbox['width']))
        tk.Label(edit_window, text="Wysokosc:").grid(row=2, column=0)
        height_entry = tk.Entry(edit_window)
        height_entry.grid(row=2, column=1)
        height_entry.insert(0, str(bbox['height']))
        tk.Button(edit_window, text="Zapisz",
                  command=lambda: self.update_bbox(bbox, id_entry.get(), width_entry.get(), height_entry.get())).grid(
            row=3, column=0, columnspan=2)

    def update_bbox(self, bbox, new_id, new_width, new_height):
        try:
            bbox['id'] = int(new_id)
            bbox['width'] = int(new_width)
            bbox['height'] = int(new_height)
            self.BBox.save_bbox_data()
            self.refresh_frame()
            self.update_bbox_data_display()
            if self.csv_editor is not None:
                self.csv_editor.refresh_data()
        except ValueError:
            messagebox.showerror("Blad", "Niewlasciwa wartosc.")


    def on_select_bbox_mode(self):
        self.is_selecting_bbox = True
        self.canvas.bind("<Button-1>", self.on_canvas_click_select_bbox)
    def on_create_bbox(self):
        self.canvas.config(cursor="plus")
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
        self.update_bbox_data_display()

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
        self.temp_bbox_coords = (self.start_x, self.start_y, end_x, end_y)
        self.canvas.config(cursor="")
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        bbox_id = sd.askstring("BBox ID", "Wprowadz BBox ID:")
        if bbox_id and bbox_id.isdigit():
            bbox_id = int(bbox_id)
            self.save_bbox_with_id(*self.temp_bbox_coords, bbox_id)
        else:
            messagebox.showwarning("Niewłasciwa nazwa", "BBox ID musi byc cyfra.")
            print("Niepoprawne dane.")
        self.update_bbox_data_display()

        if self.BBox:
            current_frame = self.BBox.get_frame()
            if current_frame is not None:
                self.update_canvas(current_frame)

    def save_bbox_with_id(self, x1, y1, x2, y2, bbox_id):
        bbox_width = abs(x2 - x1)
        bbox_height = abs(y2 - y1)
        new_bbox = {
            'detection_id': self.generate_new_detection_id(),
            'x1': min(x1, x2),
            'y1': min(y1, y2),
            'width': bbox_width,
            'height': bbox_height,
            'id': bbox_id,
        }
        self.BBox.save_new_bbox(new_bbox)
        self.refresh_frame()

    def on_manage_bbox_mode(self):
        self.is_managing_bbox = True
        self.canvas.bind("<ButtonPress-1>", self.on_bbox_manage_press)
        self.canvas.bind("<B1-Motion>", self.on_bbox_manage_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_bbox_manage_release)

    def on_bbox_manage_press(self, event):
        # Sprawdź, czy kliknięto na istniejący BBox
        if self.BBox.select_bbox(event.x, event.y):
            self.BBox.start_resizing_bbox(event.x, event.y)
            self.is_managing_bbox = True
        else:
            self.BBox.selected_bbox = None

    def on_bbox_manage_drag(self, event):
        if self.is_managing_bbox and self.BBox.selected_bbox:
            self.BBox.resize_bbox(event.x, event.y)
            self.update_canvas(self.BBox.get_frame())

    def on_bbox_manage_release(self, event):
        if self.is_managing_bbox and self.BBox.selected_bbox:
            self.BBox.finish_resizing_bbox()
            self.BBox.save_bbox_data()
            if self.csv_editor is not None:
                self.csv_editor.refresh_data()
            self.is_managing_bbox = False

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

    def on_delete_bbox_key(self, event):
        self.on_delete_bbox()

    def on_manage_bbox_mode_key(self, event):
        self.on_manage_bbox_mode()

    def on_create_bbox_key(self, event):
        self.on_create_bbox()

if __name__ == "__main__":
    app = Main()
    app.mainloop()