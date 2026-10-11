"""Write the RISE launcher icons into the generated Android project.

Run from the repo root after `npx cap add android`:
    python scripts/make_icons.py

It overwrites the legacy icons, the round icons and the adaptive-icon layers
(foreground image + background colour) so every Android version shows the R.
"""
import os
import re
import sys

from PIL import Image, ImageDraw

SRC = "assets/icon-only.png"
RES = "android/app/src/main/res"
BG_HEX = "#000000"

LEGACY = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FOREGROUND = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
# The R fills about 62% of the source image. Android shows only the middle ~66%
# of an adaptive icon, so shrink it a little so nothing gets clipped.
FOREGROUND_SCALE = 0.83

ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""

BACKGROUND_XML = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">%s</color>
</resources>
"""


def main():
    if not os.path.isfile(SRC):
        sys.exit("missing " + SRC)
    if not os.path.isdir(RES):
        sys.exit("missing " + RES + " (run `npx cap add android` first)")

    src = Image.open(SRC).convert("RGB")
    written = []

    def save(img, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path, "PNG")
        written.append(path)

    # Legacy/round icons have no safe-zone shrinking, so zoom in on the R.
    zoomed = src.crop((102, 102, 922, 922))

    for dens, size in LEGACY.items():
        folder = os.path.join(RES, "mipmap-" + dens)
        square = zoomed.resize((size, size), Image.LANCZOS)
        save(square, os.path.join(folder, "ic_launcher.png"))

        mask = Image.new("L", (size * 4, size * 4), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
        mask = mask.resize((size, size), Image.LANCZOS)
        round_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        round_img.paste(square, (0, 0), mask)
        save(round_img, os.path.join(folder, "ic_launcher_round.png"))

    for dens, size in FOREGROUND.items():
        folder = os.path.join(RES, "mipmap-" + dens)
        inner = int(size * FOREGROUND_SCALE)
        art = src.resize((inner, inner), Image.LANCZOS)
        canvas = Image.new("RGB", (size, size), (0, 0, 0))
        canvas.paste(art, ((size - inner) // 2, (size - inner) // 2))
        save(canvas, os.path.join(folder, "ic_launcher_foreground.png"))

    anydpi = os.path.join(RES, "mipmap-anydpi-v26")
    os.makedirs(anydpi, exist_ok=True)
    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        path = os.path.join(anydpi, name)
        with open(path, "w") as f:
            f.write(ADAPTIVE_XML)
        written.append(path)

    # Background colour: edit the existing definition if there is one,
    # otherwise create it (a duplicate definition would break the build).
    values = os.path.join(RES, "values")
    os.makedirs(values, exist_ok=True)
    found = False
    pattern = re.compile(
        r'(<color\s+name="ic_launcher_background"\s*>)[^<]*(</color>)')
    for fname in sorted(os.listdir(values)):
        if not fname.endswith(".xml"):
            continue
        path = os.path.join(values, fname)
        with open(path) as f:
            text = f.read()
        if pattern.search(text):
            with open(path, "w") as f:
                f.write(pattern.sub(r"\g<1>" + BG_HEX + r"\g<2>", text))
            written.append(path)
            found = True
    if not found:
        path = os.path.join(values, "ic_launcher_background.xml")
        with open(path, "w") as f:
            f.write(BACKGROUND_XML % BG_HEX)
        written.append(path)

    print("wrote %d files" % len(written))
    for p in written:
        print("  " + p)


if __name__ == "__main__":
    main()
