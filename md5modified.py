import math

constants = [int(abs(math.sin(i+1)) * 2**32) & 0xFFFFFFFF for i in range(64)]
init_states = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
rotate_amounts = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                  5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
                  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
                  

fns = 	16*[lambda b, c, d: (b & c) | (~b & d)] + \
		16*[lambda b, c, d: (d & b) | (~d & c)] + \
		16*[lambda b, c, d: b ^ c ^ d] + \
		16*[lambda b, c, d: c ^ (b | ~d)]

indexer	=	16*[lambda i: i] + \
			16*[lambda i: (5 * i + 1) % 16] + \
			16*[lambda i: (3 * i + 5) % 16] + \
			16*[lambda i: (7*i) % 16]

def rot_left(x, n):
	x &= 0xFFFFFFFF
	return ((x<<n) | (x>>(32-n))) & 0xFFFFFFFF
	
def find_hash(msg):
	
	msg = bytearray(msg)
	msg_bitlen = (8 * len(msg)) & 0xffffffffffffffff
	
	msg.append(0x80)
	while len(msg) % 64 != 56:
		msg.append(0)
	msg += msg_bitlen.to_bytes(8, byteorder='little')
	hash_part = init_states
	
	for msg_part in range(0, len(msg), 64):
		a, b, c, d = hash_part
		part = msg[msg_part:msg_part+64]
		for i in range(64):
			f = fns[i](b, c, d)
			g = indexer[i](i)
			rot = a + f + constants[i] + int.from_bytes(part[4*g:4*g+4], byteorder='little')
			b2 = (b + rot_left(rot, rotate_amounts[i])) & 0xFFFFFFFF
			a, b, c, d = d, b2, b, c
		for i, hashedval in enumerate([a, b, c, d]):
			hash_part[i] += hashedval
			hash_part[i] &= 0xFFFFFFFF
	return sum(x<<(32*i) for i, x in enumerate(hash_part))
   
	

def md5_to_hex(digest):
    raw = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(raw, byteorder='big'))
 
if __name__=='__main__':
	message = input("Enter message to be hashed")
	message = message.encode()
	print(md5_to_hex(find_hash(message)),' <= "',message.decode('ascii'))



			
			
