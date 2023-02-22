import sys
import json, math
import time
import numpy as np
import alloc_utils as utils

def dynProgAlloc(cloudlet, userVms):
    CPU_UNIT = 2000
    GB_UNIT = 1024
    CLOUDLET_CPU = int(cloudlet.coords.cpu/CPU_UNIT)+1
    CLOUDLET_RAM = int(cloudlet.coords.ram/GB_UNIT)+1
    CLOUDLET_STORAGE = int(cloudlet.coords.storage/GB_UNIT)+1
    userVms.insert(0, utils.UserVM('', '', 0, utils.Resources(0, 0, 0))) # adding 'empty' user in the first position of the list for the algorithm

    T = np.full((len(userVms)+1, 
                    CLOUDLET_CPU, 
                    CLOUDLET_RAM, 
                    CLOUDLET_STORAGE), 0)
    
    for i in range(len(userVms)):
        for j in range(CLOUDLET_CPU):
            for k in range(CLOUDLET_RAM):
                for l in range(CLOUDLET_STORAGE):
                    userCPU = int(userVms[i].reqs.cpu/CPU_UNIT)
                    userRAM = int(userVms[i].reqs.ram/GB_UNIT)
                    userSTORAGE = int(userVms[i].reqs.storage/GB_UNIT)
                    if (userCPU <= j 
                        and userRAM <= k 
                        and userSTORAGE <= l):
                        T[i][j][k][l] = max(T[i-1][j][k][l],
                                                T[i-1][j-userCPU][k-userRAM][l-userSTORAGE]+userVms[i].bid)
                    else:
                        T[i][j][k][l] = T[i-1][j][k][l]
    
    S = []
    socialWelfare = 0
    alpha = CLOUDLET_CPU-1 # descreasing 1 for acessing the array values
    beta = CLOUDLET_RAM-1
    gama = CLOUDLET_STORAGE-1
    for i in range(len(userVms)-1, 0, -1):
        if T[i-1, alpha, beta, gama] != T[i, alpha, beta, gama]:
            S.append(userVms[i])
            socialWelfare += userVms[i].bid
            alpha -= int(userVms[i].reqs.cpu/CPU_UNIT)
            beta -= int(userVms[i].reqs.ram/GB_UNIT)
            gama -= int(userVms[i].reqs.storage/GB_UNIT)
    
    print('num allocated users:', len(S))
    print('allocated users:', [(user.id, user.vmType) for user in S])
    
    #preparing data for the pricing algorithm
    normalWinners = utils.normalize(cloudlet, S)
    utils.calcDensitiesByMax(normalWinners) # this function update the maxCoord value of eah user

    del userVms[0]
    normalVms = utils.normalize(cloudlet, userVms)
    D = utils.calcDensitiesByMax(normalVms)
    D.sort(key=lambda a: a[1], reverse=True)

    return [socialWelfare, normalWinners, D]

def printResults(winner, criticalValue):
    print('-----------')
    print('user id ->', winner.id)
    print('vmType ->', winner.vmType)
    print('critical value (b_j/w_j)->', criticalValue)
    print('winner density (b_i/w_i)->', winner.bid/winner.maxCoord)
    print('winner bid (b_i)->', winner.bid)
    print('winner maxCoord (w_i)->', winner.maxCoord)
    print('winner price->', winner.price)

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
            winner.price = densities[j-1][1]*winner.maxCoord
        printResults(winner, densities[j-1][1])
        i += 1

    return [{user.id: (user.bid, str(user.price).replace('.', ','))} for user in winners]

def main(jsonFilePath):
    data = utils.readJSONData(jsonFilePath)
    cloudlet = utils.buildCloudlet(data['Cloudlets'])
    userVms = utils.buildUserVms(data['UserVMs'])
    startTime = time.time()
    result = dynProgAlloc(cloudlet, userVms)
    endTime = time.time()

    print('social welfare:', result[0])
    print('execution time:', str(endTime-startTime).replace('.', ','))
    # print('\nprices (user: (bid, price)) : ', pricing(winners=result[1], densities=result[2]))

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)