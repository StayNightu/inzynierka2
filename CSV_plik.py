import csv
import tkinter as tk
from Video import VideoPlayer

class CSVDisplay:
    def __init__(self, root, csv_file_path="1.csv"):
        self.root = root
        self.root.title("Video Player with CSV Display")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.csv_file_path = csv_file_path

        self.canvas = tk.Canvas(root)
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.video_manager = VideoPlayer(root, self.canvas)

        self.csv_frame = tk.Frame(root)
        self.csv_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.csv_frame)
        self.listbox.pack(pady=15, padx=15, expand=True, fill=tk.BOTH)

        self.current_data = None
        self.keep_checking = True
        self.after_id = None

        self.load_csv()
        self.check_for_updates()

        # Bind window closing to stop checking and close
        root.protocol("WM_DELETE_WINDOW", self.stop_checking_and_close)

    def load_csv(self):
        data = []
        with open(self.csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(', '.join(row))

        if data != self.current_data:
            self.listbox.delete(0, tk.END)
            for line in data:
                self.listbox.insert(tk.END, line)
            self.current_data = data

    def check_for_updates(self):
        if self.keep_checking:
            self.load_csv()
            # Check for updates every 1000 ms (1 second)
            self.after_id = self.root.after(1000, self.check_for_updates)

    def stop_checking_and_close(self):
        self.keep_checking = False
        if self.after_id:
            self.root.after_cancel(self.after_id)  # Cancel the after function
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def toggle_fullscreen(self, event=None):
        state = not self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', state)
        return "break"