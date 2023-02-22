import sys
import json, math
import time
import numpy as np
import alloc_utils as utils

def findLType(alpha, beta, gama):
    if alpha <= beta and beta <= gama:
        return 1
    elif alpha <= gama and gama <= beta:
        return 2
    elif beta <= alpha and alpha <= gama:
        return 3
    elif beta <= gama and gama <= alpha:
        return 4
    elif gama <= alpha and alpha <= beta:
        return 5
    elif gama <= beta and beta <= alpha:
        return 6

def dynProgAlloc(cloudlet, userVms):
    CLOUDLET_CPU = 1
    CLOUDLET_RAM = 1
    CLOUDLET_STORAGE = 1
    COMBINATIONS_L = 6

    normalizedVms = utils.normalize(cloudlet, userVms)
    P = sum(normalizedVms[i].bid for i in normalizedVms)
    normalizedVms.insert(0, utils.UserVM('', '', 0, utils.Resources(0, 0, 0))) # adding 'empty' user in the first position of the list for the algorithm

    T = np.full((len(normalizedVms)+1, 
                    P+1, 
                    COMBINATIONS_L+1), (0, 0, 0))
    
    for i in range(len(normalizedVms)+1):
        for p in range(P+1):
            for l in range(COMBINATIONS_L+1):
                if p <= normalizedVms[i].bid:
                    T[i][p][l] = T[i-1][p][l]
                else:   
                    (alpha, beta, gama) = T[i-1][p][l]
                    l_ = findLType(alpha + normalizedVms[i].reqs.cpu,
                            beta + normalizedVms[i].reqs.ram,
                            gama + normalizedVms[i].reqs.storage)
                    if (alpha + normalizedVms[i].reqs.cpu <= CLOUDLET_CPU and
                            beta + normalizedVms[i].reqs.ram <= CLOUDLET_RAM and
                            gama + normalizedVms[i].reqs.storage <= CLOUDLET_STORAGE):
                            T[i][p][l_] = min(T[i-1][p][l_], 
                                                (alpha + normalizedVms[i].reqs.cpu, 
                                                beta + normalizedVms[i].reqs.ram, 
                                                gama + normalizedVms[i].reqs.storage)) # TODO: HOW CAN I GET THE MININUM BETWEEN TRIPLETS?
    
    v_star = 0 # TODO: THE MAXIMUM VALUE P SUCH THAR T[n][v_star][l] <= (CLOUDLET_CPU, CLOUDLET_RAM, CLOUDLET_STORAGE) FOR l = 1 TO 6
    l = 0 # TODO: LET l BE THE STATE WHERE T[n][v_star][l] <= (CLOUDLET_CPU, CLOUDLET_RAM, CLOUDLET_STORAGE)
    S = []
    (A, B, C) = T[n][v_star][l]
    for i in range(len(userVms)-1, 0, -1):
        if T[i-1][v][l] != T[i][v][l]:
            S.append(userVms[i])
            ()
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