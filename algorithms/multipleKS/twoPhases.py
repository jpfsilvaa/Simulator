import math
import networkx as nx
import sim_utils
from algorithms.oneKS import greedyAlloc as alg
import algorithms.multipleKS.alloc_utils as utils
import logging
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton
import time
import gurobipy as gp
from gurobipy import GRB

TAG = 'twoPhases.py'

def twoPhasesAlloc(cloudlets, vms, detectedUserPerCloudlet):
    sim_utils.log(TAG, 'twoPhasesAlloc')

    # -------DISTRIBUTED PHASE-------
    sim_utils.log(TAG, '----distributed phase----')
    initTime1stPhase = time.time()
    allocationPerCloudlet = firstPhase(cloudlets, detectedUserPerCloudlet)
    finalTime1stPhase = time.time()
        
    # -------CENTRALIZED PHASE-------
    sim_utils.log(TAG, '----centralized phase----')
    initTime2ndPhase = time.time()
    finalAllocation = secondPhase(cloudlets, vms, allocationPerCloudlet)
    finalTime2ndPhase = time.time()
    return [calcSocialWelfare(finalAllocation), finalAllocation], getResultsFrom1stPhase(allocationPerCloudlet), [finalTime1stPhase - initTime1stPhase, finalTime2ndPhase - initTime2ndPhase]

def firstPhase(cloudlets, detectedUserPerCloudlet):
    allocationPerCloudlet = {}
    for c in cloudlets:
        if len(detectedUserPerCloudlet[c.cId]) > 0:
            allocationResult = alg.greedyAlloc_OneKS(c, detectedUserPerCloudlet[c.cId])
            allocationPerCloudlet[c.cId] = allocationResult[1]
        else:
            allocationPerCloudlet[c.cId] = []
    return allocationPerCloudlet

def secondPhase(cloudlets, vms, allocationPerCloudlet):
    nonAllocated_, allocated_ = classifyAllocatedUsers(allocationPerCloudlet, vms)
    finalAlocation = []

    # separating users by type and calling the matching algorithm
    userTypes = ['gp1', 'gp2', 'ramIntensive', 'cpuIntensive']
    for userType in userTypes:
        nonAllocatedByType = separateUsersByType(nonAllocated_, userType)
        allocatedByType = separateUsersByType(allocated_, userType)
        nbUsersInCloudlet = {}
        for c in cloudlets:
            allocatedInC = [u for u,c in allocationPerCloudlet[c.cId] if len(allocationPerCloudlet[c.cId]) > 0]
            nbUsersInCloudlet[c.cId] = len(set([u.uId for u in allocatedByType]) & set([u.uId for u in allocatedInC]))
        result = matchingAlg(cloudlets, nonAllocatedByType, allocatedByType, nbUsersInCloudlet)
        finalAlocation += result
    return finalAlocation

def getResultsFrom1stPhase(allocationPerCloudlet):
    sim_utils.log(TAG, 'getResultsFrom1stPhase')

    results = []
    for c in allocationPerCloudlet.keys():
        for tupleAlloc in allocationPerCloudlet[c]:
            results.append(tupleAlloc)
    return results

def pricing(winners1stPhase, detectedUsersPerCloudlet, usersSing, cloudlets):
    sim_utils.log(TAG, 'pricing')
    for w in winners1stPhase:
        wUser = usersSing.findById(w[0].uId)
        newPrice = alg.pricing(w, detectedUsersPerCloudlet[w[1].cId])
        if wUser.price > 0:
            wUser.price = min(wUser.price, newPrice)
        else:
            wUser.price = newPrice
        assert wUser.price <= wUser.bid

    # TODO: clean the winners1stPhase list to include only one user per id but with the correct price
    winners1stPhase_ = []
    for w in winners1stPhase:
        if w not in winners1stPhase_:
            winners1stPhase_.append(w)   
    
    for w in winners1stPhase_:
        wUser = usersSing.findById(w[0].uId)
        checkCritPrice(w[0], detectedUsersPerCloudlet, usersSing.getList() ,  cloudlets)

def checkCritPrice(user, detectedUsersPerCloudlet, vms, cloudlets):
    sim_utils.log(TAG, 'checkCritPrice')
    
    # function to check if the user would still be allocated in the 2nd phase
    # 1 - remove the user from the list and execute the 1st phase again
    for c in detectedUsersPerCloudlet.keys():
        cloudletsForUser = []
        if user.uId in [u.uId for u in detectedUsersPerCloudlet[c]]:
            removedUser = [u for u in detectedUsersPerCloudlet[c] if u.uId == user.uId][0]
            detectedUsersPerCloudlet[c].remove(removedUser)
            cloudletsForUser.append(c)
    
    allocationPerCloudlet = firstPhase(cloudlets, detectedUsersPerCloudlet)

    # 2 - put the user back in the list and execute the 2nd phase again
    for c in cloudletsForUser:
        detectedUsersPerCloudlet[c].append(user)
    
    finalAllocation = secondPhase(cloudlets, vms, allocationPerCloudlet)

    # 3 - if the user is allocated in the second phase = price zero
    #   - otherwise, the user is not allocated in the second phase = price is the critical price already calculated
    wUser = UsersListSingleton().findById(user.uId)
    if user.uId in [u.uId for u,c in finalAllocation]:
        wUser.price = 0

