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
    userPointer = 0

    initTimeLoop = time.time()
    while (utils.isNotFull(occupation)) and userPointer < len(D):
        chosenUser = D[userPointer][0]
        if utils.userFits(chosenUser, occupation) and utils.checkLatencyThreshold(chosenUser, cloudlet):
            utils.allocate(chosenUser, occupation)
            allocatedUsers.append((chosenUser, cloudlet))
            socialWelfare += chosenUser.bid
        userPointer += 1
    finalTime = time.time()

    pricing(allocatedUsers, cloudlet, vms)
    sim_utils.log(TAG, f'elapsed loop time: {finalTime - initTimeLoop}')
    sim_utils.log(TAG, f'elapsed total time: {finalTime - initTime}')
    sim_utils.log(TAG, f'allocated users / total users: {len(allocatedUsers)} / {len(vms)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return [socialWelfare, allocatedUsers]

def pricing(winners, cloudlet, users):
    sim_utils.log(TAG, 'pricing')

    for w in winners:
        normalVms = utils.normalize(cloudlet, users)
        D = utils.calcDensitiesByMax(normalVms)
        D.sort(key=lambda a: a[1], reverse=True)

        occupation = utils.Resources(0, 0, 0)
        userPointer = 0

        while (utils.isNotFull(occupation)) and userPointer < len(D):
            chosenUser = D[userPointer][0]
            if chosenUser.uId != w[0].uId:
                if utils.userFits(chosenUser, occupation):
                    utils.allocate(chosenUser, occupation)
                    if not utils.userFits(w[0], occupation):
                        w[0].price = D[userPointer][1]*w[0].maxReq
                        sim_utils.log(TAG, f'new price for user {w[0].uId}: {w[0].price}')
                        sim_utils.log(TAG, f'BID < PRICE? {w[0].bid < w[0].price}')
                        break 
            userPointer += 1
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
