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

def initRoutine(usersObjs, cloudletsObjs, subtraces, simClock, heapSing, graph, algorithm):
    utils.log(TAG, 'initRoutine')
    initCloudlets(cloudletsObjs, algorithm)
    initUsers(usersObjs, subtraces)
    initialAllocation(heapSing, graph)
    triggerUserPathEvents(heapSing, graph)
    timingRoutine(simClock, heapSing)

def initCloudlets(cloudlets, algorithm):
    utils.log(TAG, 'initCloudlets')
    clList = CloudletsListSingleton()
    for c in cloudlets:
        clList.insertCloudlet(c)
    clList.setAlgorithm(algorithm)

def initUsers(users, subtraces):
    utils.log(TAG, 'initUsers')
    uList = UsersListSingleton()
    uList.insertSubtraces(subtraces)
    for u in users:
        if u.initTime == 0:
            uList.insertUser(u)
        else:
            uList.usersNotStarted[u.uId] = u

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
        heapSing.insertEvent(u.initTime, Event.MOVE_USER, (u, 0, graph))
    for u in UsersListSingleton().usersNotStarted.values():
        userRouteNodes = [graph.findNodeById(routeNode) for routeNode in u.route]
        heapSing.insertEvent(u.initTime, Event.MOVE_USER, (u, 0, graph))

def startSimulation(cloudletsObjs, usersObjs, graph, subtraces, algorithm, instance, iteration):
    utils.log(TAG, 'startSimulation')
    startTime = time.time()
    stats = SimStatistics()
    heapSing = initHeap()
    simClock = initSimClock()
    initRoutine(usersObjs, cloudletsObjs, subtraces, simClock, heapSing, graph, algorithm)
    while UsersListSingleton().getUsersListSize() > 0:
        if startTime + simClock.getTimerLimit() < time.time() or simClock.getOptTimeLimitReached():
            utils.log(TAG, 'SIMULATION TIME LIMIT REACHED!')
            endTime = time.time()
            print('SIMULATION TIME LIMIT REACHED FOR INSTANCE', instance, 'WITH ALGORITHM', algorithm, 'AND ITERATION', iteration)
            break
        utils.log(TAG, f'HEAP SIZE: {heapSing.getHeapSize()}')
        utils.log(TAG, f'HEAP: {heapSing.curretEventsOnHep()}')
        utils.log(TAG, f'USERS LIST SIZE: {UsersListSingleton().getUsersListSize()}')
        timingRoutine(simClock, heapSing)
    endTime = time.time()
    utils.log(TAG, 'SIMULATION FINISHED')
    utils.log(TAG, f'TOTAL TIME: {endTime - startTime}')
    print('SIMULATION FINISHED FOR INSTANCE', instance, 'WITH ALGORITHM', algorithm, 'AND ITERATION', iteration)
    stats.writeReport(algorithm, len(usersObjs), instance, iteration)

def main(jsonFilePath, graphFilePath, busFilePath, algorithm, instance, iteration):
    cloudletsObjs, usersObjs, graph, subtraces = instGen.main(jsonFilePath, graphFilePath, busFilePath)
    startSimulation(cloudletsObjs, usersObjs, graph, subtraces, algorithm, instance, iteration)

if __name__ == '__main__':
    algorithm = sys.argv[1:][0]
    nbUsers = sys.argv[1:][1]
    instance = sys.argv[1:][2]
    jsonFilePath = sys.argv[1:][3]
    graphFilePath = sys.argv[1:][4]
    busFilePath = sys.argv[1:][5]
    iteration = sys.argv[1:][6]
    filePath = f'/home/jps/GraphGenFrw/Simulator/logfiles/alg{algorithm}-{nbUsers}users/{iteration}/simulation_{algorithm}_{instance}.log'
    logging.basicConfig(filename=filePath, filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)
    main(jsonFilePath, graphFilePath, busFilePath, algorithm, instance, iteration)