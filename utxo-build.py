import json
import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# -----------------------------------------------------------------
#                             logging
# -----------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
error_handler = logging.FileHandler("errors.txt", "w")
error_handler.setLevel(logging.ERROR)
info_handler = logging.FileHandler("logfile.txt", "w")
info_handler.setLevel(logging.INFO)

# formatters and learnings shamelessly stolen from https://realpython.com/python-logging/
stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_format)
error_handler.setFormatter(file_format)
info_handler.setFormatter(file_format)

log.addHandler(stream_handler)
log.addHandler(error_handler)
log.addHandler(info_handler)

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

# rpcuser and rpcpassword are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('turkyrpc', 'turkypass'))

best_block_hash = rpc_connection.getbestblockhash()
best_block = rpc_connection.getblock(best_block_hash)
best_block_height = int(best_block["height"])

# utxo_set is currently K: tuple( transaction_hash, index ) V: script_pubkey
# TODO: write a class object to encapsulate all the interesting information from unspent outputs 
# which can then be serialized and persisted
utxo_set = {}

# -----------------------------------------------------------------
#                             functions
# -----------------------------------------------------------------

def process_transactions(transactions, block_hash):
    for i in range(0, len(transactions)):
        txid = transactions[i]
        
        try:
            log.info(f"getrawtransaction {txid} 1 {block_hash}")
            raw_tx = rpc_connection.getrawtransaction(txid, True, block_hash)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err}")
        
        # skip handling vin for coinbase transaction
        if i > 0:
            for input in raw_tx["vin"]:
                spent_output_key = (input["txid"], input["vout"])

                if spent_output_key in utxo_set:
                    log.info(f"removing spent output with key: {spent_output_key}")
                    utxo_set.pop(spent_output_key)
                else:
                    log.error(f"spent output not found: {spent_output_key}")

        for output in raw_tx["vout"]:
            new_output_key = (txid, output["n"])
            log.info(f"adding new output with key: {new_output_key}")
            utxo_set[new_output_key] = output["scriptPubKey"]

# TODO batch RPC calls to bitcoin-cli
def build_utxo_set(start = 1, end = best_block_height):
    log.info(f"building utxo set")
    for i in range(start, end + 1):
        try:
            block_hash = rpc_connection.getblockhash(i)
            block = rpc_connection.getblock(block_hash)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err}")

        transactions = block["tx"]
        log.info(f"block {i} with hash {block_hash} contains {len(transactions)} transactions")
        process_transactions(transactions, block_hash)

# todo change this to just json dumps a serializable object (the transaction object also on the TODO list)
def print_utxo_set():
    with open("utxos.txt", "w") as utxofile: # change to json
        utxofile.write("[\n")
        for item in utxo_set.items():
            txid, index = item[0]
            script_pubkey = item[1]
            # this is OK for now, to see a prelim set and verify some transaction data
            utxofile.write(f'\t{{\n\t\t"txid": "{txid}",\n\t\t"index": "{index}",\n\t\t"script_pubkey": {script_pubkey}\n\t}},\n')
        utxofile.write("]")

# TODO: periodically check the best block hash and get all blocks up to the current height
UNDER_CONSTRUCTION = True
if __name__ == "__main__":
    start = 1
    end = best_block_height
    if UNDER_CONSTRUCTION:
        start = 1
        end = 10

    build_utxo_set(start, end)
    print_utxo_set()


# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
#commands = [ [ "getblockhash", height] for height in range(20) ]
#block_hashes = rpc_connection.batch_(commands)
#blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
#block_times = [ block["time"] for block in blocks ]
#print(block_times)