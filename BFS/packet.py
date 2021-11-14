import numpy as np
import serial
import options
import time

# serial port
rate = 9600
sp = options.port
if options.inputMode == 2:
    ser = serial.Serial(sp, rate)

# directions
directions = ['N', 'E', 'S', 'W']

rData = ""
sData = ""

s = open(options.fpTXT + "raspPacket", "a", encoding='utf-8')
r = open(options.fpTXT + "mazeInput", "r", encoding='utf-8')
e = open(options.fpTXT + "saveMaze", "a", encoding='utf-8')
inputData = None

# function to reroute setup based on input/output
def setupInput(mode):
    if mode == 1 or mode == 0:
        s.truncate(0)
    if mode == 1:
        return setupInputFile()
    if mode == 2:
        return setupSerial()

# function to reroute where input is coming from
def getData(mode, tile, facing):
    if mode == 0:
        return getManualData(tile, facing)
    if mode == 1:
        return getFileData(tile)
    if mode == 2:
        return requestData()

# function to reroute where output is sent
def sendData(mode, pathLen):
    if mode == 1 or mode == 0:
        sendFileData(pathLen)
    if mode == 2:
        sendSerial(pathLen)

# receiving manual data from console
def getManualData(tile, facing):
    walls = np.zeros(5, dtype=np.int8)
    inputStr = input("\tEnter MegaPi input data for Tile " + str(tile) + " and Direction " + directions[facing] + ": ")  # 1010
    walls[0] = int(inputStr[2])
    walls[1] = int(inputStr[1])
    walls[2] = 0
    walls[3] = int(inputStr[0])
    walls[4] = 0
    return walls

# sets up file input, determined whether from gen or input
def setupInputFile():
    inputType = r.readline()
    if inputType == "GENERATED\n":
        print("File input is a generated maze")
        return r.read().splitlines()
    if inputType == "INPUT\n":
        print("File input is manual values")
    return None

# gets data from file depending whether from gen or input
def getFileData(tile):
    if inputData is not None:
        return inputData[tile]  # generated
    else:
        inputStr = r.readline()  # input
        walls = np.zeros(5, dtype=np.int8)
        walls[0] = int(inputStr[2])
        walls[1] = int(inputStr[1])
        walls[2] = 0
        walls[3] = int(inputStr[0])
        walls[4] = 0
        return walls

# writes path to file
def sendFileData(pathLen):
    s.write(sData[pathLen:] + "\n")
    s.flush()

# sets up serial communication
def setupSerial():
    print("SETTING UP SERIAL")
    print("\tSerial setup on port: " + ser.name + "\n")
    print("waiting")

    while not ser.inWaiting():
        time.sleep(0.01)

    ser.read()  # do this to clean the buffer
    return sp

# request and receive wall positions through serial
def requestData():
    send_message = 'g'
    ser.write(bytes(send_message.encode("ascii", "ignore")))
    walls = np.zeros(5)
    receive_message = ser.read()
    while receive_message.isdigit() is False:
        print("rms: " + str(receive_message))
        receive_message = ser.read()
    time.sleep(0.1)
    walls[3] = receive_message.decode("ascii", "ignore")
    receive_message = ser.read()
    time.sleep(0.1)
    walls[1] = receive_message.decode("ascii", "ignore")
    receive_message = ser.read()
    time.sleep(0.1)
    walls[0] = receive_message.decode("ascii", "ignore")
    return walls

# send path instructions through serial
def sendSerial(pathLen):
    print("Sending: " + str(sData[pathLen:]) + "$")  # $ symbolizes the end of a send
    send_message = sData[pathLen:] + "$"
    ser.write(bytes(send_message.encode("ascii", "ignore")))

def sendToFile(gMaze):
    e.truncate(0)
    e.write(+"")
    for x in range(gMaze.length):
        e.write("G")