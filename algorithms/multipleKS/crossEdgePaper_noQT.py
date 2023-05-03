import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging
import copy

TAG = 'crossEdgePaper_noQT.py'

# Algorithm from the paper: https://doi.org/10.1016/j.comcom.2021.09.035
# The thing here is that they use the sum of the resources to calculate the densities,
# but also, they sort the cloudlets by type in decreasing order
def crossEdgeAlg(cloudlets, vms):
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
    cloudletPointer = 0
    initTimeLoop = time.time()
    while cloudletPointer < len(cloudlets):
        userPointer = 0
        occupation = utils.Resources(0, 0, 0)

        while (utils.isNotFull(occupation)) and userPointer < len(D):
            chosenUser = D[userPointer][0]
            if (utils.userFits(chosenUser, occupation) 
                    and utils.checkLatencyThreshold(chosenUser, cloudlets[cloudletPointer])):
                utils.allocate(chosenUser, occupation)
                allocatedUsers.append((chosenUser, cloudlets[cloudletPointer]))
                socialWelfare += chosenUser.bid
                del D[userPointer]
            else:
                userPointer += 1
        cloudletPointer += 1
    finalTime = time.time()
    sim_utils.log(TAG, f'elapsed loop time: {finalTime - initTimeLoop}')
    sim_utils.log(TAG, f'elapsed total time: {finalTime - initTime}')
    sim_utils.log(TAG, f'num allocated users: {len(allocatedUsers)} / {len(vms)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return [socialWelfare, allocatedUsers, utils.calcDensitiesByMax(normalVms)]

def pricing(winners, cloudlets):
    sim_utils.log(TAG, 'pricing')

    for w in winners:
        normalizedCls = [utils.Resources(0, 0, 0) for c in cloudlets]
        w[0].price = float('inf')
        winners_ = [winner for winner in winners if winner[0].uId != w[0].uId]
        D_ = utils.calcDensitiesBySum([w[0] for w in winners_])
        D_.sort(key=lambda a: a[1], reverse=True)
        j = 0
        while j < len(D_):
            for cloudletIdx in range(len(cloudlets)):
                if j < len(D_):
                    currentUser = D_[j][0]
                    if utils.userFits(currentUser, normalizedCls[cloudletIdx]) \
                        and utils.checkLatencyThreshold(currentUser, cloudlets[cloudletIdx]):
                        utils.allocate(currentUser, normalizedCls[cloudletIdx])
                        w[0].price = min(w[0].price, D_[j][1]*w[0].maxReq)
                        # This increment is not in the paper's pseudocode, but it is necessary 
                        # to avoid allocating the same user to multiple cloudlets
                        j += 1
                else:
                    break
            j += 1
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
