import cv2
import numpy as np
import util
import packet
import time

PIcap = cv2.VideoCapture(0)
USBcap = cv2.VideoCapture(1)

PIcap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
PIcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

USBcap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
USBcap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

knn = cv2.ml.KNearest_create()

height = 30 
width = 30 

features = np.loadtxt("/home/pi/Documents/KNN/trainingData/featuresFinal.txt", dtype=np.float32)
labels = np.loadtxt("/home/pi/Documents/KNN/trainingData/labelsFinal.txt", dtype=np.float32)

knn.train(features, cv2.ml.ROW_SAMPLE, labels)


red = [(0, 70, 50), (10, 255, 255)]

green = [(30, 60, 50), (80, 255, 255)]

yellow = [(0, 100, 100), (50, 255, 255)]

colorRange = red,green,yellow
colorName = ["red","green","yellow"]

def detectAll():
    
    PIpackages = 0
    USBpackages = 0
    
    PIvictim = False
    USBvictim = False


    if(PIcap.isOpened):
        
        #print("working")
        #for x in range(50):    
        ret, frame = PIcap.read()
            
        frame = cv2.flip(frame,-1)
                    
        if(ret > 0):
            
            hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
             
            for colorType in range(3):
            
                mask = cv2.inRange(hsv,colorRange[colorType][0],colorRange[colorType][1])
            
                contours,high = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            
                if(len(contours)>0):
                    #cv2.drawContours(viewFrame,contours,-1,(255,255,255),3)
                    
                    contours = max(contours,key=cv2.contourArea)
                    
                    if(cv2.contourArea(contours)>300):
                    
                        #M = cv2.moments(contours)
                        #centerX = int(M["m10"] / M["m00"])
                        #centerY = int(M["m01"] / M["m00"])
                        
                        #print(colorName[colorType])
                        
                        PIvictim = True
                        
                        if colorType == 0 or colorType == 2:
                            #print("Red/Yellow")
                            PIpackages = 1
                            
                        if colorType == 1:
                            #print("Green")
                            PIpackages = 0

                        #cv2.putText(viewFrame, colorName[colorType],(centerX-30,centerY),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
                           
            #Greyscaling, blurring, thresholding
            grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            blur = cv2.GaussianBlur(grey,(3,3),0)
            
            mask = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,51,21) #37-11
            
            #cv2.imshow("mask",mask)
            
            #Finding contour of letter
            contour, high = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            
            if len(contour) > 0:
                                
                contour = max(contour, key = cv2.contourArea)
                
                mask = cv2.drawContours(mask,[contour],0,(255,255,255),-1)
                
                contour, high = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                contour = max(contour, key = cv2.contourArea)
                
                if (cv2.contourArea(contour) > 300):
                                        
                    #Getting corners of contour
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
                    box = np.float32(box)
                    
                    s = np.sum(box, axis = 1)
                    d = np.diff(box, axis = 1)
                    
                    tL = box[np.argmin(s)]
                    bR = box[np.argmax(s)]
                    
                    tR = box[np.argmax(d)]
                    bL = box[np.argmin(d)]
                    
                    pts1 = np.float32([bR,bL,tR,tL])
                    pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
                    
                    matrix = cv2.getPerspectiveTransform(pts1,pts2)
                    imgOutput = cv2.warpPerspective(mask,matrix,(width,height))
                    
                    imgOutput = np.flip(np.rot90(imgOutput),1)
                    
                    knnInput = imgOutput.reshape(1,width*height).astype(np.float32)
                                    
                    cv2.drawContours(frame,[np.int0(box)],0,(0,255,0),2)
                    
                    _,result,neighbors,distance = knn.findNearest(knnInput,5)
                    
                    lowestDist = distance[:,0]
                    
                    result = chr(result[0][0])
                    
                
                    if lowestDist > 10000000:
                        #print("None of the Letters")
                        none = 1
                        #print("")
                        #packages = 0
                        
                    else:
                        #print(result)
                        
                        PIvictim = True
                        
                        if result == 'H':
                            PIpackages = 3
                            
                        if result == 'S':
                            PIpackages = 2
                            
                        if result == 'U':
                            PIpackages = 0
                        
                    #cv2.imshow("letter",imgOutput)
                    
    if(USBcap.isOpened):
        
        #for x in range(50):          
        ret2, frame2 = USBcap.read()
                    
        if(ret2 > 0):
            
            hsv2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2HSV)
             
            for colorType in range(3):
            
                mask2 = cv2.inRange(hsv2,colorRange[colorType][0],colorRange[colorType][1])
            
                contours2,high = cv2.findContours(mask2,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            
                if(len(contours2)>0):
                    #cv2.drawContours(viewFrame,contours,-1,(255,255,255),3)
                    
                    contours2 = max(contours2,key=cv2.contourArea)
                    
                    if(cv2.contourArea(contours2)>5000):
                    
                        #M = cv2.moments(contours2)
                        #centerX = int(M["m10"] / M["m00"])
                        #centerY = int(M["m01"] / M["m00"])
                        
                        #print(colorName[colorType])
                        
                        USBvictim = True
                        
                        if colorType == 0 or colorType == 2:
                            #print("Red/Yellow")
                            USBpackages = 1
                            
                        if colorType == 1:
                            #print("Green")
                            USBpackages = 0

                        #cv2.putText(viewFrame, colorName[colorType],(centerX-30,centerY),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)
                           
            #Greyscaling, blurring, thresholding
            grey2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
            
            blur2 = cv2.GaussianBlur(grey2,(3,3),0) 
                        
            mask2 = cv2.adaptiveThreshold(blur2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,51,21) #37-11 #39-19
            
            #cv2.imshow("mask",mask)
            
            #Finding contour of letter
            contour2, high = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            
            if len(contour2) > 0:
                                                
                contour2 = max(contour2, key = cv2.contourArea)
                
                mask2 = cv2.drawContours(mask2,[contour2],0,(255,255,255),-1)
                
                contour2, high = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                contour2 = max(contour2, key = cv2.contourArea)
                
                if (cv2.contourArea(contour2) > 300):
                                        
                    #Getting corners of contour
                    rect2 = cv2.minAreaRect(contour2)
                    box2 = cv2.boxPoints(rect2)
                    box2 = np.float32(box2)
                    
                    s2 = np.sum(box2, axis = 1)
                    d2 = np.diff(box2, axis = 1)
                    
                    tL2 = box2[np.argmin(s2)]
                    bR2 = box2[np.argmax(s2)]
                    
                    tR2 = box2[np.argmax(d2)]
                    bL2 = box2[np.argmin(d2)]
                    
                    pts12 = np.float32([bR2,bL2,tR2,tL2])
                    pts22 = np.float32([[0,0],[width,0],[0,height],[width,height]])
                    
                    matrix2 = cv2.getPerspectiveTransform(pts12,pts22)
                    imgOutput2 = cv2.warpPerspective(mask2,matrix2,(width,height))
                    
                    imgOutput2 = np.flip(np.rot90(imgOutput2),1)
                    
                    knnInput2 = imgOutput2.reshape(1,width*height).astype(np.float32)
                                    
                    #cv2.drawContours(frame2,[np.int0(box2)],0,(0,255,0),2)
                    
                    _,result2,neighbors2,distance2 = knn.findNearest(knnInput2,5)
                    
                    lowestDist2 = distance2[:,0]
                    
                    result2 = chr(result2[0][0])
                    
                
                    if lowestDist2 > 10000000:
                        #print("None of the Letters")
                        none=1
                        #print("")
                        #packages = 0
                        
                    else:
                        #print(result2)
                        
                        USBvictim = True
                        
                        if result2 == 'H':
                            USBpackages = 3
                            
                        if result2 == 'S':
                            USBpackages = 2
                            
                        if result2 == 'U':
                            USBpackages = 0
        
    cv2.imshow("Pi", frame)
    cv2.imshow("Usb", frame2)
    
    cv2.waitKey(1)
                            
    #cv2.imread(frame)
    #cv2.imread(frame2)
        
    return (PIvictim, PIpackages, USBvictim, USBpackages)
        
        #if cv2.waitKey(1) == ord('q'):
            #break
        
    #cap.release()
    #cv2.destroyAllWindows()
    
#while True:
    #print(detectAll())

def sendVictims():
    util.maze[util.tile][util.visited] = 2
    for x in range(3):
        right, packageR, left, packageL = detectAll()
    print("HERE:", left, packageL, right, packageR)

    if left is True or right is True:
        util.maze[util.tile][util.visited] = 2

        if left is True:
            send_message1 = "L" + str(packageL)
            print(send_message1)
            packet.ser.write(bytes(send_message1.encode("ascii", "ignore")))

        if right is True:
            send_message2 = "R" + str(packageR)
            print(send_message2)
            packet.ser.write(bytes(send_message2.encode("ascii", "ignore")))

def getVideo():
    PIcap.read()
    USBcap.read()
    time.sleep(0.01)
