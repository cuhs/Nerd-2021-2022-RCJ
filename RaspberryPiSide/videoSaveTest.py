import cv2
import letterDetection 
  
   
# Create an object to read 
# from camera
video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)

vd = letterDetection.Detection()

# We need to check if camera
# is opened previously or not
if (video.isOpened() == False): 
    print("Error reading video file")
  
# We need to set resolutions.
# so, convert them from float to integer.
frame_width = int(video.get(3))
frame_height = int(video.get(4))
   
size = (frame_width, frame_height*3)
   
# Below VideoWriter object will create
# a frame of above defined The output 
# is stored in 'filename.avi' file.
result = cv2.VideoWriter('filename.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         10.0, size)
    
while(True):
    ret, frame = video.read()
    
  
    if ret == True:
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.bilateralFilter(gray, 5, 75,75)
        mask  = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 59,11)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        imgOutput, center = vd.getLetter(frame,contours,mask)
        
        imgOutput = cv2.resize(imgOutput*255,(160,128))
        imgOutput = cv2.cvtColor(imgOutput, cv2.COLOR_GRAY2BGR)
        
        print(frame.shape)
        print(imgOutput.shape)

        maskTemp = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)

  
        combine = cv2.vconcat([frame, maskTemp, imgOutput])

        result.write(combine)
  
        # Display the frame
        # saved in the file
        cv2.imshow('combine', combine)
  
        # Press S on keyboard 
        # to stop the process
        if cv2.waitKey(1) & 0xFF == ord('s'):
            break
  
    # Break the loop
    else:
        break
  
# When everything done, release 
# the video capture and video 
# write objects
video.release()
result.release()
    
# Closes all the frames
cv2.destroyAllWindows()
   
print("The video was successfully saved")