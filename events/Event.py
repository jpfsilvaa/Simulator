from enum import Enum
import classes
import Algorithms.multipleKS as algs

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    CALL_PRICE = 4

    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)

    @classmethod
    def executeEvent(users, cloudlets, eTuple):
        eventType = eTuple[2]
        if eventType == Event.MOVE_USER:
            moveUser(users, cloudlets, eTuple) # TODO
        elif eventType == Event.ALLOCATE_USER:
            allocateUser(users, cloudlets, eTuple) # TODO
        elif eventType == Event.INITIAL_ALLOCATION:
            initialAlloc(users, cloudlets, eTuple) # TODO
        elif eventType == Event.CALL_OPT:
            optimizeAlloc(users, cloudlets, eTuple)  # TODO
        elif eventType == Event.CALL_PRICE:
            pass

def moveUser(users, cloudlets, eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (userID, destNodeID, graphs)
    """
        This event will be important for the prediction
        TODO: WHEN TO CALL IT?
            - If I have the whole path and timing, I can call this multiple times at the beginning of the simulation
            - I can also call it only for the next 2 (for example) hopes
    """
    userID = eTuple[3][0]
    destNodeID = eTuple[3][1]
    userIndex = findUserById(userID)
    users[userIndex].currNode = destNodeID
    users[userIndex].currLatency = latencyFunction(users[userIndex], eTuple[3][2][0])

def latencyFunction(user, mainGraph):
    # TODO: TALVEZ SERIA MELHOR ESSA FUNÇÃO FICAR EM OUTRO ARQUIVO
    # TODO: vou precisar descobrir como saber a distancia fisica do mapa entre os nós (não necessariamente pelos arcos...)
    distance = checkDistance(user.currNode, user.allocatedCloudlet, mainGraph)
    return distance * 0.01

def allocateUser(users, cloudlets, eTuple):
    # TUPLE FORMAT: (time to execute, eventID, event type, contentSubtuple)
    # contentSubtuple: (userID, cloudletID, graphs)
    userID = eTuple[3][0]
    cloudletID = eTuple[3][1]
    userIndex = findUserById(userID)
    cloudletIndex = findCloudletById(cloudletID)
    user = users[userIndex]
    cloudlet = cloudlets[cloudletIndex]

    user.latency = latencyFunction(user, eTuple[3][2][0])
    # TODO: Maybe we can save the old allocated cloudlet to  use for allocation
    user.allocatedCloudlet = cloudlet
    
    cloudlet.resources.cpu -= user.reqs.cpu
    cloudlet.resources.ram -= user.reqs.ram
    cloudlet.resources.storage -= user.reqs.storage
    cloudlet.currUsersAllocated.append(user)



def initialAlloc(users, cloudlets, eTuple):
    """
        Function to make the initial allocation of the simulation
        Possibilities:
            - Run an allocation algorithm at the beggining, according to the initial positions of the users
            - Allocate arbitrarly
        Necessary information inside the tuple
            - all users and all cloudlets (tthe graphs, basically)
            - TODO: ALL USERS WILL START AT THE SAME TIME???
                - We might have users arriving/starting in the middle of the simulation
                
    """
    result = algs.greedyAlloc(cloudlets, users)
    # TODO: CALL THE EVENT FOR ALLOCATE EACH USER ACCORDING TO THE RESULT


def optimizeAlloc(users, cloudlets, eTuple):
    """
        Function to call the optimization algorithm for allocating the users
        Necessary information inside the tuple:
            - chosen algorithm to optimize (maybe a number given at the beginning of the simulation)
            - all graphs
    """
    result = algs.greedyAlloc(cloudlets, users)
    # TODO: CALL THE EVENT FOR ALLOCATE EACH USER ACCORDING TO THE RESULT