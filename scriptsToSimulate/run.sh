nbUsers=(100 500)

for i in {0..3}
do
    algIdx=$i
    for j in {0..1}
    do
        nbUsersIdx=$j
        for instance in {0..49}
        do
            python3 /home/jps/GraphGenFrw/Simulator/simMain.py \
                ${algIdx} \
                ${nbUsers[nbUsersIdx]} \
                ${instance} \
                /home/jps/GraphGenFrw/Simulator/GraphGen/input_files/systemInput/${nbUsers[nbUsersIdx]}users/inst_${instance}.json \
                /home/jps/GraphGenFrw/Simulator/GraphGen/BusMovementModel/raw_data/map_20171024.xml
            echo 'Done with instance '${instance}' for '${nbUsers[nbUsersIdx]}' users and algorithm '${algIdx}
        done
    done
done