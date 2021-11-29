# options file, as some settings might want to be
# changed while debugging or on different systems/computers

mazeSideLen = 30  # must be even
inputMode = 1  # 0 -> manual, 1 -> input or gen from file, 2 -> serial
recursionLimit = (mazeSideLen ** 2) + 10  # buffer of 10

wallPercentage = 15  # percentage of tiles that should be walls for random generation of maze
blackTilePercentage = 5  # percent of black tiles when randomly generating a maze
genFromImage = False  # if false, will generate random maze
redoLastMaze = False  # this setting allows you to rerun the last maze, maybe if a bug or problem occurred in it

showDisplay = True  # 0 no display, 1 is display
displayRate = 10  # in milliseconds, 0 for until click
displaySize = 750  # display size, range from (0 - 1000), see line below
displaySize = displaySize // mazeSideLen  # adjust for equal image size

debug = False  # print statements

port = "/dev/ttyS0"  # serial port path
rate = 9600  # serial port rate

# serial messages in order for:
# forward, left, right, back, EOI, (end of single instruction), EOD (end of directions), SOD (start of dir.)
# example: if ["a", "b", "c", "d", ".", "$", "%"], directions for forward, left, left, forward would be:
# %a.b.b.a.$ and will be sent individually as "%", "a.", "b." etc.      ALL MESSAGES MUST BE ONE CHAR
serialMessages = ["F", "L", "R", "B", ";", "{", "}"]

# fp -> file path
fpALL = "../RaspberryPiSide/"
fpKNN = fpALL + "KNN/"
fpTXT = fpALL + "IOFiles/"
fpIMG = fpALL + "IOFiles/"
