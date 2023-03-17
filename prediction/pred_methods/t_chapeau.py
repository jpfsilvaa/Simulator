import copy
from prediction.utils import getPastCloudlets
from prediction.utils import getFuturePath
from prediction.utils import calcTChapeau

class T_Chapeau:

    def __init__(self, users, cloudlets, graph):
        self.graph = graph
        self.users = users # maybe I can just use the singleton
        self.cloudlets = cloudlets # maybe I can just use the singleton

    def predict(self, user, clToCalcPredict):
        pastPath = getPastCloudlets(user)

        # Add the current cloudlet of the user in the path
        pastPath.append(clToCalcPredict)

        # Take all T_chapeau of every "possible future": 
        # the last two past cloudlets of the user -> the current -> (possibilities according to the neighbors of the curr cloudlet)
        neighborCloudlets = getNeighborCloudlets(3*clToCalcPredict.coverageArea, clToCalcPredict)
        futurePaths = getFuturePath(pastPath, neighborCloudlets)
        
        # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
        t_chapeau_numerator = calcTChapeau(futurePaths)

        # Take all T_chapeau of every "possible future^2" (now including two hopes in the future): 
        # the last two past cloudlets of the user -> the current -> (possibilities) -> (possibilities)^2
        secFuturePaths = list()
        for j in range(len(futurePaths)):
            # taking the neighbors of the first possible future cloudlet in the possible future path
            # (which is the last element of each list inside the futurePaths list ([-1]))
            secNeighbors = getNeighborCloudlets(3*futurePaths[j][-1].coverageArea, futurePaths[j][-1])
            secFuturePaths = getFuturePath(futurePaths[j], secNeighbors)
        
        # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
        t_chapeau_denominator = calcTChapeau(secFuturePaths)

        return sum(t_chapeau_numerator.values())/sum(t_chapeau_denominator.values())

    def getNeighborCloudlets(self, radius, centerCl):
        result = list()
        centerClNode = self.graph.findNodeById(centerCl.nodeId)
        for c in self.cloudlets:
            cNode = self.graph.findNodeById(c.nodeId)
            dist = ((cNode.posX - centerClNode.posX) ** 2) + ((cNode.posY - centerClNode.posY) ** 2)
            if dist < radius ** 2:
                result.append(c)
        return c
    
    def isIn(pattern, sequence):
        for i in range(len(sequence) - len(pattern) + 1):
            if sequence[i:i+len(pattern)] == pattern:
                return True
        return False