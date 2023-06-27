nbUsers=(500)
pathToSimulator=/local1/joaosilva/GraphGenFrw/Simulator
for i in {0..5}
do
    algIdx=4
    python3 ${pathToSimulator}/simMain.py \
        ${algIdx} \
        ${nbUsers} \
        11 \
        ${pathToSimulator}/GraphGen/input_files/systemInput/newInst_500.json \
        ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/map_20171024.xml \
        ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/buses_20171024.xml
    echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
done