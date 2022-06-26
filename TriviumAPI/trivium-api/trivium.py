from collections import deque
from itertools import repeat
from PIL import Image
import numpy



# Convert strings of hex to strings of bytes and back, little-endian style
_allbytes = dict([("%02X" % i, i) for i in range(256)])

def hex_to_bytes(s):
    return [_allbytes[s[i:i+2].upper()] for i in range(0, len(s), 2)]

def hex_to_bits(s):
    return [(b >> i) & 1 for b in hex_to_bytes(s)
            for i in range(8)]

def bits_to_hex(b):
    return "".join(["%02X" % sum([b[i + j] << j for j in range(8)])
                    for i in range(0, len(b), 8)])


class Trivium:

    # Key IV are little endian bits
    key = hex_to_bits("0F62B5085BAE0154A7FA")[::-1]
    iv = hex_to_bits("288FF65DC42B92F960C7")[::-1]

    def __init__(self): #, key, iv
        """in the beginning we need to transform the key as well as the IV.
        Afterwards we initialize the state."""
        self.state = None
        self.counter = 0
        #self.key = key 
        #self.iv = iv

        # Initialize state
        # len 93
        init_list = list(map(int, list(self.key)))
        init_list += list(repeat(0, 13))
        # len 84
        init_list += list(map(int, list(self.iv)))
        init_list += list(repeat(0, 4))
        # len 111
        init_list += list(repeat(0, 108))
        init_list += list([1, 1, 1])
        self.state = deque(init_list)

        # Do 4 full cycles, drop output
        for i in range(4*288):
            self._gen_keystream()

    def encrypt(self, message):
        next_key_bit = self.keystream().__next__
        cipher = deque([])
        for byte in bytearray(message, "utf8"):
            # Key for each byte
            key = 0
            for i in range(0, 8):
                k = next_key_bit()
                key = key | (k << i)

            c = [int(i, 2) for i in bin(byte ^ key)[2:].zfill(8)]

            # Little Endian
            cipher.extendleft(c[4:])
            cipher.extendleft(c[:4])

        return list(cipher)
    

    def decrypt(self, cipher):
        next_key_bit = self.keystream().__next__

        cipher = deque(cipher)
        plain = deque([])

        for i in range(0, int((len(cipher) / 8))):
            temp = []
            for j in range(0, 8):
                temp.append(cipher.pop())

            # cipher
            c_list = []
            c_list[:4] = temp[4:]
            c_list[4:] = temp[:4]
            c = int("".join(str(i) for i in c_list), 2)

            # key
            key = 0
            for j in range(0, 8):
                k = next_key_bit()
                key = key | (k << j)

            # plain text
            plain.extendleft([c ^ key])

        return ''.join(chr(i) for i in list(plain)[::-1])

    def keystream(self):
        """output keystream
        only use this when you know what you are doing!!"""
        while self.counter < 2**64:
            self.counter += 1
            yield self._gen_keystream()

    def _gen_keystream(self):
        """this method generates triviums keystream"""

        t_1 = self.state[65] ^ self.state[92]
        t_2 = self.state[161] ^ self.state[176]
        t_3 = self.state[242] ^ self.state[287]

        out = t_1 ^ t_2 ^ t_3

        a_1 = self.state[90] & self.state[91]
        a_2 = self.state[174] & self.state[175]
        a_3 = self.state[285] & self.state[286]

        s_1 = a_1 ^ self.state[170] ^ t_1
        s_2 = a_2 ^ self.state[263] ^ t_2
        s_3 = a_3 ^ self.state[68] ^ t_3

        self.state.rotate(1)

        self.state[0] = s_3
        self.state[93] = s_1
        self.state[177] = s_2

        return out
    
    def encrypt_image(self,image):
        #Both images have the same width & height
        pix1 = image.load()
        pix1 = image.convert("RGB")
        pix1 = pix1.load()
        w, h = image.size
        imn = Image.new("RGB", (w, h), "black")
        pixn = imn.load()
        next_key_bit = self.keystream().__next__
        #cipher = deque([])
        for i in range(w): 
             #key = 0
             for j in range(h): 
                  key = 0
                  for p in range(0, 8):
                     k = next_key_bit()
                     key = key | (k << p)
                        
                     
                  r1, g1, b1 = pix1[i, j]
                
                  rn = r1 ^ key
                  gn = g1 ^ key
                  bn = b1 ^ key
        
                  pixn[i,j] =  (rn, gn, bn)
        
        #imn.show()
        imn.save("encryptedImg.png")
 
 
        print('Encryption Done...')
    
    def decrypt_image(self,image):
        pix1 = image.load()
        pix1 = image.convert("RGB")
        pix1 = pix1.load()
        w, h = image.size
        imn = Image.new("RGB", (w, h), "black")
        pixn = imn.load()
        next_key_bit = self.keystream().__next__
       # cipher = deque([])
        for i in range(w): 
             #key = 0
            for j in range(h): 
                 key = 0
                 for p in range(0, 8):
                     k = next_key_bit()
                     key = key | (k << p)     
                 r1, g1, b1 = pix1[i, j]
                
                 rn = r1 ^ key
                 gn = g1 ^ key
                 bn = b1 ^ key
        
                 pixn[i,j] =  (rn, gn, bn)
        
        #imn.show()
        imn.save("decryptedImg.png")
        print('Decryption Done...')
        
        
    
