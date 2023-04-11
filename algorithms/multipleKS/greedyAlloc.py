import json, math
import time
import sys
import algorithms.multipleKS.alloc_utils as utils
import sim_utils
import logging

TAG = 'greedyAlloc.py'

def greedyAlloc(cloudlets, vms):
    sim_utils.log(TAG, 'greedyAlloc')
    sortedCloudlets = utils.sortCloudletsByType(cloudlets, True)
    normalVms = utils.normalize(sortedCloudlets[0], vms)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)

    allocatedUsers = []
    socialWelfare = 0
    cloudletPointer = 0

    while cloudletPointer < len(sortedCloudlets):
        userPointer = 0
        occupation = utils.Resources(0, 0, 0)

        while (utils.isNotFull(occupation)) and userPointer < len(D):
            chosenUser = D[userPointer][0]
            if (utils.userFits(chosenUser, occupation) 
                    and utils.checkLatencyThreshold(chosenUser, sortedCloudlets[cloudletPointer])):
                utils.allocate(chosenUser, occupation)
                allocatedUsers.append((chosenUser, sortedCloudlets[cloudletPointer]))
                socialWelfare += chosenUser.bid
                del D[userPointer]
            else:
                userPointer += 1
        cloudletPointer += 1
    
    sim_utils.log(TAG, f'num allocated users: {len(allocatedUsers)}')
    sim_utils.log(TAG, f'allocated users: {[(allocTup[0].uId, allocTup[0].vmType, allocTup[1].cId) for allocTup in allocatedUsers]}')
    return [socialWelfare, allocatedUsers, D]

def pricing(winners, densities):
    sim_utils.log(TAG, 'pricing')
    i = 0
    while i < len(winners):
        occupation = utils.Resources(0, 0, 0) # for identical cloudlets, this is ok, but not for different cloudlets
        winner = winners[i][0]
        j = 0
        while utils.userFits(winner, occupation) and j < len(densities):
                if densities[j][0].uId != winner.uId and utils.userFits(densities[j][0], occupation):
                        utils.allocate(densities[j][0], occupation)
                j += 1
        if j == len(densities):
            winner.price = 0 # It means the user always fits
        else:
            winner.price = densities[j-1][1]*winner.maxReq
        i += 1

    return [{user[0].uId: (user[0].bid, str(user[0].price).replace('.', ','))} for user in winners]

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
