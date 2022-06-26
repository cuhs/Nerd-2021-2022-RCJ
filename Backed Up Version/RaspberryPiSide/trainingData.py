import cv2
import numpy as np
import letterDetection

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 128)

size = 30

list_labels = []
list_features = []

letter_count = {'H':0,'S':0,'U':0}

main = letterDetection.Detection()

print("start")


with open("KNN/labels4.txt", 'w') as labels, open ("KNN/features4.txt", 'w') as features:


    while(cap.isOpened):
        
        ret, frame = cap.read()
        
        frame = frame[:,:150]
        
        if(ret > 0):
                    
            imgOutput, center = main.letterDetect(frame)
                
            input_key = cv2.waitKey(1)
            
            if input_key == ord(' '):
            
                
                cv2.imshow("imgOutput", imgOutput)
                        
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
                
                np.savetxt(labels,training_labels)
                np.savetxt(features,training_features)
                
                break 
            
            cv2.imshow("frame",frame)
            cv2.imshow("imgOutput", imgOutput)

    cap.release()
    cv2.destroyAllWindows()
    
    
            
        
            
            
            
            
            
            
            
            
            
            
            
        
    
    
