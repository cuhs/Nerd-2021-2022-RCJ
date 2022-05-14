import cv2
import numpy as np
import KNN
import util
import IO
import time

class Detection:

    # constructor
    def __init__(self):
        self.Debug = False
        self.size = 30
        self.KNN = KNN.KNN()

    # calculate the distance between two points
    def dist(self, point1, point2):
        return np.sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

    # calculate the letter seen by camera, if any
    def getLetter(self, contour, mask, name):
        if len(contour) > 0:
            contour = max(contour, key=cv2.contourArea)

            if cv2.contourArea(contour) > 175:
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.float32(box)

                '''if num == 1:
                    cv2.drawContours(self.frame1,[np.int0(box)],0,(0,255,0),2)
                elif num == 2:
                    cv2.drawContours(self.frame2,[np.int0(box)],0,(0,255,0),2)'''

                s = np.sum(box, axis=1)
                d = np.diff(box, axis=1)

                tL = box[np.argmin(s)]
                tR = box[np.argmin(d)]
                bL = box[np.argmax(d)]
                bR = box[np.argmax(s)]

                pts1 = np.float32([tL, bL, bR, tR])
                pts2 = np.float32([[0, 0], [self.size, 0], [self.size, self.size], [0, self.size]])

                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                imgOutput = cv2.warpPerspective(mask, matrix, (self.size, self.size))

                imgOutput = np.flip(np.rot90(imgOutput), 0)

                if self.dist(tL, tR) > self.dist(tL, bL):
                    imgOutput = np.rot90(imgOutput)

                if self.Debug:
                    cv2.imwrite("../RaspberryPiSide/IOFiles/victimImages/" + (time.ctime(IO.startTime) + "/" +  "-" + str(time.time()) + "cut.png"), imgOutput) #edit
                    cv2.imshow("letter_" + name, imgOutput)

                # result,dist = self.KNN(imgOutput)
                return imgOutput  # , invert

    # process frame and return letter from getLetter
    def letterDetect(self, frame, name):
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.inRange(frame, (0, 0, 0), (25,25, 25))
        contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imgOutput = self.getLetter(contours, mask, name)
        return imgOutput

    # check for letters with KNN
    def KNN_finish(self, imgOutput, distLimit):
        if imgOutput is not None:
            result, dist = self.KNN.classify(imgOutput)
        else:
            result = None
            dist = 0

        if dist > distLimit:
            result = None
        return result

    # use HSV to find color victims
    def colorDetectHSV(self, frame, hsv_lower, hsv_upper):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for i in range(2):
            mask = cv2.inRange(hsv, hsv_lower[i], hsv_upper[i])
            # cv2.imshow("mask",mask)

            contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                contours = max(contours, key=cv2.contourArea)

                if cv2.contourArea(contours) > 200:
                    if i == 0:
                        print("red")
                    if i == 2:
                        print("yellow")
                    if i == 0 or i == 2:
                        return "Y"
                        # packages = 1

                    elif i == 1:
                        return "G"
                        # packages = 0
                    else:
                        return None

    def colorDetectRatio(self, frame):
        b = 0
        g = 0
        r = 0
        
        for i in frame:
            # print(i)
            b += i[0]
            g += i[1]
            r += i[2]
        print(b, g, r)

    # return letter and color victims from right camera
    def rightDetectFinal(self,ret,frame):
        if ret > 0:
            return self.KNN_finish(self.letterDetect(frame, "frame1"), 10005000), self.colorDetectHSV(frame,util.hsv_lower,util.hsv_upper)
        return None, None
    
    # return letter and color victims from left camera
    def leftDetectFinal(self,ret,frame):
        if ret > 0:
            return self.KNN_finish(self.letterDetect(frame, "frame2"), 10005000), self.colorDetectHSV(frame,util.hsv_lower,util.hsv_upper)
        return None, None
    
# old main below
'''                       
hsv_lower = {
    0: (150,230,70),
    1: (50,40,85),
    2: (5,95,160)
    }

hsv_upper = {
     0: (179,255,205),
     1: (90,105,130),
     2: (50,175,195)
     }
main = detection()

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)

total = 0
correct = 0
start = 0

while True:
    print(main.rightDetectFinal())
    print(main.leftDetectFinal())

while cap1.isOpened(): #and cap2.isOpened():

    ret1,frame1 = cap1.read()
    ret2,frame2 = cap2.read()
                        
    if ret1 > 0: #and ret2 > 0:
        #main.colorDetectRatio(frame1)
        
        print(str(main.colorDetectHSV(frame1,hsv_lower,hsv_upper)))
        print(str(main.colorDetectHSV(frame2,hsv_lower,hsv_upper)))

        imgOutput1 = main.letterDetect(frame1,"frame1")
        imgOutput2 = main.letterDetect(frame2, "frame2")
        
        result1 = main.KNN_finish(imgOutput1,10000000)
        result2 = main.KNN_finish(imgOutput2,10000000)
            
        print("Camera1 " + str(result1))
        print("Camera2 " + str(result2))
            
        if main.Debug:
        
            cv2.imshow("frame1",frame1)
            cv2.imshow("frame2",frame2)

            
        if cv2.waitKey(1) == ord('q'):
            break

cap1.release()
cap2.release()
cv2.destroyAllWindows()'''
