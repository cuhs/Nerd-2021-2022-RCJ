import util
import sys
import time
import generateMaze
import IO
import display
import cv2
from util import np
from util import config
import letterDetection
import inspect
from vidThread import VideoGet
import RPi.GPIO as GPIO
import ast

def reset():
    util.maze = np.zeros((config.floorCount, config.mazeSideLen ** 2, util.tileLen), dtype=np.int8)  # maze[tile][attributes], read util
    util.tile = util.startTile  # creates start tile in the middle of size x size area
    util.floor = util.startFloor  # floor level
    util.direction = util.Dir.N.value  # starting direction is set to north

    # queue (just a list) and parent dictionary for BFS
    util.q = []
    util.parent = {}

    # stack (just a list) for path to tile
    util.path = []
    util.pathLen = 0

    # set starting tile as visited
    util.maze[util.floor][util.tile][util.visited] = True

def init():
    if config.mazeSideLen % 2 != 0 or not(4 <= config.mazeSideLen <= 80):
        raise ValueError("Invalid Maze Size (check config!)")
    if config.inputMode == 0 and config.displayRate is not 0:
        raise ValueError("config.displayRate Must Be 0 For Manual Input!")
    reset()

    # increase recursion limit for large mazes
    sys.setrecursionlimit(config.recursionLimit + len(inspect.stack()) + 10)

    if config.inputMode == 1:
        if config.genFromImage:
            generateMaze.genMazeFromImage()
        else:
            if not config.redoLastMaze:
                generateMaze.genRandMaze()

            # display maze when repeating
            dMaze = np.copy(util.maze)
            r = IO.inputFile("r")
            r.readline()
            for i in range(config.floorCount):
                for j in range(config.mazeSideLen ** 2):
                    dMaze[i][j][:] = [int(k) for k in str(r.readline())[:10]]

            # get ramp mappings
            util.rampMap = ast.literal_eval(r.readline())

            if config.redoLastMaze:
                display.show(None, None, dMaze, 0)

    # setup input from file or serial
    IO.setupInput(config.inputMode)

    # camera setup
    if config.inputMode == 2:
        if config.cameraCount == 1 or config.cameraCount == 2:
            if config.cameraCount == 1:
                IO.cap.append(cv2.VideoCapture(-1))
            else:
                IO.cap.append(cv2.VideoCapture(0))
            IO.cap[0].set(cv2.CAP_PROP_FRAME_WIDTH, config.cameraWidth)
            IO.cap[0].set(cv2.CAP_PROP_FRAME_HEIGHT, config.cameraHeight)

        if config.cameraCount == 2:
            IO.cap.append(cv2.VideoCapture(1))
            IO.cap[1].set(cv2.CAP_PROP_FRAME_WIDTH, config.cameraWidth)
            IO.cap[1].set(cv2.CAP_PROP_FRAME_HEIGHT, config.cameraHeight)

        if 2 < config.cameraCount < 0:
            raise ValueError("Invalid cameraCount (check config!)")

        #Start video threading
        IO.video_getter = VideoGet().start()

        #Sets up the LED for the PI
        #GPIO.setwarnings(False)
        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(16,GPIO.OUT)

'''def blink():
    for i in range(2):
        GPIO.output(16, GPIO.HIGH) # Turn on
        time.sleep(1)                  # Sleep for 1 second
        GPIO.output(16, GPIO.LOW)  # Turn off
        time.sleep(1)                  # Sleep for 1 second'''

