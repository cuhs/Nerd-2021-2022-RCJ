import cv2
import numpy as np
import KNN
import time
import letterDetection


#CONFIG----------------------------------------
  
numberOfCams = 1 #number of camera to run
cap = [None,None] #left, right
victimDetect = True #true --> tests victim detection, false --> runs camera feed
showFrames = True #true to see actual camera frames
fullDetect = True #true to see mask, bounding box, will increase processing time by much (recommend to turn off victimDetect)
oneCamEverythingDetect = False #Will show everything as letterDetection class sees, to use shut down victimDetect, full Detect, and showFrames, set cams to 1
saveVictim = False
width = 160 #camera width
height = 128 #camera height
cameraCutL = [0, 128, 0, 150]  # left slicing to ignore treads, height then width
cameraCutR = [0, 123, 0, 152]  # right slicing to ignore treads, height then width
checkFPS = False #true to check frames per second
showCenter = False #true to show center of the victim, only works if victimDetect is true
pathVI = "/home/pi/Documents/Nerd-2021-2022/Nerd-2021-2022-RCJ/RaspberryPiSide/IOFiles/victimImages"
path = pathVI + "/Fri Jul  1 10:34:42 2022/u-Fri Jul  1 10:36:29 2022.png" #set to None if not testing an image
path = None
threshParam = [19,4] #23,3

#CONFIG_END------------------------------------


def initCams():
    if (numberOfCams == 1 or numberOfCams == 2) and path is None:
        cap[0] = cv2.VideoCapture(0)
        cap[0].set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap[0].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if numberOfCams == 2 and path is None:
        cap[1] = cv2.VideoCapture(1)
        cap[1].set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap[1].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        
         
vD = letterDetection.Detection()

initCams()

