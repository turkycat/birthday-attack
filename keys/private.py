import secp256k1

NUM_ELLIPTIC_CURVE_POINTS = 115792089237316195423570985008687907852837564279074904382605163141518161494337

class PrivateKey(object):
    
    def __init__(self, value):
        if type(value) is str:
            value = int(value, 16)

        self.__create_private_key(value)

    def __str__(self):
        return self.hex()

    def __create_private_key(self, value):
        value = value % NUM_ELLIPTIC_CURVE_POINTS
        while True:
            try:
                self.__private_key = secp256k1.PrivateKey(bytes.fromhex(f"{value:0{64}x}"))
                break
            except TypeError as e:
                raise e
            except Exception:
                value = (value + 1) % NUM_ELLIPTIC_CURVE_POINTS

        self.__value = value

    def next(self):
        self.__create_private_key(self.__value + 1)

    def public_key(self, compressed = True):
        pass

    def hex(self):
        return f"{self.__value:0{64}x}"

    def value(self):
        return self.__value