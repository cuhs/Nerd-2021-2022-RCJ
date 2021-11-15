import numpy as np
import packet
import options

# two different types of directions
# True North is the starting direction, and all other directions are the "true" equivalent
# "North" means the bot's north, or where the bot is facing. All other directions are relative to the bot

# maze size = 20 -> maze size = 20x20 tiles, must be even   !integrate
mazeSize = options.mazeSideLen

# NESW -> 0123 True North is starting direction
N = 0
E = 1
S = 2
W = 3

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
    adjustedDirections = np.zeros(4, dtype=np.int8)
    if facing is N:
        adjustedDirections = [N, E, S, W]
    if facing is E:
        adjustedDirections = [E, S, W, N]
    if facing is S:
        adjustedDirections = [S, W, N, E]
    if facing is W:
        adjustedDirections = [W, N, E, S]
    return adjustedDirections

# detects walls if sensor value is below a certain threshold
# direction must be adjusted from bot to the maze
def setWalls():
    sensorData[:] = packet.getData(options.inputMode, tile, direction)
    if sensorData[4] != -1:
        adjustedDirections = adjustDirections(direction)
    else:
        adjustedDirections = adjustDirections(N)
    if sensorData[N] == 1:
        maze[tile][adjustedDirections[N]] = 1
    if sensorData[E] == 1:
        maze[tile][adjustedDirections[E]] = 1
    if sensorData[S] == 1:
        maze[tile][adjustedDirections[S]] = 1
    if sensorData[W] == 1:
        maze[tile][adjustedDirections[W]] = 1
    if options.debug is True:
        print("\tTile Array: " + str(maze[tile]))

# returns tiles to true direction of given tile
def northTile(cTile):
    return cTile - mazeSize

def eastTile(cTile):
    return cTile + 1

def southTile(cTile):
    return cTile + mazeSize

def westTile(cTile):
    return cTile - 1

# both are 90 degree turns
def leftTurn(facing):
    if facing is N:
        facing = W
    else:
        facing -= 1
    packet.sData += "mL90;"
    if options.inputMode == 2:
        packet.ser.write(bytes("mL90;".encode("ascii", "ignore")))
    return facing

def rightTurn(facing):
    if facing is W:
        facing = N
    else:
        facing += 1
    packet.sData += "mR90;"
    if options.inputMode == 2:
        packet.ser.write(bytes("mR90;".encode("ascii", "ignore")))
    return facing

# send forward message
def forwardTile(cTile):
    if options.inputMode == 2:
        packet.ser.write(bytes("mFT1;".encode("ascii", "ignore")))
    packet.sData += "mFT1;"
    if direction is N:
        return northTile(cTile)
    if direction is E:
        return eastTile(cTile)
    if direction is S:
        return southTile(cTile)
    if direction is W:
        return westTile(cTile)

def setBlackTile(cTile):
    for x in range(5):
        maze[cTile][x] = 1
    maze[northTile(cTile)][S] = 1
    maze[eastTile(cTile)][W] = 1
    maze[southTile(cTile)][N] = 1
    maze[westTile(cTile)][E] = 1
