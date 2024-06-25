import random

chars = "\0 !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
char2num = {char: "%02d" % i for i, char in enumerate(chars) if char != "\x00"}


class DecodingError(ValueError):
    pass

class Decoder:
    def __init__(self, encoded, *, start = 0):
        self.encoded = str(encoded)
        self.i = 0
        self.skip(start)
    @property
    def done(self):
        return self.i == len(self.encoded)
    def skip(self, length):
        if length < 0:
            raise DecodingError("Cannot go backwards")
        self.i += length
        if self.i > len(self.encoded):
            raise DecodingError("Passed end of encoded string")
    def raw(self, length):
        chars = self.encoded[self.i:self.i + length]
        self.skip(length)
        return chars
    def number(self):
        length = int(self.raw(1))
        if length == 0:
            raise DecodingError("Number length cannot be zero")
        string = self.raw(length)
        num = int(string)
        if string[0] == "0":
            num = -num
        return num
    def string(self):
        length = self.number()
        string = ""
        for _ in range(length):
            pos = int(self.raw(2))
            if pos >= len(chars) or chars[pos] == "\0":
                raise DecodingError(f"Unknown char {pos}")
            string += chars[pos]
        return string
    def datablock(self):
        return self.raw(self.number())
      
    
class EncodingError(ValueError):
    pass

class Encoder:
    def __init__(self):
        self.encoded = ""

    def raw(self, data):
        self.encoded += data

    def number(self, num): 
        num = round(num)
        num_str = str(abs(num))
        
        if num < 0:
            num_str = "0" + num_str
            
        if len(num_str) >= 10:
            raise EncodingError(f"Number {num} too long")
        
        self.raw(str(len(num_str)))
        self.raw(num_str)

    def string(self, string):
        length = len(string)
        self.number(length)
        
        for char in string:
            try:
                encoded = char2num[char]
            except KeyError:
                raise EncodingError(f"Cannot encode char {char!r}")
            self.raw(encoded)

    def datablock(self, data):
        data = str(data)
        if not all(map(lambda c: '0' <= c <= '9', data)):
            raise EncodingError(f"Datablock {data!r} is not numeric")
        length = len(data)
        self.number(length)
        self.raw(data)
        
def decode_snake(encoded):
    d = Decoder(encoded)
    snake = {}
    snake["tick"] = d.number()
    snake["is_master"] = d.number()
    snake["name"] = d.string()
    snake["uid"] = d.number()
    snake["datablock"] = datablock = d.datablock()
    if len(datablock) > 0:
        d2 = Decoder(datablock)
        snake["x"] = d2.number()
        snake["y"] = d2.number()
        snake["eyes"] = d2.number()
        snake["length"] = d2.number()
        snake["hue"] = d2.number()
        snake["power"] = d2.number() / 16
        if not d2.done:
            snake["skin"] = d2.datablock()
    
    # ignoring end for now
    
    # need to look into buildcommandlist
    # length = d.number()
    # for _ in range(length):
    
    
    # if not d.done:
    #     # not sure what this is for ???
    #     snake["griffpatch"] = d.number()
    return snake

def encode_snake(
        username,
        *,
        tick = None,
        is_master = 1, # not master
        uid = None,
        x = 0,
        y = 0,
        eyes = 0, # direction eyes are facing
        length = 0,
        hue = 0,
        power = 1, # speed
        skin = None,
    ):
    e = Encoder()
    e.number(random.randrange(0, 10) if tick is None else tick)
    e.number(is_master)
    e.string(username)
    e.number(random.randrange(0, 10**4) if uid is None else uid)
    
    #datablock
    e2 = Encoder()
    e2.number(x)
    e2.number(y)
    e2.number(eyes)
    e2.number(length)
    e2.number(hue),
    e2.number(power * 16),
    if skin is not None:
        e2.datablock(skin)
    e.datablock(e2.encoded)
    
    # not doing buildcommandlist yet
    e.number(0)
    
    return e.encoded
    

def get_username(encoded):
    encoded = str(encoded)
    chars = "\0 !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    i = 0
    def num():
        nonlocal i
        length = int(encoded[i])
        i += 1
        string = encoded[i:i + length]
        i += length
        num = int(string)
        if string[0] == "0":
            num = -num
        return num
    num()
    num()
    length = num()
    name = ""
    for _ in range(length):
        name += chars[int(encoded[i:i+2])]
        i += 2
    return name
        