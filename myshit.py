import math
msg = ""
tobin = ""
h0 = 0x67452301
h1 = 0xefcdab89
h2 = 0x98badcfe
h3 = 0x10325476
sinval = []
rotate = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
          5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
          4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
          6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

for i in range(64):
    sinval.append(int(abs(math.sin(i+1)) * 2 ** 32) & 0xFFFFFFFF)

def LEFTROTATE(x, c):
    x &= 0xFFFFFFFF
    return (((x) << (c)) | ((x) >> (32 - (c)))) & 0xFFFFFFFF

for i in msg:
    tobin += format(ord(i), '08b')

origlength = len(tobin) % (2 ** 64)
tobin += "1"
length = 448 - (len(tobin) % 512)

for i in range(length):
    tobin += "0"

origlength = bin(origlength)[2:]

for i in range(64 - len(origlength)):
    tobin += "0"

tobin += origlength
msgblock = []

for i in range(16):
    temp = ""
    for j in range(32):
        temp += tobin[(i * 32) + j]
    msgblock.append(temp)

a = h0
b = h1
c = h2
d = h3

for i in range(64):
    if (i < 16):
        f = (b & c) | ((~ b) & d)
        g = i
    elif (i < 32):
        f = (d & b) | ((~ d) & c)
        g = (5 * i + 1) % 16
    elif (i < 48):
        f = b ^ c ^ d
        g = (3 * i + 5) % 16
    else:
        f = c ^ (b | (~ d))
        g = (7 * i) % 16

    f = f + a + sinval[i] + int(msgblock[g],2)
    a = d
    d = c
    c = b
    b = b + LEFTROTATE(f, rotate[i]) & 0xFFFFFFFF
print(a)
h0 += a
h1 += b
h2 += c
h3 += d
out = str(hex(h0)[2:]) + str(hex(h1)[2:]) + str(hex(h2)[2:]) + str(hex(h3)[2:])
print("output: ")
print(out)
