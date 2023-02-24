TAG = 'sim_utils.py:'

def calcTimeToExec(user, routeIds, mainGraph, destNode):
    print(TAG, 'calcTimeToExec')
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