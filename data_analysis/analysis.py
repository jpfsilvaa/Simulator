import os
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np
import re

SIM_PATH = '/home/jps/GraphGenFrw/Simulator/'
PATH = f'{SIM_PATH}logfiles/alg'

def cloudletsUsageComparison(algorithms, users, instance):
    dataframes = []
    timeStep = 'time-step'
    xJitterStep = 0.13
    xJitter = -0.2
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/cloudlets_usage_{alg[0]}_{instance}.csv')
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
    ax.set_yticks(np.arange(0, 1001, 100))
    bar_width = 0.5
    bar_positions = np.arange(len(dfs[0]['time-step']))
    offset = bar_width / 4
    offsetFactor = -1.5
    for i in range(len(dfs)):
        ax.bar(bar_positions + offsetFactor*offset, dfs[i][f'unused {res}'], 
               width=bar_width/4, align='center', label=dfs[i]['algorithm'][0],
               alpha=0.5)
        offsetFactor += 1
    ax.set_ylabel(f'[bars] SUM of unused {res.upper()} (%)', fontsize=14)
    
    ax.set_title(f'{title}')
    ax.legend()

    ax2 = ax.twinx()
    for i in range(len(dfs)):
        ax2.errorbar(dfs[i]['time-step'], dfs[i][f'used {res} avg'], 
                     yerr=0, fmt='-o', markersize=4,
                     label=f'Average of used {res}', capsize=5)
    ax2.set_ylabel(f'[lines] AVERAGE used {res.upper()} (%)', fontsize=14)
    ax2.set_yticks(np.arange(0, 101, 10))

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
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/1/{inputFile}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        cumulativeSW = [df[yAxis][0]]
        for row_index in range(1, len(df)):
            cumulativeSW.append(cumulativeSW[row_index-1] + df[yAxis][row_index])
        df[cumulative] = cumulativeSW
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    plt.figure(figsize=(8, 6))
    g = sb.lineplot(x=xAxis, y=cumulative, data=merged_df, hue='algorithm')
    g.legend_.set_title(None)
    g.set_xticks(np.arange(0, len(dataframes[0][xAxis]), 1))
    sb.despine()
    plt.ylabel(f'cumulative {yAxis} ($)')
    plt.xlabel(f'{xAxis} (minutes)')
    plt.yticks(np.arange(0, 200001, 25000))
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
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/{graphType}_{alg[0]}_{instance}.csv')
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

def plotResUsage(algorithms, users, instance, graphType, x, y, ylabel, fileName ,res):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df[x] -= 1
        df[x] /= 60
        dataframes.append(df)

    bar_width = 0.5
    bar_positions = np.arange(len(dataframes[0][x]))
    offset = bar_width / 4

    fourth_bar_width = 1.2*bar_width

    fig, ax = plt.subplots()

    ax.bar(bar_positions - 2.05*offset, dataframes[0]['used cloudlets']*100, width=bar_width/4, align='edge', alpha=0.5, color='white', edgecolor='blue', linestyle="--", label=f"Sum of {res} from cloudlets considered by {dataframes[0]['algorithm'][0]}")
    ax.bar(bar_positions - 1.5*offset, dataframes[0][y]*dataframes[0]['used cloudlets'], width=bar_width/4, align='center', label=f"{res} used by {dataframes[0]['algorithm'][0]}")
    ax.bar(bar_positions - 1.05*offset, dataframes[1]['used cloudlets']*100, width=bar_width/4, align='edge', alpha=0.5, color='white', edgecolor='orange', linestyle="--", label=f"Sum of {res} from cloudlets considered by {dataframes[1]['algorithm'][0]}")
    ax.bar(bar_positions - 0.5*offset, dataframes[1][y]*dataframes[1]['used cloudlets'], width=bar_width/4, align='center', label=f"{res} used by {dataframes[1]['algorithm'][0]}")
    ax.bar(bar_positions - 0.05*offset, dataframes[2]['used cloudlets']*100, width=bar_width/4, align='edge', alpha=0.5, color='white', edgecolor='green', linestyle="--", label=f"Sum of {res} from cloudlets considered by {dataframes[2]['algorithm'][0]}")
    ax.bar(bar_positions + 0.5*offset, dataframes[2][y]*dataframes[2]['used cloudlets'], width=bar_width/4, align='center', label=f"{res} used by {dataframes[2]['algorithm'][0]}")
    ax.bar(bar_positions + 1.05*offset, dataframes[3]['used cloudlets']*100, width=bar_width/4, align='edge', alpha=0.5, color='white', edgecolor='red', linestyle="--", label=f"Sum of {res} from cloudlets considered by {dataframes[3]['algorithm'][0]}")
    ax.bar(bar_positions + 1.5*offset, dataframes[3][y]*dataframes[3]['used cloudlets'], width=bar_width/4, align='center', label=f"{res} used by {dataframes[3]['algorithm'][0]}")

    ax.set_xlabel(f'{x} (minutes)')
    ax.set_ylabel(ylabel)
    ax.set_xticks(bar_positions)
    ax.set_yticks(np.arange(0, 1001, 100))
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