def defineFirstPhasePrices(winners):
    sim_utils.log(TAG, 'defineFirstPhasePrices')

    for tupleAlloc in winners:
        user = tupleAlloc[0]
        UsersListSingleton().findById(user.uId).price = user.price

def calcSocialWelfare(allocation):
    sim_utils.log(TAG, 'calcSocialWelfare')

    socialWelfare = 0
    for tupleAlloc in allocation:
        user = tupleAlloc[0]
        socialWelfare += user.bid
    return socialWelfare

def classifyAllocatedUsers(allocationPerCloudlet, vms):
    sim_utils.log(TAG, 'classifyAllocatedUsers')

    allocatedUsers = []
    nonAllocatedUsers = []
    for vm in vms:
        allocated = False
        for c in allocationPerCloudlet.keys():
            if len(allocationPerCloudlet[c]) > 0:
                for tupleAlloc in allocationPerCloudlet[c]:
                    user = tupleAlloc[0]
                    if user.uId == vm.uId:
                        if vm not in allocatedUsers:
                            allocatedUsers.append(vm)
                            allocated = True
        if not allocated:
            nonAllocatedUsers.append(vm)
    return nonAllocatedUsers, allocatedUsers

def usersAllocatedOnlyOnce(allocationPerCloudlet, nonAllocatedUsers, allocatedMoreThanOnce):
    sim_utils.log(TAG, 'usersAllocatedOnlyOnce')

    allocation = []
    for allocs in allocationPerCloudlet.values():
        if len(allocs) > 0:
            for alloc in allocs:
                if not isIn(allocatedMoreThanOnce, alloc[0]) and not isIn(nonAllocatedUsers, alloc[0]):
                    allocation.append(alloc)
    return allocation

def isIn(list, user):
    sim_utils.log(TAG, 'isIn')

    for u in list:
        if u.uId == user.uId:
            return True
    return False

def separateUsersByType(users, userType):
    sim_utils.log(TAG, 'separateUsersByType')

    usersByType = []
    for user in users:
        if user.vmType == userType:
            usersByType.append(user)
    return usersByType

def builgBGraph(cloudlets, usersAllocated, usersNonAllocated, nbUsersInCloudletDict, C):
    sim_utils.log(TAG, 'builgBGraph')

    G = nx.DiGraph()
    # users nodes are on the left, 
    # where the alloceted users have a demand of -1 
    # and the non allocated have a demand of 0
    for u in usersAllocated:
        G.add_node(u.uId, demand=-1)
    for u in usersNonAllocated:
        G.add_node(u.uId, demand=0)
    
    # cloudlet nodes are on the right
    for c in cloudlets:
        G.add_node(c.cId, demand=0)
    
    source_node = 's'
    sink_node = 't'
    G.add_node(source_node, demand=-C)
    G.add_node(sink_node, demand=C+len(usersAllocated))

    # edges from the users to the cloudlets
    edges = []
    allUsers = [u for u in usersNonAllocated] + [u for u in usersAllocated]
    for u in allUsers:
        for c in cloudlets:
            if utils.checkLatencyThreshold(UsersListSingleton().findById(u.uId),
                                             CloudletsListSingleton().findById(c.cId)):
                G.add_edge(u.uId, c.cId, capacity=1, weight=0)

    # edges from the source only to the non allocated users
    for u in usersNonAllocated:
        G.add_edge(source_node, u.uId, capacity=1, weight=0)

    # edges from the cloudlets to the sink with nb as the capacity
    for c in cloudlets:
        G.add_edge(c.cId, sink_node, capacity=nbUsersInCloudletDict[c.cId], weight=0)
    return G

