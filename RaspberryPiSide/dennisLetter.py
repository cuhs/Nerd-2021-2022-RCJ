#!/usr/bin/python3
import numpy as np
import cv2
import time
from datetime import datetime
from datetime import timedelta

divisor = 2
framewidth = 640//divisor
frameheight= 480//divisor

class OuterCam:
     def __init__(self, name, id):
         self.name = name
         self.id = id
         self.cam = cv2.VideoCapture(id)
         self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,  framewidth)
         self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frameheight)

         self.dt = datetime.now()
         self.fps=0
         self.count=0

     def read(self):
         delta =  datetime.now()-self.dt
         self.dt = datetime.now()
         self.fps = 1000000//delta.microseconds
         self.count = (self.count+1) % 20
         if self.count==0:
             pass
             #print ("{0} at {1}".format(self.name,self.fps))
         return self.cam.read()

def countContours(img):
     npaContours,_ = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
     return len(npaContours)

def main():
     cameras = [
         OuterCam("PiCamera0",0),
         #OuterCam("Logitech1",1),
         #OuterCam("Logitech2",2)
         ]

     for camera in cameras:
         if (camera.cam.isOpened() == False):
             print ("{0} didn't open".format(camera.name))
             return
         else:
             print ("{0} Opened".format(camera.name))

     while(True):
         for camera in cameras:
             ret, frame = camera.read()
             frame = frame[:,:290]

             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
             #blur = cv2.GaussianBlur(gray,(5,5),0)

             #ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
             thresh  = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25,3)
             cv2.imshow("tthresh",thresh)
             if cv2.waitKey(1) == ord(' '):
                 time.sleep(10)
             #threshcopy = thresh.copy()
             npaContours, _ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
             
             if len(npaContours) > 0:

                 largestcnt = sorted(npaContours, key=cv2.contourArea,reverse=True)[:1][0]
                 x,y,w,h = cv2.boundingRect(largestcnt)
                 cv2.rectangle(frame,(x,y),(x+w,y+h),(0, 255, 0),2)

                 threshROI= thresh[y:y+h, x:x+w]

                 (roiy,roix) = threshROI.shape
                 #print ("y:{0} x:{1}".format(y,x))
                 topROI = threshROI[0:(roiy//3),0:roix]
                 midROI = threshROI[8+(roiy//3):2*roiy//3,0:roix]
                 botROI = threshROI[2*roiy//3:roiy,0:roix]
                 ratio = roix/roiy
                 #cv2.imshow(camera.name+"top",topROI)
                 #cv2.imshow(camera.name+"mid",midROI)
                 #cv2.imshow(camera.name+"bot",botROI)


                 topcount=countContours(topROI)
                 midcount=countContours(midROI)
                 botcount=countContours(botROI)
                 if ratio >0.88 or ratio < 0.65:
                     text="?"
                 elif topcount == 1 and midcount == 1 and botcount == 1:
                     text="S"
                 elif topcount == 2 and midcount == 1 and botcount == 2:
                     text="H"
                 elif topcount == 2 and midcount == 2 and botcount == 1:
                     text="U"
                 else:
                     text="?"

                 print ("{0} {1} {2} {3} {4} {5}".format(camera.name,text,countContours(topROI),countContours(midROI),countContours(botROI),ratio))
                 cv2.putText(frame,text,(x+2,y+h-2),cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),3,cv2.LINE_AA)
             cv2.imshow(camera.name,frame)

             if text=="S":
                 cv2.imshow("mask",thresh)
                 time.sleep(3);


         if cv2.waitKey(1) & 0xFF == ord('q'):
             break

     for camera in cameras:
         camera.cam.release()
     print ("All closed...")
     cv2.destroyAllWindows()


main()