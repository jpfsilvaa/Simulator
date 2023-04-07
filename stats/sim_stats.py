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

class SimStatistics:
    _instance = None
    _lock = threading.Lock()
    
    avgLatencies = {}
    totalSocialWelfares = {}
    totalPrices = {}
    clUsages = {}

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

        self.writeFile(timeString, LAT_FILENAME, 'latencies', self.avgLatencies)
        self.writeFile(timeString, SOCIAL_WELFARE_FILENAME, 'social welfare', self.totalSocialWelfares)
        self.writeFile(timeString, PRICES_FILENAME, 'prices', self.totalPrices)
        self.writeFile(timeString, CLOUDLETS_USAGE_FILENAME, 'cloudlets usage', self.clUsages) #TEST

    def writeLatencyStats(self, timeStep):
        utils.log(TAG, 'writeLatencyStats')
        users = UsersListSingleton().getList()
        avgLatency = sum([u.currLatency for u in users]) / len(users)
        self.avgLatencies[timeStep] = avgLatency

    def writeSocialWelfareStats(self, timeStep):
        utils.log(TAG, 'writeSocialWelfareStats')
        users = UsersListSingleton().getList()
        socialWelfare = sum([u.bid for u in users])
        self.totalSocialWelfares[timeStep] = socialWelfare

    def writePricesStats(self, timeStep):
        utils.log(TAG, 'writePricesStats')
        users = UsersListSingleton().getList()
        prices = sum([u.price for u in users])
        self.totalPrices[timeStep] = prices

    def writeCloudletsUsageStats(self, timeStep):
        utils.log(TAG, 'writeCloudletsUsageStats')
        cloudlets = CloudletsListSingleton().getList()
        cpuUsage = 0
        storageUsage = 0
        ramUsage = 0

        for c in cloudlets:
            cpuUsage += c.resources.cpu/c.resourcesFullValues.cpu * 100
            storageUsage += c.resources.storage/c.resourcesFullValues.storage * 100
            ramUsage += c.resources.ram/c.resourcesFullValues.ram * 100
        
        self.clUsages[timeStep] = ( 100 - (cpuUsage / len(cloudlets)), 
                                    100 - (storageUsage / len(cloudlets)), 
                                    100 -(ramUsage / len(cloudlets)))
            