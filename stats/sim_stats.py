import threading
from sim_entities.users import UsersListSingleton
from sim_entities.cloudlets import CloudletsListSingleton
import sim_utils as utils
import time
import csv

TAG = 'sim_stats.py'
LOG_FOLDER = '/home/jps/GraphGenFrw/Simulator/logfiles/'
LAT_FILENAME = 'latencies'
SOCIAL_WELFARE_FILENAME = 'social_welfare'
PRICES_FILENAME = 'prices'
CLOUDLETS_USAGE_FILENAME = 'cloudlets_usage'
EXEC_TIME_FILENAME = 'exec_time'
CSV = '.csv'

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

    def writeFileLat(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'avg latency (for the allocated)'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'avg latency (for the allocated)': value[1]})

    def writeFileSW(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'social welfare'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'social welfare': value})

    def writeFilePrice(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'prices'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'prices': value[1]})

    def writeFileCl(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'used cloudlets', 'used cpu', 'used storage', 'used ram'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'used cloudlets': value[1], 'used cpu': value[2][0], 'used storage': value[2][1], 'used ram': value[2][2]})
    
    def writeFileExecTime(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'exec time'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'exec time': value[1]})

    def writeReport(self, algorithm, nbUsers, instance):
        utils.log(TAG, 'writeReport')
        preTitle = f'alg{algorithm}-{nbUsers}users/'

        self.writeFileLat(preTitle, f'{LAT_FILENAME}_{instance}', self.avgLatencies)
        self.writeFileSW(preTitle, f'{SOCIAL_WELFARE_FILENAME}_{instance}', self.totalSocialWelfares)
        self.writeFilePrice(preTitle, f'{PRICES_FILENAME}_{instance}', self.totalPrices)
        self.writeFileCl(preTitle, f'{CLOUDLETS_USAGE_FILENAME}_{instance}', self.clUsages)
        self.writeFileExecTime(preTitle, f'{EXEC_TIME_FILENAME}_{instance}', self.execTimes)


    def writeLatencyStats(self, timeStep):
        utils.log(TAG, 'writeLatencyStats')
        users = UsersListSingleton().getList()
        avgLatency = sum([u.currLatency for u in users if u.currLatency < 1]) / len(users) # avgLatency only of the allocated users (<1)
        self.avgLatencies[timeStep] = (len(users), avgLatency)

    def writeSocialWelfareStats(self, timeStep, winners):
        utils.log(TAG, 'writeSocialWelfareStats')
        socialWelfare = sum([u.bid for u in winners])
        self.totalSocialWelfares[timeStep] = socialWelfare

    def writePricesStats(self, timeStep, winners):
        utils.log(TAG, 'writePricesStats')
        prices = sum([u.price for u in winners])
        self.totalPrices[timeStep] = (len(winners), prices)

    def writeCloudletsUsageStats(self, timeStep):
        utils.log(TAG, 'writeCloudletsUsageStats')
        cloudlets = CloudletsListSingleton().getList()
        users = UsersListSingleton().getList()
        cpuUsage = 0
        storageUsage = 0
        ramUsage = 0
        usedCloudlets = 0

        for c in cloudlets:
            # taking into account only the cloudlets that are being used
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