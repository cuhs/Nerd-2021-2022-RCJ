from threading import Thread
import cv2
import config
import IO

class VideoGet:
    
    def __init__(self):
        if config.cameraCount == 1 or config.cameraCount == 2:
            self.stream1 = IO.cap[0]
            (self.grabbed1, self.frame1) = self.stream1.read()

        if config.cameraCount == 2:
            self.stream2 = IO.cap[1]
            (self.grabbed2, self.frame2) = self.stream2.read()
        self.stopped = False
        
    def start(self):
        Thread(target=self.get, args = ()).start()
        return self
    
    
    def get(self):
        while not self.stopped:
            if config.cameraCount == 1 or config.cameraCount == 2:
                if not self.grabbed1:
                    self.stop()
                else:
                    (self.grabbed1, self.frame1) = self.stream1.read()
                    
            if config.cameraCount == 2:
                if not self.grabbed2:
                    self.stop()
                else:
                    (self.grabbed2, self.frame2) = self.stream2.read()
                    print("hihihi")
                    print(self.frame2)
                    print("hihihi")
                
    def stop(self):
        self.stopped = True
        


