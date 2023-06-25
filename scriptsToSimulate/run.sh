nbUsers=(25)
pathToSimulator=/home/jps/GraphGenFrw/Simulator
# for i in {0..5}
# do
algIdx=4
python3 ${pathToSimulator}/simMain.py \
    ${algIdx} \
    ${nbUsers} \
    11 \
    ${pathToSimulator}/GraphGen/input_files/systemInput/inst_25_din.json \
    ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/map_20171024.xml \
    ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/buses_20171024.xml
echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
# done