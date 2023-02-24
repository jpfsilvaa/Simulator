from sim_entities.heap import HeapSingleton
from sim_entities.clock import TimerSingleton
from events.event import Event
from GraphGen import instanceGen as instGen
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
import sim_utils as utils
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
        heapSing.insertEvent(utils.calcTimeToExec(u, u.route, graph, userRouteNodes[0]), 
                                        Event.MOVE_USER, (u, 0, graph))

def startSimulation(cloudletsObjs, usersObjs, graph):
    print(TAG, TimerSingleton().getTimerValue() + 'startSimulation')
    # statsStoring = Stats() TODO: PHASE 2
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, simClock, heapSing, graph)
    while UsersListSingleton().getUsersListSize() > 0:
        print('HEAP SIZE: ', heapSing.getHeapSize())
        print('USERS LIST SIZE: ', UsersListSingleton().getUsersListSize())
        timingRoutine(simClock, heapSing)
    print('SIMULATION FINISHED')
    # statsStoring.writeReport() # TODO: PHASE 2

def main(jsonFilePath, graphFilePath):
    print(TAG, 'main')
    cloudletsObjs, usersObjs, graph = instGen.main(jsonFilePath, graphFilePath)
    startSimulation(cloudletsObjs, usersObjs, graph)

if __name__ == '__main__':
    jsonFilePath = sys.argv[1:][0]
    graphFilePath = sys.argv[1:][1]
    main(jsonFilePath, graphFilePath)