import json
import logging
import jsonpickle
from txoutput import TxOutput
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

utxo_set = set()

# -----------------------------------------------------------------
#                             functions
# -----------------------------------------------------------------

def process_transactions(txids, block_hash):
    step = 100
    total_transactions = len(txids)
    for i in range(0, total_transactions, step):
        try:
            tx_commands = [ [ "getrawtransaction", txids[i], True, block_hash ] for i in range(i, min(i + step, total_transactions)) ]
            transactions = rpc_connection.batch_(tx_commands)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err}")
        
        # process each transaction by removing the input utxos from the unspent set and adding the new outputs as unspent
        for transaction in transactions:
            for input in transaction["vin"]:

                # coinbase transactions do not have input txids and cannot already exist in the utxo set
                if input.get("coinbase"):
                    break

                spent_output = TxOutput(input["txid"], input["vout"])
                if spent_output in utxo_set:
                    log.info(f"removing spent output {spent_output}")
                    utxo_set.remove(spent_output)
                else:
                    log.error(f"spent output not found: {spent_output}")

            # add all outputs to utxo set
            for output in transaction["vout"]:
                new_output = TxOutput(transaction["txid"], output["n"], output["scriptPubKey"])
                log.info(f"adding new output with key: {new_output}")
                utxo_set.add(new_output)

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

def persist_state():
    with open("utxos.json", "w") as utxo_file:
        utxo_file.write(jsonpickle.encode(utxo_set))

# TODO: periodically check the best block hash and get all blocks up to the current height
UNDER_CONSTRUCTION = True
if __name__ == "__main__":
    start_height = 1
    end_height = best_block_height
    if UNDER_CONSTRUCTION:
        start_height = 1
        end_height = 100

    build_utxo_set(start_height, end_height)
    persist_state()
