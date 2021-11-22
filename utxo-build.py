import json
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# rpcuser and rpcpassword are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('turkyrpc', 'turkypass'))
logfile = open("logfile.txt", "a")
errorfile = open("errors.txt", "w")
logfile.write("---------------------------------------------------------------------------\n")
logfile.write("                           new session                                     \n")
logfile.write("---------------------------------------------------------------------------\n")

best_block_hash = rpc_connection.getbestblockhash()
best_block = rpc_connection.getblock(best_block_hash)
best_block_height = int(best_block["height"])

# this was me remembering how to python, but leaving it for fun
def print_last_20_block_hashes():
    for i in range(best_block_height - 20, best_block_height):
        block_hash = rpc_connection.getblockhash(i)
        block = rpc_connection.getblock(block_hash)
        print(block["hash"])

# TODO add loglevels or replace with a library
def lw(message):
    logfile.write(message)
    logfile.write("\n")

# TODO add loglevels or replace with a library
def le(message):
    print(message)
    logfile.write(message)
    logfile.write("\n")
    errorfile.write(message)
    errorfile.write("\n")

# utxo_set is currently K: tuple( transaction_hash, index ) V: script_pubkey
# TODO: write a class object to encapsulate all the interesting information from unspent outputs 
utxo_set = {}
def process_transactions(transactions, block_hash):
    for i in range(1, len(transactions)):
        txid = transactions[i]
        lw(f"getrawtransaction {txid} 1 {block_hash}")
        raw_tx = rpc_connection.getrawtransaction(txid, True, block_hash)
        
        for input in raw_tx["vin"]:
            spent_output_key = (input["txid"], input["vout"])

            # remove the spent output from our UTXO set
            # one might think that the set must always contain the item-
            # but this isn't true. an input could be a coinbase transaction.
            # coinbase transactions are not retrievable via getrawtransaction
            if spent_output_key in utxo_set:
                lw(f"removing spent output with key: {spent_output_key}")
                utxo_set.pop(spent_output_key)
            else:
                le(f"spent output not found: {spent_output_key}")

        for output in raw_tx["vout"]:
            new_output_key = (txid, output["n"])
            lw(f"adding new output with key: {new_output_key}")
            utxo_set[new_output_key] = output["scriptPubKey"]

# TODO batch RPC calls to bitcoin-cli
def build_utxo_set(start = 0, end = best_block_height):
    for i in range(start, end):
        block_hash = rpc_connection.getblockhash(i)
        block = rpc_connection.getblock(block_hash)
        transactions = block["tx"]

        if len(transactions) == 1:
            le(f"skipping block with only coinbase: {block_hash}")
            continue
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

# using the temporary range 400, 500 while building, eventually we will want to
# periodically check the best block hash and get all blocks up to the current height
UNDER_CONSTRUCTION = False
if __name__ == "__main__":
    start = 0
    end = best_block_height
    if UNDER_CONSTRUCTION:
        start = 400
        end = 500

    build_utxo_set(start, end)
    print_utxo_set()


# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
#commands = [ [ "getblockhash", height] for height in range(20) ]
#block_hashes = rpc_connection.batch_(commands)
#blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
#block_times = [ block["time"] for block in blocks ]
#print(block_times)