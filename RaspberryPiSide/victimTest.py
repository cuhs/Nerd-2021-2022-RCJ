import cv2
import numpy as np
import KNN
import time
import letterDetection


#CONFIG----------------------------------------

numberOfCams = 2 #number of camera to run
cap = [None,None] #left, right
victimDetect = True #true --> tests victim detection, false --> runs camera feed
showFrames = True #true to see actual camera frames
width = 160 #camera width
height = 128 #camera height
cameraCutL = [0, 128, 0, 150]  # left slicing to ignore treads, height then width
cameraCutR = [0, 128, 0, 160]  # right slicing to ignore treads, height then width
checkFPS = False #true to check frames per second
showCenter = True #true to show center of the victim, only works if victimDetect is true


#CONFIG_END------------------------------------


def initCams():
    if numberOfCams == 1 or numberOfCams == 2:
        cap[0] = cv2.VideoCapture(0)
        cap[0].set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap[0].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if numberOfCams == 2:
        cap[1] = cv2.VideoCapture(1)
        cap[1].set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap[1].set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
         
vD = letterDetection.Detection()

initCams()

while (numberOfCams == 1 and cap[0].isOpened()) or (numberOfCams == 2 and cap[1].isOpened()):
    
    if numberOfCams == 1 or numberOfCams == 2:
        retL, frameL = cap[0].read()
        frameL = frameL[cameraCutL[0]:cameraCutL[1],cameraCutL[2]:cameraCutL[3]]
    if numberOfCams == 2:
        retR, frameR = cap[1].read()
        frameR = frameR[cameraCutR[0]:cameraCutR[1],cameraCutR[2]:cameraCutR[3]]
    
    if checkFPS:
        startTime = time.time()
        
    if victimDetect:
        if numberOfCams == 1 or numberOfCams == 2:
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
        if numberOfCams == 2:
            letterR, letterCR, colorR, colorCR = vD.leftDetectFinal(retR, frameR)
            if letterR is not None:
                print("Right Camera: Letter is " + str(letterR) + " at x-position " + str(np.int0(letterCR)))
                cv2.line(frameR,(np.int0(letterCR),cameraCutR[0]),(np.int0(letterCR),cameraCutR[1]), 3)
            else:
                print("Right Camera: No letter detected")
            if colorR is not None:
                print("Right Camera: Color is " + str(colorR) + " at x-position " + str(np.int0(colorCR)))
                cv2.line(frameR,(np.int0(colorCR),cameraCutR[0]),(np.int0(colorCR),cameraCutR[1]), 3)
            else:
                print("Right Camera: No color detected")

    if showFrames:
        if numberOfCams == 1 or numberOfCams == 2:
            if retL > 0:
                cv2.imshow("frameL", frameL)
        if numberOfCams == 2:
            if retR > 0:
                cv2.imshow("frameR", frameR)

    
    '''gray = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    
    blur = cv2.bilateralFilter(gray, 5, 75,75)

    thresh2  = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17,3) #21, 5'''
                            
    '''if result1 is not None:
        print("victim")
        cv2.imshow("thvictim", thresh2)
        cv2.imshow("victim", frame1)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()'''

                
        
    '''
    if cv2.waitKey(1) == ord(' '):
        print("Do you like this image?")
        #cv2.destroyAllWindows()
        cv2.imshow("image_mask",imgOutput1)
        letter = cv2.waitKey(0)
        cv2.destroyAllWindows()
        if letter == ord('y'):
            cv2.imwrite("/home/pi/Documents/Nerd-2021-2022/Nerd-2021-2022-RCJ/RaspberryPiSide/IOFiles/saveVictims/" + str(time.time()) + ".png",frame1)
            #cv2.imwrite("/home/pi/Documents/Nerd-2021-2022/Nerd-2021-2022-RCJ/RaspberryPiSide/IOFiles/saveVictims/" + "mask" + str(time.time()) + ".png",imgOutput1)
            print("saved!")
        else:
            print("not saved")'''
        

    if checkFPS:
        print("Time taken: " + str((time.time()-startTime)))

            
    if cv2.waitKey(1)  == ord('q'):
        break

if numberOfCams == 1 or numberOfCams == 2:
    cap[0].release()
if numberOfCams == 2:
    cap[1].release()
cv2.destroyAllWindows()

