from enum import Enum
from GraphGen.classes.cloudlet import Cloudlet
from GraphGen.classes.resources import Resources
from GraphGen.classes.user import UserVM
from algorithms.multipleKS import greedyAlloc as alg
from OsmToRoadGraph.utils import geo_tools
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton

TAG = 'event.py:'

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    CALL_PRICE = 4

    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    @classmethod
    def execEvent(self, simClock, heapSing, eTuple):
        print(TAG, 'execEvent')
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
    print(TAG, 'moveUser')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (User, Node, graph)
    user = eTuple[3][0]
    Node = eTuple[3][1]
    user.currNode = Node
    user.currLatency = latencyFunction(user, eTuple[3][2])
    # TODO: TRIGGER ONE MORE MOVE_USER EVENT FOR THIS USER

def allocateUser(eTuple):
    print(TAG, 'allocateUser')
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

def latencyFunction(user, mainGraph):
    print(TAG, 'latencyFunction')    
    print(user.description)
    distance = geo_tools.distance(mainGraph.findNodeById(user.currNodeId).posX, 
                                    mainGraph.findNodeById(user.currNodeId).posY, 
                                    mainGraph.findNodeById(user.allocatedCloudlet.nodeId).posX, 
                                    mainGraph.findNodeById(user.allocatedCloudlet.nodeId).posY)
    return distance * 0.01

def initialAlloc(simClock, heapSing, eTuple):
    print(TAG, 'initialAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    result = alg.greedyAlloc(cloudletsSing.getList(), usersSing.getList())
    for allocs in result[1]:
        userId = allocs[0].uId
        cloudletId = allocs[1].cId
        eventSubtuple = (userId, cloudletId, eTuple[3][0])
        heapSing.insertEvent(simClock.getTimerValue(), Event.ALLOCATE_USER, eventSubtuple)
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (graph))

def optimizeAlloc(simClock, eTuple):
    print(TAG, 'optimizeAlloc')
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graph)
    usersSing = UsersListSingleton()
    cloudletsSing = CloudletsListSingleton()
    result = alg.greedyAlloc(cloudletsSing.getList(), usersSing.getList())
    for alloc in result[1]:
        userId = alloc[0].uId
        cloudletId = alloc[1].cId
        eventSubtuple = (userId, cloudletId, eTuple)
        heapSing.insertEvent(simClock.getTimetValue(), Event.ALLOCATE_USER, eventSubtuple)
    heapSing.insertEvent(simClock.getTimerValue() + simClock.getDelta(), Event.CALL_OPT, (graph))