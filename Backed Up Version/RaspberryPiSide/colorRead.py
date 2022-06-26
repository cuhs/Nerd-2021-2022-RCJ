import cv2
import time
  
coordList = []

# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
         
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
 
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
        coordList.append(x)
        coordList.append(y)
 
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, str(x) + ',' + str(y), (x,y), font, 1, (255, 0, 0), 2)
        cv2.imshow('image', frame)
                
        if len(coordList) == 4:
            print((coordList[2]-coordList[0])*(coordList[3]-coordList[1]))
            maxH = 0
            minH = 300
            maxS = 0
            minS = 300
            maxV = 0
            minV = 300
            
            for j in range(coordList[0],coordList[2]+1):
                for i in range(coordList[1], coordList[3]+1):
                    if maxH < hsv[i][j][0]:
                        maxH = hsv[i][j][0]
                    if minH > hsv[i][j][0]:
                        minH = hsv[i][j][0]
                    if maxS < hsv[i][j][1]:
                        maxS = hsv[i][j][1]
                    if minS > hsv[i][j][1]:
                        minS = hsv[i][j][1]
                    if maxV < hsv[i][j][2]:
                        maxV = hsv[i][j][2]
                    if minV > hsv[i][j][2]:
                        minV = hsv[i][j][2]
                        
            print("Min:", minH, minS, minV)
            print("Max:", maxH, maxS, maxV)
                    
            
 
    # checking for right mouse clicks    
 
# driver function
if __name__=="__main__":
    
    print("select top left and then bottom right")
    
    cap = cv2.VideoCapture(-1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)
 
    # reading the image
    ret,frame = cap.read()
    
    cv2.imshow('image',frame)
    
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    # displaying the image
    cv2.imshow('hsv', hsv)
 
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event)
 
    # wait for a key to be pressed to exit
    cv2.waitKey(0)
 
    # close the window
    cv2.destroyAllWindows()