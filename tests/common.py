from transactions import tx

UNCOMPRESSED_PUBLIC_KEY = "04aadcac168ef4c4cc7a1165755b1235043c3ee87effbe1b1d00677d684978fa5df6eeca25032ec850336594337daf71845a3f308a92d6261cd82e35e21b112be0"
COMPRESSED_PUBLIC_KEY_01 = "0214f296079b181ab76cd817f8583761d9ba5b00ca46f16eadfab8e0bb3a2b0420"
COMPRESSED_PUBLIC_KEY_02 = "03831cfea00b5cfcd97a12fd14b469d9385140d187d2bd8add9a1044685db9552b"

TRANSACTION_01_HASH = "5a189242e85c9670cefac381de8423c11fd9d4b0ebcf86468282e0fc1fe78fb8"
TRANSACTION_01_INDEX = 0
TRANSACTION_01_BLOCK_HEIGHT = 4
TRANSACTION_01_VALUE = 1240000000
TRANSACTION_01_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
TRANSACTION_0_DECODED_SCRIPT = ["push_data_33", "03bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5", "checksig"]
# transaction 01 block hash 0000000000000a0276cda9be68104843ef907113942fda4d2162355513396291

txid_01 = tx.TXID(TRANSACTION_01_HASH, TRANSACTION_01_INDEX)
txoutput_01 = tx.TXOutput(TRANSACTION_01_HASH, TRANSACTION_01_INDEX, \
    TRANSACTION_01_BLOCK_HEIGHT, TRANSACTION_01_VALUE, TRANSACTION_01_SCRIPT)

TRANSACTION_02_HASH = "8a2ad0f8c17c767234385233f87141e87e1865725c6fe9268c7a72fd3b9618d8"
TRANSACTION_02_INDEX = 0
TRANSACTION_02_BLOCK_HEIGHT = 164221
TRANSACTION_02_VALUE = 98210200000
TRANSACTION_02_SCRIPT = "2103bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5ac"
TRANSACTION_02_DECODED_SCRIPT = ["push_data_33", "03bddd330f9f666ba93f46e6dd2717aba0878e1ecefbe5860373b2524f064a13f5", "checksig"]

txid_02 = tx.TXID(TRANSACTION_02_HASH, TRANSACTION_02_INDEX)
txoutput_02 = tx.TXOutput(TRANSACTION_02_HASH, TRANSACTION_02_INDEX, \
    TRANSACTION_02_BLOCK_HEIGHT, TRANSACTION_02_VALUE, TRANSACTION_02_SCRIPT)

