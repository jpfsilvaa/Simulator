import events
import stats
import TimerSingleton
import HeapSingleton
import GraphGen.instanceGen as instGen

def initialAllocation(graph):
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, (usersObjs, cloudletsObjs, graph))

def initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graphs, statsStoring):    
    # initCloudlets(inGraph) # TODO: PHASE 2
    # initUsers(inGraph) # TODO: PHASE 2
    initialAllocation(usersObjs, cloudletsObjs, graph)
    triggerUserPathEvents(usersObjs, cloudletsObjs, graph)
    triggerAllocClock()
    timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing, statsStoring)

def initHeap():
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    simClock = TimerSingleton()
    return simClock

def timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing, statsStoring):
    nextEvent = heapSing.nextEvent()
    invokeRoutine(usersObjs, cloudletsObjs, simClock, heapSing, nextEvent, statsStoring)

def invokeRoutine(usersObjs, cloudletsObjs, simClock, heapSing, eTuple, statsStoring):
    Event.executeEvent(simClock, heapSing, usersObjs, cloudletsObjs, eTuple)
    statsStoring.writeStats(usersObjs, cloudletsObjs, simClock.getTimerValue(), eTuple)

def triggerUserPathEvents(usersObjs, cloudletsObjs, graph):
    for u in usersObjs:
        userRouteNodes = [mainGraph.findNodeById(routeNode) for routeNode in u.route]
        currSg = mainGraph.getSubgraph(userRouteNodes)
        heapSing.insertEvent(calcTimeToExec(u, currSg, userRouteNodes[0]), Event.MOVE_USER, (usersObjs, cloudletsObjs, graphs))
        heapSing.insertEvent(calcTimeToExec(u, currSg, userRouteNodes[1]), Event.MOVE_USER, (usersObjs, cloudletsObjs, graphs))

def calcTimeToExec(user, routeSubgraph, destNode):
    distance = getDistSum(routeSubgraph, destNode)
    arrivalTime = distance // user.avgSpeed
    return arrivalTime + user.initTime

def getDistSum(routeSubgraph, destNode):
    distSum = 0
    cont = 0
    node = routeSubgraph.nodes[cont]
    while node.nId != destNode.nId:
        distSum += routeSubgraph.adjList[node.nId][destNode.nId]
        cont += 1
        node = routeSubgraph.nodes[cont]
    return distSum

def startSimulation(cloudletsObjs, users, graph):
    statsStoring = Stats()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graph, statsStoring)
    while len(heapQueue) > 0: # TODO: PHASE 2: Actually the end should be when there're no more users to move (MOVE_USER event)
        timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing, statsStoring)
    # statsStoring.writeReport() # TODO: PHASE 2

def main(jsonFilePath, graphFilePath):
    cloudletsObjs, usersObjs, graph = instGen.main(jsonFilePath, graphFilePath)
    startSimulation(cloudletsObjs, usersObjs, graphs)