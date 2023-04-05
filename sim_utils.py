from sim_entities.clock import TimerSingleton
import logging

TAG = 'sim_utils.py'

def calcTimeToExec(user, routeIds, mainGraph, destNode):
    log(TAG, 'calcTimeToExec')
    distance = getDistSum(routeIds, mainGraph, destNode)
    arrivalTime = distance // user.avgSpeed
    return arrivalTime + user.initTime + 2

def getDistSum(routeIds, mainGraph, destNode):
    log(TAG, 'getDistSum')
    distSum = 0
    cont = 0
    while routeIds[cont] != destNode.nId:
        distSum += mainGraph.adjList[routeIds[cont]][routeIds[cont+1]][0]
        cont += 1
    return distSum

def log(fileName, msg):
    logging.info(f'{fileName}: time-step:{TimerSingleton().getTimerValue()} {msg}')