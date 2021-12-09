import BFS
import display
import cv2
import detection2
import time
from BFS import util
from util import IO
from util import config

print("\nRaspberryPiSide START")
BFS.init()

victim = detection2.detection()

print("Setup Finished\n\nrunning...")

# set start tile walls
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

    # calculate and send driving instructions
    if config.inputMode != 2:
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

    # serial sending directions
    else:
        # add starting char to
        IO.sData += config.serialMessages[5]

        # while driving instructions remain
        while util.path:
            # set direction to the direction to be turned
            util.direction = BFS.turnToTile(util.path.pop(), util.direction)
            util.tile = util.goForward(util.tile)

            if config.debug:
                print("Sent:" + IO.sData[util.pathLen:(util.pathLen + 2)] + "\nStarting Victim")

            while not IO.hasSerialMessage():
                if config.debug:
                    print("\tChecking Victim")

                if not(IO.cap1.isOpened()) or not(IO.cap2.isOpened()):
                    raise ConnectionError("One or more cameras were not opened!")

                ret1, frame1 = IO.cap1.read()
                ret2, frame2 = IO.cap2.read()
                
                if ret1 > 0:
                    lVictim = victim.KNN_finish(victim.letterDetect(frame1, "frame1"), 10000000)
                    
                if ret2 > 0:
                    rVictim = victim.KNN_finish(victim.letterDetect(frame2, "frame2"), 10000000)

                if config.debug:
                    print("Left Victim: " + lVictim + "\nRight Victim: " + rVictim)
                    cv2.imshow("frame1", frame1)
                    cv2.imshow("frame2", frame2)

                # sleep for serial & camera, MUST BE AT LEAST 0.1
                time.sleep(0.1)

        IO.sData += config.serialMessages[6]
        IO.sendSerial(IO.sData[-1])

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
cv2.destroyAllWindows()