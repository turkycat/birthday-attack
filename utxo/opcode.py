# this is taken from bitcoin/system/machine/opcode.hpp | regex replace to refactor enum decl to dict syntax
# comments removed, [0, 78] removed as they are data. using this as a byte index : operation name map
# in case of update, regex replace:
# ^\s*(.*) = (\d+),.*$->    $2 : "$1",
names = {
    0 : "push_size_0",
    1 : "push_size_1",
    2 : "push_size_2",
    3 : "push_size_3",
    4 : "push_size_4",
    5 : "push_size_5",
    6 : "push_size_6",
    7 : "push_size_7",
    8 : "push_size_8",
    9 : "push_size_9",
    10 : "push_size_10",
    11 : "push_size_11",
    12 : "push_size_12",
    13 : "push_size_13",
    14 : "push_size_14",
    15 : "push_size_15",
    16 : "push_size_16",
    17 : "push_size_17",
    18 : "push_size_18",
    19 : "push_size_19",
    20 : "push_size_20",
    21 : "push_size_21",
    22 : "push_size_22",
    23 : "push_size_23",
    24 : "push_size_24",
    25 : "push_size_25",
    26 : "push_size_26",
    27 : "push_size_27",
    28 : "push_size_28",
    29 : "push_size_29",
    30 : "push_size_30",
    31 : "push_size_31",
    32 : "push_size_32",
    33 : "push_size_33",
    34 : "push_size_34",
    35 : "push_size_35",
    36 : "push_size_36",
    37 : "push_size_37",
    38 : "push_size_38",
    39 : "push_size_39",
    40 : "push_size_40",
    41 : "push_size_41",
    42 : "push_size_42",
    43 : "push_size_43",
    44 : "push_size_44",
    45 : "push_size_45",
    46 : "push_size_46",
    47 : "push_size_47",
    48 : "push_size_48",
    49 : "push_size_49",
    50 : "push_size_50",
    51 : "push_size_51",
    52 : "push_size_52",
    53 : "push_size_53",
    54 : "push_size_54",
    55 : "push_size_55",
    56 : "push_size_56",
    57 : "push_size_57",
    58 : "push_size_58",
    59 : "push_size_59",
    60 : "push_size_60",
    61 : "push_size_61",
    62 : "push_size_62",
    63 : "push_size_63",
    64 : "push_size_64",
    65 : "push_size_65",
    66 : "push_size_66",
    67 : "push_size_67",
    68 : "push_size_68",
    69 : "push_size_69",
    70 : "push_size_70",
    71 : "push_size_71",
    72 : "push_size_72",
    73 : "push_size_73",
    74 : "push_size_74",
    75 : "push_size_75",
    76 : "push_one_size",
    77 : "push_two_size",
    78 : "push_four_size",
    79 : "push_negative_1",
    80 : "reserved_80",
    81 : "push_positive_1",
    82 : "push_positive_2",
    83 : "push_positive_3",
    84 : "push_positive_4",
    85 : "push_positive_5",
    86 : "push_positive_6",
    87 : "push_positive_7",
    88 : "push_positive_8",
    89 : "push_positive_9",
    90 : "push_positive_10",
    91 : "push_positive_11",
    92 : "push_positive_12",
    93 : "push_positive_13",
    94 : "push_positive_14",
    95 : "push_positive_15",
    96 : "push_positive_16",
    97 : "nop",
    98 : "reserved_98",
    99 : "if_",
    100 : "notif",
    101 : "disabled_verif",
    102 : "disabled_vernotif",
    103 : "else_",
    104 : "endif",
    105 : "verify",
    106 : "return_",
    107 : "toaltstack",
    108 : "fromaltstack",
    109 : "drop2",
    110 : "dup2",
    111 : "dup3",
    112 : "over2",
    113 : "rot2",
    114 : "swap2",
    115 : "ifdup",
    116 : "depth",
    117 : "drop",
    118 : "dup",
    119 : "nip",
    120 : "over",
    121 : "pick",
    122 : "roll",
    123 : "rot",
    124 : "swap",
    125 : "tuck",
    126 : "disabled_cat",
    127 : "disabled_substr",
    128 : "disabled_left",
    129 : "disabled_right",
    130 : "size",
    131 : "disabled_invert",
    132 : "disabled_and",
    133 : "disabled_or",
    134 : "disabled_xor",
    135 : "equal",
    136 : "equalverify",
    137 : "reserved_137",
    138 : "reserved_138",
    139 : "add1",
    140 : "sub1",
    141 : "disabled_mul2",
    142 : "disabled_div2",
    143 : "negate",
    144 : "abs",
    145 : "not_",
    146 : "nonzero",
    147 : "add",
    148 : "sub",
    149 : "disabled_mul",
    150 : "disabled_div",
    151 : "disabled_mod",
    152 : "disabled_lshift",
    153 : "disabled_rshift",
    154 : "booland",
    155 : "boolor",
    156 : "numequal",
    157 : "numequalverify",
    158 : "numnotequal",
    159 : "lessthan",
    160 : "greaterthan",
    161 : "lessthanorequal",
    162 : "greaterthanorequal",
    163 : "min",
    164 : "max",
    165 : "within",
    166 : "ripemd160",
    167 : "sha1",
    168 : "sha256",
    169 : "hash160",
    170 : "hash256",
    171 : "codeseparator",
    172 : "checksig",
    173 : "checksigverify",
    174 : "checkmultisig",
    175 : "checkmultisigverify",
    176 : "nop1",
    177 : "checklocktimeverify",
    178 : "checksequenceverify",
    179 : "nop4",
    180 : "nop5",
    181 : "nop6",
    182 : "nop7",
    183 : "nop8",
    184 : "nop9",
    185 : "nop10",
    186 : "reserved_186",
    187 : "reserved_187",
    188 : "reserved_188",
    189 : "reserved_189",
    190 : "reserved_190",
    191 : "reserved_191",
    192 : "reserved_192",
    193 : "reserved_193",
    194 : "reserved_194",
    195 : "reserved_195",
    196 : "reserved_196",
    197 : "reserved_197",
    198 : "reserved_198",
    199 : "reserved_199",
    200 : "reserved_200",
    201 : "reserved_201",
    202 : "reserved_202",
    203 : "reserved_203",
    204 : "reserved_204",
    205 : "reserved_205",
    206 : "reserved_206",
    207 : "reserved_207",
    208 : "reserved_208",
    209 : "reserved_209",
    210 : "reserved_210",
    211 : "reserved_211",
    212 : "reserved_212",
    213 : "reserved_213",
    214 : "reserved_214",
    215 : "reserved_215",
    216 : "reserved_216",
    217 : "reserved_217",
    218 : "reserved_218",
    219 : "reserved_219",
    220 : "reserved_220",
    221 : "reserved_221",
    222 : "reserved_222",
    223 : "reserved_223",
    224 : "reserved_224",
    225 : "reserved_225",
    226 : "reserved_226",
    227 : "reserved_227",
    228 : "reserved_228",
    229 : "reserved_229",
    230 : "reserved_230",
    231 : "reserved_231",
    232 : "reserved_232",
    233 : "reserved_233",
    234 : "reserved_234",
    235 : "reserved_235",
    236 : "reserved_236",
    237 : "reserved_237",
    238 : "reserved_238",
    239 : "reserved_239",
    240 : "reserved_240",
    241 : "reserved_241",
    242 : "reserved_242",
    243 : "reserved_243",
    244 : "reserved_244",
    245 : "reserved_245",
    246 : "reserved_246",
    247 : "reserved_247",
    248 : "reserved_248",
    249 : "reserved_249",
    250 : "reserved_250",
    251 : "reserved_251",
    252 : "reserved_252",
    253 : "reserved_253",
    254 : "reserved_254",
    255 : "reserved_255"
}

