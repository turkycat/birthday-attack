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
class TXOutput(object):
    PUSH_ONE_SIZE = 76
    PUSH_TWO_SIZE = 77
    PUSH_FOUR_SIZE = 78

    def __init__(self, hash, index, block = None, script = None):
        self.hash = hash
        self.index = index
        self.block = block
        self.script = script

    def __eq__(self, other):
        return isinstance(other, TXOutput) and (self.hash == other.hash) and (self.index == other.index)

    def __hash__(self):
        return hash((self.hash, self.index))

    def __str__(self):
        return f"<<TXOutput object: {self.hash} {self.index}>>"

    def __repr__(self):
        return f"TXOutput({self.hash}, {self.index}, {self.block}, {self.script})"

    @classmethod
    def decode_hex_bytes_little_endian(cls, num_bytes, hex_string):
        num_characters_expected = num_bytes * 2
        if len(hex_string) < num_characters_expected:
           return None

        total = 0
        byte = 0
        while byte < num_bytes:
            current_byte = int(hex_string[byte * 2 : (byte + 1) * 2], 16) << (8 * byte)
            total = total + current_byte
            byte = byte + 1
        return total

    def decode_script(self):
        if self.script is None:
            return None
        
        # read the size of the first item tin the pubkey script
        # TODO : move this to a subroutine and loop it if necessary to read data pushes
        operation = int(self.script[:2], 16)
        index = 2

        # any value less than 0x4c is the size of data to follow
        data_size = 1
        if operation < self.PUSH_ONE_SIZE:
            data_size = operation
        elif operation == self.PUSH_ONE_SIZE:
            data_size = self.decode_hex_bytes_little_endian(1, self.script[2:])
            index = 4
        elif operation == self.PUSH_TWO_SIZE:
            data_size = self.decode_hex_bytes_little_endian(2, self.script[2:])
            index = 6
        elif operation == self.PUSH_FOUR_SIZE:
            data_size = self.decode_hex_bytes_little_endian(2, self.script[2:])
            index = 10

        pubkey_data = self.script[index:index + data_size]
        index = index + data_size

        # TODO this is very, very incomplete!
        return pubkey_data, self.script[index:]

    def serialize(self):
        info = [self.hash, str(self.index)]
        if self.block is not None:
            info.append(self.block)
            if self.script is not None:
                info.append(self.script)
        return ",".join(info)

    @classmethod
    def deserialize(cls, data):
        info = data.split(",")
        hash = str(info[0])
        index = int(info[1])
        if len(info) > 3:
            block = str(info[2])
            script = str(info[3])
        return TXOutput(hash, index, block, script)