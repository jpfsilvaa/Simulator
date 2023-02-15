import json, math
import time
import sys
import alloc_utils as utils

def greedyAlloc(cloudlet, vms):
    normalVms = utils.normalize(cloudlet, vms)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)

    occupation = utils.Resources(0, 0, 0)
    allocatedUsers = []
    socialWelfare = 0
    userPointer = 0

    while (utils.isNotFull(occupation)) and userPointer < len(D):
        chosenUser = D[userPointer][0]
        if utils.userFits(chosenUser, occupation):
            utils.allocate(chosenUser, occupation)
            allocatedUsers.append(chosenUser)
            socialWelfare += chosenUser.bid
        userPointer += 1
    
    print('num allocated users:', len(allocatedUsers))
    print('allocated users:', [(user.id, user.vmType) for user in allocatedUsers])
    return [socialWelfare, allocatedUsers, D]

def pricing(winners, densities):
    i = 0
    while i < len(winners):
        occupation = utils.Resources(0, 0, 0)
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
