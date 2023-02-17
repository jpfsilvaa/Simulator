from enum import Enum
import classes
import Algorithms.multipleKS as algs

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    CALL_PRICE = 4

    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    @classmethod
    def executeEvent(simClock, heapSing, users, cloudlets, eTuple):
        eventType = eTuple[2]
        if eventType == Event.MOVE_USER:
            moveUser(users, cloudlets, eTuple)
        elif eventType == Event.ALLOCATE_USER:
            allocateUser(eTuple)
        elif eventType == Event.INITIAL_ALLOCATION:
            initialAlloc(simClock, heapSing, users, cloudlets, eTuple)
        elif eventType == Event.CALL_OPT:
            optimizeAlloc(simClock, heapSing, users, cloudlets, eTuple)
        elif eventType == Event.CALL_PRICE:
            pass

def moveUser(users, cloudlets, eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (User, Node, graphs)
    user = eTuple[3][0]
    Node = eTuple[3][1]
    user.currNode = Node
    user.currLatency = latencyFunction(user, eTuple[3][2][0])

def latencyFunction(user, mainGraph):
    # TODO: vou precisar descobrir como saber a distancia fisica do mapa entre os nós (não necessariamente pelos arcos...)
    distance = checkDistance(user.currNode, user.allocatedCloudlet, mainGraph)
    return distance * 0.01

def allocateUser(eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (User, Cloudlet, graphs)
    user = eTuple[3][0]
    oldCloudlet = user.allocatedCloudlet
    newCloudlet = eTuple[3][1]
    
    oldCloudlet.resources.cpu += user.reqs.cpu
    oldCloudlet.resources.ram += user.reqs.ram
    oldCloudlet.resources.storage += user.reqs.storage
    oldCloudlet.currUsersAllocated.remove(user)

    newCloudlet.resources.cpu -= user.reqs.cpu
    newCloudlet.resources.ram -= user.reqs.ram
    newCloudlet.resources.storage -= user.reqs.storage
    newCloudlet.currUsersAllocated.append(user)

    user.latency = latencyFunction(user, eTuple[3][2][0])
    user.allocatedCloudlet = newCloudlet

def initialAlloc(simClock, heapSing, usersObjs, cloudletsObjs, eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graphs)
    result = algs.greedyAlloc(cloudletsObjs, usersObjs)
    for alloc in result[1]:
        user = alloc[0]
        cloudlet = alloc[1]
        eventSubtuple = (user, cloudlet, eTuple)
        heapSing.insertEvent(simClock, Event.ALLOCATE_USER, eventSubtuple)

def optimizeAlloc(simClock, usersObjs, cloudletsObjs, eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (graphs)
    result = algs.greedyAlloc(cloudletsObjs, usersObjs)
    for alloc in result[1]:
        user = alloc[0]
        cloudlet = alloc[1]
        eventSubtuple = (user, cloudlet, eTuple)
        heapSing.insertEvent(simClock, Event.ALLOCATE_USER, eventSubtuple)

def checkDistance(srcNodeID, dstNodeID, graph):
    # TODO
    return 1