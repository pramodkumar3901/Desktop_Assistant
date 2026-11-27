"""Blip's windows for typing: the box that asks Claude, and the draft helper's chat.

The draft chat only shows the conversation and reports what you do; blip.pyw asks Claude.
The conversation is a list of (who, text): "blip" is a rewrite, "you" is feedback and
"note" is a message about the chat itself. The newest rewrite can be edited by hand.
"""

import ctypes
import tkinter as tk

TITLE = "Blip · Draft helper"
HINT = "Tell Blip what to change.   Enter sends · Shift+Enter adds a line"
MAX_FEEDBACK = 2000
ASK_HINT = "Enter sends · Esc closes"
MAX_ASK = 20000
ASK_LINES = (2, 8)       # the box grows from this many lines to this many


class AskBox:
    """A small card above Blip with a box for a question or a task."""

    def __init__(self, master, colors, fonts, width, draft, on_send, links, on_close):
        """colors: card, raised, border, text, muted, accent. fonts: body, small, tag.
        links: [(label, action)] along the bottom. on_send(text) returns True if it
        was taken. on_close(draft) gets whatever is left unsent."""
        self.on_send, self.on_close = on_send, on_close
        c = colors

        win = self.win = tk.Toplevel(master)
        win.title("Ask Claude through Blip")
        win.overrideredirect(True)
        win.configure(bg=c["border"])
        win.attributes("-topmost", True)
        win.bind("<Escape>", lambda e: self.close())
        pad = max(6, width // 28)
        card = tk.Frame(win, bg=c["card"])
        card.pack(fill="both", expand=True, padx=1, pady=1)

        def label(row, text, command=None, color=None, font="small"):
            item = tk.Label(row, text=text, font=fonts[font], bg=c["card"],
                            fg=color or c["muted"], bd=0, cursor="hand2" if command else "")
            if command:
                item.bind("<Button-1>", lambda e: command())
                item.bind("<Enter>", lambda e: item.config(fg=c["text"]))
                item.bind("<Leave>", lambda e: item.config(fg=color or c["muted"]))
            return item

        head = tk.Frame(card, bg=c["card"])
        head.pack(fill="x", padx=pad, pady=(pad // 2, 0))
        label(head, "●", color=c["accent"], font="tag").pack(side="left")
        label(head, "ASK CLAUDE", font="tag").pack(side="left", padx=(4, 0))
        label(head, "×", self.close).pack(side="right")

        # The text box fills a frame of a fixed pixel width, whatever the font.
        holder = tk.Frame(card, bg=c["card"], width=width)
        holder.pack(fill="x", padx=pad, pady=(4, 2))
        self.entry = tk.Text(holder, wrap="word", height=ASK_LINES[0], width=1,
                             font=fonts["body"], bg=c["raised"], fg=c["text"],
                             insertbackground=c["text"], relief="flat", padx=8, pady=6,
                             undo=True, highlightthickness=1,
                             highlightbackground=c["border"], highlightcolor=c["accent"])
        self.entry.pack(fill="x")
        tk.Frame(card, bg=c["card"], width=width + 2 * pad, height=0).pack()
        self.entry.insert("1.0", draft)
        self.entry.edit_reset()
        self.entry.bind("<Return>", self.on_return)
        self.entry.bind("<KP_Enter>", self.on_return)
        self.entry.bind("<KeyRelease>", lambda e: self.grow())

        foot = tk.Frame(card, bg=c["card"])
        foot.pack(fill="x", padx=pad, pady=(0, pad // 2))
        label(foot, ASK_HINT).pack(side="left")
        for text, command in reversed(links):
            label(foot, text, command, color=c["accent"]).pack(side="right", padx=(8, 0))
        self.anchor = None       # (centre x, bottom y, screen area)
        self.round_corners()

    def text(self):
        return self.entry.get("1.0", "end-1c")

    def grow(self):
        if not self.alive():
            return
        shown = self.entry.count("1.0", "end", "displaylines")
        lines = shown[0] if isinstance(shown, tuple) else (shown or 1)
        height = min(max(lines, ASK_LINES[0]), ASK_LINES[1])
        if height != int(self.entry.cget("height")):
            self.entry.config(height=height)
            if self.anchor:
                self.place(*self.anchor)

    def on_return(self, event):
        if event.state & 0x1:  # Shift: a new line
            self.win.after_idle(self.grow)
            return None
        message = self.text().strip()[:MAX_ASK]
        if message and self.on_send(message):
            self.entry.delete("1.0", "end")
            self.close()
        return "break"

    def place(self, x, bottom, area):
        """Sit centred on x with the lower edge at `bottom`, inside the screen."""
        self.anchor = (x, bottom, area)
        self.win.update_idletasks()
        width, height = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        left, top, right, floor = area
        x = min(max(x - width // 2, left + 4), right - width - 4)
        y = min(max(bottom - height, top + 4), floor - height - 4)
        self.win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def top(self):
        return self.win.winfo_y()

    def alive(self):
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    def focus(self):
        """Bring the box forward, ready for typing."""
        self.win.deiconify()
        self.win.lift()
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetParent(self.win.winfo_id()) or self.win.winfo_id()
            user32.SetForegroundWindow(hwnd)
        except (OSError, tk.TclError, AttributeError):
            pass
        self.entry.focus_force()
        self.grow()

    def round_corners(self):
        try:
            self.win.update_idletasks()
            hwnd, small = int(self.win.wm_frame(), 16), ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(small), 4)
        except (OSError, ValueError, tk.TclError, AttributeError):
            pass

    def close(self):
        if not self.alive():
            return
        left = self.text().strip()
        self.win.destroy()
        self.on_close(left)


class DetailsWindow:
    """What Claude wants to do, in full, so you can read it before you Allow it."""

    def __init__(self, master, colors, fonts, title, text, on_close):
        self.on_close = on_close
        c = colors
        win = self.win = tk.Toplevel(master)
        win.title("Blip · " + title)
        win.configure(bg=c["card"])
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", self.close)
        win.bind("<Escape>", lambda e: self.close())
        tk.Label(win, text="Close this window, then choose Allow or Deny on Blip's card.",
                 font=fonts["small"], bg=c["card"], fg=c["muted"],
                 anchor="w").pack(side="bottom", fill="x", padx=12, pady=(4, 10))
        bar = tk.Scrollbar(win)
        bar.pack(side="right", fill="y", padx=(0, 4), pady=(10, 0))
        box = tk.Text(win, wrap="char", width=70, height=22, font=("Consolas", 10),
                      bg=c["raised"], fg=c["text"], relief="flat", padx=10, pady=8,
                      highlightthickness=0, yscrollcommand=bar.set)
        box.pack(side="left", fill="both", expand=True, padx=(12, 4), pady=(10, 0))
        bar.config(command=box.yview)
        box.insert("1.0", text)
        box.config(state="disabled")
        win.focus_force()

    def close(self):
        try:
            if not self.win.winfo_exists():
                return
            self.win.destroy()
        except tk.TclError:
            return
        self.on_close()


class DraftChat:
    def __init__(self, master, colors, fonts, items, on_send, on_copy, on_undo,
                 on_close=lambda: None):
        """colors: card, raised, hover, border, text, muted, accent.
        fonts: body, small, button. items: the conversation so far (shared, and kept
        up to date with your edits). on_send(feedback) returns True if it was taken."""
        self.items = items
        self.on_send, self.on_close = on_send, on_close
        self.busy = False
        self.writing = False     # True while this class itself changes the transcript
        self.editing = None      # the item the editable part of the transcript shows
        c = self.colors = colors

        win = self.win = tk.Toplevel(master)
        win.title(TITLE)
        win.configure(bg=c["card"])
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", self.close)
        win.bind("<Escape>", lambda e: self.close())

        def button(row, label, command, primary=False):
            return tk.Button(row, text=label, command=command, font=fonts["button"],
                             bg=c["accent"] if primary else c["raised"],
                             fg=c["card"] if primary else c["text"],
                             activebackground=c["accent"] if primary else c["hover"],
                             activeforeground=c["card"] if primary else c["text"],
                             disabledforeground=c["muted"], relief="flat", padx=14,
                             pady=3, cursor="hand2", takefocus=True)

        # Bottom up, so shrinking the window squeezes the transcript, not the controls.
        actions = tk.Frame(win, bg=c["card"])
        actions.pack(side="bottom", fill="x", padx=12, pady=(4, 12))
        self.copy_button = button(actions, "Copy latest", lambda: self.copy(on_copy))
        self.copy_button.pack(side="left")
        button(actions, "Undo (my original)", on_undo).pack(side="left", padx=(8, 0))
        button(actions, "Close", self.close).pack(side="right")

        tk.Label(win, text=HINT, font=fonts["small"], bg=c["card"], fg=c["muted"],
                 anchor="w").pack(side="bottom", fill="x", padx=12)
        row = tk.Frame(win, bg=c["card"])
        row.pack(side="bottom", fill="x", padx=12, pady=(6, 2))
        self.send_button = button(row, "Send", self.send, primary=True)
        self.send_button.pack(side="right", fill="y", padx=(8, 0))
        self.entry = tk.Text(row, wrap="word", height=2, width=20, font=fonts["body"],
                             bg=c["raised"], fg=c["text"], insertbackground=c["text"],
                             relief="flat", padx=10, pady=7, undo=True,
                             highlightthickness=1, highlightbackground=c["border"],
                             highlightcolor=c["accent"])
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_return)
        self.entry.bind("<KP_Enter>", self.on_return)

        top = tk.Frame(win, bg=c["card"])
        top.pack(side="top", fill="both", expand=True, padx=12, pady=(12, 0))
        # A slim scrollbar of our own: Windows draws Tk's in bright grey.
        bar = self.bar = tk.Canvas(top, width=6, height=1, bg=c["card"],
                                   highlightthickness=0, cursor="hand2")
        bar.pack(side="right", fill="y", padx=(6, 0))
        self.view = (0.0, 1.0)
        log = self.log = tk.Text(top, wrap="word", width=62, height=18, font=fonts["body"],
                                 bg=c["card"], fg=c["text"], insertbackground=c["text"],
                                 relief="flat", padx=4, pady=4, highlightthickness=0,
                                 yscrollcommand=self.scrolled)
        log.pack(side="left", fill="both", expand=True)
        bar.bind("<Configure>", lambda e: self.draw_bar())
        bar.bind("<Button-1>", self.drag_bar)
        bar.bind("<B1-Motion>", self.drag_bar)
        log.tag_configure("who", font=fonts["small"], foreground=c["muted"], spacing1=8)
        log.tag_configure("who_you", justify="right", rmargin=6)
        log.tag_configure("blip", background=c["raised"], lmargin1=10, lmargin2=10,
                          rmargin=40, spacing1=2, spacing3=2)
        log.tag_configure("you", foreground=c["accent"], justify="right", lmargin1=60,
                          lmargin2=60, rmargin=6)
        log.tag_configure("note", foreground=c["muted"], font=fonts["small"], spacing1=8)
        log.tag_raise("sel")
        self.guard()
        self.render()
        self.dark_title_bar()

    # -- scrolling

    def scrolled(self, first, last):
        self.view = (float(first), float(last))
        self.draw_bar()

    def draw_bar(self):
        bar, (first, last) = self.bar, self.view
        bar.delete("all")
        if last - first >= 0.999:
            return  # it all fits
        height, width = bar.winfo_height(), int(bar.cget("width"))
        bar.create_line(width / 2, first * height + 3, width / 2, last * height - 3,
                        fill=self.colors["border"], width=width - 1, capstyle="round")

    def drag_bar(self, event):
        first, last = self.view
        self.log.yview_moveto(event.y / max(1, self.bar.winfo_height())
                              - (last - first) / 2)

    # -- only the newest rewrite can be edited

    def guard(self):
        """Put a check in front of the transcript's own command, so typing, pasting
        and cutting only change the newest rewrite. It is a Tcl proc so that Tk's own
        errors (such as copying with nothing selected) reach Tk unchanged."""
        name = str(self.log)
        self.raw = name + "_raw"
        check = self.log.register(self.allowed)
        self.log.tk.call("rename", name, self.raw)
        self.log.tk.eval(
            f"proc {name} {{command args}} {{\n"
            f"    if {{[{check} $command {{*}}$args]}} {{\n"
            f"        return [{self.raw} $command {{*}}$args]\n"
            "    }\n"
            "}")

    def allowed(self, command, *args):
        if self.writing or command not in ("insert", "delete", "replace"):
            return 1
        if self.editing is None or self.busy or not args:
            return 0
        try:
            call = self.log.tk.call
            first = call(self.raw, "index", args[0])
            if command == "insert":
                last = first
            elif command == "delete" and len(args) < 2:
                last = call(self.raw, "index", f"{first}+1c")
            else:
                last = call(self.raw, "index", args[1])

            def holds(a, op, b):
                return self.log.tk.getboolean(call(self.raw, "compare", a, op, b))
            return int(holds(first, ">=", "edit_start") and holds(last, "<=", "edit_end"))
        except tk.TclError:
            return 0

    def sync(self):
        """Keep your hand edits to the newest rewrite."""
        if self.editing is None:
            return
        text = self.log.get("edit_start", "edit_end").strip()
        if text:
            self.items[self.editing] = ("blip", text)

    def render(self):
        """Draw the whole conversation again and scroll to the end."""
        self.writing = True
        try:
            log = self.log
            log.delete("1.0", "end")
            self.editing = None
            newest = max((i for i, (who, _) in enumerate(self.items) if who == "blip"),
                         default=None)
            version = 0
            for i, (who, text) in enumerate(self.items):
                if who == "note":
                    log.insert("end", text + "\n", "note")
                    continue
                if who == "blip":
                    version += 1
                    label = f"Blip · version {version}"
                    if i == newest:
                        label += " (you can edit this one)"
                    log.insert("end", label + "\n", "who")
                else:
                    log.insert("end", "You\n", ("who", "who_you"))
                start = log.index("end-1c")
                log.insert("end", text, who)
                if i == newest:
                    stop = log.index("end-1c")
                    log.mark_set("edit_start", start)
                    log.mark_gravity("edit_start", "left")
                    log.insert("end", "\n", who)
                    log.mark_set("edit_end", stop)
                    log.mark_gravity("edit_end", "right")
                    self.editing = i
                else:
                    log.insert("end", "\n", who)
            if self.busy:
                log.insert("end", "Blip is rewriting…\n", "note")
            log.edit_modified(False)
        finally:
            self.writing = False
        self.log.see("end")
        # Typed text takes the tags around it; keep the newest rewrite looking right.
        self.log.bind("<<Modified>>", self.retag)

    def retag(self, _event=None):
        if self.editing is not None and self.log.edit_modified():
            self.log.tag_add("blip", "edit_start", "edit_end")
        self.log.edit_modified(False)

    # -- the conversation

    def add(self, who, text):
        self.sync()
        self.items.append((who, text))
        self.render()

    def set_busy(self, busy):
        self.sync()
        self.busy = busy
        self.send_button.config(state="disabled" if busy else "normal")
        self.render()

    def latest(self):
        """The newest rewrite, with any edits."""
        self.sync()
        return next((text for who, text in reversed(self.items) if who == "blip"), "")

    def on_return(self, event):
        if event.state & 0x1:  # Shift: a new line
            return None
        self.send()
        return "break"

    def send(self):
        feedback = self.entry.get("1.0", "end-1c").strip()[:MAX_FEEDBACK]
        if not feedback or self.busy:
            return
        self.sync()
        if self.on_send(feedback):
            self.entry.delete("1.0", "end")
            self.entry.edit_reset()

    def give_back(self, feedback):
        """Sending failed: put the words back in the box to try again."""
        if not self.entry.get("1.0", "end-1c").strip():
            self.entry.insert("1.0", feedback)

    def copy(self, on_copy):
        on_copy(self.latest())
        self.copy_button.config(text="Copied ✓")
        self.win.after(1200, lambda: self.copy_button.config(text="Copy latest")
                       if self.alive() else None)

    # -- the window

    def alive(self):
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    def place(self, x, bottom, area):
        """Open centred on x, its lower edge near `bottom`, inside the screen."""
        self.win.update_idletasks()
        width, height = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        left, top, right, floor = area
        height = min(height, floor - top - 60)
        x = min(max(x - width // 2, left + 8), right - width - 8)
        y = min(max(bottom - height - 40, top + 8), floor - height - 40)
        self.win.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
        self.win.minsize(min(width, 360), min(height, 300))

    def focus(self):
        """Bring the window forward, ready for typing."""
        self.win.deiconify()
        self.win.lift()
        try:
            hwnd = int(self.win.wm_frame(), 16)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except (OSError, ValueError, tk.TclError, AttributeError):
            pass
        self.entry.focus_force()

    def dark_title_bar(self):
        try:
            self.win.update_idletasks()
            hwnd, on = int(self.win.wm_frame(), 16), ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(on), 4)
        except (OSError, ValueError, tk.TclError, AttributeError):
            pass

    def close(self):
        if not self.alive():
            return
        self.sync()
        self.win.destroy()
        self.on_close()
