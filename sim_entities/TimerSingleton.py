class TimerSingleton:
    _instance = None
    _lock = threading.Lock()
    timer = 0

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def incrementTimer(self, i = 1):
        self.timer += t
        return timer
    
    def getTimerValue(self):
        return self.timer