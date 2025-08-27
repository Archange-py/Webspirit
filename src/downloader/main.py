from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from app.plugin_interface import PluginInterface

class DemoPlugin(PluginInterface):
    def __init__(self):
        super().__init__()
        self.name = "Downloader"
        self.icon_path = None

    def get_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Hello Word!"))
        return widget