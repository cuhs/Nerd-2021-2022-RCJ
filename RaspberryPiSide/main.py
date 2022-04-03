"""
TODO:
- Add supplemental turns to check all walls for victims
- Integrate black and silver tiles
- Integrate Obstacle
- Have different debug levels
"""

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

# set start tile walls
util.setWalls()

# time calculation
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

    # send BFS starting char '{'
    IO.sData += config.serialMessages[5]
    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1])
    if config.debug:
        print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
    util.pathLen += 1

    # calculate instructions for next tile
    while util.path:
        # calculate driving instructions from path to next tile
        if config.debug:
            print("\tPath: " + str(util.path))

        # set direction to the direction to be turned
        nextTileInPath = util.path.pop()
        while util.tile + util.adjTiles[util.direction] != nextTileInPath:
            # calculate next direction
            if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                util.direction = util.turnRight(util.direction)
            else:
                util.direction = util.turnLeft(util.direction)
            # send direction
            IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
            if config.debug:
                print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 2])
            # find and send victims
            if config.inputMode == 2:
                if config.doVictim:
                    BFS.searchForVictims()
                else:
                    if config.debug:
                        print("\t\t\tCAMERA OVER, GOT: " + str(IO.ser.read()))
                    else:
                        IO.ser.read()
            util.pathLen += 2

        # set the tile to the tile to be moved to
        util.tile = util.goForward(util.tile)
        IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
        if config.debug:
            print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 2])
        # find and send victims
        if config.inputMode == 2:
            if config.doVictim:
                BFS.searchForVictims()
            else:
                if config.debug:
                    print("\t\t\tCAMERA OVER, GOT: " + str(IO.ser.read()))
                else:
                    IO.ser.read()
        util.pathLen += 2

    # send BFS ending char '}'
    IO.sData += config.serialMessages[6]
    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1], True)
    if config.debug:
        print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
    util.pathLen += 1

    # reset path string
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

        util.maze = util.setBlackTile(util.maze, util.tile)
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

if config.inputMode == 2:
    for i in range(len(IO.cap)):
        IO.cap[i].release()
cv2.destroyAllWindows()
