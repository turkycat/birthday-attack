import unittest
from context import *
from transactions.tx import *

# pubkey hash tx
TRANSACTION_01_HASH = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8"
TRANSACTION_01_INDEX = 0
TRANSACTION_01_BLOCK_HEIGHT = 4
TRANSACTION_01_VALUE = 12.40000000
TRANSACTION_01_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
#       varint size (33)-^ ^-compressed public key (03) followed by 32 byte x-coordinate---^|^- checksig (172)

tx_01 = Transaction(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
txoutput_01 = TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, \
    TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, TRANSACTION_01_SCRIPT)

TRANSACTION_02_HASH = "8a2ad0f8c17c767234385233f87141e87e1865725c6fe9268c7a72fd3b9618d8"
TRANSACTION_02_INDEX = 0
TRANSACTION_02_BLOCK_HEIGHT = 164221
TRANSACTION_02_VALUE = 982.10200000
TRANSACTION_02_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
TRANSACTION_02_DECODED_SCRIPT = ["push_data_33", "03bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5", "checksig"]
# transaction 01 block hash 0000000000000a0276cda9be68104843ef907113942fda4d2162355513396291

tx_02 = Transaction(TRANSACTION_02_HASH, TRANSACTION_02_INDEX)
txoutput_02 = TXOutput(TRANSACTION_02_HASH, TRANSACTION_02_INDEX, \
    TRANSACTION_02_BLOCK_HEIGHT, TRANSACTION_02_VALUE, TRANSACTION_02_SCRIPT)

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
        tx_01_other = Transaction(tx_01.hash, tx_01.index + 1)
        with self.assertRaises(KeyError):
            utxo.remove(tx_01_other)
        self.assertTrue(utxo.__sizeof__, 1)
