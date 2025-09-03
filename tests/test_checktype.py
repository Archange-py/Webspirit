from webspirit.tools.checktype import ValidatePathOrUrl, CheckType, PathOrURL, StrPath, HyperLink

from webspirit.config.constants import PATH_LANGUAGES, PATH_MUSICS_LIST

from os.path import abspath

from doctest import testmod

from types import NoneType

import unittest


# PATH_LANGUAGES, PATH_MUSICS_LIST = StrPath(PATH_LANGUAGES).relpath(), StrPath(PATH_MUSICS_LIST).relpath()

class TestHyperLink(unittest.TestCase):
    def test_is_url(self):
        self.assertTrue(HyperLink.is_url('https://youtu.be/kO8Nj09525U'))
        self.assertTrue(HyperLink.is_url(HyperLink('https://youtu.be/kO8Nj09525U')))

        self.assertFalse(HyperLink.is_url('Hello Word!'))

    def test_introspection(self):
        url = HyperLink('https://youtu.be/kO8Nj09525U')

        self.assertEqual(repr(url), "HyperLink('https://youtu.be/kO8Nj09525U')")

        with self.assertRaises(TypeError):
            HyperLink(string='https://')


class TestStrPath(unittest.TestCase):
    def test_is_path(self):
        self.assertTrue(StrPath.is_path(PATH_LANGUAGES))
        self.assertTrue(StrPath.is_path(str(PATH_LANGUAGES)))
        self.assertTrue(StrPath.is_path(StrPath(PATH_LANGUAGES)))

        self.assertTrue(StrPath.is_path(abspath(r'./src/webspirit/data/musics.csv'), suffix=('csv', 'txt')))
        self.assertTrue(StrPath.is_path(abspath(r'./src/webspirit/data/musics.csv'), suffix='csv'))
        self.assertTrue(StrPath.is_path(abspath(r'./src/webspirit/data'), dir=True))

    def _test_methods(self):
        self.assertTupleEqual(
            (StrPath(PATH_LANGUAGES).absolute(), StrPath(PATH_LANGUAGES).relpath(), StrPath(PATH_LANGUAGES).dirname()),
            (StrPath(r'C:\Users\Blondel\Documents\Programmation\Langage\Python\Projects\PyForge\plugins\Webspirit\src\webspirit\data\languages.csv'),
             StrPath(r'.\src\webspirit\data\languages.csv'),
             StrPath(r'C:\Users\Blondel\Documents\Programmation\Langage\Python\Projects\PyForge\plugins\Webspirit\src\webspirit\data'))
        )

    def _test_introspection(self):
        path = StrPath(PATH_LANGUAGES)

        self.assertEqual(repr(path.relpath()), "StrPath('src\webspirit\data\languages.csv')")

        with self.assertRaises(TypeError):
            StrPath(string=abspath(r'./src/webspirit/data/musics.txt'))

class BookOfLink:
    @CheckType()
    def append_url1(self, url: HyperLink, nbr: int) -> tuple[HyperLink, int]:
        return type(url), type(nbr)

    @CheckType()
    def append_url2(self, url: str, nbr: int | None = None) -> tuple[str, int | None]:
        return type(url), type(nbr)

    @CheckType('url', 'nbr', 'string')
    def append_url3(self, url: HyperLink, nbr: int, string: str) -> tuple[HyperLink, int, str]:
        return type(url), type(nbr), type(string)

    @CheckType('path')
    def append_path(self, path: StrPath) -> StrPath:
        return type(path)

    @ValidatePathOrUrl('link')
    def append1(self, link: PathOrURL = "https://youtu.be/_0Pf48RqSsg") -> PathOrURL:
        return type(link)

    @ValidatePathOrUrl('url')
    def append2(self, url: HyperLink) -> HyperLink:
        return type(url)

@CheckType()
def append_url1(url: HyperLink, nbr: int) -> tuple[HyperLink, int]:
    return type(url), type(nbr)

@CheckType()
def append_url2(url: str, nbr: int | None = None) -> tuple[str, int | None]:
    return type(url), type(nbr)

@CheckType('url', 'nbr', 'string')
def append_url3(url: HyperLink, nbr: int, string: str) -> tuple[HyperLink, int, str]:
    return type(url), type(nbr), type(string)

@CheckType('path')
def append_path(path: StrPath) -> StrPath:
    return type(path)

@ValidatePathOrUrl('link')
def append1(link: PathOrURL = "https://youtu.be/_0Pf48RqSsg") -> PathOrURL:
    return type(link)

@ValidatePathOrUrl('url')
def append2(url: HyperLink) -> HyperLink:
    return type(url)


class TestCheckType(unittest.TestCase):
    def test_docstring(self):
        results = testmod(__import__("webspirit.tools.checktype"), verbose=True)

        self.assertFalse(bool(results.failed))

    def test_class_book_of_link(self):
        book = BookOfLink()

        self.assertTupleEqual(book.append_url1('https://youtu.be/1V_xRb0x9aw', 7), (HyperLink, int))
        self.assertTupleEqual(book.append_url2('https://youtu.be/1V_xRb0x9aw', '7'), (str, int))
        self.assertTupleEqual(book.append_url2('https://youtu.be/1V_xRb0x9aw'), (str, NoneType))
        self.assertTupleEqual(book.append_url3('https://youtu.be/1V_xRb0x9aw', '7', 190), (HyperLink, int, str))
        self.assertEqual(book.append_path(str(PATH_MUSICS_LIST)), StrPath)

        with self.assertRaises(ValueError):
            book.append_path(abspath(r'./src/webspirit/data/musics.txt'))

    def test_function_book_of_link(self):
        self.assertTupleEqual(append_url1('https://youtu.be/1V_xRb0x9aw', 7), (HyperLink, int))
        self.assertTupleEqual(append_url2('https://youtu.be/1V_xRb0x9aw', '7'), (str, int))
        self.assertTupleEqual(append_url2('https://youtu.be/1V_xRb0x9aw'), (str, NoneType))
        self.assertTupleEqual(append_url3('https://youtu.be/1V_xRb0x9aw', '7', 190), (HyperLink, int, str))
        self.assertEqual(append_path(str(PATH_MUSICS_LIST)), StrPath)

        with self.assertRaises(ValueError):
            append_path(abspath(r'./src/webspirit/data/musics.txt'))

class ValidatePathOrUrl(unittest.TestCase):
    def test_class_book_of_link(self):
        book = BookOfLink()

        self.assertEqual(book.append1(str(PATH_MUSICS_LIST)), StrPath)
        self.assertEqual(book.append2("https://youtu.be/1V_xRb0x9aw"), HyperLink)

    def test_function_book_of_link(self):
        self.assertEqual(append1(str(PATH_MUSICS_LIST)), StrPath)
        self.assertEqual(append2("https://youtu.be/1V_xRb0x9aw"), HyperLink)

if __name__ == '__main__':
    unittest.main()