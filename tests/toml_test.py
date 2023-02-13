import unittest
import toml

TOML = """[ruby]
source.github.user = "ruby"
source.github.tag = "v3_1_3"

[ruby.pkg]
custom = '''
win32/configure.bat --prefix={PREFIX}
nmake install
'''
"""


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

        parsed = toml.loads(TOML)
        print(parsed)


if __name__ == "__main__":
    unittest.main()
