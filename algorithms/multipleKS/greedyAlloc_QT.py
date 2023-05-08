import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging
import copy

TAG = 'greedyAlloc_QT.py'

def greedyAlloc(cloudlets, vms, detectedCloudletsPerUser):
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
        timeToDetect = time.time()
        cloudlets = detectedCloudletsPerUser[d[0].uId]
        for c in cloudlets:
            if utils.userFits(d[0], cloudletsOccupation[c.entity.cId]):
                utils.allocate(d[0], cloudletsOccupation[c.entity.cId])
                allocatedUsers.append((d[0], c.entity))
                socialWelfare += d[0].bid
                break
    finalTime = time.time()
    sim_utils.log(TAG, f'elapsed loop time: {finalTime - initTimeLoop}')
    sim_utils.log(TAG, f'elapsed total time: {finalTime - initTime}')
    sim_utils.log(TAG, f'allocated users / total users: {len(allocatedUsers)} / {len(vms)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return [socialWelfare, allocatedUsers]

def pricing(winners, cloudlets):
    sim_utils.log(TAG, 'pricing')
    for w in winners:
        normalizedCls = [utils.Resources(0, 0, 0) for c in cloudlets]
        w[0].price = float('inf')
        winners_ = [winner for winner in winners if winner[0].uId != w[0].uId]
        D_ = utils.calcDensitiesByMax([w[0] for w in winners_])
        D_.sort(key=lambda a: a[1], reverse=True)
        sim_utils.log(TAG, [d[1] for d in D_])
        j = 0
        while j < len(D_):
            for cloudletIdx in range(len(cloudlets)):
                currentUser = D_[j][0]
                if utils.userFits(currentUser, normalizedCls[cloudletIdx]):
                    utils.allocate(currentUser, normalizedCls[cloudletIdx])
                    # sim_utils.log(TAG, f'j-> {j}')
                    w[0].price = min(w[0].price, D_[j-1][1]*w[0].maxReq)
                    # This increment is not in the paper's pseudocode, but it is necessary 
                    # to avoid allocating the same user to multiple cloudlets
            j += 1
        # is the price bigger than the bid?
        sim_utils.log(TAG, f'w[0].price: {w[0].price} and w[0].bid: {w[0].bid}')
        sim_utils.log(TAG, ' ')
    sim_utils.log(TAG, [{user[0].uId: (user[0].bid, str(user[0].price).replace('.', ','))} for user in winners])
    return [allocTuple[0] for allocTuple in winners]

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
