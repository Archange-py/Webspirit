# tray.py
import webbrowser
import pystray
from PIL import Image, ImageDraw

def create_image():
    """
    Crée dynamiquement une icône simple (exemple rouge sur fond blanc).
    On peut aussi charger depuis un fichier.
    """
    img = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([(8, 8), (56, 56)], fill='red')
    return img

def open_web_ui(icon, item):
    """
    Ouvre l'interface web dans le navigateur par défaut.
    """
    webbrowser.open("http://127.0.0.1:8000")

def setup_tray():
    """
    Initialise l'icône dans la barre système avec un menu.
    """
    image = create_image()
    menu = (
        pystray.MenuItem("Ouvrir l'interface web", open_web_ui),
        pystray.MenuItem("Quitter", lambda icon, item: icon.stop())
    )
    icon = pystray.Icon("BookmarksApp", image, "BookmarksApp", menu)
    icon.run()