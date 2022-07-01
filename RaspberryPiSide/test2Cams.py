import cv2
#import letterDetection

#cap1 = cv2.VideoCapture(-1)
#cap2 = cv2.VideoCapture(1)

#cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

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

#cap1.set(3,cap1.get(3)//4)
#cap1.set(4,cap1.get(4)//4+8)

#print(cap1.get(3))
#print(cap1.get(4))




while True: #and cap2.isOpened():
    
    frame = cv2.imread('IOFiles/saveVictims/1656264323.482463.png')
     
    #ret1,frame1 = cap1.read()
    #ret2,frame2 = cap2.read()
    
    #frame1 = frame1[:460,:580]
    #frame2 = frame2[:230,20:]
    
    
    
    if 0 == 0: #and ret2 > 0:
        
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        blur = cv2.blur(frame,(5,5))
        blurBilateral = cv2.bilateralFilter(frame, 5, 75,75)
        blurGaussian = cv2.GaussianBlur(frame, (5,5), 0)
        blurMedian = cv2.medianBlur(frame,5)
        
        size = 23
        constant = 3
        
        
        maskBlur  = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, size,constant)
        maskBlurBilateral  = cv2.adaptiveThreshold(blurBilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, size,constant)
        maskBlurGaussian  = cv2.adaptiveThreshold(blurGaussian, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, size,constant)
        maskBlurMedian  = cv2.adaptiveThreshold(blurMedian, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, size,constant)

        #ontours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        '''
        if len(contours) > 0:
            contours = max(contours, key = cv2.contourArea)
            x,y,w,h = cv2.boundingRect(contours)
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,255),1)
            print(str(w/h))
            print(str(h/w))
            #0.88, 0.65'''
        

        
        
        #imgOutput1 = letterDetection.Detection.letterDetect(frame1,"frame1")
        #imgOutput2 = letterDetection.Detection.letterDetect(frame2, "frame2")
        
        #result1 = letterDetection.Detection.KNN_finish(imgOutput1,10000000)
        #result2 = letterDetection.Detection.KNN_finish(imgOutput2,10000000)
            
        #print("Camera1 " + str(result1))
        #print("Camera2 " + str(result2))
        
        #print("Camera 1: " + str(letterDetection.Detection.colorDetectHSV(frame1,hsv_lower,hsv_upper)))
        #print("Camera 2: " + str(letterDetection.Detection.colorDetectHSV(frame2,hsv_lower,hsv_upper)))
        
        #height, width = frame1.shape[:2]


        #cv2.imshow("frame", frame)
        #cv2.imshow("gray", gray)
        #cv2.imshow("mask", mask)
        
        cv2.imshow("blur", maskBlur)
        cv2.imshow("Gaussian", maskBlurGaussian)
        cv2.imshow("Bilateral", maskBlurBilateral)
        cv2.imshow("Median", maskBlurMedian)

    
    if cv2.waitKey(1) == ord('q'):
        break
    
cv2.destroyAllWindows()
#cap1.release()
#cap2.release()
        
        