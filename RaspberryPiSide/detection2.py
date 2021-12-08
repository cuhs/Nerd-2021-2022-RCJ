import cv2
import numpy as np
import KNN

class detection():

    def __init__(self):

        self.Debug = True
        self.size = 30
        self.KNN = KNN.KNN()

    def dist(self, point1, point2):
        return np.sqrt(((point1[0] - point2[0]) ** 2) + ((point1[1] - point2[1]) ** 2))

    def getLetter(self, contour, mask, name):

        if len(contour) > 0:

            contour = max(contour, key=cv2.contourArea)

            if cv2.contourArea(contour) > 50:

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
                    cv2.imshow("letter_" + name, imgOutput)

                # result,dist = self.KNN(imgOutput)

                return imgOutput  # , invert

    def letterDetect(self, frame, name):

        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        mask = cv2.inRange(frame, (0, 0, 0), (50, 50, 50))

        contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        imgOutput = self.getLetter(contours, mask, name)

        return imgOutput

    def KNN_finish(self, imgOutput, distLimit):

        if imgOutput is not None:
            result, dist = self.KNN.classify(imgOutput)
        else:
            result = "None"
            dist = 0

        if dist > distLimit:
            result = "None"

        return result

    def colorDetect(self, frame, hsv_lower, hsv_upper):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for i in range(1):
            mask = cv2.inRange(hsv, hsv_lower[i], hsv_upper[i])
            # cv2.imshow("mask",mask)

            contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) > 0:

                contours = max(contours, key=cv2.contourArea)

                if cv2.contourArea(contours) > 50:

                    if i == 0 or i == 2:
                        print("Red/Yellow")
                        packages = 1

                    if i == 1:
                        print("Green")
                        packages = 0
