import tkinter as tk
import csv
from tkinter import messagebox

class CSVEditor:
    def __init__(self, master, csv_path, on_save_callback=None):
        self.master = master
        self.csv_path = csv_path
        self.on_save_callback = on_save_callback
        self.data = self.load_csv_data()
        self.create_ui()

    def load_csv_data(self):
        data = []
        with open(self.csv_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                data.append(row)
        return data

    def save_csv_data(self):
        try:
            with open(self.csv_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                for row in self.data:
                    writer.writerow(row)
            messagebox.showinfo("Sukces", "Dane zostały zapisane.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {e}")

    def create_ui(self):
        self.table = tk.Text(self.master, wrap='none')
        self.table.pack(fill=tk.BOTH, expand=True)

        for row in self.data:
            row_data = '    '.join(row) + '\n'
            self.table.insert(tk.END, row_data)

        save_button = tk.Button(self.master, text="Zapisz zmiany", command=self.on_save)
        save_button.pack()

    def on_save(self):
        updated_data = self.table.get("1.0", tk.END).strip().split('\n')
        self.data = [row.split('   ') for row in updated_data]
        self.save_csv_data()
        if self.on_save_callback:
            self.on_save_callback()

    def refresh_data(self):
        self.data = self.load_csv_data()
        self.update_table_ui()

    def update_table_ui(self):
        self.table.delete("1.0", tk.END)
        for row in self.data:
            row_data = '    '.join(row) + '\n'
            self.table.insert(tk.END, row_data)