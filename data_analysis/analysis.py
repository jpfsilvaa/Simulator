import os
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np

SIM_PATH = '/home/jps/GraphGenFrw/Simulator/'
PATH = f'{SIM_PATH}logfiles/alg'

def cloudletsUsageComparison(algorithms, users, instance):
    dataframes = []
    timeStep = 'time-step'
    xJitterStep = 0.13
    xJitter = -0.2
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/cloudlets_usage_{alg[0]}_{instance}.csv')
        df[timeStep] -= 1
        df[timeStep] /= 60
        df[timeStep] = df[timeStep].apply(lambda x: x + xJitter)
        xJitter += xJitterStep
        df['algorithm'] = alg[1]
        dataframes.append(df)
    buildGraphForRes(dataframes, 'cpu', 'CPU Usage Comparison')
    buildGraphForRes(dataframes, 'storage', 'Storage Usage Comparison')
    buildGraphForRes(dataframes, 'ram', 'RAM Usage Comparison')   

def buildGraphForRes(dfs, res, title):
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.set_xlabel('time-step (minutes)')
    ax.set_xticks(np.arange(0, len(dfs[0]['time-step']), 1))
    bar_width = 0.5
    bar_positions = np.arange(len(dfs[0]['time-step']))
    offset = bar_width / 4
    offsetFactor = -1.5
    for i in range(len(dfs)):
        ax.bar(bar_positions + offsetFactor*offset, dfs[i][f'unused {res}'], 
               width=bar_width/4, align='center', label=dfs[i]['algorithm'][0],
               alpha=0.5)
        offsetFactor += 1
    ax.set_ylabel(f'sum of unused {res.upper()} (%)', color='blue', fontsize=14)
    
    ax.set_title(f'{title}')
    ax.legend()

    ax2 = ax.twinx()
    for i in range(len(dfs)):
        ax2.errorbar(dfs[i]['time-step'], dfs[i][f'used {res} avg'], 
                     yerr=dfs[i][f'used {res} std'], fmt='-o', markersize=4,
                     label=f'Average of used {res}', capsize=5)
    ax2.set_ylabel(f'average {res.upper()} usage (%)', color='red', fontsize=14)

    # rects = ax.patches
    # labels = [f"{i} cloudlets" for i in df['used cloudlets']]

    # for rect, label in zip(rects, labels):
    #     height = rect.get_height()
    #     ax.text(
    #         rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
    #     )

    plt.savefig(f'{SIM_PATH}data_analysis/{res}_comparison_.png')
    plt.show()

def swAndProfitComparison(algorithms, users, instance, xAxis, yAxis):
    dataframes = []
    cumulative = 'cumulative'
    inputFile = yAxis if yAxis == 'prices' else 'social_welfare'
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{inputFile}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        cumulativeSW = [df[yAxis][0]]
        for row_index in range(1, len(df)):
            cumulativeSW.append(cumulativeSW[row_index-1] + df[yAxis][row_index])
        df[cumulative] = cumulativeSW
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.lineplot(x=xAxis, y=cumulative, data=merged_df, hue='algorithm')
    g.legend_.set_title(None)
    g.set_xticks(np.arange(0, len(dataframes[0][xAxis]), 1))
    sb.despine()
    plt.ylabel(f'cumulative {yAxis} ($)')
    plt.xlabel(f'{xAxis} (minutes)')
    plt.savefig(f'{yAxis}_comparison_100.png')
    plt.show()

def generateGraphsLine(algorithms, users, instance, graphType, x, y, ylabel, fileName, xJitterStep, yJitterStep):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    g = sb.lineplot(x=x, y=y, data=merged_df, hue='algorithm', errorbar=('ci', 1), alpha=0.6)
    g.legend_.set_title(None)
    g.set_xticks(np.arange(0, len(dataframes[0][x]), 1))
    
    plt.ylabel(ylabel)
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

def plotWinners(algorithms, users, instance, graphType, x, y, ylabel, fileName):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df[x] -= 1
        df[x] /= 30
        dataframes.append(df)

    bar_width = 0.5
    bar_positions = np.arange(len(dataframes[0][x]))
    offset = bar_width / 4

    fourth_bar_width = 1.2*bar_width

    fig, ax = plt.subplots()

    ax.bar(bar_positions - 2.4*offset, dataframes[0]['number of users'], width=fourth_bar_width, align='edge', alpha=0.5, color='white', edgecolor='black', linestyle="--", label='Users in the system')
    ax.bar(bar_positions - 1.5*offset, dataframes[0][y], width=bar_width/4, align='center', label=dataframes[0]['algorithm'][0])
    ax.bar(bar_positions - 0.5*offset, dataframes[1][y], width=bar_width/4, align='center', label=dataframes[1]['algorithm'][0])
    ax.bar(bar_positions + 0.5*offset, dataframes[2][y], width=bar_width/4, align='center', label=dataframes[2]['algorithm'][0])
    ax.bar(bar_positions + 1.5*offset, dataframes[3][y], width=bar_width/4, align='center', label=dataframes[3]['algorithm'][0])

    ax.set_xlabel(f'{x} (minutes)')
    ax.set_ylabel(ylabel)
    ax.set_xticks(bar_positions)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.legend()
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

