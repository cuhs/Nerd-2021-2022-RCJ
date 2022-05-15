import util
import cv2
import numpy as np
from util import config

imageSize = config.mazeSideLen * config.displaySize
lineWidth = 1 if config.mazeSideLen > 50 else 2
img = []

def setupImg():
    newImg = []
    # create blank white image
    for i in range(config.floorCount):
        newImg.append(np.zeros((imageSize, imageSize, 3), dtype=np.uint8))
        newImg[i][:] = (255, 255, 255)
    return newImg

def resetImg(cMaze):
    newImg = setupImg()
    for i in range(config.floorCount):
        newImg = createAllMazeWalls(newImg, i, cMaze[i])
    return newImg

def createWallsForTile(pImg, cFloor, theFloor, cTile):
    xPixel = (cTile % config.mazeSideLen) * config.displaySize
    yPixel = (cTile // config.mazeSideLen) * config.displaySize

    # adds the walls for the tile
    if theFloor[cTile][util.Dir.N.value] == 1:
        cv2.line(pImg[cFloor], (xPixel, yPixel), (xPixel + config.displaySize, yPixel), (0, 0, 0), lineWidth)
    if theFloor[cTile][util.Dir.E.value] == 1:
        cv2.line(pImg[cFloor], (xPixel + config.displaySize, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
    if theFloor[cTile][util.Dir.S.value] == 1:
        cv2.line(pImg[cFloor], (xPixel, yPixel + config.displaySize), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
    if theFloor[cTile][util.Dir.W.value] == 1:
        cv2.line(pImg[cFloor], (xPixel, yPixel), (xPixel, yPixel + config.displaySize), (0, 0, 0), lineWidth)
    return pImg

# creates an image from maze
def createAllMazeWalls(newImg, cFloor, theFloor):
    # parses maze by column
    for x in range(config.mazeSideLen):
        for y in range(config.mazeSideLen):
            tile = (x + (config.mazeSideLen * y))
            xPixel = x * config.displaySize
            yPixel = y * config.displaySize

            # adds the walls for the tile
            if theFloor[tile][util.Dir.N.value] == 1:
                cv2.line(newImg[cFloor], (xPixel, yPixel), (xPixel + config.displaySize, yPixel), (0, 0, 0), lineWidth)
            if theFloor[tile][util.Dir.E.value] == 1:
                cv2.line(newImg[cFloor], (xPixel + config.displaySize, yPixel), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
            if theFloor[tile][util.Dir.S.value] == 1:
                cv2.line(newImg[cFloor], (xPixel, yPixel + config.displaySize), (xPixel + config.displaySize, yPixel + config.displaySize), (0, 0, 0), lineWidth)
            if theFloor[tile][util.Dir.W.value] == 1:
                cv2.line(newImg[cFloor], (xPixel, yPixel), (xPixel, yPixel + config.displaySize), (0, 0, 0), lineWidth)
    return newImg

def addSpecialTiles(pImg, cFloor, theFloor, target, targetFloor):
    newImg = pImg[cFloor].copy()

    # parses maze by column
    for x in range(config.mazeSideLen):
        for y in range(config.mazeSideLen):
            tile = (x + (config.mazeSideLen * y))
            xPixel = x * config.displaySize
            yPixel = y * config.displaySize

            # silver tiles are grey
            if util.isCheckpoint(theFloor, tile):
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (175, 175, 175), -1)
            # adds current tile as green
            if tile == util.tile and cFloor == util.floor:
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (0, 255, 0), -1)
            # adds path tiles as yellow
            if util.path is not None:
                if (tile, cFloor) in util.path:
                    cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (0, 230, 255), -1)
            # adds target tile as red
            if tile == target and cFloor == targetFloor:
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (0, 0, 255), -1)
            # black tiles are black
            if util.isBlackTile(theFloor, tile):
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (0, 0, 0), -1)
            # up ramp tiles are dark blue
            if util.isUpRamp(theFloor, tile):
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (255, 100, 0), -1)
            # down ramp tiles are light blue
            if util.isDownRamp(theFloor, tile):
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth), (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth), (255, 200, 0), -1)

            # small grey center for seeing grey tiles when overwritten
            if util.isCheckpoint(theFloor, tile):
                cv2.rectangle(newImg, (xPixel + config.displaySize // 4, yPixel + config.displaySize // 4),
                              (xPixel + (config.displaySize // 4) * 3, yPixel + (config.displaySize // 4) * 3),
                              (175, 175, 175), -1)

            # letter stuff
            if theFloor[tile][util.nVictim]:
                cv2.putText(newImg, chr(theFloor[tile][util.nVictim]), ((xPixel + config.displaySize // 2) - (config.displaySize // 10), (yPixel + config.displaySize // 2) - config.displaySize // 4), cv2.FONT_HERSHEY_SIMPLEX, config.displaySize / 100, (0, 0, 0), lineWidth)
            if theFloor[tile][util.eVictim]:
                cv2.putText(newImg, chr(theFloor[tile][util.eVictim]), ((xPixel + config.displaySize // 2) + config.displaySize // 4, (yPixel + config.displaySize // 2)), cv2.FONT_HERSHEY_SIMPLEX, config.displaySize / 100, (0, 0, 0), lineWidth)
            if theFloor[tile][util.sVictim]:
                cv2.putText(newImg, chr(theFloor[tile][util.sVictim]), ((xPixel + config.displaySize // 2) - (config.displaySize // 10), (yPixel + config.displaySize // 2) + config.displaySize // 3), cv2.FONT_HERSHEY_SIMPLEX, config.displaySize / 100, (0, 0, 0), lineWidth)
            if theFloor[tile][util.wVictim]:
                cv2.putText(newImg, chr(theFloor[tile][util.wVictim]), ((xPixel + config.displaySize // 2) - int(config.displaySize / 2.3), (yPixel + config.displaySize // 2)), cv2.FONT_HERSHEY_SIMPLEX, config.displaySize / 100, (0, 0, 0), lineWidth)

    return newImg

def show(pImg, cMaze, tFloor, target, ms):
    createWallsForTile(pImg, util.floor, util.maze[util.floor], util.tile)

    for i in range(config.floorCount):
        newImg = addSpecialTiles(pImg, i, cMaze[i], target, tFloor)
        cv2.imshow("Floor " + str(i), newImg)

    cv2.waitKey(ms)
