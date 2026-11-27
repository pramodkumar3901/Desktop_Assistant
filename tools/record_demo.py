"""Record the README demo GIF: python tools/record_demo.py [out.gif]. Needs Pillow.

Blip runs on a virtual clock on a small stage. Every Blip window is drawn opaque on a
plain background and grabbed on its own (the others made see-through), so nothing
else on the screen can end up in a frame. Keep the screen unlocked while it runs."""
import ctypes
import importlib.machinery
import importlib.util
import random
import sys
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageGrab

ctypes.windll.shcore.SetProcessDpiAwareness(2)
random.seed(7)
OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/blip-demo.gif"
SRC = r"D:\WORK\GITHUB\PERSONAL\Blip\blip.pyw"
loader = importlib.machinery.SourceFileLoader("blip", SRC)
spec = importlib.util.spec_from_loader("blip", loader)
blip = importlib.util.module_from_spec(spec)
loader.exec_module(blip)


class Clock:
    now = 1_000_000.0

    def time(self):
        return self.now

    def strftime(self, *a):
        import time
        return time.strftime(*a)


clock = Clock()
blip.time = clock
BG = "#e4e9f0"
blip.TRANSPARENT = BG


def overlay(window):
    window.overrideredirect(True)
    window.configure(bg=BG)
    window.attributes("-topmost", True)


blip.make_overlay = overlay
blip.raise_overlay = lambda w: None
SX, SY, W, H = 300, 200, 720, 440  # the stage, on the real screen
stage = (SX, SY, SX + W, SY + H)
blip.monitors = lambda: [{"rect": stage, "work": stage, "dpi": 96, "primary": True}]
blip.load_settings = lambda: {"size": "normal", "accessory": "music", "quiet": True}
blip.save_settings = lambda *_: None
blip.Tray = lambda *a, **k: None
blip.Blip.tick = lambda self: None
blip.DANGER_DROP = 110  # the stage is short: make a fall "dangerous" sooner
blip.ARRIVED = ["Hi! I'm here. What did I miss?"]


class Lines:
    waiting = False

    def take(self, kind, wait=True):
        return "You've got this. I believe in you more than my battery does."

    def refill(self):
        pass

    def poll(self):
        return None


root = tk.Tk()
random.seed(3)
orig_choice = random.choice
b = blip.Blip(root, Lines())
b.next_antic = float("inf")
mouse = [(-5000, -5000)]
blip.tk.Misc.winfo_pointerxy = lambda self: mouse[0]

frames = []
FRAME = blip.Blip.FRAME_MS / 1000
count = [0]


def windows():
    found = []
    for x in [b] + list(b.clones.values()):
        for attr in ("door_win",):
            w = getattr(x, attr, None)
            if w is not None and w.winfo_exists() and w.winfo_viewable():
                found.append(("door", w))
    for x in [b] + list(b.clones.values()):
        if x.alive and x.root.winfo_exists() and x.root.winfo_viewable():
            found.append(("body", x.root))
    for x in [b] + list(b.clones.values()):
        if x.alive and x.bubble.winfo_exists() and x.bubble.winfo_viewable():
            found.append(("bubble", x.bubble))
    return found


def capture():
    wins = [w for _, w in windows()]
    sheet = Image.new("RGB", (W, H), BG)
    for target in wins:
        for w in wins:
            w.attributes("-alpha", 1.0 if w is target else 0.0)
        root.update()
        ctypes.windll.dwmapi.DwmFlush()
        x, y = target.winfo_rootx(), target.winfo_rooty()
        ww, hh = target.winfo_width(), target.winfo_height()
        im = ImageGrab.grab(bbox=(x, y, x + ww, y + hh), all_screens=True).convert("RGB")
        bgc = tuple(int(BG[i:i + 2], 16) for i in (1, 3, 5))
        mask = Image.frombytes("L", im.size, bytes(
            0 if p == bgc else 255 for p in im.get_flattened_data()))
        sheet.paste(im, (x - SX, y - SY), mask)
    for w in wins:
        w.attributes("-alpha", 1.0)
    frames.append(sheet)


def run(seconds):
    for _ in range(int(round(seconds / FRAME))):
        clock.now += FRAME
        if b.alive:
            b.frame_step()
        for c in list(b.clones.values()):
            if c.alive:
                c.frame_step()
        root.update_idletasks()
        count[0] += 1
        if count[0] % 3 == 0:
            capture()


left = SX
# 1. walks in through a door
b.door = None
b.enter(side=-1, stop_x=left + 120.0)
run(3.6)
b.say("Hi! I'm here. What did I miss?", seconds=2.4)
run(2.4)
# 2. strolls along, turned side-on
b.direction, b.mode, b.mode_until = 1, "walk", clock.now + 30
run(2.6)
b.mode, b.mode_until = "rest", clock.now + 30
run(0.5)
# 3. moonwalk
b.start_act("moonwalk")
run(5.2)
run(0.6)
# 4. thrown: a glider; dropped from high: a parachute
b.mode, b.mode_until = "rest", clock.now + 60
b.x = float(left + 20)
b.air, b.fall_from, b.vx, b.fall_speed = 40.0, 40.0, 1100.0, -950.0
run(3.4)
b.hush()
b.x = float(left + W / 2 - b.w / 2)
b.air = b.fall_from = float(H - b.h - 4)
b.vx = b.fall_speed = 0.0
run(3.2)
# 5. a second Claude Code session: a mini Blip walks in, works, finishes, leaves
blip.random.choice = lambda seq: seq[0]
b.spawn_clone("s2", {"cwd": r"C:\work\weather-app"})
clone = b.clones["s2"]
run(3.2)
clone.task_event({"hook_event_name": "Stop"})
run(2.6)
clone.retire()
run(3.2)
blip.random.choice = orig_choice
# 6. a compact suggestion card
b.say("It looks like you're watching a demo. Want me to narrate it?", seconds=3,
      buttons=(("Yes please!", None), ("No thanks", None)), tag="Suggestion")
run(2.8)
# 7. bye: out through the door
b.hush()
b.leave(side=1, then=b.hide_now)
run(4.2)

print("frames", len(frames))
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=100, loop=0,
               optimize=True, disposal=1)