def plotLatencyByComp(algorithms, users, instance, graphType, x, y, ylabel, fileName):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        dataframes.append(df)
    
    fig, axs = plt.subplots(2, figsize=(10, 6), height_ratios=[1, 10])
    plt.subplots_adjust(hspace=0.1)
    axs[0].bar(dataframes[0]['time-step'], dataframes[0]['number of users'], color='purple', alpha=0.2, width=0.8)
    axs[0].set_xticks([])
    axs[0].set_yticks([])
    axs[0].set_ylim([0, 150])
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['bottom'].set_visible(False)
    axs[0].spines['left'].set_visible(False)
    axs[0].spines['right'].set_visible(False)

    rects = axs[0].patches
    labels = [f"{i} users" for i in df['number of users']]
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        axs[0].text(
            rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom", fontsize=6
        )

    for row_index in range(len(dataframes[0])):
        row_values = []
        for df in dataframes:
            row_values.append(df.loc[row_index, y])
        min_value = min(row_values)
        for df in dataframes:
            df.loc[row_index, y] = ((df.loc[row_index, y] - min_value)/min_value) * 100
    
    merged_df = pd.concat(dataframes)
    g = sb.lineplot(ax=axs[1], x=x, y=y, data=merged_df, hue='algorithm', errorbar=('ci', 1), alpha=0.6)
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
        df['time-step'] -= 1
        df['time-step'] /= 30
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
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

def buildBoxplot(algorithms, users, instance, yType, x, y, ylabel, fileName):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{yType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        dataframes.append(df)

    combinedDf = pd.concat(dataframes)
    combinedDf['group'] = pd.cut(combinedDf[x], bins=range(0, 131, 35), right=False, include_lowest=True)

    plt.figure(figsize=(10, 6))

    g = sb.boxplot(data=combinedDf, x='group', y=y, hue='algorithm')
    g.legend_.set_title(None)
    plt.xlabel(x)
    plt.ylabel(ylabel)
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'Cross Edge'), 
              (3, 'Cross Edge with QuadTree'), (4, '2-phases')]
algorithms_ = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge'), (4, '2-phases'), (5, 'VCG')]
algorithms_noVCG = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
users = 100
instance = 11
byTimeStep = 'time-step'
byUsers = 'number of users'

# plotWinners(algorithms_, users, instance, 'prices', byTimeStep, 'number of winners', 'number of winners', 'winners_100')

# buildBoxplot(algorithms_, users, instance, 'latencies', byUsers, 
#              'avg latency (for the allocated)', 'latency (seconds)', 'lat_100')

buildBoxplot(algorithms_, users, instance, 'cloudlets_usage', byUsers,
                'used cpu avg', 'cpu usage (%)', 'cpu_boxplot')

buildBoxplot(algorithms_, users, instance, 'cloudlets_usage', byUsers,
                'used ram avg', 'ram usage (%)', 'ram_boxplot')

buildBoxplot(algorithms_, users, instance, 'cloudlets_usage', byUsers,
                'used storage avg', 'storage usage (%)', 'storage_boxplot')

# plotLatencyByComp(algorithms_, users, instance, 'latencies', byTimeStep, 
#                'avg latency (for the allocated)', 'how much worse (%)',
#               'lat_100')

# cloudletsUsageComparison(algorithms_, users, instance)

# generateGraphsLine(algorithms, users, instance, 'exec_time', byUsers, 'exec time', 
#                    'execution time (seconds)', 'exec_time_100')

# generateGraphsLine(algorithms_QT, users, instance,  'exec_time', byUsers, 'exec time', 
#                   'execution time (seconds)', 'exec_time_QT_100_line')

# generateGraphsLine(algorithms_, users, instance, 'latencies', byTimeStep, 
#                 'avg latency (for the allocated)', 'latency (seconds)', 
#                'lat_100') 

# generateGraphsLine(algorithms_, users, instance, 'prices', byTimeStep, 'number of winners', 
#                'winnner users', 'winners_100', 0.1, 0)

# swAndProfitComparison(algorithms_, users, instance, byTimeStep, 'social welfare')
# swAndProfitComparison(algorithms_noVCG, users, instance, byTimeStep, 'prices')