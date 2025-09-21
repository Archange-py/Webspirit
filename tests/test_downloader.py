
from doctest import testmod

import unittest


class TestDownloader(unittest.TestCase):
    # Docstring test
    def test_docstring(self):
        results = testmod(__import__("webspirit.downloader"), verbose=True)

        self.assertFalse(bool(results.failed))

if __name__ == '__main__':
    unittest.main()