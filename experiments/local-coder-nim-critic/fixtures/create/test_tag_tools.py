import unittest
from tag_tools import normalize_tag

class TagToolsTests(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(normalize_tag("Hello World"), "hello-world")

    def test_separators(self):
        self.assertEqual(normalize_tag(" A__B!! C "), "a-b-c")

    def test_digits(self):
        self.assertEqual(normalize_tag("Version 2.0"), "version-2-0")

    def test_empty(self):
        self.assertEqual(normalize_tag("***"), "")
