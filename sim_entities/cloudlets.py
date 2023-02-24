import threading

class CloudletsListSingleton:
    _instance = None
    _lock = threading.Lock()
    cloudlets = []

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def getList(self):
        return self.cloudlets
    
    def insertCloudlet(self, cloudlet):
        self.cloudlets.append(cloudlet)

    def removeCloudlet(self, cloudlet):
        self.cloudlets.remove(cloudlet)

    def getCloudletsListSize(self):
        return len(self.cloudlets)

    def findById(self, cId):
        for c in self.cloudlets:
            if c.cId == cId:
                return c
        return None
    
    def currentCloudlets(self):
        return [c.cId for c in self.cloudlets]