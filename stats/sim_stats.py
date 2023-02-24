import threading

class SimStatistics:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def writeStats(time, content):
        # TODO: store the information in a variable
        pass

    def writeReport():
        # TODO: Write all the things in a file
        pass