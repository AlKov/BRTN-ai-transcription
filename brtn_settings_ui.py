import tkinter as tk
from tkinter import ttk
import json
import os
import sys
import subprocess

# Colors
COLOR_BG_MID = "#FFEDEB"
COLOR_PRIMARY = "#EA6363"
COLOR_TEXT = "#565656"
COLOR_ACCENT = "#212121"
COLOR_BORDER = "#F2C4C4"

CONFIG_PATH = os.path.expanduser("~/.brtn_config.json")
# Updated Logo Path from user upload (second image)
LOGO_PATH = "/Users/oleksandrkovalenko/.gemini/antigravity/brain/88b2283a-3684-4210-bee6-94ad96302463/uploaded_image_1768138478257.png"

def load_config():
    defaults = {
        "start_trigger": "hold", "end_trigger": "release",
        "start_key_code": 63, "start_key_name": "Fn",
        "end_key_code": 63, "end_key_name": "Fn",
        "show_icon": True
    }
    if not os.path.exists(CONFIG_PATH): return defaults
    try:
        with open(CONFIG_PATH, 'r') as f:
            return {**defaults, **json.load(f)}
    except: return defaults

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    except: pass

def draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        try: tw.attributes("-topmost", True)
        except: pass
        
        tw.config(bg="white")
        # Tooltip styling: 14px, no border, 0.5em padding (approx 8px)
        tx = self.widget.winfo_rootx() + 25
        ty = self.widget.winfo_rooty() + 25
        tw.wm_geometry(f"+{tx}+{ty}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffff", borderwidth=0,
                         foreground=COLOR_TEXT, font=("Montserrat Medium", 14),
                         padx=8, pady=8)
        label.pack()

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()

class CustomDropdown(tk.Frame):
    def __init__(self, parent, options, var, command=None):
        super().__init__(parent, bg=COLOR_BG_MID, highlightthickness=0)
        self.options = options
        self.var = var
        self.command = command
        self.enabled = True
        
        self.label = tk.Label(self, textvariable=self.var, font=("Montserrat Medium", 16), 
                               fg=COLOR_ACCENT, bg=COLOR_BG_MID, cursor="pointinghand")
        self.label.pack(side="left", padx=(0, 5))
        
        self.arrow = tk.Label(self, text="⌵", font=("Montserrat Medium", 14), 
                               fg=COLOR_ACCENT, bg=COLOR_BG_MID, cursor="pointinghand")
        self.arrow.pack(side="right")
        
        self.line = tk.Frame(self, height=2, bg=COLOR_ACCENT)
        self.line.place(relx=0, rely=1, relwidth=1, anchor="sw")
        
        for w in (self.label, self.arrow, self):
            w.bind("<Button-1>", self.show_menu)
            
        self.menu = None

    def show_menu(self, event=None):
        if not self.enabled: return
        if self.menu:
            self.menu.destroy()
            self.menu = None
            return
            
        self.menu = tk.Toplevel(self)
        self.menu.overrideredirect(True)
        self.menu.configure(bg="white", highlightthickness=1, highlightbackground=COLOR_BORDER)
        
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.menu.geometry(f"+{x}+{y}")
        
        for opt in self.options:
            # Filter options based on external logic if needed
            l = tk.Label(self.menu, text=opt, font=("Montserrat Medium", 14), bg="white", 
                         fg=COLOR_TEXT, padx=15, pady=8, anchor="w", cursor="pointinghand")
            l.pack(fill="x")
            l.bind("<Enter>", lambda e, item=l: item.config(bg="#FFF0EF"))
            l.bind("<Leave>", lambda e, item=l: item.config(bg="white"))
            l.bind("<Button-1>", lambda e, val=opt: self.select(val))

    def select(self, val):
        self.var.set(val)
        if self.command: self.command(val)
        self.menu.destroy()
        self.menu = None

