import secp256k1

NUM_ELLIPTIC_CURVE_POINTS = 115792089237316195423570985008687907852837564279074904382605163141518161494337

class KeyRing(object):
    
    def __init__(self, value):
        if type(value) is str:
            value = int(value, 16)
        if type(value) is not int:
            raise ValueError("KeyRing must be initialized with a hex string or an integer")

        self.__create_private_key(value)

    def __str__(self):
        return self.hex()

    def __create_private_key(self, value):
        value = value % NUM_ELLIPTIC_CURVE_POINTS
        
        private_key = None
        while private_key is None:
            try:
                private_key = secp256k1.PrivateKey(bytes.fromhex(f"{value:0{64}x}"))
            except TypeError as e:
                raise e
            except Exception:
                value = (value + 1) % NUM_ELLIPTIC_CURVE_POINTS

        self.__private_key = private_key
        self.__value = int(private_key.serialize(), 16)

    def current(self):
        return self.__value
        
    def next(self):
        self.__create_private_key(self.__value + 1)

    def public_key(self, compressed = True):
        return self.__private_key.pubkey.serialize(compressed).hex()

    def hex(self):
        return f"{self.__value:0{64}x}"