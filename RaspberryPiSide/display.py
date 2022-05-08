import util
import cv2
import numpy as np
from util import config

imageSize = config.mazeSideLen * config.displaySize
img = np.zeros((imageSize, imageSize, 3), dtype=np.uint8)
lineWidth = 1 if config.mazeSideLen > 50 else 2

def imgSetup():
    # create blank white image
    img[:] = (255, 255, 255)

# creates an image from maze
def createMazeImage(cFloor, current, target, path, floor):
    # parses maze by column
    for x in range(config.mazeSideLen):
        for y in range(config.mazeSideLen):
            tile = (x + (config.mazeSideLen * y))
            xPixel = x * config.displaySize
            yPixel = y * config.displaySize

            # silver tiles are grey
            if util.isCheckpoint(cFloor, tile):
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (175, 175, 175), -1)

            # adds current tile as green
            if tile == current:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 255, 0), -1)
            # adds path tiles as yellow
            if path is not None:
                if (tile, floor) in path:
                    cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 230, 255), -1)
            # adds target tile as red
            if tile == target:
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 255), -1)
            # black tiles are black
            if util.isBlackTile(cFloor, tile):
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), -1)
            # up ramp tiles are dark blue
            if util.isUpRamp(cFloor, tile):
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (255, 100, 0), -1)
            # down ramp tiles are light blue
            if util.isDownRamp(cFloor, tile):
                cv2.rectangle(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (255, 200, 0), -1)

            # small grey center for seeing grey tiles when overwritten
            if util.isCheckpoint(cFloor, tile):
                cv2.rectangle(img, (xPixel + config.displaySize//4, yPixel + config.displaySize // 4), (xPixel + (config.displaySize//4)*3, yPixel + (config.displaySize//4)*3), (175, 175, 175), -1)

            # adds the walls for the tile
            if cFloor[tile][util.Dir.N.value] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel + config.displaySize, yPixel), (0, 0, 0), lineWidth)
            if cFloor[tile][util.Dir.E.value] == 1:
                cv2.line(img, (xPixel + config.displaySize, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
            if cFloor[tile][util.Dir.S.value] == 1:
                cv2.line(img, (xPixel, yPixel + config.displaySize), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
            if cFloor[tile][util.Dir.W.value] == 1:
                cv2.line(img, (xPixel, yPixel), (xPixel, yPixel + config.displaySize), (0, 0, 0), lineWidth)

def show(target, tFloor, cMaze, ms):
    cFloor = 0
    while cFloor <= config.floorCount and cFloor < len(cMaze):
        imgSetup()
        createMazeImage(cMaze[cFloor], util.tile if util.floor == cFloor else None, target if tFloor == cFloor else None, util.path, cFloor)
        cv2.imshow("Floor " + str(cFloor), img)
        cFloor += 1
    cv2.waitKey(ms)
