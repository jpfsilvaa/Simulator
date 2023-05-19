nbUsers=(30)

for i in {0..5}
do
    algIdx=$i
    python3 /home/jps/GraphGenFrw/Simulator/simMain.py \
        ${algIdx} \
        ${nbUsers} \
        1 \
        /home/jps/GraphGenFrw/Simulator/GraphGen/input_files/systemInput/test30.json \
        /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/map_20171024.xml
    echo 'Done with instance '${instance}' for '${nbUsers[nbUsersIdx]}' users and algorithm '${algIdx}
done