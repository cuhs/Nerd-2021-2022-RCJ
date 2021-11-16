import util
import numpy as np
import cv2
import display
from util import config

# generates a maze based on a png of one from mazegenerator.net
def generateMaze():
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
