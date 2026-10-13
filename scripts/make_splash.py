"""Add the RISE opening animation to the generated Android project.

Run from the repo root after `npx cap add android`:
    python scripts/make_splash.py

It does three things:
  1. Writes the RISE logo (from assets/icon-only.png) as a drawable the splash can use.
  2. Replaces the generated MainActivity.java with scripts/splash/MainActivity.java,
     which draws the animated overlay on top of the WebView at every app start.
  3. Makes the system launch background black, so the phone does not flash the
     default Capacitor image before the RISE animation starts.

The overlay only sits on top of the live site while it loads. It does not touch the
WebView, Capacitor plugins, login or notifications.
"""
import os
import re
import shutil
import sys

from PIL import Image

SRC = "assets/icon-only.png"
RES = "android/app/src/main/res"
JAVA_DIR = "android/app/src/main/java/com/rise/dailypeak"
JAVA_SRC = "scripts/splash/MainActivity.java"


def main():
    for path in (SRC, JAVA_SRC):
        if not os.path.isfile(path):
            sys.exit("missing " + path)
    if not os.path.isdir(RES):
        sys.exit("missing " + RES + " (run `npx cap add android` first)")
    if not os.path.isdir(JAVA_DIR):
        sys.exit("missing " + JAVA_DIR + " (is the appId still com.rise.dailypeak?)")

    # 1. Logo: crop the black margin, keep the glow, shrink to a sensible size.
    logo = Image.open(SRC).convert("RGB").crop((102, 102, 922, 922)).resize((560, 560), Image.LANCZOS)
    drawable_dir = os.path.join(RES, "drawable-nodpi")
    os.makedirs(drawable_dir, exist_ok=True)
    logo_path = os.path.join(drawable_dir, "rise_logo.png")
    logo.save(logo_path, "PNG")
    print("wrote", logo_path)

    # 2. MainActivity with the animated overlay.
    target = os.path.join(JAVA_DIR, "MainActivity.java")
    shutil.copyfile(JAVA_SRC, target)
    print("wrote", target)

    # 3. Black launch background (only if the template uses the default splash image).
    styles = os.path.join(RES, "values", "styles.xml")
    if os.path.isfile(styles):
        text = open(styles, encoding="utf-8").read()
        new = re.sub(r"@drawable/splash\b", "@android:color/black", text)
        if new != text:
            open(styles, "w", encoding="utf-8").write(new)
            print("set launch background to black in", styles)
        else:
            print("styles.xml has no default splash reference; left unchanged")


if __name__ == "__main__":
    main()
