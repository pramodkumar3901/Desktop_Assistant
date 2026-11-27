"""Blip's conversation with Claude: one saved Claude Code session, a message at a time.

No window code here. Each message runs `claude -p` on the same session (so it
remembers the chat, and messages you add in the Claude app are remembered too) and
reports back through a queue as (turn, kind, value):

    "started"     None: the session exists and can be resumed or opened
    "progress"    a short line about what Claude is doing
    "permission"  a request to use a tool; answer it with turn.answer()
    "cancel"      the id of a request Claude no longer needs answered
    "reply"       Claude's answer (the last thing it said)
    "error"       what went wrong
    "stopped"     you stopped it
"""

import json
import os
import re
import subprocess
import threading
from pathlib import Path

CHAT_PROMPT = (
    "The user is talking to you through Blip, a tiny desktop pet. Blip shows only your "
    "last message, in a small speech card, so keep it short and plain: a few sentences, "
    "no headings or tables, and lead with the answer or what you did. If you need "
    "something from them, ask in one short question. When they ask for detail, or for "
    "text to copy, give it in full."
)
NO_CONVERSATION = "No conversation found"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# What each tool is doing, for the progress line.
DOING = {
    "Read": "Reading {file}", "Write": "Writing {file}", "Edit": "Editing {file}",
    "NotebookEdit": "Editing {file}", "Glob": "Looking for files",
    "Grep": "Searching the files", "Bash": "Running a command",
    "PowerShell": "Running a command", "WebSearch": "Searching the web",
    "WebFetch": "Reading a web page", "Agent": "Getting help from a helper",
    "Task": "Getting help from a helper", "Skill": "Using a skill",
}


def clean_env():
    """The environment for Claude. If Blip was started from inside a Claude Code
    session, leave that session's variables behind."""
    env = dict(os.environ)
    if "CLAUDECODE" in env:
        for name in [n for n in env if n.startswith("CLAUDE")]:
            del env[name]
    return env


def file_name(tool_input):
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    return Path(str(path)).name or "a file"


def doing(tool, tool_input):
    if tool.startswith("mcp__"):
        return f"Using {tool.split('__')[-1].replace('_', ' ')}"
    return DOING.get(tool, f"Using {tool}").format(file=file_name(tool_input or {}))


def shown_path(path, folder):
    """A path as short as it can be without hiding where it is: relative inside the
    task folder, in full anywhere else."""
    if folder:
        full, base = os.path.abspath(path), os.path.abspath(folder)
        if os.path.normcase(full).startswith(os.path.normcase(os.path.join(base, ""))):
            return os.path.relpath(full, base)
    return path


def describe_request(request, folder=None):
    """(title, details) for a permission request: what Claude wants to do, in full."""
    tool = str(request.get("tool_name") or "a tool")
    given = request.get("input") if isinstance(request.get("input"), dict) else {}
    name = str(request.get("display_name") or tool)
    if tool in ("Bash", "PowerShell"):
        return "Run this command?", str(given.get("command") or "")
    path = given.get("file_path") or given.get("notebook_path")
    if tool in ("Write", "Edit", "NotebookEdit") and path:
        parts = [shown_path(str(path), folder)]
        old = given.get("old_string")
        if old:
            parts.append(f"Replace:\n{old}")
        new = given.get("new_string", given.get("content", given.get("new_source")))
        if new is not None:
            parts.append(f"{'With' if old else 'New text'}:\n{new}")
        if given.get("replace_all"):
            parts.append("Every match is replaced.")
        verb = "write" if tool == "Write" else "change"
        return f"Let Claude {verb} {Path(str(path)).name}?", "\n\n".join(parts)
    if tool == "WebFetch":
        return "Let Claude read this web page?", str(given.get("url") or "")
    details = "\n".join(f"{k}: {v if isinstance(v, str) else json.dumps(v)}"
                        for k, v in given.items())
    return f"Let Claude use {name}?", details


