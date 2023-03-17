from markov_main import Markov

class AllocPrediction:
    def __init__(self, users, cloudlets, mainGraph, seed):
        self.users = users
        self.cloudlets = cloudlets
        self.mainGraph = mainGraph
        self.seed = seed

    def predict(self, user):
        probabilities = getProbabilities(user)
        mc = Markov(self.cloudlets, probabilities, self.seed)
        return mc.nextState(user.allocatedCloudlet)

    def predictAll(self):
        mainResult = []
        for u in self.users:
            result = predict(u)
            mainResult.append((u, result))
        return mainResult

    def getProbabilities(self):
        probabilities = dict()
        # TODO: A METHOD TO IDENTIFY THE CLOUDLETS IN A RADIUS OF X METERS FROM ONE SOURCE CLOUDLET 
        cloudletsNearby = getCloudlets(user.allocatedCloudlet) 

        for c in cloudletsNearby:
            probabilities[c] = 0 # t_chapeau(user, allCloudlets)

        # TODO: fill the probabilities dict with the other cloudlets apart from the getCLoudlets method with probability values as zero
        return probabilities