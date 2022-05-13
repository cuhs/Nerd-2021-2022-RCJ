from threading import Thread
import config
import IO
#import BFS

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
                    #BFS.searchForVictims()
                    
            if config.cameraCount == 2:
                if not IO.frame[1][0]:
                    self.stop()
                elif self.stream2.read()[1] is not None:
                    IO.frame[1] = self.stream2.read()
                    #BFS.searchForVictims()

    def stop(self):
        self.stopped = True
        


