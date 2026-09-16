import unittest

from app import target_value


class TargetValueTests(unittest.TestCase):
    def test_target_value(self):
        self.assertEqual(target_value(), 1)
