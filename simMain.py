import events
import stats
import TimerSingleton
import HeapSingleton

global heapQueue

def initialAllocation(graphs): # TODO: MAKE A METHOD TO UPDATE ALL GRAPHS WHEN ONE GETS MODIFIED
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, graphs)

def initRoutine(users, cloudlets, simClock, heapSing, graphs, statsStoring):    
    # initCloudlets(inGraph) # TODO: PHASE 2
    # initUsers(inGraph) # TODO: PHASE 2
    initialAllocation(graphs)
    timingRoutine(users, cloudlets, simClock, heapSing, statsStoring)

def initHeap():
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    simClock = TimerSingleton()
    return simClock

def timingRoutine(users, cloudlets, simClock, heapSing, statsStoring):
    nextEvent = heapSing.nextEvent()
    invokeRoutine(users, cloudlets, simClock, nextEvent, statsStoring)

def invokeRoutine(users, cloudlets, simClock, eTuple, statsStoring):
    Event.executeEvent(users, cloudlets, eTuple)
    statsStoring.writeStats(users, cloudlets, simClock, eTuple)

def startSimulation(cloudlets, users, graphs):
    statsStoring = Stats()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(users, cloudlets, simClock, heapSing, graphs, statsStoring)
    while len(heapQueue) > 0:
        timingRoutine(users, cloudlets, simClock, heapSing, statsStoring)
    statsStoring.writeReport() # TODO

def main(cloudlets, users, graphs):
    # graphs[0] -> main graph / graphs[1] -> cloudlets subgraph / graphs[2] -> users' routes subgraphs
    startSimulation(cloudlets, users, graphs)