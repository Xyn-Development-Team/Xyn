import time
import active_cli as ac
from active_cli import pcolor as print
import sys

logo = open("logo_smol.ans","r",encoding='cp1252').read()
print(logo,breakline=False)
print("Welcome to the Xyn Control Pannel (XCP) 1.0")

while True:
    print("[Xyn Development] > ",color="magenta",breakline=False)
    nut = input()
    if nut == "help" or nut == "?":
        print("Commands:\nsay - [message(str)] [destination(channel_id)]")
        continue
    with open("command.txt", "w") as f:
        f.write(nut)
        