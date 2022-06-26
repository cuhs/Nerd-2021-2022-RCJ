import cv2
import numpy as np
import config

class KNN:
    
    def __init__(self):
        self.knn = cv2.ml.KNearest_create()
        features = np.loadtxt(config.fpKNN + "features7.txt", dtype=np.float32)
        labels = np.loadtxt(config.fpKNN + "labels7.txt", dtype=np.float32)

        self.knn.train(features, cv2.ml.ROW_SAMPLE, labels)

    def classify(self, imgOutput):
        knnInput = imgOutput.reshape(1, 30*30).astype(np.float32)
        _, result, neighbors, distance = self.knn.findNearest(knnInput, 3)
        
        #print(distance)
                    
        lowestDist = distance[:, 0]
        result = chr(result[0][0])
        
        #print("Distance: " + str(lowestDist))
        
        return result, lowestDist
