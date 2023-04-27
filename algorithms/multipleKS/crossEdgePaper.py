import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging

TAG = 'crossEdgePaper.py'

# Algorithm from the paper: https://doi.org/10.1016/j.comcom.2021.09.035
# The thing here is that they use the sum of the resources to calculate the densities,
# but also, they sort the cloudlets by type in decreasing order
def greedyAlloc(cloudlets, vms):
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
    quadtree = utils.buildQuadtree(cloudlets, vms)
    detectedCloudletsPerUser = utils.detectCloudletsFromQT(vms, quadtree) # dict: uId -> list of cloudlets

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
    return [socialWelfare, allocatedUsers, quadtree]

# The paper's authors use Critical Pricing
# TODO: NEED FIX ACCORDING TO THE QUADTREE APPROACH
def pricing(winners, cloudlets, quadtree):
    sim_utils.log(TAG, 'pricing')
    detectedUsersPerCloudlet = utils.detectUsersFromQT(cloudlets, winners[0][0], quadtree)

    for w in winners:
        cloudletOccupation = utils.Resources(0, 0, 0)
        w[0].price = w[0].bid
        possibleVms = detectedUsersPerCloudlet[w[1].cId]
        normalVms = utils.normalize(cloudlets[0], possibleVms)
        D_ = utils.calcDensitiesBySum(normalVms)
        D_.sort(key=lambda a: a[1], reverse=True)
        j = 0
        while j < len(D_):
            currentUser = D_[j][0]
            if utils.userFits(currentUser, cloudletOccupation):
                utils.allocate(currentUser, cloudletOccupation)
                w[0].price = min(w[0].price, D_[j][1]*w[0].maxReq)
            j += 1
    sim_utils.log(TAG, [{w[0].uId: (w[0].bid, str(w[0].price).replace('.', ','))} for w in winners])
    return [allocTuple[0] for allocTuple in winners]

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
