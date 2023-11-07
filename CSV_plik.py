import csv
import tkinter as tk
from tkinter import Toplevel

class CSVDisplay:
    def __init__(self, main_instance, csv_file_path="1.csv"):
        self.main_instance = main_instance
        self.csv_file_path = csv_file_path
        self.current_data = None  # Inicjalizuj current_data, jeśli tego jeszcze nie zrobiłeś

        self.canvas = tk.Canvas(main_instance.root)  # Użyj głównego okna aplikacji
        self.canvas.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.csv_frame = tk.Frame(main_instance.root)  # Użyj głównego okna aplikacji
        self.csv_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.csv_frame)
        self.listbox.pack(pady=15, padx=15, expand=True, fill=tk.BOTH)

        self.load_csv()
        self.keep_checking = True
        self.check_interval = 1000
        self.load_csv()
        self.start_checking_for_updates()

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

    def start_checking_for_updates(self):
        if self.keep_checking:
            self.check_for_updates()
            self.main_instance.root.after(self.check_interval, self.start_checking_for_updates)

    def check_for_updates(self):
        if self.keep_checking:
            self.load_csv()
            self.after_id = self.main_instance.root.after(1000, self.check_for_updates)

    def stop_checking_and_close(self):
        self.keep_checking = False
        if self.after_id:
            self.main_instance.after_cancel(self.after_id)
        self.main_instance.root.destroy()

    def run(self):
        self.main_instance()