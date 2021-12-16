import unittest
from context import *
from common import *
from transactions.tx import *

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
