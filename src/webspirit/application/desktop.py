import webview
import webbrowser

URL = "http://127.0.0.1:8000"

def start_window():
    window = webview.create_window(
        title="Bookmarks locaux",
        url=URL,
        width=1200,
        height=800
    )

    def open_browser(*args, **kwargs):
        webbrowser.open(URL)

    webview.start(open_browser, window, debug=False)
