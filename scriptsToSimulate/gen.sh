nbUsers=(250)
pathToSimulator=/home/jps/GraphGenFrw/Simulator
for algIdx in {0..5}
do
    for i in {0..20}
    do
        mkdir ${pathToSimulator}'/logfiles/alg'${algIdx}'-'${nbUsers[0]}'users/'${i}
        echo 'Done for '${nbUsers[0]}' users and algorithm '${algIdx}
    done
done