from ytload.tools.checktype import ValidatePathOrUrl, CheckType, PathOrURL, StrPath, HyperLink

from ytload.config.constants import PATH_LANGUAGES, PATH_MUSICS_LIST

from os.path import abspath

from doctest import testmod

import unittest


class TestHyperLink(unittest.TestCase):
    def test_docstring(self):
        results = testmod(__import__("ytload.tools.contexterror"), verbose=True)

        self.assertFalse(bool(results.failed))


if __name__ == '__main__':
    unittest.main()