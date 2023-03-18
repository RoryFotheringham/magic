#!/usr/bin/env bash

source venv/bin/activate
echo "" > depth_test.txt

for DEPTH in 3 4 5 6;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> depth_test.txt;
	for SEED in 0 1 2 3;
	do
		python synthesis_loop.py 15 $DEPTH $SEED >> depth_test.txt;
		echo " " >> depth_test.txt;
	done;
done 
	
for DEPTH in 6 7 8;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> depth_test.txt;
	for SEED in 2;
	do
		python synthesis_loop.py 15 $DEPTH $SEED >> depth_test.txt;
		echo "\n" >> depth_test.txt;
	done;
done