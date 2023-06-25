import os
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np

SIM_PATH = '/home/jps/GraphGenFrw/Simulator/'
PATH = f'{SIM_PATH}logfiles/alg'

def cloudletsUsageComparison(algorithms, users, instance):
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/cloudlets_usage_{alg[0]}_{instance}.csv')
        df['time-step'] -= 1
        df['time-step'] /= 60
        df['algorithm'] = alg[1]
        buildGraphForAlg(df, alg)   

def buildGraphForAlg(df, alg):
    buildGraphForRes(df, alg, 'cpu', 'CPU Usage Comparison')
    buildGraphForRes(df, alg, 'storage', 'Storage Usage Comparison')
    buildGraphForRes(df, alg, 'ram', 'RAM Usage Comparison')

def buildGraphForRes(df, alg, res, title):
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    
    ax.errorbar(df['time-step'], df[f'used {res} avg'], yerr=df[f'used {res} std'], fmt='-o', label=f'Average of used {res}')
    ax.bar(df['time-step'], df[f'unused {res}'], alpha=0.5, label=f'Unused {res}')
    ax.set_ylabel(f'{res.upper()} (%)')
    
    ax.set_title(f'{title} - {alg[1]}')
    ax.yaxis.set_ticks(np.arange(0, 1500, 100))
    ax.legend()

    rects = ax.patches
    labels = [f"{i} cloudlets" for i in df['used cloudlets']]

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
        )

    plt.savefig(f'{SIM_PATH}data_analysis/{res}_{alg[0]}_comparison_.png')
    plt.show()

def socialWelfareComparison(algorithms, users, instance, xAxis, xJitterStep, yJitterStep):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}5-{users}users/social_welfare_5_{instance}.csv')
    xJitter = -xJitterStep
    yJitter = -yJitterStep
    y = 'social welfare'
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/social_welfare_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df[xAxis] = df[xAxis].apply(lambda x: x + xJitter)
        df[y] = df[y].apply(lambda y: y + yJitter)
        xJitter += xJitterStep
        yJitter += yJitterStep
        df['time-step'] -= 1
        df['time-step'] /= 30
        df['sw/exact'] = df['social welfare']/dfExact['social welfare']
        df['sw/exact']*= 100
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.scatterplot(x=xAxis, y="sw/exact", data=merged_df, hue='algorithm', alpha=0.6)
    g.legend_.set_title(None)
    sb.despine()
    plt.ylabel('SW achieved/optimal SW (%)')
    plt.xlabel(xAxis)
    plt.xticks(np.arange(20, 110, 10))
    plt.savefig('sw_comparison_100_cumulative.png')
    plt.show()

def pricesComparison(algorithms, users, instance, xAxis, xJitterStep, yJitterStep):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}5-{users}users/social_welfare_5_{instance}.csv')
    xJitter = -xJitterStep
    yJitter = -yJitterStep
    yExact = 'social welfare'
    yAlg = 'prices'
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{yAlg}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df[xAxis] = df[xAxis].apply(lambda x: x + xJitter)
        df[yAlg] = df[yAlg].apply(lambda y: y + yJitter)
        xJitter += xJitterStep
        yJitter += yJitterStep
        df['time-step'] -= 1
        df['time-step'] /= 30
        df['prices/exact'] = df[yAlg]/dfExact[yExact]
        df['prices/exact']*= 100
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.scatterplot(x=xAxis, y="prices/exact", data=merged_df, hue='algorithm', alpha=0.6)
    g.legend_.set_title(None)
    sb.despine()
    plt.ylabel('profit achieved/optimal social welfare (%)')
    plt.xlabel(xAxis)
    plt.savefig('prices_comparison_100.png')
    plt.show()

def generateGraphsLine(algorithms, users, instance, graphType, x, y, ylabel, fileName):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 30
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.lineplot(x=x, y=y, data=merged_df, hue='algorithm', errorbar=('ci', 1), alpha=0.6)
    g.legend_.set_title(None)
    
    plt.ylabel(ylabel)
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

def generateGraphs(algorithms, users, instance, graphType, x, y, 
                                ylabel, fileName, xJitterStep, yJitterStep):
    dataframes = []
    xJitter = -xJitterStep
    yJitter = -yJitterStep
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df[x] = df[x].apply(lambda x: x + xJitter)
        df[y] = df[y].apply(lambda y: y + yJitter)
        xJitter += xJitterStep
        yJitter += yJitterStep
        df.sort_values(by=x, inplace=True)
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.scatterplot(x=x, y=y, data=merged_df, hue='algorithm', alpha=0.7)
    g.legend_.set_title(None)
    sb.despine()
    plt.ylabel(ylabel)
    plt.xticks(np.arange(20, 110, 10))
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree'), (1, 'Greedy'), 
                                                (3, 'Cross Edge'), (4, '2-phases'), (5, 'VCG')]
algorithms_ = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
users = 100
instance = 11
byTimeStep = 'time-step'
byUsers = 'number of users'

# cloudletsUsageComparison(algorithms_, users, instance)

# generateGraphsLine(algorithms, users, instance, 'exec_time', byUsers, 'exec time', 
#                    'execution time (seconds)', 'exec_time_100')

# generateGraphsLine(algorithms_QT, users, instance,  'exec_time', byUsers, 'exec time', 
#                   'execution time (seconds)', 'exec_time_QT_100_line')

generateGraphsLine(algorithms_, users, instance, 'latencies', byTimeStep, 
                'avg latency (for the allocated)', 'latency (seconds)', 
               'lat_100') 

# generateGraphsLine(algorithms_, users, instance, 'prices', byUsers, 'number of winners', 
#                  'winnner users', 'winners_100')

# socialWelfareComparison(algorithms_, users, instance, byUsers, xJitterStep=1.2, yJitterStep=0)

# pricesComparison(algorithms_, users, instance, byUsers, xJitterStep=1.2, yJitterStep=0)