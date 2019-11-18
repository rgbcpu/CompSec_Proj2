import math
from random import *
import csv
import os.path
from os import system, name
import time

sfloor = 5000000 #size of lower bounds of salt
sceiling = 5000100 #upper bounds of salt

constants = [int(abs(math.sin(i+1)) * 2**32) & 0xFFFFFFFF for i in range(64)] #constants as defined by md5
rotate_amounts = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
                  5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
                  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
                  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21] #shitfing amounts for rot_left
                  

#list of all functions, each one is repeated 16 times
fns = 16*[lambda b, c, d: (b & c) | (~b & d)] + \
      16*[lambda b, c, d: (d & b) | (~d & c)] + \
      16*[lambda b, c, d: b ^ c ^ d] + \
      16*[lambda b, c, d: c ^ (b | ~d)]

indexer	= 16*[lambda i: i] + \
          16*[lambda i: (5 * i + 1) % 16] + \
          16*[lambda i: (3 * i + 5) % 16] + \
          16*[lambda i: (7*i) % 16]

def clear():
    if name == "nt":
        _ = system('cls')
    else:
        _ = system('clear')


def rot_left(x, n): #shift the bits
    x &= 0xFFFFFFFF
    return ((x<<n) | (x>>(32-n))) & 0xFFFFFFFF
	
def find_hash(msg):#main md5 function
    init_states = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476] #initial states of a, b, c, d
    msg = bytearray(msg) #change message to bytearray
    msg_bitlen = (8 * len(msg)) & 0xffffffffffffffff
    msg.append(0x80) #adds 0x80 to message
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

def check_pass():#fucntion to check user password
    if os.path.exists("team1shadow.txt"): #looks for file
        user = input("Enter Username\n")
        while check_match(user) != 1: #if theres no user by that name
            print("That user doesnt exist")
            user = input("Enter Username\n")
        
        password = input("Enter password\n")
        with open("team1shadow.txt", "r") as shadow:
            csv_file = csv.reader(shadow, delimiter='$')
            for row in csv_file: #for every user in team1shadow.txt
                if (row[0] == user): # if username matches what was entered
                    salt = row[1]
                    md5 = row[2]
                    break

        password = salt + password #add the found salt to the password
        password = md5_to_hex(find_hash(password.encode())) #hash the password
        if password == md5: #compare with the found hash
            print("That is the correct password")
            return 0
        else:
            print("That password was incorrect")
            return 1
    else:
        print("Shadow file not found")

def check_match(user): #see if user exists
    found = 0
    with open("team1shadow.txt", "r") as shadow:
        csv_file = csv.reader(shadow, delimiter='$')
        for row in csv_file:
            if (row[0] == user):
                found = 1
    return found #returns 1 if user is found

def createuser(): #creates a user with a password
    user = input("Enter Username\n")
    if os.path.exists("team1shadow.txt"):
        while check_match(user) != 0: #cant have two users with same name
            print("Sorry, that username was taken.")
            user = input("Enter Username\n")

    password = input("Enter password to be hashed\n")
    salt = str(randint(sfloor, sceiling)) #creates a salt with random value from sfloor to sceiling
    password = salt + password #add salt to the password
    password = md5_to_hex(find_hash(password.encode()))#hash it
    with open("team1shadow.txt", "a") as shadow:
        shadow.write("%s$%s$%s\n" % (user, salt, password)) #store username, salt, and hashed password in file

def rainbow(): #make a rainbow table
    dictionary = input("Enter wordlist file\n")#the wordlist you would like to use
    if os.path.exists(dictionary):
        start = time.time()# start time of the function
        counter = 0
        counter1 = 0
        with open(dictionary, "r") as wordlist:
            with open("rainbow.txt", "w") as rainbow: #output file
                clear()
                for row in wordlist:
                    counter += 1
                    password = row.rstrip("\n\r") #remove newlines
                    password = password.replace("$","")#get rid of $ due to using as delimiter
                    password = ''.join(i if ord(i) < 128 else '' for i in password) #had errors with ascii characters > 128
                    print("hashing %s with salt" % password)
                    for i in range(sfloor, sceiling):
                        counter1 += 1
                        md5 = str(i) + password
                        md5 = md5_to_hex(find_hash(md5.encode()))
                        rainbow.write("%s$%s\n" % (password, md5))
    else:
        print("file does not exist")
        return 1
    clear()
    end = time.time()
    print("Finished!")
    print("Hashed %s passwords for a total of %s hashes!" %(counter, counter1))
    print("total time to complete: ", end - start, " seconds")
    print("path to rainbow table: ", os.path.abspath("rainbow.txt"))

def rainbowAttack(): #rainbow table attack
        if os.path.exists("rainbow.txt"):#look for files
            rainbowtable = "rainbow.txt"
        else:
            rainbowtable = input("Please input path to rainbow table\n")
        if os.path.exists("team1shadow.txt"):
            shadowfile = "team1shadow.txt"
        else:
            shadowfile = input("Please input path to the password file\n")

        start = time.time()
        with open(shadowfile, "r") as shadow:
            usersdict = {}
            csv_shadow = csv.reader(shadow, delimiter="$")
            for user in csv_shadow:
                usersdict[user[0]] = user[2]
            with open (rainbowtable, "r") as rainbow:
                csv_rainbow = csv.reader(rainbow, delimiter = "$")
                
                for row in csv_rainbow:
                    found = []
                    if len(usersdict) > 0:
                        for user in usersdict:
                            if row[1] == usersdict[user]:#if the hashes match
                                end = time.time()
                                print("%s , %s" % (user, row[0]))#print username with associated password
                                print("found in ", end - start, " seconds")
                                found.append(user)
                    else:
                        end = time.time()
                        print("found all users in ", end - start, " seconds")
                        break
                    for i in found:
                        usersdict.pop(i)
                end = time.time()
                if len(usersdict) > 0:
                    print("ran for ", end - start, "seconds")
                    print("could not find passwords for the following users: ")
                    for i in usersdict:
                        print(i)
        
if __name__=='__main__':
    while True:
        print("\nwhat would you like to do?")
        print("1. Create user")
        print("2. Verify password")
        print("3. Make rainbow table")
        print("4. time test")
        print("5. rainbow table attack")
        print("6. Quit")
        option = input("choose an option: ")
        print("")
        if (option == "1"):
            createuser()
        elif (option == "2"):
            check_pass()
        elif option == "3":
            rainbow()
        elif option == "4": #trying out timer
            start = time.time()
            test = "test"
            with open("test.txt","w") as testing:
                for i in range(100): #hash "test" 100 times with random salt
                    salt = str(randint(sfloor,sceiling))
                    password = salt + test
                    password = password.rstrip("\n\r")
                    password = password.replace("$","")
                    password = ''.join(i if ord(i) < 128 else ' ' for i in password)
                    password = md5_to_hex(find_hash(password.encode()))
                    testing.write("%s$%s$%s\n" %(test, salt, password))
            end = time.time()
            print("Average time to hash in seconds: ", (end - start) / 100) #average time over the 100 runs
        elif option == "5":
            rainbowAttack()
        elif option == "6":
            break
