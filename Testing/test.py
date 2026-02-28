import os
import secrets

name = input("What's your name? ")
print(f"Hey {name}!")

rand_2 = secrets.randbits(8)
print(f"Your lucky number: {rand_2}")
rand_1 = os.urandom(4)
print(f"Random bytes: {rand_1}")