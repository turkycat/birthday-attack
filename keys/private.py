NUM_ELLIPTIC_CURVE_POINTS = 115792089237316195423570985008687907852837564279074904382605163141518161494337

class PrivateKey(object):
    
    def __init__(self, value):
        if type(value) is str:
            value = int(value, 16)

        self.value = value % NUM_ELLIPTIC_CURVE_POINTS

    def __str__(self):
        return f"0x{self.value:0{64}x}"

    def next(self):
        self.value = (self.value + 1) % NUM_ELLIPTIC_CURVE_POINTS