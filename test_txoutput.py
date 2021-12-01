import unittest
from txoutput import TxOutput

TRANSACTION_01_HASH = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8"
TRANSACTION_01_INDEX = 0
TRANSACTION_01_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
#       varint size (33)-^ ^-compressed public key (03) followed by 32 byte x-coordinate---^|^- checksig (172)

tx_with_no_script = TxOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
tx_script_small = TxOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)

class TestTxOutputLittleEndianRead(unittest.TestCase):

    def test_too_short_01(self):
        hex_string = "f"
        val = TxOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == None

    def test_too_short_02(self):
        hex_string = "ff"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == None

    def test_too_short_03(self):
        hex_string = "fff"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == None

    def test_too_short_04(self):
        hex_string = "fffffff"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == None

    def test_extra_characters_01(self):
        hex_string = "ffffffffffffffffffffff"
        val = TxOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val != None

    def test_extra_characters_02(self):
        hex_string = "ffffffffffffffffffffff"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val != None

    def test_extra_characters_03(self):
        hex_string = "ffffffffffffffffffffff"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val != None

    def test_one_byte_little_endian_read_zero(self):
        hex_string = "00"
        val = TxOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 0

    def test_one_byte_little_endian_read_1(self):
        hex_string = "01"
        val = TxOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 1

    def test_one_byte_little_endian_read_255(self):
        hex_string = "ff"
        val = TxOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 255

    def test_two_byte_little_endian_read_256(self):
        # if read as big endian, this would be 1
        hex_string = "0001"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 256

    def test_two_byte_little_endian_read_65281(self):
        # if read as big endian, this would be 511
        hex_string = "01ff"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 65281

    def test_two_byte_little_endian_read_zero(self):
        # min value with two bytes
        hex_string = "0000"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 0

    def test_two_byte_little_endian_read_65535(self):
        # max value with two bytes
        hex_string = "ffff"
        val = TxOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 65535

    def test_four_byte_little_endian_read_16777216(self):
        # if read as big endian, this would be 1
        hex_string = "00000001"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 16777216

    def test_four_byte_little_endian_read_17501197(self):
        # if read as big endian, this would be 218893057
        hex_string = "0d0c0b01"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 17501197

    def test_four_byte_little_endian_read_cafebabe(self):
        # if read as big endian, this would be 3405691582
        hex_string = "cafebabe"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 3199925962

    def test_four_byte_little_endian_read_zero(self):
        # min value with four bytes
        hex_string = "00000000"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 3199925962

    def test_four_byte_little_endian_read_zero(self):
        # max value with four bytes
        hex_string = "ffffffff"
        val = TxOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 4294967295

if __name__ == "__main__":
    unittest.main()