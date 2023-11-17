import copy

def getPastCloudlets(user, timeStep):
    pastCls = list()
    if len(user.pastCloudlets) > 2:
        pastCls.append(user.pastCloudlets[timeStep-1][-1])
        pastCls.append(user.pastCloudlets[timeStep-2][-1])
    else:
        # IN THIS CASE, DO WE JUST NOT CONSIDER THE PAST?
        pass
    return pastCls

def getFuturePath(pastPath, neighborCloudlets):
    fPath = list()
    for i in range(len(neighborCloudlets)):
        fPath.append(copy.deepcopy(pastPath))
        fPath[i].append(neighborCloudlets[i])
    return fPath

def calcTChapeau(users, futurePaths, timeStep):
    t_chapeau = dict()
    for p in range(len(futurePaths)):
        t_chapeau[p] = 0
        for u in users:
            if isIn(futurePaths[p], u.pastCloudlets, timeStep):
                t_chapeau[p] += 1
    return t_chapeau

def isIn(p, pastCloudlets, timeStep):
    if len(p) > 1:
        print(f'p: {[c.cId for c in p]}')
        print(f'pastCloudlets: {pastCloudlets}')
        print(f'timeStep: {timeStep}')
        if pastCloudlets[timeStep-1][-1].cId == p[-2].cId and pastCloudlets[timeStep-2][-1].cId == p[-3].cId:
            return True
    return False