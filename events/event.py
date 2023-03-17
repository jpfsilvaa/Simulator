from enum import Enum
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM
from algorithms.multipleKS import greedyAlloc as alg
from OsmToRoadGraph.utils import geo_tools
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
from sim_entities.predictions import PredictionsSingleton
from prediction import AllocPrediction
import sim_utils as utils
import logging

TAG = 'event.py'

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    CALL_PRICE = 4

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
        elif eventType == Event.CALL_PRICE:
            pass # TODO: PHASE 3 or 4

def moveUser(heapSing, eTuple):
    utils.log(TAG, 'moveUser')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (User, idxFromRoute, graph)
    user = eTuple[3][0]
    idxFromRoute = eTuple[3][1]
    mainGraph = eTuple[3][2]
    user.currNode = user.route[idxFromRoute]
    user.currLatency = latencyFunction(user, mainGraph)
    idxFromRoute += 1
    
    if idxFromRoute >= len(user.route):
        UsersListSingleton().removeUser(user)
    else:
        userRouteNodes = [mainGraph.findNodeById(routeNode) for routeNode in user.route]
        heapSing.insertEvent(utils.calcTimeToExec(user, user.route, mainGraph, userRouteNodes[idxFromRoute]), 
                                        Event.MOVE_USER, (user, idxFromRoute, mainGraph))

def allocateUser(eTuple):
    utils.log(TAG, 'allocateUser')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (userId, cloudletId, graph)
    user = UsersListSingleton().findById(eTuple[3][0])
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
    user.pastCloudlets.append(oldCloudlet)

def latencyFunction(user, mainGraph):
    utils.log(TAG, 'latencyFunction')    
    distance = geo_tools.distance(mainGraph.findNodeById(user.currNodeId).posX, 
                                    mainGraph.findNodeById(user.currNodeId).posY, 
                                    mainGraph.findNodeById(user.allocatedCloudlet.nodeId).posX, 
                                    mainGraph.findNodeById(user.allocatedCloudlet.nodeId).posY)
    return distance * 0.01

def initialAlloc(simClock, heapSing, eTuple):
    utils.log(TAG, 'initialAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    result = alg.greedyAlloc(cloudletsSing.getList(), usersSing.getList())
    for allocs in result[1]:
        userId = allocs[0].uId
        cloudletId = allocs[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (eTuple[3]))

def optimizeAlloc(simClock, heapSing, eTuple):
    utils.log(TAG, 'optimizeAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()

    prediction = AllocPrediction(usersSing, cloudletsSing, eTuple[3])
    predictionRes = prediction.predictAll()
    # TODO: put that in the statistics log

    result = alg.greedyAlloc(cloudletsSing.getList(), usersSing.getList())
    PredictionsSingleton().storePredictions(simClock, predictionRes, result)
    # TODO: put that in the statistics log

    for alloc in result[1]:
        userId = alloc[0].uId
        cloudletId = alloc[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (eTuple[3]))