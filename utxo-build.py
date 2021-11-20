from json import decoder
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# rpcuser and rpcpassword are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('turkyrpc', 'turkypass'))
logfile = open("logfile.txt", "a")
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

def lw(message):
    print(message)
    logfile.write(message)
    logfile.write("\n")

utxo_set = {}
def process_transactions(transactions, block_hash):
    for i in range(1, len(transactions)):
        tx_hash = transactions[i]
        lw(str.format("getrawtransaction {0} 1 {1}", tx_hash, block_hash))
        raw_tx = rpc_connection.getrawtransaction(tx_hash, True, block_hash)
        lw(str(raw_tx))

for i in range(400, 500):
    block_hash = rpc_connection.getblockhash(i)
    block = rpc_connection.getblock(block_hash)
    transactions = block["tx"]
    if len(transactions) == 1:
        lw("skipping block with only coinbase")
        continue

    process_transactions(transactions, block_hash)
    
    



# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
#commands = [ [ "getblockhash", height] for height in range(20) ]
#block_hashes = rpc_connection.batch_(commands)
#blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
#block_times = [ block["time"] for block in blocks ]
#print(block_times)