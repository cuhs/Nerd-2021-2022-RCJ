import BFS
import display
import numpy as np
import cv2
import time
import mazeToText
from BFS import util
from util import packet
from util import config

if config.inputMode == 2:
    import display

BFS.init()
print("RaspberryPiSide START")

# display setup
display.imgSetup()

# packet setup
if config.inputMode == 1:
    if config.genFromImage:
        mazeToText.genMazeFromImage()
    else:
        mazeToText.generateMaze("open", util.mazeSize)
    ret = packet.setupInput(config.inputMode)
    if ret is not None:  # maze in file is generated maze, values must be stored
        packet.inputData = np.zeros((util.mazeSize * util.mazeSize, 5), dtype=np.int8)
        for x in range(util.mazeSize * util.mazeSize):
            cTile = ret[x]
            for y in range(4):
                packet.inputData[x][y] = cTile[y]
                packet.inputData[x][4] = -1
else:
    packet.setupInput(config.inputMode)

print("\nrunning...")

# set start tile walls
util.setWalls()

# time calculation
ot = 0
start = time.time()

# calculate next tile
nextTile = BFS.nextTile(util.tile)

while nextTile is not None:
    if config.debug is True:
        print("\tCurrent Tile:\t" + str(util.tile) + "\n\tNext Tile:\t" + str(nextTile))
    # calculate path to target tile
    BFS.pathToTile(util.tile, nextTile)
    if config.debug is True:
        print("\tTiles To Target Tile: " + str(len(util.path)))

    # display the maze
    if config.displayMode == 1:
        display.show(nextTile, util.maze, config.displayRate)

    # send driving instructions and do victim and do obstacle and do black tiles
    while util.path:
        # calculate driving instructions from path to next tile
        if config.debug is True:
            print("\tPath: " + str(util.path))

        # set direction to the direction to be turned
        util.direction = BFS.turnToTile(util.path.pop(), util.direction)

        # check for victims after done turning
        if config.inputMode == 2:
            while not packet.ser.inWaiting():
                everythingDetect.getVideo()
            if packet.ser.read().decode() == 'd':
                if not util.maze[util.tile][util.visited] == 2:
                    everythingDetect.sendVictims()

        # using serial, check for black tiles
        if config.inputMode == 2:
            # not last forward / going to new tile
            if util.path:
                # set tile to the tile in front
                util.tile = util.forwardTile(util.tile)
            else:
                # last forward in sequence, checking for black tile
                packet.ser.write(bytes("mFT1;$".encode("ascii", "ignore")))
                while not packet.ser.inWaiting():
                    everythingDetect.getVideo()
                if packet.ser.read().decode() == 'y':
                    util.tile = util.forwardTile(util.tile)
                else:
                    util.setBlackTile(util.forwardTile(util.tile))

        else:
            # set tile to the tile in front
            util.tile = util.forwardTile(util.tile)

        if config.inputMode == 2:
            while not packet.ser.inWaiting():
                everythingDetect.getVideo()
            if packet.ser.read().decode() == 'd':
                if not util.maze[util.tile][util.visited] == 2:
                    everythingDetect.sendVictims()

    if config.inputMode != 2:
        packet.sendData(config.inputMode, util.pathLen)

    # print out path to only the next tile
    if config.debug is True:
        print("\tPath To Tile: " + str(packet.sData[util.pathLen:]))
        print()
    util.pathLen = len(packet.sData)
                    
    # set tile new tile to visited, clear parent array
    util.maze[util.tile][util.visited] = 1
    util.parent.fill(-1)

    # get sensor/wall values and calculate next tile
    util.setWalls()

    # calculate next tile
    nextTile = BFS.nextTile(util.tile)

    if config.debug is True:
        print("BFS START")

# print out entire path the robot took traversing the maze and how long the algorithm took
end = time.time()
print("\nTotal Path: " + str(packet.sData) + "\nBFS Done! All tiles visited in: " + format((end-start)*1000, '.4f') + "ms ")
display.show(-1, util.maze, 0)
cv2.destroyAllWindows()
packet.s.close()
packet.r.close()
