import cv2
import numpy as np
import letterDetection
import os

size = 30

list_labels = []
list_features = []

letter_count = {'H':0,'S':0,'U':0}

main = letterDetection.Detection()

directory = "/home/pi/Documents/Nerd-2021-2022/Nerd-2021-2022-RCJ/RaspberryPiSide/IOFiles/saveVictims"


with open("KNN/labels7.txt", 'w') as labels, open ("KNN/features7.txt", 'w') as features:

    for filename in os.listdir(directory):    
        
        f = os.path.join(directory,filename)

        if os.path.isfile(f):
            
            print(f)
            
            frame = cv2.imread(f)
            
            cv2.imshow("frame", frame)
            cv2.waitKey(0) 
            
            imgOutput, center = main.letterDetect(frame)
            
            cv2.imshow("frame", frame)
            cv2.imshow("imgOutput", imgOutput*255)
                        
            letter = chr(cv2.waitKey(0)).upper()
            
            cv2.destroyAllWindows()
                
            if letter in ['H','S','U']:
                    
                letter_count[letter] += 1
                
                print("--------------------")
                print("H:",letter_count['H'])
                print("S:",letter_count['S'])
                print("U:",letter_count['U'])
                
                list_labels.append(np.float32(ord(letter)))
                list_features.append(imgOutput.reshape(1,size*size).astype(np.float32))
                                                  
                            
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
                

    cv2.destroyAllWindows()
        
        
                
            
            
            
            
            
            
            
            
            
            
            
            
        
    
    