def linearProgram(cloudlets, usersAllocated, usersNonAllocated, nbUsersInCloudletDict, C):
    sim_utils.log(TAG, 'builgBGraph')

    finalResult = []
    model = gp.Model('2nd phase allocation')
    model.Params.LogToConsole = 0
    
    source_node = 's'

    # edges from the users to the cloudlets
    adjList = {}
    arcs = {}
    usersIdsM = [u.uId for u in usersAllocated]
    usersIdsN = [u.uId for u in usersNonAllocated]
    cloudletsIds = [c.cId for c in cloudlets]
    allUsersIds = usersIdsM + usersIdsN
    for u in allUsersIds:
        adjList[u] = []
        for c in cloudletsIds:
            if utils.checkLatencyThreshold(UsersListSingleton().findById(u),
                                             CloudletsListSingleton().findById(c)):
                adjList[u].append(c)
                arcs[u, c] = model.addVar(vtype=GRB.BINARY, name='x_%s_%s' % (u, c))

    # edges from the source only to the non allocated users
    adjList[source_node] = []
    for u in usersIdsN:      
        adjList[source_node].append(u)  
        arcs[source_node, u] = model.addVar(vtype=GRB.BINARY, name='x_%s_%s' % (source_node, u))

    # edges from the cloudlets to the sink with nb as the capacity
    for c in cloudletsIds:
        adjList[c] = []
        sinkNodes = [f'sink_c{c}_{i}' for i in range(nbUsersInCloudletDict[c])]
        for sink_node in sinkNodes:
            adjList[c].append(sink_node)
            arcs[c, sink_node] = model.addVar(vtype=GRB.BINARY, name='x_%s_%s' % (c, sink_node))
    
    model.setObjective(gp.quicksum(arcs[i,j] for i in usersIdsN for j in adjList[i]), GRB.MAXIMIZE)

    # non-allocated cosntraint
    for i in usersIdsN:
        model.addConstr(gp.quicksum(arcs[i,j] for j in adjList[i]) <= 1, name=f'nonAllocated_{i}')

    # allocated constraint
    for i in usersIdsM:
        model.addConstr(gp.quicksum(arcs[i,j] for j in adjList[i]) == 1, name=f'allocated_{i}')
    
    # capacity constraint:
    for i in cloudletsIds:
        model.addConstr(gp.quicksum(arcs[i,j] for j in adjList[i]) <= nbUsersInCloudletDict[i], name=f'capacity_{i}')
    
    model.write('2phases.lp')
    model.optimize()

    if model.status == GRB.OPTIMAL:
        for i in allUsersIds:
            for j in adjList[i]:
                if arcs[i, j].x > 0.5:
                    finalResult.append((i, j))
    else:
        sim_utils.log(TAG, 'No solution found')

    model.dispose()
    return finalResult

def calculateFlow(cloudlets, usersNonAllocated, usersAllocated, nbUsersInCloudletDict, nbUsersNonAllocated):
    flowResults = {}
    c = 0
    left = 0
    right = nbUsersNonAllocated
    lastException = 0

    # first iteration
    graph = builgBGraph(cloudlets, usersAllocated, usersNonAllocated, nbUsersInCloudletDict, c)
    flowCost, flowDict = nx.network_simplex(graph)
    flowResults[c] = (flowCost, flowDict)

    while True:
        try:
            c = (left + right) // 2
            graph = builgBGraph(cloudlets, usersAllocated, usersNonAllocated, nbUsersInCloudletDict, c)
            flowCost, flowDict = nx.network_simplex(graph)
            flowResults[c] = (flowCost, flowDict)
            
            # if c is the last value before the exception, 
            # or the c is the left side, 
            # then it is the maximum c
            if c == lastException-1 or c == left:
                break
            left = c
        except nx.NetworkXUnfeasible:
            right = c
            lastException = c

    return flowResults[c], graph

def matchingAlg(cloudlets, usersNonAllocated, usersAllocated, nbUsersInCloudletDict):
    sim_utils.log(TAG, 'matchingAlg')
    lpApproach = True
    if lpApproach:
        lpPairs = linearProgram(cloudlets, usersAllocated, usersNonAllocated, nbUsersInCloudletDict, len(usersNonAllocated))
        pairs = []
        for p in lpPairs:
            user = UsersListSingleton().findById(p[0])
            cloudlet = CloudletsListSingleton().findById(p[1])
            pairs.append((user, cloudlet))
    else:
        flowResult, graph = calculateFlow(cloudlets, usersNonAllocated, usersAllocated, 
                                        nbUsersInCloudletDict, len(usersNonAllocated))

        pairs = []
        left_nodes = [u.uId for u in usersNonAllocated] + [u.uId for u in usersAllocated]
        right_nodes = [c.cId for c in cloudlets]
        for left_node in left_nodes:
            for right_node in right_nodes:
                if graph.has_edge(left_node, right_node):
                    if flowResult[1][left_node][right_node] > 0:
                        pair = (UsersListSingleton().findById(left_node), 
                                    CloudletsListSingleton().findById(right_node))
                        if pair not in pairs:
                            pairs.append(pair)
    return pairs