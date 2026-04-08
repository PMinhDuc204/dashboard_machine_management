import tkinter as tk
import threading
import time
import plc_comm
from plc_comm.writer import write_bit


class ModeButtons(tk.Frame):

    HOLD_TIME = 2  # dùng cho origin, auto, dummy

    def __init__(self, parent):
        super().__init__(parent)

        self.buttons = {}

        # ===== TẠO BUTTON =====
        self.create_button("POWER", "#2e7d32", self.power_toggle)
        self.create_button("ORIGIN", "#1565c0", self.origin)
        self.create_button("DUMMY", "#8e24aa", self.dummy_mode)
        self.create_button("EMPTY", "#6d4c41", self.empty_mode)
        self.create_button("AUTO", "#94a3b8", self.auto_mode)

        # 🔥 LOOP UPDATE
        self.after(300, self.update_ui)

    # ================= UI =================
    def create_button(self, text, color, command):

        btn = tk.Button(
            self,
            text=text,
            bg="#888888",
            fg="white",
            font=("Arial", 12, "bold"),
            command=command
        )
        btn.pack(side="left", expand=True, fill="x", padx=3)

        self.buttons[text] = btn

    # ================= READ BIT =================
    def get_bit(self, name):
        # 🔥 Dùng latest_m_modes cho M0, M303, M312, M315, M500
        modes = getattr(plc_comm, "latest_m_modes", {})
        if name in modes:
            return modes.get(name, 0)

        # Fallback: M900-M949 dùng latest_bits
        bits = getattr(plc_comm, "latest_bits", [])
        if not bits:
            return 0

        try:
            if name.startswith("M"):
                m = int(name[1:])
                offset = m - 900

                if 0 <= offset < len(bits):
                    return bits[offset]

        except Exception as e:
            print("GET BIT ERROR:", e)

        return 0

    # ================= UPDATE UI =================
    def update_ui(self):

        try:
            mapping = {
                "POWER": "M0",
                "ORIGIN": "M500",
                "DUMMY": "M312",
                "EMPTY": "M303",
                "AUTO": "M315"
            }

            for name, bit in mapping.items():

                state = self.get_bit(bit)

                if state:
                    self.buttons[name].config(bg="#22c55e")  # xanh
                else:
                    self.buttons[name].config(bg="#888888")  # xám

        except Exception as e:
            print("UI ERROR:", e)

        self.after(300, self.update_ui)

    # ================= LOGIC =================

    # 🔥 POWER → giữ ON/OFF
    def power_toggle(self):
        state = self.get_bit("M0")
        write_bit("M0", 0 if state else 1)

    # 🔥 ORIGIN (pulse 2s)
    def origin(self):
        threading.Thread(target=self._hold_pulse, args=("M500",), daemon=True).start()

    def dummy_mode(self):
        threading.Thread(target=self._hold_pulse, args=("M312",), daemon=True).start()

    def auto_mode(self):
        threading.Thread(target=self._hold_pulse, args=("M315",), daemon=True).start()

    # 🔥 EMPTY (toggle)
    def empty_mode(self):
        state = self.get_bit("M303")
        write_bit("M303", 0 if state else 1)

    # ================= HOLD 2s =================
    def _hold_pulse(self, device):
        try:
            write_bit(device, 1)
            time.sleep(self.HOLD_TIME)
            write_bit(device, 0)
        except Exception as e:
            print("PULSE ERROR:", e)