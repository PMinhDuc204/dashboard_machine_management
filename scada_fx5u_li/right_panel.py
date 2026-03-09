import tkinter as tk
import plc_comm

class RightPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padx=10, pady=10)
        self.buttons = []

        # 1. NHÓM ĐIỀU KHIỂN CHẾ ĐỘ
        self.create_btn("AUTO MODE", "#94a3b8", plc_comm.set_auto, 10)
        self.create_btn("MANUAL MODE", "#e65100", plc_comm.set_manual, 10)
        self.create_btn("BÀN XOAY", "#2563eb", plc_comm.rotate_table, 10)
        
        # Đường kẻ phân cách
        self.sep = tk.Frame(self, height=2, bg="#cbd5e1")
        self.sep.pack(fill="x", pady=15)

        # 2. NHÓM CHỨC NĂNG PHỤ
        self.create_btn("LỖI SERVO", "#00897b", None, 9)
        self.create_btn("LỖI PLC", "#00897b", None, 9)
        self.create_btn("LỊCH SỬ", "#1e3a8a", None, 9)
        self.create_btn("SẢN PHẨM LỖI", "#d97706", None, 9)

    def create_btn(self, text, color, cmd, font_size):
        btn = tk.Button(self, text=text, bg=color, fg="white", 
                        font=("Arial", font_size, "bold"), command=cmd)
        btn.pack(fill="x", pady=4, ipady=8)
        # Lưu lại font gốc và padding gốc để scale
        btn.base_font_size = font_size
        self.buttons.append(btn)

    def scale_widgets(self, factor):
        padding = max(int(8 * factor), 2)
        spacing = max(int(4 * factor), 1)
        sep_spacing = max(int(15 * factor), 5)
        
        for btn in self.buttons:
            new_size = max(int(btn.base_font_size * factor), 7)
            btn.config(font=("Arial", new_size, "bold"))
            btn.pack_configure(pady=spacing, ipady=padding)
        
        self.sep.pack_configure(pady=sep_spacing)