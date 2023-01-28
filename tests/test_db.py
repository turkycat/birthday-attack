import unittest
from context import *
from common import *
from transactions.tx import *
from database.database_controller import DatabaseController
from keys.ring import KeyRing

enumerate_records_query = "select count(*) from utxos"

class TestDBUpdates(unittest.TestCase):

    def test_insert_01(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        outputs.add(txoutput_01)
        db.update_utxos(inputs, outputs)
        result = db.execute_read_query(enumerate_records_query)
        self.assertEqual(result[0][0], 1)

    def test_insert_and_delete_01(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        outputs.add(txoutput_01)
        outputs.add(txoutput_02)
        db.update_utxos(inputs, outputs)
        result = db.execute_read_query(enumerate_records_query)
        self.assertEqual(result[0][0], 2)

        outputs.clear()
        inputs.add(txid_01)
        db.update_utxos(inputs, outputs)
        result = db.execute_read_query(enumerate_records_query)
        self.assertEqual(result[0][0], 1)

    def test_insert_and_fetch_by_target_01(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        outputs.add(txoutput_01)
        outputs.add(txoutput_02)
        db.update_utxos(inputs, outputs)
        result = db.execute_read_query(enumerate_records_query)
        self.assertEqual(result[0][0], 2)

        fetch_query = "select * from utxos where target = ?"
        params = ("03bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5",)
        result = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)

    def test_insert_and_fetch_by_target_02(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        outputs.add(txoutput_01)
        outputs.add(txoutput_02)
        db.update_utxos(inputs, outputs)
        result = db.execute_read_query(enumerate_records_query)
        self.assertEqual(result[0][0], 2)

        fetch_query = "select * from utxos where target = ? or target = ?"
        params = ("03bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5","c1b5037d85c4fb5a7ba170f49755f171473db081")
        result = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[1][0], TRANSACTION_02_HASH)

"""
To test fetching properly, we create TXOutputs with scripts following these properties:

P2PK: uncompressed and compressed
P2PKH: uncompressed and compressed
P2WPKH: compressed

Proof:
    - I verified with a database at about block 350,000 that there are 
        37,385 rows with a script length of 134 (uncompressed pubkey)
        4,133 rows with a script length of 70 (compressed pubkey)
    - a post from Peter Wuille at bitcoin stack exchange reveals the rest:
      https://bitcoin.stackexchange.com/questions/114777/why-do-compressed-and-uncompressed-public-keys-have-to-produce-different-address

"If the address was computed off a compressed public key, the compressed public key must be revealed.
If the address was computed off an uncompressed public key, the uncompressed public key must be revealed."

and 

"Note that uncompressed keys are very rare these days. Almost all wallet software written since ~2012
exclusively uses compressed keys. BIP32 (a common mechanism form generating wallet keys deterministically,
introduced in 2013) only supports compressed keys. When using segwit scripts (BIP141, introduced in august 2017),
only compressed keys are supported (using uncompressed keys in segwit will cause transactions to not be relayed).
The confusion between the two is mostly a non-issue nowadays."

There are relatively few uncompressed key UTXOs likely to exist within the chain, but computing those keys is still worthwhile
because odds are most of those transactions are very valuable. we might as well query the database for all possible single-sig
scriptPubKeys possible for each pubkey, since we can do that in a single query.

$ bx seed | bx ec-new
eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2

$ bx ec-to-public eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2
03e89fe0d92f362e912ad9413d85386b03ff2a8df7986d8639fe7ba1947a844c42
$ bx ec-to-public -u eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2
04e89fe0d92f362e912ad9413d85386b03ff2a8df7986d8639fe7ba1947a844c42ca5d6f2d4d8c14731c9e4dc772ced441a1cb8e42d6c7c6680d498c49842fa273

$ bx ec-to-public eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2 | bx sha256 | bx ripemd160
7c5541e930f3b2b92c8efd38cf4ebd7ad0443367
$ bx ec-to-public -u eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2 | bx sha256 | bx ripemd160
43fa899894cab1b9c055e4314c5b58595ac4bc66

note that the "bitcoin160" function of bx combines the sha256 and ripemd160, so we can be sure that these are correct
(command below matches above)
$ bx ec-to-public -u eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2 | bx bitcoin160
43fa899894cab1b9c055e4314c5b58595ac4bc66

"""

private_key = "eb745745dfc36f7b8f769d049cadb5e74d0f1a0bdea71b293177331ec484c6c2"
pubkey_uncompressed = "04e89fe0d92f362e912ad9413d85386b03ff2a8df7986d8639fe7ba1947a844c42ca5d6f2d4d8c14731c9e4dc772ced441a1cb8e42d6c7c6680d498c49842fa273"
pubkey_compressed = "03e89fe0d92f362e912ad9413d85386b03ff2a8df7986d8639fe7ba1947a844c42"
pubkey_uncompressed_hashed = "43fa899894cab1b9c055e4314c5b58595ac4bc66"
pubkey_compressed_hashed = "7c5541e930f3b2b92c8efd38cf4ebd7ad0443367"
pubkey_script_prefix = "21"
pubkey_script_suffix = "ac"
pubkeyhash_script_prefix = "76a914"
pubkeyhash_script_suffix = "88ac"
witness_pubkeyhash_prefix = "0014"
witness_pubkeyhash_suffix = ""
fetch_query_single = "select * from utxos where target = ?"
fetch_query = "select * from utxos where target = ? or target = ? or target = ? or target = ?"

class TestDBTargetFetch(unittest.TestCase):

    def test_uncompressed_pubkey_fetch(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = pubkey_script_prefix + pubkey_uncompressed + pubkey_script_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "pubkey")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        params = (pubkey_uncompressed,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_uncompressed)

        # at this point in the test we verified nothing newly interesting, just that the retrieval -will- work when given
        # trivially-verifiable information. now let's create the keyring using the private key and verify that we can
        # retrieve this transaction from the database using the keyring

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkey = keyring.public_key(False)
        self.assertEqual(keyring_uncompressed_pubkey, pubkey_uncompressed)
        params = (keyring_uncompressed_pubkey,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "pubkey")
        self.assertEqual(result[0][6], pubkey_uncompressed)

    def test_compressed_pubkey_fetch(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = pubkey_script_prefix + pubkey_compressed + pubkey_script_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "pubkey")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        fetch_query_single = "select * from utxos where target = ?"
        params = (pubkey_compressed,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_compressed)

        keyring = KeyRing(private_key)
        keyring_compressed_pubkey = keyring.public_key(True)
        self.assertEqual(keyring_compressed_pubkey, pubkey_compressed)
        params = (keyring_compressed_pubkey,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "pubkey")
        self.assertEqual(result[0][6], pubkey_compressed)

    def test_uncompressed_pubkeyhash_fetch(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = pubkeyhash_script_prefix + pubkey_uncompressed_hashed + pubkeyhash_script_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "pubkeyhash")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        fetch_query_single = "select * from utxos where target = ?"
        params = (pubkey_uncompressed_hashed,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_uncompressed_hashed)

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkeyhash = keyring.public_key_hash(False)
        self.assertEqual(keyring_uncompressed_pubkeyhash, pubkey_uncompressed_hashed)
        params = (keyring_uncompressed_pubkeyhash,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "pubkeyhash")
        self.assertEqual(result[0][6], pubkey_uncompressed_hashed)

    def test_compressed_pubkeyhash_fetch(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = pubkeyhash_script_prefix + pubkey_compressed_hashed + pubkeyhash_script_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "pubkeyhash")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        fetch_query_single = "select * from utxos where target = ?"
        params = (pubkey_compressed_hashed,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkeyhash = keyring.public_key_hash(True)
        self.assertEqual(keyring_uncompressed_pubkeyhash, pubkey_compressed_hashed)
        params = (keyring_uncompressed_pubkeyhash,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "pubkeyhash")
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

    def test_witness_pubkeyhash_fetch(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = witness_pubkeyhash_prefix + pubkey_compressed_hashed + witness_pubkeyhash_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "witness_v0_keyhash")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        fetch_query_single = "select * from utxos where target = ?"
        params = (pubkey_compressed_hashed,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkeyhash = keyring.public_key_hash(True)
        self.assertEqual(keyring_uncompressed_pubkeyhash, pubkey_compressed_hashed)
        params = (keyring_uncompressed_pubkeyhash,)
        result = db.execute_read_query(fetch_query_single, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "witness_v0_keyhash")
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

    def test_comprehensive_query_with_witness_pubkeyhash_fetch_01(self):
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        scriptPubKey = witness_pubkeyhash_prefix + pubkey_compressed_hashed + witness_pubkeyhash_suffix
        tx1 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey, "witness_v0_keyhash")
        outputs.add(tx1)
        db.update_utxos(inputs, outputs)

        params = (pubkey_uncompressed,pubkey_compressed,pubkey_uncompressed_hashed,pubkey_compressed_hashed)
        result = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkeyhash = keyring.public_key_hash(True)
        self.assertEqual(keyring_uncompressed_pubkeyhash, pubkey_compressed_hashed)
        result = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], TRANSACTION_01_HASH)
        self.assertEqual(result[0][1], TRANSACTION_01_INDEX)
        self.assertEqual(result[0][2], TRANSACTION_01_BLOCK_HEIGHT)
        self.assertEqual(result[0][3], TRANSACTION_01_VALUE)
        self.assertEqual(result[0][4], scriptPubKey)
        self.assertEqual(result[0][5], "witness_v0_keyhash")
        self.assertEqual(result[0][6], pubkey_compressed_hashed)

    def test_comprehensive_query_with_witness_pubkeyhash_fetch_02(self):
        # this test is the same as 01 but all five possible transactions are added to the database and the single query
        # should return all five.
        db = DatabaseController(":memory:")
        inputs = set()
        outputs = set()
        txhash01 = TRANSACTION_01_HASH[:-2] + "01"
        txhash02 = TRANSACTION_01_HASH[:-2] + "02"
        txhash03 = TRANSACTION_01_HASH[:-2] + "03"
        txhash04 = TRANSACTION_01_HASH[:-2] + "04"
        txhash05 = TRANSACTION_01_HASH[:-2] + "05"
        scriptPubKey01 = pubkey_script_prefix + pubkey_uncompressed + pubkey_script_suffix
        tx1 = TXOutput(txhash01, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey01, "pubkey")
        scriptPubKey02 = pubkey_script_prefix + pubkey_compressed + pubkey_script_suffix
        tx2 = TXOutput(txhash02, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey02, "pubkey")
        scriptPubKey03 = pubkeyhash_script_prefix + pubkey_uncompressed_hashed + pubkeyhash_script_suffix
        tx3 = TXOutput(txhash03, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey03, "pubkeyhash")
        scriptPubKey04 = pubkeyhash_script_prefix + pubkey_compressed_hashed + pubkeyhash_script_suffix
        tx4 = TXOutput(txhash04, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey04, "pubkeyhash")
        scriptPubKey05 = witness_pubkeyhash_prefix + pubkey_compressed_hashed + witness_pubkeyhash_suffix
        tx5 = TXOutput(txhash05, TRANSACTION_01_INDEX, TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, scriptPubKey05, "witness_v0_keyhash")
        outputs.add(tx1)
        outputs.add(tx2)
        outputs.add(tx3)
        outputs.add(tx4)
        outputs.add(tx5)
        db.update_utxos(inputs, outputs)

        params = (pubkey_uncompressed,pubkey_compressed,pubkey_uncompressed_hashed,pubkey_compressed_hashed)
        results = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(results), 5)

        keyring = KeyRing(private_key)
        keyring_uncompressed_pubkey = keyring.public_key(False)
        keyring_compressed_pubkey = keyring.public_key(True)
        keyring_uncompressed_pubkeyhash = keyring.public_key_hash(False)
        keyring_compressed_pubkeyhash = keyring.public_key_hash(True)
        self.assertEqual(keyring_uncompressed_pubkey, pubkey_uncompressed)
        self.assertEqual(keyring_compressed_pubkey, pubkey_compressed)
        self.assertEqual(keyring_uncompressed_pubkeyhash, pubkey_uncompressed_hashed)
        self.assertEqual(keyring_compressed_pubkeyhash, pubkey_compressed_hashed)
        results = db.execute_read_query(fetch_query, params)
        self.assertEqual(len(results), 5)
        
        # this code was written to test code used in main
        # with open("matchfile.txt", "a", encoding = "utf-8") as match_file:
        #     text_output = f"match found! private key: {keyring.hex()} with value {keyring.current()}"
        #     print(text_output)
        #     match_file.write(text_output)
        #     match_file.write("\n")

        #     for row in results:
        #         lines = ["------------------------------------match found!------------------------------------"]
        #         lines.append(f"private key: {keyring.hex()}")
        #         lines.append(f"dec: {keyring.current()}")
        #         lines.append(f"hash: {row[0]}")
        #         lines.append(f"vout: {row[1]}")
        #         lines.append(f"height: {row[2]}")
        #         lines.append(f"value: {row[3]}")
        #         lines.append(f"script: {row[4]}")
        #         lines.append(f"type: {row[5]}")
        #         lines.append(f"target: {row[6]}")
        #         lines.append("------------------------------------------------------------------------------------")

        #         for line in lines:
        #             print(line)
        #             match_file.write(line)
        #             match_file.write("\n")
