from sim_entities.heap import HeapSingleton
from sim_entities.clock import TimerSingleton
from events.event import Event
from GraphGen import instanceGen as instGen
import sys

TAG = 'simMain'

def initialAllocation(heapSing, usersObjs, cloudletsObjs, graph):
    print(TAG, 'initialAllocation')
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, (usersObjs, cloudletsObjs, graph))

def initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graph):
    print(TAG, 'initRoutine')
    # initCloudlets(inGraph) # TODO: PHASE 2
    # initUsers(inGraph) # TODO: PHASE 2
    initialAllocation(heapSing, usersObjs, cloudletsObjs, graph)
    triggerUserPathEvents(heapSing, usersObjs, cloudletsObjs, graph)
    timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing)

def initHeap():
    print(TAG, 'initHeap')
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    print(TAG, 'initSimClock')
    simClock = TimerSingleton()
    return simClock

def timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing):
    print(TAG, 'timingRoutine')
    nextEvent = heapSing.nextEvent()
    invokeRoutine(usersObjs, cloudletsObjs, simClock, heapSing, nextEvent)

def invokeRoutine(usersObjs, cloudletsObjs, simClock, heapSing, eTuple):
    print(TAG, 'invokeRoutine')
    print("CALLING EVENT", eTuple[2])
    Event.execEvent(simClock, heapSing, usersObjs, cloudletsObjs, eTuple)
    # statsStoring.writeStats(usersObjs, cloudletsObjs, simClock.getTimerValue(), eTuple)

def triggerUserPathEvents(heapSing, usersObjs, cloudletsObjs, graph):
    print(TAG, 'triggerUserPathEvents')
    for u in usersObjs:
        userRouteNodes = [graph.findNodeById(routeNode) for routeNode in u.route]
        currSg = graph.getSubgraph(userRouteNodes)
        heapSing.insertEvent(calcTimeToExec(u, currSg, userRouteNodes[0]), Event.MOVE_USER, (u, userRouteNodes[0], graph))
        heapSing.insertEvent(calcTimeToExec(u, currSg, userRouteNodes[1]), Event.MOVE_USER, (u, userRouteNodes[1], graph))

def calcTimeToExec(user, routeSubgraph, destNode):
    print(TAG, 'calcTimeToExec')
    # TODO: USAR O GEOTOOLS (LIB DA LIB DO OSM)
    distance = getDistSum(routeSubgraph, destNode)
    arrivalTime = distance // user.avgSpeed
    return arrivalTime + user.initTime

def getDistSum(routeSubgraph, destNode):
    # todo: FIX
    print(TAG, 'getDistSum')
    distSum = 0
    cont = 0
    node = routeSubgraph.nodes[cont]
    while node.nId != destNode.nId:
        distSum += routeSubgraph.adjList[node.nId][destNode.nId]
        cont += 1
        node = routeSubgraph.nodes[cont]
    return distSum

def startSimulation(cloudletsObjs, usersObjs, graph):
    print(TAG, 'startSimulation')
    # statsStoring = Stats() TODO: PHASE 2
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graph)
    while heapSing.getHeapSize() > 0: # TODO: PHASE 2: Actually the end should be when there're no more users to move (MOVE_USER event)
        print('HEAP SIZE: ', heapSing.getHeapSize())
        timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing)
    # statsStoring.writeReport() # TODO: PHASE 2

def main(jsonFilePath, graphFilePath):
    print(TAG, 'main')
    cloudletsObjs, usersObjs, graph = instGen.main(jsonFilePath, graphFilePath)
    startSimulation(cloudletsObjs, usersObjs, graph)

if __name__ == '__main__':
    jsonFilePath = sys.argv[1:][0]
    graphFilePath = sys.argv[1:][1]
    main(jsonFilePath, graphFilePath)