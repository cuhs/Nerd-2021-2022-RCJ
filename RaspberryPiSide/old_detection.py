import cv2
import numpy as np
import KNN

class detection():
    
    def __init__(self):
        
        self.Debug = True
        
        self.size = 30
    
    def dist(self,point1,point2):
        return(np.sqrt(((point1[0]-point2[0])**2) + ((point1[1]-point2[1])**2)))
    
    def centroidMethod(self, imgOutput,num):
    
        imgOutput = cv2.bitwise_not(imgOutput, mask = None)
        image = imgOutput
    
        if self.Debug:
            cv2.imshow("invert" + str(num),imgOutput)
            
        contours, hier = cv2.findContours(imgOutput, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for c in contours:
            if cv2.contourArea(c)>250:
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                cv2.circle(image,(cX,cY),3,(0,0,0),-1)
                cv2.imshow("image" + str(num),image)
            
        return imgOutput

        
    def getLetter(self, contour,mask,num):
        
        if len(contour) > 0:
            
            contour = max(contour, key = cv2.contourArea)
            
            if(cv2.contourArea(contour)>50):
                
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.float32(box)
                
                '''if num == 1:
                    cv2.drawContours(self.frame1,[np.int0(box)],0,(0,255,0),2)
                elif num == 2:
                    cv2.drawContours(self.frame2,[np.int0(box)],0,(0,255,0),2)'''
                
                s = np.sum(box, axis = 1)
                d = np.diff(box, axis = 1)
                
                tL = box[np.argmin(s)]
                tR = box[np.argmin(d)]
                bL = box[np.argmax(d)]
                bR = box[np.argmax(s)]
                                                
                pts1 = np.float32([tL, bL, bR, tR])
                pts2 = np.float32([[0,0], [self.size,0], [self.size,self.size] ,[0,self.size]])
            
                matrix = cv2.getPerspectiveTransform(pts1,pts2)
                imgOutput = cv2.warpPerspective(mask, matrix, (self.size,self.size))
                
                imgOutput = np.flip(np.rot90(imgOutput),0)
                                
                if self.dist(tL,tR) > self.dist(tL,bL):
                    imgOutput = np.rot90(imgOutput)
                
                if self.Debug:
                    cv2.imshow("letter" + str(num),imgOutput)
                
                #result,dist = self.KNN(imgOutput)
                
                return imgOutput#, invert
            
        
    def letterDetect(self,frame1,frame2):
        
        cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
    
        mask1 = cv2.inRange(frame1,(0,0,0),(50,50,50))
        mask2 = cv2.inRange(frame2,(0,0,0),(50,50,50))
    
        contours1, hier = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, hier = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        imgOutput1 = self.getLetter(contours1,mask1,1)
        imgOutput2 = self.getLetter(contours2,mask2,2)
        
        return imgOutput1,imgOutput2
        
'''main = detection()
KNN = KNN.KNN()

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

total = 0
correct = 0
start = 0

while cap1.isOpened() and cap2.isOpened():
    
    ret1,frame1 = cap1.read()
    ret2,frame2 = cap2.read()
                        
    if ret1 > 0 and ret2 > 0:
            
        imgOutput1,imgOutput2 = main.letterDetect(frame1,frame2)
        
        if imgOutput1 is not None:
            result1, dist1 = KNN.classify(imgOutput1)
        else:
            result1 = "None"
            dist1 = 0
            
        if imgOutput2 is not None:
            result2, dist2 = KNN.classify(imgOutput2)
        else:
            result2 = "None"
            dist2 = 0
        
        if dist1 > 10000000:
            result1 = "None"
            
        if dist2 > 10000000:
            result2 = "None"
            
        print("Camera1 " + result1)
        print("Camera2 " + result2)
        
        if start != 1 and cv2.waitKey(1) == ord('x'):
            print("X")
            start = 1

        if start == 1:        
            total = total+1
            
            if(result1 == 'U'):
                correct = correct+1

        
            
        if main.Debug:
                
            cv2.imshow("frame1",frame1)
            cv2.imshow("frame2",frame2)

            
    if cv2.waitKey(1) == ord('q'):
        break

print("Total: " + str(total) + "\tCorrect: " + str(correct) + "\nPercentage: " + str(float(correct)/total * 100)[:4] + "%")
cap1.release()
cap2.release()
cv2.destroyAllWindows()'''


            
