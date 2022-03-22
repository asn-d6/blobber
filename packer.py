"""
The packer module packs arbitrary bytes into EIP-4844 blobs using the get_blobs_from_data() function (utilizes max
two blobs since that's the limit for a single transaction)

It uses the padding scheme from ISO/IEC 7816-4 to pack the data into the required blob size (see get_padded()). The
padding scheme is real simple but sacrifices a single byte as the padding delimiter. Applications can pick their own
padding format.

It stuffs 31 bytes per field element, but we can do better since a BLS12-381 base field element can fit 254 bits of
data. If we chunk our data on the bit level (every 254 bits) we can do much better packing than what's implemented
below (every 31 bytes == 248 bits). In particular, we get an extra 6 bits per field element, which adds up to about 3kb
per blob.
"""
import sys
import math

FIELD_ELEMENTS_PER_BLOB = 4096 # EIP parameter
# We can pack 31 bytes per field element and we have 4096 field elements per blob.
DATA_PER_BLOB = 31*FIELD_ELEMENTS_PER_BLOB
# How much data we can stuff into a single transaction?
# We can only do two blobs per transaction, and we also reserve one byte for our (non-optimal) padding scheme
MAX_DATA_PER_TX = (DATA_PER_BLOB * 2) - 1

def get_padded(data, length):
    """Pad `data` to `length` using ISO/IEC 7816-4 padding"""
    data_len = len(data)
    pad_len = math.ceil((data_len+1)/length) * length - data_len
    return data + b'\x80' + bytes([0] * (pad_len-1))


def get_blob(data):
    """Get a blob from a bunch of data bytes"""
    # Caller should have given us the right amount of data
    assert(len(data) == DATA_PER_BLOB)

    # Start packing!
    blob = b''
    for i in range(FIELD_ELEMENTS_PER_BLOB):
        # Get the next 31 bytes from our data
        chunk = data[i*31:(i+1)*31]
        # Pad it to 32 bytes with a zero byte and stuff it into the blob
        blob += chunk + b'\x00'

    assert(len(blob) == 32*FIELD_ELEMENTS_PER_BLOB)
    return blob

def get_blobs_from_data(data):
    """Pack a bunch of data into blobs"""
    if len(data) == 0:
        print("[!] Got no data as input. Exiting without doing any work.")
        sys.exit(-1)

    if len(data) > MAX_DATA_PER_TX:
        print("[!] You provided %d bytes, but we can only pack %d bytes into a single tx. Aborting!" % (len(data), MAX_DATA_PER_TX))
        sys.exit(-1)

    # Make sure that size of provided data is not greater than the maximum possible size
    # Subtract one byte below because our padding scheme needs it
    assert(len(data) <= (MAX_DATA_PER_TX))

    # Pad data to be exactly the size of blobs
    data = get_padded(data, DATA_PER_BLOB)

    n_blobs_needed = math.ceil(len(data) / DATA_PER_BLOB)
    print("[*] Got %d bytes of data; we will need %d blobs for that." % (len(data), n_blobs_needed))

    # Pack the data into blobs!
    blobs = []
    for i in range(n_blobs_needed):
        blob = get_blob(data[i*DATA_PER_BLOB:(i+1)*DATA_PER_BLOB])
        blob = "0x" + blob.hex() # hex encode it just like JSON-RPC likes it
        blobs.append(blob)

    return blobs
