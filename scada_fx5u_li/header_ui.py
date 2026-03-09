import tkinter as tk
from PIL import Image, ImageTk

class Header(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#E6EEF7")
        
        # 1. Quản lý Logo
        self.logo_path = "assets/logo_truong.png"
        try:
            self.original_image = Image.open(self.logo_path)
        except:
            # Tạo ảnh trống nếu không tìm thấy file để tránh lỗi crash
            self.original_image = Image.new('RGB', (60, 60), color = '#E6EEF7')
            
        self.logo_tk = ImageTk.PhotoImage(self.original_image.resize((60, 60), Image.LANCZOS))
        
        self.lbl_logo = tk.Label(self, image=self.logo_tk, bg="#E6EEF7")
        self.lbl_logo.pack(side="left", padx=10)
        
        # 2. Quản lý Tiêu đề
        self.lbl_title = tk.Label(
            self,
            text="TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI",
            font=("Arial", 18, "bold"),
            bg="#E6EEF7"
        )
        self.lbl_title.pack(side="left")

    def scale_widgets(self, factor):
        # Resize Chữ tiêu đề
        new_font_size = max(int(18 * factor), 10)
        self.lbl_title.config(font=("Arial", new_font_size, "bold"))
        
        # Resize Ảnh Logo
        new_logo_size = max(int(60 * factor), 20)
        resized_img = self.original_image.resize((new_logo_size, new_logo_size), Image.LANCZOS)
        self.logo_tk = ImageTk.PhotoImage(resized_img)
        self.lbl_logo.config(image=self.logo_tk)