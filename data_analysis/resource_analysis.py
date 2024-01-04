import pandas as pd

def readCsvFile(fileName):
    df = pd.read_csv(fileName)
    return df

if __name__ == '__main__':
    alg = 2
    fileName = f'/home/jps/GraphGenFrw/Simulator/logfiles/alg{alg}-100users/{alg}/cloudlets_states_{alg}_11.csv'
    df = readCsvFile(fileName)
    
    # remove line from df if the column 'c.currUsersAllocated' is '[]'
    df = df[df['c.currUsersAllocated'] != '[]']
    
    # edit colunm name
    df.rename(columns={'c.cpu(full/unused)':'c.cpu(%used)'}, inplace=True)
    df.rename(columns={'c.storage(full/unused)':'c.storage(%used)'}, inplace=True)
    df.rename(columns={'c.ram(full/unused)':'c.ram(%used)'}, inplace=True)

    # edit each value from column 'c.cpu(%used)' removing the character '()'
    df['c.cpu(%used)'] = df['c.cpu(%used)'].str.replace('(', '').str.replace(')', '')
    df['c.storage(%used)'] = df['c.storage(%used)'].str.replace('(', '').str.replace(')', '')
    df['c.ram(%used)'] = df['c.ram(%used)'].str.replace('(', '').str.replace(')', '')

    # add a colunm with the number of users allocated in each cloudlet
    df['num allocated users'] = df['c.currUsersAllocated'].str.replace('[', '').str.replace(']', '').str.split(',').str.len()

    # edit each value from colunm 'c.cpu' to a correspondent first value devided by the second value
    df['c.cpu(%used)'] = (df['c.cpu(%used)'].str.split(',', expand=True)[0].astype(float) 
        - df['c.cpu(%used)'].str.split(',', expand=True)[1].astype(float)) / df['c.cpu(%used)'].str.split(',', expand=True)[0].astype(float)
    df['c.storage(%used)'] = (df['c.storage(%used)'].str.split(',', expand=True)[0].astype(float) 
        - df['c.storage(%used)'].str.split(',', expand=True)[1].astype(float)) / df['c.storage(%used)'].str.split(',', expand=True)[0].astype(float)
    df['c.ram(%used)'] = (df['c.ram(%used)'].str.split(',', expand=True)[0].astype(float) 
        - df['c.ram(%used)'].str.split(',', expand=True)[1].astype(float)) / df['c.ram(%used)'].str.split(',', expand=True)[0].astype(float)

    # SAVE IT INTO A CSV FILE
    df.to_csv('cloudlets_states_2_11_TREATED.csv', index=False)