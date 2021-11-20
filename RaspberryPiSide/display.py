import util
import cv2
import numpy as np
from util import config

imageSize = config.mazeSideLen * config.displaySize
img = np.zeros((imageSize, imageSize, 3), dtype=np.uint8)

def imgSetup():
    # create blank white image
    img[:] = (255, 255, 255)

# displays a passed maze with cv2
def displayMaze(target, gMaze):
    # parses maze by column
    for x in range(config.mazeSideLen):
        for y in range(config.mazeSideLen):
            tile = (x + (config.mazeSideLen * y))
            xPixel = x * config.displaySize
            yPixel = y * config.displaySize

            # adds current tile as green
            if tile == util.tile:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 255, 0), -1)
            # adds path tiles as yellow
            if util.path is not None:
                if tile in util.path:
                    cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 230, 255), -1)
            # adds target tile as red
            if tile == target:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 255), -1)
            # black tiles are black
            # if util.isBlackTile(tile):
            #    cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), -1)

            # adds walls for the tile
            if gMaze[tile][util.Dir.N.value] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel), (0, 0, 0), 2)
            if gMaze[tile][util.Dir.E.value] == 1:
                cv2.line(img, (xPixel + config.displaySize, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), 2)
            if gMaze[tile][util.Dir.S.value] == 1:
                cv2.line(img, (xPixel, yPixel + config.displaySize), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), 2)
            if gMaze[tile][util.Dir.W.value] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel, yPixel + config.displaySize), (0, 0, 0), 2)

def show(target, gMaze, ms):
    imgSetup()
    displayMaze(target, gMaze)
    cv2.imshow("maze", img)
    cv2.waitKey(ms)
