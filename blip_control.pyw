"""Start, stop, restart or reset Blip: `pythonw blip_control.pyw start|stop|restart|reset`.

The shortcuts in this folder run this without a console window.
"""

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLIP = HERE / "blip.pyw"
SETTINGS = HERE / "blip_settings.json"
NO_WINDOW = subprocess.CREATE_NO_WINDOW


def blip_processes():
    """IDs of the Python processes running blip.pyw (not this helper)."""
    script = ("Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
              "Where-Object { $_.CommandLine -match 'blip\\.pyw' -and "
              "$_.CommandLine -notmatch 'blip_control' } | "
              "ForEach-Object { $_.ProcessId }")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                         capture_output=True, text=True, creationflags=NO_WINDOW).stdout
    return [int(line) for line in out.split() if line.strip().isdigit()]


def stop():
    pids = blip_processes()
    for pid in pids:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True,
                       creationflags=NO_WINDOW)
    for _ in range(30):  # wait until it is really gone, so a restart isn't refused
        if not blip_processes():
            break
        time.sleep(0.1)


def start():
    if blip_processes():
        return  # already running
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    subprocess.Popen([str(pythonw if pythonw.exists() else sys.executable), str(BLIP)],
                     cwd=HERE, creationflags=subprocess.DETACHED_PROCESS | NO_WINDOW)


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "start"
    if action == "start":
        start()
    elif action == "stop":
        stop()
    elif action == "restart":
        stop()
        start()
    elif action == "reset":  # forget the accessory and Quiet mode, then start fresh
        stop()
        SETTINGS.unlink(missing_ok=True)
        start()


if __name__ == "__main__":
    main()
