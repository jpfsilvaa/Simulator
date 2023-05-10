import math
import numpy as np

# TODO: When computing the detected cloudlets per cloudlet, I need to increase the radius of detection by 2
# TODO: Also, the users in the parameter of this function are only the users currently in C
def hedgeAlg(currCloudlet, cloudlets, usersInC, timeSlots, detectedCloudletsPerCloudlet):
    predictionResult = {usersInC[i].uId: None for i in range(len(usersInC))}
    neighbors = detectedCloudletsPerCloudlet[currCloudlet.cId]
    pastPaths = getPastPaths(currCloudlet, neighbors, usersInC, detectedCloudletsPerCloudlet)

    for p in pastPaths:
        cumulativeLoss = [[1 for _ in range(len(neighbors))] for _ in range(len(timeSlots))]
        for t in timeSlots:
            n = 0
            loss = [0 for _ in range(len(neighbors))]
            # get users in cloudlet currCloudlet with the same past path as p at the time t
            usersWithPastPathP = getUsersInPastPath(p, users)
            for u in usersWithPastPathP:
                # draw an expert 'st 'from the probability distribution of the L
                predictionResult[u.uId] = drawExpert(epsilon, neighbors, cumulativeLoss, t)

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
    return [(u, c) for u, c in predictionResult.items() if c != None]

def getPastPaths(currCloudlet, neighbors, detectedCloudletsPerCloudlet):
    pastPaths = []
    for n in neighbors:
        neighborsOfNeighbor = detectedCloudletsPerCloudlet[n.cId]
        if n.cId != currCloudlet.cId:
            for n2 in neighborsOfNeighbor:
                if n2.cId != currCloudlet.cId:
                    pastPaths.append([n2, n, currCloudlet])
    return pastPaths

def getUsersInPastPath(pastPath, users):
    usersInPastPath = []
    for u in users:
        if userHasPastPath(pastPath, u.pastCloudlets):
            usersInPastPath.append(u)
    return usersInPastPath

def userHasPastPath(pastPath, usersPastCloudlets):
    pastPathIds = [c.cId for c in pastPath]
    usersPastCloudletsIds = [c.cId for c in usersPastCloudlets]
    if usersPastCloudletsIds[-2] == pastPathIds[-2] and usersPastCloudletsIds[-3] == pastPathIds[-3]:
        return True
    return False

def drawExpert(epsilon, neighbors, cumulativeLoss, t):
    probDistribution = []
    sumOfComulativeLoss = sum(epsilon*cumulativeLoss[t])
    for i in neighbors:
        probDistribution.append(math.exp(epsilon * cumulativeLoss[t][i]) / sumOfComulativeLoss)
    
    # draw an expert 'st 'from the probability distribution of the L
    expert = np.random.choice(neighbors, 1, p=probDistribution)
    return expert