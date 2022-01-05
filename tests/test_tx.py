import unittest
from context import *
from common import *
from rpc_controller.rpc_controller import RpcController
from transactions.tx import *

class TestTxOutputSerialization(unittest.TestCase):

    def test_serialize_01(self):
        serialized_data = txoutput_01.serialize()
        split_items = serialized_data.split(",")
        self.assertTrue(len(split_items) == 5)
        self.assertEqual(split_items[0], TRANSACTION_01_HASH)
        self.assertEqual(split_items[1], str(TRANSACTION_01_INDEX))
        self.assertEqual(split_items[2], str(TRANSACTION_01_VALUE))
        self.assertEqual(split_items[3], TRANSACTION_01_SCRIPT)
        self.assertEqual(split_items[4], TRANSACTION_01_TYPE)

    def test_deserialize_01(self):
        serialized_data = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8,0,1240000000,2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac,pubkey"
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)
        self.assertEqual(txoutput_01.script_type, txout.script_type)

    def test_serialize_and_deserialize(self):
        serialized_data = txoutput_01.serialize()
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)
        self.assertEqual(txoutput_01.script_type, txout.script_type)

class TXEqualsByIDOnly(unittest.TestCase):

    def test_output_hash_equals_txid(self):
        self.assertEqual(txid_01.hash, txoutput_01.hash)
        self.assertEqual(txid_01.index, txoutput_01.index)
        self.assertEqual(txid_01.__hash__(), txoutput_01.__hash__())

    def test_output_hash_not_equals_txid(self):
        self.assertNotEqual(txid_01.__hash__(), txoutput_02.__hash__())

    def test_input_hash_equals_txid(self):
        txinput = TXInput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
        self.assertEqual(txid_01.hash, txinput.hash)
        self.assertEqual(txid_01.index, txinput.index)
        self.assertEqual(txid_01.__hash__(), txinput.__hash__())

    def test_input_hash_equals_txid_02(self):
        txinput = TXInput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, "CAFEBABE")
        self.assertEqual(txid_01.hash, txinput.hash)
        self.assertEqual(txid_01.index, txinput.index)
        self.assertEqual(txid_01.__hash__(), txinput.__hash__())

    def test_input_hash_equals_txid_03(self):
        txinput = TXInput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, "CAFEBABE", "CAFEBABE")
        self.assertEqual(txid_01.hash, txinput.hash)
        self.assertEqual(txid_01.index, txinput.index)
        self.assertEqual(txid_01.__hash__(), txinput.__hash__())

    def test_input_hash_equals_output(self):
        txinput = TXInput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, "DEADBEEF", "DEADBEEF")
        self.assertEqual(txoutput_01.hash, txinput.hash)
        self.assertEqual(txoutput_01.index, txinput.index)
        self.assertEqual(txoutput_01.__hash__(), txinput.__hash__())

class TXSetOps(unittest.TestCase):

    def test_output_removed_by_txid(self):
        utxo = set()
        utxo.add(txoutput_01)
        self.assertTrue(utxo.__sizeof__, 1)
        utxo.remove(txid_01)
        self.assertTrue(utxo.__sizeof__, 0)

    def test_output_not_found_with_different_txid(self):
        utxo = set()
        utxo.add(txoutput_01)
        self.assertTrue(utxo.__sizeof__, 1)
        tx_01_other = TXID(txid_01.hash, txid_01.index + 1)
        with self.assertRaises(KeyError):
            utxo.remove(tx_01_other)
        self.assertTrue(utxo.__sizeof__, 1)
       
    def test_output_removed_by_input(self):
        txinput = TXInput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
        utxo = set()
        utxo.add(txoutput_01)
        self.assertTrue(utxo.__sizeof__, 1)
        utxo.remove(txinput)
        self.assertTrue(utxo.__sizeof__, 0)

class TXOutputFromDictionaryAndGets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rpc = RpcController()

    def test_get_pubkey_real_tx(self):
        pubkey_txid = "f0215df69bd55e44acd06c54a21ef671619e6ddc2fadbf659a48587cf343b1af"
        source_block_hash = "000000000b554c46f8eb7264d7d5e334382c6fc3098dabf734de37962ccd7495"
        transaction = TXOutputFromDictionaryAndGets.rpc.getrawtransaction(pubkey_txid, True, source_block_hash)

        output = TXOutput.from_dictionary(pubkey_txid, transaction["vout"][0])
        self.assertEqual(output.script_type, "pubkey")
        self.assertEqual(output.get_pubkey(), "041067b3f193a98683e0a7ee0dc93da24330e11596b4265ada6aef128006441b3225903a45b993fb8f49b9eecdfc08847878b8c1b0d39f7093e70328ec469e5f7f")
        self.assertIsNone(output.get_pubkeyhash())

    def test_get_pubkey_hash_real_tx(self):
        pubkey_hash_txid = "8a2ad0f8c17c767234385233f87141e87e1865725c6fe9268c7a72fd3b9618d8"
        source_block_hash = "0000000000000a0276cda9be68104843ef907113942fda4d2162355513396291"
        transaction = TXOutputFromDictionaryAndGets.rpc.getrawtransaction(pubkey_hash_txid, True, source_block_hash)

        output = TXOutput.from_dictionary(pubkey_hash_txid, transaction["vout"][0])
        self.assertEqual(output.script_type, "pubkeyhash")
        self.assertIsNone(output.get_pubkey())
        self.assertEqual(output.get_pubkeyhash(), "c1b5037d85c4fb5a7ba170f49755f171473db081")

        output = TXOutput.from_dictionary(pubkey_hash_txid, transaction["vout"][1])
        self.assertEqual(output.script_type, "pubkeyhash")
        self.assertIsNone(output.get_pubkey())
        self.assertEqual(output.get_pubkeyhash(), "a6ffb4527f4eea8d3e11a5c9c17ceef5e6f5fceb")

if __name__ == "__main__":
    unittest.main()