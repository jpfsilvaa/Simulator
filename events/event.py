from enum import Enum
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM

from algorithms.multipleKS import greedyAlloc_QT as g_QT
from algorithms.multipleKS import greedyAlloc_noQT as g_noQT
from algorithms.multipleKS import crossEdgePaper_QT as crossEdge_QT
from algorithms.multipleKS import crossEdgePaper_noQT as crossEdge_noQT
from algorithms.multipleKS import twoPhases as twoPhases
from algorithms.multipleKS import lp_alloc_mult as exact
from prediction.pred_methods import hedge_ as hedgePrediction

from GraphGen.OsmToRoadGraph.utils import geo_tools
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
from sim_entities.predictions import PredictionsSingleton
from stats.sim_stats import SimStatistics
from sim_entities.clock import TimerSingleton
import sim_utils as utils
import logging
import time
import random

TAG = 'event.py'

GREEDY_QT = 0
GREEDY_NO_QT = 1
CROSS_EDGE_QT = 2
CROSS_EDGE_NO_QT = 3
TWO_PHASES = 4
PRED_TCHAPEU = 5
PRED_TCHAPEU_DISC = 6
PRED_HEDGE = 7
EXACT = 8

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
            initialAlloc(simClock, heapSing, eTuple)
        elif eventType == Event.CALL_OPT:
            optimizeAlloc(simClock, heapSing, eTuple)
        elif eventType == Event.WRITE_STATISTICS:
            writeStats(simClock, heapSing, eTuple)

def writeStats(simClock, heapSing, eTuple):
    utils.log(TAG, 'writeStats')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (winners, execution time)
    stats = SimStatistics()
    stats.writeLatencyStats(eTuple[0])
    stats.writeSocialWelfareStats(eTuple[0], eTuple[3][0])
    stats.writeExecTimeStats(eTuple[0], eTuple[3][1])
    stats.writePricesStats(eTuple[0], eTuple[3][0])
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
        removeUser(user)
    else:
        userRouteNodes = [mainGraph.findNodeById(routeNode) for routeNode in user.route]
        heapSing.insertEvent(utils.calcTimeToExec(user, mainGraph, userRouteNodes[idxFromRoute]), 
                                        Event.MOVE_USER, (user, idxFromRoute, mainGraph))

def removeUser(user):
    if user.allocatedCloudlet != None:
        CloudletsListSingleton().findById(user.allocatedCloudlet.cId).resources.cpu += user.reqs.cpu
        CloudletsListSingleton().findById(user.allocatedCloudlet.cId).resources.ram += user.reqs.ram
        CloudletsListSingleton().findById(user.allocatedCloudlet.cId).resources.storage += user.reqs.storage
        CloudletsListSingleton().findById(user.allocatedCloudlet.cId).currUsersAllocated.remove(user)
    UsersListSingleton().removeUser(user)

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
        if oldCloudlet != None:
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
    
    algorithm = cloudletsSing.getAlgorithm()
    quadtree = utils.buildQuadtree(cloudletsSing.getList(), usersSing.getList())

    startTime = time.time()
    if (algorithm == PRED_HEDGE or algorithm == PRED_TCHAPEU or algorithm == PRED_TCHAPEU_DISC) and TimerSingleton().getTimerValue() <= 121:
        result = randomAlloc(quadtree)
    else:
        result = allocationAlgorithm(cloudletsSing.getList(), usersSing.getList(), algorithm, quadtree)
    endTime = time.time()
    
    resetUserPrices()
    userPrices = pricingAlgorithm(result[1], usersSing.getList(), cloudletsSing.getList(), algorithm, quadtree)

    for up in userPrices:
        user = usersSing.findById(up[0].uId)
        user.price = up[0].price

    for alloc in result[1]:
        userId = alloc[0].uId
        cloudletId = alloc[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)

    heapSing.insertEvent(simClock.getTimerValue() + 1, Event.WRITE_STATISTICS, ([winner[0] for winner in result[1]], (endTime - startTime)))
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (eTuple[3]))

