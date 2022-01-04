import transactions.opcode as opcode
import transactions.script as script

# a serializable representation of a bitcoin transaction 
# this class is uniquely identifiable, by hash and by equality, on only the hash and the index
# this allows us to add it to a set with as much transaction detail as we desire, but look it up quickly with only
# the hash and index in order to remove it from the set.
# 
# one of the original reasons to use this pattern was to store in a set vs a dictionary to help conserve memory and
# redundancy of adding extra steps when restoring from file -> memory or writing from memory -> file. Interestingly,
# the standard 'json' library only encodes types native to JSON... meaning- not 'set'. technically, a set is essentially an
# unordered list with uniqueness property- so this seems a little silly to me. further, json.dumps() doesn't even work when
# the set is converted to a list since this class must be serializable. I went through the process of doing this, but in the
# end it was overly complicated and actually created more problems. go figure! Python is great, but has some limitations.
# in the end, I want to stick to my guns of keeping the utxo set as small as possible in memory, which means no keys.
# since JSON can be ill formed with so much as a single extra comma at the end of the set, and because I want to be able to
# frequently save/load progress with a file with a large set of UTXOs, I'll serialize one transaction per line.
class TXID(object):

    def __init__(self, hash, index):
        self.hash = hash
        self.index = index

    def __hash__(self):
        return hash((self.hash, self.index))

    def __eq__(self, other):
        return isinstance(other, TXID) and (self.hash == other.hash) and (self.index == other.index)

    def __str__(self):
        return f"<<Transaction object: {self.hash} {self.index}>>"

    def __repr__(self):
        return f"Transaction({self.hash}, {self.index})"

SATS_PER_BITCOIN  = 100,000,000
class TXOutput(TXID):

    def __init__(self, hash, index, value_in_sats, serialized_script):
        super().__init__(hash, index)
        self.serialized_script = serialized_script

        if type(value_in_sats) is float:
            value_in_sats = int(value_in_sats * SATS_PER_BITCOIN)
        self.value_in_sats = value_in_sats

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return f"<<TXOutput object: {self.hash} {self.index}, {self.value_in_sats}, {self.serialized_script}>>"

    def __repr__(self):
        return f"TXOutput({self.hash}, {self.index}, {self.value_in_sats}, {self.serialized_script})"

    def serialize(self):
        info = [self.hash, str(self.index), str(self.value_in_sats), self.serialized_script]
        return ",".join(info)

    @classmethod
    def deserialize(cls, data):
        info = data.split(",")
        if len(info) < 4:
            return None

        hash = str(info[0])
        index = int(info[1])
        value_in_sats = int(info[2])
        script = str(info[3])
        return TXOutput(hash, index, value_in_sats, script)

class TXInput(TXID):

    def __init__(self, hash, index, serialized_scriptSig = None, witness = None):
        super().__init__(hash, index)
        self.serialized_scriptSig = serialized_scriptSig

        # list, witness[0] = sig, witness[1] = compressed pubkey
        self.witness = witness

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return f"<<TXInput object: {self.hash} {self.index}, {self.serialized_scriptSig}, {self.witness}>>"

    def __repr__(self):
        return f"TXInput({self.hash}, {self.index}, {self.serialized_scriptSig}, {self.witness})"

    @classmethod
    def from_dictionary(cls, input_data):
        hash = input_data["txid"]
        index = input_data["vout"]

        if input_data.get("txinwitness"):
            return TXInput(hash, index, witness = input_data["txinwitness"])

        return TXInput(hash, index, input["scriptSig"]["hex"])
