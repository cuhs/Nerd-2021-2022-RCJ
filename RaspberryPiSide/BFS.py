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

def setupCams():
    # camera setup
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

def reset():
    if config.runMode:
        display.updateLabels(status="Resetting")

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
    
    # reset video save feed
    IO.vD = letterDetection.Detection()

    # setup input from file or serial
    return IO.setupInput(config.inputMode)

def init():
    if config.mazeSideLen % 2 != 0 or not(4 <= config.mazeSideLen <= 100):
        raise ValueError("Invalid Maze Size (check config!)")
    if config.inputMode == 0 and config.displayRate is not 0:
        raise ValueError("config.displayRate Must Be 0 For Manual Input!")

    # reset maze
    reset()
    if config.runMode:
        display.updateLabels(status="Start")

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
                display.showMaze(display.resetImg(dMaze), dMaze, None, None, None, 0)

# return next tile to visit using BFS
def nextTile(cTile, cFloor):
    if config.runMode:
        display.updateLabels(status="BFS")
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
    if config.runMode:
        display.updateLabels(status="Silver")
    if config.importantDebug or config.BFSDebug:
        print("\tTile " + str(util.tile) + " is a checkpoint tile, saving maze")

    # save maze to file
    IO.writeMaze(IO.saveFile("a"), IO.directions[util.direction] + str(util.floor) + str(util.rampMap), util.maze[0], True)
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
        if config.runMode:
            display.updateLabels(status="Ramp")
        rampAdjust = 1 if walls[util.tileType] == 3 else -1
        walls[util.tileType] = 0

        # add tile to ramp mappings
        if (util.tile, util.floor) not in util.rampMap:
            util.rampMap[util.tile, util.floor] = util.tile + (util.adjTiles[util.direction] * util.rampTileCount), util.floor + rampAdjust
            util.rampMap[util.tile + (util.adjTiles[util.direction] * util.rampTileCount), util.floor + rampAdjust] = util.tile, util.floor
        util.rampTileCount = None

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
        if config.runMode:
            display.updateLabels(status="Black")

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
        if config.inputMode == 2:
            backWall = util.getBackWall()
        util.maze[util.floor][util.tile] = util.getWalls()
        if config.inputMode == 2:
            util.maze[util.floor][util.tile][util.oppositeDir(util.direction)] = backWall
    else:
        # retrieve saved maze from file
        info, savedMaze = IO.readMaze(IO.saveFile("r"))

        # reset maze, tile, and direction
        util.maze = np.copy(savedMaze)
        util.tile = checkpoint
        util.floor = int(info[1])
        util.direction = util.Dir[info[0]].value
        util.parent = {}
        util.rampMap = ast.literal_eval(info[2:])
        util.rampTileCount = None
        display.img = display.resetImg(util.maze)
        if config.importantDebug or config.BFSDebug:
            print("\tCheckpoint Loaded:\n\t\tTile: " + str(util.tile) + "\n\t\tDirection: " + str(util.direction))

        # blink LED and wait for startup
        if config.inputMode == 2:
            IO.setupInput(config.inputMode)
            IO.sendSerial('n')

        # get walls on startup
        util.maze[util.floor][util.tile] = util.getWalls()

    if config.showDisplay:
        display.showMaze(display.img, util.maze, None, util.floor, None, config.displayRate)

# searches for letter and color victims, marks and sends them
def searchForVictims(goingForward, turnDirection=None, didTurn=False, didForward=False):
    if config.runMode:
        display.updateLabels(status="Victim")

    if config.victimDebug:
        print("\t\t\tSTARTING CAMERA")

    while config.cameraCount > 0 and (not IO.ser.in_waiting):
        # check if cap is opened and throw error if not
        if not IO.cap[0].isOpened():
            print("\t\t\t\tERROR: CAMERA 1 NOT OPENED")
        if config.cameraCount == 2 and (not IO.cap[1].isOpened()):
            print("\t\t\t\tERROR: CAMERA 2 NOT OPENED")

        # get letter and color victims
        # Left or Right, Letter or Color, Victim or Position
        LLV, LLX, LCV, LCX = IO.vD.leftDetectFinal(IO.frame[0][0], IO.frame[0][1][config.cameraCutL[0]:config.cameraCutL[1],config.cameraCutL[2]:config.cameraCutL[3]])

        if LLV or LCV:
            LVic = LLV if LLV else LCV
            LVicX = LLX if LLV else LCX
            LVic = LVic.lower()

            if config.runMode:
                display.updateLabels(LVictim=LVic)
            if config.victimDebug:
                print("\t\t\t\t\t\tVICTIM ON LEFT: " + LVic)

            vTile = tileOfVictim(LVic, LVicX, didForward) if goingForward else util.tile
            vDirection = util.dirToLeft(util.direction) if goingForward else directionOfVictim(LVic, LVicX, turnDirection, didTurn)
            if (vDirection is not None) and (vTile is not None) and (not util.maze[util.floor][vTile][vDirection + util.nVictim]):
                if config.saveVictimDebug:
                    saveVictim(LVic)
                if config.importantDebug or config.serialDebug or config.victimDebug:
                    print("\t\t\t\t\t\t\tNEW VICTIM ON LEFT: " + LVic)
                util.maze[util.floor][vTile][vDirection + util.nVictim] = ord(LVic)
                IO.sendData(config.inputMode, LVic)

        # check if searching is needed on right camera
        if config.cameraCount == 2:
            # get letter and color victims
            # Left or Right, Letter or Color, Victim or X-position
            RLV, RLX, RCV, RCX = IO.vD.rightDetectFinal(IO.frame[1][0], IO.frame[1][1][config.cameraCutR[0]:config.cameraCutR[1],config.cameraCutR[2]:config.cameraCutR[3]])

            # send and record color victim
            if RLV or RCV:
                RVic = RLV if RLV else RCV
                RVicX = RLX if RLV else RCX
                RVic = RVic.upper()

                if config.runMode:
                    display.updateLabels(RVictim=RVic)
                if config.victimDebug:
                    print("\t\t\t\t\t\tVICTIM ON RIGHT: " + RVic)

                vTile = tileOfVictim(RVic, RVicX, didForward) if goingForward else util.tile
                vDirection = util.dirToRight(util.direction) if goingForward else directionOfVictim(RVic, RVicX, turnDirection, didTurn)
                if (vDirection is not None) and (vTile is not None) and (not util.maze[util.floor][vTile][vDirection + util.nVictim]):
                    if config.saveVictimDebug:
                        saveVictim(RVic)
                    if config.importantDebug or config.serialDebug or config.victimDebug:
                        print("\t\t\t\t\t\t\tNEW VICTIM ON RIGHT: " + RVic)
                    util.maze[util.floor][vTile][vDirection + util.nVictim] = ord(RVic)
                    IO.sendData(config.inputMode, RVic)

