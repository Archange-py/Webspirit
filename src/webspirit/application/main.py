
from webspirit.application.desktop import start_window

from webspirit.application.tray import start_tray

from webspirit.application.server import app

from webspirit.config.logger import Logger, DEBUG

import threading

import uvicorn


if __name__ == "__main__":
    def start_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level=DEBUG)

    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=start_tray, daemon=True).start()

    start_window()