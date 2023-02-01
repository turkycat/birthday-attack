import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from .config import rpc_info

stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log = logging.getLogger("__main__")

DEBUG = False
if DEBUG:
    debug_handler = logging.StreamHandler()
    log.setLevel(logging.DEBUG)
    debug_handler.setFormatter(stream_format)
    log.addHandler(debug_handler)

"""
This class works as a wrapper around bitcoinrpc.AuthServiceProxy that solves two problems:
1) encapsulates the connection lifetime and ensures our socket is correctly closed
   when the object is destroyed (or disconnect())
2) reconnects and retries on failure, up to {RpcController.retries} times.

Use of this controller significantly improves the readability of code. Design pattern
closely mirrors AuthServiceProxy where attribute requests on the controller object
are translated into self.service and returns a callable (the instance itself) which can
then be invoked with the appropriate parameters for the service.
"""
class RpcController(object):
    retries = 3

    def __init__(self, username = None, password = None, port = None, timeout = None):
        self.__username = str(username or rpc_info["username"])
        self.__password = str(password or rpc_info["password"])
        self.__port = int(port or rpc_info["port"])
        self.__timeout = int(timeout or rpc_info["timeout"])
        self.service = None
        self.connect()

    def __call__(self, *args):
        return self.request(self.service, *args)

    def __del__(self):
        self.disconnect()
        
    # this impl attempts to allow the pattern used by AuthServiceProxy while also
    # not denying access to this class' instance attributes.
    # note: this will not work with name mangling! private vars are not currently being used.
    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        
        self.service = name
        return self

    def connect(self):
        self.__rpc_connection = AuthServiceProxy(
            f"http://{self.__username}:{self.__password}@127.0.0.1:{self.__port}", timeout=self.__timeout)

    def disconnect(self):
        if self.__rpc_connection is not None:
            # bitcoinrpc.authproxy.AuthServiceProxy does not close socket connections when the object is destroyed. 
            self.__rpc_connection._AuthServiceProxy__conn.close()

    def request(self, service_name, *args):
        attempt = 0
        last_err = None
        while attempt < RpcController.retries:
            attempt += 1
            
            try:
                return self.__rpc_connection.__getattr__(service_name)(*args)
            except JSONRPCException as err:
                log.error(f"RPC Exception {err}")
                last_err = err
            except IOError as err:
                log.error(f"IO Error {err}")
                last_err = err

            self.connect()

        raise IOError(last_err)
