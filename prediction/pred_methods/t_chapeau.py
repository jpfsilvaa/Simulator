import copy

class T_Chapeau:

    def __init__(self, users, cloudlets, graph):
        self.graph = graph
        self.users = users # maybe I can just use the singleton
        self.cloudlets = cloudlets # maybe I can just use the singleton
    
    def predict(self, user, clToCalcPredict):
        # Take the last two past cloudlet from the user
        pastPath = list()
        if len(self.users.pastCloudlets) > 2:
            # TODO: take the last two cloudlets
            pastPath.append(self.users[-1])
            pastPath.append(self.users[-2])
        else:
            # IN THIS CASE, DO WE JUST NOT CONSIDER THE PAST?
            pass

        # Add the current cloudlet of the user in the path
        pastPath.append(clToCalcPredict)

        # Take all T_chapeau of every "possible future": 
        # the last two past cloudlets of the user -> the current -> (possibilities according to the neighbors of the curr cloudlet)
        neighborCloudlets = getNeighborCloudlets(3*clToCalcPredict.coverageArea, clToCalcPredict)
        
        futurePaths = list()
        for i in range(len(neighborCloudlets)):
            futurePaths.append(copy.deepcopy(pastPath))
            futurePaths[i].append(neighborCloudlets[i])

        # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
        t_chapeau_1 = dict()
        for p in futurePaths:
            t_chapeau_1[p] = 0
            for u in self.users:
                if isIn(p, u.pastCloudlets):
                    t_chapeau_1[p] += 1

        # Take all T_chapeau of every "possible future^2" (now including two hopes in the future): 
        # the last two past cloudlets of the user -> the current -> (possibilities) -> (possibilities)^2
        secFuturePaths = list()
        for j in range(len(futurePaths)):
            # taking the neighbors of the first possible future cloudlet in the possible future path
            # (which is the last element of each list inside the futurePaths list)
            secNeighbors = getNeighborCloudlets(3*futurePaths[j][-1].coverageArea, futurePaths[j][-1])
            for k in range(len(secNeighbors)):
                secFuturePaths.append(copy.deepcopy(futurePaths[j]))
                secFuturePaths[k].append(secNeighbors[k])
        
        # Count how many users did each of these possible paths (i.e., calc each T_chapeau)
        t_chapeau_2 = dict()
        for p in secFuturePaths:
            t_chapeau_2[p] = 0
            for u in self.users:
                if isIn(p, u.pastCloudlets):
                    t_chapeau_1[p] += 1
        return sum(t_chapeau_1.values())/sum(t_chapeau_2.values())

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