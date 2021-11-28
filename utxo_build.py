import os
import json
import logging
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

info_handler = logging.FileHandler("logfile.txt", "w", "utf-8")
info_handler.setLevel(logging.DEBUG)
info_handler.setFormatter(file_format)
log.addHandler(info_handler)

error_handler = logging.FileHandler("errors.txt", "w", "utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(file_format)
log.addHandler(error_handler)

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

# rpcuser and rpcpassword are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('turkyrpc', 'turkypass'), timeout=1200)

best_block_hash = rpc_connection.getbestblockhash()
best_block = rpc_connection.getblock(best_block_hash)
best_block_height = int(best_block["height"])

# these identifiers are for readability and shouldn't be changed
FILE_NAME_UTXO = "utxos.txt"
FILE_NAME_CACHE = "cache.json"
PROPERTY_NAME_LAST_BLOCK = "last_block"

# -----------------------------------------------------------------
#                             functions
# -----------------------------------------------------------------

# iterate over a set of block transactions, retrieve the transaction data in batches, and process them
def process_transactions(utxo_set, txids, block_hash):
    step = 100
    total_transactions = len(txids)
    for i in range(0, total_transactions, step):
        try:
            tx_commands = [ [ "getrawtransaction", txids[i], True, block_hash ] for i in range(i, min(i + step, total_transactions)) ]
            transactions = rpc_connection.batch_(tx_commands)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err} errno: {err.errno}\nwhile attempting to retrieve transactions from: {block_hash}")
            return False
        except IOError as err:
            log.error(f"IO Error {err} errno: {err.errno}\nwhile attempting to retrieve transactions from: {block_hash}")
            return False
        
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
                new_output = TxOutput(transaction["txid"], output["n"], block_hash, output["scriptPubKey"]["hex"])
                log.info(f"adding new output with key: {new_output}")
                utxo_set.add(new_output)
    return True

# iterate over a set of block hashes to retrieve each block individually and call process_transactions with all transaction hashes
def process_blocks(utxo_set, block_hashes):
    with alive_bar(len(block_hashes)) as progress_bar:
        for block_hash in block_hashes:
            try:
                block = rpc_connection.getblock(block_hash)
            except JSONRPCException as err:
                log.error(f"RPC Exception {err} errno: {err.errno}\nwhile attempting to retrieve block: {block_hash}")
                return False
            except IOError as err:
                log.error(f"IO Error {err} errno: {err.errno}\nwhile attempting to retrieve block: {block_hash}")
                return False

            current_block_height = block["height"]
            block_hash = block["hash"]
            txids = block["tx"]
            log.info(f"block {current_block_height} with hash {block_hash} contains {len(txids)} transactions")
            if not process_transactions(utxo_set, txids, block_hash):
                return False
            progress_bar()
    return True

def build_utxo_set(utxo_set, start_height, end_height = best_block_height):
    step = 1000
    last_block_processed = None
    print(f"processing {end_height - start_height} blocks in the range [{start_height}, {end_height}]")
    for i in range(start_height, end_height, step):
        target_height = min(i + step, end_height)
        commands = [ [ "getblockhash", height] for height in range(i, target_height) ]
        try:
            block_hashes = rpc_connection.batch_(commands)
        except JSONRPCException as err:
            log.error(f"RPC Exception {err}")
            break
        except IOError as err:
            log.error(f"IO Error {err}")
            break

        log.info(f"{len(block_hashes)} block hashes retrieved")
        if process_blocks(utxo_set, block_hashes):
            last_block_processed = target_height
        else:
            log.error(f"unable to process all blocks in current batch. [{i}, {target_height}]")
            break

        # save our progress every [step] blocks
        save(utxo_set, last_block_processed)
        print(f"progress is saved at block {last_block_processed}!")
    return last_block_processed

# writes the current utxo set and other stateful properties to files
def save(utxo_set, last_block_processed):
    with open(FILE_NAME_UTXO, "w", encoding="utf-8") as utxo_file:
        print("saving UTXOs to file")
        with alive_bar(len(utxo_set)) as progress_bar:
            for output in utxo_set:
                data = output.serialize()
                utxo_file.write(f"{data}\n")
                progress_bar()

    cache = {}
    cache[PROPERTY_NAME_LAST_BLOCK] = last_block_processed
    with open(FILE_NAME_CACHE, "w", encoding="utf-8") as cache_file:
        cache_file.write(json.dumps(cache))

def load():
    utxo_set = set()
    last_block_processed = None

    if os.path.exists(FILE_NAME_UTXO):
        with open(FILE_NAME_UTXO, "r", encoding="utf-8") as utxo_file:
            print("loading UTXOs from file")
            with alive_bar() as progress_bar:
                for line in utxo_file:
                    output = TxOutput.deserialize(line[:-1]) # remove newline character
                    if output is not None:
                        utxo_set.add(output)

    if os.path.exists(FILE_NAME_CACHE):
        with open(FILE_NAME_CACHE, "r", encoding="utf-8") as cache_file:
            cache = json.loads(cache_file.read())
            last_block_processed = cache[PROPERTY_NAME_LAST_BLOCK]
        
    return utxo_set, last_block_processed

TESTING = False
TESTING_HEIGHT = 100
if __name__ == "__main__":
    utxo_set, last_block_processed = load()

    utxo_set = utxo_set or set()
    last_block_processed = last_block_processed or 0
    start_height = last_block_processed + 1
    end_height = (TESTING and TESTING_HEIGHT) or best_block_height

    log.debug(f"utxo set size {len(utxo_set)}")
    log.debug(f"last_block_processed: {last_block_processed}")
    log.debug(f"start_height {start_height}")
    log.debug(f"end_height {end_height}")

    last_block_processed = build_utxo_set(utxo_set, start_height, end_height) or last_block_processed
    save(utxo_set, last_block_processed)
