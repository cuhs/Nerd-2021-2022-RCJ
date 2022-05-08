from threading import Thread
import config
import IO

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
            if config.cameraCount >= 1:
                if not IO.frame[0][0]:
                    self.stop()
                else:
                    IO.frame[0] = self.stream1.read()
                    
            if config.cameraCount == 2:
                if not IO.frame[1][0]:
                    self.stop()
                else:
                    IO.frame[1] = self.stream2.read()

    def stop(self):
        self.stopped = True
        


