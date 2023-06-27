import multiprocessing

def run_script(script_path):
    import subprocess
    subprocess.call(['python', script_path])

if __name__ == '__main__':
    nbUsers = 100
    pathToSimulator='/local1/joaosilva/GraphGenFrw/Simulator'
    
    scriptsCalls = []
    for algIdx in range(5):
        for i in range(20):
            scriptsCalls.append(
                f'python3 {pathToSimulator}/simMain.py \
                {algIdx} \
                {nbUsers} \
                11 \
                {pathToSimulator}/GraphGen/input_files/systemInput/newInst_500.json \
                {pathToSimulator}/GraphGen/BusMovementModel/raw_data/map_20171024.xml \
                {pathToSimulator}/GraphGen/BusMovementModel/raw_data/buses_20171024.xml \
                {i}')
    with multiprocessing.Pool(processes=20) as pool:
        pool.map(run_script, scriptsCalls, chunksize=5)
