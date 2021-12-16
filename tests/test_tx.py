import unittest
from context import *
from common import *
from transactions.tx import *

class TestTxOutputSerialization(unittest.TestCase):

    def test_serialize_01(self):
        serialized_data = txoutput_01.serialize()
        split_items = serialized_data.split(",")
        self.assertTrue(len(split_items) == 5)
        self.assertEqual(split_items[0], TRANSACTION_01_HASH)
        self.assertEqual(split_items[1], str(TRANSACTION_01_INDEX))
        self.assertEqual(split_items[2], str(TRANSACTION_01_BLOCK_HEIGHT))
        self.assertEqual(split_items[3], str(TRANSACTION_01_VALUE))
        self.assertEqual(split_items[4], TRANSACTION_01_SCRIPT)

    def test_deserialize_01(self):
        serialized_data = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8,0,4,1240000000,2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.block_height, txout.block_height)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)

    def test_serialize_and_deserialize(self):
        serialized_data = txoutput_01.serialize()
        txout = TXOutput.deserialize(serialized_data)
        self.assertEqual(txoutput_01.hash, txout.hash)
        self.assertEqual(txoutput_01.index, txout.index)
        self.assertEqual(txoutput_01.block_height, txout.block_height)
        self.assertEqual(txoutput_01.value_in_sats, txout.value_in_sats)
        self.assertEqual(txoutput_01.serialized_script, txout.serialized_script)

class TransactionSetOps(unittest.TestCase):

    def test_output_hash_equals_transaction(self):
        self.assertEqual(tx_01.hash, txoutput_01.hash)
        self.assertEqual(tx_01.index, txoutput_01.index)
        self.assertEqual(tx_01.hash, txoutput_01.hash)
        self.assertEqual(tx_01.__hash__(), txoutput_01.__hash__())

    def test_output_hash_not_equals_transaction(self):
        self.assertNotEqual(tx_01.__hash__(), txoutput_02.__hash__())

    def test_output_removed_by_transaction(self):
        utxo = set()
        utxo.add(txoutput_01)
        self.assertTrue(utxo.__sizeof__, 1)
        utxo.remove(tx_01)
        self.assertTrue(utxo.__sizeof__, 0)

    def test_output_not_found_with_different_transaction(self):
        utxo = set()
        utxo.add(txoutput_01)
        self.assertTrue(utxo.__sizeof__, 1)
        tx_01_other = TXID(tx_01.hash, tx_01.index + 1)
        with self.assertRaises(KeyError):
            utxo.remove(tx_01_other)
        self.assertTrue(utxo.__sizeof__, 1)

if __name__ == "__main__":
    unittest.main()