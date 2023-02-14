from enum import Enum

class Event(Enum):
    MOVE_USER = 0
    ALLOCATE_USER = 1
    INITIAL_ALLOCATION = 2
    CALL_OPT = 3
    CALL_PRICE = 4

    @classmethod
    def executeEvent(eTuple):
        if e[1] == Event.MOVE_USER:
            updateGraph(eTuple)
        elif e[1] == Event.ALLOCATE_USER:
            updateGraph(eTuple)
        elif e[1] == Event.INITIAL_ALLOCATION:
            updateGraph(eTuple)
        elif e[1] == Event.CALL_OPT:
            executeOpt(eTuple) # TODO: the algorothm to allocate will be in the tuple
        elif e[1] == Event.CALL_PRICE:
            executePricing(eTuple) # TODO: Define how to store the prices (maybe in the users' objects)

# TODO: IMPLEMENT TIMIMG -> EACH EVENT MUST HAVE A SPECIFIC TIME TO BE EXECUTED
# I CAN USE IT WITH HEAPQ AND TUPLES