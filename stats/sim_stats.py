import threading
from sim_entities.users import UsersListSingleton
from sim_entities.cloudlets import CloudletsListSingleton
import sim_utils as utils
import time
import csv
import numpy as np

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
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'number of winners', 'social welfare'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'number of winners': value[1], 'social welfare': value[2]})

    def writeFilePrice(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'number of winners', 'prices'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'number of winners': value[1], 'prices': value[2]})

    def writeFileCl(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'used cloudlets', 
                                                        'used cpu avg', 'used cpu std', 'unused cpu', 
                                                        'used storage avg', 'used storage std', 'unused storage', 
                                                        'used ram avg', 'used ram std', 'unused ram'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'used cloudlets': value[1], 
                                    'used cpu avg': value[2], 'used cpu std': value[3], 'unused cpu': value[4],
                                    'used storage avg': value[5], 'used storage std': value[6], 'unused storage': value[7],
                                    'used ram avg': value[8], 'used ram std': value[9], 'unused ram': value[10]})
    
    def writeFileExecTime(self, preTitle, fileName, dictRes):
        with open(f'{LOG_FOLDER + preTitle + fileName + CSV}', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['time-step', 'number of users', 'exec time'])
            writer.writeheader()
            for key, value in dictRes.items():
                writer.writerow({'time-step': key, 'number of users': value[0], 'exec time': value[1]})

    def writeReport(self, algorithm, nbUsers, instance):
        utils.log(TAG, 'writeReport')
        preTitle = f'alg{algorithm}-{nbUsers}users/'

        self.writeFileLat(preTitle, f'{LAT_FILENAME}_{algorithm}_{instance}', self.avgLatencies)
        self.writeFileSW(preTitle, f'{SOCIAL_WELFARE_FILENAME}_{algorithm}_{instance}', self.totalSocialWelfares)
        self.writeFilePrice(preTitle, f'{PRICES_FILENAME}_{algorithm}_{instance}', self.totalPrices)
        self.writeFileCl(preTitle, f'{CLOUDLETS_USAGE_FILENAME}_{algorithm}_{instance}', self.clUsages)
        self.writeFileExecTime(preTitle, f'{EXEC_TIME_FILENAME}_{algorithm}_{instance}', self.execTimes)


    def writeLatencyStats(self, timeStep, latencies):
        utils.log(TAG, 'writeLatencyStats')
        users = UsersListSingleton().getList()
        avgLatency = sum(latencies) / len(users)
        self.avgLatencies[timeStep] = (len(users), avgLatency)

    def writeSocialWelfareStats(self, timeStep, winners):
        utils.log(TAG, 'writeSocialWelfareStats')
        users = UsersListSingleton().getList()
        socialWelfare = sum([u.bid for u in winners])
        self.totalSocialWelfares[timeStep] = (len(users), len(winners), socialWelfare)

    def writePricesStats(self, timeStep, winners):
        utils.log(TAG, 'writePricesStats')
        users = UsersListSingleton().getList()
        prices = sum([u.price for u in winners])
        self.totalPrices[timeStep] = (len(users), len(winners), prices)

    def writeCloudletsUsageStats(self, timeStep):
        utils.log(TAG, 'writeCloudletsUsageStats')
        cloudlets = CloudletsListSingleton().getList()
        users = UsersListSingleton().getList()
        cpuUsage = []
        cpuUnused = []
        storageUsage = []
        storageUnused = []
        ramUsage = []
        ramUnused = []
        usedCloudlets = 0

        for c in cloudlets:
            # taking into account only the cloudlets that are being used
            if c.resources.cpu != c.resourcesFullValues.cpu or \
                c.resources.storage != c.resourcesFullValues.storage or \
                    c.resources.ram != c.resourcesFullValues.ram:
                usedCloudlets += 1
                
                usedCpu = c.resourcesFullValues.cpu - c.resources.cpu
                cpuUsage.append((usedCpu/c.resourcesFullValues.cpu) * 100)
                cpuUnused.append((c.resources.cpu/c.resourcesFullValues.cpu) * 100)

                usedStorage = c.resourcesFullValues.storage - c.resources.storage
                storageUsage.append((usedStorage/c.resourcesFullValues.storage) * 100)
                storageUnused.append((c.resources.cpu/c.resourcesFullValues.cpu) * 100)
                
                usedRam = c.resourcesFullValues.ram - c.resources.ram
                ramUsage.append((usedRam/c.resourcesFullValues.ram) * 100)
                ramUnused.append((c.resources.ram/c.resourcesFullValues.ram) * 100)
        
        self.clUsages[timeStep] = (len(users), usedCloudlets, np.mean(cpuUsage), np.std(cpuUsage), sum(cpuUnused),
                                                    np.mean(storageUsage), np.std(storageUsage), sum(storageUnused), 
                                                    np.mean(ramUsage), np.std(ramUsage), sum(ramUnused))
    
    def writeExecTimeStats(self, timeStep, execTime):
        utils.log(TAG, 'writeExecTimeStats')
        users = UsersListSingleton().getList()
        self.execTimes[timeStep] = (len(users), execTime)