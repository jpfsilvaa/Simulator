import threading
import sim_utils as utils

class TimerSingleton:
    _instance = None
    _lock = threading.Lock()
    delta = 10 # seconds
    timer = 0

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def incrementTimer(self, i = 1):
        if i < self.getTimerValue():
            raise ValueError('Timer cannot be decremented')
        self.timer = i
        return self.timer
    
    def getTimerValue(self):
        return self.timer
    
    def getDelta(self):
        return self.delta