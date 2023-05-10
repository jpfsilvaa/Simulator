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


def pricing(winners, users, detectedUsersPerCloudlet, cloudlets):
    sim_utils.log(TAG, 'pricing')

    for w in winners:
        sim_utils.log(TAG, f'WINNER: {w[0].uId}')
        cloudletOccupation = utils.Resources(0, 0, 0)
        w[0].price = 0
        possibleVms = detectedUsersPerCloudlet[w[1].cId]
        normalVms = utils.normalize(cloudlets[0], possibleVms)
        normalVms_ = [v for v in normalVms if v.uId != w[0].uId]    
        D_ = utils.calcDensitiesBySum(normalVms_)
        D_.sort(key=lambda a: a[1], reverse=True)
        sim_utils.log(TAG, f'densities-> {[d[1] for d in D_]}')
        allocatedUsers = []
        
        j = 0
        while utils.userFits(w[0], cloudletOccupation) and j < len(D_):
            currentUser = D_[j][0]
            if utils.userFits(currentUser, cloudletOccupation):
                utils.allocate(currentUser, cloudletOccupation)
                allocatedUsers.append(j)
            j += 1

        sim_utils.log(TAG, f'allocated users indexes -> {allocatedUsers}')
        if j >= len(D_):
            sim_utils.log(TAG, f'everyone fits in cloudlet {w[1].cId}')
            w[0].price = 0
        else:
            w[0].price = D_[j-1][1]*w[0].maxReq
            sim_utils.log(TAG, f'last user allocated j->{j}')
            sim_utils.log(TAG, f'w[0].maxReq: {w[0].maxReq}')
            sim_utils.log(TAG, f'{w[0].price > w[0].bid}')
            sim_utils.log(TAG, f'w[0].price: {w[0].price} and w[0].bid: {w[0].bid}')
            sim_utils.log(TAG, ' ')
    sim_utils.log(TAG, [{w[0].uId: (w[0].bid, str(w[0].price).replace('.', ','))} for w in winners])
    return [allocTuple for allocTuple in winners]

""" def pricing(winners, users, cloudlets):
    sim_utils.log(TAG, 'pricing')
    normalUsers = utils.normalize(cloudlets[0], users)
    for w in winners:
        normalizedCls = [utils.Resources(0, 0, 0) for c in cloudlets]
        w[0].price = float('inf')
        users_ = [u for u in normalUsers if u.uId != w[0].uId]
        D_ = utils.calcDensitiesByMax(users_)
        D_.sort(key=lambda a: a[1], reverse=True)
        D_2 = copy.deepcopy(D_)
        sim_utils.log(TAG, [d[1] for d in D_])
        for cloudletIdx in range(len(cloudlets)):
            j = 0
            while j < len(D_):
                currentUser = D_[j][0]
                if utils.userFits(currentUser, normalizedCls[cloudletIdx]) \
                    and utils.checkLatencyThreshold(currentUser, cloudlets[cloudletIdx]):
                    if utils.userFits(w[0], normalizedCls[cloudletIdx]):
                        utils.allocate(currentUser, normalizedCls[cloudletIdx])
                        del D_[j]
                    else:
                        w[0].price = (D_2[j-1][0].bid/D_2[j-1][0].maxReq)*w[0].maxReq
                        print('price for user ', w[0].uId, ' is ', w[0].price)
                        print('w[0].bid -> ', w[0].bid)
                        break
                j += 1
        # is the price bigger than the bid?
        sim_utils.log(TAG, f'w[0].maxReq: {w[0].maxReq}')
        sim_utils.log(TAG, f'{w[0].price > w[0].bid}')
        sim_utils.log(TAG, f'w[0].price: {w[0].price} and w[0].bid: {w[0].bid}')
        sim_utils.log(TAG, ' ')
    sim_utils.log(TAG, [{user[0].uId: (user[0].bid, str(user[0].price).replace('.', ','))} for user in winners])
    return [w for w in winners] """

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