# return next tile to visit recursively
def nextTile(cTile, cFloor):
    rampq = []
    q = [(cTile, cFloor)]

    while q or rampq:
        # update tile being checked
        if q:
            cTile, cFloor = q.pop(0)
        else:
            cTile, cFloor = rampq.pop(0)

        if config.BFSDebug:
            print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[cFloor][cTile][util.visited]))

        # base case, BFS done and cTile is target tile
        if not util.maze[cFloor][cTile][util.visited]:
            if config.BFSDebug:
                print("\tBFS - END, Tile:\t" + str(cTile))
            return cTile, cFloor

        for i in range(4):
            if not util.maze[cFloor][cTile][i] and util.tileExists(util.adjTiles[i] + cTile):
                # no wall in direction i
                if not ((util.adjTiles[i] + cTile, cFloor) in util.parent):
                    util.parent[(util.adjTiles[i] + cTile, cFloor)] = (cTile, cFloor)
                    q.append((util.adjTiles[i] + cTile, cFloor))

                    # adjacent to ramp
                    if util.maze[cFloor][util.adjTiles[i] + cTile][util.tileType] in (3, 4):
                        util.parent[util.rampMap[util.adjTiles[i] + cTile, cFloor]] = util.adjTiles[i] + cTile, cFloor
                        rampq.append(util.rampMap[util.adjTiles[i] + cTile, cFloor])

        if config.BFSDebug:
            print("\tQueue:\t" + str(q))

    # no tile
    if config.BFSDebug or config.importantDebug:
        print("\tBFS - NO NEXT TILE FOUND")
    return None, None

# puts path to tile in a stack
def pathToTile(cTile, cFloor, tTile, tFloor):
    util.path.clear()
    pTile = tTile
    pFloor = tFloor

    while not (pTile == cTile and pFloor == cFloor):
        util.path.append((int(pTile), int(pFloor)))
        (pTile, pFloor) = util.parent[(int(pTile), int(pFloor))]

# handles black and silver tiles
def handleSpecialTiles(walls, previousCheckpoint):
    # loading checkpoint
    if type(walls) is not np.ndarray:
        return previousCheckpoint

    # check if tile is a ramp tile
    if walls[util.tileType] in (3, 4):

        # floor adjustments
        rampAdjust = 1 if walls[util.tileType] == 3 else -1

        # add tile to ramp mappings
        if (util.tile, util.floor) not in util.rampMap:
            util.rampMap[util.tile, util.floor] = util.startTile, util.floor + rampAdjust
            util.rampMap[util.startTile, util.floor + rampAdjust] = util.tile, util.floor

        if config.importantDebug or config.BFSDebug:
            print("\t\tTILE, FLOOR: " + str(util.tile) + ", " + str(util.floor) + " is a ramp tile")
            print("\t\t\tRAMP MAP -> " + str(util.rampMap[util.tile, util.floor]))

        # create and go on ramp
        util.maze[util.floor][util.tile][util.tileType] = walls[util.tileType]
        util.setRampBorders(util.maze, util.tile, util.floor, util.oppositeDir(util.direction), rampAdjust == 1, util.rampMap[util.tile, util.floor][0])
        util.maze, util.tile, util.floor = util.goOnRamp(util.maze, util.tile, util.floor, rampAdjust == 1, False)

        # update walls
        if config.inputMode != 2:
            walls = util.getWalls()

        if config.importantDebug or config.BFSDebug:
            print("\t\tTILE, FLOOR is now: " + str(util.tile) + ", " + str(util.floor) + " after ramp tile")

    # set wall values
    for i in range(4):
        # prevent black tile walls from being overwritten
        if util.maze[util.floor][util.tile][i] == 0:
            util.maze[util.floor][util.tile][i] = walls[i]
    util.maze[util.floor][util.tile][4:] = walls[4:]

    # check if tile is a silver tile
    if util.isCheckpoint(util.maze[util.floor], util.tile):
        if config.importantDebug or config.BFSDebug:
            print("\tTile " + str(util.tile) + " is a checkpoint tile, saving maze")

        # save maze to file
        IO.writeMaze(IO.saveFile("a"), str(util.tile) + IO.directions[util.direction] + str(util.floor), util.maze[0], True)
        for i in range(1, config.floorCount):
            IO.writeMaze(IO.saveFile("a"), "", util.maze[i], False)
        return util.tile

    # check if tile is a black tile
    if util.isBlackTile(util.maze[util.floor], util.tile):
        # set borders for black tiles
        util.maze[util.floor] = util.setBlackTile(util.maze[util.floor], util.tile)

        if config.importantDebug or config.BFSDebug:
            print("\tTile " + str(util.tile) + " is a black tile, going back")

        # update tile to avoid black tile
        util.tile = util.goBackward(util.tile)

        if config.importantDebug or config.BFSDebug:
            print("\tTile is now " + str(util.tile) + " after black tile")

    return previousCheckpoint

