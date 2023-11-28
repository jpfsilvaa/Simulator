import threading
import sim_utils as utils

class TimerSingleton:
    _instance = None
    _lock = threading.Lock()
    delta = 60 # seconds
    timer = 0
    timerLimit = 3600 # seconds
    optTimeLimitReached = False

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
    
    def getTimerLimit(self):
        return self.timerLimit

    def getOptTimeLimitReached(self):
        return self.optTimeLimitReached

    def getTimerValue(self):
        return self.timer
    
    def getDelta(self):
        return self.delta