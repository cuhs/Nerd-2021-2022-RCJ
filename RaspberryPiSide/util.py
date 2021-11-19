import numpy as np
import packet
import config
from enum import Enum

# two different types of directions
# True North is the starting direction, and all other directions are the "true" equivalent
# "North" means the bot's north, or where the bot is facing. All other directions are relative to the bot

# maze size = 20 -> maze size = 20x20 tiles, must be even   !integrate
mazeSize = config.mazeSideLen

# NESW -> 0123 True North is starting direction
class Dir(Enum):
    N = 0
    E = 1
    S = 2
    W = 3

nTiles = [mazeSize, 1, -1 * mazeSize, -1] # neighboring tiles

# tile states are true NESW for getting walls, and vis for checking if visited
visited = 4

# threshold for walls. If below this number, there is a wall      !integrate
# sensorData is a filler for sensor data storage                  !integrate
sensorData = np.zeros(5)

maze = None
tile = None
direction = None
q = None
parent = None
path = None
pathLen = None

# adjust which position is facing true north
# getting sensorData[N] will get north,
# this adjusts it to true north, and all other directions
def adjustDirections(facing):
    adjustedDirections = np.array([], dtype=np.int8)
    for i in range(0, 4):
        if facing == 4:
            facing = 0
        adjustedDirections = np.append(adjustedDirections, facing)
        facing += 1
    return adjustedDirections

# detects walls if sensor value is below a certain threshold
# direction must be adjusted from bot to the maze
def setWalls():
    sensorData[:] = packet.getData(config.inputMode, tile, direction)
    if sensorData[4] != -1:
        adjustedDirections = adjustDirections(direction)
    else:
        adjustedDirections = adjustDirections(Dir.N.value)
    for i in range(0, 4):
        if sensorData[i] == 1:
            maze[tile][adjustedDirections[i]] = 1
    if config.debug is True:
        print("\tTile Array: " + str(maze[tile]))

# both are 90 degree turns
def leftTurn(facing):
    if facing == Dir.N.value:
        facing = Dir.W.value
    else:
        facing -= 1
    packet.sData += "mL90;"
    if config.inputMode == 2:
        packet.ser.write(bytes("mL90;".encode("ascii", "ignore")))
    return facing

def rightTurn(facing):
    if facing == Dir.W.value:
        facing = Dir.N.value
    else:
        facing += 1
    packet.sData += "mR90;"
    if config.inputMode == 2:
        packet.ser.write(bytes("mR90;".encode("ascii", "ignore")))
    return facing

# send forward message
def forwardTile(cTile):
    if config.inputMode == 2:
        packet.ser.write(bytes("mFT1;".encode("ascii", "ignore")))
    packet.sData += "mFT1;"
    return cTile + nTiles[direction]

def setBlackTile(cTile):
    for x in range(0, 5):
        maze[cTile][x] = 1
    for x in range(0, 4):
        maze[cTile][adjustDirections(Dir.S.value)[x]] = 1

def isBlackTile(cTile):
    return maze[cTile][0:4].all() == 1
