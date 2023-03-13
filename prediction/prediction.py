from markov_main import Markov

class AllocPrediction:
    def __init__(self, users, cloudlets, mainGraph, seed):
        self.users = users
        self.cloudlets = cloudlets
        self.mainGraph = mainGraph
        self.seed = seed

    def predict(self, user):
        probabilities = getProbabilities()
        mc = Markov(self.cloudlets, probabilities, self.seed)
        return mc.nextState(user.allocatedCloudlet)

    def predictAll(self):
        mainResult = []
        for u in self.users:
            result = predict(u)
            mainResult.append(result)
        return mainResult

    def getProbabilities(self):
        # TODO: A METHOD TO IDENTIFY THE CLOUDLETS IN A RADIUS OF X METERS FROM ONE SOURCE CLOUDLET 
        # (IT WILL BE THE CONNECTED CLOUDLETS IN THE GRAPH)
        pass