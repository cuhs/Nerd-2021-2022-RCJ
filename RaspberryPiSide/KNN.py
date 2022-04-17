import cv2
import numpy as np
import config

class KNN:
    
    def __init__(self):
        self.knn = cv2.ml.KNearest_create()
        features = np.loadtxt(config.fpKNN + "features2.txt", dtype=np.float32)
        labels = np.loadtxt(config.fpKNN + "labels2.txt", dtype=np.float32)

        self.knn.train(features, cv2.ml.ROW_SAMPLE, labels)

    def classify(self, imgOutput):
        knnInput = imgOutput.reshape(1, 30*30).astype(np.float32)
        _, result, neighbors, distance = self.knn.findNearest(knnInput, 5)
                    
        lowestDist = distance[:, 0]
        result = chr(result[0][0])
        return result, lowestDist
