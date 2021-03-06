# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## how to interpret this code

this project was written with two, sometimes conflicting, ideas. First, learn the implementation details of Bitcoin while re-learning Python- the second: to create a functional program. The reason these sometimes conflict is because of scope creep- it wasn't necessary for me, for example, to write script-parsing functionality in an attempt to identify different script types automatically when this program chooses to retrieve the block/transaction data in json (`dict`) format. I could have simply read the `type` field under `pubkeyScript` from the beginning.

at one point before Christmas 2021, I decided to put a pin in this and no longer allow scope creep to influence my goal of finishing this project. I will instead fork this project in the future to expand it with features unrelated to the purpose of 'birthday attack', such as a more general blockchain analysis application.

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
pip install secp256k1
```

## tests

from `tests/` directory, simply run
```bash
python -m unittest
```