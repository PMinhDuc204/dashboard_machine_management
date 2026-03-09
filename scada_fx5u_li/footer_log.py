import tkinter as tk
from tkinter import messagebox, simpledialog
import plc_comm

class Footer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bd=1, relief="sunken")
        self.PASSWORD = "028968"
        
        # --- PHẦN 1: KẾT NỐI PLC (Bên trái) ---
        self.frame_left = tk.Frame(self)
        self.frame_left.pack(side="left", padx=5, pady=5)

        self.lbl = tk.Label(self.frame_left, text="● Chưa kết nối PLC", 
                           fg="red", font=("Arial", 10, "bold"))
        self.lbl.pack(side="left", padx=10)
        
        self.btn_connect = tk.Button(
            self.frame_left, text="KẾT NỐI PLC", 
            command=self.handle_connect, bg="#f0f0f0"
        )
        self.btn_connect.pack(side="left", padx=5)

        # --- PHẦN 2: GHI CHÚ (Bên phải) ---
        self.frame_right = tk.Frame(self, bg="#f8f9fa")
        self.frame_right.pack(side="right", fill="x", expand=True, padx=(20, 10))
        
        self.lbl_note_tag = tk.Label(self.frame_right, text="Ghi chú:", 
                                     font=("Arial", 9, "bold"), bg="#f8f9fa")
        self.lbl_note_tag.pack(side="left", padx=5)
        
        self.ent_note = tk.Entry(self.frame_right, font=("Arial", 9), bd=0, bg="#f8f9fa")
        self.ent_note.pack(side="left", fill="x", expand=True, padx=5)
        self.ent_note.insert(0, "Hệ thống đang chờ lệnh...")

        self.btn_save = tk.Button(self.frame_right, text="Lưu", 
                                 command=self.handle_save, font=("Arial", 8))
        self.btn_save.pack(side="left", padx=2)
        
        self.btn_edit = tk.Button(self.frame_right, text="Thay đổi", 
                                 command=self.handle_change, font=("Arial", 8))
        self.btn_edit.pack(side="left", padx=2)

    def check_password(self):
        pwd = simpledialog.askstring("Xác thực", "Vui lòng nhập mật khẩu:", show='*')
        if pwd == self.PASSWORD:
            return True
        else:
            messagebox.showerror("Lỗi", "Mật khẩu không chính xác!")
            return False

    def handle_save(self):
        if self.check_password():
            messagebox.showinfo("Thành công", "Đã lưu ghi chú hệ thống.")

    def handle_change(self):
        if self.check_password():
            messagebox.showinfo("Thành công", "Đã cập nhật cấu hình ghi chú.")

    def handle_connect(self):
        self.lbl.config(text="● Đang kết nối...", fg="blue")
        self.update()
        if plc_comm.connect_plc():
            self.lbl.config(text="● Đã kết nối thành công!", fg="green")
        else:
            self.lbl.config(text="● Lỗi kết nối PLC", fg="red")

    def set_status(self, ok):
        if ok:
            self.lbl.config(text="● Đã kết nối với PLC", fg="green")
        else:
            self.lbl.config(text="● Lỗi PLC / Mất kết nối", fg="red")

    def scale_widgets(self, factor):
        # Scale Font cho toàn bộ Footer
        f_size_main = max(int(10 * factor), 8)
        f_size_note = max(int(9 * factor), 7)
        f_size_btn = max(int(8 * factor), 6)
        
        self.lbl.config(font=("Arial", f_size_main, "bold"))
        self.btn_connect.config(font=("Arial", f_size_main))
        self.lbl_note_tag.config(font=("Arial", f_size_note, "bold"))
        self.ent_note.config(font=("Arial", f_size_note))
        self.btn_save.config(font=("Arial", f_size_btn))
        self.btn_edit.config(font=("Arial", f_size_btn))