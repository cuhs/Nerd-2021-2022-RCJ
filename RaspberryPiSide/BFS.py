import util
import sys
import mazeToText
import IO
import display
import cv2
from util import np
from util import config
import letterDetection

def init():
    if config.mazeSideLen % 2 != 0 or not(2 <= config.mazeSideLen <= 80):
        raise ValueError("Invalid Maze Size (check config!)")
    if config.inputMode == 0 and config.displayRate is not 0:
        raise ValueError("displayRate must be 0 for manual input!")
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
    util.maze[util.tile][util.visited] = 1

    # increase recursion limit for large mazes
    sys.setrecursionlimit(config.recursionLimit)

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

    # packet setup
    IO.setupInput(config.inputMode)

    # display setup
    display.imgSetup()

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

# return next tile to visit recursively
def nextTile(cTile):
    if config.debug:
        print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[util.tile][util.visited]))

    # base case, BFS done and cTile is target tile
    if util.maze[cTile][util.visited] == 0:
        util.q.clear()
        if config.debug:
            print("\tBFS - END, Tile:\t" + str(cTile))
        return cTile

    # stores how many tiles are unvisited
    possibleTiles = [0, 0, 0, 0]

    for i in range(4):
        if util.maze[cTile][i] == 0:
            # no wall in direction i
            if util.parent[util.adjTiles[i] + cTile] == -1:
                util.parent[util.adjTiles[i] + cTile] = cTile
                util.q.append(util.adjTiles[i] + cTile)
            possibleTiles[i] = 1

    if config.debug:
        print("\tQueue:\t" + str(util.q))

    # recursively finds unvisited tiles
    for i in range(len(possibleTiles)):
        if possibleTiles[i] == 1:
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

# searches for letter and color victims, marks and sends them
def searchForVictims():
    if config.debug:
        print("\t\t\tSTARTING CAMERA")

    while config.cameraCount > 0 and (not IO.ser.in_waiting):
        # check if cap is opened and throw error if not
        if not IO.cap[0].isOpened():
            print("\t\t\t\tERROR: CAMERA 1 NOT OPENED")
            return
        if config.cameraCount == 2 and (not IO.cap[1].isOpened()):
            print("\t\t\t\tERROR: CAMERA 2 NOT OPENED")
            return
        
        if config.showCameras:
            _, leftFrame = IO.cap[0].read()
            cv2.imshow("left", leftFrame)
            cv2.waitKey(1)

        # check if searching needed on left camera
        if util.maze[util.tile][util.dirToLeft(util.direction)] == 1 and util.maze[util.tile][util.nVictim + util.dirToLeft(util.direction)] == 0:
            # get letter and color victims
            leftLetterVictim, leftColorVictim = letterDetection.Detection().leftDetectFinal()

            # send and record letter victim
            if leftLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + leftLetterVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftLetterVictim)
                # IO.sendData(config.inputMode, leftLetterVictim)

            # send and record color victim
            elif leftColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + leftColorVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftColorVictim)
                # IO.sendData(config.inputMode, leftColorVictim)

        # check if searching is needed on right camera
        if config.cameraCount == 2 and util.maze[util.tile][util.dirToLeft(util.direction)] == 1 and util.maze[util.tile][util.nVictim + util.dirToRight(util.direction)] == 0:
            # get letter and color victims
            rightLetterVictim, rightColorVictim = letterDetection.Detection().rightDetectFinal()

            # send and record letter victim
            if rightLetterVictim is not None:
                print("\t\t\t\tLETTER VICTIM FOUND: " + rightLetterVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightLetterVictim)
                IO.sendData(config.inputMode, rightLetterVictim)

            # send and record color victim
            elif rightColorVictim is not None:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + rightColorVictim)
                util.maze[util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(rightColorVictim)
                IO.sendData(config.inputMode, rightColorVictim)

    # remove ending of movement message from buffer
    if config.debug:
        print("\t\t\tCAMERA OVER, GOT: " + str(IO.ser.read()))
    else:
        IO.ser.read()
