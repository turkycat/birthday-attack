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
#                      transaction processing
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
        if last_block_processed is not None:
            cache[PROPERTY_NAME_LAST_BLOCK] = last_block_processed
        if keyring is not None:
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
            if PROPERTY_NAME_LAST_BLOCK in cache:
                last_block_processed = cache[PROPERTY_NAME_LAST_BLOCK]
            if PROPERTY_NAME_PRIVATE_KEY in cache:
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
OPTION_IMPORT = "--import"
SHORT_OPTION_IMPORT = "-i"
def evaulate_arguments():
    options = {
        OPTION_CLEAN: False,
        OPTION_TARGET: 0,
        OPTION_IMPORT: False
    }

    index = 1
    while index < len(sys.argv):
        if sys.argv[index] == SHORT_OPTION_CLEAN or sys.argv[index] == OPTION_CLEAN:
            options[OPTION_CLEAN] = True
        elif (sys.argv[index] == SHORT_OPTION_TARGET or sys.argv[index] == OPTION_TARGET) and index + 1 < len(sys.argv):
            index = index + 1
            options[OPTION_TARGET] = int(sys.argv[index])
        elif (sys.argv[index] == SHORT_OPTION_IMPORT or sys.argv[index] == OPTION_IMPORT) and index + 1 < len(sys.argv):
            index = index + 1
            options[OPTION_CLEAN] = True
            options[OPTION_IMPORT] = str(sys.argv[index])

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
#                            importing
# -----------------------------------------------------------------

class ImportException(Exception):
    def __init__(self, message):
        super().__init__(message)

# translate output from in3rsha's script into what bitcoin core will use
# fwiw- i prefer the style he uses. <3 in3rsha
type_name_pubkeyhash = "pubkeyhash"
type_name_scripthash = "scripthash"
type_name_pubkey = "pubkey"
type_name_multisig = "multisig"
type_name_witness_v0_keyhash = "witness_v0_keyhash"
type_name_witness_v0_scripthash = "witness_v0_scripthash"
type_name_witness_v1_taproot = "witness_v1_taproot"
type_name_nonstandard = "nonstandard"

p2_type_name_map = {
    "p2pkh": type_name_pubkeyhash,
    "p2sh": type_name_scripthash,
    "p2pk": type_name_pubkey,
    "p2ms": type_name_multisig,
    "p2wpkh": type_name_witness_v0_keyhash,
    "p2wsh": type_name_witness_v0_scripthash,
    "p2tr": type_name_witness_v1_taproot,
    "non-standard": type_name_nonstandard
}

# these variables are used to verify the hex-encoded lengths of the scripts as read from file
# it is used only to provide a warning about unexpected values in the scripts
pubkey_compressed_length = 66
pubkey_uncompressed_length = 130
static_type_lengths = {
    type_name_pubkeyhash: 40,
    type_name_scripthash: 40,
    type_name_witness_v0_keyhash: 44,
    type_name_witness_v0_scripthash: 68,
    type_name_witness_v1_taproot: 68
}

# the 'script' output is a bit strange when decompressed from bitcoin core's leveldb.
# some of the script values are only a subset of the data, as the full script can be 
# inferred from the type. i don't really -need- the full script, but i kinda like
# having them so deal with it. the database schema used in this program defines
# one column for the full script, and one indexed column for "target" with only the 
# pubkey or pubkey hash targets i care about. to keep with this design, i will reconstruct
# the full scripts for the types that need it:
# pubkeyhash: script is pubkey hash160 only.
#             prefix: [ OP_DUP (x76), OP_HASH160 (xa9), OP_PUSHBYTES_20 (x14) ]
#             suffix: [ OP_EQUALVERIFY (x88), OP_CHECKSIG (xac) ]
pubkeyhash_prefix = "76a914"
pubkeyhash_suffix = "88ac"
# scripthash: script is only the hash160.
#             prefix: [ OP_HASH160 (xa9), OP_PUSHBYTES_20 (x14) ]
#             suffix: OP_EQUAL (x87)
scripthash_prefix = "a914"
scripthash_suffix = "87"
# pubkey: script is only pubkey. may be 130(u) (65 bytes) or 66(c) (33 bytes).
#         prefix: one byte size, either 65 (x41) or 33 (x21)
#         suffix: OP_CHECKSIG (xac)
pubkey_compressed_prefix = "21"
pubkey_uncompressed_prefix = "41"
pubkey_suffix = "ac"
#
#
# types requiring no modification:
# multisig: full script included
# witness_v0_keyhash: full witness script included, [ OP_0, OP_PUSHBYTES_20, <20-byte keyhash> ]
# witness_v0_scripthash: full witness script included, [ OP_0, OP_PUSHBYTES_32, <32-byte scripthash> ]
# witness_v1_taproot: full witness script included, [ OP_PUSHNUM_1, OP_PUSHBYTES_32, <32-byte scripthash> ]
# nonstandard: full script included

