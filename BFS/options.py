# options file, as some settings might want to be
# changed while debugging or on different systems/computers

mazeSideLen = 50  # must be even
inputMode = 1  # 0 -> manual, 1 -> input or gen from file, 2 -> serial
recursionLimit = (mazeSideLen * mazeSideLen) + 10  # buffer of 10

displayMode = 1  # 0 no display, 1 is display
displayRate = 500  # in milliseconds, 0 for until click
displaySize = 15  # in pixels, displaySize * mazeSideLen < your screen height

port = "/dev/ttyS0"  # serial port

debug = False  # print statements

# fp -> file path
fpALL = "../BFS/"
fpKNN = fpALL + "KNN/"
fpTXT = fpALL + "IO/"
fpIMG = fpALL + "IO/"
