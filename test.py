import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

datasets = []
for i in range(1, 21):
    filename = f"dataset_{i}.csv"  # Replace with your actual filenames
    dataset = pd.read_csv(filename)
    datasets.append(dataset)

# Create an empty DataFrame to store the values of each row
combined_data = pd.DataFrame()

# Concatenate the rows from each dataset into the combined_data DataFrame
for dataset in datasets:
    combined_data = pd.concat([combined_data, dataset['exec time']], axis=1)

# Calculate the average and standard deviation across the rows
averages = combined_data.mean(axis=1)
std_deviations = combined_data.std(axis=1)

# Create the line plot
x = np.arange(1, len(averages) + 1)
plt.plot(x, averages, 'o-', label='Average Execution Time')

# Create the shaded region for error bars
plt.fill_between(x, averages - std_deviations, averages + std_deviations, alpha=0.3)

plt.xlabel('Row')
plt.ylabel('Execution Time')
plt.title('Average Execution Time with Error Bars')
plt.legend()
plt.show()
