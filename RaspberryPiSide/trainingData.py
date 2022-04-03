import cv2
import numpy as np
import old_detection

cap = cv2.VideoCapture(0)

labels = open("labels.txt",'w')
features = open("features.txt",'w')

size = 30

list_labels = []
list_features = []

letter_count = {'H':0,'S':0,'U':0}



main = detection.Detection()

print("hey ")

while(cap.isOpened):
    
    ret, frame = cap.read()
    
    if(ret > 0):
        
        #Greyscaling, blurring, thresholding
        cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        mask = cv2.inRange(frame,(0,0,0),(50,50,50))
        contours, hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
        input_key = cv2.waitKey(1)
        
        if input_key == ord(' '):
        
            imgOutput = main.getLetter(contours,mask,1)
                    
            letter = chr(cv2.waitKey(0)).upper()
            
            if letter in ['H','S','U']:
                
                letter_count[letter] += 1
                
                print("--------------------")
                print("H:",letter_count['H'])
                print("S:",letter_count['S'])
                print("U:",letter_count['U'])
                
                list_labels.append(np.float32(ord(letter)))
                list_features.append(imgOutput.reshape(1,size*size).astype(np.float32))
                                              
        elif input_key == ord('q'):
                        
            tuple_labels = tuple(list_labels)
            tuple_features = tuple(list_features)
            
            training_labels = np.vstack(tuple_labels)
            training_features = np.vstack(tuple_features)
            
            print(list_labels)

            print(training_labels)
            print(training_features)
            print(training_features.shape)
            
            np.savetxt("labels.txt",training_labels)
            np.savetxt(features,training_features)
            
            break
        
        cv2.imshow("frame",frame)

features.close
labels.close

cap.release()
cv2.destroyAllWindows()
    
    
            
        
            
            
            
            
            
            
            
            
            
            
            
        
    
    
