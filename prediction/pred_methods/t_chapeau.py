from prediction.pred_methods.utils.t_chapeau_utils import getPastCloudlets
from prediction.pred_methods.utils.t_chapeau_utils import getFuturePath
from prediction.pred_methods.utils.t_chapeau_utils import calcTChapeau

def calcProbability(user, users, clToCalcPredict, detectedCloudletsPerCloudlet, timeStep):
    pastPath = getPastCloudlets(user, timeStep)

    # Add the current cloudlet of the user in the path
    pastPath.append(clToCalcPredict)

    # Take all T_chapeau of every "possible future": 
    # the last two past cloudlets of the user -> the current -> (possibilities according to the neighbors of the curr cloudlet)
    neighborCloudlets = detectedCloudletsPerCloudlet[clToCalcPredict.cId]
    futurePaths = getFuturePath(pastPath, neighborCloudlets)
    
    # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
    t_chapeau_numerator = calcTChapeau(users, futurePaths, timeStep)

    # Take all T_chapeau of every "possible future^2" (now including two hopes in the future): 
    # the last two past cloudlets of the user -> the current -> (possibilities) -> (possibilities)^2
    secFuturePaths = list()
    for j in range(len(futurePaths)):
        # taking the neighbors of the first possible future cloudlet in the possible future path
        # (which is the last element of each list inside the futurePaths list ([-1]))
        secNeighbors = detectedCloudletsPerCloudlet[futurePaths[j][-1].cId]
        secFuturePaths = getFuturePath(futurePaths[j], secNeighbors)
    
    # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
    t_chapeau_denominator = calcTChapeau(users, secFuturePaths, timeStep)

    return 0 if sum(t_chapeau_denominator.values()) == 0 else sum(t_chapeau_numerator.values())/sum(t_chapeau_denominator.values())