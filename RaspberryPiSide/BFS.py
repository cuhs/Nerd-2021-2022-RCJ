import util
import sys
import time
import mazeToText
import IO
import display
import cv2
from util import np
from util import config
import letterDetection
import inspect
from vidThread import VideoGet
import RPi.GPIO as GPIO

def reset():
    util.maze = np.zeros((config.mazeSideLen ** 2, util.tileLen), dtype=np.int8)  # maze[tile][attributes], read util
    util.tile = util.startTile  # creates start tile in the middle of size x size area
    util.direction = util.Dir.N.value  # starting direction is set to north

    # queue (just a list) and parent array for BFS
    util.q = []
    util.parent = np.zeros(config.mazeSideLen ** 2, dtype=np.int16)
    util.parent.fill(-1)

    # stack (just a list) for path to tile
    util.path = []
    util.pathLen = 0

    # set starting tile as visited
    util.maze[util.tile][util.visited] = True

def init():
    if config.mazeSideLen % 2 != 0 or not(2 <= config.mazeSideLen <= 80):
        raise ValueError("Invalid Maze Size (check config!)")
    if config.inputMode == 0 and config.displayRate is not 0:
        raise ValueError("displayRate must be 0 for manual input!")
    reset()

    # increase recursion limit for large mazes
    sys.setrecursionlimit(config.recursionLimit + len(inspect.stack()) + 10)

    if config.inputMode == 1 and not config.redoLastMaze:
        if config.genFromImage:
            mazeToText.genMazeFromImage()
        else:
            mazeToText.genRandMaze()

    # display maze when repeating
    elif config.redoLastMaze:
        dMaze = np.copy(util.maze)
        r = IO.inputFile("r")
        r.readline()
        for i in range(config.mazeSideLen ** 2):
            dMaze[i][:] = [int(j) for j in str(r.readline())[:10]]
        display.show(-1, dMaze, 0)

    # display setup
    display.imgSetup()
    
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
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(16,GPIO.OUT)
        
def blink():
    for i in range(5):
        GPIO.output(16, GPIO.HIGH) # Turn on
        time.sleep(1)                  # Sleep for 1 second
        GPIO.output(16, GPIO.LOW)  # Turn off
        time.sleep(1)                  # Sleep for 1 second

# return next tile to visit recursively
def nextTile(cTile):
    if config.BFSDebug:
        print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[util.tile][util.visited]))

    # base case, BFS done and cTile is target tile
    if not util.maze[cTile][util.visited]:
        util.q.clear()
        if config.BFSDebug:
            print("\tBFS - END, Tile:\t" + str(cTile))
        return cTile

    for i in range(4):
        if not util.maze[cTile][i]:
            # no wall in direction i
            if util.parent[util.adjTiles[i] + cTile] == -1:
                util.parent[util.adjTiles[i] + cTile] = cTile
                util.q.append(util.adjTiles[i] + cTile)

    if config.BFSDebug:
        print("\tQueue:\t" + str(util.q))

    # recursively finds unvisited tiles
    if not util.q:
        return None
    return nextTile(util.q.pop(0))

# puts path to tile in a stack
def pathToTile(cTile, target):
    util.path.clear()
    i = target
    while i != cTile:
        util.path.append(int(i))
        i = util.parent[int(i)]

# handles black and silver tiles
def handleSpecialTiles(previousCheckpoint):
    # check if tile is a silver tile
    if util.isCheckpoint(util.maze, util.tile):
        if config.importantDebug or config.BFSDebug:
            print("\tTile " + str(util.tile) + " is a checkpoint tile, saving maze")

        # save maze to file
        IO.writeMaze(IO.saveFile("a"), str(util.tile) + IO.directions[util.direction], util.maze, True)
        return util.tile

    # check if tile is a black tile
    if util.isBlackTile(util.maze, util.tile):
        if config.importantDebug or config.BFSDebug:
            print("\tTile " + str(util.tile) + " is a black tile, going back")

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
        util.setWalls()
    else:
        # retrieve saved maze from file
        info, savedMaze = IO.readMaze(IO.saveFile("r"))

        # make sure file is up-to-date
        if checkpoint != int(info[:-1]):
            raise ValueError("Checkpoint mismatch")

        # reset maze, tile, and direction
        util.maze = np.copy(savedMaze)
        util.tile = checkpoint
        util.direction = util.Dir[info[-1]].value
        if config.importantDebug or config.BFSDebug:
            print("\tCheckpoint Loaded:\n\t\tTile: " + str(util.tile) + "\n\t\tDirection: " + str(util.direction))

    display.show(None, util.maze, config.displayRate)

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

        leftFrame = leftFrame[:,:152]
        
        if config.victimDebug or config.saveVictimDebug:
            cv2.imshow("left", leftFrame)
            cv2.waitKey(1)
            
        if config.cameraCount == 2:
            #rightRet, rightFrame = IO.cap[1].read()
            rightRet, rightFrame = IO.video_getter.grabbed2, IO.video_getter.frame2
            
            #print(IO.video_getter.frame2)
            
            rightFrame = rightFrame[:,:152]
            
            if config.victimDebug or config.saveVictimDebug:
                cv2.imshow("right", rightFrame)
                cv2.waitKey(1)

        # check if searching needed on left camera
        if util.maze[util.tile][util.nVictim + util.dirToLeft(util.direction)] == 0:
            # get letter and color victims
            leftLetterVictim, leftColorVictim = letterDetection.Detection().leftDetectFinal(leftRet, leftFrame)

            # send and record letter victim
            if leftLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + leftLetterVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftLetterVictim)
                IO.sendData(config.inputMode, leftLetterVictim)
                #blink()
                if config.victimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftLetterVictim + "-" + time.ctime(time.time()) + ".png"), leftFrame)
                break

            # send and record color victim
            if leftColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + leftColorVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftColorVictim)
                IO.sendData(config.inputMode, leftColorVictim)
                #blink()
                if config.victimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftColorVictim + "-" + time.ctime(time.time()) + ".png"), leftFrame)
                break

        # check if searching is needed on right camera
        if config.cameraCount == 2 and util.maze[util.tile][util.nVictim + util.dirToRight(util.direction)] == 0:
            # get letter and color victims
            rightLetterVictim, rightColorVictim = letterDetection.Detection().rightDetectFinal(rightRet, rightFrame)

            # send and record letter victim
            if rightLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + rightLetterVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightLetterVictim)
                IO.sendData(config.inputMode, rightLetterVictim)
                #blink()
                if config.victimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightLetterVictim + "-" + time.ctime(time.time()) + ".png"), rightFrame)
                break

            # send and record color victim
            elif rightColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + rightColorVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightColorVictim)
                IO.sendData(config.inputMode, rightColorVictim)
                #blink()
                if config.victimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightColorVictim + "-" + time.ctime(time.time()) + ".png"), rightFrame)
                break
        