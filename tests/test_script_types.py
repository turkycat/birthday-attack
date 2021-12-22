import unittest
from context import *
from common import *
from transactions.tx import *
from transactions.script import *

# -----------------------------------------------------------------
#                             NONE
# -----------------------------------------------------------------

class TestScriptDetermineTypeNone(unittest.TestCase):

    # script is None
    def test_invalid_script_none(self):
        test_script = None
        self.assertEqual(Type.NONE, locking_script_type(test_script))

    # script is empty list
    def test_invalid_script_empty_list(self):
        test_script = []
        self.assertEqual(Type.NONE, locking_script_type(test_script))

# -----------------------------------------------------------------
#                             P2PK
# -----------------------------------------------------------------

class TestScriptDetermineTypeP2PK(unittest.TestCase):

    # valid P2PK w/ uncompressed public key
    def test_valid_p2pk_uncompressed_key(self):
        test_script = ["push_size_65", UNCOMPRESSED_PUBLIC_KEY, "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))

    # valid P2PK w/ compressed public key 1
    def test_valid_p2pk_compressed_key_01(self):
        test_script = ["push_size_33", COMPRESSED_PUBLIC_KEY_01, "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))

    # valid P2PK w/ compressed public key 2
    def test_valid_p2pk_compressed_key_02(self):
        test_script = ["push_size_33", COMPRESSED_PUBLIC_KEY_02, "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))

    # invalid P2PK w/ uncompressed public key (too long)
    def test_invalid_p2pk_uncompressed_key_too_long(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b123d5043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK w/ uncompressed public key (too short)
    def test_invalid_p2pk_uncompressed_key_too_short(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a116575b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK w/ compressed public key (too long)
    def test_invalid_p2pk_compressed_key_too_long(self):
        test_script = ["push_size_33", "0214f296079b181abd76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK w/ compressed public key (too short)
    def test_invalid_p2pk_compressed_key_too_short(self):
        test_script = ["push_size_33", "03831cfea00b5cfcd9a12fd14b469d9385140d187d2bd8add9a1044685db9552b", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with incorrect first opcode
    def test_invalid_p2pk_compressed_key_incorect_opcode_01(self):
        test_script = ["push_size_63", COMPRESSED_PUBLIC_KEY_01, "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with incorrect last opcode
    def test_invalid_p2pk_compressed_key_incorect_opcode_02(self):
        test_script = ["push_size_33", COMPRESSED_PUBLIC_KEY_01, "checksigverify"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with missing key
    def test_invalid_p2pk_compressed_key_missing(self):
        test_script = ["push_size_33", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with empty key
    def test_invalid_p2pk_compressed_key_empty(self):
        test_script = ["push_size_33", "", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with invalid chars in key 1
    def test_invalid_p2pk_compressed_key_invalid_chars_01(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8hello1d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PK with invalid chars in key 2
    def test_invalid_p2pk_compressed_key_invalid_chars_02(self):
        test_script = ["push_size_33", "0214f296079b181ab76cd817f8ba5b#1d9ba5b00ca46f16eadfab8e0bb3a2b0420", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # too many checksigs
    def test_invalid_script_list_too_long(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # -----------------------------------------------------------------
    #                             P2PKH
    # -----------------------------------------------------------------

class TestScriptDetermineTypeP2PKH(unittest.TestCase):
    
    # valid P2PKH
    def test_valid_p2pkh(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
        
    # invalid P2PKH with missing hash
    def test_invalid_p2pkh_missing_hash(self):
        test_script = ["dup", "hash160", "push_size_20", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PKH with empty hash
    def test_invalid_p2pkh_empty_hash(self):
        test_script = ["dup", "hash160", "push_size_20", "", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2PKH with key too short
    def test_invalid_p2pkh_key_too_short(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9e60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2PKH with key too long
    def test_invalid_p2pkh_key_too_long(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9bed60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PKH with invalid chars in key 1
    def test_invalid_p2pkh_invalid_chars_01(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871fhellofb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2PKH with invalid chars in key 2
    def test_invalid_p2pkh_invalid_chars_02(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c8#1f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2PKH with missing checksig
    def test_invalid_p2pkh_list_too_short(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2PKH with double checksig
    def test_invalid_p2pkh_list_too_long(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig", "checksig"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # -----------------------------------------------------------------
    #                             P2SH
    # -----------------------------------------------------------------

class TestScriptDetermineTypeP2SH(unittest.TestCase):
    
    # valid P2SH
    def test_valid_p2sh(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.P2SH, locking_script_type(test_script))
        
    # invalid P2SH with missing hash
    def test_invalid_p2sh_missing_hash(self):
        test_script = ["hash160", "push_size_20", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2SH with empty hash
    def test_invalid_p2sh_empty_hash(self):
        test_script = ["hash160", "push_size_20", "", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2SH with key too short
    def test_invalid_p2sh_key_too_short(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07ac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2SH with key too long
    def test_invalid_p2sh_key_too_long(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07adac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2SH with invalid chars in key 1
    def test_invalid_p2sh_invalid_chars_01(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aachelloebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # invalid P2SH with invalid chars in key 2
    def test_invalid_p2sh_invalid_chars_02(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac761$#ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2SH with missing checksig
    def test_invalid_p2sh_list_too_short(self):
        test_script = ["hash160", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))
    
    # invalid P2SH with double checksig
    def test_invalid_p2sh_list_too_long(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal", "equal"]
        self.assertEqual(Type.UNKNOWN, locking_script_type(test_script))

    # -----------------------------------------------------------------
    #                             NOOP
    # -----------------------------------------------------------------

class TestScriptNoops(unittest.TestCase):

    # valid P2PK w/ NOOPs - trying for all codes and all positions
    def test_valid_p2pk_noop_01(self):
        test_script = ["nop", "push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_03(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_04(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "checksig", "nop"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_05(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop4", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_06(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop5", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_07(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop6", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_08(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop7", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_09(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop8", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_10(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop9", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
        
    def test_valid_p2pk_noop_11(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0", "nop10", "checksig"]
        self.assertEqual(Type.P2PK, locking_script_type(test_script))
    
    # valid P2PKHs with noops
    def test_valid_p2pkh_with_noop_01(self):
        test_script = ["nop", "dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
    
    def test_valid_p2pkh_with_noop_02(self):
        test_script = ["dup", "nop", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
    
    def test_valid_p2pkh_with_noop_03(self):
        test_script = ["dup", "hash160", "nop", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
    
    def test_valid_p2pkh_with_noop_05(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "nop", "equalverify", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
    
    def test_valid_p2pkh_with_noop_06(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "nop", "checksig"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))
    
    def test_valid_p2pkh_with_noop_07(self):
        test_script = ["dup", "hash160", "push_size_20", "4ea2cc288c1c871f9be60fb600c294b75fb83b40", "equalverify", "checksig", "nop"]
        self.assertEqual(Type.P2PKH, locking_script_type(test_script))

    # valid P2SH with noops
    def test_valid_p2sh_with_noop_01(self):
        test_script = ["nop", "hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.P2SH, locking_script_type(test_script))

    def test_valid_p2sh_with_noop_02(self):
        test_script = ["hash160", "nop", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal"]
        self.assertEqual(Type.P2SH, locking_script_type(test_script))

    def test_valid_p2sh_with_noop_04(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "nop", "equal"]
        self.assertEqual(Type.P2SH, locking_script_type(test_script))

    def test_valid_p2sh_with_noop_05(self):
        test_script = ["hash160", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a", "equal", "nop"]
        self.assertEqual(Type.P2SH, locking_script_type(test_script))

    # -----------------------------------------------------------------
    #                             SEGWIT
    # -----------------------------------------------------------------

class TestScriptDetermineTypeSegwit(unittest.TestCase):

    def test_valid_p2wpkh(self):
        test_script = ["push_size_0", "push_size_20", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160a"]
        self.assertEqual(Type.P2WPKH, locking_script_type(test_script))

    def test_valid_p2wpkh_decode(self):
        test_script = "001499fc7624fa2943151239b814e77407f6b9cf1099"
        self.assertEqual(Type.P2WPKH, locking_script_type(decode_script(test_script)))

    def test_valid_p2wsh(self):
        test_script = ["push_size_0", "push_size_32", "e9c3dd0c07aac76179ebc76a6c78d4d67c6c160ae9c3dd0c07aac76179ebc76a"]
        self.assertEqual(Type.P2WSH, locking_script_type(test_script))

    def test_valid_p2wsh_decode(self):
        test_script = "002099fc7624fa2943151239b814e77407f6b9cf1099e9c3dd0c07aac76179ebc76a"
        self.assertEqual(Type.P2WSH, locking_script_type(decode_script(test_script)))

    # -----------------------------------------------------------------
    #                          ANYONE CAN SPEND
    # -----------------------------------------------------------------

class TestScriptDetermineTypeAnyoneCanSpend(unittest.TestCase):
        
    # script data only
    def test_valid_anyone_can_spend(self):
        test_script = ["push_size_65", "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0"]
        self.assertEqual(Type.ANYONE_CAN_SPEND, locking_script_type(test_script))

    # -----------------------------------------------------------------
    #                             MULTISIG
    # -----------------------------------------------------------------

class TestScriptDetermineTypeMultisig(unittest.TestCase):

    # script is None
    def test_multisig_invalid_script_none(self):
        test_script = None
        self.assertEqual(Type.NONE, locking_script_multisig_type(test_script))

    # script is empty list
    def test_multisig_invalid_script_empty_list(self):
        test_script = []
        self.assertEqual(Type.NONE, locking_script_multisig_type(test_script))

    def test_multisig_01_of_01(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_1", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 1)
        self.assertEqual(N, 1)

    def test_multisig_01_of_02(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_2", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 1)
        self.assertEqual(N, 2)

    def test_multisig_01_of_03(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_3", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 1)
        self.assertEqual(N, 3)

    def test_multisig_02_of_02(self):
        test_script = ["push_positive_2",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_2", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 2)
        self.assertEqual(N, 2)

    def test_multisig_02_of_03(self):
        test_script = ["push_positive_2",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_3", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 2)
        self.assertEqual(N, 3)

    def test_multisig_03_of_03(self):
        test_script = ["push_positive_3",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_3", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)
        self.assertEqual(M, 3)
        self.assertEqual(N, 3)

    def test_multisig_02_of_03_with_locking_script_type_function(self):
        test_script = ["push_positive_2",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_3", "checkmultisig"]
        script_type = locking_script_type(test_script)
        self.assertEqual(script_type, Type.MULTISIG)

    """
    if this were production code I would write a function to generate all invalid combinations of M-of-N scripts but I
    just don't care right now. if there are issues I'll see them in the unknown set. maybe I'll do this later ¯\_(ツ)_/¯
    """
    def test_multisig_invalid_01_of_04(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_4", "checkmultisig"
            ]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_05(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_5", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_06(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_6", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_07(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_7", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_08(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_8", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_09(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_9", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_10(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_10", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_11(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_11", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_12(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_12", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_13(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_13", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_14(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_14", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_15(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_15", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_16(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            COMPRESSED_PUBLIC_KEY_02,
            "push_positive_16", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

    def test_multisig_invalid_01_of_01_total_less_than_expected(self):
        test_script = ["push_positive_1",
            COMPRESSED_PUBLIC_KEY_02, COMPRESSED_PUBLIC_KEY_02,
            "push_positive_1", "checkmultisig"]
        script_type, M, N = locking_script_multisig_type(test_script)
        self.assertEqual(script_type, Type.UNKNOWN)
        self.assertEqual(M, 0)
        self.assertEqual(N, 0)

if __name__ == "__main__":
    unittest.main()