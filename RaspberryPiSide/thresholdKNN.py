import numpy as np

value = ""
num = 0
lineFinal = ""
list_features = []
count = 0
countEnter = 0

print("hi")

with open("KNN/features3.txt", 'r') as featuresRead, open("KNN/features3-2.txt", 'w') as features:
    
    contents = featuresRead.readlines()
    
    print(contents[0][23])
    
    for line in contents:
        for letter in line:
            if letter == ' ' or letter == '\n':
                num = (float(value[0]) + float(value[2])/10 + float(value[3])/100) * (10**float(value[23])+1)
                #print(num)
                if num > 127:
                    #lineFinal += "2.550000000000000000e+02" + letter
                    lineFinal += "1.000000000000000000e+00" + letter
                else:
                    lineFinal += "0.000000000000000000e+00" + letter
                value = ""
            else:
                value = value + letter
            if letter == '\n':
                countEnter +=1
                print(countEnter)
        count += 1
        print(count)
                
        #list_features.append(line)
       # line = ""
        
    #tuple_features = tuple(list_features)
    #training_features = np.vstack(tuple_features)
        
    #training_features = np.float32(training_features)
    
    print(lineFinal)
    features.write(lineFinal)    

    #np.savetxt(features,training_features)

    

                
                
            
    
    
    
        
 

