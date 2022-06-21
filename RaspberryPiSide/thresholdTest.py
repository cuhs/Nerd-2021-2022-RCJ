import cv2
import numpy as np

def nothing(x):
    pass

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,128)

cv2.namedWindow("Trackbars")
cv2.createTrackbar("blockSize", "Trackbars", 1, 100, nothing)
cv2.createTrackbar("constant", "Trackbars", 1, 100, nothing)

while cap.isOpened():
    
    ret, frame = cap.read()
    
    if not ret:
        break
    
    blockSize = cv2.getTrackbarPos("blockSize", "Trackbars")
    constant = cv2.getTrackbarPos("constant", "Trackbars")
    
    blockSize = int(not(blockSize%2)) + blockSize
    
    if blockSize < 3:
        blockSize = 3
    
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 5, 75, 75)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,blockSize,constant)
    
    cv2.imshow("thresh", thresh)
    cv2.imshow("frame", frame)
    
    if cv2.waitKey(1)  == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()

        





