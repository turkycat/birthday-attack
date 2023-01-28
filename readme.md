# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## how to interpret this code

this project was written with two, sometimes conflicting, ideas. First, learn the implementation details of Bitcoin while re-learning Python- the second: to create a functional program. The reason these sometimes conflict is because of scope creep- it wasn't necessary for me, for example, to write script-parsing functionality in an attempt to identify different script types automatically when this program chooses to retrieve the block/transaction data in json (`dict`) format. I could have simply read the `type` field under `pubkeyScript` from the beginning. I did this to prove that I could interpret these scripts and arrive at my own conclusion to the type.

## setup

### bitcoin core configuration

verify your bitcoin.conf file contains
```
rpcuser=<some username>
rpcpassword=<some password>
rpcservertimeout=<some value>
```

I typically set my the `rpcservertimeout` value high, such as 1200. However, 30 (the default) is fine with the use of `RpcController`.

### RpcController

This repository contains an `RpcController` class which wraps the behavior of `python-bitcoinrpc` making it much easier to use. An RPC connection will be established automatically and maintained. If the connection is severed either through timeout or failure, reconnection attempts will be made. All RPC exceptions are caught and managed by the controller, making usage in a primary application much easier and cleaner, although errors will not be immediately surfaced.

To configure `RpcController`, edit `config.py` in the module directory to define your authentication credentials.

note: any time the RPC connection times out, you will see this error. It is normal, as the connection will be re-established automatically.

```bash
IO Error [Errno 32] Broken pipe
```

### dependencies

https://github.com/jgarzik/python-bitcoinrpc \
https://github.com/rsalmei/alive-progress

install using pip
```bash
pip install -r requirements.txt
```

or install manually
```bash
pip install bitcoinrpc
pip install python-bitcoinrpc
pip install secp256k1
```

## output

an `output` directory will automatically be created containing a json cache file for storing program state, an `errors.txt` file, and an sqlite database containing the unspent transactions.

### sqlite database

each row contains a single utxo.

| column | type | description | 
|--------|------|-------------|
|hash|text|transaction hash for the output|
|vout|integer|index for the output
|height|integer|block height containing this transaction
|amount|integer|value of this output, in sats
|script|text|the full scriptPubKey that 'locks' this transaction
|type|text|the type as described by bitcoin core. IE- 'pubkeyhash', 'multisig', 'witness_v0_keyhash' etc
|target|text|the target pubkey or pubkey hash, should always be a substring of the script

(`hash`, `idx`, `block_hash`) is used as a composite primary key for this database. normally, `hash` and `idx` should suffice to identify a transaction (and only those two values are used when *removing* spent outputs from the database)- but `block_hash` was also added as part of the primary key due to some early coinbase transactions having the same transaction hash.

example of a duplicate transaction hash:

`e3bf3d07d4b0375638d5f1db5255fe07ba2c4cb067cd81b84ee974b6585fb468` from block [91722](https://mempool.space/block/00000000000271a2dc26e7667f8419f2e15416dc6955e5a6c6cdf3f2574dd08e)

`e3bf3d07d4b0375638d5f1db5255fe07ba2c4cb067cd81b84ee974b6585fb468` from block [91880](https://mempool.space/block/00000000000743f190a18c5577a3c2d2a1f610ae9601ac046a38084ccb7cd721)



## tests

from `tests/` directory, simply run
```bash
python -m unittest
```