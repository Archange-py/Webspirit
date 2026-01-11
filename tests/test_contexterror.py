from doctest import testmod

import unittest


class TestContextError(unittest.TestCase):
    def test_docstring(self):
        results = testmod(__import__("webspirit.classes.tools.contexterror"), verbose=True)

        self.assertFalse(bool(results.failed))


if __name__ == '__main__':
    unittest.main()