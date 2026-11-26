"""Make Blip say something: python blip_say.py "The tests passed!"

Claude Code sessions learn about this from Blip's SessionStart hook, so you can ask
Claude things like "tell me through Blip when the build finishes". Works from any
terminal too. Prints a short note and exits 1 if Blip isn't running.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

ALERTS_FILE = Path(__file__).with_name("blip_alerts.json")


def main():
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print('usage: python blip_say.py "message"')
        return 2
    try:
        where = json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
        body = json.dumps({"hook_event_name": "Say", "message": text[:300],
                           "cwd": os.getcwd(),
                           # lets a session's own clone say it, if it has one
                           "session_id": os.environ.get("CLAUDE_CODE_SESSION_ID", ""),
                           "source": os.environ.get("CLAUDE_CODE_ENTRYPOINT", "")})
        request = urllib.request.Request(
            f"http://127.0.0.1:{int(where['port'])}/event", data=body.encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "X-Blip-Token": where["token"]})
        urllib.request.urlopen(request, timeout=3).close()
    except Exception:
        print("Blip isn't running, so the message wasn't shown.")
        return 1
    print("Blip said it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
