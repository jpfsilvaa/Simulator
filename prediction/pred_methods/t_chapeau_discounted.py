import copy
from sim_entities.clock import TimerSingleton
from sim_entities.predictions import PredictionsSingleton
from prediction.utils import getPastCloudlets
from prediction.utils import getFuturePath
from prediction.utils import calcTChapeau

class T_ChapeauDiscounted:

    def __init__(self, users, cloudlets):
        self.graph = graph
        self.users = users # maybe I can just use the singleton
        self.cloudlets = cloudlets # maybe I can just use the singleton
    
    def calcTChapeauPast(futurePaths):
        t_chapeau = dict()
        for p in secFuturePaths:
            t_chapeau[p] = 0
            for u in self.users:
                if isIn(p, u.pastCloudlets[:-1]): #THIS IS THE SECRET! TO CONSIDER THE TIME-STEP BEFORE, I JUST DON'T CONSIDER THE LAST PAST CLOUDLET
                    t_chapeau[p] += 1
        return t_chapeau

    def getDiscountFactor(clToCalcPredict):
        pastPredictions = PredictionsSingleton().getPredictionsAndResFromTimestep(timeStep - TimerSingleton().getDelta())
        usersInAlpha = 0
        usersWithGoodPrediction = 0
        for p in pastPredictions:
            predictedRes = p[0]
            for u, c in predictedRes:
                if u.pastCloudlets[-1].cId == clToCalcPredict.cId:
                    usersInAlpha += 1
                    # if the prediction was right, the curr allocated cloudlet will be the predicted
                    if u.allocatedCloudlet.cId == c.cId:
                        usersWithGoodPrediction += 1
        
        return usersWithGoodPrediction/usersInAlpha

    def calcTChapeauSum(user, clToCalcPredict, futureLevel, discountFactor):
        # -----CALCULATING THE T_CHAPEAU FROM TIME-STEP t:
        pastPath = getPastCloudlets(user)

        # Add the current cloudlet of the user in the path
        pastPath.append(clToCalcPredict)

        # Take all T_chapeau of every "possible future": 
        # the last two past cloudlets of the user -> the current -> (possibilities according to the neighbors of the curr cloudlet)
        neighborCloudlets = getNeighborCloudlets(3*clToCalcPredict.coverageArea, clToCalcPredict)
        futurePaths = getFuturePath(pastPath, neighborCloudlets)

        # Take all T_chapeau of every "possible future^2" (now including two hopes in the future): 
        # the last two past cloudlets of the user -> the current -> (possibilities) -> (possibilities)^2
        secFuturePaths = list()
        for j in range(len(futurePaths)):
            # taking the neighbors of the first possible future cloudlet in the possible future path
            # (which is the last element of each list inside the futurePaths list)
            secNeighbors = getNeighborCloudlets(3*futurePaths[j][-1].coverageArea, futurePaths[j][-1])
            secFuturePaths = getFuturePath(futurePaths[j], secNeighbors)
        
        if futureLevel == 1:
            t_chapeau_X = calcTChapeau(futurePaths)
            t_chapeau_past = getTChapeauPast(futurePaths)
        else:
            t_chapeau_X = calcTChapeau(secFuturePaths)        
            t_chapeau_past = getTChapeauPast(secFuturePaths)
        
        return ((t_chapeau_X.values()) + discountFactor * (t_chapeau_past.values()))
        

    def predict(self, timeStep, user, clToCalcPredict):
        # ----- CALCULATING THE DISCOUNT FACTOR
        deltaT = getDiscountFactor(clToCalcPredict)

        # --- NUMERATOR: THE SUM OF T_CHAPEU WITH THE PATH (alpha'', alpha', alpha, future¹)
        numeratorSum = calcTChapeauSum(user, clToCalcPredict, 1, deltaT)

        # --- DENOMINATOR: THE SUM OF T_CHAPEAU WITH THE PATH (alpha'', alpha', alpha, future¹, future²)
        denominatorSum = calcTChapeauSum(user, clToCalcPredict, 2, deltaT)

        return numeratorSum/denominatorSum