import tkinter as tk
import math


class CarouselPanel(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, bg="black", highlightthickness=0)

        self.rotation = 0

        self.sensors = [
            {"id": "10081", "label": "PROC_01"},
            {"id": "10083", "label": "FREQ_X"},
            {"id": "10085", "label": "VOLT_IN"},
            {"id": "10087", "label": "SEC_STAT"},
            {"id": "10089", "label": "MEM_POOL"},
            {"id": "10091", "label": "SIG_STR"},
        ]

        self.after(40, self.animate)

    # =========================
    # Animation Loop
    # =========================
    def animate(self):
        self.rotation += 2
        self.draw_carousel()
        self.after(40, self.animate)

    # =========================
    # Draw System
    # =========================
    def draw_carousel(self):
        self.delete("all")

        w = self.winfo_width()
        h = self.winfo_height()

        if w < 50 or h < 50:
            return

        center_x = w // 2
        center_y = h // 2

        radius = min(w, h) // 3

        # --- Orbit circle ---
        self.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline="#10b981",
            dash=(4, 4)
        )

        # --- CORE ---
        self.create_oval(
            center_x - 40,
            center_y - 40,
            center_x + 40,
            center_y + 40,
            outline="#10b981",
            fill="#062f2a"
        )

        self.create_text(
            center_x,
            center_y,
            text="CORE",
            fill="white",
            font=("Arial", 10, "bold")
        )

        # --- Sensor Nodes ---
        for i, sensor in enumerate(self.sensors):
            angle = (i * 360 / len(self.sensors)) + self.rotation
            rad = math.radians(angle)

            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)

            # Line to core
            self.create_line(center_x, center_y, x, y, fill="#333")

            node_w = 100
            node_h = 50

            x1 = x - node_w / 2
            y1 = y - node_h / 2
            x2 = x + node_w / 2
            y2 = y + node_h / 2

            # Node box
            self.create_rectangle(
                x1, y1, x2, y2,
                outline="#10b981",
                fill="#16181d",
                width=2
            )

            # Header
            self.create_rectangle(
                x1, y1,
                x2, y1 + 18,
                fill="#10b981",
                outline=""
            )

            self.create_text(
                (x1 + x2) / 2,
                y1 + 9,
                text=f"ID: {sensor['id']}",
                fill="black",
                font=("Arial", 7, "bold")
            )

            # Label
            self.create_text(
                (x1 + x2) / 2,
                y1 + 35,
                text=sensor["label"],
                fill="white",
                font=("Arial", 9)
            )