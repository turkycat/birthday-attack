import sys, os, glob, logging, time, json, sqlite3
from transactions.tx import TXOutput, TXInput
from transactions import script
from delayed_keyboard_interrupt import DelayedKeyboardInterrupt
from rpc_controller.rpc_controller import RpcController
from keys.ring import KeyRing
from database.database_controller import DatabaseController

# -----------------------------------------------------------------
#                             globals
# -----------------------------------------------------------------

# file and output related constants
FILE_NAME_CACHE = "cache.json"
FILE_NAME_ERROR = "errors.txt"
FILE_NAME_LOG = "logfile.txt"
FILE_NAME_SCRIPTS = "scripts.txt"
FILE_NAME_MATCHES = "matches.txt"
FILE_NAME_DATABASE = "db.sqlite"

DIR_OUTPUT_RELATIVE = "output"
DIR_OUTPUT_ABSOLUTE = os.path.join(os.getcwd(), DIR_OUTPUT_RELATIVE)
file_paths = {
    FILE_NAME_CACHE: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_CACHE),
    FILE_NAME_ERROR: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_ERROR),
    FILE_NAME_LOG: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_LOG),
    FILE_NAME_MATCHES: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_MATCHES),
    FILE_NAME_SCRIPTS: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_SCRIPTS),
    FILE_NAME_DATABASE: os.path.join(DIR_OUTPUT_ABSOLUTE, FILE_NAME_DATABASE)
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
def process_transaction(rpc, txid, block_height, block_hash):
    inputs = set()
    outputs = set()
    transaction = rpc.getrawtransaction(txid, True, block_hash)

    for vin in transaction["vin"]:
        input = TXInput.from_dictionary(vin)
        if input is not None:
            inputs.add(input)

    for vout in transaction["vout"]:
        output = TXOutput.from_dictionary(transaction["txid"], block_height, vout)
        if output is not None:
            if not (output.script_type == "nonstandard" or output.script_type == "nulldata"):
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
        inputs, outputs = process_transaction(rpc, txid, block_height, block_hash)
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
def save(last_block_processed, keyring):
    with DelayedKeyboardInterrupt():
        cache = {}
        cache[PROPERTY_NAME_LAST_BLOCK] = last_block_processed
        cache[PROPERTY_NAME_PRIVATE_KEY] = keyring.hex()
        with open(file_paths[FILE_NAME_CACHE], "w", encoding="utf-8") as cache_file:
            cache_file.write(json.dumps(cache))

# loads the utxo set and other stateful properties from files
def load():
    last_block_processed = None
    keyring = None

    if os.path.exists(file_paths[FILE_NAME_CACHE]):
        with open(file_paths[FILE_NAME_CACHE], "r", encoding="utf-8") as cache_file:
            cache = json.loads(cache_file.read())
            last_block_processed = cache[PROPERTY_NAME_LAST_BLOCK]
            keyring = KeyRing(cache[PROPERTY_NAME_PRIVATE_KEY])
        
    return last_block_processed, keyring

# -----------------------------------------------------------------
#                            utility
# -----------------------------------------------------------------

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600

def seconds_to_hms(seconds):
    hours = int(seconds / SECONDS_PER_HOUR)
    seconds = seconds % SECONDS_PER_HOUR
    minutes = int(seconds / SECONDS_PER_MINUTE)
    seconds = int(seconds % SECONDS_PER_MINUTE)
    return hours, minutes, seconds

OPTION_CLEAN = "--clean"
SHORT_OPTION_CLEAN = "-c"
OPTION_TARGET = "--target"
SHORT_OPTION_TARGET = "-t"
def evaulate_arguments():
    options = {
        OPTION_CLEAN: False,
        OPTION_TARGET: 0
    }

    index = 1
    while index < len(sys.argv):
        if sys.argv[index] == SHORT_OPTION_CLEAN or sys.argv[index] == OPTION_CLEAN:
            options[OPTION_CLEAN] = True
        elif (sys.argv[index] == SHORT_OPTION_TARGET or sys.argv[index] == OPTION_TARGET) and index + 1 < len(sys.argv):
            index = index + 1
            options[OPTION_TARGET] = int(sys.argv[index])

        index = index + 1
    return options

STAY_BEHIND_BEST_BLOCK_OFFSET = 6
def get_target_block_height(rpc):
    best_block_hash = rpc.getbestblockhash()
    best_block = rpc.getblock(best_block_hash)
    best_block_height = int(best_block["height"])
    target_block_height = best_block_height - STAY_BEHIND_BEST_BLOCK_OFFSET
    return target_block_height


# -----------------------------------------------------------------
#                             main
# -----------------------------------------------------------------

BLOCKS_PER_MILESTONE = 100
BLOCKS_PER_VACUUM = BLOCKS_PER_MILESTONE * 100
FETCH_QUERY = "select * from utxos where target = ? or target = ? or target = ? or target = ?"

