import unittest
from context import *
from common import *
from transactions.tx import *

class TestTxOutputSerialization(unittest.TestCase):

    def test_serialize_01(self):
        serialized_data = txoutput_01.serialize()
        split_items = serialized_data.split(",")
        self.assertTrue(len(split_items) == 4)
        self.assertEqual(split_items[0], TRANSACTION_01_HASH)
        self.assertEqual(split_items[1], str(TRANSACTION_01_INDEX))
        self.assertEqual(split_items[2], str(TRANSACTION_01_VALUE))
        self.assertEqual(split_items[3], TRANSACTION_01_SCRIPT)

    def test_deserialize_01(self):
        serialized_data = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8,0,1240000000,2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)

    def test_serialize_and_deserialize(self):
        serialized_data = txoutput_01.serialize()
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)

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

if __name__ == "__main__":
    unittest.main()