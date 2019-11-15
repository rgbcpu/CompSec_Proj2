import math
from random import *
import csv
import os.path

constants = [int(abs(math.sin(i+1)) * 2**32) & 0xFFFFFFFF for i in range(64)]
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
	init_states = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]
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

def check_pass():
    if os.path.exists("team1shadow.txt"):
        user = input("Enter Username\n")
        while check_match(user) != 1:
            print("That user doesnt exist")
            input("Enter Username\n")
        
        password = input("Enter password\n")
        with open("team1shadow.txt", "r") as shadow:
            csv_file = csv.reader(shadow, delimiter=',')
            for row in csv_file:
                if (row[0] == user):
                    salt = row[1]
                    md5 = row[2]
                    break

        password = salt + password
        password = md5_to_hex(find_hash(password.encode()))
        if password == md5:
            print("That is the correct password")
        else:
            print("That password was incorrect")
    else:
        print("Shadow file not found")

def check_match(user):
    found = 0
    with open("team1shadow.txt", "r") as shadow:
        csv_file = csv.reader(shadow, delimiter=',')
        for row in csv_file:
            if (row[0] == user):
                found = 1
    return found

def createuser():
    user = input("Enter Username\n")
    if os.path.exists("team1shadow.txt"):
        while check_match(user) != 0:
            print("Sorry, that username was taken.")
            user = input("Enter Username\n")

    password = input("Enter password to be hashed\n")
    salt = str(randint(2**48, 2**49))
    password = salt + password
    password = md5_to_hex(find_hash(password.encode()))
    with open("team1shadow.txt", "a") as shadow:
        shadow.write("%s,%s,%s\n" % (user, salt, password))
        
if __name__=='__main__':
    while True:
        print("\nwhat would you like to do?")
        print("1. Create user")
        print("2. Verify password")
        print("3. Quit")
        option = input("choose 1, 2, or 3 : ")
        print("")
        if (option == "1"):
            createuser()
        elif (option == "2"):
            check_pass()
        elif option == "3":
            break