def plain(text):
    """Claude's reply without the Markdown marks a speech card can't show."""
    text = re.sub(r"^```.*$\n?", "", text, flags=re.M)
    text = re.sub(r"\[([^\]\n]+)\]\(([^)\s]+)\)", r"\1", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"^(\s*)[-*]\s+", "\\1• ", text, flags=re.M)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class Turn:
    """One message to Claude and everything that comes back."""

    def __init__(self, exe, message, session, resume, folder, events, log):
        self.exe, self.message, self.folder = exe, message, str(folder)
        self.session, self.resume = session, resume
        self.events, self.log = events, log
        self.proc = None
        self.stopped = False
        self.lock = threading.Lock()
        threading.Thread(target=self.run, daemon=True).start()

    def command(self):
        return [self.exe, "-p",
                "--input-format", "stream-json", "--output-format", "stream-json",
                "--verbose",
                # Anything that needs your OK comes here as a request.
                "--permission-mode", "manual", "--permission-prompt-tool", "stdio",
                "--disallowedTools", "AskUserQuestion",  # it asks in words instead
                "--append-system-prompt", CHAT_PROMPT,
                *(["--resume", self.session] if self.resume
                  else ["--session-id", self.session, "--name", "Blip"])]

    def put(self, kind, value=None):
        self.events.put((self, kind, value))

    def send(self, data):
        with self.lock:
            try:
                self.proc.stdin.write(json.dumps(data) + "\n")
                self.proc.stdin.flush()
                return True
            except (OSError, ValueError, AttributeError):
                return False

    def run(self):
        errors = []
        try:
            self.proc = subprocess.Popen(
                self.command(), cwd=self.folder, env=clean_env(), text=True,
                encoding="utf-8", errors="replace", stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=NO_WINDOW)

            def drain():  # so a chatty stderr can't fill up and stall Claude
                for line in self.proc.stderr:
                    errors.append(line)
                    del errors[:-20]
            reader = threading.Thread(target=drain, daemon=True)
            reader.start()
            if self.stopped:  # stopped while it was starting
                self.kill()
            self.send({"type": "user",
                       "message": {"role": "user", "content": self.message}})
            done = self.read()
            try:
                self.proc.stdin.close()
            except OSError:
                pass
            try:
                self.proc.wait(30)
            except subprocess.TimeoutExpired:
                self.kill()
            reader.join(2)
            if self.stopped:
                self.put("stopped")
            elif not done:
                self.put("error", "".join(errors).strip()[-600:]
                         or f"claude exited {self.proc.returncode} without answering")
        except Exception as error:
            self.log.exception("chat turn failed")
            self.kill()
            if self.stopped:
                self.put("stopped")
            else:
                self.put("error", str(error))

    def read(self):
        """Follow Claude's output. True once the answer (or failure) is reported."""
        for line in self.proc.stdout:
            try:
                data = json.loads(line)
            except ValueError:
                continue
            kind = data.get("type")
            if kind == "system" and data.get("subtype") == "init":
                self.put("started")
            elif kind == "assistant" and not data.get("parent_tool_use_id"):
                for block in data.get("message", {}).get("content") or []:
                    if block.get("type") == "tool_use":
                        self.put("progress", doing(str(block.get("name")),
                                                   block.get("input")))
            elif kind == "control_request":
                self.take_request(data)
            elif kind == "control_cancel_request":
                self.put("cancel", data.get("request_id"))
            elif kind == "result":
                if self.stopped:
                    return True
                text = str(data.get("result") or "").strip()
                if data.get("is_error") or data.get("subtype") != "success":
                    problems = data.get("errors")
                    self.put("error", text or "; ".join(map(str, problems or []))
                             or str(data.get("subtype")))
                else:
                    self.put("reply", text or "Done.")
                return True
        return False

    def take_request(self, data):
        request = data.get("request") or {}
        if request.get("subtype") == "can_use_tool":
            self.put("permission", {**request, "id": data.get("request_id")})
            return
        self.send({"type": "control_response", "response": {
            "subtype": "error", "request_id": data.get("request_id"),
            "error": "Blip can't answer this kind of request"}})

    def answer(self, request, allow):
        verdict = ({"behavior": "allow", "updatedInput": request.get("input") or {}}
                   if allow else
                   {"behavior": "deny", "message": "The user pressed Deny in Blip."})
        return self.send({"type": "control_response", "response": {
            "subtype": "success", "request_id": request["id"], "response": verdict}})

    def stop(self):
        self.stopped = True
        threading.Thread(target=self.kill, daemon=True).start()

    def kill(self):
        """End Claude and anything it started."""
        proc = self.proc
        if proc is None or proc.poll() is not None:
            return
        try:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                           capture_output=True, timeout=10, creationflags=NO_WINDOW)
        except (OSError, subprocess.SubprocessError):
            proc.kill()


def open_in_app(exe, session, folder):
    """Show the session in the Claude desktop app. `claude --desktop` needs a real
    console, so give it one that stays out of sight. Returns the process."""
    hidden = subprocess.STARTUPINFO()
    hidden.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    hidden.wShowWindow = 0  # SW_HIDE
    return subprocess.Popen([exe, "--desktop", "--resume", session], cwd=str(folder),
                            env=clean_env(), startupinfo=hidden,
                            creationflags=subprocess.CREATE_NEW_CONSOLE)
