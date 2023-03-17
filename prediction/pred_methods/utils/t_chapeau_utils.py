def getPastCloudlets(user):
    pastCls = list()
    if len(user.pastCloudlets) > 2:
        pastCls.append(user.pastCloudlets[-1])
        pastCls.append(user.pastCloudlets[-2])
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

def calcTChapeau(futurePaths):
    t_chapeau = dict()
    for p in futurePaths:
        t_chapeau[p] = 0
        for u in self.users:
            if isIn(p, u.pastCloudlets):
                t_chapeau[p] += 1
    return t_chapeau
