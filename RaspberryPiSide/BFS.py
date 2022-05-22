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
import ast
import os

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
    IO.sData = ""

    # set starting tile as visited
    util.maze[util.floor][util.tile][util.visited] = True

    # reset display
    display.img = display.setupImg()
    
    # setup input from file or serial
    IO.setupInput(config.inputMode)

def init():
    if config.mazeSideLen % 2 != 0 or not(4 <= config.mazeSideLen <= 100):
        raise ValueError("Invalid Maze Size (check config!)")
    if config.inputMode == 0 and config.displayRate is not 0:
        raise ValueError("config.displayRate Must Be 0 For Manual Input!")

    # reset maze
    reset()

    # increase recursion limit for large mazes
    sys.setrecursionlimit(config.recursionLimit + len(inspect.stack()) + 10)

    # generate maze if needed
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
                display.show(display.resetImg(dMaze), dMaze, None, None, 0)

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

        # start video threading
        IO.videoGetter = VideoGet().start()
        
    if config.saveVictimDebug:
        os.mkdir(config.fpVIC + (time.ctime(IO.startTime)))

# return next tile to visit using BFS
def nextTile(cTile, cFloor):
    rampq = []
    q = [(cTile, cFloor)]

    while q or rampq:
        # update tile and floor being checked
        if q:
            cTile, cFloor = q.pop(0)
        else:
            cTile, cFloor = rampq.pop(0)

        if config.BFSDebug:
            print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[cFloor][cTile][util.visited]))

        # BFS done and cTile is target tile
        if not util.maze[cFloor][cTile][util.visited]:
            if config.BFSDebug:
                print("\tBFS - END, Tile:\t" + str(cTile))
            return cTile, cFloor

        for i in range(len(util.Dir)):
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

    # no unvisited tiles
    if config.BFSDebug or config.importantDebug:
        print("\tBFS - NO NEXT TILE FOUND")
    return None, None

# puts path to tile in a stack for popping
def pathToTile(cTile, cFloor, tTile, tFloor):
    util.path.clear()
    pTile = tTile
    pFloor = tFloor

    while not (pTile == cTile and pFloor == cFloor):
        util.path.append((int(pTile), int(pFloor)))
        (pTile, pFloor) = util.parent[(int(pTile), int(pFloor))]

# save checkpoint
def saveCheckpoint():
    if config.importantDebug or config.BFSDebug:
        print("\tTile " + str(util.tile) + " is a checkpoint tile, saving maze")

    # save maze to file
    IO.writeMaze(IO.saveFile("a"), str(util.tile) + IO.directions[util.direction] + str(util.floor), util.maze[0], True)
    for i in range(1, config.floorCount):
        IO.writeMaze(IO.saveFile("a"), "", util.maze[i], False)
    return util.tile

# handles black, silver, and ramp tiles
def handleSpecialTiles(walls, previousCheckpoint):
    # loading checkpoint
    if type(walls) is not np.ndarray:
        return previousCheckpoint

    # check if tile is a ramp tile
    if walls[util.tileType] in (3, 4):

        # floor adjustments
        #util.tile = util.goBackward(util.tile)
        #util.tile = util.goForward(util.tile, False)
        rampAdjust = 1 if walls[util.tileType] == 3 else -1
        walls[util.tileType] = 0

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
    for i in range(len(util.Dir)):
        # prevent black tile walls from being overwritten
        if util.maze[util.floor][util.tile][i] == 0:
            util.maze[util.floor][util.tile][i] = walls[i]
    util.maze[util.floor][util.tile][util.visited] = walls[util.visited]
    util.maze[util.floor][util.tile][util.tileType] = walls[util.tileType]

    # check if tile is a silver tile
    if util.isCheckpoint(util.maze[util.floor], util.tile):
        return saveCheckpoint()

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

