import cv2
import everythingDetect
import serial

rate = 9600
sp = "/dev/ttyS0"
ser = serial.Serial(sp, rate)

startMessage = 'v'

while True:
    
    send_message1 = ""
    send_message2 = ""
    
    right, packageR, left, packageL = everythingDetect.detectAll()
    
    print("HERE:", left, packageL, right, packageR)
    
    if left is True or right is True:
        ser.write(bytes(startMessage.encode("ascii", "ignore")))
    
    if left is True:
        send_message1 = "L" + str(packageL)
        print(send_message1)
        ser.write(bytes(send_message1.encode("ascii", "ignore")))
        
    if right is True:
        send_message2 = "R" + str(packageR)
        print(send_message2)
        ser.write(bytes(send_message2.encode("ascii", "ignore")))