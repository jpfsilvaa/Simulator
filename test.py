import matplotlib.pyplot as plt
import numpy as np

# Sample data
categories = ['Category 1', 'Category 2', 'Category 3']
dataset1 = [10, 15, 8]
dataset2 = [12, 9, 6]
dataset3 = [5, 7, 9]
dataset4 = [14, 11, 13]

# Set the bar width
bar_width = 0.25

# Set the x positions of the bars
bar_positions = np.arange(len(categories))

# Calculate the offset for each dataset
offset = bar_width / 3

# Calculate the width of the fourth bar
fourth_bar_width = 1.2*bar_width

# Create the figure and the subplot
fig, ax = plt.subplots()

# Plot the fourth bar representing the fourth dataset
ax.bar(bar_positions - 1.8*offset, dataset4, width=fourth_bar_width, align='edge', alpha=0.5, color='gray', label='Dataset 4')

# Plot the bars for the first three datasets
ax.bar(bar_positions - offset, dataset1, width=bar_width/3, align='center', label='Dataset 1')
ax.bar(bar_positions, dataset2, width=bar_width/3, align='center', label='Dataset 2')
ax.bar(bar_positions + offset, dataset3, width=bar_width/3, align='center', label='Dataset 3')

# Set the labels, title, and ticks
ax.set_xlabel('Categories')
ax.set_ylabel('Values')
ax.set_title('Superimposed Bar Chart with Shadow')
ax.set_xticks(bar_positions)
ax.set_xticklabels(categories)
ax.legend()

# Show the plot
plt.show()
