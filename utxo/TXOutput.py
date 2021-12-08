import re
import utxo.opcode as opcode
from enum import Enum

# note that technically this will match ["push_size_65", "02____32bytes____"] or vice-versa
# however, it should not be necessary to break these into seperate templates because that script would be invalid
p2pk_script_template = [re.compile(r"^push_size_(?:65|33)$"), re.compile("^0(?:4[0-9a-fA-F]{128}$|[23][0-9a-fA-F]{64})$"), re.compile(r"^checksig$")]

p2pkh_script_template = [re.compile(r"^dup$"), re.compile(r"^hash160$"), re.compile(r"^push_size_20$"), re.compile("^[0-9a-fA-F]{40}$"), re.compile(r"^equalverify$"), re.compile(r"^checksig$")]

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

    @classmethod
    def determine_script_type(cls, decoded_script):
        
        if decoded_script is None or len(decoded_script) == 0:
            return ScriptType.NONE

        # test script against P2PKH template
        if len(decoded_script) == len(p2pkh_script_template):
            match = True
            for i in range(0, len(p2pkh_script_template)):
                match = match and p2pkh_script_template[i].match(decoded_script[i])
            if match:
                return ScriptType.P2PKH

        # test script against P2PK template
        if len(decoded_script) == len(p2pk_script_template):
            match = True
            for i in range(0, len(p2pk_script_template)):
                # if match is set to None it will never call .match again, although loop continues ¯\_(ツ)_/¯
                match = match and p2pk_script_template[i].match(decoded_script[i])
            if match:
                return ScriptType.P2PK

        # TODO: other script types
        return ScriptType.UNKNOWN

    def decode_script(self):
        if self.script is None:
            return None

        decoded_script = []
        # Since 2 characters = 1 byte, I'm interested to see if we get any odd script sizes or if  it is handled correctly.
        # Rather than dissect the Bitcoin Core code, I'll print out something special temporarily. assuming we can prefix 0 to correct ?
        if len(self.script) % 2 == 1:
            decoded_script.append("ODD SCRIPT LENGTH CORRECTED") # TODO: remove this, obviously
            self.script = "0" + self.script
        
        script_position = 0
        while script_position < len(self.script):
            # read two characters (one byte) to determine current operation
            operation = int(self.script[script_position : script_position + 2], 16)
            script_position = script_position + 2

            # add the name of the operation to the decoded script
            decoded_script.append(opcode.names[operation])
            
            # if the opcode isn't data, there is nothing else to do
            if operation > opcode.PUSH_FOUR_SIZE:
                continue

            data_size = 1
            if operation < opcode.PUSH_ONE_SIZE:
                data_size = operation
            elif operation == opcode.PUSH_ONE_SIZE:
                data_size = self.decode_hex_bytes_little_endian(1, self.script[script_position:])
                script_position = script_position + 2
            elif operation == opcode.PUSH_TWO_SIZE:
                data_size = self.decode_hex_bytes_little_endian(2, self.script[script_position:])
                script_position = script_position + 4
            elif operation == opcode.PUSH_FOUR_SIZE:
                data_size = self.decode_hex_bytes_little_endian(4, self.script[script_position:])
                script_position = script_position + 8

            if data_size is None:
                raise ScriptLengthShorterThanExpected(len(decoded_script) + 1, opcode.names[operation], self.script, decoded_script)

            number_of_characters_to_read = 2 * data_size
            data = self.script[script_position : script_position + number_of_characters_to_read]
            script_position = script_position + number_of_characters_to_read
            decoded_script.append(data)

        script_type = TXOutput.determine_script_type(decoded_script)
        return decoded_script, script_type

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

class ScriptType(Enum):
    NONE = 0
    UNKNOWN = 1
    P2PK = 2
    P2PKH = 3
    P2SH = 4

class ScriptDecodingException(Exception):
    def __init__(self, message):
        super().__init__(message)

class ScriptLengthShorterThanExpected(ScriptDecodingException):
    def __init__(self, param_number, opcode, script, decoded_script_so_far):
        message = f"param number {param_number} is {opcode} but failed to read required data\n{script}\n{decoded_script_so_far}"
        super().__init__(message)