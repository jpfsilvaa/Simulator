import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### Set your path to the folder containing the .csv files
SIM_PATH = '/home/jps/GraphGenFrw/Simulator/'
PATH = f'{SIM_PATH}logfiles/alg' # Use your path

def latencyComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/latencies_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        dataframes.append(df)

    # Merge dataframes using a common key, such as a timestamp
    merged_df = pd.concat(dataframes)

    # Group the merged dataframe by algorithm and timestamp and calculate the mean
    grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

    # Create a line plot with three lines, each representing one algorithm
    fig, ax = plt.subplots(figsize=(10, 6))

    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['avg latency (for the allocated)'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Latency (seconds)')
    ax.set_title('Latency Comparison')
    ax.legend()
    plt.savefig('latency_comparison.png')
    # plt.show()

def execTimeComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/exec_time_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        dataframes.append(df)

    # Merge dataframes using a common key, such as a timestamp
    merged_df = pd.concat(dataframes)

    # Group the merged dataframe by algorithm and timestamp and calculate the mean
    grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

    # Create a line plot with three lines, each representing one algorithm
    fig, ax = plt.subplots(figsize=(8, 6))

    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['exec time'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Execution Time (seconds)')
    ax.set_title('Execution Time Comparison')
    ax.legend()
    plt.savefig('exec_time_comparison_noQT.png')
    # plt.show()

def socialWelfareComparison(algorithms, users, instance):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}8-30users/social_welfare_8_1.csv')
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/social_welfare_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['time-step'] -= 1
        df['time-step'] /= 60
        df['social welfare'] /= dfExact['social welfare']
        dataframes.append(df)

    # Merge dataframes using a common key, such as a timestamp
    merged_df = pd.concat(dataframes)

    # Group the merged dataframe by algorithm and timestamp and calculate the mean
    grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

    # Create a line plot with three lines, each representing one algorithm
    fig, ax = plt.subplots(figsize=(8, 6))

    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['social welfare'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Ratio (social welfare achieved/optimal social welfare)')
    ax.set_title('Social Welfare Comparison')
    ax.legend()
    plt.savefig('social_welfare_comparison.png')
    # plt.show()

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

    # Plotting the line graph with error bars
    ax.errorbar(df['time-step'], df[f'used {res} avg'], yerr=df[f'used {res} std'], fmt='-o', label=f'Average of used {res}')

    # Adding vertical bars representing 'unused cpu'
    ax.bar(df['time-step'], df[f'unused {res}'], alpha=0.5, label=f'Unused {res}')

    # Adding labels and title to the graph
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    
    if res == 'ram' or res == 'storage':
        ax.set_ylabel(f'{res.upper()} (MB)')
    else:
        ax.set_ylabel('CPU (Processing units)')
    
    ax.set_title(f'title - {alg[1]}')
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







# def cloudletsUsageComparison(algorithms, users, instance):
#     dataframes = []
#     for alg in algorithms:
#         df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/cloudlets_usage_{alg[0]}_{instance}.csv')
#         df['usage'] = df[['used cpu', 'used storage', 'used ram']].mean(axis=1)
#         print(alg[1])
#         print(df['usage'])
#         df['time-step'] -= 1
#         df['time-step'] /= 60
#         dataframes.append(df)

#     # Merge dataframes using a common key, such as a timestamp
#     merged_df = pd.concat(dataframes)

#     # Group the merged dataframe by algorithm and timestamp and calculate the mean
#     grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

#     # Create a line plot with three lines, each representing one algorithm
#     fig, ax = plt.subplots(figsize=(8, 6))

#     for algorithm in grouped_data.index.get_level_values('algorithm').unique():
#         data = grouped_data.loc[algorithm]
#         ax.plot(data.index.get_level_values('time-step'), data['usage'], label=algorithm)

#     # Customize the plot
#     ax.set_xticks(merged_df['time-step'].unique())
#     ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
#     ax.set_ylabel('Cloudlets Usage (%)')
#     ax.set_title('Cloudlets Usage Comparison')
#     ax.legend()
#     plt.savefig('cloudlets_usage_comparison.png')
#     plt.show()

def pricesComparison(algorithms, users, instance):
    dataframes = []
    dfExact = pd.read_csv(f'{PATH}8-30users/social_welfare_8_1.csv')
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

    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['prices'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Ratio (profit achived/optimal social welfare)')
    ax.set_title('Profit Comparison')
    ax.legend()
    plt.savefig('prices_comparison.png')
    # plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'Cross Edge with QuadTree'), (3, 'Cross Edge'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
algorithms_noQT = [(1, 'Greedy'), (3, 'Cross Edge'), (4, '2-phases')]
users = 100
instance = 1

cloudletsUsageComparison(algorithms, users, instance)
latencyComparison(algorithms, users, instance)
execTimeComparison(algorithms_noQT, users, instance)
execTimeComparison(algorithms_QT, users, instance)
socialWelfareComparison(algorithms, users, instance)
pricesComparison(algorithms, users, instance)
