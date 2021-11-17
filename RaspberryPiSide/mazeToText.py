import util
import numpy as np
import cv2
import random
import display
from util import config

# generates a maze based on a png of one from mazegenerator.net
def genMazeFromImage():
    # maze values holds the maze generated from picture
    mazeValues = np.zeros((util.mazeSize * util.mazeSize, 5), dtype=np.int8)
    img = cv2.imread(config.fpIMG + "maze" + str(util.mazeSize) + ".png", cv2.IMREAD_COLOR)

    # variable sizes, works with any even sided maze
    gMazeSize = util.mazeSize
    imgSize = int(img.shape[0]/gMazeSize)

    # loops through image and gets BGR values of pixels where walls are located
    for y in range(gMazeSize):
        for x in range(gMazeSize):
            xPixel = x * imgSize + int(imgSize/2)
            yPixel = y * imgSize + int(imgSize/2)

            mazeValues[x + (gMazeSize * y)][0] = (1 if (img.item(yPixel - 8, xPixel, 0) < 100) or (y is 0) else 0)
            mazeValues[x + (gMazeSize * y)][1] = (1 if (img.item(yPixel, xPixel + 8, 0) < 100) else 0)
            mazeValues[x + (gMazeSize * y)][2] = (1 if (img.item(yPixel + 8, xPixel, 0) < 100) or (y is gMazeSize - 1) else 0)
            mazeValues[x + (gMazeSize * y)][3] = (1 if (img.item(yPixel, xPixel - 8, 0) < 100) else 0)

    # displays check for correct
    if config.displayMode != 0:
        cv2.imshow('original', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        display.show(-1, mazeValues, 0)

    # writes maze values to "mazeInput.txt"
    r = open(config.fpTXT + "mazeInput", "a", encoding='utf-8')
    r.truncate(0)
    r.write("GENERATED\n")
    for x in range(util.mazeSize * util.mazeSize):
        r.write(str(int(mazeValues[x][0])) + str(int(mazeValues[x][1])) + str(int(mazeValues[x][2])) + str(int(mazeValues[x][3])) + "\n")

    print("Maze write finished!")

def generateMaze(mazeType, length):
    maze = np.zeros((length * length, 5), dtype=np.int8)

    for i in range(0, length):
        maze[i][0] = 1
    for i in range(length - 1, length * length, length):
        maze[i][1] = 1
    for i in range(0, length * length, length):
        maze[i][3] = 1
    for i in range(((length * length) - length), length * length):
        maze[i][2] = 1

    if mazeType[:4] == "open":
        for i in range(0, length * length):
            if random.randint(0, config.tilePercentage - 1) == 0:
                maze[i][0] = 1
                if i - length >= 0:
                    maze[i - length][2] = 1
            if random.randint(0, config.tilePercentage - 1) == 0:
                maze[i][1] = 1
                if i + 1 < length * length:
                    maze[i + 1][3] = 1
            if random.randint(0, config.tilePercentage - 1) == 0:
                maze[i][2] = 1
                if i + length < length * length:
                    maze[i + length][0] = 1
            if random.randint(0, config.tilePercentage - 1) == 0:
                maze[i][3] = 1
                if i - 1 >= 0:
                    maze[i - 1][1] = 1



    if config.displayMode != 0:
        display.show(-1, maze, 0)
        cv2.destroyAllWindows()

    # writes maze values to "mazeInput.txt"
    r = open(config.fpTXT + "mazeInput", "a", encoding='utf-8')
    r.truncate(0)
    r.write("GENERATED\n")
    for x in range(length * length):
        r.write(str(int(maze[x][0])) + str(int(maze[x][1])) + str(int(maze[x][2])) + str(int(maze[x][3])) + "\n")
