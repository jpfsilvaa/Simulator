nbUsers=(25)
pathToSimulator=/local1/joaosilva/GraphGenFrw_dyn/GraphGenFrw/Simulator
# for i in {0..5}
# do
algIdx=0
python3 ${pathToSimulator}/simMain.py \
    ${algIdx} \
    ${nbUsers} \
    11 \
    ${pathToSimulator}/GraphGen/input_files/systemInput/inst_25_din.json \
    ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/map_20171024.xml \
    ${pathToSimulator}/GraphGen/BusMovementModel/raw_data/buses_20171024.xml
echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
# done