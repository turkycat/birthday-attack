from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import config

class RpcController(object):

    # todo allow user, pass, timeout parameters
    def __init__(self, username = None, password = None, port = None, timeout = None):
        self.username = str(username or config.rpc_info["username"])
        self.password = str(password or config.rpc_info["password"])
        self.port = int(port or config.rpc_info["port"])
        self.timeout = int(timeout or config.rpc_info["timeout"])
        self.connect()

    def connect(self):
        self.rpc_connection = AuthServiceProxy(f"http://{self.username}:{self.password}@127.0.0.1:{self.port}", timeout=self.timeout)