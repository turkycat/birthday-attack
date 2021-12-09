import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from .config import rpc_info

log = logging.getLogger(__name__)

class RpcController(object):
    retries = 3

    def __init__(self, username = None, password = None, port = None, timeout = None):
        self.username = str(username or rpc_info["username"])
        self.password = str(password or rpc_info["password"])
        self.port = int(port or rpc_info["port"])
        self.timeout = int(timeout or rpc_info["timeout"])

        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.rpc_connection = AuthServiceProxy(
            f"http://{self.username}:{self.password}@127.0.0.1:{self.port}", timeout=self.timeout)

    def disconnect(self):
        if self.rpc_connection is not None:
            # bitcoinrpc.authproxy.AuthServiceProxy does not close socket connections when the object
            # is destroyed. this is further complicated by the __getattr__ override returning a callable
            # honestly, I love the design and think it's super clever as we can call for any service on the
            # AuthServiceProxy type without needing for each one to be defined. however, we can't just retrieve
            # the '__conn' object directly as rpc_connection.__conn would invoke __getattr__. The below is a hack.
            self.rpc_connection.__dict__["_AuthServiceProxy__conn"].close()

    def request(self, service_name):
        attempt = 0
        while attempt < RpcController.retries:
            attempt += 1
            
            try:
                response = self.rpc_connection.__getattr__(service_name)()
                return response
            except JSONRPCException as err:
                log.error(f"RPC Exception {err}")
            except IOError as err:
                log.error(f"IO Error {err}")

            self.connect()
        
    def best_block_hash(self):
        return self.request("getbestblockhash")
                