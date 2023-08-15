import multiprocessing

def run_script(script_path):
    import subprocess
    script_path.insert(0, 'python3')
    subprocess.call(script_path)

if __name__ == '__main__':
    nbUsers = 100
    home = '/home/jps/'
    pathToSimulator = home + 'GraphGenFrw/Simulator'
    instance = 'newInst100_f2_'
    
    scriptsCalls = []
    for algIdx in [4]:
        # for i in range(20):
        scriptsCalls.append(
        [f'{pathToSimulator}/simMain.py',
        f'{algIdx}', 
        f'{nbUsers}',
        '11', 
        f'{pathToSimulator}/GraphGen/input_files/systemInput/{instance}.json', 
        f'{pathToSimulator}/GraphGen/BusMovementModel/raw_data/map_20171024.xml',
        f'{pathToSimulator}/GraphGen/BusMovementModel/raw_data/buses_20171024.xml',
        f'0'])
        
    with multiprocessing.Pool(processes=1) as pool:
        pool.map(run_script, scriptsCalls, chunksize=1)
