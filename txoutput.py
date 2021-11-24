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
# that is where this jsonpickle library comes in! rather than implementing my own serialization, I'll opt for the speed of a library.

import jsonpickle

# the use of (object) here is redundant in python 3+
# new style class objects are required for jsonpickle
class TxOutput(object):

    def __init__(self, hash, index, script = None):
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
        return f"TxOutput({self.hash}, {self.index}, {self.script})"

def tx_to_json(transaction):
    return jsonpickle.encode(transaction)

def json_to_tx(json_string):
    return jsonpickle.decode(json_string)