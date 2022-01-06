import sys, os, glob, logging, time, json
from transactions.tx import TXOutput, TXInput
from transactions import script
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt
from rpc_controller.rpc_controller import RpcController
from keys.ring import KeyRing
from alive_progress import alive_bar

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

# file and output related constants
FILE_NAME_CACHE = "cache.json"
FILE_NAME_ERROR = "errors.txt"
FILE_NAME_LOG = "logfile.txt"
FILE_NAME_SCRIPTS = "scripts.txt"
FILE_NAME_MATCHES = "matches.txt"
FILE_NAME_UTXO = "utxos.txt"

DIR_OUTPUT_RELATIVE = "output"
DIR_OUTPUT_ABSOLUTE = os.path.join(os.getcwd(), DIR_OUTPUT_RELATIVE)
file_paths = {
    FILE_NAME_CACHE: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_CACHE),
    FILE_NAME_ERROR: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_ERROR),
    FILE_NAME_LOG: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_LOG),
    FILE_NAME_MATCHES: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_MATCHES),
    FILE_NAME_SCRIPTS: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_SCRIPTS),
    FILE_NAME_UTXO: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_UTXO)
}

if not os.path.exists(DIR_OUTPUT_ABSOLUTE):
    os.makedirs(DIR_OUTPUT_ABSOLUTE)

# cache properties
PROPERTY_NAME_LAST_BLOCK = "last_block"
PROPERTY_NAME_PRIVATE_KEY = "private_key"

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
    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.DEBUG)
    info_handler.setFormatter(file_format)
    log.addHandler(info_handler)

ERROR_LOGGING = True
if ERROR_LOGGING:
    error_handler = logging.FileHandler(file_paths[FILE_NAME_ERROR], "a", "utf-8")
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
                scripts_file.write(f"\n{output.serialized_script}\n")

                try:
                    decoded_script = script.decode_script(output.serialized_script)
                    scripts_file.write(f"{decoded_script}\n")
                except script.ScriptDecodingException as err:
                    log.error(output.__repr__())
                    log.error(err)

                scripts_file.write("\n")
                progress_bar()

# interpret a single transaction
def process_transaction(rpc, txid, block_hash):
    inputs = set()
    outputs = set()
    transaction = rpc.getrawtransaction(txid, True, block_hash)

    for vin in transaction["vin"]:
        input = TXInput.from_dictionary(vin)
        if input is not None:
            inputs.add(input)

    for vout in transaction["vout"]:
        output = TXOutput.from_dictionary(transaction["txid"], vout)
        if output is not None:
            outputs.add(output)

    return inputs, outputs

# interprets all transactions from a specific block, returns a union of two sets: inputs consumed and outputs created
# note: as it is possible to consume a new output as an input in the same block, some equiv TXIDs may exist in both sets
def process_block(rpc, block_height):
    block_hash = rpc.getblockhash(block_height)
    block = rpc.getblock(block_hash)
    txids = block["tx"]
    log.info(f"block {block_height} with hash {block_hash} contains {len(txids)} transactions")

    block_inputs = set()
    block_outputs = set()
    for txid in txids:
        inputs, outputs = process_transaction(rpc, txid, block_hash)
        block_inputs = block_inputs.union(inputs)
        block_outputs = block_outputs.union(outputs)
    
    return block_inputs, block_outputs

# -----------------------------------------------------------------
#                        saving & loading
# -----------------------------------------------------------------

def clean_outputs():
    files = glob.glob(DIR_OUTPUT_ABSOLUTE + "/*")
    for file in files:
        try:
            os.remove(file)
        except OSError as err:
            log.error(f"OSError occurred while attempting to delete {file}, {err}")

# writes the current utxo set and other stateful properties to files
def save(utxo_set, last_block_processed, keyring):
    with DelayedKeyboardInterrupt():
        with open(file_paths[FILE_NAME_UTXO], "w", encoding="utf-8") as utxo_file:
            print(f"saving utxos to file at block {last_block_processed}")
            with alive_bar(len(utxo_set)) as progress_bar:
                for output in utxo_set:
                    data = output.serialize()
                    utxo_file.write(f"{data}\n")
                    progress_bar()

        cache = {}
        cache[PROPERTY_NAME_LAST_BLOCK] = last_block_processed
        cache[PROPERTY_NAME_PRIVATE_KEY] = keyring.hex()
        with open(file_paths[FILE_NAME_CACHE], "w", encoding="utf-8") as cache_file:
            cache_file.write(json.dumps(cache))

