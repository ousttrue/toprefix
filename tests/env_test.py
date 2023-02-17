import unittest
from toprefix.envman import EnvMan
from toprefix import vcenv


class TestEnv(unittest.TestCase):
    def test_upper(self):
        vcenv.get_env({})


if __name__ == "__main__":
    unittest.main()
