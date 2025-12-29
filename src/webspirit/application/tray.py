from PIL import Image

import webbrowser
import pystray
import sys

URL: str = "http://127.0.0.1:8000"

def start_tray():
    image = Image.new("RGB", (64, 64), color=(99, 102, 241))
    menu = pystray.Menu(
        pystray.MenuItem("Ouvrir", lambda _: webbrowser.open(URL)),
        pystray.MenuItem("Quitter", lambda _: sys.exit())
    )
    pystray.Icon("Webspirit", image, "Local Webspirit", menu).run()
