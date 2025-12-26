from webspirit.config.logger import debug, info, error, warning, critical

from webspirit.classes.tools.jsonmanager import JSONManager

from webspirit.classes.tools.csvmanager import StrPath

from webspirit.classes.tools.contexterror import ecm

from webspirit.config.constants import (
    HOME_DIR, DIR_TMP
)


EDGE: str = 'EDGE'

# Asynchrone ???

class Bookmarks(JSONManager):
    def __init__(self, navigator: str | None = None):
        self.navigator: str = self.find_navigator() if navigator is None else navigator
        self.path: StrPath = self.load_bookmarks()

    def find_navigator(self) -> str:
        return EDGE

    def get_bookmarks(self) -> StrPath:
        edge_path = StrPath(HOME_DIR / "AppData/Local/Microsoft/Edge/User Data/Default/Bookmarks")

        return edge_path

    def load_bookmarks(self) -> StrPath:
        navigator_path = self.get_bookmarks()
        local_path = StrPath(DIR_TMP / r"Bookmarks.json", exist=False)

        with ecm("An error was occurred when the copy of the Bookmarks system file beginning"):
            with navigator_path.open('r', encoding='UTF-8') as file:
                content: str = file.read()

            with local_path.open('w', encoding='UTF-8') as file:
                file.write(content)

        return local_path
