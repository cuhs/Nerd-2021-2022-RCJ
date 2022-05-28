# config file for settings that may differ when debugging, on different systems, etc.

mazeSideLen = 10  # must be even
floorCount = 3  # starts at middle floor
inputMode = 1  # 0 -> manual, 1 -> input or gen from file, 2 -> serial
recursionLimit = (mazeSideLen ** 2) * floorCount  # buffer added on setup
runMode = True  # enables QT interface for running

wallPercentage = 25  # percentage of tiles that should be walls for random generation of maze
blackTilePercentage = 5  # percent of black tiles when randomly generating a maze
silverTilePercentage = 2  # percent of silver tiles when randomly generating a maze
genFromImage = False  # if false, will generate random maze
redoLastMaze = False  # allows you to rerun last generated maze, for debugging

showDisplay = True  # 0 no display, 1 is display
displayRate = 1  # in milliseconds, 0 for until keypress
displaySize = 500  # display size, range from (0 - 1000), see line below
displaySize = displaySize // mazeSideLen  # adjust for equal image size
monitorDimensions = (1024, 600)  # (x, y, width, height)

importantDebug = False  # important print statements, overrides other settings
BFSDebug = False  # print statements for maze traversal
victimDebug = False  # shows camera feeds
saveVictimDebug = False  # saves victim images if found
serialDebug = False  # prints serial IO

port = "/dev/ttyS0"  # serial port path (serial: /dev/ttyAMA0)
rate = 9600  # serial port rate
LEDPin = 18  # GPIO pin for LED

doVictim = True  # check for color and letter victims
cameraCount = 2  # number of cameras, cam0 is left, cam1 is right. if only one camera, left
cameraWidth = 160  # width of camera feed for both cameras 160
cameraHeight = 128  # height of camera feed for both cameras 128

manualCheckpointLoading = False  # load back to last checkpoint when 'c' is pressed

# list of serial messages sent by the Pi to the robot:
# F -> forward, L -> left, R -> right, B -> back, W -> up ramp, M -> down ramp
# ; -> end of single instruction, { -> start of instruction list, } -> end of instruction list
serialOutMsgs = ["F", "L", "R", "B", "W", "M", ";", "{", "}"]

# fp -> file path
fpALL = "../RaspberryPiSide/"
fpKNN = fpALL + "KNN/"
fpTXT = fpALL + "IOFiles/"
fpIMG = fpALL + "IOFiles/"
fpVIC = fpALL + "IOFiles/victimImages/"

test = 50
