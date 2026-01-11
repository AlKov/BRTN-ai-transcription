import os
import sys
import json
import time
import wave
import threading
import queue
import math
import tempfile
import numpy as np
import pyaudio
import pyperclip
from pynput.keyboard import Controller, Key
import tkinter as tk
from faster_whisper import WhisperModel
import Quartz

# LOGGING
def log(msg):
    with open("transcriber_debug.txt", "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")

# Check macOS Accessibility
def check_accessibility():
    try:
        if not Quartz.AXIsProcessTrusted():
            log("WARNING: Accessibility not enabled.")
            return False
        return True
    except: return False

log("=== BRTN START - ZERO FOCUS MODE ===")

# Key Capture
def is_key_pressed(code):
    v = (code >> 24) & 0xFF if code > 65535 else code & 0xFF
    return Quartz.CGEventSourceKeyState(Quartz.kCGEventSourceStateCombinedSessionState, min(255, max(0, v)))

CONFIG_PATH = os.path.expanduser("~/.brtn_config.json")
def load_config():
    defaults = {"start_trigger": "hold", "start_key_code": 63, "show_icon": True}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f: return {**defaults, **json.load(f)}
        except: pass
    return defaults

class TranscriberUI:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.waves = []
        self.queue = queue.Queue()
        self.animating = False
        self.step = 0
        self.vol = 0

    def create(self):
        self.root = tk.Tk()
        # CRITICAL: LSUIElement and overrrideredirect(True) for focus passivity
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # This style prevents the window from ever being focused or appearing in Cmd+Tab
        try:
            self.root.tk.call('tk', 'unsupported', 'MacWindowStyle', 'style', self.root, 'help', 'none')
            self.root.config(bg='systemTransparent')
            self.root.attributes("-transparent", True)
            self.root.attributes("-hasShadow", False)
        except: 
            self.root.config(bg="white")
            
        self.root.attributes("-alpha", 0.0) # Start invisible
        
        size = 110
        x = 30
        y = self.root.winfo_screenheight() - size - 80
        self.root.geometry(f"{size}x{size}+{x}+{y}")
        
        self.canvas = tk.Canvas(self.root, width=size, height=size, bg='systemTransparent', highlightthickness=0, borderwidth=0)
        self.canvas.pack()
        self.canvas.create_oval(5, 5, 105, 105, fill="white", outline="", width=0)
        
        for i in range(5):
            w = self.canvas.create_line(39+i*8, 55, 39+i*8, 55, fill="#EA6363", width=4, capstyle="round")
            self.waves.append(w)
            
        # MAP ONCE and never withdraw/deiconify again (prevents focus shuffling)
        self.root.deiconify()
        self.root.update()
        log("UI: Ghost Badge Ready.")

    def update(self):
        if not self.root: return
        try:
            while True:
                cmd, val = self.queue.get_nowait()
                if cmd == "show":
                    self.root.attributes("-alpha", 1.0)
                    if not self.animating:
                        self.animating = True
                        self.animate()
                elif cmd == "hide":
                    self.root.attributes("-alpha", 0.0)
                    self.animating = False
                elif cmd == "color":
                    for w in self.waves: self.canvas.itemconfig(w, fill=val)
        except queue.Empty: pass
        self.root.update()

    def animate(self):
        if not self.animating: return
        self.step += 1
        for i, w in enumerate(self.waves):
            h = 4 + self.vol * 40 * (0.6 + 0.4 * abs(math.sin(self.step * 0.2 + i)))
            self.canvas.coords(w, 39+i*8, 55-h, 39+i*8, 55+h)
        self.root.after(20, self.animate)

class Engine:
    def __init__(self, ui):
        self.ui = ui
        self.pa = pyaudio.PyAudio()
        self.keyboard = Controller()
        self.model = None
        self.rec = False
        self.frames = []
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=4)
        log("ENGINE: Model Loaded.")

    def start(self):
        if self.rec: return
        self.rec = True
        self.frames = []
        self.ui.queue.put(("show", None))
        self.ui.queue.put(("color", "#EA6363"))
        threading.Thread(target=self._run_rec, daemon=True).start()

    def stop(self):
        if not self.rec: return
        self.rec = False
        self.ui.queue.put(("color", "#1DB954")) # Green

    def _run_rec(self):
        try:
            stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            while self.rec:
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
                v = np.frombuffer(data, dtype=np.int16)
                self.ui.vol = min(1.0, np.abs(v).mean() / 1500) if v.size > 0 else 0
            stream.stop_stream(); stream.close()
            self.process()
        except: pass

    def process(self):
        log("TRANS: Start")
        # 1. HIDE IMMEDIATELY to return focus
        self.ui.queue.put(("hide", None))
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                wf = wave.open(tf.name, 'wb')
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000)
                wf.writeframes(b''.join(self.frames)); wf.close()
                
                while not self.model: time.sleep(0.1)
                segments, info = self.model.transcribe(tf.name, beam_size=1, vad_filter=True, language="en")
                text = " ".join([s.text for s in segments]).strip()
                
                log(f"TRANS: Result: '{text}'")
                
                if text and len(text) > 1:
                    # 2. Use Clipboard - much more reliable than direct typing for large bursts
                    pyperclip.copy(text)
                    log(f"CLIPBOARD: Verified '{pyperclip.paste()[:20]}...'")
                    
                    time.sleep(0.4) # Focus settle
                    
                    # 3. MODIFIER FLUSH (Ensure Fn-key/Cmd aren't "hanging")
                    for k in [Key.cmd, Key.shift, Key.alt, Key.ctrl, Key.cmd_r]:
                        self.keyboard.release(k)
                    
                    # 4. ROBUST NATIVE PASTE
                    log("ACTION: Executing Native Paste Shortcut...")
                    os.system('osascript -e "tell application \\"System Events\\" to keystroke \\"v\\" using command down"')
                else:
                    log("TRANS: No text found.")
            os.remove(tf.name)
        except Exception as e:
            log(f"PROC ERROR: {e}")

def main():
    config = load_config()
    ui = TranscriberUI()
    ui.create()
    engine = Engine(ui)
    
    check_accessibility()
    
    sk = config.get("start_key_code", 63)
    st = config.get("start_trigger", "hold")
    last_p = False
    last_t = 0
    
    while True:
        p = is_key_pressed(sk)
        now = time.time()
        
        if st == "hold":
            if p and not last_p: engine.start()
            elif not p and last_p: engine.stop()
        elif st == "tap":
            if p and not last_p: engine.start() if not engine.rec else engine.stop()
        elif st == "double_tap":
            if p and not last_p:
                if now - last_t < 0.4: engine.start() if not engine.rec else engine.stop()
                last_t = now
        
        last_p = p
        ui.update()
        time.sleep(0.01)

if __name__ == "__main__":
    try: main()
    except Exception as e: log(f"FATAL ERROR: {e}")
