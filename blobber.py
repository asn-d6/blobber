import sys
import logging

import requests
from jsonrpcclient import request, parse, Ok

url = 'http://localhost:8545' # url of my geth node

### Get account
response = requests.post(url, json=request('eth_accounts'))
parsed = parse(response.json())
if not isinstance(parsed, Ok):
    logging.error(parsed.message)
    sys.exit(1)
my_address = parsed.result[0]
print("[*] Going with address: %s" % (my_address))

### Unlock account
### XXX need to call geth with --allow-insecure-unlock
response = requests.post(url, json=request('personal_unlockAccount', params=(my_address, '')))
assert(isinstance(parsed, Ok))

### Get nonce
response = requests.post(url, json=request('eth_getTransactionCount', params=(my_address, 'latest')))
parsed = parse(response.json())
if not isinstance(parsed, Ok):
     logging.error(parsed.message)
     sys.exit(1)
nonce = parsed.result[0]
print("[*] Going with nonce: %s" % (nonce))

# Create some blobs
blob1_data = b'\x42'*4096*32
blob1 = "0x" + blob1_data.hex()

### Create transaction
tx_params = {
    'from': my_address,
    'to' : '0xae64071b92ae1573ac9b5f6a0dc3bb1cfd5121ef',
    'nonce' : hex(int(nonce)),
    'data' : "0xdeadbeef",
    'blobs' : [blob1],
    'maxFeePerGas' : hex(12000),
    'maxPriorityFeePerGas' : hex(12000),
    'gas' : hex(20000)
}

# Pass the transaction to be signed
response = requests.post(url, json=request('eth_signTransaction', params=[tx_params]))
parsed = parse(response.json())
assert(isinstance(parsed, Ok))
raw_tx = parsed.result['raw']
#print("[*] Got the raw tx: %s" % (raw_tx))
print(parsed)

# Push the signed transaction to the interwebs
response = requests.post(url, json=request('eth_sendRawTransaction', params=([raw_tx])))
parsed = parse(response.json())
print("[*] Just sent something and got: %s" % (parsed.message))