# loads the utxo set and other stateful properties from files
def load():
    utxo_set = set()
    last_block_processed = None
    keyring = None

    if os.path.exists(file_paths[FILE_NAME_UTXO]):
        with open(file_paths[FILE_NAME_UTXO], "r", encoding="utf-8") as utxo_file:
            print("loading UTXOs from file")
            with alive_bar() as progress_bar:
                for line in utxo_file:
                    output = TXOutput.deserialize(line[:-1]) # remove newline character
                    if output is not None:
                        utxo_set.add(output)
                    progress_bar()

    if os.path.exists(file_paths[FILE_NAME_CACHE]):
        with open(file_paths[FILE_NAME_CACHE], "r", encoding="utf-8") as cache_file:
            cache = json.loads(cache_file.read())
            last_block_processed = cache[PROPERTY_NAME_LAST_BLOCK]
            keyring = KeyRing(cache[PROPERTY_NAME_LAST_BLOCK])
        
    return utxo_set, last_block_processed, keyring

# -----------------------------------------------------------------
#                             main
# -----------------------------------------------------------------

MINUTES_BETWEEN_SAVES = 20.0
SECONDS_PER_MINUTE = 60.0
STAY_BEHIND_BEST_BLOCK_OFFSET = 6

OPTION_CLEAN = "--clean"
SHORT_OPTION_CLEAN = "-c"
def evaulate_arguments():
    options = {
        OPTION_CLEAN: False
    }

    for index in range(1, len(sys.argv)):
        if sys.argv[index] == SHORT_OPTION_CLEAN or sys.argv[index] == OPTION_CLEAN:
            options[OPTION_CLEAN] = True
    return options

TESTING = False
TESTING_HEIGHT = 1000
def get_target_block_height(rpc):
    best_block_hash = rpc.getbestblockhash()
    best_block = rpc.getblock(best_block_hash)
    best_block_height = int(best_block["height"])
    target_block_height = (TESTING and TESTING_HEIGHT) or best_block_height - STAY_BEHIND_BEST_BLOCK_OFFSET
    return target_block_height

if __name__ == "__main__":
    options = evaulate_arguments()
    if options[OPTION_CLEAN]:
        clean_outputs()

    utxo_set, last_block_processed, keyring = load()
    utxo_set = utxo_set or set()
    last_block_processed = last_block_processed or 0
    keyring = keyring or KeyRing("1313131313131313131313131313131313131313131313131313131313131313")
    last_save_time = time.time()
    next_save_time = last_save_time + (MINUTES_BETWEEN_SAVES * SECONDS_PER_MINUTE)
    rpc = RpcController()
    targets = dict()
    
    running = True
    while running:
        try:
            target_block_height = get_target_block_height(rpc)

            while last_block_processed < target_block_height and time.time() < next_save_time:
                current_block = last_block_processed + 1
                print(f"reading block {current_block}", end = "\r")
            
                block_inputs, block_outputs = process_block(rpc, current_block)

                # we must add all new outputs to our primary set first, then subtract spent outputs from that set
                modified_utxo_set = utxo_set.union(block_outputs)
                modified_utxo_set = modified_utxo_set.difference(block_inputs)

                with DelayedKeyboardInterrupt():
                    utxo_set = modified_utxo_set
                    last_block_processed = current_block

            # refresh our targets
            #if time.time() < next_save_time:
            targets.clear()
            for utxo in utxo_set:
                target = utxo.get_pubkeyhash() or utxo.get_pubkey()
                if target is not None:
                    targets[target] = utxo.id()

            count = 0
            while time.time() < next_save_time:
                if keyring.public_key_hash() in targets or keyring.public_key() in targets or \
                    keyring.public_key_hash(False) in targets or keyring.public_key(False) in targets:
                    
                    with open(file_paths[FILE_NAME_MATCHES], "a", encoding = "utf-8") as match_file:
                        text_output = f"match found! {keyring.hex()} with value {keyring.current()}\n"
                        print(text_output)
                        match_file.write(text_output)

                        if keyring.public_key_hash() in targets:
                            text_output = f"{keyring.public_key_hash()} : {targets[keyring.public_key_hash()]}"

                        if keyring.public_key_hash(False) in targets:
                            text_output = f"{keyring.public_key_hash(False)} : {targets[keyring.public_key_hash(False)]}"

                        if keyring.public_key() in targets:
                            text_output = f"{keyring.public_key()} : {targets[keyring.public_key()]}"

                        if keyring.public_key(False) in targets:
                            text_output = f"{keyring.public_key(False)} : {targets[keyring.public_key(False)]}"

                        print(text_output)
                        match_file.write(text_output)

                keyring.next()
                count += 1
                if count % 1000 == 0:
                    print(f"attempted {count} private keys in this rotation, current: {keyring.current()}")


        except KeyboardInterrupt:
            log.info(f"KeyboardInterrupt intercepted at {time.time()}")
            print(f"Keyboard interrupt received, saving and stopping...")
            running = False
            
        save(utxo_set, last_block_processed, keyring)
        last_save_time = time.time()
        next_save_time = last_save_time + (MINUTES_BETWEEN_SAVES * SECONDS_PER_MINUTE)
