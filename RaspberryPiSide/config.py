# options file, as some settings might want to be
# changed while debugging or on different systems/computers

mazeSideLen = 20  # must be even
inputMode = 1  # 0 -> manual, 1 -> input or gen from file, 2 -> serial
recursionLimit = (mazeSideLen * mazeSideLen) + 10  # buffer of 10

tilePercentage = 20  # in percentage
tilePercentage = int(100/tilePercentage)

if inputMode == 1:
    genFromImage = False  # if false, will get random

displayMode = 1  # 0 no display, 1 is display
displayRate = 10  # in milliseconds, 0 for until click
displaySize = 750  # display size, range from (0 - 1000), see line below
displaySize = int(displaySize/mazeSideLen)  # adjust for equal image size

port = "/dev/ttyS0"  # serial port

debug = False  # print statements

# fp -> file path
fpALL = "../RaspberryPiSide/"
fpKNN = fpALL + "KNN/"
fpTXT = fpALL + "IO/"
fpIMG = fpALL + "IO/"
