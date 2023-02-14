import events
import stats
import TimerSingleton
import HeapSingleton

global heapQueue

def initialAllocation(graphs): # TODO: MAKE A METHOD TO UPDATE ALL GRAPHS WHEN ONE GETS MODIFIED
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, graphs)

def initRoutine(simClock, heapSing, graphs, statsStoring):    
    # initCloudlets(inGraph) # TODO: PHASE 2
    # initUsers(inGraph) # TODO: PHASE 2
    initialAllocation(graphs)
    timingRoutine(simClock, heapSing, statsStoring)

def initHeap():
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    simClock = TimerSingleton()
    return simClock

def timingRoutine(simClock, heapSing, statsStoring):
    nextEvent = heapSing.nextEvent()
    invokeRoutine(simClock, nextEvent, statsStoring)

def invokeRoutine(simClock, eTuple, statsStoring):
    simClock = eTuple[1]
    Event.executeEvent(simClock, eTuple)
    statsStoring.writeStats(simClock, eTuple)

def startSimulation(graphs):
    statsStoring = Stats()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(simClock, heapSing, graphs, statsStoring)
    while len(heapQueue) > 0:
        timingRoutine(simClock, heapSing, statsStoring)
    statsStoring.writeReport() # TODO

def main(graphs):
    # graphs[0] -> main graph / graphs[1] -> cloudlets subgraph / graphs[2] -> users' routes subgraphs
    startSimulation(graphs)