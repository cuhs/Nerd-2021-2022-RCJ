import cv2
import letterDetection

cap1 = cv2.VideoCapture(-1)
#cap2 = cv2.VideoCapture(1)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)
#cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
#cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)

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


while cap1.isOpened(): #and cap2.isOpened():
     
    ret1,frame1 = cap1.read()
    #ret2,frame2 = cap2.read()
    
    if ret1 > 0: #and ret2 > 0:
        
        imgOutput1 = letterDetection.Detection.letterDetect(frame1,"frame1")
        #imgOutput2 = letterDetection.Detection.letterDetect(frame2, "frame2")
        
        result1 = letterDetection.Detection.KNN_finish(imgOutput1,10000000)
        #result2 = letterDetection.Detection.KNN_finish(imgOutput2,10000000)
            
        print("Camera1 " + str(result1))
        #print("Camera2 " + str(result2))
        
        print("Camera 1: " + str(letterDetection.Detection.colorDetectHSV(frame1,hsv_lower,hsv_upper)))
        #print("Camera 2: " + str(letterDetection.Detection.colorDetectHSV(frame2,hsv_lower,hsv_upper)))

        cv2.imshow("frame1", frame1)
        #cv2.imshow("frame2", frame2)

    
    if cv2.waitKey(1) == ord('q'):
        break
    
cv2.destroyAllWindows()
cap1.release()
#cap2.release()
        
        