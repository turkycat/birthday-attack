import unittest
import logging
from context import *
from rpc_controller.rpc_controller import RpcController

stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

DEBUG = False
if DEBUG:
    log = logging.getLogger("BitcoinRPC")
    debug_handler = logging.StreamHandler()
    log.setLevel(logging.DEBUG)
    debug_handler.setFormatter(stream_format)
    log.addHandler(debug_handler)

BLOCK_HASH_000_001 = "00000000839a8e6886ab5951d76f411475428afc90947ee320161bbf18eb6048"
TRANSACTION_HASH_FROM_BLOCK_000_001 = "0e3e2357e806b6cdb1f70b54c3a3a17b6714ee1f0e68bebb44a74b1efd512098"

class TestRpcController(unittest.TestCase):

    def test_config_default_fields(self):
        # we can't test for a specific value here, otherwise test will fail if config is changed.
        # instead, validate that a value is set and types are correct
        controller = RpcController()
        assert type(controller._RpcController__username) is str
        assert type(controller._RpcController__password) is str
        assert type(controller._RpcController__port) is int
        assert type(controller._RpcController__timeout) is int

    def test_config_override_fields(self):
        test_user = "this_is_a_test_username"
        test_pass = "this_is_a_test_password"
        test_port = 1113
        test_timeout = 1313
        controller = RpcController(
            username = test_user,
            password = test_pass,
            port = test_port,
            timeout = test_timeout
        )
        assert controller._RpcController__username == test_user
        assert controller._RpcController__password == test_pass
        assert controller._RpcController__port == test_port
        assert controller._RpcController__timeout == test_timeout

    def test_connect_with_default(self):
        controller = RpcController()
        best_block_hash = controller.getbestblockhash()
        assert type(best_block_hash) is str
        assert len(best_block_hash) == 64

    def test_block_hash_001(self):
        controller = RpcController()
        block_hash = controller.getblockhash(1)
        assert block_hash == BLOCK_HASH_000_001

    def test_get_block_001(self):
        controller = RpcController()
        block = controller.getblock(BLOCK_HASH_000_001)
        assert type(block) is dict
        assert block["hash"] == BLOCK_HASH_000_001
        assert block["height"] == 1
        assert type(block["tx"]) is list
        assert len(block["tx"]) == 1
        
    def test_transaction_001(self):
        controller = RpcController()
        transaction_data = controller.getrawtransaction(TRANSACTION_HASH_FROM_BLOCK_000_001, True, BLOCK_HASH_000_001)
        assert len(transaction_data) > 0

if __name__ == "__main__":
    unittest.main()