# reset program to checkpoint
def loadCheckpoint(checkpoint):
    if config.importantDebug or config.BFSDebug:
        print("\tLoading Checkpoint " + str(checkpoint))

    # check if no checkpoints reached yet, reset if so
    if checkpoint == -1:
        reset()
        util.getWalls()
    else:
        # retrieve saved maze from file
        info, savedMaze = IO.readMaze(IO.saveFile("r"))

        # make sure file is up-to-date
        if checkpoint != int(info[:-2]):
            raise ValueError("Checkpoint Mismatch")

        # reset maze, tile, and direction
        util.maze = np.copy(savedMaze)
        util.tile = checkpoint
        util.floor = int(info[-1])
        util.direction = util.Dir[info[-2]].value
        if config.importantDebug or config.BFSDebug:
            print("\tCheckpoint Loaded:\n\t\tTile: " + str(util.tile) + "\n\t\tDirection: " + str(util.direction))

    display.show(None, None, util.maze, config.displayRate)

# searches for letter and color victims, marks and sends them
def searchForVictims():
    if config.victimDebug:
        print("\t\t\tSTARTING CAMERA")

    while config.cameraCount > 0 and (not IO.ser.in_waiting):
        # check if cap is opened and throw error if not
        if not IO.cap[0].isOpened():
            print("\t\t\t\tERROR: CAMERA 1 NOT OPENED")
            return
        if config.cameraCount == 2 and (not IO.cap[1].isOpened()):
            print("\t\t\t\tERROR: CAMERA 2 NOT OPENED")
            return
        
        #leftRet, leftFrame = IO.cap[0].read()
        leftRet, leftFrame = IO.video_getter.grabbed1, IO.video_getter.frame1

        leftFrame = leftFrame[:,:148]

        if config.victimDebug:
            cv2.imshow("left", leftFrame)
            cv2.waitKey(1)

        if config.cameraCount == 2:
            #rightRet, rightFrame = IO.cap[1].read()
            rightRet, rightFrame = IO.video_getter.grabbed2, IO.video_getter.frame2

            #print(IO.video_getter.frame2)

            rightFrame = rightFrame[:,:152]

            if config.victimDebug:
                cv2.imshow("right", rightFrame)
                cv2.waitKey(1)

        # check if searching needed on left camera
        if util.maze[util.floor][util.tile][util.nVictim + util.dirToLeft(util.direction)] == 0:
            # get letter and color victims
            leftLetterVictim, leftColorVictim = letterDetection.Detection().leftDetectFinal(leftRet, leftFrame)

            # send and record letter victim
            if leftLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + leftLetterVictim)
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftLetterVictim)
                IO.sendData(config.inputMode, leftLetterVictim)
                #blink()
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftLetterVictim + "-" + time.ctime(time.time()) + ".png"), leftFrame)
                break

            # send and record color victim
            if leftColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + leftColorVictim)
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftColorVictim)
                IO.sendData(config.inputMode, leftColorVictim)
                #blink()
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftColorVictim + "-" + time.ctime(time.time()) + ".png"), leftFrame)
                break

        # check if searching is needed on right camera
        if config.cameraCount == 2 and util.maze[util.floor][util.tile][util.nVictim + util.dirToRight(util.direction)] == 0:
            # get letter and color victims
            rightLetterVictim, rightColorVictim = letterDetection.Detection().rightDetectFinal(rightRet, rightFrame)

            # send and record letter victim
            if rightLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + rightLetterVictim)
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightLetterVictim)
                IO.sendData(config.inputMode, rightLetterVictim)
                #blink()
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightLetterVictim + "-" + time.ctime(time.time()) + ".png"), rightFrame)
                break

            # send and record color victim
            elif rightColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + rightColorVictim)
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightColorVictim)
                IO.sendData(config.inputMode, rightColorVictim)
                #blink()
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightColorVictim + "-" + time.ctime(time.time()) + ".png"), rightFrame)
                break

