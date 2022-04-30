import numpy as np
import config
import cv2
import serial
import time
import os

if config.inputMode == 2:
    ser = serial.Serial(config.port, config.rate)

# directions
directions = ['N', 'E', 'S', 'W']

# path taken stored in this string
sData = ""

# cameras
cap = []

video_getter = None

# starting time of the program
startTime = None

# get file editors
def outputFile(mode):
    return open(config.fpTXT + "outputDirections", str(mode), encoding='utf-8')
def inputFile(mode):
    return open(config.fpTXT + "generatedMaze", str(mode), encoding='utf-8')
def saveFile(mode):
    return open(config.fpTXT + "savedMaze", str(mode), encoding='utf-8')

# function to reroute setup based on input/output
def setupInput(mode):
    # manual or from file
    if mode == 1 or mode == 0:
        # clear output file
        outputFile("r+").truncate(0)
    # from file
    if mode == 1:
        setupInputFile()
    # serial
    if mode == 2:
        return setupSerial()

# function to reroute where input is coming from
def getData(mode, tile):
    if mode == 0:
        return getManualData(tile)
    if mode == 1:
        return getFileData(tile)
    if mode == 2:
        return getSerialData()

def sendData(mode, msg, newLine=False):
    if mode == 1:
        return sendFileData(msg, newLine)
    if mode == 2:
        return sendSerial(msg)

# receiving manual data from console
def getManualData(tile):
    walls = np.zeros(10, dtype=np.int8)
    inputStr = input("\tEnter MegaPi input data for Tile " + str(tile) + ": ")  # 1010 -> 1010100000
    for i in range(4):
        walls[i] = int(inputStr[i])
    walls[4] = 1
    for i in range(5, 10):
        walls[i] = 0
    return walls

# sets up file input, determines whether from generated or image
def setupInputFile():
    inputType = inputFile("r").readline()
    if inputType == "GENERATED\n":
        if config.importantDebug:
            print("File input is a generated maze")
    elif inputType == "IMAGE\n":
        if config.importantDebug:
            print("File input is a maze from image")
    else:
        raise ValueError("Invalid Input File Type!\nExpected: \"GENERATED\" or \"IMAGE\"\nGot: " + str(inputType))

# gets data from file depending on whether from gen or input
def getFileData(tile):
    # skips until desired tile
    f = inputFile("r")
    for i in range(tile + 1):
        f.readline()
    return [int(j) for j in str(f.readline())[:10]]

# writes path to file
def sendFileData(msg, newLine):
    if newLine:
        msg += "\n"
    outputFile("a").write(msg)
    outputFile("a").flush()

def writeMaze(file, header, maze, delete):
    if delete:
        file.truncate(0)
    if header:
        file.write(str(header) + "\n")
    for i in range(config.mazeSideLen ** 2):
        file.write(str(''.join(str(j) for j in maze[i])) + "\n")
    file.close()

def readMaze(file):
    maze = np.zeros((config.mazeSideLen ** 2, 10), dtype=np.int8)
    header = file.readline()
    for i in range(config.mazeSideLen ** 2):
        maze[i][:] = [int(j) for j in str(file.readline())[:10]]
    file.close()
    return header[:len(header) - 1], maze

# sets up serial communication
def setupSerial():
    print("SETTING UP SERIAL")
    print("\tSerial setup on port: " + ser.name + "\n")
    print("waiting")

    msg = getNextSerialByte()
    while msg != 'a':  # setup acknowledgement
        print("INVALID SETUP ACKNOWLEDGEMENT: " + msg)
        msg = getNextSerialByte()

    if config.saveVictimDebug:
        os.mkdir(config.fpVIC + (time.ctime(startTime)))
    return config.port

# gets one byte of data from serial
def getNextSerialByte():
    #while (not ser.inWaiting()) and cap:
        #for i in range(len(cap)):
            #cap[i].read()
            #_, f = cap[i].read()
            #if config.victimDebug or config.saveVictimDebug:
                #cv2.imshow("left" if i == 0 else "right", f)
                #cv2.waitKey(1)

    msg = ser.read().decode("ascii", "ignore")
    if config.importantDebug or config.serialDebug:
        print("MESSAGE RECEIVED: " + msg)
    return msg

# request and receive wall positions through serial
def getSerialData():
    walls = np.zeros(10)
    msg = getNextSerialByte()

    if msg == 'a':
        return msg

    # account for black and silver tiles
    if not msg.isdigit():
        if msg == 'b':
            return None
        else:
            walls[9] = 2
            msg = getNextSerialByte()                
            if msg == 'a':
                return msg

    walls[0] = msg
    time.sleep(0.1)

    msg = getNextSerialByte()
    if msg == 'a':
        return msg
    walls[1] = msg
    time.sleep(0.1)

    msg = getNextSerialByte()
    if msg == 'a':
        return msg
    walls[3] = msg
    time.sleep(0.1)

    walls[2] = 0
    return walls

# send path instructions through serial
def sendSerial(msg):
    if config.serialDebug:
        print("Sending: " + msg)  # send msg over serial
    ser.write(bytes(msg.encode("ascii", "ignore")))
    time.sleep(0.1)
