import cv2
import numpy as np
import KNN
import util

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
            contour = sorted(contour, key=cv2.contourArea, reverse = True)
            
            for c in contour:
                rect = cv2.minAreaRect(c)
               #print(rect[1][0]/rect[1][1])
                if(rect[1][0]/(rect[1][1] if rect[1][1] != 0 else 0.001) < 2.5 and rect[1][0]/(rect[1][1] if rect[1][1] else 0.001) > 0.3):
                    contour = c
                    break
                contour = None

            if contour is not None and cv2.contourArea(contour) > 0:
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)
                box = np.float32(box)
                
                center = rect[0][0]

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
                
                for r in range(0,30):
                    for h in range(0,30):
                        if imgOutput[r][h] < 127:
                            imgOutput[r][h] = 0 
                        else:
                            imgOutput[r][h] = 1 
                                                        
                return imgOutput, center
            
        return None, None

    # process frame and return letter from getLetter
    def letterDetect(self, frame, name):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.bilateralFilter(gray, 5, 75,75)
        mask  = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 59,11)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        imgOutput, center = self.getLetter(contours, mask, name)
                    
        return imgOutput, center

    # check for letters with KNN
    def KNN_finish(self, imgOutput, center, distLimit):
        if imgOutput is not None:
            for x in range(4):
                result, dist = self.KNN.classify(imgOutput)
                if dist <= distLimit and result is not None:
                    return result, center
                imgOutput = np.rot90(imgOutput)
        return None, None

    # use HSV to find color victims
    def colorDetectHSV(self, frame, hsv_lower, hsv_upper):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for i in range(3):
            mask = cv2.inRange(hsv, hsv_lower[i], hsv_upper[i])

            contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                contours = max(contours, key=cv2.contourArea)

                if cv2.contourArea(contours) > 210: #210
                    rect = cv2.minAreaRect(contours)
                    center = rect[0][0]
                    if i == 0 or i == 2:
                        return "Y", center
                        # packages = 1

                    elif i == 1:
                        return "G", center
                        # packages = 0
                    else:
                        return None, None
        return None, None

    # return letter and color victims from right camera
    #letter center color center 
    def rightDetectFinal(self,ret,frame):
        if ret > 0:
            imgOutput, center = self.letterDetect(frame,"frame1")
            letter, letter_center  = self.KNN_finish(imgOutput, center, 10000000)
            color, color_center = self.colorDetectHSV(frame, util.hsv_lower, util.hsv_upper)
            return letter, letter_center, color, color_center
        return None, None, None, None
    
    # return letter and color victims from left camera
    def leftDetectFinal(self,ret,frame):
        if ret > 0:
            imgOutput, center = self.letterDetect(frame,"frame2")
            letter, letter_center  = self.KNN_finish(imgOutput, center, 10000000)
            color, color_center = self.colorDetectHSV(frame, util.hsv_lower, util.hsv_upper)
            return letter, letter_center, color, color_center
        return None, None, None, None
    