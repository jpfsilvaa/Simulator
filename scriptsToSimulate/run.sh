nbUsers=(25)

for i in {0..5}
do
    algIdx=0
    python3 /home/jps/GraphGenFrw/Simulator/simMain.py \
        ${algIdx} \
        ${nbUsers} \
        11 \
        /home/jps/GraphGenFrw/Simulator/GraphGen/input_files/systemInput/inst_25_din.json \
        /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/map_20171024.xml \
        /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/buses_20171024.xml
    echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
done