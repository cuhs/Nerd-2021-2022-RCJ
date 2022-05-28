import numpy as np
import config
import serial
import time

import display
import util
if config.inputMode == 2:
    import RPi.GPIO as GPIO

if config.inputMode == 2:
    ser = serial.Serial(config.port, config.rate)

# directions
directions = ['N', 'E', 'S', 'W']

# total path taken stored in this string
sData = ""

# cameras
cap = []
frame = []
videoGetter = None

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
        saveFile("r+").truncate(0)
    # from file
    if mode == 1:
        setupInputFile()
    # serial
    if mode == 2:
        return setupSerial()

# function to reroute where input is coming from
def getData(mode, tile, floor):
    if mode == 0:
        return getManualData(tile)
    if mode == 1:
        return getFileData(tile, floor)
    if mode == 2:
        return getSerialData()

def sendData(mode, msg, newLine=False):
    if mode == 1:
        return sendFileData(msg, newLine)
    if mode == 2:
        return sendSerial(msg)

# receiving manual data from console
def getManualData(tile):
    walls = np.zeros(util.tileLen, dtype=np.int8)
    inputStr = input("\tEnter MegaPi input data for Tile " + str(tile) + ": ")  # 1010 -> 1010100000
    for i in range(len(util.Dir)):
        walls[i] = int(inputStr[i])
    walls[util.visited] = True
    for i in range(len(util.Dir) + 1, util.tileLen):
        walls[i] = False
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
def getFileData(tile, floor):
    # skips until desired tile
    f = inputFile("r")
    inputType = f.readline()
    for i in range(((floor if inputType != "IMAGE\n" else 0) * (config.mazeSideLen ** 2)) + tile):
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
    maze = np.zeros((config.floorCount, config.mazeSideLen ** 2, util.tileLen), dtype=np.int8)
    header = file.readline()
    for i in range(config.floorCount):
        for j in range(config.mazeSideLen ** 2):
            maze[i][j][:] = [int(k) for k in file.readline()[:util.tileLen]]
    file.close()
    return header[:len(header) - 1], maze

# sets up serial communication
def setupSerial():
    GPIO.output(config.LEDPin, GPIO.HIGH)
    print("SETTING UP SERIAL")
    print("\tSerial setup on port: " + ser.name + "\n")
    print("waiting")

    msg = getNextSerialByte()
    while msg != 'a':  # setup acknowledgement
        print("INVALID SETUP ACKNOWLEDGEMENT: " + msg)
        msg = getNextSerialByte()
        
    GPIO.output(config.LEDPin, GPIO.LOW)

# gets one byte of data from serial
def getNextSerialByte():
    if config.runMode:
        display.updateLabels(status="inWaiting")
    msg = ser.read().decode("ascii", "ignore")
    
    while not(msg in ('d', 'u', ';', 'a', 'b', 'x', 'X', 'm', 's') or msg.isdigit()):
        time.sleep(0.1)
        
        if config.importantDebug or config.serialDebug:
            print("MESSAGE RECEIVED & IGNORED: " + msg)
            
        msg = ser.read().decode("ascii", "ignore")

    if config.runMode:
        display.updateLabels(receiveData=msg)
    if config.importantDebug or config.serialDebug:
        print("MESSAGE RECEIVED: " + msg)
    
    return msg

# request and receive wall positions through serial
def getSerialData():
    walls = np.zeros(util.tileLen)
    msg = getNextSerialByte()

    if msg == 'a':
        return msg

    # account for special tiles
    if not msg.isdigit():
        # black tile
        if msg == 'b':
            walls[util.tileType] = 1
            return walls
        # ramp going up
        elif msg == 'u':
            walls[util.tileType] = 3
            msg = getNextSerialByte()
        # ramp going down
        elif msg == 'd':
            walls[util.tileType] = 4
            msg = getNextSerialByte()
        # checkpoint tile
        else:
            walls[util.tileType] = 2
            msg = getNextSerialByte()                
            if msg == 'a':
                return msg

    # north wall
    walls[0] = msg
    time.sleep(0.1)

    # east
    msg = getNextSerialByte()
    if msg == 'a':
        return msg
    walls[1] = msg
    time.sleep(0.1)

    # west
    msg = getNextSerialByte()
    if msg == 'a':
        return msg
    walls[3] = msg
    time.sleep(0.1)

    # south
    walls[2] = False
    return walls

# send path instructions through serial
def sendSerial(msg):
    if config.serialDebug:
        print("Sending: " + msg)  # send msg over serial
    ser.write(bytes(msg.encode("ascii", "ignore")))
    display.updateLabels(sendData=msg)
    time.sleep(0.1)
