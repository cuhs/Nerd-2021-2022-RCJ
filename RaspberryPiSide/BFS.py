import util
import sys
import mazeToText
import IO
import display
import cv2
from util import np
from util import config

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
        IO.cap1 = cv2.VideoCapture(0)
        # IO.cap2 = cv2.VideoCapture(1)

        IO.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        IO.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
        # IO.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        # IO.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)


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

# changes direction being faced, favors left turns
def turnToTile(target, facing):
    for i in range(4):
        if target == util.adjTiles[i] + util.tile:
            if facing == util.dirToLeft(i):
                facing = util.turnRight(facing)
            else:
                while facing != i:
                    facing = util.turnLeft(facing)
    return facing
