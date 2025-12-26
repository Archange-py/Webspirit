# main.py
import threading
import uvicorn
import server
from tray import setup_tray

if __name__ == "__main__":
    # Démarrer le serveur FastAPI dans un thread
    def start_server():
        uvicorn.run(server.app, host="127.0.0.1", port=8000, log_level="debug")

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    # Démarrer l'icône système (bloquant)
    setup_tray()