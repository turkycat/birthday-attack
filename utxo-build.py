import json
import logging
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from alive_progress import alive_bar

# -----------------------------------------------------------------
#                             logging
# -----------------------------------------------------------------

# formatters and learnings shamelessly stolen from https://realpython.com/python-logging/
stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# info_handler = logging.FileHandler("logfile.txt", "w", "utf-8")
# info_handler.setLevel(logging.INFO)
# info_handler.setFormatter(file_format)
# log.addHandler(info_handler)

error_handler = logging.FileHandler("errors.txt", "w", "utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(file_format)
log.addHandler(error_handler)

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

def process_transactions(txids, block_hash):
    step = 100
    total_transactions = len(txids)
    for i in range(0, total_transactions, step):
        try:
            #log.info(f"getrawtransaction {txid} 1 {block_hash}")
            #raw_tx = rpc_connection.getrawtransaction(txid, True, block_hash)
            tx_commands = [ [ "getrawtransaction", txids[i], True, block_hash ] for i in range(i, min(i + step, total_transactions)) ]
            transactions = rpc_connection.batch_(tx_commands)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err}")
        
        # process each transaction by removing the input utxos from the unspent set and adding the new outputs as unspent
        for transaction in transactions:

            # remove all inputs from utxo_set
            for input in transaction["vin"]:

                # coinbase transactions do not have input txids and cannot already exist in the utxo set
                if input.get("coinbase"):
                    break

                spent_output_key = (input["txid"], input["vout"])
                if spent_output_key in utxo_set:
                    log.info(f"removing spent output with key: {spent_output_key}")
                    utxo_set.pop(spent_output_key)
                else:
                    log.error(f"spent output not found: {spent_output_key}")

            for output in transaction["vout"]:
                new_output_key = (transaction["txid"], output["n"])
                log.info(f"adding new output with key: {new_output_key}")
                utxo_set[new_output_key] = output["scriptPubKey"]

def build_utxo_set(start_height = 1, end_height = best_block_height):
    step = 1000
    end_height = end_height + 1 # height is zero-indexed
    with alive_bar(end_height - start_height) as progress_bar:
        for i in range(start_height, end_height, step):
            commands = [ [ "getblockhash", height] for height in range(i, min(i + step, end_height)) ]
            try:
                block_hashes = rpc_connection.batch_(commands)
                blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
            except JSONRPCException as err:
                log.error(f"RPC Exception {err}")

            log.info(f"{len(blocks)} blocks retrieved")
            for block in blocks:
                block_height = block["height"]
                block_hash = block["hash"]
                txids = block["tx"]
                log.info(f"block {block_height} with hash {block_hash} contains {len(txids)} transactions")
                process_transactions(txids, block_hash)
                progress_bar()


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
UNDER_CONSTRUCTION = False
if __name__ == "__main__":
    start_height = 1
    end_height = best_block_height
    if UNDER_CONSTRUCTION:
        start_height = 1
        end_height = 130

    build_utxo_set(start_height, end_height)
    print_utxo_set()


# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
#commands = [ [ "getblockhash", height] for height in range(20) ]
#block_hashes = rpc_connection.batch_(commands)
#blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
#block_times = [ block["time"] for block in blocks ]
#print(block_times)