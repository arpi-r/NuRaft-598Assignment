#!/bin/sh

# echo "start..."
for i in {2..32..2}
do 
    echo "i: $i"
    ./raft_bench 1 10.10.10.1:12347 20 100000 $i 2048 10.10.10.2:12345 10.10.10.3:12346
    echo "$i done"
    # echo "iteration done"
done
# echo "all iterations done"