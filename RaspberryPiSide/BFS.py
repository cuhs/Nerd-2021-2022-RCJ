import util
import sys
from util import np
from util import config

def init():
    util.maze = np.zeros((util.mazeSize * util.mazeSize, 5), dtype=np.int8)  # maze[tile][state], read util
    util.tile = int(((util.mazeSize * util.mazeSize) / 2) + (util.mazeSize / 2))  # creates start tile in the middle of size x size area
    util.direction = util.N  # starting direction is set to north

    # queue (just a list) and parent array for RaspberryPiSide
    util.q = []
    util.parent = np.zeros(util.mazeSize * util.mazeSize, dtype=np.int16)
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
        print("\tRaspberryPiSide - Tile: " + str(cTile) + " is visited: " + str(util.maze[util.tile][util.visited]))
    # recursive loop until returned
    if util.maze[cTile][util.visited] == 0:
        util.q.clear()
        if config.debug is True:
            print("\tRaspberryPiSide - END, Tile:\t" + str(cTile))
        return cTile

    # stores how many tiles are unvisited
    possibleTiles = [0, 0, 0, 0]

    # check if wall at true north
    if util.maze[cTile][util.N] == 0:
        # no walls north
        if util.parent[util.northTile(cTile)] == -1:
            util.parent[util.northTile(cTile)] = cTile
            util.q.append(util.northTile(cTile))
        possibleTiles[0] = 1

    # check if wall at true east
    if util.maze[cTile][util.E] == 0:
        # no walls east
        if util.parent[util.eastTile(cTile)] == -1:
            util.parent[util.eastTile(cTile)] = cTile
            util.q.append(util.eastTile(cTile))
        possibleTiles[1] = 1

    # check if wall at true south
    if util.maze[cTile][util.S] == 0:
        # no walls south
        if util.parent[util.southTile(cTile)] == -1:
            util.parent[util.southTile(cTile)] = cTile
            util.q.append(util.southTile(cTile))
        possibleTiles[2] = 1

    # check if wall at true west
    if util.maze[cTile][util.W] == 0:
        # no walls west
        if util.parent[util.westTile(cTile)] == -1:
            util.parent[util.westTile(cTile)] = cTile
            util.q.append(util.westTile(cTile))
        possibleTiles[3] = 1

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
    # target == north of tile
    if target == util.northTile(util.tile):
        if facing == util.W:
            facing = util.rightTurn(facing)
        else:
            while facing != util.N:
                facing = util.leftTurn(facing)
    # target == east of tile
    if target == util.eastTile(util.tile):
        if facing == util.N:
            facing = util.rightTurn(facing)
        else:
            while facing != util.E:
                facing = util.leftTurn(facing)
    # target == south of tile
    if target == util.southTile(util.tile):
        if facing == util.E:
            facing = util.rightTurn(facing)
        else:
            while facing != util.S:
                facing = util.leftTurn(facing)
    # target == west of tile
    if target == util.westTile(util.tile):
        if facing == util.S:
            facing = util.rightTurn(facing)
        else:
            while facing != util.W:
                facing = util.leftTurn(facing)
    return facing