# reset program to last checkpoint
def loadCheckpoint(checkpoint):
    if config.importantDebug or config.BFSDebug:
        print("\tLoading Checkpoint " + str(checkpoint))

    # reset to start if no previous checkpoints have been loaded
    if checkpoint == -1:
        reset()
        util.maze[util.floor][util.tile] = util.getWalls()
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
        util.parent = {}
        display.img = display.resetImg(util.maze)
        if config.importantDebug or config.BFSDebug:
            print("\tCheckpoint Loaded:\n\t\tTile: " + str(util.tile) + "\n\t\tDirection: " + str(util.direction))

        # get walls on startup
        util.maze[util.floor][util.tile] = util.getWalls()

    if config.showDisplay:
        display.show(display.img, util.maze, None, None, config.displayRate)

# searches for letter and color victims, marks and sends them
def searchForVictims():
    if config.victimDebug:
        print("\t\t\tSTARTING CAMERA")

    while config.cameraCount > 0 and (not IO.ser.in_waiting):
        # check if cap is opened and throw error if not
        if not IO.cap[0].isOpened():
            print("\t\t\t\tERROR: CAMERA 1 NOT OPENED")
        if config.cameraCount == 2 and (not IO.cap[1].isOpened()):
            print("\t\t\t\tERROR: CAMERA 2 NOT OPENED")

        # get letter and color victims
        leftLetterVictim, leftColorVictim = letterDetection.Detection().leftDetectFinal(IO.frame[0][0], IO.frame[0][1][:,:150])

        # send and record letter victim
        if leftLetterVictim is not None:
            leftLetterVictim = leftLetterVictim.lower()
            if config.victimDebug or config.importantDebug:
                print("\t\t\t\tLETTER VICTIM FOUND: " + leftLetterVictim + " AT TILE: " + str((util.tile, util.floor)) + " DIRECTION: " + str(util.dirToLeft(util.direction)))
            if not util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim]:
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftLetterVictim)
                IO.sendData(config.inputMode, leftLetterVictim)
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftLetterVictim + "-" + time.ctime(time.time()) + ".png"), IO.frame[0][1][:,:150])

        # send and record color victim
        elif leftColorVictim is not None:
            leftColorVictim = leftColorVictim.lower()
            if config.victimDebug or config.importantDebug:
                print("\t\t\t\tCOLOR VICTIM FOUND: " + leftColorVictim + " AT TILE: " + str((util.tile, util.floor)) + " DIRECTION: " + str(util.dirToLeft(util.direction)))
            if not util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim]:
                util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(leftColorVictim)
                IO.sendData(config.inputMode, leftColorVictim)
                if config.saveVictimDebug:
                    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftColorVictim + "-" + time.ctime(time.time()) + ".png"), IO.frame[0][1][:,:150])

        # check if searching is needed on right camera
        if config.cameraCount == 2:
            # get letter and color victims
            rightLetterVictim, rightColorVictim = letterDetection.Detection().rightDetectFinal(IO.frame[1][0], IO.frame[1][1][:,:150])

            # send and record letter victim
            if rightLetterVictim is not None:
                rightLetterVictim = rightLetterVictim.upper()
                if config.victimDebug or config.importantDebug:
                    print("\t\t\t\tLETTER VICTIM FOUND: " + rightLetterVictim + " AT TILE: " + str((util.tile, util.floor)) + " DIRECTION: " + str(util.dirToRight(util.direction)))
                if not util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim]:
                    util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim] = ord(rightLetterVictim)
                    IO.sendData(config.inputMode, rightLetterVictim)
                    if config.saveVictimDebug:
                        cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightLetterVictim + "-" + time.ctime(time.time()) + ".png"), IO.frame[1][1][:,:150])

            # send and record color victim
            elif rightColorVictim is not None:
                rightColorVictim = rightColorVictim.upper()
                if config.victimDebug or config.importantDebug:
                    print("\t\t\t\tCOLOR VICTIM FOUND: " + rightColorVictim + " AT TILE: " + str((util.tile, util.floor)) + " DIRECTION: " + str(util.dirToRight(util.direction)))
                if not util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim]:
                    util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim] = ord(rightColorVictim)
                    IO.sendData(config.inputMode, rightColorVictim)
                    if config.saveVictimDebug:
                        cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightColorVictim + "-" + time.ctime(time.time()) + ".png"), IO.frame[1][1][:,:150])