def tileOfVictim(cVictim, cPos, wentForward):
    cDirection = util.dirToLeft(util.direction) if cVictim.islower() else util.dirToRight(util.direction)
    backTile = util.goBackward(util.tile) if wentForward else util.tile
    frontTile = util.tile if wentForward else util.goBackward(util.tile)
    
    # i disagree with this wholeheartedly
    if util.maze[util.floor][backTile][cDirection + util.nVictim] == ord(cVictim) or util.maze[util.floor][frontTile][cDirection + util.nVictim] == ord(cVictim):
        return None
    
    # check if both tiles have possible walls for victims
    checkPosition = util.maze[util.floor][backTile][cDirection] and (util.maze[util.floor][frontTile][cDirection] if util.maze[util.floor][frontTile][util.visited] else True)
    if not checkPosition:
        #print("no two walls")
        if util.maze[util.floor][backTile][cDirection]:
            #print("back")
            return backTile
        #print("front")
        return frontTile

    # calculate percentage forward of victim
    if cVictim.islower():
        cPos = (cPos / (config.cameraCutL[3] - config.cameraCutL[2])) * 100
    else:
        cPos = 100 - ((cPos / (config.cameraCutR[3] - config.cameraCutR[2])) * 100)
        
    #print("\tpos:" + str(cPos))

    # victim likely in next/previous tile, ignore
    if (wentForward and cPos < 40) or (not wentForward and cPos > 60):
        #print("\t\tnot in bounds")
        return None

    # use victim position to determine tile
    if wentForward:
        #print("\t\t\t\tfront")
        return frontTile
    #print("\t\t\t\tback")
    return backTile

def directionOfVictim(cVictim, cPos, turnDirection, didTurn):
    startDirection = util.dirToRight(util.direction) if turnDirection == "L" else util.dirToLeft(util.direction) if didTurn else util.direction
    startCamDirection = util.dirToLeft(startDirection) if cVictim.islower() else util.dirToRight(startDirection)
    endCamDirection = util.dirToLeft(startCamDirection) if turnDirection == "L" else util.dirToRight(startCamDirection)

    # i disagree with this wholeheartedly
    if util.maze[util.floor][util.tile][startCamDirection + util.nVictim] == ord(cVictim) or util.maze[util.floor][util.tile][endCamDirection + util.nVictim] == ord(cVictim):
        return None

    # check if both directions have possible walls
    checkPosition = util.maze[util.floor][util.tile][startCamDirection] and util.maze[util.floor][util.tile][endCamDirection]
    if not checkPosition:
        #print("no two walls")
        if util.maze[util.floor][util.tile][startCamDirection]:
            print("start")
            return startCamDirection
        #print("end")
        return endCamDirection

    # calculate percentage forward of victim
    if cVictim.islower():
        cPos = (cPos / (config.cameraCutL[3] - config.cameraCutL[2])) * 100
    else:
        cPos = 100 - ((cPos / (config.cameraCutR[3] - config.cameraCutR[2])) * 100)

    # victim likely in next/previous tile, ignore
    if (didTurn and cPos > 90) or (not didTurn and cPos < 10):
        return None

    # use victim position to determine direction
    if didTurn:
        #print("DIDTURN")
        if cPos < 40:
            #print("start")
            return startCamDirection
        #print("end")
        return endCamDirection
    if cPos > 80:
        #print("end")
        return endCamDirection
    #print("start")
    return startCamDirection

def saveVictim(victim):
    cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + victim + "-" + time.ctime(time.time()) + ".png"),
                IO.frame[0][1][config.cameraCutL[0]:config.cameraCutL[1], config.cameraCutL[2]:config.cameraCutL[3]])
