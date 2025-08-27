
from doctest import testmod

import unittest


class TestJSONManager(unittest.TestCase):
    # Docstring test
    def test_docstring(self):
        results = testmod(__import__("ytload.tools.jsonmanager"), verbose=True)

        self.assertFalse(bool(results.failed))

if __name__ == '__main__':
    unittest.main()