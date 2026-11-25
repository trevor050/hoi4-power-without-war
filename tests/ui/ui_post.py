"""Drive a harness HoI4 window with posted window messages (works while the
Windows session is locked or disconnected, when real input and desktop capture
do not). Coordinates are in game render pixels (the --size resolution); they
are scaled to the window's client size. Screenshots use the game's own
screenshot key and land in the isolated userdir's screenshots folder.

  python tests/ui/ui_post.py PID key SPACE click 1054 478 wait 1 shot out.png
Commands: click X Y | rclick X Y | move X Y | key NAME | wait S | shot PATH
"""
import ctypes, glob, os, shutil, sys, time
from ctypes import wintypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ui_drive as d

u = ctypes.windll.user32
SHOTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                     ".hoi4-userdir", "home", "Documents", "Paradox Interactive", "Hearts of Iron IV", "screenshots")
RENDER = tuple(int(v) for v in os.environ.get("PWW_RENDER", "1920x1080").split("x"))


def scale(h, x, y):
    r = wintypes.RECT(); u.GetClientRect(h, ctypes.byref(r))
    return int(float(x) * r.right / RENDER[0]), int(float(y) * r.bottom / RENDER[1])


def post_mouse(h, x, y, down, up, btnflag):
    cx, cy = scale(h, x, y); lp = (cy << 16) | (cx & 0xFFFF)
    u.PostMessageW(h, 0x200, 0, lp); time.sleep(0.08)
    u.PostMessageW(h, down, btnflag, lp); time.sleep(0.06)
    u.PostMessageW(h, up, 0, lp); time.sleep(0.15)


def post_key(h, vk):
    sc = u.MapVirtualKeyW(vk, 0)
    u.PostMessageW(h, 0x100, vk, 1 | (sc << 16)); time.sleep(0.06)
    u.PostMessageW(h, 0x101, vk, 1 | (sc << 16) | 0xC0000000); time.sleep(0.15)


def shot(h, path):
    before = set(glob.glob(os.path.join(SHOTS, "*.png")))
    post_key(h, 0x7A)  # F11, the game's screenshot key
    for _ in range(60):
        time.sleep(0.25)
        new = set(glob.glob(os.path.join(SHOTS, "*.png"))) - before
        if new:
            time.sleep(0.5)
            src = new.pop(); shutil.move(src, path); print("shot", path); return
    print("shot FAILED", path)


def main(a):
    h = d.find_hwnd(int(a[0])); i = 1
    while i < len(a):
        c = a[i]
        if c == "click": post_mouse(h, a[i+1], a[i+2], 0x201, 0x202, 1); i += 3
        elif c == "rclick": post_mouse(h, a[i+1], a[i+2], 0x204, 0x205, 2); i += 3
        elif c == "move":
            cx, cy = scale(h, a[i+1], a[i+2]); u.PostMessageW(h, 0x200, 0, (cy << 16) | cx); time.sleep(0.2); i += 3
        elif c == "key": post_key(h, d.VK[a[i+1].upper()]); i += 2
        elif c == "wait": time.sleep(float(a[i+1])); i += 2
        elif c == "shot": shot(h, a[i+1]); i += 2
        else: sys.exit("unknown " + c)


if __name__ == "__main__":
    main(sys.argv[1:])