def initialAlloc(simClock, heapSing, eTuple):
    utils.log(TAG, 'optimizeAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    detectAllUsersPosition(eTuple[3])
    
    algorithm = cloudletsSing.getAlgorithm()
    quadtree = utils.buildQuadtree(cloudletsSing.getList(), usersSing.getList())

    startTime = time.time()
    if algorithm == PRED_HEDGE or algorithm == PRED_TCHAPEU or algorithm == PRED_TCHAPEU_DISC:
        result = randomAlloc(quadtree)
    else:
        result = allocationAlgorithm(cloudletsSing.getList(), usersSing.getList(), algorithm, quadtree)
    endTime = time.time()
    
    resetUserPrices()
    userPrices = pricingAlgorithm(result[1], usersSing.getList(), cloudletsSing.getList(), algorithm, quadtree)

    for up in userPrices:
        user = usersSing.findById(up[0].uId)
        user.price = up[0].price

    for alloc in result[1]:
        userId = alloc[0].uId
        cloudletId = alloc[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)

    heapSing.insertEvent(simClock.getTimerValue() + 1, Event.WRITE_STATISTICS, ([winner[0] for winner in result[1]], (endTime - startTime)))
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (eTuple[3]))

def randomAlloc(quadtree):
    utils.log(TAG, 'randomAlloc')
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    result = []
    detectedCloudletsPerUser = utils.detectCloudletsFromQT(usersSing.getList(), quadtree)
    for u in usersSing.getList():
        randomCloudlet = random.choice([p.entity for p in detectedCloudletsPerUser[u.uId]])
        result.append((u, randomCloudlet))
    return [0, result]

def allocationAlgorithm(cloudlets, users, algorithm, quadtree):
    utils.log(TAG, 'allocationAlgorithm')
    detectedCloudletsPerUser = utils.detectCloudletsFromQT(users, quadtree) # dict: uId -> list of cloudlets

    if algorithm == GREEDY_QT:
        return g_QT.greedyAlloc(cloudlets, users, detectedCloudletsPerUser)
    elif algorithm == GREEDY_NO_QT:
        return g_noQT.greedyAlloc(cloudlets, users)
    elif algorithm == CROSS_EDGE_QT:
        return crossEdge_QT.crossEdgeAlg(cloudlets, users, detectedCloudletsPerUser)
    elif algorithm == CROSS_EDGE_NO_QT:
        return crossEdge_noQT.crossEdgeAlg(cloudlets, users)
    elif algorithm == TWO_PHASES:
        detectedUsersPerCloudlet = utils.detectUsersFromQT(cloudlets, cloudlets[0].coverageArea, quadtree) # dict: cId -> list of users
        return twoPhases.twoPhasesAlloc(cloudlets, users, detectedUsersPerCloudlet)
    elif algorithm == EXACT:
        return exact.build(cloudlets, users)
    elif algorithm == PRED_TCHAPEU:
        pass
    elif algorithm == PRED_TCHAPEU_DISC:
        pass
    elif algorithm == PRED_HEDGE:
        detectedCloudletsPerCloudlet = utils.detectCloudletsFromQT_(cloudlets, quadtree) # dict: cId -> list of cloudlets
        predResult = []
        for c in cloudlets:
            usersInC = currentUsersInC(users, c)
            if len(usersInC) > 0:
                predResult += hedgePrediction.hedgeAlg(c, cloudlets, usersInC, 
                                        int(TimerSingleton().getTimerValue()/TimerSingleton().getDelta()), 
                                        detectedCloudletsPerCloudlet)
        utils.log(TAG, 'TOTAL USERS ALLOCATEC BY THE PREDICTION ALGORITHM: ' + str(len(predResult)))
        utils.log(TAG, f'USERS ALLOCATED BY THE PREDICTION ALGORITHM: {predResult}')
        return [0, predResult]

def currentUsersInC(users, c):
    result = []
    for u in users:
        if u.allocatedCloudlet.cId == c.cId:
            result.append(u)
    return result

def pricingAlgorithm(winners, users, cloudlets, algorithm, quadtree):
    detectedUsersPerCloudlet = utils.detectUsersFromQT(cloudlets, cloudlets[0].coverageArea, quadtree) # dict: cId -> list of users
    detectedCloudletsPerUser = utils.detectCloudletsFromQT(users, quadtree) # dict: uId -> list of cloudlets
    if algorithm == GREEDY_QT or algorithm == TWO_PHASES \
        or algorithm == PRED_TCHAPEU or algorithm == PRED_TCHAPEU_DISC \
        or algorithm == PRED_HEDGE:
        return g_QT.pricing(winners, users, detectedCloudletsPerUser, cloudlets)
    elif algorithm == EXACT:
        return winners
    elif algorithm == GREEDY_NO_QT:
        return g_noQT.pricing(winners, users, cloudlets)
    elif algorithm == CROSS_EDGE_QT:
        return crossEdge_QT.pricing(winners, users, detectedUsersPerCloudlet, cloudlets)
    elif algorithm == CROSS_EDGE_NO_QT:
        return crossEdge_noQT.pricing(winners, users, cloudlets)