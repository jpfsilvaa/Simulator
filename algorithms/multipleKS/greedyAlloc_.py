import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging
import copy
from timeout_decorator import timeout

TAG = 'greedyAlloc_.py'

@timeout(60)
def greedyAlloc(cloudlets, vms, detectedCloudletsPerUser, withQuadtree):
    sim_utils.log(TAG, 'greedyAlloc')
    # For homogeneous cloudlets, the step below is not necessary
    # But for heterogeneous cloudlets, it is necessary and I should do it only once instead of every opt call
    # sortedCloudlets = utils.sortCloudletsByType(cloudlets, True)
    initTime = time.time()
    normalVms = utils.normalize(cloudlets[0], vms)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)

    allocatedUsers = []
    socialWelfare = 0
    cloudletsOccupation = {c.cId: utils.Resources(0, 0, 0) for c in cloudlets}

    initTimeLoop = time.time()
    for d in D:
        currentUser = d[0]
        c = firstFit(currentUser, cloudlets, cloudletsOccupation, detectedCloudletsPerUser, withQuadtree)
        if c is not None:
            utils.allocate(currentUser, cloudletsOccupation[c.cId])
            allocatedUsers.append((currentUser, c))
            socialWelfare += currentUser.bid
    finalTime = time.time()

    printAllocation(initTimeLoop, initTime, finalTime, allocatedUsers, vms)
    return [socialWelfare, allocatedUsers]

def firstFit(user, cloudlets, cloudletsOccupation, detectedCloudletsPerUser, withQuadtree):
    if withQuadtree:
        for c in detectedCloudletsPerUser[user.uId]:
            if utils.userFits(user, cloudletsOccupation[c.entity.cId]):
                return c.entity
    else:
        for c in cloudlets:
            if utils.userFits(user, cloudletsOccupation[c.cId]) \
            and utils.checkLatencyThreshold(user, c):
                return c
    return None

def printAllocation(initTimeLoop, initTime, finalTime, allocatedUsers, vms):
    sim_utils.log(TAG, f'elapsed loop time: {finalTime - initTimeLoop}')
    sim_utils.log(TAG, f'elapsed total time: {finalTime - initTime}')
    sim_utils.log(TAG, f'allocated users / total users: {len(allocatedUsers)} / {len(vms)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')

def pricing(winners, users, detectedCloudletsPerUser, cloudlets, withQuadtree):
    sim_utils.log(TAG, 'pricing')

    normalVms = utils.normalize(cloudlets[0], users)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)
    sim_utils.log(TAG, f'D: {[(d[0].uId, d[0].vmType) for d in D]}')

    if len(winners) == len(D):
        sim_utils.log(TAG, 'len(winners) == len(D) -> All users are winners, all users pay 0.')
        return winners
    for w in winners:
        allocatedUsers = []
        cloudletsOccupation = {c.cId: utils.Resources(0, 0, 0) for c in cloudlets}
        for d in D:
            sim_utils.log(TAG,'--------------------------')
            sim_utils.log(TAG,f'length winners: {len(winners)}')
            sim_utils.log(TAG,f'length D: {len(D)}')
            if d[0].uId == w[0].uId:
                sim_utils.log(TAG, f'CONTINUE - {w[0].uId}, {w[0].vmType}, {w[0].price}')
                continue
            currentUser = d[0]
            sim_utils.log(TAG,f'currentUser: {currentUser.uId}')
            c = firstFit(currentUser, cloudlets, cloudletsOccupation, detectedCloudletsPerUser, withQuadtree)
            sim_utils.log(TAG,f'c: {c.cId if c is not None else "None"}')            
            if c is not None:
                utils.allocate(currentUser, cloudletsOccupation[c.cId])
            if firstFit(w[0], cloudlets, cloudletsOccupation, detectedCloudletsPerUser, withQuadtree) is None:
                w[0].price = d[1] * w[0].maxReq
                break
        sim_utils.log(TAG, f'{w[0].uId}, {w[0].vmType}, {w[0].price}')
        printWinnerPrice(w)
        sim_utils.log(TAG, '--------------------------\n\n')
    return winners

def printWinnerPrice(w):
    sim_utils.log(TAG, f'price > bid? {w[0].price > w[0].bid}') 
    sim_utils.log(TAG, f'w[0].bid/w[0].maxReq: {w[0].bid/w[0].maxReq}')
    sim_utils.log(TAG, f'w[0].maxReq: {w[0].maxReq}')
    sim_utils.log(TAG, f'w[0].price: {w[0].price} and w[0].bid: {w[0].bid}')
    sim_utils.log(TAG, ' ')

def printResults(winner, criticalValue):
    sim_utils.log(TAG, 'pricingResults')
    print('user id ->', winner.uId)
    print('vmType ->', winner.vmType)
    print('critical value (b_j/w_j)->', criticalValue)
    print('winner density (b_i/w_i)->', winner.bid/winner.maxReq)
    print('winner bid (b_i)->', winner.bid)
    print('winner maxCoord (w_i)->', winner.maxReq)
    print('winner price->', winner.price)
    print('-----------')

def main(jsonFilePath):
    data = utils.readJSONData(jsonFilePath)
    cloudlets = utils.buildCloudlet(data['Cloudlets'])
    userVms = utils.buildUserVms(data['UserVMs'])
    startTime = time.time()
    result = greedyAlloc(cloudlets, userVms)
    endTime = time.time()

    sim_utils.log(TAG, f'social welfare: {result[0]}')
    sim_utils.log(f"execution time: {str(endTime-startTime).replace('.', ',')}")
    # print('\nprices (user: (bid, price)) : ', pricing(winners=result[1], densities=result[2]))

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)
