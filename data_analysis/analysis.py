import os
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import numpy as np

### Set your path to the folder containing the .csv files
SIM_PATH = '/home/jps/GraphGenFrw/Simulator/'
PATH = f'{SIM_PATH}logfiles/alg' # Use your path

def socialWelfareComparison(algorithms, users, instance):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}5-{users}users/social_welfare_5_{instance}.csv')
    exactCumulative = 0
    algCumulative = 0
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/social_welfare_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        exactCumulative += dfExact['social welfare']
        algCumulative += df['social welfare']
        df['cumulative sum'] = algCumulative/exactCumulative
        df['cumulative sum']*= 100
        df.sort_values(by=['number of users'], inplace=True)
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    sb.swarmplot(x="number of users", y="cumulative sum", data=merged_df, hue='algorithm')
    sb.despine()
    plt.ylabel('Ratio - social welfare achieved/optimal social welfare (%)')
    plt.xlabel('Number of users')
    plt.savefig('sw_comparison.png')
    plt.show()

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
    # Create a figure and two axes objects
    fig, ax = plt.subplots(figsize=(20, 10))

    # Adding labels and title to the graph
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    
    if res == 'ram' or res == 'storage':
        ax.errorbar(df['time-step'], df[f'used {res} avg']/1024, yerr=df[f'used {res} std']/1024, fmt='-o', label=f'Average of used {res}')
        ax.bar(df['time-step'], df[f'unused {res}']/1024, alpha=0.5, label=f'Unused {res}')
        ax.set_ylabel(f'{res.upper()} (GB)')
    else:
        ax.errorbar(df['time-step'], df[f'used {res} avg'], yerr=df[f'used {res} std'], fmt='-o', label=f'Average of used {res}')
        ax.bar(df['time-step'], df[f'unused {res}'], alpha=0.5, label=f'Unused {res}')
        ax.set_ylabel('CPU (Processing units)')
    
    ax.set_title(f'{title} - {alg[1]}')
    ax.legend()

    # Make some labels.
    rects = ax.patches
    labels = [f"{i} cloudlets" for i in df['used cloudlets']]

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
        )

    plt.savefig(f'{SIM_PATH}/data_analysis/res_graphs/{res}_{alg[0]}_comparison.png')
    #plt.show()

    dataframes = []
    dfExact = pd.read_csv(f'{PATH}5-30users/social_welfare_5_1.csv')
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/prices_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        df['prices'] /= dfExact['social welfare']
        dataframes.append(df)

    # Merge dataframes using a common key, such as a timestamp
    merged_df = pd.concat(dataframes)

    # Group the merged dataframe by algorithm and timestamp and calculate the mean
    grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

    # Create a line plot with three lines, each representing one algorithm
    fig, ax = plt.subplots(figsize=(8, 6))

    markers = ['o', '>', 'v', '^', '<']
    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['prices'], label=algorithm, marker=markers.pop())

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Ratio (profit achived/optimal social welfare)')
    ax.set_title('Profit Comparison')
    ax.legend()
    plt.savefig('prices_comparison.png')
    # plt.show()

def pricesComparison(algorithms, users, instance):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}5-{users}users/social_welfare_5_{instance}.csv')
    exactCumulative = 0
    algCumulative = 0
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/prices_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        exactCumulative += dfExact['social welfare']
        algCumulative += df['prices']
        df['cumulative sum'] = algCumulative/exactCumulative
        df['cumulative sum']*= 100
        df.sort_values(by=['number of users'], inplace=True)
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    sb.swarmplot(x="number of users", y="cumulative sum", data=merged_df, hue='algorithm')
    sb.despine()
    plt.ylabel('Ratio - profit achieved/optimal social welfare (%)')
    plt.xlabel('Number of users')
    plt.savefig('prices_comparison.png')
    plt.show()

def generateGraphs(algorithms, users, instance, graphType, x, y, ylabel):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/{graphType}_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        dataframes.append(df)

    merged_df = pd.concat(dataframes)
    sb.swarmplot(x=x, y=y, data=merged_df, hue='algorithm')
    sb.despine()
    plt.ylabel(ylabel)
    plt.savefig(f'{graphType}_comparison.png')
    plt.show()


algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'Cross Edge with QuadTree'), (3, 'Cross Edge'), (4, '2-phases')]
algorithms_ = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
users = 30
instance = 1

# cloudletsUsageComparison(algorithms, users, instance)
generateGraphs(algorithms_, users, instance, 'exec_time', 'number of users', 'exec time', 'execution time (seconds)')
generateGraphs(algorithms_QT, users, instance, 'exec_time', 'number of users', 'exec time', 'execution time (seconds)')
generateGraphs(algorithms_, users, instance, 'latencies', 'number of users', 'avg latency (for the allocated)', 'latency (seconds)')
generateGraphs(algorithms_, users, instance, 'prices', 'number of users', 'number of winners', 'allocated users')
socialWelfareComparison(algorithms_, users, instance)
pricesComparison(algorithms_QT, users, instance)