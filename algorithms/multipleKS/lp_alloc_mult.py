from gurobipy import *
import sys
import json
import time
import algorithms.multipleKS.alloc_utils as utils
from sim_entities.cloudlets import CloudletsListSingleton
from sim_entities.users import UsersListSingleton

def buildVMsDict(users):
    return multidict(
        (u.uId, [u.vmType, u.bid, u.reqs.storage, u.reqs.cpu, u.reqs.ram, u.latencyThresholdForAllocate])
            for u in users
    )

def buildCloudletsDict(cloudlets):
    return multidict(
        (c.cId, [c.resources.storage, c.resources.cpu, c.resources.ram])
            for c in cloudlets
    )

# Display optimal values of decision variables
def printSolution(modelOpt, optResult, v_types):
    numAlloc = 0
    print('allocated users: ', end='')
    for v in optResult.keys():
        print((v, v_types[v], optResult[v]), end=', ')
    print("\nnum allocated users:", len(optResult.keys()))
    print("social welfare:", modelOpt.objVal)

def getLatency(n, v):
    user = UsersListSingleton().findById(v)
    cloudlet = CloudletsListSingleton().findById(n)
    latency = utils.getLatency(user, cloudlet)
    return latency

def build(cloudlets, users):
    #vdata = utils.readJSONData(jsonFilePath)

    v_ids, v_types, v_bid, v_storage, v_CPU, v_RAM, v_latThreshold = buildVMsDict(users)
    c_ids, c_storage, c_CPU, c_RAM = buildCloudletsDict(cloudlets)

    m = Model('Cloudlet-VM Allocation')
    m.Params.LogToConsole = 0
    x = m.addVars(c_ids, v_ids, vtype=GRB.BINARY, name="allocate")

    # storage constraint
    for n in c_ids:
        m.addConstr((
            quicksum(v_storage[v]*x[n,v] for v in v_ids) <= c_storage[n]
        ), name='storage[%s]'%n)

    # CPU constraint
    for n in c_ids:
        m.addConstr((
            quicksum(v_CPU[v]*x[n,v] for v in v_ids) <= c_CPU[n]
        ), name='CPU[%s]'%n)

    # RAM constraint
    for n in c_ids:
        m.addConstr((
            quicksum(v_RAM[v]*x[n,v] for v in v_ids) <= c_RAM[n]
        ), name='RAM[%s]'%n)

    # Latency constraint
    for v in v_ids:
        m.addConstr((
            quicksum(getLatency(n,v)*x[n,v] for n in c_ids) <= v_latThreshold[v]
        ), name='LAT[%s]'%v)

    # Allocation constraint
    for v in v_ids:
        m.addConstr((
            quicksum(x[n,v] for n in c_ids) <= 1
        ), name='alloc_constr[%s]'%v)

    expr = (quicksum(v_bid[v]*x[n,v] for n in c_ids for v in v_ids))

    m.setObjective(expr, GRB.MAXIMIZE)

    fileName = "/home/jps/GraphGenFrw/Simulator/exact_formulation.lp"
    m.write(fileName)

    startTime = time.time()
    m.optimize()
    endTime = time.time()
    optResult = getResult(m, c_ids, v_ids)
    printSolution(m, optResult, v_types)
    clSing = CloudletsListSingleton()
    usSing = UsersListSingleton()
    allocRes = [(usSing.findById(v), clSing.findById(c)) for (v,c) in optResult.items()]
    return [m.ObjVal, allocRes]
    

def getResult(model, cloudlets, vms):
    ILPResult = dict()
    for cl in cloudlets:
        for vm in vms:
            if abs(model.getVarByName(f"allocate[{cl},{vm}]").x) > 1e-6:
                ILPResult[vm] = cl
    return ILPResult
    

def pricing(model, optValue, optResult, v_bids, v_ids):
    totalPrices = 0
    userPrice = dict()
    for vm in v_ids:
        if vm in optResult.keys():
            socialWelfare = optValue - v_bids[vm]
            clarkeValue = clarkePivotRule(model, vm, optResult[vm])
            priceToPay = clarkeValue - socialWelfare
            userPrice[vm] = priceToPay
            totalPrices += priceToPay
        else:
            userPrice[vm] = 0
    return [userPrice, totalPrices]

def clarkePivotRule(model, vm, cloudlet):
    model.getVarByName(f"allocate[{cloudlet},{vm}]").ub = 0
    model.optimize()
    clarkeResult = model.ObjVal
    model.getVarByName(f"allocate[{cloudlet},{vm}]").ub = 1
    return clarkeResult

def main(jsonFilePath):    
    build(jsonFilePath)

if __name__ == "__main__":
    inputFilePath = sys.argv[1:][0]
    main(inputFilePath)
