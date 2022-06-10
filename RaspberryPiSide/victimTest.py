import cv2
import numpy as np
import KNN
import time
import letterDetection


#CONFIG----------------------------------------

numberOfCams = 1 #number of camera to run
cap = [None,None] #left, right
victimDetect = True #true --> tests victim detection, false --> runs camera feed
width = 160 #camera width
height = 128 #camera height

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
         
victimDetecton = letterDetection.Detection()


while cap1.isOpened(): #and cap2.isOpened():
    
    ret1,frame1 = cap1.read()
    #frame1 = frame1[:225,:300]
    #frame1 = frame1[:,:150]
    
    #startTime = time.time()
    
    #frame1 = cv2.flip(frame1, 0)

    #ret2,frame2 = cap2.read()
    
    frame1 = frame1[:,:150] #H, W LEFT
    
    gray = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    
    blur = cv2.bilateralFilter(gray, 5, 75,75)

    thresh2  = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17,3) #21, 5


    #frame2 = frame2[:,:152] #RIGHT
                            
    if ret1 > 0: #and ret2 > 0:
        
        print(main.colorDetect(frame1,hsv_lower,hsv_upper))
        #print(main.colorDetect(frame1,hsv_lower,hsv_upper))

        imgOutput1, center = main.letterDetect(frame1,"frame1")
        
        
        center = np.int32(center)
        
        print(center)


        cv2.imshow("imgOutput", thresh2)
        
        cv2.circle(frame1, center, 2, (255,255,0), -1)
        #imgOutput1 = main.letterDetect(frame1,"frame1")

        #imgOutput2 = main.letterDetect(frame2, "frame2")
        
        result1 =  main.KNN_finish(imgOutput1,10000000)
        
        print(str(result1))
        
        cv2.imshow("imgOUtput", imgOutput1)
        #result1 =  main.KNN_finish(imgOutput1,9000000)
        
        '''if result1 is not None:
            print("victim")
            cv2.imshow("thvictim", thresh2)
            #cv2.imshow("victim", frame1)
            cv2.waitKey(1000)
            cv2.destroyAllWindows()'''


        #result2 = main.KNN_finish(imgOutput2,10000000)
        
        #cv2.imwrite("/home/pi/Documents/VictimImages/" + str(time.time()) + ".png", frame1)
        
        
        
        '''if cv2.waitKey(1) == ord(' '):
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

        
        #print("Camera1 " + str(result1))
        #print("Time taken: " + str((time.time()-startTime)))
        #print("Camera2 " + result2)
        
        #print()
            
        if main.Debug:
            #pass
            #cv2.waitKey(1000)
            cv2.imshow("frame1",frame1)
            #cv2.imshow("thresh",thresh2)
            #cv2.imshow("mask",thresh2)
            #if imgOutput1 is not None:
                #cv2.imshow("imgOutput1",imgOutput1)
            #cv2.imshow("combine",combine)
            #cv2.imshow("frame2",frame2)

            
    if cv2.waitKey(1)  == ord('q'):
        break

cap1.release()
#cap2.release()
cv2.destroyAllWindows()

