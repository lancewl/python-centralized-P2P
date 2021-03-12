#!/bin/bash
set -m

SERVER='python ../server/server.py'
PEER='python ../peer/peer.py'
# How many peers
N=2
OUT="../out/eval2/N$N/"
rm ${OUT}*

# QUERY 100 times
ACT='WAIT\n'
for i in {1..100}
do
    ACT=$ACT'QUERY data1.txt\n0\n'
done
ACT=$ACT'WAIT\n'

# start the indexing server
$SERVER > ${OUT}server.txt 2>&1 &

for (( i=1; i<=$N; i++ ))
do
    echo -e $ACT | $PEER 500${i}0 --dir peer_folder${i} > ${OUT}p${i}.txt 2>&1 &
    pids[${i}]=$!
done

# wait for all peers
for pid in ${pids[*]}; do
    wait $pid
done

echo "All peer is done!"
kill -SIGINT %1