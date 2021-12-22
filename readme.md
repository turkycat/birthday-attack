# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## why python

re-visiting python after some years to explore new features and libraries.

## todos

- allow spent transactions and new outputs to be built in parts, difference and unioned (in progress)
  - allows for decoding of new transaction scripts
- replace files by database
  - not particularly useful for this program, but the blockchain data would be valuable for others.

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

### dependencies

https://github.com/jgarzik/python-bitcoinrpc \
https://github.com/rsalmei/alive-progress

install using pip
```bash
pip install -r requirements.txt
```

or install manually
```bash
pip install python-bitcoinrpc
pip install alive-progress
```

## tests

from `tests/` directory, simply run
```bash
python -m unittest
```