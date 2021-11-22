# birthday attack

an exploratory script to build the UTXO set from RPC commands and attempt to collide by randomizing private keys

yes, I know it's basically impossible. should be fun, though

## todos

- batch RPC calls to bitcoin-cli
- add a class to store interesting transaction data
- replace le and lw with a logger class
- change utxo printing to instead use a serializable class object
- create method for reading in the utxo set from the file and saving our place
- print out progress instead of all the output

## dependencies

https://github.com/jgarzik/python-bitcoinrpc

## setup

```bash
pip install python-bitcoinrpc
```
