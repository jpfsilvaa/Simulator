nbUsers=(15)

for i in {0..5}
do
    algIdx=$i
    python3 /home/jps/GraphGenFrw/Simulator/simMain.py \
        ${algIdx} \
        ${nbUsers} \
        11 \
        /home/jps/GraphGenFrw/Simulator/GraphGen/input_files/systemInput/newInst.json \
        /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/map_20171024.xml
    echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
done