def buildBoxplot(algorithms, users, instance, yType, x, y, ylabel, fileName, cutGroups):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/{yType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        dataframes.append(df)

    combinedDf = pd.DataFrame()
    for df in dataframes:
        combinedDf[df['algorithm'][0]] = df[y]

    plt.figure(figsize=(10, 6))
    g = sb.boxplot(data=pd.melt(combinedDf), x='variable', y='value')
    plt.xlabel('')
    plt.ylabel(ylabel)
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()

def buildBoxplot_VMTypes(algorithms, users, instance, yType, x, y, ylabel, fileName):
    dataframes = []
    alg_names = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/{yType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        alg_names.append(alg[1])
        df['time-step'] -= 1
        df['time-step'] /= 60
        df['gp1'] = 0
        df['gp2'] = 0
        df['ramIntensive'] = 0
        df['cpuIntensive'] = 0
        for idx, row in df.iterrows():
            df.at[idx, 'gp1'] = len(re.findall(r"'gp1'", row['result list']))
            df.at[idx, 'gp2'] = len(re.findall(r"'gp2'", row['result list']))
            df.at[idx, 'ramIntensive'] = len(re.findall(r"'ramIntensive'", row['result list']))
            df.at[idx, 'cpuIntensive'] = len(re.findall(r"'cpuIntensive'", row['result list']))
        dataframes.append(df)
    
    combinedDf_gp1 = pd.DataFrame()
    combinedDf_gp2 = pd.DataFrame()
    combinedDf_ramIntensive = pd.DataFrame()
    combinedDf_cpuIntensive = pd.DataFrame()
    for df in dataframes:
        combinedDf_gp1[df['algorithm'][0]] = df['gp1']
        combinedDf_gp2[df['algorithm'][0]] = df['gp2']
        combinedDf_ramIntensive[df['algorithm'][0]] = df['ramIntensive']
        combinedDf_cpuIntensive[df['algorithm'][0]] = df['cpuIntensive']
    combinedDf_gp1['type'] = "gp1"
    combinedDf_gp2['type'] = "gp2"
    combinedDf_ramIntensive['type'] = "ramIntensive"
    combinedDf_cpuIntensive['type'] = "cpuIntensive"
    
    combinedDf = pd.concat([combinedDf_gp1, combinedDf_gp2, combinedDf_ramIntensive, combinedDf_cpuIntensive])
    melted_data = pd.melt(combinedDf, id_vars=['type'], value_vars=alg_names, var_name='Category', value_name='Values')
    # print(melted_data)

    plt.figure(figsize=(10, 6))
    g = sb.boxplot(x='Category', y='Values', data=melted_data, hue='type')
    plt.xlabel('')
    plt.ylabel('number of winners')
    plt.savefig(f'{fileName}_comparison.png')
    plt.show()
    

def addPercentageColumns(df):
    resources = ['cpu', 'ram', 'storage']
    for resource in resources:
        for index, value in df[f'c.{resource}(full/unused)'].items():
                formattedValue = value.replace('(', '').replace(')', '')
                full, unused = formattedValue.split(',')
                usedCpu = (float(full) - float(unused)) / float(full) 
                df.loc[index, f'used {resource} (%)'] = usedCpu * 100

def readCloudletsStates(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/0/cloudlets_states_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        for index, value in df['c.currUsersAllocated'].items():
            if value == '[]':
                df.drop(index, inplace=True)
        addPercentageColumns(df)
        dataframes.append(df)
    return dataframes

def buildBoxplotForCloudlets(algorithms, users, instance):
    dfs = readCloudletsStates(algorithms, users, instance)
    combinedDf = pd.concat(dfs)
    resources = ['cpu', 'ram', 'storage']
    for resource in resources:
        plt.figure(figsize=(14, 8))
        g = sb.boxplot(data=combinedDf, x='time-step', y=f'used {resource} (%)', hue='algorithm')
        g.legend_.set_title(None)
        # define x tick labels as integer values
        xticks = g.get_xticks()
        g.set_xticklabels(xticks.astype(int))
        plt.xlabel('time-step')
        plt.ylabel(f'used {resource} (%)')
        plt.savefig(f'cloudlets_{resource}_comparison.png')
        plt.show()

def buildExecTime(algorithms, users, instance, x, y, ylabel, fileName):
    datasets = []
    for alg in algorithms:
        algDatasets = []
        for i in range(20):
            filename = f'{PATH}{alg[0]}-{users}users/{i}/exec_time_{alg[0]}_11.csv'
            dataset = pd.read_csv(filename)
            dataset['time-step'] -= 1
            dataset['time-step'] /= 60
            dataset['total time'] = dataset['exec time'] + dataset['pricing time']
            algDatasets.append(dataset)
        datasets.append(algDatasets)
    
    combinedData = [{} for _ in range(len(algorithms))]
    for i, algDatasets in enumerate(datasets):
        for dataset in algDatasets:
            for index, row in dataset.iterrows():
                x_value = row[x]
                y_value = row['total time']

                if x_value not in combinedData[i]:
                    combinedData[i][x_value] = []
                combinedData[i][x_value].append(y_value)
    
    x_values = []
    averages = []
    std_deviations = []

    for alg in range(len(algorithms)):
        alg_x_values = []
        alg_averages = []
        alg_std_deviations = []
        sortedKeys = sorted(combinedData[alg].keys())
        for x_value in sortedKeys:
            alg_x_values.append(x_value)
            alg_averages.append(np.mean(combinedData[alg][x_value]))
            alg_std_deviations.append(np.std(combinedData[alg][x_value]))
        x_values.append(alg_x_values)
        averages.append(alg_averages)
        std_deviations.append(alg_std_deviations)
    
    fig, axs = plt.subplots(2, height_ratios=[1, 5], gridspec_kw={'hspace': 0.02}, sharex=True, figsize=(10, 6))

    axs[0].bar(x_values[0], datasets[0][0]['number of users'], color='white', edgecolor='black', linestyle="--")
    axs[0].tick_params(left = False, right = False , labelleft = False ,
                labelbottom = False, bottom = False)
    axs[0].spines['top'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['bottom'].set_visible(False)
    axs[0].spines['left'].set_visible(False)
    for i in range(len(x_values[0])):
        axs[0].text(x_values[0][i], datasets[0][0]['number of users'][i]+10, str(datasets[0][0]['number of users'][i]), ha='center', va='center')

    for i in range(len(algorithms)):
        axs[1].plot(x_values[i], averages[i], label=algorithms[i][1])
        # axs[1].fill_between(x_values[i], np.subtract(averages[i],std_deviations[i]), 
        #                 np.add(averages[i],std_deviations[i]), alpha=0.5)

    plt.legend(loc='upper right')
    plt.xlabel(x)
    plt.xticks(x_values[0])
    plt.ylabel('auction exec time (seconds)')
    plt.show()

def buildTwoPhasesComparison(users, instance, x):
    y = 'two-phases time'
    datasets = []
    for i in range(1, 20):
        filename = f'{PATH}4-{users}users/{i}/exec_time_4_11.csv'
        dataset = pd.read_csv(filename)
        dataset['time-step'] -= 1
        dataset['time-step'] /= 60
        dataset['phase 1'] = 0
        dataset['phase 2'] = 0
        for index, row in dataset.iterrows():
            dataset.loc[index, 'phase 1'] = float(dataset.loc[index, 'two-phases time'].split(',')[0].replace('[', ''))
            dataset.loc[index, 'phase 2'] = float(dataset.loc[index, 'two-phases time'].split(',')[1].replace(']', ''))
        datasets.append(dataset)

    combinedDataPhase1 = {}
    combinedDataPhase2 = {}
    for dataset in datasets:
        for index, row in dataset.iterrows():
            x_value = row[x]
            phase1 = row['phase 1']
            phase2 = row['phase 2']

            if x_value not in combinedDataPhase1:
                combinedDataPhase1[x_value] = []
            combinedDataPhase1[x_value].append(phase1)

            if x_value not in combinedDataPhase2:
                combinedDataPhase2[x_value] = []
            combinedDataPhase2[x_value].append(phase2)

    averagesPhase1 = []
    averagesPhase2 = []
    std_deviationsPhase1 = []
    std_deviationsPhase2 = []
    sortedKeys = sorted(combinedDataPhase1.keys())
    for x_value in sortedKeys:
        averagesPhase1.append(np.mean(combinedDataPhase1[x_value]))
        std_deviationsPhase1.append(np.std(combinedDataPhase1[x_value]))
        averagesPhase2.append(np.mean(combinedDataPhase2[x_value]))
        std_deviationsPhase2.append(np.std(combinedDataPhase2[x_value]))
    print(f'phase 1: {averagesPhase1}\n')
    print(f'std phase 1: {std_deviationsPhase1}\n\n')
    print(f'phase 2: {averagesPhase2}\n\n')
    print(f'std phase 2: {std_deviationsPhase2}\n')
    print(f'x values: {sortedKeys}\n\n')
    plt.stackplot(sortedKeys, averagesPhase1, averagesPhase2, labels=['phase 1', 'phase 2'])
    plt.xlabel(x)
    plt.ylabel('time (seconds)')
    plt.legend(['phase 1', 'phase 2'])
    plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'GSOTO with QuadTree'), (3, 'GSOTO'), (4, '2-phases'), (5, 'ILP')]
algorithms_cQT = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'GSOTO with QuadTree'), (3, 'GSOTO')]
algorithms_ = [(0, 'Greedy with QuadTree'), (2, 'GSOTO with QuadTree'), (4, '2-phases'), (5, 'VCG')]
algorithms_noVCG = [(0, 'Greedy with QuadTree'), (2, 'GSOTO'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'GSOTO with QuadTree')]
users = 100
instance = 11
byTimeStep = 'time-step'
byUsers = 'number of users'

