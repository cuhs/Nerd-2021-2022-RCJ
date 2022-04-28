import cv2
import time
import BFS
import display
from BFS import util
from util import IO
from util import config

# time calculation
IO.startTime = time.time()
    
if config.importantDebug:
    print("\nRaspberryPiSide START")
    
BFS.init()

if config.importantDebug:
    print("Setup Finished, Running...")

# set start tile walls
inputWalls = util.setWalls()

# calculate next tile
nextTile, nextFloor = BFS.nextTile(util.tile, util.floor)
checkpoint = -1
loadingCheckpoint = False

while nextTile is not None or util.tile != util.startTile:
    # load checkpoints manually
    if config.manualCheckpointLoading:
        if cv2.waitKey(33) == ord('c'):
            if config.importantDebug:
                print("\tCheckpoint Manually Loaded")
            loadingCheckpoint = True

    # BFS start
    if config.BFSDebug:
        print("\tCurrent Tile:\t" + str((util.tile, util.floor)) + "\n\tNext Tile:\t" + str((nextTile, nextFloor)))
    # calculate path to target tile
    BFS.pathToTile(util.tile, util.floor, nextTile, nextFloor)
    if config.BFSDebug:
        print("\tTiles To Target Tile: " + str(len(util.path)))

    # display the maze
    if config.showDisplay:
        display.show(nextTile, nextFloor, util.maze, config.displayRate)

    # send BFS starting char '{'
    IO.sData += config.serialMessages[7]
    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1])
    if config.serialDebug:
        print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
    util.pathLen += 1

    # calculate instructions for next tile
    while util.path and not loadingCheckpoint:
        # calculate driving instructions from path to next tile
        if config.BFSDebug:
            print("\tPath: " + str(util.path))

        # set direction to the direction to be turned
        (nextTileInPath, nextFloorInPath) = util.path.pop()
        while util.floor == nextFloorInPath and util.tile + util.adjTiles[util.direction] != nextTileInPath and not loadingCheckpoint:
            # calculate next direction
            if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                util.direction = util.turnRight(util.direction)
            else:
                util.direction = util.turnLeft(util.direction)
            # send direction
            IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
            if config.serialDebug:
                print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 2])
            # find and send victims
            if config.inputMode == 2:
                if config.doVictim:
                    BFS.searchForVictims()

                    victimMsg = IO.getNextSerialByte()
                    if victimMsg == 'a':
                        loadingCheckpoint = True
                        break

                    if config.serialDebug:
                        print("\t\t\tCAMERA OVER, GOT: " + str(victimMsg))
            util.pathLen += 2

        if loadingCheckpoint:
            break

        # go up ramp if needed
        if util.floor != nextFloorInPath:
            # TODO
            # fix output directions to not show F; before and after U;/D;
            # fix {} formatting for U;/D;
            util.maze, util.tile, util.floor = util.goOnRamp(util.maze, util.tile, util.floor, nextFloorInPath > util.floor)
        else:
            # set the tile to the tile to be moved to
            util.tile = util.goForward(util.tile)

        IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
        if config.serialDebug:
            print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 2])
        # find and send victims
        if config.inputMode == 2:
            if config.doVictim:
                BFS.searchForVictims()

                victimMsg = IO.getNextSerialByte()
                if victimMsg == 'a':
                    loadingCheckpoint = True
                    break

                if config.serialDebug:
                    print("\t\t\tCAMERA OVER, GOT: " + str(victimMsg))
        util.pathLen += 2

    # send BFS ending char '}'
    if not loadingCheckpoint:
        IO.sData += config.serialMessages[8]
        IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1], True)
        if config.serialDebug:
            print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
        util.pathLen += 1

        # reset path string
        util.pathLen = len(IO.sData)

        # set tile new tile to visited, clear parent array
        util.maze[util.floor][util.tile][util.visited] = True
        util.parent.clear()

        # get sensor/wall values, take care of special tiles
        inputWalls = util.setWalls()

    # load checkpoint
    if loadingCheckpoint or inputWalls is None:
        BFS.loadCheckpoint(checkpoint)
        loadingCheckpoint = False
        util.maze[util.floor][util.tile][util.visited] = False
    else:
        # set black tile borders
        if (inputWalls is False) or (config.inputMode != 2 and util.isBlackTile(util.maze[util.floor], util.tile)):
            util.maze[util.floor] = util.setBlackTile(util.maze[util.floor], util.tile)

        # set ramps, checkpoints
        if config.inputMode == 2:
            # TODO
            # integrate up/down ramp detection
            # integrate silver tile detection
            if False:
                util.maze = util.setCheckpoint(util.maze[util.floor], util.tile)
            if False:
                util.maze = util.setRamp(util.maze, util.tile, util.floor, True)

        # handle black, silver, and ramp tiles
        checkpoint = BFS.handleSpecialTiles(checkpoint)

    # calculate next tile
    nextTile, nextFloor = BFS.nextTile(util.tile, util.floor)

    if config.BFSDebug:
        print("BFS START")

    # go back to start
    if nextTile is None and util.tile != util.startTile:
        if config.importantDebug or config.BFSDebug:
            print("Maze fully traversed! Going back to start tile")
        nextTile = util.startTile
        nextFloor = util.startFloor

# print out entire path the robot took traversing the maze and how long the algorithm took
end = time.time()
if config.importantDebug:
    print("\nTotal Path: " + str(IO.sData) + "\nBFS Done! All tiles visited in: " + format((end - IO.startTime) * 1000, '.2f') + "ms ")
display.show(None, None, util.maze, 0)

if config.inputMode == 2:
    for i in range(len(IO.cap)):
        IO.cap[i].release()
cv2.destroyAllWindows()