# data from block 300,000
class Block300kData(object):
    block_hash = "000000000000000082ccf8f1557c5d40b21edabb18d2d691cfbf87118bac7254"

    tx_000_hash = "b39fa6c39b99683ac8f456721b270786c627ecb246700888315991877024b983"
    tx_000_serialized = "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4803e09304062f503253482f0403c86d53087ceca141295a00002e522cfabe6d6d7561cf262313da1144026c8f7a43e3899c44f6145f39a36507d36679a8b7006104000000000000000000000001c8704095000000001976a91480ad90d403581fa3bf46086a91b2d9d4125db6c188ac00000000"
    tx_000_deserialized = {
        "in_active_chain": True,
        "txid": "b39fa6c39b99683ac8f456721b270786c627ecb246700888315991877024b983",
        "hash": "b39fa6c39b99683ac8f456721b270786c627ecb246700888315991877024b983",
        "version": 1,
        "size": 157,
        "vsize": 157,
        "weight": 628,
        "locktime": 0,
        "vin": [
            {
                "coinbase": "03e09304062f503253482f0403c86d53087ceca141295a00002e522cfabe6d6d7561cf262313da1144026c8f7a43e3899c44f6145f39a36507d36679a8b700610400000000000000",
                "sequence": 0
            }
        ],
        "vout": [
            {
                "value": 25.04028360,
                "n": 0,
                "scriptPubKey": {
                    "asm": "OP_DUP OP_HASH160 80ad90d403581fa3bf46086a91b2d9d4125db6c1 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a91480ad90d403581fa3bf46086a91b2d9d4125db6c188ac",
                    "address": "1CjPR7Z5ZSyWk6WtXvSFgkptmpoi4UM9BC",
                    "type": "pubkeyhash"
                }
            }
        ],
        "hex": "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4803e09304062f503253482f0403c86d53087ceca141295a00002e522cfabe6d6d7561cf262313da1144026c8f7a43e3899c44f6145f39a36507d36679a8b7006104000000000000000000000001c8704095000000001976a91480ad90d403581fa3bf46086a91b2d9d4125db6c188ac00000000",
        "blockhash": "000000000000000082ccf8f1557c5d40b21edabb18d2d691cfbf87118bac7254",
        "confirmations": 414480,
        "time": 1399703554,
        "blocktime": 1399703554
    }

    tx_001_hash = "7301b595279ece985f0c415e420e425451fcf7f684fcce087ba14d10ffec1121"
    tx_001_serialized = "01000000014dff4050dcee16672e48d755c6dd25d324492b5ea306f85a3ab23b4df26e16e9000000008c493046022100cb6dc911ef0bae0ab0e6265a45f25e081fc7ea4975517c9f848f82bc2b80a909022100e30fb6bb4fb64f414c351ed3abaed7491b8f0b1b9bcd75286036df8bfabc3ea5014104b70574006425b61867d2cbb8de7c26095fbc00ba4041b061cf75b85699cb2b449c6758741f640adffa356406632610efb267cb1efa0442c207059dd7fd652eeaffffffff020049d971020000001976a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac30601c0c060000001976a914fd4ed114ef85d350d6d40ed3f6dc23743f8f99c488ac00000000"
    tx_001_deserialized = {
        "in_active_chain": True,
        "txid": "7301b595279ece985f0c415e420e425451fcf7f684fcce087ba14d10ffec1121",
        "hash": "7301b595279ece985f0c415e420e425451fcf7f684fcce087ba14d10ffec1121",
        "version": 1,
        "size": 259,
        "vsize": 259,
        "weight": 1036,
        "locktime": 0,
        "vin": [
            {
                "txid": "e9166ef24d3bb23a5af806a35e2b4924d325ddc655d7482e6716eedc5040ff4d",
                "vout": 0,
                "scriptSig": {
                    "asm": "3046022100cb6dc911ef0bae0ab0e6265a45f25e081fc7ea4975517c9f848f82bc2b80a909022100e30fb6bb4fb64f414c351ed3abaed7491b8f0b1b9bcd75286036df8bfabc3ea5[ALL] 04b70574006425b61867d2cbb8de7c26095fbc00ba4041b061cf75b85699cb2b449c6758741f640adffa356406632610efb267cb1efa0442c207059dd7fd652eea",
                    "hex": "493046022100cb6dc911ef0bae0ab0e6265a45f25e081fc7ea4975517c9f848f82bc2b80a909022100e30fb6bb4fb64f414c351ed3abaed7491b8f0b1b9bcd75286036df8bfabc3ea5014104b70574006425b61867d2cbb8de7c26095fbc00ba4041b061cf75b85699cb2b449c6758741f640adffa356406632610efb267cb1efa0442c207059dd7fd652eea"
                },
                "sequence": 4294967295
            }
        ],
        "vout": [
            {
                "value": 105.00000000,
                "n": 0,
                "scriptPubKey": {
                    "asm": "OP_DUP OP_HASH160 61cf5af7bb84348df3fd695672e53c7d5b3f3db9 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac",
                    "address": "19vAwujzTjTzJhQQtdQFKeP5u3msLusgWs",
                    "type": "pubkeyhash"
                }
            },
            {
                "value": 259.72990000,
                "n": 1,
                "scriptPubKey": {
                    "asm": "OP_DUP OP_HASH160 fd4ed114ef85d350d6d40ed3f6dc23743f8f99c4 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a914fd4ed114ef85d350d6d40ed3f6dc23743f8f99c488ac",
                    "address": "1Q6NNpHM1pyh6kEqzinBhEgsRc3nmpTGLm",
                    "type": "pubkeyhash"
                }
            }
        ],
        "hex": "01000000014dff4050dcee16672e48d755c6dd25d324492b5ea306f85a3ab23b4df26e16e9000000008c493046022100cb6dc911ef0bae0ab0e6265a45f25e081fc7ea4975517c9f848f82bc2b80a909022100e30fb6bb4fb64f414c351ed3abaed7491b8f0b1b9bcd75286036df8bfabc3ea5014104b70574006425b61867d2cbb8de7c26095fbc00ba4041b061cf75b85699cb2b449c6758741f640adffa356406632610efb267cb1efa0442c207059dd7fd652eeaffffffff020049d971020000001976a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac30601c0c060000001976a914fd4ed114ef85d350d6d40ed3f6dc23743f8f99c488ac00000000",
        "blockhash": "000000000000000082ccf8f1557c5d40b21edabb18d2d691cfbf87118bac7254",
        "confirmations": 414482,
        "time": 1399703554,
        "blocktime": 1399703554
    }

