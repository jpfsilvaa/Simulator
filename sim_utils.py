from sim_entities.clock import TimerSingleton
import logging
import utm
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM
from geopy import distance
from algorithms.multipleKS.quadTree import Point, QuadNode

TAG = 'sim_utils.py'

def calcDistance(point_1, point_2):
    # Sao Paulo's zone number and zone letter
    zone_number = 23
    zone_letter = 'K'

    lat_1, long_1 = utm.to_latlon(point_1[0], point_1[1], zone_number, zone_letter)
    lat_2, long_2 = utm.to_latlon(point_2[0], point_2[1], zone_number, zone_letter)

    distanceRes = distance.distance((lat_1, long_1), (lat_2, long_2)).meters
    return distanceRes

def calcTimeToExec(user, mainGraph, destNode):
    log(TAG, 'calcTimeToExec')
    if user.currNodeId == destNode.nId:
        dist = 0
    else:
        dist = mainGraph.adjList[user.currNodeId][destNode.nId][0]
    arrivalTime = dist // user.avgSpeed
    return arrivalTime + user.lastMove[0]

def log(fileName, msg):
    logging.info(f'{fileName}: time-step:{TimerSingleton().getTimerValue()} {msg}')

def buildQuadtree(cloudlets, vms):
    maxX = 180
    maxY = 360
    quadtree = QuadNode(0, 0, maxX, maxY)
    for cloudlet in cloudlets:
        lat_, long_ = convertUTMtoLatLong(cloudlet.position)
        quadtree.insert(Point(lat_, long_, cloudlet))
    for vm in vms:
        lat_, long_ = convertUTMtoLatLong(vm.position)
        quadtree.insert(Point(lat_, long_, vm))
    return quadtree

def detectCloudletsFromQT(users, quadtree):
    finalResult = {}
    for user in users:
        cloudlets = []
        radius = user.latencyThresholdForAllocate * 1000
        lat_, long_ = convertUTMtoLatLong(user.position)
        result = quadtree.query(lat_, long_, radius)
        filteredResult = []
        for point in result:
            if isinstance(point.entity, Cloudlet):
                filteredResult.append(point)
        finalResult[user.uId] = filteredResult
    return finalResult

def detectCloudletsFromQT_(cloudlets, quadtree):
    finalResult = {}
    for cloudlet in cloudlets:
        cloudlets = []
        radius = cloudlet.coverageArea * 2
        lat_, long_ = convertUTMtoLatLong(cloudlet.position)
        result = quadtree.query(lat_, long_, radius)
        filteredResult = []
        for point in result:
            if isinstance(point.entity, Cloudlet):
                filteredResult.append(point.entity)
        finalResult[cloudlet.cId] = filteredResult
    return finalResult

def detectUsersFromQT(cloudlets, radius, quadtree):
    finalResult = {}
    for cloudlet in cloudlets:
        users = []
        lat_, long_ = convertUTMtoLatLong(cloudlet.position)
        result = quadtree.query(lat_, long_, radius)
        filteredResult = []
        for point in result:
            if isinstance(point.entity, UserVM):
                filteredResult.append(point.entity)
        finalResult[cloudlet.cId] = filteredResult
    return finalResult

def convertUTMtoLatLong(point):
    # Sao Paulo's zone number and zone letter
    zone_number = 23
    zone_letter = 'K'
    lat_, long_ = utm.to_latlon(point[0], point[1], zone_number, zone_letter)
    return lat_, long_