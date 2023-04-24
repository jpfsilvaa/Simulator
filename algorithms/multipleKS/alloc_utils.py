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
    distance = utils.calcDistance((user.position[0], user.position[1]), 
                                        (cloudlet.position[0], cloudlet.position[1]))
    return distance * 0.001 <= user.latencyThresholdForAllocate                                        

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

def buildQuadtree(cloudlets, vms):
    maxX = 112000
    maxY = 112000
    quadtree = QuadNode(maxX/2, maxY/2, maxX, maxY)
    for cloudlet in cloudlets:
        lat_, long_ = convertUTMtoLatLong(cloudlet.position)
        quadtree.insert(Point(lat_, long_, cloudlet))
    for vm in vms:
        lat_, long_ = convertUTMtoLatLong(vm.position)
        quadtree.insert(Point(lat_, long_, vm))
    return quadtree

def detectCloudletsFromQT(user, quadtree):
    cloudlets = []
    radius = user.latencyThresholdForAllocate * 1000
    print("Radius: ", radius)
    result = quadtree.query(user.position[0], user.position[1], radius)
    filteredResult = []
    for point in result:
        if isinstance(point.entity, Cloudlet):
            filteredResult.append(point)
    print("Cloudlets found: ", len(filteredResult))
    return filteredResult

def convertUTMtoLatLong(point):
    # Sao Paulo's zone number and zone letter
    zone_number = 23
    zone_letter = 'K'

    lat_, long_ = utm.to_latlon(point[0], point[1], zone_number, zone_letter)
    return lat_, long_