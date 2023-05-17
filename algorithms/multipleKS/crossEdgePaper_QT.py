import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging

TAG = 'crossEdgePaper_QT.py'

# Algorithm from the paper: https://doi.org/10.1016/j.comcom.2021.09.035
# The thing here is that they use the sum of the resources to calculate the densities (profits),
# but also, they sort the cloudlets by type in decreasing order
def crossEdgeAlg(cloudlets, vms, detectedCloudletsPerUser):
    sim_utils.log(TAG, 'crossEdgeAlg')
    # For homogeneous cloudlets, the step below is not necessary
    # But for heterogeneous cloudlets, it is necessary and I should do it only once instead of every opt call
    # sortedCloudlets = utils.sortCloudletsByType(cloudlets, True)
    initTime = time.time()
    normalVms = utils.normalize(cloudlets[0], vms)
    D = utils.calcDensitiesBySum(normalVms)
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

def pricing(winners, users, detectedCloudletsPerUser, cloudlets):
    sim_utils.log(TAG, 'pricing')

    normalVms = utils.normalize(cloudlets[0], users)
    D = utils.calcDensitiesBySum(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)


    for w in winners:
        allocatedUsers = []
        cloudletsOccupation = {c.cId: utils.Resources(0, 0, 0) for c in cloudlets}
        for d in D:
            if d[0].uId == w[0].uId:
                continue
            timeToDetect = time.time()
            cloudletsDetected = detectedCloudletsPerUser[d[0].uId]
            for c in cloudletsDetected:
                if utils.userFits(d[0], cloudletsOccupation[c.entity.cId]):
                    utils.allocate(d[0], cloudletsOccupation[c.entity.cId])
                    allocatedUsers.append((d[0], c.entity))
                    break
            cloudletsWinner = detectedCloudletsPerUser[w[0].uId]
            stillFits = False
            for c in cloudletsWinner:
                if utils.userFits(w[0], cloudletsOccupation[c.entity.cId]):
                    stillFits = True
                    break
            if not stillFits:
                w[0].price = d[1]*w[0].reqsSum
                break
        sim_utils.log(TAG, f'price > bid? {w[0].price > w[0].bid}')
        sim_utils.log(TAG, f'w[0].bid/w[0].reqsSum: {w[0].bid/w[0].reqsSum}')
        sim_utils.log(TAG, f'w[0].reqsSum: {w[0].reqsSum}')
        sim_utils.log(TAG, f'w[0].price: {w[0].price} and w[0].bid: {w[0].bid}')
        sim_utils.log(TAG, ' ')
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
    cloudlets = utils.buildCloudlet(data['Cloudlets'])
    userVms = utils.buildUserVms(data['UserVMs'])
    startTime = time.time()
    result = greedyMMD(cloudlets, userVms)
    endTime = time.time()

    print('social welfare:', result[0])
    print('execution time:', str(endTime-startTime).replace('.', ','))
    #  print('\nprices (user: (bid, price)) : ', pricing(winners=result[1], densities=result[2]))

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)
