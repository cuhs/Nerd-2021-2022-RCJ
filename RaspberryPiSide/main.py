import cv2
import time
import BFS
import display
from BFS import util
from util import IO
from util import config
if config.inputMode == 2:
    from IO import GPIO
if config.runMode:
    from PyQt5.QtCore import QThread
import traceback

class AThread(QThread if config.runMode else object):
    def run(self):
        # time calculation
        IO.startTime = time.time()

        if config.importantDebug:
            print("\nRaspberryPiSide START")

        # initialize, (calls reset)
        BFS.init()

        if config.importantDebug:
            print("Setup Finished, Running...")

        # set start tile walls
        inputWalls = util.getWalls()
        util.maze[util.floor][util.tile] = inputWalls

        # calculate next tile
        nextTile, nextFloor = BFS.nextTile(util.tile, util.floor)
        checkpoint = -1
        loadingCheckpoint = False

        # loop while there are still tiles to move to
        while nextTile is not None or util.tile != util.startTile:
            if config.runMode:
                display.updateLabels(tTile=nextTile, tFloor=nextFloor)

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

            # send BFS starting char '{'
            IO.sData += config.serialOutMsgs[7]
            IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1])
            if config.serialDebug:
                print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
            util.pathLen += 1

            # display the maze
            if config.showDisplay:
                display.showMaze(display.img, util.maze, nextFloor, util.floor, nextTile, config.displayRate)

            # calculate instructions for next tile in the path
            while util.path and not loadingCheckpoint:
                if config.BFSDebug:
                    print("\tPath: " + str(util.path))

                # update next tile and floor in path
                (nextTileInPath, nextFloorInPath) = util.path.pop()
                while util.floor == nextFloorInPath and util.tile + util.adjTiles[util.direction] != nextTileInPath and not loadingCheckpoint:
                    # calculate next direction and turns required
                    if config.inputMode == 1:
                        if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                            util.direction = util.turnRight(util.direction, True)
                        else:
                            util.direction = util.turnLeft(util.direction, True)
                        if config.runMode:
                            display.updateLabels(cDir=util.direction)
                    else:
                        if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                            util.turnRight(util.direction, True)
                        else:
                            util.turnLeft(util.direction, True)

                    # update checkpoint
                    if util.isCheckpoint(util.maze[util.floor], util.tile):
                        checkpoint = BFS.saveCheckpoint()

                    # send turns
                    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
                    if config.serialDebug:
                        print("\t\tSENDINGD: " + IO.sData[util.pathLen:util.pathLen + 2])

                    # find and send victims
                    if config.inputMode == 2:
                        if config.doVictim:
                            victimMsg = None
                            didTurn = False

                            # loop through messages and victim checking until movement done
                            while victimMsg != ';':
                                LL, LLP, LC, LCP, RL, RLP, RC, RCP = BFS.searchForVictims()

                                # left letter detected
                                if LL and not util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim]:
                                    util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(LL)
                                    IO.sendData(config.inputMode, LL)
                                    if config.saveVictimDebug:
                                        BFS.saveVictimImage(LL)
                                # left color detected
                                elif LC and not util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim]:
                                    util.maze[util.floor][util.tile][util.dirToLeft(util.direction) + util.nVictim] = ord(LC)
                                    IO.sendData(config.inputMode, LC)
                                    if config.saveVictimDebug:
                                        BFS.saveVictimImage(LC)
                                # right letter detected
                                if RL and not util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim]:
                                    util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim] = ord(RL)
                                    IO.sendData(config.inputMode, RL)
                                    if config.saveVictimDebug:
                                        BFS.saveVictimImage(RL)
                                # right color detected
                                elif RC and not util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim]:
                                    util.maze[util.floor][util.tile][util.dirToRight(util.direction) + util.nVictim] = ord(RC)
                                    IO.sendData(config.inputMode, RC)
                                    if config.saveVictimDebug:
                                        BFS.saveVictimImage(RC)

                                if IO.ser.in_waiting:
                                    victimMsg = IO.getNextSerialByte()

                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break
                                    # reached middle of tile, change tile
                                    if victimMsg == 'm':
                                        if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                                            util.direction = util.turnRight(util.direction, False)
                                        else:
                                            util.direction = util.turnLeft(util.direction, False)
                                        if config.runMode:
                                            display.updateLabels(cDir=util.direction)
                                        if config.importantDebug or config.victimDebug or config.BFSDebug or config.serialDebug:
                                            print("\t\t\t\tNOW FACING:" + str(util.direction))
                                        didTurn = True
                                    # heat victim
                                    if victimMsg in ('x', 'X'):
                                        if config.importantDebug or config.victimDebug or config.serialDebug:
                                            print("\t\t\t\tHEAT VICTIM RECEIVED ON " + "LEFT" if victimMsg == 'x' else "RIGHT")
                                        heatDirection = util.dirToLeft(util.direction) if victimMsg == 'x' else util.dirToRight(util.direction)
                                        if not util.maze[util.floor][util.tile][util.nVictim + heatDirection]:
                                            IO.sendSerial('y')
                                            util.maze[util.floor][util.tile][util.nVictim + heatDirection] = ord(victimMsg)
                                        else:
                                            IO.sendSerial('n')

                                victimMsg = None

                            # if no 'm' was sent, manually update
                            if not didTurn:
                                if util.tile + util.adjTiles[util.dirToRight(util.direction)] == nextTileInPath:
                                    util.direction = util.turnRight(util.direction, False)
                                else:
                                    util.direction = util.turnLeft(util.direction, False)
                                if config.runMode:
                                    display.updateLabels(cDir=util.direction)

                            if config.serialDebug:
                                print("\t\t\tCAMERA OVER, GOT: " + str(victimMsg))

                    # update length after sending turn
                    util.pathLen += 2

                if loadingCheckpoint:
                    break

                nextTileIsRampStart = util.tileExists(util.goForward(util.tile, False)) and util.maze[util.floor][util.goForward(util.tile, False)][util.tileType] in (3, 4)

                # go up ramp if needed
                if util.floor != nextFloorInPath:
                    if config.inputMode == 2:
                        util.tile = util.goForward(util.tile, not nextTileIsRampStart)
                    util.maze, util.tile, util.floor = util.goOnRamp(util.maze, util.tile, util.floor, nextFloorInPath > util.floor)
                    if config.runMode:
                        display.updateLabels(cTile=util.tile, cFloor=util.floor)

                    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
                    util.pathLen += 2

                    if config.inputMode == 2:
                        victimMsg = IO.getNextSerialByte()
                        if victimMsg == 'a':
                            loadingCheckpoint = True
                            break
                        print("RAMP OVER GOT:" + str(victimMsg))
                else:
                    if config.inputMode == 1:
                        if config.runMode:
                            display.updateLabels(cTile=util.tile, cFloor=util.floor)
                        util.tile = util.goForward(util.tile, not nextTileIsRampStart)
                    else:
                        # load next IO message
                        util.goForward(util.tile, not nextTileIsRampStart)

                # update checkpoint
                if util.isCheckpoint(util.maze[util.floor], util.tile):
                    checkpoint = BFS.saveCheckpoint()

                # send next IO message
                if not nextTileIsRampStart:
                    IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 2])
                    if config.serialDebug:
                        print("\t\tSENDINGM: " + IO.sData[util.pathLen:util.pathLen + 2])

                    # find and send victims
                    if config.inputMode == 2:
                        if config.doVictim:
                            victimMsg = None
                            wentForward = False

                            # loop until movement forward completed
                            while victimMsg != ';':
                                LL, LLP, LC, LCP, RL, RLP, RC, RCP = BFS.searchForVictims()

                                # add victims and their positions
                                victimList = []
                                if LL:
                                    victimList.append((LL, LLP))
                                elif LC:
                                    victimList.append((LC, LCP))
                                if RL:
                                    victimList.append((LL, LLP))
                                elif RC:
                                    victimList.append((RC, RCP))

                                if config.importantDebug or config.victimDebug:
                                    print("\t\t\t\t\tVICTIM LIST: " + str(victimList))

                                # victim responses
                                for v in victimList:
                                    # send victim
                                    if config.importantDebug or config.victimDebug or config.serialDebug:
                                        print("\t\t\t\t\t\t\tSENDING: " + v[0])
                                    IO.sendSerial(v[0])

                                    # get cm from the wall for determining the tile of the victim
                                    victimMsg = IO.getNextSerialByte()
                                    if victimMsg == '_':
                                        continue
                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break
                                    cmFromWall = int(victimMsg) * 10
                                    victimMsg = IO.getNextSerialByte()
                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break
                                    cmFromWall += int(victimMsg)

                                    # get cm moved for determining the tile of the victim
                                    victimMsg = IO.getNextSerialByte()
                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break
                                    cmMoved = int(victimMsg) * 10
                                    victimMsg = IO.getNextSerialByte()
                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break
                                    cmMoved += int(victimMsg)

                                    if config.importantDebug or config.BFSDebug or config.victimDebug or config.serialDebug:
                                        print("cm from wall: " + str(cmFromWall) + "cmMoved: " + str(cmMoved))

                                    # validate if the victim should be sent
                                    if util.victimInPreviousTile(cmFromWall, v[1], cmMoved) != wentForward and \
                                            not util.maze[util.floor][util.tile][(util.dirToLeft(util.direction) if v[0].islower() else util.dirToRight(util.direction)) + util.nVictim]:
                                        util.maze[util.floor][util.tile][(util.dirToLeft(util.direction) if v[0].islower() else util.dirToRight(util.direction)) + util.nVictim] = ord(v[0])
                                        if config.saveVictimDebug:
                                            BFS.saveVictimImage(v[0])
                                        IO.sendSerial('y')
                                    else:
                                        IO.sendSerial('n')

                                if IO.ser.in_waiting:
                                    victimMsg = IO.getNextSerialByte()
                                    if victimMsg == 'a':
                                        loadingCheckpoint = True
                                        break

                                    # halfway through movement, update tile
                                    if victimMsg == 'm':
                                        util.tile = util.goForward(util.tile, False)
                                        if config.runMode:
                                            display.updateLabels(cTile=util.tile, cFloor=util.floor)
                                        if config.importantDebug or config.victimDebug or config.BFSDebug or config.serialDebug:
                                            print("\t\t\t\tNOW IN NEXT TILE:" + str(util.tile))
                                        wentForward = True

                                    # heat victim
                                    if victimMsg in ('x', 'X'):
                                        if config.importantDebug or config.victimDebug or config.serialDebug:
                                            print("\t\t\t\tHEAT VICTIM RECEIVED ON " + "LEFT" if victimMsg == 'x' else "RIGHT")
                                        heatDirection = util.dirToLeft(util.direction) if victimMsg == 'x' else util.dirToRight(util.direction)
                                        if not util.maze[util.floor][util.tile][util.nVictim + heatDirection]:
                                            IO.sendSerial('y')
                                            util.maze[util.floor][util.tile][util.nVictim + heatDirection] = ord(victimMsg)
                                        else:
                                            IO.sendSerial('n')

                                    # stair protocol
                                    if victimMsg == 's':
                                        # get number of horizontal tiles stairs covered
                                        stairTiles = int(IO.getNextSerialByte())
                                        if stairTiles < 2:
                                            continue

                                        if config.importantDebug or config.serialDebug or config.BFSDebug:
                                            print("\t\t\t\tGOT STAIRS, GOING FORWARD: " + str(stairTiles))
                                        if wentForward:
                                            util.tile = util.goBackward(util.tile)
                                        wentForward = False

                                        # loop through tiles skipped in stairs
                                        for i in range(stairTiles):
                                            util.tile = util.goForward(util.tile, False)

                                            # create walls on side of stairs
                                            util.maze[util.floor][util.tile][util.dirToLeft(util.direction)] = True
                                            if util.tileExists(util.tile + util.adjTiles[util.dirToLeft(util.direction)]):
                                                util.maze[util.floor][util.tile + util.adjTiles[util.dirToLeft(util.direction)]][util.oppositeDir(util.dirToLeft(util.direction))] = True
                                            util.maze[util.floor][util.tile][util.dirToRight(util.direction)] = True
                                            if util.tileExists(util.tile + util.adjTiles[util.dirToRight(util.direction)]):
                                                util.maze[util.floor][util.tile + util.adjTiles[util.dirToRight(util.direction)]][util.oppositeDir(util.dirToRight(util.direction))] = True

                                            # update image
                                            display.img = display.createWallsForTile(display.img, util.floor, util.maze[util.floor], util.tile)
                                            if config.runMode:
                                                display.updateLabels(cTile=util.tile, cFloor=util.floor)
                                            if config.importantDebug or config.serialDebug or config.BFSDebug:
                                                print("\t\t\t\t\tNOW IN NEXT TILE:" + str(util.tile))

                                victimMsg = None

                            # manually update tile if no 'm' received
                            if not wentForward:
                                util.tile = util.goForward(util.tile, False)
                                if config.runMode:
                                    display.updateLabels(cTile=util.tile, cFloor=util.floor)

                            if config.serialDebug:
                                print("\t\t\tCAMERA OVER, GOT: " + str(victimMsg))
                    # update path length after forward/ramp movement
                    util.pathLen += 2

                if config.showDisplay and config.runMode:
                    display.showMaze(display.img, util.maze, nextFloor, util.floor, nextTile, config.displayRate)

            # send BFS ending char '}'
            if not loadingCheckpoint:
                IO.sData += config.serialOutMsgs[8]
                IO.sendData(config.inputMode, IO.sData[util.pathLen:util.pathLen + 1], True)
                if config.serialDebug:
                    print("\t\tSENDING: " + IO.sData[util.pathLen:util.pathLen + 1])
                util.pathLen += 1

                # reset path string
                util.pathLen = len(IO.sData)

                # set tile new tile to visited, clear parent array
                util.maze[util.floor][util.tile][util.visited] = True
                util.parent.clear()

                # get sensor/wall values
                inputWalls = util.getWalls()

                # take care of special tiles and use wall values
                checkpoint = BFS.handleSpecialTiles(inputWalls, checkpoint)

            # load checkpoint
            if loadingCheckpoint or inputWalls is None:
                util.maze[util.floor][util.tile][util.visited] = False
                BFS.loadCheckpoint(checkpoint)
                loadingCheckpoint = False

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
        if config.importantDebug:
            print("\nTotal Path: " + str(IO.sData) + "\nBFS Done! All tiles visited in: " + format((time.time() - IO.startTime) * 1000, '.2f') + "ms ")
        if config.showDisplay:
            display.showMaze(display.img if config.showDisplay else display.resetImg(util.maze), util.maze, None, util.floor, None, 0)

# running code
if config.inputMode == 2:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(config.LEDPin, GPIO.OUT)
    BFS.setupCams()
while True:
    try:
        runThread = AThread()
        if config.runMode:
            runThread.finished.connect(display.app.exit)
            runThread.start()
            display.app.exec_()
        else:
            runThread.run()
    except Exception as e:
        if config.runMode:
            display.updateLabels(status=str(e))
        print("ERROR ENCOUNTERED: " + str(traceback.print_exc()))
        if config.inputMode == 2:
            GPIO.output(config.LEDPin, GPIO.HIGH)  # error, turn on LED
