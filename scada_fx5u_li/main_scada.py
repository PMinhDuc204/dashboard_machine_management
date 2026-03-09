import tkinter as tk
import plc_comm
from header_ui import Header
from left_panel import LeftPanel
from center_video import CarouselPanel   # <-- SỬA Ở ĐÂY
from right_panel import RightPanel
from footer_log import Footer


class ScadaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCADA FX5U - DYNAMIC SCALING")
        self.state("zoomed")

        # ================= SCALE SETUP =================
        self.base_width = 1200
        self.scale_factor = 1.0

        # ================= GRID LAYOUT =================
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # ================= HEADER =================
        self.header = Header(self)
        self.header.grid(row=0, column=0, sticky="nsew")

        # ================= MAIN FRAME =================
        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=2)
        self.main_frame.columnconfigure(1, weight=4)
        self.main_frame.columnconfigure(2, weight=2)
        self.main_frame.rowconfigure(0, weight=1)

        # LEFT PANEL
        self.left = LeftPanel(self.main_frame)
        self.left.grid(row=0, column=0, sticky="nsew")

        # CENTER CAROUSEL (THAY VIDEO BẰNG BÀN XOAY)
        self.center = CarouselPanel(self.main_frame)   # <-- SỬA Ở ĐÂY
        self.center.grid(row=0, column=1, sticky="nsew")

        # RIGHT PANEL
        self.right = RightPanel(self.main_frame)
        self.right.grid(row=0, column=2, sticky="nsew")

        # ================= FOOTER =================
        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, sticky="nsew")

        # ================= RESIZE EVENT =================
        self.bind("<Configure>", self.on_resize)

        # ================= START UPDATE LOOP =================
        self.after(1000, self.update_loop)

    # ==========================================================
    # RESIZE HANDLER
    # ==========================================================
    def on_resize(self, event):
        new_width = self.winfo_width()
        if new_width > 100:
            self.scale_factor = new_width / self.base_width
            self.update_fonts()

    def update_fonts(self):
        self.header.scale_widgets(self.scale_factor)
        self.left.scale_widgets(self.scale_factor)
        self.right.scale_widgets(self.scale_factor)
        self.footer.scale_widgets(self.scale_factor)

    # ==========================================================
    # PLC UPDATE LOOP
    # ==========================================================
    def update_loop(self):
        data = plc_comm.read_words()

        if data:
            self.left.update_data(data)

        self.after(1000, self.update_loop)


# ==============================================================
# RUN APP
# ==============================================================
if __name__ == "__main__":
    app = ScadaApp()
    app.mainloop()