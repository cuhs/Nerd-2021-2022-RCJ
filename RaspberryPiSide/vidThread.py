from threading import Thread
import config
import IO
import cv2

class VideoGet:
    
    def __init__(self):
        if config.cameraCount == 1 or config.cameraCount == 2:
            self.stream1 = IO.cap[0]
            IO.frame.append(self.stream1.read())

        if config.cameraCount == 2:
            self.stream2 = IO.cap[1]
            IO.frame.append(self.stream2.read())
        self.stopped = False
        
    def start(self):
        Thread(target=self.get, args=()).start()
        return self
    
    def get(self):
        while not self.stopped:
            #print("working 9 to 5")
            if config.cameraCount >= 1:
                if not IO.frame[0][0]:
                    self.stop()
                elif self.stream1.read()[1] is not None:
                    
                    IO.frame[0] = self.stream1.read()
                    
                    #IO.frame[0][1] = IO.frame[0][1][:,:150]

                    
                    #leftRet = IO.frame[0][0]
                    #leftFrame = IO.frame[0][1][:,:150]
                    
                    if config.victimDebug and IO.frame[0][1] is not None:
                        cv2.imshow("left", IO.frame[0][1])
                        cv2.waitKey(1)
                        
                    #if config.saveVictimDebug:
                        #cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + leftColorVictim + "-" + time.ctime(time.time()) + ".png"), leftFrame)
                    
                    #IO.victim[0], IO.victim[2] =  letterDetection.Detection().leftDetectFinal(leftRet, leftFrame)
                                        
            if config.cameraCount == 2:
                if not IO.frame[1][0]:
                    self.stop()
                elif self.stream2.read()[1] is not None:
                    IO.frame[1] = self.stream2.read()
                    
                    #IO.frame[0][0] = IO.frame[0][0][:,:150]

                    
                    #rightRet = IO.frame[1][0]
                    #rightFrame = IO.frame[1][1][:,:150]
                   
                    if config.victimDebug and IO.frame[1][1] is not None:
                        cv2.imshow("right", IO.frame[1][1])
                        cv2.waitKey(1)
                        
                    #if config.saveVictimDebug:
                        #cv2.imwrite(config.fpVIC + (time.ctime(IO.startTime) + "/" + rightLetterVictim + "-" + time.ctime(time.time()) + ".png"), rightFrame)
                        
                    #IO.victim[1], IO.victim[3] = letterDetection.Detection().rightDetectFinal(rightRet, rightFrame)

    def stop(self):
        self.stopped = True
        


