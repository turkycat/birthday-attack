import unittest
import txoutput

TRANSACTION_BLOCK_HASH = "000000006c02c8ea6e4ff69651f7fcde348fb9d557a06e6957b65552002a7820"
TRANSACTION_INDEX = 0
TRANSACTION_HASH = "20222eb90f5895556926c112bb5aa0df4ab5abc3107e21a6950aec3b2e3541e2"

class TestTxOutput(unittest.TestCase):

    def test_basic_tx_to_json(self):
        tx = txoutput.TxOutput(TRANSACTION_HASH, TRANSACTION_INDEX)
        self.assertEqual(tx.json_encode(), f'{{"hsh": "{TRANSACTION_HASH}", "idx": {TRANSACTION_INDEX}}}')

    def test_basic_tx_with_block_hash_to_json(self):
        tx = txoutput.TxOutput(TRANSACTION_HASH, TRANSACTION_INDEX, TRANSACTION_BLOCK_HASH)
        self.assertEqual(tx.json_encode(), f'{{"hsh": "{TRANSACTION_HASH}", "idx": {TRANSACTION_INDEX}, "blk": "{TRANSACTION_BLOCK_HASH}"}}')

if __name__ == "__main__":
    tx = txoutput.TxOutput(TRANSACTION_HASH, TRANSACTION_INDEX, TRANSACTION_BLOCK_HASH)
    print(tx.json_encode())
    unittest.main()