import numpy as np
import packet
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

# neighboring tiles as: N E S W, to get neighbor do: Tile + nTiles[0] for tile north of Tile
adjTiles = [-config.mazeSideLen, 1, config.mazeSideLen, -1]

# tile states are true NESW for getting walls, and vis for checking if visited
# maze[tile][5] -> return visited. 0 = not visited, 1 = visited.
visited = 4

# tile states for victims
# maze[tile][6] -> what victim on north wall of tile. "H" "S" "U" or NoneType
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
tile = None
direction = None
q = None
parent = None
path = None
pathLen = None

#  home/starting tile
startTile = int(((config.mazeSideLen ** 2) / 2) + (config.mazeSideLen / 2))

# adjust which position is facing true north
# getting sensorData[N] will get north,
# this adjusts it to true north, and all other directions
def adjustDirections(facing):
    adjustedDirections = np.array([], dtype=np.int8)
    for i in range(4):
        adjustedDirections = np.append(adjustedDirections, facing)
        facing = dirAfter(facing)
    return adjustedDirections

# returns directions after and before passed direction in N -> E -> S -> W order
def dirBefore(d):
    return d - 1 if d != 0 else 3
def dirAfter(d):
    return d + 1 if d != 3 else 0
def oppositeDir(d):
    return dirAfter(dirAfter(d))

# direction must be adjusted from bot to the maze
def setWalls():
    sensorData = packet.getData(config.inputMode, tile, direction)
    for i in range(tileLen):
        maze[tile][i] = sensorData[i]
        # prevents overwriting of black tile
        if (i < 4) and (0 <= tile + adjTiles[oppositeDir(i)] < config.mazeSideLen ** 2) and (maze[tile + adjTiles[oppositeDir(i)]][tileType] == 1):
            maze[tile][i] = 1

    if config.debug is True:
        print("\tTile Array: " + str(maze[tile]))

# both are 90 degree turns
def turnLeft(facing):
    facing = dirBefore(facing)
    packet.sData += "mL90;"
    if config.inputMode == 2:
        packet.ser.write(bytes("mL90;".encode("ascii", "ignore")))
    return facing

def turnRight(facing):
    facing = dirAfter(facing)
    packet.sData += "mR90;"
    if config.inputMode == 2:
        packet.ser.write(bytes("mR90;".encode("ascii", "ignore")))
    return facing

# send forward message
def goForward(cTile):
    if config.inputMode == 2:
        packet.ser.write(bytes("mFT1;".encode("ascii", "ignore")))
    packet.sData += "mFT1;"
    return cTile + adjTiles[direction]

def goBackward(cTile):
    if config.inputMode == 2:
        packet.ser.write(bytes("mBT1;".encode("ascii", "ignore")))
    packet.sData += "mBT1;"
    return cTile + adjTiles[oppositeDir(direction)]

def setBlackTile(cMaze, cTile, setBorders):
    if setBorders:
        for x in range(4):
            cMaze[cTile][x] = 1
        for x in range(4):
            if 0 <= cTile + adjTiles[x] < config.mazeSideLen ** 2:
                cMaze[cTile + adjTiles[x]][adjustDirections(Dir.S.value)[x]] = 1
    cMaze[cTile][tileType] = 1
    return cMaze

def isBlackTile(cMaze, cTile):
    return bool(cMaze[cTile][tileType])

def setCheckpoint(cMaze, cTile):
    cMaze[cTile][tileType] = 2
    return cMaze

def isCheckpoint(cMaze, cTile):
    return cMaze[cTile][tileType] == 2
