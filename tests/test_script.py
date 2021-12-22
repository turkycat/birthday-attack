import unittest
from context import *
from common import *
from transactions.tx import *
from transactions.script import *

class TestScriptLittleEndianRead(unittest.TestCase):

    def test_too_short_01(self):
        hex_string = "f"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            val = decode_hex_bytes_little_endian(1, hex_string)

    def test_too_short_02(self):
        hex_string = "ff"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            val = decode_hex_bytes_little_endian(2, hex_string)

    def test_too_short_03(self):
        hex_string = "fff"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            val = decode_hex_bytes_little_endian(2, hex_string)

    def test_too_short_04(self):
        hex_string = "fffffff"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            val = decode_hex_bytes_little_endian(4, hex_string)

    def test_extra_characters_01(self):
        hex_string = "ffffffffffffffffffffff"
        val = decode_hex_bytes_little_endian(1, hex_string)
        self.assertNotEqual(val, None)

    def test_extra_characters_02(self):
        hex_string = "ffffffffffffffffffffff"
        val = decode_hex_bytes_little_endian(2, hex_string)
        self.assertNotEqual(val, None)

    def test_extra_characters_03(self):
        hex_string = "ffffffffffffffffffffff"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertNotEqual(val, None)

    def test_one_byte_little_endian_read_zero(self):
        hex_string = "00"
        val = decode_hex_bytes_little_endian(1, hex_string)
        self.assertEqual(val, 0)

    def test_one_byte_little_endian_read_1(self):
        hex_string = "01"
        val = decode_hex_bytes_little_endian(1, hex_string)
        self.assertEqual(val, 1)

    def test_one_byte_little_endian_read_255(self):
        hex_string = "ff"
        val = decode_hex_bytes_little_endian(1, hex_string)
        self.assertEqual(val, 255)

    def test_two_byte_little_endian_read_256(self):
        # if read as big endian, this would be 1
        hex_string = "0001"
        val = decode_hex_bytes_little_endian(2, hex_string)
        self.assertEqual(val, 256)

    def test_two_byte_little_endian_read_65281(self):
        # if read as big endian, this would be 511
        hex_string = "01ff"
        val = decode_hex_bytes_little_endian(2, hex_string)
        self.assertEqual(val, 65281)

    def test_two_byte_little_endian_read_zero(self):
        # min value with two bytes
        hex_string = "0000"
        val = decode_hex_bytes_little_endian(2, hex_string)
        self.assertEqual(val, 0)

    def test_two_byte_little_endian_read_65535(self):
        # max value with two bytes
        hex_string = "ffff"
        val = decode_hex_bytes_little_endian(2, hex_string)
        self.assertEqual(val, 65535)

    def test_four_byte_little_endian_read_16777216(self):
        # if read as big endian, this would be 1
        hex_string = "00000001"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertEqual(val, 16777216)

    def test_four_byte_little_endian_read_17501197(self):
        # if read as big endian, this would be 218893057
        hex_string = "0d0c0b01"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertEqual(val, 17501197)

    def test_four_byte_little_endian_read_cafebabe(self):
        # if read as big endian, this would be 3405691582
        hex_string = "cafebabe"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertEqual(val, 3199925962)

    def test_four_byte_little_endian_read_zero(self):
        # min value with four bytes
        hex_string = "00000000"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertEqual(val, 3199925962)

    def test_four_byte_little_endian_read_zero(self):
        # max value with four bytes
        hex_string = "ffffffff"
        val = decode_hex_bytes_little_endian(4, hex_string)
        self.assertEqual(val, 4294967295)

class TestScriptDecode(unittest.TestCase):
    

# -----------------------------------------------------------------
#                 ERRORS AND UNEXPECTED VALUES
# -----------------------------------------------------------------

    # script is None
    def test_script_none(self):
        decoded_script = decode_script(None)
        self.assertIsNone(decoded_script)

    # script is empty
    def test_script_empty(self):
        serialized_script = ""
        decoded_script = decode_script(serialized_script)
        self.assertIsNone(decoded_script)

    # script is odd length
    def test_script_odd_length(self):
        serialized_script = "764"
        with self.assertRaises(ScriptDecodingException):
            decoded_script = decode_script(serialized_script)

    # script is shorter than expected with data
    def test_script_shorter_than_expected_01(self):
        # should be 1 byte to follow
        serialized_script = "01"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            decoded_script = decode_script(serialized_script)

    # script is shorter than expected with data
    def test_script_shorter_than_expected_02(self):
        # should be 1 byte to follow, but only 1 char (doesn't even read the data byte- fails because odd)
        serialized_script = "01f"
        with self.assertRaises(ScriptDecodingException):
            decoded_script = decode_script(serialized_script)

    # script is shorter than expected with data
    def test_script_shorter_than_expected_03(self):
        # should be 6 bytes to follow, IE 12 characters. Only has 6 characters. 
        serialized_script = "06123456"
        with self.assertRaises(ScriptLengthShorterThanExpected):
            decoded_script = decode_script(serialized_script)

