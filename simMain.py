import events
import stats
import TimerSingleton
import HeapSingleton

global heapQueue

def initialAllocation(graphs):
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, (usersObjs, cloudletsObjs, graphs))

def initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graphs, statsStoring):    
    # initCloudlets(inGraph) # TODO: PHASE 2
    # initUsers(inGraph) # TODO: PHASE 2
    initialAllocation(usersObjs, cloudletsObjs, graphs)
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
    statsStoring.writeStats(usersObjs, cloudletsObjs, simClock, eTuple)

def startSimulation(cloudletsObjs, users, graphs):
    statsStoring = Stats()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graphs, statsStoring)
    while len(heapQueue) > 0:
        timingRoutine(usersObjs, cloudletsObjs, simClock, heapSing, statsStoring)
    statsStoring.writeReport() # TODO

def main(cloudletsObjs, usersObjs, graphs):
    # graphs[0] -> main graph / graphs[1] -> cloudlets subgraph / graphs[2] -> users' routes subgraphs
    # TODO: CALL THE INSTANCE GENERATOR
    startSimulation(cloudletsObjs, usersObjs, graphs)