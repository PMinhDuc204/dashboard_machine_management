import tkinter as tk
import plc_comm.production as prod
class ProductionStats(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="white", padx=5, pady=3)

        font_label = ("Arial", 13, "bold")
        font_entry = ("Arial", 13, "bold")
        font_button = ("Arial", 13, "bold")

        # ===== PARAM =====
        self.entries = {}

        self.create_param("Current Position", "pos", 0, font_label, font_entry)
        self.create_param("Manual Speed(deg/s)", "manual_speed", 1, font_label, font_entry)
        self.create_param("Auto Speed(deg/s)", "auto_speed", 2, font_label, font_entry)
        self.create_param("ORG Compensation(deg)", "org", 3, font_label, font_entry)
        self.create_param("Length Step(deg)", "step", 4, font_label, font_entry)

        # ===== STATUS =====
        tk.Label(self, text="Status", bg="white", font=font_label)\
            .grid(row=0, column=2, padx=8)

        self.status = tk.Entry(self, width=6, font=font_entry, justify="center")
        self.status.grid(row=0, column=3)

        # ===== SEPARATOR =====
        tk.Frame(self, width=3, bg="black")\
            .grid(row=0, column=4, rowspan=6, sticky="ns", padx=15)

        tk.Frame(self, width=2, bg="gray")\
            .grid(row=0, column=5, rowspan=6, sticky="ns")

        # ===== BUTTON =====
        self.create_button("JOG -", 0, 8, font_button, prod.jog_minus)
        self.create_button("JOG +", 0, 9, font_button, prod.jog_plus)

        self.create_button("Servo ON", 1, 8, font_button, prod.servo_on)
        self.create_button("Servo OFF", 1, 9, font_button, prod.servo_off)

        self.create_button("Origin", 2, 8, font_button, prod.origin)
        self.create_button("Run 1 Step", 2, 9, font_button, prod.run_1_step)

        self.create_button("Turn on light", 3, 8, font_button, prod.onlight)
        self.create_button("Turn off light", 3, 9, font_button, prod.offlight)

        # ===== LOOP =====
        self.after(300, self.update_data)

    # ================= PARAM =================
    def create_param(self, text, key, row, font_label, font_entry):

        tk.Label(self, text=text, bg="white", font=font_label)\
            .grid(row=row, column=0, sticky="w", pady=2)

        entry = tk.Entry(self, width=10, font=font_entry, justify="center")
        entry.grid(row=row, column=1, padx=8)

        self.entries[key] = entry

    # ================= BUTTON =================
    def create_button(self, text, r, c, font_button, cmd):

        btn = tk.Button(
            self,
            text=text,
            bg="#3b6fd8",
            fg="white",
            width=14,
            font=font_button,
            command=cmd
        )

        btn.grid(row=r, column=c, padx=10, pady=4)

    # ================= UPDATE =================
    def update_data(self):

        try:
            data = prod.read_production_data()
            status = prod.read_status()

            if data:
                for key in self.entries:
                    val = data.get(key, "")
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, str(val))

            # status
            if status == 1:
                self.status.delete(0, tk.END)
                self.status.insert(0, "OK")
            else:
                self.status.delete(0, tk.END)
                self.status.insert(0, "ER")

        except Exception as e:
            print("UI ERROR:", e)

        self.after(300, self.update_data)