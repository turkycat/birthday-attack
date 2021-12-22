import unittest
from context import *
from common import *
from keys import *
from keys.private import PrivateKey

# -----------------------------------------------------------------
#                            PRIVATE KEYS
# -----------------------------------------------------------------

class TestPrivateKey(unittest.TestCase):

    def test_initialization_with_nonsense_string(self):
        with self.assertRaises(ValueError):
            private_key = PrivateKey("nonsense string")

    def test_initialization_with_empty_string(self):
        with self.assertRaises(ValueError):
            private_key = PrivateKey("")

    def test_initialization_with_string_01(self):
        private_key = PrivateKey("f")
        self.assertEqual(15, private_key.value)

    def test_initialization_with_string_02(self):
        private_key = PrivateKey("ff")
        self.assertEqual(255, private_key.value)

    def test_initialization_with_string_03(self):
        private_key = PrivateKey("0xff")
        self.assertEqual(255, private_key.value)

    def test_initialization_with_string_04(self):
        private_key = PrivateKey("0x00")
        self.assertEqual(0, private_key.value)

    def test_initialization_with_string_less_than_n(self):
        # one less than order of N
        private_key = PrivateKey("0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140")
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, private_key.value)

    def test_initialization_with_string_equal_to_n(self):
        # equal to order of N
        private_key = PrivateKey("0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141")
        self.assertEqual(0, private_key.value)

    def test_initialization_with_value_01(self):
        private_key = PrivateKey(15)
        self.assertEqual(15, private_key.value)

    def test_initialization_with_value_02(self):
        private_key = PrivateKey(255)
        self.assertEqual(255, private_key.value)

    def test_initialization_with_value_03(self):
        private_key = PrivateKey(256)
        self.assertEqual(256, private_key.value)

    def test_initialization_with_value_04(self):
        private_key = PrivateKey(0)
        self.assertEqual(0, private_key.value)

    def test_initialization_with_value_less_than_n(self):
        # one less than order of N
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494336)
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, private_key.value)

    def test_initialization_with_value_equal_to_n(self):
        # equal to order of N
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual(0, private_key.value)

    def test_to_string_01(self):
        private_key = PrivateKey("0x00")
        self.assertEqual("0x0000000000000000000000000000000000000000000000000000000000000000", private_key.__str__())

    def test_to_string_02(self):
        private_key = PrivateKey(0)
        self.assertEqual("0x0000000000000000000000000000000000000000000000000000000000000000", private_key.__str__())

    def test_to_string_03(self):
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual("0x0000000000000000000000000000000000000000000000000000000000000000", private_key.__str__())

    def test_to_string_04(self):
        private_key = PrivateKey("f0f0f0f0f0f0f0f0")
        self.assertEqual("0x000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key.__str__())

    def test_reinitialize_from_tostring_01(self):
        private_key = PrivateKey("0")
        self.assertEqual("0x0000000000000000000000000000000000000000000000000000000000000000", private_key.__str__())
        private_key2 = PrivateKey(private_key.__str__())
        self.assertEqual("0x0000000000000000000000000000000000000000000000000000000000000000", private_key2.__str__())
        self.assertEqual(private_key.value, private_key2.value)

    def test_reinitialize_from_tostring_02(self):
        private_key = PrivateKey("f0f0f0f0f0f0f0f0")
        self.assertEqual("0x000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key.__str__())
        private_key2 = PrivateKey(private_key.__str__())
        self.assertEqual("0x000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key2.__str__())
        self.assertEqual(private_key.value, private_key2.value)