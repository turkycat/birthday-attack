import re
import transactions.opcode as opcode
from enum import Enum

NUM_CHARACTERS_PER_BYTE = 2

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
class Transaction(object):

    def __init__(self, hash, index):
        self.hash = hash
        self.index = index

    def __hash__(self):
        return hash((self.hash, self.index))

    def __eq__(self, other):
        return isinstance(other, Transaction) and (self.hash == other.hash) and (self.index == other.index)

    def __str__(self):
        return f"<<Transaction object: {self.hash} {self.index}>>"

    def __repr__(self):
        return f"Transaction({self.hash}, {self.index})"

    @classmethod
    def decode_hex_bytes_little_endian(cls, num_bytes, hex_string):
        characters_expected = num_bytes * NUM_CHARACTERS_PER_BYTE
        if len(hex_string) < characters_expected:
            raise ScriptLengthShorterThanExpected(num_bytes, hex_string)

        total = 0
        byte = 0
        while byte < num_bytes:
            current_byte = int(hex_string[byte * 2 : (byte + 1) * 2], 16) << (8 * byte)
            total = total + current_byte
            byte = byte + 1
        return total

    @classmethod
    def decode_script(self, serialized_script):
        if serialized_script is None:
            return None

        decoded_script = []
        script_position = 0
        while script_position < len(serialized_script):
            # read two characters (one byte) to determine current operation
            operation = int(serialized_script[script_position : script_position + NUM_CHARACTERS_PER_BYTE], 16)
            script_position = script_position + NUM_CHARACTERS_PER_BYTE

            # add the name of the operation to the decoded script
            decoded_script.append(opcode.names[operation])
            
            # if the opcode is zero data or no data, there is nothing else to do
            if operation == opcode.PUSH_SIZE_0 or operation > opcode.PUSH_FOUR_SIZE:
                continue

            data_size = 0
            if operation < opcode.PUSH_ONE_SIZE:
                data_size = operation
            else:
                if operation == opcode.PUSH_ONE_SIZE:
                    bytes_to_decode = 1
                elif operation == opcode.PUSH_TWO_SIZE:
                    bytes_to_decode = 2
                else: #opcode.PUSH_FOUR_SIZE
                    bytes_to_decode = 4

                data_size = self.decode_hex_bytes_little_endian(bytes_to_decode, serialized_script[script_position:])
                script_position = script_position + (NUM_CHARACTERS_PER_BYTE * bytes_to_decode)

            number_of_characters_to_read = NUM_CHARACTERS_PER_BYTE * data_size
            data = serialized_script[script_position : script_position + number_of_characters_to_read]
            script_position = script_position + number_of_characters_to_read
            decoded_script.append(data)

        return decoded_script

