import math

def detectUsersByPosition(cloudlet, users):
    detectedUsers = []
    for u in users:
        distance = math.sqrt((u.position[0] - cloudlet.position[0])**2 + (u.position[1] - cloudlet.position[1])**2)
        if distance <= cloudlet.coverageRadius:
            detectedUsers.append(u)
    return detectedUsers

def allocate(cloudlets, vms):
    # DISTRIBUTED PHASE
    allocationPerCloudlet = {}
    for c in cloudlets:
        detectedUsers = detectUsersByPosition(c, vms)
        # allocationPerCloudlet[c] = call greedy alloc
    
    # CENTRALIZED PHASE
    nonAllocatedUsers = []
    allocatedMoreThanOnce = []
    # finalAlocation = users allocated only once
    userTypes = ['gp1', 'gp2', 'ramIntensive', 'cpuIntensive']
    nonAllocatedPerType = {}
    allocatedMoreThanOnceByType = {}
    for userType in userTypes:
        nonAllocatedPerType[userType] = separateUsersByType(nonAllocatedUsers, userType)
        allocatedMoreThanOnceByType[userType] = separateUsersByType(allocatedMoreThanOnce, userType)
        nbUsersInCloudlet = {}
        for c in cloudlets:
            # nbUsersInCloudlet[c] = detectar usuarios do tipo userType em c qe tambem estao em M
        # finalAlocation = finalAlocation + matchingAlg(cloudlets, nonAllocatedPerType[userType], allocatedMoreThanOnceByType[userType], nbUsersInCloudlet)
    # return finalAlocation

def matchingAlg(cloudlets, nonAllocatedUsers, allocatedMoreThanOnceUsers, nbUsersInCloudlet):
    # matchingAlg(cloudlets, nonAllocatedPerType[userType], allocatedMoreThanOnceByType[userType], nbUsersInCloudlet)
    # return finalAlocation
    pass


        
