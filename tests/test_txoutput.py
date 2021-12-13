import unittest
from context import *
from utxo.TXOutput import *

TRANSACTION_01_HASH = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8"
TRANSACTION_01_INDEX = 0
TRANSACTION_01_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
#       varint size (33)-^ ^-compressed public key (03) followed by 32 byte x-coordinate---^|^- checksig (172)

tx_with_no_script = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
tx_script_small = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)

class TestTXOutputLittleEndianRead(unittest.TestCase):

    def test_too_short_01(self):
        hex_string = "f"
        val = TXOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == None

    def test_too_short_02(self):
        hex_string = "ff"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == None

    def test_too_short_03(self):
        hex_string = "fff"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == None

    def test_too_short_04(self):
        hex_string = "fffffff"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == None

    def test_extra_characters_01(self):
        hex_string = "ffffffffffffffffffffff"
        val = TXOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val != None

    def test_extra_characters_02(self):
        hex_string = "ffffffffffffffffffffff"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val != None

    def test_extra_characters_03(self):
        hex_string = "ffffffffffffffffffffff"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val != None

    def test_one_byte_little_endian_read_zero(self):
        hex_string = "00"
        val = TXOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 0

    def test_one_byte_little_endian_read_1(self):
        hex_string = "01"
        val = TXOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 1

    def test_one_byte_little_endian_read_255(self):
        hex_string = "ff"
        val = TXOutput.decode_hex_bytes_little_endian(1, hex_string)
        assert val == 255

    def test_two_byte_little_endian_read_256(self):
        # if read as big endian, this would be 1
        hex_string = "0001"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 256

    def test_two_byte_little_endian_read_65281(self):
        # if read as big endian, this would be 511
        hex_string = "01ff"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 65281

    def test_two_byte_little_endian_read_zero(self):
        # min value with two bytes
        hex_string = "0000"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 0

    def test_two_byte_little_endian_read_65535(self):
        # max value with two bytes
        hex_string = "ffff"
        val = TXOutput.decode_hex_bytes_little_endian(2, hex_string)
        assert val == 65535

    def test_four_byte_little_endian_read_16777216(self):
        # if read as big endian, this would be 1
        hex_string = "00000001"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 16777216

    def test_four_byte_little_endian_read_17501197(self):
        # if read as big endian, this would be 218893057
        hex_string = "0d0c0b01"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 17501197

    def test_four_byte_little_endian_read_cafebabe(self):
        # if read as big endian, this would be 3405691582
        hex_string = "cafebabe"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 3199925962

    def test_four_byte_little_endian_read_zero(self):
        # min value with four bytes
        hex_string = "00000000"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 3199925962

    def test_four_byte_little_endian_read_zero(self):
        # max value with four bytes
        hex_string = "ffffffff"
        val = TXOutput.decode_hex_bytes_little_endian(4, hex_string)
        assert val == 4294967295

