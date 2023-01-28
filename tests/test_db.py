import unittest
from context import *
from common import *
from transactions.tx import *
from database.database_controller import DatabaseController

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