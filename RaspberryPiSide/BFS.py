import util
import sys
from util import np
from util import config

def init():
    util.maze = np.zeros((util.mazeSize * util.mazeSize, 5), dtype=np.int8)  # maze[tile][state], read util
    util.tile = int(((util.mazeSize * util.mazeSize) / 2) + (util.mazeSize / 2))  # creates start tile in the middle of size x size area
    util.direction = util.Dir.N.value  # starting direction is set to north

    # queue (just a list) and parent array for BFS
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
        print("\tBFS - Tile: " + str(cTile) + " is visited: " + str(util.maze[util.tile][util.visited]))
    # recursive loop until returned
    if util.maze[cTile][util.visited] == 0:
        util.q.clear()
        if config.debug is True:
            print("\tBFS - END, Tile:\t" + str(cTile))
        return cTile

    # stores how many tiles are unvisited
    possibleTiles = [0, 0, 0, 0]

    # check if wall at true north
    if util.maze[cTile][util.Dir.N.value] == 0:
        # no walls north
        if util.parent[util.northTile(cTile)] == -1:
            util.parent[util.northTile(cTile)] = cTile
            util.q.append(util.northTile(cTile))
        possibleTiles[0] = 1

    # check if wall at true east
    if util.maze[cTile][util.Dir.E.value] == 0:
        # no walls east
        if util.parent[util.eastTile(cTile)] == -1:
            util.parent[util.eastTile(cTile)] = cTile
            util.q.append(util.eastTile(cTile))
        possibleTiles[1] = 1

    # check if wall at true south
    if util.maze[cTile][util.Dir.S.value] == 0:
        # no walls south
        if util.parent[util.southTile(cTile)] == -1:
            util.parent[util.southTile(cTile)] = cTile
            util.q.append(util.southTile(cTile))
        possibleTiles[2] = 1

    # check if wall at true west
    if util.maze[cTile][util.Dir.W.value] == 0:
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
        if facing == util.Dir.W.value:
            facing = util.rightTurn(facing)
        else:
            while facing != util.Dir.N.value:
                facing = util.leftTurn(facing)
    # target == east of tile
    if target == util.eastTile(util.tile):
        if facing == util.Dir.N.value:
            facing = util.rightTurn(facing)
        else:
            while facing != util.Dir.E.value:
                facing = util.leftTurn(facing)
    # target == south of tile
    if target == util.southTile(util.tile):
        if facing == util.Dir.E.value:
            facing = util.rightTurn(facing)
        else:
            while facing != util.Dir.S.value:
                facing = util.leftTurn(facing)
    # target == west of tile
    if target == util.westTile(util.tile):
        if facing == util.Dir.S.value:
            facing = util.rightTurn(facing)
        else:
            while facing != util.Dir.W.value:
                facing = util.leftTurn(facing)
    return facing
