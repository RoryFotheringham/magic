#!/usr/bin/env bash

source venv/bin/activate
echo "" > depth_test.txt

for DEPTH in 3 4 5 6 7 8;
do 
	echo "=========| k = 20 , depth = $DEPTH |=============" >> depth_test.txt;
	for SEED in 0 1 2 3;
	do
		python synthesis_loop.py 20 $DEPTH $SEED >> depth_test.txt;
		echo "\n" >> depth_test.txt;
	done;
done 
	
