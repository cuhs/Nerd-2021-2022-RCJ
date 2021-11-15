import util
import cv2
import numpy as np
from util import options

vid = []
imageSize = util.mazeSize*(options.displaySize + 1)
img = np.zeros((imageSize, imageSize, 3), dtype=np.uint8)

def imgSetup():
    # create blank white image
    img[:] = (255, 255, 255)

# displays a passed maze with cv2
def displayMaze(target, gMaze):
    # parses maze by column
    for x in range(util.mazeSize):
        for y in range(util.mazeSize):
            tile = (x + (util.mazeSize * y))
            xPixel = x * options.displaySize
            yPixel = y * options.displaySize

            # adds current tile as green
            if tile == util.tile:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + options.displaySize, yPixel + options.displaySize), (0, 255, 0), -1)
            # adds path tiles as yellow
            if util.path is not None:
                if tile in util.path:
                    cv2.rectangle(img, (xPixel, yPixel), (xPixel + options.displaySize, yPixel + options.displaySize), (0, 230, 255), -1)
            # adds target tile as red
            if tile == target:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + options.displaySize, yPixel + options.displaySize), (0, 0, 255), -1)

            # adds walls for the tile
            if gMaze[tile][util.N] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel + options.displaySize, yPixel), (0, 0, 0), 2)
            if gMaze[tile][util.E] == 1:
                cv2.line(img, (xPixel + options.displaySize, yPixel), (xPixel + options.displaySize, yPixel + options.displaySize), (0, 0, 0), 2)
            if gMaze[tile][util.S] == 1:
                cv2.line(img, (xPixel, yPixel + options.displaySize), (xPixel + options.displaySize, yPixel + options.displaySize), (0, 0, 0), 2)
            if gMaze[tile][util.W] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel, yPixel + options.displaySize), (0, 0, 0), 2)

def show(target, gMaze, ms):
    imgSetup()
    displayMaze(target, gMaze)
    cv2.imshow("maze", img)
    cv2.waitKey(ms)
    cv2.destroyAllWindows()

