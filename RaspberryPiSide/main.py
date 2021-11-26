import BFS
import display
import cv2
import time
from BFS import util
from util import packet
from util import config

print("\nRaspberryPiSide START")
BFS.init()

print("Setup Finished\n\nrunning...")

# set start tile walls
util.setWalls()

# time calculation
ot = 0
start = time.time()

# calculate next tile
nextTile = BFS.nextTile(util.tile)

while nextTile is not None:
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
    packet.sData += config.serialMessages[5]

    # send driving instructions and do victim and do obstacle and do black tiles
    while util.path:
        # calculate driving instructions from path to next tile
        if config.debug:
            print("\tPath: " + str(util.path))

        # set direction to the direction to be turned
        util.direction = BFS.turnToTile(util.path.pop(), util.direction)
        util.tile = util.goForward(util.tile)

    # driving instructions calculated, add terminating character and send
    packet.sData += config.serialMessages[6]
    if config.inputMode == 1:
        packet.sendFileData(util.pathLen)

    # send driving instructions and do KNN  TODO: integrate w/ andy
    if config.inputMode == 2:
        packet.sendSerial(packet.sData[util.pathLen])
        util.pathLen += 1
        while util.pathLen < len(packet.sData) - 1:
            packet.sendSerial(packet.sData[util.pathLen:(util.pathLen + 2)])

            # victim goes here  TODO: send message if victim detected, add to maze

            util.pathLen += 2

        packet.sendSerial(packet.sData[-1])

    # print out path to only the next tile, reset length
    if config.debug:
        print("\tPath To Tile: " + str(packet.sData[util.pathLen:]))
        print()
    util.pathLen = len(packet.sData)

    # set tile new tile to visited, clear parent array
    util.maze[util.tile][util.visited] = 1
    util.parent.fill(-1)

    # get sensor/wall values
    util.setWalls()

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

# maze is done at this point, every tile has been visited, going back to start
BFS.pathToTile(util.tile, util.startTile)
if config.showDisplay:
    display.show(util.startTile, util.maze, config.displayRate)

while util.path:
    if config.debug:
        print("\tPath: " + str(util.path))

    util.direction = BFS.turnToTile(util.path.pop(), util.direction)
    util.tile = util.goForward(util.tile)

# print out entire path the robot took traversing the maze and how long the algorithm took
end = time.time()
print("\nTotal Path: " + str(packet.sData) + "\nBFS Done! All tiles visited in: " + format((end-start)*1000, '.2f') + "ms ")
display.show(-1, util.maze, 0)
cv2.destroyAllWindows()
