import util
import sys
from util import np
from util import config

def init():
    if config.mazeSideLen % 2 != 0 or not(2 <= config.mazeSideLen <= 80):
        raise ValueError("Invalid Maze Size (check config!)")
    util.maze = np.zeros((config.mazeSideLen ** 2, 5), dtype=np.int8)  # maze[tile][state], read util
    util.tile = int(((config.mazeSideLen ** 2) / 2) + (config.mazeSideLen / 2))  # creates start tile in the middle of size x size area
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

# return next tile to visit recursively
def nextTile(cTile):
    if config.debug is True:
        print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[util.tile][util.visited]))
    # recursive loop until returned
    if util.maze[cTile][util.visited] == 0:
        util.q.clear()
        if config.debug is True:
            print("\tBFS - END, Tile:\t" + str(cTile))
        return cTile

    # stores how many tiles are unvisited
    possibleTiles = [0, 0, 0, 0]

    for i in range(4):
        if util.maze[cTile][i] == 0:
            # no wall in direction i
            if util.parent[util.nTiles[i] + cTile] == -1:
                util.parent[util.nTiles[i] + cTile] = cTile
                util.q.append(util.nTiles[i] + cTile)
            possibleTiles[i] = 1

    if config.debug is True:
        print("\tQueue:\t" + str(util.q))

    # recursively finds unvisited tiles
    for x in range(len(possibleTiles)):
        if possibleTiles[x] == 1:
            if not util.q:
                return None
            return nextTile(util.q.pop(0))

# puts path to tile in a stack
def pathToTile(cTile, target):
    util.path.clear()
    x = target
    while x != cTile:
        util.path.append(int(x))
        x = util.parent[int(x)]

# changes direction being faced
def turnToTile(target, facing):
    for i in range(4):
        if target == util.nTiles[i] + util.tile:
            if facing == util.dirBefore(i):
                facing = util.rightTurn(facing)
            else:
                while facing != i:
                    facing = util.leftTurn(facing)
    return facing
