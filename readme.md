# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## todos

- add a class to store interesting transaction data
- change utxo printing to instead use a serializable class object
- create method for reading in the utxo set from the file and saving our place
- add a local pip install file

## dependencies

https://github.com/jgarzik/python-bitcoinrpc
https://github.com/rsalmei/alive-progress

## setup

```bash
pip install python-bitcoinrpc
```
