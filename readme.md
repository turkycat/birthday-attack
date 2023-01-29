# birthday attack

an exploratory script to build the UTXO set from RPC commands (or dump file) and attempt to collide by randomizing private keys

it's basically impossible. should be fun, though

## setup

### bitcoin core configuration

verify your bitcoin.conf file contains
```
rpcuser=<some username>
rpcpassword=<some password>
rpcservertimeout=<some value>
```

I typically set my the `rpcservertimeout` value high, such as 1200. However, 30 (the default) is fine with the use of `RpcController`.

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

## importing
I *strongly recommend* using the import feature to bootstrap this program. reading every single block from rpc takes a _**long time**_. 

in3rsha's bitcoin-utxo-dump can be used to dump the current state of the blockchain. the project can be found here:

https://github.com/in3rsha/bitcoin-utxo-dump

as of Jan 28, 2023- I've fixed a bug in this project, and until my pull request is merged by in3rsha, I have to recommend using my version:

https://github.com/turkycat/bitcoin-utxo-dump

follow the instructions in the repo to build or install bitcoin-utxo-dump, point it at a copy of your chainstate folder and run with the following parameter to get the proper format for importing: `-f txid,vout,height,amount,script,type`

the program will output a file named `utxodump.csv`, which you should then pass as an argument using the `--import` switch. IE
```
python birthday-attack.py --import ./utxodump.csv
```

importing will force clean the outputs folder (the same as running with `--clean`)- so any existing state you may have in that folder that you wish to preserve should be backed up before importing.

## RpcController

This repository contains an `RpcController` class which wraps the behavior of `python-bitcoinrpc` making it much easier to use. An RPC connection will be established automatically and maintained. If the connection is severed either through timeout or failure, reconnection attempts will be made. All RPC exceptions are caught and managed by the controller, making usage in a primary application much easier and cleaner, although errors will not be immediately surfaced.

To configure `RpcController`, edit `config.py` in the module directory to define your authentication credentials.

note: any time the RPC connection times out, you will see this error. It is normal, as the connection will be re-established automatically.

```bash
IO Error [Errno 32] Broken pipe
```

## pick a random starting point for keyring

paste output from the following command to pick a truly random starting point for target matching. either overwrite the saved value in `cache.json` or replace the value in the `KeyRing` initialization in `__main__`

TODO: add a switch to read this random value instead of hardcoding it

```bash
$ dd if=/dev/urandom bs=32 count=1 2>/dev/null | xxd -p | tr -d '\n'
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

(`hash`, `idx`, `height`) is used as a composite primary key for this database. normally, `hash` and `idx` should suffice to identify a transaction (and only those two values are used when *removing* spent outputs from the database)- but `height` was also added as part of the primary key due to some early coinbase transactions having the same transaction hash.

example of a duplicate transaction hash:

`e3bf3d07d4b0375638d5f1db5255fe07ba2c4cb067cd81b84ee974b6585fb468` from block [91722](https://mempool.space/block/00000000000271a2dc26e7667f8419f2e15416dc6955e5a6c6cdf3f2574dd08e)

`e3bf3d07d4b0375638d5f1db5255fe07ba2c4cb067cd81b84ee974b6585fb468` from block [91880](https://mempool.space/block/00000000000743f190a18c5577a3c2d2a1f610ae9601ac046a38084ccb7cd721)



## tests

from `tests/` directory, simply run
```bash
python -m unittest
```