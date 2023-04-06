from sim_entities.clock import TimerSingleton
import logging
import utm
from geopy import distance

TAG = 'sim_utils.py'

def calcDistance(point_1, point_2):
    #Sao Paulo's zone number and zone letter
    zone_number = 23
    zone_letter = 'K'

    lat_1, long_1 = utm.to_latlon(point_1[0], point_1[1], zone_number, zone_letter)
    lat_2, long_2 = utm.to_latlon(point_2[0], point_2[1], zone_number, zone_letter)

    distanceRes = distance.distance((lat_1, long_1), (lat_2, long_2)).meters
    return distanceRes

def calcTimeToExec(user, mainGraph, destNode):
    log(TAG, 'calcTimeToExec')
    print(user.lastMove[1], destNode.nId)
    dist = mainGraph.adjList[user.lastMove[1]][destNode.nId][0]
    arrivalTime = dist // user.avgSpeed # A VELOCIMEDIA SE ALTERA! NÃO DÁ PRA CONTAR DESDE O PRIMEIRO NÓ...
    return arrivalTime + user.initTime + 2

def log(fileName, msg):
    logging.info(f'{fileName}: time-step:{TimerSingleton().getTimerValue()} {msg}')