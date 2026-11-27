"""Draw Blip's tray icon, blip.ico, from its own colours. Needs Pillow (only to
regenerate the icon; Blip itself uses the standard library only):

    python tools/make_icon.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUTLINE, SHELL, SHELL_HI = "#151724", "#2e3347", "#6a7392"
BEZEL, SCREEN, EYE = "#d3d9e5", "#06080e", "#5ff3ff"
BAND, CUP, ACCENT = "#2b3042", "#2a2f40", "#ff9f1c"

N = 1024  # drawn big, then scaled down smoothly
img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
u = N / 64  # one unit = 1/64 of the icon


def box(x1, y1, x2, y2, r, fill, line=0):
    d.rounded_rectangle([x1 * u, y1 * u, x2 * u, y2 * u], r * u, fill=fill,
                        outline=OUTLINE if line else None, width=int(line * u))


# headphone band over the top
d.arc([8 * u, 4 * u, 56 * u, 46 * u], 180, 360, fill=OUTLINE, width=int(6.5 * u))
d.arc([9.2 * u, 5.2 * u, 54.8 * u, 44.8 * u], 180, 360, fill=BAND, width=int(4 * u))
# head shell, bezel and screen
box(7, 15, 57, 55, 11, SHELL, 2.2)
box(9.5, 17, 40, 27, 6, SHELL_HI)
box(11, 19, 53, 51, 8, BEZEL)
box(13.5, 21.5, 50.5, 48.5, 6.5, SCREEN)
# glowing eyes and a smile
for x in (21, 37):
    box(x, 27.5, x + 7, 37.5, 3, EYE)
    box(x + 1.2, 28.7, x + 3.6, 31.3, 1.2, "#ffffff")
d.arc([26 * u, 35 * u, 38 * u, 43.5 * u], 20, 160, fill=EYE, width=int(2.4 * u))
# ear cups with orange caps
for x1, x2 in ((1.5, 9.5), (54.5, 62.5)):
    box(x1, 24, x2, 46, 3.5, CUP, 1.8)
    cap = (x1 + 0.5, x1 + 3.5) if x1 < 30 else (x2 - 3.5, x2 - 0.5)
    box(cap[0], 27, cap[1], 43, 1.5, ACCENT)

out = Path(__file__).resolve().parent.parent / "blip.ico"
img.save(out, sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48),
                     (64, 64), (128, 128), (256, 256)])
print("wrote", out)
