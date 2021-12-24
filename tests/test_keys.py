import unittest
from context import *
from common import *
from keys import *
from keys.private import NUM_ELLIPTIC_CURVE_POINTS, PrivateKey

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
        self.assertEqual(15, private_key.value())

    def test_initialization_with_string_02(self):
        private_key = PrivateKey("ff")
        self.assertEqual(255, private_key.value())

    def test_initialization_with_string_03(self):
        private_key = PrivateKey("0xff")
        self.assertEqual(255, private_key.value())

    def test_initialization_with_string_04(self):
        # zero is not a valid pubkey, should be skipped
        private_key = PrivateKey("0x00")
        self.assertEqual(1, private_key.value())

    def test_initialization_with_string_less_than_n(self):
        # one less than order of N
        private_key = PrivateKey("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140")
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, private_key.value())

    def test_initialization_with_string_equal_to_n(self):
        # equal to order of N
        private_key = PrivateKey("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141")
        self.assertEqual(1, private_key.value())

    def test_initialization_with_value_01(self):
        private_key = PrivateKey(15)
        self.assertEqual(15, private_key.value())

    def test_initialization_with_value_02(self):
        private_key = PrivateKey(255)
        self.assertEqual(255, private_key.value())

    def test_initialization_with_value_03(self):
        private_key = PrivateKey(256)
        self.assertEqual(256, private_key.value())

    def test_initialization_with_value_04(self):
        # zero is not a valid pubkey, should be skipped
        private_key = PrivateKey(0)
        self.assertEqual(1, private_key.value())

    def test_initialization_with_value_less_than_n(self):
        # one less than order of N
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494336)
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, private_key.value())

    def test_initialization_with_value_equal_to_n(self):
        # equal to order of N
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual(1, private_key.value())

    def test_to_string_01(self):
        # zero is not a valid pubkey, should be skipped
        private_key = PrivateKey("0x00")
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", private_key.__str__())

    def test_to_string_02(self):
        # zero is not a valid pubkey, should be skipped
        private_key = PrivateKey(0)
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", private_key.__str__())

    def test_to_string_03(self):
        # this will wrap around (order) and increment over 0
        private_key = PrivateKey(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", private_key.__str__())

    def test_to_string_04(self):
        private_key = PrivateKey("f0f0f0f0f0f0f0f0")
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key.__str__())

    def test_reinitialize_from_tostring_01(self):
        private_key = PrivateKey("0")
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", private_key.__str__())
        private_key2 = PrivateKey(private_key.__str__())
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", private_key2.__str__())
        self.assertEqual(private_key.value(), private_key2.value())

    def test_reinitialize_from_tostring_02(self):
        private_key = PrivateKey("f0f0f0f0f0f0f0f0")
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key.__str__())
        private_key2 = PrivateKey(private_key.__str__())
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", private_key2.__str__())
        self.assertEqual(private_key.value(), private_key2.value())

    def test_next_01(self):
        private_key = PrivateKey("0000000000000000000000000000000000000000000000000000000000000001")
        self.assertEqual(1, private_key.value())
        private_key.next()
        self.assertEqual(2, private_key.value())

    def test_next_02(self):
        private_key = PrivateKey("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140")
        self.assertEqual(NUM_ELLIPTIC_CURVE_POINTS - 1, private_key.value())
        private_key.next()
        self.assertEqual(1, private_key.value())

    def test_next_03(self):
        private_key = PrivateKey("0xff")
        self.assertEqual(255, private_key.value())
        private_key.next()
        self.assertEqual(256, private_key.value())
        private_key.next()
        self.assertEqual(257, private_key.value())
        private_key.next()
        self.assertEqual(258, private_key.value())

# class TestPublicKey(unittest.TestCase):

#     """
#     $ python -m secp256k1 privkey -p
#     e7fa4c2e2c30b2e44da1612a1fc5506de802ee602dfad922e3e47681c89cbc3b
#     Public key: 032f3037fed32854cbfdc791ee0b1a2c21460beb399737a99e482ef0d5e7e5ea58

#     $ echo -n e7fa4c2e2c30b2e44da1612a1fc5506de802ee602dfad922e3e47681c89cbc3b | bx ec-to-public
#     032f3037fed32854cbfdc791ee0b1a2c21460beb399737a99e482ef0d5e7e5ea58
#     """

if __name__ == "__main__":
    unittest.main()