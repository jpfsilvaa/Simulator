import heapq
import threading
from events.event import Event

class HeapSingleton:
    _instance = None
    _lock = threading.Lock()
    heapQueue = []
    IDCounter = 0

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def insertEvent(self, time, event: Event, contentTuple):
        self.IDCounter += 1
        heapq.heappush(self.heapQueue, (time, self.IDCounter, event, contentTuple))

    def nextEvent(self):
        return heapq.heappop(self.heapQueue)

    def getHeapSize(self):
        return len(self.heapQueue)