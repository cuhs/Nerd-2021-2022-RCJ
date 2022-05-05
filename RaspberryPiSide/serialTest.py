import serial
import time

sp = serial.Serial("/dev/ttyS0",9600)

while True:
    msg = input("Give a message: ")
    if(msg == "stop"):
        break
    else:
        time.sleep(0.1)
        sp.write(bytes(msg.encode("ascii", "ignore")))
        time.sleep(0.1)
