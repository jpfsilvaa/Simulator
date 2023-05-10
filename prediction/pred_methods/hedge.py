class Hedge:
    
    def __init__(self, users, cloudlets):
        self.users = users
        self.cloudlets = cloudlets
    
    # FOR EACH PAST PATH, I WILL CALL THIS FUNCTION
    def hedgeAlg(self, cloudlets, pastPath, timeSlots):
        weights = [1 for _ in range(cloudlets)]
        # for every past time-slots
        for t in timeSlots:
            # draw an expert from the probability distribution of the weights
            expert = self.drawExpert(weights)

            # calculate the loss of the expert
            loss = self.calcLoss(expert)

            # update the weights of the loss
            weights = self.updateWeights(weights, loss)
    
    def drawExpert(self, weights):
        # fore every weight, calculate the probability of being chosen, where p_i = w_i / sum(w)
        # then, draw a random number between 0 and 1, and check which expert was chosen
        for i in range(len(weights)):
            weights[i] = weights[i] / sum(weights)

    def calcLoss(self, expert):
        # The loss will be how much the expert was wrong
        
        pass

    def updateWeights(self, weights, loss):
        pass

