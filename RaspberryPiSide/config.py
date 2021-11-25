# options file, as some settings might want to be
# changed while debugging or on different systems/computers

mazeSideLen = 6  # must be even
inputMode = 1  # 0 -> manual, 1 -> input or gen from file, 2 -> serial
recursionLimit = (mazeSideLen ** 2) + 10  # buffer of 10

wallPercentage = 15  # percentage of tiles that should be walls for random generation of maze
blackTileCount = 0  # number of black tiles when randomly generating a maze     TODO: make count a variable ratio

genFromImage = False  # if false, will generate random maze

showDisplay = True  # 0 no display, 1 is display
displayRate = 10  # in milliseconds, 0 for until click
displaySize = 750  # display size, range from (0 - 1000), see line below
displaySize = displaySize // mazeSideLen  # adjust for equal image size

port = "/dev/ttyS0"  # serial port path
rate = 9600  # serial port rate

debug = True  # print statements

# fp -> file path
fpALL = "../RaspberryPiSide/"
fpKNN = fpALL + "KNN/"
fpTXT = fpALL + "IO/"
fpIMG = fpALL + "IO/"
