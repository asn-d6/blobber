## Blobber

blobber packs arbitrary data into [proto-danksharded transactions](https://www.eip4844.com/) and submits them to geth using the JSON-RPC API.

### Usage

Just pipe some data into blobber and it will submit a transaction on your behalf (assuming that the size of the data is less than 256kb):

```
cat weird.pdf | python blobber.py
```

You will need a proto-danksharded geth that listens on 127.0.0.1:8545 to receive the transaction. YMMV but I've been
using the following geth command:

```
./build/bin/geth --allow-insecure-unlock --nodiscover --maxpeers 0 --http.api "eth,web3,personal" --http --http.addr localhost --netrestrict 127.0.0.1/24
```


### Install

You might need a bunch of basic dependencies to run this tool:

```
pip install requests jsonrpcclient
```
