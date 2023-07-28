# I have the following data, and I need to take the number of 'gp1', 'gp2', 'ramIntensive', and 'cpuIntensive' values at in the entire file:
# 1,27,"[('v6', 'gp1', 'c3'), ('v10', 'gp1', 'c10'), ('v13', 'gp1', 'c45'), ('v14', 'gp1', 'c3'), ('v18', 'gp1', 'c10'), ('v21', 'gp1', '$
# 61,42,"[('v14', 'gp1', 'c3'), ('v0', 'gp1', 'c21'), ('v6', 'gp1', 'c3'), ('v10', 'gp1', 'c9'), ('v13', 'gp1', 'c21'), ('v18', 'gp1', 'c$
# 121,51,"[('v10', 'gp1', 'c46'), ('v23', 'gp1', 'c46'), ('v0', 'gp1', 'c21'), ('v6', 'gp1', 'c26'), ('v13', 'gp1', 'c21'), ('v18', 'gp1'$
# 181,61,"[('v14', 'gp1', 'c1'), ('v0', 'gp1', 'c3'), ('v6', 'gp1', 'c18'), ('v10', 'gp1', 'c17'), ('v13', 'gp1', 'c3'), ('v18', 'gp1', '$
# 241,61,"[('v0', 'gp1', 'c25'), ('v37', 'gp1', 'c26'), ('v71', 'gp1', 'c26'), ('v6', 'gp1', 'c29'), ('v10', 'gp1', 'c26'), ('v14', 'gp1'$
# 301,66,"[('v0', 'gp1', 'c16'), ('v13', 'gp1', 'c25'), ('v24', 'gp1', 'c16'), ('v48', 'gp1', 'c25'), ('v59', 'gp1', 'c25'), ('v37', 'gp1$
# 361,53,"[('v48', 'gp1', 'c3'), ('v6', 'gp1', 'c2'), ('v10', 'gp1', 'c3'), ('v14', 'gp1', 'c2'), ('v18', 'gp1', 'c3'), ('v23', 'gp1', 'c$
# 421,53,"[('v18', 'gp1', 'c32'), ('v23', 'gp1', 'c32'), ('v0', 'gp1', 'c24'), ('v10', 'gp1', 'c32'), ('v13', 'gp1', 'c43'), ('v24', 'gp1$
# 481,65,"[('v18', 'gp1', 'c39'), ('v0', 'gp1', 'c44'), ('v10', 'gp1', 'c12'), ('v13', 'gp1', 'c44'), ('v21', 'gp1', 'c7'), ('v24', 'gp1'$
# 541,34,"[('v0', 'gp1', 'c48'), ('v10', 'gp1', 'c37'), ('v13', 'gp1', 'c48'), ('v18', 'gp1', 'c37'), ('v23', 'gp1', 'c37'), ('v24', 'gp1$
# 601,20,"[('v10', 'gp1', 'c0'), ('v18', 'gp1', 'c0'), ('v23', 'gp1', 'c0'), ('v48', 'gp1', 'c0'), ('v59', 'gp1', 'c0'), ('v79', 'gp1', '$
# 661,21,"[('v10', 'gp1', 'c0'), ('v18', 'gp1', 'c0'), ('v23', 'gp1', 'c0'), ('v48', 'gp1', 'c0'), ('v2', 'gp2', 'c0'), ('v17', 'gp2', 'c$
# 721,15,"[('v10', 'gp1', 'c47'), ('v18', 'gp1', 'c47'), ('v23', 'gp1', 'c47'), ('v2', 'gp2', 'c47'), ('v17', 'gp2', 'c47'), ('v78', 'gp2$
# 781,11,"[('v21', 'gp1', 'c41'), ('v55', 'gp1', 'c41'), ('v86', 'gp1', 'c41'), ('v29', 'gp2', 'c41'), ('v58', 'gp2', 'c42'), ('v20', 'ra$
# 841,3,"[('v21', 'gp1', 'c7'), ('v20', 'ramIntensive', 'c7'), ('v40', 'cpuIntensive', 'c7')]"

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Example DataFrame with multiple numeric columns
data = pd.DataFrame({
    'category': ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D'],
    'values1': [12, 15, 10, 8, 20, 14, 18, 21],
    'values2': [5, 8, 7, 11, 15, 12, 10, 9],
    'values3': [25, 30, 22, 28, 35, 29, 31, 32]
})

# Reshape the DataFrame using melt
melted_data = pd.melt(data, id_vars='category', var_name='variable', value_name='values')

# Set the size of the plot (optional)
plt.figure(figsize=(10, 6))

# Create the boxplot with hue
sns.boxplot(x='category', y='values', data=melted_data, hue='variable')

# Optionally, add a title and labels to the axes
plt.title('Boxplot by Category for Multiple Columns')
plt.xlabel('Category')
plt.ylabel('Values')

# Show the plot
plt.show()