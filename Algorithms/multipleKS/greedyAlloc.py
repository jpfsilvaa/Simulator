import json, math
import time
import sys
import alloc_utils as utils

def greedyAlloc(cloudlets, vms):
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
            if utils.userFits(chosenUser, occupation):
                utils.allocate(chosenUser, occupation)
                allocatedUsers.append((chosenUser, sortedCloudlets[cloudletPointer]))
                socialWelfare += chosenUser.bid
                del D[userPointer]
            else:
                userPointer += 1
        cloudletPointer += 1
    
    print('num allocated users:', len(allocatedUsers))
    print('allocated users:', [(allocTup[0].id, allocTup[0].vmType, allocTup[1].id) for allocTup in allocatedUsers])
    return [socialWelfare, allocatedUsers, D]

def pricing(winners, densities):
    i = 0
    while i < len(winners):
        occupation = utils.Resources(0, 0, 0) # for identical cloudlets, this is ok, but not for different cloudlets
        winner = winners[i]
        j = 0
        while utils.userFits(winner, occupation) and j < len(densities):
                if densities[j][0].id != winner.id and utils.userFits(densities[j][0], occupation):
                        utils.allocate(densities[j][0], occupation)
                j += 1
        if j == len(densities):
            winner.price = 0
        else:
            winner.price = densities[j-1][1]*winner.maxReq
        printResults(winner, densities[j-1][1])
        i += 1

    return [{user.id: (user.bid, str(user.price).replace('.', ','))} for user in winners]

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
    result = greedyAlloc(cloudlets, userVms)
    endTime = time.time()

    print('social welfare:', result[0])
    print('execution time:', str(endTime-startTime).replace('.', ','))
    #  print('\nprices (user: (bid, price)) : ', pricing(winners=result[1], densities=result[2]))

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)
