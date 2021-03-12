#!/bin/bash
rm -rf peer_folder*

for i in {1..8}
do
    mkdir "peer_folder$i"
    cd "peer_folder$i"
    for j in {1..10}
    do
        mkfile 128 "data$j.txt"
    done
    cd ..
done