if __name__ == "__main__":
    options = evaulate_arguments()
    if options[OPTION_CLEAN]:
        clean_outputs()

    last_block_processed, keyring = load()
    last_block_processed = last_block_processed or 0
    keyring = keyring or KeyRing("34e1fb6c845301f600660c3921b4baf63744f052d0cff22651039ae57bc11a84")
    rpc = RpcController()
    db = DatabaseController(file_paths[FILE_NAME_DATABASE])

    total_milestone_time = 0
    total_update_time = 0
    total_vacuum_time = 0
    key_count = 0
    
    running = True
    while running:
        milestone_start_time = time.time()
        milestone_target = last_block_processed + BLOCKS_PER_MILESTONE
        inputs = set()
        outputs = set()

        try:
            target_block_height = options[OPTION_TARGET] or get_target_block_height(rpc)
            current_target = min(target_block_height, milestone_target)

            while last_block_processed < current_target:
                current_block = last_block_processed + 1
                print(f"reading block {current_block}", end = "\r")
            
                block_inputs, block_outputs = process_block(rpc, current_block)

                # inputs are outputs that have been consumed.
                # the input set will consume outputs that exist in the database only (after first INSERT)
                # but may also consume outputs currently included in the output set, which we can discard.
                # without bringing back the nightmares of discrete math, I'm certain that it's more efficient 
                # to union each set for each block and perform a single difference before updating the database,
                # rather than iterating over N outputs for each M inputs for each K blocks = O(N * M * K)
                # this does mean we will consume more memory between database updates
                inputs.update(block_inputs)
                outputs.update(block_outputs)
                last_block_processed = current_block

            print("-------------------milestone metadata-------------------")
            print("last block processed: ", last_block_processed)
            print("original size of new outputs: ", len(outputs))
            print("original size of spent outputs: ", len(inputs))
            spent_outputs = outputs.intersection(inputs)
            outputs.difference_update(spent_outputs)
            inputs.difference_update(spent_outputs)
            print("outputs created and spent in this milestone: ", len(spent_outputs))
            print("new outputs less spent in this milestone: ", len(outputs))
            print("spent outputs less spent in this milestone: ", len(inputs))
            milestone_end_time = time.time()
            milestone_time = milestone_end_time - milestone_start_time
            total_milestone_time = total_milestone_time + milestone_time
            hours, minutes, seconds = seconds_to_hms(milestone_time)
            print(f"time to process: {minutes} minute(s), and {seconds} second(s)")
            print("---------------------end metadata-----------------------")

            print("updating database...")
            with DelayedKeyboardInterrupt():
                db.update_utxos(inputs, outputs)
                save(last_block_processed, keyring)

                update_end_time = time.time()
                update_time = update_end_time - milestone_end_time
                total_update_time = total_update_time + update_time
                hours, minutes, seconds = seconds_to_hms(update_time)
                print(f"time to write to disk: {minutes} minute(s), and {seconds} second(s)")

                # vacuum every 10 milestones
                if (last_block_processed % BLOCKS_PER_VACUUM == 0):
                    print("vacuuming database...")
                    db.vacuum()
                    vacuum_time = time.time() - update_end_time
                    total_vacuum_time = total_vacuum_time + vacuum_time
                    hours, minutes, seconds = seconds_to_hms(vacuum_time)
                    print(f"time to vacuum: {minutes} minute(s), and {seconds} second(s)")
                    hours, minutes, seconds = seconds_to_hms(total_milestone_time)
                    print(f"total time spent processing: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")
                    hours, minutes, seconds = seconds_to_hms(total_update_time)
                    print(f"total time writing to disk: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")
                    hours, minutes, seconds = seconds_to_hms(total_vacuum_time)
                    print(f"total time vacuuming: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")

            # skip keyring rotation if we haven't reached our target block height yet
            if last_block_processed < target_block_height:
                continue

            next_update_time = time.time() + SECONDS_PER_HOUR
            while time.time() < next_update_time:
                key_count += 1
                print(f"key number {key_count}: current: {keyring.current()}", end = "\r")
                
                uncompressed_pubkey = keyring.public_key(False)
                compressed_pubkey = keyring.public_key(True)
                uncompressed_pubkeyhash = keyring.public_key_hash(False)
                compressed_pubkeyhash = keyring.public_key_hash(True)

                params = (uncompressed_pubkey, compressed_pubkey, uncompressed_pubkeyhash, compressed_pubkeyhash)
                results = db.execute_read_query(FETCH_QUERY, params)
                if len(results) > 0:
                    # holy shit we did it!
                    with open(file_paths[FILE_NAME_MATCHES], "a", encoding = "utf-8") as match_file:
                        text_output = f"match found! private key: {keyring.hex()} with value {keyring.current()}"
                        print(text_output)
                        match_file.write(text_output)
                        match_file.write("\n")

                        for row in results:
                            lines = ["------------------------------------match found!------------------------------------"]
                            lines.append(f"private key: {keyring.hex()}")
                            lines.append(f"dec: {keyring.current()}")
                            lines.append(f"hash: {row[0]}")
                            lines.append(f"vout: {row[1]}")
                            lines.append(f"height: {row[2]}")
                            lines.append(f"value: {row[3]}")
                            lines.append(f"script: {row[4]}")
                            lines.append(f"type: {row[5]}")
                            lines.append(f"target: {row[6]}")
                            lines.append("------------------------------------------------------------------------------------")

                            for line in lines:
                                print(line)
                                match_file.write(line)
                                match_file.write("\n")

                keyring.next()
            print("")
            save(last_block_processed, keyring)

        except KeyboardInterrupt:
            log.info(f"KeyboardInterrupt intercepted at {time.time()}")
            print(f"\nKeyboard interrupt received, stopping...")
            running = False

        # TODO JDF - this whole loop needs a rethink because at the end of last year's development I assumed we'd be spending all idle time running the keyring.
        # may need a way to start and stop, maybe consider a Runner class or something to encapsulate the utxo set builder from the keyring stuff, keyring and utxo can extend
        running = running and last_block_processed < target_block_height
