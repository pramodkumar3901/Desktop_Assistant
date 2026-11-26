"""Claude Code hook: tell Blip what a session is doing.

Blip's "Connect to Claude Code" menu item adds this to ~/.claude/settings.json for the
UserPromptSubmit, Stop, Notification, SessionStart and SessionEnd events; Claude Code
(terminal and desktop app alike) passes the event as JSON on stdin. It forwards a few
fields to Blip's listener on this PC. If Blip isn't running it quietly does nothing; it
never fails or blocks Claude.

On SessionStart, when Blip answers, it also prints one line that Claude Code adds to
the session's context, so Claude knows it can talk to you through Blip (blip_say.py).
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

ALERTS_FILE = Path(__file__).with_name("blip_alerts.json")
SAY_SCRIPT = Path(__file__).with_name("blip_say.py").as_posix()
FIELDS = ("hook_event_name", "cwd", "message", "notification_type", "session_id")


def send(event):
    """POST an event to Blip. True if Blip took it."""
    where = json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
    body = json.dumps(event).encode("utf-8")
    request = urllib.request.Request(
        f"http://127.0.0.1:{int(where['port'])}/event", data=body, method="POST",
        headers={"Content-Type": "application/json", "X-Blip-Token": where["token"]})
    with urllib.request.urlopen(request, timeout=2) as reply:
        return reply.status < 300


def main():
    try:
        # utf-8-sig: some shells put a byte-order mark in front of piped text
        event = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
        fields = {k: event.get(k) for k in FIELDS}
        # "cli" for the terminal, "claude-desktop" for the desktop app, and so on
        fields["source"] = os.environ.get("CLAUDE_CODE_ENTRYPOINT", "")
        if send(fields) and fields["hook_event_name"] == "SessionStart":
            print(f'The user\'s desktop pet Blip is running. To get their attention '
                  f'(for example when they ask to be pinged when something finishes), '
                  f'run: python "{SAY_SCRIPT}" "short message"')
    except Exception:
        pass  # Blip closed, or anything else: never get in Claude's way


if __name__ == "__main__":
    main()
    sys.exit(0)
