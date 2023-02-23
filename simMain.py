from sim_entities.heap import HeapSingleton
from sim_entities.clock import TimerSingleton
from sim_entities.users import UsersListSingleton
from sim_entities.cloudlets import CloudletsListSingleton
from events.event import Event
from GraphGen import instanceGen as instGen
import sys

TAG = 'simMain.py:'

def initialAllocation(heapSing, graph):
    print(TAG, 'initialAllocation')
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, (graph))

def initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graph):
    print(TAG, 'initRoutine')
    initCloudlets(cloudletsObjs)
    initUsers(usersObjs)
    initialAllocation(heapSing, graph)
    triggerUserPathEvents(heapSing, graph)
    timingRoutine(simClock, heapSing)

def initCloudlets(cloudlets):
    clList = CloudletsListSingleton()
    for c in cloudlets:
        clList.insertCloudlet(c)

def initUsers(users):
    uList = UsersListSingleton()
    for u in users:
        uList.insertUser(u)

def initHeap():
    print(TAG, 'initHeap')
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    print(TAG, 'initSimClock')
    simClock = TimerSingleton()
    return simClock

def timingRoutine(simClock, heapSing):
    print(TAG, 'timingRoutine')
    nextEvent = heapSing.nextEvent()
    invokeRoutine(simClock, heapSing, nextEvent)

def invokeRoutine(simClock, heapSing, eTuple):
    print(TAG, 'invokeRoutine')
    print("CALLING EVENT", eTuple[2])
    Event.execEvent(simClock, heapSing, eTuple)
    # statsStoring.writeStats(usersObjs, cloudletsObjs, simClock.getTimerValue(), eTuple)

def triggerUserPathEvents(heapSing, graph):
    print(TAG, 'triggerUserPathEvents')
    for u in UsersListSingleton().getList():
        userRouteNodes = [graph.findNodeById(routeNode) for routeNode in u.route]
        heapSing.insertEvent(calcTimeToExec(u, u.route, graph, userRouteNodes[0]), 
                                        Event.MOVE_USER, (u, userRouteNodes[0], graph))
        heapSing.insertEvent(calcTimeToExec(u, u.route, graph, userRouteNodes[1]), 
                                        Event.MOVE_USER, (u, userRouteNodes[1], graph))

def calcTimeToExec(user, routeIds, mainGraph, destNode):
    print(TAG, 'calcTimeToExec')
    # TODO: USAR O GEOTOOLS (LIB DA LIB DO OSM)
    distance = getDistSum(routeIds, mainGraph, destNode)
    arrivalTime = distance // user.avgSpeed
    return arrivalTime + user.initTime

def getDistSum(routeIds, mainGraph, destNode):
    print(TAG, 'getDistSum')
    distSum = 0
    cont = 0
    while routeIds[cont] != destNode.nId:
        distSum += mainGraph.adjList[routeIds[cont]][routeIds[cont+1]]
        cont += 1
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