class TextTXOutputDetermineScriptType(unittest.TestCase):

    # script is None
    def test_invalid_script_none(self):
        test_script = None
        assert ScriptType.NONE == TXOutput.determine_script_type(test_script)

    # script is empty list
    def test_invalid_script_empty_list(self):
        test_script = []
        assert ScriptType.NONE == TXOutput.determine_script_type(test_script)

    # -----------------------------------------------------------------
    #                             P2PK
    # -----------------------------------------------------------------

    # valid P2PK w/ uncompressed public key
    def test_valid_p2pk_uncompressed_key(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)

    # valid P2PK w/ compressed public key 1
    def test_valid_p2pk_compressed_key_01(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)

    # valid P2PK w/ compressed public key 2
    def test_valid_p2pk_compressed_key_02(self):
        test_script = ["push_size_33", "03831cfea00b5cfcd97a12fd14b469d9385140d187d2bd8add9a1044685db9552b", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)

    # invalid P2PK w/ uncompressed public key (too long)
    def test_invalid_p2pk_uncompressed_key_too_long(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b123d5043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK w/ uncompressed public key (too short)
    def test_invalid_p2pk_uncompressed_key_too_short(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a116575b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK w/ compressed public key (too long)
    def test_invalid_p2pk_compressed_key_too_long(self):
        test_script = ["push_size_33", "0214f296079b181abd76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK w/ compressed public key (too short)
    def test_invalid_p2pk_compressed_key_too_short(self):
        test_script = ["push_size_33", "03831cfea00b5cfcd9a12fd14b469d9385140d187d2bd8add9a1044685db9552b", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with incorrect first opcode
    def test_invalid_p2pk_compressed_key_incorect_opcode_01(self):
        test_script = ["push_size_63", "0214f296079b181ab76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with incorrect last opcode
    def test_invalid_p2pk_compressed_key_incorect_opcode_02(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksigverify"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with missing key
    def test_invalid_p2pk_compressed_key_missing(self):
        test_script = ["push_size_33", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with empty key
    def test_invalid_p2pk_compressed_key_empty(self):
        test_script = ["push_size_33", "", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with invalid chars in key 1
    def test_invalid_p2pk_compressed_key_invalid_chars_01(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8hello1d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PK with invalid chars in key 2
    def test_invalid_p2pk_compressed_key_invalid_chars_02(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8ba5b#1d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
        
    # script is empty list
    def test_invalid_script_list_too_short(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # script is empty list
    def test_invalid_script_list_too_long(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # -----------------------------------------------------------------
    #                             P2PKH
    # -----------------------------------------------------------------
    
    # valid P2PKH
    def test_valid_p2pkh(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
        
    # invalid P2PKH with missing hash
    def test_invalid_p2pkh_missing_hash(self):
        test_script = ["dup", "hash160", "push_size_20", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PKH with empty hash
    def test_invalid_p2pkh_empty_hash(self):
        test_script = ["dup", "hash160", "push_size_20", "", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2PKH with key too short
    def test_invalid_p2pkh_key_too_short(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9e60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2PKH with key too long
    def test_invalid_p2pkh_key_too_long(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9bed60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PKH with invalid chars in key 1
    def test_invalid_p2pkh_invalid_chars_01(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871fhellofb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2PKH with invalid chars in key 2
    def test_invalid_p2pkh_invalid_chars_02(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c8#1f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2PKH with missing checksig
    def test_invalid_p2pkh_list_too_short(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2PKH with double checksig
    def test_invalid_p2pkh_list_too_long(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig", "checksig"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # -----------------------------------------------------------------
    #                             P2SH
    # -----------------------------------------------------------------
    
    # valid P2SH
    def test_valid_p2sh(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)
        
    # invalid P2SH with missing hash
    def test_invalid_p2sh_missing_hash(self):
        test_script = ["hash160", "push_size_20", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2SH with empty hash
    def test_invalid_p2sh_empty_hash(self):
        test_script = ["hash160", "push_size_20", "", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2SH with key too short
    def test_invalid_p2sh_key_too_short(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07ac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2SH with key too long
    def test_invalid_p2sh_key_too_long(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07adac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2SH with invalid chars in key 1
    def test_invalid_p2sh_invalid_chars_01(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aachelloebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # invalid P2SH with invalid chars in key 2
    def test_invalid_p2sh_invalid_chars_02(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac761$#ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2SH with missing checksig
    def test_invalid_p2sh_list_too_short(self):
        test_script = ["hash160", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)
    
    # invalid P2SH with double checksig
    def test_invalid_p2sh_list_too_long(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal", "equal"]
        assert ScriptType.UNKNOWN == TXOutput.determine_script_type(test_script)

    # -----------------------------------------------------------------
    #                             NOOP
    # -----------------------------------------------------------------

    # valid P2PK w/ NOOPs - trying for all codes and all positions
    def test_valid_p2pk_noop_01(self):
        test_script = ["nop", "push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_02(self):
        test_script = ["push_size_65", "nop", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_03(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_04(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig", "nop"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_05(self):
        test_script = ["push_size_65", "nop4", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_06(self):
        test_script = ["push_size_65", "nop5", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_07(self):
        test_script = ["push_size_65", "nop6", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_08(self):
        test_script = ["push_size_65", "nop7", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_09(self):
        test_script = ["push_size_65", "nop8", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_10(self):
        test_script = ["push_size_65", "nop9", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
        
    def test_valid_p2pk_noop_11(self):
        test_script = ["push_size_65", "nop10", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        assert ScriptType.P2PK == TXOutput.determine_script_type(test_script)
    
    # valid P2PKHs with noops
    def test_valid_p2pkh_with_noop_01(self):
        test_script = ["nop", "dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_02(self):
        test_script = ["dup", "nop", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_03(self):
        test_script = ["dup", "hash160", "nop", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_04(self):
        test_script = ["dup", "hash160", "push_size_20", "nop", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_05(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "nop", "equalverify", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_06(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "nop", "checksig"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)
    
    def test_valid_p2pkh_with_noop_07(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig", "nop"]
        assert ScriptType.P2PKH == TXOutput.determine_script_type(test_script)

    # valid P2SH with noops
    def test_valid_p2sh_with_noop_01(self):
        test_script = ["nop", "hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)

    def test_valid_p2sh_with_noop_02(self):
        test_script = ["hash160", "nop", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)

    def test_valid_p2sh_with_noop_03(self):
        test_script = ["hash160", "push_size_20", "nop", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)

    def test_valid_p2sh_with_noop_04(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "nop", "equal"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)

    def test_valid_p2sh_with_noop_05(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal", "nop"]
        assert ScriptType.P2SH == TXOutput.determine_script_type(test_script)

if __name__ == "__main__":
    unittest.main()