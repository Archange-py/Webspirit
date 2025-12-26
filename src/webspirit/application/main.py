# main.py
import threading
import uvicorn
from . import server
from . import tray

if __name__ == "__main__":
    # Démarrer le serveur FastAPI dans un thread
    def start_server():
        uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="debug")

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    # Démarrer l'icône système (bloquant)
    tray.setup_tray()