import time

import util
import cv2
import sys
import numpy as np
import config
if config.runMode:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolButton

# general display stuff
imageSize = config.mazeSideLen * config.displaySize
lineWidth = (1 if config.mazeSideLen > 50 else 2) + config.runMode
fontSize = 50
img = []

# QT display stuff
app = None
win = None
button = None
GUIThread = None
QtMazeImg = None
statusLabel = None
cPosLabel = None
tPosLabel = None
victimLabel = None
serialSendLabel = None
serialReceiveLabel = None

# setup QT stuff
if config.runMode:
    app = QApplication(sys.argv)

    win = QMainWindow()
    win.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    win.setGeometry(0, 0, *config.monitorDimensions)
    win.setStyleSheet("background-color: black;")

    # start/stop button
    button = QToolButton(win)
    button.setCheckable(True)
    button.setGeometry(10, 10, 100, 100)
    button.clicked.connect(lambda: sys.exit(0))
    button.setText("ST\nOP")
    button.setFont(QtGui.QFont("Monaco", fontSize//2))
    button.setStyleSheet("background-color: red;")

    # setup maze image
    QtMazeImg = QLabel(win)
    QtMazeImg.setGeometry(config.monitorDimensions[0] - config.monitorDimensions[1], 0, config.monitorDimensions[1], config.monitorDimensions[1])

    # setup all labels
    statusLabel = QLabel(win)
    statusLabel.setText("inWaiting")
    statusLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    statusLabel.setGeometry(button.x() + button.width() + 30, button.y() + 5, 250, 100)
    statusLabel.setStyleSheet("color: yellow;")
    cPosLabel = QLabel(win)
    cPosLabel.setText("C: None, None, N")
    cPosLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    cPosLabel.setGeometry(button.x(), button.y() + button.height() + 20, 400, 50)
    cPosLabel.setStyleSheet("color: white;")
    tPosLabel = QLabel(win)
    tPosLabel.setText("T: None, None")
    tPosLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    tPosLabel.setGeometry(button.x() + 10, cPosLabel.y() + 70, 400, 50)
    tPosLabel.setStyleSheet("color: white;")
    victimLabel = QLabel(win)
    victimLabel.setText("V: None, None")
    victimLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    victimLabel.setGeometry(button.x() + 5, tPosLabel.y() + 70, 400, 50)
    victimLabel.setStyleSheet("color: white;")
    serialSendLabel = QLabel(win)
    serialSendLabel.setText("S: None")
    serialSendLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    serialSendLabel.setGeometry(button.x() + 5, victimLabel.y() + 70, 400, 50)
    serialSendLabel.setStyleSheet("color: white;")
    serialReceiveLabel = QLabel(win)
    serialReceiveLabel.setText("R: None")
    serialReceiveLabel.setFont(QtGui.QFont("Rockwell", fontSize//1.5))
    serialReceiveLabel.setGeometry(button.x() + 5, serialSendLabel.y() + 70, 400, 50)
    serialReceiveLabel.setStyleSheet("color: white;")

    # show labels
    statusLabel.show()
    cPosLabel.show()
    tPosLabel.show()
    victimLabel.show()
    serialSendLabel.show()
    serialReceiveLabel.show()
    QtMazeImg.show()
    button.show()
    win.show()

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

    if util.path is not None:
        for i in range(len(util.path)):
            if util.path[i][1] == cFloor:
                xPixel = (util.path[i][0] % config.mazeSideLen) * config.displaySize
                yPixel = (util.path[i][0] // config.mazeSideLen) * config.displaySize
                cv2.rectangle(newImg, (xPixel + lineWidth, yPixel + lineWidth),
                              (xPixel + config.displaySize - lineWidth, yPixel + config.displaySize - lineWidth),
                              (0, 230, 255), -1)

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

def CVtoQT(pImg):
    RGB = cv2.cvtColor(pImg, cv2.COLOR_BGR2RGB)
    height, width = RGB.shape[:2]
    QtFormat = QtGui.QImage(RGB.data, width, height, width * 3, QtGui.QImage.Format_RGB888)
    QtScaled = QtFormat.scaled(config.monitorDimensions[1], config.monitorDimensions[1], QtCore.Qt.KeepAspectRatio)
    return QPixmap.fromImage(QtScaled)

def showMaze(pImg, cMaze, tFloor, cFloor, target, ms):
    # add walls for newly visited tiles
    createWallsForTile(pImg, util.floor, util.maze[util.floor], util.tile)

    # create maze images with special tiles
    newImg = []
    for i in range(config.floorCount):
        newImg.append(addSpecialTiles(pImg, i, cMaze[i], target, tFloor))

    # display each floor
    if not config.runMode:
        for i in range(config.floorCount):
            cv2.imshow("Floor " + str(i), newImg[i])
    if not config.runMode:
        cv2.waitKey(ms)
    else:
        QtMazeImg.setPixmap(CVtoQT(newImg[cFloor if cFloor else 0]))

def updateLabels(status=None, cFloor=None, cTile=None, cDir=None, tFloor=None, tTile=None, LVictim=None, RVictim=None, sendData=None, receiveData=None):
    if status is not None:
        statusLabel.setText(str(status))
    if cFloor is not None:
        cPosLabel.setText("C: " + str(cFloor) + ", " + str(cPosLabel.text()[cPosLabel.text().find(",") + 2:]))
    if cTile is not None:
        cPosLabel.setText(cPosLabel.text()[:cPosLabel.text().find(",") + 2] + str(cTile) + ", " + cPosLabel.text()[cPosLabel.text().find(",", cPosLabel.text().find(",") + 1) + 2:])
    if cDir is not None:
        cPosLabel.setText(cPosLabel.text()[:cPosLabel.text().find(",", cPosLabel.text().find(",") + 1)] + ", " + str('N' if cDir == 0 else 'E' if cDir == 1 else 'S' if cDir == 2 else 'W'))
    if tFloor is not None:
        tPosLabel.setText("T: " + str(tFloor) + ", " + str(tPosLabel.text()[tPosLabel.text().find(",") + 1:]))
    if tTile is not None:
        tPosLabel.setText(tPosLabel.text()[:tPosLabel.text().find(",")] + ", " + str(tTile))
    if LVictim is not None:
        victimLabel.setText("V: " + str(LVictim) + ", " + str(victimLabel.text()[victimLabel.text().find(",") + 2:]))
    if RVictim is not None:
        victimLabel.setText(victimLabel.text()[:victimLabel.text().find(",")] + ", " + str(RVictim))
    if sendData is not None:
        if len(serialSendLabel.text()) > 10:
            serialSendLabel.setText("")
        serialSendLabel.setText(serialSendLabel.text() + str(sendData))
    if receiveData is not None:
        if receiveData == 'm':
            serialReceiveLabel.setText("")
        serialReceiveLabel.setText(serialReceiveLabel.text() + str(sendData))