class TXOutput(Transaction):

    def __init__(self, hash, index, block_height, value, script):
        super().__init__(hash, index)
        self.block_height = block_height
        self.value = value
        self.serialized_script = script

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return f"<<TXOutput object: {self.hash} {self.index}, {self.block_height}, {self.serialized_script}, {self.value}>>"

    def __repr__(self):
        return f"TXOutput({self.hash}, {self.index}, {self.block_height}, {self.serialized_script}, {self.value})"

    @classmethod
    def locking_script_is_multisig(cls, decoded_script):
        if decoded_script is None or len(decoded_script) == 0:
            return ScriptType.NONE

        """
        note that this function only evaluates standard M-of-N multisig patterns
        """

        # verify OP_PUSH_POSITIVE_M, extract M
        match = ScriptTypeTemplate.POSITIVE_DIGIT.match(decoded_script[0])
        if not match:
            return ScriptType.UNKNOWN, 0, 0
        required_sigs = int(match.group(1))

        # read some number of public keys
        index = 1
        while index < len(decoded_script) and ScriptTypeTemplate.PUBLIC_KEY.match(decoded_script[index]):
            index += 1
        total_keys = index - 1

        # verify OP_PUSH_POSITIVE_N, extract N
        match = ScriptTypeTemplate.POSITIVE_DIGIT.match(decoded_script[index])
        if not match:
            return ScriptType.UNKNOWN, 0, 0
        expected_total_keys = int(match.group(1))
        index += 1

        MAX_STANDARD_PUBLIC_KEYS = 3
        if not (expected_total_keys == total_keys and required_sigs <= total_keys and \
            total_keys <= MAX_STANDARD_PUBLIC_KEYS and required_sigs <= MAX_STANDARD_PUBLIC_KEYS and \
            index == (len(decoded_script) - 1) and decoded_script[index] == opcode.names[opcode.CHECKMULTISIG]):
            # this is really unexpected and is more of a "invalid script" case
            # ScriptDecodingException might be better here but I'd rather see this turn up in the unknown set.
            return ScriptType.UNKNOWN, 0, 0

        return ScriptType.MULTISIG, required_sigs, total_keys

    @classmethod
    def locking_script_type(cls, decoded_script):
        if decoded_script is None or len(decoded_script) == 0:
            return ScriptType.NONE

        # most scripts will be of standard formats, and therefore basic pattern matching will work for the vast majority
        # test script against P2PKH template, by far the most common script type
        if len(decoded_script) == len(ScriptTypeTemplate.P2PKH):
            match = True
            for i in range(0, len(ScriptTypeTemplate.P2PKH)):
                # if match is set to None it will never call .match again, although loop continues ¯\_(ツ)_/¯
                match = match and ScriptTypeTemplate.P2PKH[i].match(decoded_script[i])
            if match:
                return ScriptType.P2PKH

        # test script against P2PK template, the OG standard
        if len(decoded_script) == len(ScriptTypeTemplate.P2PK):
            match = True
            for i in range(0, len(ScriptTypeTemplate.P2PK)):
                match = match and ScriptTypeTemplate.P2PK[i].match(decoded_script[i])
            if match:
                return ScriptType.P2PK

        # test script against P2SH template
        if len(decoded_script) == len(ScriptTypeTemplate.P2SH):
            match = True
            for i in range(0, len(ScriptTypeTemplate.P2SH)):
                match = match and ScriptTypeTemplate.P2SH[i].match(decoded_script[i])
            if match:
                return ScriptType.P2SH

        # test script against segwit patterns, both of which have the same decoded script length and 0'th param (version)
        if len(decoded_script) == len(ScriptTypeTemplate.P2WPKH) and ScriptTypeTemplate.P2WPKH[0].match(decoded_script[0]):
            if ScriptTypeTemplate.P2WPKH[1].match(decoded_script[1]) and ScriptTypeTemplate.P2WPKH[2].match(decoded_script[2]):
                return ScriptType.P2WPKH

            if ScriptTypeTemplate.P2WSH[1].match(decoded_script[1]) and ScriptTypeTemplate.P2WSH[2].match(decoded_script[2]):
                return ScriptType.P2WSH

        multisig_type, M, N = TXOutput.locking_script_is_multisig(decoded_script)
        if multisig_type == ScriptType.MULTISIG:
            return ScriptType.MULTISIG

        simplified_script = []
        for i in range(0, len(decoded_script)):
            # for the purposes of this program, any unspendable output is considered invalid
            if decoded_script[i] == opcode.names[opcode.RETURN_] or decoded_script[i] in opcode.invalid_opcode_names:
                return ScriptType.INVALID
            
            # skip all NOOP codes
            if decoded_script[i] in opcode.noop_code_names:
                continue
            
            simplified_script.append(decoded_script[i])

        # if we've simplified the script at all, we can evaluate again against the common patterns.
        # note the script length can only be shortened and this recursion can only occur once, at most.
        if len(simplified_script) < len(decoded_script):
            return TXOutput.locking_script_type(simplified_script)

        # TODO: other script types
        return ScriptType.UNKNOWN

    def serialize(self):
        info = [self.hash, str(self.index), str(self.block_height), self.serialized_script, str(self.value)]
        return ",".join(info)

    @classmethod
    def deserialize(cls, data):
        info = data.split(",")
        if len(info) < 5:
            return None

        hash = str(info[0])
        index = int(info[1])
        block_height = int(info[2])
        script = str(info[3])
        value = float(info[4])
        return TXOutput(hash, index, block_height, script, value)

class ScriptType(Enum):
    NONE = 0
    INVALID = 1
    UNKNOWN = 2
    P2PK = 3
    P2PKH = 4
    P2SH = 5
    P2WPKH = 6
    P2WSH = 7
    MULTISIG = 8

class ScriptTypeTemplate(object):
    """
    note that matching patterns is much easier than validating them in the first place. for example, P2PK template
    below technically will match ["push_size_65", "02____32bytes____"] or vice-versa, which would not be valid Script.
    however, it should not be necessary to break these into seperate templates because that script would be invalid.
    Therefore, we can take some shortcuts when detecting the type of a transaction that has already been mined.
    """
    # building blocks
    POSITIVE_DIGIT = re.compile(r"push_positive_(\d{1,2})")
    PUBLIC_KEY = re.compile(r"^0(?:4[0-9a-fA-F]{128}$|[23][0-9a-fA-F]{64})$")
    PUBLIC_KEY_HASH = re.compile(r"^[0-9a-fA-F]{40}$")
    WITNESS_KEY_HASH = re.compile(r"^[0-9a-fA-F]{40}$")
    WITNESS_SCRIPT_HASH = re.compile(r"^[0-9a-fA-F]{64}$")

    # standard patterns
    P2PK = [re.compile(r"^push_size_(?:65|33)$"), PUBLIC_KEY, re.compile(r"^checksig$")]
    P2PKH = [re.compile(r"^dup$"), re.compile(r"^hash160$"), re.compile(r"^push_size_20$"), PUBLIC_KEY_HASH, re.compile(r"^equalverify$"), re.compile(r"^checksig$")]
    P2SH = [re.compile(r"^hash160$"), re.compile(r"^push_size_20$"), PUBLIC_KEY_HASH, re.compile(r"^equal$")]
    P2WPKH = [re.compile(r"^push_size_0$"), re.compile(r"^push_size_20$"), WITNESS_KEY_HASH]
    P2WSH = [re.compile(r"^push_size_0$"), re.compile(r"^push_size_32$"), WITNESS_SCRIPT_HASH]

class ScriptDecodingException(Exception):
    def __init__(self, message):
        super().__init__(message)

class ScriptLengthShorterThanExpected(ScriptDecodingException):
    def __init__(self, num_bytes, hex_string):
        message = f"failed to read required data\nbytes expected: {num_bytes}\ndata: {hex_string}"
        super().__init__(message)