import BFS
import display
import cv2
import time
import detection2
from BFS import util
from util import IO
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

    # calculate and send driving instructions
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

    # send beginning char "{"
    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1], util.pathLen == len(IO.sData) - 1)
    if config.debug:
        print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
    util.pathLen += 1

    # send driving instructions one at a time
    while util.pathLen < len(IO.sData):
        IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2], util.pathLen == len(IO.sData) - 2)
        if config.debug:
            print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 2])
        util.pathLen += 2

        # camera stuff
        if config.inputMode == 2:
            while (not IO.hasSerialMessage()) and IO.cap1.isOpened():  # and IO.cap2.isOpened
                ret1, frame1 = IO.cap1.read()
                # ret2, frame2 = IO. cap2.read()

                if ret1 > 0:  # and ret2 > 0
                    result1 = detection2.detection().KNN_finish(detection2.detection().letterDetect(frame1, "frame1"), 10000000)
                    # detection2.detection().KNN_finish(detection2.detection().letterDetect(frame2, "frame2"), 10000000)
                    
                    print(result1)

                if config.debug:
                    cv2.imshow("frame1", frame1)
                    # cv2.imshow("frame2", frame2)


    # send ending char "}"
    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1], util.pathLen == len(IO.sData) - 1)
    if config.debug:
        print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
    util.pathLen += 1

    # print out path to only the next tile, reset length
    if config.debug:
        print("\tPath To Tile: " + str(IO.sData[util.pathLen:]))

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

if config.inputMode == 2:
    IO.cap1.release()
    # IO.cap2.release()
cv2.destroyAllWindows()