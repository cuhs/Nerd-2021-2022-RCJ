import BFS
import display
import cv2
import time
from BFS import util
from util import IO
from util import config

print("\nRaspberryPiSide START")
BFS.init()

print("Setup Finished\n\nrunning...")

# set start tile walls, if serial, turn to get back wall
util.setWalls()

# turn to get wall values on start if serial
if config.inputMode == 2:
    IO.sData += config.serialMessages[5]
    util.direction = BFS.turnToTile(util.tile, util.dirToLeft(util.direction))
    IO.sData += config.serialMessages[6]
    IO.sendSerial(IO.sData)

    util.setWalls()

# time calculation
ot = 0
start = time.time()

# calculate next tile
nextTile = BFS.nextTile(util.tile)
lastCheckpoint = -1

while nextTile is not None or util.tile != util.startTile:
    if config.debug:
        print("\tCurrent Tile:\t" + str(util.tile) + "\n\tNext Tile:\t" + str(nextTile))
    # calculate path to target tile
    BFS.pathToTile(util.tile, nextTile)
    if config.debug:
        print("\tTiles To Target Tile: " + str(len(util.path)))

    # display the maze
    if config.showDisplay:
        display.show(nextTile, util.maze, config.displayRate)

    # start of driving instructions
    IO.sData += config.serialMessages[5]

    # send driving instructions and do victim and do obstacle and do black tiles
    while util.path:
        # calculate driving instructions from path to next tile
        if config.debug:
            print("\tPath: " + str(util.path))

        # set direction to the direction to be turned
        util.direction = BFS.turnToTile(util.path.pop(), util.direction)
        util.tile = util.goForward(util.tile)

    # driving instructions calculated, add terminating character and send
    IO.sData += config.serialMessages[6]
    if config.inputMode == 1:
        IO.sendFileData(util.pathLen)

    # send driving instructions and do KNN  TODO: integrate w/ andy
    if config.inputMode == 2:
        IO.sendSerial(IO.sData[util.pathLen])
        util.pathLen += 1
        while util.pathLen < len(IO.sData) - 1:
            IO.sendSerial(IO.sData[util.pathLen:(util.pathLen + 2)])

            if config.debug:
                print("Starting Victim")

            while not IO.hasSerialMessage():
                if config.debug:
                    print("\tChecking Victim")

                # check & mark victims

                time.sleep(0.1)

            util.pathLen += 2

        IO.sendSerial(IO.sData[-1])

    # print out path to only the next tile, reset length
    if config.debug:
        print("\tPath To Tile: " + str(IO.sData[util.pathLen:]))
        print()
    util.pathLen = len(IO.sData)

    # set tile new tile to visited, clear parent array
    util.maze[util.tile][util.visited] = 1
    util.parent.fill(-1)

    # get sensor/wall values
    util.setWalls()

    # check if tile is a silver tile
    if util.isCheckpoint(util.maze, util.tile):
        if config.debug:
            print("\tTile " + str(util.tile) + " is a checkpoint tile, saving maze")

        lastCheckpoint = util.tile
        IO.writeMaze(IO.saveFile("a"), str(util.tile) + IO.directions[util.direction], util.maze, True)

    # check if tile is a black tile
    if util.isBlackTile(util.maze, util.tile):
        if config.debug:
            print("\tTile " + str(util.tile) + " is a black tile, going back")

        util.maze = util.setBlackTile(util.maze, util.tile, setBorders=True)
        util.tile = util.goBackward(util.tile)

        if config.debug:
            print("\tTile now " + str(util.tile) + " after black tile")

    # calculate next tile
    nextTile = BFS.nextTile(util.tile)

    if config.debug:
        print("BFS START")

    # go back to start
    if nextTile is None and util.tile != util.startTile:
        if config.debug:
            print("Maze fully traversed! Going back to start tile")
        nextTile = util.startTile

# print out entire path the robot took traversing the maze and how long the algorithm took
end = time.time()
print("\nTotal Path: " + str(IO.sData) + "\nBFS Done! All tiles visited in: " + format((end - start) * 1000, '.2f') + "ms ")
display.show(-1, util.maze, 0)
cv2.destroyAllWindows()
