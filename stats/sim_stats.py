import threading
from sim_entities.users import UsersListSingleton
from sim_entities.cloudlets import CloudletsListSingleton
import sim_utils as utils
import time
import csv

TAG = 'sim_stats.py'
LOG_FOLDER = 'logfiles/'
LAT_FILENAME = 'latencies.csv'
SOCIAL_WELFARE_FILENAME = 'social_welfare.csv'
PRICES_FILENAME = 'prices.csv'
CLOUDLETS_USAGE_FILENAME = 'cloudlets_usage.csv'
EXEC_TIME_FILENAME = 'exec_time.csv'

class SimStatistics:
    _instance = None
    _lock = threading.Lock()
    
    avgLatencies = {}
    totalSocialWelfares = {}
    totalPrices = {}
    clUsages = {}
    execTimes = {}

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def writeFile(self, timeString, fileName, colunmName, dictRes):
        with open(f'{LOG_FOLDER + timeString}-{fileName}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', colunmName])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, colunmName: value})

    def writeReport(self):
        utils.log(TAG, 'writeReport')
        currTime = time.localtime()
        timeString = time.strftime("%d%m%Y_%H%M%S", currTime)

        self.writeFile(timeString, LAT_FILENAME, '(number of users, latencies)', self.avgLatencies)
        self.writeFile(timeString, SOCIAL_WELFARE_FILENAME, '(number of users, social welfare)', self.totalSocialWelfares)
        self.writeFile(timeString, PRICES_FILENAME, '(number of users, prices)', self.totalPrices)
        self.writeFile(timeString, CLOUDLETS_USAGE_FILENAME, '(number of users, used cloudlets, cloudlets usage)', self.clUsages)
        self.writeFile(timeString, EXEC_TIME_FILENAME, '(number of users, execution time)', self.execTimes)


    def writeLatencyStats(self, timeStep):
        utils.log(TAG, 'writeLatencyStats')
        users = UsersListSingleton().getList()
        avgLatency = sum([u.currLatency for u in users]) / len(users)
        self.avgLatencies[timeStep] = (len(users), avgLatency)

    def writeSocialWelfareStats(self, timeStep):
        utils.log(TAG, 'writeSocialWelfareStats')
        users = UsersListSingleton().getList()
        socialWelfare = sum([u.bid for u in users])
        self.totalSocialWelfares[timeStep] = (len(users), socialWelfare)

    def writePricesStats(self, timeStep):
        utils.log(TAG, 'writePricesStats')
        users = UsersListSingleton().getList()
        prices = sum([u.price for u in users])
        self.totalPrices[timeStep] = (len(users), prices)

    def writeCloudletsUsageStats(self, timeStep):
        utils.log(TAG, 'writeCloudletsUsageStats')
        cloudlets = CloudletsListSingleton().getList()
        users = UsersListSingleton().getList()
        cpuUsage = 0
        storageUsage = 0
        ramUsage = 0

        for c in cloudlets:
            # taking into account only the cloudlets that are being used
            usedCloudlets = 0
            if c.resources.cpu != c.resourcesFullValues.cpu or \
                c.resources.storage != c.resourcesFullValues.storage or \
                    c.resources.ram != c.resourcesFullValues.ram:
                usedCloudlets += 1
                cpuUsage += c.resources.cpu/c.resourcesFullValues.cpu * 100
                storageUsage += c.resources.storage/c.resourcesFullValues.storage * 100
                ramUsage += c.resources.ram/c.resourcesFullValues.ram * 100
        
        self.clUsages[timeStep] = (len(users), usedCloudlets, ( 100 - (cpuUsage / len(cloudlets)), 
                                    100 - (storageUsage / len(cloudlets)), 
                                    100 -(ramUsage / len(cloudlets))))
    
    def writeExecTimeStats(self, timeStep, execTime):
        utils.log(TAG, 'writeExecTimeStats')
        users = UsersListSingleton().getList()
        self.execTimes[timeStep] = (len(users), execTime)