# the names as defines, generated from enum using tr
PUSH_SIZE_0 = 0
PUSH_SIZE_1 = 1
PUSH_SIZE_2 = 2
PUSH_SIZE_3 = 3
PUSH_SIZE_4 = 4
PUSH_SIZE_5 = 5
PUSH_SIZE_6 = 6
PUSH_SIZE_7 = 7
PUSH_SIZE_8 = 8
PUSH_SIZE_9 = 9
PUSH_SIZE_10 = 10
PUSH_SIZE_11 = 11
PUSH_SIZE_12 = 12
PUSH_SIZE_13 = 13
PUSH_SIZE_14 = 14
PUSH_SIZE_15 = 15
PUSH_SIZE_16 = 16
PUSH_SIZE_17 = 17
PUSH_SIZE_18 = 18
PUSH_SIZE_19 = 19
PUSH_SIZE_20 = 20
PUSH_SIZE_21 = 21
PUSH_SIZE_22 = 22
PUSH_SIZE_23 = 23
PUSH_SIZE_24 = 24
PUSH_SIZE_25 = 25
PUSH_SIZE_26 = 26
PUSH_SIZE_27 = 27
PUSH_SIZE_28 = 28
PUSH_SIZE_29 = 29
PUSH_SIZE_30 = 30
PUSH_SIZE_31 = 31
PUSH_SIZE_32 = 32
PUSH_SIZE_33 = 33
PUSH_SIZE_34 = 34
PUSH_SIZE_35 = 35
PUSH_SIZE_36 = 36
PUSH_SIZE_37 = 37
PUSH_SIZE_38 = 38
PUSH_SIZE_39 = 39
PUSH_SIZE_40 = 40
PUSH_SIZE_41 = 41
PUSH_SIZE_42 = 42
PUSH_SIZE_43 = 43
PUSH_SIZE_44 = 44
PUSH_SIZE_45 = 45
PUSH_SIZE_46 = 46
PUSH_SIZE_47 = 47
PUSH_SIZE_48 = 48
PUSH_SIZE_49 = 49
PUSH_SIZE_50 = 50
PUSH_SIZE_51 = 51
PUSH_SIZE_52 = 52
PUSH_SIZE_53 = 53
PUSH_SIZE_54 = 54
PUSH_SIZE_55 = 55
PUSH_SIZE_56 = 56
PUSH_SIZE_57 = 57
PUSH_SIZE_58 = 58
PUSH_SIZE_59 = 59
PUSH_SIZE_60 = 60
PUSH_SIZE_61 = 61
PUSH_SIZE_62 = 62
PUSH_SIZE_63 = 63
PUSH_SIZE_64 = 64
PUSH_SIZE_65 = 65
PUSH_SIZE_66 = 66
PUSH_SIZE_67 = 67
PUSH_SIZE_68 = 68
PUSH_SIZE_69 = 69
PUSH_SIZE_70 = 70
PUSH_SIZE_71 = 71
PUSH_SIZE_72 = 72
PUSH_SIZE_73 = 73
PUSH_SIZE_74 = 74
PUSH_SIZE_75 = 75
PUSH_ONE_SIZE = 76
PUSH_TWO_SIZE = 77
PUSH_FOUR_SIZE = 78
PUSH_NEGATIVE_1 = 79
RESERVED_80 = 80
PUSH_POSITIVE_1 = 81
PUSH_POSITIVE_2 = 82
PUSH_POSITIVE_3 = 83
PUSH_POSITIVE_4 = 84
PUSH_POSITIVE_5 = 85
PUSH_POSITIVE_6 = 86
PUSH_POSITIVE_7 = 87
PUSH_POSITIVE_8 = 88
PUSH_POSITIVE_9 = 89
PUSH_POSITIVE_10 = 90
PUSH_POSITIVE_11 = 91
PUSH_POSITIVE_12 = 92
PUSH_POSITIVE_13 = 93
PUSH_POSITIVE_14 = 94
PUSH_POSITIVE_15 = 95
PUSH_POSITIVE_16 = 96
NOP = 97
RESERVED_98 = 98
IF_ = 99
NOTIF = 100
DISABLED_VERIF = 101
DISABLED_VERNOTIF = 102
ELSE_ = 103
ENDIF = 104
VERIFY = 105
RETURN_ = 106
TOALTSTACK = 107
FROMALTSTACK = 108
DROP2 = 109
DUP2 = 110
DUP3 = 111
OVER2 = 112
ROT2 = 113
SWAP2 = 114
IFDUP = 115
DEPTH = 116
DROP = 117
DUP = 118
NIP = 119
OVER = 120
PICK = 121
ROLL = 122
ROT = 123
SWAP = 124
TUCK = 125
DISABLED_CAT = 126
DISABLED_SUBSTR = 127
DISABLED_LEFT = 128
DISABLED_RIGHT = 129
SIZE = 130
DISABLED_INVERT = 131
DISABLED_AND = 132
DISABLED_OR = 133
DISABLED_XOR = 134
EQUAL = 135
EQUALVERIFY = 136
RESERVED_137 = 137
RESERVED_138 = 138
ADD1 = 139
SUB1 = 140
DISABLED_MUL2 = 141
DISABLED_DIV2 = 142
NEGATE = 143
ABS = 144
NOT_ = 145
NONZERO = 146
ADD = 147
SUB = 148
DISABLED_MUL = 149
DISABLED_DIV = 150
DISABLED_MOD = 151
DISABLED_LSHIFT = 152
DISABLED_RSHIFT = 153
BOOLAND = 154
BOOLOR = 155
NUMEQUAL = 156
NUMEQUALVERIFY = 157
NUMNOTEQUAL = 158
LESSTHAN = 159
GREATERTHAN = 160
LESSTHANOREQUAL = 161
GREATERTHANOREQUAL = 162
MIN = 163
MAX = 164
WITHIN = 165
RIPEMD160 = 166
SHA1 = 167
SHA256 = 168
HASH160 = 169
HASH256 = 170
CODESEPARATOR = 171
CHECKSIG = 172
CHECKSIGVERIFY = 173
CHECKMULTISIG = 174
CHECKMULTISIGVERIFY = 175
NOP1 = 176
CHECKLOCKTIMEVERIFY = 177
CHECKSEQUENCEVERIFY = 178
NOP4 = 179
NOP5 = 180
NOP6 = 181
NOP7 = 182
NOP8 = 183
NOP9 = 184
NOP10 = 185
RESERVED_186 = 186
RESERVED_187 = 187
RESERVED_188 = 188
RESERVED_189 = 189
RESERVED_190 = 190
RESERVED_191 = 191
RESERVED_192 = 192
RESERVED_193 = 193
RESERVED_194 = 194
RESERVED_195 = 195
RESERVED_196 = 196
RESERVED_197 = 197
RESERVED_198 = 198
RESERVED_199 = 199
RESERVED_200 = 200
RESERVED_201 = 201
RESERVED_202 = 202
RESERVED_203 = 203
RESERVED_204 = 204
RESERVED_205 = 205
RESERVED_206 = 206
RESERVED_207 = 207
RESERVED_208 = 208
RESERVED_209 = 209
RESERVED_210 = 210
RESERVED_211 = 211
RESERVED_212 = 212
RESERVED_213 = 213
RESERVED_214 = 214
RESERVED_215 = 215
RESERVED_216 = 216
RESERVED_217 = 217
RESERVED_218 = 218
RESERVED_219 = 219
RESERVED_220 = 220
RESERVED_221 = 221
RESERVED_222 = 222
RESERVED_223 = 223
RESERVED_224 = 224
RESERVED_225 = 225
RESERVED_226 = 226
RESERVED_227 = 227
RESERVED_228 = 228
RESERVED_229 = 229
RESERVED_230 = 230
RESERVED_231 = 231
RESERVED_232 = 232
RESERVED_233 = 233
RESERVED_234 = 234
RESERVED_235 = 235
RESERVED_236 = 236
RESERVED_237 = 237
RESERVED_238 = 238
RESERVED_239 = 239
RESERVED_240 = 240
RESERVED_241 = 241
RESERVED_242 = 242
RESERVED_243 = 243
RESERVED_244 = 244
RESERVED_245 = 245
RESERVED_246 = 246
RESERVED_247 = 247
RESERVED_248 = 248
RESERVED_249 = 249
RESERVED_250 = 250
RESERVED_251 = 251
RESERVED_252 = 252
RESERVED_253 = 253
RESERVED_254 = 254
RESERVED_255 = 255