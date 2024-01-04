import json, math
import copy
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM
import sim_utils as utils
from algorithms.multipleKS.quadTree import Point, QuadNode
import utm
from geopy import distance

def checkLatencyThreshold(user, cloudlet):
    return getLatency(user, cloudlet) <= user.latencyThresholdForAllocate

def getLatency(user, cloudlet):
    distance = utils.calcDistance((user.position[0], user.position[1]), 
                                        (cloudlet.position[0], cloudlet.position[1]))
    return distance * 0.001                                         

def normalize(cloudlet, vms):
    normalized = []
    for v in vms:
        # uId, vmType, bid, avgSpeed, initTime, route, reqs, position
        nUser = UserVM(v.uId, v.vmType, v.bid, v.avgSpeed, v.initTime,
            v.route, Resources(
            v.reqs.cpu/cloudlet.resourcesFullValues.cpu,
            v.reqs.ram/cloudlet.resourcesFullValues.ram,
            v.reqs.storage/cloudlet.resourcesFullValues.storage))
        nUser.position = v.position
        normalized.append(nUser)
    return normalized

def calcEfficiency(vms, normOption):
    if normOption == 'l2':
        return calcDensitiesBy_L2(vms)
    elif normOption == 'prioritize_cpu':
        return calcDensitiesByPrioritizing(vms, 'cpu')
    elif normOption == 'prioritize_ram':
        return calcDensitiesByPrioritizing(vms, 'ram')
    elif normOption == 'prioritize_storage':
        return calcDensitiesByPrioritizing(vms, 'storage')
    elif normOption == 'weighted_avg_l1':
        return calcDensitiesByWeightedAvg_L1(vms)
    elif normOption == 'weighted_avg_l2':
        return calcDensitiesByWeightedAvg_L2(vms)
    elif normOption == 'weighted_avg_max':
        return calcDensitiesByWeightedAvg_Max(vms)
    elif normOption == 'max':
        return calcDensitiesByMax(vms)
    elif normOption == 'sum':
        return calcDensitiesBySum(vms)

# Calculting densities by L2 norm
def calcDensitiesBy_L2(vms):
    dens = []
    for v in vms:
        v.normReq = math.sqrt(v.reqs.cpu**2 + v.reqs.ram**2 + v.reqs.storage**2)
        dens.append((v, v.bid/v.normReq))
    return dens

# Calculting densities by prioritizing one of the resources
def calcDensitiesByPrioritizing(vms, prioritizedResource):
    dens = []
    for v in vms:
        if prioritizedResource == 'cpu':
            v.normReq = v.reqs.cpu
        elif prioritizedResource == 'ram':
            v.normReq = v.reqs.ram
        elif prioritizedResource == 'storage':
            v.normReq = v.reqs.storage
        
        dens.append((v, v.bid/v.normReq))
    return dens

# Calculating densities by weighted average - l1 norm
def calcDensitiesByWeightedAvg_L1(vms):
    weights = [0.2864216034, 0.3472441883, 0.3663342083]
    dens = []
    for v in vms:
        v.normReq = (v.reqs.cpu*weights[0]
                            + v.reqs.ram*weights[1]
                            + v.reqs.storage*weights[2])
        dens.append((v, v.bid/v.normReq))
    return dens

# Calculating densities by weighted average - l2 norm
def calcDensitiesByWeightedAvg_L2(vms):
    weights = [0.2864216034, 0.3472441883, 0.3663342083]
    dens = []
    for v in vms:
        v.normReq = (math.sqrt(v.reqs.cpu**2)*weights[0] 
                         + math.sqrt(v.reqs.ram**2)*weights[1] 
                         + math.sqrt(v.reqs.storage**2)*weights[2])
        dens.append((v, v.bid/v.normReq))
    return dens

# Calculating densities by weighted average - max norm
# but the max must be calculated not using built-in max function
def calcDensitiesByWeightedAvg_Max(vms):
    weights = [0.2864216034, 0.3472441883, 0.3663342083]
    dens = []
    for v in vms:
        v.normReq = calcMax(v.reqs.cpu*weights[0], v.reqs.ram*weights[1], v.reqs.storage*weights[2])
        dens.append((v, v.bid/v.normReq))
    return dens

def calcMax(a, b, c):
    if a > b:
        if a > c:
            return a
        else:
            return c
    else:
        if b > c:
            return b
        else:
            return c

def calcDensitiesByMax(vms):
    dens = []
    for v in vms:
        v.normReq = calcMax(v.reqs.cpu, v.reqs.ram, v.reqs.storage)
        dens.append((v, v.bid/v.normReq))
    
    return dens

def calcDensitiesBySum(vms):
    dens = []
    for v in vms:
        v.normReq = (v.reqs.cpu + v.reqs.ram + v.reqs.storage)
        dens.append((v, v.bid/v.normReq))
    
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