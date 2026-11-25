"""Drive a harness-started HoI4 window for UI screenshots.

Usage (commands run in order; coordinates are game client pixels). The first
argument is the game pid the harness printed ("game pid N"); the driver refuses
any other process, so it never touches another lane's game:
  python tests/ui/ui_drive.py 1234 shot out.png
  python tests/ui/ui_drive.py 1234 key SPACE wait 1 click 640 300 wait 1 shot a.png
  python tests/ui/ui_drive.py 1234 rclick 900 400 move 10 10 shot b.png

Commands: shot PATH | click X Y | rclick X Y | dclick X Y | move X Y |
          key NAME (SPACE, ESCAPE, F1..F12, A..Z, 0..9) | wait SECONDS | size
Only windows of a hoi4.exe whose command line carries the harness -userdir
tag are touched; the user's own game is never driven.
"""
import ctypes
import subprocess
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:  # noqa: BLE001
    user32.SetProcessDPIAware()


def harness_pids():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"Name='hoi4.exe'\" | ForEach-Object { \"$($_.ProcessId)|$($_.CommandLine)\" }"],
        capture_output=True, text=True).stdout
    pids = []
    for line in out.splitlines():
        if "|" in line:
            pid, cmd = line.split("|", 1)
            if ".hoi4-userdir" in cmd or "-userdir=" in cmd:
                pids.append(int(pid))
    return pids


def find_hwnd(pid):
    if pid not in harness_pids():
        sys.exit(f"pid {pid} is not a running harness hoi4.exe")
    pids = {pid}
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value in pids and user32.IsWindowVisible(hwnd):
            r = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(r))
            found.append((r.right * r.bottom, hwnd))
        return True

    user32.EnumWindows(cb, 0)
    if not found:
        sys.exit("game window not found")
    return max(found)[1]


def client_origin(hwnd):
    p = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(p))
    r = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    return p.x, p.y, r.right, r.bottom


def focus(hwnd):
    user32.ShowWindow(hwnd, 5)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)


MOUSE = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010)}


def mouse_to(hwnd, x, y):
    ox, oy, _, _ = client_origin(hwnd)
    user32.SetCursorPos(ox + int(x), oy + int(y))
    time.sleep(0.08)


def click(hwnd, x, y, button="left", n=1):
    focus(hwnd)
    mouse_to(hwnd, x, y)
    down, up = MOUSE[button]
    for _ in range(n):
        user32.mouse_event(down, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(up, 0, 0, 0, 0)
        time.sleep(0.08)


VK = {"SPACE": 0x20, "ESCAPE": 0x1B, "RETURN": 0x0D, "TAB": 0x09, "PRINT": 0x2C}
VK.update({f"F{i}": 0x6F + i for i in range(1, 13)})
VK.update({chr(c): c for c in range(ord("A"), ord("Z") + 1)})
VK.update({chr(c): c for c in range(ord("0"), ord("9") + 1)})


def key(hwnd, name):
    focus(hwnd)
    vk = VK[name.upper()]
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, 2, 0)
    time.sleep(0.1)


def shot(hwnd, path):
    from PIL import ImageGrab
    ox, oy, w, h = client_origin(hwnd)
    focus(hwnd)
    time.sleep(0.3)
    ImageGrab.grab(bbox=(ox, oy, ox + w, oy + h), all_screens=True).save(path)
    print("shot", path, w, h)


def main(argv):
    hwnd = find_hwnd(int(argv[0]))
    i = 1
    while i < len(argv):
        c = argv[i]
        if c == "shot":
            shot(hwnd, argv[i + 1]); i += 2
        elif c in ("click", "rclick", "dclick"):
            click(hwnd, float(argv[i + 1]), float(argv[i + 2]),
                  "right" if c == "rclick" else "left", 2 if c == "dclick" else 1)
            i += 3
        elif c == "move":
            focus(hwnd); mouse_to(hwnd, float(argv[i + 1]), float(argv[i + 2])); i += 3
        elif c == "key":
            key(hwnd, argv[i + 1]); i += 2
        elif c == "wait":
            time.sleep(float(argv[i + 1])); i += 2
        elif c == "size":
            print(client_origin(hwnd)); i += 1
        else:
            sys.exit(f"unknown command {c}")


if __name__ == "__main__":
    main(sys.argv[1:])
