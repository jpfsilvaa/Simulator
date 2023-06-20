import math
import networkx as nx
import sim_utils
from algorithms.oneKS import greedyAlloc as alg
import algorithms.multipleKS.alloc_utils as utils
import logging
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton

TAG = 'twoPhases.py'

def twoPhasesAlloc(cloudlets, vms, detectedUserPerCloudlet):
    sim_utils.log(TAG, 'twoPhasesAlloc')

    # -------DISTRIBUTED PHASE-------
    sim_utils.log(TAG, '----distributed phase----')
    allocationPerCloudlet = {}
    for c in cloudlets:
        if len(detectedUserPerCloudlet[c.cId]) > 0:
            allocationResult = alg.greedyAlloc_OneKS(c, detectedUserPerCloudlet[c.cId])
            allocationPerCloudlet[c.cId] = allocationResult[1]
            defineFirstPhasePrices(allocationResult[1])
        else:
            allocationPerCloudlet[c.cId] = []
        
    # -------CENTRALIZED PHASE-------
    sim_utils.log(TAG, '----centralized phase----')
    nonAllocated_, allocated_ = classifyAllocatedUsers(allocationPerCloudlet, vms)
    finalAlocation = []

    # separating users by type and call the matching algorithm
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
    return [calcSocialWelfare(finalAlocation), finalAlocation]

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

    while c < nbUsersNonAllocated:
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