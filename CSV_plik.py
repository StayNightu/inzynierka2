import csv
import tkinter as tk

class CSVDisplay:
    def __init__(self, csv_file_path="1.csv"):
        self.window = tk.Tk()
        self.window.title("CSV Display")
        self.window.geometry("250x250")
        self.csv_file_path = csv_file_path

        self.listbox = tk.Listbox(self.window)
        self.listbox.pack(pady=15, padx=15, expand=True, fill=tk.BOTH)

        self.current_data = None
        self.keep_checking = True
        self.after_id = None

        self.load_csv()
        self.check_for_updates()

        # Bindujemy zamknięcie okna, żeby ustawić flagę keep_checking na False
        self.window.protocol("WM_DELETE_WINDOW", self.stop_checking_and_close)

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
            # Sprawdzanie aktualizacji co 1000 ms (co sekundę)
            self.after_id = self.window.after(1000, self.check_for_updates)

    def stop_checking_and_close(self):
        self.keep_checking = False
        if self.after_id:
            self.window.after_cancel(self.after_id)  # Anulowanie funkcji after
        self.window.destroy()

    def run(self):
        self.window.mainloop()