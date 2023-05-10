import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### Set your path to the folder containing the .csv files
PATH = '/home/jps/GraphGenFrw/Simulator/logfiles/alg' # Use your path

"""     # Load data from CSV files into pandas dataframes
    df0 = pd.read_csv(f'{PATH}0-100users/latencies_0_1.csv')
    df0['algorithm'] = 'Greedy with QuadTree'
    df1 = pd.read_csv(f'{PATH}1-100users/latencies_1_1.csv')
    df1['algorithm'] = 'Greedy'
    df2 = pd.read_csv(f'{PATH}2-100users/latencies_2_1.csv')
    df2['algorithm'] = 'Cross Edge with QuadTree'
    df3 = pd.read_csv(f'{PATH}3-100users/latencies_3_1.csv')
    df3['algorithm'] = 'Cross Edge'
    df4 = pd.read_csv(f'{PATH}4-100users/latencies_4_1.csv')
    df4['algorithm'] = '2-phases' """

def latencyComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg}-{users}users/latencies_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        dataframes.append(df)

    # Merge dataframes using a common key, such as a timestamp
    merged_df = pd.concat(dataframes)

    # Group the merged dataframe by algorithm and timestamp and calculate the mean
    grouped_data = merged_df.groupby(['algorithm', 'time-step']).mean()

    # Create a line plot with three lines, each representing one algorithm
    fig, ax = plt.subplots(figsize=(8, 6))

    for algorithm in grouped_data.index.get_level_values('algorithm').unique():
        data = grouped_data.loc[algorithm]
        ax.plot(data.index.get_level_values('time-step'), data['avg latency (for the allocated)'], label=algorithm)

    # Customize the plot
    ax.set_xlabel('Time-step')
    ax.set_ylabel('Latency')
    ax.set_title('Latency Comparison')
    ax.legend()
    plt.show()

def execTimeComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/exec_time_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
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
    ax.set_xlabel('Time-step')
    ax.set_ylabel('Execution Time')
    ax.set_title('Execution Time Comparison')
    ax.legend()
    plt.show()

def socialWelfareComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/social_welfare_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
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
    ax.set_xlabel('Time-step')
    ax.set_ylabel('Social Welfare')
    ax.set_title('Social Welfare Comparison')
    ax.legend()
    plt.show()

def cloudletsUsageComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/cloudlets_usage_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
        df['usage'] = df[['used cpu', 'used storage', 'used ram']].mean(axis=1)
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
    ax.set_xlabel('Time-step')
    ax.set_ylabel('Cloudlets Usage')
    ax.set_title('Cloudlets Usage Comparison')
    ax.legend()
    plt.show()

def pricesComparison(algorithms, users, instance):
    dataframes = []
    for alg in algorithms:
        df = pd.read_csv(f'{PATH}{alg[0]}-{users}users/prices_{alg[0]}_{instance}.csv')
        df['algorithm'] = alg[1]
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
    ax.set_xlabel('Time-step')
    ax.set_ylabel('Price')
    ax.set_title('Price Comparison')
    ax.legend()
    plt.show()

algorithms = [(0, 'Greedy with QuadTree'), (1, 'Greedy'), (2, 'Cross Edge with QuadTree'), (3, 'Cross Edge'), (4, '2-phases')]
algorithms_QT = [(0, 'Greedy with QuadTree'), (2, 'Cross Edge with QuadTree')]
algorithms_noQT = [(1, 'Greedy'), (3, 'Cross Edge'), (4, '2-phases')]
users = 100
instance = 1
cloudletsUsageComparison(algorithms, users, instance)