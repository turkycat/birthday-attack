import os
import json
import logging
import time
from utxo.TXOutput import TXOutput, ScriptDecodingException
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt
from rpc_controller.rpc_controller import RpcController
from alive_progress import alive_bar

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

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
def process_transactions(rpc, utxo_set, txids, block_hash):
    for txid in txids:
        transaction = rpc.getrawtransaction(txid, True, block_hash)
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

def process_block(rpc, utxo_set, block_height):
    block_hash = rpc.getblockhash(block_height)
    block = rpc.getblock(block_hash)
    txids = block["tx"]
    log.info(f"block {block_height} with hash {block_hash} contains {len(txids)} transactions")
    if process_transactions(rpc, utxo_set, txids, block_hash):
        return block_height

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

MINUTES_BETWEEN_SAVES = 20.0
SECONDS_PER_MINUTE = 60.0
STAY_BEHIND_BEST_BLOCK_OFFSET = 6

def get_target_block_height(rpc):
    best_block_hash = rpc.getbestblockhash()
    best_block = rpc.getblock(best_block_hash)
    best_block_height = int(best_block["height"])
    target_block_height = (TESTING and TESTING_HEIGHT) or best_block_height - STAY_BEHIND_BEST_BLOCK_OFFSET
    return target_block_height

TESTING = True
TESTING_HEIGHT = 1000
if __name__ == "__main__":
    utxo_set, last_block_processed = load()
    utxo_set = utxo_set or set()
    last_block_processed = last_block_processed or 0
    last_save_time = time.time()
    next_save_time = last_save_time + (MINUTES_BETWEEN_SAVES * SECONDS_PER_MINUTE)
    rpc = RpcController()

    target_block_height = get_target_block_height(rpc)
    running = True
    while running:
        while last_block_processed < target_block_height and time.time() < next_save_time:
            try:
                last_block_processed = process_block(rpc, utxo_set, last_block_processed + 1) or last_block_processed
            except KeyboardInterrupt:
                log.info(f"KeyboardInterrupt intercepted at {time.time()}")
                print(f"Keyboard interrupt received, saving and stopping...")
                running = False
                break
            
        save(utxo_set, last_block_processed)
        last_save_time = time.time()
        next_save_time = last_save_time + (MINUTES_BETWEEN_SAVES * SECONDS_PER_MINUTE)
        target_block_height = get_target_block_height(rpc)

        # this is here to prevent infinite looping over the save functionality and is temporary.
        # In the future, we will spend the remaining time trying to generate collisions with
        # the utxo set and so the loop is designed with that in mind.
        if last_block_processed >= target_block_height:
            running = False

    # decode_transaction_scripts(utxo_set)