class CustomKeyInput(tk.Frame):
    def __init__(self, parent, name_var, code_var, enabled=True):
        super().__init__(parent, bg=COLOR_BG_MID, highlightthickness=0)
        self.name_var = name_var
        self.code_var = code_var
        self.enabled = enabled
        
        self.canvas = tk.Canvas(self, width=100, height=40, bg=COLOR_BG_MID, highlightthickness=0)
        self.canvas.pack()
        
        self.draw_box()
        
        if enabled:
            self.canvas.bind("<Button-1>", self.start_capture)
            self.canvas.config(cursor="pointinghand")

    def draw_box(self, active=False):
        self.canvas.delete("all")
        color = COLOR_PRIMARY if active else COLOR_BORDER
        fill = "white" if not active else "#FFF0EF"
        draw_rounded_rect(self.canvas, 2, 2, 98, 38, 10, fill=fill, outline=color, width=2)
        text = self.name_var.get()
        self.canvas.create_text(50, 20, text=text, font=("Montserrat Medium", 14), fill=COLOR_TEXT)

    def start_capture(self, event=None):
        if not self.enabled: return
        self.name_var.set("...")
        self.draw_box(active=True)
        self.canvas.focus_set()
        self.canvas.bind("<Key>", self.on_key)

    def on_key(self, event):
        raw = event.keycode
        code = (raw >> 24) & 0xFF if raw > 65535 else raw & 0xFF
        sym = event.keysym
        mapping = {63: "Fn", 179: "Fn", "Super_L": "Fn", 131: "Cmd", 135: "Cmd"}
        name = mapping.get(code, mapping.get(sym, sym))
        
        if name == "Shift_L": name = "Shift"
        elif name == "Control_L": name = "Ctrl"
        elif name == "Alt_L": name = "Opt"
        
        self.name_var.set(name)
        self.code_var.set(code)
        self.draw_box()
        self.canvas.unbind("<Key>")

class BRTNSettingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BRTN Settings")
        self.root.overrideredirect(True)
        self.w, self.h = 750, 600
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        self.root.geometry(f"{self.w}x{self.h}+{sw//2 - self.w//2}+{sh//2 - self.h//2}")
        self.root.configure(bg=COLOR_BG_MID)
        
        self.config = load_config()
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg=COLOR_BG_MID, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.setup_ui()
        
    def safe_exit(self, event=None):
        try:
            self.root.quit()
            self.root.destroy()
        except: pass
        os._exit(0)

    def draw_background(self):
        mid_r, mid_g, mid_b = 255, 237, 235
        for x in range(self.w):
            rel = x / self.w
            if rel <= 0.05 or rel >= 0.95:
                color = "#FFFFFF"
            elif rel < 0.5:
                f = (rel - 0.05) / 0.45
                g = int(255 + (mid_g - 255) * f)
                b = int(255 + (mid_b - 255) * f)
                color = f"#ff{g:02x}{b:02x}"
            else:
                f = (rel - 0.5) / 0.45
                g = int(mid_g + (255 - mid_g) * f)
                b = int(mid_b + (255 - mid_b) * f)
                color = f"#ff{g:02x}{b:02x}"
            self.canvas.create_line(x, 0, x, self.h, fill=color)

    def setup_ui(self):
        self.draw_background()
        
        # Logo Integration (Prominent Bottom Right)
        try:
            self.logo_img = tk.PhotoImage(file=LOGO_PATH)
            # Doubled size: subsample 2 instead of 4
            self.logo_small = self.logo_img.subsample(2, 2) 
            # Position: Right 5% (0.95), Bottom 10% (0.90)
            self.canvas.create_image(self.w * 0.95, self.h * 0.90, image=self.logo_small, anchor="se")
        except: pass

        self.canvas.create_text(self.w/2, 80, text="BRTN loves btns. Set yours:", 
                                font=("Chonburi", 28, "bold"), fill=COLOR_PRIMARY)
        
        self.close_btn = self.canvas.create_text(self.w-40, 40, text="✕", font=("Montserrat Medium", 24), fill=COLOR_TEXT)
        self.canvas.tag_bind(self.close_btn, "<Button-1>", self.safe_exit)
        self.canvas.tag_bind(self.close_btn, "<Enter>", lambda e: self.canvas.itemconfig(self.close_btn, fill=COLOR_PRIMARY))
        self.canvas.tag_bind(self.close_btn, "<Leave>", lambda e: self.canvas.itemconfig(self.close_btn, fill=COLOR_TEXT))

        start_y = 200
        finish_y = 290
        left_label_x = 120
        text_i_will_x = 285
        dropdown_x = 420
        input_x = 580
        hint_x = 85 
        
        # Section Start
        # Hint Start: Clear border, absolute position
        self.hint_s = tk.Canvas(self.root, width=24, height=24, bg="white", highlightthickness=0, borderwidth=0)
        self.hint_s.create_oval(1, 1, 23, 23, outline=COLOR_BORDER, width=1, fill="white")
        self.hint_s.create_text(12, 12, text="?", font=("Arial", 12, "bold"), fill=COLOR_BORDER)
        self.canvas.create_window(hint_x, start_y, window=self.hint_s)
        ToolTip(self.hint_s, "On start: set a trigger for recording")

        self.canvas.create_text(left_label_x, start_y, text="To Start:", font=("Chonburi", 22, "bold"), fill=COLOR_PRIMARY, anchor="w")
        self.canvas.create_text(text_i_will_x, start_y, text="I will", font=("Montserrat Medium", 18), fill=COLOR_TEXT, anchor="w")
        
        self.st_var = tk.StringVar(value=self.config.get("start_trigger", "hold"))
        self.st_dd = CustomDropdown(self.root, ["hold", "tap", "double tap"], self.st_var, self.on_trigger_change)
        self.canvas.create_window(dropdown_x, start_y, window=self.st_dd)
        
        self.sk_name = tk.StringVar(value=self.config.get("start_key_name", "Fn"))
        self.sk_code = tk.IntVar(value=self.config.get("start_key_code", 63))
        self.sk_inp = CustomKeyInput(self.root, self.sk_name, self.sk_code)
        self.canvas.create_window(input_x, start_y, window=self.sk_inp)
        
        # Section Finish
        # Hint Finish: Clear border
        self.hint_f = tk.Canvas(self.root, width=24, height=24, bg="white", highlightthickness=0, borderwidth=0)
        self.hint_f.create_oval(1, 1, 23, 23, outline=COLOR_BORDER, width=1, fill="white")
        self.hint_f.create_text(12, 12, text="?", font=("Arial", 12, "bold"), fill=COLOR_BORDER)
        self.canvas.create_window(hint_x, finish_y, window=self.hint_f)
        ToolTip(self.hint_f, "Finish ends recording and starts transcription")

        self.canvas.create_text(left_label_x, finish_y, text="To Finish:", font=("Chonburi", 22, "bold"), fill=COLOR_PRIMARY, anchor="w")
        self.canvas.create_text(text_i_will_x, finish_y, text="I will", font=("Montserrat Medium", 18), fill=COLOR_TEXT, anchor="w")
        
        self.et_var = tk.StringVar(value=self.config.get("end_trigger", "release"))
        self.et_dd = CustomDropdown(self.root, ["release", "tap", "double tap"], self.et_var)
        self.canvas.create_window(dropdown_x, finish_y, window=self.et_dd)
        
        self.ek_name = tk.StringVar(value=self.config.get("end_key_name", "Fn"))
        self.ek_code = tk.IntVar(value=self.config.get("end_key_code", 63))
        self.ek_inp = CustomKeyInput(self.root, self.ek_name, self.ek_code)
        self.canvas.create_window(input_x, finish_y, window=self.ek_inp)
        
        consent_x = left_label_x
        consent_y = 385
        self.show_icon_var = tk.BooleanVar(value=self.config.get("show_icon", True))
        self.cb_canvas = tk.Canvas(self.root, width=32, height=32, bg=COLOR_BG_MID, highlightthickness=0)
        self.draw_checkbox()
        self.canvas.create_window(consent_x + 16, consent_y, window=self.cb_canvas)
        cb_label = self.canvas.create_text(consent_x + 45, consent_y, text="Display recording icon while active", 
                                          font=("Montserrat Medium", 17), fill=COLOR_TEXT, anchor="w")
        self.cb_canvas.bind("<Button-1>", self.toggle_icon_consent)
        self.canvas.tag_bind(cb_label, "<Button-1>", self.toggle_icon_consent)
        self.cb_canvas.config(cursor="pointinghand")
        
        self.draw_save_btn()
        self.on_trigger_change()

    def draw_checkbox(self):
        self.cb_canvas.delete("all")
        v = self.show_icon_var.get()
        outline = COLOR_ACCENT if v else COLOR_BORDER
        self.cb_canvas.create_rectangle(2, 2, 30, 30, outline=outline, width=2, fill="white")
        if v:
            self.cb_canvas.create_line(8, 16, 14, 22, fill=COLOR_PRIMARY, width=3)
            self.cb_canvas.create_line(14, 22, 24, 10, fill=COLOR_PRIMARY, width=3)

    def toggle_icon_consent(self, event=None):
        self.show_icon_var.set(not self.show_icon_var.get())
        self.draw_checkbox()

    def draw_save_btn(self):
        bx, by = self.w/2, 500
        bw, bh = 240, 70
        r = 35 
        
        # Improved rounded border - solid 2px
        self.save_rect = draw_rounded_rect(self.canvas, bx-bw/2, by-bh/2, bx+bw/2, by+bh/2, r,
                                          fill="", outline=COLOR_ACCENT, width=2, tags="save_btn")
        
        self.save_text = self.canvas.create_text(bx, by, text="save", font=("Chonburi", 22, "bold"), fill=COLOR_ACCENT, tags="save_btn")
        
        def on_hover_save(h):
            color = COLOR_PRIMARY if h else COLOR_ACCENT
            self.canvas.itemconfig(self.save_rect, outline=color)
            self.canvas.itemconfig(self.save_text, fill=color)
            self.canvas.config(cursor="pointinghand" if h else "")
        self.canvas.tag_bind("save_btn", "<Enter>", lambda e: on_hover_save(True))
        self.canvas.tag_bind("save_btn", "<Leave>", lambda e: on_hover_save(False))
        self.canvas.tag_bind("save_btn", "<Button-1>", lambda e: self.save())

    def on_trigger_change(self, val=None):
        st = self.st_var.get()
        if st == "hold":
            self.et_var.set("release")
            self.et_dd.label.config(fg="#cccccc")
            self.et_dd.enabled = False
            self.ek_inp.enabled = False
            self.ek_inp.draw_box()
        else:
            # If Tap/Double Tap enabled for start, Release finish is logically impossible/disabled
            if self.et_var.get() == "release":
                self.et_var.set("tap")
            self.et_dd.label.config(fg=COLOR_ACCENT)
            self.et_dd.enabled = True
            self.ek_inp.enabled = True
            self.ek_inp.draw_box()

    def save(self):
        conf = {
            "start_trigger": self.st_var.get(), "end_trigger": self.et_var.get(),
            "start_key_code": int(self.sk_code.get()) & 0xFF,
            "start_key_name": self.sk_name.get(),
            "end_key_code": int(self.ek_code.get()) & 0xFF,
            "end_key_name": self.ek_name.get(),
            "show_icon": self.show_icon_var.get()
        }
        save_config(conf)
        try: os.system("pkill -f brtn_transcriber.py")
        except: pass
        subprocess.Popen([sys.executable, "brtn_transcriber.py"], start_new_session=True)
        self.safe_exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = BRTNSettingsApp(root)
    root.mainloop()
