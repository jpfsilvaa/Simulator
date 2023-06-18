import threading

class UsersListSingleton:
    _instance = None
    _lock = threading.Lock()
    users = []
    usersNotStarted = {}
    subtraces = []

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def getList(self):
        return self.users

    def startUser(self, userId):
        user = self.usersNotStarted[userId]
        self.users.append(user)

    def insertUser(self, user):
        self.users.append(user)

    def removeUser(self, user):
        self.users.remove(user)

    def getUsersListSize(self):
        return len(self.users)

    def findById(self, uId):
        for u in self.users:
            if u.uId == uId:
                return u
        return None
    
    def currentUsers(self):
        return [u.uId for u in self.users]
    
    def insertSubtraces(self, subtraces):
        self.subtraces = subtraces
    
    def getSubtraces(self):
        return self.subtraces