import util
import numpy as np
import cv2
import random
import packet
import display
from util import config

# generates a maze based on a png of one from mazegenerator.net
def genMazeFromImage():
    # maze values holds the maze generated from picture
    mazeValues = np.zeros((config.mazeSideLen ** 2, 4), dtype=np.int8)
    img = cv2.imread(config.fpIMG + "maze" + str(config.mazeSideLen) + ".png", cv2.IMREAD_COLOR)

    # variable sizes, works with any even sided maze
    imgSize = img.shape[0] // config.mazeSideLen

    # loops through image and gets BGR values of pixels where walls are located
    for y in range(config.mazeSideLen):
        for x in range(config.mazeSideLen):
            xPixel = x * imgSize + imgSize // 2
            yPixel = y * imgSize + imgSize // 2

            mazeValues[x + (config.mazeSideLen * y)][0] = (1 if (img.item(yPixel - 8, xPixel, 0) < 100) or (y is 0) else 0)
            mazeValues[x + (config.mazeSideLen * y)][1] = (1 if (img.item(yPixel, xPixel + 8, 0) < 100) else 0)
            mazeValues[x + (config.mazeSideLen * y)][2] = (1 if (img.item(yPixel + 8, xPixel, 0) < 100) or (y is config.mazeSideLen - 1) else 0)
            mazeValues[x + (config.mazeSideLen * y)][3] = (1 if (img.item(yPixel, xPixel - 8, 0) < 100) else 0)

    # displays check for correct
    if config.showDisplay:
        cv2.imshow('original', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        display.show(-1, mazeValues, 0)

    # writes maze values to "mazeInput.txt"
    r = packet.inputFile("a")
    r.truncate(0)
    r.write("IMAGE\n")
    for i in range(config.mazeSideLen ** 2):
        r.write(str(''.join(str(j) for j in mazeValues[i])) + "100000\n")

    r.close()
    print("Maze write finished!")

# generate maze from random walls
def genRandMaze():
    maze = np.zeros((config.mazeSideLen ** 2, 10), dtype=np.int8)

    # create maze borders
    for i in range(config.mazeSideLen):
        maze[i][0] = 1
    for i in range(config.mazeSideLen - 1, config.mazeSideLen ** 2, config.mazeSideLen):
        maze[i][1] = 1
    for i in range(0, config.mazeSideLen ** 2, config.mazeSideLen):
        maze[i][3] = 1
    for i in range(((config.mazeSideLen ** 2) - config.mazeSideLen), config.mazeSideLen ** 2):
        maze[i][2] = 1

    # generate random walls
    for i in range((config.mazeSideLen ** 2) * 4):
        if random.randint(0, (100 // config.wallPercentage) - 1) == 0:
            maze[i // 4][i % 4] = 1
            if 0 <= i // 4 + util.adjTiles[i % 4] < config.mazeSideLen**2:
                maze[i // 4 + util.adjTiles[i % 4]][util.oppositeDir(i % 4)] = 1

    for i in range(config.blackTileCount):
        r = random.randint(0, config.mazeSideLen ** 2 - 1)

        # making sure not overwriting another black tile or starting tile
        while maze[r][util.tileType] == 1 or r == util.startTile:
            r = random.randint(0, config.mazeSideLen ** 2 - 1)

        maze = util.setBlackTile(maze, r, setBorders=False)

    for i in range(config.mazeSideLen ** 2):
        maze[i][util.visited] = 1

    if config.showDisplay:
        display.show(-1, maze, 0)
        cv2.destroyAllWindows()

    # writes maze values to "mazeInput.txt"
    r = packet.inputFile("a")
    r.truncate(0)
    r.write("GENERATED\n")
    for i in range(config.mazeSideLen ** 2):
        s = ""
        for j in range(util.tileLen):
            s += str(maze[i][j])
        r.write(str(s) + "\n")

    r.close()
    print("Maze write finished!")
