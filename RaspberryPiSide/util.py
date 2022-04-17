import numpy as np
import IO
import config
from enum import Enum

# two different types of directions
# True North is the starting direction, and all other directions are the "true" equivalent
# "North" means the bot's north, or where the bot is facing. All other directions are relative to the bot

# NESW -> 0123 True North is starting direction
class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3

# neighboring tiles as: N E S W, to get neighbor do: Tile + adjTiles[0] for tile north of Tile
adjTiles = [-config.mazeSideLen, 1, config.mazeSideLen, -1]

# tile states are true NESW for getting walls, and vis for checking if visited
# maze[tile][5] -> return visited. 0 = not visited, 1 = visited.
visited = 4

# tile states for victims (ascii code of char victim)
# maze[tile][6] -> what victim on north wall of tile. "H" "S" "U", "R" "Y" "G" or None
nVictim = 5
eVictim = 6
sVictim = 7
wVictim = 8

# tile type, normal, black, or checkpoint
# maze[tile][9] -> special tile features: 0 = normal, 1 = black, 2 = checkpoint
tileType = 9

# length of attributes for each tile, for maze & array creation
tileLen = 10

maze = None
layer = None
tile = None
direction = None
q = None
parent = None
path = None
pathLen = None

# home/starting tile
startTile = int(((config.mazeSideLen ** 2) / 2) + (config.mazeSideLen / 2))

# hsv ranges for color victims
hsv_lower = {
    0: (150, 230, 100),
    1: (50, 40, 100),
    2: (5, 95, 100)
}

hsv_upper = {
     0: (179, 255, 240),
     1: (90, 105, 240),
     2: (50, 175, 240)
}

# adjust which position is facing true north
# getting sensorData[N] will get north,
# this adjusts it to true north, and all other directions
def adjustDirections(facing):
    adjustedDirections = np.array([], dtype=np.int8)
    for i in range(4):
        adjustedDirections = np.append(adjustedDirections, facing)
        facing = dirToRight(facing)
    return adjustedDirections

# returns directions after and before passed direction in N -> E -> S -> W order
def dirToLeft(d):
    return d - 1 if d != 0 else 3
def dirToRight(d):
    return d + 1 if d != 3 else 0
def oppositeDir(d):
    return dirToRight(dirToRight(d))

# returns whether tile exists / is in maze
def tileExists(cTile):
    return 0 <= cTile < config.mazeSideLen ** 2

# direction must be adjusted from bot to the maze
def setWalls():
    sensorData = IO.getData(config.inputMode, tile)

    if config.inputMode != 2:
        for i in range(tileLen):
            # prevents overwriting of black tile
            if maze[tile][i] == 0:
                maze[tile][i] = sensorData[i]
    else:
        # black tile
        if sensorData is None:
            return None
        if (type(sensorData) is not np.ndarray) and sensorData == 'a':
            return False

        # adjust directions for bot alignment
        for i in range(4):
            maze[tile][adjustDirections(direction)[i]] = sensorData[i]
        maze[tile][5] = 1
        for i in range(5, 10):
            maze[tile][i] = 0

    if config.BFSDebug:
        print("\tTile Array for tile " + str(tile) + ": " + str(maze[tile]))
    return True

# both are 90 degree turns
def turnLeft(facing):
    facing = dirToLeft(facing)
    IO.sData += (config.serialMessages[1] + config.serialMessages[4])
    return facing

def turnRight(facing):
    facing = dirToRight(facing)
    IO.sData += (config.serialMessages[2] + config.serialMessages[4])
    return facing

# send forward message
def goForward(cTile):
    IO.sData += (config.serialMessages[0] + config.serialMessages[4])
    return cTile + adjTiles[direction]

def goBackward(cTile):
    # msg = config.serialMessages[3] + config.serialMessages[4]
    # packet.sData += msg
    return cTile + adjTiles[oppositeDir(direction)]

def setBlackTile(cMaze, cTile, setBorders=True):
    # set the borders of the black tile
    if setBorders:
        for i in range(4):
            cMaze[cTile][i] = 1
        for i in range(4):
            if tileExists(cTile + adjTiles[i]) and not (i == 1 and (cTile + 1) % config.mazeSideLen == 0) and not (i == 3 and cTile % config.mazeSideLen == 0):
                cMaze[cTile + adjTiles[i]][adjustDirections(Dir.S.value)[i]] = 1
    # mark the tile as black
    cMaze[cTile][tileType] = 1
    return cMaze

def isBlackTile(cMaze, cTile):
    return cMaze[cTile][tileType] == 1

def setCheckpoint(cMaze, cTile):
    cMaze[cTile][tileType] = 2
    return cMaze

def isCheckpoint(cMaze, cTile):
    return cMaze[cTile][tileType] == 2