while (path is not None) or (numberOfCams == 1 and cap[0].isOpened()) or (numberOfCams == 2 and cap[1].isOpened()):
    
    if (numberOfCams == 1 or numberOfCams == 2) and path is None:
        retL, frameL = cap[0].read()
        frameL = frameL[cameraCutL[0]:cameraCutL[1],cameraCutL[2]:cameraCutL[3]]
    if numberOfCams == 2 and path is None:
        retR, frameR = cap[1].read()
        frameR = frameR[cameraCutR[0]:cameraCutR[1],cameraCutR[2]:cameraCutR[3]]
    if path is not None:
        frame = cv2.imread(path)
        dim = frame.shape
    
    if checkFPS:
        startTime = time.time()
        
    if victimDetect:
        if (numberOfCams == 1 or numberOfCams == 2) and path is None:
            letterL, letterCL, colorL, colorCL = vD.leftDetectFinal(retL, frameL)
            if letterL is not None:
                print("Left Camera: Letter is " + str(letterL) + " at x-position " + str(np.int0(letterCL)))
                if showCenter:
                    cv2.line(frameL,(np.int0(letterCL),cameraCutL[0]),(np.int0(letterCL),cameraCutL[1]), 3)
            else:
                print("Left Camera: No letter detected")
            if colorL is not None:
                print("Left Camera: Color is " + str(colorL) + " at x-position " + str(np.int0(colorCL)))
                if showCenter:
                    cv2.line(frameL,(np.int0(colorCL),cameraCutL[0]),(np.int0(colorCL),cameraCutL[1]), 3)
            else:
                print("Left Camera: No color detected")
                
        if numberOfCams == 2 and path is None:
            letterR, letterCR, colorR, colorCR = vD.leftDetectFinal(retR, frameR)
            if letterR is not None:
                print("Right Camera: Letter is " + str(letterR) + " at x-position " + str(np.int0(letterCR)))
                if showCenter:
                    cv2.line(frameR,(np.int0(letterCR),cameraCutR[0]),(np.int0(letterCR),cameraCutR[1]), 3)
            else:
                print("Right Camera: No letter detected")
            if colorR is not None:
                print("Right Camera: Color is " + str(colorR) + " at x-position " + str(np.int0(colorCR)))
                if showCenter:
                    cv2.line(frameR,(np.int0(colorCR),cameraCutR[0]),(np.int0(colorCR),cameraCutR[1]), 3)
            else:
                print("Right Camera: No color detected")
                
        if path is not None:
            letter, letterC, color, colorC = vD.leftDetectFinal(1,frame)
            if letter is not None:
                print("Path: Letter is " + str(letter) + " at x-position " + str(np.int0(letterC)))
                if showCenter:
                    cv2.line(frame,(np.int0(letterC),0),(np.int0(letterC),dim[0]), 3)
            else:
                print("Path: No letter detected")
            if color is not None:
                print("Path: Color is " + str(color) + " at x-position " + str(np.int0(colorC)))
                if showCenter:
                    cv2.line(frameR,(np.int0(colorC),0),(np.int0(colorC),dim[0]), 3)
            else:
                print("Path: No color detected")

    if fullDetect:
        if (numberOfCams == 1 or numberOfCams == 2) and path is None:
            grayL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
            blurL = cv2.bilateralFilter(grayL, 5, 75, 75)
            threshL = cv2.adaptiveThreshold(blurL,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,threshParam[0],threshParam[1])
            imgOutputL, cL = vD.letterDetect(frameL) 
            
        if numberOfCams == 2 and path is None:
            grayR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)
            blurR = cv2.bilateralFilter(grayR, 5, 75, 75)
            threshR = cv2.adaptiveThreshold(blurR,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,threshParam[0],threshParam[1])
            imgOutputR, cR = vD.letterDetect(frameR)
            
        if path is not None:
            #REMINDER: MAKING CHANGES HERE WILL NOT EFFECT VICTIM DETECTION/KNN
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.bilateralFilter(gray, 5, 75, 75)
            thresh = cv2.adaptiveThreshold(blur,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,threshParam[0],threshParam[1])
            imgOutput, c = vD.letterDetect(frame)
    
    
    #Will show everything as letterDetection class sees, to use shut down victimDetect, full Detect, and showFrames, set cams to 1
    if oneCamEverythingDetect and not victimDetect and not fullDetect and not showFrames and numberOfCams == 1:
        vD.setDebugMode(True)
        vD.letterDetect(frameL)
        
    else:
        vD.setDebugMode(False)
        

    if showFrames:
        if (numberOfCams == 1 or numberOfCams == 2) and path is None:
            if retL > 0:
                cv2.imshow("frameL", frameL)
        if numberOfCams == 2 and path is None:
            if retR > 0:
                cv2.imshow("frameR", frameR)
        if path is not None:
            cv2.imshow("pathImage",frame)
        if fullDetect:
            if (numberOfCams == 1 or numberOfCams == 2) and path is None:
                cv2.imshow("threshL", threshL*255)
                if imgOutputL is not None:
                    cv2.imshow("imgOutputL", imgOutputL*255)
            if numberOfCams == 2 and path is None:
                cv2.imshow("threshR", threshR*255)
                if imgOutputR is not None:
                    cv2.imshow("imgOutputR", imgOutputR*255)
            if path is not None:
                cv2.imshow("thresh", thresh*255)
                if imgOutput is not None:
                    cv2.imshow("imgOutput", imgOutput*255)
    
                            
    '''if result1 is not None:
        print("victim")
        cv2.imshow("thvictim", thresh2)
        cv2.imshow("victim", frame1)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()'''

                
        
    if saveVictim and numberOfCams == 1:
        if cv2.waitKey(1) == ord(' '):
            print("Do you like this image?")
            cv2.imshow("image_mask",imgOutputL*255)
            letter = cv2.waitKey(0)
            cv2.destroyAllWindows()
            if letter == ord('y'):
                cv2.imwrite("/home/pi/Documents/Nerd-2021-2022/Nerd-2021-2022-RCJ/RaspberryPiSide/IOFiles/saveVictims/" + str(time.time()) + ".png",frameL)
                print("saved!")
            else:
                print("not saved")
        

    if checkFPS:
        print("Time taken: " + str((time.time()-startTime)))

            
    if cv2.waitKey(1)  == ord('q'):
        break

if numberOfCams == 1 or numberOfCams == 2:
    cap[0].release()
if numberOfCams == 2:
    cap[1].release()
cv2.destroyAllWindows()