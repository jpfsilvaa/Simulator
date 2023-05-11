import math
import numpy as np
import sim_utils
import algorithms.multipleKS.alloc_utils as utils
from sim_entities.users import UsersListSingleton

TAG = 'hedge.py'
EPSILON = 1

# TODO: When computing the detected cloudlets per cloudlet, I need to increase the radius of detection by 2
# TODO: Also, the users in the parameter of this function are only the users currently in C
def hedgeAlg(currCloudlet, cloudlets, usersInC, timeSlots, detectedCloudletsPerCloudlet):
    sim_utils.log(TAG, 'hedgeAlg')
    predictionResult = {usersInC[i].uId: None for i in range(len(usersInC))}
    neighbors = detectedCloudletsPerCloudlet[currCloudlet.cId]
    pastPaths = getPastPaths(currCloudlet, neighbors, detectedCloudletsPerCloudlet)

    for p in pastPaths:
        sim_utils.log(TAG, f'past path: {p}')
        cumulativeLoss = [[1 for _ in range(len(neighbors))] for _ in range(timeSlots+1)]
        for t in range(timeSlots):
            sim_utils.log(TAG, f'time-slot: {t}')
            n = 0
            loss = [0 for _ in range(len(neighbors))]
            # get users in cloudlet currCloudlet with the same past path as p at the time t
            usersWithPastPathP = getUsersInPastPath(p, usersInC)
            if len(usersWithPastPathP) > 0:
                for u in usersWithPastPathP:
                    # draw an expert 'st' from the probability distribution of the L
                    predictionResult[u.uId] = drawExpert(EPSILON, neighbors, cumulativeLoss, t)

                    # compute the estimated loss
                    for j in range(len(neighbors)):
                        loss[j] += 0 if utils.checkLatencyThreshold(u, neighbors[j]) else 1

                    n += 1

                # normalize each loss
                for j in range(len(neighbors)):
                    loss[j] = loss[j] / n
            
            for j in range(len(neighbors)):
                cumulativeLoss[t+1][j] = cumulativeLoss[t][j] + loss[j]
            
            MIN = cumulativeLoss[t+1][0]

            for j in range(len(neighbors)):
                if cumulativeLoss[t+1][j] < MIN:
                    MIN = cumulativeLoss[t+1][j]
            
            for j in range(len(neighbors)):
                cumulativeLoss[t+1][j] = cumulativeLoss[t+1][j] - MIN
    uS = UsersListSingleton()
    allocatedUsers = [(uS.findById(u), c) for u, c in predictionResult.items() if c != None]
    sim_utils.log(TAG, f'allocated users for this cloudlet / total users for this cloudlet: {len(allocatedUsers)} / {len(usersInC)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return allocatedUsers

def getPastPaths(currCloudlet, neighbors, detectedCloudletsPerCloudlet):
    pastPaths = []
    for n in neighbors:
        neighborsOfNeighbor = detectedCloudletsPerCloudlet[n.cId]
        for n2 in neighborsOfNeighbor:
            pastPaths.append([n2, n, currCloudlet])
    return pastPaths

def getUsersInPastPath(pastPath, users):
    usersInPastPath = []
    for u in users:
        sim_utils.log(TAG, f'u.pastCloudlets -> {[c.cId for c in u.pastCloudlets]}')
        sim_utils.log(TAG, f'pastPath -> {[c.cId for c in pastPath]}')
        if userHasPastPath(pastPath, u.pastCloudlets):
            usersInPastPath.append(u)
    return usersInPastPath

def userHasPastPath(pastPath, usersPastCloudlets):
    pastPathIds = [c.cId for c in pastPath]
    if len(usersPastCloudlets) > 1:
        usersPastCloudletsIds = [c.cId for c in usersPastCloudlets]
        if usersPastCloudletsIds[-1] == pastPathIds[-2] and usersPastCloudletsIds[-2] == pastPathIds[-3]:
            sim_utils.log(TAG, 'TRUE')
            return True
    return False

def drawExpert(epsilon, neighbors, cumulativeLoss, t):
    probDistribution = []
    sumOfComulativeLoss = 0
    for i in range(len(neighbors)):
        sumOfComulativeLoss += math.exp(epsilon * cumulativeLoss[t][i])

    for i in range(len(neighbors)):
        probDistribution.append((math.exp(epsilon * cumulativeLoss[t][i]) / sumOfComulativeLoss))
    
    # draw an expert 'st 'from the probability distribution of the L
    expert = np.random.choice(neighbors, 1, p=probDistribution)
    return expert[0]