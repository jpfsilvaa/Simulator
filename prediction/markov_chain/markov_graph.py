import pydtmc as mc

class Markov:
    def __init__(self, cloudlets, probabilities, seed):
        self.states = [c.cId for c in cloudlets]
        self.probabilities = probabilities
        self.currState = ''
        self.history = []
        self.mChain = mc.MarkovChain(self.probabilities, self.states)
    
    @property
    def printMC(self):
        print(self.mChain)

    def nextState(self, currState):
        history.append(currState)
        self.currState = self.mChain.next(self.currState, self.seed)
        return self.currState