"""
01000000000101cff8c557b3e4e773e216c63d20991b639a814bbd9e8168e47f7fe95373f8cd950100000000ffffffff020000000000000000536a4c50000898970002382324c19216437fdb3bdb2d85e7044d518dbd36d3674acc4c49da5742d5a084caddb468ec6057f24e14e5d6f5af5daa52dc07015365918bdc18d28d32ad8cb5bd6d89823a43e7397651bd6b030000000000160014fbf683cfe18dfeb1c07aa7dad0fd621543cf913302473044022037f4a75c67aa66ba5b2dca566080b54cb3572884177fbbd76aaff358134e0fd0022030e4c0d6f6e7036b114812dfe9835c93e2b1b001b916506978b0ec962fd406d5012102336efc1fee56253fe9bed2d90e6bfe19b9b68c0be301d33bc5993771af0e3bf800000000

01 00 00 00 
00 = no inputs (marker)
01 = segwit (marker)
------
01 = input count
cff8c557 b3e4e773 e216c63d 20991b63 9a814bbd 9e8168e4 7f7fe953 73f8cd95 (reverse this), previous hash
01000000 (reverse this), index = 01 
00 = script size
[]
ffffffff = sequence
02 = output count
------
00000000 00000000 (reverse this), value = 0
53 (script size) = 83
[
    6a4c5000 08989700 02382324 c1921643 7fdb3bdb 2d85e704 4d518dbd 36d3674a
    cc4c49da 5742d5a0 84caddb4 68ec6057 f24e14e5 d6f5af5d aa52dc07 01536591
    8bdc18d2 8d32ad8c b5bd6d89 823a43e7 397651
]
bd6b0300 00000000 (reverse this), value = 00000000 00036bbd = 224,189
16 (script size) = 22
[
    00 14 fbf683cf e18dfeb1 c07aa7da d0fd6215 43cf9133
]
--
from the code, it will read a number of witnesses equal to the input count
from bip-144,
It is encoded as a var_int item count followed by each item encoded as a var_int length followed by a string of bytes. 
The number of script witnesses is not explicitly encoded as it is implied by txin_count.
Empty script witnesses are encoded as a zero byte.
The order of the script witnesses follows the same order as the associated txins.
--
02 = item count
{
    47 item size = 71
    [
        30440220 37f4a75c 67aa66ba 5b2dca56 6080b54c b3572884 177fbbd7 6aaff358
        134e0fd0 022030e4 c0d6f6e7 036b1148 12dfe983 5c93e2b1 b001b916 506978b0
        ec962fd4 06d501
    ]
    21 item size = 33
    [
        02336efc 1fee5625 3fe9bed2 d90e6bfe 19b9b68c 0be301d3 3bc59937 71af0e3b f8
    ]
}
00000000 (lock time)
"""