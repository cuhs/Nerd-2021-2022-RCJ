import util
import numpy as np
import cv2
import random
import IO
import display
from util import config

# generates a maze based on a png of one from mazegenerator.net
def genMazeFromImage():
    # maze values holds the maze generated from picture
    maze = np.zeros((config.floorCount, config.mazeSideLen ** 2, util.tileLen), dtype=np.int8)
    img = cv2.imread(config.fpIMG + "maze" + str(config.mazeSideLen) + ".png", cv2.IMREAD_COLOR)

    # variable sizes, works with any even sided maze
    imgSize = img.shape[0] // config.mazeSideLen

    # loops through image and gets BGR values of pixels where walls are located
    for y in range(config.mazeSideLen):
        for x in range(config.mazeSideLen):
            xPixel = x * imgSize + imgSize // 2
            yPixel = y * imgSize + imgSize // 2

            maze[util.startFloor][x + (config.mazeSideLen * y)][0] = (1 if (img.item(yPixel - 8, xPixel, 0) < 100) or (y is 0) else 0)
            maze[util.startFloor][x + (config.mazeSideLen * y)][1] = (1 if (img.item(yPixel, xPixel + 8, 0) < 100) else 0)
            maze[util.startFloor][x + (config.mazeSideLen * y)][2] = (1 if (img.item(yPixel + 8, xPixel, 0) < 100) or (y is config.mazeSideLen - 1) else 0)
            maze[util.startFloor][x + (config.mazeSideLen * y)][3] = (1 if (img.item(yPixel, xPixel - 8, 0) < 100) else 0)

    for i in range(config.mazeSideLen ** 2):
        maze[util.startFloor][i][util.visited] = True

    # displays check for correct
    if config.showDisplay:
        cv2.imshow('original', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        display.show(display.img, maze, None, None, 0)

    # writes maze values to "generatedMaze.txt"
    IO.writeMaze(IO.inputFile("a"), "IMAGE", maze[util.startFloor], True)

    if config.importantDebug:
        print("Maze write finished!")

# generate maze from random walls
def genRandMaze():
    maze = np.zeros((config.floorCount, config.mazeSideLen ** 2, 10), dtype=np.int8)

    for i in range(config.floorCount):
        # create maze borders/edges
        for j in range(config.mazeSideLen):
            maze[i][j][0] = True
        for j in range(config.mazeSideLen - 1, config.mazeSideLen ** 2, config.mazeSideLen):
            maze[i][j][1] = True
        for j in range(0, config.mazeSideLen ** 2, config.mazeSideLen):
            maze[i][j][3] = True
        for j in range(((config.mazeSideLen ** 2) - config.mazeSideLen), config.mazeSideLen ** 2):
            maze[i][j][2] = True
    
        # generate random walls
        for j in range((config.mazeSideLen ** 2) * 4):
            if random.randint(0, int(100 / (config.wallPercentage / 2))) == 0:
                # create wall
                maze[i][j // 4][j % 4] = True

                # create wall on opposite side
                if util.tileExists(j // 4 + util.adjTiles[j % 4]):
                    maze[i][j // 4 + util.adjTiles[j % 4]][util.oppositeDir(j % 4)] = True
    
        # generate black tiles
        for j in range(int(((config.mazeSideLen ** 2)/100) * config.blackTilePercentage)):
            r = random.randint(0, config.mazeSideLen ** 2 - 1)
    
            # making sure not overwriting another black tile or starting tile
            while maze[i][r][util.tileType] > 0 or r == util.startTile:
                r = random.randint(0, config.mazeSideLen ** 2 - 1)
    
            maze[i] = util.setBlackTile(maze[i], r, setBorders=False)
    
        # generate silver tiles
        for j in range(int(((config.mazeSideLen ** 2)/100) * config.silverTilePercentage)):
            r = random.randint(0, config.mazeSideLen ** 2 - 1)
    
            # making sure not overwriting another black tile or starting tile
            while maze[i][r][util.tileType] > 0 or r == util.startTile:
                r = random.randint(0, config.mazeSideLen ** 2 - 1)
    
            maze[i] = util.setCheckpoint(maze[i], r)

    # create ramps
    rampMappings = {}
    for i in range(config.floorCount - 1):
        # create direction of ramp
        rampDir = random.randint(0, 3)

        # find tile for bottom ramp tile
        bottomRampTile = random.randint(0, config.mazeSideLen ** 2 - 1)
        while maze[i][bottomRampTile][util.tileType] > 0 \
                or (bottomRampTile == util.startTile and i == util.startFloor) \
                or not util.tileExists(bottomRampTile + util.adjTiles[rampDir]) \
                or maze[i][bottomRampTile + util.adjTiles[rampDir]][util.tileType] in (1, 3, 4) \
                or rampDir == 1 and (bottomRampTile + 1) % config.mazeSideLen == 0 \
                or rampDir == 3 and bottomRampTile % config.mazeSideLen == 0:
            bottomRampTile = random.randint(0, config.mazeSideLen ** 2 - 1)

        # find tile for corresponding top ramp tile
        topRampTile = random.randint(0, config.mazeSideLen ** 2 - 1)
        while maze[i + 1][topRampTile][util.tileType] > 0 \
                or (topRampTile == util.startTile and (i + 1) == util.startFloor) \
                or not util.tileExists(topRampTile + util.adjTiles[util.oppositeDir(rampDir)]) \
                or maze[i + 1][topRampTile + util.adjTiles[util.oppositeDir(rampDir)]][util.tileType] in (1, 3, 4) \
                or util.oppositeDir(rampDir) == 1 and (topRampTile + 1) % config.mazeSideLen == 0 \
                or util.oppositeDir(rampDir) == 3 and topRampTile % config.mazeSideLen == 0:
            topRampTile = random.randint(0, config.mazeSideLen ** 2 - 1)

        # create ramps at tiles generated above
        maze = util.setRampBorders(maze, bottomRampTile, i, rampDir, True, topRampTile)
        rampMappings[bottomRampTile, i] = topRampTile, i + 1
        rampMappings[topRampTile, i + 1] = bottomRampTile, i

    # writes maze values to "generatedMaze.txt"
    IO.writeMaze(IO.inputFile("a"), "GENERATED", maze[0], True)
    for i in range(1, config.floorCount):
        IO.writeMaze(IO.inputFile("a"), None, maze[i], False)
    IO.inputFile("a").write(str(rampMappings))

    if config.showDisplay:
        display.show(display.resetImg(maze), maze, None, None, 0)
        cv2.destroyAllWindows()

    if config.importantDebug:
        print("Maze write finished!")
