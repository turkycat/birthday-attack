import re
import transactions.opcode as opcode
from enum import Enum

NUM_CHARACTERS_PER_BYTE = 2

def decode_hex_bytes_little_endian(num_bytes, hex_string):
    characters_expected = num_bytes * NUM_CHARACTERS_PER_BYTE
    if len(hex_string) < characters_expected:
        raise ScriptLengthShorterThanExpected(characters_expected, hex_string)

    total = 0
    byte = 0
    while byte < num_bytes:
        current_byte = int(hex_string[byte * 2 : (byte + 1) * 2], 16) << (8 * byte)
        total = total + current_byte
        byte = byte + 1
    return total

def decode_script(serialized_script):
    if serialized_script is None or serialized_script == "":
        return None

    if len(serialized_script) % 2 == 1:
        raise ScriptDecodingException("serialized script must not be odd length")

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

            data_size = decode_hex_bytes_little_endian(bytes_to_decode, serialized_script[script_position:])
            script_position = script_position + (NUM_CHARACTERS_PER_BYTE * bytes_to_decode)

        characters_expected = NUM_CHARACTERS_PER_BYTE * data_size
        data = serialized_script[script_position : script_position + characters_expected]
        if len(data) < characters_expected:
            raise ScriptLengthShorterThanExpected(characters_expected, serialized_script[script_position:])
        
        script_position = script_position + characters_expected
        decoded_script.append(data)

    return decoded_script

def locking_script_multisig_type(decoded_script):
    if decoded_script is None or len(decoded_script) == 0:
        return Type.NONE

    """
    note that this function only evaluates standard M-of-N multisig patterns
    """

    # verify OP_PUSH_POSITIVE_M, extract M
    match = TypeTemplate.POSITIVE_DIGIT.match(decoded_script[0])
    if not match:
        return Type.UNKNOWN, 0, 0
    required_sigs = int(match.group(1))

    # read some number of public keys
    index = 1
    while index < len(decoded_script) and TypeTemplate.PUBLIC_KEY.match(decoded_script[index]):
        index += 1
    total_keys = index - 1

    # verify OP_PUSH_POSITIVE_N, extract N
    match = TypeTemplate.POSITIVE_DIGIT.match(decoded_script[index])
    if not match:
        return Type.UNKNOWN, 0, 0
    expected_total_keys = int(match.group(1))
    index += 1

    MAX_STANDARD_PUBLIC_KEYS = 3
    if not (expected_total_keys == total_keys and required_sigs <= total_keys and \
        total_keys <= MAX_STANDARD_PUBLIC_KEYS and required_sigs <= MAX_STANDARD_PUBLIC_KEYS and \
        index == (len(decoded_script) - 1) and decoded_script[index] == opcode.names[opcode.CHECKMULTISIG]):
        # this is really unexpected and is more of a "invalid script" case
        # ScriptDecodingException might be better here but I'd rather see this turn up in the unknown set.
        return Type.UNKNOWN, 0, 0

    return Type.MULTISIG, required_sigs, total_keys

def locking_script_type(decoded_script):
    if decoded_script is None or len(decoded_script) == 0:
        return Type.NONE

    # most scripts will be of standard formats, and therefore basic pattern matching will work for the vast majority
    # test script against P2PKH template, by far the most common script type
    if len(decoded_script) == len(TypeTemplate.P2PKH):
        match = True
        for i in range(0, len(TypeTemplate.P2PKH)):
            # if match is set to None it will never call .match again, although loop continues ¯\_(ツ)_/¯
            match = match and TypeTemplate.P2PKH[i].match(decoded_script[i])
        if match:
            return Type.P2PKH

    # test script against P2PK template, the OG standard
    if len(decoded_script) == len(TypeTemplate.P2PK):
        match = True
        for i in range(0, len(TypeTemplate.P2PK)):
            match = match and TypeTemplate.P2PK[i].match(decoded_script[i])
        if match:
            return Type.P2PK

    # test script against P2SH template
    if len(decoded_script) == len(TypeTemplate.P2SH):
        match = True
        for i in range(0, len(TypeTemplate.P2SH)):
            match = match and TypeTemplate.P2SH[i].match(decoded_script[i])
        if match:
            return Type.P2SH

    # test script against segwit patterns, both of which have the same decoded script length and 0'th param (version)
    if len(decoded_script) == len(TypeTemplate.P2WPKH) and TypeTemplate.P2WPKH[0].match(decoded_script[0]):
        if TypeTemplate.P2WPKH[1].match(decoded_script[1]) and TypeTemplate.P2WPKH[2].match(decoded_script[2]):
            return Type.P2WPKH

        if TypeTemplate.P2WSH[1].match(decoded_script[1]) and TypeTemplate.P2WSH[2].match(decoded_script[2]):
            return Type.P2WSH

    multisig_type, M, N = locking_script_multisig_type(decoded_script)
    if multisig_type == Type.MULTISIG:
        return Type.MULTISIG

    simplified_script = []
    for i in range(0, len(decoded_script)):
        # for the purposes of this program, any unspendable output is considered invalid
        if decoded_script[i] == opcode.names[opcode.RETURN_] or decoded_script[i] in opcode.invalid_opcode_names:
            return Type.INVALID
        
        # skip all NOOP codes
        if decoded_script[i] in opcode.noop_code_names:
            continue
        
        simplified_script.append(decoded_script[i])

    # if we've simplified the script at all, we can evaluate again against the common patterns.
    # note the script length can only be shortened and this recursion can only occur once, at most.
    if len(simplified_script) < len(decoded_script):
        return locking_script_type(simplified_script)

    # this type falls under the 'nonstandard' category, but is something of a curiosity for me
    # note that this pattern would technically match segwit, so checking for it must occur after segwit.
    if len(decoded_script) > 1:
        if TypeTemplate.PUSH_SIZE.match(decoded_script[-2]) and decoded_script[-2] != opcode.names[opcode.PUSH_SIZE_0] and \
            TypeTemplate.HEX_DATA.match(decoded_script[-1]):
            return Type.ANYONE_CAN_SPEND

    return Type.UNKNOWN

class Type(Enum):
    NONE = 0
    INVALID = 1
    UNKNOWN = 2
    P2PK = 3
    P2PKH = 4
    P2SH = 5
    P2WPKH = 6
    P2WSH = 7
    MULTISIG = 8
    ANYONE_CAN_SPEND = 100 # not a real transaction type, but interesting

class TypeTemplate(object):
    """
    note that matching patterns is much easier than validating them in the first place. for example, P2PK template
    below technically will match ["push_size_65", "02____32bytes____"] or vice-versa, which would not be valid Script.
    however, it should not be necessary to break these into separate templates because that script would be invalid.
    Therefore, we can take some shortcuts when detecting the type of a transaction that has already been mined.
    """
    # building blocks
    HEX_DATA = re.compile(r"(?<![0-9a-fA-F]{1})(?:[0-9a-fA-F]{2})+(?![0-9a-fA-F]{1})")
    POSITIVE_DIGIT = re.compile(r"push_positive_(\d{1,2})")
    PUBLIC_KEY = re.compile(r"^0(?:4[0-9a-fA-F]{128}$|[23][0-9a-fA-F]{64})$")
    PUBLIC_KEY_HASH = re.compile(r"^[0-9a-fA-F]{40}$")
    PUSH_SIZE = re.compile(r"^push_size_(\d{1,2})$")
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
    def __init__(self, num_chars, hex_string):
        message = f"failed to read required data\nhex chars expected: {num_chars}\ndata: {hex_string}"
        super().__init__(message)