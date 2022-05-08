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

# tile states for victims (UNICODE of char victim)
# maze[tile][6] -> what victim on north wall of tile. "H" "S" "U", "R" "Y" "G" or 0
nVictim = 5
eVictim = 6
sVictim = 7
wVictim = 8

# tile type, normal, black, or checkpoint
# maze[tile][9] -> special tile features: 0 = normal, 1 = black, 2 = checkpoint, 3 = up-ramp, 4 = down-ramp
tileType = 9

# length of attributes for each tile, for maze & array creation
tileLen = 10

maze = None
tile = None
floor = None
direction = None
parent = None
path = None
pathLen = None
rampMap = None

# home/starting tile and floor
startTile = int(((config.mazeSideLen ** 2) / 2) + (config.mazeSideLen / 2))
startFloor = (config.floorCount - 1) // 2

# hsv ranges for color victims
hsv_lower = {
    0: (87, 115, 60),
    1: (40, 30, 50),
    2: (0, 55, 85)
}

hsv_upper = {
     0: (180, 255, 170),
     1: (100, 150, 155),
     2: (36, 160, 185)
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
def getWalls():
    sensorData = IO.getData(config.inputMode, tile, floor)
    retData = np.zeros(tileLen, dtype=np.int8)

    # reset to checkpoint
    if (type(sensorData) is not np.ndarray) and sensorData == 'a':
        return None

    # set walls
    if config.inputMode != 2:
        for i in range(tileLen):
            retData[i] = sensorData[i]
        retData[visited] = 1
    else:
        # adjust directions for bot alignment
        for i in range(4):
            retData[adjustDirections(direction)[i]] = sensorData[i]
        for i in range(5, 10):
            retData[i] = 0
        retData[util.visited] = 1


    if config.BFSDebug:
        print("\tTile Array for tile " + str(tile) + ": " + str(retData))

    return retData

# both are 90 degree turns
def turnLeft(facing):
    facing = dirToLeft(facing)
    IO.sData += (config.serialMessages[1] + config.serialMessages[6])
    return facing

def turnRight(facing):
    facing = dirToRight(facing)
    IO.sData += (config.serialMessages[2] + config.serialMessages[6])
    return facing

# send forward message
def goForward(cTile, sendMsg):
    if sendMsg:
        IO.sData += (config.serialMessages[0] + config.serialMessages[6])
    return cTile + adjTiles[direction]

def goBackward(cTile):
    return cTile + adjTiles[oppositeDir(direction)]

def setBlackTile(cFloor, cTile, setBorders=True):
    # set the borders of the black tile
    if setBorders:
        for i in range(4):
            cFloor[cTile][i] = 1
        for i in range(4):
            if tileExists(cTile + adjTiles[i]) and not (i == 1 and (cTile + 1) % config.mazeSideLen == 0) and not (i == 3 and cTile % config.mazeSideLen == 0):
                cFloor[cTile + adjTiles[i]][oppositeDir(i)] = 1
    # mark the tile as black
    cFloor[cTile][tileType] = 1
    return cFloor

def isBlackTile(cMaze, cTile):
    return cMaze[cTile][tileType] == 1

def setCheckpoint(cMaze, cTile):
    cMaze[cTile][tileType] = 2
    return cMaze

def isCheckpoint(cMaze, cTile):
    return cMaze[cTile][tileType] == 2

def setRampBorders(cMaze, cTile, cFloor, cDirection, upRamp, rTile):
    if upRamp and cFloor == config.floorCount - 1 or not upRamp and cFloor == 0:
        raise ValueError("Invalid Ramp Creation (May Need To Increase config.floorCount)!")

    rampAdjust = 1 if upRamp else -1
    cMaze[cFloor][cTile][tileType] = 3 if upRamp else 4
    cMaze[cFloor + rampAdjust][rTile][tileType] = 4 if upRamp else 3

    # set the borders of the ramp tile
    for i in range(4):
        if i == cDirection:
            cMaze[cFloor][cTile][i] = 0
        else:
            cMaze[cFloor][cTile][i] = 1

    # set the borders of tiles bordering the ramp tile
    for i in range(4):
        if tileExists(cTile + adjTiles[i]) and not (i == 1 and (cTile + 1) % config.mazeSideLen == 0) and not (i == 3 and cTile % config.mazeSideLen == 0):
            if i == cDirection:
                cMaze[cFloor][cTile + adjTiles[i]][oppositeDir(i)] = 0
            else:
                cMaze[cFloor][cTile + adjTiles[i]][oppositeDir(i)] = 1

    # set the borders of the top/bottom ramp tile
    for i in range(4):
        if i == oppositeDir(cDirection):
            cMaze[cFloor + rampAdjust][rTile][i] = 0
        else:
            cMaze[cFloor + rampAdjust][rTile][i] = 1

    # set the borders of tiles bordering the ramp tile
    for i in range(4):
        if tileExists(rTile + adjTiles[i]) and not (i == 1 and (rTile + 1) % config.mazeSideLen == 0) and not (i == 3 and rTile % config.mazeSideLen == 0):
            if i == oppositeDir(cDirection):
                cMaze[cFloor + rampAdjust][rTile + adjTiles[i]][oppositeDir(i)] = 0
            else:
                cMaze[cFloor + rampAdjust][rTile + adjTiles[i]][oppositeDir(i)] = 1

    return cMaze

def setRamp(cMaze, cTile, cFloor, upRamp):
    cMaze[cFloor][cTile][tileType] = 3 if upRamp else 4
    return cMaze

def isUpRamp(cMaze, cTile):
    return cMaze[cTile][tileType] == 3

def isDownRamp(cMaze, cTile):
    return cMaze[cTile][tileType] == 4

def goOnRamp(cMaze, cTile, cFloor, upRamp, sendMsg=True):
    if sendMsg:
        IO.sData += (config.serialMessages[4] if upRamp else config.serialMessages[5]) + config.serialMessages[6]
        if path:
            path.pop()

    # set ramp tile on new floor visited, update tile
    cTile, cFloor = rampMap[cTile, cFloor]
    cMaze[cFloor][cTile][visited] = True

    # go to tile in front of ramp
    cTile += adjTiles[direction]
    cMaze[cFloor][cTile][visited] = True
    if config.importantDebug:
        print("\t\t\tCurrent Position: " + str(cTile) + ", " + str(cFloor))
    return cMaze, cTile, cFloor
