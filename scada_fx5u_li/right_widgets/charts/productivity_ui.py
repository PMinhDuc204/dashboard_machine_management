import tkinter as tk

class Productivity(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.label = tk.Label(self, font=("Arial", 14, "bold"))
        self.label.pack()

        self.history_label = tk.Label(self, font=("Arial", 11))
        self.history_label.pack()

    def update_data(self, total, history):

        self.label.config(
            text=f"Năng suất /1h: {total} sản phẩm"
        )
