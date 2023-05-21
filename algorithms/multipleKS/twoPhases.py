import math
import networkx as nx
import sim_utils
from algorithms.oneKS import greedyAlloc as alg
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
    nonAllocated, allocatedMore = classifyAllocatedUsers(allocationPerCloudlet, vms)
    finalAlocation = usersAllocatedOnlyOnce(allocationPerCloudlet, nonAllocated, allocatedMore)
    print(finalAlocation)
    # separating users by type and call the matching algorithm
    userTypes = ['gp1', 'gp2', 'ramIntensive', 'cpuIntensive']
    for userType in userTypes:
        nonAllocatedByType = separateUsersByType(nonAllocated, userType)
        moreThanOnceByType = separateUsersByType(allocatedMore, userType)
        nbUsersInCloudlet = {}
        for c in cloudlets:
            allocatedInC = [u for u,c in allocationPerCloudlet[c.cId] if len(allocationPerCloudlet[c.cId]) > 0]
            nbUsersInCloudlet[c.cId] = len(set([u.uId for u in moreThanOnceByType]) & set([u.uId for u in allocatedInC]))
        result = matchingAlg(cloudlets, nonAllocatedByType + moreThanOnceByType, nbUsersInCloudlet)
        finalAlocation += result
    sim_utils.log(TAG, f'FINAL allocated users: {[(u.uId, c.cId) for (u,c) in finalAlocation]}')
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

    allocatedMoreThanOnce = []
    nonAllocatedUsers = []
    for vm in vms:
        allocated = False
        for c in allocationPerCloudlet.keys():
            if len(allocationPerCloudlet[c]) > 0:
                for tupleAlloc in allocationPerCloudlet[c]:
                    user = tupleAlloc[0]
                    if user.uId == vm.uId:
                        if allocated:
                            if vm not in allocatedMoreThanOnce:
                                allocatedMoreThanOnce.append(user)
                        else:
                            allocated = True
        if not allocated:
            nonAllocatedUsers.append(vm)
    return nonAllocatedUsers, allocatedMoreThanOnce

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

def builgBGraph(cloudlets, users, nbUsersInCloudletDict):
    sim_utils.log(TAG, 'builgBGraph')

    G = nx.Graph()
    left_nodes = [u.uId for u in users]
    right_nodes = [c.cId for c in cloudlets]
    edges = []
    for u in users:
        for c in cloudlets:
            edges.append((u.uId, c.cId, {'capacity': 1, 'weight': int(sim_utils.calcDistance((u.position[0], u.position[1]), 
                                                    (c.position[0], c.position[1])))}))

    G.add_node('s', bipartite=0)
    G.add_node('t', bipartite=1)
    G.add_nodes_from(left_nodes, bipartite=0)
    G.add_nodes_from(right_nodes, bipartite=1)
    G.add_edges_from(edges)
    source_node = 's'
    sink_node = 't'
    for node in left_nodes:
        G.add_edge(source_node, node, capacity=1, weight=0)
    for node in right_nodes:
        G.add_edge(node, sink_node, capacity=nbUsersInCloudletDict[node], weight=0)
    return G, left_nodes, right_nodes

def matchingAlg(cloudlets, users, nbUsersInCloudletDict):
    sim_utils.log(TAG, 'matchingAlg')

    graph, left_nodes, right_nodes = builgBGraph(cloudlets, users, nbUsersInCloudletDict)
    flowDict = nx.max_flow_min_cost(graph, 's', 't')
    pairs = []
    for left_node in left_nodes:
        for right_node in right_nodes:
            if graph.has_edge(left_node, right_node) and flowDict[left_node][right_node] > 0:
                pair = (UsersListSingleton().findById(left_node), 
                                CloudletsListSingleton().findById(right_node))
                if pair not in pairs:
                    pairs.append(pair)
    return pairs