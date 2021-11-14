import cv2

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


while cap1.isOpened() and cap2.isOpened():
     
    ret1,frame1 = cap1.read()
    ret2,frame2 = cap2.read()
    
    
    if ret1 > 0 and ret2 > 0:
        
        cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        
        mask1 = cv2.inRange(frame1,(0,0,0),(50,50,50))
        mask2 = cv2.inRange(frame2,(0,0,0),(50,50,50))
        
        contours1, hier = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours2, hier = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours1) > 0 and len(contours2) > 0:
        
            contours1 = max(contours1, key = cv2.contourArea)
            contours2 = max(contours2, key = cv2.contourArea)
        
            cv2.drawContours(frame1, contours1[0], -1, (255,0,0), 2)
            cv2.drawContours(frame2, contours2[0], -1, (0,0,255), 2)

        cv2.imshow("frame1", frame1)
        cv2.imshow("frame2", frame2)
        
        cv2.imshow("mask1",mask1)
        cv2.imshow("mask2",mask2)
    
    if cv2.waitKey(1) == ord('q'):
        break
    
cv2.destroyAllWindows()
cap1.release()
cap2.release()
        
        