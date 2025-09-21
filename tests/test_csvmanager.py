from webspirit.tools.csvmanager import CSVManager, Music

from webspirit.tools.checktype import HyperLink

from doctest import testmod

import unittest


class TestMusic(unittest.TestCase):
    def test_music(self):
        music = Music('https://youtu.be/kO8Nj09525U')

        self.assertEqual(type(music.youtube_url), HyperLink)
        self.assertEqual(repr(music), "Music(youtube_url=HyperLink('https://youtu.be/kO8Nj09525U'), path=None, extension=None, type=None, spotify_url=None, picture=None, meta=None)")

        youtube_url, path, extension, _type, spotify_url, picture, meta = music

        self.assertTupleEqual((youtube_url, path, extension, _type, spotify_url, picture, meta), ((HyperLink('https://youtu.be/kO8Nj09525U'), None, None, None, None, None, None)))

class TestCSVManager(unittest.TestCase):
    def test_docstring(self):
        results = testmod(__import__("webspirit.tools.csvmanager"), verbose=True)

        self.assertFalse(bool(results.failed))


if __name__ == '__main__':
    unittest.main()