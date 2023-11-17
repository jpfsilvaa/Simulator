import prediction.pred_methods.t_chapeau as t_c
import random

def predictAll(users, detectedCloudletsPerUser, detectedCloudletsPerCloudlet, timeStep):
    mainResult = []
    for u in users:
        result = predict(u, users, detectedCloudletsPerUser, detectedCloudletsPerCloudlet, timeStep)
        mainResult.append((u, result.entity))
    return mainResult

def predict(user, users, detectedCloudletsPerUser, detectedCloudletsPerCloudlet, timeStep):
    probabilities, cloudlets = getProbabilities(user, users, detectedCloudletsPerUser, detectedCloudletsPerCloudlet, timeStep)
    print(f'cloudlets: {[c.entity.cId for c in cloudlets]}')
    print(f'probabilities: {probabilities}')
    
    if sum(probabilities) == 0:
        for p in range(len(probabilities)):
            probabilities[p] = 1
    
    resultCloudlet = random.choices(cloudlets, weights=probabilities, k=1)
    print(f'resultCloudlet: {resultCloudlet[0].entity.cId}')
    return resultCloudlet[0]
    

def getProbabilities(user, users, detectedCloudletsPerUser, detectedCloudletsPerCloudlet, timeStep):
    probabilities = []
    cloudlets = detectedCloudletsPerUser[user.uId]
    for c in cloudlets:
        probabilities.append(t_c.calcProbability(user, users, c.entity, detectedCloudletsPerCloudlet, timeStep))
    
    return probabilities, cloudlets