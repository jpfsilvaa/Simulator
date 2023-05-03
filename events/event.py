from enum import Enum
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM
from algorithms.multipleKS import greedyAlloc as alg
from algorithms.multipleKS import greedyAlloc_old as alg_old
from algorithms.multipleKS import crossEdgePaper as crossEdgeAlg
from GraphGen.OsmToRoadGraph.utils import geo_tools
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
from sim_entities.predictions import PredictionsSingleton
from stats.sim_stats import SimStatistics
from sim_entities.clock import TimerSingleton
# from prediction import AllocPrediction
import sim_utils as utils
import logging
import time

TAG = 'event.py'

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    WRITE_STATISTICS = 4

    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    @classmethod
    def execEvent(self, simClock, heapSing, eTuple):
        utils.log(TAG, 'execEvent')
        eventType = eTuple[2]
        simClock.incrementTimer(eTuple[0])
        if eventType == Event.MOVE_USER:
            moveUser(heapSing, eTuple)
        elif eventType == Event.ALLOCATE_USER:
            allocateUser(eTuple)
        elif eventType == Event.INITIAL_ALLOCATION:
            optimizeAlloc(simClock, heapSing, eTuple)
        elif eventType == Event.CALL_OPT:
            optimizeAlloc(simClock, heapSing, eTuple)
        elif eventType == Event.WRITE_STATISTICS:
            writeStats(simClock, heapSing, eTuple)

def writeStats(simClock, heapSing, eTuple):
    utils.log(TAG, 'writeStats')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: ()
    stats = SimStatistics()
    stats.writeLatencyStats(eTuple[0])
    stats.writeSocialWelfareStats(eTuple[0])
    stats.writePricesStats(eTuple[0])
    stats.writeCloudletsUsageStats(eTuple[0])

def moveUser(heapSing, eTuple):
    utils.log(TAG, 'moveUser')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (User, idxFromRoute, graph)
    user = eTuple[3][0]
    idxFromRoute = eTuple[3][1]
    mainGraph = eTuple[3][2]
    user.lastMove = (TimerSingleton().getTimerValue(), user.currNodeId)
    user.avgSpeed = getAvgSpeed(user.currNodeId, user.route[idxFromRoute], mainGraph)
    user.currNodeId = user.route[idxFromRoute]
    user.currLatency = latencyFunction(user, mainGraph)
    idxFromRoute += 1
    
    if idxFromRoute >= len(user.route):
        UsersListSingleton().removeUser(user)
    else:
        userRouteNodes = [mainGraph.findNodeById(routeNode) for routeNode in user.route]
        heapSing.insertEvent(utils.calcTimeToExec(user, mainGraph, userRouteNodes[idxFromRoute]), 
                                        Event.MOVE_USER, (user, idxFromRoute, mainGraph))

def getAvgSpeed(dest, src, mainGraph):
    DEFAULT_SPEED = 16
    if dest == src:
        return DEFAULT_SPEED
    else:
        return mainGraph.getEdgeWeight(dest, src)[1]

def allocateUser(eTuple):
    utils.log(TAG, 'allocateUser')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (userId, cloudletId, graph)
    
    # If the user is not in the list, he means that it has already finished its route
    user = UsersListSingleton().findById(eTuple[3][0])
    if user != None:
        oldCloudlet = user.allocatedCloudlet
        newCloudlet = CloudletsListSingleton().findById(eTuple[3][1])
        
        if oldCloudlet != None: # first allocation
            oldCloudlet.resources.cpu += user.reqs.cpu
            oldCloudlet.resources.ram += user.reqs.ram
            oldCloudlet.resources.storage += user.reqs.storage
            oldCloudlet.currUsersAllocated.remove(user)

        newCloudlet.resources.cpu -= user.reqs.cpu
        newCloudlet.resources.ram -= user.reqs.ram
        newCloudlet.resources.storage -= user.reqs.storage
        newCloudlet.currUsersAllocated.append(user)

        user.allocatedCloudlet = newCloudlet
        user.latency = latencyFunction(user, eTuple[3][2])
        utils.log(TAG, f'ALLOCATED USER LATENCY: {user.uId}: {user.latency}')
        user.pastCloudlets.append(oldCloudlet)
    else:
        utils.log(TAG, f'User {eTuple[3][0]} has already finished its route')

def latencyFunction(user, mainGraph):
    utils.log(TAG, 'latencyFunction')
    if user.allocatedCloudlet == None: 
        return 30
    else: 
        userCurrPosition = findUserPosition(user, mainGraph)
        distance = utils.calcDistance((userCurrPosition[0], userCurrPosition[1]), 
                                            (user.allocatedCloudlet.position[0], user.allocatedCloudlet.position[1]))        
        return distance * 0.001

def findUserPosition(user, mainGraph):
    utils.log(TAG, 'findUserPosition')
    deltaTime = TimerSingleton().getTimerValue() - user.lastMove[0]
    if deltaTime >= 0 and user.lastMove[1] != user.currNodeId:
        distance = user.avgSpeed * deltaTime
        jumpsToSubPoints = int(distance/50) # 50m is the aproximated distance between subpoints
        currLinkId = f'{user.lastMove[1]}-{user.currNodeId}'
        currSubtrace = UsersListSingleton().getSubtraces()[currLinkId]
        if jumpsToSubPoints >= len(currSubtrace): jumpsToSubPoints = len(currSubtrace) - 1
        return (float(currSubtrace[jumpsToSubPoints][0]), float(currSubtrace[jumpsToSubPoints][1]))
    else: 
        # user haven't move yet
        return (mainGraph.findNodeById(user.currNodeId).posX, mainGraph.findNodeById(user.currNodeId).posY)

def resetUserPrices():
    for u in UsersListSingleton().getList():
        u.price = 0

def detectAllUsersPosition(mainGraph):
    for u in UsersListSingleton().getList():
        u.position = findUserPosition(u, mainGraph)

def optimizeAlloc(simClock, heapSing, eTuple):
    utils.log(TAG, 'optimizeAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    detectAllUsersPosition(eTuple[3])
    
    # Pre-processing quadtree
    quadtree = utils.buildQuadtree(cloudletsSing.getList(), usersSing.getList())
    detectedCloudletsPerUser = utils.detectCloudletsFromQT(usersSing.getList(), quadtree) # dict: uId -> list of cloudlets

    startTime = time.time()
    result = alg.greedyAlloc(cloudletsSing.getList(), usersSing.getList(), detectedCloudletsPerUser)
    # result = alg_old.greedyAlloc(cloudletsSing.getList(), usersSing.getList())
    # result = crossEdgeAlg.crossEdgeAlg(cloudletsSing.getList(), usersSing.getList())
    endTime = time.time()
    SimStatistics().writeExecTimeStats(simClock.getTimerValue() + 1, (endTime - startTime))

    quadtree = None
    detectedCloudletsPerUser = None
    
    resetUserPrices()
    userPrices = alg.pricing(result[1], cloudletsSing.getList())
    for up in userPrices:
        user = usersSing.findById(up.uId)
        user.price = up.price

    for alloc in result[1]:
        userId = alloc[0].uId
        cloudletId = alloc[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)

    heapSing.insertEvent(simClock.getTimerValue() + 1, Event.WRITE_STATISTICS, ())
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (eTuple[3]))