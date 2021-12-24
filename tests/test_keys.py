import unittest
from context import *
from common import *
from keys.ring import NUM_ELLIPTIC_CURVE_POINTS, KeyRing

# -----------------------------------------------------------------
#                            PRIVATE KEYS
# -----------------------------------------------------------------

class TestPrivateKey(unittest.TestCase):

    def test_initialization_with_nonsense_string(self):
        with self.assertRaises(ValueError):
            key_ring = KeyRing("nonsense string")

    def test_initialization_with_empty_string(self):
        with self.assertRaises(ValueError):
            key_ring = KeyRing("")

    def test_initialization_with_string_01(self):
        key_ring = KeyRing("f")
        self.assertEqual(15, key_ring.current())

    def test_initialization_with_string_02(self):
        key_ring = KeyRing("ff")
        self.assertEqual(255, key_ring.current())

    def test_initialization_with_string_03(self):
        key_ring = KeyRing("0xff")
        self.assertEqual(255, key_ring.current())

    def test_initialization_with_string_04(self):
        # zero is not a valid pubkey, should be skipped
        key_ring = KeyRing("0x00")
        self.assertEqual(1, key_ring.current())

    def test_initialization_with_string_less_than_n(self):
        # one less than order of N
        key_ring = KeyRing("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140")
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, key_ring.current())

    def test_initialization_with_string_equal_to_n(self):
        # equal to order of N
        key_ring = KeyRing("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141")
        self.assertEqual(1, key_ring.current())

    def test_initialization_with_value_01(self):
        key_ring = KeyRing(15)
        self.assertEqual(15, key_ring.current())

    def test_initialization_with_value_02(self):
        key_ring = KeyRing(255)
        self.assertEqual(255, key_ring.current())

    def test_initialization_with_value_03(self):
        key_ring = KeyRing(256)
        self.assertEqual(256, key_ring.current())

    def test_initialization_with_value_04(self):
        # zero is not a valid pubkey, should be skipped
        key_ring = KeyRing(0)
        self.assertEqual(1, key_ring.current())

    def test_initialization_with_value_less_than_n(self):
        # one less than order of N
        key_ring = KeyRing(115792089237316195423570985008687907852837564279074904382605163141518161494336)
        self.assertEqual(115792089237316195423570985008687907852837564279074904382605163141518161494336, key_ring.current())

    def test_initialization_with_value_equal_to_n(self):
        # equal to order of N
        key_ring = KeyRing(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual(1, key_ring.current())

    def test_to_string_01(self):
        # zero is not a valid pubkey, should be skipped
        key_ring = KeyRing("0x00")
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", key_ring.__str__())

    def test_to_string_02(self):
        # zero is not a valid pubkey, should be skipped
        key_ring = KeyRing(0)
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", key_ring.__str__())

    def test_to_string_03(self):
        # this will wrap around (order) and increment over 0
        key_ring = KeyRing(115792089237316195423570985008687907852837564279074904382605163141518161494337)
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", key_ring.__str__())

    def test_to_string_04(self):
        key_ring = KeyRing("f0f0f0f0f0f0f0f0")
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", key_ring.__str__())

    def test_reinitialize_from_tostring_01(self):
        key_ring = KeyRing("0")
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", key_ring.__str__())
        key_ring2 = KeyRing(key_ring.__str__())
        self.assertEqual("0000000000000000000000000000000000000000000000000000000000000001", key_ring2.__str__())
        self.assertEqual(key_ring.current(), key_ring2.current())

    def test_reinitialize_from_tostring_02(self):
        key_ring = KeyRing("f0f0f0f0f0f0f0f0")
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", key_ring.__str__())
        key_ring2 = KeyRing(key_ring.__str__())
        self.assertEqual("000000000000000000000000000000000000000000000000f0f0f0f0f0f0f0f0", key_ring2.__str__())
        self.assertEqual(key_ring.current(), key_ring2.current())

    def test_next_01(self):
        key_ring = KeyRing("0000000000000000000000000000000000000000000000000000000000000001")
        self.assertEqual(1, key_ring.current())
        key_ring.next()
        self.assertEqual(2, key_ring.current())

    def test_next_02(self):
        key_ring = KeyRing("fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364140")
        self.assertEqual(NUM_ELLIPTIC_CURVE_POINTS - 1, key_ring.current())
        key_ring.next()
        self.assertEqual(1, key_ring.current())

    def test_next_03(self):
        key_ring = KeyRing("0xff")
        self.assertEqual(255, key_ring.current())
        key_ring.next()
        self.assertEqual(256, key_ring.current())
        key_ring.next()
        self.assertEqual(257, key_ring.current())
        key_ring.next()
        self.assertEqual(258, key_ring.current())

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