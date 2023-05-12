import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### Set your path to the folder containing the .csv files
PATH = '/home/jps/GraphGenFrw/Simulator/logfiles/alg' # Use your path

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
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/social_welfare_{alg[0]}_{instance}.csv')
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
        ax.plot(data.index.get_level_values('time-step'), data['social welfare'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Social Welfare ($)')
    ax.set_title('Social Welfare Comparison')
    ax.legend()
    plt.savefig('social_welfare_comparison.png')
    # plt.show()

def cloudletsUsageComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/cloudlets_usage_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['usage'] = df[['used cpu', 'used storage', 'used ram']].mean(axis=1)
        print(alg[1])
        print(df['usage'])
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
        ax.plot(data.index.get_level_values('time-step'), data['usage'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Cloudlets Usage (%)')
    ax.set_title('Cloudlets Usage Comparison')
    ax.legend()
    plt.savefig('cloudlets_usage_comparison.png')
    plt.show()

def pricesComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/prices_{alg[0]}_{instance}.csv')
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
        ax.plot(data.index.get_level_values('time-step'), data['prices'], label=algorithm)

    # Customize the plot
    ax.set_xticks(merged_df['time-step'].unique())
    ax.set_xlabel('Optimization call Δt (every 1 minute in simulation time)')
    ax.set_ylabel('Price ($)')
    ax.set_title('Price Comparison')
    ax.legend()
    plt.savefig('prices_comparison.png')
    # plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'Cross Edge with QuadTree'), (3, 'Cross Edge'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
algorithms_noQT = [(1, 'Greedy'), (3, 'Cross Edge'), (4, '2-phases')]
users = 100
instance = 1

# cloudletsUsageComparison(algorithms, users, instance)
latencyComparison(algorithms, users, instance)
# execTimeComparison(algorithms, users, instance)
# execTimeComparison(algorithms_QT, users, instance)
# socialWelfareComparison(algorithms, users, instance)
# pricesComparison(algorithms, users, instance)