# -----------------------------------------------------------------
#                            OPCODES
# -----------------------------------------------------------------

    # script is single opcodes 1
    def test_script_opcodes_only_01(self):
        serialized_script = "A0"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "greaterthan"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    # script is single opcodes 2
    def test_script_opcodes_only_02(self):
        serialized_script = "AA"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "hash256"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    # script is single opcodes 3
    def test_script_opcodes_only_03(self):
        serialized_script = "D4"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "reserved_212"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    # script is single opcodes 4
    def test_script_opcodes_all(self):
        # generated. every hex value in range [79, 255] (non-data opcodes)
        # seq 79 255 | while read n; do printf "%02x" $n; done
        serialized_script = "4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_negative_1","reserved_80","push_positive_1","push_positive_2","push_positive_3",
            "push_positive_4","push_positive_5","push_positive_6","push_positive_7","push_positive_8",
            "push_positive_9","push_positive_10","push_positive_11","push_positive_12","push_positive_13",
            "push_positive_14","push_positive_15","push_positive_16","nop","reserved_98","if_","notif",
            "disabled_verif","disabled_vernotif","else_","endif","verify","return_","toaltstack",
            "fromaltstack","drop2","dup2","dup3","over2","rot2","swap2","ifdup","depth","drop",
            "dup","nip","over","pick","roll","rot","swap","tuck","disabled_cat","disabled_substr",
            "disabled_left","disabled_right","size","disabled_invert","disabled_and","disabled_or",
            "disabled_xor","equal","equalverify","reserved_137","reserved_138","add1","sub1","disabled_mul2",
            "disabled_div2","negate","abs","not_","nonzero","add","sub","disabled_mul","disabled_div",
            "disabled_mod","disabled_lshift","disabled_rshift","booland","boolor","numequal","numequalverify",
            "numnotequal","lessthan","greaterthan","lessthanorequal","greaterthanorequal","min","max",
            "within","ripemd160","sha1","sha256","hash160","hash256","codeseparator","checksig","checksigverify",
            "checkmultisig","checkmultisigverify","nop1","checklocktimeverify","checksequenceverify","nop4",
            "nop5","nop6","nop7","nop8","nop9","nop10","reserved_186","reserved_187","reserved_188","reserved_189",
            "reserved_190","reserved_191","reserved_192","reserved_193","reserved_194","reserved_195",
            "reserved_196","reserved_197","reserved_198","reserved_199","reserved_200","reserved_201",
            "reserved_202","reserved_203","reserved_204","reserved_205","reserved_206","reserved_207",
            "reserved_208","reserved_209","reserved_210","reserved_211","reserved_212","reserved_213",
            "reserved_214","reserved_215","reserved_216","reserved_217","reserved_218","reserved_219",
            "reserved_220","reserved_221","reserved_222","reserved_223","reserved_224","reserved_225",
            "reserved_226","reserved_227","reserved_228","reserved_229","reserved_230","reserved_231",
            "reserved_232","reserved_233","reserved_234","reserved_235","reserved_236","reserved_237",
            "reserved_238","reserved_239","reserved_240","reserved_241","reserved_242","reserved_243",
            "reserved_244","reserved_245","reserved_246","reserved_247","reserved_248","reserved_249",
            "reserved_250","reserved_251","reserved_252","reserved_253","reserved_254","reserved_255"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    # script is data of various lengths
    def test_script_various_data_lengths_00(self):
        serialized_script = "00"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_0"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_various_data_lengths_01(self):
        serialized_script = "01ff"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_1", "ff"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_various_data_lengths_02(self):
        serialized_script = "01aaff"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_1", "aa", "reserved_255"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_various_data_lengths_03(self):
        serialized_script = "02aaff"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_2", "aaff"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_various_data_lengths_04(self):
        serialized_script = "10000102030405060708090A0B0C0D0E10"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_16", "000102030405060708090A0B0C0D0E10"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_various_data_lengths_05(self):
        serialized_script = "0600010203040510000102030405060708090A0B0C0D0E10"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_6", "000102030405", "push_size_16", "000102030405060708090A0B0C0D0E10"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_data_lengths_uncompressed_pubkey(self):
        serialized_script = "4104aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0ac"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_65", UNCOMPRESSED_PUBLIC_KEY, "checksig"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_data_lengths_compressed_pubkey(self):
        serialized_script = "210214f296079b181ab76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420ac"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "push_size_33", COMPRESSED_PUBLIC_KEY_01, "checksig"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

    def test_script_data_lengths_pubkeyhash(self):
        serialized_script = "76a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac"
        decoded_script = decode_script(serialized_script)
        correct_decoded_script = [
            "dup", "hash160", "push_size_20", PUBKEYHASH, "equalverify", "checksig"
        ]
        self.assertEqual(decoded_script, correct_decoded_script)

if __name__ == "__main__":
    unittest.main()