# buildBoxplot_VMTypes(algorithms_, users, instance, 'alloc_results', byUsers, 'number of winners', 'price (USD)', 'vm_types_100')

# buildExecTime(algorithms_, users, instance, byTimeStep, 'exec time', 'execution time (seconds)', 'exec_time_100')

# buildTwoPhasesComparison(users, instance, byTimeStep) # vai virar uma frase só, sem grafico

# plotWinners(algorithms_, 100, instance, 'prices', byTimeStep, 'number of winners', 'number of winners', 'winners_100')

# plotResUsage(algorithms_, users, instance, 'cloudlets_usage', byTimeStep, 'used cpu avg', 'used cpu (%)', 'cpu_250', 'CPU')
# plotResUsage(algorithms_, users, instance, 'cloudlets_usage', byTimeStep, 'used ram avg', 'used ram (%)', 'ram_100','RAM')
# plotResUsage(algorithms_, users, instance, 'cloudlets_usage', byTimeStep, 'used storage avg', 'used storage (%)', 'storage_100', 'Storage')

# buildBoxplot(algorithms_, users, instance, 'latencies', byUsers, 
#             'avg latency (for the allocated)', 'latency (seconds)', 'lat_100', False)

# swAndProfitComparison(algorithms_, users, instance, byTimeStep, 'social welfare')
swAndProfitComparison(algorithms_, users, instance, byTimeStep, 'prices')

# buildBoxplot(algorithms_, users, instance, 'prices', byUsers, 
#               'number of winners', 'winner users', 'winners_bp', False)

# ---------------------------------------------------------------------------

# plotLatencyByComp(algorithms_, users, instance, 'latencies', byTimeStep, 
#                'avg latency (for the allocated)', 'how much worse (%)',
#               'lat_100')

# generateGraphsLine(algorithms, users, instance, 'exec_time', byUsers, 'exec time', 
#                    'execution time (seconds)', 'exec_time_100')

# generateGraphsLine(algorithms_QT, users, instance,  'exec_time', byUsers, 'exec time', 
#                   'execution time (seconds)', 'exec_time_QT_100_line')

# generateGraphsLine(algorithms_, users, instance, 'latencies', byTimeStep, 
#                 'avg latency (for the allocated)', 'latency (seconds)', 
#                'lat_100') 

# generateGraphsLine(algorithms_, users, instance, 'prices', byTimeStep, 'number of winners', 
#                'winnner users', 'winners_100', 0.1, 0)