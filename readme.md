# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## why python

re-visiting python after some years to explore new features and libraries.

## todos

- add a local pip install file
- periodically check the best block hash and get all blocks up to the current height
- allow spent transactions and new outputs to be built in parts, difference and unioned
  - allows for keyboard interrupt to trigger a save without distorting current set
  - allows for decoding of new transaction scripts

## dependencies

https://github.com/jgarzik/python-bitcoinrpc \
https://github.com/rsalmei/alive-progress

## setup

set `bitcoin.conf` property `rpcservertimeout=1200` to guarantee that the RPC connection doesn't get terminated early. if this is undesirable or impossible, the `utxo_build.py` should be modified to reconnect when `IOError` is caught or reconnect before each new batch of block hashes is retrieved as default timeouts period of 30s can occur when saving/loading progress.

```bash
pip install python-bitcoinrpc
pip install alive-progress
```
