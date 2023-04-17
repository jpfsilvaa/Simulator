from sim_entities.heap import HeapSingleton
from sim_entities.clock import TimerSingleton
from events.event import Event
from GraphGen import instanceGen as instGen
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
from stats.sim_stats import SimStatistics
import sim_utils as utils
import sys
import time
import logging

TAG = 'simMain.py'

def initialAllocation(heapSing, graph):
    utils.log(TAG, 'initialAllocation')
    heapSing.insertEvent(0, Event.INITIAL_ALLOCATION, (graph))

def initRoutine(usersObjs, cloudletsObjs, subtraces, simClock, heapSing, graph):
    utils.log(TAG, 'initRoutine')
    initCloudlets(cloudletsObjs)
    initUsers(usersObjs, subtraces)
    initialAllocation(heapSing, graph)
    triggerUserPathEvents(heapSing, graph)
    timingRoutine(simClock, heapSing)

def initCloudlets(cloudlets):
    utils.log(TAG, 'initCloudlets')
    clList = CloudletsListSingleton()
    for c in cloudlets:
        clList.insertCloudlet(c)

def initUsers(users, subtraces):
    utils.log(TAG, 'initUsers')
    uList = UsersListSingleton()
    uList.insertSubtraces(subtraces)
    for u in users:
        uList.insertUser(u)

def initHeap():
    utils.log(TAG, 'initHeap')
    heapSing = HeapSingleton()
    return heapSing

def initSimClock():
    utils.log(TAG, 'initSimClock')
    simClock = TimerSingleton()
    return simClock

def timingRoutine(simClock, heapSing):
    utils.log(TAG, 'timingRoutine')
    nextEvent = heapSing.nextEvent()
    invokeRoutine(simClock, heapSing, nextEvent)

def invokeRoutine(simClock, heapSing, eTuple):
    utils.log(TAG, 'invokeRoutine')
    utils.log(TAG, f"CALLING EVENT  {eTuple[2]}")
    Event.execEvent(simClock, heapSing, eTuple)

def triggerUserPathEvents(heapSing, graph):
    utils.log(TAG, 'triggerUserPathEvents')
    for u in UsersListSingleton().getList():
        userRouteNodes = [graph.findNodeById(routeNode) for routeNode in u.route]
        heapSing.insertEvent(utils.calcTimeToExec(u, graph, userRouteNodes[0]), 
                                        Event.MOVE_USER, (u, 0, graph))

def startSimulation(cloudletsObjs, usersObjs, graph, subtraces):
    utils.log(TAG, 'startSimulation')
    startTime = time.time()
    stats = SimStatistics()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, subtraces, simClock, heapSing, graph)
    while UsersListSingleton().getUsersListSize() > 0:
        utils.log(TAG, f'HEAP SIZE: {heapSing.getHeapSize()}')
        utils.log(TAG, f'HEAP: {heapSing.curretEventsOnHep()}')
        utils.log(TAG, f'USERS LIST SIZE: {UsersListSingleton().getUsersListSize()}')
        timingRoutine(simClock, heapSing)
    endTime = time.time()
    utils.log(TAG, 'SIMULATION FINISHED')
    utils.log(TAG, f'TOTAL TIME: {endTime - startTime}')
    stats.writeReport()

def main(jsonFilePath, graphFilePath):
    utils.log(TAG, 'main')
    cloudletsObjs, usersObjs, graph, subtraces = instGen.main(jsonFilePath, graphFilePath)    
    startSimulation(cloudletsObjs, usersObjs, graph, subtraces)

if __name__ == '__main__':
    jsonFilePath = sys.argv[1:][0]
    graphFilePath = sys.argv[1:][1]
    logging.basicConfig(filename='logfiles/simulation.log', filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)
    main(jsonFilePath, graphFilePath)