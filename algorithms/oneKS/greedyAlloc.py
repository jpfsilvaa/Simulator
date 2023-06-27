import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging

TAG = 'greedyAlloc_OneKS.py'

def greedyAlloc_OneKS(cloudlet, vms):
    sim_utils.log(TAG, 'greedyAlloc')

    initTime = time.time()
    normalVms = utils.normalize(cloudlet, vms)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)

    occupation = utils.Resources(0, 0, 0)
    allocatedUsers = []
    socialWelfare = 0
    # userPointer = 0

    initTimeLoop = time.time()
    for d in D:
        currentUser = d[0]
        if utils.userFits(currentUser, occupation) and utils.checkLatencyThreshold(currentUser, cloudlet):
            utils.allocate(currentUser, occupation)
            allocatedUsers.append((currentUser, cloudlet))
            socialWelfare += currentUser.bid
    finalTime = time.time()

    sim_utils.log(TAG, f'elapsed loop time: {finalTime - initTimeLoop}')
    sim_utils.log(TAG, f'elapsed total time: {finalTime - initTime}')
    sim_utils.log(TAG, f'allocated users / total users: {len(allocatedUsers)} / {len(vms)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return [socialWelfare, allocatedUsers]

def pricing(winners, users):
    sim_utils.log(TAG, 'pricing')

    for w in winners:
        sim_utils.log(TAG, f'pricing for user {w[0].uId}')
        normalVms = utils.normalize(w[1], users)
        D = utils.calcDensitiesByMax(normalVms)
        D.sort(key=lambda a: a[1], reverse=True)

        occupation = utils.Resources(0, 0, 0)
        for d in D:
            sim_utils.log(TAG, f'pricing for user {w[0].uId} - user {d[0].uId}')
            currentUser = d[0]
            if utils.userFits(currentUser, occupation) and utils.checkLatencyThreshold(currentUser, w[1]):
                utils.allocate(currentUser, occupation)
            if not utils.userFits(w[0], occupation):
                if w[0].price > 0:
                    w[0].price = min(w[0].price, d[1] * w[0].maxReq)
                else:
                    w[0].price = d[1] * w[0].maxReq
                sim_utils.log(TAG, f'new price for user {w[0].uId}: {w[0].price}')
                sim_utils.log(TAG, f'bid WINNER\'S BID {w[0].uId}: {w[0].bid}')
                sim_utils.log(TAG, f'BID < PRICE? {w[0].bid < w[0].price}')
                break 
    return winners

def printResults(winner, criticalValue):
    print('-----------')
    print('user id ->', winner.id)
    print('vmType ->', winner.vmType)
    print('critical value (b_j/w_j)->', criticalValue)
    print('winner density (b_i/w_i)->', winner.bid/winner.maxReq)
    print('winner bid (b_i)->', winner.bid)
    print('winner maxCoord (w_i)->', winner.maxReq)
    print('winner price->', winner.price)

def main(jsonFilePath):
    data = utils.readJSONData(jsonFilePath)
    cloudlet = utils.buildCloudlet(data['Cloudlets'])
    userVms = utils.buildUserVms(data['UserVMs'])
    startTime = time.time()
    result = greedyAlloc(cloudlet, userVms)
    endTime = time.time()

    print('social welfare:', result[0])
    print('execution time:', str(endTime-startTime).replace('.', ','))
    print('\nprices (user: (bid, price)) : ', pricing(winners=result[1], densities=result[2]))

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)
