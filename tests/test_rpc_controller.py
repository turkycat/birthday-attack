import unittest
import logging
from context import *
from rpc_controller.rpc_controller import RpcController

file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger("BitcoinRPC")
#info_handler = logging.FileHandler("rpc.txt", "w", "utf-8")
info_handler = logging.StreamHandler()
info_handler.setLevel(logging.DEBUG)
info_handler.setFormatter(file_format)
log.addHandler(info_handler)

class TestRpcController(unittest.TestCase):

    def test_config_default_fields(self):
        # we can't test for a specific value here, otherwise test will fail if config is changed.
        # instead, validate that a value is set and types are correct
        controller = RpcController()
        assert type(controller.username) is str
        assert type(controller.password) is str
        assert type(controller.port) is int
        assert type(controller.timeout) is int

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
        assert controller.username == test_user
        assert controller.password == test_pass
        assert controller.port == test_port
        assert controller.timeout == test_timeout

    def test_connect_with_default(self):
        controller = RpcController()
        best_block_hash = controller.best_block_hash()
        assert type(best_block_hash) is str

if __name__ == "__main__":
    unittest.main()