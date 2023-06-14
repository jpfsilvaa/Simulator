nbUsers=(25)

for i in {0..5}
do
    algIdx=$i
    python3 /home/jps/GraphGenFrw/Simulator/simMain.py \
        ${algIdx} \
        ${nbUsers} \
        11 \
        /home/jps/GraphGenFrw/Simulator/GraphGen/input_files/systemInput/overflow_test25_2.json \
        /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/map_20171024.xml
    echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
done