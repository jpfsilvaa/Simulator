import json, math
import copy
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM

""" class Resources:
    def __init__(self, cpu, ram, storage):
        self.cpu = cpu
        self.ram = ram
        self.storage = storage

class UserVM:
    def __init__(self, id, vmType, bid, reqs):
        self.id = id
        self.vmType = vmType
        self.bid = bid
        self.price = 0
        self.maxReq = 0
        self.reqs = reqs
        self.reqsSum = 0

class Cloudlet:
    def __init__(self, id, resources):
        self.id = id
        self.resources = resources """

def normalize(cloudlet, vms):
    normalized = []
    for v in vms:
        # uId, vmType, bid, avgSpeed, initTime, route, reqs
        normalized.append(UserVM(v.uId, v.vmType, v.bid, v.avgSpeed, v.initTime,
            v.route, Resources(
            v.reqs.cpu/cloudlet.resources.cpu,
            v.reqs.ram/cloudlet.resources.ram,
            v.reqs.storage/cloudlet.resources.storage
        )))
    return normalized

def calcDensitiesByMax(vms):
    dens = []
    for v in vms:
        v.maxReq = max(v.reqs.cpu, v.reqs.ram, v.reqs.storage)
        dens.append((v, v.bid/v.maxReq))
    
    return dens

def calcDensitiesBySum(vms):
    dens = []
    for v in vms:
        v.reqsSum = (v.reqs.cpu + v.reqs.ram + v.reqs.storage)
        dens.append((v, v.bid/v.reqsSum))
    
    return dens

def sortCloudletsByType(cloudlets, reverse):
    sortedCloudlets = copy.deepcopy(cloudlets)
    sortedCloudlets.sort(key=lambda x: x.cId, reverse=reverse)
    return sortedCloudlets

def userFits(user, occupation):
    return (user.reqs.cpu + occupation.cpu <= 1
            and user.reqs.ram + occupation.ram <= 1 
            and user.reqs.storage + occupation.storage <= 1)

def allocate(user, occupation):
    occupation.cpu += user.reqs.cpu
    occupation.ram += user.reqs.ram
    occupation.storage += user.reqs.storage

def isNotFull(occupation):
    return (occupation.cpu <= 1 and occupation.ram <= 1 
            and occupation.storage <= 1)

def readJSONData(jsonFilePath):
    jsonFile = open(jsonFilePath)
    data = json.load(jsonFile)
    jsonFile.close()
    return data

def buildCloudlet(jsonData):
    cloudlets = []
    for cloudlet in jsonData:
        cloudlets.append(Cloudlet(cloudlet['id'], 
                            Resources(int(cloudlet['c_CPU']), 
                            int(cloudlet['c_RAM']),
                            int(cloudlet['c_storage']))
                            )
                        )
    return cloudlets

def buildUserVms(jsonData):
    vmsList = []
    for user in jsonData:
        vmsList.append(UserVM(user['id'], user['vmType'], int(user['bid']),
                            Resources(int(user['v_CPU']), 
                            int(user['v_RAM']),
                            int(user['v_storage']))
                            )
                        )
    return vmsList