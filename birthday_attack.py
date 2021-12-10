import os
import json
import logging
import time
from utxo.TXOutput import TXOutput, ScriptDecodingException
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from alive_progress import alive_bar

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

# rpcuser and rpcpassword are set in the bitcoin.conf file, and yes don't worry this is a dummy user and password
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('turkyrpc', 'turkypass'), timeout=1200)

best_block_hash = rpc_connection.getbestblockhash()
best_block = rpc_connection.getblock(best_block_hash)
best_block_height = int(best_block["height"])

# file and output related constants
FILE_NAME_CACHE = "cache.json"
FILE_NAME_ERROR = "errors.txt"
FILE_NAME_LOG = "logfile.txt"
FILE_NAME_SCRIPTS = "scripts.txt"
FILE_NAME_UTXO = "utxos.txt"

DIR_OUTPUT_RELATIVE = "output"
DIR_OUTPUT_ABSOLUTE = os.path.join(os.getcwd(), DIR_OUTPUT_RELATIVE)
file_paths = {
    FILE_NAME_CACHE: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_CACHE),
    FILE_NAME_ERROR: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_ERROR),
    FILE_NAME_LOG: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_LOG),
    FILE_NAME_SCRIPTS: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_SCRIPTS),
    FILE_NAME_UTXO: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_UTXO)
    }

if not os.path.exists(DIR_OUTPUT_ABSOLUTE):
    os.makedirs(DIR_OUTPUT_ABSOLUTE)

# cache properties
PROPERTY_NAME_LAST_BLOCK = "last_block"

# -----------------------------------------------------------------
#                             logging
# -----------------------------------------------------------------

# formatters from https://realpython.com/python-logging/
stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

DEBUGGING = False
if DEBUGGING:
    log.setLevel(logging.DEBUG)
    info_handler = logging.FileHandler(file_paths[FILE_NAME_LOG], "w", "utf-8")
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(file_format)
    log.addHandler(info_handler)

ERROR_LOGGING = True
if ERROR_LOGGING:
    error_handler = logging.FileHandler(file_paths[FILE_NAME_ERROR], "w", "utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    log.addHandler(error_handler)

# -----------------------------------------------------------------
#                             functions
# -----------------------------------------------------------------

# decipher each script type to determine its type and parameters note that some of this is
# provided for us in the getrawtransaction payload, but is intentionally ignored
def decode_transaction_scripts(transactions):
    print("decoding transaction scripts")
    with open(file_paths[FILE_NAME_SCRIPTS], "w", encoding="utf-8") as scripts_file:
        with alive_bar(len(transactions)) as progress_bar:
            for output in transactions:
                scripts_file.write(output.__repr__())
                scripts_file.write(f"\n{output.script}\n")

                try:
                    decoded_script = output.decode_script()
                    scripts_file.write(f"{decoded_script}\n")#{output.script_type}\n")
                except ScriptDecodingException as err:
                    log.error(output.__repr__())
                    log.error(err)

                scripts_file.write("\n")
                progress_bar()

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

                spent_output = TXOutput(input["txid"], input["vout"])
                if spent_output in utxo_set:
                    log.info(f"removing spent output {spent_output}")
                    utxo_set.remove(spent_output)
                else:
                    log.error(f"spent output not found: {spent_output}")

            # add all outputs to utxo set
            for output in transaction["vout"]:
                new_output = TXOutput(transaction["txid"], output["n"], block_hash, output["scriptPubKey"]["hex"])
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

# using rpc, query parts of the blockchain in small groups until we are able to build the entire utxo set.
# note that it would surely be faster and easier to read the data files directly. I am doing it this way
# for fun and experimentation with Python, and to keep the node running and TODO: updating live as blocks are processed.
def build_utxo_set(utxo_set, start_height, end_height = best_block_height):
    step = 1000
    last_block_processed = None
    last_save_time = time.time()
    MINUTES_BETWEEN_SAVES = 20.0
    SECONDS_PER_MINUTE = 60.0
    print(f"processing {end_height - start_height + 1} blocks in the range [{start_height}, {end_height}]")

    # end_height is a zero-indexed value representing the height of the max block we want to process
    # we will batch for [step] block hashes at once due to predictable size of 32,000 bytes.
    # we will take care to include the end_height block by adding 1 but also not to go over the
    # available blocks by a (max) full step during the last iteration.
    end_height = end_height + 1
    for i in range(start_height, end_height, step):
        count = min(step, end_height - i)
        commands = [ [ "getblockhash", height] for height in range(i, i + count) ]
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
            last_block_processed = i + count - 1
        else:
            log.error(f"unable to process all blocks in current batch. [{i}, {i + count - 1}]")
            break

        # save our progress if enough time has passed
        if (time.time() - last_save_time) > (MINUTES_BETWEEN_SAVES * SECONDS_PER_MINUTE):
            save(utxo_set, last_block_processed)
            print(f"progress is saved at block {last_block_processed}!")
            last_save_time = time.time()
    return last_block_processed

# -----------------------------------------------------------------
#                        saving & loading
# -----------------------------------------------------------------

# writes the current utxo set and other stateful properties to files
def save(utxo_set, last_block_processed):
    with DelayedKeyboardInterrupt():
        with open(file_paths[FILE_NAME_UTXO], "w", encoding="utf-8") as utxo_file:
            print("saving UTXOs to file")
            with alive_bar(len(utxo_set)) as progress_bar:
                for output in utxo_set:
                    data = output.serialize()
                    utxo_file.write(f"{data}\n")
                    progress_bar()

        cache = {}
        cache[PROPERTY_NAME_LAST_BLOCK] = last_block_processed
        with open(file_paths[FILE_NAME_CACHE], "w", encoding="utf-8") as cache_file:
            cache_file.write(json.dumps(cache))

# loads the utxo set and other stateful properties from files
def load():
    utxo_set = set()
    last_block_processed = None

    if os.path.exists(file_paths[FILE_NAME_UTXO]):
        with open(file_paths[FILE_NAME_UTXO], "r", encoding="utf-8") as utxo_file:
            print("loading UTXOs from file")
            with alive_bar() as progress_bar:
                for line in utxo_file:
                    output = TXOutput.deserialize(line[:-1]) # remove newline character
                    if output is not None:
                        utxo_set.add(output)

    if os.path.exists(file_paths[FILE_NAME_CACHE]):
        with open(file_paths[FILE_NAME_CACHE], "r", encoding="utf-8") as cache_file:
            cache = json.loads(cache_file.read())
            last_block_processed = cache[PROPERTY_NAME_LAST_BLOCK]
        
    return utxo_set, last_block_processed

# -----------------------------------------------------------------
#                             main
# -----------------------------------------------------------------

TESTING = False
TESTING_HEIGHT = 1000
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

    if start_height < end_height:
        last_block_processed = build_utxo_set(utxo_set, start_height, end_height) or last_block_processed
        save(utxo_set, last_block_processed)

    decode_transaction_scripts(utxo_set)