# import from an output file written using in3rsha's utxo dump
# https://github.com/in3rsha/bitcoin-utxo-dump
# run with -f txid,vout,height,amount,script,type
def import_from_utxo_dump():
    db = DatabaseController(file_paths[FILE_NAME_DATABASE])
    max_block_height = 0
    type_lengths = dict()
    inputs = set()
    outputs = set()
    INSERT_COUNT = 10000
    
    with open(options[OPTION_IMPORT], "r", encoding = "utf-8") as import_file:
        line = import_file.readline()
        if line.find("txid,vout,height,amount,script,type") != 0:
            raise ImportException("input format does not match expected, be sure to run utxodump with '-f txid,vout,height,amount,script,type'")

        line = import_file.readline()
        line_count = 0
        while len(line) > 0:
            line_count += 1
            print(f"importing transaction from line {line_count}", end = "\r")

            fields = line.split(',')
            height = int(fields[2])
            max_block_height = max(max_block_height, height)

            # remap the 'type' as reported by bitcoin-utxo-dump and verify the script length
            # we will still import a transaction that fails this check, but it's useful here
            # as additional information about the quality of our imports
            script = fields[4]
            script_type = p2_type_name_map.get(fields[5][:-1], "unknown") # remove newline
            if script_type in static_type_lengths:
                if len(script) != static_type_lengths[script_type]:
                    print(f"warning: unexpected length for type '{script_type}'. expected {static_type_lengths[script_type]}, actual: {len(script)}")
                    print(line)
            elif script_type == "pubkey":
                if len(script) != pubkey_compressed_length and len(script) != pubkey_uncompressed_length:
                    print(f"warning: unexpected length for type 'pubkey'. expected {pubkey_compressed_length} or {pubkey_uncompressed_length}, actual: {len(script)}")
                    print(line)

            # modify the scripts where necessary, see notes above suffix & prefix definitions
            if script_type == type_name_pubkeyhash:
                script = pubkeyhash_prefix + script + pubkeyhash_suffix
            elif script_type == type_name_scripthash:
                script = scripthash_prefix + script + scripthash_suffix
            elif script_type == type_name_pubkey:
                if len(script) == pubkey_compressed_length:
                    script = pubkey_compressed_prefix + script + pubkey_suffix
                elif len(script) == pubkey_uncompressed_length:
                    script = pubkey_uncompressed_prefix + script + pubkey_suffix

            # txhash = fields[0], vout = fields[1], height = fields[2], amount = fields[3], script = fields[4], script_type = fields[5]
            output = TXOutput(fields[0], int(fields[1]), height, int(fields[3]), script, script_type)
            outputs.add(output)
            if line_count % INSERT_COUNT == 0:
                db.update_utxos(inputs, outputs)
                outputs.clear()

            line = import_file.readline()

    db.update_utxos(inputs, outputs)
    save(max_block_height, None)

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
        
    if options[OPTION_IMPORT]:
        import_from_utxo_dump()

    last_block_processed, keyring = load()
    last_block_processed = last_block_processed or 0
    keyring = keyring or KeyRing("c2cc7fb3997955c46ff39265f8bf22803372eda3fd01e75978f608c241e68abf")
    rpc = RpcController()
    db = DatabaseController(file_paths[FILE_NAME_DATABASE])

    total_milestone_time = 0
    total_update_time = 0
    total_vacuum_time = 0
    start_key_count = 0
    key_count = 0
    
    running = True
    while running:
        milestone_start_time = time.time()
        milestone_target = last_block_processed + BLOCKS_PER_MILESTONE
        milestone_start_block = last_block_processed
        inputs = set()
        outputs = set()

        # -----------------------------------------------------------------
        #                     read blockchain updates
        # -----------------------------------------------------------------
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

            # print a more detailed milestone message if we're updating large amounts of blocks
            if last_block_processed < target_block_height:
                print("-------------------milestone metadata-------------------")
                print("last block processed:", last_block_processed)
                print("original size of new outputs:", len(outputs))
                print("original size of spent outputs:", len(inputs))
                spent_outputs = outputs.intersection(inputs)
                outputs.difference_update(spent_outputs)
                inputs.difference_update(spent_outputs)
                print("outputs created and spent in this milestone:", len(spent_outputs))
                print("new outputs less spent in this milestone:", len(outputs))
                print("spent outputs less spent in this milestone:", len(inputs))
                milestone_end_time = time.time()
                milestone_time = milestone_end_time - milestone_start_time
                total_milestone_time = total_milestone_time + milestone_time
                hours, minutes, seconds = seconds_to_hms(milestone_time)
                print(f"time to process: {minutes} minute(s), and {seconds} second(s)")
                print("---------------------end metadata-----------------------")
            else:
                print("last block processed:", last_block_processed)

            print("updating database...")
            with DelayedKeyboardInterrupt():
                db.update_utxos(inputs, outputs)
                save(last_block_processed, keyring)

            # more of those extra messages for large block updates
            if last_block_processed < target_block_height:
                update_end_time = time.time()
                update_time = update_end_time - milestone_end_time
                total_update_time = total_update_time + update_time
                hours, minutes, seconds = seconds_to_hms(update_time)
                print(f"time to write to disk: {minutes} minute(s), and {seconds} second(s)")

                # TODO: update vacuum logic
                # if (last_block_processed % BLOCKS_PER_VACUUM == 0):
                #     print("vacuuming database...")
                #     db.vacuum()
                #     vacuum_time = time.time() - update_end_time
                #     total_vacuum_time = total_vacuum_time + vacuum_time
                #     hours, minutes, seconds = seconds_to_hms(vacuum_time)
                #     print(f"time to vacuum: {minutes} minute(s), and {seconds} second(s)")
                #     hours, minutes, seconds = seconds_to_hms(total_milestone_time)
                #     print(f"total time spent processing: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")
                #     hours, minutes, seconds = seconds_to_hms(total_update_time)
                #     print(f"total time writing to disk: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")
                #     hours, minutes, seconds = seconds_to_hms(total_vacuum_time)
                #     print(f"total time vacuuming: {hours} hour(s), {minutes} minute(s), and {seconds} second(s)")

            # skip keyring rotation if we haven't reached our target block height yet
            if last_block_processed < target_block_height:
                continue

        except IOError as err:
            message = "RPC failure. waiting 1 minute before trying again..."
            last_block_processed = milestone_start_block
            print(message)
            log.error(message)
            time.sleep(SECONDS_PER_MINUTE)
            continue

        except KeyboardInterrupt:
            log.info(f"KeyboardInterrupt intercepted at {time.time()}")
            print(f"\nKeyboard interrupt received, stopping...")

            # we intentionally do not want to save here as we will record
            # a last_block_processed which is not persisted in the database
            running = False
            continue

        # -----------------------------------------------------------------
        #                           key rotation
        # -----------------------------------------------------------------
        try:
            next_update_time = time.time() + SECONDS_PER_HOUR
            start_key_count = key_count
            print("rotating keys...")
            while time.time() < next_update_time:
                key_count += 1
                print(f"key number {key_count}: current: {keyring.hex()}", end = "\r")
                
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
            print(f"{key_count - start_key_count} private keys generated in the last period")
            save(last_block_processed, keyring)

        except KeyboardInterrupt:
            log.info(f"KeyboardInterrupt intercepted at {time.time()}")
            print(f"\nKeyboard interrupt received, stopping...")
            
            # save if we were interrupted while rotating keys
            if key_count > start_key_count:
                save(last_block_processed, keyring)

            running = False
