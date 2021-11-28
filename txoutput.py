# a serializable representation of a bitcoin transaction 
# this class is uniquely identifiable, by hash and by equality, on only the hash and the index
# this allows us to add it to a set with as much transaction detail as we desire, but look it up quickly with only
# the hash and index in order to remove it from the set.
# 
# one of the original reasons to use this pattern was to storing in a set vs a dictionary to helps conserve memory and
# redundancy of adding extra steps when restoring from file -> memory or writing from memory -> file  (extra steps would include
# using (hash, index) tuple as key). Interestingly, the standard 'json' library only encodes types native to JSON.
# meaning- not 'set'. technically, a set is essentially an unordered list with uniqueness property- so this seems a little
# silly to me. further, json.dumps() doesn't even work when the set is converted to a list since this class must be serializable
# and that isn't as simple as just overriding a function. go figure! Python is great, but has some limitations.
# in the end, I want to stick to my guns of keeping the utxo set as small as possible in memory, which means no keys.

KEY_HASH = "hsh"
KEY_INDEX = "idx"
KEY_BLOCK = "blk"
KEY_SCRIPT = "scr"

import json
class TxOutput(object):

    def __init__(self, hash, index, block = None, script = None):
        self.block = block
        self.hash = hash
        self.index = index
        self.script = script

    def __eq__(self, other):
        return isinstance(other, TxOutput) and (self.hash == other.hash) and (self.index == other.index)

    def __hash__(self):
        return hash((self.hash, self.index))

    def __str__(self):
        return f"<<TxOutput object: {self.hash} {self.index}>>"

    def __repr__(self):
        return f"TxOutput({self.hash}, {self.index}, {self.block}, {self.script})"

    def json_encode(self):
        info = {}
        info[KEY_HASH] = self.hash
        info[KEY_INDEX] = self.index
        if self.block is not None:
            info[KEY_BLOCK] = self.block
        if self.script is not None:
            info[KEY_SCRIPT] = self.script
        return json.dumps(info)

    # @classmethod
    # def json_decode(cls, j)
    
class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TxOutput):
            return obj.to_json()

        return json.JSONEncoder.default(self, obj)

class JsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if isinstance(obj, dict):
            if KEY_HASH in obj and KEY_INDEX in obj:
                hash = str(obj[KEY_HASH])
                index = int(obj[KEY_INDEX])
                if KEY_BLOCK in obj:
                    block = obj[KEY_BLOCK]
                if KEY_SCRIPT in obj:
                    script = obj[KEY_SCRIPT]

                return TxOutput(hash, index, block, script)

        return obj