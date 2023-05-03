import math
from algorithms.oneKS import greedyAlloc as alg

def allocate(cloudlets, vms, detectedUserPerCloudlet):
    # -------DISTRIBUTED PHASE-------
    allocationPerCloudlet = {}
    for c in cloudlets:
        allocationResult = alg.greedyAlloc(c, vms)
        allocationPerCloudlet[c] = allocationResult[1]
        
    # -------CENTRALIZED PHASE-------
    nonAllocated, allocatedMore = classifyAllocatedUsers(allocationPerCloudlet, vms)
    finalAlocation = usersAllocatedonlyOnce(allocationPerCloudlet, nonAllocated, allocatedMore)
    
    # separating users by type and call the matching algorithm
    userTypes = ['gp1', 'gp2', 'ramIntensive', 'cpuIntensive']
    for userType in userTypes:
        nonAllocatedByType = separateUsersByType(nonAllocatedUsers, userType)
        moreThanOnceByType = separateUsersByType(allocatedMoreThanOnce, userType)
        nbUsersInCloudlet = {}
        for c in cloudlets:
            nbUsersInCloudlet[c] = set(moreThanOnceByType) & set(allocationPerCloudlet[c])
        result = matchingAlg(cloudlets, nonAllocatedPerType + moreThanOnceByType, nbUsersInCloudlet)
        finalAlocation += result
    return finalAlocation

def classifyAllocatedUsers(allocationPerCloudlet, vms):
    allocatedMoreThanOnce = []
    nonAllocatedUsers = []
    for vm in vms:
        allocated = False
        for c in allocationPerCloudlet:
            for user in allocationPerCloudlet[c]:
                if user.uId == vm.uId:
                    if allocated:
                        allocatedMoreThanOnce.append(vm)
                    else:
                        allocated = True
        if not allocated:
            nonAllocatedUsers.append(vm)
    return nonAllocatedUsers, allocatedMoreThanOnce

def usersAllocatedonlyOnce(allocationPerCloudlet, nonAllocatedUsers, allocatedMoreThanOnce):
    allocation = []
    for alloc in allocationPerCloudlet.values():
        if alloc[0] not in allocatedMoreThanOnce and not alloc[0] in nonAllocatedUsers:
            allocation.append(alloc)
    return allocation

def separateUsersByType(users, userType):
    usersByType = []
    for user in users:
        if user.vmType == userType:
            usersByType.append(user)
    return usersByType

def matchingAlg(cloudlets, users, nbUsersInCloudletDict):
    graph = builgBGraph(cloudlets, users, nbUsersInCloudletDict)
    flux = fordFulkerson(graph, 's', 't')

def fordFulkerson(graph, source, sink):
    # This array is filled by BFS and to store path
    parent = [-1] * (len(graph))
    max_flow = 0 # There is no flow initially
    # Augment the flow while there is path from source to sink
    while bfs(graph, source, sink, parent):
        # Find minimum residual capacity of the edges along the
        # path filled by BFS. Or we can say find the maximum flow
        # through the path found.
        path_flow = float("Inf")
        s = sink
        while(s != source):
            path_flow = min(path_flow, graph[parent[s]][s])
            s = parent[s]
        # Add path flow to overall flow
        max_flow += path_flow
        # update residual capacities of the edges and reverse edges
        # along the path
        v = sink
        while(v != source):
            u = parent[v]
            graph[u][v] -= path_flow
            graph[v][u] += path_flow
            v = parent[v]
    return max_flow

def bfs(graph, source, sink, parent):
    # Mark all the vertices as not visited
    visited = [False] * (len(graph))
    # Create a queue for BFS
    queue = []
    # Mark the source node as visited and enqueue it
    queue.append(source)
    visited[source] = True
    # Standard BFS Loop
    while queue:
        u = queue.pop(0)
        # Get all adjacent vertices's of the dequeued vertex u
        # If a adjacent has not been visited, then mark it
        # visited and enqueue it
        for ind, val in enumerate(graph[u]):
            if visited[ind] == False and val > 0:
                queue.append(ind)
                visited[ind] = True
                parent[ind] = u
    # If we reached sink in BFS starting from source, then return
    # true, else false
    return True if visited[sink] else False