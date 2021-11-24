# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## why python

re-visiting python after some years to explore new features and libraries.

## todos

- add a local pip install file
- periodically check the best block hash and get all blocks up to the current height

## dependencies

https://github.com/jgarzik/python-bitcoinrpc \
https://github.com/rsalmei/alive-progress

## setup

```bash
pip install python-bitcoinrpc
pip install alive-progress
pip install -U jsonpickle
```
